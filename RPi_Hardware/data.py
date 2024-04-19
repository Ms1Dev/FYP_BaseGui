from pynmeagps import NMEAMessage, NMEAReader, nmeahelpers
import deviceManager
import time
import threading
import zmq
import json
from typing import Tuple, Any


class Data:
    """
        This object collects data from the various serial devices and then broadcasts it over TCP.
        Some data is passed directly to the Ctrl class.
    """

    pressureUnits = "mb"
    temperatureUnits = "°C"
    mobileNmeaSentenceType = "GNGGA"
    baseNmeaSentenceType = "GNGGA"
    compass_offset = -30

    class Connection(threading.Thread):
        """
            Connection to a serial device that listens for new data.
        """
        
        def __init__(self, connectedDevice : deviceManager.ConnectedDevice, recvCallback):
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


    def __init__(self, ctrlDataQueue = None, ctrlPointsOfInterest = []):
        zmqContext = zmq.Context()
        self.messageSender = zmqContext.socket(zmq.PUB)
        self.messageSender.bind("tcp://127.0.0.1:5557")
        self.messageSender.set_hwm(10000)

        self.connections = {
            "hc12"      : Data.Connection(deviceManager.hc12, self.receiveHc12),
            "gps"       : Data.Connection(deviceManager.gps, self.receiveGps),
            "barometric": Data.Connection(deviceManager.barometric, self.receiveBaro),
            "antenna"   : Data.Connection(deviceManager.antenna, self.receiveAnt),
            "compass"   : Data.Connection(deviceManager.compass, self.receiveCompass)
        }
        self.data = {}
        self.prevData = {}
        self.broadcastTimings = {}
        self.ctrlDataQueue = ctrlDataQueue
        self.ctrlPointsOfInterest = ctrlPointsOfInterest
        self.liveUpdates = [
            "antenna_azimuth",
            "antenna_elevation",
            "ping"
        ]
        

    def testRecv(self):
        while True:
            print(self.receiver.recv_json())
    

    def broadcast(self, label, value, repeat = False):
        min_time = 0.5
        if label in self.liveUpdates:
            min_time = 0
        if repeat:
            min_time = 1
        currentTime = time.time()
        lastBroadcast = self.broadcastTimings.get(label)
        if lastBroadcast:
            if currentTime - lastBroadcast > min_time:
                self.broadcastTimings[label] = currentTime
                try:
                    dataJson = json.dumps({label : value})
                    self.messageSender.send_json(dataJson)
                except Exception as e:
                    print({label : value}, e)
        else:
            self.broadcastTimings[label] = currentTime
    
    
    def receiveHc12(self, data):
        data = data.replace(b'\x00', b'')
        dataStr = data.decode("UTF-8", errors="ignore").strip()
        try:
            if dataStr[0] == "␆":
                self.forwardDataToCtrl(("ping",dataStr[1:4]))
        except:
            pass
        dataLabel = dataStr[:2]
        if dataLabel == "P=":
            value = dataStr[2:]
            self.addToData("mobile_pressure", value + self.pressureUnits)
        elif dataLabel == "T=":
            value = dataStr[2:]
            self.addToData("mobile_temperature", value + self.temperatureUnits)
        elif dataLabel == "G=":
            try:
                value = dataStr[2:]
                value = value.split(",")
                self.addToData("mobile_gps_pos", {"lat": float(value[0]), "lon": float(value[1])})
            except Exception as e:
                print("Failed to convert mobile GPS pos - ", e)


    def receiveGps(self, data):
        message : NMEAMessage = self.filterGpsSentence(data, self.baseNmeaSentenceType)
        if message is not None:
            self.addToData("base_gps_pos", self.formattedCoords(message))
        

    def receiveBaro(self, data):
        if len(data) > 1:
            data = data.decode("UTF-8", errors="ignore").strip()
            if data[0] == "T":
                self.addToData("base_temperature", data[2:] + self.temperatureUnits)
            elif data[0] == "P":
                self.addToData("base_pressure", data[2:] + self.pressureUnits)


    def receiveAnt(self, data):
        try:
            data = data.decode("UTF-8", errors="ignore").strip()
            if data[:3] == "AZ=":
                self.addToData("antenna_azimuth", data[3:])
            elif data[:3] == "EL=":
                self.addToData("antenna_elevation", data[3:])
        except:
            pass


    def receiveCompass(self, data):
        try:
            data = data.decode("UTF-8", errors="ignore").strip()
            d = data.split(",")
            if d[0][:1] == "C":
                self.addToData("compass_calibration", (float(d[0][1:]), 1))
            elif d[0][:1] == "V":
                 self.addToData("compass_validation", (float(d[0][1:]), float(d[1])))
            else:
                reading = float(d[1]) + self.compass_offset
                self.addToData("compass_bearing", (float(d[0]), reading))
        except:
            pass
    

    def addToData(self, label, value):
        repeat = self.prevData.get(label) == value
        self.broadcast(label,value,repeat)
        self.prevData[label] = value
        if label in self.ctrlPointsOfInterest:
            self.forwardDataToCtrl((label,value))



    def forwardDataToCtrl(self, data : Tuple[str,Any]):
        if self.ctrlDataQueue is not None:
            self.ctrlDataQueue.put(data)
        

    def formattedCoords(self, nmeamessage : NMEAMessage):
        return {"lat" : nmeamessage.lat, "lon" : nmeamessage.lon, "alt" : nmeamessage.alt}


    def filterGpsSentence(self, line : str, filter):
        try:
            nmeaMessage = NMEAReader.parse(line)
            identity = nmeaMessage.identity
        except Exception:
            return None
        else:          
            if identity == filter and nmeaMessage.lat is not None and nmeaMessage.lon is not None:
                return nmeaMessage
