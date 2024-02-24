from django.contrib import admin

from .models import Recipe, Ingredient, Tag


class RecipeAdmin(admin.ModelAdmin):
    """Отображение модели Recipe в админ панели сайта."""

    list_display = (
        'author',
        'title',
        'tags',
    )
    list_editable = (
        'title',
    )
    search_fields = (
        'author',
        'title',
        'tags',
    )
    list_filter = (
        'author',
        'title',
        'tags',
    )


class IngredientAdmin(admin.ModelAdmin):
    """Отображение модели Ingredient в админ панели сайта."""

    list_display = ('name',)
    list_editable = ('name',)
    search_fields = ('name',)
    list_filter = ('unit',)


class TagAdmin(admin.ModelAdmin):
    """Отображение модели TagRecipe в админ панели сайта."""

    list_display = (
        'name',
        'color',
        'slug',
    )
    list_editable = (
        'name',
        'color',
        'slug',
    )
    search_fields = (
        'name',
        'color',
        'slug',
    )


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
