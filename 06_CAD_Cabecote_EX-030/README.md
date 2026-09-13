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

### A Gedeon CERTA — o arquivo do usuário, medido (desde 2026-09-13 mora em `07_CAD_Matrizes/`)

`02_CAD_Modelos_Historicos/matrizGedeonCerta.step` (atalho para
`07_CAD_Matrizes/Matriz_Gedeon_Certa/matrizGedeonCerta.step`) foi medido face por face por
`gerar_gedeon_certa.py` e não é bloco bruto: é a matriz pronta — 1 sólido, 18 faces, **640.180,7 mm³** de aço,
com a fenda **75,00 × 1,50 com R 0,75** atravessando de Z = 0,17 a Z = 109,00 (sai pela face de saída), o cone de
entrada que abre em **Ø 75,60** na face traseira e fecha em Z = 20,98, e os **2 furos de pino Ø 1,78 × 10,00** a
|x| = 40,61..42,39, Z 44,50..54,50. Os três estágios do envelope batem com o SSOT: Ø 93,00 até Z 69,90,
Ø 89,50 até Z 80,70, Ø 79,50 até Z 109,00. Caminho de fluxo medido (cone + fenda): **43.017,9 mm³**.

Os entregáveis da Gedeon não ficam nesta pasta: ficam em `07_CAD_Matrizes/Matriz_Gedeon_Certa/` — o arquivo dele,
o par aberto no plano de partição (`MatrizGedeon_Certa_Body_A/B.step`, A 320.090,4 + B 320.090,4 = o bloco com
diferença de **0,0004 mm³**, 1 casca cada, BRepCheck válido, A ∩ B = 0,0000 mm³), a `_Explodida.step` e a prancha
`DESENHO_2D_GEDEON_CERTA_X_JONATHA.pdf`. A montagem que ele pediu deste cabeçote continua aqui:
`STEP/Cabecote_EX-030_com_Matriz_Gedeon_Certa.step`.

Interface conferida na mesma colocação medida: ∩ matriz × cabeçote = **0,0000 mm³**, aço do cabeçote dentro do
cone+fenda = **0,0000 mm³**, e a face de saída da matriz fica **14,00 mm** além da face do cabeçote (Z = 95,00) —
a fenda não encosta no nariz. **O único defeito do arquivo dele** é de fabricabilidade, não de forma: os furos de
pino são cavidades seladas dentro do aço (o sólido tem 3 cascas; sobram 4,11 mm até o Ø 93,00 externo, sem por
onde entrar ferramenta). O conserto é só partir em Y = 0; nenhum aço foi escavado do arquivo dele.

A comparação com a v27 e com a Gedeon antiga, faixa a faixa no mesmo escalonamento, está na prancha; área de
seção medida em X = 0: 5.885,5 mm² na Gedeon entregue, 5.883,5 mm² na v27, **8.776,5 mm² na certa**. Números do
desenho: `07_CAD_Matrizes/Matriz_Gedeon_Certa/desenho_gedeon.json`.

**A tentativa de "Gedeon corrigida" (2026-09-12) foi apagada em 2026-09-13, a pedido, por inteiro** — gerador,
JSON, relatório, os cinco STEP e a montagem `Cabecote_EX-030_com_Matriz_Gedeon_Corrigida.step`. Ela escavava no
arquivo do usuário o canal histórico `MatrizGedeon_Canal_Fluxo.step` (213.790,0 mm³) inteiro, o que tirava
**171.024,0 mm³** de aço que não é da Gedeon: o vazio da matriz certa é o cone de entrada + a fenda, e só. Não há
script que a recrie, e não há de haver. Quem quiser o confronto entre as duas Gedeon o vê reimpresso a cada
rodada do portão, medido nos arquivos de `07_CAD_Matrizes/Matriz_Gedeon_Entregue_HISTORICA/`.

E sobre "está igual à Jonatha": medido em booleano nos dois sentidos, **não está** — 171.224,1 mm³ de aço só na
Gedeon certa e 44,9 mm³ só na v27 (a faixa dos furos de pino). São gêmeas de envelope de propósito (a exigência
do projeto é envelope idêntico); o que as separa é interno: a v27 tem funil escavado no próprio aço, a Gedeon não
tem funil nenhum e quem converge o fluxo é o furo estagiado do cabeçote.

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

Referencial: Z é o eixo da matriz (face do nariz em Z = 95, face de entrada do cabeçote em Z = 0), então o arquivo monta direto com `07_CAD_Matrizes/Matriz_Jonatha_v28_1_PROPOSTA/MatrizJonatha_v28.step`.

## `STEP/estudos/` — cenários, não entregas

O que está aqui foi gerado para *ver*, não para *usar*: por exemplo
`python 04_Dados_SSOT_e_Scripts/gerar_cabecote_ex030.py --com-m12 --angulo-graus 90` abre o furo
transversal Ø12 no ângulo que o desenho não determina, e o gerador manda o resultado para cá em vez de
tocar nos dois STEP acima: na rodada de cenário os arquivos ganham sufixo `_M12` e o relatório e as mediações vão para a mesma pasta (`CABECOTE_EX-030_STEP_M12.md`, `cabecote_step_M12.json`), nunca para `03_Relatorios_e_Documentacao/`. A pasta está no `.gitignore` — cenário sem decisão aprovada não vira
entregável, e é recriável com um comando.

Medições, o que foi removido e o que ainda não está resolvido (fixação da junta, ângulo do M12):
`03_Relatorios_e_Documentacao/CABECOTE_EX-030_STEP.md`.
