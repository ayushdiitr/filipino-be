from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from models import Conversation, Message, User

@require_http_methods(["POST"])
def create_conversation(request):
    # Create new conversation between two users.
    data = request.json
    user1_id = data.get('user1_id')
    user2_id = data.get('user2_id')
    
    if not user1_id or not user2_id:
        return JsonResponse({'error': 'user1_id and user2_id are required.'}, status=400)
    
    user1 = User.objects(id = user1_id).first()
    user2 = User.objects(id = user2_id).first()
    
    if not user1 or not user2:
        return JsonResponse({'error': 'User not found.'}, status=404)
    
    conversation = Conversation(participants=[user1, user2])
    conversation.save()
    
    return JsonResponse({
        'message': 'Conversation created successfully.',
        'data': {'conversation_id': str(conversation.id)},
        'messageStatus': 'Success'
    }, status = 201)
    
    