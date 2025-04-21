from celery import shared_task
from .models import ProductVariant


@shared_task
def refill_stock(threshold=10, refill_to=100):
    """
    Refill stock for products with stock below the threshold.
    """
    products = ProductVariant.objects.filter(stock_count__lt=threshold)
    for product in products:
        product.stock_count = refill_to
        product.save()
    return f"Refilled stock for {products.count()} products."
