# Matriz 2 (Gedeon) reconstruída a partir do backup do usuário

> **REFUTADA em 2026-09-12, na mesma noite desta entrega.** Este relatório mede o que os
> arquivos históricos são, e continua sendo a fonte dessas medições — mas a reconstrução que ele
> descreve não é a matriz: escavar `MatrizGedeon_Canal_Fluxo.step` (213.790,0 mm³) em
> `matrizGedeonCerta.step` tirava **170.821,9 mm³** de aço que não é da Gedeon. O arquivo do usuário
> já é a matriz pronta (fenda 75,00 × 1,50 com R 0,75 atravessada, cone de entrada Ø 75,60, 2 furos
> de pino Ø 1,78 × 10,00). Entrega válida: `06_CAD_Cabecote_EX-030/STEP/Gedeon_Certa/`, gerada por
> `gerar_gedeon_certa.py`; os STEP desta tentativa foram movidos para
> `06_CAD_Cabecote_EX-030/STEP/Gedeon_Corrigida_REFUTADA/`.
Gerado por `04_Dados_SSOT_e_Scripts/gerar_gedeon_corrigida.py`. Todo número aqui é medição dos STEP
reimportados; `02_CAD_Modelos_Historicos/` foi aberto só para leitura (regra 2) e
`01_/MatrizJonatha.step` não foi tocado (regra 1). A reconstrução é `bloco do backup − canal da
própria Gedeon − pinos do próprio arquivo dele`, partida no plano Y = 0.

## Por que ela abria 'corrompida' (medido nos arquivos, não opinado)

| arquivo | sólidos | volume | cascas por sólido | válidos |
| :--- | ---: | ---: | :--- | :--- |
| `backup do usuario (matrizGedeonCerta.step)` | 1 | 640,180.7 mm³ | [3] | True |
| `MatrizGedeon.step (inteira)` | 5 | 683,248.4 mm³ | [1, 1, 1, 1, 1] | True |
| `MatrizGedeon_Body_A.step` | 1 | 234,332.8 mm³ | [3] | True |
| `MatrizGedeon_Body_B.step` | 1 | 234,823.9 mm³ | [1] | True |
| `MatrizGedeon_Canal_Fluxo.step` | 1 | 213,790.0 mm³ | [1] | True |
| `MatrizJonatha.step (v27, master)` | 2 | 469,001.7 mm³ | [3, 1] | True |
| `MatrizJonatha_Canal_Fluxo.step (v27)` | 3 | 214,246.7 mm³ | [1, 1, 1] | True |

- O backup (`matrizGedeonCerta.step`) é o **bloco inteiro sem escavar**: 640,180.7 mm³ contra 640,180.7 mm³ das duas metades brutas de `MatrizGedeon.step` (diferença 0.000 mm³). Não é uma matriz pronta: não tem canal, e tem as cavidades internas como cascas.
- `MatrizGedeon.step` (a inteira) são **5 sólidos que se atravessam** — as duas metades brutas, o funil de 43.017,9 mm³ e dois pinos de ~24,9 mm³. Corpo dentro de corpo com o vazio virando sólido: é isso que importador de STEP mostra como peça quebrada.
- `MatrizGedeon_Body_A.step` é **1 sólido com 3 cascas** — o `Body_B` tem 1. Casca interna é cavidade selada: não tem ferramenta que a faça, e é o mesmo mal do G-03 da auditoria.
- O `_Canal_Fluxo.step` da Gedeon **confere**: 213,790.0 mm³ contra 213,770.9 mm³ de funil ∪ cavidade cortada nas metades (sobra de 19.095 mm³ e 0.000 mm³ nos dois sentidos). **A P5 da triagem estava errada**: ela comparou o canal completo contra o funil só, que é o que está dentro de `MatrizGedeon.step`.

## Por que ela 'parece a Jonatha' — e em quanto ela é diferente

- **Aço**: par reconstruído 469,358.8 mm³ contra 469,001.7 mm³ da v27 — diferença de 357.1 mm³ (0.08 %). Booleano nos dois sentidos: par−v27 = 155.1 mm³, v27−par = 44.9 mm³.
- **Caminho do plástico**: canal da Gedeon 213,790.0 mm³ (1 sólido) contra 214,246.7 mm³ da v27, que vem espalhado em 3 sólidos (o G-05 da auditoria — é por isso que a comparação soma os três, em vez de pegar o maior) da v27; **Gedeon−Jonatha = 0.0 mm³** e Jonatha−Gedeon = 155.1 mm³. Ou seja: o canal da Gedeon cabe inteiro no da Jonatha, e a Jonatha é a Gedeon com 155.1 mm³ a mais de vazio na saída (o chanfro de 1,50 × 45°, anel medido em Z 107,50 → 109,00) e sem os bolsos de pino (44,9 mm³ na zona Z 44,50 → 64,50) (0.07 %). As duas são gêmeas de propósito: a exigência do projeto é envelope externo idêntico, e a caixa medida é a mesma (±46.50 × Z -0.00..109.00).
- Isso tem consequência prática e ela é dela, não do arquivo: o que a v28.1 propõe para a Jonatha (chanfro do master mantido, pinos conjugados, canal em 1 sólido) é exatamente o remédio que faltava na Gedeon. A Gedeon não precisa virar Jonatha; precisa ter bolso de pino aberto no plano de partição.

## O par reconstruído

- `Body_A`: 234,579.8 mm³, **1 casca**, 26 faces, válido: True. `Body_B`: 234,779.0 mm³, **1 casca**, 27 faces, válido: True.
- A ∩ B = **0.000000 mm³** (se tocam no plano de partição, não se sobrepõem); A ∩ canal = 0.000000 mm³ e B ∩ canal = 0.000000 mm³ (nenhum metal no caminho do plástico).
- Envelope: Ø93.00 × Z -0.00..109.00 — o mesmo do backup e do arquivo original, por construção (a única coisa removida do bloco é o canal e os bolsos de pino).
- Os pinos vêm do **próprio arquivo da Gedeon**: 2 sólidos de 10.00 mm de comprimento a Ø1,78, atravessando Y = 0 — por isso o bolso sai conjugado nas duas metades (o que a v28.1 faz por projeto, aqui é a geometria que já pedia).
- Diferença simétrica contra as metades que vieram no repositório: A 168.4 mm³, B 27.1 mm³ — é o bolso de pino aberto, nada mais.

## No cabeçote EX-030

- Com o encosto medido de 0.00 mm: ∩ com o cabeçote = 0.0000 / 0.0000 mm³ (A e B), face de saída em Z = 109.00 (+14.00 mm em relação à face do nariz).
- Os 3 sólidos do arquivo de montagem ficam separados de propósito: em bipartida, o plano de partição é o dado.

## Arquivos entregues

| peça | arquivo | bytes | sólidos | cascas por sólido | válidos |
| :--- | :--- | ---: | ---: | :--- | :--- |
| Body_A | `06_CAD_Cabecote_EX-030/STEP/Gedeon_Corrigida_REFUTADA/MatrizGedeon_Corrigida_Body_A.step` | 97,921 | 1 | [1] | True |
| Body_B | `06_CAD_Cabecote_EX-030/STEP/Gedeon_Corrigida_REFUTADA/MatrizGedeon_Corrigida_Body_B.step` | 119,785 | 1 | [1] | True |
| Canal_Fluxo | `06_CAD_Cabecote_EX-030/STEP/Gedeon_Corrigida_REFUTADA/MatrizGedeon_Corrigida_Canal_Fluxo.step` | 43,193 | 1 | [1] | True |
| Explodida | `06_CAD_Cabecote_EX-030/STEP/Gedeon_Corrigida_REFUTADA/MatrizGedeon_Corrigida_Explodida.step` | 268,553 | 5 | [1, 1, 1, 1, 1] | True |
| com o cabeçote | `06_CAD_Cabecote_EX-030/STEP/Gedeon_Corrigida_REFUTADA/Cabecote_EX-030_com_Matriz_Gedeon_Corrigida.step` | 274,036 | 3 | [1, 1, 1] | True |

## Números que o portão do projeto cobra deste JSON

Canal da Gedeon medido no arquivo: **213790,0 mm³** (o `_Canal_Fluxo.step` é o canal completo da Gedeon, não um resíduo da Jonatha). Ampliação que a Jonatha fez sobre esse canal: **155,1 mm³**. Os dois saem de `04_Dados_SSOT_e_Scripts/gedeon_corrigida.json`, gerados por `gerar_gedeon_corrigida.py`, e `verificar_cadeia.py` confere se este texto continua batendo com eles — se um mudar sem o outro, o portão fecha.

## O que isto não resolve

- O Ø90,00 reto do furo do cabeçote não desce sobre a banda Ø93 da matriz (faltam 1,50 mm de raio): a superfície de aperto do collete EX-031 continua por confirmar, e a pressão que fecha a bipartição é condicional a isso.
- Acesso axial dos cartuchos/termopares: folga −2,750 mm medida; sai com o nariz em Z ≥ 99,75 mm. É do cabeçote, não da matriz, e continua o único NC vivo do projeto.
- A Gedeon corrigida **não** substitui o master (regra 1) nem os históricos (regra 2): vive em `06_CAD_Cabecote_EX-030/STEP/Gedeon_Corrigida/` como peça de trabalho, e o que vale é o que o processo de auditoria aprovar.
