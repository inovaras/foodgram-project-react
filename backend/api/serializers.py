import base64

from django.core.files.base import ContentFile
from djoser import serializers as djoser_serializers
from rest_framework import serializers

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from users.models import User


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class UserSerializer(djoser_serializers.UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        cur_user = self.context['request'].user
        return (
            cur_user.is_authenticated
            and obj.following.filter(user=cur_user).exists()
        )


class FollowerSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

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


class RecipeIngredientSerializerRead(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class RecipeSerializerRead(serializers.ModelSerializer):
    tags = TagSerializer(read_only=True, many=True)
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializerRead(
        read_only=True, many=True, source='recipeingredients'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, recipe):
        cur_user = self.context['request'].user
        return (
            cur_user.is_authenticated
            and recipe.favorited.filter(id=cur_user.id).exists()
        )

    def get_is_in_shopping_cart(self, recipe):
        cur_user = self.context['request'].user
        return (
            cur_user.is_authenticated
            and recipe.shopping_cart.filter(id=cur_user.id).exists()
        )


class RecipeIngredientSerializerWrite(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeSerializerWrite(serializers.ModelSerializer):
    image = Base64ImageField()
    ingredients = RecipeIngredientSerializerWrite(many=True)

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError(
                'Нельзя создать рецепт без ингредиентов'
            )

        if len(set(ingredient['id'] for ingredient in ingredients)) != len(
            ingredients
        ):
            raise serializers.ValidationError('Нельзя дублировать ингредиенты')
        return ingredients

    def make_ingredients(self, recipe, ingredients):
        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount'],
            )
            for ingredient in ingredients
        )

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.make_ingredients(recipe, ingredients)
        return recipe

    def update(self, recipe, validated_data):
        ingredients = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags', None)
        super().update(recipe, validated_data)
        if tags:
            recipe.tags.set(tags)
        if ingredients:
            recipe.ingredients.clear()
            self.make_ingredients(recipe, ingredients)
        return recipe

    def to_representation(self, instance):
        return RecipeSerializerRead(instance, context=self.context).data
