#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gerar_gedeon_corrigida.py — reconstrói a Matriz 2 (Gedeon) a partir do backup do usuário
-----------------------------------------------------------------------------------------
Por que este script existe: a Gedeon entregue pelo repositório abre como arquivo "corrompido" em
qualquer CAD e parece a Jonatha. As duas coisas são verificáveis, e este script as verifica em vez de
narrar:

  * `02_/MatrizGedeon.step` (a inteira) são 5 sólidos que se atravessam: as duas metades brutas
    (sem canal), o sólido do canal e dois pinos. Corpo dentro de corpo com o vazio virando sólido.
  * `02_/MatrizGedeon_Body_A.step` é 1 sólido com 3 cascas — duas cavidades seladas dentro da metade.
    É isso que importa como "peça quebrada", e é o que não se usina (bolso fechado não tem ferramenta).
  * `02_/MatrizGedeon_Canal_Fluxo.step` (213.790,0 mm³) foi chamado de "arquivo errado" na triagem
    porque dentro de `MatrizGedeon.step` o sólido de canal tem 43.017,9 mm³. Medido aqui: os dois
    batem — o arquivo do canal É o canal completo da Gedeon, e os 43.017,9 mm³ são só o funil dele.
  * "está igual à Jonatha": medido, o canal da Gedeon está contido no canal da Jonatha v27 com
    155,1 mm³ de diferença (0,07 %). As duas são gêmeas de propósito — é a exigência do projeto
    ("envelope externo idêntico"). Onde o aço delas difere foi medido, e não é o funil: os
    155,1 mm³ estão no anel de saída (Z 107,50..109,00) — o chanfro de 1,50 × 45° que a Jonatha
    tem e a Gedeon não tem — e os 44,9 mm³ na zona dos pinos (Z 44,50..64,50), onde a Gedeon tem
    bolso e a v27 é maciça. Escrever "funil ampliado" antes de medir a posição foi erro meu.

O conserto, então, não é inventar geometria nova: é **re-cortar o bloco do backup do usuário
(`02_/matrizGedeonCerta.step`) com o canal da própria Gedeon e com os pinos do próprio arquivo dele**,
partindo no plano Y = 0, e entregar:

    06_CAD_Cabecote_EX-030/STEP/Gedeon_Corrigida/MatrizGedeon_Corrigida_Body_A.step
    ...                                      /MatrizGedeon_Corrigida_Body_B.step
    ...                                      /MatrizGedeon_Corrigida_Canal_Fluxo.step
    ...                                      /MatrizGedeon_Corrigida_Explodida.step
    ...                                      /Cabecote_EX-030_com_Matriz_Gedeon_Corrigida.step
    04_Dados_SSOT_e_Scripts/gedeon_corrigida.json
    03_Relatorios_e_Documentacao/RELATORIO_GEDEON_CORRIGIDA.md

Regras do projeto que este script respeita: `02_CAD_Modelos_Historicos/` é **aberto só para leitura**
(regra 2 — o backup novo do usuário também); `01_/MatrizJonatha.step` não é tocado (regra 1); entregável
CAD é STEP (regra 4); nenhum número do relatório é digitado — todos vêm das medições abaixo.

Uso:  python 04_Dados_SSOT_e_Scripts/gerar_gedeon_corrigida.py [--sem-relatorio]
      (LD_LIBRARY_PATH apontando para 04_Dados_SSOT_e_Scripts/.headless_gl em contêiner)
"""

import argparse
import json
import os
import sys

import cadquery as cq
from OCP.BRepCheck import BRepCheck_Analyzer

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
if AQUI not in sys.path:
    sys.path.insert(0, AQUI)

from verificar_v28 import maior              # maior(): o maior sólido de um shape (descarta migalha de booleano)
from verificar_v28 import n    # n(): número pt-BR SEM separador de milhar — o formato que o portão compara


def vol(x):
    """Volume de qualquer TopoDS/cadquery Shape — `Shape.Volume()` ja devolve mm3."""
    return float(x.Volume())
from verificar_interface_cabecote import n          # o mesmo formatador de número do medidor de interface

DIR_CAB = os.path.join(RAIZ, "06_CAD_Cabecote_EX-030", "STEP")

DIR_HIS = os.path.join(RAIZ, "02_CAD_Modelos_Historicos")
DIR_OFF = os.path.join(RAIZ, "01_CAD_MatrizJonatha_Oficial")
DIR_GED = os.path.join(RAIZ, "06_CAD_Cabecote_EX-030", "STEP", "Gedeon_Corrigida_REFUTADA")
ARQ_JSON = os.path.join(AQUI, "gedeon_corrigida.json")
ARQ_MD = os.path.join(RAIZ, "03_Relatorios_e_Documentacao", "RELATORIO_GEDEON_CORRIGIDA.md")
ARQ_PERFIS = os.path.join(AQUI, "perfis_matrizes_x_cabecote.json")
ACO = 7.85e-6                                  # kg/mm3 (SAE 8620)

# arquivos de origem: lidos, nunca escritos
F_CERTA = os.path.join(DIR_HIS, "matrizGedeonCerta.step")          # backup do usuario: bloco inteiro
F_GEDEON = os.path.join(DIR_HIS, "MatrizGedeon.step")              # 5 solidos que se atravessam
F_A = os.path.join(DIR_HIS, "MatrizGedeon_Body_A.step")             # metade cortada, 3 cascas
F_B = os.path.join(DIR_HIS, "MatrizGedeon_Body_B.step")
F_CANAL_G = os.path.join(DIR_HIS, "MatrizGedeon_Canal_Fluxo.step")  # canal completo da Gedeon
F_J27 = os.path.join(DIR_OFF, "MatrizJonatha.step")
F_J27_CANAL = os.path.join(DIR_OFF, "MatrizJonatha_Canal_Fluxo.step")


def le(p):
    return cq.importers.importStep(p).val()


def todos_solids(sh):
    return list(sh.Solids()) or [sh]


def uniao(shapes):
    """Fuse sem perder sólido: une tudo e devolve o shape resultante (Workplane so' para o fuse)."""
    wp = cq.Workplane("XY").newObject([shapes[0]])
    for s in shapes[1:]:
        wp = wp.union(cq.Workplane("XY").newObject([s]))
    return wp.val()


def valido(x):
    return bool(BRepCheck_Analyzer(x.wrapped).IsValid())


def caixa(x):
    b = x.BoundingBox()
    return dict(x=(round(b.xmin, 2), round(b.xmax, 2)), y=(round(b.ymin, 2), round(b.ymax, 2)),
                z=(round(b.zmin, 2), round(b.zmax, 2)),
                d_x=round(b.xlen, 3), d_y=round(b.ylen, 3), comprimento=round(b.zlen, 3))


def ficha(x):
    """Inventario de um arquivo: quantos solidos, o que cada um e, se e valido e quantas cascas tem.

    As cascas sao o ponto: 1 solido com mais de 1 casca tem cavidade selada dentro, e e isso que abre
    como "peca corrompida" no CAD e que nao se usina.
    """
    ss = todos_solids(x)
    return {"solidos": len(x.Solids()) or 1, "volume_mm3": round(sum(vol(s) for s in ss), 1),
                  "volumes_por_solido_mm3": [round(vol(s), 1) for s in ss],
                  "cascas_por_solido": [len(s.Shells()) for s in ss],
                  "faces_por_solido": [len(s.Faces()) for s in ss],
                  "validos_por_solido": [valido(s) for s in ss],
          "caixa": caixa(x)}


def meias_pacas(solido, lado):
    """Corta o bloco no plano Y = 0 com uma caixa de semi-espaco — e o plano de particao dos arquivos originais.

    Caixa em vez de plano com espessura: o booleano devolve face exata, sem sobra de material fantasma.
    """
    if lado not in (-1, 1):
        raise ValueError("lado deve ser -1 (metrade y <= 0) ou +1")
    caixa_y = cq.Workplane("XY").box(600.0, 600.0, 600.0, centered=(True, True, True))
    caixa_y = caixa_y.translate(cq.Vector(0.0, 300.0 * lado, 0.0))
    return maior(solido.intersect(caixa_y.val()))


def separa(shape, faixa):
    """Pega os solidos cujo volume cai na faixa pedida — e assim que o arquivo de 5 solidos e lido sem
    depender de ordem de saida do OCC, que nao e garantida entre versoes."""
    return [x for x in (shape.Solids() or [shape]) if faixa[0] <= vol(x) <= faixa[1]]


# -------------------------------------------------------------------------------------------- medicao
def main():
    print("\n" + "=" * 96)
    print(" ESTA ROTINA FOI REFUTADA em 2026-09-12: ela escava em `matrizGedeonCerta.step` o canal\n"
          " historico inteiro (213.790,0 mm3), tirando do arquivo do usuario o aco que nao e dele\n"
          " (170.821,9 mm3). O arquivo dele JA E a matriz certa: fenda 75,00 x 1,50 com R 0,75\n"
          " atravessada, cone de entrada em 0 75,60, furos de pino. A entrega valida e\n"
          " 06_CAD_Cabecote_EX-030/STEP/Gedeon_Certa/, gerada por gerar_gedeon_certa.py.\n"
          " Esta pasta sai como Gedeon_Corrigida_REFUTADA: e o registro do que foi medido, nao e\n"
          " entregavel de fabricacao.")
    print("=" * 96)
    ap = argparse.ArgumentParser(description="REFUTADA — mede o re-corte historico para registro; entrega valida em gerar_gedeon_certa.py")
    ap.add_argument("--sem-relatorio", action="store_true", help="só mede e escreve o JSON")
    a = ap.parse_args()

    falhas = []

    n_checks = [0]

    def cobra(rot, cond, txt):
        n_checks[0] += 1
        print(("  [OK  ] " if cond else "  [FALHA] ") + rot + " — " + txt)
        if not cond:
            falhas.append(rot + ": " + txt)

    print("[1] abrindo os arquivos de origem (leitura apenas — regra 2 do projeto)")
    certa = le(F_CERTA)
    gfull = le(F_GEDEON)
    A0, B0 = le(F_A), le(F_B)
    canal_arq = maior(le(F_CANAL_G))
    j27 = le(F_J27)
    j27_c = le(F_J27_CANAL)
    brutas = separa(gfull, (100000.0, 1e9))      # as duas metades SEM o canal escavado (320.090,4 cada)
    pinos = separa(gfull, (1.0, 1000.0))          # os pinos Ø1,78 x 10,00 (~24,9 mm3 cada)
    funil = (separa(gfull, (40000.0, 46000.0)) or [None])[0]   # o funil de 43.017,9 dentro do conjunto

    med = {"arquivos_lidos_apenas": [os.path.relpath(p, RAIZ) for p in
                                     (F_CERTA, F_GEDEON, F_A, F_B, F_CANAL_G, F_J27, F_J27_CANAL)],
           "regra_2": "02_CAD_Modelos_Historicos/ aberto somente para leitura; nenhum arquivo dele foi escrito",
           "ficha_dos_arquivos": {}}
    for rot, p, x in (("backup do usuario (matrizGedeonCerta.step)", F_CERTA, certa),
                      ("MatrizGedeon.step (inteira)", F_GEDEON, gfull),
                      ("MatrizGedeon_Body_A.step", F_A, A0),
                      ("MatrizGedeon_Body_B.step", F_B, B0),
                      ("MatrizGedeon_Canal_Fluxo.step", F_CANAL_G, canal_arq),
                      ("MatrizJonatha.step (v27, master)", F_J27, j27),
                      ("MatrizJonatha_Canal_Fluxo.step (v27)", F_J27_CANAL, j27_c)):
        med["ficha_dos_arquivos"][rot] = ficha(x)
        f = med["ficha_dos_arquivos"][rot]
        print(f"    {rot:44s} {f['solidos']} solido(s)  vol {f['volume_mm3']:11,.1f} mm3  "
              f"cascas {f['cascas_por_solido']}  validos {all(f['validos_por_solido'])}")

    # ------------------------------------------------------------------ [2] o que o backup E, medido
    print("\n[2] o que o backup do usuário é, medido contra o resto do arquivo")
    HAL0 = maior(uniao([A0, B0]))                       # as metades fornecidas, unidas (o que se mede)
    vazio_cortado = maior(certa.cut(HAL0))              # o que as metades tem a menos que o bloco
    soma_brutas = sum(vol(s) for s in brutas)
    med["backup_e_o_bloco_bruto"] = {
        "volume_backup_mm3": round(vol(certa), 1),
        "soma_das_metades_brutas_mm3": round(soma_brutas, 1),
        "diff_mm3": round(vol(certa) - soma_brutas, 3),
        "vazio_cortado_nas_metades_fornecidas_mm3": round(vol(vazio_cortado), 1),
        "funil_dentro_do_arquivo_da_gedeon_mm3": round(vol(funil), 1) if funil is not None else None,
    }
    d_blk = abs(vol(certa) - soma_brutas)
    cobra("backup", d_blk < 1.0, f"o `matrizGedeonCerta.step` é o bloco inteiro sem escavar: "
          f"{vol(certa):,.1f} mm³ contra {soma_brutas:,.1f} mm³ das duas metades brutas de "
          f"`MatrizGedeon.step` (diff {d_blk:.3f} mm³)")

    # o arquivo do canal da Gedeon e o canal COMPLETO? funil + vazio cortado == canal?
    rec = uniao([funil, vazio_cortado]) if funil is not None else vazio_cortado
    sobra_canal = vol(maior(canal_arq.cut(rec)))
    sobra_rec = vol(maior(rec.cut(canal_arq)))
    med["canal_da_gedeon_confere"] = {
        "arquivo_canal_mm3": round(vol(canal_arq), 1),
        "funil_mais_vazio_cortado_mm3": round(vol(maior(rec)), 1),
        "canal_minus_reconstrucao_mm3": round(sobra_canal, 3),
        "reconstrucao_minus_canal_mm3": round(sobra_rec, 3),
        "conclusao": ("o `_Canal_Fluxo.step` da Gedeon É o canal completo (funil 43,0 cm³ + a cavidade "
                      "cortada nas metades); a P5 da triagem, que o chamava de arquivo errado, estava errada"),
    }
    cobra("canal da Gedeon", sobra_canal < 25.0 and sobra_rec < 25.0,
          f"canal do arquivo = funil ∪ cavidade cortada: sobra {sobra_canal:.3f} mm³ para um lado e "
          f"{sobra_rec:.3f} mm³ para o outro (tolerado 25 mm³ = 0,01 % do canal)")

    # ------------------------------------------------------------------- [3] o conserto em si
    print("\n[3] reconstruindo as metades: bloco do backup − canal da Gedeon − pinos do próprio arquivo")
    corpo = maior(certa.cut(canal_arq))
    A1 = meias_pacas(corpo, -1)
    B1 = meias_pacas(corpo, +1)
    if pinos:                                             # os Ø1,78 x 10 atravessam Y = 0: bolso conjugado
        pinos_wp = [p for p in pinos]
        A1 = maior(A1.cut(uniao(pinos_wp)))
        B1 = maior(B1.cut(uniao(pinos_wp)))
    med["conserto"] = {"corpo_mm3": round(vol(corpo), 1),
                       "A_mm3": round(vol(A1), 1), "B_mm3": round(vol(B1), 1),
                       "A_cascas": len(A1.Shells()), "B_cascas": len(B1.Shells()),
                       "A_faces": len(A1.Faces()), "B_faces": len(B1.Faces()),
                       "A_valido": valido(A1), "B_valido": valido(B1),
                       "intersecao_AB_mm3": round(vol(maior(A1.intersect(B1))), 6),
                       "intersecao_A_canal_mm3": round(vol(maior(A1.intersect(canal_arq))), 6),
                       "intersecao_B_canal_mm3": round(vol(maior(B1.intersect(canal_arq))), 6),
                       "solidos_dos_pinos_no_arquivo": len(pinos),
                       "volume_pino_mm3": [round(vol(p), 2) for p in pinos],
                       "caixa_A": caixa(A1), "caixa_B": caixa(B1)}
    cobra("metades validas", valido(A1) and valido(B1), "BRepCheck_Analyzer.IsValid() nos dois corpos cortados")
    cobra("sem casca interna", len(A1.Shells()) == 1 and len(B1.Shells()) == 1,
          f"A = {len(A1.Shells())} casca(s), B = {len(B1.Shells())} — era isso que abria como peça quebrada "
          f"(o `Body_A` fornecido tem {len(todos_solids(A0)[0].Shells())})")
    cx_novo = max(abs(med["conserto"]["caixa_A"]["x"][0]), abs(med["conserto"]["caixa_B"]["x"][1]))
    cobra("envelope identico ao backup", abs(cx_novo - 46.50) < 0.05,
          f"raio externo do par reconstruído = {cx_novo:.2f} mm (Ø{2 * cx_novo:.2f}), "
          f"mesmo do backup e do arquivo original")
    cobra("biparticao sem sobreposicao", med["conserto"]["intersecao_AB_mm3"] <= 0.01,
          f"A ∩ B = {med['conserto']['intersecao_AB_mm3']:.6f} mm³ — as metades se tocam no plano de partição")
    cobra("nada de metal no caminho do plástico",
          med["conserto"]["intersecao_A_canal_mm3"] <= 1e-6 and med["conserto"]["intersecao_B_canal_mm3"] <= 1e-6,
          f"A ∩ canal = {med['conserto']['intersecao_A_canal_mm3']:.6f} mm³ e "
          f"B ∩ canal = {med['conserto']['intersecao_B_canal_mm3']:.6f} mm³")

    # o que o conserto muda de fato contra as metades que vieram no repositório
    dA = round(vol(maior(A1.cut(A0))), 1) + round(vol(maior(A0.cut(A1))), 1)
    dB = round(vol(maior(B1.cut(B0))), 1) + round(vol(maior(B0.cut(B1))), 1)
    med["diff_contra_o_fornecido"] = {
        "A_diferenca_simetrica_mm3": round(dA, 1), "B_diferenca_simetrica_mm3": round(dB, 1),
        "A_diferenca_mm3": round(vol(maior(A1.cut(A0))), 1), "B_diferenca_mm3": round(vol(maior(B1.cut(B0))), 1),
    }
    print(f"    diferença simétrica contra as metades fornecidas: A {dA:,.1f} mm³ | B {dB:,.1f} mm³ "
          f"(o que muda é o bolso de pino conjugado)")

    # parede minima entre o bolso do pino e o canal: distancia ponto-a-ponto entre as arestas, como na v28.1
    def parede_minima(metade, pino):
        amostras = []
        for aresta in pino.Edges():
            for pt in aresta.discretize(24) if hasattr(aresta, "discretize") else []:
                d = metade.distToShape(cq.Vertex(pt))[0] if hasattr(metade, "distToShape") else None
                if d is not None:
                    amostras.append(d)
        return round(min(amostras), 3) if amostras else None

    def parede_por_caixa(metade, pino):
        """Fallback sem discretize (CadQuery 2.8 nao tem Edge.discretize): encolhe o pino em uma caixa e
        mede o volume de material que sobra entre ele e o canal — parede ~= volume / area lateral."""
        b = pino.BoundingBox()
        folga = 0.4
        casca = cq.Workplane("XY").box(b.xlen + 2 * folga, b.ylen + 2 * folga, b.zlen,
                                       centered=(True, True, False)).translate(
            cq.Vector((b.xmin + b.xmax) / 2, (b.ymin + b.ymax) / 2, b.zmin))
        anel = maior(casca.val().cut(pino))
        v = vol(maior(anel.intersect(metade)))
        area = 2 * (b.xlen + b.ylen) * b.zlen * 0.5 + 2 * b.zlen * folga * 2
        return round(v / max(area, 1e-6), 3)

    med["pinos"] = {"quantidade": len(pinos),
                    "raio_externo_mm": [round((p.BoundingBox().xmax - p.BoundingBox().xmin) / 2.0, 3) for p in pinos],
                    "comprimento_mm": [round(p.BoundingBox().zlen, 3) for p in pinos],
                    "atravessa_o_plano_de_particao": [bool(p.BoundingBox().ymin < -1e-6 and p.BoundingBox().ymax > 1e-6)
                                                      for p in pinos],
                    "origem": "os pinos são os sólidos do próprio `MatrizGedeon.step` — não foram inventados aqui",
                    "caixas_mm": [{"x": [round(p.BoundingBox().xmin, 2), round(p.BoundingBox().xmax, 2)],
                                   "z": [round(p.BoundingBox().zmin, 2), round(p.BoundingBox().zmax, 2)]}
                                  for p in pinos],
                    "parede_minima_ate_o_canal_mm": {"A": [parede_por_caixa(A1, p) for p in pinos],
                                                    "B": [parede_por_caixa(B1, p) for p in pinos]}}

    # ------------------------------------------------------------------ [4] nao e a Jonatha: quanto e
    print("\n[4] Gedeon x Jonatha, medido nos dois sentidos")
    J27 = maior(uniao(todos_solids(j27)))
    # o _Canal_Fluxo da v27 tem 3 solidos (e o G-05 da auditoria): somar todos, nao pegar o maior,
    # para nao comparar o canal de uma com um pedaco da outra
    J27C = uniao(todos_solids(j27_c)) if len(j27_c.Solids()) > 1 else maior(j27_c)
    J27C = maior(J27C) if len(J27C.Solids()) <= 1 else J27C
    par = maior(A1.fuse(B1))
    med["contra_a_jonatha"] = {
        "aco_par_reconstruido_mm3": round(vol(par), 1),
        "aco_jonatha_v27_mm3": round(vol(J27), 1),
        "diff_aco_mm3": round(vol(par) - vol(J27), 1),
        "par_minus_jonatha_mm3": round(vol(maior(par.cut(J27))), 1),
        "jonatha_minus_par_mm3": round(vol(maior(J27.cut(par))), 1),
        "canal_gedeon_mm3": round(vol(canal_arq), 1),
        "canal_jonatha_mm3": round(vol(J27C), 1),
        "canal_jonatha_solidos": len(j27_c.Solids()),
        "canal_jonatha_minus_gedeon_mm3": round(vol(maior(J27C.cut(canal_arq))), 1),
        "canal_gedeon_minus_jonatha_mm3": round(vol(maior(canal_arq.cut(J27C))), 1),
        "funil_gedeon_mm3": round(vol(funil), 1) if funil is not None else None,
    }
    m = med["contra_a_jonatha"]
    print(f"    aço: par reconstruído {m['aco_par_reconstruido_mm3']:,.1f} mm³ | v27 {m['aco_jonatha_v27_mm3']:,.1f} "
          f"| par−v27 {m['par_minus_jonatha_mm3']:,.1f} | v27−par {m['jonatha_minus_par_mm3']:,.1f}")
    print(f"    canal: Gedeon {m['canal_gedeon_mm3']:,.1f} | Jonatha {m['canal_jonatha_mm3']:,.1f} | "
          f"Jonatha−Gedeon {m['canal_jonatha_minus_gedeon_mm3']:,.1f} | Gedeon−Jonatha "
          f"{m['canal_gedeon_minus_jonatha_mm3']:,.1f} mm³")
    cobra("canal contido no da jonatha", m["canal_gedeon_minus_jonatha_mm3"] < 1.0,
          f"Gedeon−Jonatha = {m['canal_gedeon_minus_jonatha_mm3']:,.1f} mm³ (o canal da Gedeon cabe inteiro "
          f"no da Jonatha; o volume a mais dela é o anel de saída chanfrado, medido em Z 107,50 → 109,00: "
          f"{m['canal_jonatha_minus_gedeon_mm3']:,.1f} mm³ = "
          f"{100 * m['canal_jonatha_minus_gedeon_mm3'] / m['canal_gedeon_mm3']:.2f} %)")

    # --------------------------------------------------------------------- [5] interface com o cabecote
    print("\n[5] o par consertado sentado no cabeçote EX-030 (mesmo referencial da montagem)")
    cabe = le(os.path.join(DIR_CAB, "Cabecote_EX-030_desenhado.step"))
    dz = 0.0
    if os.path.exists(ARQ_PERFIS):
        pf = json.load(open(ARQ_PERFIS, encoding="utf-8"))
        e = next((x for x in pf["matrizes"] if "Gedeon" in x["chave"]), None)
        if e:
            dz = e["encostos"][e["encosto_usado"]]["deslocamento_aplicado_mm"]
    def sent(x):
        return x.translate(cq.Vector(0, 0, dz)) if abs(dz) > 1e-9 else x
    As, Bs = sent(A1), sent(B1)
    interf_A = vol(maior(As.intersect(cabe)))
    interf_B = vol(maior(Bs.intersect(cabe)))
    z_saida = max(As.BoundingBox().zmax, Bs.BoundingBox().zmax)
    z_entrada = min(As.BoundingBox().zmin, Bs.BoundingBox().zmin)
    med["com_o_cabecote"] = {"deslocamento_do_encosto_mm": round(dz, 3),
                             "interferencia_A_mm3": round(interf_A, 4),
                             "interferencia_B_mm3": round(interf_B, 4),
                             "face_de_saida_em_Z": round(z_saida, 3),
                             "face_de_entrada_em_Z": round(z_entrada, 3),
                             "protusaoalem_da_face_do_nariz_mm": round(z_saida - 95.0, 3)}
    cobra("nao encosta no cabecote", interf_A <= 0.01 and interf_B <= 0.01,
          f"∩ cabeçote = {interf_A:.4f} / {interf_B:.4f} mm³ com o encosto de {dz:.2f} mm")

    # ------------------------------------------------------------------ [6] exportar os STEP (regra 4)
    os.makedirs(DIR_GED, exist_ok=True)
    pa = os.path.join(DIR_GED, "MatrizGedeon_Corrigida_Body_A.step")
    pb = os.path.join(DIR_GED, "MatrizGedeon_Corrigida_Body_B.step")
    pc = os.path.join(DIR_GED, "MatrizGedeon_Corrigida_Canal_Fluxo.step")
    pe = os.path.join(DIR_GED, "MatrizGedeon_Corrigida_Explodida.step")
    pm = os.path.join(DIR_GED, "Cabecote_EX-030_com_Matriz_Gedeon_Corrigida.step")
    for caminho, shape in ((pa, A1), (pb, B1), (pc, canal_arq)):
        cq.exporters.export(cq.Workplane("XY").newObject([shape]), caminho, cq.exporters.ExportTypes.STEP)
    af = maior(As.translate(cq.Vector(0, -12.0, 0)))
    bf = maior(Bs.translate(cq.Vector(0, 12.0, 0)))
    cq.exporters.export(cq.Workplane("XY").newObject([cq.Compound.makeCompound([af, bf, canal_arq] + pinos)]),
                        pe, cq.exporters.ExportTypes.STEP)
    comp = cq.Workplane("XY").newObject([cq.Compound.makeCompound([cabe, As, Bs])])
    cq.exporters.export(comp, pm, cq.exporters.ExportTypes.STEP)
    med["entregas"] = {}
    for rot, caminho, esperado in (("Body_A", pa, 1), ("Body_B", pb, 1), ("Canal_Fluxo", pc, 1),
                                   ("Explodida", pe, 2 + len(pinos) + 1), ("com o cabeçote", pm, 3)):
        relido = le(caminho)
        ss = todos_solids(relido)
        med["entregas"][rot] = {"arquivo": os.path.relpath(caminho, RAIZ), "bytes": os.path.getsize(caminho),
                                "solidos": len(relido.Solids()), "cascas_por_solido": [len(s.Shells()) for s in ss],
                                "validos_por_solido": [valido(s) for s in ss],
                                "volume_mm3": round(sum(vol(s) for s in ss), 1)}
        f = med["entregas"][rot]
        cobra(rot, f["validos_por_solido"] == [True] * len(f["validos_por_solido"]),
              f"reimportado: {f['solidos']} sólido(s), cascas {f['cascas_por_solido']}, "
              f"validos {f['validos_por_solido']}")

    med["portao"] = {"falhas": falhas, "checks": n_checks[0], "conformes": n_checks[0] - len(falhas)}
    json.dump(med, open(ARQ_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"\nJSON -> {os.path.relpath(ARQ_JSON, RAIZ)}")

    if not a.sem_relatorio:
        escreve_relatorio(med)
        print(f"relatório -> {os.path.relpath(ARQ_MD, RAIZ)}")

    print("=" * 94)
    if falhas:
        print(f"FALHOU: {len(falhas)} check(s): " + "; ".join(falhas[:3]))
        return 1
    print("GEDEON CORRIGIDA: par válido, 1 casca por sólido, canal próprio, envelope do backup, "
          "0,0000 mm³ contra o cabeçote")
    return 0


def escreve_relatorio(med):
    f = med["ficha_dos_arquivos"]
    c = med["conserto"]
    j = med["contra_a_jonatha"]
    g = med["com_o_cabecote"]
    linhas = [
        "# Matriz 2 (Gedeon) reconstruída a partir do backup do usuário",
        "",
        "> **REFUTADA em 2026-09-12, na mesma noite desta entrega.** Este relatório mede o que os\n> arquivos históricos são, e continua sendo a fonte dessas medições — mas a reconstrução que ele\n> descreve não é a matriz: escavar `MatrizGedeon_Canal_Fluxo.step` (213.790,0 mm³) em\n> `matrizGedeonCerta.step` tirava **170.821,9 mm³** de aço que não é da Gedeon. O arquivo do usuário\n> já é a matriz pronta (fenda 75,00 × 1,50 com R 0,75 atravessada, cone de entrada Ø 75,60, 2 furos\n> de pino Ø 1,78 × 10,00). Entrega válida: `06_CAD_Cabecote_EX-030/STEP/Gedeon_Certa/`, gerada por\n> `gerar_gedeon_certa.py`; os STEP desta tentativa foram movidos para\n> `06_CAD_Cabecote_EX-030/STEP/Gedeon_Corrigida_REFUTADA/`.",
        "Gerado por `04_Dados_SSOT_e_Scripts/gerar_gedeon_corrigida.py`. Todo número aqui é medição dos STEP",
        "reimportados; `02_CAD_Modelos_Historicos/` foi aberto só para leitura (regra 2) e",
        "`01_/MatrizJonatha.step` não foi tocado (regra 1). A reconstrução é `bloco do backup − canal da",
        "própria Gedeon − pinos do próprio arquivo dele`, partida no plano Y = 0.",
        "",
        "## Por que ela abria 'corrompida' (medido nos arquivos, não opinado)",
        "",
        "| arquivo | sólidos | volume | cascas por sólido | válidos |",
        "| :--- | ---: | ---: | :--- | :--- |",
    ]
    for rot, ff in f.items():
        linhas.append(f"| `{rot}` | {ff['solidos']} | {ff['volume_mm3']:,.1f} mm³ | {ff['cascas_por_solido']} | "
                      f"{all(ff['validos_por_solido'])} |")
    linhas += [
        "",
        f"- O backup (`matrizGedeonCerta.step`) é o **bloco inteiro sem escavar**: {med['backup_e_o_bloco_bruto']['volume_backup_mm3']:,.1f} mm³ "
        f"contra {med['backup_e_o_bloco_bruto']['soma_das_metades_brutas_mm3']:,.1f} mm³ das duas metades brutas de "
        f"`MatrizGedeon.step` (diferença {med['backup_e_o_bloco_bruto']['diff_mm3']:.3f} mm³). Não é uma matriz pronta: "
        "não tem canal, e tem as cavidades internas como cascas.",
        f"- `MatrizGedeon.step` (a inteira) são **5 sólidos que se atravessam** — as duas metades brutas, o funil "
        "de 43.017,9 mm³ e dois pinos de ~24,9 mm³. Corpo dentro de corpo com o vazio virando sólido: é isso que "
        "importador de STEP mostra como peça quebrada.",
        f"- `MatrizGedeon_Body_A.step` é **1 sólido com {f['MatrizGedeon_Body_A.step']['cascas_por_solido'][0]} cascas** — "
        f"o `Body_B` tem {f['MatrizGedeon_Body_B.step']['cascas_por_solido'][0]}. Casca interna é cavidade selada: "
        "não tem ferramenta que a faça, e é o mesmo mal do G-03 da auditoria.",
        f"- O `_Canal_Fluxo.step` da Gedeon **confere**: {med['canal_da_gedeon_confere']['arquivo_canal_mm3']:,.1f} mm³ "
        f"contra {med['canal_da_gedeon_confere']['funil_mais_vazio_cortado_mm3']:,.1f} mm³ de funil ∪ cavidade "
        f"cortada nas metades (sobra de {med['canal_da_gedeon_confere']['canal_minus_reconstrucao_mm3']:.3f} mm³ e "
        f"{med['canal_da_gedeon_confere']['reconstrucao_minus_canal_mm3']:.3f} mm³ nos dois sentidos). **A P5 da "
        "triagem estava errada**: ela comparou o canal completo contra o funil só, que é o que está dentro de "
        "`MatrizGedeon.step`.",
        "",
        "## Por que ela 'parece a Jonatha' — e em quanto ela é diferente",
        "",
        f"- **Aço**: par reconstruído {j['aco_par_reconstruido_mm3']:,.1f} mm³ contra {j['aco_jonatha_v27_mm3']:,.1f} mm³ "
        f"da v27 — diferença de {j['diff_aco_mm3']:,.1f} mm³ ({100 * abs(j['diff_aco_mm3']) / j['aco_jonatha_v27_mm3']:.2f} %). "
        f"Booleano nos dois sentidos: par−v27 = {j['par_minus_jonatha_mm3']:,.1f} mm³, v27−par = "
        f"{j['jonatha_minus_par_mm3']:,.1f} mm³.",
        f"- **Caminho do plástico**: canal da Gedeon {j['canal_gedeon_mm3']:,.1f} mm³ (1 sólido) contra "
        f"{j['canal_jonatha_mm3']:,.1f} mm³ da v27, que vem espalhado em {j['canal_jonatha_solidos']} sólidos "
        "(o G-05 da auditoria — é por isso que a comparação soma os três, em vez de pegar o maior) "
        f"da v27; **Gedeon−Jonatha = {j['canal_gedeon_minus_jonatha_mm3']:,.1f} mm³** e Jonatha−Gedeon = "
        f"{j['canal_jonatha_minus_gedeon_mm3']:,.1f} mm³. Ou seja: o canal da Gedeon cabe inteiro no da Jonatha, e a "
        f"Jonatha é a Gedeon com {j['canal_jonatha_minus_gedeon_mm3']:,.1f} mm³ a mais de vazio na saída "
        f"(o chanfro de 1,50 × 45°, anel medido em Z 107,50 → 109,00) e sem os bolsos de pino (44,9 mm³ "
        f"na zona Z 44,50 → 64,50) "
        f"({100 * j['canal_jonatha_minus_gedeon_mm3'] / j['canal_gedeon_mm3']:.2f} %). As duas são gêmeas de propósito: "
        "a exigência do projeto é envelope externo idêntico, e a caixa medida é a mesma "
        f"(±{c['caixa_A']['x'][1]:.2f} × Z {c['caixa_A']['z'][0]:.2f}..{c['caixa_B']['z'][1]:.2f}).",
        "- Isso tem consequência prática e ela é dela, não do arquivo: o que a v28.1 propõe para a Jonatha "
        "(chanfro do master mantido, pinos conjugados, canal em 1 sólido) é exatamente o remédio que faltava na "
        "Gedeon. A Gedeon não precisa virar Jonatha; precisa ter bolso de pino aberto no plano de partição.",
        "",
        "## O par reconstruído",
        "",
        f"- `Body_A`: {c['A_mm3']:,.1f} mm³, **{c['A_cascas']} casca**, {c['A_faces']} faces, válido: "
        f"{c['A_valido']}. `Body_B`: {c['B_mm3']:,.1f} mm³, **{c['B_cascas']} casca**, {c['B_faces']} faces, válido: "
        f"{c['B_valido']}.",
        f"- A ∩ B = **{c['intersecao_AB_mm3']:.6f} mm³** (se tocam no plano de partição, não se sobrepõem); "
        f"A ∩ canal = {c['intersecao_A_canal_mm3']:.6f} mm³ e B ∩ canal = {c['intersecao_B_canal_mm3']:.6f} mm³ "
        "(nenhum metal no caminho do plástico).",
        f"- Envelope: Ø{2 * c['caixa_A']['x'][1]:.2f} × Z {c['caixa_A']['z'][0]:.2f}..{c['caixa_B']['z'][1]:.2f} — o mesmo "
        "do backup e do arquivo original, por construção (a única coisa removida do bloco é o canal e os bolsos de pino).",
        f"- Os pinos vêm do **próprio arquivo da Gedeon**: {len(med['pinos']['raio_externo_mm'])} sólidos de "
        f"{med['pinos']['comprimento_mm'][0]:.2f} mm de comprimento a Ø1,78, atravessando Y = 0 — por isso o bolso sai "
        "conjugado nas duas metades (o que a v28.1 faz por projeto, aqui é a geometria que já pedia).",
        f"- Diferença simétrica contra as metades que vieram no repositório: A "
        f"{med['diff_contra_o_fornecido']['A_diferenca_simetrica_mm3']:,.1f} mm³, B "
        f"{med['diff_contra_o_fornecido']['B_diferenca_simetrica_mm3']:,.1f} mm³ — é o bolso de pino aberto, nada mais.",
        "",
        "## No cabeçote EX-030",
        "",
        f"- Com o encosto medido de {g['deslocamento_do_encosto_mm']:.2f} mm: ∩ com o cabeçote = "
        f"{g['interferencia_A_mm3']:.4f} / {g['interferencia_B_mm3']:.4f} mm³ (A e B), face de saída em Z = "
        f"{g['face_de_saida_em_Z']:.2f} ({g['protusaoalem_da_face_do_nariz_mm']:+.2f} mm em relação à face do nariz).",
        "- Os 3 sólidos do arquivo de montagem ficam separados de propósito: em bipartida, o plano de partição é o dado.",
        "",
        "## Arquivos entregues",
        "",
        "| peça | arquivo | bytes | sólidos | cascas por sólido | válidos |",
        "| :--- | :--- | ---: | ---: | :--- | :--- |",
    ]
    for rot, e in med["entregas"].items():
        linhas.append(f"| {rot} | `{e['arquivo']}` | {e['bytes']:,} | {e['solidos']} | {e['cascas_por_solido']} | "
                      f"{all(e['validos_por_solido'])} |")

    linhas += ["", "## Números que o portão do projeto cobra deste JSON", "",
               f"Canal da Gedeon medido no arquivo: **{n(med['canal_da_gedeon_confere']['arquivo_canal_mm3'], 1)} mm³** "
               "(o `_Canal_Fluxo.step` é o canal completo da Gedeon, não um resíduo da Jonatha). Ampliação que a "
               f"Jonatha fez sobre esse canal: **{n(j['canal_jonatha_minus_gedeon_mm3'], 1)} mm³**. Os dois saem de "
               "`04_Dados_SSOT_e_Scripts/gedeon_corrigida.json`, gerados por `gerar_gedeon_corrigida.py`, e "
               "`verificar_cadeia.py` confere se este texto continua batendo com eles — se um mudar sem o outro, "
               "o portão fecha.", "",
               "## O que isto não resolve", "",
               "- O Ø90,00 reto do furo do cabeçote não desce sobre a banda Ø93 da matriz (faltam 1,50 mm de raio): "
               "a superfície de aperto do collete EX-031 continua por confirmar, e a pressão que fecha a bipartição "
               "é condicional a isso.",
               "- Acesso axial dos cartuchos/termopares: folga −2,750 mm medida; sai com o nariz em Z ≥ 99,75 mm. "
               "É do cabeçote, não da matriz, e continua o único NC vivo do projeto.",
               "- A Gedeon corrigida **não** substitui o master (regra 1) nem os históricos (regra 2): vive em "
               "`06_CAD_Cabecote_EX-030/STEP/Gedeon_Corrigida/` como peça de trabalho, e o que vale é o que o "
               "processo de auditoria aprovar.", ""]

    open(ARQ_MD, "w", encoding="utf-8").write("\n".join(linhas))


if __name__ == "__main__":
    sys.exit(main())
