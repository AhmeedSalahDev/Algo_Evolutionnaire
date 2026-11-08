"""Cédule de maintenance de 7 centrales électriques par algorithme génétique.

On reprend exactement la modélisation du support de cours :

- l'année est coupée en 4 intervalles (demande 80, 90, 65, 70 MW) ;
- un chromosome = 7 gènes de 4 bits, un gène par unité, « 1 » = l'unité
  est en maintenance pendant cet intervalle ;
- performance = la plus petite réserve sur l'année (0 si elle est négative) ;
- croisement et mutation travaillent sur des blocs de 4 bits, jamais au
  milieu d'un gène, sinon on fabrique des cédules qui n'ont pas de sens.

Lancer depuis la racine du dépôt :  python -m td3_cedule.cedule
"""
import itertools
import random

from td3_cedule.selection import SELECTIONS, elitisme

CAPACITES = [20, 15, 35, 40, 15, 15, 10]   # MW, unités 1 à 7
DUREES = [2, 2, 1, 1, 1, 1, 1]             # nombre d'intervalles de maintenance
DEMANDES = [80, 90, 65, 70]                # MW, intervalles 1 à 4
NB_INTERVALLES = len(DEMANDES)
CAPACITE_TOTALE = sum(CAPACITES)           # 150 MW


def genes_possibles(duree, n=NB_INTERVALLES):
    """Blocs de `duree` « 1 » consécutifs : 2 -> 1100 0110 0011."""
    return ["0" * d + "1" * duree + "0" * (n - duree - d) for d in range(n - duree + 1)]


GENES_VALIDES = [genes_possibles(d) for d in DUREES]


# ----------------------------------------------------------- évaluation
def puissance_en_maintenance(chromosome):
    return [sum(c for c, gene in zip(CAPACITES, chromosome) if gene[t] == "1")
            for t in range(NB_INTERVALLES)]


def reserves(chromosome):
    perdue = puissance_en_maintenance(chromosome)
    return [CAPACITE_TOTALE - p - d for p, d in zip(perdue, DEMANDES)]


def performance(chromosome):
    """La plus petite réserve de l'année ; 0 si une réserve est négative."""
    return max(0, min(reserves(chromosome)))


def est_valide(chromosome):
    return all(g in GENES_VALIDES[u] for u, g in enumerate(chromosome))


def decrire(chromosome):
    lignes = []
    for u, gene in enumerate(chromosome):
        inter = [t + 1 for t in range(NB_INTERVALLES) if gene[t] == "1"]
        lignes.append(f"  unité {u + 1} ({CAPACITES[u]:2d} MW) : maintenance en {inter}")
    return "\n".join(lignes)


# ----------------------------------------------------------- opérateurs
def individu_aleatoire(rng):
    return [rng.choice(g) for g in GENES_VALIDES]


def croisement(p1, p2, rng):
    """Croisement en un point, la coupure tombe toujours entre deux gènes."""
    point = rng.randint(1, len(p1) - 1)
    return p1[:point] + p2[point:], p2[:point] + p1[point:]


def mutation(chromosome, pm, rng):
    """Chaque gène a une probabilité pm d'être remplacé par une AUTRE
    période de maintenance valide pour la même unité (ex. du cours :
    0001 -> 0100). L'enfant reste donc toujours une cédule correcte."""
    enfant = list(chromosome)
    for u in range(len(enfant)):
        if rng.random() < pm:
            autres = [g for g in GENES_VALIDES[u] if g != enfant[u]]
            enfant[u] = rng.choice(autres)
    return enfant


# ----------------------------------------------------------- AG
def algorithme_genetique(taille=42, generations=60, pc=0.8, pm=0.1,
                         selection="roulette", nb_elites=1, seed=None):
    """AG générationnel classique.

    Renvoie (meilleur, historique) où historique contient, pour chaque
    génération, la meilleure performance et la performance moyenne.
    taille = 42 suit la règle du cours : 6 à 7 fois le nombre de variables (7).
    """
    rng = random.Random(seed)
    choisir = SELECTIONS[selection]
    population = [individu_aleatoire(rng) for _ in range(taille)]
    historique = {"meilleur": [], "moyenne": []}

    def noter(adapt):
        historique["meilleur"].append(max(adapt))
        historique["moyenne"].append(sum(adapt) / taille)

    for _ in range(generations):
        adapt = [performance(c) for c in population]
        noter(adapt)
        nouvelle = [list(c) for c in elitisme(population, adapt, nb_elites)]
        while len(nouvelle) < taille:
            p1 = choisir(population, adapt, rng)
            p2 = choisir(population, adapt, rng)
            if rng.random() < pc:
                e1, e2 = croisement(p1, p2, rng)
            else:
                e1, e2 = list(p1), list(p2)
            nouvelle.append(mutation(e1, pm, rng))
            if len(nouvelle) < taille:
                nouvelle.append(mutation(e2, pm, rng))
        population = nouvelle

    noter([performance(c) for c in population])   # génération finale
    meilleur = max(population, key=performance)
    return meilleur, historique


# ----------------------------------------------------------- contrôle
def toutes_les_cedules():
    return (list(c) for c in itertools.product(*GENES_VALIDES))


def enumeration_exhaustive():
    """Le problème est petit (3 x 3 x 4^5 = 9216 cédules) : on peut tout
    tester et savoir avec certitude quel est l'optimum."""
    perf = [performance(c) for c in toutes_les_cedules()]
    best = max(perf)
    return len(perf), best, perf.count(best), perf


EXEMPLE_COURS = ["0110", "0011", "0001", "1000", "0100", "0010", "1000"]


def main():
    print("Exemple du support :", " ".join(EXEMPLE_COURS))
    print("  puissance en maintenance :", puissance_en_maintenance(EXEMPLE_COURS))
    print("  réserves                 :", reserves(EXEMPLE_COURS))
    print("  performance              :", performance(EXEMPLE_COURS), "MW\n")

    meilleur, hist = algorithme_genetique(seed=2026)
    print("AG (roulette, N=42, 60 générations, pc=0.8, pm=0.1, élitisme 1)")
    print("Meilleure cédule :", " ".join(meilleur))
    print(decrire(meilleur))
    print("Réserves :", reserves(meilleur), "-> performance =", performance(meilleur), "MW")
    atteint = next(g for g, v in enumerate(hist["meilleur"]) if v == max(hist["meilleur"]))
    print(f"Meilleure valeur atteinte dès la génération {atteint}\n")

    n, best, nb, _ = enumeration_exhaustive()
    print(f"Vérification exhaustive : {n} cédules, optimum = {best} MW, atteint par {nb} cédules")


if __name__ == "__main__":
    main()
