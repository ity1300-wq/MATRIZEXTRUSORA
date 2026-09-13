"""Varre SO a vista do corte do cabecote (eixo y=0, face d=0 em x=11,7464 un).
d = distancia axial da face do nariz (mm), r = raio acima do eixo (mm). Arestas a 45 = chanfros."""
import ezdxf, math
K, XFACE = 25.534, 11.7464
doc = ezdxf.readfile("/home/user/cabecote.dxf"); msp = doc.modelspace()
def dentro(x, y):
    return XFACE - 0.6 <= x <= XFACE + 95.5/K and -5.4 <= y <= 5.4
recs = []
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
        if None in (x0, y0, x1, y1) or not (dentro(x0, y0) and dentro(x1, y1)): continue
        d0, d1 = (x0-XFACE)*K, (x1-XFACE)*K
        r0, r1 = abs(y0)*K, abs(y1)*K
        dx, dy = abs(x1-x0)*K, abs(y1-y0)*K
        L = math.hypot(dx, dy)
        if L < 0.30: continue
        a = math.degrees(math.atan2(dy, dx)) % 180.0
        recs.append(dict(L=L, d0=min(d0, d1), d1=max(d0, d1), r0=r0, r1=r1, lay=lay, ang=a))
print(f"arestas na vista do corte: {len(recs)}")
H = sorted([r for r in recs if r["ang"] < 0.3 or r["ang"] > 179.7], key=lambda s: (-max(s["r0"], s["r1"]), s["d0"]))
V = sorted([r for r in recs if 89.7 < r["ang"] < 90.3], key=lambda s: (s["d0"], -s["r0"]))
D = sorted([r for r in recs if 3.0 < r["ang"] < 87.0], key=lambda s: -s["L"])
print(f"\n=== cilindros (arestas horizontais): raio, faixa axial ===")
for s in H[:34]:
    print(f"  r={max(s['r0'],s['r1']):7.2f}  d de {s['d0']:7.2f} a {s['d1']:7.2f}  [{s['lay']}]")
print(f"\n=== faces axiais (verticais): d, faixa de raio ===")
for s in V[:40]:
    print(f"  d={s['d0']:7.2f}  r de {min(s['r0'],s['r1']):7.2f} a {max(s['r0'],s['r1']):7.2f}  [{s['lay']}]")
print(f"\n=== INCLINADAS (candidatas a chanfro/cone) ===")
for s in D[:30]:
    print(f"  comp {s['L']:7.3f}  ang {s['ang']:6.2f}  de (d {s['d0']:7.2f}, r {s['r0']:6.2f}) "
          f"a (d {s['d1']:7.2f}, r {s['r1']:6.2f})  [{s['lay']}]")
