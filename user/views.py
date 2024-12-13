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
from models.user import User, Profile
from bson import ObjectId
import logging
from django.utils.text import get_valid_filename

logger = logging.getLogger(__name__)

def user_to_dict(user):
    return {
        'id': str(user.user_id),
        'name': user.name,
        'email': user.email,
        'username': user.username,
        'gender': user.gender,
        'birth_date': user.birth_date,
        'bio': user.bio,
        'photos': user.photos,
        'profile_picture': user.profile_picture,
        'is_active': user.is_active,
        'created_at': user.created_at,
        'last_login': user.last_login,
        'work': user.work,
        'education': user.education,
        'looking_for': user.looking_for,
        'interests': user.interests,
        'location': user.location,
        # Add other fields as necessary, except sensitive ones like password and _id
    }
    
def userProf_to_dict(user):
    return {
        'id': str(user.id),
        'liked_users': [str(u.id) for u in user.liked_users],  # Convert each user to string ID
        'disliked_users': [str(u.id) for u in user.disliked_users],
        'matched_users': [str(u.id) for u in user.matched_users],
        'work': user.work,
        'education': user.education,
        'looking_for': user.looking_for,
        'interests': user.interests,
        'location': user.location,
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
        logger.info("Starting upload_profile_picture function")

        # Ensure user exists
        user = User.objects.get(user_id=user_id)

        # Check if 'profile_picture' exists in request.FILES
        if 'profile_picture' not in request.FILES:
            logger.error("No profile picture found in request.FILES")
            return JsonResponse({'error': 'No profile picture found'}, status=400)
        
        # Get the file from request.FILES
        file = request.FILES['profile_picture']
        logger.info(f"Processing file: {file.name}")

        # Sanitize file name
        sanitized_name = get_valid_filename(file.name)
        logger.info(f"Sanitized file name: {sanitized_name}")

        # Construct relative path for file
        file_path = f'profile_pictures/{user_id}/{sanitized_name}'
        logger.info(f"Relative path for file: {file_path}")

        try:
            # Save the file using relative path
            saved_path = default_storage.save(file_path, ContentFile(file.read()))
            file_url = f'{settings.MEDIA_URL}{saved_path}'
            logger.info(f"File saved successfully at: {saved_path}")
        except Exception as e:
            logger.error(f"Error saving file {sanitized_name}: {str(e)}")
            return JsonResponse({'error': f'Error saving file: {str(e)}'}, status=500)

        # Save the file URL to user's profile
        user.profile_picture = file_url
        user.save()

        logger.info(f'Uploaded profile picture: {file_url}')
        return JsonResponse({'message': 'Profile picture uploaded successfully', 'data': {'profile_picture': file_url}}, status=200)

    except User.DoesNotExist:
        logger.error(f"User not found: {user_id}")
        return JsonResponse({'error': 'User not found'}, status=404)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

    

@csrf_exempt
def upload_pictures(request, user_id):
    try:
        logger.info("Starting upload_pictures function")

        # Ensure user exists
        user = User.objects.get(user_id=user_id)

        # Check request.FILES
        logger.info(f"request.FILES: {request.FILES}")
        files = request.FILES.getlist('profile_picture')
        logger.info(f"Files in 'profile_picture': {files}")

        if len(files) == 0:
            logger.error("No files provided in 'profile_picture'")
            return JsonResponse({'error': 'No profile pictures found in request.FILES'}, status=400)

        file_paths = []
        logger.info(f"settings.MEDIA_URL: {settings.MEDIA_URL}")

        for idx, file in enumerate(files):
            logger.info(f"Processing file: {file.name}")
            if idx >= 6:
                break

            # Sanitize file name
            sanitized_name = get_valid_filename(file.name)
            logger.info(f"Sanitized file name: {sanitized_name}")

            # Use only the relative path for storage
            relative_path = f'photos/{user_id}/{sanitized_name}'
            logger.info(f"Relative path for file: {relative_path}")

            try:
                # Save file using relative path
                saved_path = default_storage.save(relative_path, ContentFile(file.read()))
                file_paths.append(f'{settings.MEDIA_URL}{saved_path}')
                logger.info(f"File saved successfully at: {saved_path}")
            except Exception as e:
                logger.error(f"Error saving file {sanitized_name}: {str(e)}")

        if not file_paths:
            logger.error("No files were saved")
            return JsonResponse({'error': 'Failed to save files'}, status=500)

        # Save file paths to user's profile
        user.photos.extend(file_paths)
        user.save()

        logger.info(f'Uploaded file paths: {file_paths}')
        return JsonResponse({'message': 'Profile pictures uploaded successfully', 'data': {'profile_pictures': file_paths}}, status=200)

    except User.DoesNotExist:
        logger.error(f"User not found: {user_id}")
        return JsonResponse({'error': 'User not found'}, status=404)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

  
    
@csrf_exempt
def update_profile(request, user_id):
    try:
        user = User.objects.get(user_id=user_id)
        data = json.loads(request.body)
        
        # Update the user fields based on the request data
        allowed_fields = ['bio', 'work', 'education', 'gender', 'location', 'looking_for', 'interests', 'language']
        
        # Check for invalid fields
        invalid_fields = [key for key in data if key not in allowed_fields]
        if invalid_fields:
            return JsonResponse({'error': f"Invalid fields: {', '.join(invalid_fields)}"}, status=400)
         
        # Update the user fields based on the request data
        for key, value in data.items():
            if key == 'gender' and value not in ['Male', 'Female', 'Other']:
                return JsonResponse({'error': 'Invalid gender value'}, status=400)
            setattr(user, key, value)
        
        # Save the updated user
        user.save()
        return JsonResponse({'message': 'Profile updated successfully', 'data': user_to_dict(user)}, status=200)
    
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)