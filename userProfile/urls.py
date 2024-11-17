from django.urls import path 
from .views import swipe_user

urlpatterns = [
    path('swipe/<str:user_id>/<str:action>/', swipe_user, name='swipe_user')
]