# user_manager.py
from models.user import User
from django.contrib.auth.hashers import make_password

class UserManager:
    @staticmethod
    def create_user(email, username, password, **extra_fields):
        if User.objects(email=email).first():
            raise ValueError('User with this email already exists.')
        hashed_password = make_password(password)
        user = User(
            email=email,
            username=username,
            password=hashed_password,
            **extra_fields
        )
        user.save()
        return user

    @staticmethod
    def authenticate(email, password):
        user = User.objects(email=email).first()
        if user and user.check_password(password):
            return user
        return None
    
    @staticmethod
    def get_all_users():
        return User.objects.all()
