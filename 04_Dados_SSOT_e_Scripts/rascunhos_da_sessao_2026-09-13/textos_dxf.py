"""Todos os TEXT/MTEXT/ATTRIB do DXF com posicao convertida para mm do desenho. As cotas do arquivo
foram explodidas na conversao do DWG, entao o numero que o desenhante escreveu vive como texto."""
import ezdxf

K, EIXO, XF = 25.534, 657.7, 42.56
doc = ezdxf.readfile("/home/user/cabecote.dxf")


def varre(msp, onde):
    out = []
    for e in msp:
        t = e.dxftype()
        if t in ("TEXT", "ATTRIB"):
            try:
                txt, ins = e.dxf.text, e.dxf.insert
            except Exception:
                continue
            out.append((txt, ins.x, ins.y, e.dxf.layer, onde, t))
        elif t == "MTEXT":
            try:
                txt, ins = e.text, e.dxf.insert
            except Exception:
                continue
            out.append((txt.replace("\\P", " | ").replace("\\fArial|b0|i0;", ""), ins.x, ins.y,
                        e.dxf.layer, onde, t))
        elif t == "INSERT":
            try:
                blk = doc.blocks.get(e.dxf.name)
            except Exception:
                continue
            for sub in varre(blk, onde + ">" + e.dxf.name):
                out.append((sub[0], sub[1] + e.dxf.insert.x, sub[2] + e.dxf.insert.y,
                            sub[3], sub[4], sub[5]))
    return out


todos = varre(doc.modelspace(), "msp")
print(f"{len(todos)} textos no arquivo.\n")
# agrupa por "vista": pelo Y da origem (cada vista tem seu eixo) - aqui so mostro d/r na vista 1 e
# o par bruto em papel, para poder agrupar depois
v1 = []
for txt, x, y, lay, onde, t in todos:
    d, r = x * K - XF, y * K - EIXO
    v1.append((d, r, txt, lay, onde, t))
for d, r, txt, lay, onde, t in sorted(v1, key=lambda z: z[0]):
    if abs(r) < 260 and -60 < d < 400:
        print(f"  d {d:8.2f}  r {r:8.2f}   '{txt[:46]:46s}'  [{lay}]  {onde}/{t}")
print("\n--- o que nao coube na janela da vista 1 (outras vistas), so os que tem numero ---")
import re
for d, r, txt, lay, onde, t in sorted(v1, key=lambda z: z[0]):
    if not (abs(r) < 260 and -60 < d < 400) and re.search(r"\d", txt):
        print(f"  papel d {d:8.2f}  r {r:8.2f}   '{txt[:40]:40s}'  [{lay}]")
