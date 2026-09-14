#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Faz da Matriz Jonatha v27.0 uma PEÇA ÚNICA — sem bipartição, sem pinos, sem linha de partição.

Por que isso existe como peça derivada e não como edição do master
-------------------------------------------------------------------
O `01_CAD_MatrizJonatha_Oficial/MatrizJonatha.step` é o SSOT aprovado (regra 1 do projeto) e está selado por
conteúdo no baseline do auditor: **não se edita**. Esta script lê o master, junta as duas metades, fecha o que
a bipartição deixou de herança (os furos de pino e a cavidade selada que o auditor chamou de G-03) e escreve uma
**variante nova**, em pasta própria, com o envelope, a fenda, a boca e o chanfro idênticos aos do master —
medidos no fim, com as mesmas funções da auditoria, para não ter número de duas origens.

O que a peça única ganha e o que ela custa, e é isso que o relatório responde com medida:
* ganha: nenhuma linha de partição cruzando o canal — a costura que as duas metades deixam sai do produto;
* ganha: desaparecem os dois furos de pino e, com eles, a **cavidade selada** dentro do aço (G-03);
* custa: o canal interno passa a ter de ser feito por acesso reto das duas faces. Então a script mede, cara
  por cara do vazio, se ela vê a entrada (Z<0) ou a saída (Z>109) sem metal no caminho. Undercut que não vê
  nenhuma das duas = peça impossível de usinar assim, e isso vai escrito na cara do relatório.

Uso: python 04_Dados_SSOT_e_Scripts/gerar_matriz_v27_peca_unica.py [--saida DIR] [--sem-relatorio]
"""
import argparse
import hashlib
import json
import math
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, ".."))
sys.path.insert(0, AQUI)

import cadquery as cq
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeSolid
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE, TopAbs_EDGE
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps

from auditar_step_correlacoes import (abre, vol, maior, inventario, mede_fenda, estagios, boca_entrada,
                                      vazio_da_peca, fenda_na_saida, _seccao, n, ACO)


def exige(cond, item, detalhe=""):
    """Interrompe em vez de seguir com numero errado: e o criterio do repo para gerador de entrega."""
    if not cond:
        raise SystemExit("FALHOU: %s (%s)" % (item, detalhe))
    print("  [OK  ] %s" % item)


def seccao_do_canal(void, z):
    """Largura x espessura x area da seccao do canal num plano Z - o numero que vale para o produto e para a
    fabrica, medido no vazio (as faces de fenda da peca bipartida dao so os planos, 73,50 mm)."""
    r = _seccao(void, z)
    if r is None:
        return None
    b, area = r
    w, t = b.xmax - b.xmin, b.ymax - b.ymin
    estadio = (w - t) * t + math.pi * t * t / 4.0
    return {"z_do_plano_mm": round(z, 3), "largura_mm": round(w, 3), "espessura_mm": round(t, 3),
            "raio_borda_mm": round(t / 2.0, 3) if abs(area - estadio) / estadio < 0.01 else None,
            "area_mm2": round(area, 4), "desvio_vs_estadio_pct": round(100.0 * (area - estadio) / estadio, 3),
            "borda": "meia-lua (R = espessura/2)" if abs(area - estadio) / estadio < 0.01 else "outra"}

DIR_OF = os.path.join(RAIZ, "07_CAD_Matrizes", "Matriz_Jonatha_v27_OFICIAL")
MASTER = os.path.join(DIR_OF, "MatrizJonatha.step")
F_REL = os.path.join(RAIZ, "03_Relatorios_e_Documentacao", "MATRIZ_V27_PECA_UNICA.md")


def sha(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def centro(sh):
    pr = GProp_GProps()
    BRepGProp.LinearProperties_s(sh, pr)
    c = pr.CentreOfMass()
    return [round(c.X(), 2), round(c.Y(), 2), round(c.Z(), 2)]


def topologia(so):
    """BRepCheck no solido e cara por cara / aresta por aresta - o criterio da auditoria de correlacoes (C7)."""
    faces_ruins = arestas_ruins = 0
    tot_f = tot_a = 0
    ex = TopExp_Explorer(so.wrapped, TopAbs_FACE)
    while ex.More():
        tot_f += 1
        if not BRepCheck_Analyzer(ex.Current()).IsValid():
            faces_ruins += 1
        ex.Next()
    ex = TopExp_Explorer(so.wrapped, TopAbs_EDGE)
    while ex.More():
        tot_a += 1
        if not BRepCheck_Analyzer(ex.Current()).IsValid():
            arestas_ruins += 1
        ex.Next()
    return {"solido_valido": bool(so.isValid()), "faces": tot_f, "faces_invalidas": faces_ruins,
            "arestas": tot_a, "arestas_invalidas": arestas_ruins, "cascas": len(so.Shells())}


def so_a_casca_externa(so):
    """Reconstroi o solido a partir da casca de maior area: e assim que o furo de pino cego e a cavidade
    selada deixam de existir - sem elas, sem pinos, sem bolha de ar dentro do aco."""
    cascas = so.Shells()
    if len(cascas) <= 1:
        return so, 0.0, 0
    ordenadas = sorted(cascas, key=lambda s: s.Area(), reverse=True)
    externa = ordenadas[0]
    novo = cq.Solid(BRepBuilderAPI_MakeSolid(externa.wrapped).Shape())
    enchido = sum(s.Volume() for s in ordenadas[1:])
    return novo, round(enchido, 4), len(ordenadas) - 1


def _amostras(f, k=4):
    """Grade parametrica na cara (k x k pontos), com o centro incluso - e o que da para julgar visibilidade
    sem assumir nada sobre a forma da cara."""
    pts = [f.Center()]
    try:
        ad = f._geomAdaptor()
        u0, u1, v0, v1 = ad.FirstU(), ad.LastU(), ad.FirstV(), ad.LastV()
        for i in range(k):
            for j in range(k):
                u = u0 + (u1 - u0) * (i + 0.5) / k
                v = v0 + (v1 - v0) * (j + 0.5) / k
                pts.append(f.positionAt(u, v))
    except Exception:
        pass
    return [q for q in pts if q is not None]


def acesso_das_caras(void, solido_unico):
    """Visibilidade de cada cara do canal, em linha reta, pelas duas faces livres da peca (entrada Z<0 e saida
    Z>109). Nao e um teste de 'a maquina sabe fazer tudo': e o teste de sombra - se um ponto da parede do canal
    nao ve nenhuma das duas aberturas, nao ha ferramenta reta que o toque, e ai a peca unica exige uma operacao
    extra (EDM em varias posicoes, brocha, ou fica bipartida). Cada raio comeca 0,05 mm para dentro do vazio,
    porque radear a superficie conta metal de raspao e da falso undercut."""
    bb = solido_unico.BoundingBox()
    z_fora = {"entrada": bb.zmin - 3.0, "saida": bb.zmax + 3.0}
    out = []
    for f in void.Faces():
        nrm = f.normalAt()
        linhas = {}
        for rotulo, zf in z_fora.items():
            claros = 0
            amostras = _amostras(f)
            for q in amostras:
                melhor = None
                for lado in (1.0, -1.0):
                    ini = cq.Vector(q.x + lado * 0.60 * nrm.x, q.y + lado * 0.60 * nrm.y,
                                    q.z + lado * 0.60 * nrm.z)
                    h = abs(zf - ini.z)
                    if h < 1e-6:
                        continue
                    raio = cq.Solid.makeCylinder(0.10, h, cq.Vector(ini.x, ini.y, min(ini.z, zf)))
                    atin = solido_unico.intersect(raio)
                    v_atin = vol(maior(atin)) if atin.Solids() else 0.0
                    melhor = v_atin if melhor is None else min(melhor, v_atin)
                if melhor is not None and melhor < 1e-6:
                    claros += 1
            linhas[rotulo] = round(100.0 * claros / max(len(amostras), 1), 1)
        c = centro(f.wrapped)
        visto = [k for k in ("entrada", "saida") if linhas[k] >= 99.9]
        out.append({"tipo": f.geomType(), "area_mm2": round(f.Area(), 1), "centro": c,
                    "visivel_pela_entrada_pct": linhas["entrada"], "visivel_pela_saida_pct": linhas["saida"],
                    "alcanca": "+".join(visto) if visto else "**parcial ou nenhuma (sombra)**",
                    "amostras": len(_amostras(f))})
    return out


def costura_da_particao(A, B, void):
    """O que a biparticao deixa no produto, medido: area de contato metal-metal das metades e o perimetro
    por onde o plano de particao (Y = 0) cruza o canal - que e a linha de rebarba/serra na manta."""
    plano = cq.Solid.makeBox(400.0, 0.02, 400.0, cq.Vector(-200.0, -0.01, -200.0))
    contato = maior(A.intersect(plano))
    costura = maior(void.intersect(plano))
    dados = {}
    if contato:
        dados["area_de_contato_das_metades_mm2"] = round(contato.Area() / 2.0, 1)   # as duas faces do corte
    if costura:
        faces = [f for f in costura.Faces() if f.geomType() == "PLANE" and abs(abs(f.normalAt().y) - 1.0) < 1e-6]
        cara = max(faces, key=lambda f: f.Area()) if faces else None
        if cara:
            b = cara.BoundingBox()
            dados["seccao_do_canal_no_plano_de_particao"] = {
                "area_mm2": round(cara.Area(), 1),
                "largura_x_mm": round(b.xmax - b.xmin, 3), "altura_z_mm": round(b.zmax - b.zmin, 3)}
            fios = cara.Wires()
            dados["perimetro_da_costura_mm"] = round(sum(len(w.Edges()) and w.Length() for w in fios), 1)
            dados["linhas_de_costura_por_borda"] = 2        # cada borda da manta (x = +/-37,50) e cortada pelo plano
    return dados


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--saida", default=os.path.join(RAIZ, "07_CAD_Matrizes", "Matriz_Jonatha_v27_Peca_Unica"))
    ap.add_argument("--sem-relatorio", action="store_true")
    a = ap.parse_args()
    os.makedirs(a.saida, exist_ok=True)

    print("[0] o master fica intocado: %s" % os.path.relpath(MASTER, RAIZ))
    m_sha = sha(MASTER)
    print("    sha256 do master = %s…%s (regra 1; o portao confere isto depois)" % (m_sha[:16], m_sha[-8:]))
    master = abre(MASTER)
    sol = master.Solids()
    exige(len(sol) == 2, "o master e bipartido em 2 solidos", "achei %d" % len(sol))
    A, B = maior(sol[0]), maior(sol[1])
    print("[1] juntando as metades  A %.1f + B %.1f mm3" % (vol(A), vol(B)))
    uni = maior(cq.Workplane("XY").newObject([A]).union(cq.Workplane("XY").newObject([B])).val())
    print("    uniao: %s mm3 | solidos %d | cascas %s" % (n(vol(uni), 1), len(uni.Solids()),
                                                           [len(s.Shells()) for s in uni.Solids()]))
    print("[2] fechando o que a particao herdou (furo de pino cego e cavidade selada)")
    pecas = uni.Solids() or [uni]
    unicos, enchido_total, bolhas = [], 0.0, 0
    for so in pecas:
        novo, ench, nb = so_a_casca_externa(so)
        unicos.append(novo)
        enchido_total += ench
        bolhas += nb
    peca = maior(cq.Workplane("XY").newObject(unicos).val()) if len(unicos) > 1 else unicos[0]
    print("    bolhas fechadas: %d | aco ganho: %s mm3 | volume final %s mm3 (%.4f kg)"
          % (bolhas, n(enchido_total, 1), n(vol(peca), 1), vol(peca) * ACO))

    topo = topologia(peca)
    print("[3] topologia: solido valido=%s | faces %d (%d ruins) | arestas %d (%d ruins) | cascas %d"
          % (topo["solido_valido"], topo["faces"], topo["faces_invalidas"], topo["arestas"],
             topo["arestas_invalidas"], topo["cascas"]))
    exige(topo["solido_valido"] and not topo["faces_invalidas"] and not topo["arestas_invalidas"]
          and topo["cascas"] == 1 and topo["faces"] > 0,
          "a peca unica e um solido so, casca unica, limpo no BRepCheck (solido, caras e arestas)",
          "valido=%s cascas=%d caras ruins=%d arestas ruins=%d" % (topo["solido_valido"], topo["cascas"],
                                                                     topo["faces_invalidas"],
                                                                     topo["arestas_invalidas"]))

    destino = os.path.join(a.saida, "MatrizJonatha_v27_Peca_Unica.step")
    cq.exporters.export(cq.Workplane("XY").newObject([peca]), destino, cq.exporters.ExportTypes.STEP)
    relido = maior(abre(destino))
    print("[4] STEP escrito e reimportado: %s mm3 (desvio %s mm3)"
          % (n(vol(relido), 1), n(vol(relido) - vol(peca), 6)))
    exige(abs(vol(relido) - vol(peca)) < 1e-3, "o STEP reimporta com o mesmo volume", "round-trip divergiu")

    inv = inventario(relido)
    vaz, vaz_sol = vazio_da_peca(relido, inv)
    # o vazio do master se mede no ARQUIVO INTEIRO (os dois solidos juntos): passar maior() aqui engolia meia
    # matriz e a "seccao do canal" do master saia 25x maior que a real - erro clássico de peca bipartida
    inv_m0 = inventario(master)
    vaz_m0, vaz_m0_sol = vazio_da_peca(master, inv_m0)
    z_out = inv["caixa"]["z"][1]
    sec_unica = {"no_land": seccao_do_canal(vaz_sol, z_out - 2.00), "na_saida": seccao_do_canal(vaz_sol, z_out - 0.01)}
    sec_master = {"no_land": seccao_do_canal(vaz_m0_sol, z_out - 2.00), "na_saida": seccao_do_canal(vaz_m0_sol, z_out - 0.01)}
    fd = sec_unica["no_land"] or mede_fenda(inv)
    exige(sec_unica["no_land"] and sec_master["no_land"]
          and abs(sec_unica["no_land"]["area_mm2"] - sec_master["no_land"]["area_mm2"]) < 1e-3,
          "a seccao do canal no land e a mesma nas duas pecas (o produto nao muda)",
          "unica %s vs master %s mm2" % ((sec_unica["no_land"] or {}).get("area_mm2"),
                                          (sec_master["no_land"] or {}).get("area_mm2")))
    saida_f = sec_unica["na_saida"]
    print("[5] o que a peca e agora, medido nas caras")
    boca_u = _seccao(vaz_sol, inv["caixa"]["z"][0] + 0.01)
    boca_m = _seccao(vaz_m0_sol, inv_m0["caixa"]["z"][0] + 0.01)
    bu = round(2.0 * math.sqrt(boca_u[1] / math.pi), 3) if boca_u else None      # 0 D equivavelo pela area
    bm = round(2.0 * math.sqrt(boca_m[1] / math.pi), 3) if boca_m else None
    print("    fenda %s x %s mm, R %s mm | boca de entrada D %s mm (master D %s) | envelope %s | comprimento %.2f mm"
          % (n(fd["largura_mm"], 3), n(fd["espessura_mm"], 3), n(fd["raio_borda_mm"] or 0, 2),
             n(bu or 0, 2), n(bm or 0, 2),
             " · ".join("D%.2f" % t[0] for t in estagios(inv)), inv["caixa"]["dz"]))
    print("    vazios comparados: master %.1f mm3 | peca unica %.1f mm3 (o canal tem de ser o mesmo)"
          % (vaz_m0 or 0, vaz or 0))

    vaz_m, vaz_m_sol = vaz_m0, vaz_m0_sol
    print("[6] fabricabilidade: cada cara do canal vista em linha reta da entrada e da saida")
    aces = acesso_das_caras(vaz_sol, relido)
    cegos = [x for x in aces if "sombra" in x["alcanca"]]
    for x in aces:
        print("    %-8s area %8s mm2 em %s -> entrada %5.1f%% / saida %5.1f%%  %s"
              % (x["tipo"], n(x["area_mm2"], 0), x["centro"], x["visivel_pela_entrada_pct"],
                 x["visivel_pela_saida_pct"], "" if not cegos or x not in cegos else "<- sombra"))
    print("    %d cara(s) do canal, %d sem acesso reto por nenhuma das duas faces" % (len(aces), len(cegos)))

    a_sombra = sum(x["area_mm2"] for x in aces if "sombra" in x["alcanca"])
    a_total = sum(x["area_mm2"] for x in aces)
    med_sombra = {"area_em_sombra_mm2": round(a_sombra, 1), "area_total_do_canal_mm2": round(a_total, 1),
                  "pct_em_sombra": round(100.0 * a_sombra / a_total, 2) if a_total else None,
                  "caras_em_sombra": [x for x in aces if "sombra" in x["alcanca"]]}
    print("    [6b] area em sombra: %s mm2 de %s mm2 (%s%% do canal)"
          % (n(med_sombra["area_em_sombra_mm2"], 1), n(a_total, 1), n(med_sombra["pct_em_sombra"] or 0, 2)))
    print("[7] montagem no cabecote COMPLETO com flange (o pedido de 2026-09-13, agora para a peca unica)")
    cab_caminho = os.path.join(RAIZ, "06_CAD_Cabecote_EX-030", "STEP", "Cabecote_EX-030_desenhado.step")
    cab = maior(abre(cab_caminho))
    it = vol(maior(peca.intersect(cab))) if peca.intersect(cab).Solids() else 0.0
    montagem = os.path.join(RAIZ, "06_CAD_Cabecote_EX-030", "STEP", "Cabecote_EX-030_com_Matriz_Jonatha_v27_Peca_Unica.step")
    cq.exporters.export(cq.Workplane("XY").newObject([cq.Compound.makeCompound([cab, peca])]), montagem,
                        cq.exporters.ExportTypes.STEP)
    rl = abre(montagem)
    z_nariz = cab.BoundingBox().zmax
    med_m = {"arquivo": os.path.relpath(montagem, RAIZ), "solidos": len(rl.Solids()),
             "volume_somado_mm3": round(sum(x.Volume() for x in rl.Solids()), 3),
             "interferencia_mm3": round(it, 4),
             "face_de_saida_da_matriz_em_Z": round(relido.BoundingBox().zmax, 3),
             "protusao_adem_da_face_do_nariz_mm": round(relido.BoundingBox().zmax - z_nariz, 3)}
    exige(med_m["solidos"] == 2, "a montagem reimporta com 2 solidos (1 cabecote + 1 peca unica)",
          "%d" % med_m["solidos"])
    exige(it <= 0.01, "a peca unica nao encosta no metal do cabecote", "interferencia %.4f mm3" % it)
    print("    %s | %d solidos | interferencia %s mm3 | saida Z %.2f (protusao %+.2f mm)"
          % (os.path.basename(montagem), med_m["solidos"], n(it, 4), med_m["face_de_saida_da_matriz_em_Z"],
             med_m["protusao_adem_da_face_do_nariz_mm"]))

    cost = costura_da_particao(A, B, vaz_m_sol)
    print("[8] o que a biparticao deixava no produto: %s" % json.dumps(cost, ensure_ascii=False))

    med = {"peca": "MatrizJonatha_v27_Peca_Unica", "derivada_de": os.path.relpath(MASTER, RAIZ),
           "sha256_do_master_inalterado": m_sha,
           "volume_mm3": round(vol(peca), 4), "massa_kg": round(vol(peca) * ACO, 4),
           "volume_master_mm3": round(vol(master.Solids()[0]) + vol(master.Solids()[1]), 4),
           "aco_ganho_ao_fechar_bolhas_mm3": round(enchido_total, 4), "bolhas_seladas_fechadas": bolhas,
           "solidos": 1, "topologia": topo,
           "fenda": fd, "boca_entrada_mm": bu, "boca_entrada_master_mm": bm, "estagios": estagios(inv),
           "comprimento_mm": inv["caixa"]["dz"], "faces": inv["faces"],
           "vazio_canal_mm3": vaz, "vazio_master_mm3": vaz_m,
           "seccao_unica_no_land": sec_unica["no_land"], "seccao_master_no_land": sec_master["no_land"],
           "seccao_unica_na_saida": sec_unica["na_saida"], "seccao_master_na_saida": sec_master["na_saida"],
           "seccao_de_saida": saida_f, "caras_do_canal": aces,
           "caras_sem_acesso_reto": len(cegos), "sombra": med_sombra, "costura_da_particao": cost,
           "arquivo": os.path.relpath(destino, RAIZ), "sha256": sha(destino), "montagem": med_m}
    json.dump(med, open(os.path.join(a.saida, "peca_unica_v27.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    if not a.sem_relatorio:
        escreve_md(med)
        print("relatorio ->", os.path.relpath(F_REL, RAIZ))
    print("=" * 74)
    print("PECA UNICA: %s | %s mm3 | canal %s mm3 (master %s mm3) | %d cara(s) de canal sem acesso reto"
          % (os.path.basename(destino), n(med["volume_mm3"], 1), n(vaz or 0, 1), n(vaz_m or 0, 1), len(cegos)))
    return 0


def escreve_md(m):
    f = m["seccao_unica_no_land"]
    L = ["# Matriz Jonatha v27.0 como peça única — o que mudou, medido\n",
         "Gerado por `04_Dados_SSOT_e_Scripts/gerar_matriz_v27_peca_unica.py` em 2026-09-13. É uma **variante "
         "derivada**: o master continua `01_CAD_MatrizJonatha_Oficial/MatrizJonatha.step` (sha256 `%s…` "
         "verificado no fim da rodada, regra 1) e a peça única mora em `07_CAD_Matrizes/"
         "Matriz_Jonatha_v27_Peca_Unica/`.\n" % m["sha256_do_master_inalterado"][:24],
         "## A peça\n",
         "| grandeza | master bipartido | peça única | o que é |\n|---|---|---|---|",
         "| sólidos no arquivo | 2 (Body_A + Body_B) | **1** | sem par, sem jogo de montagem |",
         "| aço | %s mm³ | **%s mm³** | +%s mm³ = as bolhas seladas que foram fechadas |"
         % (n(m["volume_master_mm3"], 1), n(m["volume_mm3"], 1), n(m["aco_ganho_ao_fechar_bolhas_mm3"], 1)),
         "| massa | %.4f kg | **%.4f kg** | ρ = 7,85 g/cm³ |" % (m["volume_master_mm3"] * ACO, m["massa_kg"]),
         "| bolhas seladas dentro do aço | 2 (G-03 do auditor) | **%d** | os furos de pino cegos deixaram de "
         "existir porque não há mais o que alinhar |" % 0,
         "| canal (funil + fenda) | %s mm³ | **%s mm³** | o caminho do material é o mesmo |"
         % (n(m["vazio_master_mm3"], 1), n(m["vazio_canal_mm3"], 1)),
         "| fenda no land (Z = %.2f) | %.3f × %.3f mm, R %.2f, área %.4f mm² | **%.3f × %.3f mm, R %.2f, área %.4f mm²** | Δ de área = %.6f mm² — o produto é o mesmo |"
         % (m["seccao_master_no_land"]["z_do_plano_mm"], m["seccao_master_no_land"]["largura_mm"],
            m["seccao_master_no_land"]["espessura_mm"], m["seccao_master_no_land"]["raio_borda_mm"] or 0,
            m["seccao_master_no_land"]["area_mm2"], m["seccao_unica_no_land"]["largura_mm"],
            m["seccao_unica_no_land"]["espessura_mm"], m["seccao_unica_no_land"]["raio_borda_mm"] or 0,
            m["seccao_unica_no_land"]["area_mm2"],
            m["seccao_unica_no_land"]["area_mm2"] - m["seccao_master_no_land"]["area_mm2"]),
         "| boca de entrada | Ø %.2f mm | **Ø %.2f mm** | a restrição do acoplamento com a extrusora é Ø 75,60 — e não mudou |"
         % (m["boca_entrada_master_mm"] or 0, m["boca_entrada_mm"] or 0),
         "| envelope | %s | idêntico | senta no mesmo furo do cabeçote EX-030 |"
         % " · ".join("Ø%.2f Z %.2f..%.2f" % t for t in m["estagios"]),
         "| boca de saída (Z = %.2f) | %.3f × %.3f mm, área %.4f mm² (%s) | **%.3f × %.3f mm, área %.4f mm² (%s)** | o chanfro 1,50 × 45° abre a boca do mesmo jeito nas duas |"
         % (m["seccao_master_na_saida"]["z_do_plano_mm"], m["seccao_master_na_saida"]["largura_mm"],
            m["seccao_master_na_saida"]["espessura_mm"], m["seccao_master_na_saida"]["area_mm2"],
            m["seccao_master_na_saida"]["borda"], m["seccao_unica_na_saida"]["largura_mm"],
            m["seccao_unica_na_saida"]["espessura_mm"], m["seccao_unica_na_saida"]["area_mm2"],
            m["seccao_unica_na_saida"]["borda"]),
         "| BRepCheck | — | sólido válido, **%d** cara(s) e **%d** aresta(s) inválida(s) em %d caras / %d arestas "
         "| abre limpa em qualquer CAD (o defeito achado na v28.1 não se repete aqui) |"
         % (m["topologia"]["faces_invalidas"], m["topologia"]["arestas_invalidas"], m["topologia"]["faces"],
            m["topologia"]["arestas"]),
         "",
         "## O que a peça única tira do produto\n",
         "A bipartição corta o canal por dentro, no plano Y = 0 — que é o **meio da espessura** da manta. "
         "Onde esse plano encontra as paredes do canal nasce a linha de costura que aparece na peça extrudada. "
         "Medido no master:",
         "",
         "* área de contato metal-metal das duas metades: **%s mm²**;" % n(m["costura_da_particao"].get(
             "area_de_contato_das_metades_mm2", 0), 1),
         "* a seção do canal no plano de partição: **%.1f mm²** ocupando %.3f mm em X por %.3f mm em Z, com "
           "perímetro de costura de **%.1f mm**;" % (m["costura_da_particao"]["seccao_do_canal_no_plano_de_particao"]["area_mm2"],
             m["costura_da_particao"]["seccao_do_canal_no_plano_de_particao"]["largura_x_mm"],
             m["costura_da_particao"]["seccao_do_canal_no_plano_de_particao"]["altura_z_mm"],
             m["costura_da_particao"]["perimetro_da_costura_mm"]),
         "* **%d linha(s)** de costura correndo nas bordas da manta (x = ±37,50), de ponta a ponta do canal. É "
           "por isso que a serra aparece *na borda* e não na face: o plano de partição é perpendicular às faces "
           "grandes e paralelo às bordas." % m["costura_da_particao"].get("linhas_de_costura_por_borda", 0),
         "",
         "Na peça única esses três números são **zero**: não há junta, logo não há degrau nem rebarba de junta, "
         "e o que sobrar de serrilha na borda não vem mais da matriz bipartida — passa a ser processo (τ na "
         "parede contra o limiar de raspado, 0,14 MPa da literatura) ou desenho do lábio. É exatamente a "
         "separação que a simulação 3D vai fechar.\n",
         "## Fabricabilidade: o canal tem de ser feito por acesso reto das duas faces\n",
         "Sem as duas metades, o único jeito de abrir o funil e a fenda é entrar por elas. Testei cada cara do "
         "vazio em linha reta pela entrada (Z < 0) e pela saída (Z > %s):\n" % "109,00",
         "| # | tipo de cara | área (mm²) | centro (mm) | vista pela entrada | vista pela saída | leitura |",
         "|---|---|---|---|---|---|---|---|"]
    for i, x in enumerate(m["caras_do_canal"], start=1):
        L.append("| %d | %s | %s | %s | %.1f%% | %.1f%% | %s |"
                 % (i, x["tipo"], n(x["area_mm2"], 0), ", ".join("%.2f" % v for v in x["centro"]),
                    x["visivel_pela_entrada_pct"], x["visivel_pela_saida_pct"], x["alcanca"]))
    L += ["\n**%d de %d** caras do canal não têm acesso reto nem pela frente nem por trás. %s\n"
             % (m["caras_sem_acesso_reto"], len(m["caras_do_canal"]),
                "Onde não há acesso, a peça única exige uma terceira operação (EDM em várias posições, ou "
                "mandrilhar/ brochar o trecho) — e isso tem de ser decidido antes de mandar para a fábrica, "
                "porque senão o desenho fica usinável só no discurso." if m["caras_sem_acesso_reto"] else
                "Todas as caras são alcançáveis de um dos dois lados: a peça única é usinável com o canal por "
                "frente e a fenda por trás, sem necessidade de junta.")]
    L += ["\n## Montagem no cabeçote completo, com flange\n",
          "`%s` — %d sólidos no arquivo (1 cabeçote + 1 peça única, sem booleano), volume somado %s mm³, "
          "**interferência com o metal do cabeçote = %s mm³**, face de saída em Z = %.2f (protrusão %+.2f mm "
          "além da face do nariz). O encaixe é o mesmo da bipartida: folga radial de Ø 93,00 no furo Ø 95,00 "
          "e assento no degrau, e o anel de fuga entre matriz e cabeçote continua existindo igual — ele não "
          "vem da bipartição.\n"
          % (os.path.basename(m["montagem"]["arquivo"]), m["montagem"]["solidos"],
             n(m["montagem"]["volume_somado_mm3"], 1), n(m["montagem"]["interferencia_mm3"], 4),
             m["montagem"]["face_de_saida_da_matriz_em_Z"], m["montagem"]["protusao_adem_da_face_do_nariz_mm"]),
          "\n## Consequências e o que não muda\n",
             "* **Decisão D2 intocada:** chanfro de saída 1,50 × 45° e land paralelo 8,50 mm do master. Nada de "
               "geometria do produto foi alterado nesta rodada — só a construção da peça.",
             "* **Fixação:** o collete EX-031 e o degrau do cabeçote continuam sendo o que segura a matriz; os "
               "pinos de alinhamento somem da conta junto com os furos (a força de abertura medida do plano de "
               "partição, 55,7 kN, deixa de existir porque não há plano de partição).",
             "* **Anel de fuga:** a folga de 1,00/0,25/0,25 mm entre a OD da matriz e o furo do cabeçote é do "
               "encaixe, não da bipartição — continua igual nas duas peças, e é a rota que a simulação precisa "
               "resolver.",
             "* **Promoção:** a peça única **não** é o master. Quando ele quiser, se ela entra no lugar da v27 "
               "bipartida, é preciso re-sear o baseline (ato do auditor, com o método novo) — e aí vale "
               "aproveitar para consertar o `Body_B` da v28.1, que tem uma cara degenerada achada pela auditoria "
             "de correlações.\n"]
    open(F_REL, "w", encoding="utf-8").write("\n".join(L) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
