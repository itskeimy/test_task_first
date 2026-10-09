from decimal import Decimal
from datetime import datetime, timedelta
from django import forms
from django.conf import settings
from django.utils import timezone
from .models import Receipt
from .utils import get_promo_config, RUSSIA_MAX_TZ_OFFSET_HOURS


class ReceiptCreateForm(forms.ModelForm):
    purchase_date = forms.DateTimeField(
        input_formats=[
            '%d.%m.%Y %H:%M',
            '%d.%m.%Y',
            '%Y-%m-%dT%H:%M',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M'
        ]
    )

    total_amount = forms.CharField(
        widget=forms.TextInput(
            attrs={'placeholder': '1 000.00 ₽', 'class': 'form-input'}
        )
    )

    class Meta:
        model = Receipt
        fields = ('fn', 'fd', 'fp', 'purchase_date', 'total_amount')
        widgets = {
            'purchase_date': forms.TextInput(
                attrs={'placeholder': 'дд.мм.гггг чч:мм', 'class': 'form-input'}
            ),
            'fn': forms.TextInput(attrs={'placeholder': '16 цифр'}),
            'fd': forms.TextInput(attrs={'placeholder': 'номер ФД'}),
            'fp': forms.TextInput(attrs={'placeholder': 'номер ФП'}),
        }

    def clean_fn(self):
        fn = self.cleaned_data.get('fn', '').strip()
        if not fn.isdigit():
            raise forms.ValidationError('ФН должен состоять только из цифр.')
        if len(fn) != 16:
            raise forms.ValidationError('ФН должен состоять ровно из 16 цифр.')
        return fn

    def clean_fd(self):
        fd = self.cleaned_data.get('fd', '').strip()
        if not fd.isdigit():
            raise forms.ValidationError('ФД должен состоять только из цифр.')
        return fd

    def clean_fp(self):
        fp = self.cleaned_data.get('fp', '').strip()
        if not fp.isdigit():
            raise forms.ValidationError('ФП должен состоять только из цифр.')
        return fp

    def clean_total_amount(self):
        raw_val = self.cleaned_data.get('total_amount', '')
        if isinstance(raw_val, (int, float, Decimal)):
            amount = Decimal(str(raw_val))
        else:
            clean_str = str(raw_val).replace('₽', '').replace(' ', '').replace('\xa0', '').replace(',', '.').strip()
            try:
                amount = Decimal(clean_str)
            except Exception:
                raise forms.ValidationError('Введите корректную сумму чека (например, 1000.00).')

        promo = get_promo_config()
        if amount < promo['min_amount']:
            raise forms.ValidationError(
                f'Сумма чека для участия в акции должна быть не менее {promo["min_amount"]} ₽.'
            )
        return amount

    def clean_purchase_date(self):
        purchase_date = self.cleaned_data.get('purchase_date')
        if not purchase_date:
            return purchase_date

        # 1. Проверка на будущее время с учетом часовых поясов РФ:
        # Самый восточный пояс (Камчатка UTC+12) опережает сервер (Europe/Moscow UTC+3) на 9 часов.
        # Чек не может быть выбит позже времени, которое наступило в самой дальней точке страны.
        now = timezone.now() if timezone.is_aware(purchase_date) else datetime.now()
        max_allowed_time = now + timedelta(hours=RUSSIA_MAX_TZ_OFFSET_HOURS)
        if purchase_date > max_allowed_time:
            raise forms.ValidationError('Дата покупки не может быть в будущем.')

        # 2. Проверка периода акции по местному календарному дню:
        # Кассовый чек по 54-ФЗ печатает локальное время кассы без таймзоны.
        # Проверяем, что календарный день покупки входит в диапазон акции (с start_date по end_date).
        promo = get_promo_config()
        if promo['start_dt'] and promo['end_dt']:
            purchase_day = purchase_date.date()
            promo_start_day = promo['start_dt'].date()
            promo_end_day = promo['end_dt'].date()

            if not (promo_start_day <= purchase_day <= promo_end_day):
                raise forms.ValidationError(
                    f'Чек должен быть оформлен в период акции '
                    f'(с {promo["start_display"]} по {promo["end_display"]}).'
                )

        return purchase_date

    def clean(self):
        cleaned_data = super().clean() or {}
        fn = cleaned_data.get('fn')
        fd = cleaned_data.get('fd')
        fp = cleaned_data.get('fp')

        # Проверка уникальности по 54-ФЗ (защита от падения базы с 500-й ошибкой)
        if fn and fd and fp:
            if Receipt.objects.filter(fn=fn, fd=fd, fp=fp).exists():
                raise forms.ValidationError(
                    'Чек с такими реквизитами (ФН, ФД, ФП) уже зарегистрирован в акции!'
                )

        return cleaned_data