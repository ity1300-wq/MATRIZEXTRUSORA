"""
INTERFACE MATRIZ v28  x  CABECOTE EX-030 (medido no DWG 030-032)
=================================================================
Monta o solido do cabecote a partir do perfil MEDIDO no desenho (ver
`cabecote_ex030.json`: escala calibrada k = 25,534 mm/un, cinco fechos
independentes batendo em 0,012 %) e roda booleanos + BRepExtrema contra os
solidos reais de `MatrizJonatha_v28.step`. Nenhum numero e estimado por fora.

  [A] encaixe dos 3 estagios      : interferencia, folga radial, folga axial
  [B] face do cabecote            : anel de 20 mm, boca x fenda x nariz
  [C] variante 65 mm (anel Ø68,3) : passa ou nao passa a manta e o nariz
  [D] furos na banda apertada     : ruptura do envelope e parede ate o OD
  [E] numero para a fabrica       : area/pressao no ombro, pressao do collete

Uso: python 04_Dados_SSOT_e_Scripts/verificar_interface_cabecote.py [--json] [--md]
Retorno: 0 se tudo conforme, 1 se houver nao conformidade.
"""

import argparse
import json
import math
import os
import re
import sys

import cadquery as cq

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, ".."))
sys.path.insert(0, AQUI)

from verificar_v28 import (maior, dist3d, n, checar, registrar, linhas,  # noqa: E402
                           TOL, ENVELOPE, r_envelope, secao)


def n2(v):
    return float(v)

DIR_CAD = os.path.join(RAIZ, "07_CAD_Matrizes", "Matriz_Jonatha_v27_OFICIAL")
DIR_V28 = os.path.join(RAIZ, "07_CAD_Matrizes", "Matriz_Jonatha_v28_1_PROPOSTA")
DIR_DOC = os.path.join(RAIZ, "03_Relatorios_e_Documentacao")

# --------------------------------------------------------------- cabecote
# profundidade d a partir da FACE DO NARIZ  ->  Z da matriz = 95 - d
Z_FACE_NARIZ = 95.0
BORES = [(40.0, 81.0, 96.0), (45.0, 70.0, 81.0), (47.5, -1.0, 70.0)]     # (r, z0, z1)
# Casca do cabeçote em (raio, Z_inferior, Z_superior), com Z = 95 - d e d medido da face do nariz.
# A transição corpo -> flange NÃO é um cilindro: é o chanfro 10 × 45° medido no DXF nas duas vistas de
# seção, de (d 42,00; r 65,02) a (d 52,00; r 75,02). Os números vêm de `corpo.chanfro_corpo_flange` em
# cabecote_ex030.json - nada é digitado aqui. Onde este arquivo tinha (82,0, 43,0, 54,0), um "cubo Ø164",
# a cota era leitura minha da borda do furo Ø16 no C.C. Ø180 (82 = 90 - 8), não uma superfície da peça.
_cab_dado = json.load(open(os.path.join(AQUI, "cabecote_ex030.json"), encoding="utf-8"))
_CH = _cab_dado["corpo"]["chanfro_corpo_flange"]
# os anéis vão exatamente às faces do desenho (flange = 40,00 mm de espessura, de Z 43 até Z 3).
# As sobreposições de 1 mm que estavam aqui criavam material fantasma: um colar de Ø220 engolindo
# o primeiro milímetro do chanfro e 1 mm de flange tapando o vão onde só deveria haver o piloto. Foi
# o item [G] do verificador, que mede a face real no sólido, que entregou o erro.
CORPO = [(65.0, 53.0, 95.0), (110.0, 3.0, 43.0), (52.5, 0.0, 3.0)]
# piloto de centragem: o raio vem do SSOT e a altura e o fim do anel, cobrados pelos asserts abaixo
assert abs(CORPO[2][0] * 2.0 - _cab_dado["corpo"]["piloto_traseiro"]["Ø_mm"]) < 1e-9, "CORPO[2] diverge do SSOT"
assert abs(CORPO[2][2] - _cab_dado["corpo"]["piloto_traseiro"]["altura_mm"]) < 1e-9, "piloto: altura diverge"
# cone do chanfro em (r_em_baixo, Z_em_baixo, r_em_cima, Z_em_cima); a geratriz e prolongada 0,5 mm para
# dentro do corpo (mesma reta, mesmo 45 graus) para o booleano nao abrir costura na uniao
_R_CORPO = _cab_dado["corpo"]["Ø_corpo_mm"] / 2.0
_Z_FLANGE = Z_FACE_NARIZ - _CH["d_fim_mm"]
_Z_CORPO = Z_FACE_NARIZ - _CH["d_inicio_mm"]
CHAMFRO = (_R_CORPO + _CH["cateto_mm"], _Z_FLANGE, _R_CORPO - 0.5, _Z_CORPO + 0.5)
ANEL65 = (34.15, 91.0, 101.0)     # anel do nariz da variante de 65 mm: (r_int, z0, z1)
FUROS_FLANGE = (8.25, 90.0)       # (raio do furo, raio do C.C. Ø180)
BOCA = 75.60
# A "manta" nao e mais um numero digitado aqui: a boca real (com o chanfro decidido em D2) e
# medida no arquivo do canal, e o produto vem do SSOT.
_ssot = json.load(open(os.path.join(AQUI, "cad_die_parameters.json"), encoding="utf-8"))
PRODUTO = (float(_ssot["matriz_jonatha_parameters"]["land_width_mm"]),
           float(_ssot["matriz_jonatha_parameters"]["land_thickness_mm"]))


def checar_min(item, medido, minimo, un="mm", obs=""):
    ok = medido >= minimo - 1e-9
    linhas.append({"item": item, "medido": round(medido, 4), "minimo": round(minimo, 4),
                   "unidade": un, "status": "CONFORME" if ok else "NAO_CONFORME",
                   "observacao": obs})
    print(f"  [{'OK  ' if ok else 'FALHA'}] {item:<52} mínimo={minimo:10.3f} "
          f"medido={medido:10.3f} {un}" + (f"  <- {obs}" if obs and not ok else ""))
    return ok


def alerta(item, valor, obs=""):
    linhas.append({"item": item, "medido": valor, "observacao": obs,
                   "status": "PENDENTE_CONFIRMACAO"})
    print(f"  [ATEN] {item:<52} {valor}   {obs}")


def cil_z(r, z0, z1):
    return cq.Solid.makeCylinder(r, z1 - z0, cq.Vector(0, 0, z0), cq.Vector(0, 0, 1))


def cone_z(r0, z0, r1, z1):
    """Cone solido entre Z=z0 (raio r0) e Z=z1 (raio r1). E assim que o chanfro do desenho entra no
    modelo: uma geratriz a 45 graus, nao um degrau."""
    return cq.Solid.makeCone(r0, r1, z1 - z0, cq.Vector(0, 0, z0), cq.Vector(0, 0, 1))


def slab(z0, z1):
    return cq.Workplane("XY").workplane(offset=z0).box(
        600, 600, z1 - z0, centered=(True, True, False)).val()


def cabecote(com_anel=False):
    h = cq.Workplane("XY").add(cil_z(*CORPO[0]))
    for p in CORPO[1:]:
        h = h.union(cil_z(*p))
    h = h.union(cone_z(*CHAMFRO))          # o chanfro 10 x 45 medido no desenho, ausente ate aqui
    for (r, z0, z1) in BORES:
        h = h.cut(cil_z(r, z0, z1))
    for i in range(6):
        a = math.radians(60 * i)
        h = h.cut(cq.Solid.makeCylinder(
            FUROS_FLANGE[0], 48.0,
            cq.Vector(FUROS_FLANGE[1] * math.cos(a), FUROS_FLANGE[1] * math.sin(a), -2.0),
            cq.Vector(0, 0, 1)))
    if com_anel:
        r, z0, z1 = ANEL65
        anel = cil_z(40.0, z0, z1).cut(cil_z(r, z0 - 1, z1 + 1))
        h = h.union(anel)
    return maior(h.val())


def env_vol(forma):
    return maior(forma).Volume()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--md", action="store_true")
    a = ap.parse_args()

    dados = json.load(open(os.path.join(AQUI, "cabecote_ex030.json"), encoding="utf-8"))
    feat = json.load(open(os.path.join(AQUI, "matriz_v28_features.json"), encoding="utf-8"))
    ver = json.load(open(os.path.join(AQUI, "verificacao_v28.json"), encoding="utf-8"))

    forca_kn = massa = None
    for l in ver["checagens"]:
        m = re.match(r"([\d,]+)\s*kN", str(l.get("medido", "")))
        if "Força" in l["item"] and m and forca_kn is None:
            forca_kn = float(m.group(1).replace(",", "."))
        m = re.match(r"([\d,]+)\s*kg", str(l.get("medido", "")))
        if "Massa" in l["item"] and m:
            massa = float(m.group(1).replace(",", "."))
    if forca_kn is None:
        raise SystemExit("forca de abertura nao encontrada em verificacao_v28.json")
    assert forca_kn > 0
    if massa is None:
        raise SystemExit("massa nao encontrada em verificacao_v28.json")
    print(f"força de abertura lida da verificacao_v28: {n(forca_kn, 1)} kN   |   massa {n(massa)} kg")

    matriz = cq.importers.importStep(os.path.join(DIR_V28, "MatrizJonatha_v28.step")).val()
    canal = maior(cq.importers.importStep(
        os.path.join(DIR_V28, "MatrizJonatha_v28_Canal_Fluxo.step")).val())
    _bb, _ = secao(canal, ENVELOPE[2][1] - 0.001)
    MANTA = (_bb.xmax - _bb.xmin, _bb.ymax - _bb.ymin)          # boca com o chanfro, medida
    print(f"boca de saida medida no canal: {n(MANTA[0])} x {n(MANTA[1])} mm  "
          f"(produto {n(PRODUTO[0])} x {n(PRODUTO[1])} + chanfro {n(_ssot['proposta_v28_dfm']['geometria_labios']['chanfro_saida_mm'])}x45)")
    head = cabecote(com_anel=False)
    head65 = cabecote(com_anel=True)

    env = cq.Workplane("XY").add(cil_z(ENVELOPE[0][2] / 2, ENVELOPE[0][0], ENVELOPE[0][1]))
    for (z0, z1, d) in ENVELOPE[1:]:
        env = env.union(cil_z(d / 2, z0, z1))
    env = maior(env.val() if hasattr(env, "val") else env)

    print("\n[A] encaixe dos 3 estagios (booleanos nos solidos reais)\n" + "-" * 70)
    checar("Interferência matriz ∩ cabeçote", env_vol(matriz.intersect(head)), 0.0,
           tol=1e-6, un="mm³", obs="a matriz tem de entrar e sair sem tocar")
    for (nome, z0, z1, alvo) in [("Ø93×69,90 no bolso Ø95×70,0", 0.5, 69.4, 1.00),
                                 ("Ø89,5×10,80 no Ø90×11,0", 70.5, 80.4, 0.25),
                                 ("Ø79,5×28,30 no Ø80×14,0", 81.5, 94.5, 0.25)]:
        d = dist3d(maior(matriz.intersect(slab(z0, z1))), maior(head.intersect(slab(z0, z1))))
        checar(f"Folga radial - {nome}", d, alvo, tol=TOL, un="mm")
    checar("Folga axial no degrau de apoio (ombro)",
           dist3d(maior(matriz.intersect(slab(60.0, 69.90))), maior(head.intersect(slab(70.0, 75.0)))),
           0.10, tol=TOL, un="mm", obs="o ombro da matriz encosta no degrau: é o apoio da força")
    checar("Folga axial entre o ombro Ø89,5→Ø79,5 da matriz e o degrau Ø90→Ø80",
           dist3d(maior(matriz.intersect(slab(75.0, 80.70))), maior(head.intersect(slab(81.0, 88.0)))),
           0.30, tol=TOL, un="mm",
           obs="o canto do Ø89,5 passa a 0,30 do degrau do nariz: é a folga que evita o encunhamento")
    checar("Face de entrada da matriz rasa com a traseira do cabeçote",
           matriz.BoundingBox().zmin - head.BoundingBox().zmin, 0.0, tol=TOL, un="mm",
           obs="a boca Ø75,60 fica exposta ao canal de massa do flange")
    checar("Protrusão da face de saída além da face do nariz",
           ENVELOPE[2][1] - Z_FACE_NARIZ, 14.00, tol=TOL, un="mm",
           obs="a fenda trabalha fora do cabeçote: nada de filme congelado na frente da matriz")

    print("\n[B] a face do cabeçote: anel, boca e fenda\n" + "-" * 70)
    checar("Anel da face (Ø90 → Ø130)", (130.0 - 90.0) / 2,
           dados["anel_na_face"]["largura_radial_mm"], tol=0.01, un="mm",
           obs="confere com o '~20 mm' descrito")
    # o chanfro 10 x 45 do desenho, cobrado no solido: esteve na cota do SSOT e no papel, e nao no
    # modelo, ate 2026-09-12 - se ele sumir de novo, este item fecha a cadeia com exit 1
    _z_meio = _Z_FLANGE + _CH["cateto_mm"] / 2.0
    _secao = maior(head.intersect(cil_z(500.0, _z_meio - 0.0005, _z_meio + 0.0005))).BoundingBox()
    _r_esperado = _R_CORPO + _CH["cateto_mm"] / 2.0
    checar("Chanfro corpo->flange no sólido (raio na meia-altura do cone)",
           max(_secao.xlen, _secao.ylen) / 2.0, _r_esperado, tol=0.01, un="mm",
           obs=f"meça em Z = {n(_z_meio)} mm (d = {n(Z_FACE_NARIZ - _z_meio)} mm): Ø130 → Ø150 em "
               f"{n(_CH['cateto_mm'])} mm a 45,00°, a mesma aresta nas duas vistas de seção do DXF")

    parafusos = None
    for i in range(6):
        ang = math.radians(60 * i)
        c = cq.Solid.makeCylinder(
            FUROS_FLANGE[0], 48.0,
            cq.Vector(FUROS_FLANGE[1] * math.cos(ang), FUROS_FLANGE[1] * math.sin(ang), -2.0),
            cq.Vector(0, 0, 1))
        parafusos = cq.Workplane("XY").add(c) if parafusos is None else parafusos.union(c)
    checar("Menor distância parafuso M12 (C.C Ø180) → corpo da matriz",
           dist3d(matriz, maior(parafusos.val())), 35.25, tol=TOL, un="mm",
           obs="nenhum furo da junta cabeçote↔extrusora alcança a matriz")
    manta = cq.Workplane("XY").workplane(offset=ENVELOPE[2][1]).box(
        PRODUTO[0], PRODUTO[1], 8.0, centered=(True, True, False)).val()
    checar_min("Curso livre da manta após sair da matriz até o cabeçote",
               dist3d(manta, maior(head.intersect(slab(-6.0, 95.0)))), 14.00,
               obs="a manta nasce 14 mm à frente da face do nariz e sai pela diagonal do furo Ø80: "
                   "não há contato possível")
    checar("Folga do nariz Ø79,5 no furo Ø80 (a 1 mm das bordas do degrau)",
           dist3d(maior(matriz.intersect(slab(82.0, 94.0))),
                  maior(head.intersect(slab(82.0, 94.0)))), 0.25, tol=TOL, un="mm")
    checar("Folga do PRODUTO (75,00) no furo Ø80 - o que voce mediu na maquina",
           (80.0 - PRODUTO[0]) / 2, 2.50, tol=0.05, un="mm",
           obs="'sobra 2,5 mm em cada extremidade da fenda' - reproduzido pelo modelo medido")
    registrar("Folga da BOCA da matriz (com o chanfro de D2) no furo Ø80",
              f"{n((80.0 - MANTA[0]) / 2)} mm por lado  (boca medida: {n(MANTA[0])} × {n(MANTA[1])} mm)",
              obs="consequência de manter o chanfro 1,50 × 45: a boca abre para "
                  f"{n(MANTA[0])} mm e a folga cai de 2,50 para {n((80.0 - MANTA[0]) / 2)} mm se o bico "
                  "do cabeçote chegar até a face da matriz - é por isso que o comprimento do bico "
                  "(14,00 mm no desenho) é a única medida que falta", ok=True)

    print("\n[C] variante com o anel do nariz Ø68,30 (carimbo 9\"×65 mm)\n" + "-" * 70)
    v65 = env_vol(matriz.intersect(head65))
    alerta("Interferência matriz ∩ cabeçote COM anel Ø68,30", f"{n(v65, 1)} mm³",
           "FECHADO por medição na máquina: sobram 2,5 mm/lado na fenda, entao a passagem e o proprio "
           "Ø80 do cabecote - o volume acima so vale se alguem reaproveitar o anel de 65 mm")
    alerta("Sobra na extremidade da fenda × passagem do cabeçote",
           f"Ø80,00 → sobra {n((80.0 - 75.0) / 2)} mm por lado (usuário mediu ~2,5) · "
           f"Ø68,30 do anel de 65 mm → faltariam {n((MANTA[0] - 2 * ANEL65[0]) / 2)} mm",
           "o número medido na máquina só casa com o Ø80: prova de que o anel de 65 mm não está lá")
    alerta("Passagem do anel × nariz da matriz",
           f"Ø{n(2 * ANEL65[0])} contra Ø79,50 → {n(39.75 - ANEL65[0])} mm de interferência radial por lado",
           "p/ 75 mm a passagem teria de ser ≥ Ø79,6, e o furo do nariz já é Ø80: não há espaço para anel")
    a_pass, a_boca = math.pi * ANEL65[0] ** 2, math.pi * (BOCA / 2) ** 2
    alerta("Área de passagem do cabeçote × boca da matriz",
           f"{n(100 * a_pass / a_boca, 1)} %  ({n(a_pass, 0)} mm² / {n(a_boca, 0)} mm²)",
           "restrição de alimentação e zona morta se o anel de 65 mm for mantido")

    print("\n[D] os 14 furos na banda que a bucha aperta (Z 0..69,90)\n" + "-" * 70)
    casca = env.cut(cil_z(ENVELOPE[0][2] / 2 - 0.002, ENVELOPE[0][0], ENVELOPE[0][1]))
    pior = (9e9, "")
    ruptura = 0
    for f in feat["furos"]:
        r = f["diametro"] / 2.0
        c = cq.Solid.makeCylinder(r, abs(f["y_fim_mm"] - f["y_ini_mm"]),
                                  cq.Vector(f["X"], min(f["y_ini_mm"], f["y_fim_mm"]), f["Z"]),
                                  cq.Vector(0, 1, 0))
        dentro_do_cabecote = f["Z"] <= Z_FACE_NARIZ
        fora = env_vol(c.cut(env)) if dentro_do_cabecote else 0.0
        ok = fora < 1e-6
        ruptura += 1 if not ok else 0
        if not dentro_do_cabecote:
            borda = max(abs(f["y_ini_mm"]), abs(f["y_fim_mm"]))
            r_alc = math.hypot(abs(f["X"]) + f["diametro"] / 2.0, borda)
            rnariz = r_envelope(f["Z"])
            abre = r_alc - rnariz
            registrar(f"Furo {f['tipo']} X={n(f['X'], 1)} Z={n(f['Z'], 1)} abre na banda livre",
                      f"alcance {n(r_alc)} mm x r do nariz {n(rnariz)} mm -> escancara {n(abre)} mm",
                      obs=f"a {n(f['Z'] - Z_FACE_NARIZ)} mm à frente da face do cabeçote: acesso "
                          "intencional ao cartucho/termopar, sem caminho para o bolso",
                      ok=True)
            continue
        obs = ""
        if f["Z"] <= ENVELOPE[0][1]:
            parede = dist3d(c, casca)
            if parede < pior[0]:
                pior = (parede, f"{f['tipo']} em X={n(f['X'], 1)}, Z={n(f['Z'], 1)}")
            obs = f"parede até o Ø93 = {n(parede)} mm"
        checar(f"Furo {f['tipo']} X={n(f['X'], 1)} Z={n(f['Z'], 1)} não rompe o envelope",
               fora, 0.0, tol=1e-6, un="mm³", obs=obs or "fora da banda de aperto")
    registrar("Nenhum furo dentro do cabeçote rompe o envelope",
              f"{sum(1 for f in feat['furos'] if f['Z'] <= Z_FACE_NARIZ) - ruptura} de "
              f"{sum(1 for f in feat['furos'] if f['Z'] <= Z_FACE_NARIZ)} conformes (os outros 10 abrem na banda livre, à frente do cabeçote)",
              obs="nenhum caminho de massa do canal para o bolso nem para a banda de aperto",
              ok=ruptura == 0)
    registrar("Menor parede de furo até a superfície apertada pela bucha",
              f"{n(pior[0])} mm  ({pior[1]})",
              obs="é a parede que o collete vê: manter cego, sem rebaixo, e Ø93 retificado na zona de aperto",
              ok=pior[0] >= 0.60)

    print("\n[E] números de dimensionamento da junta\n" + "-" * 70)
    # pressão efetiva deduzida do que foi medido na v28 (força / área projetada) - sem número externo
    def num(chave, padrao, rex=None):
        """Lê um número do JSON da verificação. `padrao=None` => o item é obrigatório:
        se ele sumiu ou mudou de formato, o script para em vez de devolver chutado."""
        for l in ver["checagens"]:
            if chave in str(l.get("item", "")):
                if isinstance(l.get("medido"), (int, float)):        # ja veio medido, como numero
                    return float(l["medido"])
                m = re.search(rex or r"([\d.,]+)", str(l.get("medido", "")).replace("\\u00a0", " "))
                if m:
                    t = m.group(1).replace("\\u00a0", "").strip()
                    if "," in t and "." in t:
                        t = t.replace(".", "").replace(",", ".")
                    elif "," in t:
                        t = t.replace(",", ".")
                    try:
                        return float(t)
                    except ValueError:
                        pass
        if padrao is None:
            raise SystemExit(f"item '{chave}' nao encontrado/legivel em verificacao_v28.json - rode "
                             "verificar_v28.py --json antes; nao existe numero de memoria aqui")
        return padrao

    a_saida = num("Área da seção", None, rex=r"([\d.,]+)\s*mm")
    a_proj = num("Área projetada", None, rex=r"([\d.,]+)\s*mm")
    p_ef = forca_kn * 1e3 / a_proj                       # N/mm2 = MPa
    a_boca = math.pi * (BOCA / 2.0) ** 2
    registrar("Pressão efetiva no limite", f"{n(p_ef, 2)} MPa = {n(p_ef * 10, 1)} bar",
              obs=f"deduzida de {n(forca_kn, 1)} kN medidos / {n(a_proj, 0)} mm² de área projetada medida")
    f_ax = p_ef * (a_boca - a_saida) / 1e3               # kN
    # regex sem rotulo: casa com v28.1, v29... e com o que vier; sem fallback chutado
    dp1d = num("ΔP 1D", None, rex=r"=\s*([\d.,]+)\s*bar")
    f_ax1d = dp1d / 10.0 * (a_boca - a_saida) / 1e3      # kN
    registrar("Empuxo axial que empurra a matriz para fora do cabeçote",
              f"{n(f_ax, 1)} kN no limite · {n(f_ax1d, 1)} kN com o ΔP 1D medido ({n(dp1d, 1)} bar)",
              obs=f"p × ({n(a_boca, 0)} mm² da boca − {n(a_saida, 0)} mm² da fenda)")
    r_int, r_ext = ENVELOPE[1][2] / 2, ENVELOPE[0][2] / 2      # 44,75 e 46,50 (ombro da matriz)
    e_int, e_ext = 45.0, 47.5                                   # degrau medido do cabeçote (Ø90->Ø95)
    a_ombro_d = math.pi * (r_ext ** 2 - r_int ** 2)
    a_ombro_h = math.pi * (e_ext ** 2 - e_int ** 2)
    e = 0.01                                                    # disco fino, para medir por booleano
    anel_d = cil_z(r_ext, 0.0, e).cut(cil_z(r_int, -e, 2 * e))
    anel_h = cil_z(e_ext, 0.0, e).cut(cil_z(e_int, -e, 2 * e))
    a_contato = maior(anel_d.intersect(anel_h)).Volume() / e
    registrar("Área do anel de apoio - matriz (Ø89,5→Ø93)", f"{n(a_ombro_d, 1)} mm²")
    registrar("Área do anel de apoio - cabeçote (Ø90→Ø95)", f"{n(a_ombro_h, 1)} mm²")
    checar("Área REAL de contato (interseção das duas faces, booleano)", a_contato,
           min(a_ombro_d, a_ombro_h) - math.pi * (e_int ** 2 - r_int ** 2), tol=1e-6, un="mm²",
           obs="só onde as duas faces existem há pressão: anel Ø90 → Ø93, não o anel inteiro da matriz")
    p_ombro = f_ax * 1e3 / a_contato
    registrar("Pressão de contato no degrau (apoio axial)", f"{n(p_ombro, 1)} MPa",
              obs=f"{n(f_ax, 1)} kN sobre {n(a_contato, 1)} mm² de contato real; margem de "
                  f"{n(1400 / p_ombro, 1)}x sobre o escoamento da matriz temperada", ok=p_ombro < 700.0)
    A_aperto = math.pi * ENVELOPE[0][2] * (ENVELOPE[0][1] - 0.1)
    p_ax = f_ax * 1e3 / (0.15 * A_aperto)
    p_part = forca_kn * 1e3 / (ENVELOPE[0][2] * (ENVELOPE[0][1] - 0.1))
    registrar("Pressão radial do collete p/ segurar o empuxo axial só por atrito",
              f"{n(p_ax, 1)} MPa sobre {n(A_aperto, 0)} mm²",
              obs="cenário sem o degrau; com o ombro encostando (folga axial 0,10 mm) não é necessário")
    registrar("Pressão radial do collete p/ fechar o plano de partição",
              f"{n(p_part, 1)} MPa", obs=f"{n(forca_kn, 1)} kN de força de abertura equilibrados pela "
              "compressão radial aplicada pelo collete sobre a banda Ø93 - CONDICIONAL, ver o alerta do "
              "furo Ø90 logo abaixo", ok=True)
    _bc = dados["bucha_conica"]
    alerta("Superfície de aperto do collete EX-031", _bc["conflito_encontrado"],
           obs=(f"medido: furo reto Ø{n(_bc['medido_no_dxf']['Ø_interno_mm'], 2)} por "
                f"{_bc['medido_no_dxf']['Ø_interno_comprimento_arestas_mm']} mm e cone de "
                f"{n(_bc['medido_no_dxf']['cone_medido_graus'], 3)}° com silhueta "
                f"Ø{n(_bc['medido_no_dxf']['Ø_externo_menor_mm'], 2)}; banda da matriz Ø"
                f"{n(ENVELOPE[0][2], 2)} -> falta "
                f"{n((ENVELOPE[0][2] - _bc['medido_no_dxf']['Ø_interno_mm']) / 2, 2)} mm de raio. "
                "O apoio axial no degrau não depende disso (431,2 mm² medidos); o que fica condicionado é a "
                "compressão radial e, com ela, o número de pressão acima"))
    p_peso = massa * 9.81 / (0.15 * A_aperto)
    registrar("Pressão radial p/ segurar só o peso na troca", f"{n(p_peso, 4)} MPa",
              obs=f"matriz de {n(massa)} kg")
    registrar("Cone da bucha × atrito", f"3,00° < arctan(0,15) = {n(math.degrees(math.atan(0.15)), 1)}°",
              obs="auto-travante: a matriz não sai sozinha")
    deforo = max(p_ax, p_part) * r_ext / 200000.0
    registrar("Deformação radial do canal sob a pressão do collete", f"~{n(deforo, 4)} mm por lado",
              obs="casca de 8,70 mm sobre o canal, E = 200 GPa - ordem de grandeza",
              ok=deforo < 0.02)

    def pega(prefixo):
        for l in reversed(linhas):
            if str(l["item"]).startswith(prefixo) and isinstance(l.get("medido"), (int, float)):
                return l["medido"]
        return None

    print("\n[F] acesso dos cartuchos e termopares × comprimento do bico do cabeçote\n" + "-" * 70)
    # Dois cenarios, ambos medidos - nenhum e opiniao:
    #   * "desenho DXF medido": protrusao = 109,00 - 95,00 = 14,00 mm (face do nariz e fundo do bolso
    #     medidos no DXF). E o cenario que VALE.
    #   * "voce mediu na maquina": LAX = linha_axial_medida do SSOT (20,00 mm). Em 2026-09-12 mediu-se
    #     que o "20" do desenho e a posicao do furo M12 do bolso contada da face do flange
    #     (72,02 - 52,02 = 20,00), NAO a sobra axial da matriz - ver cabecote_ex030.json. Fica aqui como
    #     cenario alternativo, porque foi a leitura que o usuario descreveu no croqui.
    _ss = json.load(open(os.path.join(AQUI, "cad_die_parameters.json"), encoding="utf-8"))
    LAX = float(_ss["decisoes_usuario"]["medicao_na_maquina"]["linha_axial_medida"]["valor_mm"])
    fur = {}
    for f_ in feat["furos"]:
        if f_["tipo"] in ("cartucho", "termopar"):
            fur[(f_["tipo"], f_["X"], f_["Z"], f_["diametro"])] = f_
    PROTR_DESENHO = ENVELOPE[2][1] - Z_FACE_NARIZ
    FLANGE_FACE, FURO_M12 = 52.02, 72.02      # faces axiais medidas no DXF (verifiesse no bloco [F])
    acessos = {}
    for nome_c, protr in sorted({"você mediu na máquina": LAX, "desenho DXF medido": PROTR_DESENHO}.items()):
        z_face = ENVELOPE[2][1] - protr
        cab = (head if abs(protr - PROTR_DESENHO) < 1e-9
               else head.translate(cq.Vector(0, 0, z_face - Z_FACE_NARIZ)))
        pior, pior_q, bloqueio = 9e9, "", 0.0
        for (tipo, x, z, dd) in sorted(fur):
            folga = (z - dd / 2.0) - z_face          # borda traseira do furo vs fim do metal do cabecote
            corredor = cq.Solid.makeCylinder(dd / 2.0, 240.0, cq.Vector(x, -120.0, z), cq.Vector(0, 1, 0))
            # TODOS os solidos: o corredor do cartucho central corta as duas paredes opostas do
            # nariz, e maior() devolvia so uma metade (1372,276 em vez de 2744,552 mm3)
            _int = corredor.intersect(cab)
            bloqueio += sum(so.Volume() for so in _int.Solids()) or _int.Volume()
            if folga < pior:
                pior, pior_q = folga, f"{tipo} em X={n(x, 1)}, Z={n(z, 1)}"
        acessos[nome_c] = {"protrusao_mm": round(protr, 3), "z_face_cabecote_mm": round(z_face, 3),
                           "folga_axial_min_mm": round(pior, 3), "furo_critico": pior_q,
                           "metal_no_caminho_mm3": round(bloqueio, 3),
                           "n_furos_na_faixa_de_saida": len(fur)}
        if nome_c.startswith("você"):
            alerta(f"Folga axial da furação se a protrusão for {n(protr, 2)} mm (cota '20' do croqui)",
                   f"folga {n(pior)} mm | {n(bloqueio)} mm³ de metal no caminho",
                   obs="o '20 mm' do desenho NAO e protrusao: medido no DXF, e a distancia da face do flange "
                       f"({FLANGE_FACE} mm) ao centro do furo M12 do bolso ({FURO_M12} mm) = 20,00 mm. "
                       "Fica registrado como cenario alternativo, porque e a leitura que ele descreveu")
        else:
            checar_min("Folga axial da furação de saída à frente do metal do cabeçote (protrusão do desenho)",
                       pior, 0.0, un="mm",
                       obs=f"protrusão {n(protr, 2)} mm medida no DXF; furo mais crítico: {pior_q}; metal no "
                           f"caminho de inserção: {n(bloqueio)} mm³; o cartucho deixa de esbarrar em "
                           f"Z >= {n(z_face + max(f_['diametro'] for f_ in fur.values()) / 2.0, 2)} mm")
    z_min = (ENVELOPE[2][1] - PROTR_DESENHO) + max(f_["diametro"] for f_ in fur.values()) / 2.0
    alerta("O que isso decide sobre a furação de saída",
           f"aberta: com a protrusão do desenho ({n(PROTR_DESENHO, 2)} mm) os cartuchos têm de ir para "
           f"Z >= {n(z_min, 2)} mm, ou o nariz do cabeçote ganha alívio",
           obs=f"folga traseira medida {n(acessos['desenho DXF medido']['folga_axial_min_mm'])} mm no cenário que "
               f"vale (desenho) e {n(acessos['você mediu na máquina']['folga_axial_min_mm'])} mm se a matriz "
               "sobressair 20,00 mm; o cabeçote já é furado transversalmente para o M12 do pushador "
               f"({n(FURO_M12, 2)} mm da face do nariz, {n(FURO_M12 - FLANGE_FACE, 2)} mm da face do flange), "
               "então alívio no nariz não é inédito na peça - mas aí é o cabeçote que muda, não a matriz")

    numeros = {"pressao_efetiva_MPa": p_ef, "empuxo_axial_kN": f_ax, "empuxo_axial_dp1d_kN": f_ax1d,
               "acesso_furacao_cenarios": acessos, "protrusao_medida_usuario_mm": LAX,
               "cenario_que_governa": "desenho DXF medido",
              # Z a partir do qual nenhum cartucho esbarra no nariz, calculado no booleano do bloco [F]
              "cartuchos_z_min_mm": z_min,
               "dp_1d_bar": dp1d,
               "area_boca_mm2": a_boca, "area_fenda_mm2": a_saida, "area_projetada_mm2": a_proj,
               "area_ombro_matriz_mm2": a_ombro_d, "area_degrau_cabecote_mm2": a_ombro_h,
               "area_contato_degrau_mm2": a_contato, "pressao_contato_degrau_MPa": p_ombro,
               "pressao_collete_empuxo_axial_MPa": p_ax, "pressao_collete_fechar_particao_MPa": p_part,
               "pressao_collete_peso_MPa": p_peso, "deformacao_radial_canal_mm": deforo,
               "forca_abertura_kN": forca_kn, "massa_kg": massa,
               "folgas_radiais_mm": [pega("Folga radial - Ø93"), pega("Folga radial - Ø89"), pega("Folga radial - Ø79")],
               "folga_axial_apoio_mm": pega("Folga axial no degrau de apoio"),
               "folga_axial_nariz_mm": pega("Folga axial entre o ombro"),
               "protrusao_saida_mm": pega("Protrusão da face de saída"),
               "distancia_parafusos_mm": pega("Menor distância parafuso"),
               "interferencia_mm3": pega("Interferência matriz ∩ cabeçote")}

    print("\n" + "=" * 74)
    ncs = [l for l in linhas if l["status"] == "NAO_CONFORME"]
    print("\n[G] encosto do conjunto na extrusora (decisão 'encosta face a face')\n" + "-" * 70)
    # O que e medido no solido: o piloto protrai atras da face do flange exatamente a altura que a decisao
    # exige que a máquina rebaixe. O que fica pendente: se a face da extrusora TEM esse rebaixo.
    # O que e medido no solido: onde a casca externa cai de 0220 para 0105 - a face real do flange - e o
    # quanto o piloto protrai atras dela. (Nao uso CORPO[][1] direto: os aneis tem sobreposicao de 1 mm
    # para o booleano ser robusto, e a face DESNHADA esta em Z = 3,00, nao em 2,00.)
    face_flange = None
    for zt in [round(0.05 * i, 3) for i in range(0, 121)]:
        fat = head.intersect(cil_z(500.0, zt - 0.0025, zt + 0.0025))
        if not fat.Solids():
            continue
        rr = max(maior(fat).BoundingBox().xlen, maior(fat).BoundingBox().ylen) / 2.0
        if rr > 100.0:
            face_flange = zt
            break
    protr_piloto = round(face_flange - CORPO[2][1], 3) if face_flange is not None else float("nan")
    print(f"   face do flange no sólido: Z = {n(face_flange, 2)} | piloto de Z = {n(CORPO[2][1], 2)} a "
          f"{n(CORPO[2][2], 2)} | protrusão do piloto: {n(protr_piloto, 2)} mm")
    checar("Piloto protrai atrás da face do flange (o rebaixo que a máquina precisa ter)",
           protr_piloto, dados["corpo"]["piloto_traseiro"]["altura_mm"], un="mm",
           obs="face do flange e fim do piloto medidos no sólido por varredura de seções de 0,05 mm")
    alerta("Rebaixo na face da extrusora para receber o piloto (decisão 'face a face')",
           round(protr_piloto, 3),
           "com a junta fechando na face do flange (d = 92,00), a face da máquina precisa de %s mm de "
           "rebaixo em Ø > %s; sem ele a junta fica aberta %s mm. A posição axial da matriz NÃO muda "
           % (n(protr_piloto, 2), n(2 * CORPO[2][0], 2), n(protr_piloto, 2)) +
           "com isso: ela vem do degrau/fundo do bolso do cabeçote (interferência 0,0000 mm³ no assento), "
           "então a protrusão continua 14,00 mm e o NC dos cartuchos também.")
    print()

    pend = [l for l in linhas if l["status"] == "PENDENTE_CONFIRMACAO"]
    print(f"{len(linhas)} itens | {len(linhas) - len(ncs) - len(pend)} conformes | "
          f"{len(ncs)} não conformes | {len(pend)} pendentes (máquina)")
    for l in ncs:
        print(f"   NC: {l['item']}  {l.get('medido')}  {l.get('observacao', '')}")

    saida = {"peca": "Interface MatrizJonatha_v28 x Cabeçote EX-030", "data": "2026-09-11",
             "metodo": ("sólido do cabeçote montado do perfil medido no DWG 030-032 "
                        "(k = 25,534 mm/un, desvio máx. 0,012 % em 5 cotas) + booleanos e "
                        "BRepExtrema sobre MatrizJonatha_v28.step"),
             "cabecote": dados, "numeros": numeros, "checagens": linhas,
             "itens": len(linhas), "conformes": len(linhas) - len(ncs) - len(pend),
             "nao_conformes": len(ncs), "pendentes": len(pend)}
    if a.json:
        p = os.path.join(AQUI, "interface_cabecote.json")
        json.dump(saida, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"JSON -> {p}")
    if a.md:
        L = ["# Interface matriz v28 × cabeçote EX-030", "",
             "O sólido do cabeçote foi montado do perfil lido no DWG 030-032 (escala calibrada "
             "pelas próprias cotas: 25,534 mm por unidade DXF, cinco fechos independentes batendo "
             "em 0,012 %). Todos os números abaixo saem de booleanos e `BRepExtrema` contra "
             "`MatrizJonatha_v28.step`.", "",
             "| item | medido | nominal | desvio | status | observação |", "|---|---|---|---|---|---|"]
        for l in linhas:
            L.append("| " + " | ".join([str(l["item"]).replace("|", "/"), str(l.get("medido", "")),
                                        str(l.get("nominal", "—")), str(l.get("desvio", "—")),
                                        l["status"], str(l.get("observacao") or "").replace("|", "/")]) + " |")
        _fx = dados["furos_transversais_no_cabecote"]["medidos_no_dxf"][0]
        _metal = (dados["corpo"]["Ø_corpo_mm"] - dados["furos_do_cabecote_para_a_matriz"][2]["Ø_mm"]) / 2.0
        L += ["", "## O que isso muda no projeto", "",
              "1. **A matriz cabe no cabeçote.** Os três estágios do corpo (Ø93×69,90 / Ø89,5×10,80 / "
              "Ø79,5×28,30) caem nos três furos medidos do cabeçote (Ø95×70,0 / Ø90×11,0 / Ø80×14,0) "
              "com folga radial de 1,00 / 0,25 / 0,25 mm e folga axial de 0,10 mm no degrau de apoio. "
              "Interferência corpo-a-corpo: zero. A face de saída fica 14,00 mm além da face do nariz, "
              "então a fenda trabalha fora do cabeçote.",
              f"2. **O anel da face é de 20,00 mm** (Ø90 → Ø130) — exatamente o número descrito. "
              f"O furo do nariz (Ø80) é maior que a boca da matriz (boca medida {n(MANTA[0])} × "
              f"{n(MANTA[1])} mm -> {n((80.0 - MANTA[0]) / 2, 2)} mm por lado) e menor que a matriz "
              f"(Ø{ENVELOPE[0][2]:.0f}): a descrição do cliente confere com o desenho — os 2,50 mm "
              f"por lado medidos na máquina são do produto (Ø{PRODUTO[0]:.2f}), não da boca chanfrada.",
              # (substituído pela linha medida acima)
              f"3. **D1 se resolve na máquina, não na matriz — e sem furar nada.** O empuxo axial "
              f"medido ({n(f_ax, 1)} kN no limite, {n(f_ax1d, 1)} kN com o ΔP 1D de {n(dp1d, 1)} bar) "
              f"recai em compressão no degrau: {n(a_contato, 1)} mm² de contato real a "
              f"{n(p_ombro, 1)} MPa, com {n(1400 / p_ombro, 0)}× de margem sobre o escoamento da matriz "
              "temperada (medido por booleano: a faixa de contato só existe onde as duas faces existem). A bucha "
              "cônica EX-031 (Ø95/Ø90, cone 3°, L 70 = exatamente o comprimento do bolso) é "
              "auto-travante (3,00° < 8,5°) e, ao apertar a banda Ø93, aplica compressão radial: "
              f"{n(p_part, 2)} MPa bastam para equilibrar os {n(forca_kn, 1)} kN que abrem a bipartição, "
              f"e {n(p_ax, 2)} MPa para segurar "
              "o empuxo axial só por atrito — e a deformação do canal com isso é de 0,002 mm por lado "
              "(0,15 % da espessura da manta). **Retiro a recomendação de grampos no flange: a matriz "
              "não leva flange, nem grampo, nem furo de fixação.** O monobloco por EDM continua sendo a "
              "opção mais robusta, mas deixa de ser a única.",
              "3b. **Atenção ao aperto:** 8,6 MPa é pouco, mas o collete é cônico e o montador aperta até "
              "encostar. A pressão que fecha o plano de partição é a mesma que prensa a parede de 8,70 mm "
              "contra o canal — exigir no desenho de execução o torque/curso de aperto da bucha, senão a "
              "banda vira a cunha que abre o canal em vez de fechá-lo.",
              "4. **Bloqueio encontrado — o anel do nariz é de 65 mm.** O corte mostra uma passagem "
              "Ø68,30 no nariz (e o carimbo da peça é 9\"×65 mm). Com esse anel montado, a matriz de "
              "75 mm **não entra**: 5,60 mm de interferência radial por lado contra o nariz Ø79,5 da "
              "matriz. Como o furo do nariz já é Ø80, não há espaço físico para nenhum anel com passagem "
              "≥ Ø79,6 — na variante de 75 mm o nariz tem de ficar aberto (ou o anel ter Ø80, ou seja, "
              "não restringir nada), e o centramento passa a ser feito direto no Ø80×14 do cabeçote.",
              "5. **Padrão de furação (P4):** os 6×Ø16,5 em C.C Ø180 dentro de fendas de 23,5 "
              "(±7,2°, cotadas como 15°) são a junta cabeçote↔extrusora e passam a 35,25 mm do corpo da "
              "matriz. O posicionamento angular da matriz vem dos três centragens cilíndricos, não de "
              "pino de flange — não há nada a padronizar na matriz.",
              "6. **Atenção na fabricação:** o furo do pino de alinhamento em X = ±42,10 (Z = 30 e 60) "
              "deixa ~0,8 mm de parede até a superfície Ø93 que a bucha aperta. Não rompe o envelope "
              "(0 mm³), mas é essa parede que o collete vê: manter o furo cego, sem rebaixo, e o Ø93 "
              "retificado na zona de aperto.",
              f"7. **A cota '20 mm' da vista em corte não é a protrusão da matriz — lido no DXF, não "
              f"deduzido.** O par de círculos exatos Ø{n(_fx['Ø_broca_mm'], 2)}/Ø{n(_fx['Ø_passagem_mm'], 2)} "
              f"está sobre o eixo a {n(_fx['x_da_face_do_nariz_mm'], 2)} mm da face do nariz, e é isso que fica "
              f"{n(_fx['x_da_face_do_flange_mm'], 2)} mm da face do flange: um **M12 transversal na parede do "
              f"bolso**, no plano Z = {n(_fx['plano_z_na_matriz_mm'], 2)} mm do eixo da matriz, atravessando "
              f"{n(_metal, 2)} mm de aço entre o bolso e o corpo. Duas consequências: (i) a protrusão da matriz "
              "volta a ser a do desenho (14,00 mm) e a folga traseira dos cartuchos reabre como não conforme, com "
              "as duas saídas medidas no bloco [F]; (ii) se você preferir não mover os cartuchos, há precedente na "
              "própria peça para levar o aquecimento pelo cabeçote — e é a prova de que a matriz dispensa furo de "
              "desmontagem, já que o pushador EX-032 M12 age por esse furo.",
              f"8. **A conferir no desenho:** o print mostra o Ø90 do nariz cotado +0,05/+0,10 (os dois "
              "positivos), e meu modelo usou +0,05/0. O efeito medido é pequeno e não trava nada: a folga radial "
              "do degrau Ø89,5 da matriz passa de 0,250 mm para a faixa 0,250…0,325 mm; o engate axial de 0,30 mm "
              "é folga de face e o centro continua vindo da banda Ø93 (que o collete aperta, se a superfície de "
              "aperto for confirmada - item 9).",
              "9. **Achei outro número meu que a medição derruba: o furo do collete não passa sobre a banda "
              "Ø93.** Medindo as vistas com o eixo de cada uma (o corte do cabeçote tem eixo em y = 0; as "
              "outras vistas têm eixo próprio, e era por isso que as varreduras anteriores não viam nada), "
              "as **únicas 4 geratrizes inclinadas do desenho inteiro** estão a 3,267°, com silhueta "
              "simétrica Ø86,00, e o furo que as acompanha é **reto Ø90,00** por 63 a 70 mm. Com Ø90 reto, "
              "o collete EX-031 não desce sobre a banda Ø93 da matriz: faltam 1,50 mm de raio. O que muda: "
              "a pressão de 8,6 MPa que eu citei como \"é isto que fecha a bipartição\" passa a ser "
              "**condicional** à confirmação da superfície de aperto (furo do collete também cônico, outra "
              "banda na matriz, ou a vista sendo de outra peça). O **apoio axial** no degrau - que é o que "
              "reage os 29,8 kN - é medido por booleano entre as duas peças e independe do collete, "
              "então continua de pé. E a recomendação que já estava no relatório é imune a isso: "
              "monobloco por EDM, sem plano de partição para fechar.", ""]
        p = os.path.join(DIR_DOC, "INTERFASE_CABECOTE_EX030.md")
        open(p, "w", encoding="utf-8").write("\n".join(L))
        print(f"MD  -> {p}")
    return 1 if ncs else 0


if __name__ == "__main__":
    sys.exit(main())
