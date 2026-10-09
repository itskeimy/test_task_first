from datetime import datetime
from decimal import Decimal

from django.test import Client
from django.urls import reverse
from django.utils import timezone

from receipts.models import Receipt, ReceiptStatus
from receipts.tests.base import BaseReceiptTestCase


class ReceiptViewsTests(BaseReceiptTestCase):
    """Тесты представлений личного кабинета и AJAX эндпоинта регистрации."""

    def test_unauthenticated_user_redirected_to_login(self):
        """Неавторизованный запрос в кабинет перенаправляется на вход."""
        response = Client().get(reverse("receipts:cabinet"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)

    def test_cabinet_shows_only_current_user_receipts(self):
        """Кабинет отображает только чеки текущего пользователя."""
        tz = timezone.get_current_timezone()
        Receipt.objects.create(
            user=self.user_a,
            fn="1111111111111111",
            fd="101",
            fp="201",
            purchase_date=datetime(2026, 10, 5, 12, 0, tzinfo=tz),
            total_amount=Decimal("1200.00"),
        )
        Receipt.objects.create(
            user=self.user_b,
            fn="2222222222222222",
            fd="102",
            fp="202",
            purchase_date=datetime(2026, 10, 5, 13, 0, tzinfo=tz),
            total_amount=Decimal("1800.00"),
        )

        response = self.client_a.get(reverse("receipts:cabinet"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "1200")
        self.assertNotContains(response, "1800")

    # --- Граничные случаи пагинации (Pagination edge cases) ---

    def test_pagination_exactly_10_receipts_single_page(self):
        """Граничное значение: ровно 10 чеков отображаются на одной странице."""
        tz = timezone.get_current_timezone()
        Receipt.objects.bulk_create(
            [
                Receipt(
                    user=self.user_a,
                    fn=f"{i:016d}",
                    fd=str(i),
                    fp=str(i),
                    purchase_date=datetime(2026, 10, 5, 10, 0, tzinfo=tz),
                    total_amount=Decimal("1000.00"),
                )
                for i in range(1, 11)
            ]
        )

        response = self.client_a.get(reverse("receipts:cabinet"))
        self.assertEqual(len(response.context["receipts"]), 10)
        self.assertFalse(response.context["is_paginated"])

    def test_pagination_11_receipts_spans_two_pages(self):
        """Граничное значение: 11 чеков создают вторую страницу с 1 чеком."""
        tz = timezone.get_current_timezone()
        Receipt.objects.bulk_create(
            [
                Receipt(
                    user=self.user_a,
                    fn=f"{i:016d}",
                    fd=str(i),
                    fp=str(i),
                    purchase_date=datetime(2026, 10, 5, 10, 0, tzinfo=tz),
                    total_amount=Decimal("1000.00"),
                )
                for i in range(1, 12)
            ]
        )

        res_p1 = self.client_a.get(reverse("receipts:cabinet"))
        self.assertEqual(len(res_p1.context["receipts"]), 10)
        self.assertTrue(res_p1.context["is_paginated"])

        res_p2 = self.client_a.get(reverse("receipts:cabinet") + "?page=2")
        self.assertEqual(len(res_p2.context["receipts"]), 1)

    def test_pagination_invalid_page_number_returns_last_page(self):
        """Невалидный номер страницы (?page=999) отдает последнюю страницу без 404."""
        tz = timezone.get_current_timezone()
        Receipt.objects.bulk_create(
            [
                Receipt(
                    user=self.user_a,
                    fn=f"{i:016d}",
                    fd=str(i),
                    fp=str(i),
                    purchase_date=datetime(2026, 10, 5, 10, 0, tzinfo=tz),
                    total_amount=Decimal("1000.00"),
                )
                for i in range(1, 12)
            ]
        )

        response = self.client_a.get(reverse("receipts:cabinet") + "?page=999")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["receipts"]), 1)

    # --- Регистрация чека по AJAX ---

    def test_ajax_register_valid_receipt_success(self):
        """Валидный POST-запрос возвращает HTTP 200 и связывает чек с текущим пользователем."""
        payload = self.get_valid_payload()
        response = self.client_a.post(reverse("receipts:register"), data=payload)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])

        receipt = Receipt.objects.get(fn=payload["fn"])
        self.assertEqual(receipt.user, self.user_a)
        self.assertEqual(receipt.status, ReceiptStatus.PENDING)

    def test_ajax_register_invalid_amount_returns_400(self):
        """Сумма ниже порога возвращает HTTP 400 со словарем ошибок."""
        payload = self.get_valid_payload(total_amount="500.00 ₽")
        response = self.client_a.post(reverse("receipts:register"), data=payload)
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["success"])
        self.assertIn("total_amount", response.json()["errors"])

    def test_ajax_register_get_method_not_allowed(self):
        """GET-запрос на эндпоинт регистрации чека отклоняется с кодом 405."""
        response = self.client_a.get(reverse("receipts:register"))
        self.assertEqual(response.status_code, 405)
