# urls.py (in your Django app folder)
from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('register/', views.register_user, name='register_user'),
    path('getAllUsers/', views.get_all_users, name='get_all_users'),
    path('uploadProfilePicture/<str:user_id>/', views.upload_profile_picture, name='upload_profile_picture'),
    path('uploadPictures/<str:user_id>/', views.upload_pictures, name='upload_pictures'),
    path('updateProfile/<str:user_id>/', views.update_profile, name='update_profile'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
