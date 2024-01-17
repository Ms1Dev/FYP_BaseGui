from pynmeagps import nmeahelpers, NMEAMessage, NMEAReader
import deviceManager
import time
import threading

class MobilePosition:

    def __init__(self, deviceManager : deviceManager.DeviceManager):
        self.deviceManager = deviceManager
        self.hc12 = None
        self.position = None
        monitorThread = threading.Thread(target=self.monitorPosition)
        monitorThread.start()

    def hc12ConnectionLostCallback(self):
        self.hc12 = None

    def monitorPosition(self):
        while True:
            while self.hc12 == None:
                self.hc12 = self.deviceManager.hc12.getSerialDevice()
                time.sleep(0.5)

            self.hc12.addConnectionFailCallback(self.hc12ConnectionLostCallback)

            while self.hc12 != None:
                self.messageReceived(self.hc12.listen())

    def messageReceived(self, message):
        message = self.filterGPGGA(message.decode("UTF-8", errors="ignore"))
        try:
            position = NMEAReader.parse(message)
        except:
            pass
        if position:
            self.position = position

    def filterGPGGA(self, line : str):
        try:
            start = line.index("GPGGA")
            substr = line[start-1:]
            end = substr.index("*") + 3
            return substr[:end]
        except ValueError:
            return None



