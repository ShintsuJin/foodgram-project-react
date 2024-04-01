import base64

from django.core.files.base import ContentFile
from django.core.validators import RegexValidator
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from django.db import transaction

from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingList, Tag)
from users.models import Subscribe, User


class Base64ImageField(serializers.ImageField):
    """Custom field for processing images in base64 format."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name=f'image.{ext}')
        return super().to_internal_value(data)


class SetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True)
    current_password = serializers.CharField(required=True)

    def validate_current_password(self, value):
        if not self.context['request'].user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value


class CustomUserSerializer(UserSerializer):
    """Serializer for custom users."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Subscribe.objects.filter(user=user, author=obj.id).exists()


class CustomUserCreateSerializer(UserCreateSerializer):
    """Serializer for create users."""
    email = serializers.EmailField(
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message='Enter a valid email address.',
            ),
        ]
    )

    username = serializers.CharField(
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message='Enter a valid username.',
            ),
        ]
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = True

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'password'
        )


class RecipeSubSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField(source='get_image')

    def get_image(self, obj):
        return obj.image.url

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(CustomUserSerializer):
    """Serializer for Subscribtion."""
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    email = serializers.ReadOnlyField()
    username = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def validate(self, data):
        user = self.context.get('request').user
        author = self.instance
        if user == author:
            raise serializers.ValidationError(
                'You literally cant subscribe urself.')
        if Subscribe.objects.filter(
                user=user, author=author).exists():
            raise serializers.ValidationError(
                f'You already subscribed on {author}.')
        return data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author_id=obj.id).count()

    def get_recipes(self, obj):
        recipes_limit = (self.context.get('request').
                         query_params.get('recipes_limit'))
        try:
            if recipes_limit is not None:
                recipes_limit = int(recipes_limit)
        except ValueError:
            raise serializers.ValidationError(
                'recipes_limit should be an int.')

        recipes_queryset = Recipe.objects.filter(author=obj)

        if recipes_limit is not None:
            recipes_queryset = recipes_queryset[:recipes_limit]

        recipes_serializer = RecipeSubSerializer(recipes_queryset, many=True)

        return recipes_serializer.data


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for ingredients."""

    class Meta:
        model = Ingredient
        fields = ('id', 'measurement_unit', 'name')


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags."""
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientRecipeSerializers(serializers.ModelSerializer):
    """Serializer to get an amount of ingredients."""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeListSerializer(serializers.ModelSerializer):
    """Serializer to display recipes."""
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    image = serializers.SerializerMethodField(source='get_image')

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')

    def get_image(self, obj):
        return obj.image.url

    def get_ingredients(self, obj):
        queryset = IngredientRecipe.objects.filter(recipe=obj)
        return [{'id': item.id, 'name': item.ingredient.name,
                 'measurement_unit': item.ingredient.measurement_unit,
                 'amount': item.amount} for item in queryset]

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(user=request.user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return ShoppingList.objects.filter(
            user=request.user,
            recipe=obj).exists()


class CreateIgredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all())

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Serializer to add recipes."""
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all())
    ingredients = CreateIgredientRecipeSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags',
                  'ingredients', 'name', 'image',
                  'text', 'cooking_time',)

    def validate(self, obj):
        if not self.initial_data.get('ingredients'):
            raise serializers.ValidationError('No ingredients provided.')
        if not self.initial_data.get('tags'):
            raise serializers.ValidationError('No tags provided.')
        return obj

    def validate_tags(self, data):
        tags = self.initial_data.get('tags')
        if tags is None or len(tags) == 0:
            raise serializers.ValidationError(
                'Choose at least one tag.')
        tags_list = []
        for tag in tags:
            if tag in tags_list:
                raise serializers.ValidationError('Tags are not unique')
            tags_list.append(tag)
        return data

    def validate_ingredients(self, data):
        ingredients = self.initial_data.get('ingredients')
        if len(ingredients) == 0:
            raise serializers.ValidationError(
                'Choose at least one ingredient.')

        ingredients_list = []
        for ingredient in ingredients:

            if ingredient.get('id') in ingredients_list:
                raise serializers.ValidationError(
                    'Ingredients are not unique')
            if ingredient.get('amount') in (None, 0):
                raise serializers.ValidationError(
                    'Recipe cant be without ingredients')
            ingredients_list.append(ingredient.get('id'))

        return data

    def create_ingredients(self, recipe, ingredients_data):
        ingredients = []
        for ingredient_data in ingredients_data:
            ingredient = ingredient_data.get('id')
            amount = ingredient_data.get('amount')
            ingredient_obj = IngredientRecipe(recipe=recipe, ingredient=ingredient, amount=amount)
            ingredients.append(ingredient_obj)
        IngredientRecipe.objects.bulk_create(ingredients)

    @transaction.atomic
    def create(self, validated_data):
        author = self.context['request'].user
        tags_data = validated_data.pop('tags', [])
        ingredients_data = validated_data.pop('ingredients', [])

        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags_data)
        self.create_ingredients(recipe, ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        super().update(instance, validated_data)
        tags = validated_data.get("tags")
        instance.tags.set(tags)
        instance.ingredients.clear()
        ingredients = validated_data.get('ingredients')
        self.create_ingredients(instance, ingredients)
        instance.save()
        return instance

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeListSerializer(instance, context=context).data
