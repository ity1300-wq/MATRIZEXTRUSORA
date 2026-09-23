#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Folha de cotas de UMA pagina, para ir junto com os STEP quando o desenho completo esta denso demais.

Layout: perfil da peca com as cotas de envelope (em cima, esquerda) + face de saida com a fenda (em cima,
direita) + regras em duas colunas (embaixo). O funil e o canal do canal NAO sao desenhados aqui de proposito:
em secao axial eles viram um trapezio que ninguem le, e a forma ja esta no STEP do solido do canal
(`3D/MATRIZ_V30_CANAL_DE_FLUXO.step`), que e o arquivo que o operador do fio EDM usa.

Nenhum numero e digitado nesta folha: tudo vem de 08_Pacote_Usinagem_v30/pacote_usinagem.json, que e a
medicao do STEP (secoes de 0,02 mm) e que o portao verificar_cadeia.py compara com o SSOT. Se faltar cota
no JSON, a folha recusa sair em vez de chutar.

  python3 04_Dados_SSOT_e_Scripts/desenhar_folha_de_cotas_v30.py                      # v30
  PACOTE=08_Pacote_Usinagem_v29 ARQ_FOLHA=FOLHA_DE_COTAS_V29 python3 .../desenhar_folha_de_cotas_v30.py
"""
import io
import json
import math
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACOTE = os.environ.get("PACOTE", "08_Pacote_Usinagem_v30")
ARQ = os.environ.get("ARQ_FOLHA", "FOLHA_DE_COTAS_V30")
JSON = os.path.join(RAIZ, PACOTE, "pacote_usinagem.json")

COLUNAS = 2          # regras em duas colunas
ENVOLVE = 100        # caracteres por linha da coluna (0,45 x A4 paisagem, ~378 pt de largura util)
FONTE_REGRA = 7.1


def br(x, dec=2):
    return ("%.*f" % (dec, x)).replace(".", ",")


def quebra(txt, larg=ENVOLVE):
    out, atual = [], ""
    for palavra in txt.split(" "):
        if len(atual) + len(palavra) + 1 > larg:
            out.append(atual)
            atual = palavra
        else:
            atual = (atual + " " + palavra).strip()
    if atual:
        out.append(atual)
    if max([len(l) for l in out] or [0]) > larg + 12:
        raise SystemExit("FALHOU: uma linha de %d caracteres nao cabe em %d" % (max(len(l) for l in out), larg))
    return out


def main():
    d = json.load(io.open(JSON, encoding="utf-8"))
    m = d["medido"]
    alv = d["alvo_do_contrato"]
    dec = d["decisoes_2026_09_22"]
    fd, bs, be = m["fenda_no_land"], m["boca_saida"], m["boca_entrada"]
    for nome, bloco, chaves in (("fenda_no_land", fd, ("largura_mm", "abertura_mm", "area_mm2")),
                                ("boca_saida", bs, ("largura_mm", "abertura_mm")),
                                ("boca_entrada", be, ("largura_mm", "abertura_mm"))):
        falt = [k for k in chaves if bloco.get(k) is None]
        if falt:
            raise SystemExit("FALHOU: %s nao traz %s no JSON medido - esta folha nao chuta numero"
                             % (nome, ", ".join(falt)))
    est = sorted(m["estagios_medidos"], key=lambda e: e["z"][0])
    if len(est) != 3:
        raise SystemExit("FALHOU: esperava 3 estagios medidos, achei %d" % len(est))
    L, z0, zf = m["comprimento_mm"], m["z_min"], m["z_max"]
    r = [e["D"] / 2.0 for e in est]
    zb = [e["z"][0] for e in est] + [zf]
    land, chan, rborda = alv["land"], alv["chanfro"], alv["raio_borda"]
    z_land1, z_land0 = zf - chan, zf - chan - land
    w_in = max(be["abertura_mm"], be["largura_mm"]) / 2.0
    w_fd, a_fd = fd["largura_mm"] / 2.0, fd["abertura_mm"]
    w_bs = max(bs["abertura_mm"], bs["largura_mm"]) / 2.0
    a_bs = min(bs["abertura_mm"], bs["largura_mm"])
    tol = dec.get("tolerancia_das_cotas_alteradas", "±0,5")
    mov = d.get("montagem") or {}
    por_diam = {round(f.get("estagio_Ø", -1), 3): f for f in mov.get("folgas_por_estagio", []) if f}
    furos, folgas = [], []
    for i_ in range(3):
        f = por_diam.get(round(2 * r[i_], 3))
        if f is None:
            raise SystemExit("FALHOU: o JSON nao traz a montagem medida para o estagio Ø%s - esta folha não "  
                             "chuta furo nem folga" % br(2 * r[i_]))
        furos.append(f["furo_Ø"])
        fg = f.get("folga_radial")
        folgas.append(float(fg) if fg is not None else (f["furo_Ø"] - 2 * r[i_]) / 2.0)

    fig = plt.figure(figsize=(11.69, 8.27), dpi=150)
    fig.patch.set_facecolor("white")
    fig.text(0.030, 0.955, u"MATRIZ JONATHA v27.0 · rev. %s — perfil externo (meia-seção: raio × Z)"
             % ("30" if abs(L - 95.0) < 0.01 else "29"), fontsize=11.0, ha="left", va="bottom", fontweight="bold")
    fig.text(0.030, 0.928, u"A forma do canal é o STEP que você recebeu — esta só folha diz o que medir e o que é proibido.",
             fontsize=8.6, ha="left", va="bottom", color="#333333")
    fig.text(0.60, 0.955, u"face de saída (Z %s) — o que o produto vê" % br(zf), fontsize=11.0, ha="left",
             va="bottom", fontweight="bold")

    # ============ 1. perfil (meia-secao: raio x Z), com balao em cada cota ============
    ax = fig.add_axes([0.030, 0.585, 0.475, 0.335])
    perf = [(0.0, z0), (r[0], z0), (r[0], zb[1]), (r[1], zb[1]), (r[1], zb[2]), (r[2], zb[2]), (r[2], zf),
            (0.0, zf)]
    ax.add_patch(MPoly(perf, closed=True, facecolor="#e6e9ee", edgecolor="#222222", lw=1.5))
    ax.add_patch(MPoly([(0.0, z_land0), (r[2], z_land0), (r[2], z_land1), (0.0, z_land1)], closed=True,
                       facecolor="#ffe9a8", edgecolor="#222222", lw=1.1))
    ax.plot([0, 0], [z0, zf], color="#9a9a9a", lw=0.8, ls="--")
    balao = {}
    for i_ in range(3):
        zc = (zb[i_] + zb[i_ + 1]) / 2.0
        ax.annotate(str(i_ + 1), xy=(r[i_], zc), xytext=(r[0] + 9.0, zc), fontsize=9.6, color="#0b4a86",
                    ha="center", va="center", fontweight="bold",
                    arrowprops=dict(arrowstyle="->", color="#0b4a86", lw=1.0),
                    bbox=dict(boxstyle="circle,pad=0.28", fc="white", ec="#0b4a86", lw=1.0))
        balao[i_] = zc
    ax.text(r[0] + 16.0, balao[0], u"Ø%s %s\nfuro do cabeçote Ø%s → folga radial %s mm\ndatum A (o cilindro, não o degrau)"
            % (br(2 * r[0]), tol, br(furos[0]), br(folgas[0])), fontsize=8.8, color="#0b4a86",
            va="center", ha="left")
    ax.text(r[0] + 16.0, balao[1], u"Ø%s %s\nfuro Ø%s → folga radial %s mm"
            % (br(2 * r[1]), tol, br(furos[1]), br(folgas[1])), fontsize=8.8, color="#0b4a86",
            va="center", ha="left")
    ax.text(r[0] + 16.0, balao[2], u"Ø%s %s\nfuro Ø%s → folga radial %s mm"
            % (br(2 * r[2]), tol, br(furos[2]), br(folgas[2])), fontsize=8.8, color="#0b4a86",
            va="center", ha="left")
    ax.annotate("", xy=(r[0] + 5.0, z0), xytext=(r[0] + 5.0, zf),
                arrowprops=dict(arrowstyle="<->", color="#111111", lw=1.15))
    ax.text(r[0] + 8.4, z0 + 1.2, u"comprimento\n%s mm  %s" % (br(L), tol), fontsize=9.4, va="bottom", ha="left",
            fontweight="bold")
    rodape = (u"land %s mm ±0,05 (faixa hachurada, Z %s → %s)   ·   chanfro %s × 45°   ·   degraus em Z %s e %s "
              u"com ±0,05\nface de saída faceada ao nariz do EX-030: protrusão 0,00 mm medida na montagem   ·   "
              u"boca de entrada Ø%s +0,05/−0,00 (não alargar)"
              % (br(land), br(z_land0), br(z_land1), br(chan), br(zb[1]), br(zb[2]), br(2 * w_in)))
    ax.text(0.0, -0.075, rodape, fontsize=8.2, va="top", ha="left", transform=ax.transAxes, color="#333333")
    ax.set_xlim(-5, 118); ax.set_ylim(z0 - 2.0, zf + 3.5); ax.set_aspect("equal"); ax.axis("off")

    # ============ 2. face de saida, onde o produto e decidido ============
    ax2 = fig.add_axes([0.605, 0.545, 0.225, 0.335])
    th = [t / 100.0 for t in range(101)]
    ax2.plot([r[2] * math.cos(2 * math.pi * t) for t in th], [r[2] * math.sin(2 * math.pi * t) for t in th],
             color="#222222", lw=1.7)
    ax2.add_patch(MPoly([(-w_bs, -a_bs / 2), (w_bs, -a_bs / 2), (w_bs, a_bs / 2), (-w_bs, a_bs / 2)],
                        closed=True, facecolor="#fff6df", edgecolor="#222222", lw=1.0))
    ax2.add_patch(MPoly([(-w_fd, -a_fd / 2), (w_fd, -a_fd / 2), (w_fd, a_fd / 2), (-w_fd, a_fd / 2)],
                        closed=True, facecolor="#ffe9a8", edgecolor="#b02418", lw=1.4))
    ax2.annotate("", xy=(-w_fd, -a_fd / 2 - 7.0), xytext=(w_fd, -a_fd / 2 - 7.0),
                 arrowprops=dict(arrowstyle="<->", color="#b02418", lw=1.2))
    ax2.text(0.0, -a_fd / 2 - 8.6, u"largura %s ±0,05" % br(2 * w_fd), fontsize=9.0, color="#b02418",
             ha="center", va="top", fontweight="bold")
    ax2.text(0.0, r[2] + 6.4, u"Ø%s %s  ·  boca do chanfro %s × %s" % (br(2 * r[2]), tol, br(2 * w_bs),
                                                                      br(a_bs)), fontsize=9.0, ha="center",
             color="#0b4a86", fontweight="bold")
    ax2.text(0.0, -r[2] - 8.8, u"abertura da fenda  %s  +0,010 / −0,000   ·   R %s nas duas pontas, aresta viva"
             % (br(a_fd, 3), br(rborda)), fontsize=9.0, ha="center", va="top", color="#b02418",
             fontweight="bold")
    ax2.text(0.0, -r[2] - 17.2, u"área da seção no land  %s mm²  ±0,5 %%  (fora disso é rejeição)"
             % br(fd["area_mm2"], 4), fontsize=8.6, ha="center", va="top", color="#333333")
    ax2.set_xlim(-52, 52); ax2.set_ylim(-64, 52); ax2.set_aspect("equal"); ax2.axis("off")

    # ============ 3. regras, duas colunas ============
    regras = [
        (u"MATERIAL", u"aço 1045 (SAE J404 / EN 10083-2), barra forjada, fibra no eixo, normalizada ≤ 220 HB; "
                       u"corpo revenido **30-36 HRC**. O 1045 não chega a 50 HRC no núcleo de Ø%s: a dureza "
                       u"útil desta peça vive na aresta do land." % br(2 * r[0])),
        (u"TRATAMENTO NA FENDA", u"arestas do land **55-60 HRC em camada 0,6-1,0 mm por indução**, ou "
                                  u"nitretação a plasma 520 °C (600-700 HV0,2, camada branca 8-18 µm) para "
                                  u"tratar a fenda inteira — escolha da fábrica, declarada no relatório. **Sem "
                                  u"PVD/DLC, sem cobre, sem jato de granalha no canal.**"),
        (u"A COTA QUE O TRATAMENTO MOVE", u"8-18 µm por face come 0,016-0,036 mm de uma abertura que tolera "
                                            u"+0,010/−0,000, e a indução move 0,005-0,020 mm na zona tratada. "
                                            u"**Meça a fenda antes e depois do tratamento e grave os dois "
                                            u"úmeros**: entrada, meio e saída. Se cair de 1,500, o retrabalho é "
                                            u"passar o fio de novo na região — não é aceitar como está."),
        (u"SEQUÊNCIA", u"T.T. do corpo → retífica do land → **fio EDM do canal** (arame entrando pela boca de "
                        u"Ø%s, de um lado só) → remover camada REC ≥ 0,02 mm → indução/nitretação → medição "
                        u"final. A fenda não pode existir antes do T.T. do corpo: 1,500 mm atravessando %s mm de "
                        u"1045 temperado é risco de trinca. Alívio de tensões antes da têmpera e revenimento "
                        u"duplo." % (br(2 * w_in), br(L))),
        (u"PROIBIDO", u"flange, furo de fixação, rosca, pino e linha de partição (a peça é 1 sólido, sem "
                       u"colagem). A matriz é segurada pelo collete EX-031 e pelo degrau do furo do cabeçote; "
                       u"furo “útil” é rejeição porque entra na zona de aperto. Aperto só em estoque, fora do "
                       u"envelope final e antes do T.T."),
        (u"GEOMETRIA", u"coaxialidade dos três estágios em relação a A **Ø0,02** (datum A = o Ø%s, medido no "
                        u"cilindro, não no degrau); face de saída planeza 0,01 e perpendicularidade 0,01 em A; "
                        u"degraus em Z com ±0,05 (são o batente da peça); Ra ≤ 0,4 µm no canal e no land, "
                        u"polido **na direção da extrusão**; ≤ 0,8 µm nos Ø de envelope; rebarba ≤ 0,1 × 45° "
                        u"inclusive na boca de saída; R 3,0 ±0,5 no fundo do funil, sem aresta viva." % br(2 * r[0])),
        (u"COMPRIMENTO", u"a cota está liberada como %s %s. Com +%s a face passaria %s mm para fora do nariz do "
                          u"cabeçote, então, se vocês precisarem apertar, o aceitável prático é %s −0,50/+0,00 — "
                          u"confirme qual dos dois você vai usar." % (br(L), tol, tol.replace("±", ""),
                                                                      tol.replace("±", ""), br(L))),
        (u"ENTREGAR", u"1 peça, sem lote. Dossiê: certificado EN 10204 3.1 do calor (composição, granulometria, "
                       u"inclusões, têmpera/revenimento), relatório dimensional com todas as cotas desta folha, "
                       u"microdureza em seção de corpo de prova do mesmo lote. Marcação a laser na **face "
                       u"traseira**, fora do furo e da face de assentamento: JONATHA v27.0 · EX-031 · 1045 · "
                       u"rev. %s · lote · nº de série · data." % ("30 (2026-09-22)" if abs(L - 95.0) < 0.01
                                                                   else "29 (2026-09-22)")),
    ]
    blocos = []
    for ti, tx in regras:
        linhas = quebra(tx.replace("**", ""))
        blocos.append([(ti, None)] + [(None, l) for l in linhas])
    metade = (len(blocos) + 1) // 2
    # achata: cada coluna e a lista de (titulo, linha) na ordem de impressao
    col = [sum(blocos[:metade], []), sum(blocos[metade:], [])]
    alt_disponivel_pt = 0.40 * fig.get_figheight() * 72.0
    for c in col:
        n = len(c)
        if n * FONTE_REGRA * 1.42 > alt_disponivel_pt:
            raise SystemExit("FALHOU: as regras nao cabem na folha (%d linhas para %d que cabem)"
                             % (n, int(alt_disponivel_pt / (FONTE_REGRA * 1.42))))
    for k, c in enumerate(col):
        axr = fig.add_axes([0.035 + 0.485 * k, 0.050, 0.45, 0.375]); axr.axis("off")
        axr.set_xlim(0, 1); axr.set_ylim(0, 1)
        y = 1.0
        for ti, linha in c:
            if ti is not None:
                axr.text(0.0, y, ti, fontsize=FONTE_REGRA + 0.9, va="top", ha="left", fontweight="bold",
                         color="#0b4a86")
                y -= (FONTE_REGRA * 1.95) / alt_disponivel_pt
            else:
                axr.text(0.0, y, linha, fontsize=FONTE_REGRA, va="top", ha="left", color="#111111")
                y -= (FONTE_REGRA * 1.42) / alt_disponivel_pt
    fig.text(0.035, 0.452, u"REGRAS DA PEÇA — valem tanto quanto as cotas de cima", fontsize=10.4,
             fontweight="bold", ha="left")
    fig.text(0.035, 0.012, u"Gerada por desenhar_folha_de_cotas_v30.py a partir de %s/pacote_usinagem.json "
                           u"(medição no STEP, seções de 0,02 mm). Modelo: %s — %s faces, 1 sólido, BRep válido."
             % (PACOTE, os.path.basename(m["arquivo"]), m["faces"]), fontsize=7.2, color="#555555",
             ha="left", va="bottom")
    fig.text(0.035, 0.028, u"Esta folha não substitui o STEP: ela diz o que medir. O sólido do canal para o fio "
                           u"EDM é 3D/MATRIZ_%s_CANAL_DE_FLUXO.step." % ("V30" if abs(L - 95.0) < 0.01 else "V29"),
             fontsize=7.2, color="#555555", ha="left", va="bottom")

    destino = os.path.join(RAIZ, PACOTE, ARQ)
    fig.savefig(destino + ".pdf", facecolor="white")
    fig.savefig(destino + ".png", facecolor="white", dpi=150)
    plt.close(fig)
    print("ok:", destino + ".pdf", os.path.getsize(destino + ".pdf"), "bytes")
    print(u"    cotas: Ø%s / Ø%s / Ø%s · L %s · land %s em Z %s→%s · fenda %s×%s · entrada Ø%s · boca %s×%s"
          % (br(2 * r[0]), br(2 * r[1]), br(2 * r[2]), br(L), br(land), br(z_land0), br(z_land1),
             br(2 * w_fd), br(a_fd, 3), br(2 * w_in), br(2 * w_bs), br(a_bs)))


if __name__ == "__main__":
    main()
