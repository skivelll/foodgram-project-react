from django.contrib import admin
from django.contrib.admin import display

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
        'id',
        'author',
        'name',
        'added_in_favorites',
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
    readonly_fields = ('added_in_favorites',)

    inlines = [RecipeIngredientInline, RecipeTagInline]


    @display(description='Количество в избранных')
    def added_in_favorites(self, obj):
        return Favorite.objects.filter(recipe=obj).count()


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
