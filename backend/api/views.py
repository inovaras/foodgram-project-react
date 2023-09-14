from django.shortcuts import render
from django.contrib.auth import get_user_model
from djoser import views
from rest_framework.decorators import action
from rest_framework import viewsets
from .serializers import FollowerSerializer
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError

from users.models import Follow


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
            raise ValidationError("Такая подписка уже существует")
        if request.user == following:
            raise ValidationError("Нельзя подписаться на самого себя")
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
            raise ValidationError("Такой подписки не существует")
        follow.delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )

class TagViewSet(viewsets.ModelViewSet):
    pass
