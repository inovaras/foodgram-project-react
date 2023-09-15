from django.contrib.auth import get_user_model
from djoser import views
from rest_framework.decorators import action
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny

from users.models import Follow
from recipes.models import Tag, Ingredient, Recipe
from .serializers import FollowerSerializer, TagSerializer, IngredientSerializer, RecipeSerializerRead, RecipeSerializerWrite, RecipeMinified
from .filters import IngredientFilter, RecipeFilter
from .permissions import IsAuthorOrAdminOrReadOnly


User = get_user_model()


class UserViewSet(views.UserViewSet):
    http_method_names = ['get', 'post', 'delete']
    @action(
        detail=False,
        serializer_class=FollowerSerializer
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(following__user=self.request.user)
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['post'],
        serializer_class=FollowerSerializer
    )
    def subscribe(self, request, id):
        following = get_object_or_404(User, id=id)
        serializer = self.get_serializer(following)
        if following.following.filter(user=request.user).exists():
            raise ValidationError('Такая подписка уже существует')
        if request.user == following:
            raise ValidationError('Нельзя подписаться на самого себя')
        Follow.objects.create(
            following=following,
            user=request.user
        )
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    @subscribe.mapping.delete
    def unsubscribe(self, request, id):
        following = get_object_or_404(User, id=id)
        follow = following.following.filter(user=request.user)
        if not follow.exists():
            raise ValidationError('Такой подписки не существует')
        follow.delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH'):
            return RecipeSerializerWrite
        return RecipeSerializerRead

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['post'],
        serializer_class=RecipeMinified
    )
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        if recipe.shopping_cart.filter(id=request.user.id).exists():
            raise ValidationError('Рецепт уже добавлен в список покупок')
        recipe.shopping_cart.add(request.user)
        serializer = self.serializer_class(recipe)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    @shopping_cart.mapping.delete
    def delete_from_shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        if not recipe.shopping_cart.filter(id=request.user.id).exists():
            raise ValidationError('Рецепта нет в списке покупок')
        recipe.shopping_cart.remove(request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post'],
        serializer_class=RecipeMinified
    )
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        if recipe.favorited.filter(id=request.user.id).exists():
            raise ValidationError('Рецепт уже добавлен в избранное')
        recipe.favorited.add(request.user)
        serializer = self.serializer_class(recipe)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    @favorite.mapping.delete
    def delete_from_favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        if not recipe.favorited.filter(id=request.user.id).exists():
            raise ValidationError('Рецепта нет в избранном')
        recipe.favorited.remove(request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)
