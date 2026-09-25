# -*- coding: utf-8 -*-
"""Autoversao da REVALORACAO_FOCO_SERRILHADO_2026-09-25.md.

Re-meDE cada numero do documento nos STEP do repo (mesmo codigo do `medir_alivio_pontas.py`,
importado - nao reimplementado) e confere com o que esta escrito. Saída: PASS / DIVERGE.

Uso: python3 04_Dados_SSOT_e_Scripts/verificar_revaloracao_serrilhado_2026_09_25.py
"""
import os, sys

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
os.chdir(ROOT)
sys.path.insert(0, BASE)

import medir_alivio_pontas as MV          # o MESMO codigo que produz os numeros

DOC = "03_Relatorios_e_Documentacao/REVALORACAO_FOCO_SERRILHADO_2026-09-25.md"
ok, fail = [], []


def chk(nome, med, aleg, tol=0.02, un=""):
    d = abs(med - aleg) / max(abs(aleg), 1e-9)
    row = "%-52s medido %10s  no doc %10s  %.3f%%%s" % (nome, f"{med:,.3f}", f"{aleg:,.3f}", 100 * d, un)
    (ok if d <= tol else fail).append(row)


def txt_has(s):
    return 1.0 if s in TXT else 0.0


TXT = open(DOC, encoding="utf-8").read()

DIES = {
    "copo": ("06_CAD_Cabecote_EX-030/STEP/Cabecote_EX-030_com_Matriz_Copo.step", "die"),
    "v30": ("06_CAD_Cabecote_EX-030/STEP/Cabecote_EX-030_com_Matriz_Jonatha_v30.step", "die"),
    "gedeon": ("07_CAD_Matrizes/Matriz_Gedeon_Certa/matrizGedeonCerta.step", "only"),
}
S = {}
for k, (path, mode) in DIES.items():
    die, err = MV.pick_solid(path, mode)
    assert die is not None, (path, err)
    axis, zout = MV.detect_axis(die)
    S[k] = (die, axis, zout)
    print("  %-8s eixo=%s  face de saida Z=%.2f" % (k, axis, zout))

# (d) canal que alimenta a PONTA, 11 mm atras da boca: 18,90 (copo) | 1,55 (v30) | 1,50 (Gedeon)
for k, aleg in [("copo", 18.90), ("v30", 1.52), ("gedeon", 1.52)]:
    die, axis, zout = S[k]
    g = MV.gap_at_depth(die, axis, zout, 36.60, 11.0)
    chk("altura do canal na ponta, d=11 (%s)" % k, g, aleg, 0.06)

# (b) land da copo no centro: primeira profundidade em que a abertura passa de 1,6 mm
import cadquery as cq
die, axis, zout = S["copo"]
land = None
d = 0.2
while d < 20.0:
    g = MV.gap_at_depth(die, axis, zout, 0.0, d)
    if g is None or g > 1.60:
        land = d - 0.2
        break
    d += 0.2
chk("land paralelo da Copo, medido (mm)", land if land else 0.0, 10.00, 0.06)

# (a) Gedeon: a fenda e' cortada ATE a face de tras -> o 'land' e' a peca inteira
gd, gaxis, gzout = S["gedeon"]
zmin_slit = None
z = gd.BoundingBox().zmin + 0.05
while z < gzout:
    g = MV._gap(gd, gaxis, 0.0, z)
    if g is not None and g <= 1.60:
        zmin_slit = z
        break
    z += 0.25
chk("Gedeon: fim do cone / inicio da fenda paralela (Z)", zmin_slit or 0.0, 20.98, 0.05)
GED_LAND = (gzout + 0.20) - (zmin_slit or 0.0)
chk("Gedeon: land paralelo medido (mm)", GED_LAND, 88.00, 0.02)

# (e) a aritmetica da tabela: dR calibrado na Copo, e os deficit/pressoes derivados
GRAD = MV.GRAD_BAR_PER_MM
dR = 0.158 * 10.00 * 0.95
chk("delta-R calibrado no Copo (mm equivalentes de land)", dR, 1.50, 0.02)
for nome, L0, frac, aleg_def in [("Copo", 10.00, 0.950, 14.3), ("v30", 8.50, 0.697, 12.3),
                                 ("Gedeon", 88.00, 1.000, 1.7)]:
    chk("deficit implied (%s), %%" % nome, 100 * dR / (L0 / frac), aleg_def, 0.05)
for L0, aleg in [(10.00, 22), (8.50, 19), (31.60, 69), (52.70, 115), (88.00, 193)]:
    chk("pressao do land de %.2f mm (bar)" % L0, GRAD * L0, aleg, 0.03)

# (f) nada no documento e sem alivio: as tres bocas medem ~1,5 em toda a largura
for k in DIES:
    die, axis, zout = S[k]
    g0 = MV.gap_at_depth(die, axis, zout, 0.0, 0.2)
    gt = MV.gap_at_depth(die, axis, zout, 36.60, 0.2)
    chk("boca na ponta, mesma da boca no centro (%s)" % k, gt, g0, 0.001)

# texto: os numeros citados tem de estar escritos la
for nome, q in [("88,00 mm de land na Gedeon", "88,00 mm"), ("1,52 mm na ponta", "1,52 mm"), ("18,90 mm", "18,90 mm"),
                ("193 bar", "193 bar"), ("14,3 %", "14,3 %"), ("12,3 %", "12,3 %"), ("1,7 %", "1,7 %"),
                ("fenda atravessada", "atravessa"), ("Gedeon nao tem alivio", "não tem alívio"),
                ("paliativo estacionado", "estacionada")]:
    chk("doc cita: %s" % nome, txt_has(q), 1.0, 0.0)

print("== PASS (%d)" % len(ok))
for x in ok:
    print("  ok  ", x.strip())
if fail:
    print("== DIVERGE (%d)" % len(fail))
    for x in fail:
        print("  XX  ", x.strip())
sys.exit(1 if fail else 0)
