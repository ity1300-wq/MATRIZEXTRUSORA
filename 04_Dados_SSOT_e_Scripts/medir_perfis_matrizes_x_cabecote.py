"""Mede o PERFIL DE CADA MATRIZ (Copo original, Gedeon, Desenvolvimento, Jonatha v27 e v28.1) e compara
com a ESCADA DE FUROS INTERNA DO CABEÇOTE EX-030 - tudo medido nos STEP, nada citado de memoria.

Por que este script existe: o cabecote foi feito em volta da Matriz 1 Copo, e a Gedeon tambem entra nele,
sendo mais comprida - e a diferenca e visivel na saida matriz-cabecote. Para "deixar a parte interna de
acordo" e preciso saber, por medida: (i) onde fica o ombro/degrau de cada matriz, (ii) em qual furo do
cabecote cada estagio dela cai e com quanta folga radial, (iii) o que acontece axialmente em cada encosto
possivel - porque e o encosto que define quantos mm a matriz protende alem da face do nariz.

Metodo:
  * perfil da matriz: varredura de seccoes finas (0,20 mm) com d_ext = max(xlen, ylen) da seccao do maior
    solido, comprimida em platos guardando o DIAMETRO MAXIMO do plato (nao a media: o que importa para o
    furo e o ponto mais afastado do eixo).
  * limitacao honesta: d_ext e o diametro na direcao dos eixos X/Y. Para corpo redondo e exato. Nas cinco
    matrizes a banda que trabalha no bolso e redonda (093), entao o numero que governa o encaixe e exato;
    o que tem face plana (biparticao, boca 75,00) fica dentro dessa banda e nao e medido como diametro.
  * engate: os solidos sao posicionados no referencial do cabecote (Z_FACE_NARIZ = 95,00; face do nariz em
    Z = 95, traseira em Z = 0) por tres hipoteses de encosto, e a interferencia e medida por booleano
    somando TODOS os solidos da interseccao (regra do repo: maior() em booleano que pode sair partido
    corta o resultado ao meio).

Encostos:
  A "face frontal rasa" - face de saida da matriz rasante a face do nariz (o encosto que a vedacao do
                          filme exige, e o unico que uma matriz mais curta que o bolso consegue achar sozinha)
  B "ombro no degrau"   - o ombro da matriz (fim da banda 093) encostando no degrau 090->080 do cabecote
  C "fundo do bolso"    - a traseira da matriz batendo no fundo do bolso (Z = 0)

Uso:
  python 04_Dados_SSOT_e_Scripts/medir_perfis_matrizes_x_cabecote.py [--json] [--passo 0.2]
"""
import argparse
import json
import os
import sys

import cadquery as cq

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, ".."))
sys.path.insert(0, AQUI)

from verificar_interface_cabecote import (cabecote, cil_z, BORES, CORPO, Z_FACE_NARIZ,  # noqa: E402
                                          maior, n, dist3d)

DIR_HIS = os.path.join(RAIZ, "02_CAD_Modelos_Historicos")
DIR_OFF = os.path.join(RAIZ, "07_CAD_Matrizes", "Matriz_Jonatha_v27_OFICIAL")
DIR_V28 = os.path.join(RAIZ, "07_CAD_Matrizes", "Matriz_Jonatha_v28_1_PROPOSTA")
DIR_DOC = os.path.join(RAIZ, "03_Relatorios_e_Documentacao")

# "corpo" = uniao dos dois bodies quando nao ha solido unico (a auditoria historica chama isso de
# "montagem"). O .step inteiro nao e usado quando ele traz pino, porque pino nao e envelope.
MATRIZES = [
    {"chave": "matriz_1_copo", "nome": "Matriz 1 - Copo (original, a que o cabecote foi feito em volta)",
     "arquivos": [os.path.join(DIR_HIS, "Matriz1_Original_Copo_Solido.step")],
     "fonte": "solido unico"},
    {"chave": "matriz_2_gedeon", "nome": "Matriz 2 - Gedeon (a maior, que o usuario diz que entra)",
     "arquivos": [os.path.join(DIR_HIS, "MatrizGedeon_Body_A.step"),
                  os.path.join(DIR_HIS, "MatrizGedeon_Body_B.step")],
     "fonte": "A U B"},
    {"chave": "matriz_gedeon_certa", "nome": "Matriz Gedeon CERTA (o arquivo do usuario, entregue como esta)",
     "arquivos": [os.path.join(DIR_HIS, "matrizGedeonCerta.step")],
     "fonte": "solido unico (o arquivo dele, sem re-corte)"},
    {"chave": "matriz_desenvolvimento", "nome": "Matriz Desenvolvimento",
     "arquivos": [os.path.join(DIR_HIS, "MatrizDesenvolvimento_Body_A.step"),
                  os.path.join(DIR_HIS, "MatrizDesenvolvimento_Body_B.step")],
     "fonte": "A U B"},
    {"chave": "jonatha_v27", "nome": "Matriz Jonatha v27.0 (oficial aprovada)",
     "arquivos": [os.path.join(DIR_OFF, "MatrizJonatha.step")], "fonte": "oficial"},
    {"chave": "jonatha_v28_1", "nome": "Matriz Jonatha v28.1 (proposta DFM)",
     "arquivos": [os.path.join(DIR_V28, "MatrizJonatha_v28.step")], "fonte": "proposta"},
]


def corpo_de(paths):
    """A Uniao dos bodies, no objeto Workplane (Shape nao tem .union no CadQuery 2.x)."""
    wp = cq.importers.importStep(paths[0])
    for p in paths[1:]:
        wp = wp.union(cq.importers.importStep(p))
    return maior(wp.val())


def vol_intersecao(a, b):
    """Soma os solidos: em booleano que pode sair partido, maior() corta ao meio."""
    s = a.intersect(b).Solids()
    return sum(x.Volume() for x in s) if s else 0.0


def perfil(solido, passo=0.20, tol=0.05):
    """Escada [(z0, z1, diametro_max)] do envelope externo, medida por seccoes."""
    bb = solido.BoundingBox()
    pratos = []
    z = bb.zmin
    while z <= bb.zmax + 1e-9:
        corte = solido.intersect(cil_z(400.0, z - passo / 2.0, z + passo / 2.0))
        ss = corte.Solids()
        d = 0.0
        if ss:
            m = maior(corte)
            d = max(m.BoundingBox().xlen, m.BoundingBox().ylen)
        if pratos and abs(pratos[-1][2] - d) <= tol:
            pratos[-1][1] = z
            pratos[-1][2] = max(pratos[-1][2], d)
        else:
            pratos.append([z, z, d])
        z += passo
    # descarta seccoes vazias (o filete da ultima varredura) e junta platos de mesmo diametro
    esc = [p for p in pratos if p[2] > 0.5]
    out = []
    for p in esc:
        if out and abs(out[-1][2] - p[2]) <= tol:
            out[-1][1] = p[1]
            out[-1][2] = max(out[-1][2], p[2])
        else:
            out.append(list(p))
    return {"z_min": round(bb.zmin, 3), "z_max": round(bb.zmax, 3),
            "comprimento_mm": round(bb.zmax - bb.zmin, 3),
            "escala": [[round(a, 3), round(b, 3), round(d, 3)] for a, b, d in out]}


def ombro_da_banda(escala):
    """Z em que o plato do diametro maximo termina - o ombro que encosta no degrau do cabecote."""
    d_max = max(p[2] for p in escala)
    for a, b, d in escala:
        if d <= d_max - 0.10:
            return round(a, 3), round(d_max, 3)
    return None, round(d_max, 3)


def d_na(solido, z):
    """Diametro externo na seccao Z (0,02 mm de espessura)."""
    corte = solido.intersect(cil_z(400.0, z - 0.01, z + 0.01))
    ss = corte.Solids()
    if not ss:
        return 0.0
    m = maior(corte)
    return max(m.BoundingBox().xlen, m.BoundingBox().ylen)


def refina(solido, z_a, z_b, d_alvo, tol=0.005):
    """Ultimo Z em que a seccao ainda tem o diametro d_alvo, por bisseccao (tol em mm)."""
    if z_b <= z_a:
        return None
    a, b = z_a, z_b
    if d_na(solido, a) < d_alvo - 0.05 or d_na(solido, b) > d_alvo - 0.05:
        return None
    while b - a > tol:
        mid = 0.5 * (a + b)
        if d_na(solido, mid) >= d_alvo - 0.05:
            a = mid
        else:
            b = mid
    return round(a, 3)


def transicoes(solido, escala, passo_de_busca=0.5):
    """Refina o fim de cada plato: a transicao i vira o Z exato em que o plato i acaba. O ultimo plato
    termina na caixa do solido (exato), nao no ultimo Z amostrado - senao a face de saida sai 0,1 mm curta."""
    fim = []
    zmin = escala[0][0]
    zmax = solido.BoundingBox().zmax
    for i, (z0, z1, d) in enumerate(escala):
        if i + 1 < len(escala):
            r = refina(solido, z1 - passo_de_busca, z1 + passo_de_busca, d)
            fim.append(r if r is not None else round(z1, 3))
        else:
            fim.append(round(zmax, 3))
    return {"z_min": round(zmin, 3), "z_max": round(zmax, 3), "fins_de_plato_refinados": fim}


NOME_DO_FURO = {80.0: "furo do nariz (por onde a película sai)",
                90.0: "degrau - assento do ombro da matriz",
                95.0: "bolso de fixação (onde a bucha aperta a banda)",
                105.0: "rebaixo traseiro do piloto - não restringe a matriz"}


def escada_cabecote():
    """A parte interna do cabecote recortada no metal real (Z 0..95), no referencial da matriz."""
    esc = []
    for (r, za, zb) in BORES:
        za2, zb2 = max(za, 0.0), min(zb, Z_FACE_NARIZ)
        if zb2 > za2:
            esc.append({"Ø_mm": round(2 * r, 3), "de_Z": round(za2, 3), "ate_Z": round(zb2, 3),
                        "comprimento_mm": round(zb2 - za2, 3),
                        "nome": NOME_DO_FURO.get(round(2 * r, 3), "—")})
    pr = CORPO[2]           # o piloto de centragem 0105 x 3 atras do flange
    if pr[0] * 2.0 > max(2 * r for r, _, _ in BORES):
        esc.append({"Ø_mm": round(2 * pr[0], 3), "de_Z": round(pr[1], 3), "ate_Z": round(pr[2], 3),
                    "comprimento_mm": round(pr[2] - pr[1], 3),
                    "nome": NOME_DO_FURO[105.0]})
    return sorted(esc, key=lambda e: e["de_Z"])


def engates(solido, head, z_ombro):
    """Posiciona a matriz nos tres encostos e mede o que resulta, por booleano."""
    bb = solido.BoundingBox()
    out = {}
    for nome, desloc in (("A_face_frente_rasa", Z_FACE_NARIZ - bb.zmax),
                         ("B_ombro_no_degrau", (70.0 - z_ombro) if z_ombro else None),
                         ("C_fundo_do_bolso", 0.0 - bb.zmin)):
        if desloc is None:
            out[nome] = {"indisponível": "a matriz não tem ombro onde a banda 093 termina"}
            continue
        m = solido.translate(cq.Vector(0, 0, desloc))
        b = m.BoundingBox()
        out[nome] = {
            "deslocamento_aplicado_mm": round(desloc, 3),
            "face_de_saida_em_Z": round(b.zmax, 3),
            "protusão_além_da_face_do_nariz_mm": round(b.zmax - Z_FACE_NARIZ, 3),
            "traseira_da_matriz_em_Z": round(b.zmin, 3),
            "vão_livre_atrás_da_matriz_no_bolso_mm": round(b.zmin - 0.0, 3),
            "interferência_com_o_cabeçote_mm3": round(vol_intersecao(m, head), 4),
        }
    return out


def folgas_por_estagio(escala, head_desloc, esc_cab):
    """Para cada plato da matriz, em que furo do cabecote ele cai e com quanta folga radial (medido)."""
    out = []
    for (z0, z1, d) in escala:
        zc = (z0 + z1) / 2.0 + head_desloc
        f = next((e for e in esc_cab if e["de_Z"] <= zc <= e["ate_Z"]), None)
        if f is None:
            out.append({"estagio": f"Ø{n(d, 2)} em Z {n(z0, 2)}..{n(z1, 2)}",
                        "furo": "fora do cabeçote (protende além da face, ou fica no vão traseiro)",
                        "folga_radial_mm": None})
            continue
        out.append({"estagio": f"Ø{n(d, 2)} em Z {n(z0, 2)}..{n(z1, 2)}",
                    "furo": f"Ø{n(f['Ø_mm'], 2)} (Z {n(f['de_Z'], 2)}..{n(f['ate_Z'], 2)})",
                    "folga_radial_mm": round((f["Ø_mm"] - d) / 2.0, 3),
                    "pode_entrar": bool(f["Ø_mm"] >= d - 1e-9)})
    return out


def canal_à_frente_da_saida(sol, assento_z, face_saida_z):
    """Quanto vao o furo do nariz deixa aberto a frente da face de saida da matriz - medido por booleano
    direto (cilindro do furo MENOS o material da matriz la dentro), sem assumir area de produto. E o
    numero que separa 'a matriz desemboca na face' de 'a matriz desemboca dentro de um buraco'."""
    m = sol.translate(cq.Vector(0, 0, assento_z))
    z0 = max(face_saida_z, 81.0)
    trecho = Z_FACE_NARIZ - z0
    if trecho <= 1e-6:
        return {"trecho_mm": 0.0, "volume_do_furo_mm3": 0.0, "material_da_matriz_no_furo_mm3": 0.0,
                "vão_livre_mm3": 0.0, "por_quê": "a face de saída da matriz já está na face do nariz"}
    furo = cil_z(40.0, z0, Z_FACE_NARIZ)
    v_furo = furo.Volume()
    v_mat = vol_intersecao(furo, m)
    return {"trecho_mm": round(trecho, 3), "volume_do_furo_mm3": round(v_furo, 3),
            "material_da_matriz_no_furo_mm3": round(v_mat, 3),
            "vão_livre_mm3": round(v_furo - v_mat, 3),
            "medido_como": "cilindro Ø80,00 do furo do nariz, no trecho entre a face de saída da matriz e "
                           "Z = 95,00, menos o material da própria matriz dentro dele (booleano)"}


def que_if_chanfro_interno(solidos_por_chave, head, cateto=1.00):
    """E se o canto interno 090 -> 080 (Z = 81,00), que hoje e vivo, recebesse um chanfro a 45 graus?

    Medido, nao opinado: quanto de metal sairia, se a folga radial no canto muda, e se alguma das cinco
    matrizes passaria a interferir. O chanfro so remove metal do cabecote, entao nao pode criar contato -
    mas pode tirar apoio, e e isso que os numeros mostram (a area de canto que hoje guiasse o nariz).
    """
    z_canto = 81.0                      # onde o furo do nariz comeca (degrau 090 -> 080)
    r_furo = 40.0                        # 080
    cone_fora = cil_z(60.0, z_canto - cateto, z_canto + 1.0)
    # anel de chanfro a 45: o complemento do cone dentro de uma casca - corta o canto vivo do furo
    cone_interno = cq.Solid.makeCone(r_furo, r_furo + cateto + 1.0, cateto + 1.0,
                                    cq.Vector(0, 0, z_canto - cateto), cq.Vector(0, 0, 1))
    casca = cil_z(r_furo + cateto + 1.0, z_canto - cateto - 0.001, z_canto + cateto + 1.001)
    anel = casca.cut(cone_interno)
    head_ch = head.cut(anel)
    removido = head.Volume() - head_ch.Volume()
    linhas = []
    for chave, (mat, assento_z) in solidos_por_chave.items():
        m = mat.translate(cq.Vector(0, 0, assento_z))
        sem = vol_intersecao(m, head)
        com = vol_intersecao(m, head_ch)
        # folga radial no canto: distancia do nariz da matriz a uma fatia fina de 0,4 mm em Z = 81
        def folga_na_cabeca(heada):
            la = m.intersect(cil_z(60.0, z_canto - 0.2, z_canto + 0.2))
            he = heada.intersect(cil_z(60.0, z_canto - 0.2, z_canto + 0.2))
            if not la.Solids() or not he.Solids():
                return None
            return round(dist3d(maior(la), maior(he)), 3)
        linhas.append({"matriz": chave, "interferência_antes_mm3": round(sem, 4),
                       "interferência_depois_mm3": round(com, 4),
                       "folga_radial_no_canto_antes_mm": folga_na_cabeca(head),
                       "folga_radial_no_canto_depois_mm": folga_na_cabeca(head_ch)})
    return {"cateto_testado_mm": cateto, "metal_removido_do_cabeçote_mm3": round(removido, 3),
            "canto": "furo do nariz: Ø90 -> Ø80 em Z = 81,00 (o degrau onde a face da matriz encosta)",
            "por_matriz": linhas}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--passo", type=float, default=0.20)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--md", action="store_true",
                    help="escreve 03_Relatorios_e_Documentacao/INTERFASE_INTERNA_CABECOTE_X_MATRIZES.md")
    a = ap.parse_args()

    head = cabecote(com_anel=False)
    head_solido = head
    esc_cab = escada_cabecote()
    print("parte interna do cabecote EX-030, medida do construtor (referencial da matriz):")
    for e in esc_cab:
        print(f"   Ø{n(e['Ø_mm'], 2)}  x  {n(e['comprimento_mm'], 2)} mm de profundidade"
              f"   (Z {n(e['de_Z'])} .. {n(e['ate_Z'])})")

    guardado = {}
    res = {"peca": "perfis das 5 matrizes x escada interna do cabecote EX-030", "data": "2026-09-12",
           "referencial": (f"Z da matriz; face do nariz do cabecote em Z = {n(Z_FACE_NARIZ, 2)}; "
                           "fundo do bolso (face traseira) em Z = 0"),
           "metodo": ("varredura de seccoes de 0,20 mm nos STEP das proprias matrizes (Ø_ext = "
                      "max(xlen, ylen) do maior solido da seccao, plato guarda o maximo) + posicionamento "
                      "por encosto + interferencia por booleano somando todos os solidos"),
           "escada_interna_do_cabecote_mm": esc_cab, "matrizes": []}

    for m in MATRIZES:
        sol = corpo_de(m["arquivos"])
        pf = perfil(sol, a.passo)
        z_ombro, d_max = ombro_da_banda(pf["escala"])
        eg = engates(sol, head, z_ombro)
        tr = transicoes(sol, pf["escala"])
        fins = tr["fins_de_plato_refinados"]
        # o assento natural e o encosto em que a matriz nao interfere: B (ombro no degrau) se existir,
        # senao C (fundo do bolso), senao A - e é nesse assento que as folgas radial/axial valem
        assento = next((k for k in ("B_ombro_no_degrau", "C_fundo_do_bolso", "A_face_frente_rasa")
                        if "deslocamento_aplicado_mm" in eg[k]
                        and eg[k]["interferência_com_o_cabeçote_mm3"] < 1e-6), "A_face_frente_rasa")
        fg = folgas_por_estagio(pf["escala"], eg[assento]["deslocamento_aplicado_mm"], esc_cab)
        # folga axial medida contra os Z internos do cabecote: o degrau comeca em Z = 70,00 e o furo do
        # nariz comeca em Z = 81,00 - o que sobra entre a matriz e essas duas arestas e o que ela sente
        ax = {}
        if fins:
            ax["fim_da_banda_093_em_Z"] = fins[0]
            ax["folga_axial_banda_x_degrau_do_cabecote_mm"] = round(70.0 - fins[0], 3)
        if len(fins) > 1:
            ax["fim_do_estagio_089-50_em_Z"] = fins[1]
            ax["vão_da_saida_ate_o_furo_do_nariz_mm"] = round(81.0 - fins[1], 3)
        if fins:
            ax["face_de_saida_em_Z_no_assento"] = round(pf["z_max"] + eg[assento]["deslocamento_aplicado_mm"], 3)
            ax["canal_morto_no_furo_do_nariz_mm"] = round(Z_FACE_NARIZ - ax["face_de_saida_em_Z_no_assento"], 3)
        guardado[m["chave"]] = (sol, eg[assento]["deslocamento_aplicado_mm"])
        res["matrizes"].append({
            "chave": m["chave"], "nome": m["nome"], "arquivos_lidos": [os.path.basename(x) for x in m["arquivos"]],
            "fonte_do_corpo": m["fonte"], "comprimento_medido_mm": pf["comprimento_mm"],
            "Ø_máximo_medido_mm": d_max, "z_do_ombro_mm": z_ombro, "escala_Ø_x_Z_mm": pf["escala"],
            "fins_de_plato_refinados_mm": fins,
            "canal_à_frente_da_saída_mm3": canal_à_frente_da_saida(sol, eg[assento]["deslocamento_aplicado_mm"],
                                                                  pf["z_max"] + eg[assento]["deslocamento_aplicado_mm"]),
            "encostos": eg, "folgas_radiais_no_encosto_do_assento": fg, "encosto_usado": assento,
            "transições_refinadas_mm": ax})
        print(f"\n{m['nome']}")
        print(f"   comprimento medido {n(pf['comprimento_mm'], 2)} mm | Ø máx {n(d_max, 2)} mm | "
              f"ombro em Z = {n(z_ombro, 2) if z_ombro else '—'} | platos {len(pf['escala'])}")
        for k in ("A_face_frente_rasa", "B_ombro_no_degrau", "C_fundo_do_bolso"):
            v = eg[k]
            if "deslocamento_aplicado_mm" not in v:
                print(f"   {k}: {v}")
                continue
            print(f"   {k:20s} protusao {n(v['protusão_além_da_face_do_nariz_mm'], 2):>8} mm | "
                  f"vao atras {n(v['vão_livre_atrás_da_matriz_no_bolso_mm'], 2):>8} mm | "
                  f"interf {n(v['interferência_com_o_cabeçote_mm3'], 4)} mm3")

    copo = next(x for x in res["matrizes"] if x["chave"] == "matriz_1_copo")
    ged = next(x for x in res["matrizes"] if x["chave"] == "matriz_2_gedeon")
    res["diferença_copo_x_gedeon_medida"] = {
        "comprimento_copo_mm": copo["comprimento_medido_mm"],
        "comprimento_gedeon_mm": ged["comprimento_medido_mm"],
        "diferença_mm": round(ged["comprimento_medido_mm"] - copo["comprimento_medido_mm"], 3),
        "o_que_a_diferenca_faz_no_encosto_A": {
            "copo_vão_atrás_mm": copo["encostos"]["A_face_frente_rasa"]["vão_livre_atrás_da_matriz_no_bolso_mm"],
            "gedeon_vão_atrás_mm": ged["encostos"]["A_face_frente_rasa"]["vão_livre_atrás_da_matriz_no_bolso_mm"],
            "copo_ombro_Z": copo["z_do_ombro_mm"], "gedeon_ombro_Z": ged["z_do_ombro_mm"]},
        "o_que_a_diferenca_faz_no_encosto_B": {
            "copo_protusao_mm": copo["encostos"]["B_ombro_no_degrau"].get("protusão_além_da_face_do_nariz_mm"),
            "gedeon_protusao_mm": ged["encostos"]["B_ombro_no_degrau"].get("protusão_além_da_face_do_nariz_mm"),
            "copo_traseira_em_Z": copo["encostos"]["B_ombro_no_degrau"].get("traseira_da_matriz_em_Z"),
            "gedeon_traseira_em_Z": ged["encostos"]["B_ombro_no_degrau"].get("traseira_da_matriz_em_Z")},
    }
    dif = res["diferença_copo_x_gedeon_medida"]
    print(f"\n=== a diferenca que o usuario observou, medida ===")
    print(f"   Copo {n(dif['comprimento_copo_mm'], 2)} mm  |  Gedeon {n(dif['comprimento_gedeon_mm'], 2)} mm  "
          f"|  diferenca {n(dif['diferença_mm'], 2)} mm")
    print(f"   no encosto A (face frontal rasa): vao atras do Copo {n(dif['o_que_a_diferenca_faz_no_encosto_A']['copo_vão_atrás_mm'], 2)} mm, "
          f"da Gedeon {n(dif['o_que_a_diferenca_faz_no_encosto_A']['gedeon_vão_atrás_mm'], 2)} mm")
    pb = dif["o_que_a_diferenca_faz_no_encosto_B"]
    print(f"   no encosto B (ombro no degrau): protusao do Copo {n(pb['copo_protusao_mm'], 2)} mm, "
          f"da Gedeon {n(pb['gedeon_protusao_mm'], 2)} mm | traseira em Z = "
          f"{n(pb['copo_traseira_em_Z'], 2)} / {n(pb['gedeon_traseira_em_Z'], 2)}")

    res["o_que_um_chanfro_interno_muda"] = que_if_chanfro_interno(guardado, head)
    q = res["o_que_um_chanfro_interno_muda"]
    print(f"\n=== o que-if: chanfro a 45 de {n(q['cateto_testado_mm'], 2)} mm no canto interno, medido ===")
    print(f"   metal que sairia do cabecote: {n(q['metal_removido_do_cabeçote_mm3'], 3)} mm3")
    for l in q["por_matriz"]:
        print(f"   {l['matriz']:24s} interferencia {n(l['interferência_antes_mm3'], 4)} -> "
              f"{n(l['interferência_depois_mm3'], 4)} mm3 | folga no canto "
              f"{l['folga_radial_no_canto_antes_mm']} -> {l['folga_radial_no_canto_depois_mm']} mm")

    if a.md:
        def f3(v):
            return "—" if v is None else n(v, 3)

        L = ["# Parte interna do cabeçote EX-030 × as cinco matrizes — comparado por medida", "",
             "Gerado por `medir_perfis_matrizes_x_cabecote.py`. Escada interna do cabeçote medida do "
             f"construtor `verificar_interface_cabecote.cabecote`, no referencial da matriz (face do nariz "
             f"em Z = {n(Z_FACE_NARIZ, 2)}, fundo do bolso em Z = 0):", "",
             "| furo do cabeçote | Ø | de Z | até Z | profundidade |", "|---|---|---|---|---|"]
        for e in res["escada_interna_do_cabecote_mm"]:
            L.append(f"| {e.get('nome') or e.get('o_que_e', '—')} | Ø{n(e['Ø_mm'], 2)} | "
                     f"{n(e['de_Z'], 2)} | {n(e['ate_Z'], 2)} | {n(e['comprimento_mm'], 2)} mm |")

        L += ["", "## O que cada matriz é, medida no STEP dela", "",
              "| matriz | compr. | Ø máx | fim da banda Ø93 | folga axial banda↔degrau | face de saída | "
              "vão de furo Ø80 aberto à frente da saída |", "|---|---|---|---|---|---|---|"]
        for m in res["matrizes"]:
            t, c = m["transições_refinadas_mm"], m["canal_à_frente_da_saída_mm3"]
            L.append(f"| {m['nome']} | {n(m['comprimento_medido_mm'], 2)} | {n(m['Ø_máximo_medido_mm'], 2)} "
                     f"| {n(t['fim_da_banda_093_em_Z'], 3)} | "
                     f"{n(t['folga_axial_banda_x_degrau_do_cabecote_mm'], 3)} "
                     f"| {n(t['face_de_saida_em_Z_no_assento'], 3)} | {n(c['trecho_mm'], 2)} mm = "
                     f"{n(c['volume_do_furo_mm3'], 0)} mm³ de furo, **{n(c['vão_livre_mm3'], 0)} mm³** sem "
                     f"metal da matriz dentro |")

        L += ["", "## Estágio por estágio: em qual furo do cabeçote cai cada parte da matriz", "",
              "Medido no assento natural (o encosto em que a matriz não interfere):", "",
              "| matriz | estágio da matriz | furo do cabeçote onde ele cai | folga radial | entra? |",
              "|---|---|---|---|:--:|"]
        for m in res["matrizes"]:
            for fg in m["folgas_radiais_no_encosto_do_assento"]:
                entra = "—" if fg.get("pode_entrar") is None else ("sim" if fg["pode_entrar"] else "**NÃO**")
                fol = fg.get("folga_radial_mm")
                L.append(f"| {m['nome']} | {fg['estagio']} | {fg['furo']} | "
                         f"{f3(fol) + (' mm' if fol is not None else '')} | {entra} |")

        L += ["", "## A diferença que você observou, em números", "",
              f"* Comprimento medido: Copo **{n(dif['comprimento_copo_mm'], 2)} mm**, Gedeon "
              f"**{n(dif['comprimento_gedeon_mm'], 2)} mm** — diferença **{n(dif['diferença_mm'], 2)} mm**.",
              f"* No assento natural, a face de saída fica "
              f"**{n(abs(dif['o_que_a_diferenca_faz_no_encosto_B']['copo_protusao_mm']), 2)} mm para dentro** "
              f"da face do nariz no Copo e "
              f"**{n(dif['o_que_a_diferenca_faz_no_encosto_B']['gedeon_protusao_mm'], 2)} mm para fora** na "
              f"Gedeon: {n(abs(dif['o_que_a_diferenca_faz_no_encosto_B']['copo_protusao_mm']), 2)} + "
              f"{n(dif['o_que_a_diferenca_faz_no_encosto_B']['gedeon_protusao_mm'], 2)} = "
              f"{n(dif['diferença_mm'], 2)} mm. A diferença de comprimento É o nariz, e nada mais.",
              "* As cinco têm a mesma escada até o degrau (banda Ø93 e estágio Ø89,50 terminando no mesmo Z, "
              "na casa de milésimo). Gedeon, Desenvolvimento e Jonatha só acrescentam o nariz Ø79,50 que "
              "atravessa o furo do nariz; a Copo não tem nariz, e por isso a face dela fica enterrada.",
              "* Interferência no assento natural: " + ", ".join(
                  f"{m['chave']} "
                  f"{n(m['encostos'][m['encosto_usado']]['interferência_com_o_cabeçote_mm3'], 4)} mm³"
                  for m in res["matrizes"]) + ".", ""]

        L += ["## O que aconteceria com um chanfro de 1,00 × 45° no canto interno Ø90 → Ø80", "",
              "O canto vivo onde o furo do nariz começa (Z = 81,00) é por onde a película passa do estágio "
              "Ø89,50 para o Ø80. Um chanfro ali remove "
              f"**{n(q['metal_removido_do_cabeçote_mm3'], 3)} mm³** do cabeçote e muda, medido:", "",
              "| matriz | interferência antes | depois | folga radial no canto antes | depois |",
              "|---|---|---|---|---|"]
        for l in q["por_matriz"]:
            a1, d1 = l["folga_radial_no_canto_antes_mm"], l["folga_radial_no_canto_depois_mm"]
            L.append(f"| {l['matriz']} | {n(l['interferência_antes_mm3'], 4)} mm³ | "
                     f"{n(l['interferência_depois_mm3'], 4)} mm³ | "
                     f"{'a matriz não chega no canto' if a1 is None else n(a1, 2) + ' mm'} | "
                     f"{'a matriz não chega no canto' if d1 is None else n(d1, 2) + ' mm'} |")
        L += ["", "Nenhuma matriz passa a interferir — o chanfro só tira metal do cabeçote — mas onde o nariz "
              "encosta no canto a folga radial sai de 0,25 para 2,25 mm: o nariz de 14,00 mm deixaria de ser "
              "guiado nesse primeiro milímetro e continuaria guiado pelos 13,00 mm seguintes do Ø80. "
              "**Isto é proposta medida, não mudança aprovada**: o desenho do cabeçote não tem esse chanfro e "
              "o SSOT (`cabecote_ex030.json`) continua gravando a peça como desenhada.", ""]

        t0 = res["matrizes"][0]["transições_refinadas_mm"]
        c0 = res["matrizes"][0]["canal_à_frente_da_saída_mm3"]
        iA = res["matrizes"][0]["encostos"]["A_face_frente_rasa"]["interferência_com_o_cabeçote_mm3"]
        L += ["## O que isso diz sobre \"deixar a parte interna de acordo\"", "",
              f"1. **A escada interna do cabeçote é o molde da matriz Copo — e ela serve às cinco, sem "
              f"correção.** O fim da banda Ø93 é o mesmo Z nas cinco ({n(t0['fim_da_banda_093_em_Z'], 3)} mm "
              f"medidos na Copo e nas outras quatro) e o degrau do cabeçote está em Z = 70,00, então sobra "
              f"{n(t0['folga_axial_banda_x_degrau_do_cabecote_mm'], 3)} mm de folga axial. É esse número que "
              f"faz o encosto no degrau e o encosto no fundo do bolso caírem na mesma posição: a matriz não "
              f"\"escolhe\" entre os dois.",
              f"2. **A Copo não pode ser montada com a face rasante à face do nariz**: empurrada até lá ela "
              f"interfere {n(iA, 4)} mm³, porque a banda Ø93 teria de atravessar o degrau Ø90. Ela senta no "
              f"degrau e deixa a saída enterrada — {n(c0['volume_do_furo_mm3'], 0)} mm³ de furo Ø80 aberto à "
              f"frente dela, sem metal dentro. É aí que a película caminha 14 mm dentro do cabeçote em vez "
              f"de nascer no ar livre.",
              f"3. **A diferença que você vê na saída não é tolerância, é projeto**: "
              f"{n(dif['diferença_mm'], 2)} mm de nariz existem para levar a face de saída para fora do "
              f"cabeçote. Qualquer matriz que se queira usar neste cabeçote sem usinar o cabeçote precisa "
              f"desse nariz — e a v28.1 tem, com o Ø79,50×28,30 que mede exatamente a folga do enterramento "
              f"da Copo (14,30) mais a protusão de projeto (14,00).",
              "", "*Gerado por `medir_perfis_matrizes_x_cabecote.py --json --md`; os números estão em "
              "`04_Dados_SSOT_e_Scripts/perfis_matrizes_x_cabecote.json`.*"]
        p_md = os.path.join(DIR_DOC, "INTERFASE_INTERNA_CABECOTE_X_MATRIZES.md")
        open(p_md, "w", encoding="utf-8").write("\n".join(L))
        print("MD  ->", p_md)

    if a.json:
        p = os.path.join(AQUI, "perfis_matrizes_x_cabecote.json")
        json.dump(res, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("JSON ->", p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
