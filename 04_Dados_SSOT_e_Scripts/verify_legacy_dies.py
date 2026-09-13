"""
AUDITORIA DAS MATRIZES (HISTÓRICAS + OFICIAL) - O QUE É REAL E O QUE NÃO É
==========================================================================
Mede a geometria real de cada matriz nos arquivos STEP e confronta com:

  1. A consistência interna dos arquivos entregues
     (o "canal de fluxo" isolado corresponde ao vazio da montagem?);
  2. Os números declarados nos relatórios (`dados_simulacao_reologica.json`),
     recalculando a perda de carga por lei das potências em 1D sobre a
     geometria MEDIDA (escoamento desenvolvido, aproximação de lubrificação).

Uso:
    python verify_legacy_dies.py            # relatório no console
    python verify_legacy_dies.py --json     # salva auditoria_matrizes_historicas.json

Requisitos: cadquery (pip install cadquery). Em contêineres sem libGL, rode antes
`bash setup_headless_gl.sh` e exporte LD_LIBRARY_PATH.

IMPORTANTE (limites do método): a estimativa 1D não captura contrações bruscas
(parede cega de 90°) nem efeitos de entrada (Bagley). Ela serve para validar a
ORDEM DE GRANDEZA dos números declarados e comparar matrizes entre si.
"""

import argparse
import json
import math
import os
import sys

try:
    import cadquery as cq
except ImportError:  # pragma: no cover
    print("ERRO: cadquery não está instalado.", file=sys.stderr)
    sys.exit(2)

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OFICIAL = os.path.join(RAIZ, "07_CAD_Matrizes", "M01_Jonatha_v27_OFICIAL")
HIST = os.path.join(RAIZ, "02_CAD_Modelos_Historicos")
DADOS = os.path.join(RAIZ, "04_Dados_SSOT_e_Scripts")

# Parâmetros reológicos do SSOT (usados nas contas do próprio projeto)
K_PA_SN = 18500.0
N_INDICE = 0.32
Q_MM3_S = 15000.0

ESP = 0.002  # espessura da lâmina de corte [mm]


def secao(solido, z, esp=ESP):
    """(largura X, altura Y, área) da seção do sólido na cota Z."""
    lam = cq.Workplane("XY").workplane(offset=z).box(400, 400, esp).val()
    inter = solido.intersect(lam)
    b = inter.BoundingBox()
    return b.xmax - b.xmin, b.ymax - b.ymin, inter.Volume() / esp


def dp_fenda(W_mm, H_mm, L_mm):
    """Δp [bar] em fenda larga com fluido de lei das potências (escoamento desenvolvido)."""
    if W_mm <= 0 or H_mm <= 0 or L_mm <= 0:
        return 0.0
    W, H, L = W_mm * 1e-3, H_mm * 1e-3, L_mm * 1e-3
    Q = Q_MM3_S * 1e-9
    # Q = W * 2n/(2n+1) * (G/K)^(1/n) * (H/2)^((2n+1)/n)
    # -> G = K * ( Q*(2n+1) / (2*W*n*(H/2)^((2n+1)/n)) )^n
    # (a versão anterior tinha um fator extra (1+n)/n, que inflava o Δp em
    #  ((1+n)/n)^n = 1,573x; verificado contra o CFD 2D da seção do land)
    num = Q * (1 + 2 * N_INDICE)
    den = 2 * W * N_INDICE * (H / 2) ** ((1 + 2 * N_INDICE) / N_INDICE)
    return K_PA_SN * L * (num / den) ** N_INDICE / 1e5


def dp_circular(R_mm, L_mm):
    """Δp [bar] em duto circular com fluido de lei das potências."""
    if L_mm <= 0 or R_mm <= 0:
        return 0.0
    R, L = R_mm * 1e-3, L_mm * 1e-3
    Q = Q_MM3_S * 1e-9
    val = (3 * N_INDICE + 1) / N_INDICE * Q / (math.pi * R ** 3)
    return 2 * K_PA_SN * L / R * val ** N_INDICE / 1e5


def dp_total(canal, z_fim, dz=0.5):
    """Integra o Δp [bar] ao longo de Z pela geometria medida, em passos dz."""
    total, z, pico, z_pico = 0.0, 0.0, 0.0, 0.0
    if dz > z_fim:
        dz = max(z_fim / 100.0, 1e-4)  # sólidos muito curtos
    while z < z_fim - 1e-6:
        zc = min(z + dz / 2, z_fim - 1e-4)
        try:
            wx, wy, a = secao(canal, zc)
        except Exception:
            z += dz
            continue
        if a > 1 and wy > 0:
            if abs(wx - wy) <= 0.05 * wx:  # seção aproximadamente circular
                d = dp_circular(wx / 2, dz)
            else:
                d = dp_fenda(a / wy, wy, dz)  # largura efetiva = área / altura
            total += d
            if d > pico:
                pico, z_pico = d, zc
        z += dz
    return total, z_pico, pico / dz * z_fim if False else pico


def comprimento_land(canal, z_fim, espessura=1.5, tol=0.02):
    """Retorna (Z em que o canal atinge a espessura do land, comprimento do land)."""
    z_ini = None
    z = 0.0
    while z <= z_fim:
        try:
            _, wy, a = secao(canal, min(z, z_fim - 1e-4))
        except Exception:
            break
        if a > 1 and abs(wy - espessura) <= tol:
            z_ini = z
            break
        z += 0.25
    if z_ini is None:
        return None, 0.0
    return z_ini, z_fim - z_ini


def tau_parede(W_mm, H_mm):
    """Tensão de cisalhamento na parede [kPa] pela lei das potências (fenda larga)."""
    gdot_app = 6 * Q_MM3_S / (W_mm * H_mm * H_mm)
    gdot_w = ((2 * N_INDICE + 1) / (3 * N_INDICE)) * gdot_app
    return K_PA_SN * gdot_w ** N_INDICE / 1000.0, gdot_w


def construir_envelope(estagios):
    """Sólido do envelope externo a partir de [(z0, z1, diametro), ...]."""
    env = None
    for z0, z1, d in estagios:
        seg = cq.Workplane("XY").workplane(offset=z0).circle(d / 2).extrude(z1 - z0)
        env = seg if env is None else env.union(seg)
    return env.val()


def volume_vazio(corpos, estagios):
    """Volume exato do vazio interno [mm³] = envelope externo - união dos corpos de aço.

    Método robusto (um único boolean por corpo), independente de a montagem trazer
    ou não o sólido do canal de polímero.
    """
    uniao = None
    for c in corpos:
        uniao = c if uniao is None else uniao.fuse(c)
    envelope = construir_envelope(estagios)
    return envelope.Volume() - uniao.Volume()


MATRIZES = [
    {
        "nome": "Matriz 1 - Copo (original)",
        "montagem": os.path.join(HIST, "Matriz1_Original_Copo.step"),
        "canal": os.path.join(HIST, "Matriz1_Original_Copo_Canal_Fluxo.step"),
        "canal_da_montagem": False,
        "declarado": "Matriz_1_Copo",
        # Matriz 1 (copo) não possui o 3º estágio: termina em Z=80,70 mm
        "estagios": [(0.0, 69.9, 93.0), (69.9, 80.7, 89.5)],
    },
    {
        "nome": "Matriz 2 - Gedeon",
        "montagem": os.path.join(HIST, "MatrizGedeon.step"),
        "canal": os.path.join(HIST, "MatrizGedeon_Canal_Fluxo.step"),
        # nesta montagem o núcleo é um sólido separado; o arquivo isolado está errado
        "canal_da_montagem": True,
        "declarado": "Matriz_2_Gedeon",
        "estagios": [(0.0, 69.9, 93.0), (69.9, 80.7, 89.5), (80.7, 109.0, 79.5)],
    },
    {
        "nome": "Matriz Desenvolvimento",
        "montagem": os.path.join(HIST, "MatrizDesenvolvimento_Com_Fluxo.step"),
        "canal": os.path.join(HIST, "MatrizDesenvolvimento_Canal_Fluxo.step"),
        "canal_da_montagem": False,
        "declarado": None,
        "estagios": [(0.0, 69.9, 93.0), (69.9, 80.7, 89.5), (80.7, 109.0, 79.5)],
    },
    {
        "nome": "Matriz Jonatha v27 (oficial)",
        "montagem": os.path.join(OFICIAL, "MatrizJonatha_Com_Fluxo.step"),
        "canal": os.path.join(OFICIAL, "MatrizJonatha_Canal_Fluxo.step"),
        "canal_da_montagem": False,
        "declarado": "Matriz_Jonatha_Master_v27_0",
        "estagios": [(0.0, 69.9, 93.0), (69.9, 80.7, 89.5), (80.7, 109.0, 79.5)],
    },
]


def analisar(cfg, declarados):
    print("\n" + "=" * 100)
    print(f"### {cfg['nome']}")
    r = {"matriz": cfg["nome"]}

    mont = cq.importers.importStep(cfg["montagem"])
    sols = mont.solids().vals()
    bb = mont.val().BoundingBox()
    aco_total = sum(s.Volume() for s in sols if s.Volume() > 1000)
    pequenos = sorted(round(s.Volume(), 2) for s in sols if s.Volume() <= 1000)
    bbs = sorted((s.BoundingBox().zmax - s.BoundingBox().zmin, s.Volume()) for s in sols)
    print(f"  Montagem: {len(sols)} sólidos | Z total = {bb.zmax - bb.zmin:.2f} mm | "
          f"Ø externo máx = {bb.xmax - bb.xmin:.2f} mm")
    r["z_total_mm"] = round(bb.zmax - bb.zmin, 3)
    r["diametro_externo_mm"] = round(bb.xmax - bb.xmin, 3)

    # canal: do arquivo isolado e/ou do sólido dentro da montagem
    canal_arq = None
    if os.path.exists(cfg["canal"]):
        c = cq.importers.importStep(cfg["canal"])
        cs = c.solids().vals()
        canal_arq = max(cs, key=lambda s: s.Volume()) if cs else None
        r["canal_arquivo_solidos"] = len(cs)
        r["canal_arquivo_vol_mm3"] = round(canal_arq.Volume(), 2) if canal_arq else None
        print(f"  Canal (arquivo isolado): {len(cs)} sólido(s) | vol = "
              f"{r['canal_arquivo_vol_mm3']} mm³")

    # vazio real do corpo (soma das fatias: disco externo - aço) = volume do canal de polímero
    # Corpos de aço = os 2 maiores sólidos (as duas metades bipartidas)
    ordenados = sorted(sols, key=lambda s: s.Volume(), reverse=True)
    corpos = ordenados[:2]
    vazio = volume_vazio(corpos, cfg["estagios"])
    r["canal_montagem_vol_mm3"] = round(vazio, 2)
    print(f"  Canal (vazio real da matriz = envelope - aço): vol = {vazio:.2f} mm³")

    # O canal real pode vir como sólido separado dentro da montagem (núcleo de polímero)
    canal_mont = None
    for s in ordenados[2:]:
        if vazio > 0 and abs(s.Volume() - vazio) <= 0.05 * vazio:
            canal_mont = s
            print(f"  Canal (núcleo de polímero dentro da montagem): vol = "
                  f"{s.Volume():.2f} mm³  <- usado nas medições abaixo")
            break
    if canal_arq and vazio:
        vol_arq_total = sum(x.Volume() for x in cq.importers.importStep(cfg["canal"]).solids().vals())
        dif = abs(vol_arq_total - vazio)
        # tolerância de 0,5%: o vazio da matriz inclui os furos de pino, que não
        # fazem parte do canal de polímero isolado
        r["canal_consistente"] = dif < max(1.0, 0.005 * vazio)
        r["canal_usado"] = "montagem" if canal_mont else "arquivo isolado"
        r["canal_arquivo_vol_total_mm3"] = round(vol_arq_total, 2)
        print(f"  >> CONSISTÊNCIA canal arquivo x montagem: "
              f"{'OK' if r['canal_consistente'] else 'INCONSISTENTE'} "
              f"(diferença de {dif:.2f} mm³)")
        if not r["canal_consistente"]:
            fator = vol_arq_total / vazio
            print(f"     ATENÇÃO: o arquivo isolado tem {fator:.2f}x o volume do canal real "
                  f"da matriz. Qualquer CFD/EDM feito sobre ele não representa esta matriz.")
        elif dif > 1.0:
            print(f"     (diferença de {dif:.2f} mm³ = furos de pino, que não são canal de polímero)")
    canal = canal_mont if canal_mont is not None else canal_arq

    # geometria do canal
    try:
        wx0, wy0, a0 = secao(canal, 0.01)
        area_circ = math.pi / 4 * wx0 ** 2
        if abs(wx0 - wy0) <= 0.05 and abs(a0 - area_circ) <= 0.005 * area_circ:
            tipo_entrada = f"circular Ø{wx0:.2f}"
        else:
            tipo_entrada = f"retangular/slot {wx0:.1f} x {wy0:.1f}"
        print(f"  Entrada em Z=0: {tipo_entrada} | área = {a0:.1f} mm²")
        r["entrada"] = tipo_entrada
        r["entrada_area_mm2"] = round(a0, 1)
        wx1, wy1, a1 = secao(canal, 1.0)
        print(f"     (em Z=1,0 mm a seção já é {wx1:.1f} x {wy1:.1f} = {a1:.0f} mm²)")
        r["secao_em_z1_mm"] = [round(wx1, 2), round(wy1, 2)]
    except Exception:
        pass
    z_land, comp_land = comprimento_land(canal, bb.zmax - bb.zmin)
    r["z_inicio_land"] = z_land
    r["comprimento_land_mm"] = round(comp_land, 2)
    print(f"  Início do land: Z = {z_land} mm | comprimento do land = {comp_land:.2f} mm")
    dpt, z_pico, pico = dp_total(canal, bb.zmax - bb.zmin)
    r["dp_estimado_1d_bar"] = round(dpt, 1)
    print(f"  ΔP 1D (geometria medida, lei das potências) = {dpt:6.1f} bar")
    if cfg["declarado"] and cfg["declarado"] in declarados:
        d = declarados[cfg["declarado"]]
        r["dp_declarado_bar"] = d["perda_carga_bar"]
        r["uniformidade_declarada_pct"] = d["uniformidade_velocidade_pct"]
        print(f"  ΔP declarado no relatório = {d['perda_carga_bar']} bar "
              f"(uniformidade {d['uniformidade_velocidade_pct']}%) -> razão medida/declarada "
              f"= {dpt / d['perda_carga_bar']:.2f}x")

    # tensão de cisalhamento no land (mesma seção e mesma vazão para todas as matrizes)
    tau, gdot = tau_parede(74.678, 1.5)
    r["tau_parede_land_kpa"] = round(tau, 1)
    print(f"  τ na parede do land (75x1,5; Q=15 cm³/s) = {tau:.1f} kPa "
          f"(γ̇_w = {gdot:.0f} 1/s)")
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    with open(os.path.join(DADOS, "dados_simulacao_reologica.json"), encoding="utf-8") as f:
        declarados = json.load(f)["resultados"]

    print("=" * 100)
    print("AUDITORIA DAS MATRIZES - GEOMETRIA MEDIDA NOS ARQUIVOS STEP x NÚMEROS DECLARADOS")
    print(f"Reologia usada nas contas: K = {K_PA_SN} Pa·s^n | n = {N_INDICE} | Q = {Q_MM3_S} mm³/s")
    print("=" * 100)

    res = [analisar(cfg, declarados) for cfg in MATRIZES]

    print("\n" + "=" * 100)
    print("QUADRO-RESUMO (comprimento do land x perda de carga)")
    print("=" * 100)
    print(f"{'Matriz':<32}{'funil até':>10}{'land':>8}{'ΔP 1D':>9}{'ΔP decl.':>10}{'razão':>8}")
    for r in res:
        d = r.get("dp_declarado_bar")
        razao = f"{r['dp_estimado_1d_bar'] / d:.2f}x" if d else "-"
        print(f"{r['matriz']:<32}{r.get('z_inicio_land') or '-':>10}"
              f"{r.get('comprimento_land_mm') or 0:>8.2f}{r['dp_estimado_1d_bar']:>9.1f}"
              f"{(d if d else '-'):>10}{razao:>8}")
    print("\nObservação: para a Matriz 1 (copo) o método 1D subestima muito, porque a perda")
    print("dominante é a contração brusca de 90° (parede cega), que exige modelo 2D/3D.")

    if args.json:
        destino = os.path.join(DADOS, "auditoria_matrizes_historicas.json")
        with open(destino, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "projeto": "Auditoria_Comparativa_Das_Matrizes",
                    "data": "2026-09-11",
                    "metodo": "Medição direta das seções dos STEP + lei das potências 1D "
                              "(escoamento desenvolvido) com K=18500 Pa.s^n, n=0,32, Q=15 cm3/s",
                    "limitacoes": "Modelo 1D não captura contração brusca de 90° nem perdas "
                                  "de entrada (Bagley); use para ordem de grandeza, não como CFD.",
                    "matrizes": res,
                },
                f,
                ensure_ascii=False,
                indent=2,
            )
        print(f"\nJSON salvo em {os.path.relpath(destino, RAIZ)}")


if __name__ == "__main__":
    main()
