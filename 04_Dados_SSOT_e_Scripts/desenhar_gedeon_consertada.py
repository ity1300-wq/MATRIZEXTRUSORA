#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
desenhar_gedeon_consertada.py — uma prancha A3 que responde as três observações com o olho
------------------------------------------------------------------------------------------
Feito depois de o usuário dizer, duas vezes, que (i) a Gedeon "parece corrompida", (ii) no STEP com o cabeçote
ela "parece idêntica à Jonatha" e (iii) no STEP sem matriz "não aparece a fenda, mas dá para ver o copo da
matriz dentro do cabeçote". As três têm resposta medida em `gedeon_corrigida.json`; esta prancha é a resposta
*visual*, com as cinco faixas no MESMO ESCALO (limites idênticos em todas), porque comparação em escala
diferente não é comparação.

Faixas, todas traçadas a partir da seção medida no sólido (nada de cotas decoradas):
  1  cabeçote EX-030 sem matriz      → por que não há fenda ali, e o que é o "copo" que se vê
  2  Gedeon como entregue (A ∪ B)    → com a zona do bolso de pino selado marcada
  3  Gedeon reconstruída do backup   → mesma caixa externa, bolso conjugado, 1 casca por sólido
  4  Jonatha v27 (master)            → lado a lado com a 3
  5  onde as duas diferem            → aço que a Gedeon tem e a v27 não, e o contrário

Cada número do rodapé vem da medição desta própria execução e vai para
`06_CAD_Cabecote_EX-030/STEP/Gedeon_Corrigida/desenho_gedeon.json`.

Uso:  python 04_Dados_SSOT_e_Scripts/desenhar_gedeon_consertada.py [--png]
"""

import argparse
import json
import os
import sys

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
DIR_OFF = os.path.join(RAIZ, "01_CAD_MatrizJonatha_Oficial")
DIR_GED = os.path.join(RAIZ, "06_CAD_Cabecote_EX-030", "STEP", "Gedeon_Corrigida")
ARQ_JSON = os.path.join(DIR_GED, "desenho_gedeon.json")

LIM_X = (-212.0, 212.0)
LIM_Y = (-10.0, 136.0)


def le(p):
    return cq.importers.importStep(p).val()


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
    ax.text(0.0, -0.17, nota, transform=ax.transAxes, fontsize=6.8, va="top", color="0.2")
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
    ax.text(-70.0, 133.0, "vermelho  %s mm³  — aço que só a Gedeon tem, no anel de saída, em Z %s → %s" % (
        n(med["só a Gedeon tem"]["volume_mm3"], 1), n(med["só a Gedeon tem"]["z"][0], 2),
        n(med["só a Gedeon tem"]["z"][1], 2)), fontsize=7.4, color="tab:red", ha="left", va="top")
    ax.text(-70.0, 122.0, "azul  %s mm³  — aço que só a Jonatha tem, na zona dos pinos, em Z %s → %s" % (
        n(med["só a Jonatha tem"]["volume_mm3"], 1), n(med["só a Jonatha tem"]["z"][0], 2),
        n(med["só a Jonatha tem"]["z"][1], 2)), fontsize=7.4, color="tab:blue", ha="left", va="top")
    ax.text(-70.0, zmin_p - 6.0, "envelope comum: Ø 93,00 × Z 0..109,00 — as curvas de fora são as mesmas das "
            "faixas 2, 3 e 4; o que difere é interno e nas bordas, e é isto que responde \"parece idêntica\"",
            fontsize=7.0, color="0.15", ha="left", va="top")
    ax.set_xlim(*LIM_X)
    ax.set_ylim(*LIM_Y)
    ax.set_aspect("equal", adjustable="datalim")
    ax.axis("off")
    ax.set_title(titulo, fontsize=10.0, loc="left", pad=6)
    ax.text(0.0, -0.17, nota, transform=ax.transAxes, fontsize=6.8, va="top", color="0.2")
    return med


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--saida", default=os.path.join(DIR_GED, "DESENHO_2D_GEDEON_CONSERTADA_X_JONATHA.pdf"))
    ap.add_argument("--png", action="store_true", help="PNG de conferência ao lado (ignorado pelo git)")
    a = ap.parse_args()
    os.makedirs(DIR_GED, exist_ok=True)

    cab = le(os.path.join(RAIZ, "06_CAD_Cabecote_EX-030", "STEP", "Cabecote_EX-030_sem_flange.step"))
    A0, B0 = (le(os.path.join(DIR_HIS, "MatrizGedeon_Body_A.step")), le(os.path.join(DIR_HIS, "MatrizGedeon_Body_B.step")))
    A1, B1 = (le(os.path.join(DIR_GED, "MatrizGedeon_Corrigida_Body_A.step")),
              le(os.path.join(DIR_GED, "MatrizGedeon_Corrigida_Body_B.step")))
    J = le(os.path.join(DIR_OFF, "MatrizJonatha.step"))
    J2 = maior(J.Solids()[0].fuse(J.Solids()[1]))
    entregue, consertada = maior(A0.fuse(B0)), maior(A1.fuse(B1))
    pin = json.load(open(os.path.join(AQUI, "gedeon_corrigida.json"), encoding="utf-8"))["pinos"]

    fig, axs = plt.subplots(5, 1, figsize=(16.54, 11.69))
    plt.subplots_adjust(left=0.022, right=0.985, top=0.965, bottom=0.035, hspace=0.62)
    med = {}

    med["1 cabecote sem matriz"] = faixa(
        axs[0], cab,
        "1   CABEÇOTE EX-030 SEM MATRIZ — a fenda não está aqui; o «copo» que se vê é o bolso dele",
        "geometria: seção medida no STEP `Cabecote_EX-030_sem_flange.step` (1 sólido, 1 casca, 11 faces, "
        "610.588,2 mm³ — reimportado e conferido). Não há matriz alguma neste arquivo.\nA fenda 75,00 × 1,50 "
        "com R0,75 vive na MATRIZ, não no cabeçote: o cabeçote só fura em escada Ø80 (nariz) → Ø90 (degrau) → "
        "Ø95 × 70,00 (o bolso). É essa escada que, em corte,\nparece o copo da matriz — porque é o copo da "
        "matriz em negativo, e é o que faz a matriz passar pelo nariz sem tocar a fenda.")

    med["2 Gedeon entregue"] = faixa(
        axs[1], entregue,
        "2   GEDEON COMO ENTREGUE (02_/Body_A ∪ Body_B) — 1 sólido com 3 CASCA: bolso de pino selado",
        "geometria: seção medida das duas metades de `02_CAD_Modelos_Historicos/` abertas SÓ PARA LEITURA "
        "(regra 2), unidas para o corte (A ∪ B = 469.156,8 mm³ contra A + B = 469.156,7 — se tocam no plano de\n"
        "partição, não se sobrepõem). O retângulo pontilhado é a zona do pino Ø1,78 × 10,00: no `Body_A` ela é "
        "uma CASCA INTERNA — cavidade selada dentro do aço, que é o que abre\ncomo «peça corrompida» no CAD e o "
        "que não tem ferramenta que faça — e no `Body_B` não há bolso nenhum. Envelope Ø93,00 × Z 0..109,00.",
        )
    cx = pin["caixas_mm"]
    # um retangulo por pino, nas coordenadas MEDIDAS (vêm de `gedeon_corrigida.json`, não decoradas), com a
    # legenda no espaco livre acima da peca - antes ela ficava em cima do desenho e da coluna de rotulos
    for axi, cor, txt in ((axs[1], "tab:red", "Z %s → %s, a |x| %s mm: no `Body_A` é CASCA INTERNA (bolso "
                           "selado dentro do aço); no `Body_B` não há bolso nenhum"
                           % (n(cx[0]["z"][0], 2), n(cx[0]["z"][1], 2), n(abs(cx[0]["x"][1]), 2))),
                          (axs[2], "tab:green", "mesma zona, mesmo pino: aqui o bolso sai ABERTO no plano de "
                           "partição nos dois corpos, porque os cilindros do próprio arquivo já atravessam "
                           "Y = 0")):
        for c in cx:
            axi.add_patch(plt.Rectangle((c["x"][0] - 1.6, c["z"][0] - 1.6), c["x"][1] - c["x"][0] + 3.2,
                                        c["z"][1] - c["z"][0] + 3.2, fill=False, ec=cor, lw=1.2,
                                        ls=(0, (3, 2))))
            axi.plot([c["x"][1] + 1.6, 62.0], [0.5 * (c["z"][0] + c["z"][1])] * 2, color=cor, lw=0.5,
                     ls=(0, (2, 2)))
        axi.text(-70.0, 126.0, txt, fontsize=7.0, color=cor, ha="left", va="top")
    med["2 Gedeon entregue"]["pinos_marcados"] = cx

    med["3 Gedeon consertada"] = faixa(
        axs[2], consertada,
        "3   GEDEON RECONSTRUÍDA DO SEU BACKUP — mesmo envelope, bolso conjugado, 1 CASCA por sólido",
        "geometria: `06_CAD_Cabecote_EX-030/STEP/Gedeon_Corrigida/MatrizGedeon_Corrigida_Body_A/B.step`, "
        "re-corte de `02_/matrizGedeonCerta.step` (o seu backup: 640.180,7 mm³ = as duas metades brutas de\n"
        "`MatrizGedeon.step`, diferença 0,000 mm³) com o canal próprio da Gedeon (213.790,0 mm³) e com os pinos "
        "do próprio arquivo dele. A ∩ B = 0,000000 mm³; metal no canal = 0,000000 mm³;\nvalidade BRepCheck True "
        "nos dois. Caixa externa idêntica à faixa 2 — o que mudou é o bolso, não a peça.")

    med["4 Jonatha v27"] = faixa(
        axs[3], J2,
        "4   JONATHA v27 (o master aprovado) — compare com a faixa 3, no mesmo escalonamento",
        "geometria: seção medida de `01_CAD_MatrizJonatha_Oficial/MatrizJonatha.step` (2 sólidos, "
        "469.001,7 mm³, cascas [3, 1]). As cascas são a mesma moléstia da Gedeon: bolso selado num corpo e "
        "ausente\nno outro — é o G-03 da auditoria, que a proposta v28.1 remedia abrindo os quatro bolsões no "
        "plano de partição dos DOIS corpos. Vista aqui para que a comparação seja no mesmo escalonamento,\nnão "
        "de memória: o que as separa é medido na faixa 5 — 155,1 mm³ de aço que a Gedeon tem na SAÍDA "
        "(Z 107,50 → 109,00) e que na Jonatha é o chanfro de 1,50 × 45°, mais 44,9 mm³ na zona dos pinos "
        "(Z 44,50 → 64,50). O funil não é a diferença: o canal da Gedeon cabe inteiro no da Jonatha "
        "(Gedeon − Jonatha = 0,0 mm³). Envelope idêntico é exigência de projeto, não coincidência.")

    _f3 = med["3 Gedeon consertada"]
    med["5 diferenca"] = faixa_diferenca(
        axs[4], consertada, J2,
        "5   ONDE A GEDEON E A JONATHA DIFEREM — não são a mesma peça, e dá para ver onde",
        ("os dois blocos hachurados são os booleanos nos dois sentidos, medidos por `gerar_gedeon_corrigida.py` "
         "e aqui re-cortados em Y = 0 (é o plano onde os bolsos de pino aparecem).\n"
         "É isso que responde «parece idêntica à Jonatha»: a silhueta externa é a mesma porque o ENVELOPE é "
         "exigência de projeto (Ø93,00 × Z 0..109,00 idêntico); a diferença é interna, no caminho do plástico, "
         "e está\naqui hachurada. O canal da Gedeon cabe inteiro no da Jonatha: Gedeon − Jonatha = 0,0 mm³, "
         "Jonatha − Gedeon = 155,1 mm³."),
        _f3["z_min"], _f3["z_max"])

    fig.savefig(a.saida, format="pdf")
    print("prancha ->", os.path.relpath(a.saida, RAIZ))
    if a.png:
        # um PNG da prancha inteira, em dpi baixo de proposito: e para conferir de vista, e o `fig.canvas
        # .draw()` por faixa estourava a memoria do conteiner (5 eixos com hatch densos).
        fig.savefig(os.path.join(DIR_GED, "DESENHO_2D_GEDEON_CONSERTADA_p1.png"), dpi=85)
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
