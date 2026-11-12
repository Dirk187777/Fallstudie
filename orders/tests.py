from decimal import Decimal
from io import StringIO

from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from shop.models import Blend, Ingredient

from .models import Order

ADDRESS = {
    "name": "Erika Muster",
    "email": "erika@example.com",
    "street": "Hauptstr. 1",
    "zip_code": "12345",
    "city": "Berlin",
}


class CheckoutTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("load_demo_data", stdout=StringIO())
        cls.mix = Blend.objects.get(name="Whey Protein", flavor__name="Schoko")

    def add_mix(self):
        self.client.post(reverse("orders:cart_add", args=[self.mix.pk]))

    def test_change_quantity_and_remove_at_zero(self):
        self.add_mix()
        url = reverse("orders:cart_update", args=[self.mix.pk, "regular"])
        self.client.post(url, {"quantity": 3})
        self.assertEqual(self.client.session["cart"], {f"{self.mix.pk}:regular": 3})
        self.client.post(url, {"quantity": 99})
        self.assertEqual(self.client.session["cart"][f"{self.mix.pk}:regular"], 20)
        self.client.post(url, {"quantity": 0})
        self.assertEqual(self.client.session["cart"], {})

    def test_empty_cart_redirects_to_cart(self):
        self.assertRedirects(self.client.get(reverse("orders:checkout")), reverse("orders:cart"))

    def test_guest_checkout_creates_order_and_clears_cart(self):
        self.add_mix()
        self.add_mix()
        response = self.client.post(reverse("orders:checkout"), ADDRESS)

        order = Order.objects.get()
        self.assertRedirects(response, reverse("orders:confirmation", args=[order.pk]))
        self.assertIsNone(order.user)
        self.assertEqual(order.status, Order.Status.OPEN)
        item = order.items.get()
        self.assertEqual(item.quantity, 2)
        self.assertEqual(item.unit_price, Decimal("42.00"))
        self.assertEqual(order.total_price, Decimal("84.00"))
        self.assertNotIn("cart", self.client.session)

    def test_price_is_kept_when_ingredient_price_changes(self):
        self.add_mix()
        self.client.post(reverse("orders:checkout"), ADDRESS)
        self.mix.base.price = Decimal("9.99")
        self.mix.base.save()
        self.assertEqual(Order.objects.get().items.get().unit_price, Decimal("42.00"))

    def test_checkout_reduces_stock_per_portion(self):
        self.client.post(reverse("orders:cart_add", args=[self.mix.pk]), {"size": "large"})
        self.client.post(reverse("orders:checkout"), ADDRESS)
        # Große Dose = 60 Portionen von Basis und Geschmack
        self.mix.base.refresh_from_db()
        self.mix.flavor.refresh_from_db()
        self.assertEqual(self.mix.base.stock, 600 - 60)
        self.assertEqual(self.mix.flavor.stock, 600 - 60)

    def test_checkout_fails_without_stock_and_books_nothing(self):
        self.add_mix()
        Ingredient.objects.filter(pk=self.mix.flavor.pk).update(stock=10)
        response = self.client.post(reverse("orders:checkout"), ADDRESS)
        self.assertContains(response, "nicht mehr genug auf Lager")
        self.assertFalse(Order.objects.exists())
        self.mix.base.refresh_from_db()
        self.assertEqual(self.mix.base.stock, 600)

    def test_invalid_form_creates_no_order(self):
        self.add_mix()
        response = self.client.post(reverse("orders:checkout"), {**ADDRESS, "email": "kaputt"})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Order.objects.exists())

    def test_confirmation_only_visible_in_own_session(self):
        self.add_mix()
        self.client.post(reverse("orders:checkout"), ADDRESS)
        url = reverse("orders:confirmation", args=[Order.objects.get().pk])
        self.assertContains(self.client.get(url), "Danke für deine Bestellung")
        self.client.logout()  # neue Session
        self.assertRedirects(self.client.get(url), reverse("shop:home"))

    def test_only_ready_made_mixes_can_be_added_directly(self):
        custom = Blend.objects.create(name="Privat", base=self.mix.base, flavor=self.mix.flavor)
        response = self.client.post(reverse("orders:cart_add", args=[custom.pk]))
        self.assertEqual(response.status_code, 404)

    def test_order_item_stores_size_and_large_price(self):
        self.client.post(reverse("orders:cart_add", args=[self.mix.pk]), {"size": "large"})
        self.client.post(reverse("orders:checkout"), ADDRESS)
        item = Order.objects.get().items.get()
        self.assertEqual(item.size, "large")
        self.assertEqual(item.unit_price, Decimal("75.60"))
        self.assertEqual(item.can_grams, 1800)


class DemoOrdersTests(TestCase):
    def test_demo_orders_are_repeatable_and_consistent(self):
        call_command("load_demo_data", stdout=StringIO())
        call_command("load_demo_orders", stdout=StringIO())
        collagen = Ingredient.objects.get(name="Kollagen").stock
        for _ in range(3):
            call_command("load_demo_orders", stdout=StringIO())
        # Wiederholen bucht den Bestand nicht mehrfach ab
        self.assertEqual(Ingredient.objects.get(name="Kollagen").stock, collagen)

        orders = Order.objects.all()
        self.assertEqual(orders.count(), 9)
        self.assertEqual(set(orders.values_list("status", flat=True)), set(Order.Status.values))
        self.assertTrue(orders.filter(user__isnull=True).exists())
        for order in orders:
            items_total = sum(i.unit_price * i.quantity for i in order.items.all())
            self.assertEqual(order.total_price, items_total)
        self.assertTrue(self.client.login(username="betrieb@mischwerk.de", password="mischwerk-demo"))
        self.assertContains(self.client.get(reverse("backoffice:order_list")), "Erika Muster")
