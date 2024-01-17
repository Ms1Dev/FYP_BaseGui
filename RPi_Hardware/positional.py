from pynmeagps import nmeahelpers, NMEAMessage
import deviceManager
import queue
import time

class BasePosition:

    def __init__(self, deviceManager : deviceManager.DeviceManager):
        self.deviceManager = deviceManager
        self.queue = queue.Queue()
        self.gps = None
        self.barometric = None
        self.updateListeners = []

    def gpsConnectionLostCallback(self):
        print("what")
        self.gps = None

    def monitorPosition(self):
        while True:
            while self.gps == None:
                self.gps = self.deviceManager.gps.getSerialDevice()
                time.sleep(0.5)

            self.gps.addConnectionFailCallback(self.gpsConnectionLostCallback)
            self.gps.addQueue(self.queue)

            while self.gps != None:
                line = None
                try:
                    line = self.queue.get(timeout=1)
                except queue.Empty:
                    pass
                if line:
                    line = self.filterGPGGA(line.decode("UTF-8", errors="ignore"))

    
    def filterGPGGA(self, line : str):
        try:
            start = line.index("GPGGA")
            substr = line[start-1:]
            end = substr.index("*") + 3
            return substr[:end]
        except ValueError:
            return None


dm = deviceManager.DeviceManager()

bp = BasePosition(dm)

bp.monitorPosition()



