import json

from channels.generic.websocket import AsyncWebsocketConsumer
import zmq
import asyncio
import sys

class GuiConsumer(AsyncWebsocketConsumer):
    def __init__(self):
        super().__init__()
        zmqContext = zmq.Context()

        self.receiver = zmqContext.socket(zmq.PULL)
        self.receiver.connect("tcp://127.0.0.1:5555")

        self.sender = zmqContext.socket(zmq.PUSH)
        self.sender.connect("tcp://127.0.0.1:5556")

    async def connect(self):
        await self.accept()
        self.messagePollingTask = asyncio.create_task(self.pollMessages())

    async def disconnect(self, close_code):
        pass


    async def receive(self, text_data):
        data_json = json.loads(text_data)
        self.sender.send_json(data_json)
        

    async def pollMessages(self):
        while True:
            data = self.receiver.recv_json()
            await self.send(data)
            await asyncio.sleep(1)