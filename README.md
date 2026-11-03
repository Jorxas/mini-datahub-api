# Mini-DataHub und Protokollauswertung

Stand: 2. November 2026 — **P02-T02: lokaler idempotenter SQLite-Import umgesetzt und geprüft; Gesamtanwendung offen**. Die weiteren Basisphasen bleiben zeitlich getrennt; Abschluss spätestens 8. November 2026. Geschätzter Basisaufwand: 4 Stunden ohne Einrichtung und Erweiterungen.

Ein Team möchte Anwendungsprotokolle importieren, Fehler erkennen und Entwicklungsumgebungen überwachen.

Geplantes Gesamtergebnis: JSONL-Import in SQL, Fehlerübersicht und Abfrage-API; Elastic als gesonderte Variante.

Aktuell vorhanden: [Datenwörterbuch](vertraege/DATENWOERTERBUCH.md), JSON-Schema und ein Prüfer mit Python-Standardbibliothek für fünf unveränderte synthetische JSONL-Zeilen. Der optionale SQLite-Import validiert dieselben Felder, markiert das Wort „Zeitüberschreitung“ per Regex und behält je Kennung den ersten gültigen Inhalt. Fehler und Inhaltskonflikte erscheinen in der JSON-Ausgabe. Zwei getrennte Importprozesse ergaben drei und danach null neue Ereignisse bei unverändertem Bestand von drei. Ausführung, Regeln und Grenzen stehen in [START.md](START.md); [Abnahmenachweis](nachweise/P02-T02-pruefung.json).

Das lokale Importszenario zu A1 ist geprüft; die übergreifenden Lastenheftkästchen werden in dieser begrenzten Phase nicht geändert. Umgebungsabfrage und Fehleranzahl (A2), API (A3) und Elastic (A4) sind nicht umgesetzt.

Vorgesehene Technologien: Python, Pandas, SQL, PostgreSQL, ETL, Regex, REST/API, FastAPI, Elastic Stack. Eine Nennung ist kein Nachweis einer Umsetzung.

## Einstieg

1. [Lastenheft](LASTENHEFT.md) lesen.
2. [Abgeschlossenes Importticket](tickets/P02-T02.md) öffnen.
3. [Technischen Einstieg](START.md) prüfen und ein Ticket nach dem anderen bearbeiten.
4. [Arbeitsjournal](ARBEITSJOURNAL.md) und echte Nachweise aktualisieren.

Abhängigkeiten: keine weiteren Projekte.

[Erweiterungen](VARIANTEN.md) haben einen eigenen Umsetzungsstand. [Private Unternehmenszuordnung](UNTERNEHMEN.lokal.md) bleibt außerhalb der Git-Verwaltung.

## Projektsprache

Dokumentation, selbst gewählte Bezeichner, Kommentare, Meldungen und Beispieldaten werden auf Deutsch geschrieben. Festgelegte API-Schlüssel, Sprachsyntax und Produktnamen bleiben unverändert.
