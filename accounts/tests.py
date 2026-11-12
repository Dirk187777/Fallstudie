from io import StringIO

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from orders.models import Order
from shop.models import Blend

PASSWORD = "Sicheres-Passwort-123"


def register_data(**overrides):
    return {
        "first_name": "Erika",
        "last_name": "Muster",
        "email": "Erika@Example.com",
        "phone": "",
        "password1": PASSWORD,
        "password2": PASSWORD,
        **overrides,
    }


class AccountTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("load_demo_data", stdout=StringIO())
        cls.mix = Blend.objects.get(name="Whey Protein", flavor__name="Schoko")

    def create_user(self):
        return User.objects.create_user(
            "erika@example.com", "erika@example.com", PASSWORD, first_name="Erika", last_name="Muster"
        )

    def guest_order(self, email):
        return Order.objects.create(
            name="Erika Muster", email=email, street="Hauptstr. 1",
            zip_code="12345", city="Berlin", total_price=1,
        )

    def test_register_logs_in_and_assigns_guest_orders(self):
        old_order = self.guest_order("erika@example.com")
        other_order = self.guest_order("jemand@example.com")

        response = self.client.post(reverse("accounts:register"), register_data())

        self.assertRedirects(response, reverse("accounts:account"))
        user = User.objects.get(username="erika@example.com")
        self.assertEqual(user.profile.phone, "")
        old_order.refresh_from_db()
        other_order.refresh_from_db()
        self.assertEqual(old_order.user, user)
        self.assertIsNone(other_order.user)
        self.assertContains(self.client.get(reverse("accounts:account")), "Hallo Erika")

    def test_register_rejects_existing_email(self):
        self.create_user()
        response = self.client.post(reverse("accounts:register"), register_data())
        self.assertContains(response, "schon ein Konto")

    def test_login_with_email_ignores_case(self):
        self.create_user()
        response = self.client.post(
            reverse("accounts:login"), {"username": "ERIKA@example.com", "password": PASSWORD}
        )
        self.assertRedirects(response, reverse("accounts:account"))

    def test_account_requires_login(self):
        response = self.client.get(reverse("accounts:account"))
        self.assertRedirects(response, reverse("accounts:login") + "?next=" + reverse("accounts:account"))

    def test_reorder_own_blend_but_not_foreign(self):
        user = self.create_user()
        own = Blend.objects.create(name="Mein Mix", base=self.mix.base, flavor=self.mix.flavor, user=user)
        foreign = Blend.objects.create(name="Fremd", base=self.mix.base, flavor=self.mix.flavor)
        self.client.force_login(user)

        self.assertRedirects(self.client.post(reverse("orders:cart_add", args=[own.pk])), reverse("orders:cart"))
        self.assertEqual(self.client.post(reverse("orders:cart_add", args=[foreign.pk])).status_code, 404)

    def test_checkout_is_prefilled_and_linked_to_user(self):
        user = self.create_user()
        self.client.force_login(user)
        self.client.post(reverse("orders:cart_add", args=[self.mix.pk]))

        response = self.client.get(reverse("orders:checkout"))
        self.assertContains(response, 'value="Erika Muster"')
        self.assertContains(response, 'value="erika@example.com"')

        self.client.post(reverse("orders:checkout"), {
            "name": "Erika Muster", "email": "erika@example.com",
            "street": "Hauptstr. 1", "zip_code": "12345", "city": "Berlin",
        })
        self.assertEqual(Order.objects.get().user, user)

        # Beim nächsten Mal ist die letzte Adresse vorbelegt
        self.client.post(reverse("orders:cart_add", args=[self.mix.pk]))
        self.assertContains(self.client.get(reverse("orders:checkout")), 'value="Hauptstr. 1"')
