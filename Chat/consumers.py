import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .serializers import MessageSerializer
from .models import Message,Chat
from rest_framework.renderers import JSONRenderer
from django.contrib.auth import get_user_model


class ChatConsumer(WebsocketConsumer):
    
    def new_message(self,data):
        message = data['message']
        username = data['username']
        roomname = data['roomname']
        chat = Chat.objects.get(roomname =roomname)
        user = get_user_model().objects.filter(username=username).first()
        message_object = Message.objects.create(author=user,content=message,related_chat =chat)
        message = self.message_serializer(message_object)
        message = eval(message)
        self.send_to_chat_message(message)
        
    def fetch_message(self,data):
        roomname = data['roomname']
        query = Message.last_message(self, roomname)
        messge_json = self.message_serializer(query)
        content ={
            "message":eval(messge_json),
            "command":"fetch_message"
        } 
        self.chat_message(content)
     
    def message_serializer(self,query_set):
        if query_set.__class__.__name__ =='QuerySet':
            bool_ = True
        else:
            bool_ =False
        serialized = MessageSerializer(query_set,many=bool_)
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
        # message = text_data_json.get("message",None)
        # username = text_data_json.get("username",None)
        commad = text_data_json["command"]
        self.commends[commad](self,text_data_json)

    def send_to_chat_message(self,message):
        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"type": "chat_message",
                                   "content": message['content'],
                                   'command':'new_message',
                                    '__str__': message['__str__']
            }
                                
        )

    # Receive message from room group
    def chat_message(self, event):
        
        """event = {
            "type": "chat_message",
            "message": message
            "command": fetch or new message
        }
        """
        # message = event["message"]
        # Send message to WebSocket
        self.send(text_data=json.dumps(event))