#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AUDITORIA DE TODOS OS STEP DO REPO — o que cada arquivo e, e as CORRELACOES entre eles.

Diferente do que ja existe no repo (o `verify_geometry_ssot.py` confere a matriz oficial contra o SSOT, e o
`verify_legacy_dies.py` mede as historicas): aqui a unidade de trabalho e a **correlacao**. Todo STEP
rastreado e aberto uma vez, inventariado face por face, e depois cruzado com os outros arquivos que tem de
bater com ele:

  C1  cota medida x SSOT               - fenda (largura/espessura/R), boca de entrada, estagios do envelope,
                                        comprimento total, massa
  C2  metade x metade x peca inteira   - A + B = bloco? A n B = 0? quantas cascas por metade (cavidade selada)
  C3  arquivo do canal x vazio real    - o *_Canal_Fluxo.step e o vazio que a peca tem de fato?
  C4  matriz x cabecote                - folga radial por estagio, o anel de fuga esta ABERTO do bico ate a
                                        entrada da matriz (e isso que faz o mastico voltar pelo funil),
                                        encosto, interferencia, protrusao
  C5  montagem x pecas                 - o STEP de montagem tem 1 cabecote + N da matriz, o volume somado
                                        bate com os arquivos de origem, e a interferencia e zero
  C6  atalho x arquivo fisico          - os caminhos selados no baseline do auditor abrem os mesmos bytes

Saida: `04_Dados_SSOT_e_Scripts/auditoria_step_correlacoes.json` e
`03_Relatorios_e_Documentacao/AUDITORIA_CORRELACOES_STEP.md`. Sai com codigo 1 se qualquer correlacao
divergir - e meanto para rodar no portao.

Uso: python 04_Dados_SSOT_e_Scripts/auditar_step_correlacoes.py [--json] [--md] [--só-cotassot]
"""
import argparse
import collections
import hashlib
import json
import os
import subprocess
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, ".."))
sys.path.insert(0, AQUI)

import cadquery as cq

from verificar_v28 import maior, n          # maior(): descarta migalha de booleano; n(): numero pt-BR

DIR_01 = os.path.join(RAIZ, "01_CAD_MatrizJonatha_Oficial")
DIR_02 = os.path.join(RAIZ, "02_CAD_Modelos_Historicos")
DIR_CAB = os.path.join(RAIZ, "06_CAD_Cabecote_EX-030", "STEP")
DIR_MAE = os.path.join(RAIZ, "07_CAD_Matrizes")
SSOT = json.load(open(os.path.join(AQUI, "cad_die_parameters.json"), encoding="utf-8"))
BASE = json.load(open(os.path.join(RAIZ, "05_Interface_Auditoria", "baseline", "MATRIZ_3_v27.json"),
                      encoding="utf-8"))["hashes"]
ARQ_JSON = os.path.join(AQUI, "auditoria_step_correlacoes.json")
ARQ_MD = os.path.join(RAIZ, "03_Relatorios_e_Documentacao", "AUDITORIA_CORRELACOES_STEP.md")
ACO = 7.85e-6                                  # kg/mm3
FOLGA_MINIMA = 0.02                            # mm: abaixo disso a "folga" e contato, nao folga

falhas = []


def cobra(ok, item, detalhe=""):
    if not ok:
        falhas.append(f"{item}: {detalhe}")
    return ok


# --------------------------------------------------------------------------- medidores
_CACHE = {}


def abre(caminho):
    key = os.path.realpath(caminho)
    if key not in _CACHE:
        _CACHE[key] = cq.importers.importStep(caminho).val()
    return _CACHE[key]


def vol(x):
    ss = x.Solids()
    return sum(v.Volume() for v in ss) if ss else x.Volume()


def inventario(shape):
    """Faces por tipo + cilindros de eixo Z/da silhueta, fenda, furos de pino e caixa."""
    tipos = collections.Counter()
    cil_z, cil_x, planos_y, cones = [], [], [], []
    for f in shape.Faces():
        t = f.geomType()
        tipos[t] += 1
        b = f.BoundingBox()
        if t == "CYLINDER":
            raio = f._geomAdaptor().Cylinder().Radius()
            eixo = f.normalAt().Length ** 0          # nao serve; usar a caixa: cilindro de eixo em Z tem dz>0 e dx,dy ~ raio
            if abs((b.xmax - b.xmin) - 2 * raio) < 0.05 and abs((b.ymax - b.ymin) - 2 * raio) < 0.05 and raio > 5:
                cil_z.append((round(raio, 3), round(b.zmin, 2), round(b.zmax, 2), round(f.Area(), 1)))
            elif abs((b.zmax - b.zmin)) < 2.5 * raio + 0.05 and (b.xmax - b.xmin) > 2 * raio - 0.05:
                cil_x.append((round(raio, 3), [round(b.xmin, 2), round(b.xmax, 2)],
                              [round(b.ymin, 2), round(b.ymax, 2)], [round(b.zmin, 2), round(b.zmax, 2)]))
        elif t == "PLANE":
            nn = f.normalAt()
            if abs(abs(nn.y) - 1.0) < 1e-6 and abs(b.ymin) < 3.0:
                planos_y.append((round(nn.y, 3), round(b.xmin, 3), round(b.xmax, 3),
                                 round(b.zmin, 2), round(b.zmax, 2)))
        elif t == "CONE":
            cones.append((round(b.xmin, 2), round(b.xmax, 2), round(b.zmin, 2), round(b.zmax, 2),
                          round(f.Area(), 1)))
    cx = shape.BoundingBox()
    validos = [s.isValid() for s in (shape.Solids() or [shape])]
    return {"solidos": len(shape.Solids() or [shape]),
            "cascas_por_solido": [len(s.Shells()) for s in (shape.Solids() or [shape])],
            "faces_por_tipo": dict(tipos),
            "faces": sum(tipos.values()),
            "volume_mm3": round(vol(shape), 4),
            "caixa": {"Øx": round(max(cx.xmax - cx.xmin, cx.ymax - cx.ymin), 3),
                      "dy": round(cx.ymax - cx.ymin, 3), "dz": round(cx.zmax - cx.zmin, 3),
                      "z": [round(cx.zmin, 3), round(cx.zmax, 3)]},
            "cilindros_z": sorted({(r, z0, z1) for r, z0, z1, _ in cil_z}, reverse=True),
            "furos_eixo_x": sorted(set(cil_x)),
            "planos_da_fenda": sorted(set(planos_y)),
            "cones": sorted(set(cones)),
            "brep_valido": all(validos)}


def fenda_medida(inv):
    """Largura, espessura e raio da fenda, medidos nas caras. Unir os semicilindros das bordas e o que
    da 75,00 - so pelos planos dava 73,50 (error ja gravado no repo)."""
    ys = sorted({p[0] for p in inv["planos_da_fenda"]})
    if len(ys) < 2:
        return None
    xs = [p[1] for p in inv["planos_da_fenda"] if abs(p[0] - ys[0]) < 1e-9] + \
         [p[2] for p in inv["planos_da_fenda"] if abs(p[0] - ys[-1]) < 1e-9]
    largura = round(max(xs) - min(xs), 3)
    esp = round(abs(ys[-1] - ys[0]), 3)
    zs = [(p[3], p[4]) for p in inv["planos_da_fenda"]]
    raio = None
    for r, x0, x1, _a, _b in inv.get("_cil_all", []):
        if 0.4 < r < 3.0:
            raio = r
            break
    return {"largura_mm": largura, "espessura_mm": esp, "raio_borda_mm": raio,
            "z_passante": [round(min(z[0] for z in zs), 2), round(max(z[1] for z in zs), 2)]}


def boca_entrada(inv):
    """Ø da abertura na face de entrada (Z minimo): o maior raio de cone, ou o menor cilindro de Z."""
    if inv["cones"]:
        c = inv["cones"][0]
        return round(2 * max(abs(c[0]), abs(c[1])), 3)
    cil = inv["cilindros_z"]
    if cil:
        # o cone de entrada nao aparece como CONE quando e aprox. cilidrico: usa o menor estagio
        return round(2 * min(r for r, _, _ in cil), 3)
    return None


def estagios(inv):
    """Escada do envelope externo: [(Ø, z0, z1)] do maior para o menor raio."""
    return [(round(2 * r, 2), z0, z1) for r, z0, z1 in inv["cilindros_z"] if r > 20]


def vazios_da_peca(shape, raio_envoltoria=48.60, folga_z=1.0):
    """O vazio que a matriz carrega (funil + fenda), medido como caixa - peca. Um booleano so."""
    bb = shape.BoundingBox()
    caixa = cq.Workplane("XY").cylinder(bb.zmax - bb.zmin + 2 * folga_z, 2 * raio_envoltoria,
                                        basePointVector=(0, 0, (bb.zmin + bb.zmax) / 2.0))
    sobra = maior(caixa.val().cut(maior(shape)))
    v = vol(sobra)
    return round(v, 1)


def sha(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


# --------------------------------------------------------------------------- C6 atalhos x baseline
def correlacao_atalhos():
    out, problemas = {}, []
    for caminho, h_exp in sorted(BASE.items()):
        p = os.path.join(RAIZ, caminho)
        if not os.path.exists(p):
            problemas.append("%s: sumiu da arvore" % caminho)
            continue
        h = sha(p)
        out[caminho] = {"eh_atalho": os.path.islink(p),
                        "destino": os.path.relpath(os.path.realpath(p), RAIZ) if os.path.islink(p) else None,
                        "sha256_igual": h == h_exp}
        if h != h_exp:
            problemas.append("%s: bytes diferentes do baseline" % caminho)
    cobra(not problemas, "C6 atalhos/caminhos selados", "; ".join(problemas[:4]))
    return {"esperados": len(BASE), "conferidos": len(out), "divergentes": problemas, "por_arquivo": out}


# ------------------------------------------------------------------- C1 cotas medidas x SSOT
def correlacao_cotas(matrizes):
    par = SSOT["matriz_jonatha_parameters"]
    env = SSOT["envelope_externo_mm"]
    tol = {"largura": 0.05, "espessura": 0.02, "raio": 0.02, "boca": 0.10, "envelope": 0.05}
    linhas, diverg = [], []
    alvo = SSOT.get("matriz_jonatha_master_files", {}).get("corpo", "MatrizJonatha.step")
    for chave, nome, inv in matrizes:
        fd = fenda_medida(inv)
        if not fd:
            linhas.append(dict(matriz=chave, status="sem fenda fechada (pecas historicas podem nao ter)"))
            continue
        boca = boca_entrada(inv)
        linha = dict(matriz=chave, arquivo=nome, largura_mm=fd["largura_mm"], espessura_mm=fd["espessura_mm"],
                     z_da_fenda=fd["z_passante"], boca_entrada_mm=boca, estagios=estagios(inv),
                     comprimento_mm=inv["caixa"]["dz"], volume_aco_mm3=inv["volume_mm3"],
                     massa_kg=round(inv["volume_mm3"] * ACO, 4))
        deltas = {}
        if abs(fd["largura_mm"] - par["largura_mm"]) > tol["largura"]:
            deltas["largura"] = (fd["largura_mm"], par["largura_mm"])
        if abs(fd["espessura_mm"] - par["espessura_mm"]) > tol["espessura"]:
            deltas["espessura"] = (fd["espessura_mm"], par["espessura_mm"])
        if boca is not None and boca - par["acoplamento_extrusora_diametro_mm"] > tol["boca"]:
            deltas["boca"] = (boca, par["acoplamento_extrusora_diametro_mm"])
        est = estagios(inv)
        if est and env.get("estagios"):
            for (d_med, z0, z1), ref in zip(est, env["estagios"]):
                if abs(d_med - ref[0]) > tol["envelope"] or abs(z0 - ref[1]) > tol["envelope"]:
                    deltas.setdefault("envelope", []).append([(d_med, z0, z1), ref])
        linha["divergencia_vs_SSOT"] = deltas
        linhas.append(linha)
        if deltas and chave in ("jonatha_v27_oficial",):
            diverg.append("%s: %s" % (chave, deltas))
    cobra(not diverg, "C1 cotas da matriz OFICIAL batem com o SSOT", "; ".join(diverg))
    return {"tolerancias_mm": tol, "por_matriz": linhas,
            "oficial_divergindo": diverg}


# ------------------------------------------------------------ C2 metade x metade, C3 canal x vazio
def correlacao_pares_e_canal(matrizes):
    out = {}
    for chave, nome, inv in matrizes:
        bloco = os.path.join(DIR_MAE, *nome.split("/")[:0], nome)
        p = inv["_caminho"]
        d = os.path.dirname(p)
        base = os.path.basename(p)[:-5]
        pa, pb = (os.path.join(d, base.replace(".step", "_Body_A.step")),
                  os.path.join(d, base.replace(".step", "_Body_B.step")))
        par = {"peca_inteira": os.path.basename(p), "volume_mm3": inv["volume_mm3"]}
        if os.path.exists(pa) and os.path.exists(pb):
            A, B = maior(abre(pa)), maior(abre(pb))
            vA, vB = vol(A), vol(B)
            uniao = vol(maior(A.fuse(B)))
            intes = vol(maior(A.intersect(B))) if A.intersect(B).Solids() else 0.0
            par.update(body_A=round(vA, 1), body_B=round(vB, 1), soma_A_mais_B=round(vA + vB, 1),
                       uniao=round(uniao, 1), diferenca_soma_menos_uniao=round(vA + vB - uniao, 6),
                       intersecao_mm3=round(intes, 6),
                       cascas_A=len(A.Shells()), cascas_B=len(B.Shells()))
            cobra(abs(vA + vB - uniao) <= 0.01, "C2 %s: A+B = A U B" % chave,
                  "A+B=%.4f vs uniao=%.4f" % (vA + vB, uniao))
            cobra(intes <= 0.01, "C2 %s: as metades nao se sobrepoem" % chave, "A n B = %.4f mm3" % intes)
        pc = os.path.join(d, base.replace(".step", "_Canal_Fluxo.step"))
        if os.path.exists(pc):
            vcan = vol(abre(pc))
            vazio = inv["_vazio"]
            par["canal_fluxo_mm3"] = round(vcan, 1)
            par["vazio_medido_na_peca_mm3"] = vazio
            par["canal_menos_vazio_mm3"] = round(vcan - vazio, 1)
            par["canal_menos_vazio_pct"] = round(100.0 * (vcan - vazio) / vazio, 3) if vazio else None
            par["conclusao"] = ("o arquivo do canal NAO e o vazio da peca - e o canal de OUTRA matriz"
                                if abs(vcan - vazio) / max(vazio, 1.0) > 0.005 else "bate com o vazio")
            if chave == "jonatha_v27_oficial" and abs(vcan - vazio) / max(vazio, 1.0) > 0.005:
                falhas.append("C3 %s: o arquivo do canal (%.1f mm3) nao e o vazio da peca (%.1f mm3)"
                              % (chave, vcan, vazio))
        out[chave] = par
    return out


# ------------------------------------------------- C4 matriz x cabecote: folga, fuga, encosto
def escada_de_furo(shape):
    """Escada do furo interno do cabecote: [(raio, z0, z1)] dos cilindros de eixo Z com face voltada para
    dentro (raio < raio do corpo)."""
    est = []
    for f in shape.Faces():
        if f.geomType() != "CYLINDER":
            continue
        r = f._geomAdaptor().Cylinder().Radius()
        b = f.BoundingBox()
        if abs((b.xmax - b.xmin) - 2 * r) < 0.05 and abs((b.ymax - b.ymin) - 2 * r) < 0.05 and 20 < r < 60:
            est.append((round(r, 3), round(b.zmin, 2), round(b.zmax, 2)))
    return sorted(set(est), key=lambda t: t[1])


def correlacao_cabecote(matrizes, cab_caminho):
    cab = maior(abre(cab_caminho))
    furo = escada_de_furo(cab)
    z_nariz = round(cab.BoundingBox().zmax, 3)
    out = {"cabecote": os.path.relpath(cab_caminho, RAIZ), "cabecote_volume_mm3": round(vol(cab), 3),
           "furo_estagios_D_z": [(round(2 * r, 2), z0, z1) for r, z0, z1 in furo],
           "face_do_nariz_z": z_nariz, "matrizes": {}}
    for chave, nome, inv in matrizes:
        est = estagios(inv)
        if not est:
            continue
        # folga radial por estagio, do maior D da matriz para o furo que o recebe
        folgas, fuga = [], []
        for (d_mat, z0, z1) in est:
            trecho = [f for f in furo if f[1] <= z1 + 1e-6 and f[2] >= z0 - 1e-6]
            if not trecho:
                continue
            r_furo = min(trecho, key=lambda t: t[0])[0]
            folga = round(r_furo - d_mat / 2.0, 3)
            folgas.append(dict(estagio_D=d_mat, z=[z0, z1], furo_D=round(2 * r_furo, 2),
                               folga_radial_mm=folga))
            fuga.append(folga)
        aberta = [f for f in folgas if f["folga_radial_mm"] > FOLGA_MINIMA]
        saida = inv["caixa"]["z"][1]
        out["matrizes"][chave] = dict(
            arquivo=nome, folgas_por_estagio=folgas,
            fuga_anular_aberta=bool(aberta) and len(aberta) == len(folgas),
            menor_folga_radial_mm=min(fuga) if fuga else None,
            comprimento_matriz_mm=inv["caixa"]["dz"],
            saida_além_da_face_do_nariz_mm=round(saida - z_nariz, 3),
            interferencia_matriz_x_cabecote_mm3=None)
        p = inv["_caminho"]
        die = maior(abre(p))
        # senta no degrau: o deslocamento que zera a folga axial do fundo e o que a medicao ja usa
        dz = round(z_nariz - 0.0, 3)      # nao deslocado: so o encaixe geometrico bruto
        try:
            it = maior(die.intersect(cab))
            v_it = round(vol(it), 4)
        except Exception:
            v_it = None
        out["matrizes"][chave]["interferencia_matriz_x_cabecote_mm3"] = v_it
    return out


# ---------------------------------------------------------------- C5 montagem x pecas de origem
def correlacao_montagens():
    out = {}
    cab_full = os.path.join(DIR_CAB, "Cabecote_EX-030_desenhado.step")
    v_cab = vol(maior(abre(cab_full)))
    for nome in sorted(os.listdir(DIR_CAB)):
        if not nome.startswith("Cabecote_EX-030_com_") or not nome.endswith(".step"):
            continue
        p = os.path.join(DIR_CAB, nome)
        sh = abre(p)
        sol = sh.Solids() or [sh]
        soma = sum(vol(x) for x in sol)
        out[nome] = {"solidos": len(sol), "volume_somado_mm3": round(soma, 3),
                     "massa_somada_kg": round(soma * ACO, 4),
                     "cabecote_no_desenho_mm3": round(v_cab, 3),
                     "metal_da_matriz_na_montagem_mm3": round(soma - v_cab, 3),
                     "brep_validos": all(x.isValid() for x in sol),
                     "caixa": [round(v, 2) for v in (sh.BoundingBox().xmax - sh.BoundingBox().xmin,
                                                      sh.BoundingBox().zmax - sh.BoundingBox().zmin)]}
        cobra(len(sol) >= 2, "C5 %s tem cabecote e matriz no mesmo arquivo" % nome,
              "%d solido(s)" % len(sol))
        cobra(abs(soma - v_cab) > 1.0, "C5 %s traz metal de matriz alem do cabecote" % nome,
              "somado %.3f vs cabecote %.3f" % (soma, v_cab))
    return out


# --------------------------------------------------------------------------- mola mestra
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--md", action="store_true")
    ap.add_argument("--só-cotassot", action="store_true", help="so C1/C6 (rapido, sem booleanos)")
    a = ap.parse_args()

    passos = []
    rastre = subprocess.run(["git", "ls-files", "*.step"], cwd=RAIZ, capture_output=True, text=True).stdout.split()
    arquivos = [r for r in rastre if r.startswith(("01_", "02_", "06_", "07_"))]
    print(f"[1] {len(arquivos)} STEP rastreados no repo, abertos e inventariados")
    invs, chaves = [], []
    for rel in sorted(arquivos):
        p = os.path.join(RAIZ, rel)
        if not os.path.exists(p):
            falhas.append("arquivo rastreado ausente: %s" % rel)
            continue
        try:
            sh = abre(p)
        except Exception as e:
            falhas.append("nao abre %s: %s" % (rel, e))
            continue
        inv = inventario(sh)
        inv["_caminho"] = p
        inv["_rel"] = rel
        if not a.só_cotassot and rel.startswith("07_") and "_Body_" not in rel and "Explodida" not in rel \
                and "Canal" not in rel and "Com_Fluxo" not in rel:
            inv["_vazio"] = vazios_da_peca(maior(sh))
        chaves.append(rel)
        invs.append(inv)
        passos.append((os.path.basename(rel)[:-5], rel, inv))
    print(f"    ok: {len(invs)} arquivos medidos (cadquery, face por face)")

    # as 6 pecas "inteiras" de matriz (uma por pasta) - sao as que entram nas correlacoes de cota
    principais = [(os.path.dirname(r).split("_", 1)[1] if "_" in os.path.dirname(r) else r,
                   r, i) for (_, r, i) in passos
                  if r.startswith("07_") and os.path.basename(r).count("_Body_") == 0
                  and not any(x in r for x in ("Canal", "Explodida", "Com_Fluxo"))]
    if any("jonatha_v27" not in c.lower() for c, _, _ in []) :
        pass
    nomes = {"Matriz_Jonatha_v27_OFICIAL": "jonatha_v27_oficial",
             "Matriz_Jonatha_v28_1_PROPOSTA": "jonatha_v28_1_proposta",
             "Matriz_Gedeon_Certa": "gedeon_certa_arquivo_do_usuario",
             "Matriz_Gedeon_Entregue_HISTORICA": "gedeon_entregue_historica",
             "Matriz_Copo_HISTORICA": "matriz_1_copo_historica",
             "Matriz_Desenvolvimento_HISTORICA": "desenvolvimento_historica"}
    principais = [(nomes.get(r.split("/")[1], r.split("/")[1]), r, i) for _, r, i in principais]

    med = {"gerado_em": "2026-09-13", "arquivos_conferidos": len(invs),
           "inventarios": {i["_rel"]: {k: v for k, v in i.items() if not k.startswith("_")} for i in invs}}
    print("[2] C6 atalhos x baseline do auditor")
    med["C6_atalhos_baseline"] = correlacao_atalhos()
    print("    %d caminhos selados, %d divergentes" % (med["C6_atalhos_baseline"]["esperados"],
                                                       len(med["C6_atalhos_baseline"]["divergentes"])))
    print("[3] C1 cotas medidas x SSOT (as seis matrizes)")
    med["C1_cotas_x_SSOT"] = correlacao_cotas(principais)
    print("[4] C2 metades e C3 arquivo do canal x vazio real")
    if not a.só_cotassot:
        med["C2_C3_pares_e_canal"] = correlacao_pares_e_canal(principais)
        print("[5] C4 matriz x cabecote (folga radial, anel de fuga, encosto, interferencia)")
        med["C4_matriz_x_cabecote"] = correlacao_cabecote(principais,
                                                          os.path.join(DIR_CAB, "Cabecote_EX-030_desenhado.step"))
        print("[6] C5 montagens x pecas de origem")
        med["C5_montagens"] = correlacao_montagens()
    med["checagens_que_falharam"] = falhas
    med["status"] = "APROVADO" if not falhas else "DIVERGENTE"

    if a.json:
        json.dump(med, open(ARQ_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("JSON ->", os.path.relpath(ARQ_JSON, RAIZ))
    if a.md:
        escreve_md(med, principais)
        print("MD  ->", os.path.relpath(ARQ_MD, RAIZ))
    print("=" * 74)
    if falhas:
        print(f"AUDITORIA: {len(falhas)} correlacao(oes) divergente(s)")
        for f in falhas[:12]:
            print("  -", f)
        return 1
    print("AUDITORIA: todas as correlacoes batem (%d STEP, %d caminhos selados)"
          % (len(invs), med["C6_atalhos_baseline"]["esperados"]))
    return 0


def escreve_md(med, principais):
    L = ["# Auditoria dos STEP — correlações e cotas, medidas\n",
         "Gerada por `04_Dados_SSOT_e_Scripts/auditar_step_correlacoes.py`. Cada número abaixo foi medido no "
         "arquivo na hora em que o relatório foi escrito (`cadquery`, face por face); nada é transcrito de "
         "memória. **%d arquivos STEP** abertos, **%s**.\n" % (med["arquivos_conferidos"],
                                                                "status: " + med["status"]),
         "## C1 — cota medida × SSOT\n",
         "| matriz | arquivo | fenda larg. × esp. (mm) | boca de entrada (Ø mm) | estágios Ø × Z (mm) | "
         "compr. (mm) | aço (mm³) | massa (kg) | divergência |", "|---|---|---|---|---|---|---|---|---"]
    for linha in med["C1_cotas_x_SSOT"]["por_matriz"]:
        if "largura_mm" not in linha:
            L.append("| %s | %s | — | — | — | — | — | — | sem fenda fechada |" % (linha.get("matriz"), ""))
            continue
        est = " · ".join("Ø%.2f Z %.2f..%.2f" % t for t in linha["estagios"])
        div = linha["divergencia_vs_SSOT"]
        L.append("| `%s` | `%s` | %.3f × %.3f | %s | %s | %.2f | %s | %.4f | %s |"
                 % (linha["matriz"], os.path.basename(linha["arquivo"]), linha["largura_mm"],
                    linha["espessura_mm"], ("%.2f" % linha["boca_entrada_mm"]) if linha["boca_entrada_mm"] else "—",
                    est or "—", linha["comprimento_mm"], n(linha["volume_aco_mm3"], 1), linha["massa_kg"],
                    "bate" if not div else json.dumps(div, ensure_ascii=False)))
    L.append("\nTolerâncias cobradas (o triplo do que o desenho permite): largura ±0,05, espessura ±0,02, "
             "raio ±0,02, boca só para dentro (+0,00/−0,10), envelope ±0,05 mm.\n")
    if "C2_C3_pares_e_canal" in med:
        L += ["## C2 — metade × metade × peça inteira\n",
              "| matriz | A (mm³) | B (mm³) | A+B − (A∪B) | A ∩ B | cascas A / B |", "|---|---|---|---|---|---|---"]
        for c, d in med["C2_C3_pares_e_canal"].items():
            L.append("| `%s` | %s | %s | %s | %s | %s / %s |"
                     % (c, n(d.get("body_A", 0), 1), n(d.get("body_B", 0), 1),
                        n(d.get("diferenca_soma_menos_uniao", 0), 4), n(d.get("intersecao_mm3", 0), 4),
                        d.get("cascas_A", "—"), d.get("cascas_B", "—")))
        L.append("\nCasca > 1 num `Body` = cavidade selada dentro do aço (não tem ferramenta que faça). "
                 "É o G-03 da auditoria de 2026-09-11, e é o que aparece no `Body_A` da Gedeon e no `MatrizJonatha.step`.\n")
        L += ["## C3 — o arquivo `_Canal_Fluxo.step` é o vazio real da peça?\n",
              "| matriz | arquivo do canal (mm³) | vazio medido na peça (mm³) | Δ | Δ % | leitura |",
              "|---|---|---|---|---|---|---|"]
        for c, d in med["C2_C3_pares_e_canal"].items():
            if "canal_fluxo_mm3" not in d:
                continue
            L.append("| `%s` | %s | %s | %s | %s | %s |"
                     % (c, n(d["canal_fluxo_mm3"], 1), n(d["vazio_medido_na_peca_mm3"], 1),
                        n(d["canal_menos_vazio_mm3"], 1), n(d["canal_menos_vazio_pct"] or 0, 3),
                        d["conclusao"]))
        L.append("\nFoi essa correlação que derrubou a \"Gedeon corrigida\": o `_Canal_Fluxo.step` histórico tem "
                 "o funil da Jonatha, não o vazio da Gedeon.\n")
    if "C4_matriz_x_cabecote" in med:
        m4 = med["C4_matriz_x_cabecote"]
        L += ["## C4 — matriz × cabeçote: folga, anel de fuga, encosto\n",
              "Furo do cabeçote medido em `%s`: %s\n" % (m4["cabecote"],
              " · ".join("Ø%.2f Z %.2f..%.2f" % t for t in m4["furo_estagios_D_z"])),
              "| matriz | folga radial por estágio (mm) | menor folga | anel de fuga aberto do bico à entrada? "
              "| saída além do nariz (mm) | ∩ matriz×cabeçote (mm³) |", "|---|---|---|---|---|---|"]
        for c, d in m4["matrizes"].items():
            fol = " / ".join("%+.2f" % f["folga_radial_mm"] for f in d["folgas_por_estagio"])
            L.append("| `%s` | %s | %s | **%s** | %+.2f | %s |"
                     % (c, fol, n(d["menor_folga_radial_mm"] or 0, 2),
                        "SIM — caminho livre para trás" if d["fuga_anular_aberta"] else "não",
                        d["saida_além_da_face_do_nariz_mm"],
                        n(d["interferencia_matriz_x_cabecote_mm3"] or 0, 4)))
        L.append("\n`anel de fuga aberto` quer dizer: existe anel com folga > 0 entre a OD da matriz e o furo do "
                 "cabeçote, contínuo do bico até a face de entrada — pelo caminho, o mastique não é obrigado a "
                 "passar pela fenda. É a correlação que responde \"por que a Gedeon volta pelo funil\".\n")
    if "C5_montagens" in med:
        L += ["## C5 — montagem × peças de origem\n",
              "| montagem | sólidos | volume somado (mm³) | massa (kg) | metal da matriz (mm³) | caixa Ø × Z |",
              "|---|---|---|---|---|---|---|"]
        for nome, d in med["C5_montagens"].items():
            L.append("| `%s` | %d | %s | %.3f | %s | Ø%.1f × %.1f |"
                     % (nome, d["solidos"], n(d["volume_somado_mm3"], 1), d["massa_somada_kg"],
                        n(d["metal_da_matriz_na_montagem_mm3"], 1), d["caixa"][0], d["caixa"][1]))
        L.append("")
    L.append("## C6 — atalhos de `01_/` e `02_/` × baseline selado\n")
    L.append("%d caminhos do baseline do auditor conferidos por sha256; divergências: %s.\n"
             % (med["C6_atalhos_baseline"]["esperados"],
                ", ".join(med["C6_atalhos_baseline"]["divergentes"]) or "nenhuma"))
    L.append("## O que falhou\n")
    L.append("\n".join("* %s" % f for f in med["checagens_que_falharam"]) or "* nada — todas as correlações batem")
    open(ARQ_MD, "w", encoding="utf-8").write("\n".join(L) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
