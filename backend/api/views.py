import tempfile

from django.db import transaction
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from fpdf import FPDF
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.status import (HTTP_200_OK, HTTP_201_CREATED,
                                   HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST)
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from users.models import Subscribers, User

from .filters import IngredientFilter, RecipeFilter
from .pagination import CustomPagination
from .permissions import IsAdminOrReadOnly, IsAuthorOrAdminOrReadOnly
from .serializers import (CustomUserSerializer, FavoriteSerializer,
                          IngredientSerializer, RecipeCompactSerializer,
                          RecipeCreateSerializer, RecipeSerializer,
                          ShoppingCartSerializer, SubscriptionCreateSerializer,
                          SubscriptionSerializer, TagSerializer)


class CustomUserViewSet(UserViewSet):
    """
    ViewSet описывающий работу с пользователями
    (действия с аккаунтом и подписками).
    """
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        if self.action == 'me':
            return [IsAuthenticated()]
        return super().get_permissions()

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id):
        if request.method == 'POST':
            return self.create_subscription(request, id)
        return self.delete_subscription(request, id)

    @transaction.atomic
    def create_subscription(self, request, id):

        get_object_or_404(User, id=id)

        limit = request.GET.get('recipes_limit')
        serializer = SubscriptionCreateSerializer(
            data={
                'user': request.user.id,
                'author': id
            },
            context={'request': request, 'limit': limit}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=HTTP_201_CREATED)

    def delete_subscription(self, request, id):

        author_exists = User.objects.filter(id=id).exists()
        if not author_exists:
            raise NotFound({'author': 'Автор не найден.'})

        delete = Subscribers.objects.filter(
            author=id,
            user=request.user
        ).delete()
        if not delete[0]:
            return Response(
                {"detail": "Страница не найдена."},
                status=HTTP_400_BAD_REQUEST
            )
        return Response(status=HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated],
        methods=['GET']
    )
    def subscriptions(self, request):
        paginator = CustomPagination()
        limit = int(request.GET.get('recipes_limit', 10))
        authors = User.objects.filter(subscribers__user=request.user)
        paginator.page_size = limit
        page = paginator.paginate_queryset(authors, request)

        if page is not None:
            serializer = SubscriptionSerializer(page, many=True,
                                                context={
                                                    'request': request,
                                                    'limit': limit
                                                })
            return paginator.get_paginated_response(serializer.data)
        serializer = SubscriptionSerializer(authors, many=True,
                                            context={
                                                'request': request,
                                                'limit': limit
                                            })
        return Response(serializer.data, status=HTTP_200_OK)


class ViewSet(ReadOnlyModelViewSet):
    pagination_class = None
    permission_classes = [IsAdminOrReadOnly]


class TagsViewSet(ViewSet):
    """ViewSet описывающий работу с тегами."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientsViewSet(ViewSet):
    """ViewSet описывающий работу с ингредиентами."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter


class RecipesViewSet(ModelViewSet):
    """
    ViewSet описывающий работу с рецептами и добавление в корзину и избранное.
    """
    queryset = Recipe.objects.all()
    permission_classes = [IsAuthorOrAdminOrReadOnly]
    http_method_names = ['get', 'post', 'patch', 'delete']
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializer
        return RecipeCreateSerializer

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return self.create_shopping_cart(request, pk)
        return self.delete_shopping_cart(request, pk)

    @transaction.atomic
    def create_shopping_cart(self, request, recipe_id):
        existing_cart = ShoppingCart.objects.filter(
            recipe_id=recipe_id,
            user=request.user
        )
        if existing_cart.exists():
            return Response(
                {"error": "Рецепт уже находится в корзине"},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            recipe = Recipe.objects.get(id=recipe_id)
        except Recipe.DoesNotExist:
            raise ValidationError(f'Рецепт с id {recipe_id} не найден.')
        data = {
            'recipe': recipe.id,
            'user': request.user.id
        }
        serializer = ShoppingCartSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        recipe_data = RecipeCompactSerializer(recipe).data
        return Response(recipe_data, status=status.HTTP_201_CREATED)

    def delete_shopping_cart(self, request, recipe_id):
        recipe = Recipe.objects.filter(id=recipe_id).first()
        if not recipe:
            return Response(
                {"detail": "Рецепт не найден."},
                status=status.HTTP_404_NOT_FOUND
            )

        shopping_cart = ShoppingCart.objects.filter(
            recipe=recipe,
            user=request.user
        ).first()
        if not shopping_cart:
            return Response(
                {"detail": "Рецепт не находится в корзине."},
                status=status.HTTP_400_BAD_REQUEST
            )

        shopping_cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        if request.method == 'POST':
            return self.create_favorite(request, pk)
        return self.delete_favorite(request, pk)

    @transaction.atomic
    def create_favorite(self, request, recipe_id=None):
        existing_cart = Favorite.objects.filter(
            recipe_id=recipe_id,
            user=request.user
        )
        if existing_cart.exists():
            return Response(
                {"error": "Рецепт уже находится в избранных"},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            recipe = Recipe.objects.get(id=recipe_id)
        except Recipe.DoesNotExist:
            raise ValidationError(f'Рецепт с id {recipe_id} не найден.')
        data = {
            'recipe': recipe.id,
            'user': request.user.id
        }
        serializer = FavoriteSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            recipe_data = RecipeCompactSerializer(recipe).data
            return Response(recipe_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete_favorite(self, request, recipe_id=None):
        recipe = Recipe.objects.filter(id=recipe_id).first()
        if not recipe:
            return Response(
                {"detail": "Рецепт не найден."},
                status=status.HTTP_404_NOT_FOUND
            )

        favorite = Favorite.objects.filter(
            recipe=recipe,
            user_id=request.user.id
        ).first()
        if not favorite:
            return Response(
                {"detail": "Страница не найдена."},
                status=HTTP_400_BAD_REQUEST
            )

        favorite.delete()
        return Response(status=HTTP_204_NO_CONTENT)

    def create_shopping_list_pdf(self, ingredients):
        file_path = tempfile.NamedTemporaryFile(
            suffix=".pdf",
            delete=False
        ).name

        pdf = FPDF()
        pdf.add_page()
        pdf.add_font(
            'GeistMono',
            '',
            'static/font/GeistMono-Medium.ttf',
            uni=True
        )
        pdf.set_font('GeistMono', size=25)

        pdf.cell(200, 10, txt="Корзина покупок:", ln=True, align='C')

        for ingredient, info in ingredients.items():
            text = f"{ingredient}({info['unit']}): {info['total_amount']}"
            pdf.cell(200, 10, txt=text, ln=True, align='C')

        pdf.output(name=file_path)
        return file_path

    @action(
        detail=False,
        permission_classes=[IsAuthenticated],
        methods=['GET']
    )
    def download_shopping_cart(self, request):
        cart_items = ShoppingCart.objects.filter(user=request.user)

        ingredients = {}
        for cart_item in cart_items:
            recipe_ingredients = RecipeIngredient.objects.filter(
                recipe=cart_item.recipe
            )

            for recipe_ingredient in recipe_ingredients:

                ingredient = recipe_ingredient.ingredient
                amount = recipe_ingredient.amount
                unit = recipe_ingredient.ingredient.measurement_unit

                if ingredient.name in ingredients:
                    ingredients[ingredient.name]['total_amount'] += amount
                else:
                    ingredients[ingredient.name] = {
                        'total_amount': amount,
                        'unit': unit
                    }
        path = self.create_shopping_list_pdf(ingredients)
        with open(path, 'rb') as pdf_file:
            pdf_data = pdf_file.read()
            response = HttpResponse(pdf_data, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{path}"'
        return response
