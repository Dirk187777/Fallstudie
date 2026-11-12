from django.conf import settings
from django.db import models


class Profile(models.Model):
    """Ergänzt den Django-User um Kundendaten."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    phone = models.CharField("Telefon", max_length=30, blank=True)

    class Meta:
        verbose_name = "Profil"
        verbose_name_plural = "Profile"

    def __str__(self):
        return f"Profil von {self.user}"


class Address(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="addresses"
    )
    street = models.CharField("Straße und Hausnummer", max_length=200)
    zip_code = models.CharField("PLZ", max_length=10)
    city = models.CharField("Ort", max_length=100)
    is_default = models.BooleanField("Standardadresse", default=False)

    class Meta:
        verbose_name = "Adresse"
        verbose_name_plural = "Adressen"

    def __str__(self):
        return f"{self.street}, {self.zip_code} {self.city}"
