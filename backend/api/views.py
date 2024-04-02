from django.contrib.auth import update_session_auth_hash
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser import utils
from djoser.conf import settings as sett
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingList, Tag)
from users.models import Subscribe, User
from .filters import IngredientFilter, RecipeFilter
from .pagination import LimitPageNumberPagination
from .permissions import IsAuthorOrAdminOrReadOnly
from .serializers import (CustomUserCreateSerializer, CustomUserSerializer,
                          IngredientSerializer, RecipeCreateSerializer,
                          RecipeListSerializer, RecipeSubSerializer,
                          SetPasswordSerializer, SubscribeSerializer,
                          TagSerializer)
from .utils import txt_generation


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (IsAuthenticatedOrReadOnly,)


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class CustomUserViewSet(viewsets.ModelViewSet):
    """ViewSet for Users performance."""
    queryset = User.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('username', 'email')
    serializer_class = CustomUserSerializer
    pagination_class = LimitPageNumberPagination

    @action(["post"], detail=False)
    def set_password(self, request, *args, **kwargs):
        serializer = SetPasswordSerializer(
            data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        self.request.user.set_password(serializer.data["new_password"])
        self.request.user.save()

        if sett.LOGOUT_ON_PASSWORD_CHANGE:
            utils.logout_user(self.request)
        elif sett.CREATE_SESSION_ON_LOGIN:
            update_session_auth_hash(self.request, self.request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_queryset(self):
        queryset = super().get_queryset()
        limit = self.request.query_params.get('limit')
        if limit:
            queryset = queryset[:int(limit)]
        return queryset

    def create(self, request, *args, **kwargs):
        self.permission_classes = [permissions.AllowAny]
        serializer = CustomUserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=False,
        url_path='me',
        methods=['get'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def me_get(self, request):
        """View for authenticated user to retrieve their profile."""
        serializer = CustomUserSerializer(request.user,
                                          context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        url_path='me',
        methods=['patch'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def me_patch(self, request):
        """View for authenticated user to update their profile."""
        serializer = self.get_serializer(request.user,
                                         data=request.data,
                                         partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        url_path='subscriptions',
        methods=('get',),
        permission_classes=(permissions.IsAuthenticated,),
    )
    def subscriptions(self, request):
        """View to list subscriptions of the authenticated user."""
        subscriptions = Subscribe.objects.filter(user=request.user)
        authors_ids = subscriptions.values_list('author_id', flat=True)
        authors = User.objects.filter(id__in=authors_ids)
        result_page = self.paginate_queryset(authors)
        serializer = SubscribeSerializer(
            result_page,
            many=True,
            context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=('post', 'delete'),
        url_path='subscribe',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def subscribe(self, request, *args, **kwargs):
        """Action to handle user subscribe and unsubscribe."""
        if request.method == 'POST':
            author = get_object_or_404(User, id=kwargs['pk'])
            serializer = SubscribeSerializer(
                author, data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            Subscribe.objects.create(user=request.user, author=author)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            author = get_object_or_404(User, id=kwargs['pk'])
            subscription = Subscribe.objects.filter(
                user=request.user, author=author).first()
            if subscription:
                subscription.delete()
                return Response({'detail': 'Unsubscribed'},
                                status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({'detail': 'There is no active sub'},
                                status=status.HTTP_400_BAD_REQUEST)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = [IsAuthorOrAdminOrReadOnly]
    pagination_class = LimitPageNumberPagination

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeListSerializer
        return RecipeCreateSerializer

    @action(detail=True, methods=['post', 'delete'], url_path='favorite',
            permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk):
        if request.method == 'POST':
            try:
                Recipe.objects.get(pk=pk)
            except Recipe.DoesNotExist:
                return Response(
                    {'errors': 'Recipe does not exist'},
                    status=status.HTTP_400_BAD_REQUEST)

            if Favorite.objects.filter(
                    user=request.user, recipe__id=pk).exists():
                return Response({'errors': 'Recipe is already added in list'},
                                status=status.HTTP_400_BAD_REQUEST)
            recipe = get_object_or_404(Recipe, id=pk)
            Favorite.objects.create(user=request.user, recipe=recipe)
            serializer = RecipeSubSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            try:
                obj = get_object_or_404(Favorite.objects.filter(
                    user=request.user, recipe__id=pk))
                obj.delete()
                return Response({'detail': 'Removed'},
                                status=status.HTTP_204_NO_CONTENT)
            except Favorite.DoesNotExist:
                return Response({'errors': 'Recipe is already deleted'},
                                status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post', 'delete'], url_path='shopping_cart',
            permission_classes=[permissions.IsAuthenticated])
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            try:
                Recipe.objects.get(pk=pk)
            except Recipe.DoesNotExist:
                return Response({'errors': 'Recipe does not exist'},
                                status=status.HTTP_400_BAD_REQUEST)
            if ShoppingList.objects.filter(user=request.user,
                                           recipe__id=pk).exists():
                return Response({'errors': 'Recipe is already existed'},
                                status=status.HTTP_400_BAD_REQUEST)
            recipe = get_object_or_404(Recipe, id=pk)
            ShoppingList.objects.create(user=request.user, recipe=recipe)
            serializer = RecipeSubSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            try:
                obj = get_object_or_404(
                    ShoppingList.objects.filter(
                        user=request.user, recipe__id=pk))
                obj.delete()
                return Response(
                    {'detail': 'Removed'}, status=status.HTTP_204_NO_CONTENT)
            except ShoppingList.DoesNotExist:
                return Response({'errors': 'Recipe is already deleted'},
                                status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='download_shopping_cart',
            permission_classes=[permissions.IsAuthenticated])
    def download_shopping_cart(self, request):
        ingredient_queryset = (
            IngredientRecipe.objects
            .filter(recipe__shoppinglist_recipe__user=request.user)
            .select_related('ingredient')
        )
        return txt_generation(ingredient_queryset)
