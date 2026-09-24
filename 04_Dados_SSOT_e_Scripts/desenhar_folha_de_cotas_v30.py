#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Folha de 1 pagina (A4 paisagem) para mandar JUNTO com os 3 STEP. Nao substitui o STEP.

Quatro blocos, nada alem do que decide aceite:
  1. meia-secao no plano da ABERTURA (aqui aparece o funil/cone interno);
  2. DETALHE A ampliado do fim do canal, onde a abertura 1,500 mm fica clara;
  3. face de saida com as duas dimensoes da fenda;
  4. regras em quatro colunas curtas.
Nenhum numero e digitado neste arquivo: tudo vem de pacote_usinagem.json (medicao no STEP).
Uso:
  python3 desenhar_folha_de_cotas_v30.py
  PACOTE=08_Pacote_Usinagem_v29 ARQ_FOLHA=FOLHA_DE_COTAS_V29 python3 desenhar_folha_de_cotas_v30.py
So precisa de matplotlib (nada e re-medido aqui).
"""
import io, json, math, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly, Rectangle as MRect

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACOTE = os.environ.get("PACOTE", "08_Pacote_Usinagem_v30")
ARQ = os.environ.get("ARQ_FOLHA", "FOLHA_DE_COTAS_V30")
VERM, AZUL, VERDE, MARROM, CINZA = "#b02418", "#0b4a86", "#0d7a3f", "#7a3d00", "#555555"

# caixas [x, y, larg, alt] em fracao da folha (A4 paisagem)
CX_MAIN = [0.020, 0.300, 0.460, 0.470]
CX_DET = [0.500, 0.425, 0.300, 0.345]
CX_FACE = [0.815, 0.420, 0.180, 0.350]
CX_REGRAS = [0.020, 0.040, 0.972, 0.235]

d = json.load(io.open(os.path.join(RAIZ, PACOTE, "pacote_usinagem.json"), encoding="utf-8"))
m, alv = d["medido"], d["alvo_do_contrato"]
fd, bs = m["fenda_no_land"], m["boca_saida"]


REV = PACOTE.rsplit("_", 1)[-1].lstrip("v")


def br(x, dec=2):
    return ("%.*f" % (dec, float(x))).replace(".", ",")


def quebra(txt, larg):
    out, atual = [], ""
    for pal in txt.split(" "):
        if len(atual) + len(pal) + 1 > larg:
            if atual:
                out.append(atual)
            atual = pal
        else:
            atual = (atual + " " + pal).strip()
    if atual:
        out.append(atual)
    return out


def main():
    est = sorted(m["estagios_medidos"], key=lambda e: e["z"][0])
    L, z0, zf = m["comprimento_mm"], m["z_min"], m["z_max"]
    r = [e["D"] / 2.0 for e in est]
    zb = [e["z"][0] for e in est] + [zf]
    land, chan, rborda = alv["land"], alv["chanfro"], alv["raio_borda"]
    a_fd, w_fd = fd["abertura_mm"], fd["largura_mm"] / 2.0
    z_land1 = zf - chan
    z_land0 = z_land1 - land
    R_in = alv["boca_entrada"] / 2.0
    a_bs, w_bs = bs["abertura_mm"], bs["largura_mm"] / 2.0
    y_f = (z_land0 + z_land1) / 2.0

    aco = [(0, z0), (r[0], z0), (r[0], zb[1]), (r[1], zb[1]), (r[1], zb[2]), (r[2], zb[2]), (r[2], zf), (0, zf)]
    # funil: Ø75,60 na entrada (Z 0,00) ate a fenda no inicio do land. A parede real e BSpline
    # (medida no STEP); o que se desenha aqui e a forma entre as secoes medidas.
    canal = [(0, z0), (R_in, z0), (a_fd / 2.0, z_land0), (a_fd / 2.0, z_land1), (a_bs / 2.0, zf), (0, zf)]

    fig = plt.figure(figsize=(11.69, 8.27), dpi=150)                      # A4 paisagem
    fig.patch.set_facecolor("white")

    # ------------------------------------------------------------ 1. MEIA-SECAO
    ax = fig.add_axes(CX_MAIN)
    ax.add_patch(MPoly(aco, closed=True, facecolor="#e9ecf2", edgecolor="#111111", lw=1.8))
    ax.add_patch(MPoly(canal, closed=True, facecolor="#ffffff", edgecolor=VERM, lw=1.6))
    ax.plot([a_fd / 2.0, a_fd / 2.0], [z_land0, z_land1], color=VERM, lw=3.4)
    ax.plot([0, 0], [z0 - 3, zf + 3], color="#aaaaaa", lw=0.7, ls="--")
    ax.add_patch(MRect((-3.5, z_land0 - 3.5), 22.0, (zf + 1.0) - (z_land0 - 3.5), fill=False,
                       edgecolor=VERDE, lw=1.1, ls="--"))
    ax.text(-3.5, zf + 2.0, "DETALHE A — ampliado ao lado →", fontsize=8.6, color=VERDE,
            ha="left", va="bottom", fontweight="bold")
    for i in range(3):
        yc = (zb[i] + zb[i + 1]) / 2.0
        ax.annotate("", xy=(r[i], yc), xytext=(r[0] + 17, yc),
                    arrowprops=dict(arrowstyle="<->", color=AZUL, lw=1.2))
        ax.text(r[0] + 18, yc, "Ø%s  ±0,5" % br(2 * r[i]), fontsize=11, color=AZUL,
                va="center", ha="left", fontweight="bold")
    ax.annotate("", xy=(r[0] + 5, z0), xytext=(r[0] + 5, zf),
                arrowprops=dict(arrowstyle="<->", color="#111111", lw=1.3))
    ax.text(r[0] + 6.5, (z0 + zf) / 2.0, "comprimento\n%s mm  ±0,5" % br(L),
            fontsize=11, ha="left", va="center", fontweight="bold", linespacing=1.15)
    ax.annotate("", xy=(-R_in, z0 - 6.0), xytext=(R_in, z0 - 6.0),
                arrowprops=dict(arrowstyle="<->", color=MARROM, lw=1.0))
    ax.text(0.0, z0 + 5.5, "boca de entrada Ø%s\n+0,05 / −0,00 — não alargar" % br(2 * R_in),
            fontsize=8.6, ha="center", va="center", color=MARROM, linespacing=1.3)
    # ponto sobre a parede do funil (a recta que liga a boca de entrada ao inicio do land)
    y_fun = 0.62 * z_land0
    x_fun = a_fd / 2.0 + (R_in - a_fd / 2.0) * (z_land0 - y_fun) / z_land0
    ax.annotate("funil interno\n(o cone que fecha\naté a fenda)",
                xy=(x_fun, y_fun), xytext=(-40.0, 0.74 * z_land0), fontsize=8.6,
                ha="left", va="center", color="#111111", linespacing=1.25,
                arrowprops=dict(arrowstyle="->", color="#111111", lw=0.9))
    MAIN_X = (-42.0, 116.0)
    MAIN_Y = (z0 - 12.0, zf + 6.0)
    ax.set_xlim(*MAIN_X)
    ax.set_ylim(*MAIN_Y)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(u"MATRIZ JONATHA v27.0 · rev. %s — MEIA-SEÇÃO NO PLANO DA ABERTURA\n"
                 u"o funil fecha de Ø%s (Z 0,00) até a fenda %s × %s mm no land (Z %s) — "
                 u"o perfil exato é a superfície BSpline do STEP\n"
                 u"O STEP é a definição; esta folha é a régua de aceitação."
                 % (REV, br(2 * R_in), br(2 * w_fd), br(a_fd, 3), br(z_land0)),
                 fontsize=10.5, loc="left", fontweight="bold", pad=12, linespacing=1.5)

    # ------------------------------------------------------------ 2. DETALHE A (zoom no canto)
    ax4 = fig.add_axes(CX_DET)
    ax4.add_patch(MPoly(aco, closed=True, facecolor="#e9ecf2", edgecolor="#111111", lw=1.9))
    ax4.add_patch(MPoly(canal, closed=True, facecolor="#ffffff", edgecolor=VERM, lw=1.9))
    ax4.plot([a_fd / 2.0, a_fd / 2.0], [z_land0, z_land1], color=VERM, lw=3.6)
    ax4.plot([0, 0], [z_land0 - 13, zf + 0.6], color="#bbbbbb", lw=0.6, ls="--")
    DET_X = (-13.5, 13.5)
    DET_Y = (z_land0 - 13.0, zf + 8.0)
    ax4.set_xlim(*DET_X)
    ax4.set_ylim(*DET_Y)
    # a abertura da fenda, com linhas de chamada
    ax4.plot([DET_X[0] + 3.0, -3.1], [zf + 3.0, y_f + a_fd / 2.0 + 0.5], color=VERM, lw=0.8, ls=":")
    ax4.annotate("", xy=(-2.6, y_f - a_fd / 2.0), xytext=(-2.6, y_f + a_fd / 2.0),
                 arrowprops=dict(arrowstyle="<->", color=VERM, lw=2.4))
    ax4.plot([-2.6, a_fd / 2.0 + 0.3], [y_f - a_fd / 2.0] * 2, color=VERM, lw=0.9, ls=":")
    ax4.plot([-2.6, a_fd / 2.0 + 0.3], [y_f + a_fd / 2.0] * 2, color=VERM, lw=0.9, ls=":")
    ax4.text(DET_X[0] + 0.3, zf + 5.4, "ABERTURA DA FENDA\n%s mm  \n+0,010 / −0,000" % br(a_fd, 3),
             fontsize=10.0, color=VERM, ha="left", va="center", fontweight="bold", linespacing=1.25)
    ax4.annotate("", xy=(4.6, z_land0), xytext=(4.6, z_land1),
                 arrowprops=dict(arrowstyle="<->", color=VERDE, lw=1.3))
    ax4.plot([a_fd / 2.0 + 0.3, 4.6], [z_land0] * 2, color=VERDE, lw=0.8, ls=":")
    ax4.plot([a_fd / 2.0 + 0.3, 4.6], [z_land1] * 2, color=VERDE, lw=0.8, ls=":")
    ax4.text(5.2, y_f, "land\n%s ±0,05" % br(land), fontsize=9.0, color=VERDE,
             ha="left", va="center", fontweight="bold", linespacing=1.2)
    ax4.set_aspect("equal")
    ax4.axis("off")
    # fator de ampliado real (unidades/mm por polegada de caixa, com o aspect "equal")
    in_por_un_main = (CX_MAIN[2] * 11.69) / (MAIN_X[1] - MAIN_X[0])
    in_por_un_det = (CX_DET[2] * 11.69) / (DET_X[1] - DET_X[0])
    ax4.set_title("DETALHE A — fim do canal, ≈ %d×" % round(in_por_un_det / in_por_un_main),
                  fontsize=10.5, loc="left", fontweight="bold", pad=8)
    cap = ("land %s ±0,05: a parede paralela que calibra a espessura · chanfro %s × 45° na face de saída · "
           "R %s nas duas pontas da fenda, aresta viva (sem raio na quina) · fenda aberta a fio EDM depois do "
           "tratamento térmico, com a abertura medida antes e depois" % (br(land), br(chan), br(rborda)))
    capls = quebra(cap, 92)
    fig.text(CX_DET[0], CX_DET[1] - 0.012 - 0.011 * (len(capls) - 1), "\n".join(capls),
             fontsize=7.8, color="#111111", ha="left", va="bottom", linespacing=1.45)
    if CX_DET[1] - 0.012 - 0.011 * (len(capls) - 1) < 0.300:
        raise SystemExit("a legenda do detalhe A desceu demais (%d linhas)" % len(capls))

    # ------------------------------------------------------------ 3. FACE DE SAIDA
    ax2 = fig.add_axes(CX_FACE)
    th = [t / 120.0 for t in range(121)]
    ax2.plot([r[2] * math.cos(2 * math.pi * t) for t in th],
             [r[2] * math.sin(2 * math.pi * t) for t in th], color="#111111", lw=1.9)
    ax2.add_patch(MPoly([(-w_bs, -a_bs / 2), (w_bs, -a_bs / 2), (w_bs, a_bs / 2), (-w_bs, a_bs / 2)],
                        closed=True, facecolor="#ffffff", edgecolor="#111111", lw=1.1))
    ax2.add_patch(MPoly([(-w_fd, -a_fd / 2), (w_fd, -a_fd / 2), (w_fd, a_fd / 2), (-w_fd, a_fd / 2)],
                        closed=True, facecolor="#ffd9c2", edgecolor=VERM, lw=2.2))
    ax2.annotate("", xy=(0, -a_fd / 2 - 9), xytext=(0, a_fd / 2 + 9),
                 arrowprops=dict(arrowstyle="<->", color=VERM, lw=2.0))
    ax2.text(1.5, a_fd / 2 + 11, "abertura\n%s mm" % br(a_fd, 3), fontsize=9.5, color=VERM,
             ha="center", va="bottom", fontweight="bold", linespacing=1.15)
    ax2.annotate("", xy=(-w_fd, -a_fd / 2 - 5.5), xytext=(w_fd, -a_fd / 2 - 5.5),
                 arrowprops=dict(arrowstyle="<->", color=VERM, lw=1.5))
    ax2.text(0, -a_fd / 2 - 12.0, "largura %s ±0,05" % br(2 * w_fd), fontsize=9.0, color=VERM,
             ha="center", va="top", fontweight="bold")
    ax2.text(0, -a_fd / 2 - 22.0, "área %s mm²  ±0,5 %%\nprojetor de perfil ou CMM"
             % br(fd["area_mm2"], 4), fontsize=7.4, ha="center", va="top", color=CINZA, linespacing=1.25)
    ax2.set_xlim(-48, 48)
    ax2.set_ylim(-56, 48)
    ax2.set_aspect("equal")
    ax2.axis("off")
    ax2.set_title("face de saída (Z %s)\no que o produto vê" % br(zf), fontsize=9.4,
                  loc="center", fontweight="bold", pad=8, linespacing=1.25)

    # ------------------------------------------------------------ 4. REGRAS
    ax3 = fig.add_axes(CX_REGRAS)
    ax3.axis("off")
    ax3.set_xlim(0, 1)
    ax3.set_ylim(0, 1)
    col = [
        [("AÇO E DUREZA", True),
         ("1045 forjado, fibra no eixo. Corpo revenido 30–36 HRC. Land 55–60 HRC por indução "
          "(0,6–1,0 mm) ou nitretação a plasma 600–700 HV0,2 — escolha da fábrica, declarada no "
          "relatório. Sem PVD, sem DLC: 10 µm de revestimento mudam a espessura do produto.", False)],
        [("ORDEM (não inverter)", True),
         ("T.T. do corpo → retífica do land → fio EDM do canal pela boca de Ø%s (um lado só) → "
          "remover camada REC ≥ 0,02 mm → tratamento de superfície → medição final. Medir a abertura "
          "ANTES e DEPOIS do tratamento: 8–18 µm de camada comem 0,016–0,036 mm da tolerância de "
          "0,010; se fechar abaixo de %s mm, passar o fio de novo." % (br(2 * R_in), br(a_fd, 3)), False)],
        [("PROIBIDO", True),
         ("Flange, furo de fixação, rosca, pino e linha de partição — a peça é 1 sólido e o aperto é "
          "pelo collete EX-031 e pelo degrau do furo do cabeçote (elemento de aperto só no estoque, "
          "fora do envelope final). Não alargar a boca de entrada Ø%s. Não acertar a fenda com raio na "
          "quina nem com polimento transversal." % br(2 * R_in), False)],
        [("ACEITAÇÃO", True),
         ("Comprimento %s ±0,5 com a face de saída ralada no fim, faceada ao nariz do EX-031 "
          "(protrusão 0,00). Coaxialidade Ø0,02 nos 3 estágios (datum A = Ø%s). Face de saída: "
          "planeza 0,01 e perpendicularidade 0,01 em A. Rebarba ≤ 0,1 × 45°. Marcação a laser na "
          "face traseira. Certificado EN 10204 3.1 + relatório dimensional das cotas desta folha."
          % (br(L), br(2 * r[0])), False)],
    ]
    linhas_max, sobra = 0, []
    for j, bloco in enumerate(col):
        x0 = j * 0.251
        y = 1.0
        for txt, tt in bloco:
            if tt:
                ax3.text(x0, y, txt, fontsize=9.2, fontweight="bold", va="top", ha="left", color=AZUL)
                y -= 0.108
            else:
                ls = quebra(txt, 47)
                for ln in ls:
                    ax3.text(x0, y, ln, fontsize=7.4, va="top", ha="left", color="#111111")
                    y -= 0.104
                linhas_max = max(linhas_max, len(ls) + 1)
        sobra.append(round(y, 3))
    for j in range(1, 4):
        ax3.plot([j * 0.251 - 0.011, j * 0.251 - 0.011], [-0.02, 1.0], color="#d5d8de", lw=0.8)
    if min(sobra) < -0.02:
        raise SystemExit("regras nao cabem na folha: sobra por coluna = %s" % sobra)
    fig.text(CX_REGRAS[0], CX_REGRAS[1] + CX_REGRAS[3] + 0.008,
             "REGRAS DA PEÇA — valem tanto quanto as cotas", fontsize=10.5,
             fontweight="bold", va="bottom", ha="left")

    peca = os.path.basename(m["arquivo"])
    fig.text(CX_MAIN[0], 0.012, u"Folha gerada por 04_Dados_SSOT_e_Scripts/desenhar_folha_de_cotas_v30.py a "
                                u"partir de %s/pacote_usinagem.json — cada número é medição no STEP "
                                u"(seções de 0,02 mm). Modelo 3D/%s (%s faces, %s sólido, BRep válido) · "
                                u"volume do canal %s mm³ · aço %s mm³ = %s kg · se o desenho e o STEP "
                                u"discordarem, vale o STEP."
             % (PACOTE, peca, m["faces"], m["solidos"], br(m["volume_canal_mm3"]),
                br(m["volume_aco_mm3"], 1), br(m["massa_kg"], 4)),
             fontsize=6.6, color=CINZA, va="bottom")

    destino = os.path.join(RAIZ, PACOTE, ARQ)
    fig.savefig(destino + ".pdf", facecolor="white")
    fig.savefig(destino + ".png", facecolor="white", dpi=150)
    plt.close(fig)
    print("ok:", destino + ".pdf", os.path.getsize(destino + ".pdf"), "bytes · regras:",
          "máx %d linhas por coluna" % linhas_max, "· sobra", sobra, "· legenda do detalhe",
          len(capls), "linhas")


if __name__ == "__main__":
    main()
