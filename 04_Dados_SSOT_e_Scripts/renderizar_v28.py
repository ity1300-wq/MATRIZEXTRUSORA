"""
RENDERIZACAO DE CONFERENCIA - MATRIZ JONATHA v28.0 (e v27.0, para comparar)
============================================================================
Nao usa GPU nem servidor de visualizacao: tesseliza os STEP e projecta em
ortogonal com matplotlib, numa figura de 6 vistas. Serve para conferir com o
olho o que o verificador mediu (furos presentes, chanfro novo, sem bolha
selada). headless por natureza.

Uso: python 04_Dados_SSOT_e_Scripts/renderizar_v28.py [--saida arquivo.png]
"""

import argparse
import math
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import cadquery as cq

from matplotlib.collections import PolyCollection

from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.BRep import BRep_Tool
from OCP.TopAbs import TopAbs_FACE
from OCP.TopExp import TopExp_Explorer
from OCP.TopLoc import TopLoc_Location
from OCP.TopoDS import TopoDS

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DIR_CAD = os.path.join(RAIZ, "07_CAD_Matrizes", "M01_Jonatha_v27_OFICIAL")
DIR_V28 = os.path.join(RAIZ, "07_CAD_Matrizes", "M02_Jonatha_v28_PROPOSTA")

def _pasta_matriz(nome):
    """Arquivo com _v28 no nome mora na pasta da proposta; o resto e o master."""
    return DIR_V28 if "_v28" in nome else DIR_CAD
EIXOS = {"saida_Z": (0, 1), "long_Y": (0, 2), "lado_X": (1, 2)}  # (h, v)


def triangulos(solido, deflexao=0.15):
    """Lista de polígonos (N,3,3) em coordenadas do sólido."""
    shp = solido.wrapped if hasattr(solido, "wrapped") else solido
    BRepMesh_IncrementalMesh(shp, deflexao, False, 0.35, True)
    out, exp = [], TopExp_Explorer(shp, TopAbs_FACE)
    while exp.More():
        face = TopoDS.Face_s(exp.Current())
        loc = TopLoc_Location()
        tri = BRep_Tool.Triangulation_s(face, loc)
        if tri is not None:
            trsf = loc.Transformation()
            nod = np.array([[tri.Node(i).Transformed(trsf).X(),
                             tri.Node(i).Transformed(trsf).Y(),
                             tri.Node(i).Transformed(trsf).Z()] for i in range(1, tri.NbNodes() + 1)])
            for k in range(1, tri.NbTriangles() + 1):
                t = tri.Triangle(k)
                out.append(nod[[t.Value(1) - 1, t.Value(2) - 1, t.Value(3) - 1]])
        exp.Next()
    return np.array(out)


def carregar(nome):
    return cq.importers.importStep(os.path.join(_pasta_matriz(nome), nome))


def principal(solidos):
    """Solido externo = uniao dos corpos; o canal e desenhado atras, em azul."""
    return solidos


def desenhar(ax, tris, proj, inverter_v=True, cor="#8f9aa8", alpha=1.0, edge="#20262c"):
    h, v = EIXOS[proj]
    poly = tris[:, :, [h, v]].copy()
    if inverter_v:
        poly[:, :, 1] = -poly[:, :, 1]
    ax.add_collection(PolyCollection(poly, facecolors=cor, edgecolors=edge,
                                     linewidths=0.15, alpha=alpha))
    lo = np.nanmin(poly.reshape(-1, 2), axis=0) - 2
    hi = np.nanmax(poly.reshape(-1, 2), axis=0) + 2
    ax.set_xlim(lo[0], hi[0])
    ax.set_ylim(lo[1], hi[1])
    ax.set_aspect("equal")
    ax.set_title(f"{proj}", fontsize=9)
    ax.axis("off")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--saida", default=os.path.join(RAIZ, "v28_conferencia.png"))
    ap.add_argument("--sufixo", default="_v28")
    a = ap.parse_args()
    sfx = a.sufixo

    A = max(carregar(f"MatrizJonatha{sfx}_Body_A.step").solids().vals(), key=lambda x: x.Volume())
    B = max(carregar(f"MatrizJonatha{sfx}_Body_B.step").solids().vals(), key=lambda x: x.Volume())
    CH = carregar(f"MatrizJonatha{sfx}_Canal_Fluxo.step").solids().vals()
    canal = max(CH, key=lambda x: x.Volume())
    aco = A.fuse(B)
    # meia-secao real: remove a metade Y>0 para enxergar o funil por dentro
    semidie = maior(A)
    t_aco, t_semi, t_b, t_c = (triangulos(aco), triangulos(semidie), triangulos(B),
                              triangulos(canal))

    fig, axs = plt.subplots(2, 3, figsize=(20, 12))
    fig.patch.set_facecolor("#11151a")
    cor_aco, cor_canal, aresta = "#9aa6b4", "#1f7ac0", "#161b20"

    ax = axs[0][0]
    desenhar(ax, t_aco, "saida_Z", cor=cor_aco, edge=aresta)
    ax.add_collection(PolyCollection(t_c[:, :, [0, 1]], facecolors=cor_canal,
                                     edgecolors="#0d3550", linewidths=0.2, alpha=0.9))
    ax.set_title("1 · VISTA DE SAÍDA (olhando −Z) — fenda, chanfro e lábio", fontsize=10, color="w")

    ax = axs[0][1]
    desenhar(ax, t_aco, "long_Y", cor=cor_aco, edge=aresta)
    ax.add_collection(PolyCollection(t_c[:, :, [0, 2]], facecolors=cor_canal,
                                     edgecolors="#0d3550", linewidths=0.2, alpha=0.55))
    ax.set_title("2 · LONGITUDINAL (olhando −Y) — funil, land 9,20 e chanfro 0,80",
                 fontsize=10, color="w")

    ax = axs[0][2]
    desenhar(ax, t_semi, "long_Y", cor=cor_aco, edge=aresta)
    ax.add_collection(PolyCollection(t_c[:, :, [0, 2]], facecolors=cor_canal,
                                     edgecolors="#0d3550", linewidths=0.2, alpha=0.85))
    ax.set_title("3 · MEIA-SEÇÃO Y>0 removida — interior do canal (só Body_A)",
                 fontsize=10, color="w")

    for ax, t, titulo, cor in [
        (axs[1][0], t_aco, "4 · AÇO COMPLETO (X-Z) — 14 furos: 4 pinos, 6 cartuchos, 4 TCs", cor_aco),
        (axs[1][1], triangulos(B), "5 · Body_B sozinho (X-Z) — furos conjugados ao Body_A", cor_aco),
        (axs[1][2], t_c, "6 · Canal de fluxo isolado (1 sólido, p/ EDM e CFD)", cor_canal)]:
        desenhar(ax, t, "long_Y", cor=cor, edge=aresta if cor == cor_aco else "#0d3550")
        ax.set_title(titulo, fontsize=10, color="w")

    fig.suptitle(f"Matriz Jonatha {sfx} — conferência visual (lida dos STEP oficiais)",
                 color="w", fontsize=13)
    for ax in axs.ravel():
        ax.set_facecolor("#11151a")
    fig.tight_layout()
    fig.savefig(a.saida, dpi=130, facecolor=fig.get_facecolor(), bbox_inches="tight")
    print("->", a.saida, os.path.getsize(a.saida), "bytes")


def maior(forma):
    from OCP.TopAbs import TopAbs_SOLID
    from OCP.TopExp import TopExp_Explorer
    shp = forma.wrapped if hasattr(forma, "wrapped") else forma
    exp, melhor, mv = TopExp_Explorer(shp, TopAbs_SOLID), None, -1.0
    while exp.More():
        s = cq.Solid(exp.Current())
        if s.Volume() > mv:
            melhor, mv = s, s.Volume()
        exp.Next()
    return melhor if melhor is not None else forma


if __name__ == "__main__":
    main()
