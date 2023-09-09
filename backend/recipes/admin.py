from django.contrib import admin
from .models import Recipe, Tag, RecipeIngredient, Ingredient


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    list_filter = ('name', 'color', 'slug')
    empty_value_display = '-пусто-'


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name', 'measurement_unit')
    empty_value_display = '-пусто-'


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')
    list_filter = ('name', 'author')
    empty_value_display = '-пусто-'


class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('ingredient', 'recipe')
    list_filter = ('ingredient', 'recipe')
    empty_value_display = '-пусто-'


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)

