"""SO camada 'contorno' na vista do corte (eixo y=657,7 mm; d = x - 42,56 = axial da face frontal).
Imprime a silhueta completa em cima do eixo e marca toda aresta que NAO e horizontal nem vertical."""
import ezdxf, math
K, EIXO, XF = 25.534, 657.7, 42.56
doc = ezdxf.readfile("/home/user/cabecote.dxf"); msp = doc.modelspace()
out = []
for e in msp:
    if e.dxf.layer != "contorno": continue
    t = e.dxftype(); pts = []
    if t == "LINE": pts = [(e.dxf.start.x, e.dxf.start.y), (e.dxf.end.x, e.dxf.end.y)]
    elif t in ("LWPOLYLINE", "POLYLINE"):
        try:
            pts = ([(p[0], p[1]) for p in e.get_points("xy")] if t == "LWPOLYLINE"
                   else [(v.dxf.location.x, v.dxf.location.y) for v in e.vertices])
        except Exception: continue
        if len(pts) > 2: pts = pts + [pts[0]]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if None in (x0, y0, x1, y1): continue
        d0, d1 = (x0-K*0-XF)/1*K, (x1-K*0-XF)/1*K   # x em mm menos XF
        d0, d1 = x0*K-XF, x1*K-XF
        r0, r1 = abs(y0*K-EIXO), abs(y1*K-EIXO)
        dx, dy = abs(d1-d0), abs(r1-r0); L = math.hypot(dx, dy)
        if L < 0.20: continue
        a = math.degrees(math.atan2(dy, dx)) % 180.0
        out.append(dict(d0=min(d0, d1), d1=max(d0, d1), r0=r0, r1=r1, L=L, ang=a))
print(f"arestas 'contorno' no arquivo: {len(out)}")
D = [s for s in out if 1.0 < s["ang"] < 89.0]
print(f"\n### sao {len(D)} arestas INCLINADAS em camada contorno (o resto e H/V). Todas:")
for s in sorted(D, key=lambda s: -s["L"]):
    print(f"  comp {s['L']:7.2f}  ang {s['ang']:6.2f}  de (d {s['d0']:7.2f}, r {s['r0']:6.2f}) a (d {s['d1']:7.2f}, r {s['r1']:6.2f})")
print("\n### silhueta (horizontais: cada raio e onde ha cilindro, com a faixa axial):")
H = [s for s in out if s["ang"] < 1.0]
por_r = {}
for s in H: por_r.setdefault(round(max(s["r0"], s["r1"]), 2), []).append((s["d0"], s["d1"]))
for r in sorted(por_r, reverse=True):
    if r < 20: continue
    faixas = sorted(por_r[r])
    txt = ", ".join(f"{a:.2f}..{b:.2f}" for a, b in faixas[:8])
    print(f"  r={r:7.2f} (O{2*r:7.2f})  d: {txt}")
print("\n### faces axiais (verticais):")
V = [s for s in out if s["ang"] > 89.0]
por_d = {}
for s in V: por_d.setdefault(round(s["d0"], 2), []).append((min(s["r0"], s["r1"]), max(s["r0"], s["r1"])))
for d in sorted(por_d):
    print(f"  d={d:7.2f}  r: " + ", ".join(f"{a:.2f}..{b:.2f}" for a, b in sorted(por_d[d])[:8]))
