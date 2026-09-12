"""
AVALIAÇÃO DA MATRIZ 3 (JONATHA) - UNIFORMIDADE TRANSVERSAL
=========================================================
Lê o resultado do CFD 2D por seção (`avaliacao_matriz_3_secoes.json`) e resume a
uniformidade de vazão ao longo da largura de 75 mm.

Métrica principal (a que importa para a espessura final):
    uniformidade = q_min / q_max  (vazão local por mm de largura)
onde q_min e q_max são os extremos medidos na seção. Como a vazão local é
proporcional à espessura entregue (após a puxada), essa razão é também a razão
entre a espessura mínima e a máxima esperadas naquela seção.

Quando a seção é de fenda fina (land, altura ≈ 1,5 mm), o perfil q(x) é
integrado para mostrar QUANTO da vazão passa no núcleo de chapa plana
(|x| <= 36,75 mm) e nos últimos 0,75 mm de cada lado (zona do raio de borda
R0,75). Nas seções do funil o perfil amostrado não tem resolução suficiente
(seção alta, malha grossa para o passo do bin) - nesses casos só as métricas
escalares são reportadas, com a ressalva registrada.

Uso:  python avaliacao_matriz3_uniformidade.py [--json]
"""

import argparse
import json
import os

import numpy as np

DADOS = os.path.dirname(os.path.abspath(__file__))
RAIO_BORDA = 0.75      # mm - raio de borda R0,75
MEIA_LARGURA = 37.5    # mm
LIM_CORE = MEIA_LARGURA - RAIO_BORDA


def perfil_do_land(secao):
    """Integra o perfil q(x) na região de fenda plana. Só vale para o land."""
    x = np.array(secao["x_bin_mm"])
    q = np.array(secao["q_perfil"])
    o = np.argsort(x)
    x, q = x[o], q[o]
    mc = x <= LIM_CORE
    mb = x > LIM_CORE
    if not mc.any():
        return None
    Q_core = float(np.trapezoid(q[mc], x[mc]))
    Q_borda = float(np.trapezoid(q[mb], x[mb])) if mb.any() else 0.0
    larg_borda = float(x[mb].max() - LIM_CORE) if mb.any() else 0.0
    q_core_med = float(Q_core / (x[mc].max() - x[mc].min()))
    r = {
        "core_q_medio_mm3_s_mm": round(q_core_med, 1),
        "core_parcela_vazao_pct": round(100 * Q_core / (Q_core + Q_borda), 2),
        "core_dentro_5pct": round(100 * float(np.trapezoid(
            q[mc][np.abs(q[mc] - q_core_med) <= 0.05 * q_core_med], x[mc][np.abs(q[mc] - q_core_med) <= 0.05 * q_core_med]))
            / Q_core, 1),
        "core_dentro_10pct": round(100 * float(np.trapezoid(
            q[mc][np.abs(q[mc] - q_core_med) <= 0.10 * q_core_med], x[mc][np.abs(q[mc] - q_core_med) <= 0.10 * q_core_med]))
            / Q_core, 1),
    }
    # zona do raio de borda: o perfil amostrado tem 1 bin dentro do raio (0,5 mm).
    # Integra os últimos 1,0 mm de cada lado estendendo o último valor até a ponta
    # (x = 37,5 mm) - aproximação registrada como tal.
    m1 = x >= (MEIA_LARGURA - 1.0)
    if m1.any():
        x1, q1 = x[m1], q[m1]
        Q_1mm = float(np.trapezoid(np.append(q1, q1[-1]), np.append(x1, MEIA_LARGURA)))
        r["ultimo_1mm_parcela_vazao_pct"] = round(100 * Q_1mm / (Q_core + Q_borda), 2)
        r["ultimo_1mm_q_medio_mm3_s_mm"] = round(Q_1mm / 1.0, 1)
        r["ultimo_1mm_q_relativo_ao_nucleo_pct"] = round(100 * (Q_1mm / 1.0) / q_core_med, 1)
    if larg_borda > 0:
        q_borda_med = Q_borda / larg_borda
        r["borda_parcela_vazao_pct"] = round(100 * Q_borda / (Q_core + Q_borda), 2)
        r["borda_q_medio_mm3_s_mm"] = round(q_borda_med, 1)
        r["borda_q_relativa_ao_nucleo_pct"] = round(100 * q_borda_med / q_core_med, 1)
    r["perfil_ultimos_2mm"] = [[round(float(xi), 2), round(float(qi), 1)]
                               for xi, qi in zip(x[x >= (MEIA_LARGURA - 2.0)],
                                                 q[x >= (MEIA_LARGURA - 2.0)])]
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    with open(os.path.join(DADOS, "avaliacao_matriz_3_secoes.json"), encoding="utf-8") as fh:
        dados = json.load(fh)

    print("=" * 100)
    print("UNIFORMIDADE TRANSVERSAL DA VAZÃO — MATRIZ 3 (fenda de 75,00 mm, borda R0,75)")
    print("=" * 100)
    print(f"{'Z':>6} {'altura':>8} {'q médio':>9} {'q mín':>8} {'q máx':>8} {'uniformidade':>13} {'τ parede':>9}")
    print(f"{'[mm]':>6} {'[mm]':>8} {'[mm³/s/mm]':>9} {'[mm³/s/mm]':>8} {'[mm³/s/mm]':>8} {'qmin/qmax [%]':>13} {'[kPa]':>9}")
    linhas = []
    for s in dados["secoes"]:
        q_med = float(s["Q_total_mm3_s"]) / 75.0
        unif = 100 * float(s["q_min_mm3_s_por_mm"]) / float(s["q_max_mm3_s_por_mm"])
        linha = {
            "z_mm": s["z_mm"],
            "altura_max_mm": s["altura_max_mm"],
            "q_medio_mm3_s_mm": round(q_med, 1),
            "q_min_mm3_s_mm": s["q_min_mm3_s_por_mm"],
            "q_max_mm3_s_por_mm": s["q_max_mm3_s_por_mm"],
            "uniformidade_qmin_qmax_pct": round(unif, 1),
            "tau_medio_parede_kpa": s["tau_medio_parede_kpa"],
            "G_bar_mm": s["G_bar_por_mm"],
        }
        print(f"{s['z_mm']:6.1f} {s['altura_max_mm']:8.3f} {q_med:9.1f} {s['q_min_mm3_s_por_mm']:8.1f} "
              f"{s['q_max_mm3_s_por_mm']:8.1f} {unif:12.1f}% {s['tau_medio_parede_kpa']:9.1f}")
        if abs(s["altura_max_mm"] - 1.5) < 0.05:      # land: perfil tem resolução
            p = perfil_do_land(s)
            if p:
                linha.update(p)
        else:
            linha["aviso"] = ("perfil q(x) amostrado não resolve a seção alta do funil; "
                              "usar apenas as métricas escalares")
        linhas.append(linha)

    land = next((l for l in linhas if abs(l["altura_max_mm"] - 1.5) < 0.05), None)
    if land and "core_q_medio_mm3_s_mm" in land:
        print(f"\nLAND (Z={land['z_mm']:.1f} mm), detalhe do perfil na largura:")
        print(f"   núcleo plano |x| <= {LIM_CORE:.2f} mm (73,50 mm = {100 * 2 * LIM_CORE / 75:.0f}% da largura):")
        print(f"      q médio = {land['core_q_medio_mm3_s_mm']:.1f} mm³/s/mm | "
              f"{land['core_parcela_vazao_pct']:.2f}% da vazão total")
        print(f"      {land['core_dentro_5pct']:.1f}% da vazão do núcleo cai dentro de ±5% da média do núcleo; "
              f"{land['core_dentro_10pct']:.1f}% dentro de ±10%")
        print(f"   zona do raio R0,75 (últimos 0,75 mm de cada lado):")
        print(f"      {land['borda_parcela_vazao_pct']:.2f}% da vazão total | "
              f"q médio = {land['borda_q_medio_mm3_s_mm']:.1f} mm³/s/mm "
              f"({land['borda_q_relativa_ao_nucleo_pct']:.1f}% do núcleo)")
        print(f"   últimos 1,0 mm de cada lado: {land['ultimo_1mm_parcela_vazao_pct']:.2f}% da vazão total | "
              f"q médio = {land['ultimo_1mm_q_medio_mm3_s_mm']:.1f} mm³/s/mm "
              f"({land['ultimo_1mm_q_relativo_ao_nucleo_pct']:.1f}% do núcleo)")
        print("   perfil q(x) nos últimos 2 mm [x mm, q mm³/s/mm]: "
              + ", ".join(f"({a:.2f}, {b:.1f})" for a, b in land["perfil_ultimos_2mm"]))
        print("\n   Leitura: a aresta R0,75 recebe menos material por mm de largura do que o núcleo.")
        print("   Como a espessura entregue é proporcional à vazão local, a aresta sai mais fina —")
        print("   comportamento esperado e coerente com o R0,75 especificado na geometria.")

    if args.json:
        destino = os.path.join(DADOS, "avaliacao_matriz_3_uniformidade.json")
        with open(destino, "w", encoding="utf-8") as fh:
            json.dump({"projeto": "Avaliacao_Uniformidade_Matriz_3",
                       "metrica": "q_min/q_max da vazão local por mm de largura",
                       "raio_borda_mm": RAIO_BORDA, "limite_nucleo_mm": LIM_CORE,
                       "secoes": linhas}, fh, ensure_ascii=False, indent=2)
        print(f"\nJSON salvo em {os.path.relpath(destino, os.path.dirname(DADOS))}")


if __name__ == "__main__":
    main()
