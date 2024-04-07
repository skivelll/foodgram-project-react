from django.db import models
from users.models import User

from .validators import validate_is_hex

SHORT_LENGTH: int = 64
LONG_LENGTH: int = 256


class Ingredient(models.Model):
    """Модель ингредиента."""
    name = models.CharField('Название', max_length=SHORT_LENGTH)
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=SHORT_LENGTH
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'
        unique_together = [['name', 'measurement_unit']]

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Модель тега."""
    name = models.CharField(
        'Название',
        max_length=SHORT_LENGTH,
        unique=True
    )
    color = models.CharField(
        'Цвет',
        max_length=7,
        validators=[validate_is_hex],
        unique=True
    )
    slug = models.SlugField(
        'Слаг',
        unique=True
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецепта."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    name = models.CharField('Название', max_length=SHORT_LENGTH)
    image = models.ImageField(
        upload_to='recipes/images/',
        null=True,
        default=None
    )
    tags = models.ManyToManyField(
        Tag,
        through='RecipeTag',
        through_fields=('recipe', 'tag'),
        verbose_name='Тег'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты'
    )
    cooking_time = models.IntegerField('Время приготовления')
    text = models.TextField('Рецепт')

    class Meta:
        ordering = ('name',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_in_ingredient',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_in_recipe',
        verbose_name='Ингредиент'
    )
    amount = models.FloatField('Количество')

    class Meta:
        verbose_name = 'Рецепт - Ингредиент'
        verbose_name_plural = 'Рецепт - Ингредиент'
        unique_together = [['recipe', 'ingredient']]


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_in_tag',
        verbose_name='Рецепт'
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='tag_in_recipe',
        verbose_name='Тег'
    )

    class Meta:
        verbose_name = 'Рецепт - Тег'
        verbose_name_plural = 'Рецепт - Тег'
        unique_together = [['recipe', 'tag']]


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        unique_together = [['user', 'recipe']]


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        unique_together = [['recipe', 'user']]
