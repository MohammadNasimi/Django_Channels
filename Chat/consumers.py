import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"] # info connection save in scope like request in api 
        self.room_group_name = f"chat_{self.room_name}"

        # Join room group --> consumer -> channel_name --> add to group o channel_layer
        await self.channel_layer.group_add(
            self.room_group_name, self.channel_name  # channel name uniqe generate with consumer -->user 
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name, self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat_message", "message": message}
        )

    # Receive message from room group
    async def chat_message(self, event):
        
        """event = {
            "type": "chat_message",
            "message": message
        }
        """
        message = event["message"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message}))