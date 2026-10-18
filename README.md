# TD2 – Optimisation : Recherche taboue & Recuit simulé (Python)

Faculté des Sciences de Sfax — Algorithmes évolutionnaires / métaheuristiques.

## Contenu

| Fichier | Description |
|---|---|
| `exercice2_transport_tabou.py` | Exercice 2 : problème de transport (2 dépôts, 3 magasins) résolu par **recherche taboue** (voisinage en cycle « stepping stone », solution initiale coin Nord-Ouest) + vérification exhaustive |
| `exercice3_tsp.py` | Exercice 3 : voyageur de commerce à 8 villes — **recherche taboue** (solution initiale 1-2-3-4-5-6-7-8-1) et **recuit simulé** (5 itérations, T0 réglée empiriquement) + vérification exhaustive |
| `generer_rapport.py` | Génère les figures et le compte rendu PDF (`Compte_rendu_TD2.pdf`) |
| `sortie_exercice2.txt`, `sortie_exercice3.txt` | Traces d'exécution |

## Exécution

```bash
python exercice2_transport_tabou.py
python exercice3_tsp.py
pip install matplotlib reportlab   # seulement pour le rapport
python generer_rapport.py
```

## Résultats

- **Exercice 2** : D1 → M1 = 3, D1 → M2 = 5, D2 → M1 = 1, D2 → M3 = 8 ; **coût minimal = 52** (identique au Branch and Bound).
- **Exercice 3** :
  - Recherche taboue : 103 → **98** (tour 1-8-3-7-6-5-4-2-1, i.e. 1-2-4-5-6-7-3-8-1) en 11 itérations.
  - Recuit simulé (5 itérations, T0 ≈ 10,78, α = 0,8) : meilleur = 103 ; version longue : **98**.
  - Optimum exact (énumération des 5040 tours) : **98**.
