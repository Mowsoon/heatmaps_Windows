import pywifi as pw
import time


def wifi_scan():
    wifi = pw.PyWiFi()
    iface = wifi.interfaces()[0]
    iface.scan()
    time.sleep(3)
    return iface.scan_results()
