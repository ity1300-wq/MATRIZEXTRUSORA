"""Gera o STEP do CABECOTE EX-030 SEM a parte que conecta na extrusora (a junta com o flange).

Geometria: 100% do que foi medido no DWG 030-032 (`cabecote_ex030.json`) e do construtor solido que o
verificador de interface usa (`verificar_interface_cabecote.cabecote`). Nenhuma cota e digitada aqui.

"A parte que conecta na extrusora" e definida por medida, nao por gosto: e tudo que esta fora do raio
do corpo (r > 65,00 mm = 0130). Entrassem o chanfro 10 x 45 graus da transicao corpo->flange
        (de (d 42,00; r 65,02) a (d 52,00; r 75,02), medido nas duas vistas de secao do DXF), o flange
        0220 x 40 (d 52..92) com os
6x016,5 em C.C. 0180 nas fendas de 23,5 e o resalto 0203 x 3 (d 92..95). Os furos da junta estao a
r = 90 mm, todos fora de 0130 - a intersecao pelo cilindro do corpo leva os seis junto com o flange.

O M12 transversal medido a 72,02 mm da face do nariz NAO entra no modelo-padrao: no arquivo que chegou
ele existe so como par de circulos concentricos (010,50/012,00) com marca de centro sobre o eixo, sem
aresta de seccao correspondente em parte nenhuma, e a leitura exata (furo roscado transversal que abriria
na banda onde o collete aperta, ou furo coaxial no fundo do bolso) muda o que a peca faz. Usa-se
--com-m12 para ver o cenario transversal.

  python 04_Dados_SSOT_e_Scripts/gerar_cabecote_ex030.py [--com-m12] [--angulo-graus 90]

Saida (pasta 06_CAD_Cabecote_EX-030/STEP/, criada se nao existir):
        Cabecote_EX-030_desenhado.step    referencia, com a junta
        Cabecote_EX-030_sem_flange.step   o pedido
        com --com-m12 (ou --saida para outra pasta) os STEP ganham sufixo _M12 e vao para
        STEP/estudos/, assim como o relatorio (CABECOTE_EX-030_STEP_M12.md) e as medicoes
        (cabecote_step_M12.json): rodada de cenario nao escreve em documento oficial do repo
        04_Dados_SSOT_e_Scripts/cabecote_step.json                 (medicoes da operacao)
        03_Relatorios_e_Documentacao/CABECOTE_EX-030_STEP.md       (o que foi removido e o que prova)
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

from verificar_interface_cabecote import (cabecote, cil_z, CORPO, BORES, Z_FACE_NARIZ,  # noqa: E402
                                          FUROS_FLANGE, DIR_CAD)
from verificar_v28 import ENVELOPE, maior  # noqa: E402
from verificar_v28 import n  # noqa: E402

DADO = json.load(open(os.path.join(AQUI, "cabecote_ex030.json"), encoding="utf-8"))
# pasta dos desenhos STEP do cabecote: s66 entregue aqui; cenario de estudo (ex. --com-m12) vai
# para STEP/estudos/, que e fora do repo por .gitignore - cenario nao e decisao aprovada
DIR_CAB = os.path.join(RAIZ, "06_CAD_Cabecote_EX-030", "STEP")
DIR_ESTUDO = os.path.join(DIR_CAB, "estudos")
DIR_HIS = os.path.join(RAIZ, "02_CAD_Modelos_Historicos")   # lido, nunca escrito (regra 2)
DIR_OFF = os.path.join(RAIZ, "01_CAD_MatrizJonatha_Oficial")
PERFIS = os.path.join(AQUI, "perfis_matrizes_x_cabecote.json")
# as montagens que o usuario pediu: o cabecote com a matriz original e com a Gedeon sentadas
MONTAGENS = [("matriz_1_copo", "Matriz_Copo"), ("matriz_2_gedeon", "Matriz_Gedeon")]
DIR_DOC = os.path.join(RAIZ, "03_Relatorios_e_Documentacao")
def vol(sh):
    """Volume de Shape/Compound: soma os solidos (maior() pegaria so uma das metades)."""
    ss = sh.Solids()
    return sum(x.Volume() for x in ss) if ss else sh.Volume()


ACO = 7.85e-6                       # kg/mm3 (7,85 g/cm3) - a mesma densidade usada na matriz
RAIO_CORPO = CORPO[0][0]            # 65,00 mm: o raio do corpo 0130 medido
Z0, Z1 = min(z for _, z, _ in CORPO), max(z for _, _, z in CORPO)
RAIO_BOLSO = BORES[2][0]            # 47,50 mm: raio do bolso 095
RAIO_BANDA = ENVELOPE[0][2] / 2.0   # 46,50 mm: a banda 093 da matriz - o que NAO pode perder 1 mm3
M12 = DADO["furos_transversais_no_cabecote"]["medidos_no_dxf"][0]


def com_m12(forma, angulo_graus):
    """Cenario: furo liso 012 atravessando as duas paredes, no plano medido. So para ver."""
    z = Z_FACE_NARIZ - M12["x_da_face_do_nariz_mm"]
    a = math.radians(angulo_graus)
    d = cq.Vector(math.cos(a), math.sin(a), 0.0)
    L = 2.0 * (RAIO_CORPO + 2.0)
    return forma.cut(cq.Solid.makeCylinder(M12["Ø_passagem_mm"] / 2.0, L,
                                           cq.Vector(0, 0, z) - d * (L / 2.0), d))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--com-m12", action="store_true",
                    help="abre o 012 transversal no cenario do plano lido (o angulo nao esta cotado)")
    ap.add_argument("--angulo-graus", type=float, default=90.0)
    ap.add_argument("--saida", default=None,
                    help=f"padrao: {os.path.relpath(DIR_CAB, RAIZ)}/ (ou STEP/estudos/ com --com-m12)")
    ap.add_argument("--sem-relatorio", action="store_true")
    a = ap.parse_args()
    if a.saida is None:  # o cenario M12 nunca sobrescreve os STEP entregues
        a.saida = DIR_ESTUDO if a.com_m12 else DIR_CAB
    os.makedirs(a.saida, exist_ok=True)
    # regra da pasta: fora do STEP/ oficial NADA escreve em documento do repo - nem STEP, nem relatorio,
    # nem JSON de medicoes. Cenario (--com-m12, ou --saida apontando para outro lugar) fica em
    # STEP/estudos/, com sufixo no nome, e so ali
    oficial = os.path.abspath(a.saida) == os.path.abspath(DIR_CAB)
    sufixo = "" if oficial else "_M12"
    cam_json = (os.path.join(AQUI, "cabecote_step.json") if oficial
                else os.path.join(a.saida, "cabecote_step_M12.json"))

    cheio = cabecote(com_anel=False)
    novo = cheio.intersect(cil_z(RAIO_CORPO, Z0 - 1.0, Z1 + 1.0))
    if a.com_m12:
        novo = com_m12(novo, a.angulo_graus)

    # ---------------------------------------------------------------- medicoes
    removido = cheio.cut(novo)
    ate_a_matriz = vol(removido.intersect(cil_z(RAIO_BANDA + 0.001, Z0 - 1, Z1 + 1)))
    no_que_trabalha = ate_a_matriz
    na_parede_do_bolso = (vol(removido.intersect(cil_z(RAIO_BOLSO + 0.001, Z0 - 1, Z1 + 1)))
                          - ate_a_matriz)
    bf, bn = cheio.BoundingBox(), novo.BoundingBox()
    matriz = cq.importers.importStep(os.path.join(RAIZ, "01_CAD_MatrizJonatha_Oficial",
                                                  "MatrizJonatha_v28.step")).val()
    interf_cheio = vol(matriz.intersect(cheio))
    interf_novo = vol(matriz.intersect(novo))
    aneis = sorted({f"Ø{2 * r:.0f} (d {Z_FACE_NARIZ - z1:.2f}..{Z_FACE_NARIZ - z0:.2f})"
                    for r, z0, z1 in CORPO if r > RAIO_CORPO})

    med = {
        "peca": "EX-030 CABECOTE - variante sem a junta da extrusora",
        "operacao": f"intersecao pelo cilindro Ø{2 * RAIO_CORPO:.0f} do corpo (r = {n(RAIO_CORPO)} mm)",
        "anis_removidos": aneis,
        "m12_aberto": bool(a.com_m12), "angulo_m12_graus": a.angulo_graus if a.com_m12 else None,
        "volume_desenhado_mm3": round(cheio.Volume(), 3),
        "volume_sem_flange_mm3": round(novo.Volume(), 3),
        "volume_removido_mm3": round(removido.Volume(), 3),
        "massa_desenhada_kg": round(cheio.Volume() * ACO, 4),
        "massa_sem_flange_kg": round(novo.Volume() * ACO, 4),
        "massa_removida_kg": round(removido.Volume() * ACO, 4),
        "Ø_por_x_y_mm": [round(bn.xlen, 3), round(bn.ylen, 3)],
        "comprimento_axial_mm": round(bn.zlen, 3),
        "comprimento_antes_mm": round(bf.zlen, 3),
        "metal_removido_ate_a_banda_da_matriz_mm3": round(ate_a_matriz, 6),
        "metal_removido_na_parede_do_bolso_mm3": round(na_parede_do_bolso, 3),
        "interferencia_matriz_x_desenhado_mm3": round(interf_cheio, 6),
        "interferencia_matriz_x_sem_flange_mm3": round(interf_novo, 6),
        "furos_da_junta_fora_do_corpo": bool(FUROS_FLANGE[1] - FUROS_FLANGE[0] > RAIO_CORPO),
        "bolso_Ø_mm": 2 * RAIO_BOLSO,
        "bolso_comprimento_mm": round(BORES[2][2] - BORES[2][1], 3),
    }
    med["comprimento_preservado"] = abs(bn.zlen - bf.zlen) < 1e-6
    med["redondo"] = abs(bn.xlen - 2 * RAIO_CORPO) < 1e-6 and abs(bn.ylen - 2 * RAIO_CORPO) < 1e-6
    json.dump(med, open(cam_json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    p1 = os.path.join(a.saida, f"Cabecote_EX-030_desenhado{sufixo}.step")
    p2 = os.path.join(a.saida, f"Cabecote_EX-030_sem_flange{sufixo}.step")
    cq.exporters.export(cheio, p1)
    cq.exporters.export(novo, p2)

    # round-trip: o que foi escrito tem de reimportar com o mesmo volume, senao o entregavel nao vale
    rt = {}
    for nome, caminho, origem in (("desenhado", p1, cheio), ("sem_flange", p2, novo)):
        relido = cq.importers.importStep(caminho).val()
        rt[f"volume_reimportado_{nome}_mm3"] = round(vol(relido), 3)
        rt[f"desvio_round_trip_{nome}_mm3"] = round(vol(relido) - origem.Volume(), 6)
        rt[f"sólidos_no_arquivo_{nome}"] = len(relido.Solids()) or 1
    med.update(rt)
    json.dump(med, open(cam_json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    desvio_max = max(abs(rt[k]) for k in rt if k.startswith("desvio_round_trip"))
    print(f"desenhado  -> {p1}\n           {n(cheio.Volume(), 0)} mm3 | {n(cheio.Volume() * ACO, 3)} kg "
          f"| Ø{bf.xlen:.0f} x {n(bf.zlen)} mm de comprimento")
    print(f"SEM FLANGE -> {p2}\n           {n(novo.Volume(), 0)} mm3 | {n(novo.Volume() * ACO, 3)} kg "
          f"| Ø{bn.xlen:.2f} x {bn.ylen:.2f} x {n(bn.zlen)} mm | removido "
          f"{n(removido.Volume() * ACO, 3)} kg "
          f"({n(100 * removido.Volume() / cheio.Volume(), 1)} % do volume)")
    print(f"metal removido ate a banda da matriz (r <= {n(RAIO_BANDA, 2)} mm): {n(ate_a_matriz, 4)} mm3 | "
          f"na parede do bolso: {n(na_parede_do_bolso, 3)} mm3")
    print(f"interferencia com MatrizJonatha_v28.step: desenhado {n(interf_cheio, 4)} mm3 | "
          f"sem flange {n(interf_novo, 4)} mm3")
    print(f"round-trip dos STEP reimportados: desvio máximo {n(desvio_max, 6)} mm³ "
          f"({med['sólidos_no_arquivo_desenhado']} e {med['sólidos_no_arquivo_sem_flange']} sólido(s))")
    ok = (abs(no_que_trabalha) < 1e-6 and abs(interf_novo) < 1e-6 and med["comprimento_preservado"]
          and med["redondo"] and desvio_max < 1e-3)
    print("CHECAGENS:", "0 mm3 no que trabalha, redondo, comprimento igual, matriz passa, STEP "
          "reimporta - passou"
          if ok else "FALHOU - ver os numeros acima")

    # ------------------------------------------------- montagens: cabecote + matriz sentada, num STEP so
    # Composto de 2 solidos no MESMO referencial axial (Z = 0 no plano mais traseiro da pecas), SEM booleano:
    # e assim que o CAD mede folga e interferencia, e assim que o arquivo continua valido como montagem. As
    # matrizes sao lidas de 02_/01_ sem modificar (regra 2), unidas A U B quando a peca e bipartida - o mesmo
    # corpo que `medir_perfis_matrizes_x_cabecote.py` mede, para o STEP entregue e a medicao nao divergirem.
    med["montagens"] = {}
    falhas_m = ""
    if os.path.exists(PERFIS):
        pf = json.load(open(PERFIS, encoding="utf-8"))
        for chave, curto in MONTAGENS:
            e = next((x for x in pf["matrizes"] if x["chave"] == chave), None)
            if e is None:
                falhas_m = "chave %s ausente em perfis_matrizes_x_cabecote.json" % chave
                print("FALHOU:", falhas_m)
                continue
            paths = []
            for nome in e["arquivos_lidos"]:
                pt = next((os.path.join(d, nome) for d in (DIR_HIS, DIR_OFF)
                           if os.path.exists(os.path.join(d, nome))), None)
                if pt is None:
                    falhas_m = "nao acho o STEP da matriz %s" % nome
                    print("FALHOU:", falhas_m)
                    break
                paths.append(pt)
            else:
                wp = cq.importers.importStep(paths[0])
                for pt in paths[1:]:
                    wp = wp.union(cq.importers.importStep(pt))
                corpo = maior(wp.val())
                dz = e["encostos"][e["encosto_usado"]]["deslocamento_aplicado_mm"]
                if abs(dz) > 1e-9:
                    corpo = corpo.translate(cq.Vector(0.0, 0.0, dz))
                comp = cq.Workplane("XY").newObject([cq.Compound.makeCompound([cheio, corpo])])
                pm = os.path.join(a.saida, f"Cabecote_EX-030_com_{curto}{sufixo}.step")
                cq.exporters.export(comp, pm, cq.exporters.ExportTypes.STEP)
                relido = cq.importers.importStep(pm).val()
                vs = [x.Volume() for x in relido.Solids()] or [vol(relido)]
                saida = e["comprimento_medido_mm"] + dz
                med["montagens"][chave] = {
                    "arquivo": os.path.relpath(pm, RAIZ),
                    "arquivos_da_matriz": [os.path.relpath(x, RAIZ) for x in paths],
                    "encosto_usado": e["encosto_usado"], "deslocamento_aplicado_mm": round(dz, 3),
                    "solidos_no_arquivo": len(relido.Solids()),
                    "volume_somado_mm3": round(sum(vs), 3),
                    "desvio_round_trip_mm3": round(sum(vs) - (cheio.Volume() + corpo.Volume()), 6),
                    "interferencia_matriz_x_desenhado_mm3": round(vol(corpo.intersect(cheio)), 4),
                    "interferencia_matriz_x_sem_flange_mm3": round(vol(corpo.intersect(novo)), 4),
                    "face_de_saida_da_matriz_em_Z": round(saida, 3),
                    "protusao_adem_da_face_do_nariz_mm": round(saida - Z_FACE_NARIZ, 3),
                    "massa_somada_kg": round((cheio.Volume() + corpo.Volume()) * ACO, 4),
                }
                m = med["montagens"][chave]
                print(f"MONTAGEM {curto:13s} -> {os.path.relpath(pm, RAIZ)} | {m['solidos_no_arquivo']} solidos"
                      f" | interferencia com o cabecote {n(m['interferencia_matriz_x_desenhado_mm3'], 4)} mm3"
                      f" | saida da matriz em Z = {n(m['face_de_saida_da_matriz_em_Z'], 2)}"
                      f" (protrusao {n(m['protusao_adem_da_face_do_nariz_mm'], 2)} mm)")
                if m["solidos_no_arquivo"] != 2 or abs(m["desvio_round_trip_mm3"]) > 1e-3:
                    falhas_m = ("montagem %s nao reimporta como 2 solidos de volume fiel (solidos %d, desvio "
                                "%s mm3)" % (chave, m["solidos_no_arquivo"], m["desvio_round_trip_mm3"]))
                    print("FALHOU:", falhas_m)
                json.dump(med, open(cam_json, "w", encoding="utf-8"), indent=1)
    else:
        print("aviso: falta perfis_matrizes_x_cabecote.json - montagens nao geradas "
              "(rode medir_perfis_matrizes_x_cabecote.py --json)")

    if not a.sem_relatorio:
        escreve_relatorio(med, p1, p2)
    return 0 if ok else 1


def escreve_relatorio(med, p1, p2):
    linhas = [
        "# Cabeçote EX-030 em STEP — sem a parte que conecta na extrusora",
        "",
        "Os dois sólidos vêm do que foi **medido no DWG 030-032** (`cabecote_ex030.json`) e do mesmo",
        "construtor que o verificador de interface usa, com o booleano abaixo:",
        "",
        "``",
        "python 04_Dados_SSOT_e_Scripts/gerar_cabecote_ex030.py        # gera, mede e prova",
        "``",
        "",
        "| arquivo | o que é |",
        "| :--- | :--- |",
        f"| `{os.path.relpath(p2, RAIZ)}` | **o pedido**: corpo Ø{2 * RAIO_CORPO:.0f} × "
        f"{n(med['comprimento_axial_mm'])} mm com o nariz Ø80, o degrau Ø90 e o bolso "
        f"Ø{med['bolso_Ø_mm']:.0f} × {n(med['bolso_comprimento_mm'])} mm |",
        f"| `{os.path.relpath(p1, RAIZ)}` | o cabeçote como está no desenho (cubo + flange + resalto), "
        "para referência e para a subtração |",
        "",
        "## O cabeçote com cada matriz sentada (montagens entregues)",
        "",
        "Dois arquivos compostos - 2 sólidos no mesmo referencial axial (Z = 0 no plano mais traseiro), sem",
        "booleano, para que a folga e a interferência sejam medidas no CAD de quem recebe. As matrizes são",
        "lidas de `02_CAD_Modelos_Historicos/` / `01_CAD_MatrizJonatha_Oficial/` **sem modificar** (regra 2),",
        "unidas A ∪ B quando a peça é bipartida - o mesmo corpo que `medir_perfis_matrizes_x_cabecote.py`",
        "mede, para o STEP entregue e a medição não divergirem.",
        "",
        "| montagem | encosto usado | interferência com o cabeçote | saída da matriz em Z | protrusão |",
        "| :--- | :--- | ---: | ---: | ---: |",
        *[f"| `{m['arquivo']}` | `{m['encosto_usado']}` ({n(m['deslocamento_aplicado_mm'], 2)} mm) | "
          f"**{n(m['interferencia_matriz_x_desenhado_mm3'], 4)} mm³** | {n(m['face_de_saida_da_matriz_em_Z'], 2)} | "
          f"{n(m['protusao_adem_da_face_do_nariz_mm'], 2)} mm |"
          for m in med.get("montagens", {}).values()],
        "",
        "A diferença de sinal entre as duas linhas é o ponto que o usuário observou na máquina: a Copo "
        "termina",
        f"**{n(abs(list(med.get('montagens', {}).values())[0]['protusao_adem_da_face_do_nariz_mm']) if med.get('montagens') else 0, 2)} mm antes** da face do nariz (falta o nariz de 28,30 mm que a Gedeon tem), e a Gedeon "
        "desemboca",
        "fora dele. Os dois valores são comprimentos medidos nos STEP das próprias peças: "
        f"{', '.join(n(x['face_de_saida_da_matriz_em_Z'], 2) for x in med.get('montagens', {}).values())} mm.",
        "",
        "## O que foi removido, e como isso foi definido",
        "",
        "Remover = intersectar pelo cilindro Ø130 do corpo. A definição não é arbitrária: a junta",
        "cabeçote↔extrusora é exatamente o que está fora do corpo, medido em anéis:",
        "",
        *[f"* {x};" for x in med["anis_removidos"]],
        f"* os 6 furos Ø{n(FUROS_FLANGE[0] * 2)} em C.C. Ø{n(FUROS_FLANGE[1] * 2)} ficam a "
        f"{n(FUROS_FLANGE[1])} mm do eixo, **todos** fora de r = {n(RAIO_CORPO)} mm — o corte leva os seis "
        "junto com o flange, sem precisar de furo novo e sem tocar em nenhuma face de centragem.",
        "",
        "## O que a medição do sólido prova",
        "",
        f"* volume {n(med['volume_desenhado_mm3'], 0)} → {n(med['volume_sem_flange_mm3'], 0)} mm³; massa "
        f"**{n(med['massa_desenhada_kg'], 3)} → {n(med['massa_sem_flange_kg'], 3)} kg**, foram "
        f"**{n(med['massa_removida_kg'], 3)} kg** de aço a menos "
        f"({n(100 * med['volume_removido_mm3'] / med['volume_desenhado_mm3'], 1)} % do volume) — a conta "
        "do material e do tempo de usinagem muda de verdade;",
        f"* **{n(med['metal_removido_ate_a_banda_da_matriz_mm3'], 4)} mm³** de metal removido até "
        f"r = {n(RAIO_BANDA, 2)} mm, que é a banda Ø93 em que a matriz é apertada: o bolso Ø95, o degrau "
        "Ø90→Ø95 (a face que reage os 29,8 kN de empuxo) e o nariz Ø80 continuam os do desenho, "
        "milímetro por milímetro;",
        f"* comprimento axial **{n(med['comprimento_axial_mm'])} mm**, igual ao do desenho "
        f"({n(med['comprimento_antes_mm'])} mm), e a bounding box ficou "
        f"Ø{n(med['Ø_por_x_y_mm'][0])} × Ø{n(med['Ø_por_x_y_mm'][1])}: corpo redondo, sem nada sobrando "
        "da junta;",
        f"* na parede do bolso (entre a banda Ø93 e o furo Ø95): "
        f"{n(med['metal_removido_na_parede_do_bolso_mm3'], 3)} mm³ removidos pelo corte — o Ø12 do M12, se "
        f"ele for transversal, abre 1,00 mm além da banda da matriz, na parede onde o collete EX-031 encosta, "
        f"e não na matriz;",
        f"* interferência com `MatrizJonatha_v28.step`: **{n(med['interferencia_matriz_x_sem_flange_mm3'], 4)} mm³** "
        f"(no cabeçote com flange: {n(med['interferencia_matriz_x_desenhado_mm3'], 4)} mm³) — a matriz entra, "
        "senta no degrau e sai da mesma maneira na variante sem flange.",
        "",
        "## O que o corte NÃO resolve (lê antes de mandar usinar)",
        "",
        "1. **Sem o flange, a peça não se fixa em lugar nenhum.** Os 6 × M12 eram a única interface mecânica "
        "com a extrusora, e é o aperto deles que segura o conjunto contra o empuxo do fundido. Este STEP "
        "serve para ver montagem, volume, massa e interface com a matriz. Para fabricar, a junta precisa de "
        "substituto (flange de outro diâmetro, grampos no corpo, ou apoio direto na boca da extrusora "
        "usando os centragens que já existem).",
        f"2. **O M12 transversal ficou fora do modelo.** Medido: par de círculos concêntricos "
        f"Ø{n(M12['Ø_broca_mm'])}/Ø{n(M12['Ø_passagem_mm'])} com marca de centro sobre o eixo a "
        f"{n(M12['x_da_face_do_nariz_mm'])} mm da face do nariz (= "
        f"{n(M12['x_da_face_do_flange_mm'])} mm da face do flange — é daí que sai o '20' cotado, e é por isso "
        "que aquele '20' não é a protrusão da matriz). No arquivo que chegou ele não tem aresta de seção "
        "correspondente em parte nenhuma, então a natureza exata (furo roscado transversal, abrindo na banda "
        "onde o collete aperta, ou furo coaxial no fundo do bolso para o pushador EX-032) não é "
        f"determinável. Modelar `--com-m12` abre o Ø12 atravessando as duas paredes no ângulo que você "
        f"especifar (padrão {n(med['angulo_m12_graus'] or 90, 0)}°) para você ver o cenário — e nada neste "
        "STEP depende dele.",
        "3. Nada aqui mexe na matriz: `MatrizJonatha.step` continua o v27.0 aprovado e a v28.1 continua "
        "proposta (decisão D4).",
        "",
        "*Gerado por `gerar_cabecote_ex030.py`; medições em `04_Dados_SSOT_e_Scripts/cabecote_step.json`.*",
    ]
    # escreve_relatorio e chamada tambem pelas rodadas de cenario, que nao tem `a` em escopo:
    # o destino se deduz da pasta para onde os proprios STEP foram escritos
    oficial = os.path.abspath(os.path.dirname(p2)) == os.path.abspath(DIR_CAB)
    p = (os.path.join(DIR_DOC, "CABECOTE_EX-030_STEP.md") if oficial
         else os.path.join(os.path.dirname(p2), "CABECOTE_EX-030_STEP_M12.md"))
    open(p, "w", encoding="utf-8").write("\n".join(linhas) + "\n")
    print("relatório ->", p)


if __name__ == "__main__":
    raise SystemExit(main())
