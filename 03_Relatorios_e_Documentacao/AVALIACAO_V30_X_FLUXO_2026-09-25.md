# Avaliação: a v30 resolve o serrilhado da manta? (2026-09-25)

Pergunta dele, literal: *o Fernando acha que não vai resolver, avalie*. E o enquadramento que ele deu: a v30
**é a matriz bipartida convertida em peça única** — geometria de fenda, land e chanfro idênticos ao master
v27.0; o que mudou foi o funil, o comprimento (faceada ao nariz) e a junta eliminada. Abaixo o veredito com os
números que **já existem neste repositório**, todos re-citados com o arquivo de origem; nada aqui veio de chute,
e onde o repo não sabe responder, está escrito que ele não sabe.

---

## 1. Veredito em uma frase

**Fernando está certo no essencial: nenhum elemento da v30 redistribui vazão na largura da fenda — e a v30
nunca deveria ter sido apresentada como a correção do serrilhado, porque o que ela corrige é outra coisa (a
junta), que também é um defeito real.**

## 2. O que o projeto já media sobre isso (e eu não bati na tecla o suficiente)

| fato | número | onde está |
|---|---:|---|
| uniformidade transversal no land, `q_min/q_max` | **52,3 %** (Z = 99,5 / 103,0 / 107,0) | rodado agora: `04_/avaliacao_matriz3_uniformidade.py` |
| variação dentro do núcleo plano (｜x｜≤ 36,75 mm, 98 % da largura) | **92,3 % da vazão dentro de ±5 %**; 97,0 % dentro de ±10 % | idem |
| vazão nos **últimos 1,00 mm de cada lado** | **0,63 %** da vazão total, com q = **23,2 %** do núcleo | idem |
| perfil na borda (q em mm³/s/mm) | 215,5 no centro → 162,1 → 141,1 → 112,7 → 37,6 aos 37,25 mm | idem |
| τ na parede na saída do land | **160,9 kPa** (mesma tabela) | idem |
| limiar de rasgo de borda / *sharkskin* adotado pelo projeto | **0,14 MPa** (Vlachopoulos; sobe a 0,5 MPa com aids) | `04_/masti_epdm_reologia.py:19` |
| ΔP da matriz (v30) com o anel de fuga medido | **203,6 bar**, τ no land 0,797 MPa, v de saída 7,98 m/min | `03_/SIMULACAO_ROTAS_E_COMPRIMENTO.md`, tabela de 22/09 |
| o que um coat-hanger de verdade custaria | **+141 % de ΔP** (100,9 × 41,9 bar no método do projeto), **sem mudar a espessura** — porque fenda e land são os mesmos | `03_/ESTUDO_FUNIL_COATHANGER.md` (D3) |

Lendo a tabela do D3, a frase que decide é a recomendação que **o próprio repo escreveu antes**: o único
mecanismo que compensa o caminho mais longo das bordas é **altura das asas decrescente do centro para as
pontas** (`h(±37,50) < h(0)`) — e não é o funil cônico que temos. A v30 tem funil cônico + land reto de largura
constante: ela **não tem** o mecanismo.

## 3. Por que isso é diferente de "a v30 é inútil"

A v30 resolve, com número, três coisas que a bipartida não resolve:

* **junta de partição zerada** — a costura corria pelas duas bordas da manta (372,8 mm de perímetro no plano
  Y = 0, 759,5 mm² de contato metal-metal) e é exatamente dali que vem degrau/rebarba de junta, que aparece
  como risco na manta (`03_/MATRIZ_V27_PECA_UNICA.md`, e o "motivo" da inspeção nº 8: *"face ondulada abre
  junta de material e aparece como risco na manta"*);
* **0,00 % da superfície do canal em sombra** — nada de plástico parado que queima e volta como gel/inclusão;
* **face rasante ao nariz** (protrusão 0,00) e comprimento 95,00 −0,50/+0,00, com ΔP 8 % menor que a v29
  (203,6 × 219,7 bar).

Nada disso é equilíbrio de fluxo. É limpeza, purga, repetibilidade e montagem. Se a manta hoje tem risco
*vindo da junta*, a v30 sozinha melhora a peça — e essa parte do ganho é real e mensurável.

## 4. O limite honesto do nosso próprio modelo (por que ninguém aqui pode "provar" nada)

O `avaliacao_matriz3_uniformidade.py` trabalha sobre **cortes 2D seção a seção**: em cada seção ele resolve o
perfil e integra a vazão por mm de largura. Isso **pressupõe pressão igual ao longo da largura daquela seção**
— ou seja, o modelo é *cego* ao mecanismo que o Fernando descreve (diferença de pressão entre o caminho curto do
centro e o caminho longo da borda, que é um efeito de coletor 3D). Então:

* o **52,3 %** acima é a geometria do canto (R 0,75), não o gradiente centro→borda. Não serve de defesa nem de
  acusação;
* os 99,10 % / 68,96 % / 54,73 % que apareciam no relatório de CFD do cliente já estavam marcados como **não
  auditáveis** (`03_/TRIAGEM_DE_PROBLEMAS_DAS_MATRIZES.md`, P6), e as discrepâncias de ΔP medidas lá (0,39× e
  0,13× do declarado) são motivo de sobra para não confiar em nenhum número de uniformidade que venha de fora;
* **a única coisa que fecha essa questão é CFD 3D com o mastique medido, que você mesmo adiou em 22/09** (CFD
  adiado, decisão registrada). Sem isso, o que se decide abaixo é por risco e custo, não por simulação.

## 5. Dois números que a v30 não muda, e que a conversa não tocou

1. **τ na parede na saída: 160,9 kPa, e o limiar que o projeto adota é 140 kPa** (`masti_epdm_reologia.py`).
   Para um fluido em regime, `τ_parede` no land depende de **vazão por unidade de largura e da folga** — não do
   comprimento do land nem da forma do funil. Como a peça é 1,50 mm de espessura e a linha é a mesma,
   **nenhuma matriz nova derruba o τ**: o que mexe nele é vazão da linha, temperatura da matriz/fundido e aids de
   processo. Isso vale para a v30 e para o "sorriso" dele igualmente.
2. **Serrilhado de borda ≠ *sharkskin*.** Na foto da amostra (IMG-06 do PDF) o denteado é **idêntico nas duas
   bordas longas** — assinatura de faca/disco; e os dois quadros do vídeo que o PDF embute mostram um **disco
   girando encostado na borda**, com a superfície do perfil lisa ao lado (`03_/CONTATO_MATRIZARIA_FERNANDO_2026-09-24.md`, §3b). Se o
   denteado vem do corte ou da puxada, **matriz nenhuma resolve**, e a v30 seria fabricada para "não ter
   funcionado" injustamente. As "ondinhas" no centro são outra coisa (aí sim, fluxo/pulsação) — e crista
   transversal periódica é também a assinatura de pulsação da rosca, que se trata com tela/filtro, não com
   land.

## 6. Onde o veredito dele é injusto com a v30

Ele comparou nosso projeto com a matriz que **ele mesmo** fabricou: disco plano, sem degrau, sem chanfro, sem
land paralelo, fenda cortada e sem retífica, com rebaixo nas costas como único ajuste (IMG-10/11 do PDF). A v30
tem três estágios com coaxialidade Ø0,02, land 8,50 retificado, Ra ≤ 0,4, fenda a fio EDM depois do tratamento,
tolerância de +0,010/−0,000 na abertura. Isso não é "igual ao que ele faz, só que caro": é outra classe de peça.
A crítica dele é **específica ao canal de fluxo**, e nesse ponto ela é correta — não é uma nota geral sobre a
matriz.

## 7. O que eu faria, na ordem do mais barato

| # | ação | o que decide | custo |
|---|---|---|---|
| 0 | Medir o período das cristas e comparar com o passo da rosca (régua na manta, 5 min) e ver o vídeo completo do corte | é fluxo, é pulsação ou é o disco de corte? | zero |
| 1 | **Freio na matriz que está em uso** (a oferta dele: cantoneira/disco) | se a manta melhora com freio no centro, **a causa é equilíbrio** e a v30 sem freio não resolveria mesmo | o menor que existe; reversível |
| 2 | Se (1) ajudar: **rev. 31 = v30 + janela de alívio na face traseira** | mantém peça única e sem junta no fluxo, e devolve o "recurso de bancada" que ele diz ser impossível num corpo cônico | desenho novo, mesma fabricação |
| 3 | Em paralelo, pedir a cotação da v30 como está, **com a ressalva escrita de que ela não promete equilíbrio** | preço e prazo reais para decidir com número | zero |
| 4 | Só depois disto, CFD 3D (o que ficou adiado) para dimensionar asas decrescentes | se vale pagar o +141 % de ΔP que o D3 mediu | o caro, e mexe no dimensionamento da extrusora |

**Recomendação:** não mandar fabricar a v30 como "cura do serrilhado" agora. Mande como **fabricação da matriz
limpa de peça única** se você quer o ganho da junta zerada de qualquer forma — mas feche primeiro o passo 0 e o
passo 1, porque são dias e quase nada de dinheiro, e eles é que dizem se a geometria de canal merece +40 % de
usinagem. E se o caminho for "freio", prefiro a **rev. 31 com alívio na traseira** ao corpo cônico seco: é o
único jeito de não ficar sem recurso depois, que é exatamente o medo que ele formulou.

## 8. Correção que eu devo ao próprio repositório

`03_/PLANO_DE_VALIDACAO_E_SIMULACAO.md` (documento antigo, anterior às rodadas medidas) tem três frases que não
se sustentam: *"Prova matematicamente que a fita sairá perfeitamente retilínea, sem arrasto nas pontas e sem o
efeito serrilhado (sharkskin)"*, *"NÃO haverá refluxo pelo funil de alimentação"* e *"NÃO ocorrerão os rasgos de
borda (edge tearing)"*. Ele as apresenta como resultado de um CFD que **nunca foi rodado** (o critério era
"diferença de velocidade centro×bordas < 2 %", que nenhum arquivo deste repo mediu), e ainda chama o denteado
de borda de *sharkskin*, que é fratura de superfície do fundido — outro fenômeno, com outro remédio. Marquei o
texto com nota de correção datada; o arquivo fica como estava, porque apagar histórico de plano é pior do que
anotar que ele errou.

## 9. O que este documento **não** fez

Nenhuma cota, geometria, JSON, prancha, pacote ou tag foi alterada. Se você escolher o passo 2, a rev. 31 nasce
de projeto + medição no STEP (com o `restaurar_workspace.sh` de pé para re-medir), não de número de conversa.
