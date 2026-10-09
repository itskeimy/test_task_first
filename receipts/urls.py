from django.urls import path

from . import views

app_name = 'receipts'

urlpatterns = [
    path('', views.cabinet_view, name='cabinet'),
    path('cabinet/', views.cabinet_view, name='cabinet_alias'),
    path('register/', views.receipt_register_view, name='register'),
    path('api/receipts/', views.receipts_api_view, name='api_receipts'),
]
