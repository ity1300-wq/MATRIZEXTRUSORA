"""Reconstrue o contorno do DXF e procura a visao do cabecote pelo par de linhas a +-110 mm do eixo
(flange 0220) / +-65 mm (corpo 0130). Depois imprime TODAS as arestas dessa visao, incluindo diagonais."""
import ezdxf, math
from collections import defaultdict
doc = ezdxf.readfile("/home/user/cabecote.dxf"); msp = doc.modelspace()
K = 25.534
segs = []
for e in msp:
    t = e.dxftype()
    def push(x0, y0, x1, y1):
        if None in (x0, y0, x1, y1): return
        segs.append((x0*K, y0*K, x1*K, y1*K, e.dxf.layer))
    if t == "LINE":
        push(e.dxf.start.x, e.dxf.start.y, e.dxf.end.x, e.dxf.end.y)
    elif t in ("LWPOLYLINE", "POLYLINE"):
        try:
            pts = ([(p[0], p[1]) for p in e.get_points("xy")] if t == "LWPOLYLINE"
                   else [(v.dxf.location.x, v.dxf.location.y) for v in e.vertices])
        except Exception: continue
        for a, b in zip(pts, pts[1:]): push(a[0], a[1], b[0], b[1])
        if len(pts) > 2: push(pts[-1][0], pts[-1][1], pts[0][0], pts[0][1])
print("arestas:", len(segs))
HOR, VER, DIA = [], [], []
for x0, y0, x1, y1, lay in segs:
    dx, dy = abs(x1-x0), abs(y1-y0); L = math.hypot(dx, dy)
    if L < 0.30 or "hachura" in lay.lower(): continue
    a = math.degrees(math.atan2(dy, dx)) % 180.0
    rec = (L, x0, y0, x1, y1, lay, a)
    if a < 0.25 or a > 179.75: HOR.append(rec)
    elif 89.75 < a < 90.25: VER.append(rec)
    else: DIA.append(rec)
print(f"horizontais {len(HOR)} | verticais {len(VER)} | inclinadas {len(DIA)}  (sem hachura, > 0,3 mm)")
# eixo candidato: par de horizontais longas simetricas em +-110 (flange) ou +-65 (corpo)
by_y = defaultdict(list)
for L, x0, y0, x1, y1, lay, a in HOR:
    if L > 25: by_y[round(y0, 1)].append((L, x0, x1, lay))
eixos = defaultdict(list)
for y in sorted(by_y):
    for R in (110.0, 65.0, 82.0, 101.5):
        for yy in (round(y - 2*R, 1), round(y - 2*R, 0)):
            if yy in by_y: eixos[(round((y+yy)/2, 1), R)].append((y, yy))
print("\neixos com par simetrico (y_sup, y_inf) a uma raio R:")
for (y0, R), pares in sorted(eixos.items(), key=lambda kv: -len(kv[1]))[:8]:
    print(f"   eixo y={y0:8.1f}  R={R:6.1f}  pares={len(pares)}  faixas de y: "
          + ", ".join(f"{a:.1f}/{b:.1f}" for a, b in pares[:6]))
