# Resfriar a matriz: as contas, as opções e o controle (2026-09-25)

Feito sob demanda dele, depois do fato novo que resolveu a discussão: **"sempre que esfria sai boa, mas depois
que a manta começa a esquentar ela sai quente de novo"**. Documento de plano de trabalho; nenhuma cota do SSOT,
do STEP ou do pacote foi tocada.

---

## 1. Para onde vai o calor, em número

Do `pacote_usinagem.json` e dos métodos do projeto (vazão de referência Q = 15.000 mm³/s, aço da v30 =
**3,442 kg** medido no sólido):

| grandeza | número | de onde vem |
|---|---:|---|
| potência dissipada no material (ΔP 26,68 bar, 1D do projeto) | **40 W** | ΔP × Q |
| potência dissipada (ΔP 203,6 bar, modelo com o anel de fuga medido) | **305 W** | idem, pior caso |
| parte que sai **na parede do land** (69,7 % do ΔP é o land) | **28 a 213 W** | PRP-0002 / tabela de inspeção |
| aquecimento do **bolo** de mastique se todo esse calor ficasse nele | **+0,7 a +5,7 K** | 18,75 g/s × cp ≈ 2 J/g·K |
| capacidade térmica da **matriz** (aço 1045, 3,442 kg) | **1,69 kJ/K** | massa medida × 0,49 kJ/kg·K |
| tempo para a matriz subir 20 °C sem resfriamento nenhum | **2,6 min (pior caso) a 20 min (melhor caso)** | 1,69 kJ/K ÷ (28 a 213 W) |

**É isso que ele está vendo.** O material quase não aquece (meio grau a cinco graus); quem aquece é a **matriz**,
que é um bloco de 3,4 kg recebendo de 30 a 200 watts e conduzindo calor do cabeçote quente. Nos primeiros metros
ela ainda está fria → a pele do extrudado congela no lábio e a borda aguenta a tração → manta limpa. Depois de
alguns minutos ela satura → o lábio esquenta → a pele não congela → o centro, que corre mais, rasga a ponta em
dente. A ordem de grandeza do tempo bate com "aos poucos ao longo da produção", o que não aconteceria se fosse
defeito de forma (aí serrilharia desde o primeiro metro).

Conclusão de projeto: **não é preciso máquina de gelo nenhuma — são 30 a 200 W.** Água de rede a 1 L/min sobe
3 °C com 213 W. O problema de refrigeração é pequeno; o que falta é caminho térmico e controle.

## 2. As cinco maneiras de resfriar, da mais barata para a mais cara

| # | o que é | o que resfria de fato | custo/risco |
|---|---|---|---|
| 1 | **Copo de gotejamento no nariz** (técnica clássica de extrusão de perfil): um copo/armação presa no nariz do cabeçote, com água escorrendo na face de saída da matriz; no lugar do copo, uma **faixa de pano/borracha encharcada** em volta do nariz, trocada a cada tanda | o **lábio** - que é exatamente onde a pele tem que congelar | zero; a água evapora e some com os 28-213 W; risco: gotejar na manta (use pano, não jato) |
| 2 | **Air knife / faca de ar** na manta nos primeiros 30-50 cm: tubo com fenda de 0,5 a 1,0 mm atravessando os 75 mm, ar comprimido de 0,3 a 0,5 bar | arrefece a superfície **e segura a borda** contra a tração que rasga | peça de bancada, barato; é o único item que ataca as duas causas ao mesmo tempo |
| 3 | **Cuneta de água no nariz do cabeçote + anel prensado** (groove circunferencial com duas portinhas de mangueira, 0,2 a 1 L/min) | o corpo da matriz por fora, pela via que já existe hoje: o **encosto Ø94/Ø89/Ø79** dentro do furo | usinagem no **cabeçote**, não na matriz; é a melhor relação por watt. Mexe na peça 06_ - decisão dele |
| 4 | **Resfriar antes da matriz**: garrafa/trocador na alimentação ou **tela mais grossa + cabeça mais fria**, para o mastique chegar mais frio | o que entra, em vez de brigar com o calor gerado | zero de usinagem; efeito colateral: sobe a pressão (já está em 203,6 bar no pior caso) |
| 5 | **Furos de água dentro da matriz** (furação transversal com buchas, como se faz em matriz industrial) | a matriz inteira | **cara e apertada aqui**: ver §3. Não recomendo como primeira opção |

## 3. Por que "água dentro da matriz" quase não cabe na nossa geometria (o motivo é medido, não é opinião)

A boca de entrada do canal é **Ø75,60 em Z = 0** e o primeiro estágio da matriz é **Ø94,00** → sobram
**9,20 mm de aço no raio**. Para um furo de água Ø4 mm com a parede mínima de **4,00 mm** até o canal (alvo do
projeto, o mesmo critério usado no `ESTUDO_RECUO_CARTUCHOS.md`) e folga até a face externa, sobra uma faixa de
centro de furo entre 43,8 e 45,0 mm de raio: **1,2 mm de janela**. Dá, mas:

- só na região do Ø94 (longe do land, onde o calor nasce - o land é em Z = 85 a 93,50, e ali o aço que sobra é o
  do lábio, que já é fino por contrato);
- furação **antes** do tratamento térmico (a aresta do land vai a 55-60 HRC; não se fura depois) e buchas de
  vedação que aguentem 200 bar de pressão de matriz + risco de queima em fenda viva;
- e é exatamente o "custo de usinagem maior" de que o Fernando avisou.

**Então: refrigere por fora (1, 2, 3) primeiro.** O item 1 e o 2 não têm nada a errar: dá para testar amanhã.

## 4. O controle, que vale mais que o equipamento

O que ele descreveu é uma **temperatura-limiar**. Descubra o número e o problema vira termostato:

1. Ponha um **termômetro de infravermelho** apontado para a face de saída da matriz (o lábio).
2. Rode até aparecer o primeiro dente. Anote: **temperatura do lábio, tempo de produção e velocidade da linha**.
3. Repita 3 vezes em velocidades diferentes (100 %, 80 %, 60 %) e 3 vezes com resfriamento (copo/pano).
4. Isso dá o `T_limiar` (aposto que fica entre 55 e 75 °C, mas o número é seu, medido, não meu).
5. Regra operacional enquanto a matriz não vem: **segurar o lábio em `T_limiar − 10 °C`**, molhando/parando quando
   o IR passar. Com os 1,69 kJ/K da matriz, isso é um "liga/desliga" a cada poucos minutos - nada sofisticado.

Com esse número na mão dá para dimensionar o item 3 (a cuneta no nariz): W a trocar = a potência que chega ao
lábio, e ela está entre 28 e 213 W acima.

## 5. Dois avisos de contrapeso, para não trocar um defeito por outro

- **não congele demais**: matriz muito fria em relação à cabeça = pressão maior (o 1D do projeto já dá 26,68 bar,
  e o modelo com fuga 203,6 bar) e risco de a casca **não soldar** nos cantos R 0,75, que é onde a manta é mais
  fraca e onde ela arrebenta. Alvo: **10 a 25 °C abaixo da cabeça**, não gelo.
- resfriar **não conserta o puxamento do centro sobre a borda** - só dá tempo para a pele endurecer antes de
  rasgar. Por isso o refrigeração e a revisão da fenda (gotas nos extremos + arco) são **complementares**, não
  alternativos: um muda a janela de tempo, o outro tira a carga da borda.

## 6. O que eu coloco no pacote quando ele decidir

- Se a resposta for "cuneta no nariz": entra como exigência no **cabeçote** (`06_CAD_Cabecote_EX-030`) com cota de
  groove e porta de água, e a matriz **não muda** - é o caminho de menor risco para o desenho da matriz.
- Se a resposta for "gota e ar": não muda desenho nenhum; vira **procedimento de operação** escrito (e o
  `05_O_QUE_O_STEP_NAO_DIZ.md` do pacote já é o lugar natural para uma linha sobre controle térmico, que hoje é
  a pendência P3 da triagem: matriz sem controle térmico).
- Em qualquer dos dois casos, o critério de aceite da linha passa a ser o que ele medir no §4, e não uma
  promessa minha sobre a forma do canal.
