"""
GERADOR DA REVISAO v28.0 - MATRIZ JONATHA (Design for Manufacture)
===================================================================
Fecha as pendencias P2, P7 e P8 do RELATORIO DE TRIAGEM e acrescenta o conteudo
de fabrica que o v27.0 nao tinha (pinos de alinhamento conjugados, aquecimento
da zona do land e furos de desmontagem).

Nao sobrescreve o master aprovado: os arquivos v28.0 vao para
`01_CAD_MatrizJonatha_Oficial/` com o sufixo `_v28`, e o SSOT passa a registrar
a revisao como PROPOSTA PENDENTE DE APROVACAO.

O funil de fluxo e herdado 1:1 do STEP aprovado: o corte parte do solido real
do v27.0 e so a regiao Z >= 99,00 (land + chanfro) e reconstuida. Nada do que
foi aprovado e re-gerado por estimativa.

Uso:  python 04_Dados_SSOT_e_Scripts/gerar_matriz_v28.py
Saida: 01_CAD_MatrizJonatha_Oficial/MatrizJonatha_v28*.step
       04_Dados_SSOT_e_Scripts/matriz_v28_features.json
"""

import json
import math
import os

import cadquery as cq

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DIR_CAD = os.path.join(RAIZ, "01_CAD_MatrizJonatha_Oficial")
DIR_DADOS = os.path.join(RAIZ, "04_Dados_SSOT_e_Scripts")

# ---------------------------------------------------------------- parametros
# O labio de saida NAO e mais numero datilografado aqui: vem do SSOT
# (proposta_v28_dfm.geometria_labios), que registra a decisao D2 do usuario de 2026-09-11 -
# manter o chanfro de 1,50 x 45 graus e o land paralelo de 8,50 mm do master aprovado.
# --land / --chanfro so servem para re-rodar variantes ja rejeitadas (ex.: a v28.0 com 0,80).
_SSOT_PROP = json.load(open(os.path.join(DIR_DADOS, "cad_die_parameters.json"),
                           encoding="utf-8"))["proposta_v28_dfm"]
_SSOT_LABIO = _SSOT_PROP.get("geometria_labios", {})
ROTULO_DOC = _SSOT_PROP.get("rotulo", "v28")   # rotulo citado em documentos; ROTULO e so o prefixo do arquivo
Z_LAND = float(_SSOT_LABIO.get("z_inicio_land_mm", 99.00))   # inicio do land (herdado do v27.0)
Z_FIM = float(_SSOT_LABIO.get("z_fim_mm", 109.00))           # face de saida
LAND_PARALELO = float(_SSOT_LABIO.get("land_paralelo_mm", 8.50))
CHANFRO = float(_SSOT_LABIO.get("chanfro_saida_mm", 1.50))
LARGURA, ESPESSURA = 75.00, 1.50
ENVELOPE = [(0.00, 69.90, 93.00), (69.90, 80.70, 89.50), (80.70, 109.00, 79.50)]

DIAM_PINO, PROF_PINO = 4.00, 12.00
PINOS = [(-42.10, 30.00), (42.10, 30.00), (-42.10, 60.00), (42.10, 60.00)]

DIAM_CARTUCHO, PAREDE_CARTUCHO = 9.50, 4.00
CARTUCHOS = [(0.00, 97.00), (-22.00, 97.00), (22.00, 97.00)]

DIAM_TERMOPAR, PROF_TERMOPAR = 4.80, 20.00
TERMOPARES = [(-11.00, 103.00), (11.00, 103.00)]

# (os furos de alavanca de desmontagem foram SUPRIMIDOS: na faixa de aco de
# 8,7 mm entre o canal e o Ø93 qualquer furo Ø5 deixaria menos de 1,0 mm de
# parede na superficie externa. Verificar com `verificar_v28.py`. Desmontagem
# se faz pelo chanfro de 1 x 45 que sera pedido na aresta do plano de particao.)
DIAM_DESM, PROF_DESM, DESLOGA = 0.0, 0.0, []

# meia-altura do canal em Y por Z (medida no solido; preenchido em main())
ALTURA = {}


def maior(forma):
    """Maior sólido de um Shape, Compound ou lista de shapes."""
    from OCP.TopAbs import TopAbs_SOLID
    from OCP.TopExp import TopExp_Explorer
    if isinstance(forma, (list, tuple)):
        return max(forma, key=lambda x: x.Volume())
    shp = forma.wrapped if hasattr(forma, "wrapped") else forma
    exp = TopExp_Explorer(shp, TopAbs_SOLID)
    melhor, melhor_v = None, -1.0
    while exp.More():
        s = cq.Solid(exp.Current())
        if s.Volume() > melhor_v:
            melhor, melhor_v = s, s.Volume()
        exp.Next()
    return melhor if melhor is not None else forma



def r_envelope(z):
    for z0, z1, d in ENVELOPE:
        if z0 - 1e-9 <= z <= z1 + 1e-9:
            return d / 2.0
    return 0.0


def altura_canal(z):
    """max |Y| do canal no plano Z, interpolado da medicao (passo 0,5 mm)."""
    if not ALTURA:
        return 0.0
    z = min(max(z, 0.0), 109.0)
    a = round(math.floor(z / 0.5) * 0.5, 2)
    b = round(a + 0.5, 2)
    f = (z - a) / 0.5
    return ALTURA.get(a, 0.0) * (1 - f) + ALTURA.get(b, 0.0) * f


def altura_max_na_janela(z, raio):
    """Maior |Y| do canal sobre todo o disco do furo (z -+ raio). Conservador."""
    return max(altura_canal(t) for t in [z - raio, z - raio / 2, z, z + raio / 2, z + raio])


def medir_alturas(canal):
    lam = None
    for i in range(0, 219):
        z = round(i * 0.5, 2)
        fatia = cq.Workplane("XY").workplane(offset=z - 0.002) \
                  .box(400, 400, 0.004, centered=(True, True, False)).val()
        sec = maior(canal.intersect(fatia))
        ALTURA[z] = sec.BoundingBox().ymax if sec.Volume() > 1e-9 else 0.0


def cil_indo_em_y(x, z, y0, y1, r):
    """Cilindro de raio r, eixo paralelo a Y, de y0 ate y1 (nao depende de
    orientacao de workplane: usa primitiva explicita)."""
    return cq.Solid.makeCylinder(r, abs(y1 - y0), cq.Vector(x, min(y0, y1), z),
                                 cq.Vector(0, 1, 0))


# ------------------------------------------------------------------ 1. canal
def construir_canal():
    src = cq.importers.importStep(os.path.join(DIR_CAD, "MatrizJonatha_Canal_Fluxo.step"))
    canal27 = max(src.solids().vals(), key=lambda s: s.Volume())
    z_corte = Z_LAND - 0.001                      # 1 um de sobreposicao: uniao estanque
    fora = cq.Workplane("XY").workplane(offset=z_corte).box(400, 400, 80,
                                                            centered=(True, True, False)).val()
    funil = maior(canal27.cut(fora))
    land = cq.Workplane("XY").workplane(offset=z_corte).slot2D(LARGURA, ESPESSURA) \
                             .extrude(Z_LAND + LAND_PARALELO - z_corte).val()
    z_ch = Z_LAND + LAND_PARALELO
    cha = cq.Workplane("XY").workplane(offset=z_ch).slot2D(LARGURA, ESPESSURA) \
             .workplane(offset=CHANFRO).slot2D(LARGURA + 2 * CHANFRO, ESPESSURA + 2 * CHANFRO) \
             .loft(ruled=True).val()
    canal = maior(funil.fuse(land).fuse(cha))
    return canal, {"z_land": Z_LAND, "land_paralelo": LAND_PARALELO,
                   "chanfro": CHANFRO, "z_saida": Z_FIM, "z_corte": z_corte}


# ------------------------------------------------------------- 2. corpo + furos
def construir(corpo_externo, canal):
    aco = maior(corpo_externo.cut(canal))
    furos, cil = [], []

    for (x, z) in PINOS:                       # abertos no plano de particao
        c = cil_indo_em_y(x, z, -PROF_PINO, +PROF_PINO, DIAM_PINO / 2)
        furos.append(("pino_alinhamento", DIAM_PINO, x, z, 2 * PROF_PINO, "ambas",
                      -PROF_PINO, +PROF_PINO))
        cil.append(c)

    for (x, z) in CARTUCHOS:                   # cegos, do exterior para dentro
        r = DIAM_CARTUCHO / 2
        y_fora = math.sqrt(r_envelope(z) ** 2 - x * x) + 2.0
        y_fundo = altura_max_na_janela(z, r) + PAREDE_CARTUCHO + r
        for lado, qual in ((+1, "Body_B"), (-1, "Body_A")):
            c = cil_indo_em_y(x, z, lado * y_fundo, lado * y_fora, r)
            furos.append(("cartucho", DIAM_CARTUCHO, x, z, y_fora - y_fundo, qual,
                          min(lado * y_fundo, lado * y_fora), max(lado * y_fundo, lado * y_fora)))
            cil.append(c)

    for (x, z) in TERMOPARES:
        r = DIAM_TERMOPAR / 2
        y_fora = math.sqrt(r_envelope(z) ** 2 - x * x) + 2.0
        y_fundo = max(y_fora - (PROF_TERMOPAR + 2.0),
                      altura_max_na_janela(z, r) + 3.0 + r)
        for lado, qual in ((+1, "Body_B"), (-1, "Body_A")):
            c = cil_indo_em_y(x, z, lado * y_fundo, lado * y_fora, r)
            furos.append(("termopar", DIAM_TERMOPAR, x, z, y_fora - y_fundo, qual,
                          min(lado * y_fundo, lado * y_fora), max(lado * y_fundo, lado * y_fora)))
            cil.append(c)

    for c in cil:
        aco = maior(aco.cut(c))

    # biparticao: intersecao com dois semiespacos (exato; face plana em Y=0)
    caixa_b = cq.Solid.makeBox(600, 400, 600, cq.Vector(-300, 0.0, -300))
    caixa_a = cq.Solid.makeBox(600, 400, 600, cq.Vector(-300, -400.0, -300))
    corpo_b = maior(aco.intersect(caixa_b))
    corpo_a = maior(aco.intersect(caixa_a))
    return aco, corpo_a, corpo_b, furos


ROTULO = "v28"


def _flags():
    """--land/--chanfro reabrem variantes rejeitadas; --rotulo evita sobrescrever arquivos."""
    global LAND_PARALELO, CHANFRO, ROTULO
    import argparse
    ap = argparse.ArgumentParser(description="gera a proposta DFM da Matriz Jonatha")
    ap.add_argument("--land", type=float, default=None, help="comprimento do land paralelo (mm)")
    ap.add_argument("--chanfro", type=float, default=None, help="chanfro de saida 45 graus (mm)")
    ap.add_argument("--rotulo", default="v28", help="prefixo dos STEP gerados")
    a = ap.parse_args()
    if a.land is not None:
        LAND_PARALELO = a.land
    if a.chanfro is not None:
        CHANFRO = a.chanfro
    ROTULO = a.rotulo
    return a


def main():
    _flags()
    print("=" * 78)
    print(f"MATRIZ JONATHA - REVISAO {ROTULO_DOC} (DFM)  |  prefixo dos arquivos: {ROTULO}  |  "
          f"land {LAND_PARALELO:.2f} + chanfro {CHANFRO:.2f} x 45 (lidos do SSOT)")
    print("=" * 78)

    c1 = cq.Workplane("XY").circle(93.00 / 2).extrude(69.90)
    c2 = cq.Workplane("XY").workplane(offset=69.90).circle(89.50 / 2).extrude(10.80)
    c3 = cq.Workplane("XY").workplane(offset=80.70).circle(79.50 / 2).extrude(28.30)
    externo = maior(c1.union(c2).union(c3).val())

    canal, meta = construir_canal()
    medir_alturas(canal)
    print(f"  canal: volume = {canal.Volume():.3f} mm3 | land paralelo = "
          f"{meta['land_paralelo']:.2f} mm | chanfro = {meta['chanfro']:.2f} mm")

    aco, corpo_a, corpo_b, furos = construir(externo, canal)
    vol_a, vol_b = corpo_a.Volume(), corpo_b.Volume()
    print(f"  Body_A = {vol_a:.3f} mm3 | Body_B = {vol_b:.3f} mm3 | "
          f"massa = {(vol_a + vol_b) * 7.85e-6:.3f} kg")

    nome = lambda ext: os.path.join(DIR_CAD, f"MatrizJonatha_{ROTULO}{ext}")
    for (suf, cores) in [("", (corpo_a, corpo_b, None)),
                         ("_Explodida", (corpo_a, corpo_b.translate((0, 40, 0)), None)),
                         ("_Com_Fluxo", (corpo_a, corpo_b, canal))]:
        a = cq.Assembly(name="MatrizJonatha_v28" + suf)
        a.add(cores[0], name="Body_A", color=cq.Color(0.68, 0.75, 0.85))
        a.add(cores[1], name="Body_B", color=cq.Color(0.55, 0.62, 0.72))
        if cores[2] is not None:
            a.add(cores[2], name="Canal_Fluxo_Polimero",
                  color=cq.Color(0.0, 0.55, 0.90, 0.60))
        a.save(nome(suf + ".step"), "STEP")

    cq.exporters.export(corpo_a, nome("_Body_A.step"))
    cq.exporters.export(corpo_b, nome("_Body_B.step"))
    cq.exporters.export(canal, nome("_Canal_Fluxo.step"))

    # kit de pinos: 4 solidos DISTINTOS (fuso deles daria 1 peaca unica e o
    # arquivo deixaria de ser um kit). Um nome por pino, para a lista de corte.
    kit = cq.Assembly(name="Pinos_Alinhamento_v28")
    for i, (x, z) in enumerate(PINOS, start=1):
        pino = cil_indo_em_y(x, z, -PROF_PINO, +PROF_PINO, DIAM_PINO / 2 - 0.008)
        kit.add(pino, name=f"Pino_{i}_Ø4x24_X{x:+.2f}_Z{z:.2f}")
    kit.save(nome("_Pinos_Alinhamento.step"), "STEP")

    feats = {"meta": meta, "diametro_pino_mm": DIAM_PINO, "profundidade_pino_mm": PROF_PINO,
             "diametro_cartucho_mm": DIAM_CARTUCHO, "diametro_termopar_mm": DIAM_TERMOPAR,
             "diametro_desmontagem_mm": DIAM_DESM, "parede_alvo_cartucho_mm": PAREDE_CARTUCHO,
             "volume_canal_mm3": round(canal.Volume(), 3),
             "volume_body_a_mm3": round(vol_a, 3), "volume_body_b_mm3": round(vol_b, 3),
             "envelope": ENVELOPE,
             "furos": [{"tipo": t, "diametro": d, "X": round(x, 3), "Z": round(z, 3),
                        "comprimento_mm": round(cc, 3), "metade": q,
                        "y_ini_mm": round(y0, 3), "y_fim_mm": round(y1, 3)}
                       for (t, d, x, z, cc, q, y0, y1) in furos]}
    with open(os.path.join(DIR_DADOS, "matriz_v28_features.json"), "w", encoding="utf-8") as f:
        json.dump(feats, f, indent=2, ensure_ascii=False)

    print(f"\n  {len(furos)} furos posicionados:")
    for (t, d, x, z, c, q, y0, y1) in furos:
        print(f"    {t:<18} Ø{d:5.2f}  X={x:7.2f}  Z={z:6.2f}  L={c:6.2f} mm  "
              f"Y=[{y0:7.2f},{y1:6.2f}]  [{q}]")
    print(f"\n-> STEP {ROTULO_DOC} gravados em 01_CAD_MatrizJonatha_Oficial/ (prefixo MatrizJonatha_{ROTULO})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
