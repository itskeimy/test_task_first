from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from .forms import ReceiptCreateForm
from .models import Receipt
from .utils import RECEIPTS_PER_PAGE, get_promo_config


@login_required
def cabinet_view(request):
    """
    Личный кабинет участника акции
    """
    user_receipts = Receipt.objects.filter(user=request.user).order_by("-created_at")
    paginator = Paginator(user_receipts, RECEIPTS_PER_PAGE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    promo = get_promo_config()

    context = {
        "receipts": page_obj.object_list,
        "page_obj": page_obj,
        "paginator": paginator,
        "is_paginated": page_obj.has_other_pages(),
        "promo_start_display": promo["start_display"],
        "promo_end_display": promo["end_display"],
        "promo_start_iso": promo["start_iso"],
        "promo_end_iso": promo["end_iso"],
        "min_amount": promo["min_amount"],
    }
    return render(request, "receipts/cabinet.html", context)


@login_required
@require_POST
def receipt_register_view(request):
    """
    Обработка AJAX-запроса на регистрацию чека
    """
    form = ReceiptCreateForm(request.POST)
    if form.is_valid():
        receipt = form.save(commit=False)
        receipt.user = request.user
        receipt.save()
        return JsonResponse({"success": True, "message": "Чек успешно зарегистрирован и отправлен на проверку!"})

    return JsonResponse({"success": False, "errors": form.errors}, status=400)


@login_required
def receipts_api_view(request):
    """
    API /api/receipts/
    """
    user_receipts = Receipt.objects.filter(user=request.user).order_by("-created_at")

    results = []
    for r in user_receipts:
        results.append(
            {
                "id": r.id,
                "fn": r.fn,
                "fd": r.fd,
                "fp": r.fp,
                "purchase_date": r.purchase_date.isoformat(),
                "amount": str(r.total_amount),
                "status": r.status,
                "status_display": r.get_status_display(),
                "reject_reason": r.reject_reason if r.status == "rejected" else "",
                "created_at": r.created_at.isoformat(),
            }
        )

    return JsonResponse(
        {
            "count": user_receipts.count(),
            "next": None,
            "previous": None,
            "results": results,
        }
    )
