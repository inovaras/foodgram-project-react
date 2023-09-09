from django.contrib.auth import get_user_model
from djoser import serializers as djoser_serializers


User = get_user_model()


class UserCreateSerializer(djoser_serializers.UserCreateSerializer):
    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name')


class UserSerializer(djoser_serializers.UserSerializer):
    pass