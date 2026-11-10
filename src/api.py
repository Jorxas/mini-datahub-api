"""Synthetische SQLite-Protokolle mit FastAPI ausschließlich lesend abfragen."""
import os
import sqlite3
from contextlib import closing
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel

PROJEKTORDNER = Path(__file__).resolve().parents[1]
UMGEBUNGEN = ("entwicklung", "test")


class Fehlermeldung(BaseModel):
    """Einheitlicher Fehlerinhalt für den API-Vertrag."""
    detail: str


def anwendung_erstellen(datenbank):
    """Den Importbestand lesen; fehlende Datenbanken niemals neu anlegen."""
    datenbank = Path(datenbank).resolve()
    anwendung = FastAPI(title="Mini-DataHub", description="Lokale Protokollabfrage",
                        version="0.1.0", docs_url=None, redoc_url=None)

    def zeilen_lesen(abfrage, parameter=()):
        try:
            with closing(sqlite3.connect(datenbank.as_uri() + "?mode=ro", uri=True)) as verbindung:
                verbindung.row_factory = sqlite3.Row
                return [dict(zeile) for zeile in verbindung.execute(abfrage, parameter)]
        except sqlite3.Error:
            raise HTTPException(status_code=503, detail="Protokolldatenbank nicht lesbar; Import und Schema prüfen.") from None

    @anwendung.exception_handler(RequestValidationError)
    async def eingabefehler(_anfrage: Request, _fehler: RequestValidationError):
        return JSONResponse(status_code=422, content={
            "detail": "Umgebung erforderlich: 1 bis 32 Kleinbuchstaben, Ziffern oder Bindestriche; Beginn mit einem Buchstaben."
        })

    @anwendung.get("/ereignisse", summary="Ereignisse einer Umgebung lesen",
                   response_description="Abfrage erfolgreich", responses={
                       404: {"model": Fehlermeldung, "description": "Unbekannte Umgebung"},
                       422: {"model": Fehlermeldung, "description": "Ungültige Eingabe"},
                       503: {"model": Fehlermeldung, "description": "Datenbank nicht lesbar"}})
    def ereignisse_lesen(umgebung: str = Query(
            ..., min_length=1, max_length=32, pattern=r"^[a-z][a-z0-9-]*$",
            description="Bekannte Umgebungen: entwicklung, test")):
        if umgebung not in UMGEBUNGEN:
            raise HTTPException(status_code=404, detail="Unbekannte Umgebung.")
        ereignisse = zeilen_lesen(
            "SELECT ereignis_id, zeitpunkt, umgebung, stufe, nachricht, ist_zeitueberschreitung "
            "FROM ereignisse WHERE umgebung = ? ORDER BY zeitpunkt, ereignis_id", (umgebung,))
        return {"umgebung": umgebung, "ereignisanzahl": len(ereignisse),
                "fehleranzahl": sum(ereignis["stufe"] == "ERROR" for ereignis in ereignisse),
                "ereignisse": ereignisse}

    @anwendung.get("/status", summary="Minimalen Datenbankstatus lesen",
                   response_description="Status erfolgreich gelesen", responses={
                       503: {"model": Fehlermeldung, "description": "Datenbank nicht lesbar"}})
    def status_lesen():
        zeilen = zeilen_lesen(
            "SELECT umgebung, COUNT(*) AS ereignisanzahl, "
            "SUM(CASE WHEN stufe = 'ERROR' THEN 1 ELSE 0 END) AS fehleranzahl "
            "FROM ereignisse GROUP BY umgebung ORDER BY umgebung")
        return {"zustand": "bereit", "ereignisanzahl": sum(zeile["ereignisanzahl"] for zeile in zeilen),
                "fehleranzahl": sum(zeile["fehleranzahl"] for zeile in zeilen), "umgebungen": zeilen}

    return anwendung


anwendung = anwendung_erstellen(os.environ.get(
    "MINIDATAHUB_DATENBANK", PROJEKTORDNER / "ausgabe" / "protokolle.sqlite"))
