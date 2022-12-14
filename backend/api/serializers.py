from django.shortcuts import get_object_or_404
from recipes.models import (Favorite, Ingredient, IngredientList, Recipe,
                            ShoppingList, Tag)
from rest_framework import serializers
from users.serializers import UserSerializer

from .fields import Base64ImageField


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientListSerializer(serializers.ModelSerializer):

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientList
        fields = ['id', 'name', 'measurement_unit']


class RecipeSerializer(serializers.ModelSerializer):

    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientListSerializer(many=True)
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited')
    is_in_shopping_list = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_list')

    class Meta:
        model = Recipe
        fields = [
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_list',
            'name',
            'image',
            'text',
            'cooking_time'
        ]

    def get_is_favorited(self, recipe):
        user = self.context['request'].user
        return (
            user.is_authenticated
            and Favorite.objects.filter(recipe=recipe, user=user).exists()
        )

    def get_is_in_shopping_list(self, recipe):
        user = self.context['request'].user
        return (
            user.is_authenticated
            and ShoppingList.objects.filter(recipe=recipe, user=user).exists()
        )


class AddIngredientRecipeSerializer(serializers.ModelSerializer):
    """ ???????????????????????? ???????????????????? ?????????????????????? ?? ????????????. """

    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientList
        fields = ['id', 'amount']


class CreateRecipeSerializer(serializers.ModelSerializer):
    """ ???????????????????????? ????????????????/???????????????????? ??????????????. """

    author = UserSerializer(read_only=True)
    ingredients = AddIngredientRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = [
            'id',
            'author',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time'
        ]

    def validate_ingredients(self, data):
        ingredients = data
        ingredients_list = []
        for ingredient in ingredients:
            quantity = ingredient['amount']
            if int(quantity) < 1:
                raise serializers.ValidationError({
                   'amount': '???????????????????? ???????????? ???????? ???????????? 0!'
                })
            if ingredient['id'] in list:
                raise serializers.ValidationError({
                   'ingredient': '?????????????????????? ???????????? ???????? ??????????????????????!'
                })
            ingredients_list.append(ingredient['id'])
        return data

    def validate_tags(self, data):
        tags = data
        if not tags:
            raise serializers.ValidationError('???????????? ???????????? ???????? ????????????-??????!')
        tags_list = []
        for tag in tags:
            if tag in tags_list:
                raise serializers.ValidationError('?????????? ???????????????????? ????????')
            tags_list.append(tag)
        return data

    def create_ingredients(self, ingredients, recipe):
        IngredientList.objects.bulk_create(
            [IngredientList(
                get_object_or_404(Ingredient, id=ingredient['id']),
                recipe=recipe,
                amount=ingredient['amount']
            ) for ingredient in ingredients]
        )

    def create_tags(self, tags, recipe):
        for tag in tags:
            recipe.tags.add(tag)

    def create(self, validated_data):
        author = self.context.get('request').user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=author, **validated_data)
        self.create_tags(tags, recipe)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, recipe, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        IngredientList.objects.filter(recipe=recipe).delete()
        self.create_ingredients(ingredients, recipe)
        recipe.tags.set(tags)
        return super().update(recipe, validated_data)

    def to_representation(self, instance):
        return RecipeSerializer(instance, context={
            'request': self.context.get('request')
        }).data


class FavoriteSerializer(serializers.ModelSerializer):
    """ ???????????????????????? ???????????? ??????????????????. """

    class Meta:
        model = Favorite
        fields = ['user', 'recipe']

    def to_representation(self, instance):
        return ShowFavoriteSerializer(instance.recipe, context={
            'request': self.context.get('request')
        }).data


class ShowFavoriteSerializer(serializers.ModelSerializer):
    """ ???????????????????????? ?????? ?????????????????????? ????????????????????. """

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']


class ShoppingListSerializer(serializers.ModelSerializer):
    """ ???????????????????????? ?????? ???????????? ??????????????. """

    class Meta:
        model = ShoppingList
        fields = ['user', 'recipe']

    def to_representation(self, instance):
        return ShowFavoriteSerializer(instance.recipe, context={
            'request': self.context.get('request')
        }).data


class RecipeShortSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )
