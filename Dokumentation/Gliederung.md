# Gliederung der Dokumentation

Ziel: ca. 28 Seiten Text (Vorgabe 25 bis max. 30). Verzeichnisse und Anhang zählen in der Regel nicht mit, das bitte beim Dozenten kurz klären.

Bewertet werden Form, Gestaltung, Struktur und Inhalt (60 % der Note). Pflicht sind mindestens eine Methode der Systemanalyse und das Kapitel Projektmanagement mit Notwendigkeit, positiven und negativen Erfahrungen sowie Bewertung in der Gruppe.

## Übersicht

| Kapitel | Seiten | Verantwortlich (Vorschlag) | Material im Repo |
| --- | --- | --- | --- |
| 1 Einleitung | 2 | PM | `AUFGABE.md` |
| 2 Markt und Wettbewerb | 2 | PM | `AUFGABE.md` (Wettbewerber) |
| 3 Anforderungen | 3 | Modelle/Doku | Abschnitt „Funktionsumfang“ in `AUFGABE.md` |
| 4 Modellierung | 6 | Modelle/Doku | alle Diagramme in `Dokumentation/` |
| 5 Design | 4 | Frontend | Screenshots, Gestaltungsquellen in `AUFGABE.md` |
| 6 Realisierung und Evaluation | 6 | Backend | Code, `README.md`, Tests |
| 7 Projektmanagement | 4 | PM | Git-Verlauf, Fahrplan in `AUFGABE.md` |
| 8 Fazit und Ausblick | 1 | alle | – |
| **Summe** | **28** | | |

## Vorspann (zählt meist nicht mit)

- Deckblatt (Thema 3.5, Titel „Mischwerk“, Namen, Matrikelnummern, Datum, Dozent)
- Inhaltsverzeichnis
- Abbildungs- und Tabellenverzeichnis
- Abkürzungsverzeichnis (z. B. BPMN, ERM, ET, HTMX, PAngV, LMIV, WCAG)

## 1 Einleitung (2 S.)

1.1 **Ausgangssituation und Aufgabenstellung:** Thema 3.5 „Internet-Shop für definierte Artikel“, Rahmen der Fallstudie.
1.2 **Projektidee Mischwerk:** Protein- und Performance-Drinks selbst zusammenstellen, ähnlich wie mymuesli. Dazu fertige Produkte und eine Betreiberseite mit Rezeptur.
1.3 **Ziel und Aufbau der Arbeit:** Was der Prototyp zeigen soll, kurzer Überblick über die Kapitel.

## 2 Markt und Wettbewerb (2 S.)

2.1 **Markt für Sporternährung:** Trend zu Personalisierung, Clear Protein, Energy und Hydration als eigene Kategorien.
2.2 **Wettbewerber:** Vergleichstabelle mit Gainful, INFINIT Nutrition und True Nutrition (personalisiert, USA) sowie ESN, More Nutrition und foodspring (fertige Produkte, DACH). Spalten zum Beispiel: Personalisierung, Produktlinien, Preis pro kg, Transparenz der Zutaten.
2.3 **Zielgruppe und Alleinstellungsmerkmal:** Wer kauft bei uns? USP: Konfigurator mit Live-Preis und Nährwerten, „Sieh, was drin ist“ (Dose mit Zutatenschichten), klare Dosierungsregeln.

## 3 Anforderungen (3 S.)

3.1 **Vorgehen:** Einteilung in Muss- und Kann-Kriterien, Abgrenzung des Prototyps.
3.2 **Funktionale Anforderungen:** Tabelle mit ID, Anforderung, Muss/Kann und Status (umgesetzt ja/nein). Beispiele: Shop mit Sorten und Größen, Konfigurator, max. 3 Booster, Koffein-Hinweis, Gast-Checkout, Kundenkonto, Betreiberseite, Lagerwarnung.
3.3 **Nicht-funktionale Anforderungen:** Bedienbarkeit, Barrierefreiheit (WCAG), Reaktionszeit der Live-Vorschau, mobile Nutzung, lokal lauffähig, Datensicherheit im Grundsatz.
3.4 **Abgrenzung:** bewusst nicht umgesetzt sind Hosting, echte Zahlung, vollständige Rechtspflichten, E-Mail-Versand und das Ziel-Quiz aus dem Mockup.

## 4 Modellierung (6 S.)

4.1 **Methodenwahl:** Warum genau diese Methoden und was jede beiträgt (Akteure, Ablauf, Daten, Regeln, Zustände).
4.2 **Use-Case-Diagramm** (`UseCase.png`): Akteure Gast, Kunde und Betreiber, «include» und «extend» erklären.
4.3 **BPMN Bestellprozess** (`BPMN_Bestellprozess.png`): Pools und Lanes, Lagerprüfung, paralleles und ereignisbasiertes Gateway, Nachrichtenflüsse.
4.4 **ERM** (`ERM.png`): Entitäten, Beziehungen und Kardinalitäten. Entscheidungen erklären: fertige Produkte als Mischung, Gast ohne User, Preis zum Kaufzeitpunkt. Hinweis User und Profil (sieben fachliche, acht technische Tabellen).
4.5 **Entscheidungstabelle** (`Entscheidungstabelle_Konfigurator.png`): Bedingungen, Aktionen, Konsolidierung, Vollständigkeitsprüfung mit 64 Fällen.
4.6 **Zustandsdiagramm Bestellung** (`Zustandsdiagramm_Bestellung.png`): Status und Übergänge, Korrekturen.

Tipp: Jedes Diagramm in drei Schritten beschreiben: Was zeigt es, wie liest man es, welche Entscheidung steckt dahinter.

## 5 Design (4 S.)

5.1 **Gestaltungsrichtlinien:** Baymard Institute (Shop, Checkout, Gastbestellung), Shopify Polaris (Betreiberseite), Nielsen-Heuristiken, WCAG. Jeweils mit Quelle.
5.2 **Designentscheidungen:**
- Konfigurator als Herzstück
- Dose mit Zutatenschichten statt Produktfotos
- Farben und Typografie
- feste Preisleiste auf dem Handy
- Animationen mit Rücksicht auf „reduzierte Bewegung“
- Hell- und Dunkelmodus

5.3 **Wichtige Bildschirme:** Screenshots von Startseite, Produktseite, Konfigurator, Kasse und Betreiberseite, jeweils mit kurzer Erklärung.
5.4 **Rechtliche Anforderungen an einen echten Shop:** Button „zahlungspflichtig bestellen“, Impressum, Widerrufsbelehrung, Grundpreis pro kg (PAngV), Nährwerte und Allergene (LMIV). Was der Prototyp davon umsetzt und was nicht.

## 6 Realisierung und Evaluation (6 S.)

6.1 **Technologie-Stack und Begründung:** Django, SQLite (später PostgreSQL), Tailwind CSS, HTMX. Warum kein Hosting.
6.2 **Architektur:** Django-Apps `shop`, `orders`, `accounts` und `backoffice`, Ablauf einer Anfrage, Live-Vorschau mit HTMX.
6.3 **Umsetzung zentraler Funktionen:**
- Konfigurator mit Live-Berechnung und Animation
- Produktlinien, Sorten und Größen (Rabatt auf die große Dose)
- Warenkorb in der Session, Checkout als Gast oder mit Konto
- Betreiberseite mit Rezeptur und Statuswechsel
- Lagerverwaltung: Abbuchen, Ablehnen, Warnung

6.4 **Qualitätssicherung:** automatisierte Tests (`python manage.py test`), Browser-Tests, gefundene und behobene Fehler als Beispiele. Zum Beispiel die Live-Vorschau, die wegen der Formularprüfung von HTMX nicht lief, oder die falsche Sortierung der Bestellübersicht.
6.5 **Evaluation nach Nielsen:** die zehn Heuristiken kurz auf den Prototyp anwenden, als Tabelle mit erfüllt / teilweise / offen.
6.6 **Grenzen des Prototyps:** keine E-Mail-Bestätigung (Gastbestellungen übernehmbar), keine Zahlung, Adresstabelle ungenutzt, Beispielwerte für Preise und Nährwerte, nur lokal.
6.7 **Einsatz von KI-Werkzeugen:** wofür KI genutzt wurde (z. B. Code, Diagrammentwürfe) und wie die Ergebnisse geprüft wurden. Laut Aufgabenstellung sind KI-Tools erlaubt, transparent machen ist trotzdem sinnvoll.

## 7 Projektmanagement (4 S.) – Pflichtkapitel

7.1 **Notwendigkeit von Projektmanagement:** vier Personen, feste Abgabe, Abhängigkeiten zwischen Modell, Code und Doku.
7.2 **Organisation:** Rollen, Kommunikation, Werkzeuge (GitHub, draw.io, Doku-Vorlage).
7.3 **Zeitplan:** Gantt-Diagramm, Soll (Fahrplan) gegen Ist.
7.4 **Positive Erfahrungen**
7.5 **Negative Erfahrungen und Lehren daraus**
7.6 **Bewertung in der Gruppe:** gemeinsame Einschätzung, ggf. pro Person ein kurzer Absatz.

Dieses Kapitel kann nur das Team selbst schreiben. Am besten führt ihr ab sofort ein kurzes Projekttagebuch: Datum, was passiert ist, was gut oder schlecht lief.

## 8 Fazit und Ausblick (1 S.)

8.1 **Zielerreichung:** Muss-Kriterien und Zusatzziel erfüllt, Bezug zu Kapitel 3.
8.2 **Ausblick:** Hosting, Stripe-Zahlung, E-Mail-Bestätigung, Abo-Modell, Nachbestell-Erinnerung, echte Nährwert- und Allergendaten.

## Anhang (zählt meist nicht mit)

- Literatur- und Quellenverzeichnis
- Diagramme in voller Größe
- Installationsanleitung (aus `README.md`)
- Demo-Logins und Testdaten
- ggf. Eigenständigkeitserklärung

## Hinweise zur Form

- Eine Vorlage für alle (Schrift, Ränder, Überschriften), früh festlegen, damit am Ende nicht formatiert werden muss.
- Abbildungen und Tabellen durchnummerieren, mit Beschriftung und Quelle („eigene Darstellung“).
- Einheitliche Begriffe: z. B. immer „Mischung“, „Zutat“, „Betreiberseite“, so wie im Prototyp.
- Einheitliche Ansprache: entweder „wir“ oder neutral, nicht mischen.
- Kapitel 4 und 6 aufeinander beziehen („wie im BPMN in Abschnitt 4.3 dargestellt“).
