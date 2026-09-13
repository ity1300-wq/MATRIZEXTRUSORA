# M04 — Matriz Gedeon COMO ENTREGUE no CAD antigo (histórica, não fabricável)

A matriz dos arquivos históricos: `02_CAD_Modelos_Historicos/MatrizGedeon.step` (5 sólidos que se atravessam),
`MatrizGedeon_Body_A.step` (1 sólido com **3 cascas** — o bolso do pino é cavidade selada dentro do aço),
`MatrizGedeon_Body_B.step`, `MatrizGedeon_Canal_Fluxo.step` (213.790,0 mm³). A+B = 469.156,8 mm³ de aço.

**Estes arquivos não foram movidos para cá** — a regra 2 do projeto proíbe mexer em `02_CAD_Modelos_Historicos/`
(ler é permitido). Esta pasta é o índice e a medição, não a cópia.

Medidas que sustentam a comparação com a `M03_Gedeon_CERTA/`: seção em X = 0 de 5.885,5 mm² (contra 8.776,5 mm²
na certa), envelope Ø 93,00 × Z 0,1..109,00 nas duas, e a diferença de aço das peças inteiras:
170.821,9 mm³ que a Gedeon entregue não tem porque teve o funil da Jonatha escavado nela.

`README-REFUTADA.md` desta pasta declara a tentativa de 2026-09-12 (re-cortar o canal histórico no arquivo do
usuário), os números dela e o porquê de estar refutada. Os STEP daquela tentativa saíram do repositório;
`python 04_Dados_SSOT_e_Scripts/gerar_gedeon_corrigida.py` os recria aqui, abrindo com a refutação impressa, e
as medições ficam em `04_Dados_SSOT_e_Scripts/gedeon_corrigida.json` +
`03_Relatorios_e_Documentacao/RELATORIO_GEDEON_CORRIGIDA.md`.
