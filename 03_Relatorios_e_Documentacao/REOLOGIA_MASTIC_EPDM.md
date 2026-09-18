# Reologia do mastique resistivo à base de EPDM — o que a simulação vai usar

Você definiu o material (*"mastic resistivo não linear a base de EPDM"*) e mandou buscar valores de literatura. Este arquivo é o resultado, gerado por `04_Dados_SSOT_e_Scripts/masti_epdm_reologia.py`: **uma banda, não um número**, porque reômetro deste lote não existe no repo e inventar precisão aqui seria o pior tipo de erro.

## Os três jogos

| nível | K (Pa·sⁿ) | n | η(0,1 s⁻¹) | η(10 s⁻¹) | η(100 s⁻¹) | η(1000 s⁻¹) (Pa·s) | o que representa |
|---|---|---|---|---|---|---|---|
| `otimista` | 37678 | 0.30 | 188838.8 | 37678.3 | 7517.8 | 299.3 | banda baixa: mastique quente e bem plastificado - o minimo plausivel para um resistivo |
| `tipico` | 125594 | 0.30 | 629462.7 | 125594.3 | 25059.4 | 997.6 | centro da faixa: o que a literatura de composto EPDM + negro de fumo pede em 10^2 1/s |
| `pessimista` | 376783 | 0.30 | 1888388.1 | 376783.0 | 75178.1 | 2992.9 | banda alta: mastique frio e muito carregado - o cenario em que nada passa pela fenda |

Ponto de partida: o SSOT traz K = 18500 Pa·s^0.32 a 190 °C (EPR/XLPE/PVC modificado). Deslocado para 90 °C com a Ea/R do próprio SSOT, dá K = 231512; os três níveis acima são 3×, 8× e 20× esse valor — que é a ordem de grandeza entre um masterbatch e um mastique resistivo muito carregado.

## Os dois critérios que a simulação tem de responder

1. **passa ou volta** — a queda de pressão necessária na fenda de cada matriz, comparada à janela da linha: no processo análogo medido na literatura, matriz de perfil EPDM opera com **2,1–9,4 MPa** a 41–128 g/min. Acima do topo, o material procura outra saída; e neste conjunto existe exatamente outra saída (medida na C4 da auditoria de correlações: anel com folga de 1,00/0,25/0,25 mm, contínuo do bico até a entrada da matriz).
2. **raspa ou não raspa** — a tensão de cisalhamento na parede na boca de saída. O limiar de *sharkskin* é **0,14 MPa** (escorregamento a partir de ~0,1 MPa; com auxiliar de processamento, até ~0,5 MPa). Onde a parede passa disso nos **cantos** da fenda, é aí que a serra aparece — e é por isso que a forma da borda (estádio × canto vivo) foi medida na auditoria, na seção a 0,01 mm da face de saída: Copo e Gedeon CERTA dão **112,017 mm²** = estádio 75,00 × 1,50 com R 0,75; Jonatha v27 e v28.1 dão **346,654 mm²** = o mesmo estádio já aberto pelo chanfro de saída (boca 78,00 × 4,50); a `MatrizDesenvolvimento` histórica dá **351,0 mm²** = o retângulo 78,00 × 4,50 **sem arredondamento nenhum** — canto vivo, onde a manta rasga. É a diferença geométrica que a sua serra na borda pede para olhar primeiro.

## O que não é medido aqui

* não há reômetro deste lote específico no repo: K é a família do SSOT deslocada em temperatura e multiplicada por 3/8/20 — os três números têm de ser lidos como intervalo
* o limiar de escoamento (tau_y) é faixa de literatura, não medida: se ele existir de fato, o miolo da fenda para de escoar antes da borda, e é aí que a serra nasce
* a temperatura real do seu cabeçote (EX-030) não foi medida; usamos a da linha análoga (90 C)

## Fontes

* dP de matriz 2,1-9,4 MPa; 41-128 g/min; matriz a 70 C, cabeça 79-87 C (EPDM, perfil) — Polymers 18(9):1122 (2026) — Numerical Investigation of Die Swell Behavior in EPDM Rubber Extrusion ([link](https://www.mdpi.com/2073-4360/18/9/1122))
* sharkskin em tau_parede >= 0,14 MPa; escorregamento em ~0,1 MPa; limiar sobe a ~0,5 MPa com auxiliar de processamento/BN — J. Vlachopoulos, The Role of Rheology in Polymer Extrusion ([link](http://www.polydynamics.com/Rheology.pdf))
* composto cru: lei-potência boa em faixa larga de gama, Herschel-Bulkley melhor no total — Journal of Rheology 70, 65 (2026) — Viscosity characterization of uncured rubber compounds via uniaxial compression ([link](https://pubs.aip.org/sor/jor/article/70/1/65/3374181/))
* EPDM com negro de fumo: viscosidade/tau_Parede/die swell medidos em capilar; Cox-Merz não vale — Polymer 39 (1998) — Rheological properties of EPDM compound ([link](https://www.sciencedirect.com/science/article/abs/pii/S0032386197002310))

Gerado em 2026-09-13. Os números de geometria citados vêm de `03_/AUDITORIA_CORRELACOES_STEP.md` (medidos nos STEP).
