from django.contrib import admin

from .models import (
    Favorite,
    Ingredient,
    Ingredient_list,
    Recipe,
    Shopping_list,
    Tag
)

admin.site.register(Tag)
admin.site.register(Favorite)
admin.site.register(Ingredient_list)
admin.site.register(Shopping_list)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'measurement_unit'
    )
    search_fields = ('name',)
    empty_value_display = '-пусто-'


class IngredientsInline(admin.TabularInline):
    model = Ingredient


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'author',
        'name',
        'text',
        'image',
        'quantity_favorites'

    )

    search_fields = ('name', 'author',) 
    list_filter = ('name', 'tags', 'author')
    empty_value_display = '-пусто-'

    def quantity_favorites(self, obj):
        return obj.favorites.count()