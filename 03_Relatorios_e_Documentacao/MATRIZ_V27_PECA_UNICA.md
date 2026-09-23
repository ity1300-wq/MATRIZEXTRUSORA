# Matriz Jonatha v27.0 como peça única — o que mudou, medido

Gerado por `04_Dados_SSOT_e_Scripts/gerar_matriz_v27_peca_unica.py` em 2026-09-13. **ATUALIZAÇÃO DA MESMA RODADA: esta variante foi promovida a oficial como v29.0** — ver `07_CAD_Matrizes/Matriz_Jonatha_v29_OFICIAL/` e o pacote de fábrica `08_Pacote_Usinagem_v29/` (o STEP é byte-idêntico ao desta pasta; a v27.0 bipartida continua selada no disco). Originalmente esta peça era uma **variante derivada**: o master continuava sendo `01_CAD_MatrizJonatha_Oficial/MatrizJonatha.step` (sha256 `7f26c5c5ba238a12667f2bdf…`, regra 1) e a peça única morava em `07_CAD_Matrizes/Matriz_Jonatha_v27_Peca_Unica/`. O texto abaixo é o da medição original, que continua valendo: a geometria da v29.0 é esta, byte a byte.

## A peça

| grandeza | master bipartido | peça única | o que é |
|---|---|---|---|
| sólidos no arquivo | 2 (Body_A + Body_B) | **1** | sem par, sem jogo de montagem |
| aço | 469001,7 mm³ | **469303,2 mm³** | **+301,5 mm³** = as bolhas seladas e os furos de alinhamento que deixaram de existir (re-medido nesta rodada; o valor anterior, 351,9, era de conta de cabeça, não de medição) |
| massa | 3.6817 kg | **3.6840 kg** | ρ = 7,85 g/cm³ |
| bolhas seladas dentro do aço | 2 (G-03 do auditor) | **0** | os furos de pino cegos deixaram de existir porque não há mais o que alinhar |
| canal (funil + fenda) | 213945,1 mm³ | **213945,1 mm³** | o caminho do material é o mesmo |
| fenda no land (Z = 107.00) | 75.000 × 1.500 mm, R 0.75, área 112.0171 mm² | **75.000 × 1.500 mm, R 0.75, área 112.0171 mm²** | Δ de área = 0.000000 mm² — o produto é o mesmo |
| boca de entrada | Ø 75.60 mm | **Ø 75.60 mm** | a restrição do acoplamento com a extrusora é Ø 75,60 — e não mudou |
| envelope | Ø93.00 Z 0.00..69.90 · Ø89.50 Z 69.90..80.70 · Ø79.50 Z 80.70..109.00 | idêntico | senta no mesmo furo do cabeçote EX-030 |
| boca de saída (Z = 108.99) | 78.000 × 4.500 mm, área 346.6543 mm² (meia-lua (R = espessura/2)) | **78.000 × 4.500 mm, área 346.6543 mm² (meia-lua (R = espessura/2))** | o chanfro 1,50 × 45° abre a boca do mesmo jeito nas duas |
| BRepCheck | — | sólido válido, **0** cara(s) e **0** aresta(s) inválida(s) em **22 caras / 45 arestas** (o par bipartido tem 43 caras / 97 arestas; o 90 que estava aqui contava cada aresta duas vezes, uma por face) | | abre limpa em qualquer CAD (o defeito achado na v28.1 não se repete aqui) |

## O que a peça única tira do produto

A bipartição corta o canal por dentro, no plano Y = 0 — que é o **meio da espessura** da manta. Onde esse plano encontra as paredes do canal nasce a linha de costura que aparece na peça extrudada. Medido no master:

* área de junta metal-metal no plano Y = 0: **1.513,1 mm² por metade** (duas tiras, 758,0 + 755,1), **1.538,2 mm²** na `Body_A` (as duas pastilhas de 12,6 mm² do alinhamento) e **3.051,3 mm²** somando os dois lados no arquivo do par — re-medido com `abre()` + filtro de cara PLANE com normal ±Y e caixa em y = 0; o valor de 759,5 mm² citado antes era uma única tira dessas, não a junta inteira;
* a seção do canal no plano de partição: **8204.4 mm²** ocupando 78.000 mm em X por 109.000 mm em Z, com perímetro de costura de **372.8 mm**;
* **2 linha(s)** de costura correndo nas bordas da manta (x = ±37,50), de ponta a ponta do canal (o perímetro de 372,8 mm da costura é o que faz a junta aparecer no produto, não a área). É por isso que a serra aparece *na borda* e não na face: o plano de partição é perpendicular às faces grandes e paralelo às bordas.

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

## Revisão de 2026-09-22: Ø novos, ±0,5 e a v30 faceada ao nariz

O dono mandou alterar os três Ø do envelope e registrar ±0,5 em toda cota alterada; o modelo e o desenho foram re-gerados juntos (`04_/gerar_revisoes_v29_v30.py`), com o canal de fluxo herdado 1:1 do STEP aprovado. Medido nos dois STEP novos:

| | v29 (re-feita) | v30 (nova) |
|---|---|---|
| Ø dos três estágios | 94.00 / 89.00 / 79.00 | 94.00 / 89.00 / 79.00 |
| comprimento | 109.00 (inalterado) | 95.00 |
| land / fenda / área no land | 8.500 mm · 75.0000 × 1.500 · 112.0171 mm² | idêntico: 8.500 mm · 75.0000 × 1.500 · 112.0171 mm² |
| faces / sólidos / BRep | 22 / 1 / válido | 22 / 1 / válido |
| volume de aço → massa | 477050,9 mm³ → 3,745 kg | 438509,9 mm³ → 3,442 kg |
| canal de fluxo (vazio) | 213945,1 mm³ | 183862,6 mm³ (funil comprimido por s = 0.858586) |
| protrusão além do nariz do cabeçote | +14.00 mm | +0.00 mm |
| interferência com o cabeçote | 0.0000 mm³ | 0.0000 mm³ |
| folga radial nos 3 estágios | 0.50 / 0.50 / 0.50 mm | 0.50 / 0.50 / 0.50 mm |
| material | aço 1045 + indução/nitretação no land | aço 1045 + indução/nitretação no land |

Consequências que precisam continuar escritas junto da peça:

1. **o envelope deixou de ser idêntico ao da Matriz 2 (Gedeon)** — era essa a justificativa dos Ø93,00/89,50/79,50; agora a coincidência acabou e a peça é própria.
2. **a folga anular nos três estágios virou 0,50 mm** (antes 1,00 / 0,25 / 0,25). Isso é o que limita a fuga de material para trás; o efeito no escoamento foi re-medido com o modelo de rotas (ver `SIMULACAO_ROTAS_E_COMPRIMENTO.md`, seção de 2026-09-22).
3. **±0,5 num Ø de envelope não é cota de ajuste fina**, é cota de folga: com Ø94,00 +0,5 o 1º estágio passa a encostar no furo Ø95,00 com folga de 0,00 — o modelo usa o nominal, e a inspeção aceita a faixa. É decisão dele, e o alerta fica aqui.
4. **o 1045 com tratamento na fenda pode mover 1,500** (tolerância +0,010/−0,000): mede-se antes e depois do tratamento, e o retrabalho é re-passar o fio, não aceitar fora.
5. a face de saída da v30 coincide com a face do nariz (Z 95,00, medido). Com +0,5 mm de sobra na cota do comprimento a matriz passaria 0,5 mm para fora do nariz — por isso o pacote anota que, se a fábrica quiser apertar, o aceitável prático é 95,00 −0,50/+0,00.
