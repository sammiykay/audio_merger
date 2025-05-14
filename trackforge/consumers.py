# consumers.py (in trackforge/)
from channels.generic.websocket import AsyncWebsocketConsumer
import json

class StatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.room_group_name = f"status_{self.session_id}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def send_status(self, event):
        await self.send(text_data=json.dumps(event["message"]))

