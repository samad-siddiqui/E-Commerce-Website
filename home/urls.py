from django.urls import path, include
from .views import (
    UserRegister,
    ProfileViewSet,
    CategoryViewSet,
    ProductViewSet,
    ProductVarientViewSet,
    CartViewSet,
    OrderViewSet,
    ShippingAddressViewSet,
    WishlistViewSet,
    CouponViewSet,
)
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()
router.register(r'profile', ProfileViewSet, basename='profile')
router.register(r'category', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='products')
router.register(r'product-variants', ProductVarientViewSet,
                basename='product-variants')
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'orders', OrderViewSet, basename='orders')
router.register(r'shipping-address', ShippingAddressViewSet,
                basename='shipping-address')
router.register(r'wishlist', WishlistViewSet, basename='wishlist')
router.register(r'coupons', CouponViewSet, basename='coupons')

urlpatterns = [
    path('api/users/register/', UserRegister.as_view(),
         name='user-register'),
    path('api/login/', TokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(),
         name='token_refresh'),

    path('api/', include(router.urls)),
]
