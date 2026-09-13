"""Recorta a visao de secao do cabecote (eixo y = 657,7 mm) e imprime: escada do contorno (meia-secao,
raio acima do eixo) e TODAS as arestas inclinadas dentro da faixa - que e onde um chanfro aparece."""
import ezdxf, math
doc = ezdxf.readfile("/home/user/cabecote.dxf"); msp = doc.modelspace()
K, EIXO, BANDA = 25.534, 657.7, 118.0
hor, ver, dia = [], [], []
for e in msp:
    t = e.dxftype()
    def push(x0, y0, x1, y1, lay, col):
        if None in (x0, y0, x1, y1): return
        X0, Y0, X1, Y1 = x0*K, y0*K, x1*K, y1*K
        if min(Y0, Y1) < EIXO - BANDA or max(Y0, Y1) > EIXO + BANDA: return
        dx, dy = abs(X1-X0), abs(Y1-Y0); L = math.hypot(dx, dy)
        if L < 0.25 or "hachura" in lay.lower(): return
        a = math.degrees(math.atan2(dy, dx)) % 180.0
        rec = (L, X0, Y0, X1, Y1, lay, a)
        (hor if (a < 0.25 or a > 179.75) else ver if 89.75 < a < 90.25 else dia).append(rec)
    if t == "LINE":
        push(e.dxf.start.x, e.dxf.start.y, e.dxf.end.x, e.dxf.end.y, e.dxf.layer, e.dxf.color)
    elif t in ("LWPOLYLINE", "POLYLINE"):
        try:
            pts = ([(p[0], p[1]) for p in e.get_points("xy")] if t == "LWPOLYLINE"
                   else [(v.dxf.location.x, v.dxf.location.y) for v in e.vertices])
        except Exception: continue
        for a, b in zip(pts, pts[1:]): push(a[0], a[1], b[0], b[1], e.dxf.layer, e.dxf.color)
        if len(pts) > 2: push(pts[-1][0], pts[-1][1], pts[0][0], pts[0][1], e.dxf.layer, e.dxf.color)
def acima(y): return y - EIXO
print(f"na banda +-{BANDA} mm do eixo: {len(hor)} horizontais, {len(ver)} verticais, {len(dia)} inclinadas")
print("\n=== ESCADA DO CONTORNO: arestas horizontais (raio acima do eixo, x em mm da vista) ===")
for L, x0, y0, x1, y1, lay, a in sorted(hor, key=lambda s: (abs(acima(s[2])), s[1])):
    if abs(acima(y0)) < 3: continue
    print(f"  r={acima(y0):7.2f}  x de {min(x0,x1):8.2f} a {max(x0,x1):8.2f}  (comp {L:7.2f})  [{lay}]")
print("\n=== INCLINADAS (candidatas a chanfro), meia-secao superior ===")
for L, x0, y0, x1, y1, lay, a in sorted(dia, key=lambda s: -s[0]):
    r0, r1 = acima(y0), acima(y1)
    if min(r0, r1) < 0: continue
    print(f"  comp {L:7.3f}  ang {a:6.2f}  de (x {x0:8.2f}, r {r0:7.2f}) a (x {x1:8.2f}, r {r1:7.2f})  [{lay}]")
