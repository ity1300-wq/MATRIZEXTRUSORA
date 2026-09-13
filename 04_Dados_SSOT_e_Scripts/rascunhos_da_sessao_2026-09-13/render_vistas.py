import matplotlib; matplotlib.use("Agg")
import ezdxf
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
import matplotlib.pyplot as plt
K, EIXO, XF = 25.534, 657.7, 42.56
doc = ezdxf.readfile("/home/user/cabecote.dxf"); msp = doc.modelspace(); ctx = RenderContext(doc)
def salva(nome, d0, d1, raio_max, nota):
    xlim = ((XF + d0)/K, (XF + d1)/K); ylim = ((EIXO - raio_max)/K, (EIXO + raio_max)/K)
    fig = plt.figure(figsize=(16, 11), dpi=110); ax = fig.add_axes([0, 0, 1, 1])
    ax.set_axis_off(); ax.set_facecolor("#101010"); fig.patch.set_facecolor("#101010")
    Frontend(ctx, MatplotlibBackend(ax)).draw_layout(msp, finalize=True)
    ax.set_xlim(*xlim); ax.set_ylim(*ylim)
    fig.savefig(nome, facecolor="#101010"); plt.close(fig); print("->", nome, "|", nota)
salva("/home/user/tmp/vista1.png", -34, 96, 132, "vista com a linha do corpo em d 0..42")
salva("/home/user/tmp/vista2.png", 299.95-34- XF, 299.95+96-XF, 132, "segunda vista com corpo 0130 em d 0..42")
salva("/home/user/tmp/vista1_zoom.png", -8, 40, 78, "zoom no canto frontal da vista 1")
