# Cahier des charges — P02

## Utilisateur et problème

Une équipe veut importer des logs applicatifs, détecter les erreurs et suivre l'état de ses environnements.

## Périmètre étudiant

Import JSONL vers SQL, vue des erreurs, API de consultation et variante Elastic ciblée.

Un utilisateur local, des données synthétiques et un parcours démontrable. Volume réduit pour terminer une première version dans la semaine.

## Recette du socle

- [ ] C1 — Un import répété n'ajoute aucun doublon ; les lignes mal formées vont dans les rejets.
- [ ] C2 — La requête par environnement renvoie les bons événements et un compteur d'erreurs.
- [ ] C3 — L'API sépare données valides, entrée invalide et environnement inconnu.
- [ ] C4 — L'extension Elastic conserve une capture de la même requête ; sans exécution, Elastic reste prévu.

## Prérequis

- Python 3
- FastAPI/Pandas à installer dans un environnement dédié

## Démonstration de cinq minutes

Importer deux fois les mêmes logs puis expliquer pourquoi le nombre d'événements ne double pas.

Montrer une entrée valide, une erreur, le résultat et le fichier qui porte la logique. Expliquer une décision technique et une limite.

## Livraison

- Commande de démarrage exacte, versions utilisées et données d'exemple.
- Recette exécutée, résultats réels et une capture ou un journal sans données personnelles.
- Ticket et journal mis à jour ; commit local correspondant au travail réellement effectué.
- Lecture et explication du code par l'étudiant avant réutilisation dans une candidature.

## Limites

Le socle ne comprend ni déploiement public ni exploitation en production. Les logiciels ou frameworks d'une variante nécessitent une exécution distincte. Une certification, une pratique professionnelle, un niveau de langue et une expérience d'équipe ne se déduisent pas de cet exercice.

## Réutilisation future dans un CV

Mini pipeline ETL de logs synthétiques ; citer les moteurs et bibliothèques réellement utilisés.

Formulation actuelle autorisée : « Projet personnel en préparation : Mini DataHub et analyse de journaux ». Une formulation « réalisé » attend la recette et l'explication du code.
