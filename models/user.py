# models.py
import uuid
import mongoengine as me
from django.utils import timezone
from .userProfile import Profile

class User(me.Document):
    user_id = me.UUIDField(default=uuid.uuid4, binary=False, unique=True)
    name = me.StringField(max_length=100, required=True)
    email = me.EmailField(required=True, unique=True)
    username = me.StringField(max_length=50, required=True, unique=True)
    gender = me.StringField(choices=['Male', 'Female', 'Other'], required=True)
    birth_date = me.DateField(required=True)
    password = me.StringField(required=True)
    bio = me.StringField(max_length=500, default='')
    photos = me.ListField(me.StringField(), default=[])  # Store URL or file path
    profile_picture = me.StringField()  # Store URL or file path
    is_active = me.BooleanField(default=True)
    is_admin = me.BooleanField(default=False)
    created_at = me.DateTimeField(default=timezone.now())
    last_login = me.DateTimeField(null=True)
    profile = me.ReferenceField("Profile", reverse_delete_rule=me.CASCADE, required=False)
    
        #profile attributes
    work = me.StringField(max_length=100, default='')
    education = me.StringField(max_length=100, default='')
    location = me.StringField(max_length=100, default='')
    looking_for = me.StringField(max_length=100, default='')
    interests = me.ListField(me.StringField(max_length=30), default=[])

    meta = {
        'collection': 'users',
        'ordering': ['-created_at'],
        'indexes': ['email', 'username'],
    }

    def __str__(self):
        return self.username
