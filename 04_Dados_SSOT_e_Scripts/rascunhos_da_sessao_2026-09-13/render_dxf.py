"""Renderiza a folha inteira e recortes em torno das vistas, para OLHAR o desenho (as entidades sao
polilinhas explodeas, sem texto, so geometria)."""
import matplotlib
matplotlib.use("Agg")
import ezdxf, math
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
import matplotlib.pyplot as plt
doc = ezdxf.readfile("/home/user/cabecote.dxf"); msp = doc.modelspace()
ctx = RenderContext(doc)
def salva(nome, xlim=None, ylim=None, px=2200):
    fig = plt.figure(figsize=(px/100, px/100), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_axis_off(); ax.set_facecolor("#000")
    fig.patch.set_facecolor("#000")
    Frontend(ctx, MatplotlibBackend(ax)).draw_layout(msp, finalize=True)
    if xlim: ax.set_xlim(*xlim)
    if ylim: ax.set_ylim(*ylim)
    fig.savefig(nome, facecolor="#000", bbox_inches="tight", pad_inches=0.02)
    plt.close(fig); print("->", nome)
salva("/home/user/tmp/dxf_folha.png")
