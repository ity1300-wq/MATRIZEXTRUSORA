#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Codemod da reorganizacao 2026-09-13: aponta codigo e documentos para 07_CAD_Matrizes/."""
import os
import re
import json
import ast

R = "/home/user/MATRIZEXTRUSORA"
D01 = "01_CAD_MatrizJonatha_Oficial"
M01 = "07_CAD_Matrizes/M01_Jonatha_v27_OFICIAL"
M02 = "07_CAD_Matrizes/M02_Jonatha_v28_PROPOSTA"
M03 = "07_CAD_Matrizes/M03_Gedeon_CERTA"
M04 = "07_CAD_Matrizes/M04_Gedeon_ENTREGUE_HISTORICA"
IGNORA = ("05_Interface_Auditoria", ".github", "02_CAD_Modelos_Historicos", ".git")


def em_esqueleto(p):
    return any(seg in p for seg in IGNORA)


def caminhos_py(s):
    """Regras de reescrita dos .py (constantes de diretorio e joins inline)."""
    # 1) constante de pasta: DIR_* = os.path.join(RAIZ, "01_CAD...")
    s = re.sub(r'(DIR_[A-Z0-9_]+|OFICIAL)\s*=\s*os\.path\.join\(RAIZ, "01_CAD_MatrizJonatha_Oficial"\)',
               r'\1 = os.path.join(RAIZ, "07_CAD_Matrizes", "M01_Jonatha_v27_OFICIAL")', s)
    # 2) join inline com nome de arquivo: separa v28 (proposta) do v27 (oficial)
    s = re.sub(r'os\.path\.join\(RAIZ,\s*\n?\s*"01_CAD_MatrizJonatha_Oficial",\s*\n?\s*"(MatrizJonatha_v28[^"]*)"',
               r'os.path.join(RAIZ,\n                 "07_CAD_Matrizes", "M02_Jonatha_v28_PROPOSTA", "\1"', s)
    s = re.sub(r'os\.path\.join\(RAIZ,\s*\n?\s*"01_CAD_MatrizJonatha_Oficial",\s*\n?\s*"(MatrizJonatha[^"]*)"',
               r'os.path.join(RAIZ,\n                 "07_CAD_Matrizes", "M01_Jonatha_v27_OFICIAL", "\1"', s)
    # 3) usos do antigo DIR_OFF/DIR_CAD com arquivos _v28 -> DIR_V28
    tem_v28 = re.search(r'os\.path\.join\((DIR_CAD|DIR_OFF|OFICIAL),\s*\n?\s*"MatrizJonatha_v28', s)
    if tem_v28:
        s = re.sub(r'os\.path\.join\((DIR_CAD|DIR_OFF|OFICIAL),(\s*\n?\s*)"MatrizJonatha_v28',
                   r'os.path.join(DIR_V28,\2"MatrizJonatha_v28', s)
        for var in ("DIR_CAD", "DIR_OFF", "OFICIAL"):
            pad = re.search(r'^(' + var + r' = os\.path\.join\(RAIZ, "07_CAD_Matrizes", "M01_Jonatha_v27_OFICIAL"\))$',
                            s, re.M)
            if pad:
                s = s[:pad.end()] + ('\n' + var.replace("_CAD", "_V28").replace("_OFF", "_V28")
                                     .replace("OFICIAL", "DIR_V28") +
                                     ' = os.path.join(RAIZ, "07_CAD_Matrizes", "M02_Jonatha_v28_PROPOSTA")') + s[pad.end():]
                break
    # 3b) caso especial: gerar_matriz_v28.py le o canal do v27 de um lado e escreve o v28 do outro
    if "nome = lambda ext: os.path.join(DIR_CAD, f\"MatrizJonatha_{ROTULO}{ext}\")" in s:
        s = s.replace('DIR_CAD = os.path.join(RAIZ, "07_CAD_Matrizes", "M01_Jonatha_v27_OFICIAL")',
                      'DIR_CAD = os.path.join(RAIZ, "07_CAD_Matrizes", "M01_Jonatha_v27_OFICIAL")\n'
                      'DIR_OUT = os.path.join(RAIZ, "07_CAD_Matrizes", "M02_Jonatha_v28_PROPOSTA")', 1)
        s = s.replace('os.path.join(DIR_CAD, f"MatrizJonatha_{ROTULO}{ext}")',
                      'os.path.join(DIR_OUT, f"MatrizJonatha_{ROTULO}{ext}")')
        s = s.replace('"\\n-> STEP {ROTULO_DOC} gravados em 01_CAD_MatrizJonatha_Oficial/',
                      '"\\n-> STEP {ROTULO_DOC} gravados em 07_CAD_Matrizes/M02_Jonatha_v28_PROPOSTA/')
    # 4) pastas do cabecote que hospedavam as matrizes
    s = s.replace('"06_CAD_Cabecote_EX-030", "STEP", "Gedeon_Certa"', '"07_CAD_Matrizes", "M03_Gedeon_CERTA"')
    s = s.replace('"06_CAD_Cabecote_EX-030", "STEP", "Gedeon_Corrigida_REFUTADA"',
                  '"07_CAD_Matrizes", "M04_Gedeon_ENTREGUE_HISTORICA"')
    s = s.replace('"06_CAD_Cabecote_EX-030", "STEP", "Gedeon_Corrigida"',
                  '"07_CAD_Matrizes", "M04_Gedeon_ENTREGUE_HISTORICA"')
    s = s.replace('06_CAD_Cabecote_EX-030/STEP/Gedeon_Corrigida_REFUTADA', '07_CAD_Matrizes/M04_Gedeon_ENTREGUE_HISTORICA')
    s = s.replace('06_CAD_Cabecote_EX-030/STEP/Gedeon_Corrigida', '07_CAD_Matrizes/M04_Gedeon_ENTREGUE_HISTORICA')
    s = s.replace('06_CAD_Cabecote_EX-030/STEP/Gedeon_Certa', '07_CAD_Matrizes/M03_Gedeon_CERTA')
    return s


def caminhos_doc(s):
    """So os caminhos com nome de arquivo: as mencoes a `01_/` como pasta continuam validas (atalhos)."""
    for par in ((D01 + "/MatrizJonatha_v28", M02 + "/MatrizJonatha_v28"),
                (D01 + "/MatrizJonatha", M01 + "/MatrizJonatha"),
                ("06_CAD_Cabecote_EX-030/STEP/Gedeon_Corrigida_REFUTADA", M04),
                ("06_CAD_Cabecote_EX-030/STEP/Gedeon_Corrigida", M04),
                ("06_CAD_Cabecote_EX-030/STEP/Gedeon_Certa", M03)):
        s = s.replace(par[0], par[1])
    return s


def main():
    tocados = []
    for base, dirs, files in os.walk(R):
        dirs[:] = [d for d in dirs if not em_esqueleto(os.path.relpath(os.path.join(base, d), R))]
        for fn in files:
            rel = os.path.relpath(os.path.join(base, fn), R)
            if em_esqueleto(rel):
                continue
            p = os.path.join(R, rel)
            if fn.endswith(".py") and rel.startswith("04_Dados_SSOT_e_Scripts"):
                s = open(p, encoding="utf-8").read()
                n = caminhos_py(s)
                if n != s:
                    try:
                        ast.parse(n)
                    except SyntaxError as e:
                        print("  REJEITADO", rel, "=>", e.msg, "linha", e.lineno)
                        continue
                    open(p, "w", encoding="utf-8").write(n)
                    tocados.append(rel)
            elif fn.endswith((".md", ".json")) and (rel.startswith(("03_", "06_", "04_")) or rel == "README.md"):
                s = open(p, encoding="utf-8").read()
                if rel == "04_Dados_SSOT_e_Scripts/cad_die_parameters.json":
                    n = s.replace(D01 + "/MatrizJonatha_v28", M02 + "/MatrizJonatha_v28")
                    n = n.replace("06_CAD_Cabecote_EX-030/STEP/Gedeon_Corrigida_REFUTADA", M04)
                    n = n.replace("06_CAD_Cabecote_EX-030/STEP/Gedeon_Certa", M03)
                    n = n.replace("06_CAD_Cabecote_EX-030/STEP/Gedeon_Corrigida", M04)
                else:
                    n = caminhos_doc(s)
                if n != s:
                    if fn.endswith(".json"):
                        json.loads(n)
                    open(p, "w", encoding="utf-8").write(n)
                    tocados.append(rel)
    print("%d arquivos reescritos" % len(tocados))
    for t in tocados:
        print("   ", t)


main()
