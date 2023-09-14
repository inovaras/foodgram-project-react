from django.contrib.auth import get_user_model
from djoser import serializers as djoser_serializers
from rest_framework import serializers
from recipes.models import Recipe

User = get_user_model()


class UserSerializer(djoser_serializers.UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        cur_user = self.context['request'].user
        return cur_user.is_authenticated and obj.following.filter(user=cur_user).exists()


class FollowerSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'is_subscribed', 'recipes', 'recipes_count')

    def get_recipes(self, obj):
        queryset = obj.recipes.all()
        request = self.context['request']
        recipes_limit = int(request.query_params.get('recipes_limit', 0))
        if recipes_limit > 0:
            queryset = queryset[:recipes_limit]
        return RecipeMinified(queryset, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class RecipeMinified(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
