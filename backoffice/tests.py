from io import StringIO

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from orders.models import Order, OrderItem
from shop.models import Blend


class BackofficeTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("load_demo_data", stdout=StringIO())
        cls.staff = User.objects.create_user("betrieb@example.com", password="x", is_staff=True)
        cls.customer = User.objects.create_user("kunde@example.com", password="x")
        cls.order = Order.objects.create(
            name="Erika Muster", email="erika@example.com", street="Hauptstr. 1",
            zip_code="12345", city="Berlin", total_price="2.20",
        )
        blend = Blend.objects.get(name="Energy Pump", flavor__name="Mango-Maracuja")
        OrderItem.objects.create(order=cls.order, blend=blend, quantity=2, unit_price="1.10")
        cls.status_url = reverse("backoffice:order_set_status", args=[cls.order.pk])

    def test_only_staff_has_access(self):
        url = reverse("backoffice:order_list")
        self.assertRedirects(self.client.get(url), reverse("accounts:login") + "?next=" + url)
        self.client.force_login(self.customer)
        self.assertEqual(self.client.get(url).status_code, 302)
        self.assertEqual(self.client.post(self.status_url, {"status": "shipped"}).status_code, 302)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.Status.OPEN)

    def test_list_filters_by_status(self):
        self.client.force_login(self.staff)
        url = reverse("backoffice:order_list")
        self.assertContains(self.client.get(url), "Erika Muster")
        self.assertContains(self.client.get(url, {"status": "open"}), "Erika Muster")
        self.assertNotContains(self.client.get(url, {"status": "shipped"}), "Erika Muster")

    def test_list_shows_newest_first(self):
        newer = Order.objects.create(
            name="Neu", email="neu@example.com", street="x", zip_code="1", city="y", total_price=1
        )
        OrderItem.objects.create(order=newer, blend=self.order.items.get().blend, unit_price=1)
        self.client.force_login(self.staff)
        orders = list(self.client.get(reverse("backoffice:order_list")).context["orders"])
        self.assertEqual(orders[0], newer)

    def test_low_stock_warning_and_stock_page(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse("backoffice:order_list"))
        self.assertContains(response, "Lagerwarnung")
        self.assertContains(response, "Kokos: 0")
        response = self.client.get(reverse("backoffice:stock_list"))
        self.assertContains(response, "ausverkauft")
        self.assertContains(response, "Haselnuss")

    def test_detail_shows_recipe(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse("backoffice:order_detail", args=[self.order.pk]))
        self.assertContains(response, "2 × Energy Pump")
        self.assertContains(response, "Beta-Alanin")
        self.assertContains(response, "Citrullin")

    def test_status_change_with_htmx_returns_partial(self):
        self.client.force_login(self.staff)
        response = self.client.post(self.status_url, {"status": "in_progress"}, HTTP_HX_REQUEST="true")
        self.assertTemplateUsed(response, "backoffice/_status.html")
        self.assertContains(response, "in Bearbeitung")
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.Status.IN_PROGRESS)

    def test_unknown_status_is_rejected(self):
        self.client.force_login(self.staff)
        self.assertEqual(self.client.post(self.status_url, {"status": "kaputt"}).status_code, 400)
