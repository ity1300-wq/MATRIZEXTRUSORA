# Material e tratamento — aço 1045 (decisão de 2026-09-22)

| item | especificação |
|---|---|
| aço | **SAE J404 / EN 10083-2: aço 1045, barra forjada, fibra no eixo, condição de entrega normalizada (≤ 220 HB)** |
| condição de entrega | normalizada, ≤ 220 HB, usinar mole; fibra no eixo da peça |
| dureza final | corpo revenido 30-36 HRC; arestas do land 55-60 HRC em camada de 0,6-1,0 mm por indução (ou nitretação a plasma 520 °C, 8-18 µm, se a fábrica preferir tratar a fenda inteira) — escolha da fábrica, declarada no relatório |
| densidade | 7,85 g/cm³ → 3,442 kg por peça |
| certificação | EN 10204 3.1 do calor: composição, granulometria, inclusão, resultado de têmpera/revenimento |
| tratamento na fenda | **pedido do dono**: indução nas arestas do land **ou** nitretação a plasma na região da fenda, à escolha da fábrica, declarado no relatório |

Por que o 1045 é diferente do 1.2344 que estava aqui: o 1045 não é aço de trabalho a quente. Ele não tem cromo/molibdênio/vanádio suficientes para manter dureza quando aquecido, e a temperabilidade dele acaba por volta de 20-25 mm de seção em água. Na prática desta matriz: (a) o núcleo do Ø94 fica em 30-36 HRC mesmo com têmpera, e é a indução (ou a nitretação) no land que segura o desgaste da fenda; (b) o produto sai a ~90 °C, então não há revenimento em serviço - o 1045 aguenta isso; (c) o risco real é trinca na têmpera, porque a peça tem uma fenda de 1,500 mm atravessando 95 mm de aço e o 1045 é temperado em água/salina. Daí a sequência abaixo: fenda aberta por fio EDM DEPOIS do tratamento térmico do corpo, e indução só nas arestas, com a cota 1,500 re-medida no fim.

## O que o tratamento pode fazer com a cota de 1,500 mm (e o que fazer com isso)

A abertura da fenda é +0,010 / −0,000. Uma camada de nitretação de 8-18 µm por face come 0,016-0,036 mm da
abertura — **mais que a tolerância inteira**. Indução não adiciona material, mas expande a superfície e move
0,005-0,020 mm na zona tratada. Portanto:

1. medir a abertura **antes** do tratamento e **depois**, gravar os dois números;
2. se depois do tratamento a abertura cair abaixo de 1,500, o retrabalho é **passar o fio de novo** na região
   e re-medir; não é "aceitar como está";
3. nenhuma peça é embalada sem a leitura final de 1,500 na boca de saída, no meio da largura e nas duas bordas;
4. se a fábrica optar por revestimento (PVD/DLC), isso **não foi pedido** — o 1045 com revestimento de 2-4 µm
   muda a geometria do produto e a gente não aceita sem teste.

T.T. do corpo (normalização 840 °C + têmpera em água 30-40 °C ou salina + revenimento 540-580 °C) tem de
acontecer **antes** da abertura do canal por fio: é o único jeito de a fenda sair sem trinca e dentro de
±0,010. Indução nas arestas, se for o caminho escolhido, vem **depois** da retífica do land e **antes** do
polimento final do canal.
