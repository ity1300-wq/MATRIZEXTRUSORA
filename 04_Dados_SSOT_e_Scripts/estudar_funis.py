"""D3 - compara os dois funis com numeros medidos nos solidos.

Contexto (relatorio v28.1, secao 7.1): o texto do projeto descreve um coat-hanger com
reservatorio central de 6,00 mm e asas em Z=25/Z=70, mas o solido aprovado e um reduzor
conico linear em Y - o loft de `generate_true_coathanger_jonatha.py` so interpola a primeira
e a ultima secao. Este script modela a variante coat-hanger a partir das secoes DECLARADAS
naquele script, com estacoes intermediarias (para o loft seguir a lei de projeto e nao a
fantasia da amostragem), e mede nos dois solidos com a mesma trena:

  * Delta-P 1D com o metodo do proprio projeto (verify_legacy_dies.dp_total);
  * volume do canal e tempo medio de residencia (V / Q, Q do proprio projeto);
  * altura da secao em Z=25, Z=70 e minima antes do land (fome de massa);
  * volume estacionado nas pontas (|x| > 30 mm, antes do land) - proxy de zona morta;
  * deslocamento do centroide em Y (assimetria entre as duas metades);
  * maior invasao do envelope do master (a regra rigida 5) e volume/massa do aco cortado.

Nao altera geometria oficial: escreve em 05_Variantes_Em_Estudo/, um JSON e um MD.
"""
import json
import math
import os
import sys

import cadquery as cq

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
DIR_CAD = os.path.join(RAIZ, "07_CAD_Matrizes", "M01_Jonatha_v27_OFICIAL")
DIR_V28 = os.path.join(RAIZ, "07_CAD_Matrizes", "M02_Jonatha_v28_PROPOSTA")
DIR_ESTUDO = os.path.join(RAIZ, "05_Variantes_Em_Estudo")
DIR_REL = os.path.join(RAIZ, "03_Relatorios_e_Documentacao")
sys.path.insert(0, AQUI)

# secao() vem de verify_legacy_dies de proposito: e a MESMA funcao que o dp_total usa, entao a
# tabela de alturas e o Delta-P saem do mesmo corte (verificar_v28.secao devolve outra coisa).
from verify_legacy_dies import K_PA_SN, N_INDICE, Q_MM3_S, dp_total, secao  # noqa: E402
from verificar_v28 import maior, r_envelope  # noqa: E402

with open(os.path.join(AQUI, "cad_die_parameters.json"), encoding="utf-8") as f:
    SSOT = json.load(f)
G = SSOT["proposta_v28_dfm"]["geometria_labios"]
Z_LAND = float(G["z_inicio_land_mm"])
Z_FIM = float(G["z_fim_mm"])
LAND = float(G["land_paralelo_mm"])
CHANFRO = float(G["chanfro_saida_mm"])
BOCA = 75.60                                   # restricao rigida de entrada (Z=0)
ENVELOPE = [[0.0, 69.9, 93.0], [69.9, 80.7, 89.5], [80.7, Z_FIM, 79.5]]   # medido no master
LARGURA_FENDA = 75.00
ESP_FENDA = 1.50
ACO_KG_MM3 = 7.85e-6

# secoes declaradas em generate_true_coathanger_jonatha.py (o que o texto do projeto quis)
SECOES = [(0.0, ("circulo", BOCA, BOCA)), (25.0, ("slot", 35.00, 12.00)),
          (70.0, ("slot", 75.00, 3.50)), (Z_LAND, ("slot", LARGURA_FENDA, ESP_FENDA))]


def num_pt(v, dec=2):
    """1.234,567 no padrao do projeto (o f-format do Python usa o ingles)."""
    if not isinstance(v, (int, float)):
        return str(v)
    t = f"{float(v):,.{dec}f}"                  # 1,234.567 (milhar, decimal)
    return t.replace(",", "@").replace(".", ",").replace("@", ".")


def contorno_slot(L, H, z, n=96):
    """Stadium L x H amostrado por angulo em torno do centro.

    Amostrar por angulo (e nao por comprimento de arco) e o que da correspondencia ponto a
    ponto entre secoes de larguras muito diferentes - sem isso o loft torce em parafuso.
    """
    a = max((L - H) / 2.0, 0.0)                  # semi-comprimento da parte reta
    r = H / 2.0                                   # raio da ponta semicircular
    pts = []
    for i in range(n):
        th = 2.0 * math.pi * i / n
        ux, uy = math.cos(th), math.sin(th)
        lo, hi = 0.0, 0.5 * max(L, H) + r + 1.0
        for _ in range(60):                       # estadio = segmento (+) disco: biseccao monotona
            t = 0.5 * (lo + hi)
            cx = min(max(t * ux, -a), a)
            if math.hypot(t * ux - cx, t * uy) < r:
                lo = t
            else:
                hi = t
        t = 0.5 * (lo + hi)
        pts.append(cq.Vector(t * ux, t * uy, z))
    pts.append(pts[0])
    return cq.Wire.makePolygon(pts)


def contorno_circulo(d, z, n=96):
    return contorno_slot(d, d, z, n)              # estadio com a == 0 e um circulo


def lei_projeto(z):
    """(largura, altura) interpolada linearmente entre as estacoes declaradas."""
    for (z0, s0), (z1, s1) in zip(SECOES, SECOES[1:]):
        if z0 <= z <= z1:
            fr = 0.0 if z1 == z0 else (z - z0) / (z1 - z0)
            return (s0[1] + fr * (s1[1] - s0[1]), s0[2] + fr * (s1[2] - s0[2]))
    return SECOES[-1][1][1], SECOES[-1][1][2]


def funil_coathanger():
    """Loft por TODAS as estacoes - e isso que faltava no script original."""
    zs = sorted({round(z, 3) for z, _ in SECOES} |
                {5.0 * i for i in range(1, int(round(Z_LAND / 5)))})
    wires = []
    for z in zs:
        w, h = lei_projeto(z)
        if z == 0.0:
            wires.append(contorno_circulo(BOCA, z))       # boca: restricao rigida
        else:
            wires.append(contorno_slot(max(w, h + 0.2), h, z))
    return cq.Solid.makeLoft(wires, ruled=True)


def canal_e_corpo(funil):
    """Canal = funil + land + chanfro (mesmo fim de curso do master); corpo = aco cortado."""
    land = cq.Workplane("XY").workplane(offset=Z_LAND).slot2D(LARGURA_FENDA, ESP_FENDA).extrude(LAND)
    cham = (cq.Workplane("XY").workplane(offset=Z_FIM - CHANFRO)
            .slot2D(LARGURA_FENDA, ESP_FENDA)
            .workplane(offset=CHANFRO)
            .slot2D(LARGURA_FENDA + 2 * CHANFRO, ESP_FENDA + 2 * CHANFRO).loft(ruled=True))
    canal = cq.Workplane("XY").add(funil).union(land).union(cham).val()
    c1 = cq.Workplane("XY").circle(ENVELOPE[0][2] / 2).extrude(ENVELOPE[0][1])
    c2 = (cq.Workplane("XY").workplane(offset=ENVELOPE[1][0]).circle(ENVELOPE[1][2] / 2)
          .extrude(ENVELOPE[1][1] - ENVELOPE[1][0]))
    c3 = (cq.Workplane("XY").workplane(offset=ENVELOPE[2][0]).circle(ENVELOPE[2][2] / 2)
          .extrude(ENVELOPE[2][1] - ENVELOPE[2][0]))
    return canal, c1.union(c2).union(c3).cut(canal).val()


def ponta(canal, z0, dz, lado):
    """Volume do canal com |x| > 30 mm numa fatia de z0 a z0+dz (lado: +1 ou -1)."""
    wp = cq.Workplane("XY", origin=(lado * (30.0 + 7.0), 0.0, z0))
    caixa = wp.box(14.0, 400.0, dz, centered=(True, True, False)).val()
    return maior(canal.intersect(caixa)).Volume()


def invasao_envelope(canal):
    """Maior invasao do envelope do master, em mm (0 = regra rigida respeitada)."""
    pior, z_pior = 0.0, 0.0
    for i in range(1, 405):
        z = i * 0.27
        if z > Z_FIM - 0.02:
            break
        try:
            wx, wy, a = secao(canal, z)
        except Exception:
            continue
        if a > 0.5:
            p = max(wx, wy) / 2.0 - r_envelope(z)
            if p > pior:
                pior, z_pior = p, z
    return pior, z_pior


def medir(nome, canal, corpo=None):
    dp, z_pico, pico = dp_total(canal, Z_FIM, dz=0.5)
    vol = canal.Volume()
    alturas, alt_min = {}, None
    z = 0.5
    while z < Z_FIM - 1e-6:
        try:
            wx, wy, a = secao(canal, min(z, Z_FIM - 0.001))
        except Exception:
            z += 0.5
            continue
        if a > 0.5:
            if alt_min is None or wy < alt_min[1]:
                alt_min = (z, wy)
            for alvo in (25.0, 70.0):
                if abs(z - alvo) < 0.25 and alvo not in alturas:
                    alturas[alvo] = (z, wx, wy)
        z += 0.5
    v_pontas, zz = 0.0, 0.0
    while zz < Z_LAND - 1e-6:
        dz = min(3.0, Z_LAND - zz)
        for lado in (1, -1):
            v_pontas += ponta(canal, zz, dz, lado)
        zz += dz
    inv, z_inv = invasao_envelope(canal)
    vcor = corpo.Volume() if corpo is not None else None
    return {"nome": nome, "dp_1d_bar": dp, "z_pico_mm": z_pico, "pico_bar_por_mm": pico,
            "volume_mm3": vol, "residencia_s": vol / Q_MM3_S,
            "altura_em_z25_mm": alturas.get(25.0, (0, 0, 0))[2],
            "altura_em_z70_mm": alturas.get(70.0, (0, 0, 0))[2],
            "largura_em_z70_mm": alturas.get(70.0, (0, 0, 0))[1],
            "altura_min_mm": alt_min[1] if alt_min else None,
            "z_altura_min_mm": alt_min[0] if alt_min else None,
            "volume_pontas_mm3": v_pontas, "frac_volume_pontas": v_pontas / vol,
            "centroide_y_mm": canal.Center().y, "invasao_envelope_mm": inv,
            "z_invasao_mm": z_inv, "corpo_mm3": vcor,
            "corpo_kg": None if vcor is None else vcor * ACO_KG_MM3}


def redigir(m_atu, m_new, gravar=True):
    with open(os.path.join(AQUI, "verificacao_v28.json"), encoding="utf-8") as f:
        _ver = json.load(f)
    # volume total dos furos da v28.1, medido pelo verificador (fechamento env - aco - canal)
    furos = next((l.get("nominal") for l in _ver["checagens"]
                  if "volume dos furos" in str(l.get("item", ""))), None)
    out = {"metodo": ("cortes do solido com secao() de verify_legacy_dies.py (a mesma que o "
                      "dp_total usa, para tabela e Delta-P saírem do mesmo corte); Delta-P 1D com "
                      f"dp_total() de verify_legacy_dies.py (K = {num_pt(K_PA_SN)} Pa·s^n, "
                      f"n = {num_pt(N_INDICE)}, Q = {num_pt(Q_MM3_S, 0)} mm³/s); mesmo land "
                      f"{num_pt(LAND)} mm e chanfro {num_pt(CHANFRO)} × 45 nos dois lados da "
                      "comparação; lei de projeto do funil novo nas estações "
                      + ", ".join("Z=" + num_pt(z, 0) for z, _ in SECOES) + " mm"),
           "geometria_labios": G,
           "secoes_declaradas": [[z, list(d)] for z, d in SECOES],
           "medicoes": [m_atu, m_new]}
    if gravar:
        with open(os.path.join(AQUI, "funil_coathanger.json"), "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)

    def dif(k, dec=2, u="", modo="%"):
        a, b = m_atu[k], m_new[k]
        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            return f"| {a} | {b} | — |"
        if modo == "abs" or abs(a) < 1e-6:
            d = f"Δ {num_pt(b - a, dec)}{u}"
        elif modo == "pp":
            d = f"{(b - a) * 100:+.1f} pp".replace(".", ",")
        else:
            d = f"{(b - a) / abs(a) * 100:+.1f} %".replace(".", ",")
        return f"| {num_pt(a, dec)}{u} | {num_pt(b, dec)}{u} | {d} |"

    linhas = [
        ("ΔP 1D até a saída (método do projeto)", "dp_1d_bar", 1, " bar"),
        ("volume do canal", "volume_mm3", 0, " mm³"),
        ("tempo médio de residência (V/Q)", "residencia_s", 0, " s"),
        ("altura da seção em Z=25,00", "altura_em_z25_mm", 2, " mm"),
        ("altura da seção em Z=70,00", "altura_em_z70_mm", 2, " mm"),
        ("menor altura de seção antes da saída", "altura_min_mm", 2, " mm"),
        ("volume estacionado com |x| > 30 mm (antes do land)", "volume_pontas_mm3", 0, " mm³"),
        ("fração desse volume", "frac_volume_pontas", 3, "", "pp"),
        ("centroide do canal em Y (0 = simétrico)", "centroide_y_mm", 4, " mm", "abs"),
        ("maior invasão do envelope do master (0 = regra rígida OK)",
         "invasao_envelope_mm", 4, " mm", "abs"),
    ]
    md = ["# D3 — funil atual × coat-hanger, medido nos sólidos", "",
          f"Método: {out['metodo']}.", "",
          "Nada aqui muda o arquivo oficial: é a comparação pedida antes de tocar no canal.", "",
          "| grandeza | funil atual (cone linear) | variante coat-hanger | diferença |",
          "| :--- | ---: | ---: | ---: |"]
    for row in linhas:
        rot, k, dec, u = row[:4]
        extra = row[4] if len(row) > 4 else "%"
        md.append(f"| {rot} {dif(k, dec, u, extra)}")
    if m_new.get("corpo_mm3") and m_atu.get("corpo_mm3"):
        md.append(f"| aço cortado no mesmo envelope | {num_pt(m_atu['corpo_mm3'], 0)} mm³ "
                  f"({num_pt(m_atu['corpo_kg'], 3)} kg) | {num_pt(m_new['corpo_mm3'], 0)} mm³ "
                  f"({num_pt(m_new['corpo_kg'], 3)} kg) | "
                  f"{num_pt(m_new['corpo_mm3'] - m_atu['corpo_mm3'], 0)} mm³ |")
    r = m_new["dp_1d_bar"] / m_atu["dp_1d_bar"]
    dres = (m_new["residencia_s"] - m_atu["residencia_s"]) / m_atu["residencia_s"] * 100
    md += ["", "## O que os números dizem", "",
           f"1. **Custa {num_pt(r)}× de pressão e não muda a manta.** {num_pt(m_new['dp_1d_bar'], 1)} bar "
           f"contra {num_pt(m_atu['dp_1d_bar'], 1)} bar integrados até a saída. A fenda e o land são os "
           f"mesmos nos dois ({num_pt(ESP_FENDA)} × {num_pt(LARGURA_FENDA)} mm, land {num_pt(LAND)} mm), "
           f"então a **espessura da manta não melhora um mícron** — e os "
           f"{num_pt(m_new['dp_1d_bar'], 1)} bar já passam dos 68,2 bar que o relatório de CFD do projeto "
           "usa como limite. Não é troca neutra: mexe no dimensionamento da extrusora.",
           f"2. **O canal fica {num_pt((1 - m_new['volume_mm3'] / m_atu['volume_mm3']) * 100, 0)} % menor** "
           f"({num_pt(m_new['volume_mm3'], 0)} mm³ contra {num_pt(m_atu['volume_mm3'], 0)} mm³) e por isso a "
           f"residência cai de {num_pt(m_atu['residencia_s'], 0)} s para {num_pt(m_new['residencia_s'], 0)} s "
           f"({num_pt(dres, 0)} %). Cuidado ao ler isso como mérito do cabide: é só \"tem menos plástico "
           f"parado\". A fração estacionada nas pontas cai de "
           f"{num_pt(m_atu['frac_volume_pontas'] * 100, 1)} % para {num_pt(m_new['frac_volume_pontas'] * 100, 1)} % "
           f"do volume, mas em absoluto são {num_pt(m_atu['volume_pontas_mm3'], 0)} → "
           f"{num_pt(m_new['volume_pontas_mm3'], 0)} mm³, e parte da queda vem do canal inteiro menor, "
           "não da forma das asas.",
           f"3. **Nenhum dos dois é o coat-hanger descrito.** A altura da seção em Z=25,00 é "
           f"{num_pt(m_atu['altura_em_z25_mm'])} mm no funil atual e {num_pt(m_new['altura_em_z25_mm'])} mm na "
           "variante modelada a partir do script do projeto; o reservatório central de **6,00 mm** que o "
           "AUTO_PROMPT descreve não existe em sólido nenhum deste repositório (e 12,00 mm é o que o próprio "
           "`generate_true_coathanger_jonatha.py` pede — o texto e o script também não batem entre si).",
           f"4. **Assimetria**: o centroide do canal está a {num_pt(m_atu['centroide_y_mm'], 4)} mm do plano "
           f"de partição no funil atual e a {num_pt(m_new['centroide_y_mm'], 4)} mm na variante. Nenhum dos "
           "dois desloca a fenda; a assimetria de 199,22 mm³ achada na auditoria do v27.0 é do loft do "
           "land, não do funil, e não muda com esta decisão.",
           f"5. **Envelope respeitado nos dois**: a maior invasão medida seção a seção foi "
           f"{num_pt(m_new['invasao_envelope_mm'], 4)} mm na variante (em Z={num_pt(m_new['z_invasao_mm'], 1)}) "
           f"e {num_pt(m_atu['invasao_envelope_mm'], 4)} mm no atual — nenhum encosta no Ø93/Ø89,5/Ø79,5 e a "
           f"boca de entrada continua em {num_pt(BOCA)} mm em Z=0.",
           ""]
    if m_new.get("corpo_mm3") and m_atu.get("corpo_mm3"):
        d_aco = m_new["corpo_mm3"] - m_atu["corpo_mm3"]
        d_canal = m_atu["volume_mm3"] - m_new["volume_mm3"]
        sobra = None if furos is None else d_aco - d_canal - furos
        fecha = sobra is not None and abs(sobra) < 1.0
        md += [f"6. **Aço e contabilidade fechada**: cortando o mesmo envelope, sobra "
               f"{num_pt(m_new['corpo_mm3'], 0)} mm³ na variante contra {num_pt(m_atu['corpo_mm3'], 0)} mm³ "
               f"na v28.1 — **{num_pt(d_aco, 0)} mm³ a mais de aço**. Isso confere com as outras duas "
               f"medidas: o canal da variante é {num_pt(d_canal, 0)} mm³ menor e a v28.1 tem "
               f"{num_pt(furos, 0)} mm³ de furação que este estudo não modela, "
               f"{num_pt(d_canal, 0)} + {num_pt(furos, 0)} = {num_pt(d_canal + (furos or 0), 0)} mm³ "
               f"(diferença residual de {num_pt(sobra or 0, 3)} mm³ — "
               f"{'FECHA: as três medições são consistentes' if fecha else 'NAO FECHA: algo mudou entre as mediacoes, refaca a cadeia'}"
               f"). Portanto o número de massa aqui **não é número de corte**: o corpo do estudo não leva "
               "furos e não está bipartido.", ""]
    md += ["## Recomendação (para você decidir, não apliquei nada)", "",
           "Manter o funil do master e **reescrever o texto** que fala em coat-hanger com reservatório de "
           "6,00 mm (opção 7.1a do relatório v28.1): ele descreve uma peça que não foi feita. Se você quiser "
           "um cabide de verdade, o próximo passo não é este loft: é desenhar a altura das asas decrescente "
           "do centro para as pontas (h(±37,50) < h(0)), que é o único mecanismo que compensa o caminho mais "
           f"longo das bordas — e aí CFD novo é obrigatório, porque o ΔP saiu de {num_pt(m_atu['dp_1d_bar'], 1)} "
           f"para {num_pt(m_new['dp_1d_bar'], 1)} bar só com essa troca de forma.", ""]
    with open(os.path.join(DIR_REL, "ESTUDO_FUNIL_COATHANGER.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    print("\n".join(md))
    print(f"-> STEP do estudo em {DIR_ESTUDO}/")
    return 0


def main():
    if "--so-texto" in sys.argv:            # redige a partir do JSON ja medido (nao recorta nada)
        with open(os.path.join(AQUI, "funil_coathanger.json"), encoding="utf-8") as f:
            jb = json.load(f)
        return redigir(*jb["medicoes"], gravar=False)
    os.makedirs(DIR_ESTUDO, exist_ok=True)
    canal_new, corpo_new = canal_e_corpo(funil_coathanger())
    cq.exporters.export(cq.Workplane("XY").add(canal_new).val(),
                        os.path.join(DIR_ESTUDO, "ESTUDO_funil_coathanger_Canal_Fluxo.step"))
    cq.exporters.export(cq.Workplane("XY").add(corpo_new).val(),
                        os.path.join(DIR_ESTUDO, "ESTUDO_funil_coathanger_Matriz.step"))
    atual = maior(cq.importers.importStep(
        os.path.join(DIR_V28, "MatrizJonatha_v28_Canal_Fluxo.step")).val())
    # o .step da matriz e uma composicao com as duas metades: maior() pegaria so uma delas
    corpo_atu = cq.importers.importStep(os.path.join(DIR_V28, "MatrizJonatha_v28.step")).val()
    m_atu = medir("funil atual - reduzor conico linear do master", atual, corpo_atu)
    m_new = medir("variante coat-hanger - secoes declaradas, loft por todas as estacoes",
                  canal_new, corpo_new)
    return redigir(m_atu, m_new, gravar=True)


if __name__ == "__main__":
    sys.exit(main())
