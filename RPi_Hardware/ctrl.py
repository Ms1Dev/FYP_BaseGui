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
import interface

class Ctrl:

    pointsOfInterest = [
        "base_gps_pos",
        "mobile_gps_pos",
        "base_pressure",
        "mobile_pressure"
    ]

    def __init__(self):
        self.antennaConnection = deviceManager.antenna
        self.hc12Connection = deviceManager.hc12
        self.dataQueue = queue.Queue()
        self.cmdQueue = queue.Queue()
        self.data = data.Data(self.dataQueue,self.pointsOfInterest)
        self.base_pos = Position()
        self.mobile_pos = Position()
        self.mobile_pos.setSampleSize(1)
        self.mobile_pos.liveLocation()
        self.mobile_alt_relative = None
        self.alt_diff = 0
        self.base_alt_relative = None
        self.calibratedVerticalDiff = self.loadCalibrationValue()
        self.manual_antenna_ctrl = False


    def begin(self):
        threading.Thread(target=self.getIpAddr).start()
        dataBroadcastThread = threading.Thread(target=self.data.broadcast)
        commandRecvThread = threading.Thread(target=self.cmdListen)
        zmqContext = zmq.Context()
        self.receiver = zmqContext.socket(zmq.PULL)
        self.receiver.bind("tcp://127.0.0.1:5556")
        commandRecvThread.daemon = True
        commandRecvThread.start()
        dataBroadcastThread.daemon = True
        dataBroadcastThread.start()
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
        

    def altFromPressure(self, pressure):
        pressure = float(pressure)
        pressure = pressure * 100 # convert to pa
        return atmosphere.pres2alt(pressure)
    

    def getElevation(self):
        horizontal_distance = self.base_pos.getDistanceTo(self.mobile_pos)
        if horizontal_distance:
            vertical_distance = self.getVerticalDistance()
            elevation = math.atan(vertical_distance / horizontal_distance)
            return math.degrees(elevation)
        return None


    def getVerticalDistance(self):
        if self.hasElevations():
            return self.mobile_alt_relative - self.base_alt_relative - self.calibratedVerticalDiff
    

    def calibrateVerticalDistance(self):
        if self.hasElevations():
            self.calibratedVerticalDiff = self.mobile_alt_relative - self.base_alt_relative
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

    
    def hasElevations(self):
        return self.mobile_alt_relative is not None and self.base_alt_relative is not None


    def updateAntennaAzimuth(self):
        bearing = self.base_pos.getBearingTo(self.mobile_pos)
        if bearing is not None and not self.manual_antenna_ctrl:
            self.moveAntenna(az = bearing)
    

    def updateAntennaElevation(self):
        if self.hasElevations() and not self.manual_antenna_ctrl:
            elevation = self.getElevation()
            self.moveAntenna(el = elevation)


    def newData(self, data : Tuple[str, Any]):
        if data[0] == "base_gps_pos":
            self.base_pos.newData((data[1]["lat"], data[1]["lon"]))
            self.printPos(self.base_pos.getLatest(), 1)
            self.data.data["base_ctrl_coord"] = self.base_pos.getLatest()
            self.updateAntennaAzimuth()
        elif data[0] == "mobile_gps_pos":
            self.mobile_pos.newData((data[1]["lat"], data[1]["lon"]))
            self.updateAntennaAzimuth()
        elif data[0] == "base_pressure":
            unitsIndex = data[1].index("mb")
            pressure = data[1][:unitsIndex]
            self.base_alt_relative = self.altFromPressure(pressure)
            self.updateAntennaElevation()
        elif data[0] == "mobile_pressure":
            unitsIndex = data[1].index("mb")
            pressure = data[1][:unitsIndex]
            self.mobile_alt_relative = self.altFromPressure(pressure)
            self.alt_diff = self.getVerticalDistance()
            self.data.data["alt_diff"] = self.alt_diff
            self.updateAntennaElevation()


    def printPos(self, pos, row):
        try:
            oled.print_text("Base: " + str(round(pos[0], 3)) + " ,  " + str(round(pos[1], 3)), row)
        except TypeError as e:
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
        print(cmd)
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
        elif "info" in cmd:
            self.sendInfo()


    def sendInfo(self):
        info = {
            "manual_override" : self.manual_antenna_ctrl,
            "antenna_pos_mode": self.base_pos.getMode()
        }


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
        

    def getIpAddr(self):
        addr = None
        while addr is None:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.connect(("8.8.8.8", 80))
                addr = sock.getsockname()[0]
                sock.close()
            except Exception:
                pass
        oled.print_text(addr, 0, 127)



if __name__ == '__main__':
    control = Ctrl()
    control.begin()