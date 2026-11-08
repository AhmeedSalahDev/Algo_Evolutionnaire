"""
TD2 - Exercice 3 : Problème du voyageur de commerce (8 villes)
  1) Recherche taboue (solution initiale 1-2-3-4-5-6-7-8-1)
  2) Recuit simulé (5 itérations, variation empirique de T)

Une case "-" dans le tableau signifie qu'il n'existe pas de liaison
directe entre les deux villes. On lui associe une grande pénalité
(INF = 1000) : un tour qui utilise une telle arête est donc irréalisable
et ne pourra jamais être retenu comme meilleure solution.
"""

import math
import random
from itertools import permutations

INF = 1000
N = 8

TRIANGLE = {
    1: {2: 14, 3: 15, 4: None, 5: None, 6: None, 7: None, 8: 17},
    2: {3: 13, 4: 14, 5: 20, 6: None, 7: None, 8: 21},
    3: {4: 11, 5: 21, 6: 17, 7: 9, 8: 9},
    4: {5: 11, 6: 10, 7: 8, 8: 20},
    5: {6: 15, 7: 18, 8: None},
    6: {7: 9, 8: None},
    7: {8: 13},
}


def construire_matrice():
    D = [[0] * (N + 1) for _ in range(N + 1)]
    for i, ligne in TRIANGLE.items():
        for j, d in ligne.items():
            D[i][j] = D[j][i] = INF if d is None else d
    return D


D = construire_matrice()


def longueur(tour):
    """tour = [1, ..., ] sans répéter la ville de départ à la fin."""
    return sum(D[tour[k]][tour[(k + 1) % len(tour)]] for k in range(len(tour)))


def fmt(tour):
    return "-".join(map(str, tour + [tour[0]]))


def swap(tour, a, b):
    t = tour[:]
    t[a], t[b] = t[b], t[a]
    return t


def recherche_taboue(tour_init, max_iter=30, tenure=5,
                     max_sans_amelioration=15, verbose=True):
    """Recherche taboue avec swap, aspiration, et ville 1 fixe en tête."""
    courant = tour_init[:]
    meilleur, meilleur_cout = courant[:], longueur(courant)
    tabou = {}
    hist = [(0, fmt(courant), meilleur_cout, "-", meilleur_cout, [])]
    sans_amelioration = 0
    if verbose:
        print(f"Solution initiale : {fmt(courant)}  longueur = {meilleur_cout}")

    for it in range(1, max_iter + 1):
        best_move = None
        for a in range(1, N):
            for b in range(a + 1, N):
                u, v = courant[a], courant[b]
                voisin = swap(courant, a, b)
                c = longueur(voisin)
                est_tabou = tabou.get(frozenset((u, v)), 0) >= it
                if est_tabou and c >= meilleur_cout:
                    continue
                if best_move is None or c < best_move[2]:
                    best_move = ((u, v), voisin, c)
        if best_move is None:
            break
        (u, v), courant, c = best_move
        tabou[frozenset((u, v))] = it + tenure
        if c < meilleur_cout:
            meilleur, meilleur_cout = courant[:], c
            sans_amelioration = 0
        else:
            sans_amelioration += 1
        liste = sorted(tuple(sorted(k)) for k, fin in tabou.items() if fin > it)
        hist.append((it, fmt(courant), c, f"({u},{v})", meilleur_cout, liste))
        if verbose:
            print(f"It {it:2d} : swap({u},{v}) -> {fmt(courant)}  L={c:4d}  "
                  f"meilleur={meilleur_cout}  tabou={liste}")
        if sans_amelioration >= max_sans_amelioration:
            break
    return meilleur, meilleur_cout, hist


def temperature_initiale(tour, echantillons=50, p0=0.5, seed=0):
    """Estime la température initiale à partir des dégradations observées."""
    rng = random.Random(seed)
    L0 = longueur(tour)
    deltas = []
    for _ in range(echantillons):
        a, b = rng.sample(range(1, N), 2)
        d = longueur(swap(tour, a, b)) - L0
        if 0 < d < INF / 2:
            deltas.append(d)
    delta_moy = sum(deltas) / len(deltas)
    return -delta_moy / math.log(p0), delta_moy


def recuit_simule(tour_init, n_iter=5, alpha=0.8, seed=18, verbose=True):
    """Recuit simulé avec voisinage swap et règle d'acceptation de Metropolis."""
    rng = random.Random(seed)
    T0, delta_moy = temperature_initiale(tour_init)
    T = T0
    courant = tour_init[:]
    Lc = longueur(courant)
    meilleur, Lb = courant[:], Lc
    hist = []
    if verbose:
        print(f"Delta moyen observé = {delta_moy:.2f}  ->  T0 = {T0:.2f}")
        print(f"Solution initiale : {fmt(courant)}  L = {Lc}")

    for it in range(1, n_iter + 1):
        a, b = sorted(rng.sample(range(1, N), 2))
        u, v = courant[a], courant[b]
        voisin = swap(courant, a, b)
        Lv = longueur(voisin)
        delta = Lv - Lc
        if delta <= 0:
            p, r, accepte = 1.0, None, True
        else:
            p = math.exp(-delta / T)
            r = rng.random()
            accepte = r < p
        hist.append(dict(it=it, T=T, swap=(u, v), voisin=fmt(voisin), Lv=Lv,
                         delta=delta, p=p, r=r, accepte=accepte))
        if accepte:
            courant, Lc = voisin, Lv
            if Lc < Lb:
                meilleur, Lb = courant[:], Lc
        hist[-1].update(courant=fmt(courant), Lc=Lc, Lb=Lb)
        if verbose:
            rs = "  -  " if r is None else f"{r:.3f}"
            print(f"It {it} : T={T:6.2f}  swap({u},{v}) -> {fmt(voisin)}  "
                  f"L={Lv:4d}  delta={delta:5d}  p={p:.3f}  r={rs}  "
                  f"{'ACCEPTÉ' if accepte else 'refusé'}  meilleur={Lb}")
        T *= alpha
    return meilleur, Lb, hist, T0


def recuit_complet(tour_init, alpha=0.95, paliers=200, iter_palier=50, seed=1):
    """Version longue (pour comparaison) : beaucoup plus d'itérations."""
    rng = random.Random(seed)
    T, _ = temperature_initiale(tour_init)
    courant, Lc = tour_init[:], longueur(tour_init)
    meilleur, Lb = courant[:], Lc
    for _ in range(paliers):
        for _ in range(iter_palier):
            a, b = rng.sample(range(1, N), 2)
            v = swap(courant, a, b)
            d = longueur(v) - Lc
            if d <= 0 or rng.random() < math.exp(-d / T):
                courant, Lc = v, Lc + d
                if Lc < Lb:
                    meilleur, Lb = courant[:], Lc
        T *= alpha
    return meilleur, Lb


def optimum_exact():
    """Énumération des 7! = 5040 tours (ville 1 fixée) pour vérifier."""
    best = None
    for p in permutations(range(2, N + 1)):
        t = [1, *p]
        L = longueur(t)
        if best is None or L < best[1]:
            best = (t, L)
    return best


if __name__ == "__main__":
    init = [1, 2, 3, 4, 5, 6, 7, 8]
    print("=== 1) Recherche taboue ===")
    tb, Ltb, _ = recherche_taboue(init)
    print(f"Meilleur tour (tabou) : {fmt(tb)}  longueur = {Ltb}\n")
    print("=== 2) Recuit simulé : 5 itérations ===")
    rs, Lrs, _, _ = recuit_simule(init, n_iter=5)
    print(f"Meilleur tour après 5 itérations : {fmt(rs)}  longueur = {Lrs}\n")
    rc, Lrc = recuit_complet(init)
    print(f"Recuit simulé (version longue) : {fmt(rc)}  longueur = {Lrc}\n")
    opt, Lopt = optimum_exact()
    print(f"Vérification (énumération exhaustive) : {fmt(opt)}  longueur = {Lopt}")
