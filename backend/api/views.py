from django.db.models import Sum
from django.shortcuts import HttpResponse, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import (Favorite, Ingredient, IngredientList,
                            Recipe, ShoppingList, Tag)
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.permissions import AllowAny, IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response

from .filters import RecipeFilter
from .paginations import LimitPagePagination
from .permissions import IsAuthorOrAdminOrReadOnly
from .serializers import (CreateRecipeSerializer, IngredientSerializer,
                          RecipeSerializer, RecipeShortSerializer,
                          TagSerializer)


class TagsViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    search_fields = ('^name',)
    filter_backends = (DjangoFilterBackend,)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    pagination_class = LimitPagePagination
    filter_backends = (DjangoFilterBackend,)
    filter_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeSerializer
        return CreateRecipeSerializer

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        if request.method == 'POST':
            return self.add_to(Favorite, request.user, pk)
        else:
            return self.delete_from(Favorite, request.user, pk)

    @action(
        detail=False,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
        url_path=r'(?P<recipe_id>[0-9]+)/shopping_list',
    )
    def shopping_list(self, request, pk):
        if request.method == 'POST':
            return self.add_to(ShoppingList, request.user, pk)
        else:
            return self.delete_from(ShoppingList, request.user, pk)

    def add_to(self, model, user, pk):
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response({'errors': 'Рецепт уже добавлен!'},
                            status=status.HTTP_400_BAD_REQUEST)
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = RecipeShortSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_from(self, model, user, pk):
        object = model.objects.filter(user=user, recipe__id=pk)
        if object.exists():
            object.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': 'Рецепт уже удален!'},
                        status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def download_shopping_cart(request):
    ingredient_list = "Cписок покупок:"
    ingredients = IngredientList.objects.filter(
        recipe__shopping_cart__user=request.user
    ).values(
        'ingredient__name', 'ingredient__measurement_unit'
    ).annotate(quantity=Sum('amount'))
    for number, item in enumerate(ingredients):
        ingredient_list += (
            f"\n{item['ingredient__name']} - "
            f"{item['quantity']} {item['ingredient__measurement_unit']}"
        )
        if number < ingredients.count() - 1:
            ingredient_list += ', '
    file = 'shopping_list'
    response = HttpResponse(ingredient_list, 'Content-Type: application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{file}.pdf"'
    return response
