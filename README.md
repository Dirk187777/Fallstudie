# Mischwerk

Prototyp eines Webshops für Protein- und Performance-Drinks (Fallstudie Systemanalyse, 3. Semester).
Kunden stellen ihr Pulver im Konfigurator selbst zusammen oder kaufen fertige Produkte.
Details zur Aufgabe stehen in [AUFGABE.md](AUFGABE.md).

## Voraussetzungen

- Python 3.10 oder neuer (empfohlen 3.13)
- Node.js (für Tailwind CSS und HTMX)

## Erstes Einrichten

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
npm install
npm run build                      # erzeugt das CSS und kopiert HTMX nach static/vendor
python manage.py migrate
python manage.py load_demo_data    # Zutaten und fertige Produkte
python manage.py load_demo_orders  # Demo-Logins, Kunden und Bestellungen
```

## Starten

```bash
source .venv/bin/activate
python manage.py runserver
```

Danach im Browser http://127.0.0.1:8000 öffnen.

Beim Arbeiten an Templates in einem zweiten Terminal `npm run watch` laufen lassen, damit neue Tailwind-Klassen sofort im CSS landen.

## Demo-Logins

Angelegt von `load_demo_orders`. Nur für die lokale Demo gedacht.

| Rolle | E-Mail | Passwort | Sieht |
| --- | --- | --- | --- |
| Betrieb | `betrieb@mischwerk.de` | `mischwerk-demo` | Betreiberseite `/betrieb/` und Admin `/admin/` |
| Kundin | `erika@example.com` | `mischwerk-demo` | gespeicherte Mischungen und Bestellungen |
| Kunde | `max@example.com` | `mischwerk-demo` | dito |
| Kundin | `lena@example.com` | `mischwerk-demo` | dito |

Dazu kommen drei Gastbestellungen ohne Konto. Die neun Bestellungen sind über die letzten zwei Wochen verteilt und haben alle drei Status.

**Lager in der Demo:** Jede Bestellung bucht den Bestand der Zutaten ab. Kokos ist ausverkauft (im Shop ausgegraut), Haselnuss knapp, und Kollagen fällt durch eine Demo-Bestellung unter den Mindestbestand. Die Warnung erscheint auf `/betrieb/`, die Übersicht unter `/betrieb/lager/`. Nachfüllen geht im Admin direkt in der Zutatenliste.

## Seiten

| Adresse | Inhalt |
| --- | --- |
| `/` | Startseite mit allen Produkten nach Linie |
| `/mix/<id>/` | Produktseite mit Sorten- und Größenwahl |
| `/konfigurator/` | eigene Mischung mit Live-Preis und Nährwerten |
| `/warenkorb/`, `/kasse/` | Warenkorb und Checkout (Gast oder Konto) |
| `/konto/` | Registrierung, Anmeldung, gespeicherte Mischungen |
| `/betrieb/` | Bestellübersicht, Rezeptur, Status und Lagerwarnung (nur Mitarbeiter) |
| `/betrieb/lager/` | Lagerbestand aller Zutaten |
| `/admin/` | Stammdaten: Zutaten, Preise, Produkte |

## Nach jedem `git pull`

Wenn andere Models, Testdaten oder Styles geändert haben:

```bash
pip install -r requirements.txt
npm install && npm run build
python manage.py migrate
python manage.py load_demo_data
python manage.py load_demo_orders
```

Beide `load_demo_…`-Befehle lassen sich gefahrlos wiederholen.

## Frische Datenbank (z. B. für den Demo-Laptop)

```bash
rm db.sqlite3
python manage.py migrate
python manage.py load_demo_data
python manage.py load_demo_orders
```

## Tests

```bash
python manage.py test
```

## Struktur

| Ordner | Inhalt |
| --- | --- |
| `config/` | Django-Einstellungen und URLs |
| `accounts/` | Registrierung, Anmeldung, Kontoseite; Profil und Adresse zum Django-User |
| `shop/` | Zutat, Mischung, Mischung-Zutat; Startseite, Produktseite, Konfigurator, Katalog-Testdaten |
| `orders/` | Bestellung, Bestellposition, Warenkorb, Checkout, Demo-Bestellungen |
| `backoffice/` | Betreiberseite (keine eigenen Tabellen) |
| `templates/` | HTML-Templates |
| `static/src/` | Tailwind-Eingabe (`static/css/output.css` wird erzeugt) |
| `static/js/` | Animationen im Konfigurator |
