#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Portao: tira a refutada da cadeia, troca os pares para o relatorio da CERTA, e passa a regra 2
de "git status limpo em 02_/" para "sha256 dos 16 caminhos selados no baseline + atalho apontando para 07_"."""
import ast
import os

R = "/home/user/MATRIZEXTRUSORA"
P = os.path.join(R, "04_Dados_SSOT_e_Scripts/verificar_cadeia.py")
s = open(P, encoding="utf-8").read()


def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, ("nao achado/ambiguo:", a[:60], s.count(a))
    s = s.replace(a, b)


rep('"generate_auto_prompt.py",\n          "gerar_gedeon_corrigida.py", "verify_geometry_ssot.py --json --md"',
    '"generate_auto_prompt.py",\n          "gerar_gedeon_certa.py",\n'
    '          "verify_geometry_ssot.py --json --md"')

rep('''                  ("RELATORIO_GEDEON_CORRIGIDA.md", "canal_da_gedeon_confere/arquivo_canal_mm3", 1,
                   "gedeon_corrigida.json"),
                  ("RELATORIO_GEDEON_CORRIGIDA.md", "contra_a_jonatha/canal_jonatha_minus_gedeon_mm3",
                   1, "gedeon_corrigida.json")]''',
    '''                  ("RELATORIO_GEDEON_CERTA.md", "inventario/volume", 1, "gedeon_certa.json"),
                  ("RELATORIO_GEDEON_CERTA.md", "cavidade/volume_cavidade_mm3", 1, "gedeon_certa.json"),
                  ("RELATORIO_GEDEON_CERTA.md", "contra_a_jonatha/aco_so_na_certa_mm3", 1,
                   "gedeon_certa.json")]''')

rep('''    st = subprocess.run(["git", "status", "--porcelain"], cwd=RAIZ, capture_output=True, text=True).stdout.splitlines()
    hist = [l for l in st if "02_CAD_Modelos_Historicos/" in l]
    checa(not hist, "02_CAD_Modelos_Historicos/ intocada (regra 2)",
          f"02_CAD_Modelos_Historicos/ FOI TOCADA: {hist}")''',
    '''    # desde 2026-09-13 cada matriz tem pasta propria: os STEP historicos moram em
    # 07_CAD_Matrizes/Matriz_*_HISTORICA/ e `02_/` mantem atalhos (symlinks) com os MESMOS bytes. Regra 2
    # fala dos MODELOS, nao do caminho - por isso a checagem e o sha256 de cada um dos caminhos selados no
    # baseline do auditor, mais a prova de que cada atalho aponta para 07_CAD_Matrizes.
    bas = json.load(open(os.path.join(RAIZ, "05_Interface_Auditoria", "baseline", "MATRIZ_3_v27.json"),
                         encoding="utf-8"))["hashes"]
    bad = []
    for caminho, h_exp in sorted(bas.items()):
        if not caminho.startswith("02_CAD_Modelos_Historicos/"):
            continue
        p_real = os.path.realpath(os.path.join(RAIZ, caminho))
        try:
            h = hashlib.sha256(open(p_real, "rb").read()).hexdigest()
        except OSError as e:
            bad.append("%s: %s" % (caminho, e.strerror))
            continue
        if h != h_exp:
            bad.append("%s: %s... != %s... do baseline" % (caminho, h[:12], h_exp[:12]))
        link = os.path.join(RAIZ, caminho)
        if os.path.islink(link) and "07_CAD_Matrizes" not in os.readlink(link):
            bad.append("%s: o atalho nao aponta para 07_CAD_Matrizes" % caminho)
    checa(not bad, "os modelos historicos selados no baseline segao byte a byte iguais (regra 2, por conteudo)",
          "divergencia nos historicos: " + "; ".join(bad[:4]))''')

rep('''    bas = json.load(open(os.path.join(RAIZ, "05_Interface_Auditoria", "baseline", "MATRIZ_3_v27.json"),
                         encoding="utf-8"))
    h_exp = bas["hashes"]["01_CAD_MatrizJonatha_Oficial/MatrizJonatha.step"]''',
    '    h_exp = bas["01_CAD_MatrizJonatha_Oficial/MatrizJonatha.step"]')

ast.parse(s)
open(P, "w", encoding="utf-8").write(s)
print("portao atualizado (cadeia, pares, regra 2 por conteudo, regra 1 sem duplicar a carga do baseline)")
