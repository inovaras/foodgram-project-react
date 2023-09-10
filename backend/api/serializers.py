from django.contrib.auth import get_user_model
from djoser import serializers as djoser_serializers
from rest_framework import serializers

User = get_user_model()


class UserSerializer(djoser_serializers.UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        cur_user = self.context['request'].user
        return cur_user.is_authenticated and obj.following.filter(user=cur_user).exists()

