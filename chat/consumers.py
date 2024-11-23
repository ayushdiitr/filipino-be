import json
from channels.generic.websocket import AsyncWebsocketConsumer
from models import Conversation, Message
from models import User
import hashlib

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs'].get('conversation_id')  # Optional
        if self.conversation_id:
            self.room_group_name = f"chat_{self.conversation_id}"
        else:
            # For new chats, use a temporary group name until a conversation is created
            hashed_channel_name = hashlib.md5(self.channel_name.encode('utf-8')).hexdigest()
            self.room_group_name = f"chat_temp_{hashed_channel_name}"        
        
        # Join the room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        
        self.send(text_data=json.dumps({'message': 'Connected'}))

    async def receive(self, text_data):
        data = json.loads(text_data)
        sender_id = data.get('sender_id')
        content = data.get('content')
        recepient_id = data.get('recepient_id')
        
        # Validate sender and recipient
        sender = User.objects(user_id=sender_id).first()
        recepient = User.objects(user_id=recepient_id).first() if recepient_id else None

        if not sender:
            await self.send(text_data=json.dumps({'error': 'Invalid sender'}))
            return

        if not self.conversation_id:
            # Create a new conversation dynamically if no conversation ID exists
            if not recepient:
                await self.send(text_data=json.dumps({'error': 'Invalid recepient'}))
                return
            
            conversation = Conversation(participants=[sender, recepient])
            conversation.save()
            self.conversation_id = str(conversation.id)
            self.room_group_name = f"chat_{self.conversation_id}"

            # Rejoin the correct room group with the new conversation ID
            await self.channel_layer.group_discard(
                f"chat_temp_{self.channel_name}",
                self.channel_name
            )
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

        # Save the message and broadcast
        message = Message(
            conversation=conversation,
            sender=sender,
            content=content
        )
        message.save()

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

        
   