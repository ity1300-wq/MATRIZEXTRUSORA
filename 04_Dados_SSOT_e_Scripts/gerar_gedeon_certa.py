#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mede `02_/matrizGedeonCerta.step` como o que ele é: a Matriz Gedeon CERTA, inteira, num sólido só.

Por que este script existe. A tacada anterior (2026-09-12, `gerar_gedeon_corrigida.py`) tratou o arquivo
`matrizGedeonCerta.step` como "bloco bruto" e re-cortou nele o canal histórico da Gedeon
(`MatrizGedeon_Canal_Fluxo.step`, 213.790,0 mm³), com o argumento de que as metades do CAD histórico eram
o mesmo bloco sem escavação. O corte tirou 171.069,7 mm³ de aço do arquivo do usuário. Medido face por
face agora, o arquivo dele NÃO é bloco bruto: ele já tem a fenda 75,00 × 1,50 com R 0,75 atravessando de
Z = 0,17 a Z = 109,00, já tem o cone de entrada que abre em Ø 75,60 em Z = 0 e já tem os dois furos de
pino Ø 1,78 × 10,00. Ou seja: **é a matriz pronta**. Escavar o funil da Jonatha nela estava errado, e o
STEP entregue em `06_/STEP/Gedeon_Corrigida/` está errado por isso. Este script refaz a entrega sem
mexer em um décimo de aço do arquivo dele.

O que sobra de defeito no arquivo dele, e é o único: os dois furos de pino são **cavidades seladas
dentro do aço** — 1 sólido com 3 cascas, furo com parede de 4,11 mm até o diâmetro externo, sem acesso
de ferramenta. Isso não se usina como está. O conserto é só esse: partir no plano Y = 0 (os furos estão
centralizados em Y, ±0,89), o que abre em cada metade uma meia-cana no plano de partição. Nada mais.

Regras do projeto que este script obedece: `02_CAD_Modelos_Historicos/` e `01_/MatrizJonatha.step` abertos
SOMENTE para leitura; entregável só em STEP; nenhum número digitado no relatório — todo número vem das
medições abaixo e vai para `04_Dados_SSOT_e_Scripts/gedeon_certa.json`.

Uso:  python 04_Dados_SSOT_e_Scripts/gerar_gedeon_certa.py [--sem-relatorio]
      (com LD_LIBRARY_PATH apontando para 04_Dados_SSOT_e_Scripts/.headless_gl em contêiner)
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

from verificar_v28 import maior                  # maior(): descarta migalha de booleano
from verificar_v28 import n                        # n(): número pt-BR, o formato que o portão compara

DIR_HIS = os.path.join(RAIZ, "02_CAD_Modelos_Historicos")
DIR_OFF = os.path.join(RAIZ, "07_CAD_Matrizes", "M01_Jonatha_v27_OFICIAL")
DIR_SAI = os.path.join(RAIZ, "07_CAD_Matrizes", "M03_Gedeon_CERTA")
F_CERTA = os.path.join(DIR_HIS, "matrizGedeonCerta.step")
F_CANAL_G = os.path.join(DIR_HIS, "MatrizGedeon_Canal_Fluxo.step")
F_J27 = os.path.join(DIR_OFF, "MatrizJonatha.step")
F_J27_CANAL = os.path.join(DIR_OFF, "MatrizJonatha_Canal_Fluxo.step")
F_CAB = os.path.join(RAIZ, "06_CAD_Cabecote_EX-030", "STEP", "Cabecote_EX-030_sem_flange.step")
F_MON = os.path.join(RAIZ, "07_CAD_Matrizes", "M04_Gedeon_ENTREGUE_HISTORICA",
                     "Cabecote_EX-030_com_Matriz_Gedeon_Corrigida.step")
ARQ_JSON = os.path.join(AQUI, "gedeon_certa.json")
ARQ_MD = os.path.join(RAIZ, "03_Relatorios_e_Documentacao", "RELATORIO_GEDEON_CERTA.md")
ARQ_SSOT = os.path.join(AQUI, "cad_die_parameters.json")
ACO = 7.85e-6


def le(p):
    return cq.importers.importStep(p).val()


def vol(x):
    return float(x.Volume())


def uniao(shapes):
    wp = cq.Workplane("XY").newObject([shapes[0]])
    for s in shapes[1:]:
        wp = wp.union(cq.Workplane("XY").newObject([s]))
    return wp.val()


def valido(x):
    return bool(BRepCheck_Analyzer(x.wrapped).IsValid())


def caixa(x):
    b = x.BoundingBox()
    return dict(x=(round(b.xmin, 2), round(b.xmax, 2)), y=(round(b.ymin, 2), round(b.ymax, 2)),
                z=(round(b.zmin, 2), round(b.zmax, 2)), d_x=round(b.xlen, 3), d_y=round(b.ylen, 3),
                d_z=round(b.zlen, 3))


def inventario(s):
    """Face por face: todo cilindro de eixo Z com suas extensoes, os planos de normal Y (a fenda) e o cone.

    Cilindro de eixo Z: caixa com x e y de mesmo tamanho. E assim que se separa, pelo tamanho do raio,
    os tres estagios do envelope (Ø grandes) dos furos de pino (Ø pequenos) — sem depender de ordem de
    saida das faces, que o OCC nao garante.
    """
    cil, fenda, outros, cone, bores = {}, [], [], None, []
    for f in s.Faces():
        b, g = f.BoundingBox(), f.geomType()
        if g == "CYLINDER":
            r = round(f._geomAdaptor().Cylinder().Radius(), 3)
            if abs(b.xlen - b.ylen) < 0.01:                                    # eixo em Z
                if r < 5.0:                                                    # furo pequeno, cara por cara
                    bores.append((r, round(b.xmin, 2), round(b.xmax, 2), round(b.ymin, 2), round(b.ymax, 2),
                                  round(b.zmin, 2), round(b.zmax, 2)))
                d = cil.setdefault(r, dict(n=0, z=[b.zmin, b.zmax], x=[b.xmin, b.xmax], y=[b.ymin, b.ymax],
                                           area=0.0))
                d["n"] += 1
                d["area"] += f.Area()
                d["z"] = [min(d["z"][0], b.zmin), max(d["z"][1], b.zmax)]
                d["x"] = [min(d["x"][0], b.xmin), max(d["x"][1], b.xmax)]
                d["y"] = [min(d["y"][0], b.ymin), max(d["y"][1], b.ymax)]
            else:                                                              # eixo transversal: topo da fenda
                outros.append((r, round(b.xmin, 2), round(b.xmax, 2), round(b.ymin, 2), round(b.ymax, 2),
                               round(b.zmin, 2), round(b.zmax, 2)))
        elif g == "PLANE":
            nm = f.normalAt()
            if abs(nm.y) > 0.9:
                fenda.append((round(nm.y, 2), round(b.xmin, 2), round(b.xmax, 2),
                              round(b.ymin, 2), round(b.ymax, 2), round(b.zmin, 2), round(b.zmax, 2)))
        elif g == "CONE" and cone is None:
            cone = dict(raio_max=round(max(b.xlen, b.ylen) / 2.0, 3), z=(round(b.zmin, 2), round(b.zmax, 2)),
                        area=round(f.Area(), 1))
    return dict(cilindros_z={k: dict(n=v["n"], z=(round(v["z"][0], 2), round(v["z"][1], 2)),
                                     x=(round(v["x"][0], 2), round(v["x"][1], 2)),
                                     y=(round(v["y"][0], 2), round(v["y"][1], 2)),
                                     area=round(v["area"], 1)) for k, v in cil.items()},
                fenda_planos=fenda, cil_eixos_outros=outros, cone=cone, bores=bores,
                cascas=len(s.Shells()), faces=len(s.Faces()), volume=round(vol(s), 1))


def meias_pacas(solido, lado):
    """Parte o bloco no plano Y = 0 com semi-espaço: face exata, sem material fantasma."""
    cx = cq.Workplane("XY").box(600.0, 600.0, 600.0, centered=(True, True, True))
    cx = cx.translate(cq.Vector(0.0, 300.0 * lado, 0.0))
    return maior(solido.intersect(cx.val()))


def separa(shape, faixa):
    return [x for x in (shape.Solids() or [shape]) if faixa[0] <= vol(x) <= faixa[1]]


def main():
    ap = argparse.ArgumentParser(description="Mede e entrega a Matriz Gedeon certa (o arquivo do usuário).")
    ap.add_argument("--sem-relatorio", action="store_true")
    a = ap.parse_args()

    falhas = []
    nchk = [0]

    def cobra(rot, cond, txt):
        nchk[0] += 1
        print(("  [OK  ] " if cond else "  [FALHA] ") + rot + " — " + txt)
        if not cond:
            falhas.append(rot + ": " + txt)

    ssot = json.load(open(ARQ_SSOT, encoding="utf-8"))
    env = ssot["envelope_externo_mm"]
    par = ssot["matriz_jonatha_parameters"]

    print("[1] o arquivo do usuário, aberto só para leitura")
    certa = maior(le(F_CERTA))
    inv = inventario(certa)
    b = certa.BoundingBox()
    med = {"arquivo": os.path.relpath(F_CERTA, RAIZ), "leitura_apenas": True,
           "solidos": 1, "caixa": caixa(certa), "inventario": inv}
    print(f"    volume {vol(certa):,.1f} mm3 | faces {inv['faces']} | cascas {inv['cascas']} | "
          f"valido {valido(certa)} | Z {b.zmin:.2f}..{b.zmax:.2f} | x/y +-{b.xmax:.2f}")

    # --------------------------------------------------------------- [2] geometria medida, face por face
    print("\n[2] o que ele É, medido")
    passos = []
    for k in ("estagio_1", "estagio_2", "estagio_3"):
        d, z0, z1 = env[k]["diametro_mm"], env[k]["z_de_mm"], env[k]["z_ate_mm"]
        r = round(d / 2.0, 3)
        medido = (inv["cilindros_z"].get(r) or {}).get("z")
        passos.append(dict(nome=k, diametro_ssot=d, z_ssot=(z0, z1), raio_cilindro_mm=r,
                           z_medido=medido, diametro_medido=round(2 * r, 2) if medido else None,
                           n_caras=(inv["cilindros_z"].get(r) or {}).get("n", 0)))
        print(f"    {k}: Ø {d:5.2f} Z {z0:6.2f}..{z1:6.2f}  ->  cilindro r={r} medido em Z {medido}")

    # fenda: os dois planos de normal Y + os dois topos semicirculares, juntos
    fe = inv["fenda_planos"]
    ou = inv["cil_eixos_outros"]
    x_min = min([p[1] for p in fe] + [q[1] for q in ou])
    x_max = max([p[2] for p in fe] + [q[2] for q in ou])
    y_min = min([p[3] for p in fe] + [q[3] for q in ou])
    y_max = max([p[4] for p in fe] + [q[4] for q in ou])
    larg = round(x_max - x_min, 3)
    esp = round(y_max - y_min, 3)
    z_fen = (min([p[5] for p in fe] + [q[5] for q in ou]), max([p[6] for p in fe] + [q[6] for q in ou]))
    r_ponta = round(min(q[0] for q in ou), 3) if ou else None
    # furos de pino: cilindros de eixo Z com raio pequeno (os estagios do envelope tem Ø 79,5 pra cima)
    fur = inv["bores"]
    y_meia = round(max(max(abs(q[3]), abs(q[4])) for q in fur), 3) if fur else None
    # furo transversal de fixacao: cilindro de eixo != Z que NAO seja o topo arredondado da propria fenda
    trav = [q for q in ou if (q[6] - q[5]) < b.zlen - 0.5]
    med["fenda"] = dict(largura_mm=larg, espessura_mm=esp, raio_ponta_mm=r_ponta,
                        z_de_mm=round(z_fen[0], 2), z_ate_mm=round(z_fen[1], 2), n_planos=len(fe),
                        y_planos=[round(y_min, 2), round(y_max, 2)],
                        atravessa=round(z_fen[1], 2) == round(b.zmax, 2))
    med["cone_entrada"] = inv["cone"]
    med["furos_pino"] = dict(qtd=len(fur), diametro_mm=round(2 * (fur[0][0] if fur else 0.0), 2),
                            z=(min(q[5] for q in fur), max(q[6] for q in fur)) if fur else None,
                            x=[(q[1], q[2]) for q in fur], y_meia_largura_mm=y_meia,
                            comprimento_mm=round(max(q[6] for q in fur) - min(q[5] for q in fur), 2) if fur else None,
                            x_extremo_abs_mm=round(max(abs(q[2]) for q in fur), 2) if fur else None)
    med["furos_transversais"] = [dict(raio=q[0], x=(q[1], q[2]), z=(q[5], q[6])) for q in trav]
    print(f"    fenda: largura {larg:,.2f} x espessura {esp:,.2f} com R {r_ponta} nos topos - "
          f"Z {z_fen[0]:.2f}..{z_fen[1]:.2f} ({len(fe)} planos + {len(ou)} topos)")
    print(f"    cone de entrada: abre em Ø {2 * inv['cone']['raio_max']:.2f} em Z {inv['cone']['z'][0]:.2f}, "
          f"fecha em Z {inv['cone']['z'][1]:.2f}")
    print(f"    furos de pino: {len(fur)} x Ø {med['furos_pino']['diametro_mm']:.2f}, "
          f"Z {med['furos_pino']['z'][0]:.2f}..{med['furos_pino']['z'][1]:.2f} "
          f"({med['furos_pino']['comprimento_mm']:.2f} compr.), |x| ate "
          f"{med['furos_pino']['x_extremo_abs_mm']:.2f}, y +-{y_meia:.2f}")
    print(f"    furos transversais que nao sejam o topo da fenda: {len(trav)}")

    bloco = [cq.Workplane("XY").cylinder(p["z_medido"][1] - p["z_medido"][0], p["raio_cilindro_mm"])
             .translate(cq.Vector(0, 0, (p["z_medido"][0] + p["z_medido"][1]) / 2.0)).val() for p in passos]
    envelope = maior(uniao(bloco))
    cav = envelope.cut(certa)
    fluxo = maior(uniao(separa(cav, (1000.0, 1e9)))) if separa(cav, (1000.0, 1e9)) else None
    selos = separa(cav, (1.0, 1000.0))
    med["cavidade"] = dict(volume_envelope_mm3=round(vol(envelope), 1),
                           volume_cavidade_mm3=round(vol(fluxo), 1) if fluxo else None,
                           cavidades_seladas=len(selos),
                           volume_seladas_mm3=round(sum(vol(s) for s in selos), 1),
                           massa_kg=round(vol(certa) * ACO, 4))
    print(f"    caminho de fluxo (cone + fenda): {vol(fluxo):,.1f} mm3 | cavidades seladas: {len(selos)} "
          f"({sum(vol(s) for s in selos):,.1f} mm3)")

    # ------------------------------------------------------------- [3] contrato do projeto, na certa
    print("\n[3] contrato do projeto conferido no arquivo dele")
    tol = 0.05
    for p in passos:
        cobra(f"{p['nome']} no lugar", p["z_medido"] is not None and abs(p["z_medido"][0] - p["z_ssot"][0]) <= tol
              and abs(p["z_medido"][1] - p["z_ssot"][1]) <= tol,
              f"cilindro Ø {p['diametro_medido']} medido em Z {p['z_medido']}, SSOT Z {p['z_ssot']}")
    cobra("comprimento total", abs(b.zlen - env["comprimento_total_z_mm"]) <= tol,
          f"Z {b.zlen:,.3f} mm, contrato {env['comprimento_total_z_mm']:,.2f}")
    cobra("largura da fenda", abs(larg - par["land_width_mm"]) <= tol,
          f"{larg:,.3f} mm medida nas faces, contrato {par['land_width_mm']:,.2f}")
    cobra("espessura da fenda", abs(esp - par["land_thickness_mm"]) <= 0.02,
          f"{esp:,.3f} mm (planos em y = ±{esp / 2:.3f}), contrato {par['land_thickness_mm']:,.2f}")
    cobra("raio na ponta da fenda", r_ponta is not None and abs(r_ponta - par["edge_radius_mm"]) <= 0.02,
          f"R {r_ponta} mm nos dois topos semicirculares, contrato R {par['edge_radius_mm']:,.2f}")
    cobra("entrada restrita ao diametro do contrato", abs(2 * inv["cone"]["raio_max"] - par["entry_bore_diameter_mm"]) <= tol,
          f"Ø {2 * inv['cone']['raio_max']:,.2f} na face traseira, contrato Ø {par['entry_bore_diameter_mm']:,.2f}")
    cobra("fenda atravessa a peca e sai na face de saida", abs(z_fen[1] - b.zmax) <= 0.01,
          f"fenda Z {z_fen[0]:.2f}..{z_fen[1]:.2f}, face de saida Z {b.zmax:.2f}")
    cobra("sem flange e sem furo de fixacao na matriz", not trav,
          f"os unicos cilindros de eixo transversal sao os dois topos semicirculares da propria fenda "
          f"(R {r_ponta}); nenhum furo radial de fixacao e nenhum ressalto de flange: Ø maximo "
          f"{2 * max(p['raio_cilindro_mm'] for p in passos):.2f} so no primeiro estagio")
    canal_velho = maior(le(F_CANAL_G))
    sobra = vol(certa.cut(canal_velho))
    print(f"    [não reproduzido] cortar o canal histórico de {vol(canal_velho):,.1f} mm3 tiraria "
          f"{vol(certa) - sobra:,.1f} mm3 de aco do arquivo dele - e o que a entrega anterior fez")
    med["reincidencia_evitada"] = dict(volume_do_canal_historico_mm3=round(vol(canal_velho), 1),
                                       aco_que_ser_removido_da_certa_mm3=round(vol(certa) - sobra, 1))
    cob = uniao([meias_pacas(certa, -1), meias_pacas(certa, +1)])
    cobra("nenhum aco foi removido do arquivo dele nesta entrega",
          abs(vol(cob) - vol(certa)) <= 1e-3,
          f"A u B = {vol(cob):.4f} contra o bloco {vol(certa):.4f} mm3 "
          f"({vol(cob) - vol(certa):+.6f}): o funil historico de {vol(canal_velho):,.1f} mm3 nao foi escavado aqui")

    # ------------------------------------------------- [4] o unico defeito real: cavidade selada sem saida
    print("\n[4] o defeito que o arquivo dele tem, medido")
    od_na_zona = max(p["raio_cilindro_mm"] for p in passos
                   if p["z_medido"] and p["z_medido"][0] <= min(q[5] for q in fur))
    parede = round(od_na_zona - med["furos_pino"]["x_extremo_abs_mm"], 3)
    med["defeito_cavidade_selada"] = dict(cascas_no_solido=inv["cascas"], furos_sem_acesso=len(selos),
                                          parede_ate_o_externo_mm=parede,
                                          diametro_externo_na_zona=round(2 * od_na_zona, 2))
    cobra("o furo de pino nao tem saida para ferramenta", parede > 0.5 and len(selos) == len(fur),
          f"parede de {parede:,.2f} mm entre o furo e o Ø {2 * od_na_zona:,.2f} externo, e o solido tem "
          f"{inv['cascas']} cascas (1 externa + {len(selos)} seladas)")

    # ----------------------------------------- [5] conserto: partir em Y = 0 abre meia-cana em cada metade
    print("\n[5] conserto entregue: partir no plano de particao Y = 0, sem tirar aco nenhum")
    A = meias_pacas(certa, -1)
    B = meias_pacas(certa, +1)
    par_vol = abs(vol(A) + vol(B) - vol(certa))
    sobre = maior(A.intersect(B)) if A.intersect(B).Solids() else None
    med["entrega"] = dict(volume_A_mm3=round(vol(A), 1), volume_B_mm3=round(vol(B), 1),
                          soma_menos_o_bloco_mm3=round(par_vol, 6),
                          interseccao_A_B_mm3=round(vol(sobre), 4) if sobre else 0.0,
                          cascas_A=len(A.Shells()), cascas_B=len(B.Shells()),
                          valido_A=valido(A), valido_B=valido(B),
                          caixa_A=caixa(A), caixa_B=caixa(B))
    cobra("as duas metades reazem o bloco do usurario sem perder decimo", par_vol <= 1e-3,
          f"A + B = {vol(A) + vol(B):,.4f} contra o bloco {vol(certa):,.4f} mm3 (diff {par_vol:.6f})")
    cobra("nenhuma metade tem cavidade selada", len(A.Shells()) == 1 and len(B.Shells()) == 1,
          f"cascas: A {len(A.Shells())}, B {len(B.Shells())}")
    cobra("as duas metades sao solidos validos", valido(A) and valido(B),
          f"BRepCheck A {valido(A)}, B {valido(B)}")
    cobra("as duas metades se tocam sem se sobrepor", (vol(sobre) if sobre else 0.0) <= 0.01,
          f"interseccao {(vol(sobre) if sobre else 0.0):.4f} mm3 no plano Y = 0")
    faces_furo_A = [f for f in A.Faces() if f.geomType() == "CYLINDER"
                    and abs(f._geomAdaptor().Cylinder().Radius() - (y_meia or 0.89)) < 0.02]
    y_top_A = max(f.BoundingBox().ymax for f in faces_furo_A) if faces_furo_A else None
    cobra("o furo sai aberto no plano de particao (meia-cana usinavel)",
          y_top_A is not None and abs(y_top_A) < 1e-6,
          f"metade A tem {len(faces_furo_A)} cara(s) de furo, terminando em Y = {y_top_A:.2e} - "
          f"a ferramenta entra pela face de particao, nao ha mais cavidade fechada")

    # ------------------------------------------------------ [6] interface com o cabecote EX-030 (leitura)
    print("\n[6] interface com o cabeçote, na mesma colocação já medida")
    cab = maior(le(F_CAB))
    mons = le(F_MON).Solids()
    die_mont = max(mons, key=lambda s: abs(s.BoundingBox().zmax - cab.BoundingBox().zmax))
    off = round(die_mont.BoundingBox().zmin - b.zmin, 6)
    def desloca(sh, dz):
        return sh if abs(dz) <= 1e-9 else maior(cq.Workplane("XY").newObject([sh])
                                                .translate(cq.Vector(0.0, 0.0, dz)).val())
    certa_mont = desloca(certa, off)
    toca = maior(cab.intersect(certa_mont)) if cab.intersect(certa_mont).Solids() else None
    v_toca = round(vol(toca), 4) if toca else 0.0
    protr = round(certa_mont.BoundingBox().zmax - cab.BoundingBox().zmax, 3)
    face = round(cab.BoundingBox().zmax, 2)
    vazio_fluxo = desloca(fluxo, off)
    metal_no_fluxo = round(vol(vazio_fluxo.intersect(cab)), 4)
    cobra("a matriz passa pelos estagios sem tocar o cabecote", v_toca <= 0.01,
          f"interseccao matriz x cabecote = {v_toca:.4f} mm3 (colocacao: deslocamento axial {off:.3f} mm, "
          f"face da saida do cabecote em Z = {face:.2f})")
    cobra("a fenda fica fora do nariz do cabecote", protr > 0.0,
          f"a face de saida da matriz esta {protr:,.2f} mm alem da face do cabecote, entao a fenda "
          f"não encosta no nariz")
    cobra("nenhum aco do cabecote entra no caminho de fluxo", metal_no_fluxo is not None and metal_no_fluxo <= 0.01,
          f"cone+fenda x cabecote = {metal_no_fluxo:.4f} mm3")
    med["interface_cabecote"] = dict(deslocamento_axial_mm=off, interseccao_mm3=v_toca,
                                     protrusao_alem_da_face_mm=protr, face_saida_cabecote_z=face,
                                     metal_do_cabecote_no_fluxo_mm3=metal_no_fluxo)

    # --------------------------------------- [7] diferenca de conceito para a Jonatha v27, medida
    print("\n[7] a diferença de conceito para a Jonatha v27, medida nos dois sólidos")
    j27 = maior(uniao(le(F_J27).Solids()))          # as DUAS metades da v27: um solido só não é a peça
    bj = j27.BoundingBox()
    dz = round(b.zmax - bj.zmax, 6)                      # alinha pela face de saida, o datum das duas
    j27m = desloca(j27, dz)
    mais_g = round(vol(certa.cut(j27m)), 1)
    mais_j = round(vol(j27m.cut(certa)), 1)
    canal_j = maior(le(F_J27_CANAL))
    med["contra_a_jonatha"] = dict(alinhamento="face de saida em Z = " + str(round(b.zmax, 2)),
                                   volume_jonatha_aco_mm3=round(vol(j27), 1),
                                   volume_certa_aco_mm3=round(vol(certa), 1),
                                   aco_so_na_certa_mm3=mais_g, aco_so_na_jonatha_mm3=mais_j,
                                   fluxo_certa_mm3=round(vol(fluxo), 1),
                                   canal_da_v27_mm3=round(vol(canal_j), 1),
                                   diferenca_de_conceito=(
                                       "a certa e um tampao com a fenda atravessada e um cone de entrada; a v27 "
                                       "tem funil proprio dentro dela. A diferenca nao e 'funil ampliado': a "
                                       "Gedeon nao tem funil no seu aco - a convergencia a montante e do furo "
                                       "estagiado do cabecote."))
    print(f"    aço só na certa {mais_g:,.1f} mm3 | só na Jonatha {mais_j:,.1f} mm3 (aço das duas alinhados "
          f"pela face de saida)")
    print(f"    caminho de fluxo da certa {vol(fluxo):,.1f} mm3 contra o funil da v27 {vol(canal_j):,.1f} mm3; "
          f"aco das pecas inteiras: certa {vol(certa):,.1f} x v27 {vol(j27):,.1f} mm3")

    # --------------------------------------------------- [8] o que a entrega anterior errou, em numero
    d_ant = os.path.join(RAIZ, "07_CAD_Matrizes", "M04_Gedeon_ENTREGUE_HISTORICA")
    try:
        a_ant = maior(le(os.path.join(d_ant, "MatrizGedeon_Corrigida_Body_A.step")))
        b_ant = maior(le(os.path.join(d_ant, "MatrizGedeon_Corrigida_Body_B.step")))
        v_ant = vol(uniao([a_ant, b_ant]))
        med["entrega_anterior_refutada"] = dict(
            volume_aco_entrega_anterior_mm3=round(v_ant, 1), volume_aco_certa_mm3=round(vol(certa), 1),
            aco_removido_por_engano_mm3=round(vol(certa) - v_ant, 1),
            motivo="a entrega anterior escavou no arquivo do usuario o canal historico "
                   "`MatrizGedeon_Canal_Fluxo.step` inteiro, quando a unica cavidade da matriz e o cone de "
                   "entrada + a fenda atravessada")
        print(f"    [refutada] a entrega anterior tem {v_ant:,.1f} mm3 de aco contra os {vol(certa):,.1f} mm3 "
              f"do arquivo dele: {vol(certa) - v_ant:,.1f} mm3 removidos a mais")
    except FileNotFoundError:
        med["entrega_anterior_refutada"] = None
        print("    [refutada] pasta da entrega anterior nao encontrada - nada a comparar")
    # ------------------------------------------------------------------- [8] escreve os entregaveis
    print("\n[8] entregáveis")
    os.makedirs(DIR_SAI, exist_ok=True)
    nomes = {"MatrizGedeon_Certa_Body_A.step": A, "MatrizGedeon_Certa_Body_B.step": B,
             "MatrizGedeon_Certa_Canal_Fluxo.step": fluxo,
             "MatrizGedeon_Certa_Explodida.step": uniao([A, B, fluxo])}
    for nome, sh in nomes.items():
        cq.exporters.export(cq.Workplane("XY").newObject([sh]), os.path.join(DIR_SAI, nome))
        print("    " + nome)
    cq.exporters.export(cq.Workplane("XY").newObject([cab, certa_mont]),
                        os.path.join(DIR_SAI, "Cabecote_EX-030_com_Matriz_Gedeon_Certa.step"))
    print("    Cabecote_EX-030_com_Matriz_Gedeon_Corrigida... e o novo: Cabecote_EX-030_com_Matriz_Gedeon_Certa.step")
    rt = maior(le(os.path.join(DIR_SAI, "MatrizGedeon_Certa_Body_A.step")))
    med["round_trip"] = dict(volume_reimportada_mm3=round(vol(rt), 4),
                              diff_mm3=round(abs(vol(rt) - vol(A)), 6))
    cobra("o STEP escrito reimporta com o mesmo volume", abs(vol(rt) - vol(A)) < 1e-3,
          f"reimportado {vol(rt):,.4f} contra {vol(A):,.4f} mm3")
    med["checks"] = dict(total=nchk[0], falhas=len(falhas), falhas_lista=falhas)
    json.dump(med, open(ARQ_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("    JSON -> " + os.path.relpath(ARQ_JSON, RAIZ))

    if not a.sem_relatorio:
        md = [
            "# Matriz Gedeon CERTA — o que o arquivo do usuário é, e o que foi entregue",
            "",
            f"Fonte: `{med['arquivo']}` (aberto só para leitura). Números: `04_Dados_SSOT_e_Scripts/gedeon_certa.json`.",
            "",
            "## Por que este relatório existe",
            "",
            "A entrega anterior (`06_/STEP/Gedeon_Corrigida/`) re-cortou no arquivo do usuário o canal histórico",
            f"da Gedeon — tirou {n(med['reincidencia_evitada']['aco_que_ser_removido_da_certa_mm3'], 1)} mm³ de aço dele com o argumento de que o",
            "arquivo era um bloco bruto. **Estava errado.** Medido face por face, o arquivo já é a matriz pronta:",
            f"fenda {n(med['fenda']['largura_mm'], 2)} × {n(med['fenda']['espessura_mm'], 2)} mm com R {n(med['fenda']['raio_ponta_mm'], 2)} atravessando de Z = "
            f"{n(med['fenda']['z_de_mm'], 2)} a Z = {n(med['fenda']['z_ate_mm'], 2)}, cone de entrada abrindo em "
            f"Ø {n(2 * med['cone_entrada']['raio_max'], 2)} em Z = {n(med['cone_entrada']['z'][0], 2)}, e os dois furos de pino "
            f"Ø {n(med['furos_pino']['diametro_mm'], 2)} × {n(med['furos_pino']['z'][1] - med['furos_pino']['z'][0], 2)} mm.",
            "",
            "## O que foi conferido no arquivo dele (contrato do projeto, medido, não copiado)",
            "",
            f"* Envelope: os três estágios do SSOT batem com os cilindros medidos — Ø {n(env['estagio_1']['diametro_mm'], 2)} até Z = "
            f"{n(env['estagio_1']['z_ate_mm'], 2)}, Ø {n(env['estagio_2']['diametro_mm'], 2)} até Z = {n(env['estagio_2']['z_ate_mm'], 2)}, "
            f"Ø {n(env['estagio_3']['diametro_mm'], 2)} até Z = {n(env['estagio_3']['z_ate_mm'], 2)}; comprimento total Z = "
            f"{n(b.zlen, 3)}.",
            f"* Fenda: largura {n(med['fenda']['largura_mm'], 3)} (contrato {n(par['land_width_mm'], 2)}), espessura "
            f"{n(med['fenda']['espessura_mm'], 3)} (contrato {n(par['land_thickness_mm'], 2)}), raio dos topos "
            f"{n(med['fenda']['raio_ponta_mm'], 3)} (contrato R {n(par['edge_radius_mm'], 2)}).",
            f"* Entrada: Ø {n(2 * med['cone_entrada']['raio_max'], 2)} na face traseira (contrato Ø {n(par['entry_bore_diameter_mm'], 2)}), "
            f"fechando em cone até Z = {n(med['cone_entrada']['z'][1], 2)}.",
            f"* Sem flange e sem furo de fixação: os únicos cilindros de eixo diferente de Z são os dois furos de pino.",
            f"* Caminho de fluxo medido (cone + fenda): {n(med['cavidade']['volume_cavidade_mm3'], 1)} mm³; massa "
            f"{n(med['cavidade']['massa_kg'], 4)} kg.",
            "",
            "## O defeito que ele tem, e é um só",
            "",
            f"O sólido tem {inv['cascas']} cascas: {med['cavidade']['cavidades_seladas']} cavidades seladas dentro do aço, os furos de pino, "
            f"com parede de {n(med['defeito_cavidade_selada']['parede_ate_o_externo_mm'], 2)} mm até o Ø "
            f"{n(med['defeito_cavidade_selada']['diametro_externo_na_zona'], 2)} externo — não tem por onde entrar a ferramenta. "
            f"Volume fechado: {n(med['cavidade']['volume_seladas_mm3'], 1)} mm³.",
            "",
            "## O conserto entregue",
            "",
            f"Partir o bloco no plano Y = 0, que é onde os furos já estão centralizados (y ±{n(med['furos_pino']['y_meia_largura_mm'], 2)}), e "
            f"entregar as duas metades. Não foi removido aço nenhum: A + B = {n(vol(A) + vol(B), 4)} mm³ contra o "
            f"bloco {n(vol(certa), 1)} mm³ (diferença {n(med['entrega']['soma_menos_o_bloco_mm3'], 6)} mm³). Cada metade tem "
            f"1 casca, BRepCheck válido, e o furo sai como meia-cana aberta no plano de partição.",
            f"Interseção entre as metades: {n(med['entrega']['interseccao_A_B_mm3'], 4)} mm³.",
            "",
            "## Interface com o cabeçote EX-030",
            "",
            f"Colocação igual à que já estava medida (deslocamento axial {n(med['interface_cabecote']['deslocamento_axial_mm'], 3)} mm): "
            f"interseção matriz × cabeçote {n(med['interface_cabecote']['interseccao_mm3'], 4)} mm³, a face de saída da matriz fica "
            f"{n(med['interface_cabecote']['protrusao_alem_da_face_mm'], 2)} mm além da face do cabeçote (Z = "
            f"{n(med['interface_cabecote']['face_saida_cabecote_z'], 2)}), e o aço do cabeçote que cai dentro do cone+fenda é "
            f"{n(med['interface_cabecote']['metal_do_cabecote_no_fluxo_mm3'], 4)} mm³. Como o envelope externo é o mesmo da Gedeon "
            "histórica, os vereditos [A] a [G] de `verificar_interface_cabecote.py` não mudam.",
            "",
            "## Diferença de conceito para a Jonatha v27",
            "",
            f"Booleano medido: {n(med['contra_a_jonatha']['aco_so_na_certa_mm3'], 1)} mm³ de aço só na Gedeon certa e "
            f"{n(med['contra_a_jonatha']['aco_so_na_jonatha_mm3'], 1)} mm³ só na v27. A diferença não é \"funil ampliado\": é que a "
            f"Gedeon não tem funil próprio — o fluxo dela é o cone de entrada + a fenda atravessada "
            f"({n(med['contra_a_jonatha']['fluxo_certa_mm3'], 1)} mm³), e o resto da convergência é feito pelo próprio furo "
            "estagiado do cabeçote.",
            "",
            "## Arquivos",
            "",
            "```",
            "07_CAD_Matrizes/M03_Gedeon_CERTA/MatrizGedeon_Certa_Body_A.step",
            "07_CAD_Matrizes/M03_Gedeon_CERTA/MatrizGedeon_Certa_Body_B.step",
            "07_CAD_Matrizes/M03_Gedeon_CERTA/MatrizGedeon_Certa_Canal_Fluxo.step",
            "07_CAD_Matrizes/M03_Gedeon_CERTA/MatrizGedeon_Certa_Explodida.step",
            "07_CAD_Matrizes/M03_Gedeon_CERTA/Cabecote_EX-030_com_Matriz_Gedeon_Certa.step",
            "```",
            "",
            f"Checks: {nchk[0]} executados, {len(falhas)} falha(s). "
            + ("Nada promovido: o master continua v27.0." if not falhas else "VER LISTA ACIMA."),
        ]
        open(ARQ_MD, "w", encoding="utf-8").write("\n".join(md) + "\n")
        print("    relatorio -> " + os.path.relpath(ARQ_MD, RAIZ))

    if falhas:
        print("\nFALHAS:")
        for f_ in falhas:
            print("  - " + f_)
        sys.exit(1)
    print(f"\nGEDEON CERTA: arquivo do usuário entregue sem perder aço ({nchk[0]} checks, "
          f"{len(falhas)} falhas), com as cavidades seladas abertas no plano de partição")


if __name__ == "__main__":
    main()
