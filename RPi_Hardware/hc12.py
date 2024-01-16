import serial
import threading
import queue

class HC12:
    uart = serial.Serial(port="/dev/ttyS0", baudrate=9600, timeout=1)
    uart_lock = threading.Lock()

    def __init__(self):
        listen_thread = threading.Thread(target=self.listen, name="HC12_listen_thread")
        listen_thread.start()
        self.output_queue = queue.Queue()

    def listen(self):
        while True:
            with self.uart_lock:
                recv = self.uart.read_until(b'\n')
            if recv:
                self.output_queue.put(recv)

    def send(self, message):
        message = message.encode("UTF-8")
        with self.uart_lock:
            self.uart.write(message)

    def getQueue(self):
        return self.output_queue


hc12 = HC12()

q = hc12.getQueue()

while True:
    data = q.get()
    print(data)
