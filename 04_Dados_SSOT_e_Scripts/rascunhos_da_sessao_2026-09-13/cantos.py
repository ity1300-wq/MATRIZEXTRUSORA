"""Recorta a vista do corte em janelas de raio e imprime TUDO (horizontal/vertical/inclinada) - assim um
chanfro num canto aparece como diagonal fechando o canto, ou entao ele nao esta desenhado la."""
import ezdxf, math
K, XFACE = 25.534, 11.7464
doc = ezdxf.readfile("/home/user/cabecote.dxf"); msp = doc.modelspace()
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
        if None in (x0, y0, x1, y1): continue
        d0, d1, r0, r1 = (x0-XFACE)*K, (x1-XFACE)*K, abs(y0)*K, abs(y1)*K
        dx, dy = abs(x1-x0)*K, abs(y1-y0)*K; L = math.hypot(dx, dy)
        if L < 0.25: continue
        a = math.degrees(math.atan2(dy, dx)) % 180.0
        recs.append(dict(L=L, d0=min(d0, d1), d1=max(d0, d1), rmin=min(r0, r1), rmax=max(r0, r1),
                         lay=lay, ang=a))
def janela(nome, r_a, r_b, d_a, d_b):
    sel = [s for s in recs if s["rmax"] >= r_a and s["rmin"] <= r_b and s["d1"] >= d_a and s["d0"] <= d_b]
    print(f"\n### {nome}: raio {r_a}..{r_b} mm, axial d {d_a}..{d_b} mm -> {len(sel)} arestas")
    for s in sorted(sel, key=lambda s: (s["d0"], -s["rmax"]))[:46]:
        tipo = "HORIZ" if (s["ang"] < 0.3 or s["ang"] > 179.7) else ("VERT " if 89.7 < s["ang"] < 90.3 else "INCL ")
        print(f"   {tipo} d {s['d0']:7.2f}..{s['d1']:7.2f}  r {s['rmin']:7.2f}..{s['rmax']:7.2f} "
              f" comp {s['L']:6.2f} ang {s['ang']:6.2f}  [{s['lay']}]")
janela("CANTO EXTERNO DA FACE FRONTAL (corpo 0130, d=0)", 58, 72, -3, 12)
janela("ROSTO DO NARIZ (080 -> 090, d ~ 14) ", 36, 50, 8, 22)
janela("DEGRAU / BOLO 090 -> 095 (d ~ 25)", 44, 52, 20, 32)
janela("SAIDA TRASEIRA DO BOLO (d ~ 92..95)", 44, 60, 88, 100)
