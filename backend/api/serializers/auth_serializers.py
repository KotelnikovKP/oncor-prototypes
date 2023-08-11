from django.contrib.auth.models import User
from rest_framework import serializers

from api.serializers.serializers import BaseResponseSerializer


class UserSerializer(serializers.ModelSerializer):
    """
        Standard user schema (for all responses)
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', )


class UserRegisterSerializer(serializers.ModelSerializer):
    """
        User registration schema

        1. Fields validation
        2. Check equalization of passwords
    """
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("username", "password", "password2", )
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        username = validated_data["username"]
        password = validated_data["password"]
        password2 = validated_data["password2"]
        if password != password2:
            raise serializers.ValidationError({"password": "Passwords aren't equal"})
        user = User(username=username)
        user.set_password(password)
        user.save()
        return user


class UserCreateSerializer(BaseResponseSerializer):
    """
        User create response schema
    """
    result = UserSerializer(many=False)


class UserDetailsSerializer(serializers.Serializer):
    """
        User retrieve schema
    """
    user = UserSerializer(many=False)


