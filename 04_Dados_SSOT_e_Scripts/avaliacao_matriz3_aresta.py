"""
AVALIAÇÃO DA MATRIZ 3 — POR QUE A ARESTA R0,75 RECEBE POUCO MATERIAL (versão intuitiva)
========================================================================================
Gera a figura `03_Relatorios_e_Documentacao/figuras/aresta_R075_intuicao.png` e a tabela de
números que explicam, sem jargão, por que a ponta arredondada da fenda entrega muito menos
material por milímetro do que o núcleo da chapa.

Três curvas são comparadas, ao longo dos últimos 2 mm da largura:

1. FOLGA LOCAL h(x) — a geometria do R0,75 (o quanto a fenda se fecha);
2. INGÊNUO (h/H) — o que se esperaria se a vazão caísse na mesma proporção da folga;
3. REAL ((h/H)^((2n+1)/n)) — a lei de escoamento de um polímero que se "afina com o
   cisalhamento" (n = 0,32): a vazão cai com a folga elevada a 5,125;
4. MEDIDO — o perfil de vazão por mm calculado no CFD 2D da seção do land.

Uso:  python avaliacao_matriz3_aresta.py
"""

import json
import math
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DIR_DADOS = os.path.dirname(os.path.abspath(__file__))
DIR_FIG = os.path.join(RAIZ, "03_Relatorios_e_Documentacao", "figuras")

H = 1.50          # mm - folga nominal da fenda
R = 0.75          # mm - raio de borda R0,75
MEIA_LARGURA = 37.5
X_C = MEIA_LARGURA - R            # 36,75 mm - onde a fenda começa a fechar
N_PL = 0.32
EXPOENTE = (2 * N_PL + 1) / N_PL  # 5,125


def folga_local(x_mm):
    """Folga da fenda (mm) na posição x, dentro da região do raio de borda."""
    dx = np.clip(np.abs(x_mm) - X_C, 0.0, R)
    return H * np.sqrt(np.maximum(1.0 - (dx / R) ** 2, 0.0))


def capacidade(x_mm):
    """Fração da vazão por mm em relação a uma fenda plana, pela lei do polímero."""
    return (folga_local(x_mm) / H) ** EXPOENTE


def main():
    # --- geometria e lei de escoamento
    x = np.linspace(MEIA_LARGURA - 2.0, MEIA_LARGURA, 4000)
    h = folga_local(x)
    cap = (h / H) ** EXPOENTE
    cap_ingenuo = h / H

    # integral da capacidade na aresta: quanto ela entrega vs. uma fenda plana de mesmo comprimento
    u = np.linspace(0.0, 1.0, 200001)
    fracao_aresta = float(np.trapezoid((1.0 - u ** 2) ** (EXPOENTE / 2.0), u))

    print("=" * 96)
    print("POR QUE A ARESTA R0,75 ENTREGA POUCO — NÚMEROS")
    print("=" * 96)
    print(f"Lei do polímero: vazão por mm ∝ folga^((2n+1)/n) = folga^{EXPOENTE:.3f}   (n = {N_PL})")
    print(f"\n{'posição x (mm)':>15} {'folga (mm)':>12} {'ingênuo (h/H)':>15} {'real ((h/H)^5,125)':>20}")
    for uu in (0.0, 0.25, 0.5, 0.7, 0.8, 0.9, 0.95):
        xx = X_C + R * uu
        print(f"{xx:15.3f} {folga_local(xx):12.3f} {100 * (folga_local(xx) / H):14.1f}% "
              f"{100 * capacidade(xx):19.2f}%")
    print(f"\nA aresta (2 × 0,75 = 1,50 mm de largura, {100 * 1.5 / 75:.0f}% da chapa) entrega apenas")
    print(f"   {100 * fracao_aresta:.1f}% do que entregaria se fosse fenda plana com a MESMA largura.")
    print(f"\nRegra de bolso: 1% de folga a menos -> {100 * (1.01 ** EXPOENTE - 1):.1f}% de vazão a menos;")
    print(f"                10% de folga a menos -> {100 * (1.10 ** EXPOENTE - 1):.1f}% de vazão a menos.")

    # --- perfil medido no CFD (seção do land)
    medido = None
    arq = os.path.join(DIR_DADOS, "avaliacao_matriz_3_secoes.json")
    if os.path.exists(arq):
        with open(arq, encoding="utf-8") as fh:
            dados = json.load(fh)
        sec = next((s for s in dados["secoes"] if abs(s["altura_max_mm"] - 1.5) < 0.02), None)
        if sec:
            xm = np.array(sec["x_bin_mm"])
            qm = np.array(sec["q_perfil"])
            o = np.argsort(xm)
            xm, qm = xm[o], qm[o]
            nucleo = xm <= X_C
            q_ref = float(np.trapezoid(qm[nucleo], xm[nucleo]) / (xm[nucleo].max() - xm[nucleo].min()))
            m = xm >= (MEIA_LARGURA - 2.0)
            medido = (xm[m], qm[m] / q_ref)
            print(f"\nReferência medida (núcleo do land, CFD): q = {q_ref:.1f} mm³/s por mm")
            print("Perfil medido nos últimos 2 mm (normalizado pelo núcleo):")
            for xx, qq in zip(*medido):
                print(f"   x = {xx:6.3f} mm -> {100 * qq:5.1f}% do núcleo")

    # --- figura
    os.makedirs(DIR_FIG, exist_ok=True)
    fig, ax = plt.subplots(figsize=(9.6, 5.2), dpi=160)
    ax.plot(x, 100 * cap_ingenuo, "--", color="#9aa5b1", lw=2.2,
            label="se a vazão caísse igual à folga (ingênuo)")
    ax.plot(x, 100 * cap, "-", color="#c0392b", lw=3.0,
            label=f"real: vazão ∝ folga$^{{{EXPOENTE:.3f}}}$ (n = {N_PL})")
    if medido is not None:
        ax.plot(medido[0], 100 * medido[1], "o", color="#1f3d7a", ms=8, zorder=5,
                label="medido no CFD 2D (seção do land)")
    ax.axvspan(X_C, MEIA_LARGURA, color="#f2f4f7", zorder=0)
    ax.axvline(X_C, color="#5b6672", lw=1.0, ls="--", alpha=0.7)
    ax.text(X_C + 0.03, 78, "começa o raio R0,75\n(folga aqui ainda é 1,50 mm)",
            fontsize=9, color="#5b6672", va="top")
    if medido is not None:
        i = int(np.argmin(np.abs(medido[0] - X_C)))
        ax.annotate("folga 100%, mas vazão já em 56%:\n"
                    "o canto/parede da ponta freia o fundido",
                    xy=(medido[0][i], 100 * medido[1][i]), xytext=(35.6, 26),
                    fontsize=9, color="#1f3d7a", ha="left",
                    arrowprops=dict(arrowstyle="->", color="#1f3d7a", lw=1.4))
    ax.set_xlim(MEIA_LARGURA - 2.0, MEIA_LARGURA)
    ax.set_ylim(0, 105)
    ax.set_xlabel("posição na largura da chapa  x  [mm]   (0 = núcleo plano, 37,5 = ponta)")
    ax.set_ylabel("vazão local por mm  [% do núcleo plano]")
    ax.set_title("Por que a aresta recebe pouco material: a folga manda, mas elevada a 5,125\n"
                 "Matriz 3 (Jonatha) — fenda 75,00 × 1,50 mm com R0,75 nas pontas",
                 fontsize=11.5)
    ax.grid(alpha=0.25)
    ax.legend(loc="lower left", fontsize=9.5, framealpha=0.95)
    ax2 = ax.twinx()
    ax2.plot(x, h, ":", color="#2e7d32", lw=1.8)
    ax2.set_ylabel("folga local da fenda  [mm]", color="#2e7d32")
    ax2.tick_params(axis="y", colors="#2e7d32")
    ax2.set_ylim(0, 1.7)
    fig.tight_layout()
    destino = os.path.join(DIR_FIG, "aresta_R075_intuicao.png")
    fig.savefig(destino)
    print(f"\nFigura salva em {os.path.relpath(destino, RAIZ)}")


if __name__ == "__main__":
    main()
