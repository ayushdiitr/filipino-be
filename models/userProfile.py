from mongoengine import Document, StringField, ReferenceField, ListField, DateTimeField
from django.utils import timezone
# Create your models here.

class Profile(Document):
    user = ReferenceField('User', required=True, unique=True)
    liked_users =ListField(ReferenceField('User'))
    disliked_users = ListField(ReferenceField('User'))
    matched_users = ListField(ReferenceField('User'))
    last_swipe_date = DateTimeField(default=timezone.now)
    
    meta = {
        'collection':'profiles',
        'indexes':['user'],
    }
    
    def like_user(self, liked_user):
        if liked_user not in self.liked_users and liked_user not in self.disliked_users:
            self.liked_users.append(liked_user)
            self.save()
            
    def dislike_user(self, disliked_user):
        if disliked_user not in self.liked_users and disliked_user not in self.disliked_users:
            self.disliked_users.append(disliked_user)
            self.save()
            
    def match_user(self, matched_user):
        if matched_user in self.liked_users and self.user in matched_user.profile.liked_users:
            self.matched_users.append(matched_user)
            matched_user.profile.matched_users.append(self)
            self.save()
            matched_user.profile.save()
            return True
        return False