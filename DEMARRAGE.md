# Démarrage — P02

## Inspecter immédiatement la base

Depuis le dossier de ce projet, avec Node.js :

~~~powershell
node ../scripts/inspecter.cjs P02
~~~

Cette commande vérifie la présence de la fixture et du point d'entrée. Elle ne valide pas le métier.

## Point d'entrée technique

Prérequis : Python 3 ; FastAPI/Pandas à installer dans un environnement dédié.

~~~powershell
python src/pipeline.py
~~~

Le programme de départ indique son état initialisé. Les fonctions métier lèvent volontairement une erreur tant que les tickets ne sont pas faits. Les frameworks et bibliothèques non installés doivent être ajoutés dans leur ticket, avec leur version réelle et un fichier de dépendances verrouillé quand applicable.

## Prochain travail

Décrire event_id, timestamp, environment, level et message ; traiter une ligne cassée. Puis suivre les tickets dans l'ordre.

## Documents techniques

- [Python csv](https://docs.python.org/3/library/csv.html) pour les lecteurs.
- [Angular CLI](https://angular.dev/tools/cli/setup-local) pour la variante frontend.
- [.NET WPF](https://learn.microsoft.com/en-us/dotnet/desktop/wpf/get-started/create-app-visual-studio) pour l'écran Windows.

Lire la documentation du framework réellement choisi avant d'ajouter son bootstrap.
