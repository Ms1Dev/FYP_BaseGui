import subprocess
import oled
import netifaces
import zmq
import threading
import json

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



############# Live Info ##################

base_pos = []
antenna_pos = [0,0]

def _observeBasePos(data):
    global base_pos
    base_pos.clear()
    base_pos.append("Lat: " + str(data["lat"]))
    base_pos.append("Lon: " + str(data["lon"]))
    base_pos.append("Alt: " + str(data["alt"]))


def _observeAntennaPosAz(data):
    global antenna_pos
    antenna_pos[0] = "AZ: " + str(data) + "°"

def _observeAntennaPosEl(data):
    global antenna_pos
    antenna_pos[1] = "EL: " + str(data) + "°"


liveInfoListeners = {
    "base_gps_pos" : _observeBasePos,
    "antenna_azimuth" : _observeAntennaPosAz,
    "antenna_elevation" : _observeAntennaPosEl
}


def liveInfo():
    zmqContext = zmq.Context()
    receiver = zmqContext.socket(zmq.SUB)
    receiver.connect("tcp://127.0.0.1:5557")
    receiver.subscribe("")

    while True:
        cmd = json.loads(receiver.recv_json())
        for parameter, method in liveInfoListeners.items():
            if parameter in cmd:
                method(cmd.get(parameter))
            
liveInfoThread = threading.Thread(target=liveInfo)
liveInfoThread.daemon = True
liveInfoThread.start()