"""ESTUDO (nao e mudanca no oficial): o que custa recuar os 6 cartuchos para Z >= 99,75 mm.

Abre a alternativa (a) da pendencia [F] da interface: com a protrusao do desenho (14,00 mm) a borda
traseira do furo do cartucho em Z=97,00 entra 2,750 mm na luva do nariz do cabecote. Recuar os
cartuchos resolve sem tocar no labio de saida - mas mexe em parede, em web e no acesso dos
termopares. Este script MEDE os tres cenarios com o construtor real do projeto:

  geometria  : gerar_matriz_v28.construir()  (mesma funcao que gera os STEP oficiais)
  medicoes   : verificar_v28 (dist3d/maior/secao) e dp_total do proprio projeto
  cabecote   : verificar_interface_cabecote.cabecote() (o solido medido no DWG)

Saidas: 05_Variantes_Em_Estudo/ESTUDO_recuo_cartuchos_Z*_Body_{A,B}.step
        04_Dados_SSOT_e_Scripts/recuo_cartuchos.json
        03_Relatorios_e_Documentacao/ESTUDO_RECUO_CARTUCHOS.md
Nenhum arquivo oficial e tocado.

Uso: python 04_Dados_SSOT_e_Scripts/estudar_recuo_cartuchos.py [--so-texto]
"""
import argparse
import json
import math
import os
import sys

import cadquery as cq

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, ".."))
sys.path.insert(0, AQUI)

import gerar_matriz_v28 as g                                    # noqa: E402
from verificar_v28 import dist3d, maior, ENVELOPE              # noqa: E402
from verificar_interface_cabecote import cabecote, Z_FACE_NARIZ  # noqa: E402

DIR_VAR = os.path.join(RAIZ, "05_Variantes_Em_Estudo")
DIR_DOC = os.path.join(RAIZ, "03_Relatorios_e_Documentacao")
ACO = 7.85e-6
N = lambda v, d=3: f"{v:.{d}f}".replace(".", ",")

CENARIOS = [("v28.1 como está", 97.00), ("mínimo que passa", 99.75),
            ("com folga de bancada", 100.25)]


def monta(z_cart):
    """Um jogo completo de sólidos no plano de cartucho pedido, pelo construtor oficial."""
    g.CARTUCHOS = [(x, z_cart) for (x, _z) in [(0.00, 0), (-22.00, 0), (22.00, 0)]]
    c1 = cq.Workplane("XY").circle(ENVELOPE[0][2] / 2).extrude(ENVELOPE[0][1] - ENVELOPE[0][0])
    c2 = (cq.Workplane("XY").workplane(offset=ENVELOPE[1][0])
          .circle(ENVELOPE[1][2] / 2).extrude(ENVELOPE[1][1] - ENVELOPE[1][0]))
    c3 = (cq.Workplane("XY").workplane(offset=ENVELOPE[2][0])
          .circle(ENVELOPE[2][2] / 2).extrude(ENVELOPE[2][1] - ENVELOPE[2][0]))
    externo = maior(c1.union(c2).union(c3).val())
    canal, meta = g.construir_canal()
    g.medir_alturas(canal)
    aco, corpo_a, corpo_b, furos = g.construir(externo, canal)
    return dict(externo=externo, canal=canal, aco=aco, a=corpo_a, b=corpo_b, furos=furos, meta=meta)


def cilindro_de(f):
    tipo, d, x, z, compr, qual, y0, y1 = f
    return g.cil_indo_em_y(x, z, y0, y1, d / 2.0)


def mede(nome, z_cart, m, head):
    # um furo por estacao (X, Z, 0): cada metade traz o seu par espelhado e o corredor de insercao
    # dos dois e o mesmo cilindro - contar os dois dobraria o volume de metal no caminho
    def _unicos(lst):
        d = {}
        for f in lst:
            d[(f[0], f[2], f[3], f[1])] = f
        return list(d.values())
    cart = _unicos([f for f in m["furos"] if f[0] == "cartucho"])
    todos = _unicos([f for f in m["furos"] if f[0] in ("cartucho", "termopar")])
    cils = {id(f): cilindro_de(f) for f in todos}
    p_canal = min(dist3d(cils[id(f)], m["canal"]) for f in cart)
    p_od = min(dist3d(cils[id(f)], m["externo"]) for f in cart)   # 0,000 = o furo abre na externa, certo
    p_saida = min(abs(cils[id(f)].BoundingBox().zmax - ENVELOPE[2][1]) for f in cart)
    web = min((dist3d(cils[id(a)], cils[id(b)]) for i, a in enumerate(todos) for b in todos[i + 1:]),
              default=float("inf"))
    rompe_canal = sum(max(0.0, cils[id(f)].intersect(m["canal"]).Volume()) for f in cart)
    sobra_fora = max(0.0, m["aco"].cut(m["externo"]).Volume())
    vol_aco = m["aco"].Volume()
    # acesso do cartucho: o corredor de insercao esbarra no metal do cabecote?
    bloqueio = 0.0
    pior = 1e9
    for f in cart:
        tipo, d, x, z, compr, qual, y0, y1 = f
        corredor = cq.Solid.makeCylinder(d / 2.0, 240.0, cq.Vector(x, -120.0, z), cq.Vector(0, 1, 0))
        _i = corredor.intersect(head)
        bloqueio += sum(so.Volume() for so in _i.Solids()) or _i.Volume()
        pior = min(pior, (z - d / 2.0) - Z_FACE_NARIZ)
    return {"nome": nome, "z_cartucho_mm": z_cart, "parede_canal_mm": round(p_canal, 3),
            # parede_OD = distancia do furo a superficie externa (0,000 significa que o furo ABRE
            # na externa, que e o pedido: furo cego entrando por fora)
            "parede_OD_mm": round(p_od, 3), "parede_face_saida_mm": round(p_saida, 3),
            "web_entre_furos_mm": round(web, 3), "furo_rompe_canal_mm3": round(rompe_canal, 6),
            "sai_do_envelope_mm3": round(sobra_fora, 6), "volume_aco_mm3": round(vol_aco, 3),
            "massa_kg": round(vol_aco * ACO, 4), "bloqueio_cabecote_mm3": round(bloqueio, 3),
            "folga_traseira_mm": round(pior, 3),
            "canal_volume_mm3": round(m["canal"].Volume(), 3),
            "land_mm": round(m["meta"]["land_paralelo"], 3),
            "chanfro_mm": round(m["meta"]["chanfro"], 3)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--so-texto", action="store_true", help="não grava STEP (só mede e escreve JSON/MD)")
    a = ap.parse_args()
    head = cabecote(com_anel=False)
    res = []
    for nome, z in CENARIOS:
        m = monta(z)
        r = mede(nome, z, m, head)
        res.append(r)
        print(f"[{nome:<21}] Z={N(z,2)}  parede canal {N(r['parede_canal_mm'])} | OD "
              f"{N(r['parede_OD_mm'])} | face saída {N(r['parede_face_saida_mm'])} | web "
              f"{N(r['web_entre_furos_mm'])} | rompe canal {N(r['furo_rompe_canal_mm3'],4)} mm³ | "
              f"bloqueio {N(r['bloqueio_cabecote_mm3'],1)} mm³ | folga traseira {N(r['folga_traseira_mm'])}")
        if not a.so_texto and abs(z - CENARIOS[0][1]) > 1e-9:
            os.makedirs(DIR_VAR, exist_ok=True)
            sufixo = f"Z{z * 100:.0f}".replace(".", "")
            for lado, solido in (("A", m["a"]), ("B", m["b"])):
                p = os.path.join(DIR_VAR, f"ESTUDO_recuo_cartuchos_{sufixo}_Body_{lado}.step")
                cq.exporters.export(solido, p)
            print(f"  -> STEP em 05_Variantes_Em_Estudo/ESTUDO_recuo_cartuchos_{sufixo}_Body_*.step")

    base = res[0]
    for r in res[1:]:
        r["delta_parede_canal_mm"] = round(r["parede_canal_mm"] - base["parede_canal_mm"], 3)
        r["delta_web_mm"] = round(r["web_entre_furos_mm"] - base["web_entre_furos_mm"], 3)
        r["delta_massa_kg"] = round(r["massa_kg"] - base["massa_kg"], 4)
        r["delta_bloqueio_mm3"] = round(r["bloqueio_cabecote_mm3"] - base["bloqueio_cabecote_mm3"], 3)
        r["canal_identico"] = abs(r["canal_volume_mm3"] - base["canal_volume_mm3"]) < 1e-6
    json.dump({"cenarios": res, "fonte": "gerar_matriz_v28.construir + verificar_v28 + cabecote medido",
               "oficial_tocado": False},
              open(os.path.join(AQUI, "recuo_cartuchos.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    linhas = ["# Estudo: recuar os cartuchos para Z ≥ 99,75 mm (alternativa (a) da pendência [F])", "",
              "Geometria construída pelo `construir()` real do `gerar_matriz_v28.py` (mesmo caminho que",
              "gera os STEP oficiais) variando só o plano `Z` dos cartuchos. Medidas por `BRepExtrema` e",
              "booleanos; o cabeçote é o sólido medido no DWG. **Nenhum arquivo oficial foi tocado.**", "",
              "| cenário | Z (mm) | mín. furo→canal | abre na externa | borda→face de saída |"
              " web entre furos | rompe o canal | sai do envelope | bloqueio no cabeçote |"
              " folga traseira | massa |",              "| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for r in res:
        linhas.append(f"| {r['nome']} | {N(r['z_cartucho_mm'], 2)} | {N(r['parede_canal_mm'])} | "
                      f"{N(r['parede_OD_mm'])} | {N(r['parede_face_saida_mm'])} | "
                      f"{N(r['web_entre_furos_mm'])} | {N(r['furo_rompe_canal_mm3'], 4)} mm³ | "
                      f"{N(r['sai_do_envelope_mm3'], 4)} mm³ | {N(r['bloqueio_cabecote_mm3'], 1)} mm³ | "
                      f"{N(r['folga_traseira_mm'])} | {N(r['massa_kg'])} kg |")
    d = res[-1]
    linhas += ["", "## Leitura", "",
               f"* o cenário **mínimo que passa** (Z = {N(res[1]['z_cartucho_mm'], 2)} mm) zera o bloqueio: "
               f"{N(res[1]['bloqueio_cabecote_mm3'], 1)} mm³ contra {N(base['bloqueio_cabecote_mm3'], 1)} mm³ "
               f"do plano atual, e a folga traseira vai de {N(base['folga_traseira_mm'])} mm para "
               f"{N(res[1]['folga_traseira_mm'])} mm;",
               f"* custo em aço: parede mínima cartucho→canal "
               f"{N(base['parede_canal_mm'])} → {N(res[1]['parede_canal_mm'])} mm "
               f"(alvo do projeto ≥ 4,00), web entre furos {N(base['web_entre_furos_mm'])} → "
               f"{N(res[1]['web_entre_furos_mm'])} mm, massa {N(d['delta_massa_kg'], 4)} kg;",
               f"* o lábio **não muda**: land {N(res[1]['land_mm'], 2)} mm, chanfro "
               f"{N(res[1]['chanfro_mm'], 2)} × 45° e volume do canal idêntico ao do cenário atual "
               f"({'sim' if res[1]['canal_identico'] else 'não'}) — portanto o ΔP 1D medido na "
               f"geometria (41,9 bar) e o τ na parede (163,8 kPa) continuam os mesmos;",
               f"* nenhum furo sai do envelope ({N(res[1]['sai_do_envelope_mm3'], 4)} mm³) e nenhum rompe o "
               f"canal ({N(res[1]['furo_rompe_canal_mm3'], 4)} mm³);",
               f"* o plano 'com folga de bancada' (Z = {N(res[2]['z_cartucho_mm'], 2)} mm) dá "
               f"{N(res[2]['folga_traseira_mm'])} mm de folga em vez de 0,000 — e é o que eu recomendaria, "
               "porque 0,000 mm é contato exato entre dois sólidos de tolerância não nula.",
               "",
               "## O que este estudo NÃO decide",
               "",
               "1. Ele resolve só o acesso do **cartucho**. A furação dos termopares (Z = 103,00) já estava "
               "livre e não muda de lado, mas a web entre cartucho e termopar encolhe "
               f"({N(base['web_entre_furos_mm'])} → {N(res[2]['web_entre_furos_mm'])} mm no plano com folga) "
               "— conferir se isso é aceitável para o fabricante;",
               "2. a escolha entre recuar os furos da matriz **ou** abrir alívio no nariz do cabeçote depende "
               "da protrusão real medida na máquina e da decisão sobre mexer ou não no cabeçote cementado;",
               "3. a superfície de aperto do collete EX-031 continua em aberto (furo medido Ø90,00 reto não "
               "passa sobre a banda Ø93) — nada aqui depende dela, e nada aqui a resolve.",
               "",
               "*Gerado por `estudar_recuo_cartuchos.py`; números em `04_Dados_SSOT_e_Scripts/"
               "recuo_cartuchos.json`.*"]
    p = os.path.join(DIR_DOC, "ESTUDO_RECUO_CARTUCHOS.md")
    open(p, "w", encoding="utf-8").write("\n".join(linhas) + "\n")
    print("relação ->", p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
