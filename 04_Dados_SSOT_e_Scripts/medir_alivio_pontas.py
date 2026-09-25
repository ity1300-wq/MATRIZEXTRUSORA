# -*- coding: utf-8 -*-
"""Mede, direto no STEP, se a matriz tem ALIVIO nas pontas da fenda ou não.

Por que isto existe: o objetivo primordial declarado e' o serrilhado nas duas bordas da manta, e o
serrilhado e' falta de material chegando nas pontas. Todo o resto (espessura, igualizacao, refrigera-
cao) e' meio. Para saber o que uma matriz nova precisa ter, primeiro precisa saber o que as existentes
tem - e isso nao se discute, se mede.

Metodo (sem boolemana frageril, sem malha): varredura de ponto-em-solido (`Shape.isInside`).
Para cada estacao `u` ao longo da fenda e cada profundidade `d` atras da face de saida, mede a
ABERTURA da fenda naquele ponto. Land reto = mesma abertura em toda a profundidade. Alivio = a
abertura cresce, ou o land encurta, conforme se vai do centro para as pontas.

Eixo da fenda (x ou y) e' detectado, nao assumido: o eixo certo e' aquele em que a boca e' fina
(~1,5 mm) e comprida (>= 70 mm).

Uso:  python3 04_Dados_SSOT_e_Scripts/medir_alivio_pontas.py [--json saida.json]
Saida: tabela por matriz + veredito `TEM ALIVIO` / `Nao tem alivio`, e o numero que a linha dele
       cobra (queda de resistencia necessaria nas pontas) a partir do perfil medido por ele.

Atencao: o "land" impresso aqui e' limitado pela lista PROFUNDIDADES (ate 15 mm atras da boca) - serve
para comparar matrizes entre si, nao para cotar. O comprimento exato de land de cada matriz, com o
cone de entrada da Gedeon descontado, sai de
`04_Dados_SSOT_e_Scripts/verificar_revaloracao_serrilhado_2026_09_25.py`, que e' o que confere o
documento `REVALORACAO_FOCO_SERRILHADO_2026-09-25.md` numero por numero.
"""
import json, math, sys, os

import cadquery as cq

RHO_MAST = 1.25e-3          # g/mm3 - literatura do repo (masti_epdm_reologia.py)
N_LEI = 0.32                # expoente da lei-potencia do mastique (SSOT)
Q_MM3_S = 15000.0           # vazao de referencia do pacote 3D
GRAD_BAR_PER_MM = 2.187     # gradiente do land, metodo 1D do projeto (PRP-0002)
FOLGA_NOMINAL = 1.500
LARGURA = 75.00

DIE_FILES = [
    ("Copo  (a que esta na maquina hoje)",
     "06_CAD_Cabecote_EX-030/STEP/Cabecote_EX-030_com_Matriz_Copo.step", "die"),
    ("Jonatha v30 (pacote publicado)",
     "06_CAD_Cabecote_EX-030/STEP/Cabecote_EX-030_com_Matriz_Jonatha_v30.step", "die"),
    ("Jonatha v29",
     "07_CAD_Matrizes/Matriz_Jonatha_v29_OFICIAL/matrizJonathaV29.step", "only"),
    ("Jonatha v27 (pecas A+B: usa o conjunto do cabecote)",
     "06_CAD_Cabecote_EX-030/STEP/Cabecote_EX-030_com_Matriz_Jonatha_v27.step", "die"),
    ("Gedeon CERTA (a que ele diz que da certo)",
     "07_CAD_Matrizes/Matriz_Gedeon_Certa/matrizGedeonCerta.step", "only"),
    ("Gedeon entregue (historica)",
     "07_CAD_Matrizes/Matriz_Gedeon_Entregue_HISTORICA/MatrizGedeon.step", "only"),
    ("Matriz Desenvolvimento (historica)",
     "07_CAD_Matrizes/Matriz_Desenvolvimento_HISTORICA/matriz3.step", "only"),
]
ESTACOES = [0.0, 18.75, 30.00, 36.60]      # centro, meia largura, perto da ponta, na ponta
PROFUNDIDADES = [0.20, 1.00, 2.00, 3.00, 5.00, 7.00, 8.50, 10.00, 12.00, 15.00]


def pick_solid(path, mode):
    """die = o solido menor da montagem; only = o unico/maior solido do arquivo."""
    if not os.path.exists(path):
        return None, "arquivo nao existe"
    S = list(cq.importers.importStep(path).solids().vals())
    if not S:
        return None, "sem solidos"
    if mode == "die":
        return min(S, key=lambda s: s.Volume()), ""
    return max(S, key=lambda s: s.Volume()), ""


def detect_axis(die):
    """Retorna ('x'|'y', zmax_da_saida). A boca: fina na perpendicular, comprida ao longo."""
    bb = die.BoundingBox()
    best = None
    for axis in ("x", "y"):
      for ztest in (bb.zmax - 0.20, bb.zmax - 2.00, bb.zmax - 3.00, bb.zmin + 0.20):
            gap = _gap(die, axis, 0.0, ztest)
            if gap is None or not (1.20 <= gap <= 1.80):
                continue
            # comprimento: ate onde a boca continua fina ao longo do eixo
            L = 0.0
            u = 0.0
            while u < 55.0:
                g = _gap(die, axis, u, ztest)
                if g is None or g > 3.00:
                    break
                L = u
                u += 1.0
            # L e' a MEIA largura da fenda: 37,5 para uma fenda de 75,00
            score = L if L >= 30.0 else -1.0
            if best is None or score > best[2]:
                best = (axis, bb.zmax, score)
    if best is None:
        return None, None
    return best[0], best[1]


def _at(die, axis, u, s, z_ref, dz):
    """Ponto (u ao longo da fenda, s na perpendicular), a dz de profundidade atras da face."""
    z = z_ref - dz
    if axis == "x":
        return die.isInside(cq.Vector(u, s, z))
    return die.isInside(cq.Vector(s, u, z))


def _gap(die, axis, u, z_abs):
    """Abertura da fenda na estacao u, na cota absoluta z_abs (varre a perpendicular)."""
    step = 0.02
    # o centro da boca e' o eixo; se tiver material ali, nao ha fenda naquele ponto
    def arm(sign):
        s = 0.0
        if _at(die, axis, u, 0.0, z_abs, 0.0):
            return None
        while s < 12.0:
            if _at(die, axis, u, sign * s, z_abs, 0.0):
                return s
            s += step
        return None
    a = arm(+1.0)
    b = arm(-1.0)
    if a is None or b is None:
        return None
    return a + b


def gap_at_depth(die, axis, zmax_out, u, d):
    return _gap(die, axis, u, zmax_out - d)


def perfil_along_slot(die, axis, zmax_out, u):
    """Abertura em cada profundidade; None = sem vazao ali (acabou a boca / virou parede)."""
    return {("d=%.2f" % d): gap_at_depth(die, axis, zmax_out, u, d) for d in PROFUNDIDADES}


def land_length(die, axis, zmax_out, u):
    """Ultima profundidade em que a abertura ainda e' a da boca (+5%): o land paralelo.

    Se atras da boca houver janela de alivio, a abertura salta e o land 'paralelo' para de
    crescer antes do fim do corpo - e e' isso que diferencia matriz com recurso de matriz cega.
    """
    g0 = gap_at_depth(die, axis, zmax_out, u, 0.20)
    if g0 is None:
        return None, None
    last = 0.20
    for d in PROFUNDIDADES:
        g = gap_at_depth(die, axis, zmax_out, u, d)
        if g is None or g > 1.06 * g0:
            break
        last = d
    return last, g0


# ---- o numero que a linha dele cobra ------------------------------------------------
def queda_resistencia_necessaria(perfil_medido):
    """Do perfil de espessura (que e' vazao local, porque a manta e' um solido so) para a
    queda de resistencia que igualaria as pontas. Lei: q ~ (1/R)^(1/n), 1/n = 3,125."""
    tmax = max(perfil_medido)
    out = []
    for t in perfil_medido:
        k = tmax / t
        out.append(k ** (-N_LEI))          # R_ponta / R_centro necessario
    return out


def main():
    want_json = "--json" in sys.argv
    out_json = {}
    print("=" * 78)
    print("ALIVIO NAS PONTAS - medido no STEP por varredura de ponto em solido")
    print("(abertura da fenda em mm, a cada profundidade atras da face de saida)")
    print("=" * 78)
    for tag, path, mode in DIE_FILES:
        die, err = pick_solid(path, mode)
        if die is None:
            print("\n%-40s  PULA: %s" % (tag, err))
            continue
        axis, zout = detect_axis(die)
        if axis is None:
            print("\n%-40s  NAO ACHOU boca de 1,5 com >=60 mm (talvez nao seja matriz de fenda)" % tag)
            continue
        zmax = zout
        lin = []
        lands = {}
        for u in ESTACOES:
            L, g0 = land_length(die, axis, zmax, u)
            lands[u] = L
            prof = perfil_along_slot(die, axis, zmax, u)
            lin.append((u, g0, L, prof))
        print("\n%-40s  eixo da fenda: %s   face de saida Z=%.2f" % (tag, axis, zmax))
        print("   %-12s %10s %12s   %s" % ("estacao", "boca mm", "land mm", "abertura por profundidade atras da boca"))
        for u, g0, L, prof in lin:
            s = "  ".join("%s:%s" % (k.split('=')[1], ("%.2f" % v) if v is not None else "--")
                          for k, v in prof.items())
            print("   u=%-9.2f %10s %12s   %s" % (u, ("%.3f" % g0) if g0 else "--",
                                                  ("%.2f" % L) if L else "--", s))
        c = lands.get(0.0)
        p = lands.get(36.60)
        vered = "sem dados"
        if c and p:
            vered = ("TEM ALIVIO: land das pontas %.2f mm vs centro %.2f mm" % (p, c)) if (c - p) >= 0.50 \
                else "NAO TEM ALIVIO: land igual no centro e nas pontas (%.2f vs %.2f)" % (c, p)
        print("   >>> %s" % vered)
        out_json[tag] = {"eixo": axis, "z_saida": zout,
                         "land_por_estacao_mm": {("%g" % k): v for k, v in lands.items()},
                         "veredito": vered}

    print("\n" + "=" * 78)
    print("O QUE O PERFIL DELE MANDA FAZER (lei-potencia n = %.2f, 1/n = %.3f)" % (N_LEI, 1 / N_LEI))
    print("=" * 78)
    for nome, perfil in [("1a medicao (paquimetro)", [1.50, 2.00, 2.57, 1.80, 1.50]),
                         ("2a medicao (paquimetro)", [1.50, 2.50, 2.50, 2.00, 1.50])]:
        r = queda_resistencia_necessaria(perfil)
        print("  %s: q_ponta/q_centro = %.3f  ->  R_ponta precisa cair %.1f%%  (ou o centro subir %.1f%%)"
              % (nome, min(perfil) / max(perfil), 100 * (1 - r[0]), 100 * (1 / r[0] - 1)))
        for frac, rot, L0 in [(0.697, "se o land for 69,7% do delta-P (v30, metodo 1D)", 8.50),
                              (0.950, "se o land for ~95% do delta-P (Copo)", 10.00),
                              (1.000, "pior caso: todo o delta-P mora no land", 10.00)]:
            cut = (1.0 - r[0]) / frac
            if cut >= 1.0:
                print("       %-46s nao da: exigiria land zero" % rot); continue
            print("       %-46s land das pontas: %5.2f -> %5.2f mm  (tirar %.2f mm)"
                  % (rot, L0, L0 * (1 - cut), L0 * cut))
    print()
    print("=" * 78)
    print("O MESMO DEFEITO DE ENTRADA, DILUIDO EM CADA COMPRIMENTO DE LAND")
    print("=" * 78)
    print("  O desequilibrio nas pontas e' uma resistencia EXTRA fixa (delta-R) que a entrada")
    print("  da matriz deixa nas pontas. Nao depende do land. Entao o que o land faz e mudar")
    print("  a FRACAO que delta-R representa no total - e e' a fracao que vira defeito na manta.")
    # delta-R em "mm equivalentes de land", calibrado no que ele MEDIU no copo:
    # deficit de 15,8% de R com land de 10,00 mm sendo ~95% do delta-P
    dR_mm = 0.158 * 10.00 * 0.95
    print("  calibracao: Copo -> deficit medido 15,8%% de R  =>  delta-R = %.2f mm equivalentes de land" % dR_mm)
    for L0, frac, rot in [(10.00, 0.950, "Copo  (land 10,00 mm)"),
                          (8.50, 0.697, "Jonatha v30 (land 8,50 mm)"),
                          (10.00, 0.697, "v30 com land igual ao do copo"),
                          (31.60, 0.950, "land 31,60 mm (alvo: 5% de deficit)"),
                          (52.70, 0.950, "land 52,70 mm (alvo: 3% de deficit)"),
                          (108.83, 1.000, "Gedeon CERTA (fenda atravessada, 109,00 - 0,17)")]:
        deficit = dR_mm / (L0 / frac)
        print("  %-48s deficit %.5s  %%   pressao do land %6.0f bar"
              % (rot, ("%.1f" % (100 * deficit)), GRAD_BAR_PER_MM * L0))
    print("  leitura: a Gedeon nao tem 'recurso' nenhum nas pontas - ela tem 10x mais land,")
    print("  e paga isso em pressao. Uma matriz com land curto so fica uniforme se a ENTRADA")
    print("  da fenda for uniforme ao longo dos 75 mm (e nao e' em nenhuma das tres medidas aqui).")
    if want_json:
        json.dump(out_json, open("alivio_pontas.json", "w"), indent=1, ensure_ascii=False)
        print("\ngravo alivio_pontas.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
