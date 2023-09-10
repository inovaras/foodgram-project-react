from django.shortcuts import render
from djoser import views


class UserViewSet(views.UserViewSet):
    http_method_names = ['get', 'post']



