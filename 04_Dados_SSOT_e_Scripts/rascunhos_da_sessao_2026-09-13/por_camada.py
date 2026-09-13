"""Varre o DXF por camada: conta arestas, lista as INCLINADAS que NAO sao hachura, e mostra os
vertices do contorno perto da aresta externa da face frontal do cabecote (o ponto da seta)."""
import ezdxf, math
from collections import Counter, defaultdict
doc = ezdxf.readfile("/home/user/cabecote.dxf")
msp = doc.modelspace()
K = 25.534
segs = []
def add(x0, y0, x1, y1, layer, color):
    if None in (x0, y0, x1, y1): return
    dx, dy = x1 - x0, y1 - y0
    if abs(dx) < 1e-12 and abs(dy) < 1e-12: return
    a = math.degrees(math.atan2(abs(dy), abs(dx)))          # 0 = horizontal, 90 = vertical
    segs.append(dict(x0=x0*K, y0=y0*K, x1=x1*K, y1=y1*K, ang=a,
                     comp=math.hypot(dx, dy)*K, layer=layer, color=color))
for e in msp:
    t = e.dxftype()
    if t == "LINE":
        add(e.dxf.start.x, e.dxf.start.y, e.dxf.end.x, e.dxf.end.y, e.dxf.layer, e.dxf.color)
    elif t in ("LWPOLYLINE", "POLYLINE"):
        try:
            pts = ([(p[0], p[1]) for p in e.get_points("xy")] if t == "LWPOLYLINE"
                   else [(v.dxf.location.x, v.dxf.location.y) for v in e.vertices])
        except Exception:
            continue
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            add(x0, y0, x1, y1, e.dxf.layer, e.dxf.color)
print("camadas (n de arestas):")
for lay, c in Counter(s["layer"] for s in segs).most_common():
    print(f"   {lay:16s} {c}")
HA = lambda l: "hachura" in l.lower() or "hash" in l.lower()
n = [s for s in segs if not HA(s["layer"]) and 3.0 <= s["ang"] <= 87.0]
print(f"\narestas INCLINADAS fora de camada de hachura: {len(n)}")
for s in sorted(n, key=lambda s: -s["comp"])[:30]:
    print(f"  {s['layer']:12s} cor {s['color']:3d} ang {s['ang']:6.2f} comp {s['comp']:8.3f} mm "
          f"de ({s['x0']:8.2f},{s['y0']:8.2f}) a ({s['x1']:8.2f},{s['y1']:8.2f})")
print("\ncurtas (< 12 mm), que e a faixa de um chanfro:")
for s in sorted([x for x in n if x["comp"] < 12.0], key=lambda s: s["comp"]):
    print(f"  {s['layer']:12s} ang {s['ang']:6.2f} comp {s['comp']:8.3f} mm "
          f"de ({s['x0']:8.2f},{s['y0']:8.2f}) a ({s['x1']:8.2f},{s['y1']:8.2f})")
