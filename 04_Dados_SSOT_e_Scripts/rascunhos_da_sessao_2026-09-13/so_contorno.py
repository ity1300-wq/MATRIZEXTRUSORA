import ezdxf, math
doc = ezdxf.readfile("/home/user/cabecote.dxf"); msp = doc.modelspace()
K, EIXO = 25.534, 657.7
recs = []
for e in msp:
    t = e.dxftype(); lay = e.dxf.layer
    if "hachura" in lay.lower() or "isolante" in lay.lower(): continue
    def push(x0, y0, x1, y1):
        if None in (x0, y0, x1, y1): return
        X0, Y0, X1, Y1 = x0*K, y0*K, x1*K, y1*K
        dx, dy = abs(X1-X0), abs(Y1-Y0); L = math.hypot(dx, dy)
        if L < 0.4: return
        a = math.degrees(math.atan2(dy, dx)) % 180.0
        recs.append((L, X0, Y0, X1, Y1, lay, a))
    if t == "LINE": push(e.dxf.start.x, e.dxf.start.y, e.dxf.end.x, e.dxf.end.y)
    elif t in ("LWPOLYLINE", "POLYLINE"):
        try:
            pts = ([(p[0], p[1]) for p in e.get_points("xy")] if t == "LWPOLYLINE"
                   else [(v.dxf.location.x, v.dxf.location.y) for v in e.vertices])
        except Exception: continue
        for a_, b_ in zip(pts, pts[1:]): push(a_[0], a_[1], b_[0], b_[1])
        if len(pts) > 2: push(pts[-1][0], pts[-1][1], pts[0][0], pts[0][1])
# so o que esta na meia-secao superior do cabecote: r entre 25 e 130 acima do eixo
meia = [r for r in recs if 25.0 <= min(r[2], r[4]) - EIXO or (25 <= r[2]-EIXO <= 130 or 25 <= r[4]-EIXO <= 130)]
print("=== contornos HORIZONTAIS na meia-secao (r de 25 a 130 acima do eixo) ===")
H = sorted([r for r in recs if (r[6] < 0.25 or r[6] > 179.75) and 25 <= abs(r[2]-EIXO) <= 130
            and abs(r[2]-EIXO) == max(abs(r[2]-EIXO), abs(r[4]-EIXO))], key=lambda s: min(s[1], s[3]))
for L, x0, y0, x1, y1, lay, a in H:
    print(f"  x {min(x0,x1):7.2f} .. {max(x0,x1):7.2f}  r={y0-EIXO:7.2f}  [{lay}]")
print("\n=== contornos VERTICAIS (faces axiais) na mesma faixa ===")
V = sorted([r for r in recs if 89.75 < r[6] < 90.25 and min(abs(y0 := (r[2]-EIXO), r[4]-EIXO)) >= 20], key=lambda s: s[1])
for L, x0, y0, x1, y1, lay, a in V:
    if not (20 <= abs(y0) <= 140): continue
    print(f"  x ={x0:8.2f}  r de {min(y0, y1-EIXO):7.2f} a {max(y0, y1-EIXO):7.2f}  (alt {L:6.2f})  [{lay}]")
print("\n=== QUALQUER aresta INCLINADA em camada de contorno/tracejada, meia-secao do cabecote ===")
D = [r for r in recs if 5.0 < r[6] < 85.0 and (x0 := r[1]) > 0 and (25 <= abs(r[2]-EIXO) <= 135 or 25 <= abs(r[4]-EIXO) <= 135)]
for L, x0, y0, x1, y1, lay, a in sorted(D, key=lambda s: s[1]):
    if lay in ("0",): continue
    print(f"  comp {L:7.3f}  ang {a:6.2f}  de (x {x0:7.2f}, r {y0-EIXO:7.2f}) a (x {x1:7.2f}, r {y1-EIXO:7.2f})  [{lay}]")
print("\n=== camadas presentes ===")
from collections import Counter
print(Counter(r[5] for r in recs).most_common(12))
