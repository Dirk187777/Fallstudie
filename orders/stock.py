"""Lagerbestand: Jede Dose verbraucht von jeder ihrer Zutaten so viele Portionen, wie sie enthält."""
from collections import Counter

from django.db.models import F

from shop.models import Ingredient


class OutOfStock(Exception):
    def __init__(self, ingredients):
        self.ingredients = ingredients
        super().__init__(", ".join(i.name for i in ingredients))


def required_portions(cart_items):
    needs = Counter()
    for item in cart_items:
        portions = item["blend"].summary_for(item["size"])["portions"] * item["quantity"]
        for ingredient in item["blend"].ingredients():
            needs[ingredient.pk] += portions
    return needs


def reserve(cart_items):
    """Bestand prüfen und abbuchen. Muss innerhalb einer Transaktion laufen."""
    needs = required_portions(cart_items)
    ingredients = Ingredient.objects.select_for_update().filter(pk__in=needs)
    missing = [i for i in ingredients if i.stock < needs[i.pk]]
    if missing:
        raise OutOfStock(missing)
    for pk, portions in needs.items():
        Ingredient.objects.filter(pk=pk).update(stock=F("stock") - portions)


def release(cart_items):
    """Bestand zurückbuchen, z. B. wenn Bestellungen gelöscht werden."""
    for pk, portions in required_portions(cart_items).items():
        Ingredient.objects.filter(pk=pk).update(stock=F("stock") + portions)
