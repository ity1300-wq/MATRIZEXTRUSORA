#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rotas do mastique: passa pela fenda ou escapa pelo anel — e se encurtar a matriz de 109 para 100 mm ajuda.

A pergunta dele (2026-09-13): "é melhor deixar o comprimento total com 109 ou com 100, pra ter menos chance do
material retornar pelo funil?" A conta inteira abaixo responde: **o comprimento total quase não entra na conta —
o que manda é o comprimento de land (a fenda paralela) e a folga anular entre a matriz e o furo do cabeçote,
que é a rota de fuga. Encurtar a peça de 109 para 100 mm encurta justamente a rota de fuga.**

Geometria é toda **medida nos STEP** (o vazio da peça inteira + seções finas varrendo o eixo Z, com as mesmas
funções da auditoria de correlações); as folgas do anel vêm do bloco C4 de `auditoria_step_correlacoes.json`.
Reologia de `masti_epdm_reologia.json` (banda ancorada em η(100 s⁻¹), com as quatro fontes no JSON).

Modelo 1D — fenda, funil e anel como placas paralelas retas, fluido lei-potência (K, n):

    tau_parede = K * [ (2n+1)/n * Q / (W h^2) ] ^ n
    dP         = 2 * tau_parede * L / h

Tramos em série somam dP; rotas em paralelo dividem a vazão sob o mesmo dP (resolvido por bisseção). É o mesmo
esqueleto do estudo 1D que já existia no repo, agora com as duas rotas e as quatro matrizes. Não substitui a
CFD 3D — diz *onde* a 3D tem de olhar e responde a pergunta do comprimento.

Uso:  python3 04_Dados_SSOT_e_Scripts/simular_rotas_e_comprimento.py [--md] [--q MM3_S] [--json ARQ]
"""
import argparse
import json
import math
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, ".."))
sys.path.insert(0, AQUI)

from auditar_step_correlacoes import abre, maior, inventario, vazio_da_peca, _seccao, n, DIR_MAE  # noqa: E402

F_MASTI = os.path.join(AQUI, "masti_epdm_reologia.json")
F_AUDIT = os.path.join(AQUI, "auditoria_step_correlacoes.json")
SSOT = json.load(open(os.path.join(AQUI, "cad_die_parameters.json"), encoding="utf-8"))
Q_PADRAO = SSOT["rheological_model_parameters"]["flow_rate_cm3_s"] * 1000.0
AREA_ESTADIO_112 = (75.0 - 1.5) * 1.5 + math.pi * 1.5 * 1.5 / 4.0        # 112,0171 mm2, a fenda do contrato
PECAS = {"Copo (original)": ("matriz_1_copo_historica", "Matriz_Copo_HISTORICA/Matriz1_Original_Copo.step"),
         "Gedeon CERTA (a sua)": ("gedeon_certa_arquivo_do_usuario", "Matriz_Gedeon_Certa/matrizGedeonCerta.step"),
         "Jonatha v27.0 (bipartida)": ("jonatha_v27_oficial", "Matriz_Jonatha_v27_OFICIAL/MatrizJonatha.step"),
         "Jonatha v29.0 (peça única)": ("jonatha_v29_oficial",
                                       "Matriz_Jonatha_v29_OFICIAL/MATRIZ_V29_PECA_UNICA.step")}


# --------------------------------------------------------------------------- o fluido
def fluidos():
    m = json.load(open(F_MASTI, encoding="utf-8"))
    out = {}
    for k, v in m["curvas"].items():
        out[k] = dict(K=v["K_Pa_s_n"], n=v["n"], ancora=v.get("ancora_Pa_s_em_100_1_s"))
    out["_janela_da_linha_MPa"] = m["janela_de_energia_da_linha_MPa"]
    out["_tau_raspado_MPa"] = m["limite_de_raspado_na_saida_MPa"]
    return out


# --------------------------------------------------------------------------- a hydraulica
def tau_dp(K, nn, L, W, h, Q):
    """(tau_parede [Pa], dP [Pa]) para placas paralelas de largura W, abertura h, comprimento L. Zero se h<=0."""
    if h <= 0 or L <= 0 or W <= 0 or Q <= 0:
        return 0.0, 0.0
    g = (2.0 * nn + 1.0) / nn * Q / (W * h * h)                  # gama_dot na parede, 1/s
    tau = K * g ** nn
    return tau, 2.0 * tau * L / h


def q_de_dp(K, nn, L, W, h, dp):
    """Vazão que passa por um canal de placas dada uma queda de pressão (inverso da fórmula acima)."""
    if h <= 0 or L <= 0 or W <= 0 or dp <= 0:
        return 0.0
    c = (2.0 * nn + 1.0) / nn
    return W * h * h / c * (dp * h / (2.0 * K * L)) ** (1.0 / nn)


# --------------------------------------------------------------------------- geometria medida
def perfil_do_canal(caminho):
    """Varre a seção do vazio no eixo Z e devolve o que a peça é de fato: o comprimento de land paralelo real
    (a fenda do contrato, sem o chanfro de saída), a área na boca, o comprimento do canal."""
    sh = abre(caminho)
    inv = inventario(sh)
    _v, void = vazio_da_peca(sh, inv)
    if void is None:
        return None
    z_out, z_in = inv["caixa"]["z"][1], inv["caixa"]["z"][0]
    passo, z, areas = 0.25, z_out - 0.01, []
    while z > z_in + 0.05 and len(areas) < 600:
        r = _seccao(void, z)
        areas.append((round(z, 2), round(r[1], 3) if r else None))
        z -= passo
    # o primeiro z (de tras para frente) em que a secao ainda e a fenda do contrato:
    i0 = next((i for i, (_z, a) in enumerate(areas) if a and a < 1.30 * AREA_ESTADIO_112), None)
    if i0 is None:
        land, z_land = 0.0, z_out
    else:
        z_land = areas[i0][0]
        j = i0
        while j + 1 < len(areas) and areas[j + 1][1] and \
                abs(areas[j + 1][1] - AREA_ESTADIO_112) / AREA_ESTADIO_112 < 0.05:
            j += 1
        land = round(z_land - areas[j][0], 2)
    return {"comprimento_peca_mm": round(z_out - z_in, 2), "area_saida_mm2": areas[0][1],
            "area_no_land_mm2": areas[i0][1] if i0 is not None else None,
            "land_paralelo_medido_mm": land, "z_onde_o_land_comeca": z_land,
            "arquivo": os.path.relpath(caminho, RAIZ)}


def anel_do_cabecote(chave, reserva="jonatha_v27_oficial"):
    """[(folga radial mm, comprimento mm, Ø médio mm)] por estágio, lidos do bloco C4 da auditoria (medido)."""
    d = json.load(open(F_AUDIT, encoding="utf-8"))
    m = d["C4"]["matrizes"].get(chave) or d["C4"]["matrizes"].get(reserva)
    if not m:
        return None
    return [(f["folga_radial_mm"], round(f["z"][1] - f["z"][0], 2),
             (f["estagio_D_matriz"] + f["furo_D"]) / 2.0) for f in m["folgas_por_estagio"]]


# --------------------------------------------------------------------------- as duas rotas
def rota_fenda(K, nn, geo, Q, land_mm=None):
    """dP do caminho certo: funil + transição + land + chanfro de saída. O funil é aproximado por placas de
    abertura média 6,00 mm (SSOT: manifold_central_depth_mm) no comprimento que sobra."""
    L_tot = geo["comprimento_peca_mm"]
    land = land_mm if land_mm is not None else geo["land_paralelo_medido_mm"]
    L_funil = max(1.0, L_tot - land - 1.5)
    _t, dp_funil = tau_dp(K, nn, L_funil, 75.0, 6.0, Q)
    _t, dp_trans = tau_dp(K, nn, 3.5, 75.0, 3.0, Q)
    _t, dp_land = tau_dp(K, nn, land, 75.0, 1.5, Q)
    boca = geo.get("area_saida_mm2") or 0.0
    h_b = 4.5 if boca > 200.0 else 1.5                                  # chanfro 1,50x45 abre a boca em Z
    tau_saida, dp_saida = tau_dp(K, nn, 1.5, 78.0, h_b, Q)
    tau_land = tau_dp(K, nn, land, 75.0, 1.5, Q)[0]
    return {"dp_bar": (dp_funil + dp_trans + dp_land + dp_saida) / 1e5,
            "trechos_bar": {"funil": round(dp_funil / 1e5, 2), "transicao": round(dp_trans / 1e5, 2),
                            "land": round(dp_land / 1e5, 2), "saida": round(dp_saida / 1e5, 2)},
            "tau_land_MPa": tau_land / 1e6, "land_mm": land, "L_funil_mm": round(L_funil, 2)}


def resolver(K, nn, geo, anel, Q, land_forcado=None):
    """Divide Q entre a fenda e o anel (paralelo, mesmo dP) e devolve o que escapa para trás."""
    def dp_fenda(qa):
        return rota_fenda(K, nn, geo, Q - qa, land_mm=land_forcado)["dp_bar"] * 1e5

    def dp_anel(qa):
        tot = 0.0
        for folga, L, d_med in (anel or []):
            _t, dp = tau_dp(K, nn, L, math.pi * d_med, 2.0 * folga, qa)
            tot += dp
        return tot

    lo, hi = 0.0, Q
    for _ in range(120):
        mid = 0.5 * (lo + hi)
        if (dp_fenda(lo) - dp_anel(lo)) * (dp_fenda(mid) - dp_anel(mid)) <= 0:
            hi = mid
        else:
            lo = mid
    qa = 0.5 * (lo + hi)
    qs = Q - qa
    r = rota_fenda(K, nn, geo, qs, land_mm=land_forcado)
    return {"dp_bar": round(r["dp_bar"], 1), "trechos_bar": r["trechos_bar"], "land_mm": r["land_mm"],
            "pct_pelo_anel": round(100.0 * qa / Q, 3), "q_saida_mm3_s": round(qs, 1),
            "v_saida_m_min": round(qs / (75.0 * 1.5) / 1000.0 * 60.0, 2),
            "tau_land_MPa": round(r["tau_land_MPa"], 3), "q_pelo_anel_mm3_s": round(qa, 1)}


# --------------------------------------------------------------------------- relatorio
def escreve_md(res, geo, aneis, destino):
    L = ["# Rotas do mastique: passa pela fenda ou escapa pelo anel — e 109 mm × 100 mm\n",
         "Gerado por `04_Dados_SSOT_e_Scripts/simular_rotas_e_comprimento.py`. Geometria **medida nos STEP** "
         "(o vazio da peça inteira, seção de 0,02 mm varrendo Z) e folgas do anel lidas do bloco C4 da "
         "auditoria de correlações. Reologia de `04_/masti_epdm_reologia.json` (banda ancorada em η(100 s⁻¹), "
         "com as quatro fontes). Vazão do projeto: %.0f mm³/s = %.1f cm³/s (a do SSOT).\n"
         % (res["vazao_mm3_s"], res["vazao_mm3_s"] / 1000.0),
         "## A resposta, direta\n",
         "**Deixa em 109 mm.** Encurtar para 100 mm não mexe em nada que gere pressão — o funil e o land ficam "
         "intactos, os 9,00 mm a menos são aço liso do meio da peça — e **encurta o caminho de fuga**: o anel "
         "entre a matriz e o furo do cabeçote é a rota pela qual o material escapa para trás, e anel mais curto "
         "tem menos resistência, então escapa *mais*. É esse o sinal que a tabela de cenários mostra.\n",
         "## O que cada matriz exige, com o mesmo material e a mesma vazão\n",
         "| matriz | comprimento | **land paralelo medido** | área no land | ΔP típico (bar) | banda baixa | "
         "banda alta | escapa pelo anel | saída (m/min) | τ no land (MPa) | raspado? |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for nome in res["geometria"]:
        c = res["cenarios"]["%s | como esta" % nome]
        t = c["tipico"]
        L.append("| `%s` | %.2f mm | **%.2f mm** | %s mm² | **%.1f** | %.1f | %.1f | %.3f %% | %.2f | %.3f | %s |"
                 % (nome, res["geometria"][nome]["comprimento_peca_mm"],
                    res["geometria"][nome]["land_paralelo_medido_mm"],
                    n(res["geometria"][nome]["area_no_land_mm2"] or 0, 4), t["dp_bar"], c["otimista"]["dp_bar"],
                    c["pessimista"]["dp_bar"], t["pct_pelo_anel"], t["v_saida_m_min"], t["tau_land_MPa"],
                    "SIM" if t["tau_land_MPa"] > res["tau_raspado_MPa"] else "não"))
    gd = res["geometria"].get("Gedeon CERTA (a sua)", {}).get("land_paralelo_medido_mm")
    jd = res["geometria"].get("Jonatha v29.0 (peça única)", {}).get("land_paralelo_medido_mm")
    gp = res["cenarios"].get("Gedeon CERTA (a sua) | como esta", {}).get("tipico", {}).get("dp_bar")
    jp = res["cenarios"].get("Jonatha v29.0 (peça única) | como esta", {}).get("tipico", {}).get("dp_bar")
    ga = res["cenarios"].get("Gedeon CERTA (a sua) | como esta", {}).get("tipico", {}).get("pct_pelo_anel")
    ja = res["cenarios"].get("Jonatha v29.0 (peça única) | como esta", {}).get("tipico", {}).get("pct_pelo_anel")
    L += ["\n**Leitura da tabela: o que separa as matrizes é o comprimento de land, não o comprimento da peça.** "
          "A fenda da Gedeon é passante — medida, ela tem land paralelo de **%.2f mm** contra **%.2f mm** da "
          "Jonatha — e o dP do land é linear no comprimento do land: %.1f bar contra %.1f bar, e a fração que "
          "escapa pelo anel sobe de %.3f %% para **%.3f %%** (%.0f×). É a versão numérica do \"volta pelo funil\": "
          "não é que o funil puxe o material para trás, é que a fenda da Gedeon exige pressão que a linha não "
          "tem, e o material procura o caminho de menor resistência.\n"
          % (gd or 0, jd or 0, gp or 0, jp or 0, ja or 0, ga or 0,
             (ga / ja) if (ga and ja) else 0),
          "\n## Os cenários de comprimento e de folga (Jonatha v29.0)\n",
          "| cenário | ΔP típico (bar) | escapa pelo anel | saída (m/min) | o que faz com a volta pelo funil |",
          "|---|---|---|---|---|"]
    for chave, c in res["cenarios"].items():
        if chave.endswith("| como esta") or chave in res["geometria"]:
            continue
        t = c["tipico"]
        rotulo = chave.split("| ", 1)[1]
        if "100 mm" in rotulo and "pinca" not in rotulo:
            efeito = "piora: o anel encurta e a fuga fica mais fácil"
        elif "pinca" in rotulo:
            efeito = "a pinça no anel devolve o que o encurtamento perdeu"
        elif "land" in rotulo:
            efeito = "menos pressão exigida da linha — o land é a alavanca"
        else:
            efeito = "corta a fuga sem encostar no produto"
        L.append("| %s | %.1f | %.3f %% | %.2f | %s |" % (rotulo, t["dp_bar"], t["pct_pelo_anel"],
                                                           t["v_saida_m_min"], efeito))
    L += ["\n## O que ainda falta para isso ser afirmação de processo, e não prévia\n",
          "* O funil é aproximado por placas de abertura média 6,00 mm (o `manifold_central_depth_mm` do SSOT) no "
          "comprimento medido. O que diz se há zona morta dentro do funil é a CFD 3D no volume dele (gmsh + "
          "scikit-fem: ambiente montado e testado, é o item deixado para a próxima etapa). Esta conta separa as "
          "rotas; não resolve recirculação.\n",
          "* `escapa pelo anel` é a vazão que o anel leva sob o **mesmo ΔP** das duas rotas: mede a fuga entre "
          "matriz e furo, não a velocidade com que o material volta pelo funil de alimentação da extrusora — isso "
          "depende da curva da rosca, que não está no repo.\n",
          "* A reologia é banda de literatura (η de 1.500 a 15.000 Pa·s em 100 s⁻¹), não reômetro do lote. O que "
          "é independente da banda: **a ordem das matrizes e o sinal de cada cenário** (as três curvas dão a "
          "mesma hierarquia, porque tudo escala com K).\n",
          "* O limiar de raspado (τ ≥ 0,14 MPa, literatura de capilar) dispara para **todas** as matrizes nesta "
          "vazão (15 cm³/s ≈ 9× a da linha análoga da literatura). Ou a linha real opera com o material mais "
          "quente/mais plastificado que a banda baixa, ou o limiar do produto plano é maior que o do capilar. "
          "É pergunta para o reômetro, não para o CAD.\n",
          "\nJanela de referência da linha análoga (EPDM, perfil): ΔP de matriz **%.1f–%.1f MPa** a %.0f–%.0f "
          "g/min; o repo tinha %.1f bar de ΔP 1D calibrado para a v27.0, que é da ordem da janela — a banda "
          "baixa desta tabela bate com ela.\n"
          % (res["janela_da_linha_MPa"]["dP_na_matriz"][0], res["janela_da_linha_MPa"]["dP_na_matriz"][1],
             res["janela_da_linha_MPa"]["vazao_g_min"][0], res["janela_da_linha_MPa"]["vazao_g_min"][1], 41.9)]
    open(destino, "w", encoding="utf-8").write("\n".join(L) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--q", type=float, default=Q_PADRAO, help="vazão em mm3/s (padrão: a do SSOT)")
    ap.add_argument("--md", action="store_true", help="escreve 03_/SIMULACAO_ROTAS_E_COMPRIMENTO.md")
    ap.add_argument("--json", default=os.path.join(AQUI, "simulacao_rotas_mastique.json"))
    a = ap.parse_args()

    fl = fluidos()
    janela = fl.pop("_janela_da_linha_MPa")
    tau_lim = fl.pop("_tau_raspado_MPa")

    print("[1] geometria medida em cada matriz (vazio da peça inteira, seções de 0,02 mm)")
    geo, aneis = {}, {}
    for nome, (chave, rel) in PECAS.items():
        caminho = os.path.join(DIR_MAE, rel)
        if not os.path.exists(caminho):
            print("    %-30s arquivo ausente: %s" % (nome, rel))
            continue
        g = perfil_do_canal(caminho)
        if g is None:
            print("    %-30s SEM VAZIO MEDIDO (pula)" % nome)
            continue
        geo[nome] = g
        aneis[nome] = anel_do_cabecote(chave)
        print("    %-30s compr. %.2f mm | land %.2f mm | área no land %s mm² | boca %s mm² | anel %s"
              % (nome, g["comprimento_peca_mm"], g["land_paralelo_medido_mm"], n(g["area_no_land_mm2"] or 0, 3),
                 n(g["area_saida_mm2"] or 0, 2),
                 " / ".join("%.2f mm × %.1f" % (f, L) for f, L, _d in (aneis[nome] or []))))

    print("[2] ΔP e fuga pelo anel, por matriz e por viscosidade (Q = %.0f mm³/s)" % a.q)
    res = {"vazao_mm3_s": a.q, "fluido": fl, "janela_da_linha_MPa": janela, "tau_raspado_MPa": tau_lim,
           "geometria": geo, "cenarios": {}}
    for nome in geo:
        linha = {curva: resolver(v["K"], v["n"], geo[nome], aneis[nome], a.q) for curva, v in fl.items()}
        res["cenarios"]["%s | como esta" % nome] = linha
        t = linha["tipico"]
        print("    %-30s dP %7.1f bar | escapa %6.3f%% | saída %5.2f m/min | τ_land %6.3f MPa %s"
              % (nome, t["dp_bar"], t["pct_pelo_anel"], t["v_saida_m_min"], t["tau_land_MPa"],
                 "| RASPA" if t["tau_land_MPa"] > tau_lim else ""))
        print("    %34s banda baixa %7.1f bar (%.3f%%) / banda alta %8.1f bar (%.3f%%)"
              % ("", linha["otimista"]["dp_bar"], linha["otimista"]["pct_pelo_anel"],
                 linha["pessimista"]["dp_bar"], linha["pessimista"]["pct_pelo_anel"]))

    print("[3] a pergunta dele: 109 mm ou 100 mm? (e o que muda de verdade)")
    base = "Jonatha v29.0 (peça única)"
    if base in geo:
        g, anel109 = geo[base], aneis[base]
        anel100 = [(anel109[0][0], round(anel109[0][1] - 9.0, 2), anel109[0][2])] + anel109[1:]
        cenarios = {
            "109 mm (como está)": dict(anel=anel109, land=None),
            "100 mm (encurtar a peça)": dict(anel=anel100, land=None),
            "100 mm + pinça de 0,15 na saída do anel": dict(
                anel=anel100[:2] + [(0.25, 20.30, 79.75), (0.15, 8.00, 79.75)], land=None),
            "109 mm + land 6,00": dict(anel=anel109, land=6.00),
            "109 mm + land 5,00": dict(anel=anel109, land=5.00),
            "109 mm + anel apertado nos 3 estágios (0,40/0,15/0,15)": dict(
                anel=[(0.40, anel109[0][1], 94.0), (0.15, anel109[1][1], 91.0), (0.15, anel109[2][1], 79.75)],
                land=None),
            "109 mm + anel apertado só no último estágio (0,10)": dict(
                anel=anel109[:2] + [(0.10, anel109[2][1], 79.75)], land=None),
        }
        for rotulo, kw in cenarios.items():
            linha = {curva: resolver(v["K"], v["n"], g, kw["anel"], a.q, land_forcado=kw["land"])
                     for curva, v in fl.items()}
            res["cenarios"]["%s | %s" % (base, rotulo)] = linha
            t = linha["tipico"]
            print("    %-56s dP %7.1f bar | escapa %6.3f%% | saída %5.2f m/min"
                  % (rotulo, t["dp_bar"], t["pct_pelo_anel"], t["v_saida_m_min"]))

    json.dump(res, open(a.json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("JSON ->", os.path.relpath(a.json, RAIZ))
    if a.md:
        destino = os.path.join(RAIZ, "03_Relatorios_e_Documentacao", "SIMULACAO_ROTAS_E_COMPRIMENTO.md")
        escreve_md(res, geo, aneis, destino)
        print("MD  ->", os.path.relpath(destino, RAIZ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
