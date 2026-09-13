"""Le TODAS as cotas (entidades DIMENSION) do DXF do cabecote: valor medido pela cota, texto anotado,
tipo, e a posicao convertida para o referencial da vista de seccao 1 (d da face do nariz, r do eixo).
E o que o desenho diz, sem a minha interpretacao de linhas."""
import ezdxf, math

K, EIXO, XF = 25.534, 657.7, 42.56
doc = ezdxf.readfile("/home/user/cabecote.dxf")
msp = doc.modelspace()
lin = []
for e in msp.query("DIMENSION"):
    try:
        m = e.dxf.actual_measurement
    except Exception:
        m = None
    try:
        txt = e.dxf.text
    except Exception:
        txt = ""
    try:
        p = e.dxf.defpoint
        d, r = p.x * K - XF, abs(p.y * K - EIXO)
    except Exception:
        d = r = float("nan")
    lin.append((d, r, m, txt, e.dxftype(), e.dxf.layer))


def fmt(v):
    if v is None:
        return "?"
    return f"{v:.3f}".rstrip("0").rstrip(".").replace(".", ",")


print(f"{len(lin)} entidades de cota no arquivo. As que estao na faixa da vista de seccao do cabecote "
      f"(-5 < d < 115, r < 120):")
sel = [x for x in lin if -5 < x[0] < 115 and x[1] < 120]
for d, r, m, txt, t, lay in sorted(sel, key=lambda x: (x[0])):
    print(f"   d {d:8.2f}  r {r:7.2f}   valor {fmt(m):>9}  texto '{txt[:22]:22s}'  {t:22s} [{lay}]")
print(f"\nFora dessa janela: {len(lin) - len(sel)} cotas (outras vistas / vista frontal). "
      f"Valores unicos medidos em todo o arquivo, ordenados:")
vals = sorted({round(x[2], 3) for x in lin if x[2] is not None})
print("   " + ", ".join(fmt(v) for v in vals[:120]))
print(f"\nCamadas das cotas: {sorted({x[5] for x in lin})}")
print("Textos nao-vazios (o que o desenhante escreveu, alem do numero):")
for x in lin:
    if x[3] and x[3] not in ("<>", ""):
        print(f"   '{x[3]}'  valor {fmt(x[2])}  em d {x[0]:8.2f} r {x[1]:7.2f}")
