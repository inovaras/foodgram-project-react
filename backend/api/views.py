from django.shortcuts import render
from djoser import views


class UserViewSet(views.UserViewSet):
    lookup_field = 'email'
    search_fields = ('email',)
    http_method_names = ['get', 'post', 'patch', 'delete']



