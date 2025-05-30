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