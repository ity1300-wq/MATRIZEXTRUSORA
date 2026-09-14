# Auditoria dos STEP — o que cada arquivo é e o que eles têm de bater entre si

Gerada por `04_Dados_SSOT_e_Scripts/auditar_step_correlacoes.py` (código de saída 1 se algo diverge, para entrar no portão). Cada número abaixo foi **medido no arquivo** na hora em que este relatório foi escrito, com `cadquery`, face por face: 70 arquivos STEP abertos. Status: **DIVERGENTE**.

## C1 — cota medida × SSOT (as seis peças inteiras)

| matriz | fenda L × e (mm) | R da borda | boca de entrada | estágios Ø × Z (mm) | comprimento | vazio (mm³) | borda da saída | aço (mm³) | massa (kg) | faces | divergência |
|---|---|---|---|---|---|---|---|---|
| `matriz_1_copo_historica` | 75.000 × 1.500 | 0.75 | Ø 75.60 | Ø93.00 Z 0.00..69.90 · Ø89.50 Z 69.90..80.70 · Ø75.60 Z 0.00..70.70 | 80.70 | 318480,7 | meia-lua (R = espessura/2) | 224289,0 | 1.7607 | 24 | {"envelope": "informativo: [[[75.6, 0.0, 70.7], [79.5, 80.7, 109.0]]]", "comprimento": "informativo: [80.7, 109.0]", "nota": "histórica: medida, mas não cobrada pelo contrato (só a fenda)"} |
| `desenvolvimento_historica` | 75.000 × 1.500 | 0.75 | Ø 75.00 | Ø93.00 Z 0.00..69.90 · Ø89.50 Z 69.90..80.70 · Ø79.50 Z 80.70..109.00 | 109.00 | 155370,4 | canto vivo (retangular) | 527576,4 | 4.1415 | 36 | bate |
| `gedeon_certa_arquivo_do_usuario` | 75.000 × 1.500 | 0.75 | Ø 75.60 | Ø93.00 Z 0.00..69.90 · Ø89.50 Z 69.90..80.70 · Ø79.50 Z 80.70..109.00 | 109.00 | 43017,9 | meia-lua (R = espessura/2) | 640180,7 | 5.0254 | 18 | bate |
| `gedeon_entregue_historica` | 75.000 × 1.500 | 0.75 | — | Ø93.00 Z 0.00..69.90 · Ø89.50 Z 69.90..80.70 · Ø79.50 Z 80.70..109.00 | 109.00 | 24,9 | — | 683248,4 | 5.3635 | 51 | bate |
| `jonatha_v27_oficial` | 75.000 × 1.500 | 0.75 | Ø 75.60 | Ø93.00 Z 0.00..69.90 · Ø89.50 Z 69.90..80.70 · Ø79.50 Z 80.70..109.00 | 109.00 | 213945,1 | meia-lua (R = espessura/2) | 469001,7 | 3.6817 | 43 | bate |
| `jonatha_v27_peca_unica` | 75.000 × 1.500 | 0.75 | Ø 75.60 | Ø93.00 Z 0.00..69.90 · Ø89.50 Z 69.90..80.70 · Ø79.50 Z 80.70..109.00 | 109.00 | 213945,1 | meia-lua (R = espessura/2) | 469303,2 | 3.6840 | 22 | bate |
| `jonatha_v28_1_proposta` | 75.000 × 1.500 | 0.75 | Ø 75.60 | Ø93.00 Z 0.00..69.90 · Ø89.50 Z 69.90..80.70 · Ø79.50 Z 80.70..109.00 | 109.00 | 213945,1 | meia-lua (R = espessura/2) | 456796,5 | 3.5859 | 82 | bate |

Tolerâncias cobradas: largura ±0.05, espessura ±0.02, raio ±0.02, boca +0.10/−0.10, envelope ±0.05 mm (ou seja: a metade do que o desenho autoriza). `sem fenda fechada` é legítimo nas peças históricas, que são cinco sólidos que se atravessam e não têm a fenda como face única.

## C2 — metade × metade × peça inteira, e C3 — o `_Canal_Fluxo.step` é o vazio real?

| matriz | A (mm³) | B (mm³) | A+B − (A∪B) | A ∩ B | cascas A/B | cavidade selada | canal do arquivo (mm³) | vazio medido (mm³) | Δ% | leitura |
|---|---|---|---|---|---|---|---|---|---|
| `matriz_1_copo_historica` | 112144,5 | 112144,5 | -0,0000 | 0,0000 | 1/1 | não | 318480,7 | 318480,7 | 0,000 | o arquivo do canal e o vazio da peca |
| `desenvolvimento_historica` | 263637,4 | 263939,0 | 0,0000 | 0,0000 | 1/1 | não | 155370,4 | 155370,4 | 0,000 | o arquivo do canal e o vazio da peca |
| `gedeon_certa_arquivo_do_usuario` | 320090,4 | 320090,4 | -0,0000 | 0,0000 | 1/1 | não | 43017,9 | 43017,9 | 0,000 | o arquivo do canal e o vazio da peca |
| `gedeon_entregue_historica` | 234332,8 | 234823,9 | 0,0000 | 0,0000 | 3/1 | SIM | 213790,0 | 24,9 | 858494,378 | o arquivo do canal NAO e o vazio desta peca |
| `jonatha_v27_oficial` | 234255,3 | 234746,4 | 0,0000 | 0,0000 | 3/1 | SIM | 214246,7 | 213945,1 | 0,141 | o arquivo do canal e o vazio da peca |
| `jonatha_v27_peca_unica` | 0,0 | 0,0 | 0,0000 | 0,0000 | —/— | não | — | — | — | — |
| `jonatha_v28_1_proposta` | 228299,5 | 228497,1 | -0,0316 | 0,0000 | 1/1 | não | 213945,1 | 213945,1 | 0,000 | o arquivo do canal e o vazio da peca |

Casca > 1 num `Body` = cavidade selada dentro do aço, sem ferramenta que a faça: é o G-03 da auditoria de 2026-09-11, presente no `Body_A` da Gedeon entregue e no `MatrizJonatha.step`. E a coluna do canal é a correlação que derrubou a "Gedeon corrigida": o `_Canal_Fluxo.step` histórico carrega o funil da Jonatha, não o vazio da Gedeon.

## C4 — matriz × cabeçote: folga radial, anel de fuga, encosto

Cabeçote medido: `06_CAD_Cabecote_EX-030/STEP/Cabecote_EX-030_desenhado.step` (1570339,5 mm³, 12.327 kg), furo em escada Ø105.00 Z 0.00..3.00 · Ø95.00 Z 0.00..70.00 · Ø90.00 Z 70.00..81.00 · Ø80.00 Z 81.00..95.00, face do nariz em Z = 95.00.

| matriz | folga radial por estágio (mm) | menor folga | anel de fuga contínuo? | área do anel (mm²) | comprimento do anel (mm) | saída além do nariz (mm) | ∩ com o cabeçote (mm³) |
|---|---|---|---|---|---|---|---|
| `matriz_1_copo_historica` | +1.00 / +0.25 / +7.20 | 0.25 | **SIM — caminho livre para trás** | 2238.7 | 151.40 | -14.30 | 0,0000 |
| `desenvolvimento_historica` | +1.00 / +0.25 / +0.25 | 0.25 | **SIM — caminho livre para trás** | 428.4 | 109.00 | +14.00 | 0,0000 |
| `gedeon_certa_arquivo_do_usuario` | +1.00 / +0.25 / +0.25 | 0.25 | **SIM — caminho livre para trás** | 428.4 | 109.00 | +14.00 | 0,0000 |
| `gedeon_entregue_historica` | +1.00 / +0.25 / +0.25 | 0.25 | **SIM — caminho livre para trás** | 428.4 | 109.00 | +14.00 | 0,0000 |
| `jonatha_v27_oficial` | +1.00 / +0.25 / +0.25 | 0.25 | **SIM — caminho livre para trás** | 428.4 | 109.00 | +14.00 | 0,0000 |
| `jonatha_v27_peca_unica` | +1.00 / +0.25 / +0.25 | 0.25 | **SIM — caminho livre para trás** | 428.4 | 109.00 | +14.00 | 0,0000 |
| `jonatha_v28_1_proposta` | +1.00 / +0.25 / +0.25 | 0.25 | **SIM — caminho livre para trás** | 428.4 | 109.00 | +14.00 | 0,0000 |

`anel de fuga contínuo` = existe anel com folga > 0 entre a OD da matriz e o furo do cabeçote, sem pinça, do bico até a face de entrada da matriz. Onde isso é verdadeiro, o mastique **não é obrigado** a passar pela fenda: a rota de trás (para o funil de alimentação) existe e é mais curta que a fenda. É a correlação geométrica que abre a pergunta da simulação.

## C5 — montagem × peças de origem

| montagem | sólidos | volume somado (mm³) | massa (kg) | metal da matriz (mm³) | caixa Ø × Z | válido |
|---|---|---|---|---|---|---|---|
| `Cabecote_EX-030_com_Matriz_Copo.step` | 2 | 1794628,5 | 14.088 | 224289,0 | Ø220.0 × 95.0 | sim |
| `Cabecote_EX-030_com_Matriz_Desenvolvimento.step` | 3 | 2097915,9 | 16.469 | 527576,4 | Ø220.0 × 109.0 | sim |
| `Cabecote_EX-030_com_Matriz_Gedeon.step` | 3 | 2039496,3 | 16.010 | 469156,8 | Ø220.0 × 109.0 | sim |
| `Cabecote_EX-030_com_Matriz_Gedeon_Certa.step` | 2 | 2210520,2 | 17.353 | 640180,7 | Ø220.0 × 109.0 | sim |
| `Cabecote_EX-030_com_Matriz_Jonatha_v27.step` | 3 | 2039341,1 | 16.009 | 469001,7 | Ø220.0 × 109.0 | sim |
| `Cabecote_EX-030_com_Matriz_Jonatha_v27_Peca_Unica.step` | 2 | 2039642,7 | 16.011 | 469303,2 | Ø220.0 × 109.0 | sim |
| `Cabecote_EX-030_com_Matriz_Jonatha_v28_1.step` | 3 | 2027136,0 | 15.913 | 456796,5 | Ø220.0 × 109.0 | **NÃO** |

Toda montagem é o cabeçote **completo com flange** (`Cabecote_EX-030_desenhado.step`) com a matriz sentada no degrau, entregue sem booleano: `1 cabeçote + N` sólidos, onde N é o que o arquivo da matriz tem mesmo (a Gedeon CERTA é 1 sólido; o par bipartido e a v27 são 2; a Gedeon histórica é 2 metades).

## C7 — saúde topológica: BRepCheck em cada sólido, cara e aresta

| arquivo | sólidos | faces | faces inválidas | arestas inválidas | cascas | volume (mm³) |
|---|---|---|---|---|---|---|---|
| `matriz_1_copo_historica` | 2 | 12 | 0 | 0 | 1 | 112144,5 |
| `matriz_1_copo_historica` | 2 | 12 | 0 | 0 | 1 | 112144,5 |
| `matriz_1_copo_historica_Body_A` | 1 | 12 | 0 | 0 | 1 | 112144,5 |
| `matriz_1_copo_historica_Body_B` | 1 | 12 | 0 | 0 | 1 | 112144,5 |
| `matriz_1_copo_historica_Canal_Fluxo` | 1 | 8 | 0 | 0 | 1 | 318480,7 |
| `desenvolvimento_historica` | 2 | 20 | 0 | 0 | 1 | 263637,4 |
| `desenvolvimento_historica` | 2 | 16 | 0 | 0 | 1 | 263939,0 |
| `desenvolvimento_historica_Body_A` | 1 | 20 | 0 | 0 | 1 | 263637,4 |
| `desenvolvimento_historica_Body_B` | 1 | 16 | 0 | 0 | 1 | 263939,0 |
| `desenvolvimento_historica_Canal_Fluxo` | 1 | 12 | 0 | 0 | 1 | 155370,4 |
| `gedeon_certa_arquivo_do_usuario` | 1 | 18 | 0 | 0 | 3 | 640180,7 |
| `gedeon_entregue_historica` | 5 | 19 | 0 | 0 | 1 | 320090,4 |
| `gedeon_entregue_historica` | 5 | 19 | 0 | 0 | 1 | 320090,4 |
| `gedeon_entregue_historica` | 5 | 3 | 0 | 0 | 1 | 24,9 |
| `gedeon_entregue_historica` | 5 | 3 | 0 | 0 | 1 | 24,9 |
| `gedeon_entregue_historica` | 5 | 7 | 0 | 0 | 1 | 43017,9 |
| `gedeon_entregue_historica_Body_A` | 1 | 25 | 0 | 0 | 3 | 234332,8 |
| `gedeon_entregue_historica_Body_B` | 1 | 18 | 0 | 0 | 1 | 234823,9 |
| `gedeon_entregue_historica_Canal_Fluxo` | 1 | 14 | 0 | 0 | 1 | 213790,0 |
| `jonatha_v27_oficial` | 2 | 25 | 0 | 0 | 3 | 234255,3 |
| `jonatha_v27_oficial` | 2 | 18 | 0 | 0 | 1 | 234746,4 |
| `jonatha_v27_oficial_Body_A` | 1 | 25 | 0 | 0 | 3 | 234255,3 |
| `jonatha_v27_oficial_Body_B` | 1 | 18 | 0 | 0 | 1 | 234746,4 |
| `jonatha_v27_oficial_Canal_Fluxo` | 3 | 17 | 0 | 0 | 1 | 213945,1 |
| `jonatha_v27_oficial_Canal_Fluxo` | 3 | 3 | 0 | 0 | 1 | 150,8 |
| `jonatha_v27_oficial_Canal_Fluxo` | 3 | 3 | 0 | 0 | 1 | 150,8 |
| `jonatha_v27_peca_unica` | 1 | 22 | 0 | 0 | 1 | 469303,2 |
| `jonatha_v28_1_proposta` | 2 | 39 | 0 | 0 | 1 | 228299,5 |
| `jonatha_v28_1_proposta` | 2 | 43 | 1 | 0 | 1 | 228497,1 |
| `jonatha_v28_1_proposta_Body_A` | 1 | 39 | 0 | 0 | 1 | 228299,5 |
| `jonatha_v28_1_proposta_Body_B` | 1 | 43 | 1 | 0 | 1 | 228497,1 |
| `jonatha_v28_1_proposta_Canal_Fluxo` | 1 | 20 | 1 | 0 | 1 | 213945,1 |

Achados: jonatha_v28_1_proposta: 1 cara(s) e 0 aresta(s) inválidas em 07_CAD_Matrizes/Matriz_Jonatha_v28_1_PROPOSTA/MatrizJonatha_v28.step (centro [37.02, 0.56, 99.0]); jonatha_v28_1_proposta_Body_B: 1 cara(s) e 0 aresta(s) inválidas em 07_CAD_Matrizes/Matriz_Jonatha_v28_1_PROPOSTA/MatrizJonatha_v28_Body_B.step (centro [37.02, 0.56, 99.0]); jonatha_v28_1_proposta_Canal_Fluxo: 1 cara(s) e 0 aresta(s) inválidas em 07_CAD_Matrizes/Matriz_Jonatha_v28_1_PROPOSTA/MatrizJonatha_v28_Canal_Fluxo.step (centro [37.02, 0.56, 99.0])

## C6 — atalhos e baseline selado

22 caminhos de MODELO selados pelo auditor conferidos byte a byte; divergências: **nenhuma**. Fora do escopo desta checagem (script e JSON do baseline, que esta sessão re-escreveu de propósito; re-selá-los é ato da auditoria): `04_Dados_SSOT_e_Scripts/cad_die_parameters.json`, `04_Dados_SSOT_e_Scripts/cfd_edge_relief.py`, `04_Dados_SSOT_e_Scripts/cfd_land_crosssection.py`, `04_Dados_SSOT_e_Scripts/setup_cfd_env.sh`, `04_Dados_SSOT_e_Scripts/setup_headless_gl.sh`, `04_Dados_SSOT_e_Scripts/verify_geometry_ssot.py`, `04_Dados_SSOT_e_Scripts/verify_legacy_dies.py`, `05_Interface_Auditoria/PROTOCOLO_AUDITORIA.md`, `05_Interface_Auditoria/esquema/proposta.schema.json`, `05_Interface_Auditoria/esquema/veredito.schema.json`, `05_Interface_Auditoria/scripts/auditar_proposta.py`, `05_Interface_Auditoria/scripts/monitor_auditoria.py`, `05_Interface_Auditoria/scripts/painel_auditoria.py`.

## Inventário completo (um bloco por arquivo)

| arquivo | sólidos | cascas | faces | volume (mm³) | caixa Z | fenda | boca | estágios |
|---|---|---|---|---|---|---|---|
| `01_CAD_MatrizJonatha_Oficial/MatrizJonatha.step` | 2 | 3/1 | 43 | 469001,7 | -0.00..109.00 | — | — | — |
| `01_CAD_MatrizJonatha_Oficial/MatrizJonatha_Body_A.step` | 1 | 3 | 25 | 234255,3 | -0.00..109.00 | — | — | — |
| `01_CAD_MatrizJonatha_Oficial/MatrizJonatha_Body_B.step` | 1 | 1 | 18 | 234746,4 | -0.00..109.00 | — | — | — |
| `01_CAD_MatrizJonatha_Oficial/MatrizJonatha_Canal_Fluxo.step` | 3 | 1/1/1 | 23 | 214246,7 | -0.00..109.00 | — | — | — |
| `01_CAD_MatrizJonatha_Oficial/MatrizJonatha_Com_Fluxo.step` | 5 | 3/1/1/1/1 | 66 | 683248,4 | -0.00..109.00 | — | — | — |
| `01_CAD_MatrizJonatha_Oficial/MatrizJonatha_Explodida.step` | 2 | 3/1 | 43 | 469001,7 | -0.00..109.00 | — | — | — |
| `02_CAD_Modelos_Historicos/Matriz1_Original_Copo.step` | 2 | 1/1 | 24 | 224289,0 | 0.00..80.70 | — | — | — |
| `02_CAD_Modelos_Historicos/Matriz1_Original_Copo_Body_A.step` | 1 | 1 | 12 | 112144,5 | 0.00..80.70 | — | — | — |
| `02_CAD_Modelos_Historicos/Matriz1_Original_Copo_Body_B.step` | 1 | 1 | 12 | 112144,5 | 0.00..80.70 | — | — | — |
| `02_CAD_Modelos_Historicos/Matriz1_Original_Copo_Canal_Fluxo.step` | 1 | 1 | 8 | 318480,7 | 0.00..80.70 | — | — | — |
| `02_CAD_Modelos_Historicos/Matriz1_Original_Copo_Explodida.step` | 2 | 1/1 | 24 | 224289,0 | 0.00..80.70 | — | — | — |
| `02_CAD_Modelos_Historicos/Matriz1_Original_Copo_Solido.step` | 1 | 1 | 11 | 224289,0 | 0.00..80.70 | — | — | — |
| `02_CAD_Modelos_Historicos/MatrizDesenvolvimento.step` | 2 | 1/1 | 36 | 527576,4 | -0.00..109.00 | — | — | — |
| `02_CAD_Modelos_Historicos/MatrizDesenvolvimento_Body_A.step` | 1 | 1 | 20 | 263637,4 | -0.00..109.00 | — | — | — |
| `02_CAD_Modelos_Historicos/MatrizDesenvolvimento_Body_B.step` | 1 | 1 | 16 | 263939,0 | -0.00..109.00 | — | — | — |
| `02_CAD_Modelos_Historicos/MatrizDesenvolvimento_Canal_Fluxo.step` | 1 | 1 | 12 | 155370,4 | -0.00..109.00 | — | — | — |
| `02_CAD_Modelos_Historicos/MatrizDesenvolvimento_Com_Fluxo.step` | 3 | 1/1/1 | 48 | 682946,8 | -0.00..109.00 | — | — | — |
| `02_CAD_Modelos_Historicos/MatrizDesenvolvimento_Explodida.step` | 2 | 1/1 | 36 | 527576,4 | -0.00..109.00 | — | — | — |
| `02_CAD_Modelos_Historicos/MatrizGedeon.step` | 5 | 1/1/1/1/1 | 51 | 683248,4 | -0.00..109.00 | — | — | — |
| `02_CAD_Modelos_Historicos/MatrizGedeon_Body_A.step` | 1 | 3 | 25 | 234332,8 | -0.00..109.00 | — | — | — |
| `02_CAD_Modelos_Historicos/MatrizGedeon_Body_B.step` | 1 | 1 | 18 | 234823,9 | -0.00..109.00 | — | — | — |
| `02_CAD_Modelos_Historicos/MatrizGedeon_Canal_Fluxo.step` | 1 | 1 | 14 | 213790,0 | -0.00..109.00 | — | — | — |
| `02_CAD_Modelos_Historicos/matrizGedeonCerta.step` | 1 | 3 | 18 | 640180,7 | -0.00..109.00 | — | — | — |
| `06_CAD_Cabecote_EX-030/STEP/Cabecote_EX-030_com_Matriz_Copo.step` | 2 | 1/1 | 30 | 1794628,5 | 0.00..95.00 | — | — | — |
| `06_CAD_Cabecote_EX-030/STEP/Cabecote_EX-030_com_Matriz_Desenvolvimento.step` | 3 | 1/1/1 | 55 | 2097915,9 | -0.00..109.00 | — | — | — |
| `06_CAD_Cabecote_EX-030/STEP/Cabecote_EX-030_com_Matriz_Gedeon.step` | 3 | 1/3/1 | 62 | 2039496,3 | -0.00..109.00 | — | — | — |
| `06_CAD_Cabecote_EX-030/STEP/Cabecote_EX-030_com_Matriz_Gedeon_Certa.step` | 2 | 1/3 | 37 | 2210520,2 | -0.00..109.00 | — | — | — |
| `06_CAD_Cabecote_EX-030/STEP/Cabecote_EX-030_com_Matriz_Jonatha_v27.step` | 3 | 1/3/1 | 62 | 2039341,1 | -0.00..109.00 | — | — | — |
| `06_CAD_Cabecote_EX-030/STEP/Cabecote_EX-030_com_Matriz_Jonatha_v27_Peca_Unica.step` | 2 | 1/1 | 41 | 2039642,7 | -0.00..109.00 | — | — | — |
| `06_CAD_Cabecote_EX-030/STEP/Cabecote_EX-030_com_Matriz_Jonatha_v28_1.step` | 3 | 1/1/1 | 101 | 2027136,0 | -0.00..109.00 | — | — | — |
| `06_CAD_Cabecote_EX-030/STEP/Cabecote_EX-030_desenhado.step` | 1 | 1 | 19 | 1570339,5 | 0.00..95.00 | — | — | — |
| `06_CAD_Cabecote_EX-030/STEP/Cabecote_EX-030_sem_flange.step` | 1 | 1 | 11 | 610588,2 | 0.00..95.00 | — | — | — |
| `06_CAD_Cabecote_EX-030/STEP/estudos/Cabecote_EX-030_desenhado_M12.step` | 1 | 1 | 19 | 1662551,3 | 0.00..95.00 | — | — | — |
| `06_CAD_Cabecote_EX-030/STEP/estudos/Cabecote_EX-030_sem_flange_M12.step` | 1 | 1 | 11 | 620465,2 | -0.00..95.00 | — | — | — |
| `07_CAD_Matrizes/Matriz_Copo_HISTORICA/Matriz1_Original_Copo.step` | 2 | 1/1 | 24 | 224289,0 | 0.00..80.70 | 75.000×1.500 | Ø75.60 | Ø93.00 · Ø89.50 · Ø75.60 |
| `07_CAD_Matrizes/Matriz_Copo_HISTORICA/Matriz1_Original_Copo_Body_A.step` | 1 | 1 | 12 | 112144,5 | 0.00..80.70 | — | — | — |
| `07_CAD_Matrizes/Matriz_Copo_HISTORICA/Matriz1_Original_Copo_Body_B.step` | 1 | 1 | 12 | 112144,5 | 0.00..80.70 | — | — | — |
| `07_CAD_Matrizes/Matriz_Copo_HISTORICA/Matriz1_Original_Copo_Canal_Fluxo.step` | 1 | 1 | 8 | 318480,7 | 0.00..80.70 | — | — | — |
| `07_CAD_Matrizes/Matriz_Copo_HISTORICA/Matriz1_Original_Copo_Explodida.step` | 2 | 1/1 | 24 | 224289,0 | 0.00..80.70 | — | — | — |
| `07_CAD_Matrizes/Matriz_Copo_HISTORICA/Matriz1_Original_Copo_Solido.step` | 1 | 1 | 11 | 224289,0 | 0.00..80.70 | — | — | — |
| `07_CAD_Matrizes/Matriz_Desenvolvimento_HISTORICA/MatrizDesenvolvimento.step` | 2 | 1/1 | 36 | 527576,4 | -0.00..109.00 | 75.000×1.500 | Ø75.00 | Ø93.00 · Ø89.50 · Ø79.50 |
| `07_CAD_Matrizes/Matriz_Desenvolvimento_HISTORICA/MatrizDesenvolvimento_Body_A.step` | 1 | 1 | 20 | 263637,4 | -0.00..109.00 | — | — | — |
| `07_CAD_Matrizes/Matriz_Desenvolvimento_HISTORICA/MatrizDesenvolvimento_Body_B.step` | 1 | 1 | 16 | 263939,0 | -0.00..109.00 | — | — | — |
| `07_CAD_Matrizes/Matriz_Desenvolvimento_HISTORICA/MatrizDesenvolvimento_Canal_Fluxo.step` | 1 | 1 | 12 | 155370,4 | -0.00..109.00 | — | — | — |
| `07_CAD_Matrizes/Matriz_Desenvolvimento_HISTORICA/MatrizDesenvolvimento_Com_Fluxo.step` | 3 | 1/1/1 | 48 | 682946,8 | -0.00..109.00 | — | — | — |
| `07_CAD_Matrizes/Matriz_Desenvolvimento_HISTORICA/MatrizDesenvolvimento_Explodida.step` | 2 | 1/1 | 36 | 527576,4 | -0.00..109.00 | — | — | — |
| `07_CAD_Matrizes/Matriz_Gedeon_Certa/Cabecote_EX-030_com_Matriz_Gedeon_Certa.step` | 2 | 1/3 | 29 | 1250768,9 | -0.00..109.00 | — | — | — |
| `07_CAD_Matrizes/Matriz_Gedeon_Certa/MatrizGedeon_Certa_Body_A.step` | 1 | 1 | 19 | 320090,4 | -0.00..109.00 | — | — | — |
| `07_CAD_Matrizes/Matriz_Gedeon_Certa/MatrizGedeon_Certa_Body_B.step` | 1 | 1 | 19 | 320090,4 | -0.00..109.00 | — | — | — |
| `07_CAD_Matrizes/Matriz_Gedeon_Certa/MatrizGedeon_Certa_Canal_Fluxo.step` | 1 | 1 | 7 | 43017,9 | -0.00..109.00 | — | — | — |
| `07_CAD_Matrizes/Matriz_Gedeon_Certa/MatrizGedeon_Certa_Explodida.step` | 1 | 3 | 13 | 683198,6 | 0.00..109.00 | — | — | — |
| `07_CAD_Matrizes/Matriz_Gedeon_Certa/matrizGedeonCerta.step` | 1 | 3 | 18 | 640180,7 | -0.00..109.00 | 75.000×1.500 | Ø75.60 | Ø93.00 · Ø89.50 · Ø79.50 |
| `07_CAD_Matrizes/Matriz_Gedeon_Entregue_HISTORICA/MatrizGedeon.step` | 5 | 1/1/1/1/1 | 51 | 683248,4 | -0.00..109.00 | 75.000×1.500 | — | Ø93.00 · Ø89.50 · Ø79.50 |
| `07_CAD_Matrizes/Matriz_Gedeon_Entregue_HISTORICA/MatrizGedeon_Body_A.step` | 1 | 3 | 25 | 234332,8 | -0.00..109.00 | — | — | — |
| `07_CAD_Matrizes/Matriz_Gedeon_Entregue_HISTORICA/MatrizGedeon_Body_B.step` | 1 | 1 | 18 | 234823,9 | -0.00..109.00 | — | — | — |
| `07_CAD_Matrizes/Matriz_Gedeon_Entregue_HISTORICA/MatrizGedeon_Canal_Fluxo.step` | 1 | 1 | 14 | 213790,0 | -0.00..109.00 | — | — | — |
| `07_CAD_Matrizes/Matriz_Jonatha_v27_OFICIAL/MatrizJonatha.step` | 2 | 3/1 | 43 | 469001,7 | -0.00..109.00 | 75.000×1.500 | Ø75.60 | Ø93.00 · Ø89.50 · Ø79.50 |
| `07_CAD_Matrizes/Matriz_Jonatha_v27_OFICIAL/MatrizJonatha_Body_A.step` | 1 | 3 | 25 | 234255,3 | -0.00..109.00 | — | — | — |
| `07_CAD_Matrizes/Matriz_Jonatha_v27_OFICIAL/MatrizJonatha_Body_B.step` | 1 | 1 | 18 | 234746,4 | -0.00..109.00 | — | — | — |
| `07_CAD_Matrizes/Matriz_Jonatha_v27_OFICIAL/MatrizJonatha_Canal_Fluxo.step` | 3 | 1/1/1 | 23 | 214246,7 | -0.00..109.00 | — | — | — |
| `07_CAD_Matrizes/Matriz_Jonatha_v27_OFICIAL/MatrizJonatha_Com_Fluxo.step` | 5 | 3/1/1/1/1 | 66 | 683248,4 | -0.00..109.00 | — | — | — |
| `07_CAD_Matrizes/Matriz_Jonatha_v27_OFICIAL/MatrizJonatha_Explodida.step` | 2 | 3/1 | 43 | 469001,7 | -0.00..109.00 | — | — | — |
| `07_CAD_Matrizes/Matriz_Jonatha_v27_Peca_Unica/MatrizJonatha_v27_Peca_Unica.step` | 1 | 1 | 22 | 469303,2 | -0.00..109.00 | 75.000×1.500 | Ø75.60 | Ø93.00 · Ø89.50 · Ø79.50 |
| `07_CAD_Matrizes/Matriz_Jonatha_v28_1_PROPOSTA/MatrizJonatha_v28.step` | 2 | 1/1 | 82 | 456796,5 | -0.00..109.00 | 75.000×1.500 | Ø75.60 | Ø93.00 · Ø89.50 · Ø79.50 |
| `07_CAD_Matrizes/Matriz_Jonatha_v28_1_PROPOSTA/MatrizJonatha_v28_Body_A.step` | 1 | 1 | 39 | 228299,5 | -0.00..109.00 | — | — | — |
| `07_CAD_Matrizes/Matriz_Jonatha_v28_1_PROPOSTA/MatrizJonatha_v28_Body_B.step` | 1 | 1 | 43 | 228497,1 | -0.00..109.00 | — | — | — |
| `07_CAD_Matrizes/Matriz_Jonatha_v28_1_PROPOSTA/MatrizJonatha_v28_Canal_Fluxo.step` | 1 | 1 | 20 | 213945,1 | -0.00..109.00 | — | — | — |
| `07_CAD_Matrizes/Matriz_Jonatha_v28_1_PROPOSTA/MatrizJonatha_v28_Com_Fluxo.step` | 3 | 1/1/1 | 102 | 670741,7 | -0.00..109.00 | — | — | — |
| `07_CAD_Matrizes/Matriz_Jonatha_v28_1_PROPOSTA/MatrizJonatha_v28_Explodida.step` | 2 | 1/1 | 82 | 456796,5 | -0.00..109.00 | — | — | — |
| `07_CAD_Matrizes/Matriz_Jonatha_v28_1_PROPOSTA/MatrizJonatha_v28_Pinos_Alinhamento.step` | 4 | 1/1/1/1 | 12 | 1196,7 | 28.01..61.99 | — | — | — |

## O que divergiu

* C5 Cabecote_EX-030_com_Matriz_Jonatha_v28_1.step solido valido (BRepCheck) — tem solido invalido
