# TD2 – Optimisation : recherche taboue & recuit simulé (Python)

Faculté des Sciences de Sfax — Algorithmes évolutionnaires / métaheuristiques.

## Contenu

| Fichier | Description |
|---|---|
| `td2/exercice2_transport_tabou.py` | Exercice 2 : problème de transport résolu par recherche taboue |
| `td2/exercice3_tsp.py` | Exercice 3 : voyageur de commerce résolu par recherche taboue et recuit simulé |
| `td2/generer_rapport.py` | Génère les figures et le compte rendu PDF (`td2/Compte_rendu_TD2.pdf`) |
| `td2/fig_*.png` | Figures utilisées dans le compte rendu |
| `td2/sortie_exercice*.txt` | Sorties console des exercices 2 et 3 |

## Installer le package

Depuis la racine du dépôt :

```bash
python -m pip install .
```

Exemple d'utilisation :

```python
from td2.exercice2_transport_tabou import recherche_taboue, COUTS, STOCKS, DEMANDES
from td2.exercice3_tsp import recherche_taboue as recherche_taboue_tsp

solution, cout, historique = recherche_taboue(COUTS, STOCKS, DEMANDES, verbose=False)
tour, longueur, historique_tsp = recherche_taboue_tsp(
    [1, 2, 3, 4, 5, 6, 7, 8], verbose=False
)
```

Lancer les exercices depuis la racine du dépôt :

```bash
python -m td2.exercice2_transport_tabou
python -m td2.exercice3_tsp
```

Pour générer le rapport, installer ses dépendances puis lancer :

```bash
pip install matplotlib reportlab
python -m td2.generer_rapport
```

Les figures et le PDF sont écrits dans le dossier `td2/`.
