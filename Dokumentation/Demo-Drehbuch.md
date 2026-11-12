# Demo-Drehbuch

Live-Demo, ca. 10 Minuten innerhalb der 30-minütigen Präsentation. Alle Zahlen unten gelten für eine frisch zurückgesetzte Datenbank (siehe „Vorbereitung“). Der Ablauf ist einmal komplett durchgetestet.

## Einordnung in die Präsentation

| Min. | Teil | Wer |
| --- | --- | --- |
| 0–3 | Einstieg: Problem, Idee Mischwerk | PM |
| 3–5 | Markt und Wettbewerb | PM |
| 5–8 | Anforderungen (Muss/Kann) | Modelle/Doku |
| 8–14 | Modellierung: ERM, BPMN, Use Cases, Entscheidungstabelle | Modelle/Doku |
| **14–24** | **Live-Demo** | **Frontend + Backend** |
| 24–27 | Realisierung: Technik, Entscheidungen, Grenzen | Backend |
| 27–29 | Projektmanagement: Ablauf, Erfahrungen | PM |
| 29–30 | Fazit, Fragen | alle |

Die Demo kommt direkt nach der Modellierung. So kann man sagen: „Genau diesen Prozess aus dem BPMN zeigen wir jetzt live.“

## Rollen während der Demo

- **Fahrer:** eine Person klickt die ganze Demo, ohne zu reden. Das verhindert Hektik und Tippfehler.
- **Sprecher:** wechseln pro Szene. Szenen 1–4 erklärt Frontend, Szene 5 Backend.
- Der Fahrer kennt das Drehbuch auswendig, die Sprecher sagen jeweils „Wir klicken jetzt auf …“.

## Vorbereitung

### Am Vortag
- Demo-Laptop festlegen, mit Beamer testen (1920 × 1080, Browser-Zoom 125 %).
- Projekt auf den aktuellen Stand bringen und einmal komplett durchspielen.
- Backup-Video aufnehmen (siehe unten).

### 30 Minuten vorher
```bash
source .venv/bin/activate
git pull
pip install -r requirements.txt && npm install && npm run build
rm db.sqlite3
python manage.py migrate
python manage.py load_demo_data
python manage.py load_demo_orders
python manage.py runserver
```
Internet wird nicht gebraucht, alles läuft lokal (auch CSS und HTMX).

### Fenster einrichten
| Fenster | Browser | Tabs |
| --- | --- | --- |
| **A – Shop** | normales Fenster, nicht angemeldet | `127.0.0.1:8000` |
| **B – Betrieb** | Inkognito-Fenster (eigene Sitzung) | 1. `/betrieb/` 2. `/betrieb/lager/` 3. `/admin/shop/ingredient/?q=Kokos` |

In Fenster B vorher anmelden: `betrieb@mischwerk.de` / `mischwerk-demo`.

Außerdem: Benachrichtigungen aus, Lesezeichenleiste aus, Netzteil dran, heller Modus (Dunkelmodus ist nicht durchgetestet). Gastdaten aus Szene 4 als Notiz bereitlegen.

## Ablauf

### Szene 1 – Startseite (0:00–1:00)
**Klicks:** Fenster A, Startseite langsam nach unten scrollen bis zu den fertigen Produkten.

**Sagen:**
- Mischwerk verkauft Pulver in vier Linien: Protein Shake, Clear Protein, Energy, Hydration.
- Unser Alleinstellungsmerkmal „Sieh, was drin ist“: Jedes Produktbild wird aus der Rezeptur erzeugt, jede Zutat ist eine farbige Schicht im Sichtfenster der Dose. Wir brauchen keine Produktfotos.
- Produkte haben mehrere Sorten (Farbpunkte, „10 Sorten“) und Preisstufen, z. B. Energy Classic, Vital und Pump.

### Szene 2 – Fertigprodukt (1:00–2:00)
**Klicks:** Karte **Whey Protein** → Sorte **Vanille**, dann zurück auf **Schoko** → Größe **1,8 kg**.

**Sagen:**
- Sorte und Größe wählt man auf der Produktseite, die Dose ändert sich mit.
- Groß: 75,60 € statt 2 × 42,00 €, Grundpreis sinkt von 46,67 auf 42,00 €/kg. Der Grundpreis pro kg ist nach Preisangabenverordnung Pflicht.
- **Kokos ist durchgestrichen**, also ausverkauft. Das greifen wir in Szene 5 wieder auf.

### Szene 3 – Konfigurator (2:00–5:00) · Höhepunkt
**Klicks und Sagen:**
1. Navigation **Konfigurator** → Linie **Energy**. *„Die Energy-Basis enthält schon 150 mg Koffein, deshalb gibt es hier keinen Koffein-Booster.“* (Entscheidungstabelle, Bedingung B2)
2. Linie **Protein Shake**.
3. Basis **Whey Isolat**, Geschmack **Erdbeere**. *„Das Etikett färbt sich um, Preis und Nährwerte rechnen live mit, ohne die Seite neu zu laden (HTMX).“*
4. Booster **Kreatin** → neue Schicht rieselt in die Dose.
5. Booster **Koffein** → gelber Hinweis *„Enthält 80 mg Koffein pro Portion“*.
6. Booster **Vitamin D3** und **Kollagen** → rote Meldung *„Bitte höchstens 3 Booster wählen.“* (Regel R3) → **Kollagen** und **Vitamin D3** wieder abwählen.
7. Auf **Kokos** zeigen: ausgegraut, nicht klickbar (Regel R4).
8. Name **Demo Shake** eintippen → steht sofort auf der Dose.
9. Größe **Groß · 60 Portionen** → **124,20 €** → **In den Warenkorb**.

### Szene 4 – Warenkorb und Checkout als Gast (5:00–6:30)
**Klicks:** Warenkorb zeigen (Plus/Minus erwähnen, Menge bei 1 lassen) → **Zur Kasse** → Hinweis „Schon Kunde? Anmelden“ zeigen, aber als Gast weiter → Daten eingeben:

| Feld | Wert |
| --- | --- |
| Name | Sara Yilmaz |
| E-Mail | sara.yilmaz@example.com |
| Straße | Lindenallee 3 |
| PLZ / Ort | 70173 Stuttgart |

→ **Zahlungspflichtig bestellen** → Bestätigung **Bestellung #10**.

**Sagen:**
- Gastbestellung ohne Konto, Button-Text „zahlungspflichtig bestellen“ wie gesetzlich vorgeschrieben.
- Der Shop hat vor dem Speichern den Lagerbestand geprüft und abgebucht (BPMN, Lane „Shop“). Der Preis zum Kaufzeitpunkt ist an der Bestellposition gespeichert.

### Szene 5 – Betreiberseite (6:30–9:00)
**Klicks:** Fenster B, Tab `/betrieb/` neu laden.
1. Gelbe **Lagerwarnung** (Kollagen, Haselnuss, Kokos). *„Kollagen ist durch eine frühere Bestellung unter den Mindestbestand gefallen.“*
2. Oben **#10 Sara Yilmaz · Gast · offen** → anklicken.
3. **Rezeptur** zeigen: *„1 × Demo Shake · 1,8 kg: Whey Isolat, Erdbeere, normal, Kreatin, Koffein. Genau das muss gemischt werden.“*
4. **→ in Bearbeitung** klicken: Status wechselt ohne Neuladen (Zustandsdiagramm).
5. Tab **Lager**: Whey Isolat jetzt **420** statt 480 Portionen, die große Dose hat 60 Portionen verbraucht.
6. Tab **Admin**: bei Kokos Bestand **600** eintragen → **Speichern**.
7. Fenster A, **Konfigurator** neu laden → **Kokos ist wieder wählbar**. *„Damit schließt sich der Kreis von der Bestellung über das Lager zurück in den Shop.“*

### Szene 6 – Abschluss (9:00–10:00)
**Sagen:** kurz zusammenfassen, was gezeigt wurde. Alle Muss-Anforderungen und das Zusatzziel Lagerwarnung sind umgesetzt. Danach zurück zu den Folien.

### Reserve-Szenen (bei Zeit oder für Fragen)
- **Kundenkonto:** in Fenster A mit `erika@example.com` / `mischwerk-demo` anmelden → „Mein Konto“: gespeicherte Mischungen (Morning Fuel, Night Shake) mit „Nachbestellen“, Bestellhistorie mit Status. Bei der Kasse sind Name und Adresse vorausgefüllt.
- **Handy-Ansicht:** Entwicklertools → Gerätemodus → Konfigurator mit fester Preisleiste unten.
- **Registrierung:** Gast registriert sich mit derselben E-Mail → frühere Gastbestellungen hängen am neuen Konto.

## Bezug zu den Modellen

| Demo-Moment | Modell in der Doku |
| --- | --- |
| Gast bestellt, Shop prüft Lager, Betrieb bearbeitet | BPMN Bestellprozess |
| max. 3 Booster, Kokos ausverkauft, kein Koffein-Booster bei Energy | Entscheidungstabelle (R3, R4, B2) |
| Status offen → in Bearbeitung | Zustandsdiagramm Bestellung |
| Gast, Kunde, Betreiber mit ihren Aufgaben | Use-Case-Diagramm |
| Bestellposition mit Größe und Kaufpreis, Rezeptur aus Mischung und Zutaten | ERM |

## Wenn etwas schiefgeht

| Problem | Lösung |
| --- | --- |
| Server läuft nicht oder Laptop streikt | Backup-Video abspielen |
| Seite ohne Styling | `npm run build`, Seite neu laden |
| „Nicht genug auf Lager“ beim Bestellen | Datenbank wurde nach einer Probe nicht zurückgesetzt, Befehle aus „30 Minuten vorher“ ausführen |
| Betrieb nicht angemeldet | Login `betrieb@mischwerk.de` / `mischwerk-demo` |
| Animation ruckelt | weiterreden, die Werte stimmen trotzdem |

Nach **jeder Probe** die Datenbank zurücksetzen (Befehle aus „30 Minuten vorher“, ohne `git pull`), sonst stimmen Bestellnummer und Lagerzahlen nicht mehr.

## Backup-Video

- Mit QuickTime oder `Cmd + Shift + 5` den Bildschirm aufnehmen, 1080p, Browser-Zoom wie in der Präsentation.
- Genau dieses Drehbuch abspielen, ohne Ton. In der Präsentation wird live dazu gesprochen.
- Datei lokal auf dem Demo-Laptop und zusätzlich auf einem USB-Stick ablegen.
