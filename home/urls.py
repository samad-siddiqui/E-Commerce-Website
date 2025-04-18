from django.urls import path
from .views import (UserRegister,
                    ProfileViewSet,
                    CategoryViewSet,
                    ProductViewSet,
                    ProductVarientViewSet,
                    CartViewSet,
                    OrderViewSet,
                    )
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


router = DefaultRouter()
router.register(r'api/profile', ProfileViewSet, basename='profile')
router.register(r'api/category', CategoryViewSet, basename='category')
router.register(r'api/products', ProductViewSet, basename='products')
router.register(r'api/product-variants', ProductVarientViewSet,
                basename='product-variants')
router.register(r'api/cart', CartViewSet, basename='cart')
router.register(r'api/orders', OrderViewSet, basename='orders')


urlpatterns = [
    path('api/users/register/',
         UserRegister.as_view(), name='user-register'),
    path('api/login/',
         TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/',
         TokenRefreshView.as_view(), name='token_refresh'),
]
urlpatterns += router.urls
