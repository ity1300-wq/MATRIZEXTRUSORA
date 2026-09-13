"""Varre o fim do cabeçote (d > 80) nas duas vistas de secao, SEM truncar, e procura o resalo de 3 mm:
uma aresta horizontal em r ~ 101,5 correndo d 92..95, e a aresta mais traseira da peca."""
import ezdxf, math
K, EIXO, XF = 25.534, 657.7, {1: 42.56, 2: 299.95}
doc = ezdxf.readfile("/home/user/cabecote.dxf"); msp = doc.modelspace()
for v in (1, 2):
    ach = []
    for e in msp:
        if e.dxf.layer not in ("contorno", "centro", "tracejada"): continue
        t = e.dxftype(); pts = []
        if t == "LINE": pts = [(e.dxf.start.x, e.dxf.start.y), (e.dxf.end.x, e.dxf.end.y)]
        elif t in ("LWPOLYLINE", "POLYLINE"):
            try:
                pts = ([(p[0], p[1]) for p in e.get_points("xy")] if t == "LWPOLYLINE"
                       else [(v2.dxf.location.x, v2.dxf.location.y) for v2 in e.vertices])
            except Exception: continue
            if len(pts) > 2: pts = pts + [pts[0]]
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            if None in (x0, y0, x1, y1): continue
            d0, d1 = x0*K-XF[v], x1*K-XF[v]; r0, r1 = abs(y0*K-EIXO), abs(y1*K-EIXO)
            L = math.hypot(abs(d1-d0), abs(r1-r0))
            if L < 0.30 or min(d0, d1) < 80.0 or max(d0, d1) > 105.0: continue
            if max(r0, r1) < 55: continue
            a = math.degrees(math.atan2(abs(r1-r0), abs(d1-d0))) % 180.0
            ach.append((min(d0, d1), max(d0, d1), min(r0, r1), max(r0, r1), L, a, e.dxf.layer))
    print(f"\n=== vista {v}: arestas com d >= 80, r >= 55 ({len(set(ach))}) ===")
    for x in sorted(set(ach)):
        t = "H" if x[5] < 1 else ("V" if x[5] > 89 else f"D{x[5]:.0f}")
        print(f"   {t} d {x[0]:7.2f}..{x[1]:7.2f}  r {x[2]:7.2f}..{x[3]:7.2f}  comp {x[4]:6.2f}  [{x[6]}]")
    if ach:
        print(f"   aresta mais traseira: d = {max(x[1] for x in ach):.2f} mm")
