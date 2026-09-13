#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Escreve os READMEs da organizacao 07_CAD_Matrizes/ (2026-09-13) e atualiza o indice da raiz."""
import hashlib
import json
import os

R = "/home/user/MATRIZEXTRUSORA"
M = os.path.join(R, "07_CAD_Matrizes")


def sha(rel):
    return hashlib.sha256(open(os.path.join(R, rel), "rb").read()).hexdigest()


def grava(rel, txt):
    p = os.path.join(R, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8").write(txt)
    print("   ", rel)


def quantos_pastas():
    return sorted(d for d in os.listdir(M) if d.startswith("M"))


def main():
    m01 = "07_CAD_Matrizes/M01_Jonatha_v27_OFICIAL"
    passo = sha(os.path.join(m01, "MatrizJonatha.step"))
    bas = json.load(open(os.path.join(R, "05_Interface_Auditoria/baseline/MATRIZ_3_v27.json"), encoding="utf-8"))
    esperado = bas["hashes"]["01_CAD_MatrizJonatha_Oficial/MatrizJonatha.step"]
    assert passo == esperado, "o master mudou de conteudo! %s != %s" % (passo[:12], esperado[:12])
    print("master conferido byte a byte contra o baseline do auditor:", passo[:16], "... ✓")

    grava("07_CAD_Matrizes/README.md", """# Matrizes — uma pasta por matriz

Organização pedida em 2026-09-13. Cada matriz do projeto tem a sua pasta, com os STEP que a representam, a
prancha 2D quando existe, e um README dizendo de onde ela veio e qual comando a recria.

| pasta | matriz | o que é | origem |
|---|---|---|---|
| `M01_Jonatha_v27_OFICIAL/` | Jonatha v27.0 | **o modelo oficial (master)** — 6 STEP: corpo inteiro, A, B, canal, montagens | era `01_CAD_MatrizJonatha_Oficial/` |
| `M02_Jonatha_v28_PROPOSTA/` | Jonatha v28.1 | a proposta DFM (land 8,50 + chanfro 1,50 × 45°), **não promovida** | era `01_CAD_MatrizJonatha_Oficial/`, prefixo `_v28` |
| `M03_Gedeon_CERTA/` | Gedeon certa | a matriz do backup do usuário, partida em Y = 0, + prancha de 5 faixas | deriva de `02_/matrizGedeonCerta.step` (lido, não movido) |
| `M04_Gedeon_ENTREGUE_HISTORICA/` | Gedeon entregue | a que veio do CAD antigo, com bolso de pino selado — e a tentativa minha que estava errada | `02_/MatrizGedeon*.step` (regra 2: não se move) |
| `M05_Copo_HISTORICA/` | Matriz 1 “Copo” | a matriz do desenho original, usada como testemunha de interface | `02_/Matriz1_Original_Copo*.step` |
| `M06_MatrizDesenvolvimento_HISTORICA/` | Desenvolvimento | a terceira matriz histórica, medida no mesmo lote | `02_/MatrizDesenvolvimento*.step` |

**O que não se moveu, e por quê.** `02_CAD_Modelos_Historicos/` é intocável pela regra 2 do projeto — ler é
permitido, mover não. As três pastas históricas acima, portanto, contêm ponteiro + medição, não cópia.
`01_CAD_MatrizJonatha_Oficial/` continua existindo com **atalhos** (symlinks) para os seis arquivos do v27, para
que nada que referencia o caminho oficial — os vereditos e o baseline do auditor, o CODEOWNERS, o CI — quebre;
o arquivo físico é um só, e o portão confere o conteúdo por sha256, não o caminho.

**O que saiu do repositório nesta rodada** (tudo recriável; a lista foi aprovada por ele):

| removido | tamanho | recria com |
|---|---|---|
| `05_Variantes_Em_Estudo/ESTUDO_funil_coathanger_{Matriz,Canal_Fluxo}.step` | 3,8M | `python 04_Dados_SSOT_e_Scripts/estudar_funis.py` |
| `05_Variantes_Em_Estudo/ESTUDO_recuo_cartuchos_Z{9975,10025}_Body_{A,B}.step` | 1,0M | `python 04_Dados_SSOT_e_Scripts/estudar_recuo_cartuchos.py` |
| `07_CAD_Matrizes/M04_.../MatrizGedeon_Corrigida_*.step` (a tentativa refutada) | 800K | `python 04_Dados_SSOT_e_Scripts/gerar_gedeon_corrigida.py` — abre declarando a refutação |
| `03_Relatorios_e_Documentacao/V28_CONFERENCIA_VISUAL.png` | 2,1M | `python 04_Dados_SSOT_e_Scripts/renderizar_v28.py` |
| `06_CAD_Cabecote_EX-030/STEP/estudos/*M12*` (cenário do furo M12, já resolvido) | 144K | `python 04_Dados_SSOT_e_Scripts/gerar_cabecote_ex030.py --com-m12` |
| `MatrizJonatha_v28_{Explodida,Com_Fluxo}.step` e os PNG de conferência | 1,2M | derivados; ficaram no `.gitignore` e o portão os recria |

Os `.step` de montagem do cabeçote (`Cabecote_EX-030_com_Matriz_*.step`) continuam em
`06_CAD_Cabecote_EX-030/STEP/`: são entregável do cabeçote, não da matriz.

Verificação desta reorganização: `python 04_Dados_SSOT_e_Scripts/verificar_cadeia.py` (portão completo, re-roda
os 9 geradores e confere documento × JSON), cuja checagem [7] agora compara o sha256 do master com o baseline do
auditor em vez de olhar “git status limpo no caminho”.
""")

    grava(m01 + "/README.md", """# M01 — Matriz Jonatha v27.0 (o modelo oficial)

O master aprovado. Nada aqui é editado por decisão de projeto: é o ponto de partida de toda proposta.

| arquivo | o que é |
|---|---|
| `MatrizJonatha.step` | **o modelo oficial único** — 2 sólidos, 469.001,7 mm³ de aço, cascas [3, 1] |
| `MatrizJonatha_Body_A.step` · `_Body_B.step` | as duas metades, partidas no plano Y = 0 |
| `MatrizJonatha_Canal_Fluxo.step` | o funil próprio da v27, 213.945,1 mm³ |
| `MatrizJonatha_Explodida.step` · `_Com_Fluxo.step` | montagens de leitura (A + B + canal) |

sha256 do modelo oficial: `%s` — o mesmo número registrado em
`05_Interface_Auditoria/baseline/MATRIZ_3_v27.json`; é por conteúdo (não por caminho) que o portão
`verificar_cadeia.py`, checagem [7], garante a regra 1.

`01_CAD_MatrizJonatha_Oficial/` mantém, com o mesmo nome de arquivo, um atalho (symlink) para cada um destes
seis arquivos: quem referencia o caminho oficial — auditoria, CI, CODEOWNERS — continua achando os mesmos
bytes. O arquivo físico é um só.
""" % passo)

    grava("07_CAD_Matrizes/M02_Jonatha_v28_PROPOSTA/README.md", """# M02 — Matriz Jonatha v28.1 (proposta DFM, NÃO promovida)

É uma proposta em auditoria, não o modelo de trabalho. O master continua o v27.0 em `../M01_Jonatha_v27_OFICIAL/`.

Conteúdo: corpo inteiro, A, B, canal, pinos de alinhamento (os `_Explodida.step` e `_Com_Fluxo.step` que
existiam aqui saíram do repositório como derivados; `python 04_Dados_SSOT_e_Scripts/gerar_matriz_v28.py`
recria os sete, e o portão os regenera a cada rodada — estão no `.gitignore` de propósito).

O que a v28.1 muda, medido: fenda 75,00 × 1,50 com R 0,75 (112,0171 mm²), entrada restrita a Ø 75,60 em
Z = 0, land paralelo real 8,500 + chanfro 1,500 × 45°, lâmina de 0,750 mm no lábio, envelope Ø 93,00 × 69,90 /
Ø 89,50 × 10,80 / Ø 79,50 × 28,30 (Z total 109,000), 3,586 kg, ΔP 1D 41,9 bar, τ no land 163,8 kPa, abertura
da bipartição 55,7 kN.

**Consequência da mudança de pasta, avisada:** `05_Interface_Auditoria/propostas/PRP-0005-v28-1-fabricacao.json`
lista `arquivos[]` com `caminho` apontando para `01_CAD_MatrizJonatha_Oficial/MatrizJonatha_v28*.step`. esses
caminhos não têm atalho (só o v27 tem). Quando a auditoria for reaberta, isso se resolve nascendo `PRP-0006`
com os caminhos de `07_CAD_Matrizes/M02_Jonatha_v28_PROPOSTA/` — proposta auditada não se edita.
""")

    grava("07_CAD_Matrizes/M03_Gedeon_CERTA/README.md", """# M03 — Matriz Gedeon CERTA (o arquivo do usuário, inteiro)

`02_CAD_Modelos_Historicos/matrizGedeonCerta.step` medido face por face por
`python 04_Dados_SSOT_e_Scripts/gerar_gedeon_certa.py`: 1 sólido, 18 faces, **640.180,7 mm³**, 3 cascas,
BRepCheck válido — com a fenda **75,00 × 1,50 com R 0,75** atravessada de Z = 0,17 a Z = 109,00, o cone de
entrada abrindo em **Ø 75,60** na face traseira e fechando em Z = 20,98, e os **2 furos de pino
Ø 1,78 × 10,00** a |x| 40,61..42,39, Z 44,50..54,50. Caminho de fluxo medido (cone + fenda): 43.017,9 mm³.

Entregável desta pasta:

| arquivo | o que é |
|---|---|
| `MatrizGedeon_Certa_Body_A.step` · `_Body_B.step` | o mesmo aço, partido em Y = 0 — as duas cavidades seladas viram meia-cana aberta no plano de partição (único conserto: usinabilidade) |
| `MatrizGedeon_Certa_Canal_Fluxo.step` | o vazio real da matriz: cone de entrada + fenda atravessada |
| `MatrizGedeon_Certa_Explodida.step` | A + B + canal para leitura |
| `DESENHO_2D_GEDEON_CERTA_X_JONATHA.pdf` | prancha A3 de 5 faixas no mesmo escalonamento (cabeçote · Gedeon entregue · Gedeon certa · v27 · diferença hachurada) |
| `desenho_gedeon.json` | os números impressos na prancha, medidos no mesmo lote |

Nada foi escavado do arquivo dele: A + B = o bloco com diferença de 0,0004 mm³. Interface conferida na mesma
colocação medida: ∩ matriz × cabeçote = 0,0000 mm³; a face de saída da matriz fica 14,00 mm além da face do
cabeçote; aço do cabeçote dentro do cone + fenda = 0,0000 mm³. A montagem completa está em
`06_CAD_Cabecote_EX-030/STEP/Cabecote_EX-030_com_Matriz_Gedeon_Certa.step`.

Recriar tudo: `gerar_gedeon_certa.py` e depois `desenhar_gedeon_consertada.py --png` (com
`LD_LIBRARY_PATH` apontando para `04_Dados_SSOT_e_Scripts/.headless_gl`).
""")

    grava("07_CAD_Matrizes/M04_Gedeon_ENTREGUE_HISTORICA/README.md", """# M04 — Matriz Gedeon COMO ENTREGUE no CAD antigo (histórica, não fabricável)

A matriz dos arquivos históricos: `02_CAD_Modelos_Historicos/MatrizGedeon.step` (5 sólidos que se atravessam),
`MatrizGedeon_Body_A.step` (1 sólido com **3 cascas** — o bolso do pino é cavidade selada dentro do aço),
`MatrizGedeon_Body_B.step`, `MatrizGedeon_Canal_Fluxo.step` (213.790,0 mm³). A+B = 469.156,8 mm³ de aço.

**Estes arquivos não foram movidos para cá** — a regra 2 do projeto proíbe mexer em `02_CAD_Modelos_Historicos/`
(ler é permitido). Esta pasta é o índice e a medição, não a cópia.

Medidas que sustentam a comparação com a `M03_Gedeon_CERTA/`: seção em X = 0 de 5.885,5 mm² (contra 8.776,5 mm²
na certa), envelope Ø 93,00 × Z 0,1..109,00 nas duas, e a diferença de aço das peças inteiras:
170.821,9 mm³ que a Gedeon entregue não tem porque teve o funil da Jonatha escavado nela.

`README-REFUTADA.md` desta pasta declara a tentativa de 2026-09-12 (re-cortar o canal histórico no arquivo do
usuário), os números dela e o porquê de estar refutada. Os STEP daquela tentativa saíram do repositório;
`python 04_Dados_SSOT_e_Scripts/gerar_gedeon_corrigida.py` os recria aqui, abrindo com a refutação impressa, e
as medições ficam em `04_Dados_SSOT_e_Scripts/gedeon_corrigida.json` +
`03_Relatorios_e_Documentacao/RELATORIO_GEDEON_CORRIGIDA.md`.
""")

    grava("07_CAD_Matrizes/M05_Copo_HISTORICA/README.md", """# M05 — Matriz 1 “Copo” (histórica) — índice e medição

Origem (intocável pela regra 2, por isso não foi movida): `02_CAD_Modelos_Historicos/Matriz1_Original_Copo.step`
e as variações `_Body_A`, `_Body_B`, `_Canal_Fluxo`, `_Explodida`, `_Solido`.

Para que ela existe aqui: é a testemunha de interface que responde “a matriz casa nos estágios e passa pelo
nariz?”. Montagem medida: `06_CAD_Cabecote_EX-030/STEP/Cabecote_EX-030_com_Matriz_Copo.step`; ela sai em
Z = 80,70, protrusão −14,30 mm (fica dentro do nariz) — 28,30 mm a menos que a Gedeon, que é exatamente o
nariz que a Copo não tem.

Medição de perfil × cabeçote das cinco matrizes, incluindo esta:
`python 04_Dados_SSOT_e_Scripts/medir_perfis_matrizes_x_cabecote.py` → `perfis_matrizes_x_cabecote.json`.
Reconciliação do DXF do desenho (que traz a Copo dentro do cabeçote com cotas de desenho) com o STEP medido:
`03_Relatorios_e_Documentacao/INTERFASE_CABECOTE_EX030.md`.
""")

    grava("07_CAD_Matrizes/M06_MatrizDesenvolvimento_HISTORICA/README.md", """# M06 — Matriz “Desenvolvimento” (histórica) — índice e medição

Origem (não movida, regra 2): `02_CAD_Modelos_Historicos/MatrizDesenvolvimento.step` e as variações
`_Body_A`, `_Body_B`, `_Canal_Fluxo`, `_Com_Fluxo`, `_Explodida`.

É a matriz do meio da série histórica — a que o desenho “030-032 cabeçote” traz por dentro do cabeçote com o
bolso Ø 95 (a banda da matriz desenhada com r 47,48/47,52 em Z 25,00..95,00) e o canal com 17,00 mm contra os
11,00 mm do furo. Essa divergência DXF × STEP está registrada como reconciliação em
`03_Relatorios_e_Documentacao/INTERFASE_CABECOTE_EX030.md`, não como erro de um dos dois.

Medição: `python 04_Dados_SSOT_e_Scripts/verify_legacy_dies.py` (reconstrói e confere as três históricas:
Copo, Desenvolvimento, Gedeon — sólidos, cascas, volumes e interferência contra o cabeçote).
""")

    # --- indice da raiz: a arvore de pastas, com o 07_ e o choque de numeracao dos dois 05_
    P = os.path.join(R, "README.md")
    s = open(P, encoding="utf-8").read()
    anc = "├──  01_CAD_MatrizJonatha_Oficial/       -> ARQUIVOS CAD MASTER OFICIAIS (SSOT v27.0)"
    if anc in s:
        s = s.replace(anc,
                      "├── 📂 07_CAD_Matrizes/                      -> UMA PASTA POR MATRIZ (M01..M06, com README)\n"
                      "├── 📂 01_CAD_MatrizJonatha_Oficial/       -> atalhos com o mesmo conteudo do master (SSOT v27.0);\n"
                      "│                                           os arquivos físicos moram em 07_CAD_Matrizes/M01_...")
        open(P, "w", encoding="utf-8").write(s)
        print("    README.md (arvore de pastas atualizada)")
    print("READMEs gravados em:", ", ".join(quantos_pastas()))


main()
