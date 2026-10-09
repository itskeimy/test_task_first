from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class BaseReceiptTestCase(TestCase):
    """Базовые фикстуры пользователей и клиентов."""

    def setUp(self):
        self.user_a = User.objects.create_user(
            username="user_alice", email="alice@example.com", password="Password123!"
        )
        self.user_b = User.objects.create_user(username="user_bob", email="bob@example.com", password="Password123!")
        self.moderator = User.objects.create_user(
            username="mod_carol", email="carol@example.com", password="Password123!", is_staff=True
        )

        self.client_a = Client()
        self.client_a.login(username="user_alice", password="Password123!")

        self.client_b = Client()
        self.client_b.login(username="user_bob", password="Password123!")

    @staticmethod
    def get_valid_payload(**overrides):
        """Возвращает валидные параметры чека."""
        data = {
            "fn": "9999078900012345",
            "fd": "12345",
            "fp": "9876543210",
            "purchase_date": "05.10.2026 14:30",
            "total_amount": "1 550.00 ₽",
        }
        data.update(overrides)
        return data
