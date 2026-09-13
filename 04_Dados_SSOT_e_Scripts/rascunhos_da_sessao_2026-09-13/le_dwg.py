"""Le o DWG original com Aspose.CAD e despeja toda entidade que carrega texto/cota, com posicao.
O DXF que estava no workspace so tinha geometria (0 textos, 0 DIMENSION) - a anotacao do desenho
esta aqui, e e dela que saem as 'medidas de desenho' que o usuario citou."""
import os
os.environ["DOTNET_SYSTEM_GLOBALIZATION_INVARIANT"] = "1"
from aspose.cad import Image

P = "/home/user/MATRIZEXTRUSORA/030-032- cabeçote.dwg"
img = Image.load(P)
print("tipo da imagem:", type(img).__name__)
ents = list(getattr(img, "entities", None) or [])
print("entidades:", len(ents))
por_tipo = {}
for e in ents:
    por_tipo[type(e).__name__] = por_tipo.get(type(e).__name__, 0) + 1
print("por tipo:", ", ".join(f"{k}:{v}" for k, v in sorted(por_tipo.items(), key=lambda x: -x[1])[:24]))


def pega(e, *nomes):
    for nm in nomes:
        try:
            v = getattr(e, nm)
            if v is not None and v != "":
                return v
        except Exception:
            pass
    return None


def pos(e):
    p = pega(e, "insertion_point_value", "location", "XPoint", "start_point")
    try:
        return float(p.X), float(p.Y)
    except Exception:
        pass
    try:
        return float(pega(e, "XPoint")), float(pega(e, "YPoint"))
    except Exception:
        return None


print("\n### entidades com texto")
n = 0
for e in ents:
    tn = type(e).__name__
    if not any(k in tn for k in ("Text", "Dimension", "Attrib", "MText", "Tolerance", "Leader")):
        continue
    txt = pega(e, "value", "text", "dimensions_text", "default_value", "text_value")
    if txt is None:
        continue
    n += 1
    print(f"  [{tn:26s}] '{str(txt).strip()[:58]}'  pos={pos(e)}")
print(f"  total com texto: {n}")

print("\n### campos de uma entidade de cota, para descobrir os atributos uteis")
for e in ents:
    if "Dimension" in type(e).__name__:
        print("  ", type(e).__name__, [a for a in dir(e) if not a.startswith("_")][:40])
        break
