# Rotas do mastique: passa pela fenda ou escapa pelo anel — e 109 mm × 100 mm

Gerado por `04_Dados_SSOT_e_Scripts/simular_rotas_e_comprimento.py`. Geometria **medida nos STEP** (o vazio da peça inteira, seção de 0,02 mm varrendo Z) e folgas do anel lidas do bloco C4 da auditoria de correlações. Reologia de `04_/masti_epdm_reologia.json` (banda ancorada em η(100 s⁻¹), com as quatro fontes). Vazão do projeto: 15000 mm³/s = 15,0 cm³/s (a do SSOT).

## A resposta, direta

**Deixa em 109 mm.** Encurtar para 100 mm não mexe em nada que gere pressão — o funil e o land ficam intactos, os 9,00 mm a menos são aço liso do meio da peça — e **encurta o caminho de fuga**: o anel entre a matriz e o furo do cabeçote é a rota pela qual o material escapa para trás, e anel mais curto tem menos resistência, então escapa *mais*. É esse o sinal que a tabela de cenários mostra.

## O que cada matriz exige, com o mesmo material e a mesma vazão

| matriz | comprimento | **land paralelo medido** | área no land | ΔP típico (bar) | banda baixa | banda alta | escapa pelo anel | saída (m/min) | τ no land (MPa) | raspado? |
|---|---|---|---|---|---|---|---|---|---|---|
| `Copo (original)` | 80,70 mm | **9,75 mm** | 112,0170 mm² | **211,2** | 63,4 | 633,7 | 1,327 % | 7,89 | 0,794 | SIM |
| `Gedeon CERTA (a sua)` | 109,00 mm | **88,50 mm** | 112,0170 mm² | **963,0** | 288,9 | 2.888,9 | 9,140 % | 7,27 | 0,775 | SIM |
| `Jonatha v27.0 (bipartida)` | 109,00 mm | **8,50 mm** | 112,0170 mm² | **219,9** | 66,0 | 659,7 | 0,067 % | 7,99 | 0,797 | SIM |
| `Jonatha v29.0 (peça única)` | 109,00 mm | **8,50 mm** | 112,0170 mm² | **219,9** | 66,0 | 659,7 | 0,067 % | 7,99 | 0,797 | SIM |

**Leitura da tabela: o que separa as matrizes é o comprimento de land, não o comprimento da peça.** A fenda da Gedeon é passante — medida, ela tem land paralelo de **88,50 mm** contra **8,50 mm** da Jonatha — e o dP do land é linear no comprimento do land: 963,0 bar contra 219,9 bar, e a fração que escapa pelo anel sobe de 0,067 % para **9,140 %** (136×). É a versão numérica do "volta pelo funil": não é que o funil puxe o material para trás, é que a fenda da Gedeon exige pressão que a linha não tem, e o material procura o caminho de menor resistência.


## Os cenários de comprimento e de folga (Jonatha v29.0)

| cenário | ΔP típico (bar) | escapa pelo anel | saída (m/min) | o que faz com a volta pelo funil |
|---|---|---|---|---|
| 109 mm (como está) | 219,9 | 0,067 % | 7,99 | corta a fuga sem encostar no produto |
| 100 mm (encurtar a peça) | 219,9 | 0,071 % | 7,99 | piora: o anel encurta e a fuga fica mais fácil |
| 100 mm + pinça de 0,15 na saída do anel | 219,9 | 0,036 % | 8,00 | piora: o anel encurta e a fuga fica mais fácil |
| 109 mm + land 6,00 | 196,2 | 0,045 % | 8,00 | menos pressão exigida da linha — o land é a alavanca |
| 109 mm + land 5,00 | 186,7 | 0,039 % | 8,00 | menos pressão exigida da linha — o land é a alavanca |
| 109 mm + anel apertado nos 3 estágios (0,40/0,15/0,15) | 219,9 | 0,003 % | 8,00 | corta a fuga sem encostar no produto |
| 109 mm + anel apertado só no último estágio (0,10) | 219,9 | 0,002 % | 8,00 | corta a fuga sem encostar no produto |

## O que ainda falta para isso ser afirmação de processo, e não prévia

* O funil é aproximado por placas de abertura média 6,00 mm (o `manifold_central_depth_mm` do SSOT) no comprimento medido. O que diz se há zona morta dentro do funil é a CFD 3D no volume dele (gmsh + scikit-fem: ambiente montado e testado, é o item deixado para a próxima etapa). Esta conta separa as rotas; não resolve recirculação.

* `escapa pelo anel` é a vazão que o anel leva sob o **mesmo ΔP** das duas rotas: mede a fuga entre matriz e furo, não a velocidade com que o material volta pelo funil de alimentação da extrusora — isso depende da curva da rosca, que não está no repo.

* A reologia é banda de literatura (η de 1,500 a 15,000 Pa·s em 100 s⁻¹), não reômetro do lote. O que é independente da banda: **a ordem das matrizes e o sinal de cada cenário** (as três curvas dão a mesma hierarquia, porque tudo escala com K).

* O limiar de raspado (τ ≥ 0,14 MPa, literatura de capilar) dispara para **todas** as matrizes nesta vazão (15 cm³/s ≈ 9× a da linha análoga da literatura). Ou a linha real opera com o material mais quente/mais plastificado que a banda baixa, ou o limiar do produto plano é maior que o do capilar. É pergunta para o reômetro, não para o CAD.


Janela de referência da linha análoga (EPDM, perfil): ΔP de matriz **2,1–9,4 MPa** a 41–128 g/min; o repo tinha 41,9 bar de ΔP 1D calibrado para a v27.0, que é da ordem da janela — a banda baixa desta tabela bate com ela.

## Re-medido em 2026-09-22 com as folgas novas

Re-executado o mesmo modelo (mesmo mastique, mesma vazão Q = 15000 mm³/s, as três curvas de reometria do arquivo) com o anel de fuga **medido nas montagens novas** e a rota da fenda medida no STEP de cada revisão. Nada foi copiado da tabela anterior.

| revisão | folgas do anel (mm) × comprimento congruente | dP (tipico) | escapa pelo anel | v de saída | τ no land |
|---|---|---:|---:|---:|---:|
| v29 | 0,50 × 69,9 (Ø94,5) + 0,50 × 10,7 (Ø89,5) + 0,50 × 14,0 (Ø79,5) | **219,7 bar** | 0.277 % | 7,98 m/min | 0.797 MPa |
| v30 | 0,50 × 69,9 (Ø94,5) + 0,50 × 10,7 (Ø89,5) + 0,50 × 14,0 (Ø79,5) | **203,6 bar** | 0.215 % | 7,98 m/min | 0.797 MPa |

Leitura honesta: abrir a folga dos estágios 2 e 3 de 0,25 para 0,50 mm **triplica a fração que escapa para trás** nos cenários com a matriz comprida, e o encurtamento da v30 devolve um pouco (menos trecho de anel dentro do nariz). A fenda em si não muda nada: land, área e chanfro são os mesmos medidos, então a vazão de produto e a espessura da manta continuam as da tabela acima. Quem decide a uniformidade da manta é a coaxialidade dos estágios, não o Ø.

Números completos em `04_Dados_SSOT_e_Scripts/revisoes_2026_09_22_simulacao.json` (as três curvas, trecho por trecho).
