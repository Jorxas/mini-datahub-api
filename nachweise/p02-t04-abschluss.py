"""Lokalen Abschluss mit echten Zeitpunkten und Dateiprüfsummen sichern."""
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

projektordner = Path(__file__).resolve().parents[1]
pruefung = json.loads((projektordner / "nachweise/P02-T04-pruefung.json").read_text(encoding="utf-8"))
konfiguration = json.loads((projektordner / "projekt.json").read_text(encoding="utf-8"))
befehl = ["git", "diff", "--check", "--", "."]
prozess = subprocess.run(befehl, cwd=projektordner, capture_output=True,
                         text=True, encoding="utf-8", check=False, timeout=15)
kontrollen = {
    "fachliche_abnahme_erfolgreich": pruefung["erfolgreich"] and len(pruefung["pruefungen"]) == 16,
    "ticket_lokal_erledigt": konfiguration["lokale_abnahme"]["ticket"] == "P02-T04"
    and konfiguration["lokale_abnahme"]["zustand"] == "erledigt",
    "keine_uebergreifende_freigabe": konfiguration["businessImplemented"] is False
    and (projektordner / "LASTENHEFT.md").read_text(encoding="utf-8").count("- [ ] A") == 4,
    "git_diff_check": prozess.returncode == 0,
}
dateien = list(dict.fromkeys(pruefung["wiederholung_dateien"] + [
    "nachweise/p02-t04-abschluss.py", "nachweise/P02-T04-pruefung.json",
    "README.md", "ARBEITSJOURNAL.md", "tickets/P02-T04.md", "LASTENHEFT.md",
]))
pruefsummen = {datei: hashlib.sha256((projektordner / datei).read_bytes()).hexdigest()
               for datei in dateien}
ende = datetime.now(timezone.utc)
beginn = datetime.fromisoformat("2026-11-11T03:00:43+00:00")
urspruenglicher_nachweis = projektordner / "nachweise/P02-T04-arbeitseinheit.json"
wiederholung = urspruenglicher_nachweis.exists()
nachweis = {
    "projekt": "P02", "ticket": "P02-T04", "zeitpunkt_utc": ende.isoformat(),
    "abschlusskontrollen": kontrollen, "erfolgreich": all(kontrollen.values()),
    "befehl": befehl, "prozessstatus": prozess.returncode,
    "standardausgabe": prozess.stdout, "fehlerausgabe": prozess.stderr,
    "dateien_sha256": pruefsummen,
    "studentische_schaetzung_minuten": 60,
    "hinweis": "Technische Assistentenzeit, keine menschliche Eigenleistung; kurze Einlesezeit vor erster Messung nicht erfasst. Kein Commit oder Veröffentlichung durch den Projektarbeiter.",
}
if not wiederholung:
    nachweis.update({"beginn_utc": beginn.isoformat(), "fertigstellung_utc": ende.isoformat(),
                     "tatsaechliche_assistentenzeit_sekunden": round((ende - beginn).total_seconds(), 6)})
ziel = (projektordner / "nachweise/P02-T04-abschluss-wiederholung.json"
        if wiederholung else urspruenglicher_nachweis)
ziel.write_text(json.dumps(nachweis, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Abschluss: {sum(kontrollen.values())}/{len(kontrollen)} Kontrollen erfüllt.")
print(f"Nachweis: {ziel.relative_to(projektordner).as_posix()}")
sys.exit(0 if nachweis["erfolgreich"] else 1)
