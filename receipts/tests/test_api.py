from datetime import datetime
from decimal import Decimal

from django.test import Client
from django.urls import reverse
from django.utils import timezone

from receipts.models import Receipt, ReceiptStatus
from receipts.tests.base import BaseReceiptTestCase


class ReceiptsApiTests(BaseReceiptTestCase):
    """Тесты эндпоинта GET /api/receipts/ и строгой изоляции данных."""

    def test_unauthenticated_request_redirected(self):
        """Неавторизованный запрос к API перенаправляется на форму входа."""
        response = Client().get(reverse("receipts:api_receipts"))
        self.assertEqual(response.status_code, 302)

    def test_api_strict_user_isolation(self):
        """Пользователь Б не имеет доступа к чекам пользователя А."""
        tz = timezone.get_current_timezone()
        Receipt.objects.create(
            user=self.user_a,
            fn="9999078900010001",
            fd="1001",
            fp="2001",
            purchase_date=datetime(2026, 10, 5, 12, 0, tzinfo=tz),
            total_amount=Decimal("1500.00"),
            status=ReceiptStatus.APPROVED,
        )

        res_a = self.client_a.get(reverse("receipts:api_receipts"))
        self.assertEqual(res_a.status_code, 200)
        self.assertEqual(res_a.json()["count"], 1)

        res_b = self.client_b.get(reverse("receipts:api_receipts"))
        self.assertEqual(res_b.status_code, 200)
        self.assertEqual(res_b.json()["count"], 0)
        self.assertEqual(len(res_b.json()["results"]), 0)

    def test_api_response_schema_matches_tz_specification(self):
        """Структура JSON-ответа точно соответствует пункту 6.2 ТЗ."""
        tz = timezone.get_current_timezone()
        Receipt.objects.create(
            user=self.user_a,
            fn="9999078900010002",
            fd="1002",
            fp="2002",
            purchase_date=datetime(2026, 10, 5, 12, 0, tzinfo=tz),
            total_amount=Decimal("1750.50"),
            status=ReceiptStatus.APPROVED,
        )

        response = self.client_a.get(reverse("receipts:api_receipts"))
        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Корневые ключи по ТЗ
        for key in ["count", "next", "previous", "results"]:
            self.assertIn(key, data)

        item = data["results"][0]
        expected_fields = [
            "id",
            "fn",
            "fd",
            "fp",
            "purchase_date",
            "amount",
            "status",
            "status_display",
            "reject_reason",
            "created_at",
        ]
        for field in expected_fields:
            self.assertIn(field, item)

        self.assertEqual(item["fn"], "9999078900010002")
        self.assertEqual(item["amount"], "1750.50")
        self.assertEqual(item["status_display"], "Принят")
