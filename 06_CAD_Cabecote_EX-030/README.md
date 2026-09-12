# Cabeçote EX-030

## `STEP/` — pasta dos desenhos STEP do cabeçote

Dois sólidos, gerados por `python 04_Dados_SSOT_e_Scripts/gerar_cabecote_ex030.py`
a partir do que foi medido no DWG (`04_Dados_SSOT_e_Scripts/cabecote_ex030.json`):

- `STEP/Cabecote_EX-030_sem_flange.step` — **o pedido**: o cabeçote sem a parte que conecta na extrusora (corpo Ø130 × 95,000 mm, nariz Ø80, degrau Ø90, bolso Ø95 × 70,00 e o piloto Ø105 × 3,00 na traseira, que fica dentro do corte pelo Ø130 e por isso aparece aqui).
- `STEP/Cabecote_EX-030_desenhado.step` — como está no desenho: corpo Ø130 × 42, **chanfro 10 × 45°** na transição para a face do flange (Ø130 → Ø150), flange Ø220 × 40 com as 6 fendas de 23,5 e o piloto de centragem Ø105 × 3,00 mm na traseira. Massa e volume medidos no sólido, a cada rodada: `04_Dados_SSOT_e_Scripts/cabecote_step.json`.

- `STEP/Cabecote_EX-030_com_Matriz_Copo.step` (2 sólidos) e `STEP/Cabecote_EX-030_com_Matriz_Gedeon.step`
  (**3 sólidos**: cabeçote + `Body_A` + `Body_B`) — o cabeçote **com a matriz sentada**, no mesmo referencial
  axial, **sem booleano nenhum na entrega**: cada sólido é o que está no arquivo de origem. Interferência
  medida nos dois: **0,0000 mm³** (somada peça a peça, que dá o mesmo número do booleano sobre a união porque
  as metades se tocam no plano de partição e não se sobrepõem: A ∪ B = 469.156,8 mm³ contra A + B = 469.156,7).
  Saída da matriz em Z = 80,70 (Copo, 14,30 mm *para dentro* da face do nariz) e Z = 109,00 (Gedeon, 14,00 mm
  *para fora*) — a diferença é só comprimento de peça: falta na Copo o nariz de 28,30 mm.

#### As três coisas que se veem abrindo estes arquivos, e o que a medida diz

- **`Cabecote_EX-030_sem_flange.step` não tem matriz dentro, e não tem fenda**: 1 sólido, 1 casca, 11 faces,
  610.588,2 mm³ (reimportado e conferido). A fenda 75,00 × 1,50 vive na matriz. O que aparece por dentro do
  cabeçote é a escada de furos dele — Ø80 (nariz, 14,02) → Ø90 (degrau, 11,00) → Ø95 × 70,00 (o bolso onde a
  banda da matriz entra) — que é o copo da matriz **em negativo**, e é isso que segura a matriz sem tocar a fenda.
- **A Gedeon "corrompida" são duas coisas diferentes**, ambas medidas (`inventario_dos_arquivos_de_matriz` em
  `cabecote_step.json`): `02_/MatrizGedeon.step` tem **5 sólidos que se atravessam** (as duas metades *sem* o
  canal escavado, 320.090,4 mm³ cada, + o sólido do canal de plástico, 43.017,9 mm³ + dois pinos de 24,9 mm³),
  e `02_/MatrizGedeon_Body_A.step` é **1 sólido com 3 cascas** — duas cavidades internas seladas, que é o que a
  maioria dos importadores mostra como corpo partido/fantasma. Nenhum dos dois é arquivo inválido:
  `BRepCheck_Analyzer.IsValid()` dá True em todos os sólidos. Os STEP que o projeto usa são `Body_A`/`Body_B`,
  as metades *com* o canal escavado. A primeira versão da montagem entregava A ∪ B e carregava as cascas
  internas junto — por isso ela agora entrega as metades separadas.
- **A Gedeon montada parece a Jonatha porque são gêmeas de envelope**: 469.156,8 mm³ (Gedeon) contra 469.001,7
  (v27) e 456.796,5 (v28.1), com a mesma caixa externa ±46,50 × Z 0..109,00. O que as separa é interno (funil,
  canal, bolsões de pino) e não aparece na silhueta lateral. O `[3, 1]` de cascas do `MatrizJonatha.step` é a
  mesma moléstia do `Body_A` da Gedeon — é o G-03 da auditoria, e o remédio está na v28.1.
### `STEP/Gedeon_Corrigida/` — a Gedeon reconstruída a partir do SEU backup (2026-09-12)

Você subiu `02_/matrizGedeonCerta.step` e medimos nele: é o **bloco inteiro sem escavar** (640.180,7 mm³ = as
duas metades brutas de `MatrizGedeon.step` somadas, diferença de 0,000 mm³). O conserto então não inventa
geometria: é o seu bloco **− o canal próprio da Gedeon (213.790,0 mm³) − os pinos do próprio arquivo dele**
(2 × Ø1,78 × 10,00, que já atravessam Y = 0), partido no plano Y = 0. Sai em `STEP/Gedeon_Corrigida/`:
`MatrizGedeon_Corrigida_Body_A.step` e `_Body_B.step` (aço 234.617,6 + 234.741,2 mm³), `_Canal_Fluxo.step`,
`_Explodida.step` e `Cabecote_EX-030_com_Matriz_Gedeon_Corrigida.step` (3 sólidos). Medido: **1 casca por
sólido** (o `Body_A` do repositório tem 3), A ∩ B = 0,000000 mm³, nenhum metal no canal (0,000000 mm³),
envelope Ø93,00 × Z 0..109,00 igual ao do backup, ∩ com o cabeçote = 0,0000 mm³.

E sobre "está igual à Jonatha": medido em booleano nos dois sentidos, **não está** — par−v27 = 155,1 mm³ e
v27−par = 44,9 mm³ de aço, e o canal da Gedeon cabe inteiro no da Jonatha (Gedeon−Jonatha = 0,0 mm³;
Jonatha−Gedeon = 155,1 mm³, 0,07 %). As duas são gêmeas de propósito (a exigência do projeto é envelope
idêntico); o que as separa é o funil, e a ampliação é da Jonatha. Ao medir isso apareceu que **a P5 da triagem
estava errada** — ela chamava `_Canal_Fluxo.step` de canal errado comparando-o com o funil só; a P5 está
marcada como REVOGADA no SSOT, com a medição ao lado. Números: `04_Dados_SSOT_e_Scripts/gedeon_corrigida.json`
e `03_Relatorios_e_Documentacao/RELATORIO_GEDEON_CORRIGIDA.md`, gerados por `gerar_gedeon_corrigida.py`, que
entrou na cadeia do portão.

- Achado re-confirmado ao medir (e depois revogado, ver acima): `02_/MatrizGedeon_Canal_Fluxo.step` tem **213.790,0 mm³**, enquanto o sólido de
  canal que está dentro de `MatrizGedeon.step` tem **43.017,9 mm³**. O arquivo do canal da Gedeon não é o canal
  da Gedeon (P5 da triagem) — é por isso que toda comparação desta pasta usa as metades, nunca esse arquivo.
- `STEP/DESENHO_2D_CABECOTE_X_MATRIZES.pdf` — **o desenho 2D** pedido: vista lateral em corte pelo plano
  do eixo do cabeçote, da Matriz 1 Copo e da montagem, com as cotas principais de cada vista. Gerado, não
  traçado à mão: as linhas vêm da seção dos próprios STEP e os números de `cabecote_ex030.json` +
  `perfis_matrizes_x_cabecote.json`, por `python 04_Dados_SSOT_e_Scripts/gerar_desenho_2d_cabecote_matriz.py`
  (`--png` escreve um PNG ao lado para conferência). Roda no `--com-estudos` do portão.

**Encosto do conjunto na extrusora (decisão de 2026-09-12: "encosta face a face").** A face do flange
(d = 92,00) encosta na face da máquina e o piloto Ø105 × 3,00 é centragem - o que significa que a face da
extrusora precisa de 3,00 mm de rebaixo em Ø > 105,00, senão a junta fica aberta 3,00 mm. A posição axial da
matriz **não** muda com isso: ela vem da escada interna do cabeçote (degrau + fundo do bolso), medida com
interferência 0,0000 mm³, então a protrusão continua 14,00 mm e o NC dos cartuchos também. Item [G] de
`verificar_interface_cabecote.py` mede a face do flange no sólido e cobra essa altura.

Aproveitando a medição do [G]: os anéis de `CORPO` em `verificar_interface_cabecote.py` tinham 1 mm de
sobreposição de cada lado do flange, escolha minha "para o booleano ser robusto" que criou material
fantasma - um colar de Ø220 engolindo o primeiro milímetro do chanfro e 1 mm de flange tapando o vão onde só
deveria haver o piloto. As faces do desenho agora são exatas (flange de Z = 43,00 a Z = 3,00), o que baixou
`desenhado` e `sem_flange` de acordo; os números correntes estão em `cabecote_step.json`.

O chanfro é cota do desenho e estava no SSOT (`corpo.chanfro` em `cabecote_ex030.json`) mas não estava no sólido; foi conferido hoje nas **duas** vistas de seção do DXF (aresta a 45,00° de (d 42,00; r 65,02) a (d 52,00; r 75,02), camada `contorno`) e medido no modelo depois de gerado. Onde o SSOT dizia `resalto_traseiro: Ø203 × 3`, a medição da traseira mostra outra coisa: piloto Ø105,00 × 3,00 mm protraindo além da face do flange (`H r 52,48/52,52` em `d 92,00..95,00`), com o Ø95 do bolso atravessando até `d = 95,00` — é isso que dá os 95,00 mm de comprimento total. Onde este repositório tinha um "cubo Ø164" nessa faixa, a linha era a borda do furo Ø16 no C.C. Ø180 (82 = 90 − 8), não uma superfície da peça.

Referencial: Z é o eixo da matriz (face do nariz em Z = 95, face de entrada do cabeçote em Z = 0), então o arquivo monta direto com `01_CAD_MatrizJonatha_Oficial/MatrizJonatha_v28.step`.

## `STEP/estudos/` — cenários, não entregas

O que está aqui foi gerado para *ver*, não para *usar*: por exemplo
`python 04_Dados_SSOT_e_Scripts/gerar_cabecote_ex030.py --com-m12 --angulo-graus 90` abre o furo
transversal Ø12 no ângulo que o desenho não determina, e o gerador manda o resultado para cá em vez de
tocar nos dois STEP acima: na rodada de cenário os arquivos ganham sufixo `_M12` e o relatório e as mediações vão para a mesma pasta (`CABECOTE_EX-030_STEP_M12.md`, `cabecote_step_M12.json`), nunca para `03_Relatorios_e_Documentacao/`. A pasta está no `.gitignore` — cenário sem decisão aprovada não vira
entregável, e é recriável com um comando.

Medições, o que foi removido e o que ainda não está resolvido (fixação da junta, ângulo do M12):
`03_Relatorios_e_Documentacao/CABECOTE_EX-030_STEP.md`.
