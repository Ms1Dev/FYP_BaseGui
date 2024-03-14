import pyudev
import serial.tools.list_ports
import time
import serialDevice
import threading

class ConnectedDevice:
    def __init__(self, product_name, baudrate):
        self.product_name = product_name
        self.serialDevice = None
        self.baudrate = baudrate
        self.lock = threading.Lock()

    def isConnected(self):
        return self.serialDevice is not None
    
    def connect(self, port):
        if not self.isConnected():
            self.serialDevice = serialDevice.SerialDevice(port, self.baudrate)
            self.serialDevice.addConnectionFailCallback(self.connectionFailCallback)

    def getSerialDevice(self):
        return self.serialDevice
    
    def connectionFailCallback(self):
        self.serialDevice = None


def monitorPorts():
    while True:
        for connectedDevice in usbDevices:
            for port in serial.tools.list_ports.comports(include_links=True):
                if port.product is not None and port.product.startswith(connectedDevice.product_name):
                    connectedDevice.connect(port.device)
        hc12.connect("/dev/ttyS0")
        time.sleep(1)


antenna = ConnectedDevice("USB Serial", 9600)
gps = ConnectedDevice("CP2102 GPS Dongle", 9600)
barometric = ConnectedDevice("CP2102 Barometric Dongle", 9600)
hc12 = ConnectedDevice("HC12", 9600)
usbDevices = [
    antenna,
    gps,
    barometric
]
context = pyudev.Context()
monitorThread = threading.Thread(target=monitorPorts)
monitorThread.daemon = True
monitorThread.start()


