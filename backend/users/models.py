from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
    RegexValidator,
)
from rest_framework import status
from django.db.models import CheckConstraint, F, Q, UniqueConstraint


class User(AbstractUser):
    email = models.EmailField(verbose_name='Почта', max_length=254, unique=True, blank=False)
    username = models.CharField(
        verbose_name='Имя пользователя',
        unique=True,
        max_length=150,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message='allows 150 characters or fewer @/./+/-/_ and digits',
                code=status.HTTP_400_BAD_REQUEST,
            ),
        ],
    )
    first_name = models.CharField(verbose_name='Имя', max_length=150)
    last_name = models.CharField(verbose_name='Фамилия', max_length=150)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ['username']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


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
        ordering = ['user', 'following']
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            CheckConstraint(name='not_same', check=~Q(user=F('following'))),
            UniqueConstraint(name='unique_pair', fields=['user', 'following']),
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.following}'
