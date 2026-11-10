# Mini-DataHub und Protokollauswertung

Stand: 9. November 2026 — **P02-T03: lokale FastAPI-Abfrage mit Umgebungsfilter und minimaler Statusübersicht fertiggestellt und geprüft; Gesamtanwendung offen**. P02-T04 bleibt offen. Das ursprüngliche Entwicklungsziel vom 8. November wurde verfehlt; der Fortsetzungsplan sieht offene Entwicklung bis 15. November vor. Geschätzter Basisaufwand: 4 Stunden ohne Einrichtung und Erweiterungen.

Verlauf: Am 4. November war P02-T03 wegen fehlendem FastAPI blockiert ([Blockadenachweis](nachweise/P02-T03-voraussetzungen.json)). Die am 9. November bereitgestellte Offline-Umgebung wurde bei der Wiederaufnahme tatsächlich ausgeführt. [Ticket](tickets/P02-T03.md), [HTTP-Abnahme](nachweise/P02-T03-pruefung.json) und [Prüfskript](nachweise/p02-t03-pruefen.py) dokumentieren den jetzigen Abschluss. Vorhandene Teiländerungen sind erhalten.

Ein Team möchte Anwendungsprotokolle importieren, Fehler erkennen und Entwicklungsumgebungen überwachen.

Geplantes Gesamtergebnis: JSONL-Import in SQL, Fehlerübersicht und Abfrage-API; Elastic als gesonderte Variante.

Aktuell vorhanden: [Datenwörterbuch](vertraege/DATENWOERTERBUCH.md), JSON-Schema und ein Prüfer mit Python-Standardbibliothek für fünf unveränderte synthetische JSONL-Zeilen. Der optionale SQLite-Import validiert dieselben Felder, markiert das Wort „Zeitüberschreitung“ per Regex und behält je Kennung den ersten gültigen Inhalt. Fehler und Inhaltskonflikte erscheinen in der JSON-Ausgabe. Zwei getrennte Importprozesse ergaben drei und danach null neue Ereignisse bei unverändertem Bestand von drei. Ausführung, Regeln und Grenzen stehen in [START.md](START.md); [Abnahmenachweis](nachweise/P02-T02-pruefung.json).

Die lesende API bietet `GET /ereignisse?umgebung=entwicklung` beziehungsweise `test` und `GET /status`. Fehleranzahl bedeutet Anzahl der gespeicherten Ereignisse mit Stufe `ERROR`; ein Regex-Treffer zählt nicht automatisch als Fehler. Geprüft sind 200, 422 bei ungültiger Eingabe, 404 bei unbekannter Umgebung und 503 bei Datenbankproblemen. Die Originaldaten ergeben insgesamt drei Ereignisse und einen Fehler. Startbefehle und Wiederholung stehen in [START.md](START.md).

Die lokalen Szenarien zu A1 bis A3 sind begrenzt geprüft; übergreifende Lastenheftkästchen bleiben unverändert. Kein Gesamtabschluss oder Folgeticket. PostgreSQL, Pandas und Elastic sind weiterhin nicht ausgeführt; daraus wird keine praktische Produktkompetenz abgeleitet.

Vorgesehene Technologien: Python, Pandas, SQL, PostgreSQL, ETL, Regex, REST/API, FastAPI, Elastic Stack. Eine Nennung ist kein Nachweis einer Umsetzung.

## Einstieg

1. [Lastenheft](LASTENHEFT.md) lesen.
2. [Abgeschlossenes API-Ticket](tickets/P02-T03.md) öffnen.
3. [Technischen Einstieg](START.md) prüfen und ein Ticket nach dem anderen bearbeiten.
4. [Arbeitsjournal](ARBEITSJOURNAL.md) und echte Nachweise aktualisieren.

Abhängigkeiten: keine weiteren Projekte.

[Erweiterungen](VARIANTEN.md) haben einen eigenen Umsetzungsstand. [Private Unternehmenszuordnung](UNTERNEHMEN.lokal.md) bleibt außerhalb der Git-Verwaltung.

## Projektsprache

Dokumentation, selbst gewählte Bezeichner, Kommentare, Meldungen und Beispieldaten werden auf Deutsch geschrieben. Festgelegte API-Schlüssel, Sprachsyntax und Produktnamen bleiben unverändert.
