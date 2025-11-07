import subprocess
import re
import time
from time import sleep
from collections import defaultdict
from config import SYS, WIFI_INTERFACE
import pywifi
from typing import List, Dict, Tuple, Any, DefaultDict


def wifi_scan_iw(interface: str) -> str:
    """
    Performs a Wi-Fi scan on Linux using the 'iw' command.
    Retries up to 3 times in case of errors.
    """
    retries = 3
    while retries > 0:
        try:
            # Execute the iw scan command
            output = subprocess.check_output(
                ["sudo", "/sbin/iw", "dev", interface, "scan"],
                stderr=subprocess.DEVNULL,  # Suppress error output
                universal_newlines=True
            )
            return output
        except subprocess.CalledProcessError:
            print("Error running 'iw'.")
            print("Please wait...")
            sleep(3)
            retries -= 1
    # Raise an error if all retries fail
    raise RuntimeError("Failed to run 'iw' scan after multiple attempts.")


def wifi_scan_netsh() -> str:
    """
    Performs a Wi-Fi scan on Windows using the 'netsh' command.
    This command retrieves the system's cached scan results.
    """
    try:
        # Execute the netsh command to show BSSID information
        output = subprocess.check_output(
            ["netsh", "wlan", "show", "networks", "mode=bssid"],
            stderr=subprocess.DEVNULL,  # Suppress error output
            universal_newlines=True,
            encoding="utf-8"  # Ensure correct encoding
        )
        return output
    except subprocess.CalledProcessError:
        print("Error running 'netsh'.")
        return ""


def get_band(freq: int) -> str:
    """
    Determines the Wi-Fi band (2.4GHz, 5GHz, 6GHz) based on frequency.
    """
    if 2400 <= freq <= 2485:
        return "2.4GHz"
    elif 5150 <= freq <= 5825:
        return "5GHz"
    elif 5925 <= freq <= 7125:
        return "6GHz"
    else:
        return "Unknown"


def parse_scan_output(scan_output: str) -> List[Dict[str, Any]]:
    """
    Parses the text output from the 'iw' (Linux) scan command.
    """
    networks: List[Dict[str, Any]] = []
    bssid = ssid = freq = signal = None

    for line in scan_output.splitlines():
        line = line.strip()

        # A new BSS block starts
        if line.startswith("BSS "):
            # If we have data from a previous block, save it
            if ssid and signal is not None and freq and bssid:
                band = get_band(freq)
                networks.append({
                    "ssid": ssid,
                    "bssid": bssid,
                    "signal": signal,
                    "band": band
                })

            # Start parsing the new block
            match = re.match(r"BSS ([0-9a-fA-F:]+)", line)
            if match:
                bssid = match.group(1)
                ssid = signal = freq = None  # Reset for the new block

        elif line.startswith("SSID:"):
            ssid = line[5:].strip() or "<Unknown>"

        elif line.startswith("signal:"):
            match = re.search(r"-?\d+(\.\d+)?", line)
            if match:
                signal = float(match.group(0))  # Signal is in dBm

        elif line.startswith("freq:"):
            match = re.search(r"\d+", line)
            if match:
                freq = int(match.group(0))  # Frequency is in MHz

    # Save the last network entry after the loop finishes
    if ssid and signal is not None and freq and bssid:
        band = get_band(freq)
        networks.append({
            "ssid": ssid,
            "bssid": bssid,
            "signal": signal,
            "band": band
        })

    return networks


def parse_windows_scan_output(output: str) -> List[Dict[str, Any]]:
    """
    Parses the text output from the 'netsh' (Windows) scan command.
    Uses bilingual regex to handle both English and French OS languages.
    """
    networks: List[Dict[str, Any]] = []
    lines = output.splitlines()
    ssid = bssid = rssi = None

    for line in lines:
        line = line.strip()

        # Match SSID
        match_ssid = re.match(r"^SSID \d+\s*:\s*(.+)$", line)
        if match_ssid:
            ssid = match_ssid.group(1)
            continue

        # Match BSSID
        match_bssid = re.match(r"^BSSID \d+\s*:\s*([0-9a-fA-F:]+)$", line)
        if match_bssid:
            bssid = match_bssid.group(1)
            continue

        # Match Signal (works for both EN "Signal" and FR "Signal")
        match_signal = re.match(r"^Signal\s*:\s*(\d+)%$", line)
        if match_signal:
            signal_percent = int(match_signal.group(1))
            # Convert percentage to approximate dBm (a common formula)
            rssi = (signal_percent / 2) - 100
            continue

        # Match Band (EN "Band" or FR "Bande")
        match_band = re.match(r"^(?:Band|Bande)\s*:\s*(.+)$", line)
        if match_band:
            band = match_band.group(1).replace("\u00a0", " ").strip()  # Clean non-breaking spaces

            # If we have all components for a BSSID, save it
            if ssid and bssid and rssi is not None and band:
                networks.append({
                    "ssid": ssid,
                    "bssid": bssid,
                    "signal": rssi,
                    "band": band
                })
                # Reset BSSID-specific fields for the next BSSID block
                bssid = rssi = None

    return networks


def find_best_networks(networks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Filters a list of scan results to keep only the strongest BSSID
    for each unique SSID + Band combination.
    """
    ssid_seen: Dict[Tuple[str, str], Dict[str, Any]] = {}

    for net in networks:
        ssid = net["ssid"]
        signal = net["signal"]
        band = net["band"]
        bssid = net["bssid"]

        key = (ssid, band)

        # If this SSID/Band is new, or this BSSID is stronger than the saved one
        if key not in ssid_seen or ssid_seen[key]["signal"] < signal:
            ssid_seen[key] = {
                "ssid": ssid,
                "bssid": bssid,
                "signal": signal,
                "band": band
            }

    # Return a list of the best networks
    return list(ssid_seen.values())


def count_wifi_channels_from_netsh_output(output: str) -> Dict[int, int]:
    """
    Parses the 'netsh' output to count APs on each channel.
    Uses bilingual regex for EN "Channel" and FR "Canal".
    """
    channel_counts: DefaultDict[int, int] = defaultdict(int)
    lines = output.splitlines()

    for line in lines:
        line = line.strip()
        # Match Channel (EN "Channel" or FR "Canal")
        match = re.match(r"^(?:Channel|Canal)\s*:\s*(\d+)", line)
        if match:
            channel = int(match.group(1))
            channel_counts[channel] += 1

    return dict(channel_counts)


def count_wifi_channels_from_iw_output(output: str) -> Dict[int, int]:
    """
    Parses the 'iw' output to count APs on each channel.
    """
    channel_counts: DefaultDict[int, int] = defaultdict(int)

    # Each BSS block is separated by "BSS "
    blocks = output.split("BSS ")
    for block in blocks[1:]:  # Skip the first split (before any "BSS ")
        # Search for the channel number in the DS Parameter set
        match = re.search(r"DS Parameter set:\s+channel\s+(\d+)", block)
        if match:
            channel = int(match.group(1))
            channel_counts[channel] += 1

    return dict(channel_counts)


def extract_windows() -> Tuple[List[Dict[str, Any]], Dict[int, int]]:
    """
    Windows-specific scan implementation.
    Uses pywifi to trigger a fresh scan, then netsh to read the results
    (which include channel data that pywifi misses).
    """
    if not WIFI_INTERFACE:
        return [], {}

    # Trigger a new scan. This is asynchronous.
    WIFI_INTERFACE.scan()

    # Wait for the system's scan cache to update. 3 seconds is
    # typically enough after a pywifi-triggered scan.
    time.sleep(3)

    # Read the (now fresh) scan results from netsh
    output = wifi_scan_netsh()

    # Parse the output for channel counts and network info
    channels = count_wifi_channels_from_netsh_output(output)
    networks = parse_windows_scan_output(output)

    return networks, channels


def extract_linux() -> Tuple[List[Dict[str, Any]], Dict[int, int]]:
    """
    Linux-specific scan implementation using 'iw'.
    """
    output = wifi_scan_iw(WIFI_INTERFACE)

    # Parse the output for channel counts and network info
    channels = count_wifi_channels_from_iw_output(output)
    networks = parse_scan_output(output)

    return networks, channels


def extract_scan() -> Tuple[List[Dict[str, Any]], Dict[int, int]]:
    """
    Main entry point for performing a scan.
    Calls the correct OS-specific function and returns the
    filtered (best networks only) results and channel counts.
    """
    # OS-specific function mapping
    os_actions = {
        "Windows": extract_windows,
        "Linux": extract_linux,
    }

    # Call the appropriate function for the current system (SYS from config.py)
    # Default to an empty result if OS is not supported
    networks, channels = os_actions.get(SYS, lambda: ([], {}))()

    # Filter to only the best BSSID per SSID/Band
    return find_best_networks(networks), channels