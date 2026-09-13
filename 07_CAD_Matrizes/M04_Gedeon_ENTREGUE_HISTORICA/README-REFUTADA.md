# ESTA PASTA NÃO É ENTREGA DE FABRICAÇÃO — registro de uma tentativa refutada

Os STEP daqui foram gerados por `04_Dados_SSOT_e_Scripts/gerar_gedeon_corrigida.py`, que tratou
`02_CAD_Modelos_Historicos/matrizGedeonCerta.step` como bloco bruto e escavou nele o canal histórico
`MatrizGedeon_Canal_Fluxo.step` (213.790,0 mm³). Medido face por face, o arquivo do usuário já é a matriz
pronta: fenda 75,00 × 1,50 com R 0,75 atravessada de Z = 0,17 a Z = 109,00, cone de entrada abrindo em
Ø 75,60 na face traseira e os 2 furos de pino Ø 1,78 × 10,00. O re-corte tirava **170.821,9 mm³** de aço que
não é da Gedeon: 640.180,7 mm³ (arquivo dele) contra 469.358,8 mm³ (esta pasta).

Entrega válida: `../Gedeon_Certa/` (`gerar_gedeon_certa.py`) — mesmo arquivo dele, partido em Y = 0 só para
abrir as duas cavidades seladas no plano de partição, sem remover aço (A + B = o bloco ± 0,0004 mm³).

O que continua válido aqui é a medição dos arquivos históricos (o bolso selado no `Body_A`, o volume do canal,
a comparação com a v27), registrada em `04_Dados_SSOT_e_Scripts/gedeon_corrigida.json` e em
`03_Relatorios_e_Documentacao/RELATORIO_GEDEON_CORRIGIDA.md`.
