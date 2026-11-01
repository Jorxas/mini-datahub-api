"""JSONL-Protokolle im Arbeitsspeicher prüfen, ohne einen Import zu speichern."""
import argparse
import json
import re
from datetime import datetime
from pathlib import Path

PROJEKTORDNER = Path(__file__).resolve().parents[1]
PFLICHTFELDER = {"ereignis_id", "zeitpunkt", "umgebung", "stufe", "nachricht"}


def ereignis_pruefen(ereignis):
    """Den begrenzten Vertrag aus vertraege/DATENWOERTERBUCH.md prüfen."""
    if not isinstance(ereignis, dict):
        return "Ein Ereignis muss ein JSON-Objekt sein."
    if set(ereignis) != PFLICHTFELDER:
        return "Das Ereignis muss genau die fünf vereinbarten Felder enthalten."
    if any(not isinstance(ereignis[feld], str) for feld in PFLICHTFELDER):
        return "Alle fünf Felder müssen Zeichenketten sein."
    if not ereignis["ereignis_id"]:
        return "Die Ereigniskennung darf nicht leer sein."
    if ereignis["umgebung"] not in {"entwicklung", "test"}:
        return "Die Umgebung muss entwicklung oder test sein."
    if ereignis["stufe"] not in {"INFO", "WARN", "ERROR"}:
        return "Die Stufe muss INFO, WARN oder ERROR sein."
    zeitpunkt = ereignis["zeitpunkt"]
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z", zeitpunkt):
        return "Der Zeitpunkt muss UTC im Format JJJJ-MM-TTThh:mm:ssZ verwenden."
    try:
        datetime.strptime(zeitpunkt, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        return "Der Zeitpunkt enthält kein gültiges Datum oder keine gültige Uhrzeit."
    return None


def protokoll_pruefen(pfad):
    """Jede physische Zeile prüfen; Kennungen nur für diesen Aufruf merken."""
    erste_zeilen = {}
    ergebnis = {"zeilen": 0, "gueltige_zeilen": 0, "eindeutige_kennungen": 0,
                "fehler": [], "wiederholungen": []}
    with pfad.open(encoding="utf-8") as datei:
        for zeilennummer, zeile in enumerate(datei, start=1):
            ergebnis["zeilen"] += 1
            try:
                ereignis = json.loads(zeile)
            except json.JSONDecodeError as fehler:
                meldung = f"Ungültiges JSON (Spalte {fehler.colno})."
            else:
                meldung = ereignis_pruefen(ereignis)
            if meldung:
                ergebnis["fehler"].append({"zeile": zeilennummer,
                                          "meldung": meldung,
                                          "inhalt": zeile.rstrip("\r\n")})
                continue
            ergebnis["gueltige_zeilen"] += 1
            kennung = ereignis["ereignis_id"]
            if kennung in erste_zeilen:
                ergebnis["wiederholungen"].append({"zeile": zeilennummer,
                                                  "ereignis_id": kennung,
                                                  "erste_zeile": erste_zeilen[kennung]})
            else:
                erste_zeilen[kennung] = zeilennummer
    ergebnis["eindeutige_kennungen"] = len(erste_zeilen)
    return ergebnis

if __name__ == "__main__":
    argumente = argparse.ArgumentParser(description="JSONL-Protokolle ohne Speicherung prüfen.")
    argumente.add_argument("pfad", nargs="?", type=Path,
                           default=PROJEKTORDNER / "beispieldaten" / "logs.jsonl")
    pfad = argumente.parse_args().pfad
    try:
        ergebnis = protokoll_pruefen(pfad)
    except (OSError, UnicodeError):
        argumente.exit(1, f"Protokolldatei kann nicht als UTF-8 gelesen werden: {pfad}\n")
    print(json.dumps(ergebnis, ensure_ascii=False, indent=2))
