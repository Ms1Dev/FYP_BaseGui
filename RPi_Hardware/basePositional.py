from pynmeagps import nmeahelpers, NMEAMessage, NMEAReader
import deviceManager
import queue
import time
import threading
import zmq

class BasePosition:

    def __init__(self, deviceManager : deviceManager.DeviceManager):
        self.deviceManager = deviceManager
        self.gps = None
        self.barometric = None
        self.position = None
        
        zmqContext = zmq.Context()
        self.messageSender = zmqContext.socket(zmq.PUSH)
        self.messageSender.bind("tcp://127.0.0.1:5555")

        monitorThread = threading.Thread(target=self.monitorPosition)
        monitorThread.start()

    def gpsConnectionLostCallback(self):
        self.gps = None

    def monitorPosition(self):
        while True:
            while self.gps == None:
                self.gps = self.deviceManager.gps.getSerialDevice()
                time.sleep(0.5)

            self.gps.addConnectionFailCallback(self.gpsConnectionLostCallback)

            while self.gps != None:
                self.messageReceived(self.gps.listen())

    def messageReceived(self, message):
        message = self.filterGPGGA(message.decode("UTF-8", errors="ignore"))
        try:
            position = NMEAReader.parse(message)
        except:
            pass
        if position:
            self.position = position
            message = str(position.lat) + ":" + str(position.lon)
            self.messageSender.send_string(message)

    def filterGPGGA(self, line : str):
        try:
            start = line.index("GPGGA")
            substr = line[start-1:]
            end = substr.index("*") + 3
            return substr[:end]
        except ValueError:
            return None



dm = deviceManager.DeviceManager()
basePosition = BasePosition(dm)

