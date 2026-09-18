# Matrizes — uma pasta por matriz

Regra da casa: **cada matriz tem a sua pasta**, com os arquivos dela dentro. Nem pasta vazia apontando para outro lugar, nem camada intermediaria entre aqui e a matriz — foi assim que o Jonatha pediu, em 2026-09-13.

| pasta | o que e | arquivos |
|---|---|---|
| `Matriz_Jonatha_v27_OFICIAL/` | **o master anterior** (SSOT v27.0, bipartido) — segue no disco, byte a byte, porque o baseline do auditor selou os caminhos e o portão confere o sha256; a promoção da v29.0 é declarada, não escrita por cima | `MatrizJonatha.step`, `_Body_A`, `_Body_B`, `_Canal_Fluxo`, `_Com_Fluxo`, `_Explodida` |
| `Matriz_Jonatha_v29_OFICIAL/` | **a master do projeto desde 2026-09-13** — a v27.0 como peça única (sem Bipartição, sem pino, sem junta), com o pacote de usinagem apontando para cá | `MATRIZ_V29_PECA_UNICA.step`, `MATRIZ_V29_CANAL_DE_FLUXO.step`, `CONJUNTO_MATRIZ_V29_NO_CABECOTE_EX-030.step`, `README.md` |
| `Matriz_Jonatha_v28_1_PROPOSTA/` | a variante DFM — **proposta, nao promovida** | os seis acima com `_v28_1`; `DESENHO_2D_V28.png` e derivado, fica no disco mas nao vai ao git |
| `Matriz_Jonatha_v27_Peca_Unica/` | **variante de peça única da v27.0** (as duas metades juntas, sem pinos, sem cavidade selada) — **não é o master** | `MatrizJonatha_v27_Peca_Unica.step`, `peca_unica_v27.json` |
| `Matriz_Gedeon_Certa/` | **a matriz do usuario**, entregue como esta, mais o que foi medido nela | `matrizGedeonCerta.step` (o arquivo dele, byte a byte), `MatrizGedeon_Certa_Body_A.step` e `_Body_B` (o par aberto no plano de particao), `MatrizGedeon_Certa_Explodida.step`, `DESENHO_2D_GEDEON_CERTA_X_JONATHA.pdf`, `desenho_gedeon.json` |
| `Matriz_Gedeon_Entregue_HISTORICA/` | a Gedeon **antiga**, a que veio do CAD do cabecote | `MatrizGedeon.step`, `_Body_A`, `_Body_B`, `_Canal_Fluxo` |
| `Matriz_Copo_HISTORICA/` | a matriz do desenho antigo (Copo) | `Matriz1_Original_Copo*.step` (4) |
| `Matriz_Desenvolvimento_HISTORICA/` | matriz de desenvolvimento | `MatrizDesenvolvimento*.step` (5) |

## Por que os caminhos antigos continuam valendo

As regras 1 e 2 do projeto falam dos **modelos**, nao do caminho. Entao `01_CAD_MatrizJonatha_Oficial/MatrizJonatha*.step` sao atalhos para dentro de `Matriz_Jonatha_v27_OFICIAL/`, e cada `.step` de `02_CAD_Modelos_Historicos/` e um atalho para a pasta da matriz correspondente. Quem abre pelo caminho antigo ve os mesmos bytes; `git ls-files -s 02_CAD_Modelos_Historicos/` mostra `120000` em cada linha, e o portao confere o sha256 de cada um dos caminhos selados em `05_Interface_Auditoria/baseline/MATRIZ_3_v27.json` a cada rodada. Escrever dentro de `02_/` continua fora de questao: os arquivos moram na pasta da matriz e o historico so se le.

## O que nao esta aqui, e o que foi apagado

| o que era | peso | por que |
|---|---|---|
| a **Gedeon corrigida** (gerador, JSON, relatorio, 5 STEP) | 800 KB | tentativa refutada em 2026-09-12 — `matrizGedeonCerta.step` e a Gedeon certa, nao havia canal a reconstruir; apagada por inteiro em 2026-09-13, a pedido |
| `05_/ESTUDO_JONATHA.step`, `ESTUDO_GEDEON.step` | 3,8 MB | estudo do coathanger respondido e gravado no JSON; recria com `python3 04_Dados_SSOT_e_Scripts/estudar_funis.py` |
| `05_/ESTUDO_GEDEON_REC_{COLADA,ENCAIXE_5,ENCAIXE_10}.step` | 1,0 MB | recria com `estudar_recuo_cartuchos.py` |
| os 2 STEP derivados `_Explodida`/`_Com_Fluxo` da v28 | 1,2 MB | derivados, e estao rastreados no git desde 2026-09-13 (pedido de nao deixar nada so no sandbox); os quatro STEP que vao para a fabrica estao na pasta |
| o cenario da furacao M12 em `06_/STEP/estudos/` | 144 KB | recria `python3 04_Dados_SSOT_e_Scripts/gerar_cabecote_ex030.py --com-m12` |

O **cabecote** e as montagens cabecote + matriz ficam em `06_CAD_Cabecote_EX-030/STEP/` (`Cabecote_EX-030_desenhado.step`, `_sem_flange.step`, `Cabecote_EX-030_com_Matriz_Copo.step`, `_com_Matriz_Gedeon.step`, `_com_Matriz_Gedeon_Certa.step`): a matriz e uma pasta, o conjunto e outra.
