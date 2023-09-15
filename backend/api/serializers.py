from django.contrib.auth import get_user_model
from djoser import serializers as djoser_serializers
from rest_framework import serializers
from recipes.models import Recipe, Tag, Ingredient, RecipeIngredient

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


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(source='ingredient.measurement_unit')
    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class RecipeSerializerRead(serializers.ModelSerializer):
    tags = TagSerializer(read_only=True, many=True)
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(read_only=True, many=True, source='recipeingredients')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id',
                  'tags',
                  'author',
                  'ingredients',
                  'is_favorited',
                  'is_in_shopping_cart',
                  'name',
                  'image',
                  'text',
                  'cooking_time'
                  )

    def get_is_favorited(self, recipe):
        cur_user = self.context['request'].user
        return cur_user.is_authenticated and recipe.favorited.filter(id=cur_user.id).exists()

    def get_is_in_shopping_cart(self, recipe):
        cur_user = self.context['request'].user
        return cur_user.is_authenticated and recipe.shopping_cart.filter(id=cur_user.id).exists()


class RecipeSerializerWrite(serializers.ModelSerializer):
    pass