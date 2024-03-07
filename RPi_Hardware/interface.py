import board
from Interface.button import Button
from Interface.screen import Screen
from Interface.task import Task
import asyncio
import threading
import digitalio
import oled

PIN = board.D26
led = digitalio.DigitalInOut(PIN)
led.direction = digitalio.Direction.OUTPUT
led.value = True


screens = Screen("Main menu",[
    Screen("WiFi mode", [
        Task("Access Point"),
        Task("Client")
    ]),
    Task("Test1"),
    Task("Test2"),
    Task("Test3"),
    Task("Test4")
])


class Interface:

    def __init__(self) -> None:
        self.root_screen = screens
        self.leftButton = Button(board.D5)
        self.midButton = Button(board.D6)
        self.rightButton = Button(board.D16)
        self.leftButton.setPrimaryAction(self.root_screen.leftBtnPressed)
        self.midButton.setPrimaryAction(self.root_screen.middleBtnPressed)
        self.rightButton.setPrimaryAction(self.root_screen.rightBtnPressed)
        self.leftButton.setSecondaryAction(self.root_screen.leftBtnHeld)
        self.midButton.setSecondaryAction(self.root_screen.middleBtnHeld)
        self.rightButton.setSecondaryAction(self.root_screen.rightBtnHeld)
        self.begin()


    async def monitor(self):
        lb_task = asyncio.create_task(self.leftButton.monitorKey())
        mb_task = asyncio.create_task(self.midButton.monitorKey())
        rb_task = asyncio.create_task(self.rightButton.monitorKey())
        screen_task = asyncio.create_task(self.screenUpdate())
        await asyncio.gather(lb_task,mb_task,rb_task, screen_task)

    async def screenUpdate(self):
        while True:
            oled.rows = self.root_screen.getRows()
            oled.refresh()
            await asyncio.sleep(0.1)

    def begin(self):
        asyncio.run(self.monitor())

# threading.Thread(target=begin).start()

interface = Interface()

interface.begin()