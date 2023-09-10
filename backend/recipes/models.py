from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import (
    RegexValidator,
    MinValueValidator
)
from rest_framework import status
from django.db.models import CheckConstraint, F, Q, UniqueConstraint

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(verbose_name='Название', max_length=200)
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


class Ingredient(models.Model):
    name = models.CharField(verbose_name='Название ингредиента', max_length=200)
    measurement_unit = models.CharField(verbose_name='Измерение', max_length=200)

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    name = models.CharField(verbose_name='Название рецепта', max_length=200)
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        on_delete=models.CASCADE
    )
    text = models.TextField(verbose_name='Описание')
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления в минутах',
        validators=[
            MinValueValidator(1),
        ]
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    image = models.ImageField(
        upload_to='recipes/images'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Teги'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipes',
        verbose_name='Ингредиенты',
        through='RecipeIngredient'
    )
    favorited = models.ManyToManyField(
        User,
        related_name='favorited',
        verbose_name='Избранное',
        blank=True
    )
    shopping_cart = models.ManyToManyField(
        User,
        related_name='shopping_card',
        verbose_name='Список покупок',
        blank=True
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'Рецепт: {self.name}'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, verbose_name='Рецепт', on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, verbose_name='Ингредиент', on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(
        verbose_name='Количество',
        validators=[
            MinValueValidator(1),
        ]
    )

    class Meta:
        ordering = ['recipe']
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        constraints = [
            UniqueConstraint(name='unique_pair_of_recipes', fields=['recipe', 'ingredient']),
        ]

    def __str__(self):
        return f'В {self.recipe} - {self.ingredient}, {self.amount}'




