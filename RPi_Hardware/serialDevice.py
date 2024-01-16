import serial
import threading
import queue

class SerialDevice:
    def __init__(self, port, baudrate):
        self.uart = serial.Serial(port=port, baudrate=baudrate, timeout=5)
        self.uart_lock = threading.Lock()
        listen_thread = threading.Thread(target=self.listen)
        listen_thread.daemon = True
        listen_thread.start()
        self.output_queue = queue.Queue()

    def listen(self):
        while True:
            with self.uart_lock:
                try:
                    recv = self.uart.read_until(b'\n')
                except serial.serialutil.SerialException:
                    if self.connectionFailCallback:
                        self.connectionFailCallback()
                    break
            if recv:
                self.output_queue.put(recv)

    def send(self, message):
        message = message.encode("UTF-8")
        with self.uart_lock:
            self.uart.write(message)

    def getQueue(self):
        return self.output_queue
    
    def setConnectionFailCallback(self, connectionFailCallback):
        self.connectionFailCallback = connectionFailCallback
