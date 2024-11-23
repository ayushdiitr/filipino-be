from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/chat', consumers.ChatConsumer.as_asgi()),  # New conversation
    path('ws/chat/<str:conversation_id>', consumers.ChatConsumer.as_asgi()),  # Existing conversation
]
