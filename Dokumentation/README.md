# Dokumentation

Alle Diagramme liegen als `.drawio` zum Bearbeiten (draw.io Desktop oder https://app.diagrams.net) und als `.png` für die Doku vor.
Sie beschreiben den Stand der Implementierung.

| Diagramm | Methode | Inhalt |
| --- | --- | --- |
| `ERM` | ERM (Krähenfuß) | Tabellen, Attribute und Beziehungen der Datenbank |
| `BPMN_Bestellprozess` | BPMN 2.0 | Bestellung vom Kaufwunsch bis zum Versand, mit Lagerprüfung und Lagerwarnung |
| `UseCase` | UML-Use-Case | Anwendungsfälle von Gast, Kunde und Betreiber |
| `Entscheidungstabelle_Konfigurator` | Entscheidungstabelle (ET) | Regeln, wann eine Mischung in den Warenkorb darf |
| `Zustandsdiagramm_Bestellung` | UML-Zustandsdiagramm | Status einer Bestellung: offen, in Bearbeitung, versendet |

Für die schriftliche Abgabe: [Gliederung.md](Gliederung.md) mit Kapiteln, Seitenzahlen und Zuständigkeiten.

Für die Präsentation: [Demo-Drehbuch.md](Demo-Drehbuch.md) mit Ablauf, Klicks, Logins und Notfallplan für die Live-Demo.

Ändert sich der Prototyp, müssen die betroffenen Diagramme angepasst und die PNGs neu exportiert werden (in draw.io: Datei → Exportieren als → PNG).

## ERM

- **User** ist der eingebaute Django-User (`auth_user`). Gezeigt sind nur die relevanten Spalten.
- **Profil** ergänzt den User um die Telefonnummer (1:1). In der Planung zählt es zusammen mit User als eine Tabelle, technisch sind es zwei.
- **Fertige Produkte** sind Mischungen mit `is_ready_made = true`. Mischungen mit gleichem Namen sind Sorten eines Produkts.
- **Gastbestellungen** haben keine `user_id`. Name, E-Mail und Adresse stehen an jeder Bestellung.
- **Bestellposition** speichert Größe (`size`) und Preis zum Kaufzeitpunkt (`unit_price`).
- **Mischung-Zutat** verknüpft Mischung und Booster (n:m), höchstens drei pro Mischung (Regel im Formular).

## BPMN

Zwei Pools: Kunde und Mischwerk (Lanes Shop und Betrieb). Der Shop prüft vor dem Speichern den Lagerbestand. Reicht er nicht, wird die Bestellung abgelehnt. Nach dem Speichern laufen Bearbeitung und Lagerprüfung parallel: Fällt eine Zutat unter den Mindestbestand, erscheint die Lagerwarnung, und der Betrieb füllt im Admin nach.

## Entscheidungstabelle

Konsolidierte Form mit „–“ für „egal“. Die sieben Regeln decken alle 64 Kombinationen der sechs Bedingungen genau einmal ab.
