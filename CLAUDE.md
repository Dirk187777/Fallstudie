# (Fallstudie Systemanalyse, 3. Semester)

## Aufgabe
Prototyp eines Webshops für Protein- und Performance-Drinks, bei dem Kunden ihr Pulver im Konfigurator selbst zusammenstellen. Bewertet werden Dokumentation (60 %) und Präsentation (40 %), nicht der Code an sich. Der Prototyp soll schlank und stabil sein und lokal laufen.
Abgabe: 26.11.2026. Details und Planung stehen in der Projektzusammenfassung ( Datei im Repo /Users/emilkiefer/Documents/GitHub/Fallstudie_Semester3/AUFGABE.md).

## Stack
Django (Python), SQLite lokal (später PostgreSQL), Tailwind CSS, HTMX. Kein Hosting. Stripe nur optional im Testmodus.

## Umfang
- Kern (zuerst fertig): Shop mit fertigen Mixen, Konfigurator mit Live-Preis und Nährwerten, max. 3 Booster pro Mischung, Hinweis bei Koffein, gespeicherte Mischungen, Checkout als Gast oder mit Konto, Betreiberseite mit Rezeptur und Status.
- Zusatzziel (erst danach): Lagerbestand pro Zutat, Warnung bei Mindestbestand, ausverkaufte Zutaten im Konfigurator ausgrauen.
- Nicht bauen: Hosting, vollständige Rechtspflichten, Ziel-Quiz aus dem Mockup.

## Datenmodell
Sieben Tabellen: User, Adresse (optional), Zutat, Mischung, Mischung-Zutat, Bestellung, Bestellposition.
- Fertige Mixe sind Mischungen mit `ist_fertigprodukt = True`, keine eigene Produkttabelle.
- Gastbestellung: User an der Bestellung bleibt leer, Name, E-Mail und Adresse werden an der Bestellung gespeichert.
- Bestellposition speichert den Preis zum Kaufzeitpunkt.

## Befehle
- Einrichten: siehe README.md (venv, `pip install -r requirements.txt`, `npm install`)
- Starten: `python manage.py runserver` (CSS live: `npm run watch`)
- CSS/JS bauen: `npm run build`
- Migrationen: `python manage.py makemigrations && python manage.py migrate`
- Tests: `python manage.py test`
- Testdaten laden: `python manage.py load_demo_data` (Katalog), danach `python manage.py load_demo_orders` (Logins, Kunden, Bestellungen)

## Stil
- Code-Bezeichner: Englisch (Models, Felder, Views); `verbose_name` auf Deutsch
- Texte in der Oberfläche: Deutsch
- Kleine Funktionen, Django-Standardmittel vor eigenen Lösungen, keine unnötigen Abhängigkeiten
- Kommentare kurz, nur wo die Logik nicht offensichtlich ist

## Arbeitsweise
- Bei Unklarheit zuerst fragen, nicht raten.
- Ändere nur, was die Aufgabe verlangt. Hinweise auf weitere Verbesserungen melden statt umsetzen.
- Nach jeder Änderung die Tests oder den Server prüfen.
- Antworten knapp, ohne Wiederholungen.
- Das Team besteht aus vier Personen: Änderungen klein halten, damit sie im Git-Verlauf nachvollziehbar sind.
