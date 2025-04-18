from rest_framework import viewsets, filters
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.decorators import action
from .serializers import UserRegisterSerializer
from .serializers import (ProfileSerializer,
                          CategorySerializer,
                          ProductSerializer,
                          ProductVarientSerializer,
                          CartSerializer,
                          CartItemSerializer,
                          OrderSerializer,
                          OrderItemSerializer,
                          PaymentSerializer,
                          ShippingAddressSerializer,
                          ReviewSerializer,
                          WishlistSerializer,
                          CouponSerializer,
                          ApplyCouponSerializer
                          )
from rest_framework import status
from rest_framework.views import APIView
from django.db.models import Sum, F
from .models import (Profile,
                     Category,
                     Product,
                     ProductVariant,
                     Order,
                     OrderItem,
                     Cart,
                     Payment,
                     ShippingAddress,
                     Review,
                     Wishlist,
                     Coupon
                     )


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

    @action(detail=True, methods=['post'], url_path='creviews')
    def reviews(self, request, pk=None):
        product = get_object_or_404(Product, pk=pk)
        user = request.user

        if Review.objects.filter(product=product, user=user).exists():
            return Response(
                {"detail": "You have already reviewed this product."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = ReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(product=product, user=user)

        return Response(
            {
                "message": "Review added successfully.",
                "review": serializer.data
            },
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['get'], url_path='reviews')
    def list_reviews(self, request, pk=None):
        product = get_object_or_404(Product, pk=pk)
        reviews = product.reviews.all()
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)


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
             "detail": "You do not have permission to create a product variant"
            },
            status=status.HTTP_403_FORBIDDEN
        )


class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    def get_queryset(self):
        user = self.request.user
        return Cart.objects.filter(user=user)

    def retrieve(self, request, *args, **kwargs):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='add')
    def add_item(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = CartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product_variant = serializer.validated_data['product_variant']
        quantity = serializer.validated_data['quantity']
        # price_at_time = serializer.validated_data['price_at_time']
        if product_variant.stock_count < quantity:
            return Response(
                {"detail": "Not enough stock."},
                status=status.HTTP_400_BAD_REQUEST
            )
        cart_item, created = cart.items.get_or_create(
            product_variant=product_variant,
            defaults={'quantity': quantity
                      }
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        product_variant.stock_count -= quantity

        product_variant.save()
        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data)

    @action(detail=False, methods=['put'], url_path='update')
    def update_item(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = CartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product_variant = serializer.validated_data['product_variant']
        quantity = serializer.validated_data['quantity']
        price_at_time = serializer.validated_data['price_at_time']
        cart_item = cart.items.filter(product_variant=product_variant).first()
        if not cart_item:
            return Response(
                {"detail": "Item not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        if quantity == 0:
            cart_item.delete()
            return Response({"detail": "Item removed from cart."}, status=204)

        total_available = product_variant.stock_count + cart_item.quantity
        if quantity > total_available:
            return Response(
                {"detail": "Not enough stock available."},
                status=status.HTTP_400_BAD_REQUEST
            )
        product_variant.stock_count = total_available - quantity
        product_variant.save()

    # Update cart item
        cart_item.quantity = quantity
        cart_item.price_at_time = price_at_time
        cart_item.save()

    # Return updated cart item data
        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_200_OK)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='create')
    def create_order(self, request, *args, **kwargs):
        user = self.request.user
        cart = Cart.objects.prefetch_related('items').filter(
                                                    user=user).first()
        if not cart or cart.items.count() == 0:
            return Response(
                {"detail": "Cart is empty."},
                status=status.HTTP_400_BAD_REQUEST
            )
        order = Order.objects.create(user=user)
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product_variant=item.product_variant,
                quantity=item.quantity,
                price_at_time=item.price_at_time
            )
        cart.items.all().delete()
        serializer = self.get_serializer(order)
        return Response(serializer.data)

    @action(detail=True, methods=['put'], url_path='cancel')
    def cancel(self, request, *args, **kwargs):
        user = self.request.user
        order = self.get_object()
        if order.user == user:
            if order.order_status == 'cancelled':
                return Response(
                    {"detail": "Order is already cancelled."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            order.order_status = 'cancelled'
            order.save()
            return Response(
                {"detail": "Order cancelled successfully."},
                status=status.HTTP_200_OK
            )
        return Response(
            {"detail": "You do not have permission to cancel this order."},
            status=status.HTTP_403_FORBIDDEN
        )

    @action(detail=True, methods=['get'], url_path='items')
    def list_order_items(self, request, pk=None):
        try:
            order = Order.objects.get(pk=pk, user=request.user)
        except Order.DoesNotExist:
            return Response(
                {"detail": "Order not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        items = OrderItem.objects.filter(order=order)
        serializer = OrderItemSerializer(items, many=True)
        return Response(serializer.data)


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def create(self, request, *args, **kwargs):
        user = self.request.user
        try:
            order = Order.objects.get(id=request.data['order_id'], user=user)
        except Order.DoesNotExist:
            return Response(
                {"detail": "Order not found or access denied."},
                status=status.HTTP_404_NOT_FOUND
            )
        amount = order.items.aggregate(
                total=Sum(F('price_at_time') * F('quantity'))
                                        )['total']
        payment_method = request.data.get('payment_method')
        if order.payment_status == 'paid':
            return Response(
                {"detail": "Order already paid."},
                status=status.HTTP_400_BAD_REQUEST
            )
        if order.payment_status == 'unpaid':
            payment = Payment.objects.create(
                order=order,
                amount=amount,
                payment_status='unpaid',
                payment_method=payment_method
            )
            order.payment_status = 'unpaid'
            order.save()
            serializer = self.get_serializer(payment)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        if order.payment_status == 'failed':
            payment = Payment.objects.create(
                order=order,
                amount=amount,
                payment_status='failed',
                payment_method=payment_method
            )
            order.payment_status = 'failed'
            order.save()
            return Response(
                {"detail": "Payment failed."},
                status=status.HTTP_400_BAD_REQUEST
            )
        if order.payment_status == 'pending':
            payment = Payment.objects.create(
                order=order,
                amount=amount,
                payment_status='pending',
                payment_method=payment_method
            )
            order.payment_status = 'pending'
            order.save()
            serializer = self.get_serializer(payment)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            {"detail": "You do not have permission to create a payment."},
            status=status.HTTP_403_FORBIDDEN
        )


class ShippingAddressViewSet(viewsets.ModelViewSet):
    queryset = ShippingAddress.objects.all()
    serializer_class = ShippingAddressSerializer

    def create(self, request, *args, **kwargs):
        user = self.request.user
        if user.is_authenticated:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=user)
            return Response(
                {
                    "message": "Shipping address created successfully",
                    "shipping_address": serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            {"detail":
                "You do not have permission to create a shipping address."
             },
            status=status.HTTP_403_FORBIDDEN
        )

    def list(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            queryset = self.get_queryset().filter(user=user)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        return Response(
            {"detail": "You do not have permission to view shipping addresses."
             },
            status=status.HTTP_403_FORBIDDEN
        )

    def update(self, request, *args, **kwargs):
        user = self.request.user
        if user.is_authenticated:
            shipping_address = self.get_object()
            if shipping_address.user != user:
                return Response(
                    {
                     "detail":
                     "You do not have permission to edit this shipping address"
                     },
                    status=status.HTTP_403_FORBIDDEN
                )
            serializer = self.get_serializer(
                shipping_address,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        return Response(
            {
             "detail":
             "You do not have permission to edit this shipping address."
             },
            status=status.HTTP_403_FORBIDDEN
            )

    def destroy(self, request, *args, **kwargs):
        user = self.request.user
        if user.is_authenticated:
            shipping_address = self.get_object()
            if shipping_address.user != user:
                return Response(
                    {
                     "detail":
                     "You do not have permission to delete this address."},
                    status=status.HTTP_403_FORBIDDEN
                )
            shipping_address.delete()
            return Response(
                {"detail": "Shipping address deleted successfully."},
                status=status.HTTP_204_NO_CONTENT
            )
        return Response(
            {
                "detail":
                "You do not have permission to delete this shipping address."
                },
            status=status.HTTP_403_FORBIDDEN
        )


class WishlistViewSet(viewsets.ModelViewSet):
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='add')
    def add_to_wishlist(self, request):
        user = request.user
        product = request.data.get('product')

        if not product:
            return Response(
                {"detail": "Product ID is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if Wishlist.objects.filter(user=user, product=product).exists():
            return Response(
                {"detail": "Product already in wishlist."},
                status=status.HTTP_400_BAD_REQUEST
            )

        wishlist_item = Wishlist.objects.create(user=user, product_id=product)
        serializer = self.get_serializer(wishlist_item)
        return Response(
            {
                "message": "Product added to wishlist successfully.",
                "wishlist_item": serializer.data
            },
            status=status.HTTP_201_CREATED
        )


class CouponViewSet(viewsets.ModelViewSet):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'apply_coupon':
            return ApplyCouponSerializer
        return CouponSerializer

    def list(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return super().list(request, *args, **kwargs)

        return Response(
            {"detail": "You do not have permission to view coupons."},
            status=status.HTTP_403_FORBIDDEN
        )

    @action(detail=False, methods=['post'], url_path='apply')
    def apply_coupon(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data.get('code')
        try:
            coupon = Coupon.objects.get(code=code, is_active=True)
        except Coupon.DoesNotExist:
            return Response(
                {"detail": "Invalid or expired coupon code."},
                status=status.HTTP_400_BAD_REQUEST
            )
        if coupon.expiration_date < timezone.now().date():
            return Response(
                {"detail": "Coupon has expired."},
                status=status.HTTP_400_BAD_REQUEST
            )
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart.coupon = coupon
        cart.save()
        return Response({
            "message": f"Coupon '{code}' applied successfully.",
            "discount_amount": str(coupon.discount_amount)
        }, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return super().create(request, *args, **kwargs)
        return Response(
            {"detail": "You do not have permission to create coupons."},
            status=status.HTTP_403_FORBIDDEN
        )

    def update(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return super().update(request, *args, **kwargs)
        return Response(
            {"detail": "You do not have permission to update coupons."},
            status=status.HTTP_403_FORBIDDEN
        )

    def destroy(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return super().destroy(request, *args, **kwargs)
        return Response(
            {"detail": "You do not have permission to delete coupons."},
            status=status.HTTP_403_FORBIDDEN
        )
