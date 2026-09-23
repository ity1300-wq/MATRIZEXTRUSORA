# Ficha de fábrica — MATRIZ JONATHA v27.0 · rev. 30 (2026-09-22)

**Peça única, 1 sólido, sem flange, sem furo de fixação, sem linha de junção.** Material: **SAE J404 / EN 10083-2: aço 1045, barra forjada, fibra no eixo, condição de entrega normalizada**.
Quantidade pedida: **1 matriz** (sem lote). Gerado por medição no STEP `3D/MATRIZ_V30_PECA_UNICA.step` (sha256 `b42ee2e50a10d43d…`).

| o que | valor medido no STEP |
|---|---|
| envelope maior (1º estágio) | Ø94,00 × comprimento 95,00 mm |
| estágios e faixas em Z | Ø94.00 (0→69.90) · Ø89.00 (69.90→80.70) · Ø79.00 (80.70→95.00) |
| fenda no land | largura 74,9995 mm × abertura **1,500 mm** (R0,75 nas pontas), área 112,0171 mm² |
| land paralelo | 8,500 mm (Z 85,00 → 93,50) |
| chanfro de saída | 1,50 × 45°, boca 78,00 × 4,50 mm (cone medido em Z 93.50 → 95.00) |
| boca de entrada | Ø75,60 (restrita por contrato: não alargar) |
| volume de aço / massa | 438509,9 mm³ → **3,442 kg** em 1045 (7,85 g/cm³) |
| canal (vazio de fluxo) | 183862,6 mm³ = 229,8 g de mastique dentro da matriz |
| protrusão no cabeçote | protrusão 0,00 mm medida na montagem: a face de saída coincide com a face do nariz |

## As três coisas que a fábrica precisa saber antes de ligar a máquina

1. **Não tem flange, não tem furo de fixação, não tem pino.** A matriz é segurada pelo collete EX-031 e pelo
   degrau do furo do cabeçote. Furo "útil" para segurar a peça é rejeição: entraria na zona de ~69 MPa do
   degrau. Elemento de aperto só no estoque, antes do tratamento térmico, fora do envelope final.
2. **A peça não é bipartida e isso é o produto.** A v27.0 era um par `Body_A`+`Body_B` colado em Y = 0 com
   junta de 1.513,1 mm² por metade e uma costura de 372,8 mm passando nas bordas da manta (x = ±37,50) — a
   "serra" na borda do produto vinha daí. Aqui a única superfície funcional é a do canal usinado.
3. **O canal é feito de um lado só.** Proibido partir a peça para usinar: fio EDM com o arame entrando pela boca
   de entrada Ø75,60 e polimento na direção da extrusão. Sombra de usinagem medida no
   modelo: 0,00 % de área sem acesso reto.

## Interface com o EX-030 (medida na montagem `3D/Cabecote_EX-030_com_Matriz_Jonatha_v30.step`)

  - Ø94.00 em Z 0.00 → 69.90 · folga radial 0.50 mm no furo Ø95.00
  - Ø89.00 em Z 69.90 → 80.70 · folga radial 0.50 mm no furo Ø90.00
  - Ø79.00 em Z 80.70 → 95.00 · folga radial 0.50 mm no furo Ø80.00

Interferência matriz × cabeçote: **0,0000 mm³** (zero é o certo — a matriz desliza nos
furos e encosta face a face no rebaixo, `deslocamento_aplicado_mm` = 0.00).
