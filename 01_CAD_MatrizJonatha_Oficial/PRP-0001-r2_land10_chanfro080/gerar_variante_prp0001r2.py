#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gerar_variante_prp0001r2.py — CAD da proposta PRP-0001 (revisão r2, tipo 'geometria')
=====================================================================================

Entrega a família de STEP da Matriz Jonatha com **land total de 10,00 mm e chanfro de saída de
0,80 mm x 45°**. O master oficial v27 tem chanfro de 1,50 mm, o que deixa só 8,50 mm de land reto
e paralelo e 0,75 mm de parede de aço no lábio de saída.

Previsão já aprovada pelo auditor (`05_Interface_Auditoria/vereditos/PRP-0001.json`, APROVADO):
    land_util    = 10,00 − 0,80 = 9,20 mm   (v27: 8,50)
    parede_labio = 2,25 − 0,80  = 1,45 mm   (v27: 0,75)
    dp_total     = 6,73 + 2,1866·9,20 + 0,907·0,80 = 27,57 bar (v27: 26,68 bar)

COMO A GEOMETRIA É OBTIDA — e por que não se usa o gerador legado
-----------------------------------------------------------------
`04_Dados_SSOT_e_Scripts/generate_true_coathanger_jonatha.py` **não reproduz o master entregue**:
gera um canal de 48 330 mm³ contra 213 945 mm³ medidos no STEP oficial. Esta variante é feita por
**cirurgia booleana sobre os STEP oficiais do v27**, de modo que o que a proposta não declara mudar
permaneça idêntico ao master:

  1. lê `MatrizJonatha_Canal_Fluxo.step` (maior sólido = núcleo, 213 945,146 mm³; os outros dois
     sólidos de 150,796 mm³ são os furos de pino Ø4 x 12 mm em Y = −12…0) e `Body_A`/`Body_B`;
  2. aço = `Body_A ∪ Body_B` (469 001,656 mm³, confere com envelope − canal − pinos);
  3. canal variante = (canal do master abaixo de Z = 109 − chanfro) ∪ (novo chanfro 45°);
  4. aço variante = aço do master − (canal variante − canal do master)  [só o último 1,5 mm muda];
  5. como o chanfro menor cabe dentro do cone antigo, o canal variante é subconjunto do master e o
     aço do lábio **cresce** 125,127 mm³; esse anel não existe no `Body_A/Body_B` oficiais
     (delta ∩ aço master = 0 mm³, medido), portanto o aço é reconstruído do envelope
     (env − canal − pinos) e conferido por fechamento volumétrico;
  6. bipartição no plano de partição **do próprio master** (Y = +0,0032 mm, medido no `Body_A`
     oficial) e exportação dos seis entregáveis.

Sanidade embutida: `--chanfro 1.5 --sanidade` reproduz o master (234 255,287 / 234 746,369 /
213 945,146 mm³). Rode isso antes de confiar na variante.

Regras respeitadas (Protocolo de Auditoria v1.0, §6): largura 75,00 mm, espessura 1,50 mm e
R0,75 intocados (a cirurgia é axial, nos últimos 1,5 mm); boca Ø75,60 mm; envelope idêntico à
Matriz 2; entregáveis .step AP214; `02_CAD_Modelos_Historicos/` intocado; master v27 não
sobrescrito (a variante vive nesta subpasta).

Uso:
    export LD_LIBRARY_PATH="$REPO/04_Dados_SSOT_e_Scripts/.headless_gl:$LD_LIBRARY_PATH"
    PY=$HOME/.venv/bin/python
    $PY gerar_variante_prp0001r2.py --chanfro 1.5 --prefixo SANIDADE_v27 --sanidade --log /tmp/s.log
    $PY gerar_variante_prp0001r2.py                    # variante da proposta (chanfro 0,80)
    $PY gerar_variante_prp0001r2.py --furos-passantes  # estudo: furos de pino usináveis
"""

import argparse
import datetime
import json
import os
import sys

try:
    import cadquery as cq
except ImportError as exc:  # pragma: no cover
    print("ERRO: cadquery não instalado. Rode: bash 04_Dados_SSOT_e_Scripts/setup_cfd_env.sh",
          file=sys.stderr)
    print(f"Detalhe: {exc}", file=sys.stderr)
    sys.exit(2)

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, "..", ".."))
DIR_MASTER = os.path.join(RAIZ, "01_CAD_MatrizJonatha_Oficial")
ARQ_BASELINE = os.path.join(RAIZ, "05_Interface_Auditoria", "baseline", "MATRIZ_3_v27.json")

# ------------------------------------------------------------------ constantes do projeto (SSOT)
ENVELOPE = ((0.00, 69.90, 93.00), (69.90, 80.70, 89.50), (80.70, 109.00, 79.50))
Z_TOTAL = 109.00
Z_INICIO_LAND = 99.00
LARGURA_FENDA = 75.00
ESPESSURA_FENDA = 1.50
D_EXTERNO_LABIO = 79.50
BOCA_ENTRADA = 75.60
PINOS_XZ = ((-41.50, 54.50), (41.50, 54.50))
PINOS_RAIO = 2.00
PINOS_PROF_MASTER = 12.00      # furos cegos do v27 (cavidades seladas: não conformidade conhecida)
VOLUMES_MASTER = {"body_a": 234255.287, "body_b": 234746.369, "canal": 213945.146}
TOL_VOLUME_MM3 = 0.02


# ------------------------------------------------------------------ utilidades geométricas
def caixa(x0, x1, y0, y1, z0, z1):
    """Sólido caixa alinhado aos eixos, do ponto (x0,y0,z0) ao (x1,y1,z1)."""
    return (cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False)
            .translate((x0, y0, z0)).val())


def envelope_externo():
    corpo = None
    for z0, z1, d in ENVELOPE:
        trecho = cq.Workplane("XY").workplane(offset=z0).circle(d / 2.0).extrude(z1 - z0)
        corpo = trecho if corpo is None else corpo.union(trecho)
    return corpo.val()


def ler_master():
    """(canal, pinos, aço, ymax_a) lidos dos STEP oficiais do v27.

    `ymax_a` é o plano de partição real do master (Y ≈ +0,0032 mm), medido no Body_A oficial —
    é esse plano que a variante herda, para não introduzir uma mudança não declarada.
    """
    solids = cq.importers.importStep(
        os.path.join(DIR_MASTER, "MatrizJonatha_Canal_Fluxo.step")).solids().vals()
    solids = sorted(solids, key=lambda s: -s.Volume())
    canal, pinos = solids[0], solids[1:]
    a = cq.importers.importStep(os.path.join(DIR_MASTER, "MatrizJonatha_Body_A.step")).solids().val()
    b = cq.importers.importStep(os.path.join(DIR_MASTER, "MatrizJonatha_Body_B.step")).solids().val()
    return canal, pinos, a.fuse(b), a.BoundingBox().ymax


def secao(solido, z, esp=0.002):
    """Caixa da seção transversal em Z (bbox) e a área da seção."""
    inter = solido.intersect(caixa(-100, 100, -100, 100, z, z + esp))
    bb = inter.BoundingBox()
    return bb, inter.Volume() / esp


def furos_de_pino(profundidade=PINOS_PROF_MASTER):
    """Furos Ø4 no plano XZ, ocupando Y = −profundidade…0 (posição real medida no master)."""
    furos = None
    for x, z in PINOS_XZ:
        cilindro = (cq.Workplane("XZ", origin=(x, 0.0, z)).circle(PINOS_RAIO)
                    .extrude(-profundidade).translate((0, profundidade, 0)).val())
        furos = cilindro if furos is None else furos.fuse(cilindro)
    return furos


Z_INICIO_CHANFRO_MASTER = 107.50   # medido no v27: o chanfro de 1,50 mm ocupa Z = 107,5 -> 109


def trecho_final(chanfro_mm):
    """Peça única de Z = 107,50 até Z = 109: land paralelo + chanfro divergente 45°.

    Um loft com três fios (base do chanfro antigo do master, início do chanfro novo e face de
    saída) evita dois problemas medidos na prática: deixar um vazio entre o land e o chanfro
    (104,3 mm³) e manter o cone antigo do master dentro do land novo.
    """
    z_ini = Z_TOTAL - chanfro_mm
    wp = cq.Workplane("XY").workplane(offset=Z_INICIO_CHANFRO_MASTER)
    wp = wp.slot2D(LARGURA_FENDA, ESPESSURA_FENDA)
    if z_ini > Z_INICIO_CHANFRO_MASTER + 1e-9:
        wp = (wp.workplane(offset=z_ini - Z_INICIO_CHANFRO_MASTER)
                .slot2D(LARGURA_FENDA, ESPESSURA_FENDA))
    wp = (wp.workplane(offset=chanfro_mm)
            .slot2D(LARGURA_FENDA + 2 * chanfro_mm, ESPESSURA_FENDA + 2 * chanfro_mm))
    return wp.loft(ruled=True).val()


def canal_variante(canal_master, chanfro_mm):
    """Canal do master até Z = 107,50 (onde começa o chanfro antigo) + trecho final novo."""
    parte_de_baixo = canal_master.cut(caixa(-100, 100, -100, 100,
                                            Z_INICIO_CHANFRO_MASTER, 200.0))
    return parte_de_baixo.fuse(trecho_final(chanfro_mm))


# ------------------------------------------------------------------ medição da variante
def medir(canal, body_a, body_b, chanfro_mm, land_total_mm):
    m = {}
    bb, area = secao(canal, 100.0)
    m["largura_fenda_mm"] = round(bb.xmax - bb.xmin, 4)
    m["espessura_fenda_mm"] = round(bb.ymax - bb.ymin, 4)
    m["area_fenda_mm2"] = round(area, 4)
    bb0, _ = secao(canal, 0.001)
    m["boca_entrada_mm"] = round(bb0.xmax - bb0.xmin, 4)
    bb_saida, _ = secao(canal, Z_TOTAL - 1e-3)
    m["largura_saida_mm"] = round(bb_saida.xmax - bb_saida.xmin, 4)
    m["espessura_saida_mm"] = round(bb_saida.ymax - bb_saida.ymin, 4)
    m["parede_labio_mm"] = round(D_EXTERNO_LABIO / 2.0 - (bb_saida.xmax - bb_saida.xmin) / 2.0, 4)

    # varredura do land paralelo (mesmo critério do auditor: passo fino, tol 0,02 mm na espessura)
    z, ultimo = Z_INICIO_LAND, None
    while z <= Z_TOTAL + 1e-4:
        bbz, _ = secao(canal, min(z, Z_TOTAL - 1e-3))
        if abs((bbz.ymax - bbz.ymin) - ESPESSURA_FENDA) > 0.02:
            break
        ultimo, z = z, z + 0.02
    m["land_util_mm"] = round(ultimo - Z_INICIO_LAND, 3) if ultimo else 0.0
    m["chanfro_medido_mm"] = round(Z_TOTAL - (Z_INICIO_LAND + m["land_util_mm"]), 3)
    m["z_inicio_chanfro_mm"] = round(Z_INICIO_LAND + m["land_util_mm"], 3)

    bb_c = canal.BoundingBox()
    m["volume_canal_mm3"] = round(canal.Volume(), 3)
    m["volume_body_a_mm3"] = round(body_a.Volume(), 3)
    m["volume_body_b_mm3"] = round(body_b.Volume(), 3)
    m["volume_aco_mm3"] = round(body_a.Volume() + body_b.Volume(), 3)
    m["massa_aco_kg"] = round(m["volume_aco_mm3"] / 1000.0 * 7.85 / 1000.0, 4)
    m["interferencia_mm3"] = round(body_a.intersect(body_b).Volume(), 6)
    m["z_total_mm"] = round(bb_c.zmax - bb_c.zmin, 4)
    bb_aco = body_a.fuse(body_b).BoundingBox()
    m["diametro_externo_mm"] = round(bb_aco.xmax - bb_aco.xmin, 4)

    # raio de borda equivalente, invertendo A = esp·(L − 2R) + π·R² (mesmo método do auditor)
    lo, hi = 0.0, ESPESSURA_FENDA
    for _ in range(80):
        R = 0.5 * (lo + hi)
        A = ESPESSURA_FENDA * (LARGURA_FENDA - 2 * R) + 3.141592653589793 * R * R
        if A < area:
            lo = R
        else:
            hi = R
    m["raio_borda_mm"] = round(0.5 * (lo + hi), 4)

    # Δp pelo modelo paramétrico calibrado do auditor (baseline congelado)
    if os.path.exists(ARQ_BASELINE):
        with open(ARQ_BASELINE, encoding="utf-8") as fh:
            mod = json.load(fh).get("modelo_parametrico", {})
        if mod:
            land_util = land_total_mm - chanfro_mm
            m["dp_total_bar"] = round(mod["dp_fora_do_land_bar"]
                                      + mod["G_land_bar_mm"] * land_util
                                      + mod["G_chanfro_bar_mm"] * chanfro_mm, 3)
            m["dp_modelo"] = mod
            m["dp_land_bar_mm"] = mod["G_land_bar_mm"]
    return m


# ------------------------------------------------------------------ geração
def gerar(chanfro_mm, land_total_mm=10.0, prefixo=None, furos_passantes=False, exportar=True):
    sufixo = f"L{land_total_mm:g}_C{chanfro_mm:g}"
    prefixo = prefixo or sufixo
    pasta = AQUI
    if furos_passantes:
        pasta = os.path.join(AQUI, "estudo_furos_passantes")
        os.makedirs(pasta, exist_ok=True)
        prefixo = f"{sufixo}_FUROS_PASSANTES"

    print(f"=== VARIANTE {prefixo} (land total {land_total_mm:.2f} mm, "
          f"chanfro {chanfro_mm:.2f} mm x 45°)"
          f"{' — furos de pino passantes' if furos_passantes else ''} ===")

    canal_master, pinos_master, aco_master, y_part = ler_master()
    print(f"  master: canal {canal_master.Volume():.3f} mm³ | aço {aco_master.Volume():.3f} mm³ | "
          f"pinos {[round(p.Volume(), 3) for p in pinos_master]}")

    canal = canal_variante(canal_master, chanfro_mm)
    # `canal_entregue` compõe o núcleo + os dois sólidos dos furos de pino, exatamente como no
    # `MatrizJonatha_Canal_Fluxo.step` oficial (3 sólidos) - é isso que o fechamento
    # envelope − (aço + canal + 2 furos) do auditor espera.
    canal_entregue = canal
    for pino in pinos_master:
        canal_entregue = canal_entregue.fuse(pino)

    # O chanfro novo (menor) cabe DENTRO do cone antigo, ou seja, o canal variante é SUBCONJUNTO do
    # canal do master. O aço que antes não existia no cone de 1,50 mm agora existe no anel entre o
    # chanfro de 0,80 mm e o cone antigo - e esse anel não pertence ao Body_A/Body_B do master
    # (delta ∩ aço_master = 0 mm³, medido). Por isso o aço é RECONSTRUÍDO do envelope, não derivado
    # do aço master por booleano: env − canal − furos de pino.
    env = envelope_externo()
    aco = env.cut(canal)
    for pino in pinos_master:
        aco = aco.cut(pino)                     # preserva as bolhas Ø4 x 12 seladas do v27
    if furos_passantes:
        # estudo: os furos cegos selados do v27 (não conformidade) viram furos passantes usináveis
        aco = aco.cut(furos_de_pino(profundidade=120.0))

    # fechamento volumétrico: aço + canal + furos = envelope (é o check [7] do auditor)
    esperado = env.Volume() - canal.Volume() - sum(p.Volume() for p in pinos_master)
    desvio = aco.Volume() - esperado
    delta_aco = aco.Volume() - aco_master.Volume()
    print(f"  aço da variante: {aco.Volume():.3f} mm³ (Δ {delta_aco:+.3f} vs master; "
          f"fechamento env − canal − pinos {desvio:+.4f} mm³)")
    if abs(desvio) > 0.01:
        raise SystemExit(f"ERRO: fechamento volumétrico falhou ({desvio:+.4f} mm³).")
    if abs(delta_aco - (canal_master.Volume() - canal.Volume())) > 0.01:
        raise SystemExit("ERRO: o aço não acompanhou a mudança do canal.")

    print(f"  plano de partição herdado do master: Y = {y_part:+.6f} mm")
    body_a = aco.intersect(caixa(-100, 100, -100, y_part, -50, 200))
    body_b = aco.cut(caixa(-100, 100, -100, y_part, -50, 200))

    m = medir(canal, body_a, body_b, chanfro_mm, land_total_mm)
    m["volume_furos_pino_mm3"] = round(sum(p.Volume() for p in pinos_master), 3)
    m["volume_canal_entregue_mm3"] = round(canal_entregue.Volume(), 3)
    m["solidos_no_canal_entregue"] = len(cq.Workplane("XY").add(canal_entregue).solids().vals())
    m.update({"prefixo": prefixo, "land_total_mm": land_total_mm, "chanfro_mm": chanfro_mm,
              "plano_particao_y_mm": round(y_part, 6), "furos_passantes": bool(furos_passantes),
              "gerado_em": datetime.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")})

    for k in ("land_util_mm", "chanfro_medido_mm", "parede_labio_mm", "largura_fenda_mm",
              "espessura_fenda_mm", "raio_borda_mm", "boca_entrada_mm", "volume_canal_mm3",
              "volume_body_a_mm3", "volume_body_b_mm3", "interferencia_mm3", "dp_total_bar"):
        if k in m:
            print(f"  {k} = {m[k]}")

    if exportar:
        base = os.path.join(pasta, f"MatrizJonatha_{prefixo}")
        wa, wb = cq.Workplane("XY").add(body_a), cq.Workplane("XY").add(body_b)
        wc = cq.Workplane("XY").add(canal_entregue)
        assy = cq.Assembly(name=f"MatrizJonatha_{prefixo}")
        assy.add(wa, name="Camada_01_Body_A", color=cq.Color(0.68, 0.75, 0.85))
        assy.add(wb, name="Camada_02_Body_B", color=cq.Color(0.55, 0.62, 0.72))
        assy.save(f"{base}.step", "STEP")

        assy_exp = cq.Assembly(name=f"MatrizJonatha_{prefixo}_Explodida")
        assy_exp.add(wa, name="Camada_01_Body_A_Inferior", color=cq.Color(0.68, 0.75, 0.85))
        assy_exp.add(cq.Workplane("XY").add(body_b).translate((0, 40.0, 0)),
                     name="Camada_02_Body_B_Superior_Deslocado", color=cq.Color(0.55, 0.62, 0.72))
        assy_exp.save(f"{base}_Explodida.step", "STEP")

        assy_fluxo = cq.Assembly(name=f"MatrizJonatha_{prefixo}_Com_Fluxo")
        assy_fluxo.add(wa, name="Camada_01_Body_A", color=cq.Color(0.68, 0.75, 0.85))
        assy_fluxo.add(wb, name="Camada_02_Body_B", color=cq.Color(0.55, 0.62, 0.72))
        assy_fluxo.add(wc, name="Camada_03_Canal_Fluxo_Polimero", color=cq.Color(0.0, 0.55, 0.90, 0.60))
        assy_fluxo.save(f"{base}_Com_Fluxo.step", "STEP")

        cq.exporters.export(wa, f"{base}_Body_A.step")
        cq.exporters.export(wb, f"{base}_Body_B.step")
        cq.exporters.export(wc, f"{base}_Canal_Fluxo.step")
        m["arquivos"] = [os.path.relpath(f"{base}{s}.step", RAIZ) for s in
                         ("", "_Explodida", "_Com_Fluxo", "_Body_A", "_Body_B", "_Canal_Fluxo")]
        for a in m["arquivos"]:
            print(f"  -> {a}")
    return m


def conferir_sanidade(m):
    """Compara com o master v27 (só faz sentido com --chanfro 1.5)."""
    diffs = {"body_a": m["volume_body_a_mm3"] - VOLUMES_MASTER["body_a"],
             "body_b": m["volume_body_b_mm3"] - VOLUMES_MASTER["body_b"],
             "canal": m["volume_canal_mm3"] - VOLUMES_MASTER["canal"]}
    ok = all(abs(v) <= TOL_VOLUME_MM3 for v in diffs.values()) and abs(m["land_util_mm"] - 8.5) <= 0.05
    print(f"\nSANIDADE contra o master v27: {'REPRODUZ' if ok else 'DIVERGE'} "
          f"(Δ body_a {diffs['body_a']:+.4f} | body_b {diffs['body_b']:+.4f} | "
          f"canal {diffs['canal']:+.4f} mm³ | land {m['land_util_mm']:.2f} mm)")
    return ok


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--land", type=float, default=10.0, help="land total em mm (Z=99 -> 109)")
    ap.add_argument("--chanfro", type=float, default=0.80,
                    help="chanfro de saída a 45° em mm (v27 = 1,50; proposta PRP-0001 = 0,80)")
    ap.add_argument("--prefixo", default=None, help="prefixo dos nomes de arquivo")
    ap.add_argument("--furos-passantes", action="store_true",
                    help="estudo adicional: furos de pino passantes (usináveis), em subpasta")
    ap.add_argument("--sanidade", action="store_true",
                    help="confere se reproduz o master v27 (use com --chanfro 1.5)")
    ap.add_argument("--sem-exportar", action="store_true", help="só calcula e mede, não grava STEP")
    ap.add_argument("--log", default=None, help="log JSON (padrão: gerar_variante.log)")
    args = ap.parse_args()

    m = gerar(args.chanfro, args.land, prefixo=args.prefixo, furos_passantes=False,
              exportar=not args.sem_exportar)
    if args.sanidade:
        m["sanidade_v27"] = "REPRODUZ" if conferir_sanidade(m) else "DIVERGE"
    if args.furos_passantes:
        m["estudo_furos_passantes"] = gerar(args.chanfro, args.land, furos_passantes=True,
                                            exportar=not args.sem_exportar)

    log = args.log or os.path.join(AQUI, "gerar_variante.log")
    with open(log, "w", encoding="utf-8") as fh:
        json.dump(m, fh, ensure_ascii=False, indent=2)
    print(f"\nLog JSON: {os.path.relpath(log, RAIZ)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
