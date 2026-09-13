"""Vista 1 (unica onde a traseira sai limpa): TUDO com d em 86..100, qualquer raio; e o alcance axial
do furo 0105 (r ~ 52,5) e do bolso 095 (r ~ 47,5)."""
import ezdxf, math
K, EIXO, XF = 25.534, 657.7, 42.56
doc = ezdxf.readfile("/home/user/cabecote.dxf"); msp = doc.modelspace()
alvo = []
for e in msp:
    lay = e.dxf.layer
    if "hachura" in lay.lower() or lay in ("centro",): continue
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
        d0, d1 = x0*K-XF, x1*K-XF; r0, r1 = abs(y0*K-EIXO), abs(y1*K-EIXO)
        L = math.hypot(abs(d1-d0), abs(r1-r0))
        if L < 0.30: continue
        alvo.append((min(d0, d1), max(d0, d1), min(r0, r1), max(r0, r1), L,
                     math.degrees(math.atan2(abs(r1-r0), abs(d1-d0))) % 180.0, lay))
alvo = sorted(set(alvo))
print("### arestas com d em 86..100 (qualquer raio), camada de contorno/tracejada/0")
for x in [a for a in alvo if a[0] <= 100 and a[1] >= 86 and a[6] in ("contorno", "tracejada")]:
    t = "H" if x[5] < 1 else ("V" if x[5] > 89 else f"D{x[5]:.0f}")
    print(f"   {t} d {x[0]:7.2f}..{x[1]:7.2f}  r {x[2]:7.2f}..{x[3]:7.2f}  comp {x[4]:6.2f}  [{x[6]}]")
print("\n### alcances axiais dos furos (horizontais em r proximo de 47,5 = 095 e 52,5 = 0105)")
for alvo_r, nome in ((47.5, "095 (bolso)"), (52.5, "0105"), (45.0, "090 (degrau)"), (40.0, "080 (nariz)")):
    faixas = sorted({(x[0], x[1]) for x in alvo if x[5] < 1 and abs(x[2]-alvo_r) < 0.6 and abs(x[3]-alvo_r) < 0.6})
    txt = ", ".join(f"{a:.2f}..{b:.2f}" for a, b in faixas) or "(nenhuma)"
    print(f"   r ~ {alvo_r:5.2f} mm  {nome:14s} d: {txt}")
print("\n### face mais traseira da peca em cada camada")
for lay in ("contorno", "tracejada"):
    s = [x for x in alvo if x[6] == lay]
    print(f"   {lay:11s}: d_max = {max((x[1] for x in s), default=float('nan')):.2f} mm  |  arestas com d>93: "
          f"{[(round(x[0],2), round(x[1],2), round(x[2],1), round(x[3],1)) for x in s if x[0] > 93][:6]}")
