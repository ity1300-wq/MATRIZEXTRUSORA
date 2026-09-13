#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
desenhar_gedeon_consertada.py — uma prancha A3 que responde as três observações com o olho
------------------------------------------------------------------------------------------
Feito depois de o usuário dizer, duas vezes, que (i) a Gedeon "parece corrompida", (ii) no STEP com o cabeçote
ela "parece idêntica à Jonatha" e (iii) no STEP sem matriz "não aparece a fenda, mas dá para ver o copo da
matriz dentro do cabeçote". As três têm resposta medida em `gedeon_certa.json`; esta prancha é a resposta
*visual*, com as cinco faixas no MESMO ESCALO (limites idênticos em todas), porque comparação em escala
diferente não é comparação.

Faixas, todas traçadas a partir da seção medida no sólido (nada de cotas decoradas):
  1  cabeçote EX-030 sem matriz      → por que não há fenda ali, e o que é o "copo" que se vê
  2  Gedeon como entregue (A ∪ B)    → com a zona do bolso de pino selado marcada
  3  Gedeon reconstruída do backup   → mesma caixa externa, bolso conjugado, 1 casca por sólido
  4  Jonatha v27 (master)            → lado a lado com a 3
  5  onde as duas diferem            → aço que a Gedeon tem e a v27 não, e o contrário

Cada número do rodapé vem da medição desta própria execução e vai para
`07_CAD_Matrizes/Matriz_Gedeon_Entregue_HISTORICA/desenho_gedeon.json`.

Uso:  python 04_Dados_SSOT_e_Scripts/desenhar_gedeon_consertada.py [--png]

O nome do arquivo sobrou do episodio da tentativa refutada (apagada em 2026-09-13): o que ele
desenha e a GEDEON CERTA, o arquivo do usuario, contra a v27 e contra a Gedeon entregue.
"""

import argparse
import json
import os
import sys
import textwrap

import cadquery as cq
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
if AQUI not in sys.path:
    sys.path.insert(0, AQUI)

import gerar_desenho_2d_cabecote_matriz as dd          # só as primitivas de traçado, todas módulo-a-módulo
from verificar_v28 import maior, n                       # n(): número pt-BR

DIR_HIS = os.path.join(RAIZ, "02_CAD_Modelos_Historicos")
DIR_OFF = os.path.join(RAIZ, "07_CAD_Matrizes", "Matriz_Jonatha_v27_OFICIAL")
DIR_GED = os.path.join(RAIZ, "07_CAD_Matrizes", "Matriz_Gedeon_Certa")
ARQ_JSON = os.path.join(DIR_GED, "desenho_gedeon.json")

LIM_X = (-212.0, 212.0)
LIM_Y = (-10.0, 136.0)


def le(p):
    return cq.importers.importStep(p).val()


def quebra(nota, largo=186):
    """Embrulha cada linha da nota na largura da folha: nota que passa do fim nao e nota, e mancha."""
    out = []
    for ln in str(nota).split("\n"):
        out.extend(textwrap.wrap(ln, largo) or [""])
    return "\n".join(out)


def faixa(ax, solido, titulo, nota):
    """Traça a seção medida de `solido` no escalonamento comum e anota o que a própria seção mede.

    Nada aqui vem de memória: Ø máximo, comprimento e raio interno saem do perfil de corte, fatia a fatia
    (`dd.secao` -> `perfil` = [(z, r_externo, r_interno_ou_None)]).
    """
    curvas, area, perfil, platos, plano = dd.secao(solido)
    dd.desenha_corte(ax, perfil)
    dd.desenha_arestas(ax, curvas)
    rmax = max((p[1] or 0.0) for p in perfil)
    rmin = min((p[2] for p in perfil if p[2]), default=0.0)
    zmin, zmax = perfil[0][0], perfil[-1][0]
    col = dd.Coluna(rmax + 30.0, passo=7.0)
    dd.chamada_diametro(ax, rmax, 0.5 * (zmin + zmax), "Ø %s   máximo medido nesta seção" % n(2 * rmax, 2),
                        col, cor="tab:blue")
    dd.chamada_diametro(ax, 0.0, zmax, "Z %s   face da saída" % n(zmax, 2), col, cor="0.1")
    dd.chamada_diametro(ax, 0.0, zmin, "Z %s   plano traseiro (seção em %s)" % (n(zmin, 2), plano), col,
                        cor="0.1")
    if rmin:
        dd.chamada_diametro(ax, rmin, 0.5 * (zmin + zmax) - 14.0, "Ø %s   vazio mais interno da seção"
                            % n(2 * rmin, 2), col, cor="tab:orange")
    dd.cota_v(ax, zmin, zmax, -(rmax + 40.0), "%s   comprimento" % n(zmax - zmin, 2), ha="right")
    ax.set_xlim(*LIM_X)
    ax.set_ylim(*LIM_Y)
    ax.set_aspect("equal", adjustable="datalim")
    ax.axis("off")
    ax.set_title(titulo, fontsize=10.0, loc="left", pad=6)
    ax.text(0.0, -0.27, quebra(nota), transform=ax.transAxes, fontsize=6.4, va="top", color="0.2")
    return dict(área_material_mm2=round(area, 1), D_máximo_mm=round(2 * rmax, 3), z_min=round(zmin, 3),
                z_max=round(zmax, 3), raio_interno_mín_mm=round(rmin, 3), plano=plano, platos=len(platos))


def faixa_diferenca(ax, par, jona, titulo, nota, zmin_p, zmax_p):
    """Faixa 5: o perfil da Gedeon em cinza e, por cima, o aço que só cada uma tem — em CORTE RADIAL.

    Corte em Y = 0 para as diferenças, não no plano que a auto-escolha daria: os bolsos de pino ficam a
    |x| = 41,50 mm e atravessam Y = 0, então é nesse plano que eles aparecem. O perfil de fundo vem do plano
    que a área de material escolher (X = 0 na Gedeon), como nas faixas 2, 3 e 4.
    """
    curvas, area, perfil, platos, plano = dd.secao(par)
    dd.desenha_corte(ax, perfil, cor="0.45", preenche=True, hachura=True)
    med = {}
    for rot, d, cor, hatch in (("só a Gedeon tem", maior(par.cut(jona)), "tab:red", "////"),
                               ("só a Jonatha tem", maior(jona.cut(par)), "tab:blue", "\\\\\\\\")):
        cc, aa, pp, ee, pl = dd.secao(d, eixo="y")
        dd.desenha_corte(ax, pp, cor=cor, espessura=1.0, preenche=True, hachura=True)
        bs = [q.BoundingBox() for q in d.Solids()] or [d.BoundingBox()]
        med[rot] = dict(volume_mm3=round(d.Volume(), 1),
                        z=[round(min(b.zmin for b in bs), 2), round(max(b.zmax for b in bs), 2)],
                        raio=[round(min(abs(b.xmin) for b in bs), 2), round(max(abs(b.xmax) for b in bs), 2)],
                        área_seção_mm2=round(aa, 1))
    # legenda no espaco livre ACIMA da peca: na coluna de rotulos ela ja tem Ø maximo e os Z, e as duas
    # coisas se cortavam (e cortavam o desenho) quando ficavam no meio da figura
    ax.text(-70.0, 133.0, "vermelho  %s mm³  — aço que só a Gedeon tem (Z %s → %s): aqui a v27 tem o funil "
            "escavado no proprio aco, a Gedeon e macica" % (
        n(med["só a Gedeon tem"]["volume_mm3"], 1), n(med["só a Gedeon tem"]["z"][0], 2),
        n(med["só a Gedeon tem"]["z"][1], 2)), fontsize=7.4, color="tab:red", ha="left", va="top")
    ax.text(-70.0, 122.0, "azul  %s mm³  — aço que só a Jonatha tem (Z %s → %s): ali a Gedeon tem o furo de "
            "pino, a v27 e macica" % (
        n(med["só a Jonatha tem"]["volume_mm3"], 1), n(med["só a Jonatha tem"]["z"][0], 2),
        n(med["só a Jonatha tem"]["z"][1], 2)), fontsize=7.4, color="tab:blue", ha="left", va="top")
    ax.text(-70.0, zmin_p - 6.0, "envelope comum as cinco faixas: Ø 93,00 × Z 0..109,00 — o que difere e "
            "interno, e e isto que responde \"parece identica\"",
            fontsize=7.0, color="0.15", ha="left", va="top")
    ax.set_xlim(*LIM_X)
    ax.set_ylim(*LIM_Y)
    ax.set_aspect("equal", adjustable="datalim")
    ax.axis("off")
    ax.set_title(titulo, fontsize=10.0, loc="left", pad=6)
    ax.text(0.0, -0.08, quebra(nota), transform=ax.transAxes, fontsize=6.4, va="top", color="0.2")
    return med


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--saida", default=os.path.join(DIR_GED, "DESENHO_2D_GEDEON_CERTA_X_JONATHA.pdf"))
    ap.add_argument("--png", action="store_true", help="PNG de conferência ao lado (ignorado pelo git)")
    a = ap.parse_args()
    os.makedirs(DIR_GED, exist_ok=True)

    cab = le(os.path.join(RAIZ, "06_CAD_Cabecote_EX-030", "STEP", "Cabecote_EX-030_sem_flange.step"))
    A0, B0 = (le(os.path.join(DIR_HIS, "MatrizGedeon_Body_A.step")), le(os.path.join(DIR_HIS, "MatrizGedeon_Body_B.step")))
    A1, B1 = (le(os.path.join(DIR_GED, "MatrizGedeon_Certa_Body_A.step")),
              le(os.path.join(DIR_GED, "MatrizGedeon_Certa_Body_B.step")))
    J = le(os.path.join(DIR_OFF, "MatrizJonatha.step"))
    J2 = maior(J.Solids()[0].fuse(J.Solids()[1]))
    entregue, consertada = maior(A0.fuse(B0)), maior(A1.fuse(B1))
    # a caixa do BOLSO DO PINO da Gedeon ENTREGUE, medida nos proprios arquivos de 02_/ (antes vinha do JSON
    # da tentativa refutada, que foi apagada em 2026-09-13). No arquivo historico o bolso e um cilindro de
    # eixo em X, raio 2,00 (Ø 4,00 x 4,00), que so aparece no Body_A; os raios 0,75 sao os filetes da fenda e
    # os 39,75..46,50 sao os estagios externos - daí a janela 0,95 < r < 12.
    vistas = set()
    for meio in (A0, B0):
        for f in meio.Faces():
            if f.geomType() != "CYLINDER":
                continue
            r = f._geomAdaptor().Cylinder().Radius()
            if 0.95 < r < 12.0:
                b = f.BoundingBox()
                vistas.add((round(b.xmin, 2), round(b.xmax, 2), round(b.zmin, 2), round(b.zmax, 2)))
    pin = {"caixas_mm": [dict(x=[v[0], v[1]], z=[v[2], v[3]]) for v in sorted(vistas, key=lambda v: abs(v[0]))]}
    gc = json.load(open(os.path.join(AQUI, "gedeon_certa.json"), encoding="utf-8"))
    fzp = gc["furos_pino"]
    cx3 = [dict(x=[round(v[0], 2), round(v[1], 2)], z=[round(fzp["z"][0], 2), round(fzp["z"][1], 2)])
           for v in fzp["x"]]

    fig, axs = plt.subplots(5, 1, figsize=(16.54, 11.69))
    plt.subplots_adjust(left=0.022, right=0.985, top=0.965, bottom=0.035, hspace=1.02)
    med = {}

    med["1 cabecote sem matriz"] = faixa(
        axs[0], cab,
        "1   CABEÇOTE EX-030 SEM MATRIZ — a fenda não está aqui; o «copo» que se vê é o bolso dele",
        "seção medida no STEP `Cabecote_EX-030_sem_flange.step` (1 sólido, 1 casca, 11 faces, 610.588,2 mm³, "
        "reimportado e conferido): não há matriz alguma neste arquivo.\nO cabeçote só fura em escada Ø80 "
        "(nariz) → Ø90 (degrau) → Ø95 × 70,00 (o bolso). É essa escada que, em corte, parece o copo da matriz "
        "— é o copo em negativo, e é o que faz a matriz passar pelo nariz sem tocar a fenda.")

    med["2 Gedeon entregue"] = faixa(
        axs[1], entregue,
        "2   GEDEON COMO ENTREGUE (02_/Body_A ∪ Body_B) — 1 sólido com 3 CASCA: bolso de pino selado",
        "seção medida das duas metades de `02_CAD_Modelos_Historicos/`, abertas SÓ PARA LEITURA (regra 2) e "
        "unidas para o corte: A ∪ B = %s mm³ de aço, caixa Ø93,00 × Z 0..109,00.\nO retângulo pontilhado é a "
        "zona do pino (Ø 4,00 × 4,00, eixo em X): no `Body_A` é CASCA INTERNA — cavidade selada dentro do aço, o que abre como "
        "«peça corrompida» no CAD e não tem ferramenta — e no `Body_B` não há bolso nenhum."
        % n(gc["gedeon_entregue_contra_certa"]["volume_aco_entregue_mm3"], 1))
    cx = pin["caixas_mm"]
    for c in cx:
        axs[1].add_patch(plt.Rectangle((c["x"][0] - 1.6, c["z"][0] - 1.6), c["x"][1] - c["x"][0] + 3.2,
                                       c["z"][1] - c["z"][0] + 3.2, fill=False, ec="tab:red", lw=1.2,
                                       ls=(0, (3, 2))))
        axs[1].plot([c["x"][1] + 1.6, 62.0], [0.5 * (c["z"][0] + c["z"][1])] * 2, color="tab:red", lw=0.5,
                    ls=(0, (2, 2)))
    axs[1].text(-70.0, 132.5, "Z %s → %s, ponta em |x| = %s mm: no `Body_A` o bolso é CASCA INTERNA (selada no aço); "
                "no `Body_B` não existe. E esta peça tem %s mm³ de aço contra os %s mm³ do arquivo certo"
                % (n(cx[0]["z"][0], 2), n(cx[0]["z"][1], 2), n(abs(cx[0]["x"][1]), 2),
                   n(gc["gedeon_entregue_contra_certa"]["volume_aco_entregue_mm3"], 1),
                   n(gc["gedeon_entregue_contra_certa"]["volume_aco_certa_mm3"], 1)),
                fontsize=7.0, color="tab:red", ha="left", va="top")
    med["2 Gedeon entregue"]["pinos_marcados"] = cx
    med["2 Gedeon entregue"]["aco_mm3"] = gc["gedeon_entregue_contra_certa"]["volume_aco_entregue_mm3"]

    f = gc["fenda"]; ce = gc["cone_entrada"]; dv = gc["defeito_cavidade_selada"]; en = gc["entrega"]
    med["3 Gedeon certa"] = faixa(
        axs[2], consertada,
        "3   GEDEON CERTA — O SEU ARQUIVO, INTEIRO — fenda atravessada, cone de entrada, sem funil",
        "seção medida de `02_/matrizGedeonCerta.step` (SÓ LEITURA, %d faces, %s mm³ de aço, %d cascas): a fenda "
        "de largura %s × espessura %s com R %s nos topos atravessa de Z = %s a Z = %s e sai pela face de saída; "
        "o cone de entrada abre em Ø %s na face traseira.\nO único defeito do arquivo dele: os %d furos de pino "
        "são cavidades SELADAS — %s mm de aço até o Ø %s, sem entrada de ferramenta (por isso as %d cascas). O "
        "conserto é só partir em Y = 0: A %s + B %s = o bloco com diferença de %s mm³, 1 casca cada, BRepCheck "
        "válido, A ∩ B = %s mm³. NENHUM aço foi escavado."
        % (gc["inventario"]["faces"], n(gc["inventario"]["volume"], 1), gc["inventario"]["cascas"],
           n(f["largura_mm"], 2), n(f["espessura_mm"], 2), n(f["raio_ponta_mm"], 2), n(f["z_de_mm"], 2),
           n(f["z_ate_mm"], 2), n(2 * ce["raio_max"], 2), dv["furos_sem_acesso"],
           n(dv["parede_ate_o_externo_mm"], 2), n(dv["diametro_externo_na_zona"], 2), dv["cascas_no_solido"],
           n(en["volume_A_mm3"], 1), n(en["volume_B_mm3"], 1), n(en["soma_menos_o_bloco_mm3"], 4),
           n(en["interseccao_A_B_mm3"], 4)))
    for cxi in cx3:
        axs[2].add_patch(plt.Rectangle((cxi["x"][0] - 1.6, cxi["z"][0] - 1.6), cxi["x"][1] - cxi["x"][0] + 3.2,
                                       cxi["z"][1] - cxi["z"][0] + 3.2, fill=False, ec="tab:green", lw=1.2,
                                       ls=(0, (3, 2))))
        axs[2].plot([cxi["x"][1] + 1.6, 62.0], [0.5 * (cxi["z"][0] + cxi["z"][1])] * 2, color="tab:green",
                    lw=0.5, ls=(0, (2, 2)))
    axs[2].text(-70.0, 132.5, "Z %s → %s, a |x| %s mm: no arquivo inteiro o furo é cavidade SELADA; nas duas "
                "metades entregues ele sai aberto no plano de partição (meia-cana usinável)"
                % (n(fzp["z"][0], 2), n(fzp["z"][1], 2), n(abs(fzp["x"][1][1]), 2)),
                fontsize=7.0, color="tab:green", ha="left", va="top")
    med["3 Gedeon certa"]["furos_marcados"] = cx3

    med["4 Jonatha v27"] = faixa(
        axs[3], J2,
        "4   JONATHA v27 (o master aprovado) — compare com a faixa 3, no mesmo escalonamento",
        "seção medida de `07_CAD_Matrizes/Matriz_Jonatha_v27_OFICIAL/MatrizJonatha.step` (2 sólidos, %s mm³ de aço, cascas "
        "[3, 1]). Vista no MESMO escalonamento da faixa 3 para a comparação não ser de memória: a silhueta "
        "externa é idêntica porque o envelope é exigência de projeto (Ø93,00 × Z 0..109,00 nas duas).\n"
        "O que as separa é medido na faixa 5: a v27 tem funil escavado no próprio aço (%s mm³ de canal contra "
        "%s mm³ de cone + fenda da Gedeon) e %s mm³ de aço a menos no total."
        % (n(gc["contra_a_jonatha"]["volume_jonatha_aco_mm3"], 1), n(gc["contra_a_jonatha"]["canal_da_v27_mm3"], 1),
           n(gc["contra_a_jonatha"]["fluxo_certa_mm3"], 1), n(gc["contra_a_jonatha"]["aco_so_na_certa_mm3"], 1)))

    _f3 = med["3 Gedeon certa"]
    med["5 diferenca"] = faixa_diferenca(
        axs[4], consertada, J2,
        "5   ONDE A GEDEON CERTA E A JONATHA v27 DIFEREM — diferença de conceito, medida nas duas peças",
        ("booleanos nos dois sentidos entre `matrizGedeonCerta.step` e `MatrizJonatha.step`, alinhados pela face "
         "de saída (Z = 109,00), re-cortados em Y = 0 — o plano onde os furos de pino aparecem. Números da PEÇA "
         "INTEIRA medida por `gerar_gedeon_certa.py`; a hachura é a meia-seção, por isso cada furo aparece uma "
         "vez.\nA diferença não é «funil ampliado»: a Gedeon não tem funil no próprio aço; a convergência a "
         "montante é do furo estagiado do cabeçote. Fluxo da Gedeon %s mm³ contra funil da v27 %s mm³."
         % (n(gc["contra_a_jonatha"]["fluxo_certa_mm3"], 1), n(gc["contra_a_jonatha"]["canal_da_v27_mm3"], 1))),
        _f3["z_min"], _f3["z_max"])

    fig.savefig(a.saida, format="pdf")
    print("prancha ->", os.path.relpath(a.saida, RAIZ))
    if a.png:
        # um PNG da prancha inteira, em dpi baixo de proposito: e para conferir de vista, e o `fig.canvas
        # .draw()` por faixa estourava a memoria do conteiner (5 eixos com hatch densos).
        fig.savefig(os.path.join(DIR_GED, "DESENHO_2D_GEDEON_CERTA_p1.png"), dpi=85)
        print("PNG de conferencia gravado (o .gitignore da pasta ignora DESENHO_2D_*_p*.png por design)")
    json.dump({"gerado_por": "04_Dados_SSOT_e_Scripts/desenhar_gedeon_consertada.py",
               "escalonamento_identico_as_faixas": "sim — todas com xlim %s e ylim %s" % (LIM_X, LIM_Y),
               "faixas": med,
               "prancha": os.path.relpath(a.saida, RAIZ)},
              open(ARQ_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for k, v in med.items():
        print(f"  {k:22s}", {kk: vv for kk, vv in v.items() if kk != "plano"} if isinstance(v, dict) else v)
    return 0


if __name__ == "__main__":
    sys.exit(main())
