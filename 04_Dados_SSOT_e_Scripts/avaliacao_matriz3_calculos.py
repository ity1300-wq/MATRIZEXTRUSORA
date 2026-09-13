"""
AVALIAÇÃO DA MATRIZ 3 (JONATHA) - CÁLCULOS DE ENGENHARIA
========================================================
Avaliação independente, sem alterar o modelo aprovado. Calcula, a partir da
geometria MEDIDA nos arquivos STEP:

 1. Perfil de pressão ao longo do canal (fatiamento fino, lei das potências)
    com o Δp por zona: entrada/funil, aproximação do land, land e chanfro.
    Validação cruzada: o gradiente no land é comparado com o CFD 2D
    (`cfd_land_crosssection.py`) - os dois métodos devem concordar.
 2. Força de abertura no plano de partição Y=0 e recomendação de fixação
    (quantidade de parafusos e deflexão entre eles).
 3. Tempo de residência (médio e por zona).
 4. Inchamento do extrudado (correlação de Tanner para lei das potências) e
    razão de puxada (draw-down) necessária para a espessura de 1,50 mm.
 5. Sensibilidade: comprimento do land (8,5 / 9,2 / 10 / 12 mm paralelos) e
    chanfro de saída (1,50 / 0,80 / 0,50 mm) - efeito em Δp, lábio de aço e
    comprimento útil do land.

Uso:  python avaliacao_matriz3_calculos.py [--json]
"""

import argparse
import json
import math
import os
import sys

import numpy as np

try:
    import cadquery as cq
except ImportError as exc:  # pragma: no cover
    print(f"ERRO: cadquery ausente ({exc}). Rode setup_cfd_env.sh.", file=sys.stderr)
    sys.exit(2)

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DIR_CAD = os.path.join(RAIZ, "07_CAD_Matrizes", "Matriz_Jonatha_v27_OFICIAL")
DIR_DADOS = os.path.dirname(os.path.abspath(__file__))

K_PL, N_PL, Q_MM3 = 18500.0, 0.32, 15000.0
RHO_KG_M3 = 1400.0
Z_LAND_INI, Z_PARALELO_FIM, Z_FIM = 99.0, 107.5, 109.0


def fluxo_fenda(W_mm, H_mm):
    """Vazão [m3/s] numa fenda W x H sob gradiente unitário (1 Pa/m)."""
    W, H = W_mm * 1e-3, H_mm * 1e-3
    return 2 * W * N_PL / (2 * N_PL + 1) * (H / 2) ** ((2 * N_PL + 1) / N_PL) * (1 / K_PL) ** (1 / N_PL)


def fluxo_circular(d_mm):
    """Vazão [m3/s] num duto circular Ød sob gradiente unitário."""
    r = d_mm * 1e-3 / 2
    return math.pi * r ** 2 * (N_PL / (3 * N_PL + 1)) * r ** ((N_PL + 1) / N_PL) * (1 / K_PL) ** (1 / N_PL)


def gradiente(q_fluxo):
    """Gradiente de pressão [bar/mm] para a vazão alvo."""
    return (Q_MM3 * 1e-9 / q_fluxo) ** N_PL * 1e-8


def perfil_pressao(nucleo, dz=0.5):
    """Fatiamento fino: G(z), p(z) e Δp por zona."""
    zs, Gs, Hs, As = [], [], [], []
    z = 0.0
    while z <= Z_FIM + 1e-9:
        zc = min(z, Z_FIM - 1e-6)
        lam = cq.Workplane("XY").workplane(offset=zc).box(200, 200, 0.05).val()
        try:
            it = nucleo.intersect(lam)
            bb = it.BoundingBox()
            A = it.Volume() / 0.05
            W, H = bb.xmax - bb.xmin, bb.ymax - bb.ymin
        except Exception:
            z += dz
            continue
        if A < 1e-6 or H <= 0:
            z += dz
            continue
        if abs(W - H) <= 0.05 * W:              # seção quase circular (entrada)
            q = fluxo_circular(W)
        else:
            q = fluxo_fenda(A / H, H)           # largura efetiva = área / altura
        zs.append(zc); Gs.append(gradiente(q)); Hs.append(H); As.append(A)
        z += dz

    zs = np.array(zs); Gs = np.array(Gs); Hs = np.array(Hs); As = np.array(As)
    # integral cumulativa exata: P(z) = ∫₀^z G dz' (trapézio na malha de 0,5 mm).
    # As zonas são diferenças de P nas fronteiras - sem o truncamento que a
    # integração de máscara causava (perdia 2,07 bar nas fronteiras).
    P = np.concatenate([[0.0], np.cumsum(0.5 * (Gs[1:] + Gs[:-1]) * np.diff(zs))])
    p_rel = P.max() - P                              # Δp acumulado da entrada até z
    dp = float(P[-1])

    def entre(z1, z2):
        return float(np.interp(z2, zs, P) - np.interp(z1, zs, P))

    zonas = {
        "entrada_e_funil_z0_90": entre(0.0, 90.0),
        "aproximacao_do_land_z90_99": entre(90.0, Z_LAND_INI),
        "land_paralelo_z99_107_5": entre(Z_LAND_INI, Z_PARALELO_FIM),
        "chanfro_saida_z107_5_109": entre(Z_PARALELO_FIM, Z_FIM),
    }
    return {"z": zs, "G": Gs, "H": Hs, "A": As, "p_rel": p_rel, "P": P, "dp_total": dp, "zonas": zonas}


def forca_abertura(dados, z, A, p_rel):
    """Força que separa as metades no plano Y=0 (integral de p sobre a área projetada)."""
    largura = np.where(A / np.maximum(0.0, 1.0) > 0, np.minimum(75.0, 75.0 * np.ones_like(z)), 75.0)
    # área projetada no plano de partição = largura(z) x dz; largura ≈ 75 mm para
    # toda a extensão útil (o envelope externo é cilíndrico, a cavidade é 75 mm)
    F = float(np.trapezoid(p_rel * 1e5 * 75.0 * 1e-3, z * 1e-3))      # N
    A_proj = float(np.trapezoid(75.0 * np.ones_like(z), z))            # mm2
    p_med = float(np.trapezoid(p_rel, z) / (z[-1] - z[0]))
    return {"forca_n": F, "area_projetada_mm2": A_proj, "pressao_media_bar": p_med}


def deflexao_viga(L_mm, t_mm, p_mpa=6.8, E=2.1e5):
    I = 1.0 * t_mm ** 3 / 12.0
    return p_mpa * L_mm ** 4 / (384.0 * E * I)


def inchamento_tanner(n=N_PL):
    """Razão de inchamento (espessura) - correlação de Tanner para lei das potências."""
    return 0.13 + math.sqrt(1.0 + (1.0 / (2.0 * (1.0 + n))) ** 2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--dz", type=float, default=0.5)
    args = ap.parse_args()

    nucleo = max(cq.importers.importStep(
        os.path.join(DIR_CAD, "MatrizJonatha_Canal_Fluxo.step")).solids().vals(),
        key=lambda s: s.Volume())

    print("=" * 96)
    print("AVALIAÇÃO DA MATRIZ 3 — PERFIL DE PRESSÃO POR ZONAS")
    print(f"Fatiamento a cada {args.dz} mm | lei das potências K={K_PL} Pa·s^n, n={N_PL}, Q={Q_MM3} mm³/s")
    print("=" * 96)
    d = perfil_pressao(nucleo, args.dz)
    print(f"\nΔp total estimado (1D, geometria medida) = {d['dp_total']:.2f} bar")
    for nome, v in d["zonas"].items():
        print(f"   {nome:32s} = {v:6.2f} bar   ({100 * v / d['dp_total']:4.1f}%)")
    G_land = float(np.mean(d["G"][(d["z"] > 100) & (d["z"] < 107)]))
    print(f"\n   gradiente no land: 1D = {G_land:.4f} bar/mm  |  "
          f"CFD 2D (cfd_land_crosssection.py) = 2,1761 bar/mm  ->  "
          f"concordância de {100 * min(G_land, 2.1761) / max(G_land, 2.1761):.1f}%")

    f = forca_abertura(d, d["z"], d["A"], d["p_rel"])
    print(f"\nFORÇA DE ABERTURA NO PLANO DE PARTIÇÃO")
    print(f"   área projetada ≈ {f['area_projetada_mm2']:.0f} mm² | pressão média = {f['pressao_media_bar']:.1f} bar")
    print(f"   força de abertura = {f['forca_n'] / 1000:.2f} kN  ({f['forca_n'] / 9810:.2f} tf)")
    for nb in (2, 4, 6):
        print(f"   {nb} × M8 12.9 (pré-carga conservadora de 20 kN) -> coeficiente {nb * 20e3 / f['forca_n']:.1f}")

    t_aco = 8.7   # parede de aço sobre a cavidade junto à entrada (medida na auditoria)
    print(f"\nDEFLEXÃO DO TETO DA CAVIDADE (viga engastada equivalente, aço t={t_aco} mm, p=6,8 MPa)")
    defl = {}
    for L in (25, 30, 40, 50, 60):
        w = deflexao_viga(L, t_aco)
        defl[L] = w
        print(f"   fixações a cada {L} mm -> abertura no plano de partição ≈ {w * 1000:.1f} µm "
              f"({100 * w / 1.5:.2f}% da espessura da fita)")

    vol_canal = nucleo.Volume()
    t_medio = vol_canal / Q_MM3
    print(f"\nTEMPO DE RESIDÊNCIA")
    print(f"   volume do canal = {vol_canal:.0f} mm³ | vazão = {Q_MM3} mm³/s")
    print(f"   tempo médio de residência = {t_medio:.1f} s")
    t_land = (75.0 * 1.5 * 8.5) / Q_MM3
    print(f"   no land (8,5 mm) = {t_land:.3f} s | no funil (Z=0-99) = {(vol_canal - 75 * 1.5 * 8.5) / Q_MM3:.1f} s")

    B = inchamento_tanner()
    print(f"\nINCHAMENTO (DIE SWELL) E PUXADA (DRAW-DOWN)")
    print(f"   razão de inchamento (Tanner, n={N_PL}) = {B:.3f}  -> espessura na saída ≈ {1.5 * B:.2f} mm")
    print(f"   razão de puxada para chegar a 1,50 mm = 1/{B:.3f} = {1 / B:.3f} (redução de {100 * (1 - 1 / B):.1f}%)")
    v_linha = Q_MM3 / 112.017     # mm/s
    print(f"   velocidade média no land = {v_linha:.1f} mm/s -> velocidade de recolhimento ≈ "
          f"{v_linha * B:.1f} mm/s")

    # ---- perda extensional na convergência (não capturada por escoamento desenvolvido)
    z, A = d["z"], d["A"]
    A_suave = np.convolve(A, np.ones(5) / 5, mode="same")
    v_med = (Q_MM3 * 1e-9) / np.maximum(A_suave * 1e-6, 1e-15)     # m/s
    eps_dot = np.abs(np.gradient(v_med, z * 1e-3))                # 1/s
    print(f"\nPERDA EXTENSIONAL NA CONVERGÊNCIA (não incluída no modelo 1D)")
    print(f"   taxa de deformação axial: máx = {eps_dot.max():.1f} 1/s em Z = {z[np.argmax(eps_dot)]:.1f} mm")
    pares = {}
    for razao in (3.0, 10.0):
        eta_E = razao * K_PL * np.maximum(eps_dot, 1e-6) ** (N_PL - 1.0)
        P = float(np.sum(eta_E * eps_dot ** 2 * (A_suave * 1e-6) * (z[1] - z[0]) * 1e-3))  # W
        dpe = P / (Q_MM3 * 1e-9) / 1e5                               # bar
        pares[razao] = dpe
        print(f"   razão de Trouton {razao:4.0f}x (η_E = {razao:.0f}·K·ε̇^(n-1)): Δp extensional ≈ {dpe:.1f} bar "
              f"-> Δp total {d['dp_total'] + dpe:.1f} bar")
    print(f"   ou seja: o Δp total real está entre {d['dp_total']:.1f} bar (limite desenvolvido, "
          f"Trouton baixo) e {d['dp_total'] + pares[10.0]:.1f} bar")

    # ---- residência na parede (camada de 0,05 mm)
    delta = 0.05                                                  # mm
    # G [bar/mm] -> 1e8 Pa/m ; tau_w = G*H/2
    tau_w = 0.5 * d["G"] * 1e8 * np.maximum(d["H"], 1e-6) * 1e-3     # Pa
    gdot_w = (tau_w / K_PL) ** (1.0 / N_PL)                        # 1/s
    t_parede = 0.0
    for i in range(len(z) - 1):
        v_parede = gdot_w[i] * delta                               # mm/s
        if v_parede > 1e-6:
            t_parede += (z[i + 1] - z[i]) / v_parede               # s
    # versão com o modelo de Carreau-Yasuda do SSOT (patamar newtoniano), que é mais
    # realista nas taxas baixas do funil do que extrapolar a lei das potências
    eta_0, lam, a_car = 42000.0, 0.85, 1.25
    gdot_cy = np.zeros_like(gdot_w)
    for i, tw in enumerate(tau_w):
        g = 1.0
        for _ in range(60):
            eta = eta_0 * (1.0 + (lam * g) ** a_car) ** ((N_PL - 1.0) / a_car)
            g_novo = tw / eta
            if abs(g_novo - g) / max(g_novo, 1e-30) < 1e-10:
                g = g_novo
                break
            g = 0.5 * g + 0.5 * g_novo
        gdot_cy[i] = g
    t_parede_cy = float(np.sum(np.where(gdot_cy[:-1] > 1e-12,
                                        (z[1:] - z[:-1]) / (gdot_cy[:-1] * delta), 0.0)))
    print(f"\nRESIDÊNCIA NA PAREDE (a {delta} mm da parede, onde a velocidade é v ≈ γ̇_w·δ)")
    print(f"   γ̇ na parede: {gdot_w[0]:.1f} 1/s no início do funil (Z=0) | "
          f"{np.interp(70, z, gdot_w):.1f} 1/s em Z=70 | {np.interp(100, z, gdot_w):.0f} 1/s no land")
    print(f"   tempo de trânsito total pela parede (Z=0 a 109): {t_parede:.0f} s ({t_parede / 60:.1f} min) - lei das potências")
    print(f"     com o Carreau-Yasuda do SSOT (η0 = 42000 Pa·s): {t_parede_cy:.0f} s ({t_parede_cy / 60:.1f} min)")
    print(f"     a 0,5 mm da parede (10x mais longe) os valores caem 10x: {t_parede / 10 / 60:.1f} min / {t_parede_cy / 10 / 60:.1f} min")
    print(f"   comparação: residência média (volume/vazão) = {t_medio:.1f} s")
    print("   leitura: na entrada/funil a parede cisalha a poucos 1/s e o material encostado nela")
    print("   demora minutos para atravessar - é a região de risco de degradação/gel, não o land.")

    print(f"\nSENSIBILIDADE DA VAZÃO À FOLGA (d q/q = ((2n+1)/n)·d H/H = 5,125·dH/H)")
    for dh_um in (5, 10, 20, 50):
        print(f"   erro de folga de {dh_um:3d} µm na fenda de 1,50 mm -> {100 * 5.125 * dh_um * 1e-3 / 1.5:.2f}% "
              f"de variação de vazão/espessura")

    print(f"\nSENSIBILIDADE: LAND E CHANFRO")
    gl = G_land
    dp_chanfro_atual = d["zonas"]["chanfro_saida_z107_5_109"]        # bar nos 1,50 mm de chanfro
    g_chanfro = dp_chanfro_atual / 1.5                               # bar/mm no chanfro (divergente)
    print(f"{'configuração':38s} {'land util':>10} {'Δp land':>9} {'lábio aço':>10} {'Δp total':>10}")
    casos = [
        ("atual: chanfro 1,50 mm × 45°", 8.5, 1.5, 0.75),
        ("chanfro 0,80 mm × 45°", 9.2, 0.8, 1.45),
        ("chanfro 0,50 mm × 45°", 9.5, 0.5, 1.75),
        ("land 10 mm paralelo (chanfro 1,5)", 10.0, 1.5, 0.75),
        ("land 12 mm paralelo (chanfro 1,5)", 12.0, 1.5, 0.75),
    ]
    sens = []
    for nome, land, ch, labio in casos:
        dp_land = gl * land
        dp_ch = g_chanfro * ch                      # resistência medida do chanfro (0,91 bar/mm)
        dp_tot = d["dp_total"] - gl * 8.5 - g_chanfro * 1.5 + dp_land + dp_ch
        sens.append({"caso": nome, "land_util_mm": land, "dp_land_bar": dp_land,
                     "labio_aco_mm": labio, "dp_total_bar": dp_tot, "chanfro_mm": ch})
        print(f"{nome:38s} {land:8.1f} mm {dp_land:8.2f} b {labio:9.2f} mm {dp_tot:9.2f} b")

    if args.json:
        destino = os.path.join(DIR_DADOS, "avaliacao_matriz_3_calculos.json")
        with open(destino, "w", encoding="utf-8") as fh:
            json.dump({
                "projeto": "Avaliacao_Matriz_3_Jonatha",
                "metodo": ("fatiamento fino dos STEP com lei das potências (escoamento "
                           "desenvolvido) + correlações analíticas"),
                "dp_total_bar": round(d["dp_total"], 2),
                "zonas_bar": {k: round(v, 2) for k, v in d["zonas"].items()},
                "gradiente_land_bar_mm": round(G_land, 4),
                "gradiente_land_cfd_bar_mm": 2.1761,
                "forca_abertura": {"forca_kN": round(f["forca_n"] / 1000, 2),
                                   "pressao_media_bar": round(f["pressao_media_bar"], 1),
                                   "area_projetada_mm2": round(f["area_projetada_mm2"], 0)},
                "deflexao_um": {str(k): round(v * 1000, 2) for k, v in defl.items()},
                "residencia_s": {"media": round(t_medio, 2), "land": round(t_land, 3),
                                 "parede_0_05mm": round(t_parede, 1),
                                 "parede_0_05mm_carreau": round(t_parede_cy, 1)},
                "perda_extensional_bar": {"trouton_3x": round(pares[3.0], 2), "trouton_10x": round(pares[10.0], 2)},
                "dp_total_limite_superior_bar": round(d["dp_total"] + pares[10.0], 2),
                "inchamento": {"razao_tanner": round(B, 3), "espessura_saida_mm": round(1.5 * B, 3),
                               "razao_puxada": round(1 / B, 3)},
                "sensibilidade_land_chanfro": sens,
                "perfil_pressao": {"z_mm": d["z"].tolist(), "p_rel_bar": d["p_rel"].tolist(),
                                   "G_bar_mm": d["G"].tolist(), "altura_mm": d["H"].tolist()},
            }, fh, ensure_ascii=False, indent=2)
        print(f"\nJSON salvo em {os.path.relpath(destino, RAIZ)}")


if __name__ == "__main__":
    main()
