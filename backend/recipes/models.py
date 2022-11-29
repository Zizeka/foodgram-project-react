from django.core.validators import MinValueValidator
from django.db import models

from users.models import User


class Tag(models.Model):
    name = models.CharField(
        max_length=200, 
        null=False, 
        unique=True)
    slug = models.SlugField(
        unique=True)
    color = models.CharField(
        max_length=7, 
        default='#FF00FF',
        unique=True)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        null=False)
    measurement_unit = models.CharField(
        max_length=200,
        null=False)


class Recipe(models.Model):
    ingredients = models.ManyToManyField(
        Ingredient, related_name='ingredients',)
    tags = models.ManyToManyField(
        Tag, related_name='tags'
    )
    image = models.ImageField(
        'Картинка', upload_to='recipes/'
    )
    name = models.CharField(max_length=200, null=False)
    text = models.TextField(max_length=500, verbose_name='Описание')
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1, message='Время кукинга должно быть больше 1')])
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )
    def __str__(self):
        return self.text

    class Meta:
        ordering = ['-pub_date']


class Shopping_list(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shoping_lists'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shoping_lists'
    )


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites'
    )


class Ingredient_list(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_lists'
    )

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_lists'
    )

    amount = models.PositiveSmallIntegerField(
        'Количесвто ингредиентов',
        validators=[MinValueValidator(1, message='Количество должно быть больше 0')]
    )

    def __str__(self):
        return f'{self.ingredient} {self.amount}  в рецепте {self.recipe}'