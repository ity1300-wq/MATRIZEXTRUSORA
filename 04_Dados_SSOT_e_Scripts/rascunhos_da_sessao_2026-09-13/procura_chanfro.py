"""Procura, no DXF do cabecote, TUDO que e aresta inclinada (candidato a chanfro) e todo texto de nota."""
import ezdxf, math
doc = ezdxf.readfile("/home/user/cabecote.dxf")
msp = doc.modelspace()
segs = []
def add(x0, y0, x1, y1, tipo, layer):
    if None in (x0, y0, x1, y1): return
    dx, dy = x1 - x0, y1 - y0
    if abs(dx) < 1e-12 and abs(dy) < 1e-12: return
    ang = math.degrees(math.atan2(dy, dx)) % 180.0
    segs.append((abs(dx), abs(dy), ang, x0, y0, x1, y1, tipo, layer))
for e in msp:
    t = e.dxftype()
    if t == "LINE":
        add(e.dxf.start.x, e.dxf.start.y, e.dxf.end.x, e.dxf.end.y, t, e.dxf.layer)
    elif t in ("LWPOLYLINE", "POLYLINE"):
        try:
            if t == "LWPOLYLINE":
                pts = [(p[0], p[1]) for p in e.get_points("xy")]
            else:
                pts = [(v.dxf.location.x, v.dxf.location.y) for v in e.vertices]
        except Exception as ex:
            continue
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            add(x0, y0, x1, y1, t, e.dxf.layer)
        if len(pts) > 2:
            add(pts[-1][0], pts[-1][1], pts[0][0], pts[0][1], t + "(fech.", e.dxf.layer)
print("segmentos varridos:", len(segs))
K = 25.534  # mm por unidade do desenho (medido na silhueta)
inc = [s for s in segs if 8.0 <= s[2] <= 82.0]
print("segmentos INCLINADOS (8..82 deg):", len(inc))
for s in sorted(inc, key=lambda s: -math.hypot(s[0], s[1]))[:40]:
    L = math.hypot(s[0], s[1]) * K
    print(f"  ang {s[2]:7.3f}  comp {L:9.3f} mm  de ({s[3]*K:9.2f},{s[4]*K:9.2f}) a ({s[5]*K:9.2f},{s[6]*K:9.2f})  [{s[7]} / {s[8]}]")
print("\nsegmentos a 45+-2 deg:", sum(1 for s in segs if 43 <= s[2] <= 47))
print("\n=== textos com chanfro / 45 / C-SYMBOLE ===")
for e in msp:
    t = e.dxftype()
    if t in ("TEXT", "MTEXT"):
        s = (e.dxf.text if t == "TEXT" else e.text) or ""
        u = s.upper()
        if any(k in u for k in ("CHANFR", "45", "CHAMF", "RAIO", "R ", "ESCAP", "C'")):
            print(f"  [{t} {e.dxf.layer}] {s!r} em ({(e.dxf.dxfinsert.x if t=='TEXT' else e.dxf.insert.x)*K:.2f}, {(e.dxf.dxfinsert.y if t=='TEXT' else e.dxf.insert.y)*K:.2f})")
