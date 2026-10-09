from decimal import Decimal
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class ReceiptStatus(models.TextChoices):
    PENDING = 'pending', 'На проверке'
    APPROVED = 'approved', 'Принят'
    REJECTED = 'rejected', 'Отклонен'


class Receipt(models.Model):
    id : int
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='receipts',
        verbose_name='Пользователь'
    )

    # реквизиты просто charfield
    fn = models.CharField(max_length=20, verbose_name='ФН')
    fd = models.CharField(max_length=20, verbose_name='ФД')
    fp = models.CharField(max_length=20, verbose_name='ФП')

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Сумма',
        validators=[MinValueValidator(Decimal('1000.00'))]
    )
    purchase_date = models.DateTimeField(verbose_name='Дата и время покупки')

    # Модерация
    status = models.CharField(
        max_length=20,
        choices=ReceiptStatus.choices,
        default=ReceiptStatus.PENDING,
        verbose_name='Статус',
        db_index=True
    )
    reject_reason = models.TextField(
        verbose_name='Причина отклонения',
        blank=True,
        null=True
    )

    # Служебные даты
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата регистрации',
        db_index=True
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    class Meta:
        verbose_name = 'Чек'
        verbose_name_plural = 'Чеки'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['fn', 'fd', 'fp'],
                name='unique_fn_fd_fp_receipt'
            )
        ]

    def __str__(self):
        return f"Чек #{self.id} ({self.fn}/{self.fd}/{self.fp}) — {self.total_amount} ₽"