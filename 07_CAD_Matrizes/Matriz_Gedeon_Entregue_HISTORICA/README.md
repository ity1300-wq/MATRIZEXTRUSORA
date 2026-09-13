# Matriz Gedeon ENTREGUE no CAD antigo (historica, nao fabricavel)

Os quatro arquivos originais: `MatrizGedeon.step` (5 solidos que se atravessam), `MatrizGedeon_Body_A.step` (1 solido com **3 cascas** — o bolso do pino e cavidade selada dentro do aco), `MatrizGedeon_Body_B.step`, `MatrizGedeon_Canal_Fluxo.step` (213.790,0 mm³). A ∪ B = 469.156,8 mm³ de aco.

Eles estao **fisicamente aqui** desde 2026-09-13; `02_CAD_Modelos_Historicos/` mantem atalhos com os mesmos bytes, porque a regra 2 do projeto fala dos modelos e o auditor le pelos caminhos selados no baseline. Ninguem escreve nesta pasta nem em `02_/`.

## Para que ela serve hoje

So como contraste com `Matriz_Gedeon_Certa/`, medida nos dois arquivos: secao em X = 0 de 5.885,5 mm² contra 8.776,5 mm² na certa, mesmo envelope Ø 93,00 × Z 0..109,00, e 171.024,0 mm³ de aco que a entregue nao tem porque o funil da Jonatha foi escavado nela (A ∪ B = 469.156,8 mm³ contra 640.180,7 mm³ da certa, medido hoje em `gerar_gedeon_certa.py` [8]). Os numeros saem reimpressos a cada rodada do portao (`python3 04_Dados_SSOT_e_Scripts/gerar_gedeon_certa.py`) em `03_Relatorios_e_Documentacao/RELATORIO_GEDEON_CERTA.md` e em `07_CAD_Matrizes/Matriz_Gedeon_Certa/DESENHO_2D_GEDEON_CERTA_X_JONATHA.pdf`.

A tentativa de 2026-09-12 de re-cortar o canal historico no arquivo do usuario foi **apagada de proposito** em 2026-09-13: ela tirava os 171.024,0 mm³ acima, e a matriz dele ja estava certa — nao havia canal a reconstruir. Nao ha script que a recrie, e nao ha de haver.
