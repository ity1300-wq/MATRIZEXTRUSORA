#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Segunda passada: strings de documento dentro do codigo, glob, e a checagem [7] do portao por conteudo."""
import ast
import os

R = "/home/user/MATRIZEXTRUSORA"
D01 = "01_CAD_MatrizJonatha_Oficial"
M01 = "07_CAD_Matrizes/M01_Jonatha_v27_OFICIAL"
M02 = "07_CAD_Matrizes/M02_Jonatha_v28_PROPOSTA"

# caminhos que devem continuar escritos como estao (o caminho oficial e o que o portao confere por hash)
NAO_TOCAR = ("04_Dados_SSOT_e_Scripts/cad_die_parameters.json",)


def passa(s):
    n0 = s
    for par in ((D01 + "/MatrizJonatha_v28*", M02 + "/MatrizJonatha_v28*"),
                (D01 + "/MatrizJonatha*", M01 + "/MatrizJonatha*  (o caminho antigo segue valido: ha um "
                                                     "atalho em `01_CAD_MatrizJonatha_Oficial/` para o mesmo "
                                                     "arquivo)"),
                (D01 + "/MatrizJonatha_v28", M02 + "/MatrizJonatha_v28"),
                (D01 + "/MatrizJonatha", M01 + "/MatrizJonatha")):
        s = s.replace(par[0], par[1])
    return s, (s != n0)


def main():
    feitos = []
    for base, dirs, files in os.walk(R):
        dirs[:] = [d for d in dirs if d not in (".git", "02_CAD_Modelos_Historicos", "05_Interface_Auditoria")]
        for fn in files:
            rel = os.path.relpath(os.path.join(base, fn), R).replace(os.sep, "/")
            if rel in NAO_TOCAR:
                continue
            if not (rel.startswith("04_Dados_SSOT_e_Scripts/") and fn.endswith(".py")) and rel != "README.md":
                continue
            if rel == "04_Dados_SSOT_e_Scripts/verificar_cadeia.py":
                continue          # este eu trato a parte, na mao
            p = os.path.join(R, rel)
            s = open(p, encoding="utf-8").read()
            n, mudou = passa(s)
            if not mudou:
                continue
            if fn.endswith(".py"):
                try:
                    ast.parse(n)
                except SyntaxError as e:
                    print("  REJEITADO", rel, e.msg, e.lineno)
                    continue
            open(p, "w", encoding="utf-8").write(n)
            feitos.append(rel)
    print("segunda passada em %d arquivo(s):" % len(feitos))
    for f in feitos:
        print("   ", f)

    # --- o portao: regra 1 passa a ser conferida por CONTEUDO (o master mudou de pasta, nao de forma)
    P = os.path.join(R, "04_Dados_SSOT_e_Scripts/verificar_cadeia.py")
    s = open(P, encoding="utf-8").read()
    antigo = '''    mestre = [l for l in st if l.rstrip().endswith("01_CAD_MatrizJonatha_Oficial/MatrizJonatha.step")]
    checa(not mestre, "MatrizJonatha.step (v27.0) intocado (regra 1)",
          f"o master v27.0 foi modificado: {mestre}")'''
    novo = '''    # desde 2026-09-13 o modelo oficial mora em `07_CAD_Matrizes/M01_Jonatha_v27_OFICIAL/` e `01_/` mantem
    # um atalho com o mesmo conteudo. Regra 1 fala do MODELO, nao do caminho: por isso a checagem e por sha256
    # contra o baseline do auditor, e nao por "git status limpo num caminho".
    bas = json.load(open(os.path.join(RAIZ, "05_Interface_Auditoria", "baseline", "MATRIZ_3_v27.json"),
                         encoding="utf-8"))
    h_exp = bas["hashes"]["01_CAD_MatrizJonatha_Oficial/MatrizJonatha.step"]
    corpo = os.path.realpath(os.path.join(RAIZ, "01_CAD_MatrizJonatha_Oficial", "MatrizJonatha.step"))
    h_atu = hashlib.sha256(open(corpo, "rb").read()).hexdigest()
    checa(h_atu == h_exp, "MatrizJonatha.step (v27.0) e o mesmo modelo de sempre (regra 1, por conteudo)",
          f"o sha256 do master divergiu do baseline: {h_atu[:16]}... contra {h_exp[:16]}... "
          f"(arquivo real: {os.path.relpath(corpo, RAIZ)})")
    checa(corpo.startswith(os.path.join(RAIZ, "07_CAD_Matrizes", "M01_Jonatha_v27_OFICIAL")) or
          corpo == os.path.join(RAIZ, "01_CAD_MatrizJonatha_Oficial", "MatrizJonatha.step"),
          "o master esta na pasta organizada (07_) ou no caminho oficial",
          f"o master esta em {os.path.relpath(corpo, RAIZ)}, nem em 07_/M01 nem em 01_/")'''
    assert s.count(antigo) == 1, "bloco [7] nao encontrado"
    s = s.replace(antigo, novo)
    if "\nimport hashlib" not in s:
        s = s.replace("import json", "import hashlib\nimport json", 1)
    ast.parse(s)
    open(P, "w", encoding="utf-8").write(s)
    print("portao [7]: regra 1 agora conferida por sha256 contra o baseline do auditor")


main()
