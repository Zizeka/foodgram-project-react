from django.contrib import admin
from django.contrib.admin import display

from .models import Ingredient, Recipe, Tag

admin.site.register(Tag)
admin.site.register(Recipe)
admin.site.register(Ingredient)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'measurement_unit'
    )
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


class IngredientsInline(admin.TabularInline):
    model = Ingredient


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'author',
        'name',
        'quantity_favorites'
    )

    search_fields = ('name', 'author',)
    list_filter = ('name', 'tags', 'author',)
    fields = ('name', 'text', 'tags', 'author')
    empty_value_display = '-пусто-'

    @display(description='Количество в избранных')
    def quantity_favorites(self, obj):
        return obj.favorites.count()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    search_fields = ('name',)
    list_filter = ('name',)
