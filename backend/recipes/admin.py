from django.contrib import admin

from .forms import TagForm
from .models import (Favorite, Ingredient, Recipe, RecipeIngredient, RecipeTag,
                     ShoppingCart, Tag)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient


class RecipeTagInline(admin.TabularInline):
    model = RecipeTag


class RecipeAdmin(admin.ModelAdmin):
    """Отображение модели Recipe в админ панели сайта."""

    list_display = (
        'author',
        'name',
    )
    search_fields = (
        'author',
        'name',
    )
    list_filter = (
        'author',
        'name',
        'tags',
    )

    inlines = [RecipeIngredientInline, RecipeTagInline]


class IngredientAdmin(admin.ModelAdmin):
    """Отображение модели Ingredient в админ панели сайта."""

    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('measurement_unit', 'name')


class TagAdmin(admin.ModelAdmin):
    """Отображение модели Tag в админ панели сайта."""

    list_display = (
        'name',
        'color',
        'slug',
    )
    search_fields = (
        'name',
        'color',
        'slug',
    )
    form = TagForm



class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
