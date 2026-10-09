from datetime import datetime
from decimal import Decimal

from django.conf import settings
from django.utils import timezone

# Пагинация по ТЗ: ровно 10 чеков на страницу
RECEIPTS_PER_PAGE = 10
# Разница между сервером (Europe/Moscow, UTC+3) и самым восточным поясом РФ (Камчатка UTC+12): 12 - 3 = 9 часов
RUSSIA_MAX_TZ_OFFSET_HOURS = 9
RISSIA_MAX_TZ_OFFSET = 9


def get_promo_config():
    """
    Централизованное получение настроек промо-акции из settings / .env:
    - start_dt: объект datetime с учетом часового пояса (или None)
    - end_dt: объект datetime с учетом часового пояса (или None)
    - min_amount: Decimal минимальной суммы покупки
    - start_display: строка формата 'ДД.ММ.ГГГГ' для отображения в интерфейсе
    - end_display: строка формата 'ДД.ММ.ГГГГ' для отображения в интерфейсе
    - start_iso / end_iso: исходные ISO-строки для data-атрибутов HTML-форм
    """
    raw_start = getattr(settings, "PROMO_START_DATE", None)
    raw_end = getattr(settings, "PROMO_END_DATE", None)
    raw_min = getattr(settings, "MIN_AMOUNT", "1000.00")

    start_dt = None
    end_dt = None
    tz = timezone.get_current_timezone()

    if raw_start:
        try:
            start_dt = datetime.fromisoformat(raw_start)
            if timezone.is_naive(start_dt):
                start_dt = timezone.make_aware(start_dt, tz)
        except (ValueError, TypeError):
            pass

    if raw_end:
        try:
            end_dt = datetime.fromisoformat(raw_end)
            if timezone.is_naive(end_dt):
                end_dt = timezone.make_aware(end_dt, tz)
        except (ValueError, TypeError):
            pass

    try:
        min_amount = Decimal(str(raw_min))
    except Exception:
        min_amount = Decimal("1000.00")

    return {
        "start_dt": start_dt,
        "end_dt": end_dt,
        "start_display": start_dt.strftime("%d.%m.%Y") if start_dt else "",
        "end_display": end_dt.strftime("%d.%m.%Y") if end_dt else "",
        "start_iso": raw_start or "",
        "end_iso": raw_end or "",
        "min_amount": min_amount,
    }


def clean_purchase_date_for_russia(self):
    purchase_date = self.cleaned_data.get("purchase_date")
    if not purchase_date:
        return purchase_date
