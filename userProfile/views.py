from django.http import JsonResponse
from models.user import User
from models.userProfile import Profile
from bson import ObjectId


# Create your views here.
def swipe_user(request, user_id, action):
    try:
        # Replace with the authenticated user logic if applicable
        user = User.objects.get(id=ObjectId('673911f75e57323b449d4385'))
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
