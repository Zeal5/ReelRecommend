from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "username", "password"]

    def create(self, validated_data):
        paswd = validated_data.pop("password")
        email = validated_data.pop("email")
        user = User.objects.create_user(
            email=email,
            password=paswd,
            **validated_data,
        )
        return user
