"""
ESTUDO DE ALÍVIO DE BORDA (EDGE RELIEF) NA FENDA DE SAÍDA - MATRIZ 3
====================================================================
Problema medido no CFD: a fenda reta de 75,00 x 1,50 mm entrega ~50% da
vazão nos últimos ~0,6 mm de cada ponta (atrito da parede lateral). Como a
espessura da fita é proporcional à vazão por unidade de largura q(x), as
bordas saem finas - justamente onde o R0,75 deveria garantir espessura para
controle de campo elétrico.

Este script avalia a correção clássica de matrizes planas: o ALÍVIO DE BORDA,
um aumento local da abertura da fenda nas proximidades das pontas
(geometria paramétrica, sem tocar o modelo aprovado):

    |x| <= x0                -> abertura plena 1,50 mm
    x0 < |x| <= 36,75 - d    -> rampa linear de 1,50 para 1,50 + 2d  mm
    ponta                    -> semicírculo de raio 0,75 + d  (borda da fita)

O contorno externo permanece com 75,00 mm exatos (o centro do semicírculo
recua d, compensando o raio maior). Para cada alívio d avalia-se:
  * uniformidade de espessura q_min/q_max ao longo da largura;
  * ganho de vazão nos últimos 2 mm (onde ocorre o afinamento);
  * custo em perda de carga (G e dP).

Uso:  python cfd_edge_relief.py [--json] [--alivios 0 25 50 75 100]
"""

import argparse
import json
import os
import sys
import tempfile
import time

import numpy as np

try:
    import gmsh
    from skfem import Basis, BilinearForm, FacetBasis, Functional, LinearForm, MeshTri, condense, solve
    from skfem.element import ElementTriP2
except ImportError as exc:  # pragma: no cover
    print(f"ERRO: dependências ausentes ({exc}). Rode setup_cfd_env.sh.", file=sys.stderr)
    sys.exit(2)

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DIR_DADOS = os.path.dirname(os.path.abspath(__file__))

K_PL, N_PL, Q_ALVO = 18500.0, 0.32, 15000.0     # Pa.s^n ; - ; mm3/s
MEIA_LARGURA = 37.5        # mm
RAIO_BORDA = 0.75          # mm (R0,75 nominal)
MEIA_ESPESSURA = 0.75      # mm (1,50 / 2)
X0_RAMPA = 30.0            # mm: início da rampa de alívio
TAM_MALHA = None           # None = malha graduada pela regra do cfd_land_crosssection.py
DIAGNOSTICO = False


def _sem_repetidos(pts, tol=1e-9):
    """Remove pontos consecutivos coincidentes e o fechamento duplicado."""
    saida = []
    for pt in pts:
        if not saida or (abs(pt[0] - saida[-1][0]) > tol or abs(pt[1] - saida[-1][1]) > tol):
            saida.append(pt)
    if len(saida) > 1 and abs(saida[0][0] - saida[-1][0]) < tol and abs(saida[0][1] - saida[-1][1]) < tol:
        saida.pop()
    return saida


def contorno(alivio_mm, n_rampa=60, n_arco=40):
    """Contorno fechado da seção (mm), com alívio d nas pontas.

    Abertura plena 1,50 mm em |x| <= X0_RAMPA; rampa linear até 1,50 + 2d em
    |x| = x_c; semicírculo de raio r = 0,75 + d centrado em x_c = 37,5 - r
    (mantém a largura externa em exatamente 75,00 mm).
    """
    d = float(alivio_mm)
    r = RAIO_BORDA + d
    x_c = MEIA_LARGURA - r
    a = MEIA_ESPESSURA + d          # = r  (continuidade entre rampa e ponta)

    topo_rampa = []
    for i in range(1, n_rampa + 1):
        t = i / n_rampa
        topo_rampa.append((X0_RAMPA + t * (x_c - X0_RAMPA), MEIA_ESPESSURA + t * d))

    arco = []
    for i in range(0, n_arco + 1):
        th = np.pi / 2 - np.pi * i / n_arco          # +90° -> -90°
        arco.append((x_c + r * np.cos(th), r * np.sin(th)))

    # contorno fechado da LARGURA COMPLETA (x de -37,5 a +37,5 mm), como no
    # script já validado: metade direita + sua imagem espelhada em x
    meia = ([(0.0, MEIA_ESPESSURA)] + topo_rampa + arco +
            [(x, -y) for (x, y) in topo_rampa[::-1]] + [(0.0, -MEIA_ESPESSURA)])
    meia = _sem_repetidos(meia)
    esquerda = [(-x, -y) for (x, y) in meia]
    contorno = _sem_repetidos(meia + esquerda[1:-1])
    return contorno, x_c, r, a


def resolver(pts, tam=TAM_MALHA, gdot_c=1e-3, w_inicial=None, verboso=False, alivio_mm=0.0):
    """Resolve a seção paramétrica (adimensionalizada) e devolve os indicadores."""
    with tempfile.TemporaryDirectory() as tmp:
        # geometria direto no gmsh (sem STEP): pontos -> linhas -> superfície
        gmsh.initialize(["-nopopup"])
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.model.add("sec")
        occ = gmsh.model.occ
        seq = [occ.addPoint(x, y, 0.0) for (x, y) in pts]
        linhas = [occ.addLine(seq[i], seq[i + 1]) for i in range(len(seq) - 1)]
        linhas.append(occ.addLine(seq[-1], seq[0]))
        surf = occ.addPlaneSurface([occ.addCurveLoop(linhas)])
        occ.synchronize()
        # malha graduada: mesma regra do script já validado (cfd_land_crosssection.py)
        h_local = 2 * MEIA_ESPESSURA + 2 * alivio_mm
        tam_min = 0.02 * h_local if tam is None else tam
        tam_max = max(0.10 * h_local, 0.12) if tam is None else tam * 2
        gmsh.option.setNumber("Mesh.MeshSizeMin", tam_min)
        gmsh.option.setNumber("Mesh.MeshSizeMax", tam_max)
        gmsh.option.setNumber("Mesh.Algorithm", 6)
        gmsh.model.mesh.generate(2)
        n_no = len(gmsh.model.mesh.getNodes()[0])
        n_el = len(gmsh.model.mesh.getElementsByType(2)[1])
        msh = os.path.join(tmp, "s.msh")
        gmsh.write(msh)
        gmsh.finalize()

        mesh_fis = MeshTri.load(msh).scaled(1e-3)
        L = float(mesh_fis.p[1].max() - mesh_fis.p[1].min())   # altura total da fenda
        mesh = mesh_fis.scaled(1.0 / L)
        basis = Basis(mesh, ElementTriP2())

        @LinearForm
        def carga(v, w):
            return 1.0 * v

        b = asm_c(carga, basis)
        D = basis.get_dofs()

        def forma_com(n):
            @BilinearForm
            def forma(u, v, w):
                g = w["up"].grad
                mod = (sum(gi ** 2 for gi in g) ** 0.5 + gdot_c) ** (n - 1.0)
                return mod * sum(cc * dd for cc, dd in zip(u.grad, v.grad))
            return forma

        # continuação: do caso newtoniano (n=1) até n=0,32. Nos casos seguintes,
        # reaproveita-se a solução anterior (a geometria muda só alguns µm).
        etapas = [1.0, 0.75, 0.55, 0.42, 0.35, N_PL]
        w = basis.zeros()
        for n_etapa in etapas:
            f = forma_com(n_etapa)
            for it in range(45):
                A = asm_f(f, basis, w)
                w_n = solve(*condense(A, b, D=D))
                rel = np.linalg.norm(w_n - w) / max(np.linalg.norm(w_n), 1e-30)
                w = 0.5 * w_n + 0.5 * w
                if rel < 1e-8:
                    break
            if verboso:
                print(f"      n={n_etapa:.2f}: {it + 1} it, residuo {rel:.1e}")

        Qhat = Functional(lambda w_: w_["up"].value).assemble(basis, up=basis.interpolate(w))
        U = (Q_ALVO * 1e-9) / (L ** 2 * Qhat)
        G = K_PL * U ** N_PL / L ** (N_PL + 1.0)
        if DIAGNOSTICO:
            print(f"   [diag] L={L*1e3:.4f} mm | y_max={float(mesh_fis.p[1].max())*1e3:.4f} mm | "
                  f"x_max={float(mesh_fis.p[0].max())*1e3:.4f} mm | Qhat={Qhat:.6f} | U={U:.4f} m/s | "
                  f"G={G*1e-8:.4f} bar/mm")

        ff = basis.interpolate(w)
        int_el = np.sum(np.array(ff.value) * basis.dx, axis=1) * U * L ** 2
        x_el = mesh.p[0][mesh.t].mean(axis=0) * L
        n_bin = 150
        bordas = np.linspace(0.0, mesh.p[0].max() * L, n_bin + 1)
        idx = np.clip(np.digitize(np.abs(x_el), bordas) - 1, 0, n_bin - 1)
        q_bin = np.zeros(n_bin)
        np.add.at(q_bin, idx, int_el)
        larg = bordas[1] - bordas[0]
        q = q_bin / larg * 0.5 * 1e6                      # mm3/s por mm (dom. completo)
        x_bin = 0.5 * (bordas[:-1] + bordas[1:]) * 1e3    # mm
        q_tot = float(np.sum(q_bin) * 1e9)
        q_centro = float(np.interp(0.0, x_bin, q))

        # espessura equivalente da fita (proporcional a q) e indicadores de borda
        esp = q / q_centro * (2 * MEIA_ESPESSURA)         # mm (nominal no centro)
        # uniformidade no NÚCLEO PLANO (|x| <= 30 mm, antes da rampa de borda)
        sel_nucleo = x_bin <= 30.0
        unif = 100.0 * q[sel_nucleo].min() / q[sel_nucleo].max()
        # indicadores de borda: espessura relativa no fim da fenda
        sel_borda = x_bin >= (MEIA_LARGURA - 2.0)
        esp_min_borda = float(esp[sel_borda].min())
        esp_em_36mm = float(np.interp(36.0, x_bin, esp))
        esp_em_37mm = float(np.interp(37.0, x_bin, esp))
        esp_max = float(esp[sel_nucleo].max())

        fb = FacetBasis(mesh, ElementTriP2())
        gd = np.sqrt(np.array(fb.interpolate(w).grad[0]) ** 2 +
                     np.array(fb.interpolate(w).grad[1]) ** 2) * (U / L)
        tau = K_PL * gd ** N_PL / 1000.0
        pesos = np.array(fb.dx)
        return {
            "w_adimensional": w,
            "malha_mm": tam,
            "malha_min_max_mm": [round(tam_min, 4), round(tam_max, 4)],
            "area_adimensional": None,
            "nos": n_no, "elementos": n_el,
            "x_bin_mm": x_bin.tolist(), "q_perfil": q.tolist(),
            "esp_perfil_mm": esp.tolist(),
            "uniformidade_nucleo_pct": round(unif, 2),
            "espessura_em_36mm": round(esp_em_36mm, 4),
            "espessura_em_37mm": round(esp_em_37mm, 4),
            "espessura_min_borda_mm": round(esp_min_borda, 4),
            "espessura_max_mm": round(esp_max, 4),
            "G_bar_por_mm": G * 1e-8,
            "dP_para_8_5mm_bar": G * 1e-8 * 8.5,
            "tau_medio_kpa": float(np.sum(tau * pesos) / np.sum(pesos)),
            "Q_conferida": q_tot,
        }


def asm_f(f, basis, w):
    from skfem import asm
    return asm(f, basis, up=basis.interpolate(w))


def asm_c(c, basis):
    from skfem import asm
    return asm(c, basis)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--diag", action="store_true")
    ap.add_argument("--agregar", nargs="*", default=None,
                    help="funde vários JSONs de casos em avaliacao_matriz_3_alivio_borda.json")
    ap.add_argument("--saida", default="avaliacao_matriz_3_alivio_borda.json",
                    help="arquivo JSON de saída (um por execução)")
    ap.add_argument("--alivios", type=float, nargs="*", default=[0.0, 25.0, 50.0, 75.0, 100.0, 150.0])
    args = ap.parse_args()
    global DIAGNOSTICO
    DIAGNOSTICO = bool(args.diag)

    if args.agregar:
        import glob
        casos, arquivos = [], []
        for padrao in args.agregar:
            arquivos.extend(sorted(glob.glob(padrao)))
        if not arquivos:
            print("nenhum arquivo encontrado para agregar", file=sys.stderr)
            sys.exit(2)
        for arq in arquivos:
            with open(arq, encoding="utf-8") as fh:
                casos.extend(json.load(fh)["casos"])
        casos.sort(key=lambda c: c["alivio_um"])
        with open(arquivos[0], encoding="utf-8") as fh:
            ref = json.load(fh)
        ref["casos"] = casos
        ref["observacao"] = ("cada caso foi resolvido em um processo separado do gmsh "
                             "(o OCC corrompe o estado entre geometrias no mesmo processo); "
                             "apenas os campos escalares são preservados na agregação")
        for c in casos:
            for k in ("x_bin_mm", "q_perfil", "esp_perfil_mm", "w_adimensional"):
                c.pop(k, None)
        destino = os.path.join(DIR_DADOS, args.saida)
        with open(destino, "w", encoding="utf-8") as fh:
            json.dump(ref, fh, ensure_ascii=False, indent=2)
        print(f"{len(casos)} casos agregados em {os.path.relpath(destino, os.path.dirname(DIR_DADOS))}")
        return

    print("=" * 100)
    print("ESTUDO DE ALÍVIO DE BORDA NA FENDA DE SAÍDA (75,00 x 1,50 mm, R0,75)")
    print(f"Rampa de alívio a partir de |x| = {X0_RAMPA} mm | malha graduada | Q = {Q_ALVO} mm³/s")
    print("=" * 100)
    print(f"{'alívio':>8} {'uniform.':>9} {'esp. mín':>9} {'q centro':>9} {'G':>10} {'dP(8,5mm)':>10} {'τ médio':>9}")
    print(f"{'[µm]':>8} {'[%]':>9} {'[mm]':>9} {'[mm³/s/mm]':>9} {'[bar/mm]':>10} {'[bar]':>10} {'[kPa]':>9}")

    resultados = []
    w_ant = None

    t0 = time.time()
    for d in args.alivios:
        pts, x_c, r_c, a = contorno(d * 1e-3)        # entrada da CLI em µm
        r = resolver(pts, verboso=True, alivio_mm=d * 1e-3)
        w_ant = r.pop("w_adimensional", None)
        r["alivio_um"] = d
        r["raio_borda_mm"] = round(r_c, 4)
        resultados.append(r)
        print(f"{d:8.0f} {r['uniformidade_nucleo_pct']:9.2f} {r['espessura_min_borda_mm']:9.3f} "
              f"{r['q_perfil'][len(r['q_perfil'])//2]:9.2f} {r['G_bar_por_mm']:10.4f} "
              f"{r['dP_para_8_5mm_bar']:10.2f} {r['tau_medio_kpa']:9.2f}   ({time.time()-t0:.0f}s)")

    if args.json:
        destino = os.path.join(DIR_DADOS, args.saida)
        with open(destino, "w", encoding="utf-8") as f:
            json.dump({
                "projeto": "Avaliacao_Alivio_De_Borda_Matriz_3",
                "metodo": ("p-Laplaciano 2D adimensionalizado por seção transversal; "
                           "geometria paramétrica com rampa de alívio a partir de "
                           f"|x| = {X0_RAMPA} mm; malha {TAM_MALHA} mm"),
                "parametros": {"K_Pa_s_n": K_PL, "n": N_PL, "Q_mm3_s": Q_ALVO},
                "casos": resultados,
            }, f, ensure_ascii=False, indent=2)
        print(f"\nJSON salvo em {os.path.relpath(destino, RAIZ)}")


if __name__ == "__main__":
    main()
