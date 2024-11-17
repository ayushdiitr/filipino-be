# views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .user_manager import UserManager
import json
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.serializers import serialize
import os
from django.conf import settings
from models.user import User


def user_to_dict(user):
    return {
        'id': str(user.user_id),
        'name': user.name,
        'email': user.email,
        'username': user.username,
        'gender': user.gender,
        'birth_date': user.birth_date,
        'bio': user.bio,
        'profile_picture': user.profile_picture,
        'is_active': user.is_active,
        'created_at': user.created_at,
        'last_login': user.last_login,
        # Add other fields as necessary, except sensitive ones like password and _id
    }

@csrf_exempt
def register_user(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')
        gender = data.get('gender')
        birth_date = data.get('birth_date')
        name= data.get('name')

        try:
            user = UserManager.create_user(
                email=email,
                username=username,
                password=password,
                gender=gender,
                birth_date=birth_date,
                name=name
            )
            return JsonResponse({'message': 'User registered successfully'}, status=201)
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


def get_all_users(request):
    users = UserManager.get_all_users()
    users_data = [
        user_to_dict(user)
        for user in users
    ]
    return JsonResponse({'message': 'Users fetched', 'data': users_data}, status=200)

@csrf_exempt
def upload_profile_picture(request, user_id):
    try:
        user = User.objects.get(user_id=user_id)
        
        if 'profile_picture' not in request.FILES:
            return JsonResponse({'error': 'No profile picture found'}, status=400)
        
        file = request.FILES['profile_picture']
        
        file_path = f'profile_pictures/{user_id}/{file.name}'
        full_path = os.path.join(settings.MEDIA_ROOT, file_path)
        
        path = default_storage.save(full_path, ContentFile(file.read()))
        
        user.profile_picture = f'{settings.MEDIA_URL}profile_pictures/{user_id}/{file.name}'
        user.save()
        
        return JsonResponse({'message': 'Profile picture uploaded successfully'}, status=200)
    
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)