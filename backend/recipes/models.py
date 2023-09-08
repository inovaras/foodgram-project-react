from django.db import models
from django.core.validators import (
    RegexValidator,
)
from rest_framework import status


class Tag(models.Model):
    name = models.CharField(verbose_name='Название', max_lengh=200)
    color = models.CharField(
        verbose_name='Цвет в HEX',
        max_length=7,
        validators=[
            RegexValidator(
                regex=r'^#[A-Fa-f\d]{6}$',
                message='allows color in HEX',
                code=status.HTTP_400_BAD_REQUEST,
            ),
        ],
    )
    slug = models.SlugField(
        verbose_name='Уникальный слаг',
        max_length=200,
        unique=True,
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Teг'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name
