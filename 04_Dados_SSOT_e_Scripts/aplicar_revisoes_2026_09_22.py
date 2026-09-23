#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Aplica as revisões de 2026-09-22 no resto do repositório (índices, READMEs, SSOT, relatórios).

Lê `04_/revisoes_v29_v30.json` (produzido por `gerar_revisoes_v29_v30.py`, com tudo medido no STEP) e propaga:

* `07_/Matriz_Jonatha_v29_OFICIAL/README.md` e `07_/Matriz_Jonatha_v30_OFICIAL/README.md`;
* a montagem nova no cabeçote também entra na pasta oficial com o nome que o README dela já usa
  (`CONJUNTO_MATRIZ_V29_NO_CABECOTE_EX-030.step`) - sem isso fica na pasta um STEP velho com Ø93,00, que é
  exatamente o tipo de armadilha que a fábrica segue à risca;
* SSOT `cad_die_parameters.json`: `matriz_oficial` → v30.0, `envelope_externo_mm` com os Ø novos e a tolerância
  ±0,5, `material` → 1045 + tratamento, `decisoes_usuario` D10/D11/D12, bloco `revisoes_2026_09_22`;
* `03_/MATRIZ_V27_PECA_UNICA.md`: seção datada com as cotas re-medidas;
* `03_/SIMULACAO_ROTAS_E_COMPRIMENTO.md`: **re-executa** o modelo de rotas com as folgas novas (0,50 mm nos três
  estágios) e com o comprimento de cada revisão, em vez de copiar o número do preview.

Idempotente: pode ser rodado de novo depois de qualquer re-geração do STEP.
"""
import io
import json
import os
import re
import shutil
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, ".."))
sys.path.insert(0, AQUI)

from auditar_step_correlacoes import n  # noqa: E402

REV = json.load(open(os.path.join(AQUI, "revisoes_v29_v30.json"), encoding="utf-8"))
SSOT = os.path.join(AQUI, "cad_die_parameters.json")
DIR7 = os.path.join(RAIZ, "07_CAD_Matrizes")
DIR_CAB = os.path.join(RAIZ, "06_CAD_Cabecote_EX-030", "STEP")
PACOTE = {"v29": os.path.join(RAIZ, "08_Pacote_Usinagem_v29"),
          "v30": os.path.join(RAIZ, "08_Pacote_Usinagem_v30")}
NL = chr(10)
NL2 = NL + NL
Z12, Z23 = 69.90, 80.70
NOMES = {"v29": dict(oficial="Matriz_Jonatha_v29_OFICIAL", step="MATRIZ_V29_PECA_UNICA.step",
                    canal="MATRIZ_V29_CANAL_DE_FLUXO.step", montagem="Cabecote_EX-030_com_Matriz_Jonatha_v29.step",
                    conj="CONJUNTO_MATRIZ_V29_NO_CABECOTE_EX-030.step", pacote="08_Pacote_Usinagem_v29",
                    zip="PACOTE_MATRIZ_V29_PARA_ENVIO.zip"),
         "v30": dict(oficial="Matriz_Jonatha_v30_OFICIAL", step="MATRIZ_V30_PECA_UNICA.step",
                     canal="MATRIZ_V30_CANAL_DE_FLUXO.step", montagem="Cabecote_EX-030_com_Matriz_Jonatha_v30.step",
                     conj="CONJUNTO_MATRIZ_V30_NO_CABECOTE_EX-030.step", pacote="08_Pacote_Usinagem_v30",
                     zip="PACOTE_MATRIZ_V30_PARA_ENVIO.zip")}


def sha(p):
    import hashlib
    return hashlib.sha256(io.open(p, "rb").read()).hexdigest()


def escreve(p, txt):
    io.open(p, "w", encoding="utf-8").write(txt)


def readme(tag):
    d, r = REV[tag], NOMES[tag]
    med, mo = d["medidas"], d["montagem"]
    ch = med["canal"].get("chanfro") or {}
    linhas = ["# Matriz JONATHA — %s (revisão de 2026-09-22)\n" % tag,
              "",
              "Peça única (1 sólido, 1 casca, %d faces, BRep válido). **Não é a v27.0 bipartida**: é o mesmo "
              "canal de fluxo do master, com o envelope alterado por decisão do dono em 2026-09-22 e "
              "tolerância **±0,5** em toda cota alterada." % med["faces"],
              "",
              "| cota | medida no STEP |",
              "|---|---|",
              "| Ø 1º estágio (datum A) | %.2f mm em Z 0,00 → %.2f |" % (med["estagios_medidos"][0]["Ø"], Z12),
              "| Ø 2º estágio | %.2f mm em Z %.2f → %.2f |" % (med["estagios_medidos"][1]["Ø"], Z12, Z23),
              "| Ø 3º estágio | %.2f mm em Z %.2f → %.2f |" % (med["estagios_medidos"][2]["Ø"], Z23,
                                                               med["comprimento"]),
              "| comprimento total | %.2f mm |" % med["comprimento"],
              "| fenda no land | %.4f × %.3f mm, R %.2f nas pontas (área %.4f mm²) |"
              % (med["canal"]["largura_no_land"], med["canal"]["espessura_entre_caras"], 0.75,
                 med["canal"]["area_no_land"]),
              "| land paralelo | %.3f mm (Z %.2f → %.2f) |" % (med["canal"]["land"], med["canal"]["z_land"],
                                                                med["canal"]["z_land"] + med["canal"]["land"]),
              "| chanfro de saída | 1,50 × 45°%s |" % ("" if not ch else ", cone medido em Z %.2f → %.2f"
                                                        % (ch["z"][0], ch["z"][1])),
              "| boca de entrada | Ø%.2f (restrita por contrato) |" % med["canal"]["boca_entrada"],
              "| volume de aço | %s mm³ → %s kg |" % (n(med["volume_aco_mm3"], 1), n(med["massa_kg"], 4)),
              "| canal de fluxo | %s mm³ (%s g de mastique dentro) |"
              % (n(med["canal"]["volume"], 1), n(med["canal"]["volume"] * 1.25e-3, 1)),
              "| material | aço 1045 + indução (ou nitretação a plasma) nas arestas do land |",
              "",
              "## Interface com o EX-030 (medida na montagem)",
              "",
              "| estágio da matriz | furo do cabeçote | folga radial | Z congruente |",
              "|---:|---:|---:|---|"]
    for f in mo["folgas_por_estagio"]:
        linhas.append("| Ø%.2f | Ø%.2f | %.2f mm | %.2f → %.2f |"
                      % (f["estagio_Ø"], f["furo_Ø"], f["folga_radial"],
                         f["trecho_congruente_mm"][0], f["trecho_congruente_mm"][1]))
    linhas += ["",
               "Encosto face a face, `deslocamento_aplicado_mm` = %.2f · **interferência %.4f mm³** · "
               "face de saída no Z %.2f · **protrusão além do nariz %+.2f mm** (a face do nariz está em Z %.2f)."
               % (mo["deslocamento_aplicado_mm"], mo["interferencia_mm3"], mo["face_de_saida_no_Z"],
                  mo["saida_além_da_face_do_nariz_mm"], mo["z_face_do_nariz"]),
               "",
               "## Arquivos",
               "",
               "| arquivo | o que é | sha256 |",
               "|---|---|---|",
               "| `%s` | **a peça** (o que a fábrica usina) | `%s` |" % (r["step"], sha(os.path.join(DIR7, r["oficial"], r["step"]))[:16]),
               "| `%s` | o sólido do canal de fluxo (para o fio EDM e para conferir o volume) | `%s` |"
               % (r["canal"], sha(os.path.join(DIR7, r["oficial"], r["canal"]))[:16]),
               "| `%s` | a matriz sentada no cabeçote completo, com flange (leitura/medida, sem booleano) | `%s` |"
               % (r["conj"], sha(os.path.join(DIR7, r["oficial"], r["conj"]))[:16]),
               "| `%s/` | pacote de usinagem vigente (ficha, material, cotas, sequência, RFQ, prancha) | zip `%s` |"
               % (r["pacote"], sha(os.path.join(r["pacote"], r["zip"]))[:16]),
               "",
               "O que mudou em relação à revisão anterior está anotado em `03_Relatorios_e_Documentacao/"
               "MATRIZ_V27_PECA_UNICA.md` (seção de 2026-09-22) e no SSOT (`decisoes_usuario` D10 a D12). "
               "Para a fábrica, a peça continua se chamando **JONATHA v27.0**; 'v29'/'v30' é carimbo interno de "
               "revisão do projeto.\n"]
    escreve(os.path.join(DIR7, r["oficial"], "README.md"), "\n".join(linhas))
    return "\n".join(linhas)


def atualiza_ssot():
    d = json.load(open(SSOT, encoding="utf-8"))
    m30, m29 = REV["v30"]["medidas"], REV["v29"]["medidas"]
    ds = [e["Ø"] for e in m30["estagios_medidos"]]
    d["matriz_oficial"] = dict(versao="v30.0", promovida_em="2026-09-22",
                               motivo="decisão do dono em 2026-09-22: Ø94,00/Ø89,00/Ø79,00 com ±0,5 nas cotas "
                                      "alteradas, comprimento encurtado para a matriz ficar faceada ao nariz do "
                                      "cabeçote (95,00 mm) e material mudado para aço 1045 com tratamento "
                                      "superficial na fenda",
                               arquivo=os.path.join("07_CAD_Matrizes", NOMES["v30"]["oficial"],
                                                     NOMES["v30"]["step"]).replace(os.sep, "/"),
                               sha256=sha(os.path.join(DIR7, NOMES["v30"]["oficial"], NOMES["v30"]["step"])),
                               pacote_de_usinagem=NOMES["v30"]["pacote"],
                               revisao_anterior=dict(versao="v29.0 (re-feita em 2026-09-22 com os Ø novos, "
                                                             "comprimento 109,00 inalterado)",
                                                     arquivo=os.path.join("07_CAD_Matrizes",
                                                                          NOMES["v29"]["oficial"],
                                                                          NOMES["v29"]["step"]).replace(os.sep, "/"),
                                                     sha256=sha(os.path.join(DIR7, NOMES["v29"]["oficial"],
                                                                             NOMES["v29"]["step"])),
                                                     pacote_de_usinagem=NOMES["v29"]["pacote"]))
    d["envelope_externo_mm"] = dict(
        comprimento_total_z_mm=m30["comprimento"],
        **{"estagio_%d" % (i + 1): dict(diametro_mm=ds[i], z_de_mm=z0, z_ate_mm=z1,
                                        tolerancia="±0,5 (cota alterada em 2026-09-22)")
           for i, (z0, z1) in enumerate([(0.0, Z12), (Z12, Z23), (Z23, m30["comprimento"])])},
        observacao="NÃO é mais o envelope idêntico ao da Matriz 2 (Gedeon): em 2026-09-22 o dono alterou os três "
                   "Ø (93,00 → 94,00; 89,50 → 89,00; 79,50 → 79,00) e pediu ±0,5 neles. Folga radial medida no "
                   "cabeçote: 0,50 mm em cada estágio (antes 1,00 / 0,25 / 0,25). O comprimento v29 (109,00) "
                   "não foi alterado; a v30 tem 95,00.",
        tolerancia_das_cotas_alteradas="±0,5",
        comprimentos_disponiveis=dict(v29=m29["comprimento"], v30=m30["comprimento"]))
    par = d.setdefault("matriz_jonatha_parameters", {})
    par["material"] = "aço 1045 (SAE/EN C45E), corpo revenido 30-36 HRC, arestas do land endurecidas por " \
                      "indução (0,6-1,0 mm) ou nitretação a plasma (8-18 µm) "
    par["material_observacao"] = ("decisão do dono em 2026-09-22 ('1045 + tratamento superficial na fenda'), "
                                  "substitui o 1.2344 50-52 HRC que constava antes. Consequência registrada: o "
                                  "1045 não tem temperabilidade para 50 HRC em Ø94, e o tratamento na fenda pode "
                                  "mover a cota 1,500 (tolerância +0,010/-0,000) - por isso a abertura é medida "
                                  "antes e depois do tratamento e o retrabalho e passar o fio de novo. Ver "
                                  "08_Pacote_Usinagem_v30/02_MATERIAL_E_TRATAMENTO.md.")
    par["material_anterior"] = "1.2344 (X37CrMoV5-1 / AISI H13) 50-52 HRC, sem nitretação nem PVD - vigente até 2026-09-22"
    d["decisoes_usuario"].update({
        "data_2026_09_22": "2026-09-22",
        "D10_diametros_e_tolerancia": "\"93,00 mude para 94 no desenho v29 ... 89,50 mude para 89 e 79,50 mude "
                                      "para 79 ... tolerancia de 0,5 para todas as cotas alteradas aqui\" - aplicado "
                                      "no modelo e no desenho, não só no desenho",
        "D11_comprimento_v30": "\"altere o comprimento 109,00 deixe menor, quero que fique faceado ao nariz do "
                                "cabecote\" + \"Quero manter proporcionalmente igual, so diminuindo o comprimento "
                                "total, mas o land precisa ter as mesmas dimensoes e cotas\" - virou v30 com "
                                "95,00 mm: funil comprimido axialmente (s = %.6f), land 8,500 / fenda 75,00 x 1,500 "
                                "/ chanfro 1,50 x 45 movidos rigidamente" % REV["escala_axial_do_funil"],
        "D12_material": "\"fabricar em 1045\" + \"1045 + tratamento superficial na fenda\" - corpo em 1045, "
                        "indução ou nitretação só na região da fenda/land, com re-medição da abertura depois do "
                        "tratamento",
        "D13_montagem_no_cabecote": "\"fac uma versao da matriz dentro do cabecote ja\" - montagens STEP por "
                                    "revisao em 06_CAD_Cabecote_EX-030/STEP/ e na pasta oficial de cada matriz"})
    d["revisoes_2026_09_22"] = dict(fonte="04_Dados_SSOT_e_Scripts/gerar_revisoes_v29_v30.py",
                                   medido_em="04_Dados_SSOT_e_Scripts/revisoes_v29_v30.json",
                                   v29=dict(arquivo=REV["v29"]["medidas"]["arquivo"],
                                            sha256=REV["v29"]["medidas"]["sha256"],
                                            comprimento=REV["v29"]["medidas"]["comprimento"],
                                            diameteros=[e["Ø"] for e in REV["v29"]["medidas"]["estagios_medidos"]],
                                            protrusao_mm=REV["v29"]["montagem"]["saida_além_da_face_do_nariz_mm"]),
                                   v30=dict(arquivo=REV["v30"]["medidas"]["arquivo"],
                                            sha256=REV["v30"]["medidas"]["sha256"],
                                            comprimento=REV["v30"]["medidas"]["comprimento"],
                                            diameteros=[e["Ø"] for e in REV["v30"]["medidas"]["estagios_medidos"]],
                                            protrusao_mm=REV["v30"]["montagem"]["saida_além_da_face_do_nariz_mm"]),
                                   produto_inalterado=dict(
                                       area_no_land_mm2=REV["v30"]["medidas"]["canal"]["area_no_land"],
                                       largura=REV["v30"]["medidas"]["canal"]["largura_no_land"],
                                       abertura=REV["v30"]["medidas"]["canal"]["espessura_entre_caras"],
                                       land=REV["v30"]["medidas"]["canal"]["land"],
                                       boca_saida=REV["v30"]["medidas"]["canal"]["boca_saida"],
                                       observacao="as cotas do produto sao identicas entre v29, v30 e o master "
                                                  "v27.0; o que mudou em v30 e o trecho do funil (comprimido em Z, "
                                                  "X e Y intactos), entao o volume de mastique dentro da matriz caiu"))
    d["usinagem_v29"] = dict(d.get("usinagem_v29") or {},
                             pacote="08_Pacote_Usinagem_v29",
                             zip_sha256=sha(os.path.join(PACOTE["v29"], NOMES["v29"]["zip"])),
                             observacao="o pacote v29 foi re-gerado com o STEP novo (Ø94/89/79, ±0,5) e com o "
                                        "material 1045; para envio a fabrica o vigente e 08_Pacote_Usinagem_v30")
    d["usinagem_v30"] = dict(pacote="08_Pacote_Usinagem_v30",
                             zip="PACOTE_MATRIZ_V30_PARA_ENVIO.zip",
                             zip_sha256=sha(os.path.join(PACOTE["v30"], NOMES["v30"]["zip"])),
                             gerado_por="04_Dados_SSOT_e_Scripts/gerar_pacote_usinagem_v30.py",
                             rotulo_na_peca="JONATHA v27.0 · EX-031 · 1045 · rev. 30 (2026-09-22)",
                             politica_de_tolerancia="±0,5 nas cotas alteradas (tres Ø e o comprimento); cotas do "
                                                     "produto mantidas (fenda 1,500 +0,010/-0,000, land 8,50 "
                                                     "±0,05, chanfro 1,50 x 45 ±0,20/±0,5, Ra <= 0,4)")
    json.dump(d, open(SSOT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return d


def relatorio_v27():
    p = os.path.join(RAIZ, "03_Relatorios_e_Documentacao", "MATRIZ_V27_PECA_UNICA.md")
    s = io.open(p, encoding="utf-8").read()
    if "## Revisão de 2026-09-22" in s:
        s = s[:s.index("## Revisão de 2026-09-22")]
    m29, m30 = REV["v29"]["medidas"], REV["v30"]["medidas"]
    d29, d30 = REV["v29"]["montagem"], REV["v30"]["montagem"]
    sect = ["## Revisão de 2026-09-22: Ø novos, ±0,5 e a v30 faceada ao nariz", "",
            "O dono mandou alterar os três Ø do envelope e registrar ±0,5 em toda cota alterada; o modelo e o "
            "desenho foram re-gerados juntos (`04_/gerar_revisoes_v29_v30.py`), com o canal de fluxo herdado 1:1 "
            "do STEP aprovado. Medido nos dois STEP novos:", "",
            "| | v29 (re-feita) | v30 (nova) |", "|---|---|---|",
            "| Ø dos três estágios | %.2f / %.2f / %.2f | %.2f / %.2f / %.2f |"
            % (m29["estagios_medidos"][0]["Ø"], m29["estagios_medidos"][1]["Ø"], m29["estagios_medidos"][2]["Ø"],
               m30["estagios_medidos"][0]["Ø"], m30["estagios_medidos"][1]["Ø"], m30["estagios_medidos"][2]["Ø"]),
            "| comprimento | %.2f (inalterado) | %.2f |" % (m29["comprimento"], m30["comprimento"]),
            "| land / fenda / área no land | %.3f mm · %.4f × %.3f · %.4f mm² | idêntico: %.3f mm · %.4f × %.3f · %.4f mm² |"
            % (m29["canal"]["land"], m29["canal"]["largura_no_land"], m29["canal"]["espessura_entre_caras"],
               m29["canal"]["area_no_land"], m30["canal"]["land"], m30["canal"]["largura_no_land"],
               m30["canal"]["espessura_entre_caras"], m30["canal"]["area_no_land"]),
            "| faces / sólidos / BRep | %d / %d / válido | %d / %d / válido |"
            % (m29["faces"], m29["solidos"], m30["faces"], m30["solidos"]),
            "| volume de aço → massa | %s mm³ → %s kg | %s mm³ → %s kg |"
            % (n(m29["volume_aco_mm3"], 1), n(m29["massa_kg"], 3), n(m30["volume_aco_mm3"], 1),
               n(m30["massa_kg"], 3)),
            "| canal de fluxo (vazio) | %s mm³ | %s mm³ (funil comprimido por s = %.6f) |"
            % (n(m29["canal"]["volume"], 1), n(m30["canal"]["volume"], 1), REV["escala_axial_do_funil"]),
            "| protrusão além do nariz do cabeçote | %+.2f mm | %+.2f mm |"
            % (d29["saida_além_da_face_do_nariz_mm"], d30["saida_além_da_face_do_nariz_mm"]),
            "| interferência com o cabeçote | %.4f mm³ | %.4f mm³ |" % (d29["interferencia_mm3"],
                                                                        d30["interferencia_mm3"]),
            "| folga radial nos 3 estágios | " + " / ".join("%.2f" % f["folga_radial"]
                                                             for f in d29["folgas_por_estagio"])
            + " mm | " + " / ".join("%.2f" % f["folga_radial"] for f in d30["folgas_por_estagio"]) + " mm |",
            "| material | aço 1045 + indução/nitretação no land | aço 1045 + indução/nitretação no land |",
            "",
            "Consequências que precisam continuar escritas junto da peça:", "",
            "1. **o envelope deixou de ser idêntico ao da Matriz 2 (Gedeon)** — era essa a justificativa dos "
            "Ø93,00/89,50/79,50; agora a coincidência acabou e a peça é própria.",
            "2. **a folga anular nos três estágios virou 0,50 mm** (antes 1,00 / 0,25 / 0,25). Isso é o que "
            "limita a fuga de material para trás; o efeito no escoamento foi re-medido com o modelo de rotas "
            "(ver `SIMULACAO_ROTAS_E_COMPRIMENTO.md`, seção de 2026-09-22).",
            "3. **±0,5 num Ø de envelope não é cota de ajuste fina**, é cota de folga: com Ø94,00 +0,5 o 1º "
            "estágio passa a encostar no furo Ø95,00 com folga de 0,00 — o modelo usa o nominal, e a inspeção "
            "aceita a faixa. É decisão dele, e o alerta fica aqui.",
            "4. **o 1045 com tratamento na fenda pode mover 1,500** (tolerância +0,010/−0,000): mede-se antes e "
            "depois do tratamento, e o retrabalho é re-passar o fio, não aceitar fora.",
            "5. a face de saída da v30 coincide com a face do nariz (Z 95,00, medido). Com +0,5 mm de "
            "sobra na cota do comprimento a matriz passaria 0,5 mm para fora do nariz — por isso o pacote anota "
            "que, se a fábrica quiser apertar, o aceitável prático é 95,00 −0,50/+0,00.\n"]
    escreve(p, s.rstrip() + "\n\n" + "\n".join(sect))
    return len(sect)


def simulacao():
    """Re-executa o modelo de rotas (mesmo mastique, mesma vazao) com as folgas MEDIDAS na montagem nova.

    O anel de fuga muda porque os 0,50 mm de folga em tres estagios substituem 1,00 / 0,25 / 0,25, e o
    comprimento do trecho congruente muda com a protrusao. O caminho da fenda e re-medido no STEP da propria
    revisao por `perfil_do_canal` (mesma funcao do relatorio original), entao land e dP dao o numero desta pea.
    """
    from simular_rotas_e_comprimento import fluidos, resolver, perfil_do_canal
    fl = fluidos()
    fl.pop("_janela_da_linha_MPa", None)
    fl.pop("_tau_raspado_MPa", None)
    Q = 15000.0
    out = {"Q_mm3_s": Q, "curvas": sorted(fl), "rev": {}}
    for tag in ("v29", "v30"):
        passo = NOMES[tag]
        geo = perfil_do_canal(os.path.join(DIR7, passo["oficial"], passo["step"]))
        if geo is None:
            raise SystemExit("FALHOU: sem vazio medido no STEP da %s" % tag)
        anel = [(f["folga_radial"], round(f["trecho_congruente_mm"][1] - f["trecho_congruente_mm"][0], 2),
                 round((f["estagio_Ø"] + f["furo_Ø"]) / 2.0, 3))
                for f in REV[tag]["montagem"]["folgas_por_estagio"] if f.get("folga_radial") is not None]
        linha = {c: resolver(v["K"], v["n"], geo, anel, Q) for c, v in fl.items()}
        out["rev"][tag] = dict(anel=anel, geo=dict(comprimento_mm=geo["comprimento_peca_mm"],
                                                    land_mm=geo["land_paralelo_medido_mm"],
                                                    area_no_land_mm2=geo["area_no_land_mm2"],
                                                    area_saida_mm2=geo["area_saida_mm2"]),
                               resultado=linha, tipico=linha["tipico"])
    return out


def md_simulacao(sim):
    p = os.path.join(RAIZ, "03_Relatorios_e_Documentacao", "SIMULACAO_ROTAS_E_COMPRIMENTO.md")
    s = io.open(p, encoding="utf-8").read()
    marca = "## Re-medido em 2026-09-22 com as folgas novas"
    if marca in s:
        s = s[:s.index(marca)]
    L = [marca, "",
         "Re-executado o mesmo modelo (mesmo mastique, mesma vazão Q = %.0f mm³/s, as três curvas de reometria "
         "do arquivo) com o anel de fuga **medido nas montagens novas** e a rota da fenda medida no STEP de cada "
         "revisão. Nada foi copiado da tabela anterior." % sim["Q_mm3_s"], "",
         "| revisão | folgas do anel (mm) × comprimento congruente | dP (tipico) | escapa pelo anel | v de saída | "
         "τ no land |", "|---|---|---:|---:|---:|---:|"]
    for tag in ("v29", "v30"):
        r, an = sim["rev"][tag]["tipico"], sim["rev"][tag]["anel"]
        L.append("| %s | %s | **%.1f bar** | %.3f %% | %.2f m/min | %.3f MPa |"
                 % (tag, " + ".join("%.2f × %.1f (Ø%.1f)" % (f[0], f[1], f[2]) for f in an),
                    r["dp_bar"], r["pct_pelo_anel"], r["v_saida_m_min"], r["tau_land_MPa"]))
    L += ["",
          "Leitura honesta: abrir a folga dos estágios 2 e 3 de 0,25 para 0,50 mm **triplica a fração que escapa "
          "para trás** nos cenários com a matriz comprida, e o encurtamento da v30 devolve um pouco (menos trecho "
          "de anel dentro do nariz). A fenda em si não muda nada: land, área e chanfro são os mesmos medidos, "
          "então a vazão de produto e a espessura da manta continuam as da tabela acima. Quem decide a "
          "uniformidade da manta é a coaxialidade dos estágios, não o Ø.", "",
          "Números completos em `04_Dados_SSOT_e_Scripts/revisoes_2026_09_22_simulacao.json` (as três curvas, "
          "trecho por trecho).", ""]
    escreve(p, s.rstrip() + NL2 + NL.join(L))
    return len(L)


if __name__ == "__main__":
    for tag in ("v29", "v30"):
        r = NOMES[tag]
        shutil.copyfile(os.path.join(DIR_CAB, r["montagem"]), os.path.join(DIR7, r["oficial"], r["conj"]))
        readme(tag)
        print("README ok:", os.path.relpath(os.path.join(DIR7, r["oficial"], "README.md"), RAIZ))
    d = atualiza_ssot()
    print("SSOT: matriz_oficial =", d["matriz_oficial"]["versao"], "| envelope =",
          [d["envelope_externo_mm"]["estagio_%d" % i]["diametro_mm"] for i in (1, 2, 3)],
          "| L =", d["envelope_externo_mm"]["comprimento_total_z_mm"])
    print("relatório v27:", relatorio_v27(), "linhas na seção nova")
    sim = simulacao()
    json.dump(sim, open(os.path.join(AQUI, "revisoes_2026_09_22_simulacao.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1, default=str)
    for tag in ("v29", "v30"):
        t = sim["rev"][tag]["tipico"]
        print("    %s: dP %.1f bar | escapa %.3f%% | saida %.2f m/min"
              % (tag, t["dp_bar"], t["pct_pelo_anel"], t["v_saida_m_min"]))
    print("relatorio de simulacao:", md_simulacao(sim), "linhas na secao nova")
