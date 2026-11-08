"""TD3 — exercices 1, 2 et 3 : on vérifie par le calcul ce qu'on a fait à la main.

Lancer depuis la racine du dépôt :  python -m td3_cedule.exercices
"""
import math
import random
from fractions import Fraction

from td3_cedule.selection import (elitisme, probabilites_rang,
                                  probabilites_roulette, rangs,
                                  roulette_biaisee, selection_tournoi)


# ========================================================== Exercice 1
POPULATION_EX1 = [3, 3, 5, 5, 5, 5, 7, 7]


def f_ex1(x):
    return x ** 3


def ex1_probabilites():
    """Renvoie {valeur: (p par copie, p totale)} pour la roulette et le rang."""
    adapt = [f_ex1(x) for x in POPULATION_EX1]
    resultats = {}
    for nom, probas in (("roulette", probabilites_roulette(adapt)),
                        ("rang", probabilites_rang(adapt))):
        par_valeur = {}
        for x, p in zip(POPULATION_EX1, probas):
            copie, total = par_valeur.get(x, (p, 0.0))
            par_valeur[x] = (copie, total + p)
        resultats[nom] = par_valeur
    return resultats


def en_binaire(x, n=4):
    return format(x, f"0{n}b")


def croisement_un_point(a, b, point):
    return a[:point] + b[point:], b[:point] + a[point:]


def mutation_dernier_bit(c):
    return c[:-1] + ("0" if c[-1] == "1" else "1")


def ex1_generation_suivante():
    """Énumère tous les enfants possibles (croisement en 1 point, coupures
    1 à 3) puis applique ou non la mutation du dernier bit."""
    codes = sorted({en_binaire(x) for x in POPULATION_EX1})
    apres_croisement = set()
    detail = []
    for i, a in enumerate(codes):
        for b in codes[i:]:
            for point in (1, 2, 3):
                e1, e2 = croisement_un_point(a, b, point)
                apres_croisement.update((e1, e2))
                detail.append((a, b, point, e1, e2))
    apres_mutation = {mutation_dernier_bit(c) for c in apres_croisement}
    return codes, detail, apres_croisement, apres_mutation


# ========================================================== Exercice 2
A, B, PRECISION = 0.0, 10.0, 0.1
VALEURS_EX2 = [0.5, 1.2, 2.2, 6.5, 7.6, 9.9]


def f_ex2(x):
    return x * x - 1


def nb_bits(a=A, b=B, precision=PRECISION):
    """Plus petit n tel que 2^n >= (b - a)/precision + 1."""
    nb_valeurs = round((b - a) / precision) + 1
    return math.ceil(math.log2(nb_valeurs))


def coder(x, n=None):
    n = n or nb_bits()
    k = round((x - A) / PRECISION)
    return format(k, f"0{n}b")


def decoder(chaine):
    return A + int(chaine, 2) * PRECISION


def adaptation_ex2(fx, mode="cmax"):
    """Deux façons de transformer une minimisation en adaptation positive.

    - "cmax"   : F = Cmax - f  avec Cmax = max f sur [0,10] = f(10) = 99
    - "inverse": F = 1 / (f - fmin + 1) = 1 / (f + 2)   (fmin = f(0) = -1)
    """
    if mode == "cmax":
        return f_ex2(B) - fx
    return 1 / (fx - f_ex2(A) + 1)


# ========================================================== Exercice 3
def demo_tournoi_elitisme(seed=3):
    rng = random.Random(seed)
    pop = VALEURS_EX2
    adapt = [adaptation_ex2(f_ex2(x)) for x in pop]
    tournoi = [selection_tournoi(pop, adapt, rng, k=2) for _ in range(6)]
    return tournoi, elitisme(pop, adapt, e=2)


# ========================================================== affichage
def main():
    print("=" * 66)
    print("EXERCICE 1  —  f(x) = x^3, population 3 3 5 5 5 5 7 7")
    print("=" * 66)
    adapt = [f_ex1(x) for x in POPULATION_EX1]
    print(f"f : {adapt}   somme = {sum(adapt)}")
    print(f"rangs (ex aequo moyennés) : {rangs(adapt)}   somme = {sum(rangs(adapt))}")
    res = ex1_probabilites()
    for nom in ("roulette", "rang"):
        print(f"\n  {nom}")
        for x, (copie, total) in res[nom].items():
            print(f"    x={x} : une copie {copie:.4f}   toutes copies {total:.4f}")
    tot = sum(adapt)
    print("\n  fractions exactes (roulette) :",
          {x: str(Fraction(f_ex1(x) * POPULATION_EX1.count(x), tot)) for x in (3, 5, 7)})
    print("  fractions exactes (rang)     :",
          {x: str(Fraction(int(2 * sum(r for v, r in zip(POPULATION_EX1, rangs(adapt)) if v == x)), 72))
           for x in (3, 5, 7)})

    codes, detail, croises, mutes = ex1_generation_suivante()
    print("\n  Codage 4 bits :", {int(c, 2): c for c in codes})
    print("  Croisements qui produisent quelque chose de nouveau :")
    for a, b, p, e1, e2 in detail:
        if {e1, e2} != {a, b}:
            print(f"    {a} x {b}, coupure après le bit {p} -> {e1} ({int(e1, 2)}), {e2} ({int(e2, 2)})")
    print("  Après croisement :", sorted(int(c, 2) for c in croises))
    print("  Si l'enfant est muté (dernier bit inversé) :", sorted(int(c, 2) for c in mutes))
    print("  Individus possibles en t+1 :", sorted(int(c, 2) for c in croises | mutes))

    print("\n" + "=" * 66)
    print("EXERCICE 2  —  minimiser f(x) = x^2 - 1 sur [0, 10], précision 0,1")
    print("=" * 66)
    n = nb_bits()
    print(f"(10 - 0)/0,1 + 1 = 101 valeurs  ->  2^6 = 64 < 101 <= 128 = 2^7  ->  n = {n} bits")
    print(f"{'x':>5} {'k':>4} {'binaire':>9} {'f(x)':>8} {'F=99-f':>8} {'p roul.':>8} {'F=1/(f+2)':>10} {'p roul.':>8}")
    F1 = [adaptation_ex2(f_ex2(x)) for x in VALEURS_EX2]
    F2 = [adaptation_ex2(f_ex2(x), "inverse") for x in VALEURS_EX2]
    p1, p2 = probabilites_roulette(F1), probabilites_roulette(F2)
    for x, a, b, q1, q2 in zip(VALEURS_EX2, F1, F2, p1, p2):
        c = coder(x)
        assert abs(decoder(c) - x) < 1e-9
        print(f"{x:5.1f} {int(c, 2):4d} {c:>9} {f_ex2(x):8.2f} {a:8.2f} {q1:8.4f} {b:10.4f} {q2:8.4f}")
    print(f"{'':>28}somme {sum(F1):8.2f} {'':>8} {sum(F2):10.4f}")

    print("\n  Déroulement de la roue biaisée (F = 99 - f, 6 tirages, graine 7) :")
    cumul, bornes = 0.0, []
    for x, a in zip(VALEURS_EX2, F1):
        bornes.append((x, cumul, cumul + a))
        cumul += a
    for x, lo, hi in bornes:
        print(f"    x={x:<4} secteur [{lo:7.2f} ; {hi:7.2f}[")
    trace = []
    elus = roulette_biaisee(VALEURS_EX2, F1, 6, random.Random(7), trace)
    for (r, k), x in zip(trace, elus):
        print(f"    r = {r:7.2f}  ->  secteur {k + 1}  ->  x = {x}")

    print("\n" + "=" * 66)
    print("EXERCICE 3  —  tournoi (k=2) et élitisme (e=2) sur les mêmes individus")
    print("=" * 66)
    tournoi, elite = demo_tournoi_elitisme()
    print("  6 tournois :", tournoi)
    print("  élite (2 meilleurs) :", elite)


if __name__ == "__main__":
    main()
