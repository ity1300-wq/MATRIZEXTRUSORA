#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pacotes de usinagem das revisões de 2026-09-22: v29 re-feita (Ø94/89/79) e v30 faceada ao nariz (L 95,00).

Mesma regra da casa: **toda cota sai medida do STEP** que vai para a fábrica. Este script não inventa número —
ele chama o medidor do pacote anterior (`gerar_pacote_usinagem_v29.mede_tudo`), que abre o STEP, corta seções
de 0,02 mm e devolve envelope, estágios, land, chanfro, fenda, canal, massa e sombras de usinagem. O que é
novo aqui é a camada de decisão: o material passou a **aço 1045 com tratamento superficial na fenda** e as
cotas que o dono alterou levam **±0,5** — as duas coisas entram na ficha, na tabela, na sequência de usinagem
e no RFQ.

Escreve, para cada revisão:
  08_Pacote_Usinagem_v29/   e   08_Pacote_Usinagem_v30/
      01_FICHA_DE_FABRICA.md · 02_MATERIAL_E_TRATAMENTO.md · 03_SEQUENCIA_DE_USINAGEM.md
      04_TOLERANCIAS_E_INSPECAO.md · 05_O_QUE_O_STEP_NAO_DIZ.md · 06_PEDIDO_DE_COTACAO_RFQ.md
      PRANCHA_2D_TOLERANCIADA.pdf/.png · 3D/*.step · pacote_usinagem.json · CHECKSUMS_SHA256.txt
      PACOTE_MATRIZ_<rev>_PARA_ENVIO.zip · 07_EMAIL_DE_PRIMEIRO_CONTATO.md (capa, FORA do zip: guarda o sha do zip)

Ordem obrigatória no fim (senão o pacote se auto-referencia): conteúdo → CHECKSUMS → zip → sha do zip na capa.

Uso: python3 04_Dados_SSOT_e_Scripts/gerar_pacote_usinagem_v30.py [--rev v30] [--semdos]
"""
import argparse
import io
import json
import os
import shutil
import sys
import zipfile

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, ".."))
sys.path.insert(0, AQUI)

from auditar_step_correlacoes import n  # noqa: E402
import gerar_pacote_usinagem_v29 as G    # noqa: E402  (medidor + prancha: reusados, nao re-escritos)

REV_JSON = os.path.join(AQUI, "revisoes_v29_v30.json")

# ---------------------------------------------------------------- a decisao nova sobre o material
ACO_1045 = dict(
    grupo="aço carbono SAE 1045 (EN C45E) — decisão do dono em 2026-09-22, substitui o 1.2344 da proposta",
    norma="SAE J404 / EN 10083-2: aço 1045, barra forjada, fibra no eixo, condição de entrega normalizada (≤ 220 HB)",
    dureza="corpo revenido 30-36 HRC; arestas do land 55-60 HRC em camada de 0,6-1,0 mm por indução "
           "(ou nitretação a plasma 520 °C, 8-18 µm, se a fábrica preferir tratar a fenda inteira) — escolha "
           "da fábrica, declarada no relatório",
    densidade=7.85e-6)

OBS_MATERIAL = (
    "Por que o 1045 é diferente do 1.2344 que estava aqui: o 1045 não é aço de trabalho a quente. Ele não "
    "tem cromo/molibdênio/vanádio suficientes para manter dureza quando aquecido, e a temperabilidade dele "
    "acaba por volta de 20-25 mm de seção em água. Na prática desta matriz: (a) o núcleo do Ø94 fica em "
    "30-36 HRC mesmo com têmpera, e é a indução (ou a nitretação) no land que segura o desgaste da fenda; "
    "(b) o produto sai a ~90 °C, então não há revenimento em serviço - o 1045 aguenta isso; (c) o risco real "
    "é trinca na têmpera, porque a peça tem uma fenda de 1,500 mm atravessando 95 mm de aço e o 1045 é "
    "temperado em água/salina. Daí a sequência abaixo: fenda aberta por fio EDM DEPOIS do tratamento térmico "
    "do corpo, e indução só nas arestas, com a cota 1,500 re-medida no fim.")

Z12, Z23 = 69.90, 80.70


_PROTEGER = ("1.2344", "EN 10204 3.1", "ISO 4957", "SAE J404", "EN 10083-2", "X37CrMoV5-1",
             "v27.0", "v28.1", "v29.0", "v30.0", "EX-030", "EX-031", "C45E", "0.02 mm")


def _bra(txt):
    """Decimais com virgula, que e o padrao dos documentos daqui (a casa escreve 94,00, nao 94.00). So troca o
    ponto quando ele e separador decimal de um numero solto; os tokens acima (aço 1.2344, norma EN 10204 3.1,
    rotulos de revisao, codigos de peça) sao protegidos antes da troca."""
    import re
    for i, p in enumerate(_PROTEGER):
        txt = txt.replace(p, "\x00%d\x00" % i)
    txt = re.sub(r"(\d+)\.(\d{1,4})", lambda m: m.group(1) + "," + m.group(2), txt)
    for i, p in enumerate(_PROTEGER):
        txt = txt.replace("\x00%d\x00" % i, p)
    return txt


def n_str(x):
    return ("%.2f" % x).replace(".", ",")


def escreve(pacote, nome, txt):
    """escreve um arquivo do pacote (garante UTF-8 e cria a pasta)"""
    os.makedirs(pacote, exist_ok=True)
    io.open(os.path.join(pacote, nome), "w", encoding="utf-8").write(_bra(txt))
REV = {
    "v29": dict(
        pasta="08_Pacote_Usinagem_v29", oficial="Matriz_Jonatha_v29_OFICIAL",
        step="MATRIZ_V29_PECA_UNICA.step", canal="MATRIZ_V29_CANAL_DE_FLUXO.step",
        montagem="Cabecote_EX-030_com_Matriz_Jonatha_v29.step",
        zip="PACOTE_MATRIZ_V29_PARA_ENVIO.zip", L=109.00, D=[94.00, 89.00, 79.00],
        rotulo="JONATHA v27.0 · rev. geom. 2026-09-22",
        nota_comprimento="comprimento 109,00 inalterado (cota não alterada: tolerância continua 0 / −0,05)",
        protrusao="a face de saída fica 14,00 mm além da face do nariz do cabeçote (é a cota original)"),
    "v30": dict(
        pasta="08_Pacote_Usinagem_v30", oficial="Matriz_Jonatha_v30_OFICIAL",
        step="MATRIZ_V30_PECA_UNICA.step", canal="MATRIZ_V30_CANAL_DE_FLUXO.step",
        montagem="Cabecote_EX-030_com_Matriz_Jonatha_v30.step",
        zip="PACOTE_MATRIZ_V30_PARA_ENVIO.zip", L=95.00, D=[94.00, 89.00, 79.00],
        rotulo="JONATHA v27.0 · rev. 30 (2026-09-22)",
        nota_comprimento="comprimento 95,00 = 109,00 − 14,00, a face de saída faceada com a face do nariz do "
                         "cabeçote EX-030; cota ALTERADA, leva ±0,5. Consequência medida: com +0,5 mm a matriz "
                         "passaria 0,5 mm para fora do nariz, então o aceitável prático é 95,00/−0,50 +0,00 "
                         "se a fábrica preferir apertar - a decisão de manter ±0,5 é do dono, o alerta é nosso",
        protrusao="protrusão 0,00 mm medida na montagem: a face de saída coincide com a face do nariz"),
}


def tabela(r, m):
    """A tabela do pacote anterior, com as linhas das cotas ALTERADAS reescritas a partir da MEDICAO."""
    cotas = list(G.tabela_de_cotas(m))
    ds = [e["D"] for e in sorted(m["estagios_medidos"], key=lambda e: -e["D"])]
    L = round(m["z_max"] - m["z_min"], 3)
    if [round(x, 2) for x in ds] != r["D"]:
        raise SystemExit("FALHOU: os Ø medidos no STEP (%s) não batem com os do perfil (%s)" % (ds, r["D"]))
    out = []
    for item, nom, tol, como, porq in cotas:
        # atencao: casar pelo NOME INTEIRO. Uma versao anterior cortava item[:9] e "Diâmetro do 1" tem 12
        # caracteres - as tres linhas de Ø passavam sem correcao nenhuma e o pacote saia com 93,00/89,50/79,50.
        if item.startswith("Diâmetro do 1"):
            item = "Diâmetro do 1º estágio — Ø%.2f no furo Ø95,00 do cabeçote" % ds[0]
            nom, tol = ds[0], "±0,5 (cota alterada em 2026-09-22)"+ "; medição: micrômetro 3 posições"
            porq = ("folga radial de 0,50 mm no furo; datum A da peça e o cilindro do Ø%.2f, não o degrau" % ds[0])
        elif item.startswith("Diâmetro do 2"):
            item = "Diâmetro do 2º estágio — Ø%.2f no furo Ø90,00" % ds[1]
            nom, tol = ds[1], "±0,5 (cota alterada em 2026-09-22)"
            porq = "fecha o anel de 0,50 mm entre a matriz e o furo do nariz; é cota de folga, não de produto"
        elif item.startswith("Diâmetro do 3"):
            item = "Diâmetro do 3º estágio / pescoço — Ø%.2f no furo Ø80,00" % ds[2]
            nom, tol = ds[2], "±0,5 (cota alterada em 2026-09-22)"
            porq = "mesma razão do 2º; o Ø%.2f é o maior Ø que passa no furo Ø80,00 com folga em toda a volta" % ds[2]
        elif item == "Comprimento total":
            nom, tol = L, ("±0,5 (cota alterada em 2026-09-22)" if abs(L - 109.00) > 0.01
                           else "0 / −0,05 (não alterada)")
            porq = r["nota_comprimento"]
        elif item.startswith("Dureza"):
            nom, tol, como = 33.0, "corpo 30-36 HRC; arestas do land 55-60 HRC (indução) ou 600-700 HV0,2 (nitretação)", \
                "durômetro na face traseira (HRC) + microdureza em seção cortada de corpo de prova do lote"
            porq = "o 1045 não chega a 50 HRC no núcleo de Ø94; a dureza útil desta matriz vive na aresta do land"
        elif item.startswith("Marcação"):
            nom = 0.0
            tol = ("a laser: JONATHA v27.0 · EX-031 · 1045 · %s · lote · nº de série · data, na face traseira, "
                   "fora do furo" % r["rotulo"].split("·")[-1].strip())
            porq = ("a marcação não pode entrar na zona do degrau nem na face de assentamento; a peça é a "
                    "JONATHA v27.0 para a fábrica - 'rev. 29/30' é carimbo interno do projeto")
        out.append((item, nom, tol, como, porq))
    out.append(("Tratamento superficial na fenda (pedido do dono)", 0.0,
                "indução nas arestas do land 0,6-1,0 mm OU nitretação a plasma 8-18 µm; sem cobre, sem jato "
                "de granalha no canal; Ra do canal continua ≤ 0,4 µm",
                "medir a abertura da fenda ANTES e DEPOIS do tratamento e gravar os dois números no relatório "
                "dimensional", "qualquer camada em cima de 1,500 mm muda a espessura da manta; se o tratamento "
                "abrir ou fechar a fenda, o aceitável continua 1,500 +0,010/−0,000 e o retrabalho é passar o "
                "fio de novo, não 'aceitar como está'"))
    return out


def fmt_tabela(cotas):
    L = ["| # | cota | nominal (mm) | tolerância | como medir | por que |",
         "|---:|---|---:|---|---|---|"]
    for i, (item, nom, tol, como, porq) in enumerate(cotas, 1):
        v = "—" if nom == 0.0 else ("%.4f" % nom if isinstance(nom, float) and nom < 10 else "%.3f" % nom)
        L.append("| %d | %s | %s | %s | %s | %s |" % (i, item.replace("|", "/"), v, str(tol).replace("|", "/"),
                                                       como, porq))
    return "\n".join(L)


def docs(r, m, cotas, movidos, pacote, rev_json):
    d = rev_json["v29" if r["L"] == 109.00 else "v30"]
    mo, med = d["montagem"], d["medidas"]
    est = "\n".join("  - Ø%.2f em Z %.2f → %.2f · folga radial %.2f mm no furo Ø%.2f"
                    % (f["estagio_Ø"], f["z"][0], f["z"][1], f["folga_radial"], f["furo_Ø"])
                    for f in mo["folgas_por_estagio"] if f.get("folga_radial") is not None)
    fc = m["fenda_no_land"]
    ch = (med["canal"].get("chanfro") or {})
    cz0, cz1 = (ch.get("z") or [0.0, 0.0])[:2]
    cz = "cone medido em Z %.2f → %.2f" % (cz0, cz1) if ch else "cone não identificado no STEP" 
    escreve(pacote, "01_FICHA_DE_FABRICA.md", f"""# Ficha de fábrica — MATRIZ {r['rotulo']}

**Peça única, 1 sólido, sem flange, sem furo de fixação, sem linha de junção.** Material: **{G.ACO['norma'].split('(')[0].strip()}**.
Quantidade pedida: **1 matriz** (sem lote). Gerado por medição no STEP `3D/{r['step']}` (sha256 `{med['sha256'][:16]}…`).

| o que | valor medido no STEP |
|---|---|
| envelope maior (1º estágio) | Ø{n(m['envelope_x_mm'],2)} × comprimento {n(m['z_max']-m['z_min'],2)} mm |
| estágios e faixas em Z | Ø{r['D'][0]:.2f} (0→{Z12:.2f}) · Ø{r['D'][1]:.2f} ({Z12:.2f}→{Z23:.2f}) · Ø{r['D'][2]:.2f} ({Z23:.2f}→{r['L']:.2f}) |
| fenda no land | largura {n(fc['largura_mm'],4)} mm × abertura **{n(fc['abertura_mm'],3)} mm** (R{n(m.get('raio_borda', 0.75),2)} nas pontas), área {n(fc['area_mm2'],4)} mm² |
| land paralelo | {n(med['canal']['land'],3)} mm (Z {n(med['canal']['z_land'],2)} → {n(med['canal']['z_land'] + med['canal']['land'],2)}) |
| chanfro de saída | 1,50 × 45°, boca {n(m['boca_saida']['largura_mm'],2)} × {n(m['boca_saida']['abertura_mm'],2)} mm ({cz}) |
| boca de entrada | Ø{n(med['canal']['boca_entrada'],2)} (restrita por contrato: não alargar) |
| volume de aço / massa | {n(m['volume_aco_mm3'],1)} mm³ → **{n(m['massa_kg'],3)} kg** em 1045 (7,85 g/cm³) |
| canal (vazio de fluxo) | {n(m['volume_canal_mm3'],1)} mm³ = {n(m.get('massa_mastique_por_peca_g',0),1)} g de mastique dentro da matriz |
| protrusão no cabeçote | {r['protrusao']} |

## As três coisas que a fábrica precisa saber antes de ligar a máquina

1. **Não tem flange, não tem furo de fixação, não tem pino.** A matriz é segurada pelo collete EX-031 e pelo
   degrau do furo do cabeçote. Furo "útil" para segurar a peça é rejeição: entraria na zona de ~69 MPa do
   degrau. Elemento de aperto só no estoque, antes do tratamento térmico, fora do envelope final.
2. **A peça não é bipartida e isso é o produto.** A v27.0 era um par `Body_A`+`Body_B` colado em Y = 0 com
   junta de 1.513,1 mm² por metade e uma costura de 372,8 mm passando nas bordas da manta (x = ±37,50) — a
   "serra" na borda do produto vinha daí. Aqui a única superfície funcional é a do canal usinado.
3. **O canal é feito de um lado só.** Proibido partir a peça para usinar: fio EDM com o arame entrando pela boca
   de entrada Ø{n(med['canal']['boca_entrada'],2)} e polimento na direção da extrusão. Sombra de usinagem medida no
   modelo: 0,00 % de área sem acesso reto.

## Interface com o EX-030 (medida na montagem `3D/{r['montagem']}`)

{est}

Interferência matriz × cabeçote: **{n(mo['interferencia_mm3'],4)} mm³** (zero é o certo — a matriz desliza nos
furos e encosta face a face no rebaixo, `deslocamento_aplicado_mm` = {mo['deslocamento_aplicado_mm']:.2f}).
""")

    escreve(pacote, "02_MATERIAL_E_TRATAMENTO.md", f"""# Material e tratamento — aço 1045 (decisão de 2026-09-22)

| item | especificação |
|---|---|
| aço | **{G.ACO['norma']}** |
| condição de entrega | normalizada, ≤ 220 HB, usinar mole; fibra no eixo da peça |
| dureza final | {G.ACO['dureza']} |
| densidade | 7,85 g/cm³ → {n(m['massa_kg'],3)} kg por peça |
| certificação | EN 10204 3.1 do calor: composição, granulometria, inclusão, resultado de têmpera/revenimento |
| tratamento na fenda | **pedido do dono**: indução nas arestas do land **ou** nitretação a plasma na região da fenda, à escolha da fábrica, declarado no relatório |

{OBS_MATERIAL}

## O que o tratamento pode fazer com a cota de 1,500 mm (e o que fazer com isso)

A abertura da fenda é +0,010 / −0,000. Uma camada de nitretação de 8-18 µm por face come 0,016-0,036 mm da
abertura — **mais que a tolerância inteira**. Indução não adiciona material, mas expande a superfície e move
0,005-0,020 mm na zona tratada. Portanto:

1. medir a abertura **antes** do tratamento e **depois**, gravar os dois números;
2. se depois do tratamento a abertura cair abaixo de 1,500, o retrabalho é **passar o fio de novo** na região
   e re-medir; não é "aceitar como está";
3. nenhuma peça é embalada sem a leitura final de 1,500 na boca de saída, no meio da largura e nas duas bordas;
4. se a fábrica optar por revestimento (PVD/DLC), isso **não foi pedido** — o 1045 com revestimento de 2-4 µm
   muda a geometria do produto e a gente não aceita sem teste.

T.T. do corpo (normalização 840 °C + têmpera em água 30-40 °C ou salina + revenimento 540-580 °C) tem de
acontecer **antes** da abertura do canal por fio: é o único jeito de a fenda sair sem trinca e dentro de
±0,010. Indução nas arestas, se for o caminho escolhido, vem **depois** da retífica do land e **antes** do
polimento final do canal.
""")

    escreve(pacote, "03_SEQUENCIA_DE_USINAGEM.md", f"""# Sequência de usinagem sugerida (1045, peça única, Ø{r['D'][0]:.2f} × {r['L']:.2f} mm)

| # | operação | até onde | controle |
|---:|---|---|---|
| 1 | serrar barra forjada Ø{r['D'][0] + 6:.0f} mm com folga de 3 mm de topo | — | ver fibra no eixo |
| 2 | desbocar os três estágios, facear as duas pontas | ±0,3 | comprimento {r['L']:.2f} +0,5 |
| 3 | **alívio de tensões** (600 °C, 2 h, ar) | — | obrigatório em 1045 usinado bruto |
| 4 | tornear o envelope a Ø{r['D'][0]:.2f}/Ø{r['D'][1]:.2f}/Ø{r['D'][2]:.2f} com degraus em Z {Z12:.2f} e {Z23:.2f} | ±0,25 | coaxialidade Ø 0,02 no datum A |
| 5 | abrir a boca de entrada e o funil (broca + fresamento/EDM de penetração) | folga 0,5 no contrato | **não alargar Ø75,60** |
| 6 | normalizar + temperar + revenido o corpo | 30-36 HRC | dureza na face traseira |
| 7 | retificar as duas faces planas e o 1º estágio | ±0,01 | planeza 0,01, ⊥ 0,01 em A |
| 8 | **fio EDM** do canal (funil + fenda 75,00 × 1,500 + R 0,75) | +0,010/−0,000 | arame entra pela boca de entrada; sem furo de partida no produto |
| 9 | remover a camada REC do EDM (≥ 0,02 mm) e polir o canal | Ra ≤ 0,4 | polimento na direção da extrusão |
| 10 | indução nas arestas do land (ou nitretação a plasma) | 0,6-1,0 mm / 8-18 µm | **re-medir a abertura da fenda** |
| 11 | retoque a fio, se a abertura tiver fechado; re-polimento local | 1,500 +0,010 | leitura final antes de embalar |
| 12 | chanfro de saída na boca | 1,50 × 45° ±0,20 / ±0,5° | esquadro + perfil óptico |
| 13 | marcar a laser na face traseira | fora do furo | `JONATHA v27.0 · EX-031 · 1045 · {r['rotulo'].split('·')[-1].strip()} · lote · nº série` |

Rejeições automáticas: furo de fixação, flange, pino, peça partida em duas metades, abertura fora de
1,500 +0,010/−0,000, land com ângulo (tem de ser paralelo em {n(med['canal']['land'],2)} mm), Ø maior que o
medido acima +0,5 em qualquer estágio (a matriz não entra no furo do cabeçote).
""")

    escreve(pacote, "04_TOLERANCIAS_E_INSPECAO.md", f"""# Tolerâncias e inspeção — {r['rotulo']}

Política registrada do dono (2026-09-22): **"tolerância de 0,5 para todas as cotas alteradas aqui"**. Cotas
alteradas nesta revisão: Ø{r['D'][0]:.2f}, Ø{r['D'][1]:.2f}, Ø{r['D'][2]:.2f}{"" if r['L'] == 109.00 else " e comprimento %.2f" % r['L']}.
Nada mais foi tocado: as cotas do produto (fenda, land, chanfro, boca de entrada, rugosidade) continuam com as
tolerâncias apertadas de antes, porque são elas que definem a manta de 1,50 mm.

{fmt_tabela(cotas)}

## Plano de inspeção (o que vem junto com a peça)

| momento | o que medir | instrumento | aceitação |
|---|---|---|---|
| bruto, após T.T. | envelope, comprimento, planitude | micrômetro + granito/comparador | dentro de ±0,5 das cotas alteradas |
| após o fio EDM | largura e abertura da fenda nos 3 pontos (entrada, meio, saída) | calibre de lâminas 1,500 + CMM | abertura 1,500 +0,010/−0,000; área da seção 112,0171 mm² ±0,5 % |
| após o tratamento | abertura da fenda (novamente) | idem | a cota não mudou; se mudou, retrabalho na operação 11 |
| antes de embalar | visual 10× na boca da fenda, rebarba, Ra por réplica | perfil óptico/rugosímetro | rebarba ≤ 0,1 × 45°, Ra ≤ 0,4 no canal e ≤ 0,8 nos furos |
| dossiê | certificado 3.1, relatório dimensional com os números medidos, registro do T.T./indução | — | sem dossiê a peça não é paga |

## Como a peça é montada (para a fábrica não "ajudar")

Encosto **face a face** no rebaixo do cabeçote, fixação por collete EX-031 e pelo degrau. Folga radial medida:
{", ".join("%.2f mm" % f["folga_radial"] for f in mo["folgas_por_estagio"] if f.get("folga_radial") is not None)} nos três
estágios. A matriz **não** pode roçar na fenda do nariz: interseção medida {n(mo['interferencia_mm3'],4)} mm³, e é isso que
tem de sair na conferência da fábrica com o cabeçote deles.
""")

    escreve(pacote, "05_O_QUE_O_STEP_NAO_DIZ.md", f"""# O que o STEP não diz (e precisa estar na ordem de serviço)

* **Datum.** O datum A é o cilindro do 1º estágio (Ø{r['D'][0]:.2f}, Z 0,00 → {Z12:.2f}), não a face de entrada; a face de
  entrada é a de encosto e é ela que abre junta com o cabeçote — planeza 0,01 e ⊥ 0,01 em A.
* **Sentido do polimento.** No land, polir na direção da extrusão (Z crescente). Polimento transversal marca a
  manta.
* **Camada REC do EDM.** Remover ≥ 0,02 mm depois do fio; em 1045 revenido, REC sem remoção é onde nasce trinca.
* **Tratamento na fenda** foi pedido de propósito: é o que segura o desgaste das arestas do land num aço que não
  é de trabalho a quente. Mas ele **não** pode mover a abertura de 1,500 — ver `02_`, item 1 a 4.
* **Sem furo de partida** na boca de entrada: o arame entra pelo Ø{med['canal']['boca_entrada']:.2f} já aberto; se a fábrica
  precisar de furo de entrada para o fio, fazê-lo **no excedente** da boca de saída e fechar com o chanfro de
  1,50 × 45° — nunca dentro do canal.
* **Marcação**: só na face traseira, fora do envelope de assentamento, e o carimbo para a fábrica é
  **JONATHA v27.0**; "rev. 29/30" é revisão interna do projeto.
* **Embalagem**: a boca de saída é a superfície funcional mais frágil (arestas do land endurecidas, 1,500 mm de
  vão). Proteger com capa de PE e não empilhar; transporte com a face de entrada apoiada em prato, nunca a de
  saída.
* **O que mudou em relação à revisão que estava no disco**: Ø93,00 → Ø{r['D'][0]:.2f}, Ø89,50 → Ø{r['D'][1]:.2f},
  Ø79,50 → Ø{r['D'][2]:.2f}{"" if r['L'] == 109.00 else ", comprimento 109,00 → %.2f (funil encurtado; land e chanfro movidos rigidamente)" % r['L']},
  material 1.2344 50-52 HRC → 1045 com tratamento nas arestas. O canal de fluxo continua o mesmo do master
  aprovado{"" if r['L'] == 109.00 else " (só o trecho do funil foi comprimido axialmente, X e Y intactos)"}.
""")

    escreve(pacote, "06_PEDIDO_DE_COTACAO_RFQ.md", f"""# RFQ — 1 matriz de extrusão em **aço 1045**, fenda 1,50 mm aberta a fio EDM, com indução/nitretação no land

Peça: MATRIZ {r['rotulo']} — 1 sólido, sem flange, sem furo de fixação.
Quantidade: **1 matriz** (sem lote, sem série). Envelope Ø{r['D'][0]:.2f} × {r['L']:.2f} mm, {n(m['massa_kg'],2)} kg.

Escopo:
1. material 1045 forjado, fibra no eixo, certificado EN 10204 3.1;
2. corpo usinado ±0,5 nas cotas novas; faces de assentamento ±0,01;
3. canal (funil + fenda) a fio EDM depois do tratamento térmico, abertura 1,500 +0,010/−0,000;
4. tratamento superficial na fenda/land (indução ou nitretação a plasma), com a abertura re-medida depois;
5. Ra ≤ 0,4 µm no canal, rebarba ≤ 0,1 × 45°, marcação a laser na face traseira;
6. relatório dimensional com os números medidos + dossiê de T.T.

Perguntas que precisam de resposta antes do pedido:
1. a fábrica consegue segurar 1,500 +0,010/−0,000 com fio EDM em 1045 revenido e re-medir depois do tratamento?
2. tratamento térmico é interno ou terceirizado? Quem faz a indução e com que controle de camada?
3. prazo para 1 peça (usinar + T.T. + tratamento + medição) — hoje trabalhamos com 20 dias úteis;
4. NDA antes do desenho: a peça é de um projeto em patenteamento.

É uma peça só, sem lote. Quem fechar esta matriz fica com a geometria; a segunda vem depois da validação.
""")

    escreve(pacote, "README.md", f"""# Pacote de usinagem — MATRIZ {r['rotulo']}

Gerado por `04_Dados_SSOT_e_Scripts/gerar_pacote_usinagem_v30.py` a partir do STEP medido. Se o STEP mudar, o
pacote muda junto; nada aqui foi digitado de memória.

| arquivo | o que é |
|---|---|
| `01_FICHA_DE_FABRICA.md` | o que é a peça, cotas principais medidas, interface com o EX-030 |
| `02_MATERIAL_E_TRATAMENTO.md` | **1045** + indução/nitretação na fenda, com as consequências na cota de 1,500 |
| `03_SEQUENCIA_DE_USINAGEM.md` | 13 operações, do corte da barra à marcação a laser |
| `04_TOLERANCIAS_E_INSPECAO.md` | tabela de cotas (com ±0,5 nas alteradas) e plano de inspeção |
| `05_O_QUE_O_STEP_NAO_DIZ.md` | datum, polimento, REC, embalagem, o que mudou nesta revisão |
| `06_PEDIDO_DE_COTACAO_RFQ.md` | texto pronto para mandar |
| `07_EMAIL_DE_PRIMEIRO_CONTATO.md` | **capa, não vai no zip**: guarda o sha256 do zip |
| `PRANCHA_2D_TOLERANCIADA.pdf` / `.png` | 4 vistas cotadas, geradas das seções medidas no STEP |
| `3D/` | `{r['step']}` (a peça), `{r['canal']}` (o sólido do canal, para o EDM), `{r['montagem']}` (no cabeçote) |
| `pacote_usinagem.json` | os números medidos, máquina-legível |
| `CHECKSUMS_SHA256.txt` | sha256 de tudo que vai no zip |
| `{r['zip']}` | o pacote fechado para envio |

Conferir: `cd {r['pasta']} && sha256sum -c CHECKSUMS_SHA256.txt`
""")
    json.dump(dict(matriz="JONATHA " + r["rotulo"], gerado_por="04_Dados_SSOT_e_Scripts/gerar_pacote_usinagem_v30.py",
                   medido=m, alvo_do_contrato=G.ALVO, aco=G.ACO, material_observacao=OBS_MATERIAL,
                   decisoes_2026_09_22=dict(diametros_mm=r["D"], tolerancia_das_cotas_alteradas="±0,5",
                                            comprimento_mm=r["L"], material="aço 1045",
                                            tratamento="indução ou nitretação a plasma na região da fenda"),
                   cotas=[dict(item=c[0], nominal=c[1], tolerancia=c[2], medicao=c[3], motivo=c[4]) for c in cotas],
                   medido_na_revisao=med, montagem=mo, arquivos=movidos),
              open(os.path.join(pacote, "pacote_usinagem.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rev", default="v29,v30", help="v29, v30 ou os dois (padrao: v29,v30)")
    ap.add_argument("--semdos", action="store_true", help="nao gera a prancha PDF")
    ap.add_argument("--somente-zip", action="store_true",
                    help="so refaz CHECKSUMS -> zip -> capa (documentos e prancha ja estao na pasta)")
    a = ap.parse_args()
    rv = json.load(open(REV_JSON, encoding="utf-8"))
    for tag in [x.strip() for x in a.rev.split(",") if x.strip()]:
        r = REV[tag]
        pacote = os.path.join(RAIZ, r["pasta"])
        oficial = os.path.join(RAIZ, "07_CAD_Matrizes", r["oficial"])
        os.makedirs(os.path.join(pacote, "3D"), exist_ok=True)
        print("=== %s -> %s" % (tag, r["pasta"]))
        movidos = {}
        for chave, nome, orig in (("peca_unica", r["step"], os.path.join(oficial, r["step"])),
                                  ("canal", r["canal"], os.path.join(oficial, r["canal"])),
                                  ("montagem", r["montagem"], os.path.join(RAIZ, "06_CAD_Cabecote_EX-030",
                                                                            "STEP", r["montagem"]))):
            if not os.path.exists(orig):
                raise SystemExit("FALHOU: falta %s" % orig)
            dest = os.path.join(pacote, "3D", nome)
            if (not os.path.exists(dest)) or G.sha256(dest) != G.sha256(orig):
                shutil.copyfile(orig, dest)
            movidos[chave] = dict(origem=os.path.relpath(orig, RAIZ), destino=os.path.join("3D", nome),
                                  bytes=os.path.getsize(orig), sha256=G.sha256(orig))
            print("    %-10s %9d bytes  sha256 %s..." % (chave, os.path.getsize(orig), G.sha256(orig)[:16]))
        # aponta o modulo do pacote anterior para esta revisao e usa o medidor e o prancha dele
        G.P_Pacote = pacote
        G.DESTINO = {"peca_unica": r["step"], "canal": r["canal"],
                       "montagem": r["montagem"]}   # senao o medidor do v29 procura o STEP errado
        G.ALVO = dict(largura_fenda=75.00, abertura_fenda=1.50, raio_borda=0.75, land=8.50, chanfro=1.50,
                      boca_saida=(78.00, 4.50), boca_entrada=75.60,
                      estagios=[(r["D"][0], 0.00, Z12), (r["D"][1], Z12, Z23), (r["D"][2], Z23, r["L"])],
                      comprimento=r["L"])
        G.ACO = ACO_1045
        G.TOL_D1 = G.TOL_D = "\u00b10,5"                   # os tres 94/89/79 foram alterados: ±0,5
        # o comprimento so leva ±0,5 onde ele foi alterado: na v29 o 109,00 e a cota de antes
        G.TOL_L = "0/\u22120,05" if r["L"] == 109.00 else "\u00b10,5"
        G.NOTAS_TITULO = ("E \u00b7 NOTAS GERAIS \u2014 MATRIZ JONATHA v27.0, pe\u00e7a \u00fanica, rev. %s (2026-09-22)"
                           % tag)
        G.NOTA_REVEST = ("7 \u00b7 Canal e land polidos Ra \u2264 0,4 \u00b5m na dire\u00e7\u00e3o da extrus\u00e3o. O tratamento "
                         "superficial na fenda foi PEDIDO: medir a abertura de 1,500 antes e depois dele; se mover, "
                         "o retrabalho \u00e9 passar o fio de novo")
        G.DUREZA_CURTA = "corpo 30-36 HRC; arestas do land 55-60 HRC (indu\u00e7\u00e3o) ou 600-700 HV0,2 (nitreta\u00e7\u00e3o)"
        G.MARCACAO_CURTA = "JONATHA v27.0 \u00b7 EX-031 \u00b7 1045 \u00b7 rev. %s \u00b7 lote \u00b7 n\u00ba de s\u00e9rie" % tag
        G.NOTA_COMPRIMENTO = ("12 \u00b7 Comprimento %s mm medido no STEP: %s"
                              % (n_str(r["L"]), r["protrusao"]))
        G.TITULO_FIGURA = ("MATRIZ %s · PEÇA ÚNICA · 1045 + indução/nitretação no land · Ø%.2f × %.2f mm · "
                           "1 matriz · ±0,5 nas cotas alteradas em 2026-09-22" % (r["rotulo"], r["D"][0], r["L"]))
        G.RODAPE_FIGURA = ("interface com o cabeçote EX-030: folgas radiais medidas nos três estágios · "
                           "montagem com interseção %.4f mm³ · face de saída %s · "
                           "detalhes em 04_TOLERANCIAS_E_INSPECAO.md"
                           % (rv[tag]["montagem"]["interferencia_mm3"], r["protrusao"].split("(")[0].strip()))
        if a.somente_zip:
            print("    [somente-zip] pulando medicao, documentos e prancha")
            finaliza(r, pacote)
            continue
        m, sh, inv, void = G.mede_tudo()
        print("    medido: %d sólidos / %d faces | aço %.1f mm³ = %.3f kg | canal %.1f mm³ | fenda %s × %s"
              % (m["solidos"], m["faces"], m["volume_aco_mm3"], m["massa_kg"], m["volume_canal_mm3"],
                 n(m["fenda_no_land"]["largura_mm"], 4), n(m["fenda_no_land"]["abertura_mm"], 3)))
        if abs(m["volume_aco_mm3"] - rv[tag]["medidas"]["volume_aco_mm3"]) > 0.5:
            raise SystemExit("FALHOU: o volume de aço do pacote (%.1f) diverge do medido na revisão (%.1f)"
                             % (m["volume_aco_mm3"], rv[tag]["medidas"]["volume_aco_mm3"]))
        cotas = tabela(r, m)
        docs(r, m, cotas, movidos, pacote, rv)
        print("    6 documentos + README + JSON em %s/" % r["pasta"])
        if not a.semdos:
            G.prancha(m, sh, void, cotas, os.path.join(pacote, "PRANCHA_2D_TOLERANCIADA.pdf"))
            print("    prancha PDF ok")
        finaliza(r, pacote)
        print("    CHECKSUMS (%d arquivos) -> zip -> sha do zip na capa" % r["_k"])


def finaliza(r, pacote):
    """Ordem obrigatoria: conteudo -> CHECKSUMS -> zip -> sha do zip NA CAPA, fora do zip.

    A capa e o proprio zip nunca podem entrar na lista de checksums: foi o zip ler a si mesmo (o
    arquivo de saida ja estava na pasta, da revisao anterior) que encheu o disco com 19 GB antes de o
    write estourar. Ai esta a exclusao, explicita.
    """
    capa = os.path.join(pacote, "07_EMAIL_DE_PRIMEIRO_CONTATO.md")
    if os.path.exists(capa):
        os.remove(capa)
    z = os.path.join(pacote, r["zip"])
    if os.path.exists(z):
        os.remove(z)
    k = G.checksums()
    nomes = [l.split("  ", 1)[1] for l in
             open(os.path.join(pacote, "CHECKSUMS_SHA256.txt"), encoding="utf-8").read().split("\n") if l]
    nomes = [x for x in nomes if os.path.basename(x) not in (r["zip"], "07_EMAIL_DE_PRIMEIRO_CONTATO.md",
                                                              "CHECKSUMS_SHA256.txt")]
    io.open(os.path.join(pacote, "CHECKSUMS_SHA256.txt"), "w", encoding="utf-8").write(
        "\n".join('%s  %s' % (G.sha256(os.path.join(pacote, x)), x) for x in sorted(nomes)) + "\n")
    dentro = sorted(nomes + ["CHECKSUMS_SHA256.txt"])   # o CHECKSUMS vai DENTRO do zip; o zip nao se lista
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for nome in dentro:
            zf.write(os.path.join(pacote, nome), nome)
            assert not os.path.abspath(nome).startswith(os.path.abspath(z)), "zip dentro do zip"
    shazip = G.sha256(z)
    r["_k"] = len(dentro)
    escreve(pacote, "07_EMAIL_DE_PRIMEIRO_CONTATO.md", """# E-mail de primeiro contato — capa do pacote (não vai no zip)

    **Assunto:** Cotação — 1 matriz de extrusão em aço 1045 · fenda 1,50 mm aberta a fio EDM · indução no land

    Boa tarde,

    Preciso de **uma** matriz de extrusão (peça única, sem lote) para um cabeçote EX-030. O pacote está no anexo:
    STEP da peça, sólido do canal (para o fio EDM), desenho cotado e toleranciado, ficha de fábrica, sequência de
    usinagem e plano de inspeção.

    Resumo do que é: Ø%(D0).2f × %(L).2f mm em **aço 1045**, sem flange e sem furo de fixação (segura por collete
    EX-031 e degrau), fenda de 75,00 × **1,500 +0,010/−0,000** com R 0,75 nas pontas, land paralelo de 8,50 mm e
    chanfro de saída 1,50 × 45°. Tolerância ±0,5 nas cotas de envelope que nós alteramos nesta revisão; as cotas do
    produto continuam apertadas.

    Quatro respostas antes de eu formalizar o pedido:

    1. Vocês seguram 1,500 +0,010/−0,000 com fio EDM em 1045 revenido, em land de 8,50 mm?
    2. Tratamento térmico e indução são internos ou terceirizados? E dá para re-medir a abertura da fenda depois do
       tratamento e gravar o número no relatório?
    3. Prazo para 1 matriz com dossiê (EN 10204 3.1 + relatório dimensional) — penso em 20 dias úteis, está correto?
    4. Aceitam NDA? A peça pertence a um projeto em patenteamento.

    É uma peça só, sem lote. Quem fechar esta matriz fica com a geometria; a segunda vem depois da validação no
    equipamento.

    Anexo: `%(zip)s` — **sha256 do anexo: `%(sha)s`** (%(byt)d bytes). Se o hash não bater, não abram: peça reenvio.

    ---
    %(obs)s
    """ % dict(D0=r["D"][0], L=r["L"], zip=r["zip"], sha=shazip, byt=os.path.getsize(z),
               obs=("O que NÃO mandar ainda: o modelo paramétrico, as planilhas de simulação e os relatórios "
                    "internos de auditoria — nada disso é necessário para orçar ou usinar esta peça.")))
    print("    zip %s  %d bytes  sha256 %s" % (r["zip"], os.path.getsize(z), shazip[:24]))
    return shazip


if __name__ == "__main__":
    main()
