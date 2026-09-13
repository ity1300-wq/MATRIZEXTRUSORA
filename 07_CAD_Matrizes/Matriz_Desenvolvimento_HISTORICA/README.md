# M06 — Matriz “Desenvolvimento” (histórica) — índice e medição

Origem (não movida, regra 2): `02_CAD_Modelos_Historicos/MatrizDesenvolvimento.step` e as variações
`_Body_A`, `_Body_B`, `_Canal_Fluxo`, `_Com_Fluxo`, `_Explodida`.

É a matriz do meio da série histórica — a que o desenho “030-032 cabeçote” traz por dentro do cabeçote com o
bolso Ø 95 (a banda da matriz desenhada com r 47,48/47,52 em Z 25,00..95,00) e o canal com 17,00 mm contra os
11,00 mm do furo. Essa divergência DXF × STEP está registrada como reconciliação em
`03_Relatorios_e_Documentacao/INTERFASE_CABECOTE_EX030.md`, não como erro de um dos dois.

Medição: `python 04_Dados_SSOT_e_Scripts/verify_legacy_dies.py` (reconstrói e confere as três históricas:
Copo, Desenvolvimento, Gedeon — sólidos, cascas, volumes e interferência contra o cabeçote).
