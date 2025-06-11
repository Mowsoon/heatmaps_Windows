import subprocess
import re
import time
from time import sleep
import platform

def get_wifi_interface_linux():
    try:
        output = subprocess.check_output(["iw", "dev"], encoding="utf-8")
        for line in output.splitlines():
            if line.strip().startswith("Interface"):
                return line.split()[1]
    except subprocess.CalledProcessError:
        return None

def wifi_scan_iw(interface):
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
        return wifi_scan_iw(interface)

def wifi_scan_netsh():
    try:
        output = subprocess.check_output(
            ["netsh", "wlan", "show", "networks", "mode=bssid"],
            stderr=subprocess.DEVNULL,
            universal_newlines=True,
            encoding="utf-8"
        )
        return output
    except subprocess.CalledProcessError:
        print("Error running 'netsh'.")
        return ""

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
                band = get_band(freq)
                networks.append({
                    "ssid": ssid,
                    "bssid": bssid,
                    "signal": signal,
                    "band": band
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
        band = get_band(freq)
        networks.append({
            "ssid": ssid,
            "bssid": bssid,
            "signal": signal,
            "band": band
        })

    return networks

def parse_windows_scan_output(output):
    networks = []
    lines = output.splitlines()
    ssid = bssid = rssi = None
    for line in lines:
        line = line.strip()
        match_ssid = re.match(r"^SSID \d+\s*:\s*(.+)$", line)
        if match_ssid:
            ssid = match_ssid.group(1)
            continue

        match_bssid = re.match(r"^BSSID \d+\s*:\s*([0-9a-fA-F:]+)$", line)
        if match_bssid:
            bssid = match_bssid.group(1)
            continue
        match_signal = re.match(r"^Signal\s*:\s*(\d+)%$", line)
        if match_signal:
            signal_percent = int(match_signal.group(1))
            rssi = (signal_percent / 2) - 100
            continue

        match_band = re.match(r"^Bande\s*:\s*(.+)$", line)
        if match_band:
            band = match_band.group(1).replace("\u00a0", " ").strip()  # clean non-breaking spaces
            if ssid and bssid and rssi is not None and band:
                networks.append({
                    "ssid": ssid,
                    "bssid": bssid,
                    "signal": rssi,
                    "band": band
                })
                bssid = rssi = None

    return networks


def find_best_networks(networks):
    ssid_seen = {}
    for net in networks:
        ssid = net["ssid"]
        signal = net["signal"]
        band = net["band"]
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

def extract_ssid_windows():
    time.sleep(15)
    output = wifi_scan_netsh()
    return parse_windows_scan_output(output)

def extract_ssid_linux():
    interface = get_wifi_interface_linux()
    if not interface:
        print("No WiFi interface found.")
        return []
    output = wifi_scan_iw(interface)
    return parse_scan_output(output)


def extract_ssid():
    os_actions = {
        "Windows": extract_ssid_windows,
        "Linux": extract_ssid_linux,
    }

    os = platform.system()
    networks = os_actions.get(os, lambda: [])()
    return find_best_networks(networks)

