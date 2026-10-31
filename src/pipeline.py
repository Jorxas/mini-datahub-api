"""Mini DataHub et analyse de journaux : base de travail, aucun résultat métier calculé."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]

def import_events(data):
    # À implémenter dans les tickets ; conserver les erreurs et les limites.
    raise NotImplementedError("P02 : logique métier à réaliser")

if __name__ == "__main__":
    print("P02 initialisé : consulter les fixtures et le premier ticket.")
