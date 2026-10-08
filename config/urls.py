"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path
from django.views.debug import default_urlconf

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', default_urlconf, name='index'),
]
