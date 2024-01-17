import serial
import threading

class SerialDevice:
    def __init__(self, port, baudrate):
        print(port)
        self.uart = serial.Serial(port=port, baudrate=baudrate, timeout=10)
        self.uart_lock = threading.Lock()
        listen_thread = threading.Thread(target=self.listen)
        listen_thread.start()
        self.output_queues = []
        self.connectionFailCallbacks = []

    def listen(self):
        while True:
            with self.uart_lock:
                try:
                    recv = self.uart.read_all()
                except serial.serialutil.SerialException:
                    for callback in self.connectionFailCallbacks:
                        callback()
                    break
            if recv:
                print(recv.decode("UTF-8", errors="ignore"))
                for queue in self.output_queues:
                    queue.put(recv)
                    

    def send(self, message):
        message = message.encode("UTF-8")
        with self.uart_lock:
            self.uart.write(message)

    def addQueue(self, queue):
        self.output_queues.append(queue)
    
    def addConnectionFailCallback(self, connectionFailCallback):
        self.connectionFailCallbacks.append(connectionFailCallback)


# sd = SerialDevice("/dev/ttyACM0", 115200)