"""Opérateurs de sélection vus en TD3 (exercices 1, 2 et 3).

Toutes les fonctions suivent la même convention, pour pouvoir être
branchées telles quelles dans l'AG de la cédule :

    selection_xxx(population, adaptations, rng) -> un individu

- ``population``  : liste d'individus (n'importe quel type)
- ``adaptations`` : liste de valeurs >= 0, « plus grand = meilleur »
- ``rng``         : un ``random.Random`` (pour des résultats reproductibles)

Remarque : on travaille toujours sur l'*adaptation* (fitness à maximiser).
Pour un problème de minimisation, il faut d'abord transformer f en
adaptation (voir exercice 2).
"""
import bisect
import random


# ---------------------------------------------------------------- roulette
def probabilites_roulette(adaptations):
    """p_i = F_i / somme(F). Si tout vaut 0, on revient au tirage uniforme."""
    total = sum(adaptations)
    n = len(adaptations)
    if total == 0:
        return [1 / n] * n
    return [a / total for a in adaptations]


def selection_roulette(population, adaptations, rng=random):
    """Roue de loterie (roue biaisée) : un tirage, parcours linéaire.

    On tire r uniformément dans [0, somme(F)[ puis on avance dans la roue
    jusqu'au premier secteur dont la borne cumulée dépasse r.
    Coût : O(N) par tirage.
    """
    total = sum(adaptations)
    if total == 0:
        return rng.choice(population)
    r = rng.uniform(0, total)
    cumul = 0.0
    for individu, a in zip(population, adaptations):
        cumul += a
        if r < cumul:
            return individu
    return population[-1]  # sécurité contre les arrondis flottants


def roulette_biaisee(population, adaptations, nb_tirages, rng=random, trace=None):
    """Version « exercice 2 » : on prépare la roue une fois, puis on fait
    ``nb_tirages`` tirages par recherche dichotomique.

    Préparation O(N), chaque tirage O(log N) -> O(N + m log N) au total.
    Si ``trace`` est une liste, on y ajoute (r, indice choisi) pour pouvoir
    dérouler l'algorithme à la main.
    """
    cumuls = []
    s = 0.0
    for a in adaptations:
        s += a
        cumuls.append(s)
    elus = []
    for _ in range(nb_tirages):
        r = rng.uniform(0, s)
        k = bisect.bisect_right(cumuls, r)
        k = min(k, len(population) - 1)
        elus.append(population[k])
        if trace is not None:
            trace.append((r, k))
    return elus


# ---------------------------------------------------------------- rang
def rangs(adaptations):
    """Rang 1 = le moins bon, rang N = le meilleur.

    En cas d'égalité, chaque ex aequo reçoit la moyenne des rangs qu'ils
    occupent (3 3 -> rangs 1 et 2 -> 1,5 chacun). C'est la convention la
    plus juste : deux individus identiques ont la même chance.
    """
    ordre = sorted(range(len(adaptations)), key=lambda i: adaptations[i])
    r = [0.0] * len(adaptations)
    i = 0
    while i < len(ordre):
        j = i
        while j + 1 < len(ordre) and adaptations[ordre[j + 1]] == adaptations[ordre[i]]:
            j += 1
        moyen = (i + 1 + j + 1) / 2
        for k in range(i, j + 1):
            r[ordre[k]] = moyen
        i = j + 1
    return r


def probabilites_rang(adaptations):
    """p_i = rang_i / (1 + 2 + ... + N) = 2 rang_i / (N (N+1))."""
    r = rangs(adaptations)
    total = sum(r)
    return [x / total for x in r]


def selection_rang(population, adaptations, rng=random):
    """Même roue que la roulette, mais les secteurs sont les rangs."""
    return selection_roulette(population, rangs(adaptations), rng)


# ---------------------------------------------------------------- tournoi
def selection_tournoi(population, adaptations, rng=random, k=2):
    """Tournoi de taille k : on tire k individus au hasard (avec remise)
    et on garde le meilleur. Coût O(k) par sélection, indépendant de N.
    Plus k est grand, plus la pression de sélection est forte.
    """
    meilleur = rng.randrange(len(population))
    for _ in range(k - 1):
        i = rng.randrange(len(population))
        if adaptations[i] > adaptations[meilleur]:
            meilleur = i
    return population[meilleur]


# ---------------------------------------------------------------- élitisme
def elitisme(population, adaptations, e=1):
    """Renvoie les e meilleurs individus (copiés tels quels dans la
    génération suivante). Tri : O(N log N) ; avec heapq on ferait O(N log e).
    """
    ordre = sorted(range(len(population)), key=lambda i: adaptations[i], reverse=True)
    return [population[i] for i in ordre[:e]]


SELECTIONS = {
    "roulette": selection_roulette,
    "rang": selection_rang,
    "tournoi": selection_tournoi,
}
