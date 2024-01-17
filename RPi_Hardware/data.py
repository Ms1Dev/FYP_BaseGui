from pynmeagps import NMEAMessage, NMEAReader
import deviceManager
import time
import threading
import zmq
import json

class Data:
    pressureUnits = "mb"
    temperatureUnits = "°C"

    class Connection(threading.Thread):
        def __init__(self, connectedDevice : deviceManager.DeviceManager.ConnectedDevice, recvCallback):
            super().__init__()
            self.connectedDevice = connectedDevice
            self.device = None
            self.latest = None
            self.recvCallback = recvCallback
            self.daemon = True
            self.start()

        def run(self):
            self.monitorOutput()
            
        def connectionLostCallback(self):
            self.device = None

        def monitorOutput(self):
            while True:
                while self.device == None:
                    self.device = self.connectedDevice.getSerialDevice()
                    time.sleep(0.5)

                self.device.addConnectionFailCallback(self.connectionLostCallback)

                while self.device != None:
                    self.messageReceived(self.device.listen())

        def messageReceived(self, message):
            self.latest = message
            self.recvCallback(message)


    def __init__(self):
        self.deviceManager = deviceManager.DeviceManager()
        self.connections = {
            "hc12"      : Data.Connection(self.deviceManager.hc12, self.receiveHc12),
            "gps"       : Data.Connection(self.deviceManager.gps, self.receiveGps),
            "barometric": Data.Connection(self.deviceManager.barometric, self.receiveBaro),
            "antenna"   : Data.Connection(self.deviceManager.antenna, self.receiveAnt)
        }
        self.data = {}
        self.broadcast()


    def broadcast(self):
        zmqContext = zmq.Context()
        self.messageSender = zmqContext.socket(zmq.PUSH)
        self.messageSender.bind("tcp://127.0.0.1:5555")
        while True:
            dataJson = json.dumps(self.data)
            self.messageSender.send_json(dataJson)
            time.sleep(1)

    
    def receiveHc12(self, data):
        message : NMEAMessage = self.filterGpsSentence(data)
        if message is not None:
            self.data["mobile_gps_pos"] = self.formattedCoords(message)


    def receiveGps(self, data):
        message : NMEAMessage = self.filterGpsSentence(data)
        if message is not None:
            self.data["base_gps_pos"] = self.formattedCoords(message)
        

    def receiveBaro(self, data):
        if data is not None:
            data = data.decode("UTF-8", errors="ignore").strip()
            if data[0] == "T":
                self.data["base_temperature"] = data[2:] + self.temperatureUnits
            elif data[0] == "P":
                self.data["base_pressure"] = data[2:] + self.pressureUnits
        else:
            self.data.pop("base_pressure", None)
            self.data.pop("base_temperature", None)

    def receiveAnt(self, data):
        print(data)


    def formattedCoords(self, nmeamessage : NMEAMessage):
        return {"lat" : nmeamessage.lat, "lon" : nmeamessage.lon, "alt" : nmeamessage.alt}


    def filterGpsSentence(self, line : str, filter = "GPGGA"):
        try:
            parsed = NMEAReader.parse(line)
            identity = parsed.identity
        except Exception:
            return None
        else:
            if identity == filter:
                return parsed


data = Data()
