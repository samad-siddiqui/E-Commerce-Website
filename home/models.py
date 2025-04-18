from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User  # Import the default User model


class OrderStatus(models.TextChoices):
    Pending = 'Pending'
    Shipped = 'Shipped'
    Delivered = 'Delivered'
    Canceled = 'Canceled'


class PaymentStatus(models.TextChoices):
    Paid = 'Paid'
    Unpaid = 'Unpaid'
    Refunded = 'Refunded'
    Pending = 'Pending'
    Failed = 'Failed'


class PaymentMethod(models.TextChoices):
    COD = 'COD'
    Card = 'Card'
    PayPal = 'PayPal'


class Profile(models.Model):
    """
    Profile model to store additional user information.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                related_name='profile')
    bio = models.TextField(blank=True)
    # profile_picture = models.ImageField(upload_to='profile_pictures/',
    # blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Profile of {self.user.username}"


class Category(models.Model):
    """
    Category model to store categories for products.
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE,
                               null=True, blank=True,
                               related_name='subcategories')
    description = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Product model to store product information.
    """
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE,
                                 related_name='products')
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2,
                                         null=True, blank=True)
    tags = models.ManyToManyField("Tag", blank=True)
    inventory_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                related_name='variants')
    varient_name = models.CharField(max_length=255)
    varient_value = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{
            self.product.name} - {self.varient_name}: {self.varient_value}"


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='carts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    coupon = models.ForeignKey("Coupon", null=True, blank=True,
                               on_delete=models.SET_NULL)

    def __str__(self):
        return f"Cart for {self.user.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE,
                             related_name='items')
    product_variant = models.ForeignKey(ProductVariant,
                                        on_delete=models.CASCADE,
                                        related_name='cart_items')
    quantity = models.PositiveIntegerField(default=1)
    price_at_time = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product_variant.product.name} - {self.quantity}"


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='orders')
    order_status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.Pending
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.Unpaid
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE,
                              related_name='items')
    product_variant = models.ForeignKey(ProductVariant,
                                        on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price_at_time = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product_variant.name} - {self.quantity}"


class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE,
                              related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.Pending
    )
    payment_method = models.CharField(max_length=255,
                                      choices=PaymentMethod.choices,
                                      default=PaymentMethod.COD)
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for Order #{self.order.id}"


class ShippingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='shipping_addresses')
    address_line1 = models.CharField(max_length=700)
    address_line2 = models.CharField(max_length=700, blank=True, null=True)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=255)

    def __str__(self):
        return f"Shipping Address for {self.user.username}"


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='reviews')
    rating = models.PositiveIntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Review for {self.product.name} by {self.user.username}"


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='wishlists')
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                related_name='wishlists')

    def __str__(self):
        return f"Wishlist for {self.user.username} - {self.product.name}"


class Coupon(models.Model):
    code = models.CharField(max_length=10, unique=True)
    discount_amount = models.DecimalField(max_digits=5, decimal_places=2)
    expiration_date = models.DateField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.code


class Tag(models.Model):
    """
    Tag model to store tags for products.
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
