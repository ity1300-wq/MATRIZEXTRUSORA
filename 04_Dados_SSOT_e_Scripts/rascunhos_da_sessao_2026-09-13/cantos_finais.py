"""Varre TUDO (todas as camadas, sem corte de comprimento) em janelas pequenas ao redor dos cantos das
duas vistas do corte do cabecote. d = axial desde a face frontal de cada vista."""
import ezdxf, math
K, EIXO = 25.534, 657.7
XF = {1: 42.56, 2: 299.95}          # x da face frontal em cada vista (mm do desenho)
doc = ezdxf.readfile("/home/user/cabecote.dxf"); msp = doc.modelspace()
brutos = []
for e in msp:
    t = e.dxftype(); lay = e.dxf.layer
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
        brutos.append((x0*K, y0*K, x1*K, y1*K, lay, t))
def janela(visao, d_a, d_b, r_a, r_b, nome):
    x0f = XF[visao]
    sel = []
    for X0, Y0, X1, Y1, lay, t in brutos:
        d0, d1 = X0-x0f, X1-x0f
        r0, r1 = abs(Y0-EIXO), abs(Y1-EIXO)
        if not (min(d0, d1) <= d_b and max(d0, d1) >= d_a): continue
        if not (min(r0, r1) <= r_b and max(r0, r1) >= r_a): continue
        L = math.hypot(d1-d0, r1-r0); a = math.degrees(math.atan2(abs(r1-r0), abs(d1-d0))) % 180.0
        if L < 0.05: continue
        sel.append((min(d0, d1), max(d0, d1), min(r0, r1), max(r0, r1), L, a, lay, t))
    sel = sorted(set(sel), key=lambda s: (s[0], -s[3]))
    print(f"\n### vista {visao} - {nome}: d {d_a}..{d_b}, r {r_a}..{r_b} -> {len(sel)} arestas")
    for d0, d1, r0, r1, L, a, lay, t in sel[:34]:
        tpg = "H" if a < 1 else ("V" if a > 89 else "D")
        print(f"   {tpg} d {d0:6.2f}..{d1:6.2f}  r {r0:6.2f}..{r1:6.2f}  comp {L:5.2f} ang {a:6.2f}  [{lay}|{t}]")
for v in (1, 2):
    janela(v, -2, 8, 58, 70, "CANTO EXTERNO DA FACE FRONTAL")
    janela(v, 36, 58, 58, 115, "PASSO CORPO -> FLANGE/CUBO")
    janela(v, 86, 100, 58, 115, "RESSALO / ARESTA TRASEIRA DA FLANGE")
    janela(v, -2, 30, 36, 50, "BOCA DO NARIZ (080 / 090)")

print("\n\n########## CONFIRMACAO NA VISTA 2 (a que voce imprimiu) ##########")
for nome, da, db, ra, rb in [("corpo -> face do flange", 36, 58, 60, 116), ("tras: fim do flange", 88, 102, 60, 116),
                             ("face frontal", -3, 8, 38, 70)]:
    janela(2, da, db, ra, rb, nome)
