from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
    RegexValidator,
)
from rest_framework import status
from .validators import validate_bad_value_in_username
from django.db.models import CheckConstraint, F, Q, UniqueConstraint


class User(AbstractUser):
    ADMIN = 'admin'
    USER = 'user'
    ROLE_CHOICES = (
        (ADMIN, 'администратор'),
        (USER, 'пользователь'),
    )

    username = models.CharField(
        unique=True,
        max_length=150,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message='allows 150 characters or fewer @/./+/-/_ and digits',
                code=status.HTTP_400_BAD_REQUEST,
            ),
            validate_bad_value_in_username,
        ],
    )
    email = models.EmailField(max_length=254, unique=True, blank=False)
    role = models.CharField(
        choices=ROLE_CHOICES,
        default=USER,
        verbose_name='Роль',
        max_length=max(map(len, [role for role, _ in ROLE_CHOICES])),
    )
    bio = models.TextField(blank=True, verbose_name='Биография')

    @property
    def is_admin(self):
        return self.role == self.ADMIN


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )

    class Meta:
        constraints = [
            CheckConstraint(name='not_same', check=~Q(user=F('following'))),
            UniqueConstraint(fields=['user', 'following'], name='unique_pair'),
        ]