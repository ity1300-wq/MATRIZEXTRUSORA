#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fecha a remocao da Gedeon CORRIGIDA: portao, gerador da CERTA e prancha passam a medir a GEDEON
ENTREGUE (a historica de 02_) contra a CERTA - que e o que interessava no numero - e o par
documento x JSON migra para `RELATORIO_GEDEON_CERTA.md`."""
import ast
import os

R = "/home/user/MATRIZEXTRUSORA"
G = os.path.join(R, "04_Dados_SSOT_e_Scripts/verificar_cadeia.py")
C = os.path.join(R, "04_Dados_SSOT_e_Scripts/gerar_gedeon_certa.py")
D = os.path.join(R, "04_Dados_SSOT_e_Scripts/desenhar_gedeon_consertada.py")


def carrega(p):
    return open(p, encoding="utf-8").read()


def grava(p, s):
    ast.parse(s)
    open(p, "w", encoding="utf-8").write(s)
    print("   gravado:", os.path.relpath(p, R))


# ------------------------------------------------------------------ gerador da CERTA: [8] vira medicao das duas Gedeon
s = carrega(C)
i = s.index("    # --------------------------------------------------- [8] o que a entrega anterior errou")
j = s.index("    # ------------------------------------------------------------------- [8] escreve os entregaveis")
novo = '''    # --------------------------------- [8] a GEDEON ENTREGUE (02_/) contra a CERTA, medida nos dois arquivos
    d_ant = os.path.join(RAIZ, "07_CAD_Matrizes", "Matriz_Gedeon_Entregue_HISTORICA")
    a_ant = maior(le(os.path.join(d_ant, "MatrizGedeon_Body_A.step")))
    b_ant = maior(le(os.path.join(d_ant, "MatrizGedeon_Body_B.step")))
    v_ant = vol(uniao([a_ant, b_ant]))
    med["gedeon_entregue_contra_certa"] = dict(
        arquivo="02_CAD_Modelos_Historicos/MatrizGedeon_Body_A.step + _Body_B.step (lidos; atalhos para "
                "07_CAD_Matrizes/Matriz_Gedeon_Entregue_HISTORICA/)",
        volume_aco_entregue_mm3=round(v_ant, 1), volume_aco_certa_mm3=round(vol(certa), 1),
        aco_que_falta_na_entregue_mm3=round(vol(certa) - v_ant, 1),
        motivo="a Gedeon que veio do CAD antigo tem o funil da Jonatha escavado no proprio aco; a certa do "
               "usuario nao tem funil nenhum - o vazio dela e o cone de entrada + a fenda atravessada")
    print(f"    [Gedeon entregue x certa] aco {v_ant:,.1f} mm3 contra {vol(certa):,.1f} mm3: faltam na "
          f"entregue {vol(certa) - v_ant:,.1f} mm3 que a escavacao do funil levou")

    # -------------------------------------------------- [9] a tentativa de re-corte, que nao e a matriz
    med["recorte_historico_nao_e_a_matriz"] = dict(
        volume_do_canal_historico_mm3=round(vol(canal_velho), 1),
        aco_que_ser_removido_da_certa_mm3=round(vol(certa) - sobra, 1),
        observacao="escavar `MatrizGedeon_Canal_Fluxo.step` no arquivo do usuario tiraria este aco dele; a "
                   "entrega NAO faz isso, e foi exatamente o que a tentativa anterior (apagada em "
                   "2026-09-13) fazia")

'''
s = s[:i] + novo + s[j:]
s = s.replace('''        "> **REFUTADA''', '''        "> **REFUTADA''')  # no-op defensivo
open(C, "w", encoding="utf-8").write(s)
grava(C, s)

# ------------------------------------------------------------------ prancha: faixa 2 mede os pinos ela mesma
s = carrega(D)
antigo = '''    pin = json.load(open(os.path.join(AQUI, "gedeon_corrigida.json"), encoding="utf-8"))["pinos"]'''
assert s.count(antigo) == 1
s = s.replace(antigo, '''    # as caixas dos pinos da Gedeon ENTREGUE, medidas nos proprios arquivos de 02_/ (antes vinham do JSON
    # da tentativa refutada, que foi apagada): cilindros de raio 0,89 com eixo em Z
    pin = {"caixas_mm": []}
    for meio in (A0, B0):
        for f in meio.val().Faces():
            if f.geomType() == "CYLINDER" and abs(f._geomAdaptor().Cylinder().Radius() - 0.89) < 0.02:
                b = f.BoundingBox()
                pin["caixas_mm"].append(dict(x=[round(b.xmin, 2), round(b.xmax, 2)],
                                             z=[round(b.zmin, 2), round(b.zmax, 2)]))
    pin["caixas_mm"].sort(key=lambda c: c["x"][0])''')
for vel, nv in (('"entrega_anterior_refutada"]["volume_aco_entrega_anterior_mm3"', '"gedeon_entregue_contra_certa"]["volume_aco_entregue_mm3"'),
                    ('"entrega_anterior_refutada"]["volume_aco_certa_mm3"', '"gedeon_entregue_contra_certa"]["volume_aco_certa_mm3"'),
                    ('med["2 Gedeon entregue"]["aco_mm3"] = gc["entrega_anterior_refutada"]["volume_aco_entrega_anterior_mm3"]',
                     'med["2 Gedeon entregue"]["aco_mm3"] = gc["gedeon_entregue_contra_certa"]["volume_aco_entregue_mm3"]')):
        s = s.replace(vel, nv)
s = s.replace('''                   n(gc["entrega_anterior_refutada"]["volume_aco_entrega_anterior_mm3"], 1),
                   n(gc["entrega_anterior_refutada"]["volume_aco_certa_mm3"], 1)),''',
              '''                   n(gc["gedeon_entregue_contra_certa"]["volume_aco_entregue_mm3"], 1),
                   n(gc["gedeon_entregue_contra_certa"]["volume_aco_certa_mm3"], 1)),''')
s = s.replace('''"A u B = %s mm3 de aco, caixa"''', '''"A u B = %s mm3 de aco, caixa"''')
s = s.replace('''unidas para o corte: A u B = %s mm3 de aco''', '''unidas para o corte: A u B = %s mm3 de aco''')
open(D, "w", encoding="utf-8").write(s)
grava(D, s)

# ------------------------------------------------------------------ o .gitignore, que ainda nomeava a pasta M04
P = os.path.join(R, ".gitignore")
s = carrega(P)
s = s.replace("07_CAD_Matrizes/M04_Gedeon_ENTREGUE_HISTORICA/*.step",
              "# a tentativa de re-corte da Gedeon foi APAGADA de proposito; se alguem a recriar, que fique fora")
grava(P, s)
print("done")
