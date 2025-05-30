import pywifi as pw
import time


def wifi_scan():
    wifi = pw.PyWiFi()
    iface = wifi.interfaces()[0]
    iface.scan()
    time.sleep(3)
    return iface.scan_results()

def get_band(freq):
    if 2400 <= freq <= 24835:
        return "2.4GHz"
    elif 5150 <= freq <= 5825:
        return "5GHz"
    elif 5925 <= freq <= 7125:
        return "6GHz"
    else:
        return "Unknown"

def extract_ssid(result):
    ssid_seen = {}
    for network in result:
        ssid = network.ssid
        bssid = network.bssid
        signal = network.signal
        freq = network.freq / 1000
        band = get_band(freq)

        key = (ssid, band)
        if key not in ssid_seen or ssid_seen[key]["signal"] < signal:
            ssid_seen[key] = {
                "ssid": ssid,
                "bssid": bssid,
                "signal": signal,
                "band": band
            }

    return ssid_seen.values()
