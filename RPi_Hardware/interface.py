import board
from Interface.button import Button
from Interface.submenu import Submenu
from Interface.process import Process
from Interface.info import Info, LiveInfo
from Interface import tasks
import asyncio
import digitalio
import oled


# submenus = Submenu("Main menu",[
#     Submenu("WiFi mode", [
#         Process("Station", tasks.wifiClientMode),
#         Process("Access Point", tasks.wifiAPMode)
#     ]),
#     Info("Connection details", tasks.getConnectionInfo),
#     Process("Calibrate height", ctrl.control.calibrateVerticalDistance),
#     LiveInfo("Base Location", tasks.base_pos),
#     LiveInfo("Antenna Pos", tasks.antenna_pos)
# ])


class Interface:

    def __init__(self, control) -> None:
        self.control = control
        PIN = board.D26
        led = digitalio.DigitalInOut(PIN)
        led.direction = digitalio.Direction.OUTPUT
        led.value = True

        self.root_submenu = Submenu("Main menu",[
            Submenu("WiFi mode", [
                Process("Station", tasks.wifiClientMode),
                Process("Access Point", tasks.wifiAPMode)
            ]),
            Info("Connection details", tasks.getConnectionInfo),
            Submenu("Commands",[
                Process("Start logging", self.control.beginLoggingCoordinates),
                Process("Stop logging", self.control.stopLoggingCoordinates),
                Process("Calibrate height", self.control.calibrateVerticalDistance),
                Process("Home antenna", self.control.homeAntenna)
            ]),
            Info("Data log files", tasks.getLogFileList),
            Submenu("Compass", [
                Process("On", self.control.absoluteBearing),
                Process("Off", self.control.relativeBearing)
            ]),
            LiveInfo("Base Location", tasks.base_pos),
            LiveInfo("Antenna Pos", tasks.antenna_pos)
        ])

        self.leftButton = Button(board.D5)
        self.midButton = Button(board.D6)
        self.rightButton = Button(board.D16)
        self.leftButton.setPrimaryAction(self.root_submenu.leftBtnPressed)
        self.midButton.setPrimaryAction(self.root_submenu.middleBtnPressed)
        self.rightButton.setPrimaryAction(self.root_submenu.rightBtnPressed)
        self.leftButton.setSecondaryAction(self.root_submenu.leftBtnHeld)
        self.midButton.setSecondaryAction(self.root_submenu.middleBtnHeld)
        self.rightButton.setSecondaryAction(self.root_submenu.rightBtnHeld)


    async def monitor(self):
        lb_task = asyncio.create_task(self.leftButton.monitorKey())
        mb_task = asyncio.create_task(self.midButton.monitorKey())
        rb_task = asyncio.create_task(self.rightButton.monitorKey())
        submenu_task = asyncio.create_task(self.submenuUpdate())
        await asyncio.gather(lb_task,mb_task,rb_task,submenu_task)

    async def submenuUpdate(self):
        while True:
            oled.rows = self.root_submenu.getRows()
            oled.refresh()
            await asyncio.sleep(0.1)

    def begin(self):
        asyncio.run(self.monitor())