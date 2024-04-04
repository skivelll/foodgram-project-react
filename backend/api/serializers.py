import base64
import re

from django.core.files.base import ContentFile
from django.core.validators import MinValueValidator
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.exceptions import NotFound, ValidationError

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            RecipeTag, ShoppingCart, Tag)
from users.models import Subscribers, User

#   Сериализаторы отвечающие за работу с пользователями.


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        model = User
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        ]

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscribers.objects.filter(
                user=request.user,
                author=obj
            ).exists()
        return False


class CustomUserCreateSerializer(UserCreateSerializer):

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = [
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        ]

    def validate(self, attrs):
        username = attrs.get('username')
        if not re.match(r'^[\w.@+-]+\Z', username):
            raise ValidationError('Bad Request')
        return attrs


###########################################################


class SubscriptionSerializer(CustomUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + [
            'recipes', 'recipes_count'
        ]
        read_only_fields = CustomUserSerializer.Meta.fields

    def get_recipes(self, obj):
        limit = self.context.get('limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        serialized_recipes = RecipeCompactSerializer(recipes, many=True).data
        return serialized_recipes

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()


class SubscriptionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscribers
        fields = ['user', 'author']

    def validate(self, attrs):

        user = attrs['user']
        author = attrs['author']

        if not User.objects.filter(id=author.id).exists():
            raise NotFound({'author': 'Автор не найден.'})
        if user == author:
            raise ValidationError({'author': 'Нельзя подписаться на себя.'})
        if user.subscribers.filter(author=author).exists():
            raise ValidationError(
                {'author': 'Вы уже подписаны на этого автора.'}
            )

        return attrs

    def to_representation(self, instance):
        return SubscriptionSerializer(
            instance.author,
            context=self.context
        ).data


###########################################################


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'slug']


class RecipeTagSerializer(serializers.ModelSerializer):
    tag = TagSerializer()

    class Meta:
        model = RecipeTag
        fields = ['tag']


###########################################################


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(write_only=True)
    amount = serializers.IntegerField(write_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'amount']


class RecipeGetIngredientSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(method_name='get_name')
    measurement_unit = serializers.SerializerMethodField(
        method_name='get_measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'name', 'measurement_unit', 'amount']

    def get_name(self, obj):
        return obj.ingredient.name

    def get_measurement_unit(self, obj):
        return obj.ingredient.measurement_unit


###########################################################


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=True, allow_null=True)
    author = CustomUserSerializer(default=serializers.CurrentUserDefault())
    cooking_time = serializers.IntegerField(validators=[MinValueValidator(1)])
    tags = TagSerializer(many=True, read_only=True)
    ingredients = RecipeGetIngredientSerializer(
        many=True,
        source='recipe_in_ingredient'
    )
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited'
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = [
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'image',
            'name',
            'text',
            'cooking_time'
        ]

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            user = request.user
            return Favorite.objects.filter(user=user, recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            user = request.user
            return ShoppingCart.objects.filter(user=user, recipe=obj).exists()
        return False


class RecipeCreateSerializer(serializers.ModelSerializer):
    image = Base64ImageField(use_url=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    ingredients = RecipeIngredientSerializer(many=True)
    cooking_time = serializers.IntegerField(validators=[MinValueValidator(1)])

    class Meta:
        model = Recipe
        fields = [
            'id',
            'tags',
            'author',
            'ingredients',
            'image',
            'name',
            'text',
            'cooking_time'
        ]

    def validate(self, attrs):
        if not bool(attrs.get('tags', None)):
            raise ValidationError('Поле теги обязательно для заполнения')
        tags = attrs.get('tags')
        if len(tags) != len(set(tags)):
            raise ValidationError('Теги не должны повторяться')
        if not bool(attrs.get('ingredients', None)):
            raise ValidationError(
                'Поле ингредиенты обязательно для заполнения'
            )
        ingredients_data = attrs['ingredients']
        id_set = set()
        for ingredient_data in ingredients_data:
            id = ingredient_data['id']
            amount = ingredient_data['amount']
            if id in id_set:
                raise ValidationError('Ингредиенты не должны повторяться')
            try:
                Ingredient.objects.get(id=id)
            except Ingredient.DoesNotExist:
                raise ValidationError(f'Ингредиент с id {id} не найден.')
            id_set.add(id)
        if amount < 1:
            raise ValidationError('Количество должно быть больше единицы')

        return attrs

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')

        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)

        for ingredient_data in ingredients_data:
            ingredient_id = ingredient_data['id']
            ingredient = Ingredient.objects.get(id=ingredient_id)
            amount = ingredient_data.get('amount')

            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=amount
            )

        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        ingredients_data = validated_data.pop('ingredients', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if tags is not None:
            instance.tags.set(tags)

        if ingredients_data is not None:
            RecipeIngredient.objects.filter(recipe=instance).delete()

            for ingredient_data in ingredients_data:
                ingredient_id = ingredient_data['id']
                amount = ingredient_data.get('amount')
                RecipeIngredient.objects.create(
                    recipe=instance,
                    ingredient_id=ingredient_id,
                    amount=amount
                )

        instance.save()

        return instance

    def to_representation(self, instance):
        serialized_data = RecipeSerializer(instance, context=self.context).data
        return serialized_data


class RecipeCompactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']

    def to_representation(self, instance):
        representation = super(RecipeCompactSerializer,
                               self).to_representation(instance)
        return {
            'id': representation['id'],
            'name': representation['name'],
            'image': representation['image'],
            'cooking_time': representation['cooking_time']
        }


###########################################################


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingCart
        fields = ['id', 'user', 'recipe']


###########################################################


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorite
        fields = ['id', 'user', 'recipe']
