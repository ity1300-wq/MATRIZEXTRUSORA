# M03 — Matriz Gedeon CERTA (o arquivo do usuário, inteiro)

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
