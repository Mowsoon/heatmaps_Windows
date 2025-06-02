import subprocess
import re
from time import sleep

def get_wifi_interface():
    try:
        output = subprocess.check_output(["iw", "dev"], encoding="utf-8")
        for line in output.splitlines():
            if line.strip().startswith("Interface"):
                return line.split()[1]
    except subprocess.CalledProcessError:
        return None

def wifi_scan(interface):
    try:
        output = subprocess.check_output(
            ["sudo", "/sbin/iw", "dev", interface, "scan"],
            stderr=subprocess.DEVNULL,
            universal_newlines=True
        )
        return output
    except subprocess.CalledProcessError:
        print("Error running 'iw'.")
        print("Please wait...")
        sleep(3)
        return get_wifi_signals(interface)

    

def get_band(freq):
    if 2400 <= freq <= 2485:
        return "2.4GHz"
    elif 5150 <= freq <= 5825:
        return "5GHz"
    elif 5925 <= freq <= 7125:
        return "6GHz"
    else:
        return "Unknown"

def parse_scan_output(scan_output):
    networks = []
    bssid = ssid = freq = signal = None
    
    for line in scan_output.splitlines():
        line = line.strip()

        if line.startswith("BSS "):
            if ssid and signal is not None and freq and bssid:
                networks.append({
                    "ssid": ssid,
                    "bssid": bssid,
                    "signal": signal,
                    "freq": freq
                })
            match = re.match(r"BSS ([0-9a-fA-F:]+)", line)
            if match:
                bssid = match.group(1)
                ssid = signal = freq = None  

        elif line.startswith("SSID:"):
            ssid = line[5:].strip() or "<Unknown>"

        elif line.startswith("signal:"):
            match = re.search(r"-?\d+(\.\d+)?", line)
            if match:
                signal = float(match.group(0))

        elif line.startswith("freq:"):
            match = re.search(r"\d+", line)
            if match:
                freq = int(match.group(0))

    if ssid and signal is not None and freq and bssid:
        networks.append({
            "ssid": ssid,
            "bssid": bssid,
            "signal": signal,
            "freq": freq
        })

    return networks


def find_best_networks(networks):
    ssid_seen = {}
    for net in networks:
        ssid = net["ssid"]
        signal = net["signal"]
        freq = net["freq"]
        band = get_band(freq)
        bssid = net["bssid"]

        key = (ssid, band)
        if key not in ssid_seen or ssid_seen[key]["signal"] < signal:
            ssid_seen[key] = {
                "ssid": ssid,
                "bssid": bssid,
                "signal": signal,
                "band": band
            }
    return list(ssid_seen.values())

def extract_ssid():
    interface = get_wifi_interface()
    if not interface:
        print("No WiFi interface found.")
        return []

    output = wifi_scan(interface)
    networks = parse_scan_output(output)
    return find_best_networks(networks)
