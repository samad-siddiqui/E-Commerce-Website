from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.decorators import action
from .serializers import UserRegisterSerializer
from .serializers import (ProfileSerializer,
                          CategorySerializer,
                          ProductSerializer,
                          ProductVarientSerializer
                          )
from rest_framework import status
from rest_framework.views import APIView
from .models import Profile, Category, Product, ProductVariant


class UserRegister(APIView):
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "message": "User registered successfully",
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name
            },
            status=status.HTTP_201_CREATED
        )


class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Profile.objects.filter(user=user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        profile = self.get_object()
        if profile.user != request.user:
            return Response(
                {"detail": "You do not have permission to edit this profile."},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = self.get_serializer(profile,
                                         data=request.data,
                                         partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by('-created_at')
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter,
                       filters.OrderingFilter]
    filterset_fields = ['category', 'name']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'price']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        user = self.request.user
        if user.is_superuser:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                {
                    "message": "Product created successfully",
                    "product": serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            {"detail": "You do not have permission to create a product."},
            status=status.HTTP_403_FORBIDDEN
        )

    def update(self, request, *args, **kwargs):
        user = self.request.user
        if user.is_superuser:
            product = self.get_object()
            serializer = self.get_serializer(
                product,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        return Response(
            {"detail": "You do not have permission to edit this product."},
            status=status.HTTP_403_FORBIDDEN
        )

    def destroy(self, request, *args, **kwargs):                                                                                                                            
        user = self.request.user
        if user.is_superuser:
            product = self.get_object()
            product.delete()
            return Response(
                {"detail": "Product deleted successfully."},
                status=status.HTTP_204_NO_CONTENT
            )
        return Response(
            {"detail": "You do not have permission to delete this product."},
            status=status.HTTP_403_FORBIDDEN
        )


class ProductVarientViewSet(viewsets.ModelViewSet):
    queryset = ProductVariant.objects.all()
    serializer_class = ProductVarientSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    @action(detail=True, methods=['get'], url_path='variants')
    def list_varient(self, request, *args, **kwargs):
        product = self.get_object()
        queryset = product.variants.all()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='create-variant')
    def create_varient(self, request, *args, **kwargs):
        user = self.request.user
        if user.is_superuser:
            print(user)
            product = self.get_object()
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(product=product)
            return Response(
                {
                    "message": "Product variant created successfully",
                    "product_variant": serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            {
             "detail": "You do not have permission to create a product variant."
            },
            status=status.HTTP_403_FORBIDDEN
        )
