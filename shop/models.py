from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils.functional import cached_property

MAX_BOOSTERS = 3
# Normale Dose: 30 Portionen, die Portionsgröße bestimmt die Basis
PORTIONS_PER_CAN = 30
DEFAULT_PORTION_GRAMS = 30


class Line(models.TextChoices):
    """Produktlinien. Jede Zutat ist für eine oder mehrere Linien freigegeben."""

    PROTEIN = "protein", "Protein Shake"
    CLEAR = "clear", "Clear Protein"
    ENERGY = "energy", "Energy"
    HYDRATION = "hydration", "Hydration"


class Size(models.TextChoices):
    REGULAR = "regular", "Normal"
    LARGE = "large", "Groß"


# Große Dose: doppelte Menge mit 10 % Mengenrabatt, nur bei Protein-Linien
LARGE_SIZE_LINES = {Line.PROTEIN, Line.CLEAR}
LARGE_DISCOUNT = Decimal("0.10")


def sizes_for(line):
    return list(Size) if line in LARGE_SIZE_LINES else [Size.REGULAR]


def summarize(ingredients, size=Size.REGULAR):
    """Dosenpreis, Grundpreis und Nährwerte pro Portion für eine Liste von Zutaten."""
    ingredients = list(ingredients)
    zero = Decimal("0")
    base = next((i for i in ingredients if i.type == Ingredient.Type.BASE), None)
    portion_grams = base.portion_grams if base else DEFAULT_PORTION_GRAMS
    portions = PORTIONS_PER_CAN
    price = sum((i.price for i in ingredients), zero) * portions
    if size == Size.LARGE:
        portions *= 2
        price = (price * 2 * (1 - LARGE_DISCOUNT)).quantize(Decimal("0.01"))
    can_grams = portion_grams * portions
    caffeine_mg = sum(i.caffeine_mg for i in ingredients)
    return {
        "price": price,
        "price_per_kg": price * 1000 / can_grams,
        "portions": portions,
        "portion_grams": portion_grams,
        "can_grams": can_grams,
        "kcal": sum((i.kcal for i in ingredients), zero),
        "protein": sum((i.protein for i in ingredients), zero),
        "carbs": sum((i.carbs for i in ingredients), zero),
        "fat": sum((i.fat for i in ingredients), zero),
        "caffeine_mg": caffeine_mg,
        "contains_caffeine": caffeine_mg > 0,
    }


class IngredientQuerySet(models.QuerySet):
    def for_line(self, line):
        return self.filter(**{f"for_{line}": True})

    def available(self):
        return self.filter(stock__gte=PORTIONS_PER_CAN)

    def low_stock(self):
        return self.filter(stock__lte=models.F("min_stock"))


class Ingredient(models.Model):
    class Type(models.TextChoices):
        BASE = "base", "Basis"
        FLAVOR = "flavor", "Geschmack"
        BOOSTER = "booster", "Booster"

    name = models.CharField("Name", max_length=100)
    type = models.CharField("Typ", max_length=10, choices=Type.choices)
    price = models.DecimalField("Preis pro Portion (€)", max_digits=6, decimal_places=2)
    # Nährwerte pro Portion
    kcal = models.DecimalField("kcal", max_digits=6, decimal_places=1, default=0)
    protein = models.DecimalField("Eiweiß (g)", max_digits=5, decimal_places=1, default=0)
    carbs = models.DecimalField("Kohlenhydrate (g)", max_digits=5, decimal_places=1, default=0)
    fat = models.DecimalField("Fett (g)", max_digits=5, decimal_places=1, default=0)
    caffeine_mg = models.PositiveSmallIntegerField("Koffein (mg)", default=0)
    color = models.CharField("Farbe (Hex)", max_length=7, default="#d6d3d1")
    # Nur bei Basen relevant: bestimmt Dosengewicht und Grundpreis
    portion_grams = models.PositiveSmallIntegerField(
        "Portionsgröße (g)", default=DEFAULT_PORTION_GRAMS
    )
    # Freigabe pro Produktlinie (siehe Line)
    for_protein = models.BooleanField("für Protein Shake", default=False)
    for_clear = models.BooleanField("für Clear Protein", default=False)
    for_energy = models.BooleanField("für Energy", default=False)
    for_hydration = models.BooleanField("für Hydration", default=False)
    # Zusatzziel Lagerwarnung
    stock = models.PositiveIntegerField("Lagerbestand (Portionen)", default=0)
    min_stock = models.PositiveIntegerField("Mindestbestand (Portionen)", default=0)

    objects = IngredientQuerySet.as_manager()

    class Meta:
        verbose_name = "Zutat"
        verbose_name_plural = "Zutaten"
        ordering = ["type", "name"]

    def __str__(self):
        return self.name

    @property
    def can_price(self):
        return self.price * PORTIONS_PER_CAN

    @property
    def contains_caffeine(self):
        return self.caffeine_mg > 0

    @property
    def is_sold_out(self):
        """Ausverkauft, sobald der Bestand nicht mehr für eine Dose reicht."""
        return self.stock < PORTIONS_PER_CAN

    @property
    def is_low(self):
        return self.stock <= self.min_stock

    @property
    def line(self):
        """Erste freigegebene Linie, bei Basen ist das genau eine."""
        return next((line for line in Line.values if getattr(self, f"for_{line}")), Line.PROTEIN)


class BlendQuerySet(models.QuerySet):
    def visible_to(self, user):
        """Fertige Mixe für alle, eigene Mischungen nur für den Besitzer."""
        allowed = models.Q(is_ready_made=True)
        if user.is_authenticated:
            allowed |= models.Q(user=user)
        return self.filter(allowed)


class Blend(models.Model):
    class Sweetness(models.TextChoices):
        NONE = "none", "ungesüßt"
        LIGHT = "light", "leicht"
        NORMAL = "normal", "normal"

    name = models.CharField("Name", max_length=100)
    base = models.ForeignKey(
        Ingredient,
        on_delete=models.PROTECT,
        related_name="+",
        limit_choices_to={"type": Ingredient.Type.BASE},
        verbose_name="Basis",
    )
    flavor = models.ForeignKey(
        Ingredient,
        on_delete=models.PROTECT,
        related_name="+",
        limit_choices_to={"type": Ingredient.Type.FLAVOR},
        verbose_name="Geschmack",
    )
    sweetness = models.CharField(
        "Süße", max_length=10, choices=Sweetness.choices, default=Sweetness.NORMAL
    )
    boosters = models.ManyToManyField(
        Ingredient,
        through="BlendIngredient",
        related_name="blends",
        blank=True,
        verbose_name="Booster",
    )
    is_ready_made = models.BooleanField("ist Fertigprodukt", default=False)
    description = models.CharField("Kurzbeschreibung", max_length=200, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="blends",
        verbose_name="Kunde",
    )
    created_at = models.DateTimeField("erstellt am", auto_now_add=True)

    objects = BlendQuerySet.as_manager()

    class Meta:
        verbose_name = "Mischung"
        verbose_name_plural = "Mischungen"

    def __str__(self):
        return self.name

    @property
    def line(self):
        return self.base.line

    @property
    def line_label(self):
        return Line(self.line).label

    def ingredients(self):
        return [self.base, self.flavor, *self.boosters.all()]

    @cached_property
    def summary(self):
        return summarize(self.ingredients())

    def summary_for(self, size):
        return self.summary if size == Size.REGULAR else summarize(self.ingredients(), size)

    def price(self, size=Size.REGULAR):
        return self.summary_for(size)["price"]

    def sizes(self):
        return sizes_for(self.line)

    @property
    def is_sold_out(self):
        return any(i.is_sold_out for i in self.ingredients())


class BlendIngredient(models.Model):
    """Verknüpft eine Mischung mit ihren Boostern (n:m)."""

    blend = models.ForeignKey(Blend, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.PROTECT,
        limit_choices_to={"type": Ingredient.Type.BOOSTER},
        verbose_name="Booster",
    )

    class Meta:
        verbose_name = "Mischung-Zutat"
        verbose_name_plural = "Mischung-Zutaten"
        constraints = [
            models.UniqueConstraint(
                fields=["blend", "ingredient"], name="unique_booster_per_blend"
            )
        ]

    def __str__(self):
        return f"{self.blend} – {self.ingredient}"
