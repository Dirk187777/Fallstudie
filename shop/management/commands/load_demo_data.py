from django.core.management.base import BaseCommand
from django.db import transaction

from shop.models import Blend, Ingredient, Line

T = Ingredient.Type
CREAMY = [Line.PROTEIN]
FRESH = [Line.CLEAR, Line.ENERGY, Line.HYDRATION]
ALL = Line.values

# name, preis pro portion, kcal, eiweiß, kohlenhydrate, fett, koffein mg, farbe, linie, portion g
BASES = [
    ("Whey", "1.20", 120, 24, 3, 1.5, 0, "#f1e4c9", Line.PROTEIN, 30),
    ("Whey Isolat", "1.50", 110, 27, 1, 0.3, 0, "#f7efdc", Line.PROTEIN, 30),
    ("Casein", "1.40", 115, 23, 3, 1, 0, "#f5f1ea", Line.PROTEIN, 30),
    ("Vegan (Erbse/Reis)", "1.50", 125, 21, 5, 2.5, 0, "#cfdcae", Line.PROTEIN, 30),
    ("Vegan (Soja)", "1.30", 115, 24, 2, 1.5, 0, "#e9d8a6", Line.PROTEIN, 30),
    ("Clear Whey Isolat", "1.70", 100, 24, 0.5, 0.1, 0, "#dff1f7", Line.CLEAR, 25),
    ("Clear Vegan (Erbse)", "1.80", 95, 21, 1, 0.5, 0, "#d9efd0", Line.CLEAR, 25),
    ("Energy-Basis", "0.60", 15, 0, 3, 0, 150, "#fff3b0", Line.ENERGY, 10),
    ("Elektrolyt-Basis", "0.50", 10, 0, 2, 0, 0, "#d4f3ef", Line.HYDRATION, 7),
]

# name, preis pro portion, kcal, kohlenhydrate, farbe, linien
# Reihenfolge = Reihenfolge der Sorten im Shop
FLAVORS = [
    ("Schoko", "0.20", 10, 1.5, "#c9a27e", CREAMY),
    ("Vanille", "0.20", 5, 1, "#f6e7a8", CREAMY),
    ("Erdbeere", "0.25", 8, 2, "#f6a8b8", CREAMY),
    ("Banane", "0.20", 8, 2, "#f9e27d", CREAMY),
    ("Cookies & Cream", "0.30", 12, 2, "#d6d0c8", CREAMY),
    ("Salted Caramel", "0.30", 10, 2, "#e0b07a", CREAMY),
    ("Haselnuss", "0.25", 12, 1, "#c7a07a", CREAMY),
    ("Kokos", "0.25", 12, 1, "#f4efe6", CREAMY),
    ("Pistazie", "0.35", 12, 1, "#c4d9a0", CREAMY),
    ("Zitrone", "0.15", 4, 1, "#f9f07a", FRESH),
    ("Pfirsich-Eistee", "0.20", 5, 1, "#f9c49a", FRESH),
    ("Mango-Maracuja", "0.20", 6, 1.5, "#fbb954", FRESH),
    ("Wassermelone", "0.20", 5, 1, "#f79a9a", FRESH),
    ("Himbeere", "0.20", 5, 1, "#e57da0", FRESH),
    ("Grüner Apfel", "0.15", 5, 1, "#bde58a", FRESH),
    ("Blutorange", "0.20", 5, 1, "#f48a5c", FRESH),
    ("Cola", "0.15", 4, 1, "#b08968", FRESH),
    ("Neutral", "0.00", 0, 0, "#ece9e4", ALL),
]

# name, preis pro portion, kcal, eiweiß, koffein mg, farbe, linien
# Koffein ist bei Energy kein Booster, weil die Energy-Basis schon 150 mg enthält
BOOSTERS = [
    ("Kreatin", "0.30", 0, 0, 0, "#a5c8f0", [Line.PROTEIN, Line.CLEAR, Line.ENERGY]),
    ("Koffein", "0.25", 0, 0, 80, "#f2b35b", [Line.PROTEIN, Line.CLEAR, Line.HYDRATION]),
    ("Elektrolyte", "0.35", 5, 0, 0, "#8fdccb", [Line.PROTEIN, Line.CLEAR]),
    ("Kollagen", "0.60", 36, 9, 0, "#e8b4d9", [Line.PROTEIN, Line.CLEAR]),
    ("Vitamin D3", "0.15", 0, 0, 0, "#f7d84a", [Line.PROTEIN, Line.CLEAR]),
    ("Beta-Alanin", "0.25", 0, 0, 0, "#c3b6f2", [Line.ENERGY]),
    ("Citrullin", "0.40", 0, 0, 0, "#f2a7a7", [Line.ENERGY]),
    ("Taurin", "0.20", 0, 0, 0, "#b6e3f2", [Line.ENERGY]),
    ("Vitamin B12", "0.10", 0, 0, 0, "#f7a6c9", [Line.ENERGY]),
    ("Magnesium", "0.20", 0, 0, 0, "#cfd8dc", [Line.HYDRATION]),
    ("Vitamin C", "0.15", 0, 0, 0, "#ffd166", [Line.HYDRATION]),
    ("Zink", "0.10", 0, 0, 0, "#b0bec5", [Line.HYDRATION]),
]

# Fertigprodukte: jedes gibt es in allen Sorten, die zur Linie der Basis passen.
# Die Hauptsorte wird zuerst angelegt und erscheint auf der Produktkarte.
# name, basis, booster, hauptsorte, kurzbeschreibung
PRODUCTS = [
    ("Whey Protein", "Whey", [], "Schoko", "Der Klassiker für Muskelaufbau"),
    ("Whey Isolat", "Whey Isolat", [], "Vanille", "Mehr Eiweiß, kaum Laktose"),
    ("Casein Protein", "Casein", [], "Cookies & Cream", "Langsam verdaulich, ideal am Abend"),
    ("Vegan Protein", "Vegan (Erbse/Reis)", [], "Schoko", "Pflanzlich aus Erbse und Reis"),
    ("Soja Protein", "Vegan (Soja)", [], "Pistazie", "Pflanzlich und günstig"),
    ("Clear Whey", "Clear Whey Isolat", [], "Zitrone", "Erfrischend klar wie Saft"),
    ("Clear Vegan", "Clear Vegan (Erbse)", [], "Mango-Maracuja", "Klar, fruchtig und pflanzlich"),
    ("Energy Classic", "Energy-Basis", [], "Cola", "Purer Energie-Kick"),
    ("Energy Vital", "Energy-Basis", ["Vitamin B12", "Taurin"], "Grüner Apfel", "Energie mit Vitaminen für den Alltag"),
    ("Energy Pump", "Energy-Basis", ["Beta-Alanin", "Citrullin", "Kreatin"], "Mango-Maracuja", "Pre-Workout für harte Trainingseinheiten"),
    ("Hydro Basic", "Elektrolyt-Basis", [], "Zitrone", "Elektrolyte für jeden Tag"),
    ("Hydro Sport", "Elektrolyt-Basis", ["Magnesium"], "Wassermelone", "Mit Magnesium für Training und Hitze"),
    ("Hydro Immun", "Elektrolyt-Basis", ["Vitamin C", "Zink"], "Blutorange", "Mit Vitamin C und Zink"),
]


# Lagerbestand in Portionen. Standard reicht für viele Dosen, einige Zutaten sind für die Demo knapp:
# Kokos ist ausverkauft, Haselnuss unter Mindestbestand, Kollagen fällt durch eine Demo-Bestellung darunter.
DEFAULT_STOCK, DEFAULT_MIN_STOCK = 600, 120
STOCK = {"Kokos": 0, "Haselnuss": 80, "Kollagen": 150}


def line_flags(lines):
    return {f"for_{line}": line in lines for line in Line.values}


class Command(BaseCommand):
    help = "Legt Zutaten für alle Produktlinien und fertige Mixe als Testdaten an."

    @transaction.atomic
    def handle(self, *args, **options):
        rows = []
        for name, price, kcal, protein, carbs, fat, caffeine, color, line, grams in BASES:
            rows.append((name, T.BASE, dict(
                price=price, kcal=kcal, protein=protein, carbs=carbs, fat=fat,
                caffeine_mg=caffeine, color=color, portion_grams=grams, **line_flags([line]),
            )))
        for name, price, kcal, carbs, color, lines in FLAVORS:
            rows.append((name, T.FLAVOR, dict(
                price=price, kcal=kcal, carbs=carbs, color=color, **line_flags(lines),
            )))
        for name, price, kcal, protein, caffeine, color, lines in BOOSTERS:
            rows.append((name, T.BOOSTER, dict(
                price=price, kcal=kcal, protein=protein, caffeine_mg=caffeine,
                color=color, **line_flags(lines),
            )))

        ingredients = {}
        for name, type_, values in rows:
            ingredients[name], _ = Ingredient.objects.update_or_create(
                name=name,
                defaults=dict(
                    type=type_,
                    stock=STOCK.get(name, DEFAULT_STOCK),
                    min_stock=DEFAULT_MIN_STOCK,
                    **values,
                ),
            )

        current = []
        for name, base_name, boosters, main_flavor, description in PRODUCTS:
            base = ingredients[base_name]
            flavors = [f[0] for f in FLAVORS if base.line in f[-1]]
            flavors.sort(key=lambda flavor: flavor != main_flavor)
            for flavor in flavors:
                blend, _ = Blend.objects.update_or_create(
                    name=name,
                    is_ready_made=True,
                    base=base,
                    flavor=ingredients[flavor],
                    defaults=dict(description=description),
                )
                blend.boosters.set([ingredients[b] for b in boosters])
                current.append(blend.pk)

        # Alte Fertigprodukte ausblenden statt löschen, Bestellungen verweisen darauf
        hidden = Blend.objects.filter(is_ready_made=True, user=None).exclude(pk__in=current)
        hidden.update(is_ready_made=False)

        self.stdout.write(self.style.SUCCESS(
            f"{len(rows)} Zutaten, {len(PRODUCTS)} Produkte in {len(current)} Sorten geladen."
        ))
