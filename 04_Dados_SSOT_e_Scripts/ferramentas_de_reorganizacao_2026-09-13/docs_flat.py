#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fecha a reorganizacao: apaga os restos fisicos da refutada, escreve o indice de 07_/ para a estrutura
nova (uma pasta por matriz) e conserta os ponteiros que apontavam para arquivos deletados."""
import json
import os
import subprocess

R = "/home/user/MATRIZEXTRUSORA"
M = os.path.join(R, "07_CAD_Matrizes")


def w(rel, txt):
    open(os.path.join(R, rel), "w", encoding="utf-8").write(txt)
    print("   escrito:", rel)


def rep(rel, pares, exige=True):
    p = os.path.join(R, rel)
    s = open(p, encoding="utf-8").read()
    for a, b in pares:
        n = s.count(a)
        if exige:
            assert n >= 1, ("nao achado em %s: %r" % (rel, a[:70]))
        s = s.replace(a, b)
    open(p, "w", encoding="utf-8").write(s)
    print("   corrigido:", rel)


# ------------------------------------------------------------ 1. restos fisicos da refutada, fora do disco
apagados = []
for raiz, dirs, files in os.walk(R):
    if "/.git" in raiz:
        continue
    for f in list(files):
        if "Corrigida" in f or "corrigida" in f:
            os.remove(os.path.join(raiz, f))
            apagados.append(os.path.relpath(os.path.join(raiz, f), R))
print("1) arquivos fisicos da refutada removidos:", len(apagados), apagados)

# ------------------------------------------------------------ 2. indice de 07_/
t = []
t.append("# Matrizes — uma pasta por matriz\n")
t.append("Regra da casa: **cada matriz tem a sua pasta**, com os arquivos dela dentro. Nem pasta vazia "
         "apontando para outro lugar, nem camada intermediaria entre aqui e a matriz — foi assim que o Jonatha "
         "pediu, em 2026-09-13.\n")
t.append("| pasta | o que e | arquivos |\n|---|---|---|")
t.append("| `Matriz_Jonatha_v27_OFICIAL/` | **a master do projeto** (SSOT v27.0), o que a fabrica usa | "
         "`MatrizJonatha.step`, `_Body_A`, `_Body_B`, `_Canal_Fluxo`, `_Com_Fluxo`, `_Explodida` |")
t.append("| `Matriz_Jonatha_v28_1_PROPOSTA/` | a variante DFM — **proposta, nao promovida** | os seis acima "
         "com `_v28_1`; `DESENHO_2D_V28.png` e derivado, fica no disco mas nao vai ao git |")
t.append("| `Matriz_Gedeon_Certa/` | **a matriz do usuario**, entregue como esta, mais o que foi medido nela | "
         "`matrizGedeonCerta.step` (o arquivo dele, byte a byte), `MatrizGedeon_Certa_Body_A.step` e `_Body_B` "
         "(o par aberto no plano de particao), `MatrizGedeon_Certa_Explodida.step`, "
         "`DESENHO_2D_GEDEON_CERTA_X_JONATHA.pdf`, `desenho_gedeon.json` |")
t.append("| `Matriz_Gedeon_Entregue_HISTORICA/` | a Gedeon **antiga**, a que veio do CAD do cabecote | "
         "`MatrizGedeon.step`, `_Body_A`, `_Body_B`, `_Canal_Fluxo` |")
t.append("| `Matriz_Copo_HISTORICA/` | a matriz do desenho antigo (Copo) | `Matriz1_Original_Copo*.step` (4) |")
t.append("| `Matriz_Desenvolvimento_HISTORICA/` | matriz de desenvolvimento | `MatrizDesenvolvimento*.step` (5) |")
t.append("\n## Por que os caminhos antigos continuam valendo\n")
t.append("As regras 1 e 2 do projeto falam dos **modelos**, nao do caminho. Entao `01_CAD_MatrizJonatha_Oficial/"
         "MatrizJonatha*.step` sao atalhos para dentro de `Matriz_Jonatha_v27_OFICIAL/`, e cada `.step` de "
         "`02_CAD_Modelos_Historicos/` e um atalho para a pasta da matriz correspondente. Quem abre pelo caminho "
         "antigo ve os mesmos bytes; `git ls-files -s 02_CAD_Modelos_Historicos/` mostra `120000` em cada linha, "
         "e o portao confere o sha256 de cada um dos caminhos selados em "
         "`05_Interface_Auditoria/baseline/MATRIZ_3_v27.json` a cada rodada. Escrever dentro de `02_/` continua "
         "fora de questao: os arquivos moram na pasta da matriz e o historico so se le.\n")
t.append("## O que nao esta aqui, e o que foi apagado\n")
t.append("| o que era | peso | por que |\n|---|---|---|")
t.append("| a **Gedeon corrigida** (gerador, JSON, relatorio, 5 STEP) | 800 KB | tentativa refutada em "
         "2026-09-12 — `matrizGedeonCerta.step` e a Gedeon certa, nao havia canal a reconstruir; apagada por "
         "inteiro em 2026-09-13, a pedido |")
t.append("| `05_/ESTUDO_JONATHA.step`, `ESTUDO_GEDEON.step` | 3,8 MB | estudo do coathanger respondido e "
         "gravado no JSON; recria com `python3 04_Dados_SSOT_e_Scripts/estudar_funis.py` |")
t.append("| `05_/ESTUDO_GEDEON_REC_{COLADA,ENCAIXE_5,ENCAIXE_10}.step` | 1,0 MB | recria com "
         "`estudar_recuo_cartuchos.py` |")
t.append("| os 2 STEP derivados `_Explodida`/`_Com_Fluxo` da v28 | 1,2 MB | derivados; os quatro STEP que vao "
         "para a fabrica estao na pasta |")
t.append("| o cenario da furacao M12 em `06_/STEP/estudos/` | 144 KB | recria `gerar_cabecote_ex030_cenarios.py` |")
t.append("\nO **cabecote** e as montagens cabecote + matriz ficam em `06_CAD_Cabecote_EX-030/STEP/` "
         "(`Cabecote_EX-030_desenhado.step`, `_sem_flange.step`, `Cabecote_EX-030_com_Matriz_Copo.step`, "
         "`_com_Matriz_Gedeon.step`, `_com_Matriz_Gedeon_Certa.step`): a matriz e uma pasta, o conjunto e "
         "outra.\n")
w("07_CAD_Matrizes/README.md", "\n".join(t))

# ------------------------------------------------------------ 3. README da Gedeon ENTREGUE
w("07_CAD_Matrizes/Matriz_Gedeon_Entregue_HISTORICA/README.md",
  "# Matriz Gedeon ENTREGUE no CAD antigo (historica, nao fabricavel)\n\n"
  "Os quatro arquivos originais: `MatrizGedeon.step` (5 solidos que se atravessam), `MatrizGedeon_Body_A.step` "
  "(1 solido com **3 cascas** — o bolso do pino e cavidade selada dentro do aco), `MatrizGedeon_Body_B.step`, "
  "`MatrizGedeon_Canal_Fluxo.step` (213.790,0 mm³). A ∪ B = 469.156,8 mm³ de aco.\n\n"
  "Eles estao **fisicamente aqui** desde 2026-09-13; `02_CAD_Modelos_Historicos/` mantem atalhos com os mesmos "
  "bytes, porque a regra 2 do projeto fala dos modelos e o auditor le pelos caminhos selados no baseline. "
  "Ninguem escreve nesta pasta nem em `02_/`.\n\n"
  "## Para que ela serve hoje\n\n"
  "So como contraste com `Matriz_Gedeon_Certa/`, medida nos dois arquivos: secao em X = 0 de 5.885,5 mm² contra "
  "8.776,5 mm² na certa, mesmo envelope Ø 93,00 × Z 0..109,00, e 170.821,9 mm³ de aco que a entregue nao tem "
  "porque o funil da Jonatha foi escavado nela. Os numeros saem reimpressos a cada rodada do portao "
  "(`python3 04_Dados_SSOT_e_Scripts/gerar_gedeon_certa.py`) em "
  "`03_Relatorios_e_Documentacao/RELATORIO_GEDEON_CERTA.md` e em "
  "`07_CAD_Matrizes/Matriz_Gedeon_Certa/DESENHO_2D_GEDEON_CERTA_X_JONATHA.pdf`.\n\n"
  "A tentativa de 2026-09-12 de re-cortar o canal historico no arquivo do usuario foi **apagada de proposito** "
  "em 2026-09-13: ela tirava exatamente os 170.821,9 mm³ acima, e a matriz dele ja estava certa — nao havia "
  "canal a reconstruir. Nao ha script que a recrie, e nao ha de haver.\n")

# ------------------------------------------------------------ 4. ponteiros que apontavam para o que foi apagado
rep("04_Dados_SSOT_e_Scripts/desenhar_gedeon_consertada.py",
    [('"gedeon_corrigida.json"', '"gedeon_certa.json"'), ("`gedeon_corrigida.json`", "`gedeon_certa.json`")])
rep("04_Dados_SSOT_e_Scripts/cad_die_parameters.json", [
    ("04_Dados_SSOT_e_Scripts/gedeon_corrigida.json e 03_Relatorios_e_Documentacao/"
     "RELATORIO_GEDEON_CORRIGIDA.md, gerados por gerar_gedeon_corrigida.py que entrou na cadeia do portao",
     "04_Dados_SSOT_e_Scripts/gedeon_certa.json e 03_Relatorios_e_Documentacao/RELATORIO_GEDEON_CERTA.md, "
     "gerados por gerar_gedeon_certa.py, que entrou na cadeia do portao (a tentativa `*_corrigida` foi apagada "
     "em 2026-09-13)"),
    ('"04_Dados_SSOT_e_Scripts/gedeon_corrigida.json (canal_da_gedeon_confere)"',
     '"04_Dados_SSOT_e_Scripts/gedeon_certa.json (cavidade, cone_entrada, fenda)"'),
    ("Medido em gerar_gedeon_corrigida.py:",
     "Medido em gerar_gedeon_certa.py (a tentativa `gerar_gedeon_corrigida.py` foi apagada em 2026-09-13):")])
rep("03_Relatorios_e_Documentacao/AUDITORIA_GEOMETRICA_MATRIZ_JONATHA.md", [
    ("04_Dados_SSOT_e_Scripts/gedeon_corrigida.json e 03_Relatorios_e_Documentacao/"
     "RELATORIO_GEDEON_CORRIGIDA.md, gerados por gerar_gedeon_corrigida.py que entrou na cadeia do portao",
     "04_Dados_SSOT_e_Scripts/gedeon_certa.json e 03_Relatorios_e_Documentacao/RELATORIO_GEDEON_CERTA.md, "
     "gerados por gerar_gedeon_certa.py, que entrou na cadeia do portao. A tentativa `gerar_gedeon_corrigida.py` "
     "foi APAGADA em 2026-09-13 a pedido: `matrizGedeonCerta.step` e a Gedeon certa e nao havia canal a "
     "reconstruir; o confronto entre as duas Gedeon hoje e medido em `07_CAD_Matrizes/"
     "Matriz_Gedeon_Entregue_HISTORICA/`"),
    ("07_CAD_Matrizes/Matriz_Gedeon_Entregue_HISTORICA/DESENHO_2D_GEDEON_CONSERTADA_X_JONATHA.pdf",
     "07_CAD_Matrizes/Matriz_Gedeon_Certa/DESENHO_2D_GEDEON_CERTA_X_JONATHA.pdf")])
json.load(open(os.path.join(R, "04_Dados_SSOT_e_Scripts/cad_die_parameters.json"), encoding="utf-8"))
print("   SSOT ainda parseia")
sobra = subprocess.run(["bash", "-c", "cd %s && grep -rln 'gedeon_corrigida\\|Corrigida\\|CONSERTADA' "
                        "--include=*.py --include=*.md --include=*.json . | grep -v 05_Interface" % R],
                       capture_output=True, text=True).stdout.strip()
print("4) ainda citam a refutada:", sobra or "nada fora da zona congelada")
