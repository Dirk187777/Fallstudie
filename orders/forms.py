from django import forms
from django.db import transaction

from . import cart, stock
from .models import Order, OrderItem

AUTOCOMPLETE = {
    "name": "name",
    "email": "email",
    "street": "street-address",
    "zip_code": "postal-code",
    "city": "address-level2",
}


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["name", "email", "street", "zip_code", "city"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs["autocomplete"] = AUTOCOMPLETE[name]

    @staticmethod
    def initial_for(user):
        """Vorbelegung für Kunden: Name und E-Mail aus dem Konto, Adresse der letzten Bestellung."""
        if not user.is_authenticated:
            return {}
        initial = {"name": user.get_full_name(), "email": user.email}
        last_order = user.orders.first()
        if last_order:
            initial.update(
                street=last_order.street, zip_code=last_order.zip_code, city=last_order.city
            )
        return initial

    @transaction.atomic
    def save(self, cart_items, user=None):
        """Legt die Bestellung mit den Preisen zum Kaufzeitpunkt an und bucht den Lagerbestand ab.

        Wirft stock.OutOfStock, wenn eine Zutat nicht reicht; dann wird nichts gespeichert.
        """
        stock.reserve(cart_items)
        order = super().save(commit=False)
        order.user = user if user and user.is_authenticated else None
        order.total_price = cart.total(cart_items)
        order.save()
        OrderItem.objects.bulk_create(
            OrderItem(
                order=order,
                blend=i["blend"],
                quantity=i["quantity"],
                size=i["size"],
                unit_price=i["price"],
            )
            for i in cart_items
        )
        return order
