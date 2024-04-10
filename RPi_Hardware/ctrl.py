import deviceManager
import data
from pynmeagps import nmeahelpers
from typing import Tuple, Any
import queue
import threading
import math
import socket
import oled
from pvlib import atmosphere
import zmq
import time
from position import Position
from altitude import Altitude
from interface import Interface
from coordinateLogger import CoordinateLogger

class Ctrl:
    compass_pos_offset = 10
    
    pointsOfInterest = [
        "base_gps_pos",
        "mobile_gps_pos",
        "base_pressure",
        "mobile_pressure",
        "compass_bearing",
        "compass_validation",
        "compass_calibration"
    ]

    ping_timout_s = 8.0

    def __init__(self):

        self.interface = Interface(self)
        self.antennaConnection = deviceManager.antenna
        self.hc12Connection = deviceManager.hc12
        self.compassConnection = deviceManager.compass
        self.dataQueue = queue.Queue()
        self.cmdQueue = queue.Queue()
        self.data = data.Data(self.dataQueue,self.pointsOfInterest)
        self.base_pos = Position()
        self.mobile_pos = Position()
        self.mobile_alt = Altitude("live")
        self.base_alt = Altitude("avg")
        self.mobile_pos.setSampleSize(1)
        self.mobile_pos.liveLocation()
        self.mobile_alt_relative = None
        self.alt_diff = 0
        self.base_alt_relative = None
        self.calibratedVerticalDiff = self.loadCalibrationValue()
        self.manual_antenna_ctrl = False
        self.latest_ping_id = 100
        self.ping_timeout_timer = None
        self.coordinateLogger = None
        self.latest_bearing = 0
        self.absolute_bearing = True
        

    def begin(self):
        commandRecvThread = threading.Thread(target=self.cmdListen)
        uiThread = threading.Thread(target=self.interface.begin)
        zmqContext = zmq.Context()
        self.receiver = zmqContext.socket(zmq.PULL)
        self.receiver.bind("tcp://127.0.0.1:5556")
        commandRecvThread.daemon = True
        commandRecvThread.start()
        uiThread.daemon = True
        uiThread.start()
        self.monitor()


    def cmdListen(self):
        while True:
            cmd = self.receiver.recv_json()
            self.cmdQueue.put(cmd)


    def loadCalibrationValue(self):
        try:
            with open("./calibration_value.txt") as calibrationValue:
                return float(calibrationValue.readline())
        except Exception:
            return 0.0    


    def storeCalibrationValue(self, value):
        try:
            with open("./calibration_value.txt", "w") as calibrationValue:
                calibrationValue.write(str(value))
        except Exception:
            pass  


    def getElevation(self):
        horizontal_distance = self.base_pos.getDistanceTo(self.mobile_pos)
        if horizontal_distance:
            vertical_distance = self.mobile_alt.getVerticalDistance(self.base_alt, self.calibratedVerticalDiff)
            elevation = math.atan(vertical_distance / horizontal_distance)
            return math.degrees(elevation)
        return None


    def getDistance(self):
        h_distance = self.mobile_pos.getDistanceTo(self.base_pos)
        v_distance = self.mobile_alt.getVerticalDistance(self.base_alt, self.calibratedVerticalDiff)
        
        if h_distance is None or v_distance is None:
            return None

        return math.sqrt(h_distance ** 2 + v_distance ** 2)


    def calibrateVerticalDistance(self):
        self.calibratedVerticalDiff = self.mobile_alt.getVerticalDistance(self.base_alt)
        if self.calibratedVerticalDiff:
            self.storeCalibrationValue(self.calibratedVerticalDiff)


    def moveAntenna(self, az = None, el = None):
        if self.antennaConnection.isConnected():
            device = self.antennaConnection.getSerialDevice()
            if az is not None:
                az = str(math.trunc(az))
                device.send("A" + az + "\n")
            if el is not None:
                el = str(math.trunc(el))
                device.send("E" + el + "\n")


    def homeAntenna(self):
        self.antennaConnection.getSerialDevice().send("H1\n")


    def updateAntennaAzimuth(self):
        bearing = self.base_pos.getBearingTo(self.mobile_pos)
        if bearing is not None and not self.manual_antenna_ctrl:
            if self.absolute_bearing:
                bearing = ((bearing + 180 - self.latest_bearing + self.compass_pos_offset) % 360) - 180
            self.moveAntenna(az = bearing)
    

    def updateAntennaElevation(self):
        elevation = self.getElevation()
        if elevation is not None and not self.manual_antenna_ctrl:
            self.moveAntenna(el = elevation)


    def getLatestPingId(self):
        self.latest_ping_id += 1
        if self.latest_ping_id > 999:
            self.latest_ping_id = 100
        return self.latest_ping_id
    

    def pingSent(self, pingSentWhen):
        self.browserPingSentWhen = pingSentWhen
        self.internalPingSentWhen = time.time()
        self.hc12Connection.getSerialDevice().send("␅" + str(self.getLatestPingId()))
        if self.ping_timeout_timer:
            self.ping_timeout_timer.cancel()
        self.ping_timeout_timer = threading.Timer(self.ping_timout_s, self.pingTimeout)
        self.ping_timeout_timer.start()


    def pingReceived(self, pingId):
        if int(pingId) == self.latest_ping_id:
            self.ping_timeout_timer.cancel()
            now = time.time() * 1000
            webReqTime = self.browserPingSentWhen
            ctrlToHc12 = self.internalPingSentWhen * 1000
            self.data.broadcast("ping",[webReqTime,ctrlToHc12,now])


    def pingTimeout(self):
        self.latest_ping_id += 1
        now = time.time() * 1000
        webReqTime = self.browserPingSentWhen
        ctrlToHc12 = self.internalPingSentWhen * 1000
        self.data.broadcast("ping",[webReqTime,ctrlToHc12,now,"Timeout"])


    def newData(self, data : Tuple[str, Any]):
        if data[0] == "ping":
            self.pingReceived(data[1])
        if data[0] == "base_gps_pos":
            self.base_pos.newData((data[1]["lat"], data[1]["lon"]))
            self.data.addToData("base_ctrl_coord", self.base_pos.getLatest())
            self.updateAntennaAzimuth()
        elif data[0] == "mobile_gps_pos":
            self.mobile_pos.newData((data[1]["lat"], data[1]["lon"]))
            self.updateAntennaAzimuth()
            distance = self.getDistance()
            self.data.addToData("distance", distance)
            self.logCoordinate(distance)
        elif data[0] == "base_pressure":
            unitsIndex = data[1].index("mb")
            pressure = data[1][:unitsIndex]
            self.base_alt.newData(pressure)
            self.updateAntennaElevation()
        elif data[0] == "mobile_pressure":
            unitsIndex = data[1].index("mb")
            pressure = data[1][:unitsIndex]
            self.mobile_alt.newData(pressure)
            self.alt_diff = self.mobile_alt.getVerticalDistance(self.base_alt, self.calibratedVerticalDiff)
            self.data.addToData("alt_diff",self.alt_diff)
            self.updateAntennaElevation()
        elif data[0] == "compass_bearing":
            self.latest_bearing = data[1][1]
        elif data[0] == "compass_calibration":
            pass
        elif data[0] == "compass_validation":
            pass

    def monitor(self):
        while True:
            try:
                self.newData(self.dataQueue.get(block=False))
            except queue.Empty:
                pass
            try:
                self.runCmd(self.cmdQueue.get(block=False))
            except queue.Empty:
                pass
            
            time.sleep(0.1)
                

    def runCmd(self, cmd):
        if "cal" in cmd:
            self.calibrateVerticalDistance()
        elif "antenna_home" in cmd:
            self.homeAntenna()
        elif "antenna_ctrl" in cmd:
            if cmd["antenna_ctrl"] == "man":
                self.manual_antenna_ctrl = True
            else:
                self.manual_antenna_ctrl = False
        elif "antenna_pos" in cmd:
            self.setAntennaPosMode(cmd["antenna_pos"])
        elif "azimuth" in cmd and self.manual_antenna_ctrl:
            self.moveAntenna(az = cmd["azimuth"])
        elif "elevation" in cmd and self.manual_antenna_ctrl:
            self.moveAntenna(el = cmd["elevation"])
        elif "transmit" in cmd:
            self.hc12Connection.getSerialDevice().send(cmd["transmit"])
        elif "ping" in cmd:
            self.pingSent(cmd["ping"])
        elif "bearing_absolute" in cmd:
            self.absolute_bearing = cmd["bearing_absolute"]
            self.data.addToData("base_bearing", self.absolute_bearing - 180 + self.compass_pos_offset)
        elif "compass" in cmd:
            if cmd["compass"] == "calibrate":
                self.calibrateCompass()
            elif cmd["compass"] == "validate":
                self.validateCompass()


    def logCoordinate(self, distance):
        if self.coordinateLogger is not None:
            self.coordinateLogger.update(self.base_pos, self.mobile_pos, distance)


    def beginLoggingCoordinates(self):
        self.coordinateLogger = CoordinateLogger()

    
    def stopLoggingCoordinates(self):
        self.coordinateLogger = None


    def absoluteBearing(self):
        self.absolute_bearing = True


    def relativeBearing(self):
        self.absolute_bearing = False

    
    def calibrateCompass(self):
        self.compassConnection.serialDevice.send("C1\n")


    def validateCompass(self):
        self.compassConnection.serialDevice.send("V1\n")


    def setAntennaPosMode(self, command):
        position = None
        if "pos" in command:
            position = command["pos"]
        if "mode" in command:
            if command["mode"] == "avg":
                self.base_pos.avgLocation()
            elif command["mode"] == "fixed":
                self.base_pos.fixLocation(position)
            elif command["mode"] == "live":
                self.base_pos.liveLocation()


control = Ctrl()

if __name__ == '__main__':
    control.begin()