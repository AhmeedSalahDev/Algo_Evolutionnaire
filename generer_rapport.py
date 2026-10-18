"""Génère les figures et le compte rendu PDF du TD2."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Image, KeepTogether, PageBreak, Paragraph,
                                Preformatted, SimpleDocTemplate, Spacer, Table,
                                TableStyle)

import exercice2_transport_tabou as ex2
import exercice3_tsp as ex3

GITHUB = "https://github.com/AhmeedSalahDev/TD2_Optimisation_Python_Algo"

F = "/usr/share/fonts/truetype/dejavu/"
pdfmetrics.registerFont(TTFont("DV", F + "DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DVB", F + "DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DVI", F + "DejaVuSans-Oblique.ttf"))
pdfmetrics.registerFont(TTFont("DVM", F + "DejaVuSansMono.ttf"))
from reportlab.pdfbase.pdfmetrics import registerFontFamily
registerFontFamily("DV", normal="DV", bold="DVB", italic="DVI", boldItalic="DVB")

BLEU = colors.HexColor("#1F4E79")
GRIS = colors.HexColor("#F2F2F2")
VERT = colors.HexColor("#E2F0D9")

ss = getSampleStyleSheet()
N = ParagraphStyle("N", parent=ss["Normal"], fontName="DV", fontSize=10,
                   leading=14.5, alignment=TA_JUSTIFY, spaceAfter=6)
H1 = ParagraphStyle("H1", parent=N, fontName="DVB", fontSize=15, leading=20,
                    textColor=BLEU, spaceBefore=10, spaceAfter=8, alignment=0)
H2 = ParagraphStyle("H2", parent=N, fontName="DVB", fontSize=12, leading=16,
                    textColor=BLEU, spaceBefore=8, spaceAfter=5, alignment=0)
C = ParagraphStyle("C", parent=N, alignment=TA_CENTER)
CAP = ParagraphStyle("CAP", parent=N, fontName="DVI", fontSize=8.5,
                     alignment=TA_CENTER, textColor=colors.HexColor("#555555"))
CELL = ParagraphStyle("CELL", parent=N, fontSize=8, leading=10, alignment=0,
                      spaceAfter=0)
CODE = ParagraphStyle("CODE", fontName="DVM", fontSize=6.8, leading=8.4)


def P(t, s=N):
    return Paragraph(t, s)


def tableau(data, widths, header=True, hl_rows=(), font=8.5):
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0)
    st = [("FONT", (0, 0), (-1, -1), "DV", font),
          ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#9A9A9A")),
          ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
          ("ALIGN", (0, 0), (-1, -1), "CENTER"),
          ("TOPPADDING", (0, 0), (-1, -1), 2.5),
          ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5)]
    if header:
        st += [("BACKGROUND", (0, 0), (-1, 0), BLEU),
               ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
               ("FONT", (0, 0), (-1, 0), "DVB", font)]
    for r in hl_rows:
        st.append(("BACKGROUND", (0, r), (-1, r), VERT))
    t.setStyle(TableStyle(st))
    return t


# ---------------------------------------------------------------- calculs
X2, c2, hist2 = ex2.recherche_taboue(ex2.COUTS, ex2.STOCKS, ex2.DEMANDES,
                                     max_iter=50, tenure=3, verbose=False)
X2e, c2e = ex2.verification_exhaustive(ex2.COUTS, ex2.STOCKS, ex2.DEMANDES)

INIT = [1, 2, 3, 4, 5, 6, 7, 8]
tb, Ltb, hist_tb = ex3.recherche_taboue(INIT, verbose=False)
rs, Lrs, hist_rs, T0 = ex3.recuit_simule(INIT, n_iter=5, verbose=False)
_, delta_moy = ex3.temperature_initiale(INIT)
rc, Lrc = ex3.recuit_complet(INIT)
opt, Lopt = ex3.optimum_exact()

# ---------------------------------------------------------------- figures
plt.rcParams.update({"font.size": 9, "axes.spines.top": False,
                     "axes.spines.right": False})

fig, ax = plt.subplots(figsize=(6.2, 2.6))
its = [h[0] for h in hist2]
ax.plot(its, [h[2] for h in hist2], "o-", color="#2E75B6", label="solution courante")
ax.plot(its, [h[3] for h in hist2], "s--", color="#C00000", label="meilleure solution")
ax.set_xlabel("itération"); ax.set_ylabel("coût total")
ax.legend(frameon=False); fig.tight_layout()
fig.savefig("fig_ex2_tabou.png", dpi=200); plt.close(fig)

fig, ax = plt.subplots(figsize=(6.2, 2.8))
its = [h[0] for h in hist_tb]
ax.plot(its, [h[2] for h in hist_tb], "o-", ms=3.5, color="#2E75B6", label="tour courant")
ax.plot(its, [h[4] for h in hist_tb], "--", color="#C00000", label="meilleur tour")
ax.axhline(Lopt, color="#70AD47", lw=0.8, ls=":", label=f"optimum = {Lopt}")
ax.set_xlabel("itération"); ax.set_ylabel("longueur du tour")
ax.legend(frameon=False, ncol=3, loc="upper right"); fig.tight_layout()
fig.savefig("fig_ex3_tabou.png", dpi=200); plt.close(fig)

# graphe des villes (positions schématiques) avec le tour optimal
import math
pos = {k: (math.cos(2 * math.pi * (k - 1) / 8 + math.pi / 2),
           math.sin(2 * math.pi * (k - 1) / 8 + math.pi / 2)) for k in range(1, 9)}
fig, ax = plt.subplots(figsize=(3.6, 3.4))
for i in range(1, 9):
    for j in range(i + 1, 9):
        if ex3.D[i][j] < ex3.INF:
            ax.plot(*zip(pos[i], pos[j]), color="#C8C8C8", lw=0.7, zorder=1)
            mx, my = (pos[i][0] + pos[j][0]) / 2, (pos[i][1] + pos[j][1]) / 2
            ax.text(mx, my, ex3.D[i][j], fontsize=6, color="#888888",
                    ha="center", va="center", zorder=2)
for k in range(8):
    a, b = opt[k], opt[(k + 1) % 8]
    ax.plot(*zip(pos[a], pos[b]), color="#C00000", lw=2.2, zorder=3)
for k, (x, y) in pos.items():
    ax.scatter(x, y, s=260, color="#1F4E79", zorder=4)
    ax.text(x, y, str(k), color="white", ha="center", va="center",
            fontsize=9, fontweight="bold", zorder=5)
ax.set_aspect("equal"); ax.axis("off"); fig.tight_layout()
fig.savefig("fig_ex3_graphe.png", dpi=220); plt.close(fig)

# ---------------------------------------------------------------- document
story = []

def page_garde():
    story.append(Spacer(1, 0.6 * cm))
    for t in ["RÉPUBLIQUE TUNISIENNE",
              "Ministère de l'Enseignement Supérieur et de la Recherche Scientifique",
              "Université de Sfax", "<b>Faculté des Sciences de Sfax</b>"]:
        story.append(P(t, C))
    story.append(Spacer(1, 3.2 * cm))
    story.append(P("<b>Compte rendu — Travaux Dirigés n°2</b>",
                   ParagraphStyle("T", parent=C, fontName="DVB", fontSize=20,
                                  leading=26, textColor=BLEU)))
    story.append(Spacer(1, 0.4 * cm))
    story.append(P("Algorithmes évolutionnaires et métaheuristiques",
                   ParagraphStyle("T2", parent=C, fontSize=13, leading=18)))
    story.append(Spacer(1, 1.2 * cm))
    story.append(P("Exercice 2 : problème de transport — recherche taboue<br/>"
                   "Exercice 3 : voyageur de commerce — recherche taboue et recuit simulé",
                   C))
    story.append(Spacer(1, 3.5 * cm))
    info = [["Réalisé par :", "Nom et prénom : ................................................"],
            ["Filière / groupe :", "................................................"],
            ["Langage :", "Python 3"],
            ["Code source :", Paragraph(f'<link href="{GITHUB}" color="blue">{GITHUB}</link>', CELL)],
            ["Année universitaire :", "2026 – 2027"]]
    t = Table(info, colWidths=[4.8 * cm, 11 * cm])
    t.setStyle(TableStyle([("FONT", (0, 0), (0, -1), "DVB", 10),
                           ("FONT", (1, 0), (1, -1), "DV", 10),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 7)]))
    story.append(t)
    story.append(PageBreak())


page_garde()

# ------------------------------------------------ Introduction
story.append(P("1. Introduction", H1))
story.append(P(
    "Ce TD porte sur deux problèmes d'optimisation combinatoire : un problème de "
    "transport (exercice 2) et un problème de voyageur de commerce à 8 villes "
    "(exercice 3). Les deux sont résolus avec des <b>métaheuristiques à solution "
    "unique</b>, qui partent d'une solution et l'améliorent en explorant son "
    "voisinage :"))
story.append(P(
    "• <b>Recherche taboue</b> : à chaque itération on se déplace vers le "
    "<i>meilleur voisin non tabou</i>, même s'il est moins bon que la solution "
    "courante. Une liste taboue (mémoire à court terme) interdit de refaire les "
    "derniers mouvements pendant quelques itérations, ce qui évite de tourner en rond "
    "et permet de sortir des optima locaux. Le <b>critère d'aspiration</b> lève "
    "l'interdiction si le mouvement donne une solution meilleure que la meilleure connue."))
story.append(P(
    "• <b>Recuit simulé</b> : on tire un voisin au hasard ; on l'accepte toujours "
    "s'il améliore la solution, et avec la probabilité exp(−Δ/T) s'il la dégrade "
    "(règle de Metropolis). La température T diminue au fil des itérations : au "
    "début on accepte facilement des dégradations (diversification), à la fin "
    "presque plus (intensification)."))
story.append(P(
    "Tous les programmes ont été écrits en Python 3 sans bibliothèque spécialisée. "
    "Pour valider les résultats, chaque instance étant petite, l'optimum exact a "
    "aussi été calculé par énumération complète."))

# ------------------------------------------------ Exercice 2
story.append(P("2. Exercice 2 — Problème de transport", H1))
story.append(P("2.1 Données", H2))
story.append(tableau([["", "M1", "M2", "M3", "Stock dépôt"],
                      ["D1", "5", "3", "4", "8"],
                      ["D2", "6", "7", "2", "9"],
                      ["Demande", "4", "5", "8", "17 = 17"]],
                     [2.6 * cm, 2 * cm, 2 * cm, 2 * cm, 3 * cm]))
story.append(Spacer(1, 4))
story.append(P(
    "L'offre totale (8 + 9 = 17) est égale à la demande totale (4 + 5 + 8 = 17) : "
    "le problème est <b>équilibré</b>, toutes les contraintes sont donc des égalités. "
    "(Le programme ajoute automatiquement un magasin ou un dépôt fictif de coût nul "
    "si ce n'est pas le cas.)"))

story.append(P("2.2 Modélisation en programme linéaire en nombres entiers", H2))
story.append(P(
    "Variables : x<sub>ij</sub> = nombre de containers envoyés du dépôt D<sub>i</sub> "
    "au magasin M<sub>j</sub>, x<sub>ij</sub> ∈ ℕ."))
story.append(P(
    "Min Z = 5x<sub>11</sub> + 3x<sub>12</sub> + 4x<sub>13</sub> + 6x<sub>21</sub> "
    "+ 7x<sub>22</sub> + 2x<sub>23</sub>", C))
story.append(P(
    "sous : x<sub>11</sub>+x<sub>12</sub>+x<sub>13</sub> = 8 ; "
    "x<sub>21</sub>+x<sub>22</sub>+x<sub>23</sub> = 9 ; "
    "x<sub>11</sub>+x<sub>21</sub> = 4 ; x<sub>12</sub>+x<sub>22</sub> = 5 ; "
    "x<sub>13</sub>+x<sub>23</sub> = 8", C))
story.append(P(
    "<b>Séparation et évaluation (Branch and Bound).</b> Au nœud racine on résout "
    "la relaxation continue (x<sub>ij</sub> ≥ 0 réels). On obtient "
    "x<sub>11</sub>=3, x<sub>12</sub>=5, x<sub>21</sub>=1, x<sub>23</sub>=8 et Z = 52. "
    "Cette solution est déjà entière : la matrice des contraintes d'un problème de "
    "transport est totalement unimodulaire, donc avec des stocks et des demandes "
    "entiers les sommets du polyèdre sont entiers. Aucune séparation n'est "
    "nécessaire, l'arbre se réduit à la racine et la borne 52 est l'optimum."))

story.append(P("2.3 Proposition par recherche taboue", H2))
story.append(P(
    "<b>Codage.</b> Une solution est la matrice X = [x<sub>ij</sub>] (2 × 3)."))
story.append(P(
    "<b>Solution initiale.</b> Règle du coin Nord-Ouest : "
    "X<sub>0</sub> = [[4, 4, 0], [0, 1, 8]], de coût 4·5 + 4·3 + 1·7 + 8·2 = <b>55</b>."))
story.append(P(
    "<b>Voisinage.</b> Pour garder une solution toujours réalisable, on utilise un "
    "mouvement de type « stepping stone » : on choisit deux dépôts i, k et deux "
    "magasins j, l, et on déplace une unité le long du cycle "
    "(i,j)+1, (i,l)−1, (k,l)+1, (k,j)−1. Les sommes en ligne et en colonne ne "
    "changent pas. Un mouvement n'est possible que si les deux cases diminuées "
    "sont ≥ 1."))
story.append(P(
    "<b>Liste taboue.</b> Après un mouvement, on interdit pendant 3 itérations "
    "le mouvement inverse (ré-augmenter les deux cases qu'on vient de diminuer). "
    "<b>Aspiration</b> : un mouvement tabou est autorisé s'il bat la meilleure "
    "solution. <b>Arrêt</b> : 5 itérations consécutives sans amélioration."))

rows = [["It.", "Mouvement (cases +1)", "Solution X", "Coût", "Meilleur"]]
hl = []
for k, (it, mv, c, b) in enumerate(hist2):
    if mv is None:
        txt = "initiale (Nord-Ouest)"
    else:
        i, j, kk, l = mv
        txt = f"D{i+1}M{j+1}, D{kk+1}M{l+1}"
    rows.append([str(it), txt, "", str(c), str(b)])
# reconstruire les solutions pour l'affichage
Xc = ex2.coin_nord_ouest(ex2.STOCKS, ex2.DEMANDES)
rows[1][2] = str(Xc)
for r, (it, mv, c, b) in enumerate(hist2[1:], start=2):
    i, j, k, l = mv
    Xc = [row[:] for row in Xc]
    Xc[i][j] += 1; Xc[i][l] -= 1; Xc[k][l] += 1; Xc[k][j] -= 1
    rows[r][2] = str(Xc)
    if c == c2 and rows[r - 1][4] != str(c):
        hl.append(r)
story.append(KeepTogether([
    tableau(rows, [1.1 * cm, 4.4 * cm, 4.6 * cm, 1.6 * cm, 1.9 * cm], hl_rows=hl),
    P("Tableau 1 — Trace de la recherche taboue (exercice 2)", CAP)]))
story.append(P(
    "Dès la première itération l'algorithme trouve la solution de coût 52. "
    "Ensuite tous les voisins sont moins bons ; comme le retour en arrière est "
    "tabou, l'algorithme accepte des solutions dégradées (55, 58, 61, 64) et "
    "explore une autre région de l'espace, mais ne trouve rien de mieux. Il "
    "s'arrête après 5 itérations sans amélioration."))
story.append(Image("fig_ex2_tabou.png", width=14 * cm, height=14 * 2.6 / 6.2 * cm))
story.append(P("Figure 1 — Évolution du coût (exercice 2)", CAP))

story.append(P("2.4 Résultat", H2))
story.append(KeepTogether([tableau(
    [["", "M1", "M2", "M3", "Total envoyé"],
     ["D1", str(X2[0][0]), str(X2[0][1]), str(X2[0][2]), "8"],
     ["D2", str(X2[1][0]), str(X2[1][1]), str(X2[1][2]), "9"],
     ["Reçu", "4", "5", "8", ""]],
    [2.6 * cm, 2 * cm, 2 * cm, 2 * cm, 3 * cm])]))
story.append(Spacer(1, 4))
story.append(P(
    f"Organisation des livraisons : D1 envoie 3 containers à M1 et 5 à M2 ; "
    f"D2 envoie 1 container à M1 et 8 à M3. "
    f"Coût total = 3·5 + 5·3 + 1·6 + 8·2 = <b>{c2}</b>. "
    f"L'énumération de toutes les solutions entières donne le même optimum "
    f"({c2e}) : la recherche taboue a bien trouvé la solution optimale, la même que "
    f"celle du Branch and Bound."))
story.append(P(
    "<i>Interprétation :</i> D2 est de loin le moins cher pour M3 (coût 2), il "
    "le sert entièrement. D1 est le moins cher pour M2 (3) et le sert entièrement. "
    "M1 est complété avec le reste : 3 depuis D1 (5) et 1 depuis D2 (6)."))

# ------------------------------------------------ Exercice 3
story.append(PageBreak())
story.append(P("3. Exercice 3 — Voyageur de commerce (8 villes)", H1))
story.append(P("3.1 Données et fonction objectif", H2))
mat = [["", *[str(j) for j in range(1, 9)]]]
for i in range(1, 9):
    mat.append([str(i)] + ["–" if i == j else ("∞" if ex3.D[i][j] >= ex3.INF
                                                 else str(ex3.D[i][j]))
                           for j in range(1, 9)])
t = tableau(mat, [1 * cm] * 9)
t.setStyle(TableStyle([("BACKGROUND", (0, 1), (0, -1), GRIS),
                       ("FONT", (0, 1), (0, -1), "DVB", 8.5)]))
row = Table([[t, Image("fig_ex3_graphe.png", width=6 * cm, height=6 * 3.4 / 3.6 * cm)]],
            colWidths=[9.6 * cm, 6.4 * cm])
row.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
story.append(row)
story.append(P("Tableau 2 — Matrice symétrique des distances (∞ = pas de liaison)  |  "
               "Figure 2 — Graphe des liaisons, en rouge le meilleur tour trouvé", CAP))
story.append(P(
    "Les cases « - » de l'énoncé signifient qu'il n'y a pas de route directe. "
    "Dans le programme on leur donne une pénalité INF = 1000 : un tour qui utilise "
    "une telle arête a une longueur > 1000 et n'est jamais retenu. La longueur d'un "
    "tour est la somme des distances entre villes consécutives, retour à la ville 1 "
    "compris. La ville 1 est fixée en tête du tour."))
story.append(P(
    "Solution initiale imposée : 1-2-3-4-5-6-7-8-1, de longueur "
    "14 + 13 + 11 + 11 + 15 + 9 + 13 + 17 = <b>103</b>."))

story.append(P("3.2 Question 1 — Recherche taboue", H2))
story.append(P(
    "<b>Voisinage</b> : échange (swap) de deux villes du tour (sauf la ville 1), "
    "soit C(7,2) = 21 voisins par itération. "
    "<b>Liste taboue</b> : la paire de villes {u, v} qui vient d'être échangée "
    "est taboue pendant 5 itérations. "
    "<b>Aspiration</b> : un échange tabou est accepté s'il donne un tour plus court "
    "que le meilleur connu. "
    "<b>Arrêt</b> : 30 itérations au maximum ou 15 itérations sans amélioration."))
story.append(P(
    "À l'itération 1, tous les voisins de 1-2-3-4-5-6-7-8-1 sont plus longs "
    "(le meilleur, swap(2,3), donne 107) : la solution initiale est un "
    "<b>optimum local</b> pour le voisinage swap. Une descente classique "
    "s'arrêterait ici à 103 ; la recherche taboue, elle, continue en acceptant la "
    "dégradation."))
rows = [["It.", "Swap", "Tour courant", "L", "Meilleur", "Liste taboue"]]
hl = []
prev = None
for (it, tour, L, mv, best, liste) in hist_tb:
    rows.append([str(it), mv, tour, str(L), str(best),
                 Paragraph(" ".join(f"({a},{b})" for a, b in liste) or "∅", CELL)])
    if prev is not None and best < prev:
        hl.append(len(rows) - 1)
    prev = best
story.append(tableau(rows, [0.9 * cm, 1.3 * cm, 3.8 * cm, 1.1 * cm, 1.5 * cm, 6.2 * cm],
                     hl_rows=hl, font=7.8))
story.append(P("Tableau 3 — Trace complète de la recherche taboue "
               "(ligne verte : amélioration du meilleur tour)", CAP))
story.append(P(
    "Les itérations 1 à 10 dégradent la solution (jusqu'à 115) : c'est la phase "
    "où la liste taboue empêche de revenir en arrière et pousse l'exploration. À "
    "l'itération 7, l'algorithme retombe sur 1-8-7-6-5-4-3-2-1, qui est le même "
    "cycle que la solution initiale parcouru dans l'autre sens (longueur 103). "
    "À l'itération 11, swap(7,3) donne <b>1-8-3-7-6-5-4-2-1 de longueur 98</b>. "
    "L'algorithme retrouve 98 à l'itération 20 (1-2-4-5-6-7-3-8-1, c'est le même "
    "cycle à l'envers) et s'arrête après 15 itérations sans amélioration."))
story.append(Image("fig_ex3_tabou.png", width=12.5 * cm, height=12.5 * 2.8 / 6.2 * cm))
story.append(P("Figure 3 — Convergence de la recherche taboue (exercice 3)", CAP))
story.append(P(
    "<b>Influence de la durée taboue</b> (essais réalisés) : avec une durée de 3 "
    "l'optimum 98 n'est atteint qu'à l'itération 22, avec 5 à l'itération 11 et "
    "avec 7 à l'itération 18. Une durée trop courte laisse l'algorithme cycler "
    "autour de l'optimum local 103 ; une durée trop longue interdit trop de "
    "mouvements. La valeur 5 a été retenue."))

story.append(P("3.3 Question 2 — Recuit simulé (5 itérations)", H2))
story.append(P(
    "<b>Voisin</b> : swap de deux villes tirées au hasard (ville 1 fixe). "
    "<b>Acceptation</b> : si Δ = L(voisin) − L(courant) ≤ 0 on accepte ; sinon on "
    "tire r ~ U[0,1] et on accepte si r &lt; p = exp(−Δ/T)."))
story.append(P(
    f"<b>Variation empirique de T.</b> La température initiale est réglée à partir "
    f"des données : on tire 50 voisins aléatoires de la solution initiale et on "
    f"calcule la moyenne des dégradations réalisables, Δ<sub>moy</sub> = "
    f"{delta_moy:.2f}. On veut accepter une telle dégradation avec une probabilité "
    f"de 50 % au départ : exp(−Δ<sub>moy</sub>/T<sub>0</sub>) = 0,5, donc "
    f"T<sub>0</sub> = Δ<sub>moy</sub> / ln 2 ≈ <b>{T0:.2f}</b>. Ensuite T est "
    f"multipliée par α = 0,8 à chaque itération (refroidissement géométrique) : "
    f"T = {T0:.2f} ; {T0*0.8:.2f} ; {T0*0.64:.2f} ; {T0*0.512:.2f} ; "
    f"{T0*0.4096:.2f}. (Graine aléatoire fixée à 18 pour que l'exécution soit "
    f"reproductible.)"))
rows = [["It.", "T", "Swap", "Voisin", "L", "Δ", "p", "r", "Décision", "Courant (L)"]]
for h in hist_rs:
    rows.append([str(h["it"]), f"{h['T']:.2f}", f"({h['swap'][0]},{h['swap'][1]})",
                 h["voisin"], str(h["Lv"]), str(h["delta"]),
                 f"{h['p']:.3f}" if h["p"] > 0.0005 else "≈ 0",
                 "–" if h["r"] is None else f"{h['r']:.3f}",
                 "accepté" if h["accepte"] else "refusé",
                 f"{h['courant']} ({h['Lc']})"])
story.append(tableau(rows, [0.8*cm, 1.1*cm, 1.1*cm, 3.2*cm, 1.0*cm, 1.0*cm,
                            1.1*cm, 1.0*cm, 1.4*cm, 4.4*cm], font=7.2))
story.append(P("Tableau 4 — Les 5 itérations du recuit simulé", CAP))
story.append(P(
    "• It. 1 : swap(2,3) allonge le tour de 4 ; p = exp(−4/10,78) = 0,690 et "
    "r = 0,661 &lt; p, la dégradation est <b>acceptée</b> (T est encore élevée).<br/>"
    "• It. 2 : nouvelle dégradation (Δ = 7) acceptée car r = 0,198 &lt; 0,444.<br/>"
    "• It. 3 et 4 : les voisins utilisent des arêtes inexistantes (Δ ≈ 1000), "
    "p ≈ 0 : refusés.<br/>"
    "• It. 5 : swap(4,2) améliore de 7, accepté sans tirage. Le tour courant "
    "revient à 107."))
story.append(P(
    f"Après 5 itérations, la meilleure solution rencontrée reste la solution initiale "
    f"(<b>103</b>). C'est normal : 5 itérations sont très peu, et environ la moitié "
    f"des swaps aléatoires produisent un tour irréalisable sur ce graphe peu dense. "
    f"Le tableau montre néanmoins bien le mécanisme du recuit : à haute température "
    f"il accepte des dégradations pour explorer. Pour vérification, la même "
    f"méthode lancée plus longtemps (200 paliers × 50 itérations, α = 0,95) trouve "
    f"le tour <b>{ex3.fmt(rc)} de longueur {Lrc}</b>."))

story.append(P("3.4 Vérification et comparaison", H2))
story.append(P(
    f"L'énumération des 7! = 5040 tours possibles donne l'optimum "
    f"<b>{ex3.fmt(opt)} = 14 + 14 + 11 + 15 + 9 + 9 + 9 + 17 = {Lopt}</b>. "
    f"Le tour 1-8-3-7-6-5-4-2-1 trouvé par la recherche taboue est exactement ce "
    f"cycle parcouru dans l'autre sens."))
story.append(tableau(
    [["Méthode", "Paramètres", "Meilleur tour", "Longueur"],
     ["Solution initiale", "—", "1-2-3-4-5-6-7-8-1", "103"],
     ["Recherche taboue", "swap, durée 5, ≤ 30 it.", ex3.fmt(tb), str(Ltb)],
     ["Recuit simulé (5 it.)", f"T0 = {T0:.2f}, α = 0,8", ex3.fmt(rs), str(Lrs)],
     ["Recuit simulé (long)", "10 000 it., α = 0,95", ex3.fmt(rc), str(Lrc)],
     ["Énumération exhaustive", "5040 tours", ex3.fmt(opt), str(Lopt)]],
    [4 * cm, 4.2 * cm, 4.6 * cm, 2 * cm], hl_rows=(2, 4, 5)))
story.append(P("Tableau 5 — Comparaison des résultats (exercice 3)", CAP))

# ------------------------------------------------ Conclusion
story.append(P("4. Conclusion", H1))
story.append(P(
    "Pour le problème de transport, la recherche taboue avec un voisinage en "
    "cycle (stepping stone) trouve en une itération la solution optimale de coût 52, "
    "confirmée par le Branch and Bound (la relaxation linéaire est déjà entière) et "
    "par l'énumération."))
story.append(P(
    "Pour le voyageur de commerce, la solution initiale 1-2-3-4-5-6-7-8-1 (103) "
    "est un optimum local pour le voisinage swap. La recherche taboue réussit à en "
    "sortir grâce à la liste taboue et atteint l'optimum global 98 en 11 itérations. "
    "Le recuit simulé limité à 5 itérations illustre le principe d'acceptation "
    "probabiliste mais ne suffit pas à améliorer la solution ; avec un nombre "
    "d'itérations raisonnable il atteint aussi 98."))
story.append(P(
    "On retient que le choix du voisinage et des paramètres (durée taboue, "
    "température initiale, vitesse de refroidissement) a une forte influence. "
    "Une piste d'amélioration serait d'utiliser un voisinage par insertion "
    "(déplacer une ville ailleurs dans le tour) : un essai montre qu'il trouve 98 "
    "dès la première itération à partir de la solution initiale."))
story.append(P(f'Code source : <link href="{GITHUB}" color="blue">{GITHUB}</link>'))

# ------------------------------------------------ Annexe code
story.append(PageBreak())
story.append(P("Annexe A — exercice2_transport_tabou.py", H1))
story.append(Preformatted(open("exercice2_transport_tabou.py", encoding="utf-8").read(), CODE))
story.append(PageBreak())
story.append(P("Annexe B — exercice3_tsp.py", H1))
story.append(Preformatted(open("exercice3_tsp.py", encoding="utf-8").read(), CODE))


def pied(canvas, doc):
    canvas.saveState()
    canvas.setFont("DV", 8)
    canvas.setFillColor(colors.HexColor("#777777"))
    if doc.page > 1:
        canvas.drawString(2 * cm, 1.2 * cm, "Compte rendu TD2 — Recherche taboue & recuit simulé")
        canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"{doc.page}")
    canvas.restoreState()


doc = SimpleDocTemplate("Compte_rendu_TD2.pdf", pagesize=A4,
                        leftMargin=2 * cm, rightMargin=2 * cm,
                        topMargin=1.8 * cm, bottomMargin=2 * cm,
                        title="Compte rendu TD2 - Recherche taboue et recuit simulé",
                        author="Étudiant FSS")
doc.build(story, onFirstPage=pied, onLaterPages=pied)
print("PDF généré : Compte_rendu_TD2.pdf")
