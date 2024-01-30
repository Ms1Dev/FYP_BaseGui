import serial

class SerialDevice:
    def __init__(self, port, baudrate):
        self.uart = serial.Serial(port=port, baudrate=baudrate, timeout=10)
        self.output_queues = []
        self.connectionFailCallbacks = []

    def listen(self):
        try:
            recv = self.uart.read_until(b'\n')
        except Exception:
            #TODO: log the exception?
            for callback in self.connectionFailCallbacks:
                callback()
            return None
        return recv
 
    def send(self, message):
        message = message.encode("UTF-8")
        self.uart.write(message)

    def addQueue(self, queue):
        self.output_queues.append(queue)
    
    def addConnectionFailCallback(self, connectionFailCallback):
        self.connectionFailCallbacks.append(connectionFailCallback)

