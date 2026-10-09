from decimal import Decimal
from datetime import datetime
from django import forms
from django.conf import settings
from django.utils import timezone
from .models import Receipt


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

        min_amount = Decimal(str(getattr(settings, 'MIN_AMOUNT', '1000.00')))
        if amount < min_amount:
            raise forms.ValidationError(
                f'Сумма чека для участия в акции должна быть не менее {min_amount} ₽.'
            )
        return amount

    def clean_purchase_date(self):
        purchase_date = self.cleaned_data.get('purchase_date')
        if not purchase_date:
            return purchase_date

        # Проверка: чек не может быть из будущего
        now = timezone.now() if timezone.is_aware(purchase_date) else datetime.now()
        if purchase_date > now:
            raise forms.ValidationError('Дата покупки не может быть в будущем.')

        # Считываем строки дат из настроек и преобразуем в datetime
        start_str = getattr(settings, 'PROMO_START_DATE', None)
        end_str = getattr(settings, 'PROMO_END_DATE', None)

        if start_str and end_str:
            try:
                start_date = datetime.fromisoformat(start_str)
                end_date = datetime.fromisoformat(end_str)

                # Согласовываем таймзоны (если purchase_date с часовым поясом)
                if timezone.is_aware(purchase_date):
                    tz = timezone.get_current_timezone()
                    if timezone.is_naive(start_date):
                        start_date = timezone.make_aware(start_date, tz)
                    if timezone.is_naive(end_date):
                        end_date = timezone.make_aware(end_date, tz)

                if not (start_date <= purchase_date <= end_date):
                    raise forms.ValidationError(
                        f'Чек должен быть оформлен в период акции '
                        f'(с {start_date.strftime("%d.%m.%Y")} по {end_date.strftime("%d.%m.%Y")}).'
                    )
            except ValueError:
                pass

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