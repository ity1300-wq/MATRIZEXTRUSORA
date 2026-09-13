"""Varre a camada SL35 (camada que o AutoCAD cria para GEOMETRIA DE SECao - SECTIONPLANE/SLICE) do
cabecote.dxf, mais as camadas '0', 'FINA', 'CENTRO' na janela da matriz (r 20..60, d -5..110), para
reconstruir o perfil da matriz COPO como o DESENHO a desenhou dentro do cabecote - que e o que o
usuario diz que esta la, com 'medidas de desenho' (nao as medidas do STEP)."""
import ezdxf, math
from collections import defaultdict

K, EIXO, XF = 25.534, 657.7, 42.56
doc = ezdxf.readfile("/home/user/cabecote.dxf")
msp = doc.modelspace()
por_camada = defaultdict(list)
for e in msp:
    lay = e.dxf.layer
    t = e.dxftype()
    if t == "LINE":
        pts = [(e.dxf.start.x, e.dxf.start.y), (e.dxf.end.x, e.dxf.end.y)]
    elif t in ("LWPOLYLINE", "POLYLINE"):
        try:
            if t == "LWPOLYLINE":
                pts = [(p[0], p[1]) for p in e.get_points("xy")]
            else:
                pts = [(v.dxf.location.x, v.dxf.location.y) for v in e.vertices]
        except Exception:
            continue
        if len(pts) > 2:
            pts = pts + [pts[0]]
    else:
        if t in ("HATCH",):
            por_camada[lay + "::HATCH"].append(("tipo", t))
        continue
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if None in (x0, y0, x1, y1):
            continue
        d0, d1 = x0 * K - XF, x1 * K - XF
        r0, r1 = y0 * K - EIXO, y1 * K - EIXO
        por_camada[lay].append((min(d0, d1), max(d0, d1), min(r0, r1), max(r0, r1),
                                math.degrees(math.atan2(abs(r1 - r0), abs(d1 - d0))) % 180.0))

print("camadas presentes (segmentos):")
for lay in sorted(por_camada, key=lambda l: -len(por_camada[l])):
    print(f"   {lay:24s} {len(por_camada[lay]):6d}")

for lay in sorted(por_camada):
    seg = [x for x in por_camada[lay] if x[0] != "tipo" and -5 <= x[0] <= 110 and abs(x[2]) < 60
           and abs(x[3]) < 60]
    if len(seg) < 3 or len(seg) > 4000:
        continue
    print(f"\n=== camada {lay}: {len(seg)} segmentos na janela da matriz (d -5..110, |r| < 60) ===")
    h = defaultdict(set)
    v = defaultdict(set)
    for a, b, r0, r1, ang in seg:
        if ang < 1.0:
            h[round(0.5 * (r0 + r1), 1)].add((round(a, 2), round(b, 2)))
        elif ang > 89.0:
            v[round(a, 1)].add((round(min(abs(r0), abs(r1)), 2), round(max(abs(r0), abs(r1)), 2)))
    print("  horizontais agrupadas por raio (so as que tem >= 1 segmento com 2 mm ou mais):")
    for rr in sorted(h):
        faixas = sorted(f for f in h[rr] if f[1] - f[0] >= 2.0)
        if not faixas:
            continue
        print(f"    r {rr:7.1f}  (Ø{2*rr:7.2f})  " + "; ".join(f"d {a:.2f}..{b:.2f} ({b-a:.2f})"
                                                                for a, b in faixas[:6]))
    print("  verticais agrupadas por d:")
    for dd in sorted(v):
        faixas = sorted(f for f in v[dd] if f[1] - f[0] >= 1.0)
        if not faixas:
            continue
        print(f"    d {dd:7.1f}   r " + "; ".join(f"{a:.2f}..{b:.2f} ({b-a:.2f})" for a, b in faixas[:6]))
