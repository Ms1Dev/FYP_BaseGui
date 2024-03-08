import subprocess
import oled
import netifaces


def wifiClientMode():
    result = subprocess.run("/home/michael-zwann/pidjango/ShellScripts/client_mode.sh", shell=True, capture_output=True, text=True, timeout=10)
    if len(result.stderr) == 0:
        oled.top_right = "STA"
        return True
    print(result.stderr)
    return False 


def wifiAPMode():
    result = subprocess.run("/home/michael-zwann/pidjango/ShellScripts/ap_mode.sh", shell=True, capture_output=True, text=True, timeout=10)
    if len(result.stderr) == 0:
        oled.top_right = "AP"
        return True
    print(result.stderr)
    return False 
    

def getConnectionInfo():
    rows = []
    try:
        ip_address = netifaces.ifaddresses('wlan0')[netifaces.AF_INET][0]['addr']
        if ip_address == "ADDR: 192.168.4.1":
            rows.append("SSID: Smart_antenna")
            rows.append("PSWD: longbow13")
        rows.append(ip_address)
    except:
        pass
    return rows