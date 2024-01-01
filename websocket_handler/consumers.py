# consumers.py in your Django app

from channels.generic.websocket import AsyncWebsocketConsumer

import json
import asyncio

from .models import Profile

online_users = set()

class OnlineConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_authenticated:
            await self.accept()
            online_users.add(self.user.username)
            # Handle user online status here

    async def disconnect(self, close_code):

        await asyncio.sleep(30)

        if not self.user.username in online_users:
            online_users.discard(self.user.username)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        # Handle received data here
