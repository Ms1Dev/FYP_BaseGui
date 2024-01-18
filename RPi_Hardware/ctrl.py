import deviceManager
import data
from pynmeagps import nmeahelpers
from typing import Tuple, Any
import queue
import threading
import math


class Ctrl:

    pointsOfInterest = [
        "base_gps_pos",
        "mobile_gps_pos"
    ]

    def __init__(self):
        self.antennaConnection = deviceManager.antenna
        self.dataQueue = queue.Queue()
        self.data = data.Data(self.dataQueue,self.pointsOfInterest)
        self.mobile_pos = (55, 1)
        self.base_pos = None
        dataBroadcastThread = threading.Thread(target=self.data.broadcast)
        dataBroadcastThread.daemon = True
        dataBroadcastThread.start()
        self.monitorData()


    def getBearing(self, posFrom, posTo):
        return nmeahelpers.bearing(posFrom[0], posFrom[1], posTo[0], posTo[1])


    def moveAntenna(self, az = None, el = None):
        if self.antennaConnection.isConnected():
            device = self.antennaConnection.getSerialDevice()
            if az:
                az = str(math.trunc(az))
                device.send("A" + az + "\n")
            if el:
                el = str(math.trunc(el))
                device.send("E" + el + "\n")


    def updateAntennaAzimuth(self):
        if self.mobile_pos is not None and self.base_pos is not None:
            bearing = self.getBearing(self.base_pos, self.mobile_pos)
            self.moveAntenna(az = bearing)


    def newData(self, data : Tuple[str, Any]):
        if data[0] == "base_gps_pos":
            self.base_pos = (data[1]["lat"], data[1]["lon"])
            self.updateAntennaAzimuth()
        elif data[0] == "mobile_gps_pos":
            self.mobile_pos = (data[1]["lat"], data[1]["lon"])
            self.updateAntennaAzimuth()


    def monitorData(self):
        while True:
            self.newData(self.dataQueue.get())


Ctrl()