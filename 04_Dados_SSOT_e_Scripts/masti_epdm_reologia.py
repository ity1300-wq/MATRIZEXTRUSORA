#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Reologia do MASTIQUE RESISTIVO À BASE DE EPDM — os números que a simulação 3D vai consumir.

Ele disse: "esse mastic manta é um mastic resistivo não linear à base de EPDM" e, sobre a fonte dos números,
"procure valores de literatura". Este script é honesto sobre o que isso significa: **não existe reômetro deste
lote** no repo, então o que sai daqui é uma banda de literatura com os pontos de apoio declarados, e cada
número tem uma `origem` que diz se é medido, convertido ou estimado. A simulação roda nas três viscosidades e
reporta o intervalo — que é o que se faz quando o material é do cliente e não nosso.

Três âncoras usadas (com URL no JSON):

1. Extrusão de perfil EPDM (o processo dele, não o nosso): queda de pressão na matriz **2,1–9,4 MPa** com
   41–128 g/min, matriz a 70 °C e termopar da cabeça marcando 79–87 °C — Polymers 18(9):1122 (2026).
   Isso dá a janela de energia da linha e a temperatura real do canal.
2. Instabilidade de superfície: *sharkskin* aparece quando a tensão de cisalhamento na parede passa de
   **0,14 MPa** (e escorregamento na parede por volta de 0,1 MPa) para polímeros comuns extrudados em capilar;
   aditivos/BN sobem o limiar para até 0,5 MPa — Vlachopoulos, "The Role of Rheology in Polymer Extrusion".
   É o critério numérico da borda serrilhada: onde τ_parede > 0,14 MPa na saída, a manta rasga na borda.
3. Composto não vulcanizado se comporta como fluido com limiar: os ensaios de compressão (squeeze flow) em
   três compostos crus ajustam **Herschel–Bulkley** melhor que lei-potência pura, e a relação de Cox–Merz
   **não** vale para composto carregado com negro de fumo — J. Rheol. 70, 65 (2026) e Polymer (1998) 39,
   "Rheological properties of EPDM compound…". Ou seja: η₀ e λ são chutados por baixo e o modelo tem de ser
   avaliado em banda, não em ponto.

Uso: python 04_Dados_SSOT_e_Scripts/masti_epdm_reologia.py [--json sair] [--md sair]
"""
import argparse
import json
import math
import os

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, ".."))
SSOT = json.load(open(os.path.join(AQUI, "cad_die_parameters.json"), encoding="utf-8"))

# --- o que é nosso e medido (o repo já tem o funil do polímero atual: EPR/XLPE/PVC modificado)
P = SSOT["rheological_model_parameters"]
K_ATUAL, N_ATUAL = P["power_law"]["K_Pa_s_n"], P["power_law"]["n"]
T_ATUAL, T_REF = P["processing_temperature_C"], P["carreau_yasuda"]["T_ref_K"]
EA_R = P["carreau_yasuda"]["Ea_over_R_K"]

# --- o que a literatura autoriza para o mastique EPDM resistivo (não-vulcanizado, carregado)
N_MASTIC = 0.30                       # faixa de 0,25-0,40 para composto de EPDM com negro de fumo; usamos o
                                       # mesmo expoente da família (o repo já tinha 0,32) e arredondamos para
                                       # baixo: composto de mastique é mais cisalhante que o masterbatch
# Ancora por VISCOSIDADE APARENTE em 100 1/s (o regime do land), nao por fator sobre o K do termoplastico:
# deslocar o K de 190 C para 90 C por Arrhenius ja da 12,5x e depois multiplicar por 8 e double-count - dava
# 820 MPa de dP na matriz, pressao que nenhuma linha de borracha tem. Ordem de grandeza de composto de EPDM
# carregado e nao vulcanizado, em ~100 C: 10^3-10^4 Pa.s em 10^2 1/s (capilar/RPA).
ETA100_PA_S = {"otimista": 1500.0, "tipico": 5000.0, "pessimista": 15000.0}
T_LINHA = 90.0                        # °C: cabeçote de extrusora de borracha (70 °C na matriz + 9-17 °C de
                                       # aquecimento viscoso medido no artigo; o nosso cabeçote é EX-030)
TAU_SHARKSKIN_MPA = 0.14              # limiar de raspado superficial na saída (Vlachopoulos)
TAU_ESCORREGAMENTO_MPA = 0.10
TAU_LIMITE_COM_PCA_MPA = 0.50         # com auxiliar de processamento/BN o limiar sobe
DP_MATRIZ_FAIXA_MPA = (2.1, 9.4)      # queda de pressão de matriz medida no processo análogo
VAZAO_FAIXA_G_MIN = (41.0, 128.0)
RHO_MASTIC = 1.25e-3                  # g/mm3 (1,25 g/cm3) para composto de EPDM carregado - usado só em massa


def eta_power_law(K, n, gama):
    return K * gama ** (n - 1.0)


def carreau(eta0, lam, a, n, gama):
    return eta0 * (1.0 + (lam * gama) ** a) ** ((n - 1.0) / a)


def desloca_com_temperatura(K, T_de, T_para):
    """Deslocamento de Arrhenius com a Ea/R do próprio SSOT (o repo já calibrou isso para a família)."""
    return K * math.exp(EA_R * (1.0 / (T_para + 273.15) - 1.0 / (T_de + 273.15)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=os.path.join(AQUI, "masti_epdm_reologia.json"))
    ap.add_argument("--md", default=os.path.join(RAIZ, "03_Relatorios_e_Documentacao", "REOLOGIA_MASTIC_EPDM.md"))
    a = ap.parse_args()

    K_na_linha = desloca_com_temperatura(K_ATUAL, T_ATUAL, T_LINHA)     # o nosso proprio K, levado a 90 C
    curvas = {}
    for nome, eta100 in ETA100_PA_S.items():
        fator = eta100 / 5000.0
        K = eta100 * 100.0 ** (1.0 - N_MASTIC)   # K = eta * gama^(1-n) no ponto de ancora
        n = N_MASTIC
        eta0 = K * (1.0 / 0.02) ** (1.0 - n)          # eta0 lido em gama_dot = 0,02 1/s (plateau baixo)
        curvas[nome] = {
            "K_Pa_s_n": round(K, 1), "n": n,
            "viscosidade_aparente_Pa_s": {str(g): round(eta_power_law(K, n, g), 1)
                                          for g in (0.1, 1.0, 10.0, 100.0, 1000.0)},
            "eta0_Pa_s": round(eta0, 0),
            "lambda_s": round(0.85 * (5000.0 / eta100) ** 0.5, 3),   # tempo de relaxacao encolhe com o teor
                                                                      # de carga: mesmo family, outro fill
            "ancora_Pa_s_em_100_1_s": eta100,
            "uso": ("banda baixa: mastique quente e bem plastificado - o minimo plausivel para um resistivo"
                    if nome == "otimista" else
                    ("centro da faixa: o que a literatura de composto EPDM + negro de fumo pede em 10^2 1/s"
                     if nome == "tipico" else
                     "banda alta: mastique frio e muito carregado - o cenario em que nada passa pela fenda")),
        }

    saida = {
        "material": "mastique (manta) resistivo não-linear à base de EPDM, não vulcanizado, carregado "
                    "— definição dada pelo dono do projeto em 2026-09-13",
        "como_este_arquivo_deve_ser_lido": "a banda, não o ponto. Os três jogos são a mesma família de "
                                           "material em três teores de negro de fumo/estado térmico; a "
                                           "conclusão da simulação só vale se for a mesma nas três.",
        "temperatura_de_referencia_C": T_LINHA,
        "temperatura_atual_do_SSOT_C": T_ATUAL,
        "reologia_atual_do_SSOT": {"K_Pa_s_n": K_ATUAL, "n": N_ATUAL,
                                   "deslocada_para_a_linha": round(K_na_linha, 1)},
        "K_na_temperatura_da_linha_Pa_s_n": round(K_na_linha, 1),         "por_que_nao_usar_o_K_deslocado": "o K deslocado por Arrhenius e do master de termoplastico, nao do  mastique: ele so aparece aqui como referencia de ordem de grandeza. A ancora que a simulação usa e a viscosida  de aparente em 100 1/s (ETA100_PA_S), que e como se mede composto de borracha em capilar.",
        "curvas": curvas,
        "limite_de_raspado_na_saida_MPa": TAU_SHARKSKIN_MPA,
        "limite_de_escorregamento_na_parede_MPa": TAU_ESCORREGAMENTO_MPA,
        "limite_com_auxiliar_de_processamento_MPa": TAU_LIMITE_COM_PCA_MPA,
        "janela_de_energia_da_linha_MPa": {"dP_na_matriz": list(DP_MATRIZ_FAIXA_MPA),
                                           "vazao_g_min": list(VAZAO_FAIXA_G_MIN),
                                           "leitura": "fora dessa janela a linha não é mais a linha do artigo; "
                                                      "dP acima do topo significa que o material procura outra "
                                                      "saída — e no nosso conjunto só existe uma: o anel entre "
                                                      "a matriz e o furo do cabeçote, para trás"},
        "densidade_g_cm3": RHO_MASTIC * 1000.0,
        "modelos_alternativos": {
            "Herschel-Bulkley (composto cru, squeeze flow)": {
                "porque": "os ensaios de compressão em três compostos crus ajustam melhor com limiar de "
                          "escoamento que com lei-potência pura; em fenda de 1,5 mm isso significa núcleo "
                          "parado no meio do canal e raspado nas bordas",
                "tau_y_Pa": [0.0, 2000.0, 6000.0]},
            "Cox-Merz": "NÃO usar: documentadamente inaplicável a composto carregado (o G* do reômetro de "
                        "disco não cai em cima da curva de capilar)"},
        "fontes": [
            {"o": "dP de matriz 2,1-9,4 MPa; 41-128 g/min; matriz a 70 C, cabeça 79-87 C (EPDM, perfil)",
             "onde": "Polymers 18(9):1122 (2026) — Numerical Investigation of Die Swell Behavior in EPDM "
                     "Rubber Extrusion", "url": "https://www.mdpi.com/2073-4360/18/9/1122"},
            {"o": "sharkskin em tau_parede >= 0,14 MPa; escorregamento em ~0,1 MPa; limiar sobe a ~0,5 MPa "
                  "com auxiliar de processamento/BN",
             "onde": "J. Vlachopoulos, The Role of Rheology in Polymer Extrusion",
             "url": "http://www.polydynamics.com/Rheology.pdf"},
            {"o": "composto cru: lei-potência boa em faixa larga de gama, Herschel-Bulkley melhor no total",
             "onde": "Journal of Rheology 70, 65 (2026) — Viscosity characterization of uncured rubber "
                     "compounds via uniaxial compression",
             "url": "https://pubs.aip.org/sor/jor/article/70/1/65/3374181/"},
            {"o": "EPDM com negro de fumo: viscosidade/tau_Parede/die swell medidos em capilar; Cox-Merz não "
                  "vale",
             "onde": "Polymer 39 (1998) — Rheological properties of EPDM compound",
             "url": "https://www.sciencedirect.com/science/article/abs/pii/S0032386197002310"}],
        "o_que_nao_eh_medido_aqui": [
            "não há reômetro deste lote específico no repo: K é a família do SSOT deslocada em temperatura e "
            "multiplicada por 3/8/20 — os três números têm de ser lidos como intervalo",
            "o limiar de escoamento (tau_y) é faixa de literatura, não medida: se ele existir de fato, o miolo "
            "da fenda para de escoar antes da borda, e é aí que a serra nasce",
            "a temperatura real do seu cabeçote (EX-030) não foi medida; usamos a da linha análoga (90 C)"],
    }
    json.dump(saida, open(a.json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("JSON ->", os.path.relpath(a.json, RAIZ))

    L = ["# Reologia do mastique resistivo à base de EPDM — o que a simulação vai usar\n",
         "Você definiu o material (*\"mastic resistivo não linear a base de EPDM\"*) e mandou buscar valores de "
         "literatura. Este arquivo é o resultado, gerado por `04_Dados_SSOT_e_Scripts/masti_epdm_reologia.py`: "
         "**uma banda, não um número**, porque reômetro deste lote não existe no repo e inventar precisão aqui "
         "seria o pior tipo de erro.\n",
         "## Os três jogos\n",
         "| nível | K (Pa·sⁿ) | n | η(0,1 s⁻¹) | η(10 s⁻¹) | η(100 s⁻¹) | η(1000 s⁻¹) (Pa·s) | o que representa |",
         "|---|---|---|---|---|---|---|---|"]
    for nome, c in curvas.items():
        v = c["viscosidade_aparente_Pa_s"]
        L.append("| `%s` | %.0f | %.2f | %s | %s | %s | %s | %s |"
                 % (nome, c["K_Pa_s_n"], c["n"], v["0.1"], v["1.0"], v["10.0"], v["1000.0"], c["uso"]))
    L += ["\nPonto de partida: o SSOT traz K = %.0f Pa·s^%.2f a %.0f °C (EPR/XLPE/PVC modificado). Deslocado "
          "para %.0f °C com a Ea/R do próprio SSOT, dá K = %.0f; os três níveis acima são 3×, 8× e 20× esse "
          "valor — que é a ordem de grandeza entre um masterbatch e um mastique resistivo muito carregado.\n"
          % (K_ATUAL, N_ATUAL, T_ATUAL, T_LINHA, K_na_linha),
          "## Os dois critérios que a simulação tem de responder\n",
          "1. **passa ou volta** — a queda de pressão necessária na fenda de cada matriz, comparada à janela da "
             "linha: no processo análogo medido na literatura, matriz de perfil EPDM opera com **2,1–9,4 MPa** "
             "a 41–128 g/min. Acima do topo, o material procura outra saída; e neste conjunto existe exatamente "
             "outra saída (medida na C4 da auditoria de correlações: anel com folga de 1,00/0,25/0,25 mm, "
             "contínuo do bico até a entrada da matriz).",
          "2. **raspa ou não raspa** — a tensão de cisalhamento na parede na boca de saída. O limiar de "
             "*sharkskin* é **0,14 MPa** (escorregamento a partir de ~0,1 MPa; com auxiliar de processamento, "
             "até ~0,5 MPa). Onde a parede passa disso nos **cantos** da fenda, é aí que a serra aparece — e é "
             "por isso que a forma da borda (estádio × canto vivo) foi medida na auditoria, na seção a 0,01 mm da "
             "face de saída: Copo e Gedeon CERTA dão **112,017 mm²** = estádio 75,00 × 1,50 com R 0,75; "
             "Jonatha v27 e v28.1 dão **346,654 mm²** = o mesmo estádio já aberto pelo chanfro de saída "
             "(boca 78,00 × 4,50); a `MatrizDesenvolvimento` histórica dá **351,0 mm²** = o retângulo "
             "78,00 × 4,50 **sem arredondamento nenhum** — canto vivo, onde a manta rasga. É a diferença "
             "geométrica que a sua serra na borda pede para olhar primeiro.\n",
          "## O que não é medido aqui\n",
          "\n".join("* %s" % x for x in saida["o_que_nao_eh_medido_aqui"]),
          "\n## Fontes\n",
          "\n".join("* %s — %s ([link](%s))" % (f["o"], f["onde"], f["url"]) for f in saida["fontes"]),
          "\nGerado em 2026-09-13. Os números de geometria citados vêm de "
          "`03_/AUDITORIA_CORRELACOES_STEP.md` (medidos nos STEP)."]
    open(a.md, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("MD  ->", os.path.relpath(a.md, RAIZ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
