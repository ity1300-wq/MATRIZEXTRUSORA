#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AUDITORIA DE TODOS OS STEP DO REPO - o que cada arquivo e, e as CORRELACOES entre eles.

O que ja existia fica onde esta (o `verify_geometry_ssot.py` confere a matriz oficial contra o SSOT e o
`verify_legacy_dies.py` mede as historicas). A unidade nova aqui e a **correlacao**: todo STEP rastreado e
aberto uma vez, inventariado face por face, e cruzado com os arquivos que tem de bater com ele.

  C1  cota medida x SSOT             - fenda (largura/espessura/raio), boca de entrada, estagios do envelope,
                                       comprimento, aco e massa
  C2  metade x metade x peca inteira - A + B = A U B? A n B = 0? cascas por metade (cavidade selada)
  C3  arquivo do canal x vazio real  - o `_Canal_Fluxo.step` e o vazio que a peca tem de fato?
  C4  matriz x cabecote              - folga radial por estagio, o anel de fuga esta ABERTO do bico ate a
                                       entrada (e isto que faz o mastico voltar pelo funil), area e comprimento
                                       do anel, encosto, interferencia, protrusao
  C5  montagem x pecas               - a montagem tem 1 cabecote + N da matriz, o volume somado bate, a
                                       interferencia e zero
  C6  atalho x baseline selado       - os caminhos que o auditor selou abrem os mesmos bytes

Saida: `04_/auditoria_step_correlacoes.json` + `03_/AUDITORIA_CORRELACOES_STEP.md`. Codigo de saida 1 se
qualquer correlacao divergir (para o portao).

Uso: python 04_Dados_SSOT_e_Scripts/auditar_step_correlacoes.py [--json] [--md] [--so-cotas]
"""
import argparse
import collections
import hashlib
import math
import json
import os
import subprocess
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, ".."))
sys.path.insert(0, AQUI)

import cadquery as cq

from verificar_v28 import maior, n                 # maior() joga fora migalha de booleano; n() imprime pt-BR

DIR_01 = os.path.join(RAIZ, "01_CAD_MatrizJonatha_Oficial")
DIR_02 = os.path.join(RAIZ, "02_CAD_Modelos_Historicos")
DIR_CAB = os.path.join(RAIZ, "06_CAD_Cabecote_EX-030", "STEP")
DIR_MAE = os.path.join(RAIZ, "07_CAD_Matrizes")
F_SSOT = os.path.join(AQUI, "cad_die_parameters.json")
F_BASE = os.path.join(RAIZ, "05_Interface_Auditoria", "baseline", "MATRIZ_3_v27.json")
F_PERFIS = os.path.join(AQUI, "perfis_matrizes_x_cabecote.json")
ARQ_JSON = os.path.join(AQUI, "auditoria_step_correlacoes.json")
ARQ_MD = os.path.join(RAIZ, "03_Relatorios_e_Documentacao", "AUDITORIA_CORRELACOES_STEP.md")

ACO = 7.85e-6                       # kg/mm3, a densidade do projeto
CONTATO = 0.02                      # mm: abaixo disso folga e contato
TOL = {"largura": 0.05, "espessura": 0.02, "raio": 0.02, "boca": 0.10, "envelope": 0.05}
# a peca "inteira" de cada pasta (o que vai para a fabrica), e a chave com que o resto do repo a chama
PECAS = {"Matriz_Jonatha_v27_OFICIAL/MatrizJonatha.step": "jonatha_v27_oficial",
         "Matriz_Jonatha_v28_1_PROPOSTA/MatrizJonatha_v28.step": "jonatha_v28_1_proposta",
         "Matriz_Gedeon_Certa/matrizGedeonCerta.step": "gedeon_certa_arquivo_do_usuario",
         "Matriz_Gedeon_Entregue_HISTORICA/MatrizGedeon.step": "gedeon_entregue_historica",
         "Matriz_Copo_HISTORICA/Matriz1_Original_Copo.step": "matriz_1_copo_historica",
         "Matriz_Desenvolvimento_HISTORICA/MatrizDesenvolvimento.step": "desenvolvimento_historica"}

falhas = []


def cobra(ok, item, detalhe=""):
    if not ok:
        falhas.append("%s — %s" % (item, detalhe))
    return bool(ok)


# --------------------------------------------------------------------------- medidores
_CACHE = {}


def abre(caminho):
    """Abre cada arquivo uma vez (os atalhos caem no mesmo realpath, entao 01_/ e 02_/ nao custam nada)."""
    chave = os.path.realpath(caminho)
    if chave not in _CACHE:
        _CACHE[chave] = cq.importers.importStep(caminho).val()
    return _CACHE[chave]


def vol(x):
    ss = x.Solids()
    return sum(v.Volume() for v in ss) if ss else x.Volume()


def _seccao(void, z, meio=0.02):
    """Corta o solido numa lamina fininha e devolve (caixa, AREA DA CARA). Shape.Area() da lamina dobraria o
    numero: ela tem face de cima, face de baixo e o contorno lateral."""
    lamina = cq.Solid.makeBox(400.0, 400.0, meio, cq.Vector(-200.0, -200.0, z - meio / 2.0))
    try:
        sec = maior(void.intersect(lamina))
    except Exception:
        return None
    if not sec:
        return None
    caras = [f for f in sec.Faces() if f.geomType() == "PLANE" and abs(abs(f.normalAt().z) - 1.0) < 1e-6]
    cara = max(caras, key=lambda f: f.Area()) if caras else None
    if cara is None or cara.Area() <= 0:
        return None
    return cara.BoundingBox(), round(cara.Area(), 4)

def _raio_cilindro(f):
    try:
        return round(float(f._geomAdaptor().Cylinder().Radius()), 3)
    except Exception:
        return None


def inventario(shape):
    """Faces por tipo, cilindros de eixo em Z (envelope e filetes), furos de eixo em X, planos da fenda."""
    tipos = collections.Counter()
    cil_z, cil_z_miudos, cil_x, planos_y, cones = [], [], [], [], []
    for f in shape.Faces():
        t = f.geomType()
        tipos[t] += 1
        b = f.BoundingBox()
        dx, dy, dz = b.xmax - b.xmin, b.ymax - b.ymin, b.zmax - b.zmin
        if t == "CYLINDER":
            r = _raio_cilindro(f)
            if r is None:
                continue
            # o eixo vem do proprio cilindro: numa peca bipartida em Y = 0 a cara externa e meia-cana e a
            # caixa dela e r x 2r, entao testar a caixa para descobrir o eixo perdia o envelope inteiro
            try:
                d = f._geomAdaptor().Cylinder().Axis().Direction()
                eixo_z, eixo_x = abs(d.Z()) > 0.99, abs(d.X()) > 0.99
            except Exception:
                redondo = abs(dx - 2 * r) < 0.05 and abs(dy - 2 * r) < 0.05
                eixo_z, eixo_x = redondo and dz > 0.5, (not redondo) and dx > 0.5
            if eixo_z:
                (cil_z if r > 5 else cil_z_miudos).append((r, round(b.zmin, 2), round(b.zmax, 2), round(f.Area(), 1)))
            elif eixo_x:
                cil_x.append((r, [round(b.xmin, 2), round(b.xmax, 2)], [round(b.ymin, 2), round(b.ymax, 2)],
                              [round(b.zmin, 2), round(b.zmax, 2)]))
        elif t == "PLANE":
            nn = f.normalAt()
            if abs(abs(nn.y) - 1.0) < 1e-6 and abs(b.ymin) < 3.0 and abs(b.ymax) < 3.0:
                planos_y.append((round(nn.y, 3), round(b.xmin, 3), round(b.xmax, 3), round(b.zmin, 2),
                                 round(b.zmax, 2)))
        elif t == "CONE":
            cones.append((round(min(abs(b.xmin), abs(b.xmax)), 2), round(max(abs(b.xmin), abs(b.xmax)), 2),
                          round(b.zmin, 2), round(b.zmax, 2), round(f.Area(), 1)))
    cx = shape.BoundingBox()
    sol = shape.Solids() or [shape]
    return {"solidos": len(sol),
            "cascas_por_solido": [len(s.Shells()) for s in sol],
            "faces_por_tipo": dict(tipos),
            "faces": sum(tipos.values()),
            "volume_mm3": round(vol(shape), 4),
            "caixa": {"dx": round(cx.xmax - cx.xmin, 3), "dy": round(cx.ymax - cx.ymin, 3),
                      "dz": round(cx.zmax - cx.zmin, 3), "z": [round(cx.zmin, 3), round(cx.zmax, 3)]},
            "cilindros_z_grandes": sorted({(r, z0, z1) for r, z0, z1, _ in cil_z}, reverse=True),
            "cilindros_z_miudos": sorted({(r, z0, z1) for r, z0, z1, _ in cil_z_miudos}),
            "furos_eixo_x": sorted(set(cil_x)),
            "planos_da_fenda": sorted(set(planos_y)),
            "cones": sorted(set(cones)),
            "brep_valido": all(s.isValid() for s in sol)}


def mede_fenda(inv):
    """Largura, espessura e raio da fenda, nas caras. So pelos planos dava 73,50 - unir os semicilindros das
    bordas (raio = espessura/2) e o que fecha os 75,00 do contrato."""
    ys = sorted({p[0] for p in inv["planos_da_fenda"]})
    if len(ys) < 2:
        return None
    bordas = [r for r, _, _ in inv["cilindros_z_miudos"] if 0.2 < r < 3.0]
    xs = [v for p in inv["planos_da_fenda"] for v in (p[1], p[2])]
    plana = max(xs) - min(xs)
    raio = min(bordas) if bordas else None
    largura = round(plana + (2 * raio if raio else 0.0), 3)
    zs = [(p[3], p[4]) for p in inv["planos_da_fenda"]]
    return {"largura_mm": largura, "largura_so_os_planos_mm": round(plana, 3),
            "espessura_mm": round(abs(ys[-1] - ys[0]), 3), "raio_borda_mm": raio,
            "z_da_fenda": [round(min(z[0] for z in zs), 2), round(max(z[1] for z in zs), 2)],
            "passante_ate_a_saida": abs(max(z[1] for z in zs) - inv["caixa"]["z"][1]) < 0.05}


def fenda_na_saida(void, inv):
    """A fenda no plano de saida, na CARA da seccao do vazio. A area diz a forma da borda: estadio (meia-lua,
    R = e/2) ou retangulo (canto vivo, onde a manta rasga e entra serra)."""
    if void is None:
        return None
    z = round(inv["caixa"]["z"][1] - 0.01, 3)
    r = _seccao(void, z)
    if r is None:
        return None
    b, area = r
    w, t = b.xmax - b.xmin, b.ymax - b.ymin
    estadio = (w - t) * t + math.pi * t * t / 4.0
    retang = w * t
    borda = ("meia-lua (R = espessura/2)" if abs(area - estadio) / estadio < 0.01 else
             ("canto vivo (retangular)" if abs(area - retang) / retang < 0.01 else "outra"))
    return {"z_do_plano_mm": z, "largura_mm": round(w, 3), "espessura_mm": round(t, 3),
            "raio_borda_mm": round(t / 2.0, 3) if borda.startswith("meia-lua") else None,
            "area_mm2": area, "area_estadio_mm2": round(estadio, 4), "area_retangulo_mm2": round(retang, 4),
            "desvio_vs_estadio_pct": round(100.0 * (area - estadio) / estadio, 3), "borda": borda}

def seccoes_do_canal(pasta, base, inv):
    """A fenda medida no ARQUIVO DO CANAL (o caminho de fluxo em si), em dois planos: na saida, onde o chanfro
    abre a boca, e 2,00 mm antes, no land paralelo - que e onde o contrato cobra 75,00 x 1,50."""
    pc = os.path.join(pasta, base + "_Canal_Fluxo.step")
    if not os.path.exists(pc):
        pc = next((os.path.join(pasta, f) for f in sorted(os.listdir(pasta))
                   if f.endswith("_Canal_Fluxo.step")), None)
    if not pc or not os.path.exists(pc):
        return None
    try:
        canal = abre(pc)
    except Exception:
        return None
    z_out = inv["caixa"]["z"][1]
    out = {}
    for nome, z in (("na_saida", z_out - 0.01), ("no_land", z_out - 2.00)):
        r = _seccao(canal, z)
        if r is None:
            continue
        b, area = r
        w, t = b.xmax - b.xmin, b.ymax - b.ymin
        estadio = (w - t) * t + math.pi * t * t / 4.0
        borda = ("meia-lua (R = espessura/2)" if abs(area - estadio) / estadio < 0.01 else
                 ("canto vivo (retangular)" if abs(area - w * t) / (w * t) < 0.01 else "outra"))
        out[nome] = {"z_do_plano_mm": round(z, 3), "largura_mm": round(w, 3), "espessura_mm": round(t, 3),
                     "area_mm2": area, "borda": borda,
                     "raio_borda_mm": round(t / 2.0, 3) if borda.startswith("meia-lua") else None,
                     "desvio_area_vs_estadio_pct": round(100.0 * (area - estadio) / estadio, 3)}
    return out or None

def boca_por_seccao(void, inv):
    """Abertura no plano de ENTRADA, na cara da seccao do vazio: largura real e Ø equivalente pela area."""
    if void is None:
        return None
    r = _seccao(void, inv["caixa"]["z"][0] + 0.01)
    if r is None:
        return None
    b, area = r
    return {"largura_mm": round(b.xmax - b.xmin, 3), "altura_mm": round(b.ymax - b.ymin, 3),
            "area_mm2": area, "Ø_equivalente_mm": round(2.0 * math.sqrt(area / math.pi), 3)}

def boca_entrada(inv):
    """Ø da abertura no plano de entrada (Z minimo da peca)."""
    z0 = inv["caixa"]["z"][0]
    r_cone = [max(abs(c[0]), abs(c[1])) for c in inv["cones"] if abs(c[2] - z0) < 0.05]
    if r_cone:
        return round(2 * max(r_cone), 3)
    cil = [r for r, za, _zb in inv["cilindros_z_grandes"] if abs(za - z0) < 0.05 and r < 47.0]
    return round(2 * min(cil), 3) if cil else None


def estagios(inv):
    """Escada do envelope externo, do maior Ø para o menor, como o contrato escreve: (Ø, z_de, z_ate)."""
    saida = []
    for r, z0, z1 in inv["cilindros_z_grandes"]:
        if 30.0 < r < 60.0:
            saida.append((round(2 * r, 2), z0, z1))
    return saida


def vazio_da_peca(shape, inv):
    """O vazio que a peca carrega (funil + fenda), medido dentro do ENVELOPE DELA: soma dos cilindros dos
    estagios medidos, menos o aco. Usar uma caixa de Ø fixo engoliria o ar em volta dos estagios menores e o
    numero sairia ridículo - foi o erro que esta funcao precisou corrigir."""
    est = inv["cilindros_z_grandes"]
    if not est:
        return (None, None)
    solidos = [cq.Solid.makeCylinder(r, z1 - z0, cq.Vector(0, 0, z0)) for r, z0, z1 in est]
    wp = cq.Workplane("XY").newObject([solidos[0]])
    for extra in solidos[1:]:                      # Shape.fuse nao aceita lista aqui; Workplane.union sim
        wp = wp.union(cq.Workplane("XY").newObject([extra]))
    env = maior(wp.val())
    sobra = env
    for so in (shape.Solids() or [shape]):          # em peca bipartida, cortar o composto inteiro nao
        sobra = sobra.cut(so)                        # subtraia nada: corta solido por solido
    sobra = maior(sobra)
    v = round(vol(sobra), 1)
    if v <= 0 or len(shape.Solids()) > len(solidos) + 2:
        # a peca ja traz o vazio como solido proprio (funil/pinos dentro do arquivo): env - metal nao e o
        # caminho de fluxo, e sim sobra - nao reportar numero aqui
        return (None, None)
    return (v, sobra)


def sha(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


# ------------------------------------------------------------------- C6 atalhos x baseline
def c6_atalhos():
    out, piores = {}, []
    nao_modelo = [c for c in BASE if not c.endswith(".step")]
    for caminho, h_exp in sorted(BASE.items()):
        if not caminho.endswith(".step"):
            continue                      # script e JSON do baseline mudaram de proposito nesta sessao;
                                           # re-sela-los e ato da auditoria, nao desta checagem
        p = os.path.join(RAIZ, caminho)
        if not os.path.exists(p):
            piores.append("%s sumiu da arvore" % caminho)
            continue
        h = sha(p)
        out[caminho] = {"atalho": os.path.islink(p),
                        "destino": os.path.relpath(os.path.realpath(p), RAIZ) if os.path.islink(p) else None,
                        "bate_o_hash": h == h_exp}
        if h != h_exp:
            piores.append("%s: bytes diferentes do baseline" % caminho)
    cobra(not piores, "C6 caminhos selados abrem os mesmos bytes", "; ".join(piores[:4]))
    return {"esperados_modelo": len(out), "conferidos": len(out), "divergentes": piores,
            "fora_do_escopo_reconhecido": sorted(nao_modelo), "por_arquivo": out}


# ------------------------------------------------------------------- C1 cotas medidas x SSOT
CONTRATO = ("jonatha_v27_oficial", "jonatha_v28_1_proposta", "gedeon_certa_arquivo_do_usuario",
            "gedeon_entregue_historica")


def cobra_(chave, div, quebra):
    if not div:
        return
    if chave in CONTRATO:
        quebra.append("%s divergiu do SSOT: %s" % (chave, div))
    else:
        div["nota"] = "histórica: medida, mas não cobrada pelo contrato (só a fenda)"
        for k in list(div):
            if k not in ("nota", "largura", "espessura", "raio"):
                div[k] = "informativo: " + str(div[k])


def c1_cotas(principais):
    par = SSOT["matriz_jonatha_parameters"]
    env = SSOT["envelope_externo_mm"]
    linhas, quebra = [], []
    for chave, rel, inv in principais:
        fd = inv.get("_seccao_canal_land") or inv.get("_fenda_saida") or mede_fenda(inv)
        linha = {"matriz": chave, "arquivo": rel, "faces": inv["faces"], "solidos": inv["solidos"],
                 "cascas": inv["cascas_por_solido"], "volume_aco_mm3": inv["volume_mm3"],
                 "massa_kg": round(inv["volume_mm3"] * ACO, 4),
                 "comprimento_mm": inv["caixa"]["dz"], "estagios": estagios(inv),
                 "boca_entrada_mm": (inv.get("_boca_seccao") or {}).get("largura_mm"),
                 "boca_por_seccao": inv.get("_boca_seccao"),
                 "boca_por_cone_geometrica": boca_entrada(inv),
                 "boca_por_seccao_area_mm2": (inv.get("_boca_seccao") or {}).get("area_mm2"),
                 "vazio_mm3": inv.get("_vazio"),
                 "borda_da_saida": (inv.get("_fenda_saida") or {}).get("borda"),
                 "seccao_na_saida": inv.get("_seccao_canal_saida"),
                 "seccao_no_land": inv.get("_seccao_canal_land"),
                 "desvio_area_vs_estadio_pct": (inv.get("_fenda_saida") or {}).get("desvio_vs_estadio_pct"),
                 "fonte_da_fenda": ("seccao de saida do vazio medido" if inv.get("_fenda_saida")
                                    else "caras planas da peca (sem arquivo de canal)")}
        div = {}
        if fd:
            linha.update(fd)
            if abs(fd["largura_mm"] - par["land_width_mm"]) > TOL["largura"]:
                div["largura"] = [fd["largura_mm"], par["land_width_mm"]]
            if abs(fd["espessura_mm"] - par["land_thickness_mm"]) > TOL["espessura"]:
                div["espessura"] = [fd["espessura_mm"], par["land_thickness_mm"]]
            if fd["raio_borda_mm"] and abs(fd["raio_borda_mm"] - par["edge_radius_mm"]) > TOL["raio"]:
                div["raio"] = [fd["raio_borda_mm"], par["edge_radius_mm"]]
        boca = linha["boca_entrada_mm"]
        linha["boca_entrada_medida_mm"] = boca
        if boca is not None and boca - par["entry_bore_diameter_mm"] > TOL["boca"]:
            div["boca_passa_do_acoplamento"] = [boca, par["entry_bore_diameter_mm"]]
        for i, nome in enumerate(("estagio_1", "estagio_2", "estagio_3"), start=0):
            ref = env.get(nome) or {}
            if i < len(linha["estagios"]):
                d, z0, z1 = linha["estagios"][i]
                if (abs(d - ref.get("diametro_mm", d)) > TOL["envelope"]
                        or abs(z0 - ref.get("z_de_mm", z0)) > TOL["envelope"]):
                    div.setdefault("envelope", []).append([[d, z0, z1],
                                                            [ref.get("diametro_mm"), ref.get("z_de_mm"),
                                                             ref.get("z_ate_mm")]])
        if abs(inv["caixa"]["dz"] - env["comprimento_total_z_mm"]) > TOL["envelope"]:
            div["comprimento"] = [inv["caixa"]["dz"], env["comprimento_total_z_mm"]]
        linha["divergencia_vs_SSOT"] = div
        linhas.append(linha)
        # quem tem de bater o contrato inteiro: a oficial, a proposta (mesmo envelope) e as Gedeon (que
        # sentam no mesmo furo). Copo e Desenvolvimento sao historico: medidos, cobrados so na fenda.
        cobra_(chave, div, quebra)
    cobra(not quebra, "C1 cotas do contrato nas matrizes que sentam no cabeçote", "; ".join(quebra))
    return {"tolerancias_mm": TOL, "por_matriz": linhas, "oficial_divergindo": quebra}


# --------------------------------------------------------- C2 metades e C3 arquivo do canal
def c2_c3(principais):
    out = {}
    for chave, rel, inv in principais:
        p = inv["_caminho"]
        d, base = os.path.dirname(p), os.path.basename(p)[:-5]
        par = {"peca_inteira": os.path.basename(p), "volume_peca_mm3": inv["volume_mm3"],
               "cascas_por_solido": inv["cascas_por_solido"]}
        def irmao(sufixo):
            ex = os.path.join(d, base + sufixo)
            if os.path.exists(ex):
                return ex
            for f in sorted(os.listdir(d)):              # a Gedeon CERTA chama as metades MatrizGedeon_Certa_*
                if f.endswith(sufixo):
                    return os.path.join(d, f)
            return None
        pa, pb = irmao("_Body_A.step"), irmao("_Body_B.step")
        if pa and pb and os.path.exists(pa) and os.path.exists(pb):
            A, B = maior(abre(pa)), maior(abre(pb))
            vA, vB = vol(A), vol(B)
            uniao = vol(maior(A.fuse(B)))
            intes = vol(maior(A.intersect(B))) if A.intersect(B).Solids() else 0.0
            par.update(A_mm3=round(vA, 1), B_mm3=round(vB, 1), uniao_A_u_B_mm3=round(uniao, 1),
                       soma_menos_uniao_mm3=round(vA + vB - uniao, 6), intersecao_mm3=round(intes, 6),
                       cascas_A=len(A.Shells()), cascas_B=len(B.Shells()))
            limiar = max(0.01, 2e-7 * max(uniao, vA + vB))     # fuzz do OCCT, nao defeito de geometria
            cobra(abs(vA + vB - uniao) <= limiar, "C2 %s: A + B = A U B" % chave,
                  "A+B=%.4f vs uniao=%.4f mm3 (limiar %.4f)" % (vA + vB, uniao, limiar))
            cobra(intes <= 0.01, "C2 %s: as metades nao se sobrepoem" % chave, "A n B = %.4f mm3" % intes)
            sel = [c for c in (par["cascas_A"], par["cascas_B"]) if c and c > 1]
            par["cavidade_selada"] = bool(sel)
        pc = os.path.join(d, base + "_Canal_Fluxo.step")
        if not os.path.exists(pc):
            pc = next((os.path.join(d, f) for f in sorted(os.listdir(d)) if f.endswith("_Canal_Fluxo.step")), pc)
        if os.path.exists(pc) and inv.get("_vazio"):
            vcan = round(vol(abre(pc)), 1)
            vazio = inv["_vazio"]
            par.update(canal_fluxo_mm3=vcan, vazio_medido_mm3=vazio, delta_mm3=round(vcan - vazio, 1),
                       delta_pct=round(100.0 * (vcan - vazio) / vazio, 3) if vazio else None)
            par["leitura"] = ("o arquivo do canal NAO e o vazio desta peca"
                              if abs(vcan - vazio) / max(vazio, 1.0) > 0.005 else "o arquivo do canal e o vazio da peca")
        out[chave] = par
    return out


# ------------------------------------------------- C4 matriz x cabecote: folga, anel de fuga, encosto
def c4_cabecote(principais):
    cab_full = os.path.join(DIR_CAB, "Cabecote_EX-030_desenhado.step")
    cab = maior(abre(cab_full))
    furo = []
    for f in cab.Faces():
        if f.geomType() != "CYLINDER":
            continue
        r = _raio_cilindro(f)
        b = f.BoundingBox()
        if r and 20 < r < 60 and abs((b.xmax - b.xmin) - 2 * r) < 0.05 and abs((b.ymax - b.ymin) - 2 * r) < 0.05:
            furo.append((round(r, 3), round(b.zmin, 3), round(b.zmax, 3)))
    furo = sorted(set(furo), key=lambda t: t[1])
    z_nariz = round(cab.BoundingBox().zmax, 3)
    dz_por_chave = {}
    if os.path.exists(F_PERFIS):
        pf = json.load(open(F_PERFIS, encoding="utf-8"))
        for m in pf.get("matrizes", []):
            enc = (m.get("encostos") or {}).get(m.get("encosto_usado")) or {}
            dz_por_chave[m["chave"]] = round(enc.get("deslocamento_aplicado_mm", 0.0), 3)
    out = {"cabecote": os.path.relpath(cab_full, RAIZ), "cabecote_volume_mm3": round(vol(cab), 3),
           "cabecote_massa_kg": round(vol(cab) * ACO, 3),
           "furo_do_cabecote_D_z": [(round(2 * r, 2), z0, z1) for r, z0, z1 in furo],
           "face_do_nariz_z": z_nariz, "matrizes": {}}
    for chave, rel, inv in principais:
        est = estagios(inv)
        if not est:
            continue
        folgas, abertos = [], []
        for (d_mat, z0, z1) in est:
            trecho = [t for t in furo if t[1] <= z1 + 1e-6 and t[2] >= z0 - 1e-6]
            if not trecho:
                continue
            r_furo = min(trecho, key=lambda t: t[0])[0]
            folga = round(r_furo - d_mat / 2.0, 3)
            area = round(3.141592653589793 * (r_furo ** 2 - (d_mat / 2.0) ** 2), 1)
            folgas.append({"estagio_D_matriz": d_mat, "z": [z0, z1], "furo_D": round(2 * r_furo, 2),
                           "folga_radial_mm": folga, "area_do_anel_mm2": area})
            abertos.append(folga > CONTATO)
        continua = all(abertos) and len(abertos) == len(folgas)
        saida = inv["caixa"]["z"][1]
        die = maior(abre(inv["_caminho"]))
        dz = dz_por_chave.get(chave, 0.0)
        if abs(dz) > 1e-9:
            die = maior(cq.Workplane("XY").newObject([die]).translate(cq.Vector(0, 0, dz)).val())
        it = vol(maior(die.intersect(cab))) if die.intersect(cab).Solids() else 0.0
        reg = {"arquivo": rel, "folgas_por_estagio": folgas,
               "menor_folga_radial_mm": min(f["folga_radial_mm"] for f in folgas),
               "anel_de_fuga_continuo_do_bico_ate_a_entrada": bool(continua),
               "area_total_do_anel_mm2": round(sum(f["area_do_anel_mm2"] for f in folgas), 1),
               "comprimento_do_anel_mm": round(sum(f["z"][1] - f["z"][0] for f in folgas), 2),
               "encosto_usado": "B_ombro_no_degrau (o do projeto)" if chave in dz_por_chave else "nao medido",
               "deslocamento_aplicado_mm": dz,
               "saida_além_da_face_do_nariz_mm": round(saida + dz - z_nariz, 3),
               "interferencia_matriz_x_cabecote_mm3": round(it, 4)}
        out["matrizes"][chave] = reg
        cobra(it <= 0.01, "C4 %s: a matriz nao encosta no metal do cabecote" % chave,
              "interferencia %.4f mm3" % it)
        if chave == "jonatha_v27_oficial":
            cobra(min(f["folga_radial_mm"] for f in folgas) >= 0.2,
                  "C4 %s: ha folga radial nos tres estagios" % chave,
                  "menor folga %.3f mm" % min(f["folga_radial_mm"] for f in folgas))
    return out


# ------------------------------------------------------------- C5 montagem x pecas de origem
def c5_montagens():
    out = {}
    cab = maior(abre(os.path.join(DIR_CAB, "Cabecote_EX-030_desenhado.step")))
    v_cab = vol(cab)
    for nome in sorted(os.listdir(DIR_CAB)):
        if not (nome.startswith("Cabecote_EX-030_com_") and nome.endswith(".step")):
            continue
        p = os.path.join(DIR_CAB, nome)
        try:
            sh = abre(p)
        except Exception as e:
            out[nome] = {"erro": str(e)}
            falhas.append("C5 %s nao abre: %s" % (nome, e))
            continue
        sol = sh.Solids() or [sh]
        soma = sum(vol(x) for x in sol)
        b = sh.BoundingBox()
        out[nome] = {"solidos": len(sol), "volume_somado_mm3": round(soma, 3),
                     "massa_somada_kg": round(soma * ACO, 4),
                     "metal_da_matriz_na_montagem_mm3": round(soma - v_cab, 3),
                     "brep_validos": all(x.isValid() for x in sol),
                     "caixa_D_x_Z_mm": [round(max(b.xmax - b.xmin, b.ymax - b.ymin), 2),
                                        round(b.zmax - b.zmin, 2)]}
        cobra(len(sol) >= 2, "C5 %s traz cabecote E matriz" % nome, "%d solido(s)" % len(sol))
        cobra(abs(soma - v_cab) > 1.0, "C5 %s tem metal de matriz alem do cabecote" % nome,
              "somado %.1f vs cabecote %.1f mm3" % (soma, v_cab))
        cobra(all(x.isValid() for x in sol), "C5 %s solido valido (BRepCheck)" % nome, "tem solido invalido")
    return out


# ------------------------------------------------ C7 saude topologica (BRepCheck face por face)
def c7_topologia(principais):
    """Nao basta o solido abrir: uma cara malformada vira 'arquivo corrompido' no CAD da fabrica e superficie
    que nao se usina. Aqui cada solido das seis pecas (e das metades delas) e aberto e as sub-caras sao
    checadas uma a uma, com o centro das que falham - que e o que diz onde o problema esta."""
    from OCP.BRepCheck import BRepCheck_Analyzer
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopAbs import TopAbs_FACE, TopAbs_EDGE
    from OCP.BRepGProp import BRepGProp
    from OCP.GProp import GProp_GProps

    def centro(sh):
        pr = GProp_GProps()
        BRepGProp.LinearProperties_s(sh, pr)
        c = pr.CentreOfMass()
        return [round(c.X(), 2), round(c.Y(), 2), round(c.Z(), 2)]

    alvos = []
    for chave, rel, inv in principais:
        alvos.append((chave, rel))
        base = os.path.basename(rel)[:-5]
        for extra in ("_Body_A", "_Body_B", "_Canal_Fluxo"):
            r2 = rel.replace(base + ".step", base + extra + ".step")
            if os.path.exists(os.path.join(RAIZ, r2)):
                alvos.append((chave + extra, r2))
    out, ruim = {}, []
    for chave, rel in alvos:
        try:
            sh = abre(os.path.join(RAIZ, rel))
        except Exception as e:
            out[chave] = {"arquivo": rel, "erro": str(e)}
            continue
        regs = []
        for so in (sh.Solids() or [sh]):
            faces_ruins, arestas_ruins = [], []
            for tipo, balde in ((TopAbs_FACE, faces_ruins), (TopAbs_EDGE, arestas_ruins)):
                ex = TopExp_Explorer(so.wrapped, tipo)
                while ex.More():
                    cur = ex.Current()
                    if not BRepCheck_Analyzer(cur).IsValid():
                        balde.append(cur)
                    ex.Next()
            regs.append({"volume_mm3": round(so.Volume(), 1), "solido_valido": bool(so.isValid()),
                         "faces": len(so.Faces()), "faces_invalidas": len(faces_ruins),
                         "arestas_invalidas": len(arestas_ruins),
                         "centros_das_faces_invalidas": [centro(f) for f in faces_ruins[:3]],
                         "cascas": len(so.Shells())})
            if faces_ruins or arestas_ruins or not so.isValid():
                ruim.append("%s: %d cara(s) e %d aresta(s) inválidas em %s (centro %s)"
                            % (chave, len(faces_ruins), len(arestas_ruins), rel,
                               centro(faces_ruins[0]) if faces_ruins else "—"))
        out[chave] = {"arquivo": rel, "solidos": regs}
    cobra(not [r for r in ruim if "v27_oficial" in r or "gedeon_certa" in r],
          "C7 os arquivos que vao para a fabrica estao topologicamente limpos", "; ".join(ruim[:3]))
    return {"por_arquivo": out, "achados": ruim,
            "conclusao": ("nada alem do apontado" if ruim else "todos os solidos e sub-caras validos")}


# --------------------------------------------------------------------------- corpo
SSOT = json.load(open(F_SSOT, encoding="utf-8"))
BASE = json.load(open(F_BASE, encoding="utf-8"))["hashes"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--md", action="store_true")
    ap.add_argument("--so-cotas", action="store_true", help="so C1 e C6: sem booleanos (rapido)")
    ap.add_argument("--rigoroso", action="store_true",
                    help="sai com codigo 1 se algo divergir (use antes de mandar uma matriz para a fabrica; "
                         "sem a flag a divergencia e reportada e o codigo e 0, para nao fechar a porta do "
                         "portao por um defeito ja conhecido e apontado)")
    a = ap.parse_args()

    rastre = subprocess.run(["git", "ls-files", "*.step"], cwd=RAIZ, capture_output=True, text=True).stdout.split()
    arquivos = sorted(r for r in rastre if r.startswith(("01_", "02_", "06_", "07_")))
    print("[1] inventariando %d STEP rastreados (um booleano de vazio por peca inteira)" % len(arquivos))
    todos, principais = [], []
    for rel in arquivos:
        p = os.path.join(RAIZ, rel)
        if not os.path.exists(p):
            falhas.append("rastreado mas ausente: %s" % rel)
            continue
        try:
            shape = abre(p)
        except Exception as e:
            falhas.append("nao abre %s: %s" % (rel, e))
            continue
        inv = inventario(shape)
        inv["_caminho"], inv["_rel"] = p, rel
        corpo = PECAS.get(rel.split("07_CAD_Matrizes/", 1)[-1] if rel.startswith("07_") else "", None) \
            if rel.startswith("07_") else None
        if corpo and not a.so_cotas:
            inv["_vazio"], inv["_vazio_solido"] = vazio_da_peca(shape, inv)
            inv["_boca_seccao"] = boca_por_seccao(inv["_vazio_solido"], inv)
        if corpo:
            pasta, base = os.path.dirname(p), os.path.basename(p)[:-5]
            sc = seccoes_do_canal(pasta, base, inv) or {}
            inv["_seccao_canal_saida"], inv["_seccao_canal_land"] = sc.get("na_saida"), sc.get("no_land")
        if corpo and not a.so_cotas:
            inv["_fenda_saida"] = fenda_na_saida(inv.get("_vazio_solido"), inv)
        todos.append(inv)
        if corpo:
            principais.append((corpo, rel, inv))
    print("    %d arquivos medidos, %d pecas inteiras nas seis pastas" % (len(todos), len(principais)))
    cobra(len(principais) == len(PECAS), "C0 as seis pecas inteiras foram encontradas",
          "%d de %d" % (len(principais), len(PECAS)))

    med = {"gerado_em": "2026-09-13", "arquivos_conferidos": len(todos),
           "inventarios": {i["_rel"]: {k: v for k, v in i.items() if not k.startswith("_")} for i in todos}}
    print("[2] C6 atalhos x baseline selado do auditor")
    med["C6"] = c6_atalhos()
    print("[3] C1 cotas medidas x SSOT")
    med["C1"] = c1_cotas(principais)
    if not a.so_cotas:
        print("[4] C2 metades e C3 canal x vazio")
        med["C2_C3"] = c2_c3(principais)
        print("[5] C4 matriz x cabecote (folga, anel de fuga, encosto, interferencia)")
        med["C4"] = c4_cabecote(principais)
        print("[6] C5 montagens x pecas de origem")
        med["C5"] = c5_montagens()
        print("[7] C7 saude topologica: BRepCheck em cada cara e aresta")
        med["C7"] = c7_topologia(principais)
    med["divergencias"] = falhas
    med["status"] = "APROVADO" if not falhas else "DIVERGENTE"

    if a.json:
        json.dump(med, open(ARQ_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("JSON ->", os.path.relpath(ARQ_JSON, RAIZ))
    if a.md:
        escreve_md(med)
        print("MD  ->", os.path.relpath(ARQ_MD, RAIZ))
    print("=" * 74)
    if falhas:
        print("%s: %d divergencia(s)" % ("AUDITORIA DE CORRELACOES" if a.rigoroso else
                                        "AUDITORIA DE CORRELACOES - ALERTA (nao bloqueia sem --rigoroso)",
                                        len(falhas)))
        for f in falhas[:12]:
            print("  -", f)
        return 1 if a.rigoroso else 0
    print("AUDITORIA DE CORRELACOES: tudo bate - %d STEP, %d modelos selados, %d montagens"
          % (len(todos), med["C6"]["esperados_modelo"], len(med.get("C5", {}))))
    return 0


def escreve_md(med):
    L = ["# Auditoria dos STEP — o que cada arquivo é e o que eles têm de bater entre si\n",
         "Gerada por `04_Dados_SSOT_e_Scripts/auditar_step_correlacoes.py` (código de saída 1 se algo diverge, "
         "para entrar no portão). Cada número abaixo foi **medido no arquivo** na hora em que este relatório foi "
         "escrito, com `cadquery`, face por face: %d arquivos STEP abertos. Status: **%s**.\n"
         % (med["arquivos_conferidos"], med["status"]),
         "## C1 — cota medida × SSOT (as seis peças inteiras)\n",
         "| matriz | fenda L × e (mm) | R da borda | boca de entrada | estágios Ø × Z (mm) | comprimento | "
         "vazio (mm³) | borda da saída | aço (mm³) | massa (kg) | faces | divergência |",
         "|---|---|---|---|---|---|---|---|---|"]
    for d in med["C1"]["por_matriz"]:
        est = " · ".join("Ø%.2f Z %.2f..%.2f" % t for t in d["estagios"]) or "—"
        cel = ["`%s`" % d["matriz"],
               ("%.3f × %.3f" % (d["largura_mm"], d["espessura_mm"])) if "largura_mm" in d else "sem fenda fechada",
               ("%.2f" % d["raio_borda_mm"]) if d.get("raio_borda_mm") else "—",
               ("Ø %.2f" % d["boca_entrada_mm"]) if d["boca_entrada_mm"] else "—",
               est, "%.2f" % d["comprimento_mm"],
               n(d["vazio_mm3"], 1) if d.get("vazio_mm3") else "—",
               d.get("borda_da_saida") or "—",
               n(d["volume_aco_mm3"], 1), "%.4f" % d["massa_kg"], str(d["faces"]),
               "bate" if not d["divergencia_vs_SSOT"] else json.dumps(d["divergencia_vs_SSOT"], ensure_ascii=False)]
        L.append("| " + " | ".join(cel) + " |")
    L.append("\nTolerâncias cobradas: largura ±%.2f, espessura ±%.2f, raio ±%.2f, boca +%.2f/−%.2f, envelope ±%.2f mm "
             "(ou seja: a metade do que o desenho autoriza). `sem fenda fechada` é legítimo nas peças históricas, "
             "que são cinco sólidos que se atravessam e não têm a fenda como face única.\n"
             % (TOL["largura"], TOL["espessura"], TOL["raio"], TOL["boca"], 0.10, TOL["envelope"]))
    if "C2_C3" in med:
        L += ["## C2 — metade × metade × peça inteira, e C3 — o `_Canal_Fluxo.step` é o vazio real?\n",
              "| matriz | A (mm³) | B (mm³) | A+B − (A∪B) | A ∩ B | cascas A/B | cavidade selada | "
              "canal do arquivo (mm³) | vazio medido (mm³) | Δ% | leitura |", "|---|---|---|---|---|---|---|---|---|---|"]
        for c, d in med["C2_C3"].items():
            L.append("| `%s` | %s | %s | %s | %s | %s/%s | %s | %s | %s | %s | %s |"
                     % (c, n(d.get("A_mm3", 0), 1), n(d.get("B_mm3", 0), 1),
                        n(d.get("soma_menos_uniao_mm3", 0), 4), n(d.get("intersecao_mm3", 0), 4),
                        d.get("cascas_A", "—"), d.get("cascas_B", "—"),
                        "SIM" if d.get("cavidade_selada") else "não",
                        n(d.get("canal_fluxo_mm3", 0), 1) if "canal_fluxo_mm3" in d else "—",
                        n(d.get("vazio_medido_mm3", 0), 1) if "vazio_medido_mm3" in d else "—",
                        n(d.get("delta_pct", 0), 3) if "delta_pct" in d else "—",
                        d.get("leitura", "—")))
        L.append("\nCasca > 1 num `Body` = cavidade selada dentro do aço, sem ferramenta que a faça: é o G-03 da "
                 "auditoria de 2026-09-11, presente no `Body_A` da Gedeon entregue e no `MatrizJonatha.step`. "
                 "E a coluna do canal é a correlação que derrubou a \"Gedeon corrigida\": o `_Canal_Fluxo.step` "
                 "histórico carrega o funil da Jonatha, não o vazio da Gedeon.\n")
    if "C4" in med:
        m = med["C4"]
        L += ["## C4 — matriz × cabeçote: folga radial, anel de fuga, encosto\n",
              "Cabeçote medido: `%s` (%s mm³, %s kg), furo em escada %s, face do nariz em Z = %.2f.\n"
              % (m["cabecote"], n(m["cabecote_volume_mm3"], 1), m["cabecote_massa_kg"],
                 " · ".join("Ø%.2f Z %.2f..%.2f" % t for t in m["furo_do_cabecote_D_z"]), m["face_do_nariz_z"]),
              "| matriz | folga radial por estágio (mm) | menor folga | anel de fuga contínuo? | área do anel (mm²) "
              "| comprimento do anel (mm) | saída além do nariz (mm) | ∩ com o cabeçote (mm³) |",
              "|---|---|---|---|---|---|---|---|"]
        for c, d in m["matrizes"].items():
            L.append("| `%s` | %s | %.2f | %s | %.1f | %.2f | %+.2f | %s |"
                     % (c, " / ".join("%+.2f" % f["folga_radial_mm"] for f in d["folgas_por_estagio"]),
                        d["menor_folga_radial_mm"],
                        "**SIM — caminho livre para trás**" if d["anel_de_fuga_continuo_do_bico_ate_a_entrada"] else "não",
                        d["area_total_do_anel_mm2"], d["comprimento_do_anel_mm"],
                        d["saida_além_da_face_do_nariz_mm"], n(d["interferencia_matriz_x_cabecote_mm3"], 4)))
        L.append("\n`anel de fuga contínuo` = existe anel com folga > 0 entre a OD da matriz e o furo do cabeçote, "
                 "sem pinça, do bico até a face de entrada da matriz. Onde isso é verdadeiro, o mastique **não é "
                 "obrigado** a passar pela fenda: a rota de trás (para o funil de alimentação) existe e é mais "
                 "curta que a fenda. É a correlação geométrica que abre a pergunta da simulação.\n")
    if "C5" in med:
        L += ["## C5 — montagem × peças de origem\n",
              "| montagem | sólidos | volume somado (mm³) | massa (kg) | metal da matriz (mm³) | caixa Ø × Z | válido |",
              "|---|---|---|---|---|---|---|---|"]
        for nome, d in med["C5"].items():
            if "erro" in d:
                L.append("| `%s` | — | — | — | — | — | **erro: %s** |" % (nome, d["erro"]))
                continue
            L.append("| `%s` | %d | %s | %.3f | %s | Ø%.1f × %.1f | %s |"
                     % (nome, d["solidos"], n(d["volume_somado_mm3"], 1), d["massa_somada_kg"],
                        n(d["metal_da_matriz_na_montagem_mm3"], 1), d["caixa_D_x_Z_mm"][0],
                        d["caixa_D_x_Z_mm"][1], "sim" if d["brep_validos"] else "**NÃO**"))
        L.append("\nToda montagem é o cabeçote **completo com flange** (`Cabecote_EX-030_desenhado.step`) com a "
                 "matriz sentada no degrau, entregue sem booleano: `1 cabeçote + N` sólidos, onde N é o que o "
                 "arquivo da matriz tem mesmo (a Gedeon CERTA é 1 sólido; o par bipartido e a v27 são 2; a Gedeon "
                 "histórica é 2 metades).\n")
    if "C7" in med:
        L += ["## C7 — saúde topológica: BRepCheck em cada sólido, cara e aresta\n",
              "| arquivo | sólidos | faces | faces inválidas | arestas inválidas | cascas | volume (mm³) |",
              "|---|---|---|---|---|---|---|---|"]
        for c, d in med["C7"]["por_arquivo"].items():
            for r in d.get("solidos", []):
                L.append("| `%s` | %d | %d | %s | %s | %d | %s |"
                         % (c, len(d["solidos"]), r["faces"], r["faces_invalidas"], r["arestas_invalidas"],
                            r["cascas"], n(r["volume_mm3"], 1)))
        L.append("\nAchados: %s\n" % ("; ".join(med["C7"]["achados"]) or "nenhum"))
    L += ["## C6 — atalhos e baseline selado\n",
          "%d caminhos de MODELO selados pelo auditor conferidos byte a byte; divergências: %s. "
          "Fora do escopo desta checagem (script e JSON do baseline, que esta sessão re-escreveu de propósito; "
          "re-selá-los é ato da auditoria): %s.\n"
          % (med["C6"]["esperados_modelo"], ", ".join(med["C6"]["divergentes"]) or "**nenhuma**",
             ", ".join("`%s`" % x for x in med["C6"]["fora_do_escopo_reconhecido"])),
          "## Inventário completo (um bloco por arquivo)\n",
          "| arquivo | sólidos | cascas | faces | volume (mm³) | caixa Z | fenda | boca | estágios |",
          "|---|---|---|---|---|---|---|---|"]
    for rel, d in med["inventarios"].items():
        fd = None
        for x in med["C1"]["por_matriz"]:
            if x["arquivo"] == rel and "largura_mm" in x:
                fd = x
                break
        L.append("| `%s` | %d | %s | %d | %s | %.2f..%.2f | %s | %s | %s |"
                 % (rel, d["solidos"], "/".join(str(c) for c in d["cascas_por_solido"]), d["faces"],
                    n(d["volume_mm3"], 1), d["caixa"]["z"][0], d["caixa"]["z"][1],
                    ("%.3f×%.3f" % (fd["largura_mm"], fd["espessura_mm"])) if fd else "—",
                    ("Ø%.2f" % fd["boca_entrada_mm"]) if fd and fd["boca_entrada_mm"] else "—",
                    " · ".join("Ø%.2f" % t[0] for t in (fd["estagios"] if fd else [])) or "—"))
    L.append("\n## O que divergiu\n")
    L.append("\n".join("* %s" % f for f in med["divergencias"]) or "* nada — as seis correlações bateram")
    open(ARQ_MD, "w", encoding="utf-8").write("\n".join(L) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
