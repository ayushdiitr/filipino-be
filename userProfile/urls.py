from django.urls import path 
from .views import swipe_user, get_profile_data

urlpatterns = [
    path('swipe/<str:user_id>/<str:action>/', swipe_user, name='swipe_user'),
    path('profileDetails/<str:user_id>/', get_profile_data, name='get_profile_details')
]