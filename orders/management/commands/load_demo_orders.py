from datetime import timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from accounts.models import Profile
from orders import stock
from orders.forms import CheckoutForm
from orders.models import Order, OrderItem
from shop.models import Blend, Ingredient, Size

# Nur für die lokale Demo, nie in einer echten Umgebung verwenden
PASSWORD = "mischwerk-demo"
STAFF_EMAIL = "betrieb@mischwerk.de"

CUSTOMERS = {
    "erika": ("Erika", "Muster", "erika@example.com", "Hauptstr. 1", "10115", "Berlin"),
    "max": ("Max", "Mustermann", "max@example.com", "Bahnhofstr. 12", "80335", "München"),
    "lena": ("Lena", "Schmidt", "lena@example.com", "Gartenweg 5", "50667", "Köln"),
}
GUESTS = {
    "tom": ("Tom Becker", "tom.becker@example.com", "Ringstr. 8", "20095", "Hamburg"),
    "sara": ("Sara Yilmaz", "sara.yilmaz@example.com", "Lindenallee 3", "70173", "Stuttgart"),
    "jonas": ("Jonas Weber", "jonas.weber@example.com", "Am Markt 2", "04109", "Leipzig"),
}

# Gespeicherte Mischungen der Kunden: kunde, name, basis, geschmack, booster
CUSTOM_BLENDS = [
    ("erika", "Morning Fuel", "Whey Isolat", "Vanille", ["Kreatin", "Kollagen"]),
    ("erika", "Night Shake", "Casein", "Schoko", ["Vitamin D3"]),
    ("max", "Leg Day", "Energy-Basis", "Cola", ["Beta-Alanin", "Citrullin", "Kreatin"]),
    ("lena", "Green Power", "Vegan (Erbse/Reis)", "Pistazie", ["Vitamin D3", "Elektrolyte"]),
]

# Bestellungen: vor wie vielen tagen, kunde oder gast, status, positionen
# Position: (eigene mischung oder (produkt, sorte), menge, größe)
S, L = Size.REGULAR, Size.LARGE
ORDERS = [
    (13, "erika", Order.Status.SHIPPED, [("Morning Fuel", 1, L), (("Hydro Sport", "Wassermelone"), 1, S)]),
    (11, "tom", Order.Status.SHIPPED, [(("Whey Protein", "Schoko"), 2, S)]),
    (9, "max", Order.Status.SHIPPED, [("Leg Day", 1, S), (("Energy Pump", "Mango-Maracuja"), 1, S)]),
    (6, "sara", Order.Status.IN_PROGRESS, [(("Clear Whey", "Zitrone"), 1, L)]),
    (4, "lena", Order.Status.IN_PROGRESS, [("Green Power", 1, S), (("Hydro Immun", "Blutorange"), 2, S)]),
    (2, "erika", Order.Status.OPEN, [("Night Shake", 1, S)]),
    (1, "jonas", Order.Status.OPEN, [(("Energy Classic", "Cola"), 2, S), (("Hydro Basic", "Zitrone"), 1, S)]),
    (0, "max", Order.Status.OPEN, [(("Whey Isolat", "Vanille"), 1, L)]),
    (0, "lena", Order.Status.OPEN, [(("Clear Vegan", "Mango-Maracuja"), 1, S)]),
]


class Command(BaseCommand):
    help = "Legt Demo-Logins, gespeicherte Mischungen und Bestellungen an. Vorher load_demo_data ausführen."

    @transaction.atomic
    def handle(self, *args, **options):
        if not Blend.objects.filter(is_ready_made=True).exists():
            raise CommandError("Keine Produkte gefunden. Bitte zuerst load_demo_data ausführen.")
        self.reset()
        self.create_staff()
        users = self.create_customers()
        blends = self.create_custom_blends(users)
        self.create_orders(users, blends)
        self.stdout.write(self.style.SUCCESS(
            f"{len(users)} Kunden, {len(blends)} eigene Mischungen und {len(ORDERS)} Bestellungen angelegt. "
            f"Login Betrieb: {STAFF_EMAIL} / {PASSWORD}"
        ))

    def reset(self):
        """Vorherige Demo-Daten entfernen und deren Lagerabbuchung zurückbuchen, damit der Befehl wiederholbar ist."""
        emails = [c[2] for c in CUSTOMERS.values()] + [g[1] for g in GUESTS.values()]
        items = OrderItem.objects.filter(order__email__in=emails).select_related("blend__base", "blend__flavor")
        stock.release([{"blend": i.blend, "size": i.size, "quantity": i.quantity} for i in items])
        Order.objects.filter(email__in=emails).delete()
        User.objects.filter(username__in=emails).delete()

    def create_staff(self):
        staff, _ = User.objects.get_or_create(username=STAFF_EMAIL, defaults={"email": STAFF_EMAIL})
        staff.first_name, staff.last_name = "Mia", "Betrieb"
        staff.is_staff = staff.is_superuser = True
        staff.set_password(PASSWORD)
        staff.save()

    def create_customers(self):
        users = {}
        for key, (first, last, email, *_) in CUSTOMERS.items():
            user = User.objects.create_user(email, email, PASSWORD, first_name=first, last_name=last)
            Profile.objects.create(user=user)
            users[key] = user
        return users

    def create_custom_blends(self, users):
        ingredients = {i.name: i for i in Ingredient.objects.all()}
        blends = {}
        for owner, name, base, flavor, boosters in CUSTOM_BLENDS:
            blend = Blend.objects.create(
                name=name, base=ingredients[base], flavor=ingredients[flavor], user=users[owner]
            )
            blend.boosters.set([ingredients[b] for b in boosters])
            blends[name] = blend
        return blends

    def create_orders(self, users, blends):
        now = timezone.now()
        for index, (days_ago, who, status, positions) in enumerate(ORDERS):
            items = []
            for product, quantity, size in positions:
                if isinstance(product, tuple):
                    blend = Blend.objects.get(is_ready_made=True, name=product[0], flavor__name=product[1])
                else:
                    blend = blends[product]
                price = blend.price(size)
                items.append({
                    "blend": blend, "size": size, "quantity": quantity,
                    "price": price, "subtotal": price * quantity,
                })

            user = users.get(who)
            if user:
                _, _, email, street, zip_code, city = CUSTOMERS[who]
                name = user.get_full_name()
            else:
                name, email, street, zip_code, city = GUESTS[who]
            # Gleicher Weg wie im echten Checkout, damit Preise und Summen stimmen
            form = CheckoutForm({"name": name, "email": email, "street": street, "zip_code": zip_code, "city": city})
            form.is_valid()
            order = form.save(items, user=user)
            Order.objects.filter(pk=order.pk).update(
                # Spätere Einträge in ORDERS sind am selben Tag die neueren
                status=status, created_at=now - timedelta(days=days_ago, hours=len(ORDERS) - index)
            )
