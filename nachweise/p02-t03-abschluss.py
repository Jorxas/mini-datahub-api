"""Abschlusskontrolle und gemessene Wiederaufnahme von P02-T03 sichern."""
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

projektordner = Path(__file__).resolve().parents[1]
dateien = [
    "README.md", "START.md", "ARBEITSJOURNAL.md", "projekt.json", "tickets/P02-T03.md",
    "src/api.py", "src/pipeline.py", "sql/schema.sql", "beispieldaten/logs.jsonl",
    "nachweise/p02-t03-pruefen.py", "nachweise/p02-t03-abschluss.py",
    "nachweise/P02-T03-pruefung.json", "nachweise/P02-T03-pruefung-erster-lauf.json",
    "nachweise/P02-T03-voraussetzungen.json", "nachweise/P02-T03-arbeitseinheit.json",
    "nachweise/P02-T03-voraussetzungen-bereit-2026-11-09.json",
]
pruefsummen = {pfad: hashlib.sha256((projektordner / pfad).read_bytes()).hexdigest()
               for pfad in dateien}
alter_stand = json.loads((projektordner / "nachweise/P02-T03-arbeitseinheit.json").read_text(encoding="utf-8-sig"))
pruefung = json.loads((projektordner / "nachweise/P02-T03-pruefung.json").read_text(encoding="utf-8"))
konfiguration = json.loads((projektordner / "projekt.json").read_text(encoding="utf-8"))
befehle = []
for befehl in (["git", "diff", "--check", "--", "."],
               ["git", "diff", "--exit-code", "--", "LASTENHEFT.md", "tickets/P02-T04.md"]):
    lauf = subprocess.run(befehl, cwd=projektordner, capture_output=True,
                          text=True, encoding="utf-8", check=False)
    befehle.append({"befehl": befehl, "prozessstatus": lauf.returncode,
                    "standardausgabe": lauf.stdout, "fehlerausgabe": lauf.stderr})
kontrollen = {
    "abnahme_13_von_13": pruefung["erfolgreich"] and len(pruefung["pruefungen"]) == 13,
    "importstand_erhalten": all(pruefsummen[pfad] == alter_stand["dateien_sha256"][pfad]
                                for pfad in ("src/pipeline.py", "sql/schema.sql", "beispieldaten/logs.jsonl")),
    "fuenf_originalzeilen": len((projektordner / "beispieldaten/logs.jsonl").read_text(encoding="utf-8").splitlines()) == 5,
    "konfiguration_ticket_begrenzt": konfiguration["abfrage_api"]["zustand"] == "erledigt"
                                     and konfiguration["expectedRecords"] == 5
                                     and konfiguration["businessImplemented"] is False,
    "keine_whitespacefehler": befehle[0]["prozessstatus"] == 0 and all(
        zeile == zeile.rstrip() for pfad in ("src/api.py", "nachweise/p02-t03-pruefen.py",
                                           "nachweise/p02-t03-abschluss.py")
        for zeile in (projektordner / pfad).read_text(encoding="utf-8").splitlines()),
    "lastenheft_und_folgeticket_unveraendert": befehle[1]["prozessstatus"] == 0,
}
beginn = datetime.fromisoformat("2026-11-09T20:55:16+00:00")
ende = datetime.now(timezone.utc)
nachweis = {
    "projekt": "P02", "ticket": "P02-T03", "zustand": "erledigt" if all(kontrollen.values()) else "blockiert",
    "studentische_schaetzung_minuten": 75,
    "beginn_utc": beginn.isoformat(), "abschlussdokumentation_gesichert_utc": ende.isoformat(),
    "beobachtete_assistentenzeit_sekunden": round((ende - beginn).total_seconds(), 3),
    "zeitbeschreibung": "Beobachtetes Zeitfenster dieser Wiederaufnahme ab erster Zeitmessung nach Einlesen bis Abschlusskontrolle; keine menschliche Arbeitszeit. Bei Wiederholung wird nur der aktuelle Sicherungszeitpunkt erneuert, nicht die historische Arbeitsdauer rekonstruiert.",
    "versuche": [
        {"versuch": "4. November", "ergebnis": "blockiert, keine API", "nachweis": "nachweise/P02-T03-arbeitseinheit.json"},
        {"versuch": "gemeldeter unterbrochener Lauf", "ergebnis": "Bei Wiederaufnahme keine API-Datei oder fachliche API-Abnahme vorhanden; Dauer nicht belegt. Vorhandene Import- und Voraussetzungsänderungen erhalten."},
        {"versuch": "diese Wiederaufnahme", "ergebnis": "FastAPI implementiert; beide tatsächlichen HTTP-Prüfläufe 13/13 erfolgreich."}],
    "kontrollen": kontrollen, "befehle": befehle, "dateien_sha256": pruefsummen,
    "wiederholung_dateien": pruefung["wiederholung_dateien"] + ["nachweise/p02-t03-abschluss.py"],
    "veroeffentlichung": "Jetzt lokal fertiggestellt; keine Git-Schreibbefehle. Unveränderliche Sicherung und späterer Commit durch übergeordneten Dienst.",
}
ziel = projektordner / "nachweise/P02-T03-wiederaufnahme.json"
if ziel.exists():
    # Die zuerst gesicherte Arbeitsdauer bleibt bei erneuter Kontrolle erhalten.
    bisher = json.loads(ziel.read_text(encoding="utf-8"))
    for feld in ("abschlussdokumentation_gesichert_utc", "beobachtete_assistentenzeit_sekunden"):
        nachweis[feld] = bisher[feld]
    nachweis["erneut_kontrolliert_utc"] = ende.isoformat()
ziel.write_text(json.dumps(nachweis, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Abschluss: {sum(kontrollen.values())}/{len(kontrollen)} Kontrollen erfüllt.")
print(f"Beobachtete Assistentenzeit: {nachweis['beobachtete_assistentenzeit_sekunden']} Sekunden.")
print("Nachweis: nachweise/P02-T03-wiederaufnahme.json")
sys.exit(0 if all(kontrollen.values()) else 1)
