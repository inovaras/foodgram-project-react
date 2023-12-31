from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Follow, User

admin.site.register(User, UserAdmin)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'following')
    list_filter = ('user', 'following')
    empty_value_display = '-пусто-'
