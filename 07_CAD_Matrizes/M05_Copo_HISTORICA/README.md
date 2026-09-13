# M05 — Matriz 1 “Copo” (histórica) — índice e medição

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
