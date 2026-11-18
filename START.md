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

## P02-T03: Verlauf der fehlenden API-Voraussetzung (4. November)

Am 4. November 2026 wurde die vorhandene Python-3.12-Laufzeit geprüft. Die Abfrage von `importlib.metadata.version('fastapi')` scheiterte mit `PackageNotFoundError`. Auch folgender tatsächlicher Offline-Aufruf endete mit Prozessstatus 1:

~~~powershell
uv --cache-dir ausgabe/uv-zwischenspeicher run --offline --python 3.12 --with fastapi --with uvicorn python -X utf8 -c "import fastapi, uvicorn; print('FastAPI', fastapi.__version__); print('Uvicorn', uvicorn.__version__)"
~~~

Beobachtet: `fastapi was not found in the cache`. Eine Uvicorn-Ausführung wurde dabei ebenfalls nicht erreicht; seine Verfügbarkeit wurde damals nicht unabhängig geprüft. Damals gab es keinen API-Startbefehl und keine API-Abnahme. Keine Ersatzsimulation und keine Online-Installation in diesem Versuch durchgeführt. Befehle und Fehlermeldungen: [Voraussetzungsprüfung](nachweise/P02-T03-voraussetzungen.json). Der folgende Abschnitt dokumentiert die spätere Bereitstellung.

## Fortsetzung am 9. November: API-Voraussetzung bereit

Die oben dokumentierte Blockade vom 4. November ist für die Bibliotheken behoben. FastAPI 0.162.2, Uvicorn 0.54.0 und httpx 0.28.1 wurden aus PyPI ausschließlich in den projektlokalen UV-Cache geladen. Offline-Import und ein echter TestClient-Aufruf von /openapi.json mit HTTP 200 waren erfolgreich. Starlette warnt dabei vor der künftigen Ablösung des httpx-TestClients. Noch keine fachliche DataHub-API-Abnahme.

Für P02-T03 diese tatsächlich nutzbare Umgebung verwenden:

~~~powershell
uv --cache-dir ausgabe/uv-zwischenspeicher run --offline --python 3.12 --default-index https://pypi.org/simple --with fastapi==0.162.2 --with uvicorn==0.54.0 --with httpx==0.28.1 python -X utf8 -c "import fastapi, uvicorn, httpx; print(fastapi.__version__)"
~~~

[Nachweis der Bereitstellung](nachweise/P02-T03-voraussetzungen-bereit-2026-11-09.json). Nur T03 wiederaufnehmen; keine Folgephase entwickeln.

## P02-T03: API lokal starten und abfragen

Zuerst wie oben mit `src/pipeline.py --datenbank ausgabe/protokolle.sqlite` importieren. Anschließend im Projektordner:

~~~powershell
uv --cache-dir ausgabe/uv-zwischenspeicher run --offline --python 3.12 --default-index https://pypi.org/simple --with fastapi==0.162.2 --with uvicorn==0.54.0 --with httpx==0.28.1 python -X utf8 -m uvicorn src.api:anwendung --host 127.0.0.1 --port 8000
~~~

In einer zweiten PowerShell abfragen:

~~~powershell
Invoke-RestMethod 'http://127.0.0.1:8000/ereignisse?umgebung=entwicklung'
Invoke-RestMethod 'http://127.0.0.1:8000/ereignisse?umgebung=test'
Invoke-RestMethod 'http://127.0.0.1:8000/status'
~~~

Mit Strg+C beenden. Standarddatenbank ist `ausgabe/protokolle.sqlite`, bezogen auf den Projektordner. Optional vor dem Start `$env:MINIDATAHUB_DATENBANK = 'ausgabe/andere-protokolle.sqlite'` setzen; relative alternative Pfade beziehen sich auf das Arbeitsverzeichnis. Mit `Remove-Item Env:MINIDATAHUB_DATENBANK -ErrorAction SilentlyContinue` die Auswahl zurücksetzen. Die Abnahme wählt ihre eigene temporäre Datenbank und verändert keinen bestehenden Importbestand.

`src/api.py` öffnet SQLite mit `mode=ro`, verwendet SQL-Parameter und sortiert Ereignisse nach Zeitpunkt und Kennung. `/ereignisse` benötigt `umgebung`: 1–32 Kleinbuchstaben, Ziffern oder Bindestriche, Beginn mit einem Buchstaben. Bekannte Werte sind ausschließlich `entwicklung` und `test`, passend zum vorhandenen Importvertrag. Eine bekannte leere Umgebung liefert 200 mit leerer Liste; ein syntaktisch gültiger unbekannter Wert wie `produktion` liefert 404. Fehlende, leere oder falsch formatierte Werte liefern 422 mit deutscher Meldung. Fehlende oder defekte Datenbank beziehungsweise Schemafehler liefern 503; eine fehlende Datei wird nicht angelegt. `/openapi.json` enthält den FastAPI-Vertrag.

Die Antwort enthält `umgebung`, `ereignisanzahl`, `fehleranzahl` und `ereignisse`. Gezählt wird ausschließlich Stufe `ERROR`, nicht WARN und nicht die Regex-Markierung `ist_zeitueberschreitung`. Originalbestand: `entwicklung` 2 Ereignisse/0 Fehler, `test` 1 Ereignis/1 Fehler. `/status` liefert `zustand: bereit`, insgesamt 3 Ereignisse/1 Fehler und die Zahlen je gespeicherter Umgebung. Eine lesbare leere Ereignistabelle liefert Nullwerte und eine leere Umgebungsliste. Das ist eine minimale JSON-Statusübersicht.

## API-Abnahme wiederholen

~~~powershell
uv --cache-dir ausgabe/uv-zwischenspeicher run --offline --python 3.12 --default-index https://pypi.org/simple --with fastapi==0.162.2 --with uvicorn==0.54.0 --with httpx==0.28.1 python -X utf8 nachweise/p02-t03-pruefen.py
git diff --check -- .
~~~

Tatsächlich am 9. November ausgeführt: **13/13 Prüfungen erfüllt**, Python 3.12.14, FastAPI 0.162.2, Uvicorn 0.54.0 und SQLite 3.53.1. Das Skript importiert die fünf Originalzeilen in eine temporäre Datenbank unter `ausgabe/`, startet einen echten Uvicorn-Prozess auf einem freien lokalen Port und sendet HTTP-Anfragen. Geprüft werden Filter, Zahlen, Fehlerstatus, leere bekannte Umgebung, Datenbankausfall, unveränderte Datenbank bei lesenden Anfragen sowie SHA-256 und Anzahl der Originalzeilen. Nur die temporäre Datenbank wird für Leer-/Ausfallszenarien verändert. Der Server wird anschließend ausdrücklich beendet (unter Windows Prozessstatus 1 durch `terminate`, kein fehlgeschlagener Start). Das Skript selbst endet bei erfüllter Abnahme mit 0. Es entfernt seinen temporären Ordner.

Der wiederholte Lauf ersetzt [P02-T03-pruefung.json](nachweise/P02-T03-pruefung.json); enthalten sind Befehle, Versionen, Serverprotokoll, alle HTTP-Antworten, Prüfergebnisse und reale Prüfdauer. Für die Wiederholung erforderlich: [Prüfskript](nachweise/p02-t03-pruefen.py), [API](src/api.py), [Import](src/pipeline.py), [SQL-Schema](sql/schema.sql), [Originaldaten](beispieldaten/logs.jsonl), diese Anleitung und [Projektkonfiguration](projekt.json). Zeit und Dateiprüfsummen des Abschlusses stehen in [Arbeitseinheit der Wiederaufnahme](nachweise/P02-T03-wiederaufnahme.json).

Grenze: lokaler lesender Zugriff auf das vorhandene SQLite-Schema, keine Migration, Produktivbereitstellung oder zusätzliche Produktvariante. FastAPI/Uvicorn sind tatsächlich ausgeführt; PostgreSQL, Pandas und Elastic bleiben ohne Ausführungsnachweis. P02-T04 und übergreifende Lastenheftkästchen bleiben offen. Die früheren Abschnitte beschreiben jeweils den Stand der damaligen Phase.

## P02-T04: Wiederholten Import und Fehlerauswertung gemeinsam prüfen

Im Projektordner mit dem vorhandenen Offline-Cache ausführen:

~~~powershell
uv --cache-dir ausgabe/uv-zwischenspeicher run --offline --python 3.12 --default-index https://pypi.org/simple --with fastapi==0.162.2 --with uvicorn==0.54.0 --with httpx==0.28.1 python -X utf8 nachweise/p02-t04-pruefen.py
~~~

Tatsächlich am 11. November 2026 ausgeführt: **16/16 Prüfungen erfüllt**, Prozessstatus 0, reine Prüfdauer 0,423969 Sekunden. Versionen: Python 3.12.14, SQLite 3.53.1, FastAPI 0.162.2, Starlette 1.10.0, httpx 0.28.1. Starlette meldet eine Ablösungswarnung für den httpx-TestClient; die vorhandene Umgebung führt die Prüfung erfolgreich aus. Kein Download oder Werkzeugwechsel erforderlich.

Das Skript erzeugt unter `ausgabe/` eine neue temporäre Datenbank und startet zweimal die echte Import-CLI als getrennte Prozesse mit den fünf Originalzeilen. Beobachtet: zuerst 3 neu/1 übersprungen, danach 0 neu/4 übersprungen. Alle gespeicherten Felder bleiben inhaltlich identisch; es existieren genau `e1`, `e2`, `e3`. Beide Läufe melden genau die ungültige JSON-Zeile 5 mit Originalinhalt, die Wiederholung `e2` in Zeile 4 gegenüber Zeile 2 und keine Konflikte. Die Originaldatei bleibt bei fünf Zeilen und SHA-256 `bc447d2b0032611979bf68c3f85abd5cf0ea349e388bf3561a83c8b52f236623`.

Nach jedem Import ruft TestClient die echte FastAPI-Anwendung im Prozess auf: `entwicklung` 2 Ereignisse/0 Fehler, `test` 1/1 und `/status` insgesamt 3/1, jeweils Status 200. T04 prüft keinen Netzwerkserver; die frühere echte Uvicorn-/HTTP-Prüfung steht separat unter T03. Der eine JSON-Eingabefehler ist eine andere Fehlerart als der eine gespeicherte `ERROR`. `WARN` mit Regex-Treffer ist kein `ERROR`, und die wiederholte `e2` zählt nur einmal. Die Fehlerliste wird in der Importausgabe festgehalten, nicht in einer Fehlerarchivtabelle.

Der Prüflauf entfernt seinen temporären Bestand und ersetzt [P02-T04-pruefung.json](nachweise/P02-T04-pruefung.json) bei Wiederholung. Erforderlich sind [Prüfskript mit sämtlichen Testfällen](nachweise/p02-t04-pruefen.py), [Import](src/pipeline.py), [API](src/api.py), [SQL-Schema](sql/schema.sql), [Originaldaten](beispieldaten/logs.jsonl), diese Anleitung und [Projektkonfiguration](projekt.json). Keine zusätzlichen Testdaten oder laufenden Datenbankdienste erforderlich.

PostgreSQL bleibt separat offen: kein eingerichteter PostgreSQL-Import oder tatsächlicher Abfragenachweis im Projekt, Variante P02-V01 unverändert. Elastic bleibt separat offen: keine echte Elasticsearch-Abfrage und keine Kibana-Ausführung nachgewiesen, Variante P02-V02 und Lastenheft A4 unverändert. Verfügbarkeit außerhalb dieses Projekts wurde nicht untersucht; SQLite/TestClient ersetzen keine Produktverwendung. Keine Folgetickets oder übergreifende Gesamtfreigabe.

Der lokale Abschluss mit realer Zeitmessung, Konfigurationskontrolle und Dateiprüfsummen wird durch folgenden rein lokalen Befehl dokumentiert:

~~~powershell
uv --cache-dir ausgabe/uv-zwischenspeicher run --offline --python 3.12 python -X utf8 nachweise/p02-t04-abschluss.py
~~~

[P02-T04-arbeitseinheit.json](nachweise/P02-T04-arbeitseinheit.json) nennt Beginn, Ende und Dauer der ursprünglichen Einheit. Das Abschlussskript überschreibt diese Zeitangaben bei Wiederholung nicht, sondern schreibt dann `P02-T04-abschluss-wiederholung.json`. Der übergeordnete Dienst sichert den unveränderlichen Stand und erstellt erst später den echten Commit. Keine Git-Schreibbefehle durch den Projektarbeiter.
