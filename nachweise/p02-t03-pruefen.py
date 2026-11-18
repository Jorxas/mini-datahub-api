"""T03 über einen echten lokalen Uvicorn-Prozess und HTTP prüfen."""
import hashlib
import json
import os
import re
import sqlite3
import subprocess
import sys
import tempfile
import time
from contextlib import closing
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import ProxyHandler, build_opener

projektordner = Path(__file__).resolve().parents[1]
eingabe = projektordner / "beispieldaten" / "logs.jsonl"
beginn = datetime.now(timezone.utc)
start = time.perf_counter()
pruefsumme_vorher = hashlib.sha256(eingabe.read_bytes()).hexdigest()
pruefungen = {}
anfragen = []
laeufe = []
aufruf = ("uv --cache-dir ausgabe/uv-zwischenspeicher run --offline --python 3.12 "
          "--default-index https://pypi.org/simple --with fastapi==0.162.2 "
          "--with uvicorn==0.54.0 --with httpx==0.28.1 python -X utf8 nachweise/p02-t03-pruefen.py")


def abfragen(pfad):
    # Lokale Anfragen gehen direkt an den Prüfserver, auch bei gesetztem Systemproxy.
    try:
        antwort = build_opener(ProxyHandler({})).open(basisadresse + pfad, timeout=3)
    except HTTPError as fehler:
        antwort = fehler
    with antwort:
        inhalt = json.loads(antwort.read().decode("utf-8"))
        anfragen.append({"pfad": pfad, "http_status": antwort.status, "antwort": inhalt})
        return antwort.status, inhalt


def umgebung_abfragen(umgebung):
    return abfragen("/ereignisse?" + urlencode({"umgebung": umgebung}))


(projektordner / "ausgabe").mkdir(exist_ok=True)
fehlertext = None
with tempfile.TemporaryDirectory(prefix="p02-t03-", dir=projektordner / "ausgabe") as ordner:
    ordner = Path(ordner)
    datenbank = ordner / "protokolle.sqlite"
    befehl = [sys.executable, "-X", "utf8", "src/pipeline.py", "--datenbank", str(datenbank)]
    importlauf = subprocess.run(befehl, cwd=projektordner, capture_output=True,
                                text=True, encoding="utf-8", check=False, timeout=15)
    laeufe.append({"befehl": befehl, "prozessstatus": importlauf.returncode,
                   "standardausgabe": importlauf.stdout, "fehlerausgabe": importlauf.stderr})
    importiert = json.loads(importlauf.stdout) if importlauf.returncode == 0 else {}
    pruefungen["originalimport_drei_ereignisse"] = (
        importlauf.returncode == 0 and importiert.get("eingefuegt") == 3
        and importiert.get("zeilen") == 5 and len(importiert.get("fehler", [])) == 1)
    datenbank_hash = hashlib.sha256(datenbank.read_bytes()).hexdigest()
    umgebungsvariablen = {**os.environ, "MINIDATAHUB_DATENBANK": str(datenbank)}
    befehl = [sys.executable, "-X", "utf8", "-m", "uvicorn", "src.api:anwendung",
              "--host", "127.0.0.1", "--port", "0", "--no-use-colors"]
    protokoll = ordner / "server.log"
    with protokoll.open("w", encoding="utf-8") as ausgabe:
        prozess = subprocess.Popen(befehl, cwd=projektordner, env=umgebungsvariablen,
                                   stdout=ausgabe, stderr=ausgabe)
        try:
            frist = time.monotonic() + 15
            while True:
                meldungen = protokoll.read_text(encoding="utf-8")
                adresse = re.search(r"Uvicorn running on (http://127\.0\.0\.1:\d+)", meldungen)
                if adresse:
                    basisadresse = adresse.group(1)
                    break
                if prozess.poll() is not None or time.monotonic() > frist:
                    raise RuntimeError("Lokaler Uvicorn-Start fehlgeschlagen: " + meldungen)
                time.sleep(0.05)

            status, inhalt = umgebung_abfragen("entwicklung")
            pruefungen["entwicklung_zwei_ereignisse_keine_fehler"] = (
                status == 200 and inhalt["ereignisanzahl"] == 2 and inhalt["fehleranzahl"] == 0
                and [ereignis["ereignis_id"] for ereignis in inhalt["ereignisse"]] == ["e1", "e3"]
                and all(ereignis["umgebung"] == "entwicklung" for ereignis in inhalt["ereignisse"]))
            status, inhalt = umgebung_abfragen("test")
            pruefungen["test_ein_error_ohne_duplikat"] = (
                status == 200 and inhalt["ereignisanzahl"] == inhalt["fehleranzahl"] == 1
                and [ereignis["ereignis_id"] for ereignis in inhalt["ereignisse"]] == ["e2"]
                and inhalt["ereignisse"][0]["umgebung"] == "test")
            status, inhalt = abfragen("/status")
            pruefungen["status_drei_ereignisse_ein_fehler"] = status == 200 and inhalt == {
                "zustand": "bereit", "ereignisanzahl": 3, "fehleranzahl": 1, "umgebungen": [
                    {"umgebung": "entwicklung", "ereignisanzahl": 2, "fehleranzahl": 0},
                    {"umgebung": "test", "ereignisanzahl": 1, "fehleranzahl": 1}]}
            pruefungen["unbekannte_umgebung_404"] = umgebung_abfragen("produktion") == (
                404, {"detail": "Unbekannte Umgebung."})
            ungueltige = [abfragen("/ereignisse"), *(umgebung_abfragen(wert) for wert in
                ("", "Test", "a" * 33, "test' OR 1=1 --"))]
            pruefungen["fehlende_und_ungueltige_eingaben_422_deutsch"] = all(
                status == 422 and inhalt["detail"].startswith("Umgebung erforderlich:")
                for status, inhalt in ungueltige)
            status, inhalt = abfragen("/openapi.json")
            pruefungen["fastapi_vertrag_ausgeliefert"] = (
                status == 200 and set(inhalt["paths"]) == {"/ereignisse", "/status"})
            pruefungen["abfragen_veraendern_datenbank_nicht"] = (
                hashlib.sha256(datenbank.read_bytes()).hexdigest() == datenbank_hash)

            # Nur den temporären Prüfbestand ändern, um leere bekannte Umgebungen zu prüfen.
            with closing(sqlite3.connect(datenbank)) as verbindung:
                with verbindung:
                    verbindung.execute("DELETE FROM ereignisse")
            status, inhalt = umgebung_abfragen("test")
            pruefungen["bekannte_leere_umgebung_200"] = status == 200 and inhalt == {
                "umgebung": "test", "ereignisanzahl": 0, "fehleranzahl": 0, "ereignisse": []}
            pruefungen["leerer_status_200"] = abfragen("/status") == (200, {
                "zustand": "bereit", "ereignisanzahl": 0, "fehleranzahl": 0, "umgebungen": []})
            datenbank.unlink()
            pruefungen["fehlende_datenbank_503_ohne_neuanlage"] = (
                abfragen("/status")[0] == 503 and umgebung_abfragen("test")[0] == 503
                and not datenbank.exists())
            datenbank.write_text("Absichtlich ungültige SQLite-Datei", encoding="utf-8")
            pruefungen["defekte_datenbank_503"] = abfragen("/status")[0] == 503
        except Exception as fehler:
            fehlertext = f"{type(fehler).__name__}: {fehler}"
            pruefungen["prueflauf_ohne_abbruch"] = False
        finally:
            prozess.terminate()
            try:
                prozess.wait(timeout=5)
            except subprocess.TimeoutExpired:
                prozess.kill()
                prozess.wait(timeout=5)
    laeufe.append({"befehl": befehl, "datenbank": str(datenbank),
                   "beendigung": "Prüfserver nach HTTP-Prüfung durch Prüfskript beendet.",
                   "prozessstatus": prozess.returncode,
                   "protokoll": protokoll.read_text(encoding="utf-8")})

pruefsumme_nachher = hashlib.sha256(eingabe.read_bytes()).hexdigest()
pruefungen["fuenf_originalzeilen_unveraendert"] = (
    pruefsumme_vorher == pruefsumme_nachher
    == "bc447d2b0032611979bf68c3f85abd5cf0ea349e388bf3561a83c8b52f236623"
    and len(eingabe.read_text(encoding="utf-8").splitlines()) == 5)
nachweis = {
    "projekt": "P02", "ticket": "P02-T03", "beginn_utc": beginn.isoformat(),
    "ende_utc": datetime.now(timezone.utc).isoformat(),
    "pruefdauer_sekunden": round(time.perf_counter() - start, 6), "aufruf": aufruf,
    "versionen": {"python": sys.version.split()[0], "sqlite": sqlite3.sqlite_version,
                  **{name: version(name) for name in ("fastapi", "uvicorn", "httpx")}},
    "laeufe": laeufe, "anfragen": anfragen, "pruefungen": pruefungen,
    "erfolgreich": all(pruefungen.values()), "abbruch": fehlertext,
    "eingabe_sha256_vorher": pruefsumme_vorher, "eingabe_sha256_nachher": pruefsumme_nachher,
    "wiederholung_dateien": ["nachweise/p02-t03-pruefen.py", "src/api.py", "src/pipeline.py",
                            "sql/schema.sql", "beispieldaten/logs.jsonl", "START.md", "projekt.json"],
    "grenze": "Nur lokale lesende FastAPI-Abfrage; kein Folgeticket und keine weitere Produktvariante.",
}
(projektordner / "nachweise" / "P02-T03-pruefung.json").write_text(
    json.dumps(nachweis, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Abnahme: {sum(pruefungen.values())}/{len(pruefungen)} Prüfungen erfüllt.")
if fehlertext:
    print(fehlertext)
print("Nachweis: nachweise/P02-T03-pruefung.json")
sys.exit(0 if nachweis["erfolgreich"] else 1)
