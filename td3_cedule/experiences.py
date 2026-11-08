"""Toutes les figures et sorties du compte rendu TD3.

Lancer depuis la racine du dépôt (≈ 1 à 2 minutes) :
    pip install matplotlib
    python -m td3_cedule.experiences

Les images vont dans td3_cedule/figures/, les chiffres dans td3_cedule/sorties/.
"""
import contextlib
import io
import os
import random
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(ICI))

from td3_cedule import cedule as C  # noqa: E402
from td3_cedule import exercices as E  # noqa: E402
from td3_cedule.selection import (SELECTIONS, probabilites_rang,  # noqa: E402
                                  probabilites_roulette)

FIG = os.path.join(ICI, "figures")
OUT = os.path.join(ICI, "sorties")
os.makedirs(FIG, exist_ok=True)
os.makedirs(OUT, exist_ok=True)

COUL = {"roulette": "#2F6DB5", "rang": "#E08A1E", "tournoi": "#3A9E5C"}
plt.rcParams.update({"font.size": 10, "axes.spines.top": False,
                     "axes.spines.right": False, "figure.dpi": 110})


def sauver(fig, nom):
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, nom), dpi=160)
    plt.close(fig)
    print("  figure :", nom)


# ================================================================ exercice 1
def figure_ex1():
    adapt = [E.f_ex1(x) for x in E.POPULATION_EX1]
    fig, axes = plt.subplots(1, 2, figsize=(9, 4.2))
    teintes = {3: "#C9D6E8", 5: "#7FA3CF", 7: "#2F5E96"}
    for ax, (titre, p) in zip(axes, (("Roulette  (p ∝ x³)", probabilites_roulette(adapt)),
                                      ("Rang  (p ∝ rang)", probabilites_rang(adapt)))):
        ax.pie(p, colors=[teintes[x] for x in E.POPULATION_EX1], startangle=90,
               counterclock=False, wedgeprops={"edgecolor": "white", "linewidth": 1.5},
               labels=[str(x) for x in E.POPULATION_EX1], labeldistance=0.72,
               textprops={"color": "black", "fontsize": 9})
        tot = {x: sum(q for v, q in zip(E.POPULATION_EX1, p) if v == x) for x in (3, 5, 7)}
        ax.set_title(titre + "\n" + "   ".join(f"{x} → {tot[x]:.1%}" for x in (3, 5, 7)), fontsize=10)
    fig.suptitle("Exercice 1 — même population, deux roues très différentes", fontweight="bold")
    sauver(fig, "ex1_roulette_vs_rang.png")


# ================================================================ exercice 2
def figure_ex2():
    xs = E.VALEURS_EX2
    F1 = [E.adaptation_ex2(E.f_ex2(x)) for x in xs]
    F2 = [E.adaptation_ex2(E.f_ex2(x), "inverse") for x in xs]
    trace = []
    E.roulette_biaisee(xs, F1, 6, random.Random(7), trace)
    fig, axes = plt.subplots(2, 1, figsize=(10, 3.8))
    palette = plt.cm.viridis([0.1, 0.28, 0.45, 0.62, 0.78, 0.93])
    for ax, F, titre in ((axes[0], F1, "F = 99 − f(x)"), (axes[1], F2, "F = 1 / (f(x) + 2)")):
        p = probabilites_roulette(F)
        g = 0.0
        for x, q, c in zip(xs, p, palette):
            ax.barh(0, q, left=g, color=c, edgecolor="white")
            if q > 0.04:
                ax.text(g + q / 2, 0, f"{x}\n{q:.0%}", ha="center", va="center",
                        color="white" if c[1] < 0.6 else "black", fontsize=8)
            g += q
        ax.set_xlim(0, 1)
        ax.set_yticks([])
        ax.set_ylabel(titre, rotation=0, ha="right", va="center", fontsize=10)
        ax.set_ylim(-0.5, 0.85)
        for s in ("left", "bottom"):
            ax.spines[s].set_visible(False)
        ax.set_xticks([])
    total = sum(F1)
    for r, _ in trace:
        axes[0].annotate("", xy=(r / total, 0.42), xytext=(r / total, 0.82),
                         arrowprops={"arrowstyle": "-|>", "color": "crimson"})
    axes[0].text(1.0, -0.62, "flèches rouges = les 6 tirages r de l'exemple", color="crimson", ha="right", fontsize=8)
    fig.suptitle("Exercice 2 — roue biaisée : le choix de l'adaptation change tout",
                 fontweight="bold")
    sauver(fig, "ex2_roue_biaisee.png")


# ================================================================ cédule
def dessiner_chromosome(ax, chrom, y, titre, surligne=None):
    for u, gene in enumerate(chrom):
        for b, bit in enumerate(gene):
            x = u * 4.6 + b
            fond = "#F3C969" if surligne == u else ("#2F6DB5" if bit == "1" else "#EEF1F5")
            ax.add_patch(Rectangle((x, y), 1, 1, facecolor=fond, edgecolor="#555", lw=0.6))
            ax.text(x + 0.5, y + 0.5, bit, ha="center", va="center", fontsize=8,
                    color="white" if bit == "1" and surligne != u else "black")
        ax.text(u * 4.6 + 2, y + 1.35, f"U{u + 1}", ha="center", fontsize=8, color="#444")
    ax.text(-0.6, y + 0.5, titre, ha="right", va="center", fontsize=9)


def figure_operateurs():
    p1 = C.EXEMPLE_COURS
    p2 = ["1100", "0110", "0100", "0001", "0010", "1000", "0100"]
    e1, e2 = p1[:4] + p2[4:], p2[:4] + p1[4:]
    m = list(p1)
    m[2] = "0100"
    fig, ax = plt.subplots(figsize=(10, 4.6))
    lignes = [(p1, "Parent 1"), (p2, "Parent 2"), (e1, "Enfant 1"), (e2, "Enfant 2")]
    for i, (c, t) in enumerate(lignes):
        dessiner_chromosome(ax, c, 9.5 - i * 2.1 - (0.6 if i >= 2 else 0), t)
    ax.axvline(4 * 4.6 - 0.3, ymin=0.25, ymax=0.97, color="crimson", ls="--", lw=1)
    ax.text(4 * 4.6 - 0.3, 11.6, "coupure entre deux gènes", color="crimson", ha="center", fontsize=8)
    dessiner_chromosome(ax, m, -1.6, "Mutation", surligne=2)
    ax.text(2 * 4.6 + 2, -2.4, "0001 → 0100 : on change de période, la durée reste juste",
            ha="center", fontsize=8, color="#8A6100")
    ax.set_xlim(-6, 32)
    ax.set_ylim(-3, 12.2)
    ax.axis("off")
    ax.set_title("Opérateurs par blocs de 4 bits (comme dans le support)", fontweight="bold")
    sauver(fig, "cedule_operateurs.png")


def figure_paysage(perf):
    valeurs = sorted(set(perf))
    nb = [perf.count(v) for v in valeurs]
    fig, ax = plt.subplots(figsize=(7.5, 3.6))
    barres = ax.bar([str(v) for v in valeurs], nb, color=["#B0B7C3"] + ["#2F6DB5"] * (len(valeurs) - 2) + ["crimson"])
    ax.set_yscale("log")
    for b, n in zip(barres, nb):
        ax.text(b.get_x() + b.get_width() / 2, n * 1.15, str(n), ha="center", fontsize=8)
    ax.set_xlabel("performance (plus petite réserve, MW)")
    ax.set_ylabel("nombre de cédules (échelle log)")
    ax.set_title(f"Les {len(perf)} cédules possibles : 75 % valent 0, seulement {nb[-1]} atteignent {valeurs[-1]} MW",
                 fontsize=10, fontweight="bold")
    sauver(fig, "cedule_paysage.png")


def figure_gantt(chrom):
    res = C.reserves(chrom)
    perdue = C.puissance_en_maintenance(chrom)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 3.8), gridspec_kw={"width_ratios": [1.15, 1]})
    for u, gene in enumerate(chrom):
        for t in range(4):
            if gene[t] == "1":
                a1.add_patch(Rectangle((t, 6 - u - 0.4), 1, 0.8, color="#2F6DB5"))
                a1.text(t + 0.5, 6 - u, f"{C.CAPACITES[u]} MW", ha="center", va="center", color="white", fontsize=8)
    a1.set_xlim(0, 4)
    a1.set_ylim(-0.7, 6.7)
    a1.set_yticks(range(7))
    a1.set_yticklabels([f"unité {7 - i}" for i in range(7)])
    a1.set_xticks([0.5, 1.5, 2.5, 3.5])
    a1.set_xticklabels([f"I{t + 1}" for t in range(4)])
    for t in range(1, 4):
        a1.axvline(t, color="#ddd", lw=0.8)
    a1.set_title("Qui est à l'arrêt, et quand", fontsize=10)

    x = range(4)
    a2.bar(x, C.DEMANDES, color="#B0B7C3", label="demande")
    a2.bar(x, res, bottom=C.DEMANDES, color="#3A9E5C", label="réserve")
    a2.bar(x, perdue, bottom=[d + r for d, r in zip(C.DEMANDES, res)], color="#2F6DB5", alpha=0.35,
           label="perdue (maintenance)")
    a2.axhline(C.CAPACITE_TOTALE, color="black", lw=0.8, ls=":")
    a2.text(3.45, C.CAPACITE_TOTALE + 2, "150 MW", ha="right", fontsize=8)
    for t in x:
        a2.text(t, C.DEMANDES[t] + res[t] / 2, f"{res[t]}", ha="center", va="center", color="white", fontweight="bold")
    a2.set_xticks(list(x))
    a2.set_xticklabels([f"I{t + 1}" for t in x])
    a2.set_ylabel("MW")
    a2.set_ylim(0, 165)
    a2.legend(fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=3, frameon=False)
    a2.set_title(f"Bilan de puissance — réserve minimale = {min(res)} MW", fontsize=10)
    fig.suptitle("Meilleure cédule trouvée par l'AG : " + " ".join(chrom), fontweight="bold")
    sauver(fig, "cedule_gantt.png")


def moyenne_courbes(selection, n_runs, **kw):
    best, mean = None, None
    for s in range(n_runs):
        _, h = C.algorithme_genetique(selection=selection, seed=s, **kw)
        if best is None:
            best, mean = [0.0] * len(h["meilleur"]), [0.0] * len(h["moyenne"])
        best = [a + b / n_runs for a, b in zip(best, h["meilleur"])]
        mean = [a + b / n_runs for a, b in zip(mean, h["moyenne"])]
    return best, mean


def figure_convergence(log):
    fig, ax = plt.subplots(figsize=(8, 4))
    for sel in SELECTIONS:
        best, mean = moyenne_courbes(sel, 30, taille=42, generations=40)
        ax.plot(best, color=COUL[sel], lw=2, label=f"{sel} — meilleur")
        ax.plot(mean, color=COUL[sel], lw=1.2, ls="--", label=f"{sel} — moyenne")
        log.append(f"{sel:9s} N=42 : meilleur moyen gén.0 = {best[0]:.2f}, gén.5 = {best[5]:.2f}, "
                   f"gén.40 = {best[-1]:.2f} | moyenne pop. gén.0 = {mean[0]:.2f}, gén.40 = {mean[-1]:.2f}")
    ax.axhline(25, color="crimson", lw=0.8, ls=":")
    ax.text(40, 25.4, "optimum 25 MW", color="crimson", ha="right", fontsize=8)
    ax.set_xlabel("génération")
    ax.set_ylabel("performance (MW)")
    ax.set_ylim(0, 27)
    ax.legend(fontsize=8, ncol=3, loc="lower right")
    ax.set_title("Convergence (moyenne de 30 exécutions, N = 42, pc = 0,8, pm = 0,1)", fontweight="bold")
    sauver(fig, "cedule_convergence.png")


def part_parents_nuls(sel, n_pop=200):
    """Proportion de parents de performance 0 choisis dans une population initiale."""
    tot = choisis = 0
    for s in range(n_pop):
        rng = random.Random(1000 + s)
        pop = [C.individu_aleatoire(rng) for _ in range(42)]
        adapt = [C.performance(c) for c in pop]
        for _ in range(42):
            choisis += C.performance(SELECTIONS[sel](pop, adapt, rng)) == 0
            tot += 1
    return choisis / tot


def figure_selections(log):
    runs = 300
    res = {}
    for el in (1, 0):
        for sel in SELECTIONS:
            ok = sum(C.performance(C.algorithme_genetique(taille=10, generations=15, selection=sel,
                                                           nb_elites=el, seed=s)[0]) == 25
                     for s in range(runs))
            res[(sel, el)] = ok / runs
    nuls = {sel: part_parents_nuls(sel) for sel in SELECTIONS}

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 3.9), gridspec_kw={"width_ratios": [1.4, 1]})
    largeur = 0.36
    for i, sel in enumerate(SELECTIONS):
        for j, el in enumerate((1, 0)):
            v = res[(sel, el)]
            b = a1.bar(i + (j - 0.5) * largeur, v, largeur, color=COUL[sel], alpha=1 if el else 0.45,
                       edgecolor="white")
            a1.text(b[0].get_x() + largeur / 2, v + 0.015, f"{v:.0%}", ha="center", fontsize=8)
    a1.set_xticks(range(3))
    a1.set_xticklabels(list(SELECTIONS))
    a1.set_ylim(0, 1)
    a1.set_ylabel("taux de réussite (optimum 25 MW)")
    a1.set_title(f"Petit budget : N = 10, 15 gén., {runs} graines\n(foncé : avec élitisme, clair : sans)", fontsize=10)

    a2.bar(list(SELECTIONS), [nuls[s] for s in SELECTIONS], color=[COUL[s] for s in SELECTIONS])
    for i, s in enumerate(SELECTIONS):
        a2.text(i, nuls[s] + 0.01, f"{nuls[s]:.0%}", ha="center", fontsize=9)
    a2.axhline(0.75, color="#888", ls=":", lw=0.8)
    a2.text(2.4, 0.765, "75 % de la population", fontsize=8, ha="right", color="#666")
    a2.set_ylim(0, 0.85)
    a2.set_title("Parents « nuls » choisis à la génération 0", fontsize=10)
    fig.suptitle("Comparaison des sélections sur la cédule", fontweight="bold")
    sauver(fig, "cedule_selections.png")

    for (sel, el), v in res.items():
        log.append(f"petit budget  {sel:9s} élitisme={el} : réussite {v:.1%}")
    for sel, v in nuls.items():
        log.append(f"parents de performance 0 choisis ({sel}) : {v:.1%}")


def figure_pc_pm(log):
    pcs = [0.0, 0.4, 0.6, 0.8, 1.0]
    pms = [0.0, 0.02, 0.05, 0.1, 0.2, 0.4]
    runs = 150
    grille = []
    for pc in pcs:
        ligne = []
        for pm in pms:
            ok = sum(C.performance(C.algorithme_genetique(taille=10, generations=15, pc=pc, pm=pm,
                                                           seed=s)[0]) == 25 for s in range(runs))
            ligne.append(ok / runs)
        grille.append(ligne)
    fig, ax = plt.subplots(figsize=(7, 4))
    im = ax.imshow(grille, cmap="YlGnBu", vmin=0, vmax=1, origin="lower", aspect="auto")
    for i in range(len(pcs)):
        for j in range(len(pms)):
            v = grille[i][j]
            ax.text(j, i, f"{v:.0%}", ha="center", va="center", fontsize=8,
                    color="white" if v > 0.6 else "black")
    ax.set_xticks(range(len(pms)))
    ax.set_xticklabels([str(p) for p in pms])
    ax.set_yticks(range(len(pcs)))
    ax.set_yticklabels([str(p) for p in pcs])
    ax.set_xlabel("pm (probabilité de muter chaque gène)")
    ax.set_ylabel("pc (probabilité de croisement)")
    fig.colorbar(im, ax=ax, label="taux de réussite")
    ax.set_title(f"Réglage de pc et pm (roulette + élitisme, N = 10, 15 gén., {runs} graines)",
                 fontsize=10, fontweight="bold")
    sauver(fig, "cedule_pc_pm.png")
    log.append("grille pc x pm (lignes pc = " + str(pcs) + ", colonnes pm = " + str(pms) + ")")
    for pc, ligne in zip(pcs, grille):
        log.append(f"  pc={pc:<4}: " + "  ".join(f"{v:5.1%}" for v in ligne))


def main():
    print("Sorties texte...")
    for nom, fn in (("sortie_exercices.txt", E.main), ("sortie_cedule.txt", C.main)):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            fn()
        with open(os.path.join(OUT, nom), "w", encoding="utf-8") as f:
            f.write(buf.getvalue())
        print("  sortie :", nom)

    print("Figures...")
    figure_ex1()
    figure_ex2()
    figure_operateurs()
    _, _, _, perf = C.enumeration_exhaustive()
    figure_paysage(perf)
    meilleur, _ = C.algorithme_genetique(seed=2026)
    figure_gantt(meilleur)
    log = []
    figure_convergence(log)
    figure_selections(log)
    figure_pc_pm(log)
    with open(os.path.join(OUT, "sortie_experiences.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(log) + "\n")
    print("  sortie : sortie_experiences.txt")


if __name__ == "__main__":
    main()
