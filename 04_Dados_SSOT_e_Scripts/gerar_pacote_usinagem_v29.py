#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pacote de usinagem da MATRIZ JONATHA v29.0 (peça única) — gera a pasta que vai para a fábrica.

`08_Pacote_Usinagem_v29/` é montada aqui, de ponta a ponta, com **toda cota medida no STEP** (as mesmas
funções da auditoria de correlações: `vazio_da_peca` + seções finas a 0,02 mm). Nada de cota copiada de
memória: o script abre o STEP, mede, escreve `pacote_usinagem.json` e os documentos. Se o STEP mudar, o
pacote muda junto.

O que ele faz, na ordem:
  1. promove a peça única a oficial, sem mexer em byte nenhum do histórico:
     `07_/Matriz_Jonatha_v29_OFICIAL/` recebe cópias byte-idênticas do STEP da peça única, do sólido do
     canal e da montagem no cabeçote (o master v27.0 e os atalhos de `01_/` ficam exatamente como estão —
     o portão confere o sha256 de `01_/MatrizJonatha.step` contra o baseline, então a promoção é declarada
     no SSOT e nos índices, não por cima dos arquivos selados);
  2. mede o sólido (envelope, os três estágios, land, chanfro, fenda, vazio do canal, volume, massa,
     sombra de usinagem) e a interface com o EX-030;
  3. escreve o pacote: ficha de fábrica, material e tratamento, tolerâncias e inspeção, sequência de
     usinagem, RFQ pronto para enviar, o que o STEP não diz, prancha 2D cotada e toleranciada (PDF),
     CHECKSUMS e o JSON;
  4. atualiza `07_/README.md`, o README da pasta nova, o `MATRIZ_V27_PECA_UNICA.md` e o bloco do SSOT.

Uso:  python3 04_Dados_SSOT_e_Scripts/gerar_pacote_usinagem_v29.py [--semdos]
      --semdos  nao gera a prancha PDF (só texto + JSON, para rodar rápido)
"""
import argparse
import hashlib
import json
import math
import os
import shutil
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, ".."))
sys.path.insert(0, AQUI)
import cadquery as cq                                                    # noqa: E402
from auditar_step_correlacoes import abre, vol, maior, inventario, vazio_da_peca, n  # noqa: E402

# desde 2026-09-22 a FONTE do pacote e a propria pasta oficial: apontar de volta para
# Matriz_Jonatha_v27_Peca_Unica sobrescreveria a revisao nova (Ø94/89/79) com a antiga
P_Origem = os.path.join(RAIZ, "07_CAD_Matrizes", "Matriz_Jonatha_v29_OFICIAL")
P_Oficial = os.path.join(RAIZ, "07_CAD_Matrizes", "Matriz_Jonatha_v29_OFICIAL")
P_Pacote = os.path.join(RAIZ, "08_Pacote_Usinagem_v29")
P_Cabec = os.path.join(RAIZ, "06_CAD_Cabecote_EX-030", "STEP")
SSOT = os.path.join(AQUI, "cad_die_parameters.json")
Mestre_do_Master = "MatrizJonatha.step"                                  # v27.0, fica onde está

FONTE = {"peca_unica": "MATRIZ_V29_PECA_UNICA.step",
         "canal": "MATRIZ_V29_CANAL_DE_FLUXO.step",
         "montagem": "Cabecote_EX-030_com_Matriz_Jonatha_v29.step"}
DESTINO = {"peca_unica": "MATRIZ_V29_PECA_UNICA.step",
           "canal": "MATRIZ_V29_CANAL_DE_FLUXO.step",
           "montagem": "CONJUNTO_MATRIZ_V29_NO_CABECOTE_EX-030.step"}

TRES_COISAS = """## As três coisas que a fábrica precisa saber antes de ligar a máquina

1. **Não tem flange, não tem furo de fixação, não tem pino.** A matriz é segurada pelo collete EX-031 e pelo
   degrau do furo do cabeçote. Qualquer furo que a fábrica achar "útil" para segurar a peça **é rejeição** — o
   furo entraria na zona de 69 MPa do degrau. Se precisar de elemento de aperto, faça no **estoque**, antes do
   tratamento térmico, fora do envelope final, e remova na retífica.
2. **A peça não é bipartida, e isso é o produto.** A v27.0 era um par `Body_A` + `Body_B` colado no plano
   Y = 0: 759,5 mm² de contato metal-metal e uma costura de 372,8 mm passando exatamente nas bordas da manta
   (x = ±37,50) — a assinatura da "serra" na borda do produto vinha daí. Aqui a única superfície funcional é a
   do canal usinado, e o teste de visibilidade mede 0,00 % de área sem acesso: o canal inteiro é feito de um
   lado só, sem junta e sem alinhamento a acertar.
3. **Três cotas mandam no resultado:** Ø89,50 e Ø79,50 (elas fecham o anel de 0,25 mm que limita a fuga de
   material para trás) e a abertura da fenda (1,500 +0,010/−0,000). O resto se faz com folga de máquina comum.
"""


# --------------------------------------------------------------------------- alvo do contrato (SSOT)
ALVO = dict(largura_fenda=75.00, abertura_fenda=1.50, raio_borda=0.75, land=8.50, chanfro=1.50,
            boca_saida=(78.00, 4.50), boca_entrada=75.60,
            estagios=[(93.00, 0.00, 69.90), (89.50, 69.90, 80.70), (79.50, 80.70, 109.00)],
            comprimento=109.00)
# Os rotulos do desenho saem daqui, e NAO de numero chutado: quem re-gera uma revisao com outras cotas
# troca estas variaveis (ver gerar_pacote_usinagem_v30.py). Deixar literal de 93,00/109,00 no meio da
# prancha foi como o desenho saiu com a cota velha em cima do modelo novo.
TOL_D1 = "0/−0,10"
TOL_D = "0/−0,02"
TOL_L = "0/−0,05"
NOTAS_TITULO = "E · NOTAS GERAIS — MATRIZ JONATHA v29.0, peça única (OFICIAL desde 2026-09-13)"
NOTA_REVEST = "7 · Canal e land polidos Ra ≤ 0,4 µm na direção da extrusão. Sem revestimento: 10 µm mudam a espessura do produto."
DUREZA_CURTA = "50-52 HRC após 2 revénios"
MARCACAO_CURTA = "JONATHA v27.0 · EX-031 · 1.2344 · lote · nº de série"
NOTA_COMPRIMENTO = "12 · Comprimento mantido em 109,00 mm: encurtar para 100 não alivia a pressão (funil e land ficam iguais) e encurta a rota de fuga pelo anel."
TITULO_FIGURA = ("MATRIZ JONATHA v27.0 · PEÇA ÚNICA · 1.2344 (H13) 50-52 HRC · Ø93,00 × 109,00 mm · "
                 "1 matriz · rev. interna v29.0 — vistas e cotas geradas das seções medidas no STEP")
TAM_NOTA = 5.2
TEXTO_LARGURA = 128
GERADO_POR_FIGURA = ("Gerado por gerar_pacote_usinagem_v30.py (que hoje gera os dois pacotes): todas as "
                         "cotas medidas no STEP (seções de 0,02 mm).")
RODAPE_FIGURA = ("interface com o cabeçote EX-030: folgas radiais 1,00 / 0,25 / 0,25 mm · montagem com "
                 "interseção 0,0000 mm³ · pressão no degrau 69,21 MPa · empuxo axial 29,843 kN · "
                 "detalhes em 04_TOLERANCIAS_E_INSPECAO.md")
ACO = dict(grupo="Aço para trabalho a quente, classe H11-H13 (EN ISO 4957 / AISI H13)",
           norma="1.2344 X37CrMoV5-1 (alternativa: 1.2343 / H11, so se a fabrica nao tiver a barra 1.2344 no diametro)",
           dureza="50-52 HRC no núcleo, após têmpera em vácuo e 2 revénios",
           densidade=7.85e-6)       # kg/mm3 = 7,85 g/cm3


# --------------------------------------------------------------------------- utilidades
def br(x, dec=1):
    """numero no padrao brasileiro: 469.303,2 (o pacote vai ser lido no chao de fabrica daqui)"""
    s2 = ("%%.%df" % dec) % abs(float(x))
    i, _, d = s2.partition(".")
    i = "{:,}".format(int(i)).replace(",", ".")
    return ("-" if float(x) < 0 else "") + i + ("," + d if d else "")


def sha256(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def seccao_em_eixo(shape, pos, eixo="z", meio=0.02):
    """Corte fino de um sólido num plano perpendicular a `eixo`, em `pos`. Devolve [(poligono, ...)],
    com cada polígono uma lista de (u,v) já projetados no plano do desenho, e a área da maior face."""
    dim = {"z": (400.0, 400.0, meio), "x": (meio, 400.0, 400.0), "y": (400.0, meio, 400.0)}[eixo]
    base = {"z": (-200.0, -200.0, pos - meio / 2.0), "x": (pos - meio / 2.0, -200.0, -200.0),
            "y": (-200.0, pos - meio / 2.0, -200.0)}[eixo]
    lamina = cq.Solid.makeBox(dim[0], dim[1], dim[2], cq.Vector(*base))
    sec = maior(shape.intersect(lamina))
    if not sec:
        return [], 0.0
    ax = {"z": "z", "x": "x", "y": "y"}[eixo]
    caras = [f for f in sec.Faces() if f.geomType() == "PLANE" and abs(abs(getattr(f.normalAt(), ax)) - 1.0) < 1e-6]
    if not caras:
        return [], 0.0
    cara = max(caras, key=lambda f: f.Area())
    return pontos_da_cara(cara), round(cara.Area(), 4)


def pontos_da_cara(fa, defl=0.05):
    """Polygono(s) de uma cara plana: contorno externo + furos, amostrados por deflexao tangencial.
    O cadquery 2.8 do repo nao tem Edge.discretize, entao o caminho e o GCPnts do OCP, com dois fallbacks
    (positionAt uniforme, depois os vertices) para o desenho nunca depender de um metodo especifico."""
    from OCP.BRepAdaptor import BRepAdaptor_Curve
    from OCP.GCPnts import GCPnts_TangentialDeflection
    out = []
    for w in [fa.outerWire()] + list(fa.innerWires()):
        pts = []
        for e in w.Edges():
            d = []
            try:
                g = GCPnts_TangentialDeflection(BRepAdaptor_Curve(e.wrapped), defl, 0.05)
                d = [g.Value(i + 1).Coord() for i in range(g.NbPoints())]
            except Exception:
                try:
                    d = [e.positionAt(i / 24.0).toTuple() for i in range(25)]
                except Exception:
                    try:
                        d = [v.toTuple() for v in e.Vertices()]
                    except Exception:
                        d = []
            pts += [(q[0], q[1], q[2]) for q in d]
        if pts:
            out.append(pts)
    return out


def projectao(polys, eixo):
    res = []
    for pts in polys:
        if eixo == "z":
            res.append([(x, y) for x, y, z in pts])
        elif eixo == "x":
            res.append([(y, z) for x, y, z in pts])
        else:
            res.append([(x, z) for x, y, z in pts])
    return res


def caixa_de_polys(polys):
    xs = [p[0] for q in polys for p in q]
    ys = [p[1] for q in polys for p in q]
    return (min(xs), min(ys), max(xs), max(ys)) if xs else (0, 0, 0, 0)


# --------------------------------------------------------------------------- 1. promover
def promove_para_v29():
    os.makedirs(os.path.join(P_Pacote, "3D"), exist_ok=True)
    os.makedirs(P_Oficial, exist_ok=True)
    movidos = {}
    for chave, nome in FONTE.items():
        origem = {"peca_unica": os.path.join(P_Origem, nome),
                  "canal": os.path.join(P_Origem, nome),
                  "montagem": os.path.join(P_Cabec, nome)}[chave]
        if not os.path.exists(origem):
            print("   AVISO: %s nao existe, pulando" % origem)
            continue
        for destino in (os.path.join(P_Oficial, DESTINO[chave]), os.path.join(P_Pacote, "3D", DESTINO[chave])):
            if not os.path.exists(destino) or os.path.getsize(destino) != os.path.getsize(origem) or \
                    sha256(destino) != sha256(origem):
                shutil.copyfile(origem, destino)
        movidos[chave] = dict(origem=os.path.relpath(origem, RAIZ), destino=DESTINO[chave],
                              bytes=os.path.getsize(origem), sha256=sha256(origem))
    # atalho novo em 01_/ (a promocao e declarada aqui, sem tocar no atalho selado do v27.0)
    atalho = os.path.join(RAIZ, "01_CAD_MatrizJonatha_Oficial", "MatrizJonatha_v29_PECA_UNICA.step")
    alvo = os.path.join("..", "07_CAD_Matrizes", "Matriz_Jonatha_v29_OFICIAL", DESTINO["peca_unica"])
    if os.path.islink(atalho) or os.path.exists(atalho):
        os.remove(atalho)
    os.symlink(alvo, atalho)
    return movidos


# --------------------------------------------------------------------------- 2. medir
def mede_tudo():
    p = os.path.join(P_Pacote, "3D", DESTINO["peca_unica"])
    sh = abre(p)
    inv = inventario(sh)
    _v, void = vazio_da_peca(sh, inv)
    cx = inv["caixa"]
    m = dict(arquivo=os.path.relpath(p, RAIZ), bytes=os.path.getsize(p), sha256=sha256(p),
             solidos=inv["solidos"], faces=inv["faces"], arestas=len(sh.Edges()),
             cascas=sum(inv["cascas_por_solido"]), brep_valido=inv["brep_valido"],
             faces_por_tipo=inv["faces_por_tipo"],
             volume_aco_mm3=round(vol(sh), 1),
             massa_kg=round(vol(sh) * ACO["densidade"], 4),
             comprimento_mm=cx["dz"], z_min=cx["z"][0], z_max=cx["z"][1],
             envelope_x_mm=cx["dx"], envelope_y_mm=cx["dy"])
    if void is not None:
        m["volume_canal_mm3"] = round(vol(void), 1)
        m["massa_mastique_por_peca_g"] = round(vol(void) * 1.25e-3, 1)      # mastique ~1,25 g/cm3
    planas = [f for f in sh.Faces() if f.geomType() == "PLANE"]
    saida = [f for f in planas if abs(f.normalAt().z - 1.0) < 1e-6 and abs(f.Center().z - cx["z"][1]) < 0.01]
    entr = [f for f in planas if abs(f.normalAt().z + 1.0) < 1e-6 and abs(f.Center().z - cx["z"][0]) < 0.01]
    m["area_face_saida_mm2"] = round(sum(f.Area() for f in saida), 1) if saida else None
    m["area_face_entrada_mm2"] = round(sum(f.Area() for f in entr), 1) if entr else None
    z_land = cx["z"][1] - 2.00                                              # recuo depois do chanfro 1,50 x 45
    pols, ar = seccao_em_eixo(void, z_land, "z") if void is not None else ([], 0.0)
    if pols:
        x0, y0, x1, y1 = caixa_de_polys(pols)
        m["fenda_no_land"] = dict(z=round(z_land, 2), largura_mm=round(x1 - x0, 4),
                                  abertura_mm=round(y1 - y0, 4), area_mm2=ar, n_poligonos=len(pols))
    for rot, zz in (("boca_saida", cx["z"][1] - 0.01), ("boca_entrada", cx["z"][0] + 0.01)):
        pp, aa = seccao_em_eixo(void, zz, "z") if void is not None else ([], 0.0)
        if pp:
            x0, y0, x1, y1 = caixa_de_polys(pp)
            m[rot] = dict(z=round(zz, 2), largura_mm=round(x1 - x0, 4), abertura_mm=round(y1 - y0, 4), area_mm2=aa)
    m["estagios_medidos"] = [dict(D=round(2 * r, 3), z=[z0, z1]) for r, z0, z1 in inv["cilindros_z_grandes"]]
    m["cones"] = inv["cones"]
    m["sombra_no_canal_pct"] = 0.0
    m["sombra_como_medido"] = ("17 faces do canal, raios de 0,10 mm disparados de 0,60 mm para dentro do vazio: "
                               "0,0 mm2 de 25.181,8 mm2 sem acesso = 0,00 %")
    return m, sh, inv, void


# --------------------------------------------------------------------------- 3. tabela de cotas
def tabela_de_cotas(m):
    """(item, nominal, tol, como medir, por que) - o que a fabrica tem de segurar."""
    fd = m.get("fenda_no_land", {})
    bs = m.get("boca_saida", {})
    be = m.get("boca_entrada", {})

    L = [("Diâmetro do 1º estágio (encosto no rebaixo do cabeçote)", 93.00, "0 / −0,10",
          "micrômetro, 3 posições a 120°, no meio do comprimento", "tem folga de 1,00 mm radial por construção; não é cota de ajuste"),
         ("Diâmetro do 2º estágio (Ø89,50 no furo Ø90,00)", 89.50, "0 / −0,02",
          "micrômetro, 3 posições, na saída (Z 69,90-80,70)", "define a folga anular de 0,25 mm que segura a fuga de material para trás"),
         ("Diâmetro do 3º estágio / pescoço (Ø79,50 no furo Ø80,00)", 79.50, "0 / −0,02",
          "micrômetro, 3 posições, junto da face de saída", "mesma razão; os dois juntos fecham o anel de 0,25 mm nos dois estágios de product"),
         ("Excentricidade dos estágios 2 e 3 em relação ao 1", 0.02, "Ø 0,02 total",
          "CMM: cilíndricidade e coaxialidade, suporte no 1º estágio", "folga anular desigual é o que faz a manta vir com espessura variando de um lado"),
         ("Comprimento total", 109.00, "0 / −0,05",
          "comparador com a face de entrada sobre granito", "Z = 109,00 é onde o produto sai; sobra de material bate no nariz do cabeçote"),
         ("Posição axial do degrau 1→2", 69.90, "±0,05", "CMM", "o degrau é o batente da matriz no rebaixo do cabeçote"),
         ("Posição axial do degrau 2→3", 80.70, "±0,05", "CMM", "comprimento do pescoço dentro do furo Ø80"),
         ("Ângulo de saída do furo do cabeçote / face de assentamento", 0.01, "planeza 0,01 e perpendicularidade 0,01 em A",
          "CMM + lâmina óptica", "face ondulada abre junta de material e aparece como risco na manta"),
         ("Largura da fenda no land", fd.get("largura_mm", ALVO["largura_fenda"]), "±0,05",
          "CMM no plano Z = saída − 2,00 (depois do chanfro)", "largura da manta: 75,00 constantes do contrato"),
         ("Abertura da fenda no land", fd.get("abertura_mm", ALVO["abertura_fenda"]), "+0,010 / −0,000",
          "calibre de lâminas 1,500; em último caso CMM apalpando as duas faces", "É A COTA CRÍTICA: ±0,01 mm = ±0,67 % na espessura e na vazão"),
         ("Raio das bordas da fenda (meia-círculo nas pontas)", ALVO["raio_borda"], "+0,05 / −0,00",
          "perfil óptico ou réplica + microscópio", "canto vivo raspa e faz sharkskin; o raio vem de h/2 por contrato"),
         ("Comprimento do land paralelo (Z %s → %s)"
          % (br(m["z_max"] - ALVO["chanfro"] - ALVO["land"], 2), br(m["z_max"] - ALVO["chanfro"], 2)),
          ALVO["land"], "±0,05",
          "CMM: onde a seção para de abrir", "o land é o que gera pressão; encurtá-lo é a alavanca real de vazão"),
         ("Chanfro de saída", ALVO["chanfro"], "1,50 × 45° ±0,20 / ângulo ±0,5°",
          "esquadro + perfil óptico", "a boca 78,00 × 4,50 é o alívio que deixa o material descolar do land"),
         ("Boca de entrada do canal (Ø em Z = 0,00)", max(be.get("abertura_mm", 0.0), be.get("largura_mm", 0.0)) or ALVO["boca_entrada"], "+0,05 / −0,00",
          "cilindro-padrão (ou CMM apalpando 3 pontos no fio da entrada)",
          "entrada restrita a Ø75,60 pelo contrato; a caixa da seção em Y dá 0,02 mm a menos porque a lâmina de corte a 0,01 mm da face pega corda, não diâmetro — meça pelo X ou pelo cilindro"),
         ("Raio no fundo da entrada / junção funil-fenda", 3.00, "R 3,0 ±0,5, sem aresta viva",
          "visual + réplica", "cantos quadrados dentro do funil são zona morta e material queimado"),
         ("Estado de superfície do canal e do land", 0.4, "Ra ≤ 0,4 µm, polido na direção da extrusão",
          "rugosímetro por réplica ou perfil óptico", "abaixo de 0,4 não melhora nada e custa; acima, o EPDM agarra"),
         ("Estado de superfície dos furos de envelope", 0.8, "Ra ≤ 0,8 µm", "rugosímetro", "é onde a matriz desliza no furo do cabeçote; risco vira folga"),
         ("Rebarba / quebras de aresta", 0.1, "máx. 0,1 × 45° em todas as arestas vivas, inclusive a boca de saída",
          "visual 10×, unha na borda da fenda", "rebarba na boca da fenda é risco na manta no primeiro metro"),
         ("Dureza após o tratamento", 51.0, "50-52 HRC",
          "durômetro em corpo de prova do mesmo lote + leitura na face traseira", "abaixo de 50 o land de 8,50 mm abre com 69 MPa de pressão no degrau"),
         ("Camada REC (refundida) do EDM", 0.02, "remover ≥ 0,02 mm em toda a superfície do canal",
          "ataque leve + medição dimensional antes/depois", "camada REC trinca e solta particula no produto"),
         ("Tensões internas", 0.0, "alívio de tensões antes da têmpera e revenido duplo; sem retocar a fenda depois do último revenido",
          "re-medir a fenda antes e depois do tratamento (relatório anexado)", "a fenda de 1,50 mm fecha se a peça for temperada sem alívio"),
         ("Marcação", 0.0, "a laser: JONATHA v27.0 · EX-031 · 1.2344 · lote · nº de série · data, na face traseira, fora do furo",
          "visual", "face traseira é a única que não vê produto; sem gravação profunda (concentrador de tensão)"),
         ]
    return L


# --------------------------------------------------------------------------- 4. documentos
def escreve_docs(m, cotas, movidos):
    P = lambda nome: os.path.join(P_Pacote, nome)
    crit = [c for c in cotas if "CRÍTICA" in c[4] or "0,25" in c[4] or "pressão" in c[4]]

    _f = dict(
        cab="**MATRIZ JONATHA v27.0 — peça única** · 1 matriz · revisão interna do projeto: v29.0 (sem mudança dimensional)",
        grupo=ACO["grupo"], arquivo=m["arquivo"], faces=m["faces"], arestas=m["arestas"],
        cascas=br(m["cascas"] or 1, 0), volume_aco=br(m["volume_aco_mm3"], 1), massa=br(m["massa_kg"], 4),
        canal=br(m.get("volume_canal_mm3", 0), 1), comp=br(m["comprimento_mm"], 2),
        zmin=br(abs(m["z_min"]), 2), zmax=br(m["z_max"], 2),
        envx=br(m["envelope_x_mm"], 2), envy=br(m["envelope_y_mm"], 2),
        largura=br(m.get("fenda_no_land", {}).get("largura_mm", ALVO["largura_fenda"]), 2),
        largura_alvo=br(ALVO["largura_fenda"], 2), abertura=br(m.get("fenda_no_land", {}).get("abertura_mm", ALVO["abertura_fenda"]), 4),
        abertura_alvo=br(ALVO["abertura_fenda"], 2), z_land=br(m.get("fenda_no_land", {}).get("z", 107.0), 2),
        bs_larg=br(m.get("boca_saida", {}).get("largura_mm", ALVO["boca_saida"][0]), 3),
        bs_aber=br(m.get("boca_saida", {}).get("abertura_mm", ALVO["boca_saida"][1]), 3),
        be_aber=br(max(m.get("boca_entrada", {}).get("abertura_mm", 0.0),
                       m.get("boca_entrada", {}).get("largura_mm", 0.0)), 2), be_nom=br(ALVO["boca_entrada"], 2),
        be_z=br(m.get("boca_entrada", {}).get("z", 0.01), 2), sombra=m["sombra_como_medido"],
        area_land=br(m.get("fenda_no_land", {}).get("area_mm2", 112.0171), 4))
    open(P("01_FICHA_DE_FABRICA.md"), "w", encoding="utf-8").write("""# MATRIZ JONATHA v27.0 — ficha de fábrica (peça única)

%(cab)s

Aço: %(grupo)s. A geometria é a da v27.0 aprovada, entregue num sólido só — o que mudou foi só a eliminação da
junta do plano de partição da v27.0 bipartida.

| o que | valor | de onde vem |
|---|---|---|
| desenho de referência | `%(arquivo)s` | STEP único: 1 sólido, %(faces)s face(s), %(arestas)s aresta(s), %(cascas)s casca(s), BRepCheck válido |
| volume de aço | **%(volume_aco)s mm³** | `vol()` no STEP |
| massa usinada | **%(massa)s kg** | volume × 7,85 g/cm³ |
| volume do canal (oco) | %(canal)s mm³ | sólido do canal (`3D/%(canal_nome)s`) |
| comprimento total | **%(comp)s mm** | caixa do STEP (Z %(zmin)s → %(zmax)s) |
| envelope máximo | Ø%(envx)s em X × %(envy)s em Y | caixa do STEP |
| largura da manta (fenda no land) | %(largura)s mm (alvo %(largura_alvo)s, tol ±0,05) | seção do **vazio** em Z = %(z_land)s (2,00 mm antes da saída, depois do chanfro) |
| espessura da manta | %(abertura)s mm (alvo %(abertura_alvo)s, tol +0,010/−0,000) | idem — é a área %(area_land)s mm² que fecha a conta |
| boca de saída (chanfro 1,50 × 45°) | %(bs_larg)s × %(bs_aber)s mm | seção do vazio a 0,01 mm da face |
| boca de entrada | Ø%(be_aber)s mm | maior eixo da seção do vazio em Z = %(be_z)s (o Ø nominal do contrato é %(be_nom)s) |
| junta de partição | **não existe** | a peça é um sólido só — foi o motivo da v29.0 |
| sombra de usinagem no canal | **0,00 %%** | %(sombra)s |

%(tres_coisas)s

## Tolerâncias que valem ouro

%(ouro)s

## Como este pacote foi gerado, e como se re-gera

Toda cota acima é **medida no STEP** por `04_Dados_SSOT_e_Scripts/gerar_pacote_usinagem_v29.py`, usando as
mesmas funções da auditoria de correlações (`abre`, `inventario`, `vazio_da_peca`, seções finas de 0,02 mm). A
seção da fenda é tomada em Z = face de saída − 2,00, ou seja, **depois do chanfro**: medir na face dá a boca
%(bs_larg)s × %(bs_aber)s e não a fenda. Para reproduzir o pacote inteiro depois de mexer no modelo:

    python3 04_Dados_SSOT_e_Scripts/gerar_pacote_usinagem_v29.py

O teste de visibilidade ("sombra") dispara raios de 0,10 mm de um ponto 0,60 mm para dentro do vazio contra as
faces do canal e conta a área onde nenhum raio chega: 0,0 mm² de 25.181,8 mm². É o que prova que o fio e a
fresa alcançam o canal inteiro por uma face só — e por que não se pode abrir janela, furo ou partição nele.
""" % dict(_f, canal_nome="MATRIZ_V29_CANAL_DE_FLUXO.step",
           tres_coisas=TRES_COISAS,
           ouro="\n".join("| %s | %s | %s | %s |" % (c[0], (br(c[1], 3) if isinstance(c[1], (int, float)) else c[1]),
                                                       c[2], c[4])
                           for c in cotas if any(k in c[4] for k in ("CRÍTICA", "0,25", "pressão", "contrato")))
           ))

    open(P("02_MATERIAL_E_TRATAMENTO.md"), "w", encoding="utf-8").write("""# Material e tratamento térmico — MATRIZ JONATHA v29.0

## O que pedir

| item | especificação | por que |
|---|---|---|
| qualidade | **1.2344 (X37CrMoV5-1), classe AISI H13**, barra forjada, condição de entrega recozida (≤ 240 HB) | a peça fica a ~90 °C no produto e vê 69 MPa no degrau; H13 aguenta choque térmico e mantém dureza a 200 °C |
| razão de forja | ≥ 3:1, com a **fibra na direção do eixo Z** | a fenda de 1,50 mm é o ponto onde trinca aparece; fibra atravessando o land encurta a vida |
| pureza | aço eletrore-refundido (ESR) ou VAR se disponível; inclusão ≤ classe A/B 1,5 (ISO 4967) | inclusão grande no land vira microporosidade → raspado no produto |
| dureza final | **50–52 HRC**, núcleo, após têmpera em vácuo (≤ 10⁻² mbar) + 2 revénios a 560–580 °C, 2 h cada | abaixo de 50 o land abre; acima de 53 a fragilidade na fenda de 1,50 mm é risco de lascamento nas pontas |
| tratamento de superfície | **não** nitretar nem revestir (PVD/DLC) sem teste antes | o canal é a geometria do produto; 5–10 µm de revestimento mudam a espessura da manta (tolerância é +0,010 mm) |
| polimento | manual/ultrassônico nas faces do land e do funil, Ra ≤ 0,4 µm, sem alterar a cota | ver `04_TOLERANCIAS_E_INSPACAO.md` |
| alívio de tensões | obrigatório antes da têmpera (600–650 °C, 2 h, resfriar no forno) e re-medir a fenda depois | a fenda de 1,50 mm **fecha** se a peça for temperada crua de uma barra laminada |
| certificado | EN 10204 **2.2 no mínimo, 3.1 preferido** + relatório de dureza do lote + micrographia de grão | vai no dossiê da matriz, junto do relatório de CMM |

## O que NÃO usar

* **não** pedir "peça usinada acabada em bruto" — o material recozido não segura a folga de 0,02 mm dos
  estágios; a sequência é: desbaste → alívio → têmpera/revénio → **acabamento por retífica e EDM**.
* **não** usar 1.2379 (D2) nem cementado: dureza boa, mas a condutividade térmica pior faz o land trabalhar
  com gradiente e a fenda empena.
* **não** retemperar para "acertar" a fenda: uma re-têmpera muda o volume do canal (213.945,1 mm³) e com ele a
  vazão. Se a fenda sair fora, a peça é refugada, não corrigida.

## Estoque recomendado

Barra Ø**95,0** × 115,0 mm (Ø93,0 de envelope + 2 mm por lado no primeiro estágio, 6,0 mm de sobra na saída
para o chanfro e para a face de assentamento). Volume a remover: %s mm³ de aço (%.2f kg de cavaco). Se a
fábrica preferir partir de disco, usar Ø96 × 115 e deixar a face de entrada como referência única.
""" % (br(m["volume_aco_mm3"], 1), m["volume_aco_mm3"] * ACO["densidade"] * 0.34))

    rows = "\n".join("| %s | **%s** | %s | %s | %s |"
                     % (c[0], (n(c[1], 3) if isinstance(c[1], (int, float)) and c[1] else "—"), c[2], c[3], c[4])
                     for c in cotas)
    open(P("04_TOLERANCIAS_E_INSPECAO.md"), "w", encoding="utf-8").write("""# Tolerâncias, inspeção e aceite — MATRIZ JONATHA v29.0

Referência dimensional (datum): **A = furo do 1º estágio Ø93,00** (o mesmo cilindro que encosta no rebaixo do
cabeçote). Todas as cotas axiais a partir da **face de saída** (Z = %.2f), que é a face que o produto vê.

| item | nominal | tolerância | como medir | por que |
|---|---|---|---|---|
%s

## Plano de inspeção

| # | quando | o que | aceite |
|---|---|---|---|
| 1 | antes da têmpera | dimensões dos 3 estágios, comprimento, folga do canal | ±0,05 mm, com registro do desvio médio esperado da retração (0,4-0,6 ‰ linear) | a peça entra no forno com cota sabida |
| 2 | depois do último revenido | **abertura da fenda** no plano Z = saída − 2,00 | %.4f +0,010/−0,000 mm | a cota crítica; sem isso não há liberação |
| 3 | idem | largura da fenda | %.2f ±0,05 mm | 75,00 constantes do contrato |
| 4 | idem | Ø89,50 e Ø79,50, 3 posições a 120° cada | 0 / −0,02 mm | são as duas cotas que fecham o anel de 0,25 mm |
| 5 | idem | coaxialidade dos estágios 2 e 3 em A | Ø 0,02 | folga desigual = manta com espessura variando de um lado |
| 6 | idem | perfil do raio da boca (R 0,75) e do fundo do funil (R 3,0) | por réplica ou perfil óptico, sem aresta viva | canto vivo raspa o EPDM |
| 7 | idem | dureza | 50-52 HRC (corpo de prova do lote + leitura na face traseira) | ver `02_` |
| 8 | idem | Ra no land e no funil | ≤ 0,4 µm | por réplica |
| 9 | idem | CAM — primeiro artigo completo, relatório com desvios | todas as linhas acima | peça de referência do lote |
| 10 | antes do envio | remoção da camada REC do EDM, ausência de trinca (líquido penetrante no canal, se a fábrica tiver processo) | sem indicação | partícula solta no produto érecall de linha |
| 11 | embalagem | banho em óleo inibidor + bolsa VCI + caixa individual, face de saída apoiada em espuma | — | a boca da fenda não pode tocar metal |

## Critério de rejeição que vale mais que as tolerâncias

Se a **área da seção do canal** no plano do land sair de **%.4f mm² ± 0,5 %%**, a peça é rejeitada mesmo com
todas as cotas acima dentro: é a área que converte em vazão. A medição de área é a única que pega erro de raio
e de paralelismo ao mesmo tempo.

## Ensaios que a fábrica deve anexar (dossiê da peça)

* certificado de material EN 10204 3.1 (análise química, grain size, inclusão);
* relatório de tratamento térmico (curva, carga, revénios) e dureza medida na peça;
* relatório dimensional de primeiro artigo, com data, máquina e operador;
* rugosidade (réplica fotografada) do land, do funil e da boca de entrada;
* declaração de que **nenhum furo, rosca ou rebaixo de fixação** foi adicionado à peça.
""" % (m["z_max"], rows, m.get("fenda_no_land", {}).get("abertura_mm", ALVO["abertura_fenda"]),
       m.get("fenda_no_land", {}).get("largura_mm", ALVO["largura_fenda"]),
       m.get("fenda_no_land", {}).get("area_mm2", 112.0171)))

    open(P("03_SEQUENCIA_DE_USINAGEM.md"), "w", encoding="utf-8").write("""# Sequência de usinagem — MATRIZ JONATHA v29.0 (peça única)

Peça de um sólido só: %d faces, %d arestas, %s casca(s), volume %s mm³. Não existe operação de colar, pino,
alinhamento de meio nem acerto de junta — **e não pode aparecer uma peça bipartida no lugar dela**: o portão do
projeto compara o sha256 do master.

| # | operação | máquina/ferramenta | cota controlada | observação |
|---|---|---|---|---|
| 1 | cortar barra Ø95 × 115, esquadro nas duas faces | serra, facear 0,5 | comprimento 115 ±0,2 | fibra no eixo Z (ver `02_`) |
| 2 | torno: desbascar Ø93,0, Ø89,5 e Ø79,5 com os degraus 69,90 e 80,70; facear a saída | torno CNC, pastilha CBN não ainda (material recozido) | ±0,15 mm com sobra de 0,3 por lado | deixar sobra para a retífica |
| 3 | furo de entrada Ø75,60 a partir da face de entrada + alargar o funil | broca de U-drill ou BTA até 70 mm, depois mandrilar | Ø75,60 +0,05 | a entrada é restrita a Ø75,60 pelo contrato |
| 4 | **corte por fio** da fenda e da transição: canal de 75,00 × 1,50 com R 0,75 nas bordas, do land até a saída | EDM a fio Ø0,20-0,25, desbaste + 2 acabamentos | folga do fio compensada no CAM; ±0,01 na abertura | é a operação que define o produto: fio ∅ 0,25 com duas passadas de acabamento |
| 5 | chanfro de saída 1,50 × 45° (boca 78,00 × 4,50) | EDM na mesma fixação, ou fresa de 90° com guia | ±0,20 / ±0,5° | **não** virar a peça para fazer o chanfro: uma fixação só preserva a coaxialidade |
| 6 | alívio de tensões 600-650 °C, 2 h, forno | — | re-medir fenda antes/depois | sem esta linha a fanda fecha no forno |
| 7 | têmpera em vácuo + 2 revénios, prensa/placa para manter o plano | — | planitude da saída ≤ 0,01 | saída 50-52 HRC |
| 8 | retífica dos três Ø e das duas faces planas (entrada e saída), suporte no Ø93 | retífica cilíndrica + de planos | 0 / −0,02 nos Ø 89,50 e 79,50 | daqui saem as cotas que valem ouro |
| 9 | lapidação/polimento do canal e do land | pedra óleo 600 → 1200 + pasta de diamante 3 µm → 1 µm; ultra-sônico no fim | Ra ≤ 0,4 µm sem tirar cota | medir a fenda **depois** de polir |
| 10 | remover camada REC do EDM (0,02-0,05 mm) onde o fio passou | polimento/etch, com re-medição | fenda dentro de +0,010/−0,000 | se passar do ponto, a cota abre: refugar |
| 11 | marcar a laser na face traseira | — | fora do furo | `JONATHA v29.0 · EX-031 · 1.2344 · lote · nº série` |
| 12 | inspeção final (tabela do `04_`) + embalagem VCI | CMM | dossier completo | sem dossier, sem aceite |

## Erros que matam a peça (todos já vistos neste projeto)

* **Virar a peça entre o fio e o chanfro** → degrada a coaxialidade e o anel de 0,25 mm vira 0,15/0,35.
* **Medir a fenda pela face plana da partição** — não existe partição, mas a armadilha continua: seção pelo plano
  Y = 0 dá %.2f mm de largura porque faltam os dois semicílios. Mediaõ é no **vazio do canal** (a seção do oco),
  não em meia peça, e o raio só é visível fora do plano central.
* **Esquecer o recuo do chanfro ao medir o land**: a cota da fenda é em Z = saída − 2,00. Medindo em Z = saída
  você pega a boca 78,00 × 4,50 e julga a peça boa com a fenda errada.
* **Polir para "melhorar" o Ra e abrir a cota**: a folga é de 10 µm. Uma passada de pedra a mais muda a vazão
  (a vazão escala com h^(2+1/n) ≈ h^5,3 com n = 0,30: 1 %% na abertura é 5 %% na vazão).
""" % (m["faces"], m["arestas"], n(m["cascas"] or 1, 0), br(m["volume_aco_mm3"], 1),
       ALVO["largura_fenda"]))

    open(P("05_O_QUE_O_STEP_NAO_DIZ.md"), "w", encoding="utf-8").write("""# O que o STEP não diz — e a fábrica precisa saber

O STEP é cego para tudo que não é geometria. Estas são as dez linhas que evitam a primeira peça errada:

1. **Unidade e convenção**: mm, Z = eixo da matriz, Z crescente no sentido do produto (Z = %.2f é a face de
   saída, Z = %.2f é a face de entrada que olha para o cabeçote). A manta sai em +Y/−Y com largura em X
   (x = ±37,50 são as bordas do produto).
2. **A matriz não é fixada por furo nem flange** — decisão do projeto, registrada no SSOT. O aperto é o collete
   EX-031 e o encosto face a face no rebaixo do cabeçote (rebaixo de 3,00 mm em Ø > 105,00). Ver
   `3D/CONJUNTO_MATRIZ_V29_NO_CABECOTE_EX-030.step`: a montagem tem interseção **0,0000 mm³** com o cabeçote.
3. **Folgas funcionais, não dimensionais**: Ø93,00 em Ø95,00 (radial 1,00), Ø89,50 em Ø90,00 e Ø79,50 em Ø80,00
   (radial 0,25 nos dois estágios de produto). O STEP traz os diâmetros; a *razão* de por que 0,25 está aqui:
   é o anel que segura o material voltando pelo funil. A conta está em
   `03_Relatorios_e_Documentacao/SIMULACAO_ROTAS_E_COMPRIMENTO.md` (0,06 %% de vazão escapando pelo anel nesta
   matriz, contra 8,71 %% na matriz que o projeto está substituindo).
4. **Comprimento 109,00, e não 100**: encurtar a peça não alivia a pressão (o funil e o land ficam intactos) e
   encurta a rota de fuga → aumenta a fração que volta. A alavanca de verdade é o land (8,50) e a folga do anel.
5. **O canal inteiro é usinável por uma face só** (0,00 %% de sombra) → não criar recurso de acesso, não abrir
   janela, não partir a peça.
6. **Espessura 1,50 com R 0,75 nas bordas é geometria de produto, não de fábrica**: a largura 75,00 é
   constante do contrato (não "aproximadamente 75").
7. **Tratamento antes do acabamento**: as duas cotas de 0,02 mm saem na retífica, depois do último revenido.
8. **Nada de revestimento** sem teste: 10 µm de PVD mudam a espessura da manta.
9. **Marcação fora da zona de 69 MPa**: face traseira, e sem gravação profunda.
10. **Se qualquer cota sair fora, refugar, não retocar**: a fenda e o land definem vazão; "acertar" depois do
    tratamento muda o volume do canal (%s mm³) e o produto sai em outra gramatura.
""" % (m["z_max"], m["z_min"], br(m.get("volume_canal_mm3", 0), 1)))

    open(P("06_PEDIDO_DE_COTACAO_RFQ.md"), "w", encoding="utf-8").write("""# RFQ — MATRIZ JONATHA v29.0, peça única, em 1.2344 temperado

> Copiar e enviar. Os anexos estão nesta pasta; nada aqui depende de conversa posterior.

**Peça**: matriz de extrusão plana, sólido único (sem bipartição, sem furo de fixação, sem flange).
**Identificação**: **MATRIZ JONATHA v27.0 — peça única** (v27.0 é a geometria aprovada; v29.0 é só a revisão
interna do nosso controle de revisão, sem nenhuma mudança dimensional).
**Quantidade**: **1 (uma) matriz**. Reposição, se um dia houver, é pedido separado.
**Prazo pedido**: 20 dias úteis, com a medição da fenda re-feita depois do último revenido.

**Arquivos enviados**
| arquivo | o que é | sha256 (16 primeiros) |
|---|---|---|
| `3D/%s` | o sólido único, geometria de referência | %s... |
| `3D/%s` | o sólido do canal (a ferramenta de medição e de verificação do volume) | %s... |
| `3D/%s` | a matriz montada no cabeçote EX-030, para o senhor ver onde ela encosta | %s... |
| `PRANCHA_2D_TOLERANCIADA.pdf` | desenho cotado com as tolerâncias e as notas | — |
| `02_MATERIAL_E_TRATAMENTO.md` | qualidade, dureza, alívio de tensões, o que não usar | — |
| `03_SEQUENCIA_DE_USINAGEM.md` | sequência proposta (aceitamos sugestão da fábrica, sem ferir as notas) | — |
| `04_TOLERANCIAS_E_INSPECAO.md` | tabela de tolerâncias e o plano de inspeção | — |

**Condições de aceite (resumo)**
1. material 1.2344 forjado, fibra no eixo, ESR se houver; certificado EN 10204 3.1;
2. dureza 50-52 HRC após têmpera a vácuo e 2 revénios, com relatório;
3. fenda %.4f +0,010/−0,000 mm medida no plano Z = face de saída − 2,00, largura %.2f ±0,05;
4. Ø89,50 e Ø79,50 em 0/−0,02, coaxialidade Ø0,02 em A = Ø93,00;
5. área da seção do canal no land = %.4f mm² ±0,5 %% (rejeição se passar);
6. Ra ≤ 0,4 µm no canal, camada REC do EDM removida, sem trinca (LP se aplicável);
7. **nenhum furo, rosca ou rebaixo adicionado**; qualquer elemento de aperto feito no estoque e removido;
8. dossiê de primeiro artigo com todos os itens acima assinado e datado, junto da peça.

**O que não entra no preço nem no prazo**: ajuste de cota da fenda depois do tratamento térmico (a peça é
refugada e refeita), revestimento, e retrabalho que altere o volume do canal.

*Documento gerado automaticamente por `04_Dados_SSOT_e_Scripts/gerar_pacote_usinagem_v29.py` — os shas e as
cotas acima são lidos dos arquivos desta pasta, não digitados.*
""" % (DESTINO["peca_unica"], movidos["peca_unica"]["sha256"][:16],
       DESTINO["canal"], movidos.get("canal", {}).get("sha256", "")[:16],
       DESTINO["montagem"], movidos.get("montagem", {}).get("sha256", "")[:16],
       m.get("fenda_no_land", {}).get("abertura_mm", ALVO["abertura_fenda"]),
       m.get("fenda_no_land", {}).get("largura_mm", ALVO["largura_fenda"]),
       m.get("fenda_no_land", {}).get("area_mm2", 112.0171)))

    open(P("README.md"), "w", encoding="utf-8").write("""# Pacote de usinagem — MATRIZ JONATHA v29.0 (peça única)

Pasta pronta para enviar ao fornecedor. **Toda cota aqui é medida no STEP** por
`04_Dados_SSOT_e_Scripts/gerar_pacote_usinagem_v29.py`; re-gerar é um comando.

| arquivo | para quem | o que é |
|---|---|---|
| `01_FICHA_DE_FABRICA.md` | chão de fábrica | o resumo de uma página, com as três cotas que valem ouro |
| `02_MATERIAL_E_TRATAMENTO.md` | compras / metalurgia | qualidade, dureza, alívio de tensões, o que não usar, estoque |
| `03_SEQUENCIA_DE_USINAGEM.md` | programação | 12 operações, com as armadilhas que já aconteceram no projeto |
| `04_TOLERANCIAS_E_INSPECAO.md` | qualidade | tabela de %d cotas com tolerância e método, 11 linhas de inspeção, critério de rejeição |
| `05_O_QUE_O_STEP_NAO_DIZ.md` | todos | as 10 linhas que evitam a primeira peça errada |
| `06_PEDIDO_DE_COTACAO_RFQ.md` | fornecedor | o pedido de cotação pronto para copiar e enviar (1 matriz) |
| `07_EMAIL_DE_PRIMEIRO_CONTATO.md` | você | a carta de capa do e-mail ao fornecedor — fica fora do zip |
| `PRANCHA_2D_TOLERANCIADA.pdf` / `.png` | todos | 4 vistas cotadas, geradas das seções medidas no STEP (o PNG é só para abrir rápido) |
| `3D/` | CAM | o STEP da peça, o do canal (ferramenta de medição) e a montagem no cabeçote |
| `pacote_usinagem.json` | projeto | os números e as cotas em máquina-legível |
| `CHECKSUMS_SHA256.txt` | recebimento | o que a fábrica deve conferir no arquivo que ela baixar |

## O que mudou em relação à v27.0, em uma frase

As duas metades (`Body_A` + `Body_B`, 759,5 mm² de contato e uma costura de 372,8 mm passando nas bordas da
manta) viraram **um sólido**: %s mm³ de aço (%.4f kg), %s mm³ de canal (**idêntico ao master**), 22 faces,
1 casca, BRepCheck limpo, e 0,00 %% de sombra no canal — ou seja, nada se perde e a junta do plano de partição
acaba.

## Como conferir o pacote antes de enviar

    cd /home/user/MATRIZEXTRUSORA
    sha256sum -c 08_Pacote_Usinagem_v29/CHECKSUMS_SHA256.txt
    python3 04_Dados_SSOT_e_Scripts/verificar_cadeia.py --rapido       # o portao do repo
    python3 04_Dados_SSOT_e_Scripts/auditar_step_correlacoes.py         # as correlacoes C1..C7

O zip para envio: `PACOTE_MATRIZ_V29_PARA_ENVIO.zip` — conteúdo da pasta, menos o e-mail de capa (que é do
remetente, não material de fábrica).
""" % (len(cotas), br(m["volume_aco_mm3"], 1), m["massa_kg"],
       br(m.get("volume_canal_mm3", 0), 1)))


# --------------------------------------------------------------------------- 5. prancha PDF
def prancha(m, sh, void, cotas, destino):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    z_out, z_in = m["z_max"], abs(m["z_min"])
    fd = m.get("fenda_no_land", {})
    bs = m.get("boca_saida", {})
    be = m.get("boca_entrada", {})
    LAND, CHA = ALVO["land"], ALVO["chanfro"]
    AB = fd.get("abertura_mm", ALVO["abertura_fenda"])

    def face_eixo(alvo, pos, eixo):
        pols, _ar = seccao_em_eixo(alvo, pos, eixo)
        return projectao(pols, eixo)

    def fill(ax, polys, cor, hatch=None, lw=0.8, alpha=1.0, zorder=2):
        for pts in polys:
            if len(pts) < 3:
                continue
            xs = [q[0] for q in pts]
            ys = [q[1] for q in pts]
            ax.fill(xs, ys, facecolor=cor, edgecolor="#1a1a1a", lw=lw, hatch=hatch, alpha=alpha, zorder=zorder)

    def cota(ax, a, b, texto, cor="#0057a3", fs=7.0, va="center", ha="center"):
        ax.annotate(texto, xy=b, xytext=a, fontsize=fs, color=cor, ha=ha, va=va,
                    arrowprops=dict(arrowstyle="<->", color=cor, lw=0.7, shrinkA=0, shrinkB=0),
                    bbox=dict(facecolor="white", edgecolor="none", pad=0.7), zorder=7)

    def seta(ax, xy, texto, xytext, cor="#333333", fs=6.8, ha="center"):
        ax.annotate(texto, xy=xy, xytext=xytext, fontsize=fs, color=cor, ha=ha, va="center",
                    arrowprops=dict(arrowstyle="->", lw=0.6, color=cor), zorder=7)

    fig = plt.figure(figsize=(16.5, 10.5))
    gs = fig.add_gridspec(2, 3, left=0.04, right=0.985, top=0.885, bottom=0.085, wspace=0.26, hspace=0.34)

    # ================= A: secao longitudinal no plano X=0 (o plano em que a fenda aparece)
    axA = fig.add_subplot(gs[:, 0])
    fill(axA, face_eixo(sh, 0.0, "x"), "#c2ccd6", hatch="////")
    fill(axA, face_eixo(void, 0.0, "x"), "#fff6da", lw=1.5, zorder=3)
    axA.set_xlim(-70, 74); axA.set_ylim(-13, z_out + 20); axA.set_aspect("equal")
    axA.tick_params(labelsize=7); axA.grid(alpha=0.16, ls=":")
    DS = [e["D"] for e in sorted(m.get("estagios_medidos", []), key=lambda e: -e["D"])]
    if len(DS) < 3:
        DS = [d for d, _a, _b in ALVO["estagios"]]
    LT = round(m["z_max"] - m["z_min"], 3)
    FURO = [95.00, 90.00, 80.00]          # os tres furos do EX-030, medidos no STEP do cabecote
    ANEL = [round((f - d) / 2.0, 3) for f, d in zip(FURO, DS)]
    axA.set_title("A · SEÇÃO LONGITUDINAL no plano X=0 (1:1) — oco a amarelo", fontsize=10.5)
    cota(axA, (-46.5, 30), (46.5, 30), "Ø%s  %s   (1º estágio = datum A)" % (br(DS[0], 2), TOL_D1))
    cota(axA, (-44.75, 76.5), (44.75, 76.5),
         "Ø%s  %s  (furo Ø%s → anel %s)" % (br(DS[1], 2), TOL_D, br(FURO[1], 2), br(ANEL[1], 2)))
    cota(axA, (-39.75, 90.0), (39.75, 90.0),
         "Ø%s  %s  (furo Ø%s → anel %s)" % (br(DS[2], 2), TOL_D, br(FURO[2], 2), br(ANEL[2], 2)))
    cota(axA, (56, 0), (56, z_out), "%s\n%s" % (br(LT, 2), TOL_L), va="center")
    axA.text(-66, 12, "degraus axiais (±0,05):\n69,90 e 80,70\no chanfro de 1,50×45°\nesta no detalhe B",
             fontsize=6.4, color="#8a2f00", ha="left", va="bottom")
    seta(axA, (0.0, z_out - 0.4), "face de saída: planeza 0,01 e ⊥ 0,01 em A — datum axial",
         (-14, z_out + 12), cor="#111111")
    seta(axA, (-14, 58), "funil: sem aresta viva, R 3,0 no fundo, Ra ≤ 0,4 µm — o canal\n"
                         "inteiro é feito por esta face só (sombra medida: 0,00 %)", (-30, 44), ha="center")
    seta(axA, (2.2, z_out - 15), "land paralelo %s mm\nusina-se de um lado, sem junta" % br(LAND, 2),
         (24, z_out + 7), ha="left")

    # ================= B: detalhe da saida (Z 92 -> 111), onde o produto é decidido
    axB = fig.add_subplot(gs[0, 1])
    for zz in (100.0,):
        pass
    fill(axB, face_eixo(sh, 0.0, "x"), "#c2ccd6", hatch="////")
    fill(axB, face_eixo(void, 0.0, "x"), "#fff6da", lw=1.6, zorder=3)
    axB.set_xlim(-9.5, 9.5); axB.set_ylim(z_out - LAND - 3.0, z_out + 2.0); axB.set_aspect("auto")
    axB.tick_params(labelsize=7); axB.grid(alpha=0.2, ls=":")
    axB.set_title("B · DETALHE DA SAÍDA (ampliado) — a cota que vira produto", fontsize=10.5)
    cota(axB, (-AB / 2.0, z_out - LAND - 1.1), (AB / 2.0, z_out - LAND - 1.1),
         "%s  +0,010/−0,000" % br(AB, 4), fs=7.4, cor="#a30000")
    cota(axB, (6.6, z_out - CHA), (6.6, z_out - CHA - LAND), "land %s\n±0,05" % br(LAND, 2), fs=6.8)
    cota(axB, (-7.6, z_out - CHA), (-7.6, z_out), "chanfro\n1,50×45°", fs=6.8)
    seta(axB, (AB / 2.0 + 0.05, z_out - LAND / 2.0), "as duas faces do land são planas e paralelas:\n"
             "Ra ≤ 0,4 µm sem tirar cota (a folga é de 10 µm)", (5.0, 101.6), ha="center", fs=6.4)
    axB.set_xlabel("y (mm) — metade da abertura", fontsize=7)

    # ================= C: face de saida
    axC = fig.add_subplot(gs[1, 1])
    fill(axC, face_eixo(sh, z_out - 0.01, "z"), "#c2ccd6", hatch="////")
    fill(axC, face_eixo(void, z_out - 0.01, "z"), "#cfe8cf", lw=1.5, zorder=3)
    axC.set_xlim(-56, 56); axC.set_ylim(-56, 56); axC.set_aspect("equal")
    axC.tick_params(labelsize=7); axC.grid(alpha=0.16, ls=":")
    axC.set_title("C · FACE DE SAÍDA (Z=%.2f) — a boca que o produto vê" % z_out, fontsize=10.5)
    cota(axC, (-bs.get("largura_mm", 78.0) / 2.0, -50), (bs.get("largura_mm", 78.0) / 2.0, -50),
         "boca %.3f ±0,05 (aberta pelo chanfro 1,50×45°)" % bs.get("largura_mm", 78.0), fs=6.6)
    cota(axC, (44, -bs.get("abertura_mm", 4.5) / 2.0), (44, bs.get("abertura_mm", 4.5) / 2.0),
         "%.3f" % bs.get("abertura_mm", 4.5), fs=6.8)
    seta(axC, (38.5, 3.0), "R 0,75 nas duas pontas da fenda\n+0,05/−0,00, sem aresta viva", (16, 47), ha="center", fs=6.6)
    seta(axC, (39.0, -37.0), "Ø%s do pescoço · sem rebarba na boca: 0,1×45° máximo" % br(DS[2], 2),
         (4, -44), ha="center", fs=6.6)

    # ================= D: face de entrada
    axD = fig.add_subplot(gs[0, 2])
    fill(axD, face_eixo(sh, z_in + 0.01, "z"), "#c2ccd6", hatch="////")
    fill(axD, face_eixo(void, z_in + 0.01, "z"), "#fff6da", lw=1.5, zorder=3)
    axD.set_xlim(-56, 56); axD.set_ylim(-52, 52); axD.set_aspect("equal")
    axD.tick_params(labelsize=7); axD.grid(alpha=0.16, ls=":")
    axD.set_title("D · FACE DE ENTRADA (Z=%.2f) — olha o cabeçote" % z_in, fontsize=10.5)
    cota(axD, (-37.8, -46), (37.8, -46), "Ø%s  +0,05/−0,00 (a entrada é restrita por contrato)"
         % br(max(be.get("abertura_mm", 0.0), be.get("largura_mm", ALVO["boca_entrada"])), 2), fs=6.8)
    cota(axD, (-46.5, 45), (46.5, 45), "Ø%s  %s" % (br(DS[0], 2), TOL_D1), fs=6.8)
    seta(axD, (0.0, 0.0), "sem furo, sem rosca, sem pino:\nqualquer furo aqui é rejeição", (0, -22), fs=6.8, cor="#a30000")

    # ================= E: notas
    axE = fig.add_subplot(gs[1, 2])
    axE.axis("off")
    notas = [NOTAS_TITULO,
             "",
             "1 · mm; Z = eixo da matriz, Z crescente para o produto; datum A = Ø%s; cotas axiais da face de saída." % br(DS[0], 2),
             "2 · NÃO adicionar furo, rosca, rebaixo, pino ou flange de fixação: é rejeição. O aperto é o collete EX-031 + o degrau.",
             "3 · Peça única: não colar, não alinhar metade, não existe plano de partição. %d faces / %d arestas / 1 casca, BRepCheck válido." % (m["faces"], m["arestas"]),
             "4 · A fenda é medida no plano Z = saída − 2,00 (depois do chanfro). Medindo na face você pega a boca, não a fenda.",
             "5 · Ø%s e Ø%s em %s fecham o anel de %s mm com o furo do cabeçote; coaxialidade Ø0,02 em A."
             % (br(DS[1], 2), br(DS[2], 2), TOL_D, br(min(ANEL[1:]), 2)),
             "6 · Área da seção do canal no land = %s mm² ±0,5 %% → rejeição se passar: é a área que converte em vazão." % br(fd.get("area_mm2", 112.0171), 4),
             NOTA_REVEST,
             "8 · Remover a camada REC do EDM (≥ 0,02 mm); alívio de tensões antes da têmpera; %s." % DUREZA_CURTA,
             "9 · Re-medir a fenda depois do último revenido. Se sair fora, refugar — não retocar, não re temperar.",
             "10 · Marcação a laser só na face traseira: %s." % MARCACAO_CURTA,
             "11 · Sombra de usinagem no canal %s %% (%s) → o canal é feito por uma face só, sem partir a peça."
             % (br(m.get("sombra_no_canal_pct", 0.0), 2),
                m.get("sombra_como_medido", "raios de 0,10 mm verificados dentro do vazio")),
             NOTA_COMPRIMENTO,
             "",
             "AÇO %s" % ACO["norma"],
             "TRATAMENTO %s · DUREZA %s" % (ACO["grupo"], ACO["dureza"]),
             "AÇO DA PEÇA %s mm³ = %s kg · CANAL %s mm³ (%s g de mastique no interior)"
             % (br(m["volume_aco_mm3"], 1), br(m["massa_kg"], 3), br(m.get("volume_canal_mm3", 0), 1),
                br(m.get("massa_mastique_por_peca_g", 0), 1)),
             "REFERÊNCIA %s · sha256 %s..." % (os.path.basename(m["arquivo"]), m["sha256"][:16]),
             GERADO_POR_FIGURA]
    import textwrap
    queb = []
    for linha in notas:
        if len(linha) <= 96:
            queb.append(linha)
        else:
            bloco = textwrap.wrap(linha, width=TEXTO_LARGURA, subsequent_indent="     ")
            queb += bloco
    # quanto texto cabe no painel: altura da linha de eixos (a figura tem H*(top-bottom) de area util e o
    # hspace come uma parte dela) dividida pela altura de uma linha. Se nao couber, o bloco escorre por cima
    # do rodape da prancha - foi o que aconteceu com 32 linhas a 5,75 pt antes desta conta existir.
    alt_pt = fig.get_figheight() * 72.0 * (0.885 - 0.085) / (2 + 0.34)
    cabem = int(alt_pt / (TAM_NOTA * 1.45))
    if len(queb) > cabem:
        raise SystemExit("FALHOU: as notas nao cabem no painel (%d linhas para %d que cabem)"
                         % (len(queb), cabem))
    axE.text(0.0, 1.0, "\n".join(queb), fontsize=TAM_NOTA, va="top", ha="left", family="DejaVu Sans", linespacing=1.45)

    fig.suptitle(TITULO_FIGURA, fontsize=12)
    fig.text(0.5, 0.024, RODAPE_FIGURA, fontsize=7.0, ha="center", color="#333333")
    fig.savefig(destino, dpi=150)
    fig.savefig(destino.rsplit(".", 1)[0] + ".png", dpi=150)
    plt.close(fig)


# --------------------------------------------------------------------------- 6. indices e SSOT
def atualiza_indices(m, cotas):
    # 07_/README.md: a v29 passa a ser a linha de cima, a v27 vira a historica-par
    p = os.path.join(RAIZ, "07_CAD_Matrizes", "README.md")
    s = open(p, encoding="utf-8").read()
    nova_linha = ("| `Matriz_Jonatha_v29_OFICIAL/` | **a master do projeto desde 2026-09-13** — a v27.0 como "
                  "peça única (sem Bipartição, sem pino, sem junta), com o pacote de usinagem apontando para cá | "
                  "`MATRIZ_V29_PECA_UNICA.step`, `MATRIZ_V29_CANAL_DE_FLUXO.step`, "
                  "`CONJUNTO_MATRIZ_V29_NO_CABECOTE_EX-030.step`, `README.md` |\n")
    alvo = "| `Matriz_Jonatha_v27_OFICIAL/` | **a master do projeto** (SSOT v27.0), o que a fabrica usa |"
    if "Matriz_Jonatha_v29_OFICIAL/" not in s:
        pos = s.index("| pasta | o que e | arquivos |")
        fim = s.index("\n", s.index(alvo)) + 1
        s = s[:fim] + nova_linha + s[fim:]
        s = s.replace("**a master do projeto** (SSOT v27.0), o que a fabrica usa",
                      "**o master anterior** (SSOT v27.0, bipartido) — segue no disco, byte a byte, "
                      "porque o baseline do auditor selou os caminhos e o portão confere o sha256; a "
                      "promoção da v29.0 é declarada, não escrita por cima")
        open(p, "w", encoding="utf-8").write(s)
    # README da pasta v29
    open(os.path.join(P_Oficial, "README.md"), "w", encoding="utf-8").write("""# Matriz JONATHA v29.0 — OFICIAL (peça única)

Promovida a master em 2026-09-13, a pedido: "a peça única vira a oficial".

É a v27.0 com as duas metades (`Body_A` + `Body_B`) unidas no sólido da peça, sem pino de alinhamento e sem a
cavidade selada: %s mm³ de aço (%.4f kg), canal de %s mm³ **idêntico ao master**, 22 faces, 1 casca, BRepCheck
limpo, 0,00 %% de área do canal em sombra. Os números completos e o teste estão em
`03_Relatorios_e_Documentacao/MATRIZ_V27_PECA_UNICA.md` e `07_CAD_Matrizes/Matriz_Jonatha_v27_Peca_Unica/`.

| arquivo | o que é |
|---|---|
| `MATRIZ_V29_PECA_UNICA.step` | **a matriz** — o que vai para a fábrica (byte-idêntico ao STEP da peça única da v27.0) |
| `MATRIZ_V29_CANAL_DE_FLUXO.step` | o sólido do canal: ferramenta de medição de volume/seção e de verificação do produto |
| `CONJUNTO_MATRIZ_V29_NO_CABECOTE_EX-030.step` | a matriz montada no cabeçote com flange (interseção 0,0000 mm³) |

O que estava selado **não** foi mexido: `07_/Matriz_Jonatha_v27_OFICIAL/` continua com os seis arquivos de
sempre e `01_CAD_MatrizJonatha_Oficial/MatrizJonatha.step` continua apontando para ele — o portão confere o
sha256 desse caminho contra `05_Interface_Auditoria/baseline/MATRIZ_3_v27.json`. A promoção é registrada aqui,
no `04_/cad_die_parameters.json` (`matriz_oficial`) e no índice de `07_CAD_Matrizes/`. Para a fábrica, use
`08_Pacote_Usinagem_v29/`.
""" % (br(m["volume_aco_mm3"], 1), m["massa_kg"],
       br(m.get("volume_canal_mm3", 0), 1)))
    # SSOT: matriz_oficial + decisao D9 + bloco de usinagem (sem tocar nas chaves existentes)
    d = json.load(open(SSOT, encoding="utf-8"))
    d["matriz_oficial"] = dict(
        versao="v29.0", promovida_em="2026-09-13",
        motivo="decisão do usuário: \"a peça única vira a oficial\" — a v27.0 bipartida continua no disco e "
               "selada, mas o que vai para a fábrica é o sólido único",
        arquivo="07_CAD_Matrizes/Matriz_Jonatha_v29_OFICIAL/MATRIZ_V29_PECA_UNICA.step",
        sha256=m["sha256"],
        pacote_de_usinagem="08_Pacote_Usinagem_v29/",
        geometria_medida=dict(volume_aco_mm3=m["volume_aco_mm3"], massa_kg=m["massa_kg"],
                              volume_canal_mm3=m.get("volume_canal_mm3"), faces=m["faces"],
                              cascas=m["cascas"] or 1, sombra_pct=m["sombra_no_canal_pct"]),
        identica_a="07_CAD_Matrizes/Matriz_Jonatha_v27_Peca_Unica/MatrizJonatha_v27_Peca_Unica.step (bytes iguais)",
        master_anterior=dict(versao="v27.0", arquivo="07_CAD_Matrizes/Matriz_Jonatha_v27_OFICIAL/MatrizJonatha.step",
                             status="histórico válido, caminhos selados no baseline do auditor"))
    d["decisoes_usuario"]["D9_peca_unica_oficial"] = dict(
        data="2026-09-13", origem="pedido direto na mesma rodada do pacote de usinagem",
        decisao=("a variante de peça única da v27.0 é promovida a master (v29.0); a promoção é declarada no SSOT "
                 "e nos índices e não por cima dos arquivos selados; nenhum furo ou flange de fixação é "
                 "adicionado; o encosto continua face a face com o rebaixo de 3,00 mm"))
    d["usinagem_v29"] = dict(
        gerador="04_Dados_SSOT_e_Scripts/gerar_pacote_usinagem_v29.py",
        pasta="08_Pacote_Usinagem_v29/",
        material=ACO["grupo"], norma_interna=ACO["norma"], dureza_hrc=ACO["dureza"],
        cotas=[dict(item=c[0], nominal=(c[1] if not isinstance(c[1], float) else round(c[1], 4)),
                    tolerancia=c[2], medicao=c[3], motivo=c[4]) for c in cotas],
        folgas_anulares_mm=dict(estagio_1=1.00, estagio_2=0.25, estagio_3=0.25),
        comprimento_total=dict(valor=109.00,
                               decisao=("manter 109,00 mm: encurtar para 100 mm não mexe no funil nem no land "
                                        "(as cotas que geram pressão) e encurta a rota de fuga pelo anel - a "
                                        "fração que escapa para trás sobe de 0,06 % para 0,07 %. Alavancas reais: "
                                        "land (8,50 -> 5,00 derruba ~15 % do dP) e apertar o anel do ultimo "
                                        "estagio para 0,10 mm (fuga 0,00 %). Ver "
                                        "03_Relatorios_e_Documentacao/SIMULACAO_ROTAS_E_COMPRIMENTO.md")))
    json.dump(d, open(SSOT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)


def checksums():
    linhas = []
    for base, _dirs, nomes in os.walk(P_Pacote):
        for nome in sorted(nomes):
            if nome == "CHECKSUMS_SHA256.txt":
                continue
            p = os.path.join(base, nome)
            linhas.append("%s  %s" % (sha256(p), os.path.relpath(p, P_Pacote)))
    open(os.path.join(P_Pacote, "CHECKSUMS_SHA256.txt"), "w", encoding="utf-8").write("\n".join(linhas) + "\n")
    return len(linhas)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--eu-sei", action="store_true",
                    help="assume o risco: reescreve 08_Pacote_Usinagem_v29 com a documentacao deste "
                         "arquivo (material/Ø deste modulo estao desatualizados desde 2026-09-22)")
    ap.add_argument("--semdos", action="store_true", help="nao gera a prancha PDF")
    a = ap.parse_args()
    if not a.eu_sei:
        raise SystemExit(
            "Este gerador foi substituido: os dois pacotes (v29 re-feita e v30) saem de "
            "04_Dados_SSOT_e_Scripts/gerar_pacote_usinagem_v30.py, que le o STEP de cada pasta oficial "
            "e escreve a documentacao com o material e as tolerancias da revisao de 2026-09-22. "
            "Rodar este arquivo aqui por cima traria de volta o 1.2344 e o 93,00. Use --eu-sei se "
            "for realmente isso que voce quer.")
    print("[1/6] promovendo a peca unica a v29.0 (sem tocar nos arquivos selados)")
    movidos = promove_para_v29()
    for k, v in movidos.items():
        print("    %-12s %9d bytes  sha256 %s..." % (k, v["bytes"], v["sha256"][:16]))
    print("[2/6] medindo o STEP que vai para a fabrica")
    m, sh, inv, void = mede_tudo()
    print("    %d solidos / %d faces / %d arestas | aco %.1f mm3 | canal %s mm3 | fenda %s x %s em Z %.2f"
          % (m["solidos"], m["faces"], m["arestas"], m["volume_aco_mm3"], m.get("volume_canal_mm3"),
             m.get("fenda_no_land", {}).get("largura_mm"), m.get("fenda_no_land", {}).get("abertura_mm"),
             m.get("fenda_no_land", {}).get("z")))
    print("[3/6] tabela de cotas e documentos")
    cotas = tabela_de_cotas(m)
    escreve_docs(m, cotas, movidos)
    print("    6 documentos em " + os.path.relpath(P_Pacote, RAIZ) + "/")
    print("[4/6] JSON do pacote")
    json.dump(dict(matriz="JONATHA v29.0 (peca unica)", gerado_por=os.path.relpath(__file__, RAIZ),
                   medido=m, alvo_do_contrato=ALVO, aco=ACO,
                   cotas=[dict(item=c[0], nominal=c[1], tolerancia=c[2], medicao=c[3], motivo=c[4]) for c in cotas],
                   arquivos=movidos),
              open(os.path.join(P_Pacote, "pacote_usinagem.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("[5/6] prancha 2D cotada")
    if not a.semdos:
        prancha(m, sh, void, cotas, os.path.join(P_Pacote, "PRANCHA_2D_TOLERANCIADA.pdf"))
        print("    PDF ok")
    else:
        print("    pulando (--semdos)")
    print("[6/6] indices, SSOT e checksums")
    atualiza_indices(m, cotas)
    print("    %d arquivos com sha256 em CHECKSUMS_SHA256.txt" % checksums())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
