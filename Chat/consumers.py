import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


class ChatConsumer(WebsocketConsumer):
    
    def new_message(self,message):
        print(message)
    def fetch_message(self):
         pass
    
    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"] # info connection save in scope like request in api 
        self.room_group_name = f"chat_{self.room_name}"

        # Join room group --> consumer -> channel_name --> add to group o channel_layer
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name  # channel name uniqe generate with consumer -->user 
        )

        self.accept()
        
    commends ={
        "new_message":new_message,
        "fetch_message":fetch_message
    }

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        commad = text_data_json["commad"]
        self.commends[commad](self,message)


        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"type": "chat_message", "message": message}
        )

    # Receive message from room group
    def chat_message(self, event):
        
        """event = {
            "type": "chat_message",
            "message": message
        }
        """
        message = event["message"]

        # Send message to WebSocket
        self.send(text_data=json.dumps({"message": message}))