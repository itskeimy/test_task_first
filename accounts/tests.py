from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class AccountsAuthTests(TestCase):
    """
    Тестирование регистрации, входа и выхода пользователей.
    """

    def setUp(self):
        self.client = Client()
        self.register_url = reverse("accounts:register")
        self.login_url = reverse("accounts:login")
        self.logout_url = reverse("accounts:logout")
        self.cabinet_url = reverse("receipts:cabinet")

    def test_registration_creates_user_and_auto_logs_in(self):
        """Успешная регистрация создает пользователя и перенаправляет в личный кабинет."""
        payload = {
            "username": "new_participant",
            "email": "participant@example.com",
            "password1": "SecurePass123!",
            "password2": "SecurePass123!",
        }
        response = self.client.post(self.register_url, data=payload)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.cabinet_url)

        # Проверяем, что пользователь создан в БД
        self.assertTrue(User.objects.filter(username="new_participant").exists())

        # Проверяем, что пользователь сразу авторизован в сессии
        cabinet_res = self.client.get(self.cabinet_url)
        self.assertEqual(cabinet_res.status_code, 200)
        self.assertEqual(cabinet_res.context["user"].username, "new_participant")

    def test_registration_password_mismatch_fails(self):
        """Регистрация с несовпадающими паролями возвращает ошибку формы."""
        payload = {
            "username": "bad_participant",
            "email": "bad@example.com",
            "password1": "SecurePass123!",
            "password2": "DifferentPass456!",
        }
        response = self.client.post(self.register_url, data=payload)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="bad_participant").exists())
        self.assertFormError(response.context["form"], "password2", "Введенные пароли не совпадают.")

    def test_authenticated_user_redirected_from_register_page(self):
        """Авторизованного пользователя редиректит со страницы регистрации в кабинет."""
        User.objects.create_user(username="logged_in", password="Password123!")
        self.client.login(username="logged_in", password="Password123!")

        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.cabinet_url)

    def test_login_and_logout_flow(self):
        """Проверка стандартного входа и безопасного выхода через POST."""
        User.objects.create_user(username="test_user", password="Password123!")

        # Логин
        login_res = self.client.post(self.login_url, {"username": "test_user", "password": "Password123!"})
        self.assertEqual(login_res.status_code, 302)
        self.assertRedirects(login_res, self.cabinet_url)

        # Логаут через POST
        logout_res = self.client.post(self.logout_url)
        self.assertEqual(logout_res.status_code, 302)

        # После выхода личный кабинет снова недоступен
        cab_res = self.client.get(self.cabinet_url)
        self.assertEqual(cab_res.status_code, 302)
