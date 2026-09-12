# Cabeçote EX-030

## `STEP/` — pasta dos desenhos STEP do cabeçote

Dois sólidos, gerados por `python 04_Dados_SSOT_e_Scripts/gerar_cabecote_ex030.py`
a partir do que foi medido no DWG (`04_Dados_SSOT_e_Scripts/cabecote_ex030.json`):

- `STEP/Cabecote_EX-030_sem_flange.step` — **o pedido**: o cabeçote sem a parte que conecta na extrusora (corpo Ø130 × 95,000 mm, nariz Ø80, degrau Ø90, bolso Ø95 × 70,00 e o piloto Ø105 × 3,00 na traseira, que fica dentro do corte pelo Ø130 e por isso aparece aqui).
- `STEP/Cabecote_EX-030_desenhado.step` — como está no desenho: corpo Ø130 × 42, **chanfro 10 × 45°** na transição para a face do flange (Ø130 → Ø150), flange Ø220 × 40 com as 6 fendas de 23,5 e o piloto de centragem Ø105 × 3,00 mm na traseira. Massa e volume medidos no sólido, a cada rodada: `04_Dados_SSOT_e_Scripts/cabecote_step.json`.

- `STEP/DESENHO_2D_CABECOTE_X_MATRIZ_COPO.pdf` — **o desenho 2D** pedido: vista lateral em corte pelo plano
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
