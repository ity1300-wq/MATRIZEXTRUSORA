#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Desenho DXF cotado da matriz - A3, 1:1, mm. Anatomia medida, nao receita de fabricacao.

O que a folha tem (e nada alem disso):
  · MATERIAL em 2 linhas objetivas no topo - aco 1045, norma, dureza, o que nao pode mudar;
  · SECAO NO PLANO DA ABERTURA 1:1 (a vista em que o funil aparece);
  · FACE DE SAIDA 1:1 com a fenda e a boca do chanfro com os raios de verdade;
  · DETALHE A 6:1 do fim do canal - e ai que a abertura 1,500 aparece grande;
  · TABELA DE ANATOMIA: regiao / cota de contrato / o que a medicao no STEP achou, 15 linhas;
  · carimbo com MATERIAL, cota critica, topologia solida, fonte e aceite.
8 DIMENSION reais (editaveis, virgula decimal) + a tabela. Processo detalhado, CFD e historico de
revisao continuam no README e no 03_SEQUENCIA_DE_USINAGEM.md do pacote.

Geometria desenhada = nominal exata do contrato, entao o que a maquina medir no arquivo bate com o
texto da cota. Nenhum numero e digitado aqui: nomes e cotas vem de pacote_usinagem.json (alvo_do_
contrato, cotas, medido, medido_na_revisao). Se faltar chave, o gerador para com SystemExit em vez
de chutar. Todo texto tem largura estimada e linhas contadas contra a coluna/caixa que o recebe.

Uso:
  python3 gerar_desenho_cotado_dxf_v30.py
  PACOTE=08_Pacote_Usinagem_v29 DXF=MATRIZ_V29_DESENHO_COTADO python3 gerar_desenho_cotado_dxf_v30.py
  DXF_SERIE=R2000 python3 gerar_desenho_cotado_dxf_v30.py   # gêmeo em AutoCAD 2000 (AC1015)
Depende de ezdxf (listado no 04_/restaurar_workspace.sh); o preview usa matplotlib.
"""
import io, json, math, os
import ezdxf
from ezdxf.enums import TextEntityAlignment

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACOTE = os.environ.get("PACOTE", "08_Pacote_Usinagem_v30")
DXF = os.environ.get("DXF", "MATRIZ_V30_DESENHO_COTADO")
REV = PACOTE.rsplit("_", 1)[-1].lstrip("v")
# R2010 (AC1024) é o padrão; R2000 (AC1015) sai para CAD antigo - foi o que a matrizaria pediu
# ("não consigo abrir arquivos BIN, teria como enviar em DWG ou DXF?"), e AutoCAD 2000 abre tudo.
SERIE = os.environ.get("DXF_SERIE", "R2010")
if SERIE not in ("R2010", "R2000", "R2018"):
    raise SystemExit("DXF_SERIE deve ser R2010, R2018 ou R2000, veio %r" % SERIE)
SUFIXO = "" if SERIE == "R2010" else "_AC1015" if SERIE == "R2000" else "_AC1032"

FOLHA = (420.0, 297.0)
B = (10.0, 10.0, FOLHA[0] - 10.0, FOLHA[1] - 10.0)          # moldura A3
YV = 186.0                                                   # eixo das tres vistas
X0 = 52.0                                                    # face de entrada da secao
CFC = 246.0                                                  # centro da face de saida
DXA, ESA = 318.0, 6.0                                        # DETALHE A: x do corte e escala
TABELA = (22.0, 14.0, 198.0, 114.0)                          # caixa da tabela de anatomia
CARIMBO = (210.0, 14.0, B[2] - 2, 114.0)                     # caixa do carimbo
COL = (24.0, 76.0, 140.0)                                     # colunas da tabela
COLW = (50.0, 62.0, 56.0)
FATOR = 0.68

RUIM = {0x2212: "-", 0x2013: " a ", 0x2014: "-", 0x2192: "->", 0x2265: ">=", 0x2264: "<=",
        0x2248: "~", 0x00a0: " ", 0x2260: "<>", 0x2022: "-", 0x03bc: "u", 0x2026: "...",
        0x2027: "...", 0x2010: "-", 0x2011: "-", 0x2012: "-", 0x02da: "graus"}


def tx(s):
    s = str(s)
    for o, v in RUIM.items():
        s = s.replace(chr(o), v)
    sobra = sorted({c for c in s if ord(c) > 0xFF})
    if sobra:
        raise SystemExit("texto do DXF com glifo fora do Latin-1: %s em %r" % (sobra, s))
    return s


def br(x, dec=2):
    return ("%.*f" % (dec, float(x))).replace(".", ",")


D = json.load(io.open(os.path.join(RAIZ, PACOTE, "pacote_usinagem.json"), encoding="utf-8"))
M, ALV = D["medido"], D["alvo_do_contrato"]
ACO, DEC, MON = D.get("aco", {}), D.get("decisoes_2026_09_22", {}), D.get("montagem", {})
REV_M = D.get("medido_na_revisao", {})
CAN, FEN = REV_M.get("canal", {}), REV_M.get("fenda", {})
FEND, BOCA, ENTR = M["fenda_no_land"], M["boca_saida"], M["boca_entrada"]
PROT = MON.get("saida_além_da_face_do_nariz_mm")
FALTAM = [k for k, v in (("aco/norma", ACO.get("norma")), ("aco/dureza", ACO.get("dureza")),
                         ("decisoes/material", DEC.get("material")), ("medido/arquivo", M.get("arquivo")),
                         ("cotas do contrato", D.get("cotas")), ("medido/fenda_no_land", FEND.get("area_mm2")),
                         ("medido/boca_saida", BOCA.get("largura_mm")),
                         ("medido/boca_entrada", ENTR.get("abertura_mm")),
                         ("montagem/saida_além_da_face_do_nariz_mm", PROT)) if v is None or v == ""]
if FALTAM:
    raise SystemExit("o pacote nao traz estas chaves: %s - nao chuto" % ", ".join(FALTAM))


def cota(sub):
    """a cota do contrato cujo item contem `sub`: (nominal, tolerancia resumida, medicao)"""
    for c in D["cotas"]:
        if sub.lower() in str(c["item"]).lower():
            tol = str(c["tolerancia"]).split("(")[0].strip().rstrip(";").strip()
            return float(c["nominal"]), tol, str(c.get("medicao", ""))
    raise SystemExit("o pacote nao tem a cota com o item contendo %r" % sub)


FRAG_NORMA = str(ACO["norma"]).split(":")[0].strip()
FRAG_ENTREGA = str(ACO["norma"]).rsplit("(", 1)[-1].rstrip(")").strip()
DUZ = [c.strip() for c in str(ACO["dureza"]).split(";")]


def novo_doc():
    doc = ezdxf.new(SERIE, setup=True)
    if SERIE == "R2000":
        # AC1015 nao guarda Unicode: sem dizer a pagina de codigo, o ezdxf escapa tudo em \U+XXXX
        # e o CAD antigo mostra o escape. cp1252 escreve o 0 e o ± como byte simples, como sempre foi.
        doc.header["$DWGCODEPAGE"] = "ANSI_1252"
    doc.header["$INSUNITS"] = 4
    doc.header["$MEASUREMENT"] = 1
    doc.header["$LTSCALE"] = 1.0
    for nome, cor, lt, lw in [("PERFIL", 7, "Continuous", 50), ("CANAL", 1, "Continuous", 35),
                              ("EIXO", 8, "CENTER2", 13), ("COTAS", 5, "Continuous", 18),
                              ("TABELA", 7, "Continuous", 13), ("MATERIAL", 1, "Continuous", 70),
                              ("NOTAS", 7, "Continuous", 15), ("CARIMBO", 7, "Continuous", 25)]:
        doc.layers.add(nome, color=cor, linetype=lt, lineweight=lw)
    desejado = {"dimscale": 1.0, "dimtxt": 3.5, "dimasz": 2.5, "dimexo": 0.9, "dimexe": 1.5,
                "dimgap": 0.9, "dimdec": 2, "dimtad": 1, "dimjust": 0, "dimclrd": 5, "dimclre": 5,
                "dimclrt": 5, "dimdli": 5.0, "dimaunit": 0, "dimtih": 0, "dimazin": 2}
    est = doc.dimstyles.new("COTAS")
    recusos = []
    for k, v in desejado.items():
        try:
            est.dxf.set(k, v)
        except Exception:
            recusos.append(k)
    if recusos:
        print("   aviso: o DIMSTYLE recusou %s (vale o padrao do ezdxf)" % ", ".join(recusos))
    return doc


def main():
    est = sorted(ALV["estagios"], key=lambda e: e[1])
    L, chan, land, raio = ALV["comprimento"], ALV["chanfro"], ALV["land"], ALV["raio_borda"]
    a_fd, w_fd = ALV["abertura_fenda"], ALV["largura_fenda"]
    D_ent, b_saida = ALV["boca_entrada"], ALV["boca_saida"]
    x_fim_land, x_ini_land = L - chan, L - chan - land
    r = [e[0] / 2.0 for e in est]
    xz = [e[1] for e in est] + [L]
    R_in, R_out = D_ent / 2.0, a_fd / 2.0
    w_out, a_out = b_saida[0] / 2.0, b_saida[1] / 2.0
    med_est = M.get("estagios_medidos", [])
    if len(med_est) != 3:
        raise SystemExit("esperava 3 estagios medidos no STEP, achei %d" % len(med_est))

    doc = novo_doc()
    msp = doc.modelspace()
    estouro = []

    def dim(base, p1, p2, rotulo, ang=0.0, destaque=False):
        ov = {"dimtxt": 6.0, "dimasz": 3.0, "dimclrt": 1, "dimclrd": 1, "dimclre": 1,
              "dimdli": 8.0} if destaque else {}
        ent = msp.add_linear_dim(base=base, p1=p1, p2=p2, angle=ang, text=tx(rotulo),
                                 dimstyle="COTAS", override=ov)
        ent.dimension.dxf.layer = "COTAS"
        ent.render()
        larg = len(rotulo) * ov.get("dimtxt", 3.5) * FATOR
        if larg > 130.0:
            estouro.append("texto de cota com %.0f mm: %s" % (larg, rotulo))

    def texto(t, x, y, h, camada="NOTAS", cor=None, limite=None):
        t = tx(t)
        if limite:
            if len(t) * h * FATOR > limite:
                estouro.append("linha de %.0f mm nao cabe em %.0f mm: %s"
                               % (len(t) * h * FATOR, limite, t[:44]))
            if x + len(t) * h * FATOR > B[2] + 0.01:
                estouro.append("texto sai da moldura em x: %s" % t[:44])
        a = {"layer": camada, "height": h}
        if cor is not None:
            a["color"] = cor
        msp.add_text(t, dxfattribs=a).set_placement((x, y), align=TextEntityAlignment.BOTTOM_LEFT)

    def linhas_de(t, h, largura):
        return sum(math.ceil(max(1, len(b)) / max(1.0, largura / (h * FATOR))) for b in t.split("\\P"))

    def paragrafo(t, x, y, h, largura, caixa, camada="NOTAS", cor=None):
        t = tx(t)
        nl = linhas_de(t, h, largura)
        if nl * h * 1.5 > caixa:
            estouro.append("MTEXT com %d linhas precisa de %.0f mm e a caixa tem %.0f: %s"
                           % (nl, nl * h * 1.5, caixa, t[:40]))
        m = msp.add_mtext(t, dxfattribs={"layer": camada, "char_height": h, "attachment_point": 1})
        if cor is not None:
            m.dxf.color = cor
        m.set_location((x, y))
        m.dxf.width = largura
        return nl

    # ============================================================ 1 · SECAO NO PLANO DA ABERTURA 1:1
    perf = [(X0 + x, YV + y) for x, y in [(0, -r[0]), (xz[1], -r[0]), (xz[1], -r[1]), (xz[2], -r[1]),
                                          (xz[2], -r[2]), (L, -r[2]), (L, r[2]), (xz[2], r[2]),
                                          (xz[2], r[1]), (xz[1], r[1]), (xz[1], r[0]), (0, r[0])]]
    can = [(X0 + x, YV + y) for x, y in [(0, -R_in), (x_ini_land, -R_out), (x_fim_land, -R_out),
                                         (L, -a_out), (L, a_out), (x_fim_land, R_out),
                                         (x_ini_land, R_out), (0, R_in)]]
    msp.add_lwpolyline(perf, close=True, dxfattribs={"layer": "PERFIL"})
    msp.add_lwpolyline(can, close=True, dxfattribs={"layer": "CANAL"})
    msp.add_line((X0 - 12, YV), (X0 + L + 12, YV), dxfattribs={"layer": "EIXO"})
    dim((X0 - 30, YV), (X0, YV - r[0]), (X0, YV + r[0]), "Ø%s ±0,5" % br(2 * r[0]), ang=90)
    dim((X0 - 15, YV), (X0, YV - R_in), (X0, YV + R_in), "Ø%s +0,05/-0,00" % br(D_ent), ang=90)
    dim((X0 + L + 15, YV), (X0 + L, YV - r[2]), (X0 + L, YV + r[2]), "Ø%s ±0,5" % br(2 * r[2]), ang=90)
    dim((X0 + L + 28, YV), (X0 + xz[1], YV - r[1]), (X0 + xz[1], YV + r[1]), "Ø%s ±0,5" % br(2 * r[1]),
        ang=90)
    dim((X0 + L / 2.0, YV - r[0] - 12), (X0, YV - r[0]), (X0 + L, YV - r[0]),
        "comprimento %s ±0,5" % br(L))
    texto("SEÇÃO NO PLANO DA ABERTURA · 1:1 · funil em spline (a tabela dá o resto)",
          X0 - 30, YV + r[0] + 6.0, 3.4, limite=190)

    # ============================================================ 2 · FACE DE SAIDA 1:1
    def stadium(cx, cy, meio_eixo, meio_altura, camada):
        """fenda de ponta arredondada: duas retas + dois semicirculos (bulge = 1)"""
        msp.add_lwpolyline([(cx - meio_eixo + meio_altura, cy - meio_altura, 0.0),
                            (cx + meio_eixo - meio_altura, cy - meio_altura, 1.0),
                            (cx + meio_eixo - meio_altura, cy + meio_altura, 0.0),
                            (cx - meio_eixo + meio_altura, cy + meio_altura, 1.0)],
                           close=True, format="xyb", dxfattribs={"layer": camada})

    msp.add_circle((CFC, YV), r[2], dxfattribs={"layer": "PERFIL"})
    stadium(CFC, YV, w_out, a_out / 2.0, "PERFIL")
    stadium(CFC, YV, w_fd / 2.0, a_fd / 2.0, "CANAL")
    msp.add_line((CFC - r[2] - 6, YV), (CFC + r[2] + 6, YV), dxfattribs={"layer": "EIXO"})
    msp.add_line((CFC, YV - r[2] - 6), (CFC, YV + r[2] + 6), dxfattribs={"layer": "EIXO"})
    dim((CFC, YV - r[2] - 11), (CFC - w_fd / 2.0, YV), (CFC + w_fd / 2.0, YV),
        "largura %s ±0,05" % br(w_fd))
    texto("FACE DE SAÍDA · 1:1", CFC - r[2] - 12, YV + r[2] + 7.0, 3.4, limite=90)
    texto("boca do chanfro %s × %s · fenda %s × %s" % (br(b_saida[0]), br(b_saida[1]), br(w_fd),
                                                        br(a_fd, 3)), CFC - r[2] - 12, YV + r[2] + 3.0,
          2.6, limite=100)

    # ============================================================ 3 · DETALHE A 6:1 (fim do canal)
    b = ESA
    ha, hb = (a_fd / 2.0) * b, (b_saida[1] / 2.0) * b
    xa = DXA
    xb, xc = DXA + land * b, DXA + (L - x_ini_land) * b
    msp.add_lwpolyline([(xa, YV - ha), (xb, YV - ha), (xc, YV - hb), (xc, YV + hb), (xb, YV + ha),
                        (xa, YV + ha)], close=True, dxfattribs={"layer": "CANAL"})
    msp.add_lwpolyline([(xa, YV + ha + 13), (xa, YV + ha), (xb, YV + ha), (xc, YV + hb),
                        (xc, YV + hb + 13)], dxfattribs={"layer": "PERFIL"})
    msp.add_lwpolyline([(xa, YV - ha - 13), (xa, YV - ha), (xb, YV - ha), (xc, YV - hb),
                        (xc, YV - hb - 13)], dxfattribs={"layer": "PERFIL"})
    msp.add_line((xa - 6, YV), (xc + 6, YV), dxfattribs={"layer": "EIXO"})
    dim((xa - 16, YV), (xa - 4, YV - ha), (xa - 4, YV + ha), br(a_fd, 3), ang=90, destaque=True)
    dim(((xa + xb) / 2.0, YV - ha - 14), (xa, YV - ha - 4), (xb, YV - ha - 4),
        "land %s ±0,05" % br(land))
    texto("DETALHE A · 6:1", xa - 6, YV + hb + 24.0, 3.6, limite=60)
    texto("ABERTURA %s +0,010/-0,000" % br(a_fd, 3), xa - 6, YV + hb + 16.0, 4.6, "COTAS", cor=1,
          limite=110)
    texto("chanfro %s × 45° · face de saída em x = %s" % (br(chan), br(L)), xa - 6, YV - ha - 30.0, 2.6,
          limite=118)
    texto("funil (spline) vem da esquerda; corte em x = %s" % br(x_ini_land), xa - 6, YV - ha - 35.0,
          2.6, limite=118)

    # ============================================================ 4 · MATERIAL
    texto("MATERIAL: " + str(DEC["material"]).upper() + " · SEM PVD · SEM DLC · SEM OUTRO AÇO",
          B[0] + 4, FOLHA[1] - 25, 7.5, "MATERIAL", limite=B[2] - B[0] - 8)
    msp.add_lwpolyline([(B[0] + 2, FOLHA[1] - 28), (B[2] - 2, FOLHA[1] - 28)],
                       dxfattribs={"layer": "MATERIAL", "const_width": 0.9, "color": 1})
    paragrafo("Norma: " + str(ACO["norma"]) + "\\P"
              + "Dureza e tratamento: " + str(ACO["dureza"]) + "\\P"
              + "Troca de aço só com desenho novo assinado por nós + certificado EN 10204 3.1 do lote "
              "fornecido · marcação a laser na face traseira: JONATHA v27.0 · EX-031 · 1045 · rev. " + REV,
              B[0] + 4, FOLHA[1] - 31, 3.2, B[2] - B[0] - 10, 22.0, "MATERIAL")

    # ============================================================ 5 · TABELA DE ANATOMIA
    txx0, ty0, tx1, ty1 = TABELA
    texto("ANATOMIA DA PEÇA · cota de contrato e o que a medição no STEP achou", txx0, ty1 + 4.5, 3.6,
          "TABELA", limite=tx1 - txx0 + 6)
    msp.add_line((txx0 - 2, ty1 + 2.0), (tx1, ty1 + 2.0), dxfattribs={"layer": "TABELA"})
    msp.add_line((txx0 - 2, ty1 - 3.5), (tx1, ty1 - 3.5), dxfattribs={"layer": "TABELA"})
    for cx, rot in zip(COL, ("REGIÃO", "COTA", "MEDIDO NO STEP")):
        texto(rot, cx, ty1 - 2.8, 2.8, "TABELA", cor=8)
    n1, t1, _ = cota("1º estágio")
    n2, t2, _ = cota("2º estágio")
    n3, t3, _ = cota("3º estágio")
    nb, tb, _ = cota("Boca de entrada")
    nl_, tl_, _ = cota("land paralelo")
    nc, tc, _ = cota("Chanfro de saída")
    na, ta, _ = cota("Abertura da fenda")
    nr, tr, _ = cota("Raio das bordas")
    nf, tf, _ = cota("Raio no fundo")
    nx, tx_, _ = cota("Excentricidade")
    np_, tp, _ = cota("Comprimento total")
    nd1, td1, _ = cota("degrau 1")
    nd2, td2, _ = cota("degrau 2")
    npl, tpl, _ = cota("Ângulo de saída")
    # a tolerancia do raio vem escrita como frase ("R 3,0 +/-0,5, sem aresta viva"): separar sem
    # quebrar a virgula decimal - se o texto mudar de formato, a linha inteira vira a cota
    if ", sem " in tf:
        raio_juncao = (tf.split(", sem ")[0].strip(), "sem " + tf.split(", sem ")[1].strip())
    else:
        raio_juncao = (tf, "-")
    linhas = [
        ("face de entrada (datum A)", "plana, " + tpl.split(" e ")[0], "x = 0,00"),
        ("Ø dos 3 estágios", "Ø%s / Ø%s / Ø%s %s" % (br(n1, 0), br(n2, 0), br(n3, 0), t1),
         "%s / %s / %s" % (br(med_est[0]["D"], 3), br(med_est[1]["D"], 3), br(med_est[2]["D"], 3))),
        ("degraus 1-2 e 2-3", "%s %s · %s %s" % (br(nd1), td1, br(nd2), td2),
         "medidos em %s / %s" % (br(med_est[0]["z"][1], 2), br(med_est[1]["z"][1], 2))),
        ("coaxialidade 2 e 3 em A", tx_, "-"),
        ("boca de entrada do canal", "Ø%s %s" % (br(nb), tb),
         "%s (corte em x = %s)" % (br(ENTR["largura_mm"], 4), br(ENTR["z"]))),
        ("funil (spline do STEP)", "Ø%s » %s" % (br(nb), br(a_fd, 3)),
         "de x = %s a %s" % (br(ENTR["z"]), br(x_ini_land))),
        ("raio na junção funil-fenda", *raio_juncao),
        ("land calibrado", "%s %s  de %s a %s" % (br(nl_), tl_, br(x_ini_land), br(x_fim_land)),
         "%s caras · seção %s mm²" % (CAN.get("caras_do_land", "-"), br(FEND["area_mm2"], 4))),
        ("fenda - abertura", "%s %s" % (br(na, 3), ta),
         "%s em z = %s" % (br(FEND["abertura_mm"], 3), br(FEND["z"]))),
        ("fenda - largura", "%s %s" % (br(w_fd), cota("Largura da fenda")[1]),
         br(FEND["largura_mm"], 4)),
        ("fenda - ponta (as duas)", "R %s %s" % (br(nr), tr), "meia-círculo, aresta viva"),
        ("chanfro de saída", tc.split("/")[0].strip(),
         "boca %s × %s (med %s)" % (br(b_saida[0]), br(b_saida[1]), br(BOCA["largura_mm"], 4))),
        ("comprimento total", "%s %s" % (br(np_), tp), "%s" % br(M["comprimento_mm"], 3)),
    ]
    topo = ty1 - 6.5
    fundo = ty0 + 22.0
    passo = (topo - fundo) / len(linhas)
    if passo < 4.2:
        raise SystemExit("tabela nao cabe: passo %.2f mm para %d linhas" % (passo, len(linhas)))
    for i, (a, c, m) in enumerate(linhas):
        base = topo - passo * (i + 1)
        destaque = a.startswith("fenda - abertura")
        for cx, w, val in zip(COL, COLW, (a, c, m)):
            texto(val, cx, base + 2.0, 2.5, "TABELA", cor=(1 if destaque else None), limite=w)
        msp.add_line((txx0 - 2, base), (tx1, base), dxfattribs={"layer": "TABELA"})
    texto("traço (-) = cota de projeto sem medição própria no STEP", txx0, ty0 + 16.5, 2.4, "TABELA",
          limite=tx1 - txx0)
    paragrafo("FABRICAÇÃO (o resto está no 03_SEQUENCIA_DE_USINAGEM.md): fenda a fio EDM pelo Ø%s, de um "
              "lado só, depois do T.T.; medir a abertura antes e depois; sem furo, flange, rosca, pino ou "
              "linha de partição - aperto pelo collete EX-031; certificado EN 10204 3.1 e relatório "
              "dimensional destas cotas." % br(D_ent), txx0, ty0 + 13.5, 2.6, tx1 - txx0 + 2, 15.0, "NOTAS")

    # ============================================================ 6 · CARIMBO
    kx0, ky0, kx1, ky1 = CARIMBO
    rot_x = kx0 + 52.0
    lim = kx1 - rot_x - 4
    msp.add_lwpolyline([(kx0, ky0), (kx1, ky0), (kx1, ky1), (kx0, ky1)], close=True,
                       dxfattribs={"layer": "CARIMBO"})
    cab = ky1 - 14.0
    fileiras = [("MATERIAL", cab, cab - 18.0), ("COTA CRÍTICA", cab - 18.0, cab - 30.0),
                 ("GEOMETRIA", cab - 30.0, cab - 48.0), ("MONTAGEM", cab - 48.0, cab - 60.0),
                 ("FONTE", cab - 60.0, cab - 72.0), ("ACEITAÇÃO", cab - 72.0, ky0)]
    for _, _t, ba in fileiras:
        msp.add_line((kx0, ba), (kx1, ba), dxfattribs={"layer": "CARIMBO"})
    msp.add_line((kx0, cab), (kx1, cab), dxfattribs={"layer": "CARIMBO"})
    msp.add_line((rot_x, cab), (rot_x, ky0), dxfattribs={"layer": "CARIMBO"})
    texto("MATRIZ DE EXTRUSÃO · JONATHA v27.0 · rev. %s" % REV, kx0 + 3, cab + 7.5, 4.2, "CARIMBO",
          limite=kx1 - kx0 - 6)
    texto("peça única · 1 peça · escala 1:1 e 6:1 · mm · A3 paisagem", kx0 + 3, cab + 1.5, 2.6,
          "CARIMBO", limite=kx1 - kx0 - 6)
    for rt, _t, ba in fileiras:
        texto(rt, kx0 + 3, ba + 11.0 if rt == "MATERIAL" else ba + 7.0, 2.6, "CARIMBO", cor=8)
    texto("AÇO 1045", rot_x + 1, fileiras[0][2] + 8.5, 6.0, "CARIMBO", cor=1, limite=lim)
    paragrafo(FRAG_NORMA + " · " + FRAG_ENTREGA + " · " + DUZ[0] + " · sem PVD, sem DLC", rot_x + 1,
              fileiras[0][2] + 6.0, 2.6, lim, 7.0, "CARIMBO")
    texto("abertura %s %s · largura %s %s" % (br(na, 3), ta, br(w_fd), cota("Largura da fenda")[1]),
          rot_x + 1, fileiras[1][2] + 6.0, 3.0, "CARIMBO", cor=1, limite=lim)
    paragrafo("%d sólido, %d faces, %d arestas, B-rep válido · envelope %s × %s × %s · aço %s mm³ · "
              "%s kg" % (M["solidos"], M["faces"], M["arestas"], br(M["envelope_x_mm"]),
                         br(M["envelope_y_mm"]), br(L), br(M["volume_aco_mm3"], 1), br(M["massa_kg"], 4)),
              rot_x + 1, fileiras[2][1] - 2.5, 2.6, lim, 18.0 - 5.0, "CARIMBO")
    paragrafo("canal %s mm³ · faceada ao nariz do EX-031 · protrusão medida %s mm"
              % (br(M["volume_canal_mm3"], 1), br(PROT)), rot_x + 1, fileiras[3][1] - 2.5, 2.6, lim,
              12.0 - 4.0, "CARIMBO")
    paragrafo("as 8 cotas e a tabela são medição no STEP" + chr(92) + "P" + str(M["arquivo"]),
              rot_x + 1,
              fileiras[4][1] - 2.0, 2.5, lim, 12.0 - 3.0, "CARIMBO")
    paragrafo("NDA antes de circular esta folha · sha256 do STEP %s..." % str(M["sha256"])[:12],
              rot_x + 1, fileiras[5][1] - 2.0, 2.5, lim, 12.0 - 3.0, "CARIMBO")

    texto("se o desenho e o STEP discordarem, vale o STEP · vírgula decimal padrão BR · o símbolo Ø só "
          "aparece se a fonte tiver Latin-1 (trocar para Arial)", B[0] + 4, B[1] - 4.0, 2.5, "NOTAS",
          limite=B[2] - B[0] - 8)
    texto("procedência da cota: " + str(ACO["grupo"]), B[0] + 4, B[1] - 7.5, 2.5, "NOTAS",
          limite=B[2] - B[0] - 8)

    if estouro:
        raise SystemExit("estouro de caixa no DXF (%d): %s" % (len(estouro), " | ".join(estouro)))

    msp.add_lwpolyline([(B[0], B[1]), (B[2], B[1]), (B[2], B[3]), (B[0], B[3])], close=True,
                       dxfattribs={"layer": "CARIMBO"})
    destino = os.path.join(RAIZ, PACOTE, DXF + SUFIXO + ".dxf")
    doc.saveas(destino, encoding=("cp1252" if SERIE == "R2000" else "utf-8"))
    print("gravado:", destino, os.path.getsize(destino), "bytes ·", len(msp), "entidades")

    auditado = ezdxf.readfile(destino).audit()
    print("auditoria: %d erro(s), %d correção(ões)" % (len(auditado.errors), len(auditado.fixes)))
    if auditado.errors:
        raise SystemExit("DXF com erro de estrutura - não publico")

    reabre = ezdxf.readfile(destino)
    cotas = [e.dxf.text for e in reabre.modelspace().query("DIMENSION")]
    precisa = ["Ø%s ±0,5" % br(2 * r[0]), "Ø%s ±0,5" % br(2 * r[1]), "Ø%s ±0,5" % br(2 * r[2]),
                "Ø%s +0,05/-0,00" % br(D_ent), "comprimento %s ±0,5" % br(L), "land %s ±0,05" % br(land),
                br(a_fd, 3), "largura %s ±0,05" % br(w_fd)]
    falta = [p for p in precisa if p not in cotas]
    print("cotas: %d · conferidas com o JSON: %d/%d · tabela: %d linhas"
          % (len(cotas), len(precisa) - len(falta), len(precisa), len(linhas)))
    if falta:
        raise SystemExit("cota sumiu no round-trip do DXF: %s" % falta)
    tudo = cotas + [e.dxf.text for e in reabre.modelspace().query("TEXT")]
    print("glifos acima de Latin-1:", sorted({c for t in tudo for c in t if ord(c) > 0xFF}) or "nenhum")

    # nenhuma etiqueta em cima da outra: caixa estimada por texto, intersecao > 0,8 mm nas duas direcoes
    caixas = []
    for e in reabre.modelspace():
        if e.dxftype() not in ("TEXT", "MTEXT"):
            continue
        at = e.dxfattribs()
        t = str(at.get("text", ""))
        h = float(at.get("char_height", at.get("height", 3.0)) or 3.0)
        x, y = e.dxf.insert.x, e.dxf.insert.y
        if e.dxftype() == "MTEXT":
            w = float(at.get("width", 0.0) or 0.0) or len(t) * h * FATOR
            nl = sum(math.ceil(max(1, len(b)) / max(1.0, w / (h * FATOR))) for b in t.split("\\P"))
            caixas.append((x, y - nl * h * 1.5, x + w, y + h * 0.4, t))
        else:
            caixas.append((x, y, x + len(t) * h * FATOR, y + h * 1.2, t))
    choques = []
    for i1 in range(len(caixas)):
        for i2 in range(i1 + 1, len(caixas)):
            ax0, ay0, ax1, ay1, at1 = caixas[i1]
            bx0, by0, bx1, by1, bt1 = caixas[i2]
            ov_x = min(ax1, bx1) - max(ax0, bx0)
            ov_y = min(ay1, by1) - max(ay0, by0)
            if ov_x > 0.8 and ov_y > 0.8:
                choques.append("%.0f×%.0f mm: %r / %r" % (ov_x, ov_y, at1[:26], bt1[:26]))
    print("textos sobrepostos:", len(choques))
    if choques:
        raise SystemExit("choque de texto no DXF: %s" % " | ".join(choques[:6]))

    xs, ys = [], []
    for e in reabre.modelspace():
        t = e.dxftype()
        if t == "LWPOLYLINE":
            pts = e.get_points("xy")
            xs += [p[0] for p in pts]; ys += [p[1] for p in pts]
        elif t == "LINE":
            xs += [e.dxf.start.x, e.dxf.end.x]; ys += [e.dxf.start.y, e.dxf.end.y]
        elif t == "CIRCLE":
            xs += [e.dxf.center.x - e.dxf.radius, e.dxf.center.x + e.dxf.radius]
            ys += [e.dxf.center.y - e.dxf.radius, e.dxf.center.y + e.dxf.radius]
        elif t in ("TEXT", "MTEXT"):
            at = e.dxfattribs()
            h = float(at.get("char_height", at.get("height", 3.0)) or 3.0)
            comp = float(at.get("width", 0.0) or 0.0) or len(at.get("text", "")) * h * FATOR
            xs += [e.dxf.insert.x, e.dxf.insert.x + comp]
            ys += [e.dxf.insert.y, e.dxf.insert.y + h * 1.2]
    chec = [(min(xs), B[0], B[2], "x min"), (max(xs), B[0], B[2], "x max"),
            (min(ys), B[1] - 12.5, B[3], "y min"), (max(ys), B[1] - 12.5, B[3], "y max")]
    foroo = ["%s = %s fora de %s..%s" % (n, br(v, 1), br(lo, 1), br(hi, 1)) for v, lo, hi, n in chec
             if v < lo or v > hi]
    print("conteúdo: x %s..%s · y %s..%s" % (br(min(xs), 1), br(max(xs), 1), br(min(ys), 1), br(max(ys), 1)))
    if foroo:
        raise SystemExit("conteúdo fora da moldura: %s" % " | ".join(foroo))

    if SUFIXO:                       # o gemeo AC1015 e a mesma folha: preview so na serie principal
        print("preview pulado no gume %s (a folha e identica a serie principal)" % SUFIXO)
        return

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from ezdxf.addons.drawing import RenderContext, Frontend
        from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
        fig = plt.figure(figsize=(FOLHA[0] / 25.4, FOLHA[1] / 25.4))
        ax = fig.add_axes([0.004, 0.004, 0.992, 0.992])
        ax.set_facecolor("#15151e")
        Frontend(RenderContext(reabre), MatplotlibBackend(ax)).draw_layout(reabre.modelspace(), finalize=True)
        ax.set_axis_off()
        ax.set_aspect("equal", adjustable="box")
        ax.set_xlim(B[0] - 4, B[2] + 4)
        ax.set_ylim(B[1] - 11, B[3] + 4)
        fig.savefig(destino[:-4] + "_PREVIEW.png", dpi=200, facecolor="#15151e")
        fig.savefig(destino[:-4] + "_PREVIEW.pdf", facecolor="#15151e")
        plt.close(fig)
        print("preview:", os.path.basename(destino)[:-4] + "_PREVIEW.png",
              os.path.getsize(destino[:-4] + "_PREVIEW.png"), "bytes")
    except Exception as exc:
        print("preview nao gerado (%s: %s) - o DXF em si esta OK" % (type(exc).__name__, exc))


if __name__ == "__main__":
    try:
        main()
    except SystemExit as exc:
        # nao deixa artefato reprovado na pasta do pacote
        for sufixo in (".dxf", "_PREVIEW.png", "_PREVIEW.pdf"):   # nada reprovado fica na pasta
            c = os.path.join(RAIZ, PACOTE, DXF + SUFIXO + sufixo)
            if os.path.exists(c):
                os.remove(c)
        raise SystemExit("folha reprovada (nada publicado em %s/%s): %s" % (PACOTE, DXF, exc))
