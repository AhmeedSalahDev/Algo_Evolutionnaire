# TD2 – Optimisation : recherche taboue & recuit simulé (Python)

Faculté des Sciences de Sfax — Algorithmes évolutionnaires / métaheuristiques.

## Contenu

| Fichier | Description |
|---|---|
| `exercice2_transport_tabou.py` | Exercice 2 : problème de transport résolu par recherche taboue |
| `exercice3_tsp.py` | Exercice 3 : voyageur de commerce résolu par recherche taboue et recuit simulé |
| `generer_rapport.py` | Génère les figures et le compte rendu PDF (`Compte_rendu_TD2.pdf`) |
| `td2/` | Package Python exposant les deux modules d'algorithmes |

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

Les scripts historiques restent utilisables directement :

```bash
python exercice2_transport_tabou.py
python exercice3_tsp.py
```

Pour générer le rapport, installer ses dépendances et lancer le script depuis la racine :

```bash
pip install matplotlib reportlab
python generer_rapport.py
```
