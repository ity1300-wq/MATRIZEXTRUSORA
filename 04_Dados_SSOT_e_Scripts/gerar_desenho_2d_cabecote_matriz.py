"""Gera o DESENHO 2D em PDF do cabeçote EX-030 e de cada matriz (Copo original e Gedeon) em VISTA LATERAL
EM CORTE pelo plano do eixo, com as cotas principais.

Como cada coisa é obtida, para o desenho não poder descolar da peça:
  * as curvas reais do modelo são a seção do STEP pelo plano Y = 0 (booleano com o semiespaço), plotadas
    em cinza fino por baixo - é o "exportado do 3D";
  * o PERFIL DE CORTE (material hachurado + contorno) é medido no mesmo sólido, fatia a fatia: em cada Z
    varremos os cruzamentos da seção com a linha horizontal e tomamos o |x| máximo (raio externo) e o
    mínimo (raio do furo). Isso é robusto onde a face booleana não é - o plano Y = 0 do cabeçote passa por
    dentro das fendas do flange, que são vazio, e a face do corte sai partida;
  * os NÚMEROS das cotas vêm dos dados medidos nos STEP: `cabecote_ex030.json` /
    `verificar_interface_cabecote.py` (cabeçote) e `perfis_matrizes_x_cabecote.json`
    (matriz, medido por `medir_perfis_matrizes_x_cabecote.py`). Se o STEP mudar, o portão da cadeia pega.

Vistas: página 1 = cabeçote + cada matriz solta; página 2 = a montagem de cada matriz no cabeçote, sentada
onde o booleano manda (o encosto medido pelo verificador de interface), no mesmo referencial axial.
`--matrizes` escolhe as chaves de `perfis_matrizes_x_cabecote.json` - por padrão a Copo (original) e a
Gedeon, porque é entre essas duas que a diferença de comprimento explica a saída da fenda.

Uso:
  python 04_Dados_SSOT_e_Scripts/gerar_desenho_2d_cabecote_matriz.py [--png] [--saida x.pdf]
             [--matrizes matriz_1_copo,matriz_2_gedeon]
"""
import argparse
import json
import os
import sys

import cadquery as cq

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, Polygon  # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, ".."))
sys.path.insert(0, AQUI)
DIR_CAB = os.path.join(RAIZ, "06_CAD_Cabecote_EX-030", "STEP")
DIR_HIS = os.path.join(RAIZ, "02_CAD_Modelos_Historicos")
DIR_OFF = os.path.join(RAIZ, "07_CAD_Matrizes", "Matriz_Jonatha_v27_OFICIAL")
PERFIS = os.path.join(AQUI, "perfis_matrizes_x_cabecote.json")

from verificar_interface_cabecote import CORPO, BORES, CHAMFRO, Z_FACE_NARIZ, n  # noqa: E402
from verificar_v28 import maior  # noqa: E402


def vol_intersecao(a, b):
    """Interseccao em mm3, somando os solidos (em booleano que pode sair partido, maior() corta ao
    meio). E a mesma rotina do medidor de perfis - o desenho nao inventa criterio proprio."""
    return sum(x.Volume() for x in a.intersect(b).Solids())

matplotlib.rcParams["font.size"] = 8
matplotlib.rcParams["font.family"] = "DejaVu Sans"
SOLIDO_CORTE = 0.10          # passo da varredura que define o perfil de corte (mm)


# ------------------------------------------------------------------ seccao do STEP
def curvas_de_corte(solido, eixo="y", pos=0.0, deflexao=0.05):
    """Todas as curvas da seccao do solido pelo plano (eixo) = pos, em coordenadas (radial, Z).

    `eixo="y"` corta pelo plano Y = pos e le o raio em |x| - e o plano natural do cabeçote. `eixo="x"` corta
    pelo plano X = pos e le o raio em |y| - e o que serve para a Gedeon e para a v28, cujo plano de particao
    e justamente Y = 0: cortando em Y = 0 nao ha seccao, ha a face de juncao das duas metades (723 mm2 de
    nada). Une todas as faces planas do booleano."""
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
    from OCP.BRepAdaptor import BRepAdaptor_Curve
    from OCP.GCPnts import GCPnts_UniformDeflection
    from OCP.TopAbs import TopAbs_FACE
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopoDS import TopoDS
    if eixo == "y":
        meio = cq.Solid.makeBox(3000, 2000, 3000, cq.Vector(-1500, -2000.0 + pos, -1500))
        plano, radial = "ylen", 0
    elif eixo == "x":
        meio = cq.Solid.makeBox(2000, 3000, 3000, cq.Vector(-2000.0 + pos, -1500, -1500))
        plano, radial = "xlen", 1
    else:
        raise ValueError("eixo deve ser 'x' ou 'y'")
    b = BRepAlgoAPI_Common(solido.wrapped, meio.wrapped)
    b.Build()
    if not b.IsDone():
        raise RuntimeError("corte do solido falhou")
    curvas, area = [], 0.0
    ex = TopExp_Explorer(b.Shape(), TopAbs_FACE)
    while ex.More():
        fc = cq.Face(TopoDS.Face_s(ex.Current()))
        try:
            # 1e-6, nao 1e-9: as faces do corte saem com ruido do booleano (medido: xlen = 2e-07 em
            # X = 0 na Gedeon), e com 1e-9 a seccao inteira era descartada - e o 'no section' que apareceu
            # era isso, nao falta de geometria. 1e-6 mm e 4 ordens de grandeza menor que qualquer detalhe.
            if abs(getattr(fc.BoundingBox(), plano)) < 1e-6:
                area += fc.Area()
                for w in fc.Wires():
                    for e in w.Edges():
                        ad = BRepAdaptor_Curve(TopoDS.Edge_s(e.wrapped))
                        d = GCPnts_UniformDeflection(ad, deflexao)
                        if d.IsDone() and d.NbPoints() > 1:
                            v = (getattr(d.Value(i), ("X", "Y")[radial])() for i in
                                 range(1, d.NbPoints() + 1))
                            curvas.append([(q, d.Value(i).Z()) for i, q in zip(
                                range(1, d.NbPoints() + 1), v)])
        except Exception:
            pass
        ex.Next()
    if not curvas:
        raise RuntimeError("nenhuma curva de seção em %s = %.3f" % (eixo.upper(), pos))
    return curvas, round(area, 3)


def cruzamentos(curvas, z):
    xs = []
    for c in curvas:
        for (x0, z0), (x1, z1) in zip(c, c[1:]):
            if abs(z0 - z1) < 1e-12:
                continue
            if (z0 - z) * (z1 - z) < 1e-9:
                xs.append(x0 + (z - z0) * (x1 - x0) / (z1 - z0))
    return sorted({round(x, 4) for x in xs})


def perfil_corte(curvas, zmin, zmax, passo=SOLIDO_CORTE, tol=0.05):
    """(z, r_ext, r_int) medido fatia a fatia; r_int None quando o centro é maciço."""
    prof, z = [], zmin
    while z <= zmax + 1e-9:
        xs = cruzamentos(curvas, z)
        if xs:
            re = max(abs(x) for x in xs)
            ri = min(abs(x) for x in xs)
            prof.append((z, re if re > tol else 0.0, ri if ri > 0.15 else None))
        z += passo
    # fecha buracos de amostragem (la where o plano toca uma tangente, nao ha cruzamento)
    if prof:
        out = [prof[0]]
        for p in prof[1:]:
            if p[1] == 0.0:
                out.append((p[0], out[-1][1], out[-1][2]))
            else:
                out.append(p)
        prof = out
    return prof


def escada(prof, tol=0.08):
    """(z0, z1, r_ext, r_int) comprimidos dos perfis medidos."""
    ps = []
    for z, re, ri in prof:
        chave = (round(re / tol), round((ri or 0.0) / tol))
        if ps and ps[-1][3] == chave:
            ps[-1][1] = z
        else:
            ps.append([z, z, (re, ri), chave])
    return [(round(a, 2), round(b, 2), round(d[0], 3), None if d[1] is None else round(d[1], 3))
            for a, b, d, _ in ps if b - a >= 0.8]


def desenha_corte(ax, prof, cor="0.15", espessura=1.35, preenche=True, hachura=True):
    """Corte completo (as duas metades + linha de centro), desenhado do PERFIL MEDIDO fatia a fatia.

    Poligono, nao platos comprimidos: platos apagariam o chanfro, que e uma diagonal em que o raio muda
    menos que a tolerancia a cada passo - e o trecho simplesmente sumia do desenho."""
    for lado in (1, -1):
        ext = [(lado * r, z) for (z, r, ri) in prof]
        int_ = [(lado * (ri if ri else 0.0), z) for (z, r, ri) in prof][::-1]
        if preenche:
            ax.add_patch(Polygon(ext + int_, closed=True, facecolor="0.88" if cor == "0.15" else "0.90",
                                 edgecolor="none", alpha=0.85 if cor != "0.15" else 0.6,
                                 hatch=("//////" if lado > 0 else "\\\\") if hachura else None))
        ax.plot([p[0] for p in ext], [p[1] for p in ext], color=cor, lw=espessura)
        ax.plot([p[0] for p in int_], [p[1] for p in int_], color=cor, lw=espessura * 0.75)
        for z, r, ri in (prof[0], prof[-1]):
            ax.plot([lado * (ri if ri else 0.0), lado * r], [z, z], color=cor, lw=espessura * 0.8)
    z0, z1 = prof[0][0], prof[-1][0]
    ax.plot([-1.12 * max(r for _z, r, _ri in prof), 1.12 * max(r for _z, r, _ri in prof)],
            [0.5 * (z0 + z1), 0.5 * (z0 + z1)], color="0.45", lw=0.5, ls=(0, (9, 2, 1, 2)))


def desenha_arestas(ax, curvas, cor="0.45"):
    for c in curvas:
        ax.plot([p[0] for p in c], [p[1] for p in c], color=cor, lw=0.35, alpha=0.5)


# ------------------------------------------------------------------ cotas
def cota_v(ax, z0, z1, x, texto, cor="tab:red", fs=7.0, ha="left"):
    for z in (z0, z1):
        ax.plot([x - 2.0, x + 2.0], [z, z], color=cor, lw=0.5)
    ax.add_patch(FancyArrowPatch((x, z0), (x, z1), arrowstyle="<|-|>", mutation_scale=6.5,
                                 color=cor, lw=0.7, shrinkA=0, shrinkB=0))
    ax.text(x + (2.0 if ha == "left" else -2.0), 0.5 * (z0 + z1), texto, ha=ha, va="center",
            rotation=90, color=cor, fontsize=fs)


def cota_h(ax, x0, x1, z, y, texto, cor="tab:red", fs=7.0):
    for x in (x0, x1):
        ax.plot([x, x], [z, y], color=cor, lw=0.5)
    ax.add_patch(FancyArrowPatch((x0, y), (x1, y), arrowstyle="<|-|>", mutation_scale=6.5,
                                 color=cor, lw=0.7, shrinkA=0, shrinkB=0))
    ax.text(0.5 * (x0 + x1), y + 1.2, texto, ha="center", va="bottom", color=cor, fontsize=fs)


def diametro(ax, r, z, ext, texto, cor="tab:red", fs=7.0):
    """Linha de diametro passante pelo eixo, com setas nas duas paredes e o texto fora do desenho."""
    ax.plot([-r, r], [z, z], color=cor, lw=0.6)
    for s in (1, -1):
        ax.add_patch(FancyArrowPatch((s * (ext if ext else 0.5 * r), z), (s * r, z), arrowstyle="-|>",
                                     mutation_scale=6.5, color=cor, lw=0.7, shrinkA=0, shrinkB=0))
    ax.text(r + 2.0, z, texto, ha="left", va="center", color=cor, fontsize=fs)


class Coluna:
    """Rótulos numa coluna fixa, empurrados para baixo quando dois Z cairiam em cima um do outro."""

    def __init__(self, x, passo=6.0):
        self.x, self.usados, self.passo = x, [], passo

    def aloca(self, z):
        z = float(z)
        while any(abs(z - u) < self.passo for u in self.usados):
            z += self.passo * 0.5
        self.usados.append(z)
        return z


def chamada_diametro(ax, r, z, texto, col, cor="tab:red", fs=7.0):
    """Ø com setas dos dois lados do eixo e o texto alinhado na coluna `col` (linhas guia horizontais)."""
    zz = col.aloca(z)
    ax.plot([-r, r], [z, z], color=cor, lw=0.65)
    for sg in (1, -1):
        ax.add_patch(FancyArrowPatch((sg * 0.45 * r, z), (sg * r, z), arrowstyle="-|>",
                                     mutation_scale=6.0, color=cor, lw=0.65, shrinkA=0, shrinkB=0))
    if abs(zz - z) > 0.4:
        ax.plot([r, r, col.x], [z, zz, zz], color=cor, lw=0.5)
    else:
        ax.plot([r, col.x], [z, z], color=cor, lw=0.5)
    ax.text(col.x + 2.0, zz, texto, ha="left", va="center", color=cor, fontsize=fs)


def corpo_da_matriz(m):
    """A peça como o medidor a monta: união dos arquivos quando ela é bipartida (A ∪ B). Lidos só para
    medir - `02_CAD_Modelos_Historicos/` não é modificado (regra 2)."""
    paths = []
    for nome in m["arquivos_lidos"]:
        p = next((os.path.join(d, nome) for d in (DIR_HIS, DIR_OFF) if os.path.exists(os.path.join(d, nome))),
                 None)
        if p is None:
            sys.exit("não acho %s em %s nem em %s" % (nome, os.path.relpath(DIR_HIS, RAIZ),
                                                     os.path.relpath(DIR_OFF, RAIZ)))
        paths.append(p)
    wp = cq.importers.importStep(paths[0])
    for pt in paths[1:]:
        wp = wp.union(cq.importers.importStep(pt))
    return maior(wp.val()), [os.path.relpath(x, RAIZ) for x in paths]


def secao(solido, eixo=None):
    """(curvas, área, perfil medido fatia a fatia, platos, rótulo do plano) de um sólido - é o que o desenho
    traça. Nada aqui vem de memória: é tudo medido no sólido que chegou.

    Com `eixo=None` o plano é escolhido pela medida, não por gosto: dos dois planos axiais possíveis (Y = 0 e
    X = 0, ambos contendo o eixo Z) fica o que der MAIS ÁREA DE MATERIAL. Isso existe por causa de uma
    armadilha real: em peça bipartida cujo plano de partição é Y = 0 (a Gedeon, a Desenvolvimento, a Jonatha),
    cortar em Y = 0 não corta a peça - mostra a face de junção das metades. Medido: 1.490 mm² em Y = 0 contra
    5.885 mm² em X = 0, com o raio externo chegando a 43,50 em vez de 46,50, ou seja, a silhueta saindo
    errada. Peça simétrica os dois planos empatam, e o empate fica com Y = 0."""
    opc = [("y", "Y = 0 (plano do eixo)"), ("x", "X = 0 (plano do eixo, transversal ao de partição)")]
    if eixo is not None:
        se_eixo, se_rot = eixo, {"y": "Y = 0 (plano do eixo)", "x": "X = 0 (plano do eixo)"}[eixo]
    else:
        melhor = None
        for e, rot in opc:
            try:
                c, a = curvas_de_corte(solido, eixo=e)
            except RuntimeError:
                continue
            if melhor is None or a > melhor[1]:
                melhor = (c, a, e, rot)
        if melhor is None:
            raise RuntimeError("nenhum plano de corte válido neste sólido")
        _, _, se_eixo, se_rot = melhor
    curvas, area = curvas_de_corte(solido, eixo=se_eixo)
    bb = solido.BoundingBox()
    pf = perfil_corte(curvas, bb.zmin, bb.zmax)
    return curvas, area, pf, escada(pf), se_rot


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--saida", default=os.path.join(DIR_CAB, "DESENHO_2D_CABECOTE_X_MATRIZES.pdf"))
    ap.add_argument("--png", action="store_true", help="um PNG por página, ao lado do PDF, para conferência")
    ap.add_argument("--cabecote", default=os.path.join(DIR_CAB, "Cabecote_EX-030_desenhado.step"))
    ap.add_argument("--matrizes", default="matriz_1_copo,matriz_2_gedeon",
                    help="chaves de perfis_matrizes_x_cabecote.json, separadas por vírgula")
    a = ap.parse_args()

    if not os.path.exists(PERFIS):
        sys.exit("falta %s\nrode antes: python 04_Dados_SSOT_e_Scripts/medir_perfis_matrizes_x_cabecote.py --json"
                 % os.path.relpath(PERFIS, RAIZ))
    prof_mat = json.load(open(PERFIS, encoding="utf-8"))
    chaves = [c.strip() for c in a.matrizes.split(",") if c.strip()]
    tem = {x["chave"]: x for x in prof_mat["matrizes"]}
    fora = [c for c in chaves if c not in tem]
    if fora:
        sys.exit("chave(s) de matriz desconhecida(s): %s - as medidas são %s"
                 % (", ".join(fora), ", ".join(sorted(tem))))
    mats = [tem[c] for c in chaves]

    cab = json.load(open(os.path.join(AQUI, "cabecote_ex030.json"), encoding="utf-8"))["corpo"]
    chan = cab["chanfro_corpo_flange"]
    head = max(cq.importers.importStep(a.cabecote).val().Solids(), key=lambda s: s.Volume())
    SC = secao(head, eixo="y")
    for m in mats:
        corpo, rels = corpo_da_matriz(m)
        m["_corpo"], m["_arquivos"] = corpo, rels
        m["_secao"] = secao(corpo)
        print("%-22s STEP %-46s seção %s: %d curvas, material %8.1f mm2"
              % (m["chave"], rels[0], m["_secao"][4], len(m["_secao"][0]), m["_secao"][1]))
    print("cabeçote              STEP %-46s seção %s: %d curvas, material %8.1f mm2"
          % (os.path.relpath(a.cabecote, RAIZ), SC[4], len(SC[0]), SC[1]))

    L_H = Z_FACE_NARIZ
    bores = sorted([(2 * r, za, zb) for (r, za, zb) in BORES], key=lambda t: -t[1])
    fl, pil, corpo_c = CORPO[1], CORPO[2], CORPO[0]
    rc0, zc0, rc1, zc1 = CHAMFRO
    # a direita precisa de folga: as correntes de protrusao vao para la e o rotulo de 14,30/14,00 mm
    # saia cortado com XL = 252 (conferido no PNG de 120 dpi)
    XL = (-272.0, 300.0)

    def monta(ax, titulo, nota):
        ax.set_xlim(*XL)
        ax.set_aspect("equal", adjustable="datalim")
        ax.axis("off")
        ax.set_title(titulo, fontsize=10.5, loc="left", pad=7)
        ax.text(0.0, -0.155, nota, transform=ax.transAxes, fontsize=7.0, va="top", color="0.2")

    def figura(n_faixas):
        fig, axs = plt.subplots(n_faixas, 1, figsize=(16.54, 11.69))
        plt.subplots_adjust(left=0.025, right=0.985, top=0.965, bottom=0.03,
                            hspace=0.66 if n_faixas >= 3 else 0.95)
        return fig, ([axs] if n_faixas == 1 else list(axs))

    # ============================================================== FAIXA 1  CABECOTE
    def faixa_cabecote(ax):
        curvas, area, perfil, es, plano = SC
        desenha_corte(ax, perfil)
        desenha_arestas(ax, curvas)
        col = Coluna(118.0, passo=6.5)
        for i, (d, za, zb) in enumerate(bores):
            chamada_diametro(ax, d / 2.0, 0.5 * (max(za, 0.0) + min(zb, L_H)),
                             "Ø %s   furo %d do cabeçote" % (n(d, 2), i + 1), col, cor="tab:blue")
        chamada_diametro(ax, corpo_c[0], 0.5 * (corpo_c[1] + corpo_c[2]),
                         "Ø %s   corpo" % n(2 * corpo_c[0], 2), col)
        chamada_diametro(ax, fl[0], 0.5 * (fl[1] + fl[2]), "Ø %s   flange" % n(2 * fl[0], 2), col)
        chamada_diametro(ax, pil[0], 0.5 * (pil[1] + pil[2]),
                         "Ø %s   piloto de centragem" % n(2 * pil[0], 2), col, cor="tab:purple")
        # as correntes de comprimento vao para a ESQUERDA: a direita e dos rotulos de diametro, e as duas
        # coisas se cortavam quando ficavam no mesmo lado
        xais = [-126.0, -142.0, -158.0, -174.0]
        for i, (d, za, zb) in enumerate(bores[:3]):
            cota_v(ax, max(za, 0.0), min(zb, L_H), xais[i], n(min(zb, L_H) - max(za, 0.0), 2),
                   cor="tab:blue", ha="right")
        cota_v(ax, fl[1], fl[2], -190.0, "%s   flange" % n(fl[2] - fl[1], 2), ha="right")
        cota_v(ax, pil[1], pil[2], -126.0, n(pil[2] - pil[1], 2), cor="tab:purple")
        cota_v(ax, 0.0, L_H, -206.0, "%s   comprimento total" % n(L_H, 2), ha="right")
        ax.plot([-rc0, -rc1], [zc0, zc1], color="tab:red", lw=0.7, ls=(0, (2, 2)))
        ax.text(-rc1 + 6.0, 0.5 * (zc0 + zc1) + 6.0,
                "chanfro %s × %s°\nØ %s → Ø %s (cota do desenho)" % (
                    n(chan["cateto_mm"], 2), n(chan["angulo_graus"], 0),
                    n(chan.get("de_D_mm", 2 * rc1), 2), n(chan.get("para_D_mm", 2 * rc0), 2)),
                ha="center", va="bottom", color="tab:red", fontsize=7.0)
        print("cabeçote: %d platos, área de material %.1f mm²" % (len(es), area))
        nota = ("geometria: seção do STEP `%s` (arestas reais, cinza fino) e perfil de corte medido dele fatia "
                "a fatia (preto, hachurado). Z = 0 no plano mais\ntraseiro da peça; face do nariz em Z = %s. "
                "Cotas: `cabecote_ex030.json` e `verificar_interface_cabecote.py` - os mesmos dados com que este "
                "STEP foi construído.\nNão aparecem neste corte por acaso do plano, não por omissão: as 6 fendas "
                "do flange e os 6 × Ø16,50 (M12) em C.C. Ø180,00." % (os.path.basename(a.cabecote), n(L_H, 2)))
        monta(ax, "1   CABEÇOTE EX-030 — vista lateral em corte pelo plano do eixo", nota)

    # ============================================================== FAIXA n  MATRIZ SOLTA
    def faixa_matriz(ax, m, i):
        curvas, area, perfil, es, plano = m["_secao"]
        desenha_corte(ax, perfil)
        desenha_arestas(ax, curvas)
        col = Coluna(80.0, passo=7.0)
        for j, (z0, z1, d) in enumerate(m["escala_Ø_x_Z_mm"]):
            # abs(): a escala medida devolve -0,00 para o plano de face da Gedeon (flutuador da bbox), e
            # "Z -0,00" num desenho e ruuido - o plano e o Z = 0
            chamada_diametro(ax, d / 2.0, 0.5 * (z0 + z1),
                             "Ø %s   estágio %d  (Z %s → %s)" % (n(d, 2), j + 1, n(abs(z0), 2), n(z1, 2)),
                             col, cor="tab:blue")
        for j, (z0, z1, d) in enumerate(m["escala_Ø_x_Z_mm"]):
            cota_v(ax, z0, z1, -124.0 - 16 * j, n(z1 - z0, 2), cor="tab:blue", ha="right")
        fb = m["transições_refinadas_mm"].get("fim_da_banda_093_em_Z")
        if fb is not None:
            cota_v(ax, 0.0, fb, -156.0 - 16 * len(m["escala_Ø_x_Z_mm"]),
                   "%s   banda até o ombro" % n(fb, 3), cor="0.1", ha="right")
        # a corrente do comprimento vai para alem da cadeia dos estagios (que cresce com o numero de
        # estagios: a Gedeon tem 3 e esmagava o rotulo de 109,00 contra o de "banda ate o ombro")
        cota_v(ax, 0.0, m["comprimento_medido_mm"], -206.0 - 16.0 * len(m["escala_Ø_x_Z_mm"]),
               "%s   comprimento da matriz" % n(m["comprimento_medido_mm"], 2), ha="right")
        canal = 2 * (perfil[len(perfil) // 2][2] or 0.0)
        print("%s: %d platos, área de material %.1f mm², Ø máx %.2f"
              % (m["chave"], len(es), area, m["Ø_máximo_medido_mm"]))
        nota = ("geometria e cotas: seção e escada medidas no STEP `%s` (aberto só para leitura; "
                "`02_CAD_Modelos_Historicos/` não é modificado - regra 2), publicadas em `%s`.\nA peça é %s. "
                "Corte feito no plano %s - em peça bipartida o plano Y = 0 é o de partição, onde não há seção, "
                "há a face\nde junção das metades. O canal medido nesta seção: Ø %s mm (aparece como faixa "
                "vazia). Ø máx medido %s; comprimento %s;\nombro (fim da banda) em Z = %s."
                % (", ".join(os.path.basename(x) for x in m["_arquivos"]), os.path.basename(PERFIS),
                   "bipartida (A ∪ B)" if m["fonte_do_corpo"] == "A U B" else "de corpo único",
                   plano, n(canal, 2), n(m["Ø_máximo_medido_mm"], 2), n(m["comprimento_medido_mm"], 2),
                   n(m["z_do_ombro_mm"], 2)))
        monta(ax, "%d   %s — vista lateral em corte pelo plano do eixo" % (i, m["nome"]), nota)

    # ============================================================== FAIXA n  MONTAGEM
    def faixa_montagem(ax, m, i):
        curvas_h, area_h, perfil_h, _, plano_h = SC
        curvas, area, perfil, es, plano = m["_secao"]
        desenha_corte(ax, perfil_h, cor="0.2", preenche=False, hachura=False)
        desenha_corte(ax, perfil, cor="tab:blue", espessura=1.7, hachura=True)
        dz = m["encostos"][m["encosto_usado"]]["deslocamento_aplicado_mm"]
        saida = m["comprimento_medido_mm"] + dz
        prot = saida - L_H
        interf = vol_intersecao(m["_corpo"], head)
        col = Coluna(118.0, passo=8.0)
        for j, (d, za, zb) in enumerate(bores):
            chamada_diametro(ax, d / 2.0, 0.5 * (max(za, 0.0) + min(zb, L_H)),
                             "cabeçote  Ø %s" % n(d, 2), col, cor="0.15")
        for j, (z0, z1, d) in enumerate(m["escala_Ø_x_Z_mm"]):
            chamada_diametro(ax, d / 2.0 + 3.0, 0.5 * (z0 + z1) + dz, "matriz  Ø %s" % n(d, 2), col,
                             cor="tab:blue")
        cota_v(ax, min(saida, L_H), L_H, 196.0,
               "%s   saída da matriz %s da face do nariz" % (n(abs(prot), 2), "FORA" if prot > 0 else "DENTRO"))
        cota_v(ax, 0.0, min(saida, L_H), -206.0, "%s   matriz dentro do bolso" % n(min(saida, L_H), 2),
               ha="right")
        cota_h(ax, -pil[0], pil[0], 0.0, -31.0,
               "encosto %s: %s\ninterferência medida matriz ∩ cabeçote: %s mm³ (o STEP da montagem é "
               "composto, sem booleano)"
               % (m["encosto_usado"], "traseira da matriz rasa com o plano mais traseiro do cabeçote"
                  if abs(dz) < 1e-6 else "deslocamento aplicado de %s mm" % n(dz, 2), n(interf, 4)), cor="0.1")
        folga_b = (bores[-1][0] - m["Ø_máximo_medido_mm"]) / 2.0
        nota = ("posição axial definida pelo cabeçote (degrau + fundo do bolso), não pela máquina: folga radial "
                "banda↔bolso %s mm e folga axial no\ndegrau %s mm; encosto usado = `%s` (deslocamento %s mm). "
                "Saída da matriz em Z = %s, ou %s %s da face do nariz (%s).\nCada número desta faixa é medido "
                "nos dois STEP - cabeçote cortado em %s, matriz em %s. A matriz por `%s`, o assento por\n`medir_perfis_matrizes_x_cabecote.py`.\n"
                "A seccao e tomada na uniao A U B, que conserva as cavidades internas seladas do Body_A (1 solido com "
                "3 cascas no arquivo de origem) - e por isso elas aparecem no desenho. O STEP da montagem "
                "entregue entrega as metades separadas, sem booleano (`cabecote_step.json:inventario_dos_arquivos_de_matriz`).\n"
                "Os Ø aqui são os MEDIDOS no STEP da peça - no DXF a banda da matriz coincide com o bolso Ø95 "
                "e o canal é desenhado com 17,00 mm\n(versus os 11,00 mm do furo): ver "
                "`cabecote_ex030.json:matriz_copo_desenhada_no_dxf`."
                % (n(folga_b, 3),
                   n(m["transições_refinadas_mm"]["folga_axial_banda_x_degrau_do_cabecote_mm"], 3),
                   m["encosto_usado"], n(dz, 2), n(saida, 2), n(abs(prot), 2),
                   "para fora" if prot > 0 else "para dentro", n(L_H, 2), plano_h, plano,
                   ", ".join(m["_arquivos"])))
        monta(ax, "%d   MONTAGEM — %s: cabeçote (contorno) + matriz (azul, hachurada), mesmo referencial axial"
              % (i, m["nome"].split("(")[0].strip()), nota)

    from matplotlib.backends.backend_pdf import PdfPages
    os.makedirs(os.path.dirname(a.saida), exist_ok=True)
    paginas = []
    fig, axs = figura(1 + len(mats))
    faixa_cabecote(axs[0])
    for k, m in enumerate(mats):
        faixa_matriz(axs[1 + k], m, 2 + k)
    paginas.append(fig)
    fig, axs = figura(len(mats))
    for k, m in enumerate(mats):
        faixa_montagem(axs[k], m, 1 + k)
    paginas.append(fig)

    with PdfPages(a.saida) as pdf:
        for fig in paginas:
            pdf.savefig(fig)
    print("PDF ->", a.saida, "(%d páginas)" % len(paginas))
    if a.png:
        for k, fig in enumerate(paginas, 1):
            pth = "%s_p%d.png" % (os.path.splitext(a.saida)[0], k)
            fig.savefig(pth, format="png", dpi=120)
            print("PNG ->", pth)
    for fig in paginas:
        plt.close(fig)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
