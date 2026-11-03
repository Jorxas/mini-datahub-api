"""JSONL-Protokolle prüfen und optional idempotent nach SQLite importieren."""
import argparse
import json
import re
import sqlite3
from datetime import datetime
from pathlib import Path

PROJEKTORDNER = Path(__file__).resolve().parents[1]
PFLICHTFELDER = {"ereignis_id", "zeitpunkt", "umgebung", "stufe", "nachricht"}
ZEITUEBERSCHREITUNG = re.compile(r"\bZeitüberschreitung\b", re.IGNORECASE)


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


def protokoll_pruefen(pfad, verarbeiten=None):
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
            if verarbeiten is not None:
                verarbeiten(ereignis, zeilennummer)
            kennung = ereignis["ereignis_id"]
            if kennung in erste_zeilen:
                ergebnis["wiederholungen"].append({"zeile": zeilennummer,
                                                  "ereignis_id": kennung,
                                                  "erste_zeile": erste_zeilen[kennung]})
            else:
                erste_zeilen[kennung] = zeilennummer
    ergebnis["eindeutige_kennungen"] = len(erste_zeilen)
    return ergebnis


def protokoll_importieren(pfad, datenbank):
    """Die erste gültige Kennung behalten; alle Einfügungen gemeinsam abschließen."""
    eingefuegt = 0
    uebersprungen = 0
    konflikte = []
    verbindung = sqlite3.connect(datenbank)
    try:
        verbindung.executescript(
            (PROJEKTORDNER / "sql" / "schema.sql").read_text(encoding="utf-8")
        )

        def speichern(ereignis, zeile):
            nonlocal eingefuegt, uebersprungen
            werte = tuple(ereignis[feld] for feld in
                          ("ereignis_id", "zeitpunkt", "umgebung", "stufe", "nachricht"))
            markierung = int(ZEITUEBERSCHREITUNG.search(ereignis["nachricht"]) is not None)
            abfrage = verbindung.execute(
                "INSERT INTO ereignisse "
                "(ereignis_id, zeitpunkt, umgebung, stufe, nachricht, ist_zeitueberschreitung) "
                "VALUES (?, ?, ?, ?, ?, ?) ON CONFLICT(ereignis_id) DO NOTHING",
                (*werte, markierung),
            )
            if abfrage.rowcount == 1:
                eingefuegt += 1
            else:
                uebersprungen += 1
                vorhanden = verbindung.execute(
                    "SELECT ereignis_id, zeitpunkt, umgebung, stufe, nachricht "
                    "FROM ereignisse WHERE ereignis_id = ?", (ereignis["ereignis_id"],)
                ).fetchone()
                if vorhanden != werte:
                    konflikte.append({"zeile": zeile, "ereignis_id": ereignis["ereignis_id"],
                                      "meldung": "Abweichender Inhalt; gespeichertes Ereignis bleibt erhalten."})

        # Lesefehler rollen alle Ereignisse dieses Aufrufs zurück.
        with verbindung:
            ergebnis = protokoll_pruefen(pfad, speichern)
        ergebnis.update({"eingefuegt": eingefuegt, "uebersprungen": uebersprungen,
                         "konflikte": konflikte,
                         "gespeicherte_ereignisse": verbindung.execute(
                             "SELECT COUNT(*) FROM ereignisse").fetchone()[0]})
        return ergebnis
    finally:
        verbindung.close()


if __name__ == "__main__":
    argumente = argparse.ArgumentParser(description="JSONL-Protokolle prüfen oder nach SQLite importieren.")
    argumente.add_argument("pfad", nargs="?", type=Path,
                           default=PROJEKTORDNER / "beispieldaten" / "logs.jsonl")
    argumente.add_argument("--datenbank", type=Path,
                           help="SQLite-Zieldatei; ohne diese Option nur prüfen. Der Zielordner muss bestehen.")
    eingaben = argumente.parse_args()
    pfad = eingaben.pfad
    try:
        ergebnis = (protokoll_importieren(pfad, eingaben.datenbank)
                    if eingaben.datenbank is not None else protokoll_pruefen(pfad))
    except (OSError, UnicodeError):
        argumente.exit(1, "Protokoll- oder Schemadatei kann nicht als UTF-8 gelesen werden.\n")
    except sqlite3.Error:
        argumente.exit(1, "SQLite-Import fehlgeschlagen; Datenbankpfad, Schema und Schreibzugriff prüfen.\n")
    print(json.dumps(ergebnis, ensure_ascii=False, indent=2))
