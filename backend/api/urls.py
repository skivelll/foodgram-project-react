from django.urls import include, path
from rest_framework import routers

from .views import (
    RecipesViewSet, CustomUserViewSet, TagsViewSet, IngredientsViewSet
)

router = routers.DefaultRouter()
router.register(r'recipes', RecipesViewSet, basename='recipes')
router.register(r'tags', TagsViewSet)
router.register(r'ingredients', IngredientsViewSet)
router.register(r'users', CustomUserViewSet)


urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
