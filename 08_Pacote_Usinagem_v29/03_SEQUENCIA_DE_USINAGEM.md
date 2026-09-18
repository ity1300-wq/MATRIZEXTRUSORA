# Sequência de usinagem — MATRIZ JONATHA v29.0 (peça única)

Peça de um sólido só: 22 faces, 45 arestas, 1 casca(s), volume 469.303,2 mm³. Não existe operação de colar, pino,
alinhamento de meio nem acerto de junta — **e não pode aparecer uma peça bipartida no lugar dela**: o portão do
projeto compara o sha256 do master.

| # | operação | máquina/ferramenta | cota controlada | observação |
|---|---|---|---|---|
| 1 | cortar barra Ø95 × 115, esquadro nas duas faces | serra, facear 0,5 | comprimento 115 ±0,2 | fibra no eixo Z (ver `02_`) |
| 2 | torno: desbascar Ø93,0, Ø89,5 e Ø79,5 com os degraus 69,90 e 80,70; facear a saída | torno CNC, pastilha CBN não ainda (material recozido) | ±0,15 mm com sobra de 0,3 por lado | deixar sobra para a retífica |
| 3 | furo de entrada Ø75,60 a partir da face de entrada + alargar o funil | broca de U-drill ou BTA até 70 mm, depois mandrilar | Ø75,60 +0,05 | a entrada é restrita a Ø75,60 pelo contrato |
| 4 | **corte por fio** da fenda e da transição: canal de 75,00 × 1,50 com R 0,75 nas bordas, do land até a saída | EDM a fio Ø0,20-0,25, desbaste + 2 acabamentos | folga do fio compensada no CAM; ±0,01 na abertura | é a operação que define o produto: fio ∅ 0,25 com duas passadas de acabamento |
| 5 | chanfro de saída 1,50 × 45° (boca 78,00 × 4,50) | EDM na mesma fixação, ou fresa de 90° com guia | ±0,20 / ±0,5° | **não** virar a peça para fazer o chanfro: uma fixação só preserva a coaxialidade |
| 6 | alívio de tensões 600-650 °C, 2 h, forno | — | re-medir fenda antes/depois | sem esta linha a fanda fecha no forno |
| 7 | têmpera em vácuo + 2 revénios, prensa/placa para manter o plano | — | planitude da saída ≤ 0,01 | saída 50-52 HRC |
| 8 | retífica dos três Ø e das duas faces planas (entrada e saída), suporte no Ø93 | retífica cilíndrica + de planos | 0 / −0,02 nos Ø 89,50 e 79,50 | daqui saem as cotas que valem ouro |
| 9 | lapidação/polimento do canal e do land | pedra óleo 600 → 1200 + pasta de diamante 3 µm → 1 µm; ultra-sônico no fim | Ra ≤ 0,4 µm sem tirar cota | medir a fenda **depois** de polir |
| 10 | remover camada REC do EDM (0,02-0,05 mm) onde o fio passou | polimento/etch, com re-medição | fenda dentro de +0,010/−0,000 | se passar do ponto, a cota abre: refugar |
| 11 | marcar a laser na face traseira | — | fora do furo | `JONATHA v29.0 · EX-031 · 1.2344 · lote · nº série` |
| 12 | inspeção final (tabela do `04_`) + embalagem VCI | CMM | dossier completo | sem dossier, sem aceite |

## Erros que matam a peça (todos já vistos neste projeto)

* **Virar a peça entre o fio e o chanfro** → degrada a coaxialidade e o anel de 0,25 mm vira 0,15/0,35.
* **Medir a fenda pela face plana da partição** — não existe partição, mas a armadilha continua: seção pelo plano
  Y = 0 dá 75.00 mm de largura porque faltam os dois semicílios. Mediaõ é no **vazio do canal** (a seção do oco),
  não em meia peça, e o raio só é visível fora do plano central.
* **Esquecer o recuo do chanfro ao medir o land**: a cota da fenda é em Z = saída − 2,00. Medindo em Z = saída
  você pega a boca 78,00 × 4,50 e julga a peça boa com a fenda errada.
* **Polir para "melhorar" o Ra e abrir a cota**: a folga é de 10 µm. Uma passada de pedra a mais muda a vazão
  (a vazão escala com h^(2+1/n) ≈ h^5,3 com n = 0,30: 1 % na abertura é 5 % na vazão).
