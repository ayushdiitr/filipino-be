from mongoengine import Document, StringField, ReferenceField, ListField, DateTimeField, CASCADE, BooleanField
from django.utils import timezone

class Conversation(Document):
    # Model for storing conversation details
    participants = ListField(ReferenceField('User') , required=True)
    created_at = DateTimeField(default=timezone.now)
    
    meta={
        'collection':'conversations',
        'indexes':['participants']
    }
    
    def __str__(self):
        participant_names = [str(user.id) for user in self.participants]
        return f"Conversation between {', '.join(participant_names)}"
    

class Message(Document):
    # Model for storing individual messages
    conversation = ReferenceField(Conversation, required=True, reverse_delete_rule=CASCADE)
    sender = ReferenceField('User', required=True)
    content = StringField(required=True)
    timestamp = DateTimeField(default=timezone.now)
    is_read = BooleanField(default=False)
    
    meta = {
        'collection': 'messages',
        'indexes': ['conversation']
    }
    
    def __str__(self):
        return f"Message from {self.sender.id} at {self.timestamp}"