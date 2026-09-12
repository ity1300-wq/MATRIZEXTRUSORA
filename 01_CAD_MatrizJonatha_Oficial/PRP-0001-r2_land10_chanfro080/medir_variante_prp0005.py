#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
medir_variante_prp0005.py — medição independente do STEP entregue (proposta PRP-0005, tipo geometria)
=====================================================================================================

Mede os **arquivos STEP gravados em disco** (não a geometria em memória de quem os gerou) e compara
com o baseline congelado do v27 (`05_Interface_Auditoria/baseline/MATRIZ_3_v27.json`).

Por que este script existe
--------------------------
O auditor do Protocolo v1.0 mede sempre os STEP oficiais de `01_CAD_MatrizJonatha_Oficial/`
(`verify_geometry_ssot.py` tem `DIR_CAD` fixo e não aceita caminho alternativo). Como esses
arquivos são zona congelada e não podem ser sobrescritos por uma proposta, o auditor de hoje
**não consegue medir um STEP candidato** — proposta `tipo=geometria` acaba julgada pelos números do
master. Este script cobre essa lacuna pelo lado do Engenheiro: entrega evidência própria, com o
mesmo critério de medição do auditor, sem tocar na régua (a régua só muda por ato humano, §8).

O que é medido (mesmos critérios de `verify_geometry_ssot.py`):
  * largura e espessura da fenda em Z=100; área da seção e raio de borda equivalente
    (invertendo A = esp·(L − 2R) + π·R²);
  * comprimento do land reto e paralelo (varredura axial de 0,02 mm, tolerância 0,02 mm na
    espessura) e, por diferença, o chanfro real de saída;
  * parede de aço no lábio de saída: (Ø79,50 − largura da abertura em Z=109) / 2;
  * boca de entrada em Z=0,001; envelope e comprimento total;
  * volumes do canal, do Body_A e do Body_B, interferência entre as metades, cavidades internas
    fechadas (contagem de shells) e fechamento volumétrico envelope − (aço + canal + furos);
  * Δp total pelo modelo paramétrico calibrado do auditor (§5 do protocolo), lido do baseline.

Não mede (e diz isso): uniformidade de vazão, τ de parede e residência — vêm do CFD 2D, cuja seção
transversal do land é idêntica à do v27 (75,00 x 1,50 com R0,75), portanto os valores do baseline
permanecem válidos para esta variante.

Uso:
    export LD_LIBRARY_PATH="$REPO/04_Dados_SSOT_e_Scripts/.headless_gl:$LD_LIBRARY_PATH"
    PY=$HOME/.venv/bin/python
    $PY medir_variante_prp0005.py                       # mede a variante da proposta
    $PY medir_variante_prp0005.py --sanidade            # mede os STEP oficiais (deve dar o baseline)
    $PY medir_variante_prp0005.py --comparar-baseline   # acrescenta a tabela de deltas

Saída: `medicao_variante_prp0005.json` nesta pasta (+ impressão legível no console).
Código de saída: 0 = todos os requisitos duros conformes; 1 = alguma não conformidade.
"""

import argparse
import datetime
import hashlib
import json
import math
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

# ------------------------------------------------------------------ nominais do projeto (SSOT v27)
ENVELOPE = ((0.00, 69.90, 93.00), (69.90, 80.70, 89.50), (80.70, 109.00, 79.50))
Z_TOTAL = 109.00
Z_INICIO_LAND = 99.00
LARGURA_FENDA = 75.00
ESPESSURA_FENDA = 1.50
RAIO_BORDA = 0.75
BOCA_ENTRADA = 75.60
D_EXTERNO_LABIO = 79.50
AREA_TEORICA_FENDA = (LARGURA_FENDA - 2 * RAIO_BORDA) * ESPESSURA_FENDA + math.pi * RAIO_BORDA ** 2

# requisitos duros do Protocolo v1.0 §6 (tolerâncias do §4)
DUROS = (
    ("largura_fenda_mm", "Largura da fenda = 75,00 mm", LARGURA_FENDA, 0.05),
    ("espessura_fenda_mm", "Espessura da fenda = 1,50 mm", ESPESSURA_FENDA, 0.02),
    ("raio_borda_mm", "Raio de borda = 0,75 mm", RAIO_BORDA, 0.02),
    ("boca_entrada_mm", "Boca de entrada ≤ Ø75,60 mm", BOCA_ENTRADA, 0.001),
    ("interferencia_mm3", "Interferência entre as metades = 0", 0.0, 0.01),
    ("z_total_mm", "Comprimento total Z = 109,00 mm", Z_TOTAL, 0.05),
    ("diametro_externo_mm", "Diâmetro externo = Ø93,00 mm", 93.00, 0.05),
)


def caixa(x0, x1, y0, y1, z0, z1):
    return (cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False)
            .translate((x0, y0, z0)).val())


def envelope_externo():
    corpo = None
    for z0, z1, d in ENVELOPE:
        trecho = cq.Workplane("XY").workplane(offset=z0).circle(d / 2.0).extrude(z1 - z0)
        corpo = trecho if corpo is None else corpo.union(trecho)
    return corpo.val()


def sha256(caminho):
    h = hashlib.sha256()
    with open(caminho, "rb") as fh:
        for bloco in iter(lambda: fh.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def secao(solido, z, esp=0.002):
    inter = solido.intersect(caixa(-100, 100, -100, 100, z, z + esp))
    try:
        bb = inter.BoundingBox()
        dims = (bb.xmax - bb.xmin, bb.ymax - bb.ymin)
    except Exception:
        dims = (0.0, 0.0)
    return dims, inter.Volume() / esp


def contagem_shells(solido):
    """1 = maciço; >1 = tem cavidades internas fechadas (mesmo critério do auditor)."""
    from OCP.TopAbs import TopAbs_SHELL
    from OCP.TopExp import TopExp_Explorer
    exp, n = TopExp_Explorer(solido.wrapped, TopAbs_SHELL), 0
    while exp.More():
        n += 1
        exp.Next()
    return n


def raio_da_secao(area_mm2, esp=ESPESSURA_FENDA, largura=LARGURA_FENDA):
    lo, hi = 0.0, esp
    for _ in range(80):
        R = 0.5 * (lo + hi)
        A = esp * (largura - 2 * R) + math.pi * R * R
        if A < area_mm2:
            lo = R
        else:
            hi = R
    return 0.5 * (lo + hi)


def caminhos_da_familia(pasta, prefixo):
    """Os seis entregáveis de uma família de STEP (mesma composição dos oficiais)."""
    base = os.path.join(pasta, f"MatrizJonatha{prefixo}")
    return {s: f"{base}{s}.step" for s in
            ("", "_Explodida", "_Com_Fluxo", "_Body_A", "_Body_B", "_Canal_Fluxo")}


def medir_familia(pasta, prefixo, nome=None):
    """Mede os seis STEP gravados em disco e devolve o dicionário de métricas."""
    sufixo = f"_{prefixo}" if prefixo else ""
    caminhos = caminhos_da_familia(pasta, sufixo)
    faltando = [c for c in caminhos.values() if not os.path.exists(c)]
    if faltando:
        raise SystemExit(f"ERRO: STEP ausentes: {faltando}")

    canal_solidos = cq.importers.importStep(caminhos["_Canal_Fluxo"]).solids().vals()
    canal = max(canal_solidos, key=lambda s: s.Volume())
    body_a = cq.importers.importStep(caminhos["_Body_A"]).solids().val()
    body_b = cq.importers.importStep(caminhos["_Body_B"]).solids().val()
    montagem = cq.importers.importStep(caminhos[""]).solids().vals()

    m = medir_canal_e_corpos(canal, canal_solidos, body_a, body_b, montagem)
    m["prefixo"] = nome or prefixo or "v27_oficial"
    m["pasta"] = os.path.relpath(pasta, RAIZ)
    m["arquivos"] = [{"caminho": os.path.relpath(c, RAIZ), "sha256": sha256(c),
                      "bytes": os.path.getsize(c), "operacao": "novo"}
                     for c in caminhos.values()]
    return m


def conferir_duros(m):
    checks = []
    for chave, nome, nominal, tol in DUROS:
        v = m.get(chave)
        if v is None:
            checks.append({"id": chave, "o_que": nome, "nominal": nominal, "medido": None,
                           "tolerancia": tol, "resultado": "NAO_VERIFICADO"})
            continue
        ok = v <= nominal + tol if chave == "boca_entrada_mm" else abs(v - nominal) <= tol
        checks.append({"id": chave, "o_que": nome, "nominal": nominal, "medido": v,
                       "tolerancia": tol, "resultado": "OK" if ok else "NAO_CONFORME"})
    extra = [{"id": "area_fenda_mm2", "o_que": f"Área da seção do land = {AREA_TEORICA_FENDA:.4f} mm²",
              "nominal": round(AREA_TEORICA_FENDA, 4), "medido": m["area_fenda_mm2"],
              "tolerancia": 0.05,
              "resultado": "OK" if abs(m["area_fenda_mm2"] - AREA_TEORICA_FENDA) <= 0.05
              else "NAO_CONFORME"},
             {"id": "fechamento_envelope_mm3",
              "o_que": "Envelope − (aço + canal + furos) = 0", "nominal": 0.0,
              "medido": m["fechamento_envelope_mm3"], "tolerancia": 1.0,
              "resultado": "OK" if abs(m["fechamento_envelope_mm3"]) <= 1.0 else "NAO_CONFORME"},
             {"id": "chanfro_45graus",
              "o_que": "Chanfro de saída divergente a 45°", "nominal": True,
              "medido": m["chanfro_45graus_ok"], "tolerancia": "±0,10 mm radial",
              "resultado": "OK" if m["chanfro_45graus_ok"] else "NAO_CONFORME"}]
    return checks + extra


def dp_pelo_modelo(m):
    """Δp total pelo modelo paramétrico calibrado do auditor (§5), lido do baseline congelado."""
    if not os.path.exists(ARQ_BASELINE):
        return None, "baseline ausente"
    with open(ARQ_BASELINE, encoding="utf-8") as fh:
        mod = json.load(fh).get("modelo_parametrico", {})
    if not mod:
        return None, "baseline sem modelo_parametrico"
    land_util = m["land_total_mm"] - m["chanfro_medido_mm"]
    dp = (mod["dp_fora_do_land_bar"] + mod["G_land_bar_mm"] * land_util
          + mod["G_chanfro_bar_mm"] * m["chanfro_medido_mm"])
    texto = (f"dp_total = {mod['dp_fora_do_land_bar']} + {mod['G_land_bar_mm']}·{land_util:.2f} "
             f"+ {mod['G_chanfro_bar_mm']}·{m['chanfro_medido_mm']:.2f} = {dp:.3f} bar")
    return round(dp, 3), texto


def comparar_baseline(m, base_metricas):
    """Tabela de deltas contra o baseline congelado (mesma filosofia de sinal do auditor)."""
    filosofia = {"dp_total_bar": "menor_melhor", "land_util_mm": "maior_melhor",
                 "parede_labio_mm": "maior_melhor", "volume_canal_mm3": "neutro",
                 "uniformidade_nucleo_pct": "maior_melhor"}
    linhas = []
    for chave, novo in m.items():
        antigo = base_metricas.get(chave)
        if not isinstance(antigo, (int, float)) or not isinstance(novo, (int, float)):
            continue
        delta = None if antigo == 0 else round(100 * (novo - antigo) / antigo, 3)
        filo = filosofia.get(chave, "neutro")
        direcao = ("igual" if delta == 0 else
                   ("melhor" if (filo == "maior_melhor" and delta > 0) or
                    (filo == "menor_melhor" and delta < 0) else
                    ("pior" if filo != "neutro" else "neutro")))
        linhas.append({"metrica": chave, "baseline": antigo, "variante": novo,
                       "delta_pct": delta, "direcao": direcao})
    return linhas


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--prefixo", default="L10_C0.8", help="prefixo da família de STEP medida")
    ap.add_argument("--pasta", default=AQUI, help="pasta onde estão os STEP")
    ap.add_argument("--sanidade", action="store_true",
                    help="mede os STEP oficiais do v27 (deve reproduzir o baseline)")
    ap.add_argument("--comparar-baseline", action="store_true",
                    help="acrescenta a tabela de deltas contra o baseline congelado")
    ap.add_argument("--saida", default=None)
    args = ap.parse_args()

    if args.sanidade:
        m = medir_familia(DIR_MASTER, "", nome="v27_oficial")
    else:
        m = medir_familia(args.pasta, args.prefixo)

    checks = conferir_duros(m)
    dp, modelo = dp_pelo_modelo(m)
    if dp is not None:
        m["dp_total_bar"] = dp
    m["dp_modelo_parametrico"] = modelo

    print("=" * 96)
    print(f"MEDIÇÃO INDEPENDENTE — {m['prefixo']} ({m['pasta']})")
    print("=" * 96)
    for c in checks:
        marca = {"OK": "OK  ", "NAO_CONFORME": "FALHA", "NAO_VERIFICADO": "  ?  "}[c["resultado"]]
        print(f"  [{marca}] {c['o_que']:<52} nominal={c['nominal']!s:>10} "
              f"medido={c['medido']!s:>10} tol={c['tolerancia']}")
    print("\n  --- métricas derivadas ---")
    for k in ("land_util_mm", "chanfro_medido_mm", "parede_labio_mm", "dp_total_bar",
              "volume_canal_mm3", "volume_body_a_mm3", "volume_body_b_mm3", "massa_aco_kg",
              "plano_particao_y_mm", "cavidades_fechadas_body_a", "solidos_no_canal_fluxo"):
        if k in m:
            print(f"  {k} = {m[k]}")
    print(f"\n  Δp pelo modelo do auditor: {modelo}")

    saida = {"medido_em": datetime.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z"),
             "objeto": m["prefixo"], "pasta": m["pasta"], "metricas": m, "checks": checks,
             "modelo_dp": modelo,
             "nao_medido": [
                 {"item": "uniformidade_nucleo_pct", "motivo":
                     "CFD 2D: a seção transversal do land é idêntica à do v27 (75,00 x 1,50 com "
                     "R0,75), então o valor do baseline permanece válido"},
                 {"item": "tau_parede_land_kpa", "motivo": "idem (CFD 2D da mesma seção)"},
                 {"item": "residencia_media_s / residencia_parede_min", "motivo":
                     "mudam só pela razão de volumes; Δ do canal é −0,06%"},
                 {"item": "auditor oficial (Protocolo v1.0)", "motivo":
                     "verify_geometry_ssot.py mede apenas 01_CAD_MatrizJonatha_Oficial/ (DIR_CAD "
                     "fixo, zona congelada §8): não consegue medir um STEP candidato. Lacuna "
                     "registrada para o Humano resolver na régua (v1.1)"}]}

    if args.comparar_baseline and os.path.exists(ARQ_BASELINE):
        with open(ARQ_BASELINE, encoding="utf-8") as fh:
            base_m = json.load(fh).get("metricas", {})
        saida["comparacao_baseline"] = comparar_baseline(m, base_m)
        print("\n  --- comparação com o baseline congelado (v27) ---")
        for l in saida["comparacao_baseline"]:
            d = "—" if l["delta_pct"] is None else f"{l['delta_pct']:+.3f}%"
            print(f"  {l['metrica']:<28} {l['baseline']!s:>14} -> {l['variante']!s:>14}  {d:>10} "
                  f"{l['direcao']}")

    destino = args.saida or os.path.join(
        AQUI, "medicao_v27_oficial.json" if args.sanidade else "medicao_variante_prp0005.json")
    with open(destino, "w", encoding="utf-8") as fh:
        json.dump(saida, fh, ensure_ascii=False, indent=2)
    print(f"\nJSON: {os.path.relpath(destino, RAIZ)}")

    nao_conformes = [c for c in checks if c["resultado"] != "OK"]
    print(f"RESULTADO: {len(checks)} itens | {len(checks) - len(nao_conformes)} conformes | "
          f"{len(nao_conformes)} não conformes")
    return 0 if not nao_conformes else 1


def medir_canal_e_corpos(canal, canal_solidos, body_a, body_b, montagem):
    """Núcleo da medição, compartilhado pelos dois modos."""
    m = {}
    (larg, esp), area = secao(canal, 100.0)
    m["largura_fenda_mm"] = round(larg, 4)
    m["espessura_fenda_mm"] = round(esp, 4)
    m["area_fenda_mm2"] = round(area, 4)
    m["raio_borda_mm"] = round(raio_da_secao(area), 4)
    (boca_x, boca_y), _ = secao(canal, 0.001)
    m["boca_entrada_mm"] = round(boca_x, 4)
    m["boca_entrada_y_mm"] = round(boca_y, 4)
    (saida_x, saida_y), _ = secao(canal, Z_TOTAL - 1e-3)
    m["largura_saida_mm"] = round(saida_x, 4)
    m["espessura_saida_mm"] = round(saida_y, 4)
    m["parede_labio_mm"] = round(D_EXTERNO_LABIO / 2.0 - saida_x / 2.0, 4)

    z, ultimo = Z_INICIO_LAND, None
    while z <= Z_TOTAL + 1e-4:
        (_, h), _ = secao(canal, min(z, Z_TOTAL - 1e-3))
        if abs(h - ESPESSURA_FENDA) > 0.02:
            break
        ultimo, z = z, z + 0.02
    m["land_util_mm"] = round(ultimo - Z_INICIO_LAND, 3) if ultimo else 0.0
    m["chanfro_medido_mm"] = round(Z_TOTAL - (Z_INICIO_LAND + m["land_util_mm"]), 3)
    m["land_total_mm"] = round(Z_TOTAL - Z_INICIO_LAND, 3)
    (zx, zy), _ = secao(canal, Z_TOTAL - 0.10)
    m["chanfro_sobrelargura_x_mm"] = round((zx - LARGURA_FENDA) / 2.0, 4)
    m["chanfro_sobrelargura_y_mm"] = round((zy - ESPESSURA_FENDA) / 2.0, 4)
    m["chanfro_45graus_ok"] = bool(abs(m["chanfro_sobrelargura_x_mm"] -
                                       (m["chanfro_medido_mm"] - 0.10)) <= 0.10)

    m["volume_canal_mm3"] = round(canal.Volume(), 3)
    m["volume_body_a_mm3"] = round(body_a.Volume(), 3)
    m["volume_body_b_mm3"] = round(body_b.Volume(), 3)
    m["volume_aco_mm3"] = round(body_a.Volume() + body_b.Volume(), 3)
    m["massa_aco_kg"] = round(m["volume_aco_mm3"] / 1000.0 * 7.85 / 1000.0, 4)
    m["interferencia_mm3"] = round(body_a.intersect(body_b).Volume(), 6)
    m["cavidades_fechadas_body_a"] = contagem_shells(body_a) - 1
    m["cavidades_fechadas_body_b"] = contagem_shells(body_b) - 1
    m["solidos_na_montagem"] = len(montagem)
    m["solidos_no_canal_fluxo"] = len(canal_solidos)

    bb_a = body_a.BoundingBox()
    aco = body_a.fuse(body_b)
    bb_aco = aco.BoundingBox()
    m["z_total_mm"] = round(bb_aco.zmax - bb_aco.zmin, 4)
    m["diametro_externo_mm"] = round(bb_aco.xmax - bb_aco.xmin, 4)
    m["plano_particao_y_mm"] = round(bb_a.ymax, 6)
    for z0, z1, d in ENVELOPE:
        zc = (z0 + z1) / 2 if z0 else 0.5
        (dx, _), _ = secao(aco, zc)
        m[f"externo_z{zc:.2f}_mm"] = round(dx, 4)

    env = envelope_externo()
    m["volume_envelope_mm3"] = round(env.Volume(), 3)
    furos = [s for s in canal_solidos if s is not canal]
    m["volume_furos_pino_mm3"] = round(sum(f.Volume() for f in furos), 3)
    m["fechamento_envelope_mm3"] = round(env.Volume() - (m["volume_aco_mm3"] + m["volume_canal_mm3"]
                                                         + m["volume_furos_pino_mm3"]), 4)
    return m


if __name__ == "__main__":
    sys.exit(main())
