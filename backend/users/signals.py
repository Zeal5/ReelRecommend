from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from rest_framework.authtoken.models import Token
from django.dispatch import receiver


User = get_user_model()
@receiver(post_save, sender=User)
def create_auth_token(sender, instance, created, **kwargs):
    print("Token is being created")
    if created:
        Token.objects.get_or_create(user=instance)  # generate token
