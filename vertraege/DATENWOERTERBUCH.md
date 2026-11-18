# Protokollformat und Datenwörterbuch — P02-T01

Das Eingabeformat ist JSONL in UTF-8 ohne Byte-Reihenfolge-Markierung: pro physischer Zeile genau ein JSON-Objekt. LF und CRLF sind zulässig. Leere Zeilen sind fehlerhafte Eingaben. Eine abschließende Zeilenschaltung erzeugt keinen zusätzlichen Datensatz. Alle fünf Felder sind Pflichtfelder und Zeichenketten; zusätzliche Felder und `null` sind unzulässig.

| Feld | Bedeutung | Zulässige Werte | Synthetisches Beispiel |
|---|---|---|---|
| `ereignis_id` | Kennung eines Ereignisses | Mindestens ein Zeichen; exakter, groß-/kleinschreibungssensitiver Vergleich ohne Bereinigung | `e2` |
| `zeitpunkt` | Zeitpunkt in UTC | Exakt `JJJJ-MM-TTThh:mm:ssZ`, gültiges Kalenderdatum und gültige Uhrzeit; keine Sekundenbruchteile oder Zeitzonenversätze | `2026-10-01T09:01:00Z` |
| `umgebung` | Entwicklungsumgebung | `entwicklung` oder `test` | `test` |
| `stufe` | Protokollstufe | Bestehende feste Werte `INFO`, `WARN`, `ERROR` | `ERROR` |
| `nachricht` | Freier Meldungstext | Beliebige Zeichenkette, auch leer; Zeilenumbrüche innerhalb des Wertes nur als JSON-Escapesequenz | `Verbindung abgelehnt` |

Der [JSON-Schema-Vertrag](ereignis.schema.json) beschreibt die Struktur. `src/pipeline.py` prüft diesen kleinen Vertrag mit der Python-Standardbibliothek ausdrücklich selbst; er ist kein allgemeiner JSON-Schema-Validator. Die Kalenderprüfung erfolgt zusätzlich zum Zeitmuster.

## Fehler und wiederholte Kennungen

Der Prüfer liest alle Zeilen. Syntax- und Feldfehler erscheinen mit physischer Zeilennummer (ab 1), deutscher Meldung und ursprünglichem Inhalt unter `fehler`. Ein Fehler verhindert die Prüfung nachfolgender Zeilen nicht. Ungültige Ereignisse zählen nicht als gültig und reservieren keine Kennung.

Eine gültige Zeile mit bereits gesehener Kennung wird unter `wiederholungen` mit Kennung, aktueller Zeile und erster gültiger Fundstelle ausgewiesen. Das gilt auch bei abweichendem Nachrichteninhalt. Der Prüfer bewertet keine Inhaltskonflikte und verwirft oder speichert keine Ereignisse. `gueltige_zeilen` schließt wiederholte Kennungen ein; `eindeutige_kennungen` zählt unterschiedliche Kennungen innerhalb dieses einen Aufrufs.

Die unveränderte Datei `beispieldaten/logs.jsonl` enthält fünf Zeilen. Erwartung für diese Eingabe: vier gültige Ereigniszeilen, drei unterschiedliche Kennungen, Wiederholung `e2` in Zeile 4 mit erster Fundstelle in Zeile 2 und ein JSON-Fehler in Zeile 5.

## Grenze dieser Vorbereitungseinheit

Die Kennungsprüfung verwendet ausschließlich Arbeitsspeicher und beginnt bei jedem Aufruf neu. Sie belegt keine Import-Idempotenz über mehrere Läufe. Datenbank, persistenter Import, Abfrage-API und Elastic gehören nicht zu P02-T01. Lastenheft A1 bis A4 bleiben offen; die Fehlerliste ist nur eine Vorarbeit zu A1.

Der Prozessstatus 0 bedeutet, dass die Datei vollständig geprüft wurde, auch wenn die Ergebnisliste Eingabefehler enthält. Ein nicht lesbarer oder nicht als UTF-8 dekodierbarer Eingang führt zu Status 1 und einer deutschen Meldung.
