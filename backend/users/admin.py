from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Follow

admin.site.register(User, UserAdmin)


class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'following')
    list_filter = ('user', 'following')
    empty_value_display = '-пусто-'


admin.site.register(Follow, FollowAdmin)