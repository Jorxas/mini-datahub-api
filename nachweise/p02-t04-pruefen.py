"""Zwei echte SQLite-Importe und die zugehörigen FastAPI-Zahlen prüfen."""
import hashlib
import json
import sqlite3
import subprocess
import sys
import tempfile
import time
from contextlib import closing
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path

sys.dont_write_bytecode = True
projektordner = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(projektordner))

from fastapi.testclient import TestClient
from src.api import anwendung_erstellen

beginn = datetime.now(timezone.utc)
start = time.perf_counter()
eingabe = projektordner / "beispieldaten" / "logs.jsonl"
pruefsumme_vorher = hashlib.sha256(eingabe.read_bytes()).hexdigest()
pruefungen = {}
laeufe = []
bestaende = []
abbruch = None
aufruf = (
    "uv --cache-dir ausgabe/uv-zwischenspeicher run --offline --python 3.12 "
    "--default-index https://pypi.org/simple --with fastapi==0.162.2 "
    "--with uvicorn==0.54.0 --with httpx==0.28.1 python -X utf8 nachweise/p02-t04-pruefen.py"
)
wiederholung_dateien = [
    "nachweise/p02-t04-pruefen.py", "src/pipeline.py", "src/api.py",
    "sql/schema.sql", "beispieldaten/logs.jsonl", "START.md", "projekt.json",
]
erwartete_ereignisse = [
    ("e1", "2026-10-01T09:00:00Z", "entwicklung", "INFO", "Dienst gestartet", 0),
    ("e2", "2026-10-01T09:01:00Z", "test", "ERROR", "Verbindung abgelehnt", 0),
    ("e3", "2026-10-01T09:02:00Z", "entwicklung", "WARN", "Zeitüberschreitung nach 1000 ms", 1),
]
erwartete_fehlerliste = [{
    "zeile": 5, "meldung": "Ungültiges JSON (Spalte 1).",
    "inhalt": "Absichtlich ungültige JSON-Zeile",
}]
erwarteter_status = {
    "zustand": "bereit", "ereignisanzahl": 3, "fehleranzahl": 1,
    "umgebungen": [
        {"umgebung": "entwicklung", "ereignisanzahl": 2, "fehleranzahl": 0},
        {"umgebung": "test", "ereignisanzahl": 1, "fehleranzahl": 1},
    ],
}

(projektordner / "ausgabe").mkdir(exist_ok=True)
try:
    with tempfile.TemporaryDirectory(prefix="p02-t04-", dir=projektordner / "ausgabe") as ordner:
        datenbank = Path(ordner) / "protokolle.sqlite"
        for nummer in (1, 2):
            befehl = [sys.executable, "-X", "utf8", "src/pipeline.py", "--datenbank", str(datenbank)]
            prozess = subprocess.run(befehl, cwd=projektordner, capture_output=True,
                                     text=True, encoding="utf-8", timeout=15, check=False)
            lauf = {"nummer": nummer, "befehl": befehl, "prozessstatus": prozess.returncode,
                    "standardausgabe": prozess.stdout, "fehlerausgabe": prozess.stderr, "anfragen": []}
            laeufe.append(lauf)
            if prozess.returncode != 0:
                raise RuntimeError(f"Importlauf {nummer} fehlgeschlagen.")
            ergebnis = json.loads(prozess.stdout)
            pruefungen[f"lauf_{nummer}_importzahlen"] = (
                ergebnis["zeilen"] == 5 and ergebnis["gueltige_zeilen"] == 4
                and ergebnis["eindeutige_kennungen"] == 3
                and ergebnis["eingefuegt"] == (3 if nummer == 1 else 0)
                and ergebnis["uebersprungen"] == (1 if nummer == 1 else 4)
                and ergebnis["gespeicherte_ereignisse"] == 3)
            pruefungen[f"lauf_{nummer}_fehlerliste_mit_originalinhalt"] = (
                ergebnis["fehler"] == erwartete_fehlerliste)
            pruefungen[f"lauf_{nummer}_wiederholung_ohne_konflikt"] = (
                ergebnis["wiederholungen"] == [{"zeile": 4, "ereignis_id": "e2", "erste_zeile": 2}]
                and ergebnis["konflikte"] == [])
            with closing(sqlite3.connect(datenbank)) as verbindung:
                bestand = verbindung.execute(
                    "SELECT ereignis_id, zeitpunkt, umgebung, stufe, nachricht, "
                    "ist_zeitueberschreitung FROM ereignisse ORDER BY ereignis_id").fetchall()
            bestaende.append(bestand)
            lauf["datenbankinhalt"] = bestand
            pruefungen[f"lauf_{nummer}_genau_drei_erwartete_ereignisse"] = (
                bestand == erwartete_ereignisse)
            # TestClient führt die echte FastAPI-Anwendung im Prozess aus, ohne Netzwerkserver.
            with TestClient(anwendung_erstellen(datenbank)) as klient:
                for umgebung, kennungen, fehleranzahl in (
                        ("entwicklung", ["e1", "e3"], 0), ("test", ["e2"], 1)):
                    pfad = f"/ereignisse?umgebung={umgebung}"
                    antwort = klient.get(pfad)
                    inhalt = antwort.json()
                    lauf["anfragen"].append({"pfad": pfad, "http_status": antwort.status_code,
                                              "antwort": inhalt})
                    pruefungen[f"lauf_{nummer}_api_{umgebung}_fehleranzahl"] = (
                        antwort.status_code == 200 and inhalt["umgebung"] == umgebung
                        and inhalt["ereignisanzahl"] == len(kennungen)
                        and inhalt["fehleranzahl"] == fehleranzahl
                        and [ereignis["ereignis_id"] for ereignis in inhalt["ereignisse"]] == kennungen
                        and all(ereignis["umgebung"] == umgebung for ereignis in inhalt["ereignisse"]))
                antwort = klient.get("/status")
                lauf["anfragen"].append({"pfad": "/status", "http_status": antwort.status_code,
                                          "antwort": antwort.json()})
                pruefungen[f"lauf_{nummer}_api_gesamtzahlen"] = (
                    antwort.status_code == 200 and antwort.json() == erwarteter_status)
        pruefungen["bestand_nach_wiederholung_inhaltlich_identisch"] = bestaende[0] == bestaende[1]
except Exception as fehler:
    abbruch = f"{type(fehler).__name__}: {fehler}"
    pruefungen["prueflauf_ohne_abbruch"] = False

pruefsumme_nachher = hashlib.sha256(eingabe.read_bytes()).hexdigest()
pruefungen["fuenf_originalzeilen_unveraendert"] = (
    pruefsumme_vorher == pruefsumme_nachher
    == "bc447d2b0032611979bf68c3f85abd5cf0ea349e388bf3561a83c8b52f236623"
    and len(eingabe.read_text(encoding="utf-8").splitlines()) == 5)
nachweis = {
    "projekt": "P02", "ticket": "P02-T04", "beginn_utc": beginn.isoformat(),
    "ende_utc": datetime.now(timezone.utc).isoformat(),
    "pruefdauer_sekunden": round(time.perf_counter() - start, 6), "aufruf": aufruf,
    "versionen": {"python": sys.version.split()[0], "sqlite": sqlite3.sqlite_version,
                  **{name: version(name) for name in ("fastapi", "starlette", "httpx")}},
    "laeufe": laeufe, "pruefungen": pruefungen, "erfolgreich": all(pruefungen.values()),
    "abbruch": abbruch, "eingabe_sha256_vorher": pruefsumme_vorher,
    "eingabe_sha256_nachher": pruefsumme_nachher,
    "wiederholung_dateien": wiederholung_dateien,
    "produktabgrenzung": {
        "sqlite": "Zwei echte Importprozesse und direkte Bestandsprüfung.",
        "fastapi": "Echte Anwendung über TestClient im Prozess; kein Uvicorn- oder Netzwerktest in T04.",
        "postgresql": "Nicht ausgeführt; kein eingerichteter PostgreSQL-Import oder Abfragenachweis im Projekt. P02-V01 bleibt offen.",
        "elastic": "Nicht ausgeführt; keine echte Elasticsearch-Abfrage oder Kibana-Ausführung nachgewiesen. P02-V02 und Lastenheft A4 bleiben offen.",
    },
    "grenze": "Nur lokaler T04-Endpunkt; keine Kompetenzbehauptung für PostgreSQL oder Elastic. Fehlerliste ist Importausgabe, Fehleranzahl zählt gespeicherte ERROR-Ereignisse; WARN mit Regex-Treffer zählt nicht.",
}
(projektordner / "nachweise" / "P02-T04-pruefung.json").write_text(
    json.dumps(nachweis, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Abnahme: {sum(pruefungen.values())}/{len(pruefungen)} Prüfungen erfüllt.")
if abbruch:
    print(abbruch)
print("Nachweis: nachweise/P02-T04-pruefung.json")
sys.exit(0 if nachweis["erfolgreich"] else 1)
