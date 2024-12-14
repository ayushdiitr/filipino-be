from django.http import JsonResponse
from models.user import User
from models.userProfile import Profile
from bson import ObjectId
from django.views.decorators.csrf import csrf_exempt
import logging
from user.views import user_to_dict

logger = logging.getLogger(__name__)



def profile_to_dict(profile, liked_users):
    return {
        "user": user_to_dict(profile.user),
        "liked_users": [user_to_dict(user) for user in liked_users],
        "work": profile.work,
        "education": profile.education,
        "location": profile.location,
        "looking_for": profile.looking_for,
        "interests": profile.interests
    }

# Create your views here.
def swipe_user(request, user_id, action):
    try:
        # Replace with the authenticated user logic if applicable
        user = User.objects.get(id=ObjectId('6741087d52587b9769e8da6d'))
        target_user = User.objects.get(id=ObjectId(user_id))

        # Ensure both users have profiles
        user_profile = Profile.objects(user=user).first()
        if not user_profile:
            user_profile = Profile(user=user)
            user_profile.save()

        target_profile = Profile.objects(user=target_user).first()
        if not target_profile:
            target_profile = Profile(user=target_user)
            target_profile.save()

        if action == 'like':
            user_profile.like_user(target_user)
            # Check if there is a match
            if target_user in user_profile.liked_users and user in target_profile.liked_users:
                # Add to matched users if both liked each other
                user_profile.match_user(target_user)
                return JsonResponse({'message': 'Matched!', "data": [user_profile.user.username, target_user.username]}, status=200)
            return JsonResponse({'message': 'Liked!', "data": target_user.username}, status=200)

        elif action == 'dislike':
            user_profile.dislike_user(target_user)
            return JsonResponse({'message': 'Disliked!', "data": target_user.username}, status=200)

        return JsonResponse({'error': 'Invalid action'}, status=400)

    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except Profile.DoesNotExist:
        return JsonResponse({'error': 'Profile not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def get_profile_data(request, user_id):
    try:
        logger.info("Starting get_profile_data function")

        user = User.objects.get(user_id=user_id)

        profile = Profile.objects.get(user=user)
        liked_users = User.objects.filter(user_id__in=[liked_user.user_id for liked_user in profile.liked_users])

        profile_data = profile_to_dict(profile, liked_users)

        return JsonResponse({'message':'Profile fetched', 'data':profile_data}, status=200, safe=False)

    except User.DoesNotExist: 
        logger.error("User with user_id %s does not exist", user_id)
        return JsonResponse({'error': 'User not found'}, status=404)

    except Profile.DoesNotExist:
        logger.error("Profile for user with user_id %s does not exist", user_id)
        return JsonResponse({'error': 'Profile not found'}, status=404)

    except Exception as e:
        logger.error("An error occurred: %s", str(e))
        return JsonResponse({'error': str(e)}, status=500)
