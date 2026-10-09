import csv

from django import forms
from django.contrib import admin
from django.http import HttpResponse

from .models import Receipt, ReceiptStatus


class ReceiptAdminForm(forms.ModelForm):
    """Кастомная форма для админки с валидацией бизнес-логики: если чек отклонен, обязательно требуем указать причину"""

    class Meta:
        model = Receipt
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean() or {}
        status = cleaned_data.get("status")
        reject_reason = cleaned_data.get("reject_reason")

        if status == ReceiptStatus.REJECTED and not (reject_reason and reject_reason.strip()):
            self.add_error("reject_reason", "Обязательно укажите причину отклонения")

        return cleaned_data


@admin.action(description="Экспорт отмеченных принятых чеков в CSV")
def export_receipts_to_csv(modeladmin, request, queryset):
    """
    доп фича: экспорт чеков для подведения итогов акции
    """
    approved_receipts = queryset.filter(status=ReceiptStatus.APPROVED)

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="approved_receipts.csv"'
    # BOM-символ для корректного отображения кириллицы в Excel
    response.write("\ufeff")

    writer = csv.writer(response, delimiter=";")
    writer.writerow(["ID", "Пользователь", "ФН", "ФД", "ФП", "Сумма", "Дата покупки", "Дата регистрации"])

    for r in approved_receipts:
        writer.writerow(
            [
                r.id,
                r.user.username,
                r.fn,
                r.fd,
                r.fp,
                r.total_amount,
                r.purchase_date.strftime("%Y-%m-%d %H:%M"),
                r.created_at.strftime("%Y-%m-%d %H:%M"),
            ]
        )

    return response


@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    form = ReceiptAdminForm

    # Решение проблемы N+1: загрузка связанных пользователей через JOIN
    list_select_related = ("user",)

    list_display = (
        "id",
        "user",
        "total_amount",
        "purchase_date",
        "status",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("fn", "fd", "fp", "user__username", "user__email")
    readonly_fields = ("created_at", "updated_at")
    actions = [export_receipts_to_csv]
