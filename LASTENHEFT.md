# Lastenheft — P02

## Zielgruppe und Problem

Ein Team möchte Anwendungsprotokolle importieren, Fehler erkennen und Entwicklungsumgebungen überwachen.

## Studentischer Umfang

JSONL-Import in SQL, Fehlerübersicht und Abfrage-API; Elastic als gesonderte Variante.

Lokale Einzelbenutzung, synthetische Daten und ein vorführbarer kleiner Ablauf. Umfang bewusst begrenzen, damit eine erste Version innerhalb der Zielwoche möglich bleibt.

## Abnahmekriterien

- [ ] A1 — Wiederholter Import erzeugt keine Duplikate; fehlerhafte Zeilen landen in einer Fehlerliste.
- [ ] A2 — Abfrage nach Umgebung liefert passende Ereignisse und die richtige Fehleranzahl.
- [ ] A3 — API unterscheidet gültige Anfragen, ungültige Eingaben und unbekannte Umgebungen.
- [ ] A4 — Elastic nur mit einer echten Abfrage und einem Nachweis als umgesetzt kennzeichnen.

## Voraussetzungen

Abgrenzung P02-T01 (1. November 2026): Diese erste Vorbereitungseinheit legt nur Protokollformat und Datenwörterbuch fest und prüft fünf vorhandene JSONL-Zeilen im Arbeitsspeicher. Kaputte Zeile und wiederholte Kennung werden mit Zeilennummern ausgewiesen. A1 bleibt einschließlich Import-Idempotenz offen; auch A2 bis A4 sind nicht abgenommen. Datenbank, persistente Importlogik, API und Elastic gehören nicht zu dieser Einheit. Das begrenzte Ticketkriterium steht in [P02-T01](tickets/P02-T01.md).

- Python 3
- FastAPI und Pandas in einer eigenen Umgebung installieren

## Fünfminütige Vorführung

Dieselben Protokolle zweimal importieren und erklären, warum die Ereignisanzahl gleich bleibt.

Eine gültige Eingabe, einen Fehlerfall, das Ergebnis und die zuständige Quellcodedatei zeigen. Eine technische Entscheidung und eine Grenze erklären.

## Lieferumfang

- Genaue Startbefehle, verwendete Versionen und Beispieldaten.
- Tatsächlich durchgeführte Abnahme mit Ergebnissen und einem geeigneten Nachweis.
- Aktualisierte Tickets und Journal sowie ein lokaler Commit zum realen Fortschritt.
- Verständlicher Quellcode und nachvollziehbare Unterstützung durch den Assistenten.

## Grenzen

Öffentliche Bereitstellung und Produktivbetrieb gehören nicht zur Basis. Jede Werkzeugvariante benötigt einen eigenen Ausführungsnachweis. Zertifizierung, Berufserfahrung, Sprachniveau und Teamarbeit folgen nicht automatisch aus dieser Übung.

## Spätere Verwendung im Lebenslauf

Kleine ETL-Pipeline für synthetische Protokolle; nur tatsächlich verwendete Datenbanken und Bibliotheken nennen.

Derzeit zutreffend: „Eigenes Lernprojekt in Vorbereitung: Mini-DataHub und Protokollauswertung“. „Umgesetzt“ setzt die tatsächliche Abnahme voraus.
