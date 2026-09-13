"""Procura a MATRIZ deitada dentro da seccao do cabecote no DXF: linhas horizontais nos raios que as duas
etapas da Copo teriam (093 -> r 46,50 / 089,5 -> r 44,75) e o furo dela (075,6 -> r 37,80), mais os
degraus verticais que fecham cada etapa. Vista 1 (EIXO 657,7 / XF 42,56), sem filtro de hachura, anotando
a camada - a camada diz se e contorno da peca ou linha da matriz montada."""
import ezdxf, math

K, EIXO, XF = 25.534, 657.7, 42.56
doc = ezdxf.readfile("/home/user/cabecote.dxf")
msp = doc.modelspace()
seg = []
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
        continue
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if None in (x0, y0, x1, y1):
            continue
        d0, d1 = x0 * K - XF, x1 * K - XF
        r0, r1 = abs(y0 * K - EIXO), abs(y1 * K - EIXO)
        ang = math.degrees(math.atan2(abs(r1 - r0), abs(d1 - d0))) % 180.0
        if math.hypot(abs(d1 - d0), abs(r1 - r0)) < 0.5:
            continue
        seg.append((min(d0, d1), max(d0, d1), min(r0, r1), max(r0, r1), ang, lay))

ALVOS = [(46.50, "093,00 (banda do copo)"), (44.75, "089,50 (2a etapa / canal da fenda)"),
         (37.80, "075,60 (furo de entrada da matriz)"), (47.50, "095,00 (bolso do cabecote)"),
         (45.00, "090,00 (furo de 11)"), (40.00, "080,00 (nariz)"), (52.50, "0105 (piloto)")]
print("### horizontais proximas de cada raio-alvo (d = profundidade contada da face do nariz)")
for alvo, nome in ALVOS:
    ach = set()
    for a, b, r0, r1, ang, lay in seg:
        if ang < 1.0 and abs(r0 - alvo) < 0.55 and abs(r1 - alvo) < 0.55 and -30 < a and b < 200:
            ach.add((round(a, 2), round(b, 2), lay))
    print(f"  r ~ {alvo:5.2f}  {nome}")
    for a, b, lay in sorted(ach)[:10]:
        print(f"        d {a:8.2f} .. {b:8.2f}   comp {b - a:7.2f}   [{lay}]")

print("\n### degraus verticais entre r 36 e 54, com d em 5..110 (as faces das etapas)")
vis = set()
for a, b, r0, r1, ang, lay in seg:
    if ang > 89.0 and a == b and 5 <= a <= 110 and 36 <= r0 and r1 <= 54:
        vis.add((round(a, 2), round(r0, 2), round(r1, 2), lay))
for x in sorted(vis):
    print(f"   V d = {x[0]:7.2f}   r {x[1]:6.2f} .. {x[2]:6.2f}   [{x[3]}]")

print("\n### cotas de texto que pertencem a matriz (procura por '75', '89', '93' em MTEXT/DIMTEXT)")
for e in msp:
    t = e.dxftype()
    if t in ("MTEXT", "TEXT"):
        tx = (e.dxf.text if t == "TEXT" else e.text).replace("\\P", " | ")
        if any(k in tx for k in ("75", "89", "93", "11", "COTA")) and len(tx) < 60:
            x, y = e.dxf.insert.x * K - XF, abs(e.dxf.insert.y * K - EIXO)
            if -40 < x < 210 and y < 200:
                print(f"   '{tx}'  em d {x:8.2f}  r {y:7.2f}  [{e.dxf.layer}]")
