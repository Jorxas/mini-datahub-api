# Mini-DataHub und Protokollauswertung

Stand: 1. November 2026 — **P02-T01: Protokollformat und lokale Zeilenprüfung umgesetzt; Gesamtanwendung offen**. Geplanter Abschluss der Basis: 2026-11-02, spätestens 8. November 2026. Geschätzter Basisaufwand: 4 Stunden ohne Einrichtung und Erweiterungen.

Ein Team möchte Anwendungsprotokolle importieren, Fehler erkennen und Entwicklungsumgebungen überwachen.

Geplantes Gesamtergebnis: JSONL-Import in SQL, Fehlerübersicht und Abfrage-API; Elastic als gesonderte Variante.

Aktuell vorhanden: [Datenwörterbuch](vertraege/DATENWOERTERBUCH.md), JSON-Schema und ein Prüfer mit Python-Standardbibliothek für fünf unveränderte synthetische JSONL-Zeilen. Er weist eine kaputte Zeile und eine wiederholte Kennung mit Fundstellen aus. Es gibt keinen persistenten Import; Lastenheft A1 bis A4 bleiben offen. Ausführung und Abnahme stehen in [START.md](START.md).

Vorgesehene Technologien: Python, Pandas, SQL, PostgreSQL, ETL, Regex, REST/API, FastAPI, Elastic Stack. Eine Nennung ist kein Nachweis einer Umsetzung.

## Einstieg

1. [Lastenheft](LASTENHEFT.md) lesen.
2. [Erstes Ticket](tickets/P02-T01.md) öffnen.
3. [Technischen Einstieg](START.md) prüfen und ein Ticket nach dem anderen bearbeiten.
4. [Arbeitsjournal](ARBEITSJOURNAL.md) und echte Nachweise aktualisieren.

Abhängigkeiten: keine weiteren Projekte.

[Erweiterungen](VARIANTEN.md) haben einen eigenen Umsetzungsstand. [Private Unternehmenszuordnung](UNTERNEHMEN.lokal.md) bleibt außerhalb der Git-Verwaltung.

## Projektsprache

Dokumentation, selbst gewählte Bezeichner, Kommentare, Meldungen und Beispieldaten werden auf Deutsch geschrieben. Festgelegte API-Schlüssel, Sprachsyntax und Produktnamen bleiben unverändert.
