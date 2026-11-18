"""Den begrenzten SQLite-Import in getrennten Prozessen tatsächlich prüfen."""
import hashlib
import json
import sqlite3
import subprocess
import sys
import tempfile
import time
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

projektordner = Path(__file__).resolve().parents[1]
eingabe = projektordner / "beispieldaten" / "logs.jsonl"
beginn = datetime.now(timezone.utc)
start = time.perf_counter()
pruefsumme_vorher = hashlib.sha256(eingabe.read_bytes()).hexdigest()
laeufe = []
pruefungen = {}


def ausfuehren(*argumente):
    befehl = [sys.executable, "-X", "utf8", "src/pipeline.py", *map(str, argumente)]
    lauf = subprocess.run(befehl, cwd=projektordner, capture_output=True,
                          text=True, encoding="utf-8", check=False)
    laeufe.append({"befehl": befehl, "prozessstatus": lauf.returncode,
                   "standardausgabe": lauf.stdout, "fehlerausgabe": lauf.stderr})
    return lauf, json.loads(lauf.stdout) if lauf.returncode == 0 else {}


def datenbank_lesen(pfad):
    with closing(sqlite3.connect(pfad)) as verbindung:
        return verbindung.execute(
            "SELECT ereignis_id, zeitpunkt, umgebung, stufe, nachricht, "
            "ist_zeitueberschreitung FROM ereignisse ORDER BY ereignis_id"
        ).fetchall()


(projektordner / "ausgabe").mkdir(exist_ok=True)
with tempfile.TemporaryDirectory(prefix="p02-t02-", dir=projektordner / "ausgabe") as ordner:
    ordner = Path(ordner)
    datenbank = ordner / "import.sqlite"
    erster_lauf, erstes = ausfuehren("--datenbank", datenbank)
    erster_bestand = datenbank_lesen(datenbank)
    zweiter_lauf, zweites = ausfuehren("--datenbank", datenbank)
    zweiter_bestand = datenbank_lesen(datenbank)
    erwartete_ereignisse = [json.loads(zeile) for zeile in eingabe.read_text(
        encoding="utf-8").splitlines()[:3]]
    erwarteter_bestand = [tuple(ereignis[feld] for feld in
        ("ereignis_id", "zeitpunkt", "umgebung", "stufe", "nachricht")) + (int(nummer == 2),)
        for nummer, ereignis in enumerate(erwartete_ereignisse)]
    pruefungen["zwei_importprozesse_erfolgreich"] = erster_lauf.returncode == zweiter_lauf.returncode == 0
    pruefungen["erster_import_drei_neue_eine_wiederholung"] = (
        erstes.get("eingefuegt"), erstes.get("uebersprungen"), erstes.get("gespeicherte_ereignisse")
    ) == (3, 1, 3)
    pruefungen["zweiter_import_keine_neuen_vier_wiederholungen"] = (
        zweites.get("eingefuegt"), zweites.get("uebersprungen"), zweites.get("gespeicherte_ereignisse")
    ) == (0, 4, 3)
    pruefungen["bestand_und_regex_markierung_exakt"] = erster_bestand == zweiter_bestand == erwarteter_bestand
    pruefungen["originalfehler_und_fundstellen_in_beiden_laeufen"] = all(
        ergebnis.get("zeilen") == 5 and ergebnis.get("gueltige_zeilen") == 4
        and ergebnis.get("fehler") == [{"zeile": 5, "meldung": "Ungültiges JSON (Spalte 1).",
                                        "inhalt": "Absichtlich ungültige JSON-Zeile"}]
        and ergebnis.get("wiederholungen") == [{"zeile": 4, "ereignis_id": "e2", "erste_zeile": 2}]
        for ergebnis in (erstes, zweites)
    )

    # Zusätzliche synthetische Prüfeingaben bleiben von den Originaldaten getrennt.
    grundereignis = erwartete_ereignisse[0]
    randfaelle = [
        [], {**grundereignis, "zusatz": "unzulässig"},
        {**grundereignis, "ereignis_id": ""}, {**grundereignis, "nachricht": None},
        {**grundereignis, "umgebung": "unbekannt"}, {**grundereignis, "stufe": "FALSCH"},
        {**grundereignis, "zeitpunkt": "2026-02-30T09:00:00Z"},
        {**grundereignis, "zeitpunkt": "2026-10-01"},
        {**grundereignis, "nachricht": "Abweichender Inhalt"},
        {**grundereignis, "ereignis_id": "pruefung-ja", "nachricht": "Eine ZEITÜBERSCHREITUNG!"},
        {**grundereignis, "ereignis_id": "pruefung-nein", "nachricht": "Keinezeitüberschreitung"},
    ]
    pruefeingabe = ordner / "randfaelle.jsonl"
    pruefeingabe.write_text("\n".join(json.dumps(ereignis, ensure_ascii=False)
                                    for ereignis in randfaelle) + "\n\n", encoding="utf-8")
    randlauf, randergebnis = ausfuehren(pruefeingabe, "--datenbank", datenbank)
    randbestand = datenbank_lesen(datenbank)
    pruefungen["feld_und_datumsfehler_sowie_leerzeile_abgewiesen"] = (
        randlauf.returncode == 0 and [fehler["zeile"] for fehler in randergebnis.get("fehler", [])]
        == [1, 2, 3, 4, 5, 6, 7, 8, 12] and randergebnis.get("eingefuegt") == 2
    )
    pruefungen["inhaltskonflikt_gemeldet_und_erster_inhalt_erhalten"] = (
        randergebnis.get("konflikte") == [{"zeile": 9, "ereignis_id": "e1",
            "meldung": "Abweichender Inhalt; gespeichertes Ereignis bleibt erhalten."}]
        and randbestand[:3] == erwarteter_bestand
    )
    pruefungen["regex_ignoriert_schreibung_beachtet_wortgrenze"] = (
        {zeile[0]: zeile[5] for zeile in randbestand if zeile[0].startswith("pruefung-")}
        == {"pruefung-ja": 1, "pruefung-nein": 0}
    )

    unlesbar = ordner / "ungueltiges-utf8.jsonl"
    unlesbar.write_bytes((json.dumps({**grundereignis, "ereignis_id": "ruecknahme"})
                         + "\n" + " " * 10000 + "\n").encode("utf-8") + b"\xff\n")
    fehllauf, _ = ausfuehren(unlesbar, "--datenbank", datenbank)
    pruefungen["lesefehler_status_1_und_transaktion_zurueckgenommen"] = (
        fehllauf.returncode == 1 and "UTF-8" in fehllauf.stderr
        and datenbank_lesen(datenbank) == randbestand
    )
    pfadfehler, _ = ausfuehren("--datenbank", ordner / "fehlt" / "import.sqlite")
    pruefungen["datenbankfehler_status_1_mit_deutscher_meldung"] = (
        pfadfehler.returncode == 1 and pfadfehler.stderr.startswith("SQLite-Import fehlgeschlagen;")
    )
    prueflauf, pruefergebnis = ausfuehren()
    pruefungen["bisheriger_pruefmodus_erhalten"] = (
        prueflauf.returncode == 0 and pruefergebnis.get("zeilen") == 5
        and pruefergebnis.get("eindeutige_kennungen") == 3 and "eingefuegt" not in pruefergebnis
    )

pruefsumme_nachher = hashlib.sha256(eingabe.read_bytes()).hexdigest()
pruefungen["fuenf_originalzeilen_unveraendert"] = (
    pruefsumme_vorher == pruefsumme_nachher
    == "bc447d2b0032611979bf68c3f85abd5cf0ea349e388bf3561a83c8b52f236623"
    and len(eingabe.read_text(encoding="utf-8").splitlines()) == 5
)
nachweis = {
    "projekt": "P02", "ticket": "P02-T02", "beginn_utc": beginn.isoformat(),
    "ende_utc": datetime.now(timezone.utc).isoformat(),
    "pruefdauer_sekunden": round(time.perf_counter() - start, 6),
    "python_version": sys.version.split()[0], "sqlite_version": sqlite3.sqlite_version,
    "aufruf": "uv --cache-dir ausgabe/uv-zwischenspeicher run --offline --python 3.12 python -X utf8 nachweise/p02-t02-pruefen.py",
    "laeufe": laeufe, "bestand_nach_erstem_import": erster_bestand,
    "bestand_nach_zweitem_import": zweiter_bestand, "bestand_nach_randfaellen": randbestand,
    "eingabe_sha256_vorher": pruefsumme_vorher, "eingabe_sha256_nachher": pruefsumme_nachher,
    "pruefungen": pruefungen, "erfolgreich": all(pruefungen.values()),
    "grenze": "Lokaler SQLite-Import; keine Umgebungsabfrage, API oder weitere Produktvariante.",
}
ziel = projektordner / "nachweise" / "P02-T02-pruefung.json"
ziel.write_text(json.dumps(nachweis, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Abnahme: {sum(pruefungen.values())}/{len(pruefungen)} Prüfungen erfüllt.")
print(f"Erster Import: {erstes.get('eingefuegt')} neu; zweiter Import: {zweites.get('eingefuegt')} neu; Bestand jeweils 3.")
print(f"Python {nachweis['python_version']}; SQLite {nachweis['sqlite_version']}.")
print("Nachweis: nachweise/P02-T02-pruefung.json")
sys.exit(0 if nachweis["erfolgreich"] else 1)
