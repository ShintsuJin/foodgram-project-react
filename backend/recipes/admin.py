from django.contrib import admin

from .models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                     ShoppingList, Tag)


class RecipeIngrediendsInLine(admin.TabularInline):
    model = IngredientRecipe
    extra = 3
    min_num = 1


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'ingredients_list', 'tags_list',)
    list_filter = ('author', 'name', 'tags')
    inlines = (RecipeIngrediendsInLine,)

    @admin.display(description='List of ingredients')
    def ingredients_list(self, obj):
        return [i.ingredient for i in
                obj.recipe_ingredients.all().select_related('ingredient')]

    @admin.display(description='List of tags')
    def tags_list(self, obj):
        return [i.name for i in obj.tags.all()]

    def get_favorites_count(self, obj):
        return obj.favorite_recipe.count()

    get_favorites_count.short_description = 'Favorites Count'

    readonly_fields = ('get_favorites_count',)


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
