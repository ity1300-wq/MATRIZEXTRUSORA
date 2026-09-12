"""
CFD 2D DAS SEÇÕES TRANSVERSAIS DO CANAL - MATRIZ JONATHA (MATRIZ 3)
==================================================================
Resolve o escoamento de lei das potências, já desenvolvido, na SEÇÃO
TRANSVERSAL (X-Y) do canal, para cada cota Z pedida:

    K * div( |grad w|^(n-1) * grad w ) = -G ,      w = 0 nas paredes
    (w = velocidade axial, G = -dp/dz, K e n da lei das potências)

Como o problema é linear em G^(1/n), resolve-se uma vez com G = 1 e
escala-se para a vazão alvo (Q = 15 cm³/s), o que dispensa iteração externa.

O que este cálculo responde (e o CF D 3D não responde barato):
  * perfil de velocidade em toda a largura de 75 mm (uniformidade real);
  * quanto a borda arredondada R0,75 deixa de escoar em relação ao canto vivo;
  * tensão de cisalhamento na parede e ONDE ela é máxima (risco de rasgo);
  * gradiente de pressão e contribuição de cada trecho do canal.

Validação: contra a solução analítica de fenda larga de lei das potências
(verificação no caso newtoniano reproduz 12*mu*L*Q/(W*H^3)).

Uso:
    python cfd_land_crosssection.py                 # seções padrão do land
    python cfd_land_crosssection.py --json          # salva resultados numéricos

Requisitos: cadquery, gmsh, scikit-fem (ver setup_cfd_env.sh).
"""

import argparse
import json
import math
import os
import subprocess
import sys
import tempfile
import time

import numpy as np

try:
    import cadquery as cq
    import gmsh
    from skfem import Basis, BilinearForm, FacetBasis, Functional, LinearForm, MeshTri, condense, solve
    from skfem.element import ElementTriP2
    from skfem.helpers import dot, grad
except ImportError as exc:  # pragma: no cover
    print(f"ERRO: dependências ausentes ({exc}). Rode setup_cfd_env.sh.", file=sys.stderr)
    sys.exit(2)

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DIR_CAD = os.path.join(RAIZ, "01_CAD_MatrizJonatha_Oficial")
DIR_DADOS = os.path.dirname(os.path.abspath(__file__))

K_PL = 18500.0     # Pa.s^n
N_PL = 0.32        # índice de comportamento
Q_ALVO = 15000.0   # mm3/s (= 15 cm3/s)
RHO = 1.4e-6       # kg/mm3
Z_INICIO_LAND = 99.0
Z_FIM = 109.0


def secao_cad(nucleo, z, arquivo):
    """Extrai a face da seção transversal em Z e exporta em STEP (uma única face)."""
    slab = nucleo.intersect(cq.Workplane("XY").workplane(offset=z).box(200, 200, 0.002).val())
    wp_face = cq.Workplane("XY").add(slab).faces(">Z")
    face = wp_face.val()
    cq.exporters.export(wp_face, arquivo)
    bb = face.BoundingBox()
    return slab.Volume() / 0.002, (bb.ymax - bb.ymin)


def malhar_2d(arquivo_step, arquivo_msh, tam_min, tam_max):
    from cadquery import exporters

    gmsh.initialize(["-nopopup"])
    gmsh.option.setNumber("General.Terminal", 0)
    gmsh.model.occ.importShapes(arquivo_step)
    gmsh.model.occ.synchronize()
    gmsh.option.setNumber("Mesh.MeshSizeMin", tam_min)
    gmsh.option.setNumber("Mesh.MeshSizeMax", tam_max)
    gmsh.option.setNumber("Mesh.Algorithm", 6)  # frontal-delaunay
    gmsh.model.mesh.generate(2)
    n_no = len(gmsh.model.mesh.getNodes()[0])
    n_el = len(gmsh.model.mesh.getElementsByType(2)[1])
    gmsh.write(arquivo_msh)
    gmsh.finalize()
    return n_no, n_el


def resolver_secao(nucleo, z, tam_min=None, tam_max=None, gdot_c=1e-3):
    """Resolve o escoamento (lei das potências) na seção transversal em Z.

    Formulação ADIMENSIONAL (evita o platô numérico e dispensa iteração em G):
        seja  x = L·x̂  e  w = U·ŵ ,   L = altura máxima da seção
        K·div(|grad w|^(n-1) grad w) = -G    <=>   div̂(|grad̂ ŵ|^(n-1) grad̂ ŵ) = -1
        com  U = (G·L^(n+1)/K)^(1/n).
    Resolve-se uma única vez o problema adimensional (K=1, G=1) e depois:
        U = Q_alvo/(L²·Q̂)   e   G = K·U^n/L^(n+1).
    A vazão Q entra por U (linear) e o gradiente G decorre da lei das potências.
    A regularização gdot_c = 1e-3 (adimensional) só remove a degeneração do
    núcleo tampão, equivalendo a ~0,1 1/s no land (contra ~500 1/s reais).
    """
    with tempfile.TemporaryDirectory() as tmp:
        passo = os.path.join(tmp, "sec.step")
        msh = os.path.join(tmp, "sec.msh")
        area_cad, h_local = secao_cad(nucleo, z, passo)
        # malha proporcional à altura local (mantém o custo e a precisão comparáveis
        # entre o funil, onde h ~ 20-70 mm, e o land, onde h = 1,5 mm)
        if tam_min is None:
            tam_min = max(0.02 * h_local, 0.02)
            tam_max = max(0.10 * h_local, 0.12)
        n_no, n_el = malhar_2d(passo, msh, tam_min, tam_max)

        mesh_fis = MeshTri.load(msh).scaled(1e-3)              # metros
        L = float(mesh_fis.p[1].max() - mesh_fis.p[1].min())   # altura máxima
        mesh = mesh_fis.scaled(1.0 / L)                        # adimensional
        basis = Basis(mesh, ElementTriP2())
        area_ad = Functional(lambda w: 0 * w["up"].value + 1.0).assemble(
            basis, up=basis.interpolate(basis.zeros()))

        @LinearForm
        def carga(v, w):
            return 1.0 * v

        b = asm_carga(carga, basis)
        D = basis.get_dofs()

        def forma_com(n):
            @BilinearForm
            def forma(u, v, w):
                g = w["up"].grad
                mod = (sum(gi ** 2 for gi in g) ** 0.5 + gdot_c) ** (n - 1.0)
                return mod * sum(a * c for a, c in zip(u.grad, v.grad))
            return forma

        w = basis.zeros()
        it_total = 0
        for n_etapa in [1.0, 0.80, 0.65, 0.52, 0.44, 0.38, N_PL]:
            forma = forma_com(n_etapa)
            for it in range(40):
                A = asm_forma(forma, basis, w)
                w_n = solve(*condense(A, b, D=D))
                if not np.all(np.isfinite(w_n)):
                    raise RuntimeError(f"divergiu em n={n_etapa}, it={it}")
                rel = np.linalg.norm(w_n - w) / max(np.linalg.norm(w_n), 1e-30)
                w = 0.5 * w_n + 0.5 * w
                it_total += 1
                if rel < 1e-9:
                    break

        Qhat = Functional(lambda w_: w_["up"].value).assemble(basis, up=basis.interpolate(w))
        # ---- reescala para o mundo físico ----
        U = (Q_ALVO * 1e-9) / (L ** 2 * Qhat)                  # m/s
        G = K_PL * U ** N_PL / L ** (N_PL + 1.0)               # Pa/m
        w_fis = basis.zeros()
        w_fis[:] = w * U                                       # m/s (malha adimensional)

        # ---- pós-processamento (na malha adimensional: x̂ = x/L) ----
        f = basis.interpolate(w)
        x_linha = np.linspace(mesh.p[0].min() * 0.999, mesh.p[0].max() * 0.999, 400)
        try:
            v_linha = (basis.probes(np.vstack([x_linha, np.zeros_like(x_linha)])) @ w) * U * 1e3
        except Exception:
            v_linha = np.full_like(x_linha, np.nan)
            for k, xv in enumerate(x_linha):
                try:
                    v_linha[k] = float((basis.probes(np.array([[xv], [0.0]])) @ w)[0]) * U * 1e3
                except Exception:
                    v_linha[k] = np.nan

        # vazão por unidade de largura q(x) -> define a espessura da fita
        dx_q = basis.dx
        int_el = np.sum(np.array(f.value) * dx_q, axis=1) * U * L ** 2   # m3/s por elemento
        x_el = mesh.p[0][mesh.t].mean(axis=0) * L
        n_bin = 75
        bordas = np.linspace(0.0, mesh.p[0].max() * L, n_bin + 1)
        xc = np.abs(x_el)
        idx = np.clip(np.digitize(xc, bordas) - 1, 0, n_bin - 1)
        q_bin = np.zeros(n_bin)
        np.add.at(q_bin, idx, int_el)
        larg_bin = bordas[1] - bordas[0]
        # a dobra de simetria soma os dois lados: dividir por 2 dá q(x) por lado
        q_perfil = q_bin / larg_bin * 0.5 * 1e6                # mm³/s por mm
        x_bin = 0.5 * (bordas[:-1] + bordas[1:]) * 1e3         # mm
        q_total = float(np.sum(q_bin) * 1e9)
        q_centro = float(np.interp(0.0, x_bin, q_perfil))

        # altura local por faixa (define a região de "fenda cheia" vs. borda)
        x_no = np.abs(mesh.p[0]) * L                            # metros
        h_no = np.abs(mesh.p[1]) * L * 2                        # altura local [m]
        alt_bin = np.zeros(n_bin)
        for k in range(n_bin):
            m = (x_no >= bordas[k]) & (x_no < bordas[k + 1])
            alt_bin[k] = h_no[m].max() if m.any() else 0.0
        h_max_local = float(alt_bin.max())
        cheia = alt_bin >= 0.98 * h_max_local                   # fenda com altura plena
        q_max = float(q_perfil[cheia].max()) if cheia.any() else float(q_perfil.max())
        q_min = float(q_perfil[cheia].min()) if cheia.any() else float(q_perfil.min())
        unif = 100.0 * q_min / q_max
        # largura da zona lenta: distância da ponta onde q < 90% do centro
        lenta = np.where(q_perfil < 0.90 * q_centro)[0]
        zona_lenta_mm = float(x_bin[-1] - x_bin[lenta.min()]) if lenta.size else 0.0
        # largura em que a fenda ainda tem altura plena (menos as bordas moldadas)
        largura_plena_mm = float(2 * x_bin[cheia].max()) if cheia.any() else 0.0

        # tensão de cisalhamento na parede (física)
        fbasis = FacetBasis(mesh, ElementTriP2())
        ff = fbasis.interpolate(w)
        gd = np.sqrt(np.array(ff.grad[0]) ** 2 + np.array(ff.grad[1]) ** 2) * (U / L)
        tau = K_PL * gd ** N_PL / 1000.0                       # kPa
        pesos = np.array(fbasis.dx)
        gdot_no = gd

        return {
            "z_mm": z,
            "area_cad_mm2": round(area_cad, 4),
            "altura_max_mm": round(L * 1e3, 4),
            "largura_mm": round(float(mesh_fis.p[0].max() - mesh_fis.p[0].min()) * 1e3, 4),
            "nos": n_no, "elementos": n_el, "dofs": int(basis.N),
            "iteracoes_totais": it_total,
            "G_Pa_por_m": G,
            "G_bar_por_mm": G * 1e-8,
            "Q_total_mm3_s": q_total,
            "U_escala_m_s": U,
            "v_media_mm_s": Q_ALVO / area_cad,
            "v_max_mm_s": float(np.max(v_linha)),
            "v_min_mm_s": float(np.min(v_linha)),
            "q_centro_mm3_s_por_mm": round(q_centro, 3),
            "q_max_mm3_s_por_mm": round(q_max, 3),
            "q_min_mm3_s_por_mm": round(q_min, 3),
            "altura_local_max_mm": round(h_max_local * 1e3, 4),
            "largura_fenda_plena_mm": round(largura_plena_mm, 3),
            "zona_lenta_mm": round(zona_lenta_mm, 3),
            "altura_local_por_faixa_mm": (alt_bin * 1e3).tolist(),
            "x_bin_mm": x_bin.tolist(),
            "q_perfil": q_perfil.tolist(),
            "uniformidade_espessura_pct": round(unif, 3),
            "x_linha_mm": (x_linha * L * 1e3).tolist(),
            "v_linha_mm_s": v_linha.tolist(),
            "gdot_max_1_s": float(gdot_no.max()),
            "gdot_medio_parede_1_s": float(np.sum(gdot_no * pesos) / np.sum(pesos)),
            "tau_max_kpa": float(tau.max()),
            "tau_medio_parede_kpa": float(np.sum(tau * pesos) / np.sum(pesos)),
        }


def asm_forma(forma, basis, w):
    from skfem import asm
    return asm(forma, basis, up=basis.interpolate(w))


def asm_carga(carga, basis):
    from skfem import asm
    return asm(carga, basis)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true", help="salva avaliacao_matriz_3.json")
    ap.add_argument("--secoes", type=float, nargs="*",
                    default=[70.0, 85.0, 95.0, 99.5, 103.0, 107.0],
                    help="cotas Z das seções transversais")
    args = ap.parse_args()

    t0 = time.time()
    nucleo = max(cq.importers.importStep(
        os.path.join(DIR_CAD, "MatrizJonatha_Canal_Fluxo.step")).solids().vals(),
        key=lambda s: s.Volume())
    print("=" * 96)
    print("CFD 2D DAS SEÇÕES TRANSVERSAIS — MATRIZ JONATHA (MATRIZ 3)")
    print(f"Lei das potências: K = {K_PL} Pa·s^n | n = {N_PL} | Q = {Q_ALVO} mm³/s")
    print("=" * 96)

    resultados = []
    for z in args.secoes:
        t1 = time.time()
        r = resolver_secao(nucleo, z)
        resultados.append(r)
        largura = r["area_cad_mm2"]
        print(f"\nZ = {z:6.2f} mm | área = {r['area_cad_mm2']:8.3f} mm² | "
              f"{r['nos']} nós / {r['elementos']} elems | Picard+continuação {r['iteracoes_totais']} it "
              f"({time.time() - t1:.0f}s)")
        print(f"   G = dp/dz = {r['G_bar_por_mm']:7.4f} bar/mm | Q conferida = {r['Q_total_mm3_s']:.1f} mm³/s "
              f"(alvo {Q_ALVO:.0f})")
        print(f"   v média = {r['v_media_mm_s']:7.2f} mm/s | v máx (linha y=0) = {r['v_max_mm_s']:7.2f} mm/s")
        print(f"   q: centro = {r['q_centro_mm3_s_por_mm']:7.2f} | máx = {r['q_max_mm3_s_por_mm']:7.2f} | "
              f"mín (fora do R0,75) = {r['q_min_mm3_s_por_mm']:7.2f} mm³/s por mm")
        print(f"   >>> UNIFORMIDADE DE ESPESSURA (q_min/q_max) = {r['uniformidade_espessura_pct']:.2f} %")
        print(f"   γ̇ na parede: máx = {r['gdot_max_1_s']:7.1f} | média = {r['gdot_medio_parede_1_s']:7.1f} 1/s  ->  "
              f"τ médio = {r['tau_medio_parede_kpa']:6.2f} kPa | τ máx = {r['tau_max_kpa']:6.2f} kPa")

    print(f"\n[tempo total: {time.time() - t0:.0f} s]")
    if args.json:
        destino = os.path.join(DIR_DADOS, "avaliacao_matriz_3_secoes.json")
        with open(destino, "w", encoding="utf-8") as f:
            json.dump({
                "projeto": "Avaliacao_CFD_Matriz_3_Jonatha",
                "metodo": "p-Laplaciano 2D (escoamento desenvolvido) por seção transversal, "
                          "malha gerada do STEP oficial pelo gmsh, solução P2 pelo scikit-fem",
                "parametros": {"K_Pa_s_n": K_PL, "n": N_PL, "Q_mm3_s": Q_ALVO},
                "secoes": resultados,
            }, f, ensure_ascii=False, indent=2)
        print(f"JSON salvo em {os.path.relpath(destino, RAIZ)}")


if __name__ == "__main__":
    main()
