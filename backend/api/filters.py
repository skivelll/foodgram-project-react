from django_filters import rest_framework as filters

from recipes.models import Recipe, Tag, Ingredient


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ['name']


class RecipeFilter(filters.FilterSet):
    author = filters.NumberFilter(field_name='author__id')
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_in_shopping_cart'
    )

    def filter_by_tags(self, queryset, name, value):
        return queryset.filter(tags__slug=value)

    def filter_is_favorited(self, queryset, name, value):
        if value:
            return queryset.filter(favorite__user=self.request.user.id)
        else:
            return queryset.filter(favorite__user__date=self.request.user.id)

    def filter_in_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(shoppingcart__user=self.request.user.id)
        else:
            return queryset.filter(shoppingcart__date=self.request.user.id)

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'is_favorited', 'is_in_shopping_cart']
