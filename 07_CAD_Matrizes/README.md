# Matrizes — uma pasta por matriz

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
