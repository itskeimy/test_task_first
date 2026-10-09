from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import redirect, render

from .forms import CustomUserCreationForm


def register_view(request):
    if request.user.is_authenticated:
        return redirect("receipts:cabinet")

    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Добро пожаловать, {user.username}! Вы успешно зарегистрированы.")
            return redirect("receipts:cabinet")
    else:
        form = CustomUserCreationForm()

    return render(request, "registration/register.html", {"form": form})
