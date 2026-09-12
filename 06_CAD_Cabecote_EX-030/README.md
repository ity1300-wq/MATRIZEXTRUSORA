# Cabeçote EX-030 em STEP

Dois sólidos, gerados por `python 04_Dados_SSOT_e_Scripts/gerar_cabecote_ex030.py`
a partir do que foi medido no DWG (`04_Dados_SSOT_e_Scripts/cabecote_ex030.json`):

- `Cabecote_EX-030_sem_flange.step` — **o pedido**: o cabeçote sem a parte que conecta na extrusora (corpo Ø130 × 95,000 mm, nariz Ø80, degrau Ø90, bolso Ø95 × 70). 4,902 kg.
- `Cabecote_EX-030_desenhado.step` — como está no desenho, com cubo, flange Ø220 e resalto. 13,531 kg.

Referencial: Z é o eixo da matriz (face do nariz em Z = 95, face de entrada do cabeçote em Z = 0), então o arquivo monta direto com `01_CAD_MatrizJonatha_Oficial/MatrizJonatha_v28.step`.

Medições, o que foi removido e o que ainda não está resolvido (fixação da junta, ângulo do M12):
`03_Relatorios_e_Documentacao/CABECOTE_EX-030_STEP.md`.
