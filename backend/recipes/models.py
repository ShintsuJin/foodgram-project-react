from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from users.models import User
from .consts import MAX_LENGTH_TEXT


class Tag(models.Model):
    """Model for tags."""
    name = models.CharField(
        max_length=MAX_LENGTH_TEXT,
        unique=True,
        verbose_name='Название тэга'
    )
    color = models.CharField(
        verbose_name='Цвет в HEX',
        max_length=7,
        unique=True,
        validators=[
            RegexValidator(
                regex='^#[a-fA-F0-9]{6}$',
                message='Введенное занчение не является HEX-кодом цвета.'
            )
        ]
    )
    slug = models.SlugField(
        max_length=MAX_LENGTH_TEXT,
        unique=True,
        verbose_name='Слаг',
        validators=[
            RegexValidator(
                regex='^[-a-zA-Z0-9_]+$',
                message=(
                    'slug введен неверно. Может состоять из латинских'
                    ' букв, цифр и спецсимвола _'
                )
            )
        ]
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Model for ingredients."""
    name = models.CharField(
        max_length=MAX_LENGTH_TEXT,
        verbose_name='Ингредиент'
    )
    measurement_unit = models.CharField(
        max_length=MAX_LENGTH_TEXT,
        verbose_name='Единицы измерения'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Model for recipes."""
    name = models.CharField(
        max_length=MAX_LENGTH_TEXT,
        verbose_name='Название',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Тэги рецепта')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта'
    )
    ingredients = models.ManyToManyField(
        'Ingredient',
        through='IngredientRecipe',
        verbose_name='Ингредиенты',
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='Картинка рецепта'
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                1,
                message='Минимальное время 1 минута!'
            ),
        ],
        verbose_name='Время приготовления (в минутах)',
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    """Model for an amount ingredients."""
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE,
        related_name='ingredients_recipe'
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='recipe_ingredients'
    )
    amount = models.IntegerField(
        verbose_name='Количество ингрединта',
        validators=[
            MinValueValidator(1, 'Значение должно быть не меньше 1'),
        ]
    )

    class Meta:
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
        ordering = ('amount',)
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique_ingredients_recipe',
            ),
        ]

    def __str__(self):
        return f'{self.recipe} - {self.ingredient}'


class Favorite(models.Model):
    """Model for favorites."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
        related_name='favorite_user',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite_recipe',
        verbose_name='Рецепт автора',
    )

    class Meta:
        ordering = ['recipe']
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_name_favorite'
            )
        ]

    def __str__(self):
        return f'{self.user} - {self.recipe}'


class ShoppingList(models.Model):
    """Model of shopping list."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shoppinglist_user',
        verbose_name='Пользователь сайта',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shoppinglist_recipe',
        verbose_name='Рецепт в корзине пользователя',
    )

    class Meta:
        verbose_name = 'Cписок покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shop_list'
            )
        ]

    def __str__(self):
        return f'{self.user} - {self.recipe}'
