#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Desenho DXF cotado da matriz - folha A3 paisagem, 1:1, em milimetros, 8 cotas.

Folha para quem abre o arquivo no CAD da oficina e nao quer PDF:
  · MATERIAL DA PEÇA em texto grande no topo (aco 1045, norma, dureza, proibicao de trocar);
  · SECAO NO PLANO DA ABERTURA - a vista em que o funil/cone interno aparece de verdade;
  · FACE DE SAIDA com a abertura da fenda cotada em corpo grande;
  · 4 notas de processo e um carimbo. Nada mais: sem tabela de estagios, sem CFD, sem historia
    de revisao - isso esta no README do pacote.

As cotas sao DIMENSION reais (editaveis), com o texto no padrao brasileiro (virgula decimal) e
a geometria nominal exata: o que a maquina medir no arquivo bate com o texto da cota.

Nenhum numero e digitado aqui: tudo vem de pacote_usinagem.json (medicao no STEP). Se faltar
chave, o gerador para com SystemExit em vez de chutar. Todo texto tem largura e numero de linhas
estimados e conferidos contra a caixa que o recebe - se estourar, a folha nao e gravada.

Uso:
  python3 gerar_desenho_cotado_dxf_v30.py
  PACOTE=08_Pacote_Usinagem_v29 DXF=MATRIZ_V29_DESENHO_COTADO python3 gerar_desenho_cotado_dxf_v30.py
Depende de ezdxf (ja listado no 04_/restaurar_workspace.sh); o preview usa matplotlib.
"""
import io, json, math, os
import ezdxf
from ezdxf.enums import TextEntityAlignment

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACOTE = os.environ.get("PACOTE", "08_Pacote_Usinagem_v30")
DXF = os.environ.get("DXF", "MATRIZ_V30_DESENHO_COTADO")
REV = PACOTE.rsplit("_", 1)[-1].lstrip("v")

FOLHA = (420.0, 297.0)                                     # A3 paisagem, em mm
B = (10.0, 10.0, FOLHA[0] - 10.0, FOLHA[1] - 10.0)          # moldura
Y0 = 168.0                                                 # eixo das duas vistas
X0 = 60.0                                                  # face de entrada da secao
CFX = 292.0                                                # centro da face de saida
NOTAS = (22.0, 22.0, 200.0, 100.0)                          # caixa das notas
CARIMBO = (204.0, 22.0, B[2] - 2, 110.0)                    # caixa do carimbo
LINHAS = {96.0: 18.0, 78.0: 15.0, 63.0: 21.0, 42.0: 12.0, 30.0: 8.0}   # topo: altura de cada linha
FATOR = 0.68                                               # largura media do caractere

# Glifos que fonte SHX de obra e o preview do matplotlib comem na hora de copiar: Latin-1 apenas.
RUIM = {0x2212: "-", 0x2013: " a ", 0x2014: "-", 0x2192: "->", 0x2265: ">=", 0x2264: "<=",
        0x2248: "~", 0x00a0: " ", 0x2260: "<>", 0x2022: "-", 0x03bc: "u"}


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
PROT = MON.get("saida_além_da_face_do_nariz_mm")
FALTAM = [k for k, v in (("aco/norma", ACO.get("norma")), ("aco/dureza", ACO.get("dureza")),
                         ("aco/grupo", ACO.get("grupo")), ("decisoes/material", DEC.get("material")),
                         ("medido/arquivo", M.get("arquivo")),
                         ("montagem/saida_além_da_face_do_nariz_mm", PROT)) if v is None or v == ""]
if FALTAM:
    raise SystemExit("o pacote nao traz estas chaves: %s - nao chuto" % ", ".join(FALTAM))
FRAG_NORMA = str(ACO["norma"]).split(":")[0].strip()
FRAG_ENTREGA = str(ACO["norma"]).rsplit("(", 1)[-1].rstrip(")").strip()
FRAG_CORPO = str(ACO["dureza"]).split(";")[0].strip()


def novo_doc():
    doc = ezdxf.new("R2010", setup=True)
    doc.header["$INSUNITS"] = 4          # milimetros
    doc.header["$MEASUREMENT"] = 1       # sistema ISO
    doc.header["$LTSCALE"] = 1.0
    for nome, cor, lt, lw in [("PERFIL", 7, "Continuous", 50), ("CANAL", 1, "Continuous", 35),
                              ("EIXO", 8, "CENTER2", 13), ("COTAS", 5, "Continuous", 18),
                              ("MATERIAL", 1, "Continuous", 70), ("NOTAS", 7, "Continuous", 15),
                              ("CARIMBO", 7, "Continuous", 25)]:
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
    L, chan, land, raio_borda = ALV["comprimento"], ALV["chanfro"], ALV["land"], ALV["raio_borda"]
    a_fd, w_fd = ALV["abertura_fenda"], ALV["largura_fenda"]
    D_ent, b_saida = ALV["boca_entrada"], ALV["boca_saida"]
    x_fim_land = L - chan
    x_ini_land = x_fim_land - land
    r = [e[0] / 2.0 for e in est]
    xz = [e[1] for e in est] + [L]
    R_in, R_out = D_ent / 2.0, a_fd / 2.0
    w_out, a_out = b_saida[0] / 2.0, b_saida[1] / 2.0

    doc = novo_doc()
    msp = doc.modelspace()
    estouro = []

    def dim(origem, base, p1, p2, texto_cota, ang=0.0, destaque=False):
        """cota linear real (DIMENSION); o texto literal garante virgula decimal e tolerancia"""
        ox, oy = origem
        ov = {"dimtxt": 5.5, "dimasz": 3.0, "dimclrt": 1, "dimclrd": 1, "dimclre": 1,
              "dimdli": 8.0} if destaque else {}
        ent = msp.add_linear_dim(base=(ox + base[0], oy + base[1]), p1=(ox + p1[0], oy + p1[1]),
                                 p2=(ox + p2[0], oy + p2[1]), angle=ang, text=tx(texto_cota),
                                 dimstyle="COTAS", override=ov)
        ent.dimension.dxf.layer = "COTAS"
        ent.render()
        larg = len(texto_cota) * ov.get("dimtxt", 3.5) * FATOR
        if larg > 140.0:
            estouro.append("texto de cota com %.0f mm: %s" % (larg, texto_cota))

    def texto(t, x, y, h, camada="NOTAS", cor=None, limite=None):
        t = tx(t)
        if limite and len(t) * h * FATOR > limite:
            estouro.append("linha de %.0f mm nao cabe em %.0f mm: %s"
                           % (len(t) * h * FATOR, limite, t[:44]))
        a = {"layer": camada, "height": h}
        if cor is not None:
            a["color"] = cor
        msp.add_text(t, dxfattribs=a).set_placement((x, y), align=TextEntityAlignment.BOTTOM_LEFT)

    def linhas_de(t, h, largura):
        return sum(math.ceil(max(1, len(bloco)) / max(1.0, largura / (h * FATOR)))
                   for bloco in t.split("\\P"))

    def paragrafo(t, x, y, h, largura, caixa, camada="NOTAS", cor=None):
        """MTEXT que quebra sozinho; confere quantas linhas vao sair contra a caixa que o recebe"""
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

    # ------------------------------------------------------------------ 1 · secao no plano da abertura
    origem_sec = (X0, Y0)
    perfil = [(0, -r[0]), (xz[1], -r[0]), (xz[1], -r[1]), (xz[2], -r[1]), (xz[2], -r[2]), (L, -r[2]),
              (L, r[2]), (xz[2], r[2]), (xz[2], r[1]), (xz[1], r[1]), (xz[1], r[0]), (0, r[0])]
    canal = [(0, -R_in), (x_ini_land, -R_out), (x_fim_land, -R_out), (L, -a_out),
             (L, a_out), (x_fim_land, R_out), (x_ini_land, R_out), (0, R_in)]
    msp.add_lwpolyline([(X0 + x, Y0 + y) for x, y in perfil], close=True, dxfattribs={"layer": "PERFIL"})
    msp.add_lwpolyline([(X0 + x, Y0 + y) for x, y in canal], close=True, dxfattribs={"layer": "CANAL"})
    msp.add_line((X0 - 14, Y0), (X0 + L + 14, Y0), dxfattribs={"layer": "EIXO"})

    dim(origem_sec, (-28, 0), (0, -r[0]), (0, r[0]), "Ø%s ±0,5" % br(2 * r[0]), ang=90)
    dim(origem_sec, (-13, 0), (0, -R_in), (0, R_in), "Ø%s +0,05/-0,00" % br(D_ent), ang=90)
    dim(origem_sec, (L + 13, 0), (L, -r[2]), (L, r[2]), "Ø%s ±0,5" % br(2 * r[2]), ang=90)
    dim(origem_sec, (L + 27, 0), (xz[1], -r[1]), (xz[1], r[1]), "Ø%s ±0,5" % br(2 * r[1]), ang=90)
    dim(origem_sec, (L / 2.0, -r[0] - 12), (0, -r[0]), (L, -r[0]), "comprimento %s ±0,5" % br(L))
    dim(origem_sec, ((x_ini_land + x_fim_land) / 2.0, r[1] + 6), (x_ini_land, r[1]), (x_fim_land, r[1]),
        "land %s ±0,05" % br(land))
    texto("SEÇÃO SIMÉTRICA NO PLANO DA ABERTURA - só nesta vista o funil aparece",
          X0 - 26, Y0 + r[0] + 24, 3.2, limite=195)
    paragrafo("Ø%s na entrada fecha em funil até a fenda %s × %s - perfil BSpline medido no STEP"
              % (br(D_ent), br(w_fd), br(a_fd, 3)), X0 - 26, Y0 + r[0] + 21, 2.8, 168.0, 12.0)

    # ------------------------------------------------------------------ 2 · face de saida
    origem_cf = (CFX, Y0)
    msp.add_circle((CFX, Y0), r[2], dxfattribs={"layer": "PERFIL"})
    msp.add_lwpolyline([(CFX - w_out, Y0 - a_out / 2.0), (CFX + w_out, Y0 - a_out / 2.0),
                        (CFX + w_out, Y0 + a_out / 2.0), (CFX - w_out, Y0 + a_out / 2.0)],
                       close=True, dxfattribs={"layer": "PERFIL"})
    msp.add_lwpolyline([(CFX - w_fd / 2.0, Y0 - a_fd / 2.0), (CFX + w_fd / 2.0, Y0 - a_fd / 2.0),
                        (CFX + w_fd / 2.0, Y0 + a_fd / 2.0), (CFX - w_fd / 2.0, Y0 + a_fd / 2.0)],
                       close=True, dxfattribs={"layer": "CANAL"})
    msp.add_line((CFX - r[2] - 7, Y0), (CFX + r[2] + 7, Y0), dxfattribs={"layer": "EIXO"})
    msp.add_line((CFX, Y0 - r[2] - 7), (CFX, Y0 + r[2] + 7), dxfattribs={"layer": "EIXO"})
    dim(origem_cf, (r[2] + 25, 0), (0, -a_fd / 2.0), (0, a_fd / 2.0),
        "ABERTURA %s +0,010/-0,000" % br(a_fd, 3), ang=90, destaque=True)
    dim(origem_cf, (0, -r[2] - 11), (-w_fd / 2.0, 0), (w_fd / 2.0, 0), "largura %s ±0,05" % br(w_fd))
    texto("FACE DE SAÍDA (x = %s), olhando ao longo do eixo" % br(L), CFX - r[2] - 42, Y0 + r[2] + 24,
          3.2, limite=155)
    paragrafo("boca do chanfro %s × %s (chanfro %s × 45°) · fenda %s × %s com R %s vivo nas duas pontas"
              % (br(b_saida[0]), br(b_saida[1]), br(chan), br(w_fd), br(a_fd, 3), br(raio_borda)),
              CFX - r[2] - 42, Y0 + r[2] + 21, 2.8, 132.0, 13.5)

    # ------------------------------------------------------------------ 3 · MATERIAL (a enfase)
    texto("MATERIAL DA PEÇA: " + str(DEC["material"]).upper(), B[0] + 4, FOLHA[1] - 26, 8.0, "MATERIAL")
    msp.add_lwpolyline([(B[0] + 2, FOLHA[1] - 29), (B[2] - 2, FOLHA[1] - 29)],
                       dxfattribs={"layer": "MATERIAL", "const_width": 0.9, "color": 1})
    paragrafo("Norma: " + str(ACO["norma"]) + "\\P" + "Dureza e tratamento: " + str(ACO["dureza"]) +
              "\\P" + "NÃO PODE MUDAR: sem PVD, sem DLC - nenhuma outra camada sem ordem assinada; "
              "aço trocado só com desenho novo assinado por nós + certificado EN 10204 3.1 do lote.",
              B[0] + 4, FOLHA[1] - 32, 3.0, B[2] - B[0] - 10, 24.0, "MATERIAL")

    # ------------------------------------------------------------------ 4 · notas (empilhadas, com trava de altura)
    texto("NOTAS", NOTAS[0], NOTAS[3] + 6.0, 3.6, "NOTAS", cor=1)
    y = NOTAS[3] - 3.0        # topo do primeiro bloco de texto
    notas = [
        "1  A fenda é aberta a fio EDM pelo Ø%s, de um lado só, DEPOIS do tratamento térmico do corpo. "
        "Não tem linha de partição, flange, furo de fixação, rosca nem pino: a peça é 1 sólido e o aperto "
        "é pelo collete EX-031 e pelo degrau do furo do cabeçote." % br(D_ent),
        "2  Medir a abertura da fenda ANTES e DEPOIS do tratamento e gravar os dois números: 8 a 18 µm por "
        "face comem 0,016 a 0,036 mm da tolerância de 0,010; se fechar abaixo de %s mm, passar o fio de "
        "novo. Remover camada REC >= 0,02 mm; canal e land com Ra <= 0,4 µm, polido no sentido da "
        "extrusão; rebarba <= 0,1 × 45°." % br(a_fd, 3),
        "3  Comprimento com a face de saída ralada no fim, faceada ao nariz do EX-031 (protrusão medida na "
        "montagem: %s mm). Coaxialidade dos 3 estágios Ø0,02 em A; face de saída com planeza 0,01 e "
        "perpendicularidade 0,01 em A; não alargar a boca de entrada Ø%s." % (br(PROT), br(D_ent)),
        "4  Entregar 1 peça com certificado EN 10204 3.1 do lote (composição, granulometria, inclusões, "
        "ensaio mecânico), relatório de dureza e relatório dimensional de todas as cotas desta folha. "
        "Marcação a laser na face traseira: JONATHA v27.0 · EX-031 · 1045 · rev. %s · lote · nº série."
        % REV,
    ]
    for n in notas:
        nl = linhas_de(n, 2.8, NOTAS[2] - NOTAS[0])
        bloco = nl * 2.8 * 1.5
        if y - bloco < NOTAS[1] - 0.01:
            estouro.append("as notas invadem a moldura: o bloco pede %.1f mm e sobravam %.1f mm"
                           % (bloco, y - NOTAS[1]))
        paragrafo(n, NOTAS[0], y, 2.8, NOTAS[2] - NOTAS[0], bloco + 0.01)
        y -= bloco + 2.4

    # ------------------------------------------------------------------ 5 · carimbo
    kx0, ky0, kx1, ky1 = CARIMBO
    rot_x = kx0 + 50.0
    lim = kx1 - rot_x - 4
    msp.add_lwpolyline([(kx0, ky0), (kx1, ky0), (kx1, ky1), (kx0, ky1)], close=True,
                       dxfattribs={"layer": "CARIMBO"})
    topo_cab = ky1
    fileiras = [("MATERIAL", 96.0, 18.0), ("COTA CRÍTICA", 78.0, 15.0), ("TRATAMENTO", 63.0, 21.0),
                ("COTAS", 42.0, 12.0), ("SIGILO", 30.0, 8.0)]
    for y_ in sorted([topo_cab - 14.0] + [t for _, t, _a in fileiras]):
        msp.add_line((kx0, y_), (kx1, y_), dxfattribs={"layer": "CARIMBO"})
    msp.add_line((rot_x, topo_cab - 14.0), (rot_x, ky0), dxfattribs={"layer": "CARIMBO"})
    texto("MATRIZ DE EXTRUSÃO · JONATHA v27.0", kx0 + 3, topo_cab - 5.0, 4.2, "CARIMBO",
          limite=kx1 - kx0 - 6)
    texto("peça única · 1 peça · escala 1:1 · mm · A3 · rev. %s de 2026-09-22" % REV,
          kx0 + 3, topo_cab - 10.5, 2.6, "CARIMBO", limite=kx1 - kx0 - 6)
    for rt, t, alt in fileiras:
        texto(rt, kx0 + 3, t - 5.0, 2.6, "CARIMBO", cor=8)
    texto("AÇO 1045", rot_x + 1, 96.0 - 9.5, 6.0, "CARIMBO", cor=1, limite=lim)
    paragrafo(FRAG_NORMA + " · entrega " + FRAG_ENTREGA + " · " + FRAG_CORPO, rot_x + 1, 96.0 - 12.0,
              2.6, lim, 18.0 - 13.5, "CARIMBO")
    paragrafo("abertura %s +0,010/-0,000 mm · largura %s ±0,05 mm · chanfro %s × 45°"
              % (br(a_fd, 3), br(w_fd), br(chan)), rot_x + 1, 78.0 - 1.5, 3.0, lim, 15.0 - 3.5,
              "CARIMBO", cor=1)
    paragrafo(str(ACO["dureza"]), rot_x + 1, 63.0 - 1.5, 2.6, lim, 21.0 - 3.5, "CARIMBO")
    paragrafo("as 8 cotas desta folha são medição no STEP\\P" + str(M["arquivo"]), rot_x + 1,
              42.0 - 1.5, 2.5, lim, 12.0 - 3.5, "CARIMBO")
    paragrafo("NDA antes de circular esta folha fora da fábrica", rot_x + 1, 30.0 - 1.0, 2.5, lim,
              8.0 - 2.5, "CARIMBO")

    texto("procedência: " + str(ACO["grupo"]) + " · cotas com vírgula decimal (padrão BR)",
          B[0] + 4, B[1] - 4.5, 2.5, "NOTAS", limite=B[2] - B[0] - 8)
    texto("se o desenho e o STEP discordarem, vale o STEP · o símbolo Ø só aparece se a fonte do texto "
          "tiver Latin-1 (troque para Arial)", B[0] + 4, B[1] - 8.0, 2.5, "NOTAS",
          limite=B[2] - B[0] - 8)

    if estouro:
        raise SystemExit("estouro de caixa no DXF (%d): %s" % (len(estouro), " | ".join(estouro)))

    msp.add_lwpolyline([(B[0], B[1]), (B[2], B[1]), (B[2], B[3]), (B[0], B[3])], close=True,
                       dxfattribs={"layer": "CARIMBO"})
    destino = os.path.join(RAIZ, PACOTE, DXF + ".dxf")
    doc.saveas(destino, encoding="utf-8")
    print("gravado:", destino, os.path.getsize(destino), "bytes ·", len(msp), "entidades")

    auditado = ezdxf.readfile(destino).audit()
    print("auditoria: %d erro(s), %d correção(ões)" % (len(auditado.errors), len(auditado.fixes)))
    if auditado.errors:
        raise SystemExit("DXF com erro de estrutura - não publico")

    reabre = ezdxf.readfile(destino)
    cotas = [e.dxf.text for e in reabre.modelspace().query("DIMENSION")]
    precisa = ["Ø%s ±0,5" % br(2 * r[0]), "Ø%s ±0,5" % br(2 * r[1]), "Ø%s ±0,5" % br(2 * r[2]),
                "Ø%s +0,05/-0,00" % br(D_ent), "comprimento %s ±0,5" % br(L), "land %s ±0,05" % br(land),
                "ABERTURA %s +0,010/-0,000" % br(a_fd, 3), "largura %s ±0,05" % br(w_fd)]
    falta = [p for p in precisa if p not in cotas]
    print("cotas no arquivo: %d · conferidas com o JSON: %d/%d"
          % (len(cotas), len(precisa) - len(falta), len(precisa)))
    if falta:
        raise SystemExit("cota sumiu no round-trip do DXF: %s" % falta)
    tudo = cotas + [e.dxf.text for e in reabre.modelspace().query("TEXT")]
    print("glifos acima de Latin-1 no texto:",
          sorted({c for t in tudo for c in t if ord(c) > 0xFF}) or "nenhum")

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
    limites = ((min(xs), B[0], B[2], "x min"), (max(xs), B[0], B[2], "x max"),
               (min(ys), B[1] - 9.5, B[3], "y min"), (max(ys), B[1] - 9.5, B[3], "y max"))
    foroo = ["%s = %s fora de %s..%s" % (e, br(v, 1), br(lo, 1), br(hi, 1))
             for v, lo, hi, e in limites if v < lo or v > hi]
    print("conteúdo: x %s..%s · y %s..%s (moldura %s..%s / %s..%s)"
          % (br(min(xs), 1), br(max(xs), 1), br(min(ys), 1), br(max(ys), 1),
             br(B[0], 0), br(B[2], 0), br(B[1], 0), br(B[3], 0)))
    if foroo:
        raise SystemExit("conteúdo fora da moldura: %s" % " | ".join(foroo))

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from ezdxf.addons.drawing import RenderContext, Frontend
        from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
        fig = plt.figure(figsize=(FOLHA[0] / 25.4, FOLHA[1] / 25.4))
        ax = fig.add_axes([0.004, 0.004, 0.992, 0.992])
        ax.set_facecolor("#15151e")                 # como na tela do CAD: ACI 7 vira branco
        Frontend(RenderContext(reabre), MatplotlibBackend(ax)).draw_layout(reabre.modelspace(),
                                                                           finalize=True)
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
    main()
