import board  
import digitalio 
import keypad
import asyncio

class Button:
    hold_duration = .5


    def __init__(self, pin) -> None:
        self.pin = pin
        self.primary_action = None
        self.secondary_action = None
        self.block_action = False


    async def monitorKey(self):
        with keypad.Keys((self.pin,), value_when_pressed=False) as keys:
            while True:
                event = keys.events.get()
                if event:
                    if event.pressed:
                        self.pressed()
                    elif event.released:
                        await self.released()
                await asyncio.sleep(0)


    def pressed(self):
        self.hold_task = asyncio.ensure_future(self.hold())


    async def hold(self):
        await asyncio.sleep(self.hold_duration)
        self.block_action = True
        await self.secondaryAction()


    async def released(self):
        self.hold_task.cancel()
        if not self.block_action:
            await self.primaryAction()
        self.block_action = False


    def setPrimaryAction(self, action):
        self.primary_action = action


    def setSecondaryAction(self, action):
        self.secondary_action = action


    async def primaryAction(self):
        if (self.primary_action):
            self.primary_action()

    async def secondaryAction(self):
        if (self.secondary_action):
            self.secondary_action()
