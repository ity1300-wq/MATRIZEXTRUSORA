"""Gera o DESENHO 2D em PDF das duas peças - o cabeçote EX-030 e a Matriz 1 Copo - em VISTA LATERAL
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

Vistas: 1) cabeçote  2) matriz  3) montagem (a matriz sentada onde o booleano manda: face de entrada rasa
com o plano mais traseiro do cabeçote - o "face a face", medido 0,000 mm pelo verificador de interface).

Uso:
  python 04_Dados_SSOT_e_Scripts/gerar_desenho_2d_cabecote_matriz.py [--png] [--saida x.pdf]
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
PERFIS = os.path.join(AQUI, "perfis_matrizes_x_cabecote.json")

from verificar_interface_cabecote import CORPO, BORES, CHAMFRO, Z_FACE_NARIZ, n  # noqa: E402

matplotlib.rcParams["font.size"] = 8
matplotlib.rcParams["font.family"] = "DejaVu Sans"
SOLIDO_CORTE = 0.10          # passo da varredura que define o perfil de corte (mm)


# ------------------------------------------------------------------ seccao do STEP
def curvas_de_corte(solido, y=0.0, deflexao=0.05):
    """Todas as curvas da seccao do solido pelo plano Y = y (une todas as faces planas do booleano)."""
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
    from OCP.BRepAdaptor import BRepAdaptor_Curve
    from OCP.GCPnts import GCPnts_UniformDeflection
    from OCP.TopAbs import TopAbs_FACE
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopoDS import TopoDS
    meio = cq.Solid.makeBox(3000, 2000, 3000, cq.Vector(-1500, -2000.0 + y, -1500))
    b = BRepAlgoAPI_Common(solido.wrapped, meio.wrapped)
    b.Build()
    if not b.IsDone():
        raise RuntimeError("corte do solido falhou")
    curvas, area = [], 0.0
    ex = TopExp_Explorer(b.Shape(), TopAbs_FACE)
    while ex.More():
        fc = cq.Face(TopoDS.Face_s(ex.Current()))
        try:
            if abs(fc.BoundingBox().ylen) < 1e-9:
                area += fc.Area()
                for w in fc.Wires():
                    for e in w.Edges():
                        ad = BRepAdaptor_Curve(TopoDS.Edge_s(e.wrapped))
                        d = GCPnts_UniformDeflection(ad, deflexao)
                        if d.IsDone() and d.NbPoints() > 1:
                            curvas.append([(d.Value(i).X(), d.Value(i).Z())
                                           for i in range(1, d.NbPoints() + 1)])
        except Exception:
            pass
        ex.Next()
    if not curvas:
        raise RuntimeError("nenhuma curva de seção em Y = %.3f" % y)
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--saida", default=os.path.join(DIR_CAB, "DESENHO_2D_CABECOTE_X_MATRIZ_COPO.pdf"))
    ap.add_argument("--png", action="store_true")
    ap.add_argument("--cabecote", default=os.path.join(DIR_CAB, "Cabecote_EX-030_desenhado.step"))
    ap.add_argument("--matriz", default=os.path.join(DIR_HIS, "Matriz1_Original_Copo_Solido.step"))
    ap.add_argument("--chave-matriz", default="matriz_1_copo")
    a = ap.parse_args()

    if not os.path.exists(PERFIS):
        sys.exit("falta %s\nrode antes: python 04_Dados_SSOT_e_Scripts/medir_perfis_matrizes_x_cabecote.py --json"
                 % os.path.relpath(PERFIS, RAIZ))
    prof_mat = json.load(open(PERFIS, encoding="utf-8"))
    m = next(x for x in prof_mat["matrizes"] if x["chave"] == a.chave_matriz)
    cab = json.load(open(os.path.join(AQUI, "cabecote_ex030.json"), encoding="utf-8"))["corpo"]
    chan = cab["chanfro_corpo_flange"]

    head = max(cq.importers.importStep(a.cabecote).val().Solids(), key=lambda s: s.Volume())
    die = max(cq.importers.importStep(a.matriz).val().Solids(), key=lambda s: s.Volume())
    ch_c, ch_a = curvas_de_corte(head)
    cd_c, cd_a = curvas_de_corte(die)
    bh, bd = head.BoundingBox(), die.BoundingBox()
    ph = perfil_corte(ch_c, bh.zmin, bh.zmax)
    pd_ = perfil_corte(cd_c, bd.zmin, bd.zmax)
    eh, ed = escada(ph), escada(pd_)
    print("cabeçote (seção: %d curvas, material %.1f mm2) platos:" % (len(ch_c), ch_a))
    for p in eh:
        print("   Z %7.2f..%7.2f  r_ext %7.3f  r_furo %s" % (p[0], p[1], p[2],
                                                              "-" if p[3] is None else "%6.3f" % p[3]))
    print("matriz (seção: %d curvas, material %.1f mm2) platos:" % (len(cd_c), cd_a))
    for p in ed:
        print("   Z %7.2f..%7.2f  r_ext %7.3f  r_furo %s" % (p[0], p[1], p[2],
                                                              "-" if p[3] is None else "%6.3f" % p[3]))

    L_H = Z_FACE_NARIZ
    bores = sorted([(2 * r, za, zb) for (r, za, zb) in BORES], key=lambda t: -t[1])
    fl, pil, corpo = CORPO[1], CORPO[2], CORPO[0]
    rc0, zc0, rc1, zc1 = CHAMFRO
    fig, axs = plt.subplots(3, 1, figsize=(16.54, 11.69))
    plt.subplots_adjust(left=0.025, right=0.985, top=0.965, bottom=0.03, hspace=0.66)
    XL = (-272.0, 252.0)

    def monta(ax, titulo, nota):
        ax.set_xlim(*XL)
        ax.set_aspect("equal", adjustable="datalim")
        ax.axis("off")
        ax.set_title(titulo, fontsize=10.5, loc="left", pad=7)
        ax.text(0.0, -0.155, nota, transform=ax.transAxes, fontsize=7.0, va="top", color="0.2")

    # ============================================================== 1  CABECOTE
    ax = axs[0]
    desenha_corte(ax, ph)
    desenha_arestas(ax, ch_c)
    col = Coluna(118.0, passo=6.5)
    for i, (d, za, zb) in enumerate(bores):
        chamada_diametro(ax, d / 2.0, 0.5 * (max(za, 0.0) + min(zb, L_H)),
                         "Ø %s   furo %d do cabeçote" % (n(d, 2), i + 1), col, cor="tab:blue")
    chamada_diametro(ax, corpo[0], 0.5 * (corpo[1] + corpo[2]),
                     "Ø %s   corpo" % n(2 * corpo[0], 2), col)
    chamada_diametro(ax, fl[0], 0.5 * (fl[1] + fl[2]), "Ø %s   flange" % n(2 * fl[0], 2), col)
    chamada_diametro(ax, pil[0], 0.5 * (pil[1] + pil[2]),
                     "Ø %s   piloto de centragem" % n(2 * pil[0], 2), col, cor="tab:purple")
    # correntes de comprimento vao para a ESQUERDA: a direita e dos rotulos de diametro, e as duas
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
    nota1 = ("geometria: seção do STEP `%s` (arestas reais, cinza fino) e perfil de corte medido dele fatia "
             "a fatia (preto, hachurado). Z = 0 no plano mais\ntraseiro da peça; face do nariz em Z = %s. "
             "Cotas: `cabecote_ex030.json` e `verificar_interface_cabecote.py` - os mesmos dados com que este "
             "STEP foi construído.\nNão aparecem neste corte por acaso do plano, não por omissão: as 6 fendas "
             "do flange e os 6 × Ø16,50 (M12) em C.C. Ø180,00." % (os.path.basename(a.cabecote), n(L_H, 2)))
    monta(ax, "1   CABEÇOTE EX-030 — vista lateral em corte pelo plano do eixo", nota1)

    # ============================================================== 2  MATRIZ
    ax = axs[1]
    desenha_corte(ax, pd_)
    desenha_arestas(ax, cd_c)
    col = Coluna(80.0, passo=7.0)
    for i, (z0, z1, d) in enumerate(m["escala_Ø_x_Z_mm"]):
        chamada_diametro(ax, d / 2.0, 0.5 * (z0 + z1),
                         "Ø %s   estágio %d  (Z %s → %s)" % (n(d, 2), i + 1, n(z0, 2), n(z1, 2)),
                         col, cor="tab:blue")
    for i, (z0, z1, d) in enumerate(m["escala_Ø_x_Z_mm"]):
        cota_v(ax, z0, z1, -124.0 - 16 * i, n(z1 - z0, 2), cor="tab:blue", ha="right")
    fb = m["transições_refinadas_mm"].get("fim_da_banda_093_em_Z")
    if fb is not None:
        cota_v(ax, 0.0, fb, -156.0 - 16 * len(m["escala_Ø_x_Z_mm"]),
               "%s   banda até o ombro" % n(fb, 3), cor="0.1", ha="right")
    cota_v(ax, 0.0, m["comprimento_medido_mm"], -196.0,
           "%s   comprimento da matriz" % n(m["comprimento_medido_mm"], 2), ha="right")
    canal = 2 * (pd_[len(pd_) // 2][2] or 0.0)
    nota2 = ("geometria e cotas: seção e escada medidas no STEP `%s` (aberto só para leitura; "
             "`02_CAD_Modelos_Historicos/` não é modificado - regra 2), publicadas em `%s`.\nA peça é "
             "bipartida e o corte passa pelo centro do canal da fenda: o canal de %s mm aparece como faixa "
             "vazia e as duas metades se sobrepõem nesta\nvista. Ø máx medido %s; comprimento %s; ombro (fim "
             "da banda) em Z = %s." % (os.path.basename(a.matriz), os.path.basename(PERFIS), n(canal, 2),
                                       n(m["Ø_máximo_medido_mm"], 2), n(m["comprimento_medido_mm"], 2),
                                       n(m["z_do_ombro_mm"], 2)))
    monta(ax, "2   %s — vista lateral em corte pelo plano do eixo" % m["nome"], nota2)

    # ============================================================== 3  MONTAGEM
    ax = axs[2]
    desenha_corte(ax, ph, cor="0.2", preenche=False, hachura=False)
    desenha_corte(ax, pd_, cor="tab:blue", espessura=1.7, hachura=True)
    dz = m["encostos"][m["encosto_usado"]]["deslocamento_aplicado_mm"]
    saida = m["comprimento_medido_mm"] + dz
    prot = saida - L_H
    col = Coluna(118.0, passo=8.0)
    for i, (d, za, zb) in enumerate(bores):
        chamada_diametro(ax, d / 2.0, 0.5 * (max(za, 0.0) + min(zb, L_H)),
                         "cabeçote  Ø %s" % n(d, 2), col, cor="0.15")
    for i, (z0, z1, d) in enumerate(m["escala_Ø_x_Z_mm"]):
        chamada_diametro(ax, d / 2.0 + 3.0, 0.5 * (z0 + z1) + dz, "matriz  Ø %s" % n(d, 2), col,
                         cor="tab:blue")
    cota_v(ax, min(saida, L_H), L_H, 196.0,
           "%s   saída da matriz %s da face do nariz" % (n(abs(prot), 2),
                                                          "FORA" if prot > 0 else "DENTRO"))
    cota_v(ax, 0.0, min(saida, L_H), -206.0, "%s   matriz dentro do bolso" % n(min(saida, L_H), 2),
           ha="right")
    cota_h(ax, -pil[0], pil[0], 0.0, -21.0,
           "encosto face a face: traseira da matriz rasa com o plano mais traseiro do cabeçote (medido "
           "0,000 mm)\no piloto Ø %s × %s protrai atrás da face do flange - é aí que a máquina precisa do "
           "rebaixo correspondente" % (n(2 * pil[0], 2), n(pil[2] - pil[1], 2)), cor="0.1")
    dif = prof_mat["diferença_copo_x_gedeon_medida"]
    nota3 = ("a posição axial da matriz é definida pelo cabeçote (degrau + fundo do bolso), não pela máquina: "
             "folga radial banda↔bolso %s mm e folga axial no degrau\n%s mm. A Copo desemboca %s mm %s da "
             "face do nariz - é o que você observou na saída, e o valor é a diferença de comprimento entre as "
             "matrizes:\nna Copo falta o nariz de %s mm que a Gedeon, a Desenvolvimento e a Jonatha têm "
             "(medido em `perfis_matrizes_x_cabecote.json`)."
             % (n((bores[-1][0] - m["Ø_máximo_medido_mm"]) / 2.0, 3),
                n(m["transições_refinadas_mm"]["folga_axial_banda_x_degrau_do_cabecote_mm"], 3),
                n(abs(prot), 2), "para fora" if prot > 0 else "para dentro",
                n(dif["diferença_mm"], 2)))
    monta(ax, "3   MONTAGEM — cabeçote (contorno) + matriz (azul, hachurada), no mesmo referencial axial",
          nota3)

    print("chanfro desenhado: Z %.2f..%.2f de r %.2f a r %.2f" % (zc0, zc1, rc0, rc1))
    os.makedirs(os.path.dirname(a.saida), exist_ok=True)
    fig.savefig(a.saida, format="pdf")
    print("PDF ->", a.saida)
    if a.png:
        pth = a.saida[:-4] + ".png"
        fig.savefig(pth, format="png", dpi=120)
        print("PNG ->", pth)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
