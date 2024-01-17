import pyudev
import serial.tools.list_ports
import time
import serialDevice
import threading

class DeviceManager:
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
            
    def __init__(self):
        self.antenna = DeviceManager.ConnectedDevice("USB Serial", 9600)
        self.gps = DeviceManager.ConnectedDevice("u-blox 7", 115200)
        self.barometric = DeviceManager.ConnectedDevice("CP2102", 9600)
        self.hc12 = DeviceManager.ConnectedDevice("HC12", 9600)
        self.usbDevices = [
            self.antenna,
            self.gps,
            self.barometric
        ]
        self.context = pyudev.Context()
        monitorThread = threading.Thread(target=self.monitorPorts)
        monitorThread.daemon = True
        monitorThread.start()

    def monitorPorts(self):
        while True:
            for connectedDevice in self.usbDevices:
                for port in serial.tools.list_ports.comports(include_links=True):
                    if port.product is not None and port.product.startswith(connectedDevice.product_name):
                        connectedDevice.connect(port.device)
            self.hc12.connect("/dev/ttyS0")
            time.sleep(1)
