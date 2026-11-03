# Technischer Einstieg — P02

## Protokolle lokal prüfen

Im Projektordner mit der vorhandenen Laufzeit ausführen; keine zusätzlichen Bibliotheken erforderlich:

~~~powershell
uv --cache-dir ausgabe/uv-zwischenspeicher run --offline --python 3.12 python -X utf8 src/pipeline.py
~~~

Tatsächlich verwendete Laufzeit: Python 3.12.14. Der lokale Zwischenspeicher hält die Schreibzugriffe innerhalb des Projektordners. Der voreingestellte uv-Zwischenspeicher war in dieser Ausführung nicht beschreibbar.

Ohne Pfadangabe liest das Programm `beispieldaten/logs.jsonl`. Ein optionaler Dateipfad kann als letztes Argument übergeben werden. Die Ausgabe enthält Zeilenzahlen, Fehler mit Inhalt und wiederholte Kennungen mit beiden Fundstellen. Das Programm schreibt keine Importdaten.

## Begrenzte Abnahme wiederholen

~~~powershell
uv --cache-dir ausgabe/uv-zwischenspeicher run --offline --python 3.12 python -X utf8 nachweise/p02-t01-pruefen.py
~~~

Die Abnahme führt den Prüfer als Unterprozess aus und prüft die fünf Originalzeilen, vier gültige Zeilen, drei unterschiedliche Kennungen, `e2` in Zeile 4 gegenüber Zeile 2, den JSON-Fehler in Zeile 5 und die unveränderte Eingabedatei anhand SHA-256. Sie schreibt die tatsächliche Ausgabe, Laufzeitversion, Zeitpunkte, Prozessstatus und Prüfergebnisse nach `nachweise/P02-T01-pruefung.json`. Eine erneute Abnahme ersetzt diese Nachweisdatei durch den neuen Lauf.

Format und Grenzen: [Datenwörterbuch](vertraege/DATENWOERTERBUCH.md). Dies ist keine Prüfung wiederholter persistenter Importe. Lastenheft A1 bis A4 und sämtliche späteren Tickets bleiben offen.

## P02-T02: Idempotent nach SQLite importieren

Im Projektordner ausführen; der Zielordner muss bestehen:

~~~powershell
New-Item -ItemType Directory -Force ausgabe | Out-Null
uv --cache-dir ausgabe/uv-zwischenspeicher run --offline --python 3.12 python -X utf8 src/pipeline.py --datenbank ausgabe/protokolle.sqlite
uv --cache-dir ausgabe/uv-zwischenspeicher run --offline --python 3.12 python -X utf8 src/pipeline.py --datenbank ausgabe/protokolle.sqlite
~~~

Bei einer neuen Datenbank: erster Lauf `eingefuegt: 3`, `uebersprungen: 1`; zweiter Lauf `eingefuegt: 0`, `uebersprungen: 4`. Der Bestand `gespeicherte_ereignisse` bleibt drei. Beide Läufe lesen fünf Zeilen, davon vier gültige, und melden die kaputte fünfte Zeile. Ohne `--datenbank` bleibt der bisherige reine Prüfmodus erhalten. Ein optionaler Eingabepfad ersetzt weiterhin `beispieldaten/logs.jsonl`.

`sql/schema.sql` legt die Ereignistabelle an. `ereignis_id` ist der Primärschlüssel; `ON CONFLICT(ereignis_id) DO NOTHING` verhindert weitere Einfügungen derselben Kennung auch in späteren Prozessen. Der erste gültige Inhalt bleibt bestehen. Abweichende Inhalte derselben Kennung erscheinen unter `konflikte`; ein solcher Konflikt überschreibt nichts. Ungültige Zeilen reservieren keine Kennung. Syntax- und Feldfehler stehen mit Zeilennummer und Originalinhalt unter `fehler` in der JSON-Ausgabe; diese Liste wird nicht in einer eigenen Datenbanktabelle archiviert.

Der reguläre Ausdruck `\bZeitüberschreitung\b` sucht ohne Beachtung der Groß-/Kleinschreibung im Nachrichtenfeld. Das zusätzliche SQLite-Feld `ist_zeitueberschreitung` enthält 0 oder 1. Es beschreibt einen Worttreffer, keine fachliche Fehlerbewertung oder Fehleranzahl. Die bestehenden fünf Eingabefelder bleiben unverändert.

Gültige Ereignisse werden in einer Transaktion eingefügt. Ungültige einzelne JSONL-Zeilen werden gemeldet, während gültige Zeilen importiert werden. Ein Datei-, UTF-8- oder SQLite-Fehler führt zu Prozessstatus 1; Einfügungen des laufenden Imports werden zurückgenommen. Eine neu angelegte leere Tabelle kann danach bestehen bleiben. Status 0 bedeutet einen vollständig verarbeiteten Import, auch bei gemeldeten Zeilenfehlern oder Konflikten. Vorhandene Datenbanken müssen das aktuelle Schema besitzen; eine Migration alter Schemata gehört nicht zu diesem Ticket.

## Importabnahme wiederholen

~~~powershell
uv --cache-dir ausgabe/uv-zwischenspeicher run --offline --python 3.12 python -X utf8 nachweise/p02-t02-pruefen.py
~~~

Tatsächlich geprüft: Python 3.12.14, SQLite 3.53.1, **12/12 Prüfungen erfüllt**. Der Prüflauf startet sechs getrennte CLI-Prozesse und liest den SQLite-Inhalt direkt: zwei Originalimporte, zusätzliche synthetische Randfälle, ein UTF-8-Lesefehler, ein ungültiger Datenbankpfad und der bisherige Prüfmodus. Randfälle prüfen Pflichtfelder, Typen, Werte, Kalenderdatum, Leerzeile, Inhaltskonflikt sowie Regex-Schreibung und Wortgrenze. SHA-256 und Zeilenanzahl belegen die unveränderten fünf Originalzeilen. Temporäre Prüfdaten liegen unter `ausgabe/` und werden nach erfolgreicher Prüfung entfernt.

Die wiederholbare Abnahme ersetzt `nachweise/P02-T02-pruefung.json` durch den neuen tatsächlichen Lauf. Darin stehen Prozessbefehle, Ausgaben, Versionen, Datenbankzeilen, Prüfergebnisse und Prüfdauer. Die ursprüngliche Arbeitseinheit samt behobenem Prüflauffehler ist separat unter `nachweise/P02-T02-arbeitseinheit.json` dokumentiert.

Abgrenzung: nur lokaler SQLite-Import. Keine Umgebungsabfrage, API, PostgreSQL-, Pandas-, FastAPI- oder Elastic-Ausführung. Das ursprüngliche T02-Kriterium zur Umgebungsabfrage wurde deshalb im Ticket ersetzt; übergreifende Lastenheftkriterien bleiben unverändert. Die Aussagen weiter oben zur reinen Vorbereitung beziehen sich auf P02-T01.
