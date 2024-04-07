from django.contrib import admin
from django.db.models import Count

from .models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                     ShoppingList, Tag)


class RecipeIngrediendsInLine(admin.TabularInline):
    model = IngredientRecipe
    extra = 3
    min_num = 1


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'ingredients_list', 'tags_list',
                    'favorites_count')
    list_filter = ('author', 'name', 'tags')
    inlines = (RecipeIngrediendsInLine,)

    @admin.display(description='Список ингредиентов')
    def ingredients_list(self, obj):
        return [i.ingredient for i in
                obj.recipe_ingredients.all().select_related('ingredient')]

    @admin.display(description='Список тэгов')
    def tags_list(self, obj):
        return [i.name for i in obj.tags.all()]

    @admin.display(description='Количество добавлений в избранное')
    def favorites_count(self, obj):
        return obj.favorite_recipe_count

    readonly_fields = ('favorites_count',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            favorite_recipe_count=Count(
                'favorite_recipe'))
        return queryset


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    search_fields = ('name',)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(IngredientRecipe)
admin.site.register(Favorite)
admin.site.register(ShoppingList)
