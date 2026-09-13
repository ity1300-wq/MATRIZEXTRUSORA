"""Vista do corte do cabecote = eixo y=657,7 mm (pares em +-65/82/101,5/110). Localiza as linhas do
corpo 0130, define d = x - x_da_face frontal, e imprime o QUE EXISTE no canto do passo (r de 60 a 115,
d de -6 a +60) - e la que o desenho mostra o chanfro a 45 que o STEP nao tem."""
import ezdxf, math
K, EIXO = 25.534, 657.7
doc = ezdxf.readfile("/home/user/cabecote.dxf"); msp = doc.modelspace()
se = []
for e in msp:
    t = e.dxftype(); lay = e.dxf.layer
    if "hachura" in lay.lower(): continue
    pts = []
    if t == "LINE": pts = [(e.dxf.start.x, e.dxf.start.y), (e.dxf.end.x, e.dxf.end.y)]
    elif t in ("LWPOLYLINE", "POLYLINE"):
        try:
            pts = ([(p[0], p[1]) for p in e.get_points("xy")] if t == "LWPOLYLINE"
                   else [(v.dxf.location.x, v.dxf.location.y) for v in e.vertices])
        except Exception: continue
        if len(pts) > 2: pts = pts + [pts[0]]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if None in (x0, y0, x1, y1): continue
        X0, Y0, X1, Y1 = x0*K, y0*K, x1*K, y1*K
        R0, R1 = Y0 - EIXO, Y1 - EIXO
        dx, dy = abs(X1-X0), abs(Y1-Y0); L = math.hypot(dx, dy)
        if L < 0.25: continue
        a = math.degrees(math.atan2(abs(R1-R0), abs(X1-X0))) % 180.0
        se.append(dict(L=L, x0=min(X0,X1), x1=max(X0,X1), r0=R0, r1=R1, lay=lay, ang=a))
corpo = [s for s in se if s["lay"] == "contorno" and abs(s["r0"]-65) < 0.6 and abs(s["r1"]-65) < 0.6]
print(f"linhas do corpo 0130 (contorno, r=65): {len(corpo)}")
for s in sorted(corpo, key=lambda s: s["x0"]): print(f"   x {s['x0']:8.2f} .. {s['x1']:8.2f}  comp {s['L']:7.2f}")
if not corpo: raise SystemExit("nenhuma linha do corpo achada")
XF = min(s["x0"] for s in corpo)
print(f"x da face frontal = {XF:.2f} mm  -> d = x - {XF:.2f}")
def tipo(s): return "H" if s["ang"] < 0.3 else ("V" if 89.7 < s["ang"] < 90.3 else "D")
win = [s for s in se if (x0 := s["x0"] - XF) is not None and -6 <= x0 <= 62 and 58 <= max(s["r0"], s["r1"]) <= 116]
print(f"\n### canto do passo: d -6..62, r 58..116 -> {len(win)} arestas")
for s in sorted(win, key=lambda s: (s["x0"], -max(s['r0'], s['r1']))):
    d0, d1 = s["x0"]-XF, s["x1"]-XF
    print(f"  {tipo(s)} d {d0:7.2f}..{d1:7.2f}  r {min(s['r0'],s['r1']):7.2f}..{max(s['r0'],s['r1']):7.2f}"
          f"  comp {s['L']:6.2f} ang {s['ang']:6.2f}  [{s['lay']}]")
