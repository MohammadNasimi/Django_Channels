import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .serializers import MessageSerializer
from .models import Message
from rest_framework.renderers import JSONRenderer

class ChatConsumer(WebsocketConsumer):
    
    def new_message(self,message):
        print(message)
    def fetch_message(self,data):
        query = Message.last_message(self)
        messge_json = self.message_serializer(query)
        content ={
            "message":eval(messge_json)
        } 
        self.chat_message(content)
     
    def message_serializer(self,query_set):
        serialized = MessageSerializer(query_set,many=True)
        content = JSONRenderer().render(serialized.data)
        return content
    
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
        message = text_data_json.get("message",None)
        commad = text_data_json["commad"]
        self.commends[commad](self,message)

    def send_to_chat_message(self,message):
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