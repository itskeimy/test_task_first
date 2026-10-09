from datetime import datetime
from decimal import Decimal

from django.utils import timezone

from receipts.admin import ReceiptAdminForm, export_receipts_to_csv
from receipts.models import Receipt, ReceiptStatus
from receipts.tests.base import BaseReceiptTestCase


class ReceiptAdminTests(BaseReceiptTestCase):
    """Тесты панели модератора и экспорта в CSV."""

    def test_reject_without_reason_fails(self):
        """Отклонение чека без указания причины вызывает ошибку формы."""
        tz = timezone.get_current_timezone()
        receipt = Receipt.objects.create(
            user=self.user_a,
            fn="9999078900010003",
            fd="1003",
            fp="2003",
            purchase_date=datetime(2026, 10, 5, 12, 0, tzinfo=tz),
            total_amount=Decimal("1500.00"),
        )

        form = ReceiptAdminForm(
            data={
                "user": self.user_a.id,
                "fn": receipt.fn,
                "fd": receipt.fd,
                "fp": receipt.fp,
                "purchase_date": receipt.purchase_date,
                "total_amount": receipt.total_amount,
                "status": ReceiptStatus.REJECTED,
                "reject_reason": "",
            },
            instance=receipt,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("reject_reason", form.errors)

    def test_reject_with_reason_succeeds(self):
        """Отклонение чека с заполненной причиной успешно проходит валидацию."""
        tz = timezone.get_current_timezone()
        receipt = Receipt.objects.create(
            user=self.user_a,
            fn="9999078900010004",
            fd="1004",
            fp="2004",
            purchase_date=datetime(2026, 10, 5, 12, 0, tzinfo=tz),
            total_amount=Decimal("1500.00"),
        )

        form = ReceiptAdminForm(
            data={
                "user": self.user_a.id,
                "fn": receipt.fn,
                "fd": receipt.fd,
                "fp": receipt.fp,
                "purchase_date": receipt.purchase_date,
                "total_amount": receipt.total_amount,
                "status": ReceiptStatus.REJECTED,
                "reject_reason": "Не читаются реквизиты кассового чека",
            },
            instance=receipt,
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_export_csv_action_includes_only_approved_receipts_with_bom(self):
        """Экспорт в CSV включает только принятые чеки и содержит UTF-8 BOM для Excel."""
        tz = timezone.get_current_timezone()
        Receipt.objects.create(
            user=self.user_a,
            fn="9999078900010005",
            fd="1005",
            fp="2005",
            purchase_date=datetime(2026, 10, 5, 12, 0, tzinfo=tz),
            total_amount=Decimal("2000.00"),
            status=ReceiptStatus.APPROVED,
        )
        Receipt.objects.create(
            user=self.user_a,
            fn="9999078900010006",
            fd="1006",
            fp="2006",
            purchase_date=datetime(2026, 10, 5, 12, 0, tzinfo=tz),
            total_amount=Decimal("2000.00"),
            status=ReceiptStatus.PENDING,
        )

        queryset = Receipt.objects.filter(fn__in=["9999078900010005", "9999078900010006"])
        response = export_receipts_to_csv(None, None, queryset)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv; charset=utf-8")

        content = response.content.decode("utf-8-sig")
        rows = content.strip().split("\r\n")
        self.assertEqual(len(rows), 2)  # Заголовок + 1 принятый чек
        self.assertIn("9999078900010005", rows[1])
        self.assertNotIn("9999078900010006", content)
