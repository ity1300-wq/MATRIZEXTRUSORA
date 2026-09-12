"""Mede o PERFIL DO CABEÇOTE EX-030 no DXF e escreve o meio-corte em mm (dado de entrada do STEP).

O arquivo nao tem cota nem texto (o aspose explode tudo em POLYLINE), entao o perfil e lido por
varredura de arestas: arestas horizontais = cilindros (dizem o raio e em que faixa axial ele existe),
arestas verticais = faces perpendiculares ao eixo, geratrizes inclinadas = cones, diagonais a 45 =
chanfros.

METODOS JA TENTADOS E QUE NAO FUNCIONAM neste arquivo (nao repetir):
  * ler a cota direto: 0 DIMENSION / 0 TEXT / 0 CIRCLE no modelspace - so POLYLINE;
  * agrupar por componentes conexos para separar as vistas: as linhas de centro e de cotas encostam
    em tudo e o grafo vira UM componente (47017 de 47017) para qualquer tolerancia util;
  * achar o eixo de cada vista por espelhamento de arestas: toda aresta casa consigo mesma e o voto
    sai lixo (aparecem "diametros" de 2500 mm, que sao as linhas da legenda);
  * renderizar uma janela do raster para olhar o desenho: a legenda (o X grande) entra no recorte.
O que funciona: varrer arestas em torno do EIXO SABIDO de uma vista (para o corte do cabecote, y = 0
com origem axial no x da face) e usar invariantes de razao (angulo de cone, esferecidade de circulo),
que independem de saber a escala nem a que vista o recurso pertence.

Origem axial = x da face do nariz. Escala k = 25,534 mm/unidade (calibrada no C.C. dos furos da junta).

Uso:  python medir_perfil_cabecote.py [--dxf /home/user/cabecote.dxf] [--json sair]
"""
import argparse
import collections
import json
import math
import os
import sys

K = 25.534            # mm por unidade do DXF
X_FACE = 11.7464      # unidade do DXF: plano da face do nariz
AQUI = os.path.dirname(os.path.abspath(__file__))


def segmentos(dxf):
    import ezdxf
    doc = ezdxf.readfile(dxf)
    msp = doc.modelspace()
    out = []
    for e in msp:
        if e.dxftype() != "POLYLINE":
            continue
        try:
            pts = [(v.dxf.location.x, v.dxf.location.y) for v in e.vertices]
        except Exception:
            continue
        if len(pts) < 2:
            continue
        fechado = getattr(e, "closed", None)
        if fechado is None:
            ic = getattr(e, "is_closed", False)
            fechado = ic() if callable(ic) else ic
        if fechado:
            pts = pts + pts[:1]
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            out.append((x0, y0, x1, y1))
    return out


def mm(v_u, eixo="x"):
    return v_u * K if eixo == "x" else abs(v_u * K)


def agrupa(ints, tol=0.30):
    """ une intervalos [a,b] que se tocam/encavalam, ordenados """
    ints = sorted((min(a, b), max(a, b)) for a, b in ints if max(a, b) - min(a, b) > 0.05)
    saida = []
    for a, b in ints:
        if saida and a - saida[-1][1] <= tol:
            saida[-1][1] = max(saida[-1][1], b)
        else:
            saida.append([a, b])
    return [(round(a, 2), round(b, 2)) for a, b in saida]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dxf", default="/home/user/cabecote.dxf")
    ap.add_argument("--json", default=os.path.join(AQUI, "cabecote_perfil.json"))
    ap.add_argument("--tol-raio", type=float, default=0.15)
    a = ap.parse_args()
    segs = segmentos(a.dxf)
    print(f"{len(segs)} segmentos lidos de {os.path.basename(a.dxf)}")

    horiz = collections.defaultdict(list)   # |y|mm -> [(xmin, xmax)]
    vert = collections.defaultdict(list)    # x mm   -> [(ymin,ymax)] em |y| por lado
    diag = []
    for x0, y0, x1, y1 in segs:
        xm0, xm1 = (x0 - X_FACE) * K, (x1 - X_FACE) * K
        ym0, ym1 = y0 * K, y1 * K
        dx, dy = abs(xm1 - xm0), abs(ym1 - ym0)
        if dx < 0.05 and dy > 0.4:
            vert[round(min(xm0, xm1), 1)].append((min(ym0, ym1), max(ym0, ym1)))
        elif dy < 0.05 and dx > 0.4:
            horiz[round(abs((ym0 + ym1) / 2.0), 1)].append((min(xm0, xm1), max(xm0, xm1)))
        elif 0.75 < dy / max(dx, 1e-9) < 1.33 and dx > 1.5:
            diag.append((round(min(xm0, xm1), 1), round(dx, 1), round(dy, 1)))

    # agrupa raios cujas arestas estao a menos de tol_raio entre si
    raios = collections.defaultdict(list)
    grupo = None
    for r in sorted(horiz):
        if grupo is not None and r - grupo <= a.tol_raio:
            raios[grupo] += horiz[r]
        else:
            grupo = r
            raios[r] = list(horiz[r])

    print("\n[arestas horizontais] raio | diametro | faixa axial (mm)   <- cilindros do perfil")
    perfis = {}
    for r in sorted(raios):
        if r < 3 or r > 130:
            continue
        trechos = agrupa(raios[r])
        total = sum(b - x for x, b in trechos)
        if total < 2.0:
            continue
        perfis[round(r, 2)] = trechos
        print(f"  Ø{2*r:7.2f}  r={r:6.2f}  {len(trechos):2d} trecho(s): "
              + ", ".join(f"{x:.2f}..{b:.2f}" for x, b in trechos) + f"   (total {total:.1f} mm)")

    print("\n[faces axiais] x | extensao total em |y| | se cruza o eixo | trechos")
    faces = {}
    for x in sorted(vert):
        trechos = [(lo, hi) for lo, hi in vert[x]]
        trechos = agrupa([(lo, hi) for lo, hi in trechos])
        # espelho: trechos em y negativo viram positivos
        absr = sorted(set([(min(abs(lo), abs(hi)), max(abs(lo), abs(hi))) for lo, hi in trechos]))
        un = agrupa(absr, tol=0.2)
        mx = max((max(abs(lo), abs(hi)) for lo, hi in trechos), default=0)
        cruza = any(lo <= 0.0 <= hi for lo, hi in trechos)
        if mx < 5:
            continue
        faces[x] = {"raio_max_mm": round(mx, 2), "cruza_eixo": bool(cruza),
                    "trechos": [[round(u, 2), round(v, 2)] for u, v in un]}
        print(f"  x={x:7.2f}  |y|max={mx:6.2f} (Ø{2*mx:6.2f})  cruza_eixo={'SIM' if cruza else 'nao '}"
              f"  trechos |y|: " + ", ".join(f"{u:.2f}..{v:.2f}" for u, v in un))

    print("\n[geratrizes de cone] angulo | x0,y0 -> x1,y1 | dx | dy - o detector que Achou a bucha")
    cones = collections.defaultdict(list)
    for x0, y0, x1, y1 in segs:
        dx, dy = x1 - x0, y1 - y0
        if abs(dx) < 1e-9:
            continue
        ang = math.degrees(math.atan(dy / dx))
        if 0.4 < abs(ang) < 8.0 and math.hypot(dx, dy) * K > 20.0:
            cones[round(abs(ang), 2)].append((round(x0, 3), round(y0, 3), round(x1, 3), round(y1, 3),
                                              round(dx * K, 2), round(dy * K, 2)))
    for ang, lst in sorted(cones.items()):
        print(f"  {ang:5.2f} deg x{len(lst)}: " + "; ".join(f"({a},{b})->({c},{d}) dx{e} dy{f}"
                                                             for a, b, c, d, e, f in lst[:6]))

    print("\n[diagonais ~45 deg] x_ini | dx | dy  (candidatos a chanfro)")
    for x, dx, dy in sorted(diag)[:18]:
        print(f"  x={x:7.2f}  dx={dx:5.1f}  dy={dy:5.1f}   -> chanfro ~{min(dx, dy):.1f} x 45 deg")

    saida = {"peca": "EX-030 CABECOTE", "nao_identificavel": "quais vistas sao de EX-031/EX-032 - ver docstring", "metodo": "varredura de arestas do DXF (0 DIMENSION/0 TEXT)",
             "escala_mm_por_unidade": K, "origem_axial_unidade_dxf": X_FACE,
             "arestas_horizontais": {str(k): v for k, v in sorted(perfis.items())},
             "faces_axiais": {str(k): v for k, v in sorted(faces.items())},
             "diagonais_45": [[x, dx, dy] for x, dx, dy in sorted(diag)], "geratrizes_conicas": {str(ang): lst for ang, lst in sorted(cones.items())}, "invariante_do_cone": "as 4 unicas geratrizes do arquivo dao 3,27 deg e Ø86,00 numa ponta em ambas as vistas; angulo e razao independem da escala, mas a vista a que pertencem nao e identificavel (ver docstring)"}
    if a.json:
        json.dump(saida, open(a.json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"\n-> {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
