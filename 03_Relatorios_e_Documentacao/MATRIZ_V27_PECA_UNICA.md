# Matriz Jonatha v27.0 como peça única — o que mudou, medido

Gerado por `04_Dados_SSOT_e_Scripts/gerar_matriz_v27_peca_unica.py` em 2026-09-13. É uma **variante derivada**: o master continua `01_CAD_MatrizJonatha_Oficial/MatrizJonatha.step` (sha256 `7f26c5c5ba238a12667f2bdf…` verificado no fim da rodada, regra 1) e a peça única mora em `07_CAD_Matrizes/Matriz_Jonatha_v27_Peca_Unica/`.

## A peça

| grandeza | master bipartido | peça única | o que é |
|---|---|---|---|
| sólidos no arquivo | 2 (Body_A + Body_B) | **1** | sem par, sem jogo de montagem |
| aço | 469001,7 mm³ | **469303,2 mm³** | +351,9 mm³ = as bolhas seladas que foram fechadas |
| massa | 3.6817 kg | **3.6840 kg** | ρ = 7,85 g/cm³ |
| bolhas seladas dentro do aço | 2 (G-03 do auditor) | **0** | os furos de pino cegos deixaram de existir porque não há mais o que alinhar |
| canal (funil + fenda) | 213945,1 mm³ | **213945,1 mm³** | o caminho do material é o mesmo |
| fenda no land (Z = 107.00) | 75.000 × 1.500 mm, R 0.75, área 112.0171 mm² | **75.000 × 1.500 mm, R 0.75, área 112.0171 mm²** | Δ de área = 0.000000 mm² — o produto é o mesmo |
| boca de entrada | Ø 75.60 mm | **Ø 75.60 mm** | a restrição do acoplamento com a extrusora é Ø 75,60 — e não mudou |
| envelope | Ø93.00 Z 0.00..69.90 · Ø89.50 Z 69.90..80.70 · Ø79.50 Z 80.70..109.00 | idêntico | senta no mesmo furo do cabeçote EX-030 |
| boca de saída (Z = 108.99) | 78.000 × 4.500 mm, área 346.6543 mm² (meia-lua (R = espessura/2)) | **78.000 × 4.500 mm, área 346.6543 mm² (meia-lua (R = espessura/2))** | o chanfro 1,50 × 45° abre a boca do mesmo jeito nas duas |
| BRepCheck | — | sólido válido, **0** cara(s) e **0** aresta(s) inválida(s) em 22 caras / 90 arestas | abre limpa em qualquer CAD (o defeito achado na v28.1 não se repete aqui) |

## O que a peça única tira do produto

A bipartição corta o canal por dentro, no plano Y = 0 — que é o **meio da espessura** da manta. Onde esse plano encontra as paredes do canal nasce a linha de costura que aparece na peça extrudada. Medido no master:

* área de contato metal-metal das duas metades: **759,5 mm²**;
* a seção do canal no plano de partição: **8204.4 mm²** ocupando 78.000 mm em X por 109.000 mm em Z, com perímetro de costura de **372.8 mm**;
* **2 linha(s)** de costura correndo nas bordas da manta (x = ±37,50), de ponta a ponta do canal. É por isso que a serra aparece *na borda* e não na face: o plano de partição é perpendicular às faces grandes e paralelo às bordas.

Na peça única esses três números são **zero**: não há junta, logo não há degrau nem rebarba de junta, e o que sobrar de serrilha na borda não vem mais da matriz bipartida — passa a ser processo (τ na parede contra o limiar de raspado, 0,14 MPa da literatura) ou desenho do lábio. É exatamente a separação que a simulação 3D vai fechar.

## Fabricabilidade: o canal tem de ser feito por acesso reto das duas faces

Sem as duas metades, o único jeito de abrir o funil e a fenda é entrar por elas. Testei cada cara do vazio em linha reta pela entrada (Z < 0) e pela saída (Z > 109,00):

| # | tipo de cara | área (mm²) | centro (mm) | vista pela entrada | vista pela saída | leitura |
|---|---|---|---|---|---|---|---|
| 1 | PLANE | 4489 | 0.00, 0.00, 0.00 | 100.0% | 100.0% | entrada+saida |
| 2 | BSPLINE | 93 | 37.45, -0.38, 49.60 | 100.0% | 100.0% | entrada+saida |
| 3 | BSPLINE | 9184 | 0.00, -7.88, 43.93 | 100.0% | 0.0% | entrada |
| 4 | BSPLINE | 91 | -37.46, -0.38, 49.60 | 100.0% | 100.0% | entrada+saida |
| 5 | BSPLINE | 90 | -37.46, 0.38, 49.60 | 100.0% | 100.0% | entrada+saida |
| 6 | BSPLINE | 9213 | 0.08, 7.77, 43.85 | 100.0% | 0.0% | entrada |
| 7 | BSPLINE | 0 | 37.80, 0.00, 0.21 | 100.0% | 100.0% | entrada+saida |
| 8 | BSPLINE | 54 | 37.45, 0.19, 50.00 | 100.0% | 100.0% | entrada+saida |
| 9 | CYLINDER | 20 | 36.85, 0.00, 103.25 | 100.0% | 100.0% | entrada+saida |
| 10 | PLANE | 625 | 0.00, -0.75, 103.25 | 100.0% | 100.0% | entrada+saida |
| 11 | CYLINDER | 20 | -36.85, 0.00, 103.25 | 100.0% | 100.0% | entrada+saida |
| 12 | PLANE | 625 | 0.00, 0.75, 103.25 | 100.0% | 100.0% | entrada+saida |
| 13 | CONE | 10 | 37.57, -0.00, 108.51 | 100.0% | 100.0% | entrada+saida |
| 14 | PLANE | 156 | 0.00, -1.50, 108.25 | 0.0% | 100.0% | saida |
| 15 | CONE | 10 | -37.57, 0.00, 108.51 | 100.0% | 100.0% | entrada+saida |
| 16 | PLANE | 156 | 0.00, 1.50, 108.25 | 0.0% | 100.0% | saida |
| 17 | PLANE | 347 | 0.00, 0.00, 109.00 | 100.0% | 100.0% | entrada+saida |

**0 de 17** caras do canal não têm acesso reto nem pela frente nem por trás. Todas as caras são alcançáveis de um dos dois lados: a peça única é usinável com o canal por frente e a fenda por trás, sem necessidade de junta.


## Montagem no cabeçote completo, com flange

`Cabecote_EX-030_com_Matriz_Jonatha_v27_Peca_Unica.step` — 2 sólidos no arquivo (1 cabeçote + 1 peça única, sem booleano), volume somado 2039642,7 mm³, **interferência com o metal do cabeçote = 0,0000 mm³**, face de saída em Z = 109.00 (protrusão +14.00 mm além da face do nariz). O encaixe é o mesmo da bipartida: folga radial de Ø 93,00 no furo Ø 95,00 e assento no degrau, e o anel de fuga entre matriz e cabeçote continua existindo igual — ele não vem da bipartição.


## Consequências e o que não muda

* **Decisão D2 intocada:** chanfro de saída 1,50 × 45° e land paralelo 8,50 mm do master. Nada de geometria do produto foi alterado nesta rodada — só a construção da peça.
* **Fixação:** o collete EX-031 e o degrau do cabeçote continuam sendo o que segura a matriz; os pinos de alinhamento somem da conta junto com os furos (a força de abertura medida do plano de partição, 55,7 kN, deixa de existir porque não há plano de partição).
* **Anel de fuga:** a folga de 1,00/0,25/0,25 mm entre a OD da matriz e o furo do cabeçote é do encaixe, não da bipartição — continua igual nas duas peças, e é a rota que a simulação precisa resolver.
* **Promoção:** a peça única **não** é o master. Quando ele quiser, se ela entra no lugar da v27 bipartida, é preciso re-sear o baseline (ato do auditor, com o método novo) — e aí vale aproveitar para consertar o `Body_B` da v28.1, que tem uma cara degenerada achada pela auditoria de correlações.

