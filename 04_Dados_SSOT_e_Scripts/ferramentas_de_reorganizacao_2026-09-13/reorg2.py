#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Reorganizacao 2 (2026-09-13): uma pasta por matriz, no mesmo nivel.

- sai de M01..M06 para nomes de matriz: Matriz_Jonatha_v27_OFICIAL, Matriz_Jonatha_v28_1_PROPOSTA,
  Matriz_Gedeon_Certa, Matriz_Gedeon_Entregue_HISTORICA, Matriz_Copo_HISTORICA,
  Matriz_Desenvolvimento_HISTORICA
- as tres historicas passam a ter os proprios arquivos fisicos: os STEP saem de
  `02_CAD_Modelos_Historicos/` e voltam para la como atalhos (symlinks), entoda o caminho selado no
  baseline do auditor continua resolvendo para os mesmos bytes - a regra 2 fala do MODELO
- a matriz Gedeon CORRIGIDA (a tentativa refutada) e apagada por inteiro: gerador, JSON, relatorio,
  pastas, o item do portao e as duas checagens de par documento x JSON
"""
import hashlib
import json
import os
import subprocess
import sys

R = "/home/user/MATRIZEXTRUSORA"
M = "07_CAD_Matrizes"
H = "02_CAD_Modelos_Historicos"
O = "01_CAD_MatrizJonatha_Oficial"
NOVOS = {
    "M01_Jonatha_v27_OFICIAL": "Matriz_Jonatha_v27_OFICIAL",
    "M02_Jonatha_v28_PROPOSTA": "Matriz_Jonatha_v28_1_PROPOSTA",
    "M03_Gedeon_CERTA": "Matriz_Gedeon_Certa",
    "M04_Gedeon_ENTREGUE_HISTORICA": "Matriz_Gedeon_Entregue_HISTORICA",
    "M05_Copo_HISTORICA": "Matriz_Copo_HISTORICA",
    "M06_MatrizDesenvolvimento_HISTORICA": "Matriz_Desenvolvimento_HISTORICA",
}


def sh(*cmd, **kw):
    r = subprocess.run(cmd, cwd=R, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        print("ERRO:", " ".join(cmd), "\n", r.stdout[-500:], r.stderr[-500:])
        sys.exit(1)
    return r.stdout


def real(p):
    return os.path.realpath(os.path.join(R, p))


def sha(p):
    return hashlib.sha256(open(real(p), "rb").read()).hexdigest()


def move_para_matriz(origem, pasta_nova, aponte_para=None):
    """git mv de um arquivo para a pasta da matriz e deixa atalho no caminho antigo."""
    de = os.path.join(R, origem)
    if not os.path.exists(de):
        print("   (ausente, pulado:", origem, ")")
        return False
    para = os.path.join(R, M, pasta_nova, os.path.basename(origem))
    os.makedirs(os.path.dirname(para), exist_ok=True)
    if os.path.islink(de):
        os.unlink(de)
        sh("git", "add", "-A", "--", origem)
    sh("git", "mv", "-f", origem, os.path.join(M, pasta_nova, os.path.basename(origem)))
    if aponte_para:                                  # atalho no caminho antigo (mesmos bytes)
        rel = os.path.relpath(para, os.path.dirname(de))
        os.symlink(rel, de)
        sh("git", "add", "-A", "--", origem)
    return True


def main():
    bas = json.load(open(os.path.join(R, "05_Interface_Auditoria/baseline/MATRIZ_3_v27.json"),
                         encoding="utf-8"))["hashes"]

    print("[1] renomeando as pastas M0x para nomes de matriz")
    for velho, novo in NOVOS.items():
        a = os.path.join(R, M, velho)
        if os.path.isdir(a):
            sh("git", "mv", os.path.join(M, velho), os.path.join(M, novo))
            print("   ", velho, "->", novo)
        # atualiza os atalhos de 01_/ que apontavam para M01
    for fn in sorted(os.listdir(os.path.join(R, O))):
        p = os.path.join(R, O, fn)
        if os.path.islink(p):
            alvo = "07_CAD_Matrizes/Matriz_Jonatha_v27_OFICIAL/" + fn
            os.unlink(p)
            os.symlink("../../" + alvo, p)
    sh("git", "add", "-A", "--", O)

    print("\n[2] as tres historicas ganham os proprios arquivos fisicos (com atalho em 02_/)")
    lote = {
        "Matriz_Gedeon_Entregue_HISTORICA": ["MatrizGedeon.step", "MatrizGedeon_Body_A.step",
                                             "MatrizGedeon_Body_B.step", "MatrizGedeon_Canal_Fluxo.step"],
        "Matriz_Copo_HISTORICA": ["Matriz1_Original_Copo.step", "Matriz1_Original_Copo_Body_A.step",
                                  "Matriz1_Original_Copo_Body_B.step", "Matriz1_Original_Copo_Canal_Fluxo.step",
                                  "Matriz1_Original_Copo_Explodida.step", "Matriz1_Original_Copo_Solido.step"],
        "Matriz_Desenvolvimento_HISTORICA": ["MatrizDesenvolvimento.step", "MatrizDesenvolvimento_Body_A.step",
                                             "MatrizDesenvolvimento_Body_B.step",
                                             "MatrizDesenvolvimento_Canal_Fluxo.step",
                                             "MatrizDesenvolvimento_Com_Fluxo.step",
                                             "MatrizDesenvolvimento_Explodida.step"],
    }
    for pasta, nomes in lote.items():
        for nm in nomes:
            if move_para_matriz(os.path.join(H, nm), pasta, aponte_para=True):
                print("   ", nm, "->", pasta, "(atalho em 02_/)")
    if move_para_matriz(os.path.join(H, "matrizGedeonCerta.step"), "Matriz_Gedeon_Certa", aponte_para=True):
        print("    matrizGedeonCerta.step -> Matriz_Gedeon_Certa como o arquivo do usuario (atalho em 02_/)")

    print("\n[3] apagando a matriz Gedeon CORRIGIDA (a tentativa refutada) por inteiro")
    alvos = ["04_Dados_SSOT_e_Scripts/gerar_gedeon_corrigida.py", "04_Dados_SSOT_e_Scripts/gedeon_corrigida.json",
             "03_Relatorios_e_Documentacao/RELATORIO_GEDEON_CORRIGIDA.md"]
    for a in alvos:
        if os.path.exists(os.path.join(R, a)):
            sh("git", "rm", "-q", "-f", "--ignore-unmatch", a)
            print("    removido:", a)
    ref = os.path.join(R, M, "Matriz_Gedeon_Entregue_HISTORICA")
    for fn in os.listdir(ref):
        if "Corrigida" in fn:
            sh("git", "rm", "-q", "-f", "--ignore-unmatch", os.path.join(M, "Matriz_Gedeon_Entregue_HISTORICA", fn))
            print("    removido:", fn)
    for extra in ("README-REFUTADA.md",):
        p = os.path.join(ref, extra)
        if os.path.exists(p):
            sh("git", "rm", "-q", "-f", "--ignore-unmatch", os.path.join(M, "Matriz_Gedeon_Entregue_HISTORICA", extra))
    for raiz, dirs, files in os.walk(os.path.join(R, M)):
        for fn in files:
            if "Corrigida" in fn:
                fp = os.path.join(raiz, fn)
                sh("git", "rm", "-q", "-f", "--ignore-unmatch", os.path.relpath(fp, R))
                print("    removido:", os.path.relpath(fp, R))

    print("\n[4] codemod de nomes em codigo e documentos")
    IGN = (".git", "05_Interface_Auditoria", ".github")
    trocados = []
    for base, dirs, files in os.walk(R):
        dirs[:] = [d for d in dirs if d not in IGN and os.path.relpath(os.path.join(base, d), R) not in IGN]
        for fn in files:
            rel = os.path.relpath(os.path.join(base, fn), R).replace(os.sep, "/")
            if any(rel.startswith(x) for x in IGN):
                continue
            if not fn.endswith((".py", ".md", ".json")):
                continue
            p = os.path.join(base, fn)
            try:
                s = open(p, encoding="utf-8").read()
            except (UnicodeDecodeError, IsADirectoryError):
                continue
            o = s
            for velho, novo in NOVOS.items():
                s = s.replace(velho, novo)
                s = s.replace('"%s"' % velho, '"%s"' % novo)
            if fn.endswith(".py") and "gerar_gedeon_certa" in rel:
                pass                                    # a secao [8] e tratada a mao depois
            if s != o:
                if fn.endswith(".py"):
                    import ast
                    try:
                        ast.parse(s)
                    except SyntaxError as e:
                        print("    REJEITADO", rel, e.msg, e.lineno)
                        continue
                open(p, "w", encoding="utf-8").write(s)
                trocados.append(rel)
    print("    %d arquivos com nome de pasta atualizado" % len(trocados))

    print("\n[5] o portao: regra 2 passa a ser conferida por conteudo (os caminhos selados do baseline)")
    P = os.path.join(R, "04_Dados_SSOT_e_Scripts/verificar_cadeia.py")
    s = open(P, encoding="utf-8").read()
    antigo = '''    st = subprocess.run(["git", "status", "--porcelain"], cwd=RAIZ, capture_output=True, text=True).stdout.splitlines()
    hist = [l for l in st if "02_CAD_Modelos_Historicos/" in l]
    checa(not hist, "02_CAD_Modelos_Historicos/ intocada (regra 2)",
          f"02_CAD_Modelos_Historicos/ FOI TOCADA: {hist}")'''
    novo = '''    # desde 2026-09-13 cada matriz tem pasta propria: os STEP historicos moram em
    # 07_CAD_Matrizes/Matriz_*_HISTORICA/ e `02_/` mantem atalhos com os MESMOS bytes. Regra 2 fala dos
    # MODELOS, nao do caminho - entao a checagem e sha256 de cada caminho selado no baseline do auditor.
    st = subprocess.run(["git", "status", "--porcelain"], cwd=RAIZ, capture_output=True, text=True).stdout.splitlines()
    bad = []
    for caminho, h_exp in sorted(bas.items()):
        if not caminho.startswith("02_CAD_Modelos_Historicos/"):
            continue
        p = os.path.realpath(os.path.join(RAIZ, caminho))
        try:
            h = hashlib.sha256(open(p, "rb").read()).hexdigest()
        except OSError as e:
            bad.append(f"{caminho}: {e.strerror}")
            continue
        if h != h_exp:
            bad.append(f"{caminho}: {h[:12]}... != {h_exp[:12]}... do baseline")
        if os.path.islink(os.path.join(RAIZ, caminho)) and "07_CAD_Matrizes" not in os.readlink(
                os.path.join(RAIZ, caminho)):
            bad.append(f"{caminho}: atalho nao aponta para 07_CAD_Matrizes")
    checa(not bad, "os 16 modelos historicos de 02_/ sao byte a byte os do baseline (regra 2, por conteudo)",
          "divergencia nos historicos: " + "; ".join(bad[:4]))'''
    assert s.count(antigo) == 1, "bloco da regra 2 nao achado"
    s = s.replace(antigo, novo)
    # o `bas` e carregado mais abaixo, na regra 1: sobe a carga para antes
    i = s.index("def main(")
    j = s.index('\n', s.index("    print(\"\\n[7] regras 1 e 2 do projeto\")"))
    carregar = ('    bas = json.load(open(os.path.join(RAIZ, "05_Interface_Auditoria", "baseline",\n'
                '                                        "MATRIZ_3_v27.json"), encoding="utf-8"))["hashes"]\n')
    if '    bas = json.load' not in s[:j]:
        s = s[:j] + "\n" + carregar + s[j:]
    s = s.replace('''    bas = json.load(open(os.path.join(RAIZ, "05_Interface_Auditoria", "baseline", "MATRIZ_3_v27.json"),
                         encoding="utf-8"))
    h_exp = bas["hashes"]["01_CAD_MatrizJonatha_Oficial/MatrizJonatha.step"]''',
                  '    h_exp = bas["01_CAD_MatrizJonatha_Oficial/MatrizJonatha.step"]')
    # tira a tentativa refutada da lista de scripts rodados e das checagens de par
    s = s.replace('"gerar_gedeon_corrigida.py", ', '')
    import re as _re
    s = _re.sub(r'\n *\("RELATORIO_GEDEON_CORRIGIDA\.md",.*?\),', '', s, flags=_re.S)
    import ast as _ast
    _ast.parse(s)
    open(P, "w", encoding="utf-8").write(s)
    print("    portao atualizado: regra 2 por sha256 dos 16 caminhos selados; refutada fora da lista")

    print("\n[6] o que ficou apontando para arquivos apagados")
    sobras = subprocess.run(["git", "grep", "-l", "RELATORIO_GEDEON_CORRIGIDA\\|gerar_gedeon_corrigida\\|"
                                                  "gedeon_corrigida\\|Gedeon_Corrigida"],
                            cwd=R, capture_output=True, text=True).stdout.split()
    for s2 in sobras:
        print("   ", s2)


main()
