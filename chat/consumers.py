import json
from channels.generic.websocket import AsyncWebsocketConsumer
from models import Conversation, Message
from models import User

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f"chat_{self.conversation_id}"
        
        # Join the room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        
    async def disconnect(self, code):
        # Leave the room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        sender_id = data.get('sender_id')
        content = data.get('content')
        recepient_id = data.get('recepient_id')
        
        sender = User.objects(user_id=sender_id).first()
        if not sender:
            await self.send(text_data=json.dumps({'error': 'Invalid sender'}))
            return
        
        # check if conversation exists
        conversation = Conversation.objects(id=self.conversation_id).first()
        if not conversation:
            # Initiate a new conversation if recepient_id is there
            recepient = User.objects(user_id=recepient_id).first()
            if not recepient:
                await self.send(text_data=json.dumps({'error': 'Invalid recepient'}))
                return
            
            conversation = Conversation(
                participants = [sender, recepient]
            )
            conversation.save()
            self.conversation_id = str(conversation.id)
        

        # Save message to the db
        message = Message(
            conversation = conversation,
            sender = sender,
            content = content
        )
        message.save()
        
        # Broadcast the message to the room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message_id': str(message.id),
                'sender_id': str(sender.id),
                'content': message.content,
                'timestamp': message.timestamp.isoformat()
            }
        )
        
    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event))
        