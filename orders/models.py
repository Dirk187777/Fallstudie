from django.conf import settings
from django.db import models

from shop.models import Blend, Size


class Order(models.Model):
    class Status(models.TextChoices):
        OPEN = "open", "offen"
        IN_PROGRESS = "in_progress", "in Bearbeitung"
        SHIPPED = "shipped", "versendet"

    # Leer bei Gastbestellungen
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
        verbose_name="Kunde",
    )
    created_at = models.DateTimeField("Bestelldatum", auto_now_add=True)
    status = models.CharField(
        "Status", max_length=20, choices=Status.choices, default=Status.OPEN
    )
    # Kontaktdaten und Adresse werden pro Bestellung festgehalten
    name = models.CharField("Name", max_length=150)
    email = models.EmailField("E-Mail")
    street = models.CharField("Straße und Hausnummer", max_length=200)
    zip_code = models.CharField("PLZ", max_length=10)
    city = models.CharField("Ort", max_length=100)
    total_price = models.DecimalField("Gesamtpreis (€)", max_digits=8, decimal_places=2)

    class Meta:
        verbose_name = "Bestellung"
        verbose_name_plural = "Bestellungen"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Bestellung #{self.pk}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    blend = models.ForeignKey(Blend, on_delete=models.PROTECT, verbose_name="Mischung")
    quantity = models.PositiveIntegerField("Menge", default=1)
    size = models.CharField("Größe", max_length=10, choices=Size.choices, default=Size.REGULAR)
    unit_price = models.DecimalField(
        "Preis zum Kaufzeitpunkt (€)", max_digits=6, decimal_places=2
    )

    class Meta:
        verbose_name = "Bestellposition"
        verbose_name_plural = "Bestellpositionen"

    def __str__(self):
        return f"{self.quantity} × {self.blend}"

    @property
    def can_grams(self):
        return self.blend.summary_for(self.size)["can_grams"]
