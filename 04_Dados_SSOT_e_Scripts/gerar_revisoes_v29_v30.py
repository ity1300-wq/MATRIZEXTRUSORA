#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Revisões de 2026-09-22 pedidas pelo dono: Ø94 / Ø89 / Ø79 com ±0,5 (re-faz a v29) e v30 faceada ao nariz.

O que ele disse, literal, e o que este script faz:

* "93,00 mude para 94 no desenho v29 ... 89,50 mude para 89 e 79,50 mude para 79 ... tolerancia de 0,5 para
  todas as cotas alteradas aqui" → a **v29 é re-feita**: o corpo passa a Ø94,00 / Ø89,00 / Ø79,00 nos mesmos Z
  (0→69,90 / 69,90→80,70 / 80,70→109,00) e o STEP é reescrito. Desenho e modelo têm de bater, senão a fábrica
  usina uma coisa e lê outra. Tolerância ±0,5 registrada nas cotas alteradas.
* "fac a versao 30 ... altere o comprimento 109,00 deixe menor, quero que fique faceado ao nariz do cabecote"
  → **v30** = mesmas cotas novas com comprimento **95,00 mm** = 109,00 − 14,00, sendo 14,00 a protrusão medida
  no C4 da auditoria (a face de saída da matriz estava 14,00 mm além da face do nariz do EX-030).
* "Quero manter proporcionalmente igual, so diminuindo o comprimento total, mas o land precisa ter as mesmas
  dimensões e cotas" → o corte **não** é um escalonamento bobo da peça: o canal é partido no início do land
  (Z = 98,50, medido), o funil é comprimido axialmente por s = 84,50/98,50 e o bloco **land + chanfro é movido
  rígido**, sem escala. Land 8,50, fenda 75,00 × 1,500, R 0,75 e área 112,0171 mm² ficam idênticos — e é isso
  que o script cobra com `assert` **depois** de medir, não antes.
* "fac uma versao da matriz dentro do cabecote ja" → duas montagens STEP (cabeçote completo com flange + matriz
  sentada, encosto face a face com dz = 0,00 como no perfil medido do v27), com folgas, interferência e
  protrusão medidas.

O material (aço 1045 + tratamento superficial na fenda) é decisão registrada no SSOT e na ficha do pacote;
geometria não depende dele. Nada aqui toca `02_CAD_Modelos_Historicos/`.

Uso: python3 04_Dados_SSOT_e_Scripts/gerar_revisoes_v29_v30.py
Saida: 07_CAD_Matrizes/Matriz_Jonatha_v29_OFICIAL/MATRIZ_V29_PECA_UNICA.step   (re-escrito)
       07_CAD_Matrizes/Matriz_Jonatha_v30_OFICIAL/{MATRIZ_V30_PECA_UNICA.step, MATRIZ_V30_CANAL_DE_FLUXO.step}
       06_CAD_Cabecote_EX-030/STEP/Cabecote_EX-030_com_Matriz_Jonatha_{v29,v30}.step
       04_Dados_SSOT_e_Scripts/revisoes_v29_v30.json
"""
import hashlib
import json
import math
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, ".."))
sys.path.insert(0, AQUI)

import cadquery as cq
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse
from OCP.BRepBuilderAPI import BRepBuilderAPI_GTransform, BRepBuilderAPI_Transform
from OCP.gp import gp_GTrsf, gp_Mat, gp_XYZ

from auditar_step_correlacoes import (ACO, abre, inventario, estagios, mede_fenda, vazio_da_peca,
                                      _seccao, maior, n, DIR_MAE)

DIR_V29 = os.path.join(DIR_MAE, "Matriz_Jonatha_v29_OFICIAL")
DIR_V30 = os.path.join(DIR_MAE, "Matriz_Jonatha_v30_OFICIAL")
DIR_CAB = os.path.join(RAIZ, "06_CAD_Cabecote_EX-030", "STEP")
CABECOTE = os.path.join(DIR_CAB, "Cabecote_EX-030_desenhado.step")
PERFIS = os.path.join(AQUI, "perfis_matrizes_x_cabecote.json")
CANAL_MAE = os.path.join(DIR_V29, "MATRIZ_V29_CANAL_DE_FLUXO.step")
F_JSON = os.path.join(AQUI, "revisoes_v29_v30.json")

# ------------------------------------------------------------------ decisoes dele, 2026-09-22
DIAMETROS = [94.00, 89.00, 79.00]          # antes, medidos no STEP herdado: 93,00 / 89,50 / 79,50
Z_DEGRAUS = [(0.00, 69.90), (69.90, 80.70), (80.70, 109.00)]
TOL = "±0,5 em todas as cotas alteradas (Ø94,00 / Ø89,00 / Ø79,00 e comprimento 95,00)"
ACO_NOVO = "aço 1045 + tratamento superficial por indução (ou nitretação) nas arestas do land"
L_V29, L_V30 = 109.00, 95.00


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def vol(sh):
    ss = sh.Solids()
    return sum(x.Volume() for x in ss) if ss else sh.Volume()


def cil(r_raio_or_diam, z0, z1, pelo_diametro=True):
    d = r_raio_or_diam if pelo_diametro else 2 * r_raio_or_diam
    return cq.Solid.makeCylinder(d / 2.0, z1 - z0, cq.Vector(0, 0, z0), cq.Vector(0, 0, 1))


def uniao(a, b):
    f = BRepAlgoAPI_Fuse(a.wrapped, b.wrapped)
    f.Build()
    if not f.IsDone():
        raise SystemExit("FALHOU: fuse nao convergiu (BRepAlgoAPI_Fuse)")
    r = cq.Shape.cast(f.Shape())
    if not r.isValid() or not r.Solids():
        raise SystemExit("FALHOU: fuse devolveu solido invalido ou vazio")
    return r.clean()


def corta(a, b):
    c = BRepAlgoAPI_Cut(a.wrapped, b.wrapped)
    c.Build()
    if not c.IsDone():
        raise SystemExit("FALHOU: cut nao convergiu (BRepAlgoAPI_Cut)")
    r = cq.Shape.cast(c.Shape())
    if not r.isValid() or not r.Solids():
        raise SystemExit("FALHOU: cut devolveu solido invalido ou vazio (BRepCheck diria nao)")
    return r.clean()


def escala_z(sh, z0, sz):
    """Escala so o eixo Z em volta de z0 (transformacao AFIM, nao uniforme: X e Y ficam intactos, entao toda
    seccao transversal do funil continua geometricamente identica - e o que "manter proporcionalmente igual"
    quer dizer aqui). gp_Trsf nao serve: so aceita escala uniforme, que comeria o Ø da fenda junto."""
    m = gp_Mat()
    for i in (1, 2, 3):
        for j in (1, 2, 3):
            m.SetValue(i, j, sz if i == j == 3 else (1.0 if i == j else 0.0))
    t = gp_GTrsf(m, gp_XYZ(0.0, 0.0, z0 * (1.0 - sz)))
    r = cq.Shape.cast(BRepBuilderAPI_GTransform(sh.wrapped, t, True).Shape())
    if not r.isValid():
        raise SystemExit("FALHOU: a escala axial do funil produziu solido invalido")
    return r.clean()


def copia(sh):
    """copia topo-constante: translate() do cadquery muta o shape na mao"""
    from OCP.gp import gp_Trsf
    return cq.Shape.cast(BRepBuilderAPI_Transform(sh.wrapped, gp_Trsf(), True).Shape()).clean()


def estende(canal, base):
    """Prolonga o vazio 0,5 mm para fora das duas faces antes de cortar: com a cara do canal coincidente
    com a face do corpo o booleano pode devolver casca aberta. So para o corte - o canal exportado e o
    solido original, sem os tocos."""
    t = uniao(canal, cil(75.60, -0.5, 0.0))
    w, e = base['boca_saida'][0], base['boca_saida'][1]
    return uniao(t, cq.Solid.makeBox(w, e, 0.5, cq.Vector(-w / 2.0, -e / 2.0, base['zmax'])))


def seccao(void, z):
    r = _seccao(void, z)
    if r is None:
        return None
    b, area = r
    return dict(z=round(z, 3), largura=round(b.xmax - b.xmin, 4), abertura=round(b.ymax - b.ymin, 4), area=area)


def land_por_caras(void):
    """Inicio e fim do land paralelo, medidos nas CARAS do canal e nao em seccoes amostradas: as duas paredes
    planas a Y = +/- espessura/2 sao exatamente o trecho paralelo. Varredura com passo fixo perderia 0,25 mm
    em cada ponta e daria 8,25 num land de 8,500."""
    e = 0.75                                       # metade da espessura contratada de 1,50
    zs = []
    for f in void.Faces():
        if f.geomType() != "PLANE":
            continue
        try:
            nr = f.normalAt()
        except Exception:
            continue
        if abs(abs(nr.y) - 1.0) > 1e-6:
            continue
        bb = f.BoundingBox()
        if abs(abs(bb.ymin) - e) < 1e-3 and abs(abs(bb.ymax) - e) < 1e-3 and abs(bb.ymax - bb.ymin) < 1e-6:
            zs.append((round(bb.zmin, 3), round(bb.zmax, 3), round(abs(bb.ymin), 4)))
    if not zs:
        return None
    ys = sorted({z[2] for z in zs})
    esp = round(max(ys) - min(ys), 4) if len(ys) > 1 else round(2 * e, 4)   # 0,75 -> 1,5000 entre caras
    z0 = min(z[0] for z in zs)
    z1 = max(z[1] for z in zs)
    return dict(z_land=round(z0, 3), land=round(z1 - z0, 3), caras=len(zs), espessura=esp,
                faces=sorted(set(zs)))


def cono_do_chanfro(void):
    """O chanfro de saida, pelo cone real do STEP: (R de, R para, Z de, Z para). Serve para mostrar que
    1,50 x 45 graus sobreviveu intacto ao encurtamento."""
    for f in void.Faces():
        if f.geomType() not in ("CONICAL", "CONE"):        # cadquery devolve "CONE" para superficie conica
            continue
        bb = f.BoundingBox()
        try:
            ang = f._geomAdaptor().Cone().SemiAngle()
        except Exception:
            ang = None
        r = (bb.xmax - bb.xmin) / 2.0
        return dict(raio_max=round(r, 3), z=[round(bb.zmin, 2), round(bb.zmax, 2)],
                    abertura_graus=round(math.degrees(ang), 3) if ang is not None else None)
    return None


def perfil_do_canal(canal):
    """Mede no solido do canal: comprimento, land (pelas caras), area no meio do land, bocas, chanfro e volume."""
    zmin, zmax = canal.BoundingBox().zmin, canal.BoundingBox().zmax
    lp = land_por_caras(canal)
    if lp is None:
        raise SystemExit("FALHOU: nao achei as paredes planas do land no canal")
    no_land = seccao(canal, lp["z_land"] + min(2.00, lp["land"] / 3.0))
    ent, sai = seccao(canal, zmin + 0.01), seccao(canal, zmax - 0.01)
    ch = cono_do_chanfro(canal)
    return dict(comprimento=round(zmax - zmin, 3), zmin=round(zmin, 3), zmax=round(zmax, 3),
                z_land=lp["z_land"], land=lp["land"], caras_do_land=lp["caras"],
                espessura_entre_caras=lp["espessura"],
                area_no_land=no_land["area"] if no_land else None,
                largura_no_land=no_land["largura"] if no_land else None,
                abertura_no_land=no_land["abertura"] if no_land else None,
                chanfro=ch, boca_saida=[sai["largura"], sai["abertura"], sai["area"]] if sai else None,
                boca_entrada=max(ent["largura"], ent["abertura"]) if ent else None,
                area_entrada=ent["area"] if ent else None, volume=round(vol(canal), 1))


def corpo(diametros, zspans):
    b = None
    for dia, (z0, z1) in zip(diametros, zspans):
        c = cil(dia, z0, z1)
        b = c if b is None else uniao(b, c)
    return b


def mede(p, rotulo):
    sh = abre(p)
    inv = inventario(sh)
    _v, void = vazio_da_peca(sh, inv)
    est = estagios(inv)
    fend = mede_fenda(inv)
    per = perfil_do_canal(void) if void is not None else {}
    cx = inv["caixa"]
    return dict(rotulo=rotulo, arquivo=os.path.relpath(p, RAIZ), sha256=sha(p), bytes=os.path.getsize(p),
                solidos=inv["solidos"], cascas=inv["cascas_por_solido"], faces=inv["faces"],
                brep_valido=bool(inv["brep_valido"]),
                comprimento=round(cx["z"][1] - cx["z"][0], 3), dx=cx["dx"], dy=cx["dy"],
                volume_aco_mm3=round(vol(sh), 1), massa_kg=round(vol(sh) * ACO, 4),
                estagios_medidos=[dict(Ø=e[0], z=[e[1], e[2]]) for e in est], fenda=fend,
                canal=per, vazao_area_saida=per.get("boca_saida"))


def cobra(m, alvo_D, alvo_L, base, rotulo):
    """Cobranca dura, com o numero medido impresso. Falhou, para."""
    ds = [e["Ø"] for e in m["estagios_medidos"]]
    zs = [e["z"] for e in m["estagios_medidos"]]
    falhas = []
    if sorted(ds, reverse=True)[:3] != sorted(alvo_D, reverse=True):
        falhas.append("diametros medidos %s != %s" % (ds, alvo_D))
    if abs(m["comprimento"] - alvo_L) > 0.01:
        falhas.append("comprimento medido %.3f != %.2f" % (m["comprimento"], alvo_L))
    for nome, med, alvo in (("land", m["canal"].get("land"), base["land"]),
                            ("espessura da fenda entre caras", m["canal"].get("espessura_entre_caras"),
                             base["espessura_entre_caras"]),
                            ("area no land", m["canal"].get("area_no_land"), base["area_no_land"]),
                            ("largura no land", m["canal"].get("largura_no_land"), base["largura_no_land"]),
                            ("abertura no land", m["canal"].get("abertura_no_land"), base["abertura_no_land"]),
                            ("boca de saida", m["canal"].get("boca_saida"), base["boca_saida"])):
        if med is None or alvo is None:
            falhas.append("%s nao medido" % nome)
        elif isinstance(med, list) and any(abs(x - y) > 0.01 for x, y in zip(med, alvo)):
            falhas.append("%s %s != herdado %s" % (nome, med, alvo))
        elif not isinstance(med, list) and abs(med - alvo) > 0.01:
            falhas.append("%s medido %s != herdado %s" % (nome, n(med, 4), n(alvo, 4)))
    if m["solidos"] != 1 or m["cascas"] != [1]:
        falhas.append("peca unica esperada 1 solido/1 casca, medido %d/%s" % (m["solidos"], m["cascas"]))
    if not m["brep_valido"]:
        falhas.append("BRepCheck_Analyzer rejeitou o solido")
    print("    [%s] Ø %s | L %.2f | land %s | area %s | fenda %s x %s | faces %d | BRep %s"
          % (rotulo, ds, m["comprimento"], n(m["canal"].get("land") or 0, 3),
             n(m["canal"].get("area_no_land") or 0, 4),
             n(m["fenda"]["largura_mm"], 3), n(m["fenda"]["espessura_mm"], 3), m["faces"], m["brep_valido"]))
    if falhas:
        raise SystemExit("FALHOU %s:\n  - %s" % (rotulo, "\n  - ".join(falhas)))


def montagem(nome, die_shape, dz, med_die):
    """Cabecote completo + matriz sentada, SEM booleano (a montagem e para leitura e medicao, nao para imprimir:
    a soma dos volumens dos solidos prova que nada foi fundido nem cortado)."""
    cab = abre(CABECOTE)
    pedacos = []
    for so in (die_shape.Solids() or [die_shape]):
        s = copia(so)
        if abs(dz) > 1e-9:
            s = s.translate(cq.Vector(0.0, 0.0, dz))
        pedacos.append(s)
    comp = cq.Workplane("XY").newObject([cq.Compound.makeCompound([cab] + pedacos)])
    p = os.path.join(DIR_CAB, nome)
    cq.exporters.export(comp, p, cq.exporters.ExportTypes.STEP)
    relido = abre(p)
    interf = sum(vol(x.intersect(cab)) for x in pedacos)
    from verificar_interface_cabecote import Z_FACE_NARIZ
    furos = []
    for f in cab.Faces():
        if f.geomType() != "CYLINDER":
            continue
        try:
            ad = f._geomAdaptor()
            if abs(abs(ad.Cylinder().Axis().Direction().Z()) - 1.0) > 1e-6:
                continue
            r = ad.Cylinder().Radius()
        except Exception:
            continue
        bb = f.BoundingBox()
        furos.append((r, bb.zmin, bb.zmax))
    saida = round(med_die["comprimento"] + dz, 3)
    folgas = []
    for e in med_die["estagios_medidos"]:
        z0, z1 = e["z"]
        cand = []
        for r, a, b in furos:
            ov = min(b, z1) - max(a, z0)                      # trecho em que o furo e a matriz coexistem
            if ov > 0.5 and 2 * r - e["Ø"] > 0.05 and 2 * r < 140.0:
                cand.append((round((2 * r - e["Ø"]) / 2.0, 3), round(2 * r, 3), round(ov, 2), round(max(a, z0), 2),
                             round(min(b, z1), 2)))
        if not cand:
            folgas.append(dict(estagio_Ø=e["Ø"], z=[z0, z1], furo_Ø=None,
                               obs="nenhum furo do cabecote neste Z (protrusao para fora do corpo)"))
            continue
        c = min(cand)                                          # a folga que vale e a menor do trecho
        folgas.append(dict(estagio_Ø=e["Ø"], z=[z0, z1], furo_Ø=c[1], folga_radial=c[0],
                           trecho_congruente_mm=[c[3], c[4]], comprimento_do_estagio_no_furo_mm=c[2]))
    return dict(arquivo=os.path.relpath(p, RAIZ), sha256=sha(p), bytes=os.path.getsize(p),
                solidos=len(relido.Solids()), volume_somado_mm3=round(sum(x.Volume() for x in relido.Solids()), 1),
                deslocamento_aplicado_mm=round(dz, 3),
                saida_além_da_face_do_nariz_mm=round(saida - Z_FACE_NARIZ, 3),
                face_de_saida_no_Z=round(saida, 3), z_face_do_nariz=Z_FACE_NARIZ,
                interferencia_mm3=round(interf, 4), folgas_por_estagio=folgas)


def main():
    print("[1] abrindo o canal herdado do STEP aprovado (funil 1:1, nada recriado por estimativa)")
    canal = maior(abre(CANAL_MAE))
    base = perfil_do_canal(canal)
    print("    canal: L %.3f | land %.3f em Z %.2f | area %.4f | boca entrada Ø%.3f | saida %s | volume %.1f mm3"
          % (base["comprimento"], base["land"], base["z_land"], base["area_no_land"], base["boca_entrada"],
             base["boca_saida"], base["volume"]))
    if abs(base["land"] - 8.50) > 0.002 or abs(base["area_no_land"] - 112.0171) > 0.002:
        raise SystemExit("FALHOU: o canal mae nao bate com o contrato (land %.3f, area %.4f)"
                         % (base["land"], base["area_no_land"]))
    zl = base["z_land"]      # medido nas caras do canal, nao um numero datilografado
    cauda = base["comprimento"] - zl
    print("    plano do corte do canal em Z = %.2f (inicio do land medido); cauda a preservar = %.2f mm"
          % (zl, cauda))

    print("[2] v29 re-feita: corpo Ø94/89/79 nos mesmos Z, canal intacto")
    b29 = corpo(DIAMETROS, [(z0, z1) for z0, z1 in Z_DEGRAUS])
    d29 = corta(b29, estende(canal, base))
    os.makedirs(DIR_V29, exist_ok=True)
    p29 = os.path.join(DIR_V29, "MATRIZ_V29_PECA_UNICA.step")
    cq.exporters.export(cq.Workplane("XY").newObject([d29]), p29, cq.exporters.ExportTypes.STEP)
    m29 = mede(p29, "v29")
    cobra(m29, DIAMETROS, L_V29, base, "v29")
    print("    aco %s mm3 = %s kg | faces %d | solidos %d"
          % (n(m29["volume_aco_mm3"], 1), n(m29["massa_kg"], 4), m29["faces"], m29["solidos"]))

    print("[3] v30: funil comprimido, land + chanfro movidos rigidos")
    sz = (L_V30 - cauda) / zl
    print("    s = (%.2f - %.2f) / %.2f = %.6f" % (L_V30, cauda, zl, sz))
    funil = corta(canal, cil(300.0, zl, 500.0))
    cauda_sol = corta(canal, cil(300.0, -100.0, zl))
    cauda_sol = cauda_sol.translate(cq.Vector(0.0, 0.0, -(L_V29 - L_V30)))
    canal30 = uniao(escala_z(funil, 0.0, sz), cauda_sol)
    g30 = perfil_do_canal(canal30)
    print("    canal v30: L %.3f | land %.3f em Z %.2f | area %.4f | boca entrada Ø%.3f | saida %s | volume %.1f"
          % (g30["comprimento"], g30["land"], g30["z_land"], g30["area_no_land"], g30["boca_entrada"],
             g30["boca_saida"], g30["volume"]))
    b30 = corpo(DIAMETROS, [(0.00, 69.90), (69.90, 80.70), (80.70, L_V30)])
    d30 = corta(b30, estende(canal30, g30))
    os.makedirs(DIR_V30, exist_ok=True)
    p30 = os.path.join(DIR_V30, "MATRIZ_V30_PECA_UNICA.step")
    cq.exporters.export(cq.Workplane("XY").newObject([d30]), p30, cq.exporters.ExportTypes.STEP)
    cq.exporters.export(cq.Workplane("XY").newObject([canal30]),
                        os.path.join(DIR_V30, "MATRIZ_V30_CANAL_DE_FLUXO.step"),
                        cq.exporters.ExportTypes.STEP)
    m30 = mede(p30, "v30")
    cobra(m30, DIAMETROS, L_V30, base, "v30")
    print("    aco %s mm3 = %s kg (vs %s kg na v29) | faces %d"
          % (n(m30["volume_aco_mm3"], 1), n(m30["massa_kg"], 4), n(m29["massa_kg"], 4), m30["faces"]))

    print("[4] montagens no cabecote EX-030 completo (encosto face a face, dz do perfil medido)")
    dz = 0.0
    if os.path.exists(PERFIS):
        pf = json.load(open(PERFIS, encoding="utf-8"))
        e = next((x for x in pf["matrizes"] if x["chave"] == "jonatha_v27"), None)
        if e:
            dz = float(e["encostos"][e["encosto_usado"]]["deslocamento_aplicado_mm"])
    mo29 = montagem("Cabecote_EX-030_com_Matriz_Jonatha_v29.step", abre(p29), dz, m29)
    mo30 = montagem("Cabecote_EX-030_com_Matriz_Jonatha_v30.step", abre(p30), dz, m30)
    for nome, mo in (("v29", mo29), ("v30", mo30)):
        print("    %s: saida no Z %.2f | face do nariz %.2f | protrusao %+.2f mm | interferencia %.4f mm3"
              % (nome, mo["face_de_saida_no_Z"], mo["z_face_do_nariz"],
                 mo["saida_além_da_face_do_nariz_mm"], mo["interferencia_mm3"]))
        print("        folgas: %s" % json.dumps(mo["folgas_por_estagio"], ensure_ascii=False))
    if abs(mo30["saida_além_da_face_do_nariz_mm"]) > 0.01:
        raise SystemExit("FALHOU: a v30 nao ficou faceada ao nariz (protrusao %+.3f mm)"
                         % mo30["saida_além_da_face_do_nariz_mm"])
    if mo30["interferencia_mm3"] > 1e-6 or mo29["interferencia_mm3"] > 1e-6:
        raise SystemExit("FALHOU: a matriz encosta no cabecote (interferencia %.4f / %.4f mm3)"
                         % (mo29["interferencia_mm3"], mo30["interferencia_mm3"]))

    out = dict(decisao="revisoes de 2026-09-22 pedidas pelo dono", fonte_do_canal=os.path.relpath(CANAL_MAE, RAIZ),
               canal_herdado=base, z_corte_do_canal=round(zl, 3), cauda_preservada_mm=round(cauda, 3),
               escala_axial_do_funil=round(sz, 6), diametros_alterados_mm=DIAMETROS,
               tolerancia_das_cotas_alteradas=TOL, aco_novo=ACO_NOVO,
               v29=dict(medidas=m29, montagem=mo29), v30=dict(medidas=m30, montagem=mo30))
    json.dump(out, open(F_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    print("JSON ->", os.path.relpath(F_JSON, RAIZ))
    print("sha v29", m29["sha256"][:16], "| sha v30", m30["sha256"][:16])



if __name__ == "__main__":
    main()
