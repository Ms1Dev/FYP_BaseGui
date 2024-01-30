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

class Ctrl:

    pointsOfInterest = [
        "base_gps_pos",
        "mobile_gps_pos",
        "base_pressure",
        "mobile_pressure"
    ]

    def __init__(self):
        self.antennaConnection = deviceManager.antenna
        self.dataQueue = queue.Queue()
        self.cmdQueue = queue.Queue()
        self.data = data.Data(self.dataQueue,self.pointsOfInterest)
        self.mobile_pos = None
        self.base_pos = None
        self.mobile_alt_relative = None
        self.base_alt_relative = None
        self.calibratedVerticalDiff = self.loadCalibrationValue()

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


    def getBearing(self, posFrom, posTo):
        try:
            return nmeahelpers.bearing(posFrom[0], posFrom[1], posTo[0], posTo[1])
        except TypeError:
            pass


    def getElevation(self, posFrom, posTo):
        try:
            planarDistance = nmeahelpers.planar(posFrom[0], posFrom[1], posTo[0], posTo[1])
        except TypeError:
            return None
        # print("pd " + str(planarDistance))
        verticalDistance = self.getVerticalDistance()
        # print("vd " + str(verticalDistance))
        elevation = math.atan(verticalDistance / planarDistance)
        return math.degrees(elevation)


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
            if az:
                az = str(math.trunc(az))
                device.send("A" + az + "\n")
            if el:
                el = str(math.trunc(el))
                device.send("E" + el + "\n")


    def hasPositions(self):
        return self.mobile_pos is not None and self.base_pos is not None
    
    
    def hasElevations(self):
        return self.mobile_alt_relative is not None and self.base_alt_relative is not None


    def updateAntennaAzimuth(self):
        if self.hasPositions():
            bearing = self.getBearing(self.base_pos, self.mobile_pos)
            self.moveAntenna(az = bearing)
    

    def updateAntennaElevation(self):
        if self.hasPositions() and self.hasElevations():
            elevation = self.getElevation(self.base_pos, self.mobile_pos)
            self.moveAntenna(el = elevation)


    def newData(self, data : Tuple[str, Any]):
        # print(data[0] + " : " + str(data[1]))

        if data[0] == "base_gps_pos":
            self.base_pos = (data[1]["lat"], data[1]["lon"])
            self.printPos(self.base_pos, 1)
            self.updateAntennaAzimuth()
        elif data[0] == "mobile_gps_pos":
            self.mobile_pos = (data[1]["lat"], data[1]["lon"])
            self.updateAntennaAzimuth()
        elif data[0] == "base_pressure":
            unitsIndex = data[1].index("mb")
            pressure = data[1][:unitsIndex]
            self.base_alt_relative = self.altFromPressure(pressure)
            # print("Base: " + str(self.base_alt_relative) + " Mobile: " + str(self.mobile_alt_relative))
            # print("Diff: " + str(self.getVerticalDistance()))
            self.updateAntennaElevation()
        elif data[0] == "mobile_pressure":
            unitsIndex = data[1].index("mb")
            pressure = data[1][:unitsIndex]
            self.mobile_alt_relative = self.altFromPressure(pressure)
            # print("Base: " + str(self.base_alt_relative) + " Mobile: " + str(self.mobile_alt_relative))
            # print("Diff: " + str(self.getVerticalDistance()))
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
        if cmd["message"] == "cal":
            self.calibrateVerticalDistance()


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

Ctrl()