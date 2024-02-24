from django.db import models

from users.models import User
from .validators import validate_is_hex

SHORT_LENGTH: int = 64
LONG_LENGTH: int = 256


class Recipe(models.Model):
    """Модель рецепта."""
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes', verbose_name='Автор')
    title = models.CharField('Название', max_length=SHORT_LENGTH)
    image = models.ImageField(
        upload_to='recipes/images/',
        null=True,
        default=None
    )
    ingredients = models.ManyToManyField('Ingredient', through='RecipeIngredient', verbose_name='Ингридиенты')
    tags = models.ManyToManyField('Tag', verbose_name='Тег')
    cooking_time = models.ImageField('Время приготовления')

    def __str__(self) -> str:
        return self.title


class Ingredient(models.Model):
    """Модель ингредиента."""
    name = models.CharField('Название', max_length=SHORT_LENGTH, unique=True)
    unit = models.CharField('Единица измерения', max_length=SHORT_LENGTH)

    def __str__(self) -> str:
        return self.name


class RecipeIngredient(models.Model):
    """Модель связывающая ингредиенты и рецепт."""
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, verbose_name='Рецепт')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, verbose_name='Ингридиент')
    amount = models.DecimalField('Количество')

    def __str__(self) -> str:
        return f'{self.ingredient} ({self.amount})'


class Tag(models.Model):
    """Модель тега."""
    name = models.CharField('Название', max_length=SHORT_LENGTH, unique=True)
    color = models.CharField('Цвет', max_length=7, validators=[validate_is_hex], unique=True)
    slug = models.SlugField('Слаг', unique=True)

    def __str__(self) -> str:
        return self.name
