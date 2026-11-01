"""Die begrenzte Abnahme mit unveränderter Eingabe ausführen und belegen."""
import hashlib
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

projektordner = Path(__file__).resolve().parents[1]
eingabe = projektordner / "beispieldaten" / "logs.jsonl"
beginn = datetime.now(timezone.utc)
start = time.perf_counter()
pruefsumme_vorher = hashlib.sha256(eingabe.read_bytes()).hexdigest()
lauf = subprocess.run(
    [sys.executable, "-X", "utf8", "src/pipeline.py"],
    cwd=projektordner, capture_output=True, text=True, encoding="utf-8", check=False,
)
ergebnis = json.loads(lauf.stdout) if lauf.returncode == 0 else {}
pruefsumme_nachher = hashlib.sha256(eingabe.read_bytes()).hexdigest()
pruefungen = {
    "prozessstatus_0": lauf.returncode == 0,
    "fuenf_zeilen": ergebnis.get("zeilen") == 5,
    "vier_gueltige_zeilen": ergebnis.get("gueltige_zeilen") == 4,
    "drei_eindeutige_kennungen": ergebnis.get("eindeutige_kennungen") == 3,
    "wiederholung_mit_beiden_fundstellen": ergebnis.get("wiederholungen") == [
        {"zeile": 4, "ereignis_id": "e2", "erste_zeile": 2}
    ],
    "kaputte_zeile_mit_inhalt": ergebnis.get("fehler") == [
        {"zeile": 5, "meldung": "Ungültiges JSON (Spalte 1).",
         "inhalt": "Absichtlich ungültige JSON-Zeile"}
    ],
    "eingabe_unveraendert": pruefsumme_vorher == pruefsumme_nachher
        == "bc447d2b0032611979bf68c3f85abd5cf0ea349e388bf3561a83c8b52f236623",
}
nachweis = {
    "projekt": "P02", "ticket": "P02-T01",
    "beginn_utc": beginn.isoformat(),
    "ende_utc": datetime.now(timezone.utc).isoformat(),
    "pruefdauer_sekunden": round(time.perf_counter() - start, 6),
    "python_version": sys.version.split()[0],
    "aufruf": "uv --cache-dir ausgabe/uv-zwischenspeicher run --offline --python 3.12 python -X utf8 nachweise/p02-t01-pruefen.py",
    "gepruefter_befehl": "python -X utf8 src/pipeline.py",
    "prozessstatus": lauf.returncode,
    "standardausgabe": lauf.stdout,
    "fehlerausgabe": lauf.stderr,
    "eingabe_sha256_vorher": pruefsumme_vorher,
    "eingabe_sha256_nachher": pruefsumme_nachher,
    "pruefungen": pruefungen,
    "erfolgreich": all(pruefungen.values()),
    "grenze": "Nur Format und Kennungen innerhalb eines Aufrufs; keine Import-Idempotenz.",
}
ziel = projektordner / "nachweise" / "P02-T01-pruefung.json"
ziel.write_text(json.dumps(nachweis, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(lauf.stdout, end="")
print(f"Abnahme: {sum(pruefungen.values())}/{len(pruefungen)} Prüfungen erfüllt.")
print("Nachweis: nachweise/P02-T01-pruefung.json")
sys.exit(0 if nachweis["erfolgreich"] else 1)
