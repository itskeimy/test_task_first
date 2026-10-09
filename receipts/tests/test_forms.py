from datetime import datetime, timedelta
from decimal import Decimal

from django.utils import timezone

from receipts.forms import ReceiptCreateForm
from receipts.models import Receipt, ReceiptStatus
from receipts.tests.base import BaseReceiptTestCase
from receipts.utils import RUSSIA_MAX_TZ_OFFSET_HOURS


class ReceiptFormValidationTests(BaseReceiptTestCase):
    """Тесты валидации реквизитов, сумм, дат и граничных значений чека."""

    def test_valid_payload_passes(self):
        """Корректный чек успешно валидируется."""
        form = ReceiptCreateForm(data=self.get_valid_payload())
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["total_amount"], Decimal("1550.00"))

    # --- Граничные значения суммы (Amount edge cases) ---

    def test_amount_boundary_999_99_rejected(self):
        """Граничное значение: 999.99 ₽ (на 1 коп. меньше порога) отклоняется."""
        form = ReceiptCreateForm(data=self.get_valid_payload(total_amount="999.99 ₽"))
        self.assertFalse(form.is_valid())
        self.assertIn("total_amount", form.errors)

    def test_amount_boundary_1000_00_accepted(self):
        """Граничное значение: ровно 1000.00 ₽ принимается."""
        form = ReceiptCreateForm(data=self.get_valid_payload(total_amount="1000.00 ₽"))
        self.assertTrue(form.is_valid(), form.errors)

    def test_amount_boundary_1000_01_accepted(self):
        """Граничное значение: 1000.01 ₽ (на 1 коп. выше порога) принимается."""
        form = ReceiptCreateForm(data=self.get_valid_payload(total_amount="1000.01"))
        self.assertTrue(form.is_valid(), form.errors)

    def test_amount_zero_and_negative_rejected(self):
        """Нулевая и отрицательная сумма отклоняются."""
        for val in ["0.00", "-100.00"]:
            form = ReceiptCreateForm(data=self.get_valid_payload(total_amount=val))
            self.assertFalse(form.is_valid())
            self.assertIn("total_amount", form.errors)

    # --- Граничные значения дат и таймзон (Date & Timezone edge cases) ---

    def test_date_boundary_promo_start_accepted(self):
        """Граничное значение: первая секунда старта акции (01.09.2026 00:00) принимается."""
        form = ReceiptCreateForm(data=self.get_valid_payload(purchase_date="01.09.2026 00:00"))
        self.assertTrue(form.is_valid(), form.errors)

    def test_date_boundary_before_promo_start_rejected(self):
        """Граничное значение: день накануне старта акции (31.08.2026 23:59) отклоняется."""
        form = ReceiptCreateForm(data=self.get_valid_payload(purchase_date="31.08.2026 23:59"))
        self.assertFalse(form.is_valid())
        self.assertIn("purchase_date", form.errors)

    def test_kamchatka_tz_offset_now_plus_9h_accepted(self):
        """Граничное значение: текущее время Камчатки (now + 9 часов) принимается."""
        now = timezone.localtime(timezone.now())
        max_kamchatka = (now + timedelta(hours=RUSSIA_MAX_TZ_OFFSET_HOURS)).strftime("%d.%m.%Y %H:%M")
        form = ReceiptCreateForm(data=self.get_valid_payload(purchase_date=max_kamchatka))
        self.assertTrue(form.is_valid(), form.errors)

    def test_future_beyond_kamchatka_rejected(self):
        """Превышение времени Камчатки (now + 9 ч. 10 мин.) отклоняется."""
        now = timezone.localtime(timezone.now())
        future_time = (now + timedelta(hours=RUSSIA_MAX_TZ_OFFSET_HOURS, minutes=10)).strftime("%d.%m.%Y %H:%M")
        form = ReceiptCreateForm(data=self.get_valid_payload(purchase_date=future_time))
        self.assertFalse(form.is_valid())
        self.assertIn("purchase_date", form.errors)

    # --- Граничные значения длин реквизитов (FN / FD / FP edge cases) ---

    def test_fn_length_15_and_17_digits_rejected(self):
        """ФН длиной 15 и 17 цифр (грань от 16) отклоняются."""
        for fn_val in ["1" * 15, "1" * 17]:
            form = ReceiptCreateForm(data=self.get_valid_payload(fn=fn_val))
            self.assertFalse(form.is_valid())
            self.assertIn("fn", form.errors)

    def test_fn_non_digits_rejected(self):
        """ФН, содержащий буквы, отклоняется."""
        form = ReceiptCreateForm(data=self.get_valid_payload(fn="123456789012345A"))
        self.assertFalse(form.is_valid())
        self.assertIn("fn", form.errors)

    def test_fd_and_fp_max_length_10_accepted_11_rejected(self):
        """ФД и ФП длиной 10 цифр принимаются, 11 цифр отклоняются."""
        # 10 цифр (верхняя граница)
        form_valid = ReceiptCreateForm(data=self.get_valid_payload(fd="9" * 10, fp="8" * 10))
        self.assertTrue(form_valid.is_valid(), form_valid.errors)

        # 11 цифр (превышение границы)
        form_invalid = ReceiptCreateForm(data=self.get_valid_payload(fd="9" * 11, fp="8" * 11))
        self.assertFalse(form_invalid.is_valid())
        self.assertIn("fd", form_invalid.errors)
        self.assertIn("fp", form_invalid.errors)

    # --- Уникальность тройки реквизитов (Uniqueness edge cases) ---

    def test_duplicate_exact_triplet_rejected(self):
        """Повторный ввод идентичной тройки (ФН, ФД, ФП) возвращает ошибку формы без 500."""
        payload = self.get_valid_payload()
        Receipt.objects.create(
            user=self.user_a,
            fn=payload["fn"],
            fd=payload["fd"],
            fp=payload["fp"],
            purchase_date=datetime(2026, 10, 5, 12, 0, tzinfo=timezone.get_current_timezone()),
            total_amount=Decimal("1500.00"),
            status=ReceiptStatus.PENDING,
        )

        form = ReceiptCreateForm(data=payload)
        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)

    def test_same_fn_fd_different_fp_accepted(self):
        """Совпадение ФН и ФД при различном ФП принимается (уникальна только вся тройка)."""
        payload = self.get_valid_payload()
        Receipt.objects.create(
            user=self.user_a,
            fn=payload["fn"],
            fd=payload["fd"],
            fp="1111111111",
            purchase_date=datetime(2026, 10, 5, 12, 0, tzinfo=timezone.get_current_timezone()),
            total_amount=Decimal("1500.00"),
        )

        form = ReceiptCreateForm(data=payload)
        self.assertTrue(form.is_valid(), form.errors)
