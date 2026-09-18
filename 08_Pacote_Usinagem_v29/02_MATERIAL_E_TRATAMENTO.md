# Material e tratamento térmico — MATRIZ JONATHA v29.0

## O que pedir

| item | especificação | por que |
|---|---|---|
| qualidade | **1.2344 (X37CrMoV5-1), classe AISI H13**, barra forjada, condição de entrega recozida (≤ 240 HB) | a peça fica a ~90 °C no produto e vê 69 MPa no degrau; H13 aguenta choque térmico e mantém dureza a 200 °C |
| razão de forja | ≥ 3:1, com a **fibra na direção do eixo Z** | a fenda de 1,50 mm é o ponto onde trinca aparece; fibra atravessando o land encurta a vida |
| pureza | aço eletrore-refundido (ESR) ou VAR se disponível; inclusão ≤ classe A/B 1,5 (ISO 4967) | inclusão grande no land vira microporosidade → raspado no produto |
| dureza final | **50–52 HRC**, núcleo, após têmpera em vácuo (≤ 10⁻² mbar) + 2 revénios a 560–580 °C, 2 h cada | abaixo de 50 o land abre; acima de 53 a fragilidade na fenda de 1,50 mm é risco de lascamento nas pontas |
| tratamento de superfície | **não** nitretar nem revestir (PVD/DLC) sem teste antes | o canal é a geometria do produto; 5–10 µm de revestimento mudam a espessura da manta (tolerância é +0,010 mm) |
| polimento | manual/ultrassônico nas faces do land e do funil, Ra ≤ 0,4 µm, sem alterar a cota | ver `04_TOLERANCIAS_E_INSPACAO.md` |
| alívio de tensões | obrigatório antes da têmpera (600–650 °C, 2 h, resfriar no forno) e re-medir a fenda depois | a fenda de 1,50 mm **fecha** se a peça for temperada crua de uma barra laminada |
| certificado | EN 10204 **2.2 no mínimo, 3.1 preferido** + relatório de dureza do lote + micrographia de grão | vai no dossiê da matriz, junto do relatório de CMM |

## O que NÃO usar

* **não** pedir "peça usinada acabada em bruto" — o material recozido não segura a folga de 0,02 mm dos
  estágios; a sequência é: desbaste → alívio → têmpera/revénio → **acabamento por retífica e EDM**.
* **não** usar 1.2379 (D2) nem cementado: dureza boa, mas a condutividade térmica pior faz o land trabalhar
  com gradiente e a fenda empena.
* **não** retemperar para "acertar" a fenda: uma re-têmpera muda o volume do canal (213.945,1 mm³) e com ele a
  vazão. Se a fenda sair fora, a peça é refugada, não corrigida.

## Estoque recomendado

Barra Ø**95,0** × 115,0 mm (Ø93,0 de envelope + 2 mm por lado no primeiro estágio, 6,0 mm de sobra na saída
para o chanfro e para a face de assentamento). Volume a remover: 469.303,2 mm³ de aço (1.25 kg de cavaco). Se a
fábrica preferir partir de disco, usar Ø96 × 115 e deixar a face de entrada como referência única.
