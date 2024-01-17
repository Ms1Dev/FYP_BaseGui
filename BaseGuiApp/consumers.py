import json

from channels.generic.websocket import AsyncWebsocketConsumer
import zmq
import asyncio
import sys

class GuiConsumer(AsyncWebsocketConsumer):
    def __init__(self):
        super().__init__()
        zmqContext = zmq.Context()

        self.messageReceiver = zmqContext.socket(zmq.PULL)
        self.messageReceiver.connect("tcp://127.0.0.1:5555")

    async def connect(self):
        await self.accept()
        self.messagePollingTask = asyncio.create_task(self.pollMessages())

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        await self.send(text_data=json.dumps({"message": message + "eeffe"}))

    async def pollMessages(self):
        while True:
            data = self.messageReceiver.recv_string()
            await self.send(text_data=json.dumps({"message": data}))
            await asyncio.sleep(1)