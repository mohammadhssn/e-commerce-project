from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

from apps.catalogue.models import ProductInventory


class Order(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='order_user',
        verbose_name=_('user')
    )
    full_name = models.CharField(
        max_length=50,
        verbose_name=_('full name')
    )
    email = models.EmailField(
        max_length=255,
        blank=True,
        verbose_name=_('email')
    )
    address = models.CharField(
        max_length=255,
        verbose_name=_('address')
    )
    city = models.CharField(
        max_length=100,
        verbose_name=_('city')
    )
    phone = models.CharField(
        max_length=12,
        verbose_name=_('phone')
    )
    postal_code = models.CharField(
        max_length=20,
        verbose_name=_('postal code')
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('created')
    )
    updated = models.DateTimeField(
        auto_now=True,
        verbose_name=_('updated')
    )
    total_paid = models.IntegerField(
        verbose_name=_('total paid'),
        help_text=_('format:price Toman'),
    )
    order_key = models.CharField(
        max_length=200,
        verbose_name=_('order key')
    )
    payment_option = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('payment option')
    )
    billing_status = models.BooleanField(
        default=False,
        verbose_name=_('billing status')
    )
    discount = models.IntegerField(
        blank=True,
        null=True,
        default=None,
        verbose_name=_('Discount coupon percentage'),
        help_text=_('format: not required')
    )

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return f'{self.user} : {str(self.created)}'


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('order')
    )
    product = models.ForeignKey(
        ProductInventory,
        on_delete=models.CASCADE,
        related_name='order_items',
        verbose_name=_('product')
    )
    price = models.IntegerField(
        verbose_name=_('price'),
        help_text=_('format:price Toman'),
    )
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name=_('quantity')
    )

    def __str__(self):
        return f'{self.order.user} : {str(self.pk)}'


class Coupon(models.Model):
    code = models.CharField(
        max_length=50,
        unique=True
    )
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    discount = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    active = models.BooleanField(default=False)

    def __str__(self):
        return self.code
