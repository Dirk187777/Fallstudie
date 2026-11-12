# Mischwerk – Projektzusammenfassung Webshop

Fallstudie Systemanalyse, 3. Semester · Stand 2026-10-14

## Aufgabe und Rahmenbedingungen

Unser Thema ist 3.5, „Erstellung eines Internet-Shops für definierte Artikel“: Konzeption, Design und Realisierung eines Prototyps. Das Thema ist mit dem Dozenten abgestimmt.

| Punkt | Vorgabe |
| --- | --- |
| Offizieller Start | 27.10.2026, vier Wochen Bearbeitungszeit |
| Abgabe | 26.11.2026, 23:59 Uhr per E-Mail, Dokumentation und Präsentation |
| Präsentation | ca. 30 Minuten, Termine 27.11., 01.12. oder 02.12.2026 |
| Team | in der Regel vier Personen |
| Umfang Doku | 25 bis max. 30 Seiten |
| Methodenpflicht | mindestens eine Methode aus Systemanalyse (UML, SSA, ERM, eEPK, PAP, BPMN, ET) |
| Pflichtkapitel | Projektmanagement: Notwendigkeit, positive und negative Erfahrungen, Bewertung in der Gruppe |
| Werkzeuge | frei wählbar, auch Open-Source- und KI-Tools |
| Bewertung | gemeinsame Gruppennote: Form, Gestaltung, Struktur, Inhalt 60 %, Präsentation 40 % |

Daraus folgt: Bewertet werden Dokumentation und Präsentation, nicht der Code an sich. Der Prototyp soll schlank und stabil sein, die Doku wird von Anfang an parallel geschrieben.

## Projektidee: Mischwerk

Mischwerk (Arbeitstitel) ist ein Webshop für Protein- und Performance-Drinks, in dem Kunden ihr Pulver selbst zusammenstellen, ähnlich wie bei mymuesli. Daneben gibt es fertige Mixe als feste Produkte.

Der Konfigurator hebt uns von einem einfachen Webshop ab und macht auch die Betreiberseite interessanter: Zu jeder Bestellung sieht der Betreiber die genaue Rezeptur, die gemischt werden muss.

Vergleichbare Angebote gibt es vor allem in den USA, etwa Gainful (personalisierte Mischungen im Abo) sowie INFINIT Nutrition und True Nutrition. Im deutschsprachigen Raum verkaufen große Marken wie More Nutrition, ESN oder foodspring überwiegend fertige Produkte. Diesen Vergleich nutzen wir im Kapitel Markt und Wettbewerb.

## Funktionsumfang

Zuerst wird der Kern vollständig fertig und online gestellt, erst danach kommt das Zusatzziel Lagerwarnung.

**Kern (Muss)**

- Shop mit fertigen Mixen, Produktdetails und Warenkorb
- Konfigurator: Basis (Whey, Casein, vegan), Geschmack, Süße und Booster wie Kreatin, Koffein, Elektrolyte, Kollagen, Vitamin D3
- Live-Berechnung von Preis und Nährwerten pro Portion
- Dosierungsregeln: maximal drei Booster pro Mischung, Hinweis bei Koffein
- Eigener Mix-Name, gespeicherte Mischungen im Kundenkonto zum Nachbestellen
- Checkout als Gast oder mit Kundenkonto
- Betreiberseite: Bestellübersicht mit Rezeptur pro Bestellung und Statuswechsel (offen, in Bearbeitung, versendet)

**Zusatzziel: Lagerwarnung**

- Lagerbestand pro Zutat, wird bei jeder Bestellung automatisch reduziert
- Warnung auf der Betreiberseite, sobald eine Zutat unter einen Mindestbestand fällt
- Ausverkaufte Zutaten werden im Konfigurator ausgegraut

**Offene Frage:** Reicht das eingebaute Django-Admin als Betreiberseite, oder bauen wir eine eigene? Eine eigene Seite wirkt in der Präsentation stärker.

## Technik-Stack und Hosting

Wir bauen den Shop mit Django, weil das Team Python-Vorkenntnisse hat und Django Datenbank, Login, Formulare und Sicherheit bereits mitbringt.

| Bereich | Werkzeug | Zweck |
| --- | --- | --- |
| Backend | Django (Python) | Seiten, Geschäftslogik, Datenbankzugriff |
| Datenbank | PostgreSQL (lokal anfangs SQLite) | Speicherung aller Daten |
| Design | Tailwind CSS | modernes Layout ohne viel eigenes CSS |
| Interaktion | HTMX | Live-Updates im Konfigurator ohne Seitenreload |
| Zahlung (optional) | Stripe im Testmodus | realistischer Checkout ohne echtes Geld |
| Zusammenarbeit | GitHub | Code-Verwaltung im Team |
| Diagramme | draw.io | ERM, BPMN, UML |
| Hosting | localhost | Prototyp läuft lokal, Präsentation auf einem festen Demo-Laptop |

Wir hosten nicht, sondern betreiben den Prototyp nur lokal. Bewertet werden Doku und Präsentation, und so sparen wir Einrichtung, Kosten und Risiken wie Server-Aufwachzeiten. GitHub dient als Sicherung und zum Teilen des Codes im Team.

Dafür achten wir auf vier Punkte:

- Ein Demo-Laptop wird festgelegt und vorab mit Beamer und Auflösung getestet.
- Testdaten mit Bestellungen und Kundenkonten sind angelegt, damit die Betreiberseite nicht leer ist.
- Die README erklärt, wie jeder das Projekt lokal startet.
- Ein Backup-Video der Demo liegt bereit.

## Datenmodell

Wir haben eine Datenbank mit sieben Tabellen. Diese Struktur ist gleichzeitig die Grundlage für das ERM in der Doku.

| Tabelle | Inhalt | Beziehungen |
| --- | --- | --- |
| User / Kunde | Login, E-Mail, Name, Telefon (Django-User plus Profil) | hat 0..n Bestellungen und 0..n Mischungen |
| Adresse (optional) | gespeicherte Lieferadressen | gehört zu einem User |
| Zutat | Name, Typ (Basis, Geschmack, Booster), Preis, Nährwerte, Lagerbestand, Mindestbestand | in vielen Mischungen verwendet |
| Mischung | Name, Basis, Geschmack, Süße, Feld „ist_fertigprodukt“ | optional einem User zugeordnet |
| Mischung-Zutat | verknüpft Mischung und Booster (n:m) | gehört zu Mischung und Zutat |
| Bestellung | Datum, Status, Name, E-Mail, Lieferadresse, Gesamtpreis, User (darf leer sein) | hat 1..n Bestellpositionen |
| Bestellposition | Mischung, Menge, Preis zum Kaufzeitpunkt | gehört zu einer Bestellung |

**Fertige Mixe** sind Mischungen mit „ist_fertigprodukt = ja“. Eine eigene Produkttabelle entfällt.

**Gast oder Kundenkonto:** Wir trennen das nicht in zwei Tabellen. Bei Gastbestellungen bleibt das Feld User an der Bestellung leer. Name, E-Mail und Adresse werden bei jeder Bestellung mitgespeichert, damit alte Bestellungen die damalige Lieferadresse behalten. Registriert sich ein Gast später mit derselben E-Mail, ordnen wir seine Gastbestellungen dem neuen Konto zu.

## Design-Prototyp

Das Mockup (mischwerk-shop.html) setzt auf eine cleane, intuitive Seite, die sich bewusst von Standard-Shopify-Shops abhebt.

- Der Konfigurator ist direkt die Startseite statt einer Produktkachel-Übersicht.
- Eine Dose füllt sich Schicht für Schicht, während man Zutaten wählt. Der Mix-Name erscheint auf dem Etikett.
- Preis und Nährwerte rechnen sich live mit.
- Fertige Mixe stehen als ruhige Liste da und lassen sich im Konfigurator anpassen.
- Auf dem Handy liegen Preis und Warenkorb-Button in einer festen Leiste unten.
- Die Seite unterstützt Hell- und Dunkelmodus.

Das Mockup ist ein reines Frontend. In Django werden die Optionen später aus der Datenbank geladen. Das Ziel-Quiz aus dem Mockup entfällt.

## Gestaltungsrichtlinien

Ein offizielles Regelwerk wie Apples Human Interface Guidelines gibt es für Webshops nicht. Wir orientieren uns deshalb an einer Kombination anerkannter Quellen und zitieren sie im Design-Kapitel.

| Quelle | Wofür wir sie nutzen |
| --- | --- |
| Baymard Institute | Grundlage für den Shop: Produktseiten, Warenkorb, Checkout, Gastbestellung |
| Shopify Polaris | Vorbild für die Betreiberseite |
| Nielsen-Heuristiken (Nielsen Norman Group) | Bewertung des fertigen Prototyps in der Doku |
| WCAG | Barrierefreiheit: Kontraste, Tastaturbedienung, Formularbeschriftungen |

In der Doku ergänzen wir einen kurzen Abschnitt zu den deutschen Rechtspflichten eines echten Shops: Bestellbutton „zahlungspflichtig bestellen“, Impressum, Widerrufsbelehrung, Grundpreis pro Kilogramm nach Preisangabenverordnung sowie Nährwerte und Allergene nach Lebensmittelinformationsverordnung. Im Prototyp müssen diese nicht vollständig umgesetzt sein.

## Fahrplan

Vier Arbeitswochen plus drei Tage Puffer bis zur Abgabe am 26.11.2026, 23:59 Uhr.

### Vorlauf, 14.–26.10.: Vorbereitung

- [ ] GitHub-Repo und gemeinsamen Doku-Ordner anlegen
- [ ] Werkzeuge festlegen (draw.io, Doku-Vorlage)
- [ ] Offene Frage zur Betreiberseite mit dem Dozenten klären

### Woche 1, 27.10.–02.11.: Konzeption

- [ ] Idee, Zielgruppe und Wettbewerb beschreiben
- [ ] Anforderungen als Muss- und Kann-Kriterien festlegen
- [ ] ERM für die Datenbank erstellen
- [ ] BPMN-Diagramm für den Bestellprozess erstellen
- [ ] UML-Use-Case-Diagramm für Kunde, Gast und Betreiber erstellen
- [ ] Projektplan (Gantt) und Rollen festhalten

### Woche 2, 03.–09.11.: Design und Grundgerüst

- [ ] Mockup finalisieren, Name und Farben festlegen
- [ ] Django-Models aus dem ERM bauen, Testdaten anlegen
- [ ] Produktseite und Konfigurator in der Grundfunktion

### Woche 3, 10.–16.11.: Realisierung

- [ ] Warenkorb und Checkout für Gast und Konto
- [ ] Bestellungen speichern
- [ ] Betreiberseite mit Bestellübersicht, Rezeptur und Status
- [ ] Projekt auf allen vier Rechnern lokal lauffähig machen

### Woche 4, 17.–23.11.: Lagerwarnung und Feinschliff

- [ ] Lagerbestand pro Zutat und Warnung auf der Betreiberseite (Zusatzziel)
- [ ] Ausverkaufte Zutaten im Konfigurator ausgrauen
- [ ] Testen, Testdaten anlegen, Demo-Laptop festlegen, Screenshots für die Doku
- [ ] Doku inhaltlich fertigstellen
- [ ] Präsentation bauen und komplett proben

### Puffer, 24.–26.11.: Abgabe

- [ ] Korrekturlesen und Formatierung
- [ ] Backup-Video der Demo aufnehmen
- [ ] Doku und Präsentation per E-Mail abgeben

## Dokumentation und Präsentation

Die Doku zielt auf rund 28 Seiten. Die Modellierung bekommt am meisten Platz, weil dort die Methodenpflicht erfüllt wird.

| Kapitel | Seiten |
| --- | --- |
| Einleitung und Idee | 2 |
| Markt und Wettbewerb | 2 |
| Anforderungen | 3 |
| Modellierung (ERM, BPMN, UML) | 6–7 |
| Design | 4 |
| Realisierung | 6 |
| Projektmanagement | 4 |
| Fazit | 1 |

Für die 30-minütige Präsentation planen wir etwa 10 Minuten Live-Demo ein, mit einem vorab aufgenommenen Backup-Video, falls Internet oder Server ausfallen. Jede Person präsentiert ihren eigenen Teil.

## Rollen im Team

Jede Person hat einen Schwerpunkt, programmiert aber ein Stück mit, damit alle in der Präsentation mitreden können.

| Rolle | Schwerpunkt |
| --- | --- |
| Backend und Datenbank | Django-Models, Bestelllogik, Lagerwarnung |
| Frontend und Design | Templates, Konfigurator, Tailwind und HTMX |
| Modelle und Doku-Leitung | ERM, BPMN, UML, Doku-Struktur |
| Projektmanagement und Präsentation | Zeitplan, Abstimmung, Präsentation |
