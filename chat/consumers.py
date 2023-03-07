import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


# 每个请求进来，都建立自己的consumer实例
# 每个consumer都有自己唯一的channel_name
# 而所有consumer的channel_layer都是同一个
class ChatConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.room_group_name = None

    def connect(self):
        room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "chat_%s" % room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(self.room_group_name, self.channel_name)

        self.accept()

    def disconnect(self, code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(self.room_group_name, self.channel_name)

    # # Receive message from WebSocket
    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # 给group中每一个channel_name对应的consumer都发送一个event
        # 接收到event的consumer会执行event中的"type"对应的方法，并将event以参数传递
        async_to_sync(self.channel_layer.group_send)(self.room_group_name, {"type": "chat_message", "message": message})

    # Receive message from room group
    def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        self.send(text_data=json.dumps({"message": message}))
