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
