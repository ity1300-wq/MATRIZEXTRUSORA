# Cabeçote EX-030

## `STEP/` — pasta dos desenhos STEP do cabeçote

Dois sólidos, gerados por `python 04_Dados_SSOT_e_Scripts/gerar_cabecote_ex030.py`
a partir do que foi medido no DWG (`04_Dados_SSOT_e_Scripts/cabecote_ex030.json`):

- `STEP/Cabecote_EX-030_sem_flange.step` — **o pedido**: o cabeçote sem a parte que conecta na extrusora (corpo Ø130 × 95,000 mm, nariz Ø80, degrau Ø90, bolso Ø95 × 70). 4,902 kg.
- `STEP/Cabecote_EX-030_desenhado.step` — como está no desenho: corpo Ø130 × 42, **chanfro 10 × 45°** na transição para a face do flange (Ø130 → Ø150), flange Ø220 × 40 com as 6 fendas de 23,5 e o resalto Ø203 × 3. Massa e volume medidos no sólido: `04_Dados_SSOT_e_Scripts/cabecote_step.json`.

O chanfro é cota do desenho e estava no SSOT (`corpo.chanfro` em `cabecote_ex030.json`) mas não estava no sólido; foi conferido hoje nas **duas** vistas de seção do DXF (aresta a 45,00° de (d 42,00; r 65,02) a (d 52,00; r 75,02), camada `contorno`) e medido no modelo depois de gerado. Onde este repositório tinha um "cubo Ø164" nessa faixa, a linha era a borda do furo Ø16 no C.C. Ø180 (82 = 90 − 8), não uma superfície da peça.

Referencial: Z é o eixo da matriz (face do nariz em Z = 95, face de entrada do cabeçote em Z = 0), então o arquivo monta direto com `01_CAD_MatrizJonatha_Oficial/MatrizJonatha_v28.step`.

## `STEP/estudos/` — cenários, não entregas

O que está aqui foi gerado para *ver*, não para *usar*: por exemplo
`python 04_Dados_SSOT_e_Scripts/gerar_cabecote_ex030.py --com-m12 --angulo-graus 90` abre o furo
transversal Ø12 no ângulo que o desenho não determina, e o gerador manda o resultado para cá em vez de
tocar nos dois STEP acima: na rodada de cenário os arquivos ganham sufixo `_M12` e o relatório e as mediações vão para a mesma pasta (`CABECOTE_EX-030_STEP_M12.md`, `cabecote_step_M12.json`), nunca para `03_Relatorios_e_Documentacao/`. A pasta está no `.gitignore` — cenário sem decisão aprovada não vira
entregável, e é recriável com um comando.

Medições, o que foi removido e o que ainda não está resolvido (fixação da junta, ângulo do M12):
`03_Relatorios_e_Documentacao/CABECOTE_EX-030_STEP.md`.
