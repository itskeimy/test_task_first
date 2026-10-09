from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    """
    Стандартная форма регистрации Django, привязанная к нашей кастомной модели User.
    """

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")
