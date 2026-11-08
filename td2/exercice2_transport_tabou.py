"""
TD2 - Exercice 2 : Problème de transport (dépôts -> magasins)
Résolution par RECHERCHE TABOUE.

Données :
            M1  M2  M3 | Stock
      D1     5   3   4 |   8
      D2     6   7   2 |   9
  Demande    4   5   8

Représentation d'une solution : matrice X[i][j] = nombre de containers
envoyés du dépôt Di au magasin Mj (entiers >= 0).

Voisinage (inspiré de la méthode "stepping stone") : on choisit deux
dépôts (i, k) et deux magasins (j, l) et on déplace une unité le long du
cycle  (i,j)+1  (i,l)-1  (k,l)+1  (k,j)-1.
Ce mouvement conserve automatiquement les stocks et les demandes, donc
tout voisin reste une solution réalisable.

Liste taboue : après le mouvement (i,j,k,l), le mouvement inverse
(i,l,k,j) est interdit pendant `tenure` itérations.
Critère d'aspiration : un mouvement tabou est accepté s'il donne une
solution meilleure que la meilleure trouvée jusqu'ici.
"""

from itertools import combinations, permutations, product

COUTS = [[5, 3, 4],
         [6, 7, 2]]
STOCKS = [8, 9]
DEMANDES = [4, 5, 8]


def equilibrer(couts, stocks, demandes):
    """Ajoute un magasin (ou dépôt) fictif de coût 0 si offre != demande."""
    couts = [row[:] for row in couts]
    stocks, demandes = stocks[:], demandes[:]
    diff = sum(stocks) - sum(demandes)
    if diff > 0:
        for row in couts:
            row.append(0)
        demandes.append(diff)
    elif diff < 0:
        couts.append([0] * len(demandes))
        stocks.append(-diff)
    return couts, stocks, demandes


def cout_total(X, couts):
    return sum(couts[i][j] * X[i][j]
               for i in range(len(X)) for j in range(len(X[0])))


def coin_nord_ouest(stocks, demandes):
    """Solution initiale réalisable par la règle du coin Nord-Ouest."""
    s, d = stocks[:], demandes[:]
    X = [[0] * len(d) for _ in s]
    i = j = 0
    while i < len(s) and j < len(d):
        q = min(s[i], d[j])
        X[i][j] = q
        s[i] -= q
        d[j] -= q
        if s[i] == 0:
            i += 1
        else:
            j += 1
    return X


def voisins(X):
    """Génère tous les mouvements de cycle réalisables (une unité)."""
    m, n = len(X), len(X[0])
    for i, k in combinations(range(m), 2):
        for j, l in permutations(range(n), 2):
            if X[i][l] >= 1 and X[k][j] >= 1:
                Y = [row[:] for row in X]
                Y[i][j] += 1
                Y[i][l] -= 1
                Y[k][l] += 1
                Y[k][j] -= 1
                yield (i, j, k, l), Y


def cle(cases):
    """Un mouvement est identifié par l'ensemble des cases augmentées."""
    return frozenset(cases)


def recherche_taboue(couts, stocks, demandes, max_iter=50, tenure=3,
                     max_sans_amelioration=5, verbose=True):
    couts, stocks, demandes = equilibrer(couts, stocks, demandes)
    X = coin_nord_ouest(stocks, demandes)
    meilleur, meilleur_cout = X, cout_total(X, couts)
    tabou = {}
    sans_amelioration = 0
    historique = [(0, None, meilleur_cout, meilleur_cout)]
    if verbose:
        print(f"Solution initiale (coin Nord-Ouest) : {X}  coût = {meilleur_cout}")

    for it in range(1, max_iter + 1):
        candidat = None
        for mv, Y in voisins(X):
            c = cout_total(Y, couts)
            i, j, k, l = mv
            est_tabou = tabou.get(cle([(i, j), (k, l)]), 0) >= it
            if est_tabou and c >= meilleur_cout:
                continue
            if candidat is None or c < candidat[2]:
                candidat = (mv, Y, c)
        if candidat is None:
            break
        mv, X, c = candidat
        i, j, k, l = mv
        tabou[cle([(i, l), (k, j)])] = it + tenure
        if c < meilleur_cout:
            meilleur, meilleur_cout = X, c
            sans_amelioration = 0
        else:
            sans_amelioration += 1
        historique.append((it, mv, c, meilleur_cout))
        if verbose:
            print(f"It {it:2d} : mouvement D{i+1}->M{j+1} +1 / D{k+1}->M{l+1} +1 "
                  f"(D{i+1}->M{l+1} -1, D{k+1}->M{j+1} -1)  X={X}  coût={c}  "
                  f"meilleur={meilleur_cout}")
        if sans_amelioration >= max_sans_amelioration:
            if verbose:
                print(f"Arrêt : {max_sans_amelioration} itérations sans amélioration.")
            break
    return meilleur, meilleur_cout, historique


def verification_exhaustive(couts, stocks, demandes):
    """Énumère toutes les solutions entières (petite instance) -> optimum exact."""
    best = None
    n = len(demandes)
    for ligne1 in product(*[range(min(stocks[0], d) + 1) for d in demandes]):
        if sum(ligne1) != stocks[0]:
            continue
        ligne2 = [demandes[j] - ligne1[j] for j in range(n)]
        if min(ligne2) < 0 or sum(ligne2) != stocks[1]:
            continue
        X = [list(ligne1), ligne2]
        c = cout_total(X, couts)
        if best is None or c < best[1]:
            best = (X, c)
    return best


if __name__ == "__main__":
    print("=== Exercice 2 : transport par recherche taboue ===")
    X, c, hist = recherche_taboue(COUTS, STOCKS, DEMANDES, max_iter=50, tenure=3)
    print("\nMeilleure solution trouvée :")
    for i, row in enumerate(X):
        print(f"  D{i+1} : " + "  ".join(f"M{j+1}={q}" for j, q in enumerate(row)))
    print(f"  Coût total = {c}")
    Xe, ce = verification_exhaustive(COUTS, STOCKS, DEMANDES)
    print(f"\nVérification par énumération exhaustive : {Xe}  coût optimal = {ce}")
