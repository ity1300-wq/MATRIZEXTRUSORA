# Serrilhado: por que a v30 não tira, o que tira, e quanto fresar (2026-09-25)

Documento de discussão, pedido por ele: *"nossos estudos já indicavam que o serrilhado não sairia, mas nosso
objetivo é justamente esse"*. Aqui está o problema em números do próprio repo, e o caminho para a matriz que
**tem** o objetivo de resolver. Nenhuma cota foi alterada; se a decisão cair para a rev. 31, isso entra como
proposta no protocolo (`05_/propostas/PRP-0007`) antes de tocar no SSOT.

---

## 1. Primeiro, o que os estudos realmente disseram (e o que não disseram)

* o **D3** (`ESTUDO_FUNIL_COATHANGER.md`) não "previu o serrilhado": ele disse uma coisa mais específica e mais
  grave — que **o único mecanismo que compensa o caminho mais longo das bordas é a altura das asas decrescente
  do centro para as pontas**, e que a variante coat-hanger custava **+141 % de ΔP sem mudar a espessura em um
  mícron**. A v30 tem funil cônico e land de largura constante: **não tem o mecanismo**. Isso é fato de projeto,
  não de simulação.
* o **52,3 %** de "uniformidade" que o `avaliacao_matriz3_uniformidade.py` mede no land **não é o gradiente
  centro→ponta**: é o efeito do **raio R 0,75 nas duas pontas da fenda** (últimos 1,00 mm por lado levando
  0,63 % da vazão, q a 23,2 % do núcleo). Dentro do núcleo, o modelo dá 92,3 % da vazão em ±5 %.
* o modelo é **2D por seção** e portanto **pressupõe pressão igual ao longo da largura** — é literalmente cego ao
  efeito de coletor que estamos discutindo. E o `PLANO_DE_VALIDACAO_E_SIMULACAO.md`, que prometia o contrário
  ("prova matematicamente... sem o efeito serrilhado"), nunca teve CFD atrás (nota de correção datada nele).
* **consequência honesta:** ninguém aqui tem número de distribuição transversal. O que dá para fazer é fechar o
  problema por **ordem de grandeza**, com as leis que o repo já usa, e medir na manta. É o que segue.

## 2. Por que um "pouco" de caminho a mais vira um "muito" de falta de material

O mastique é lei-potência com **n = 0,32** (`cad_die_parameters.json`, `rheological_model_parameters`). Para
fenda retangular, vazão local `q ∝ (1/R)^(1/n)`, e `1/n = 3,125`. **A não-linearidade amplifica**:

| resistência a mais na ponta | vazão na ponta em relação ao centro |
|---:|---:|
| +5 % | **−14 %** |
| +10 % | **−26 %** |
| +20 % | **−43 %** |

É por isso que a matriz dele, com as costas frescadas, "resolve com três decimais de alívio" e a nossa, com um
funil bonito e simétrico, não resolve nada: **a diferença de caminho não precisa ser grande para ser visível na
borda da manta.**

## 3. Para onde vai a pressão hoje (método 1D do projeto, o mesmo dos PRP-0002/0004)

| trecho | ΔP | fatia do total |
|---|---:|---:|
| land paralelo 8,50 mm (2,187 bar/mm) | 18,59 bar | **69,7 %** |
| chanfro de saída 1,50 × 45° (0,907 bar/mm) | 1,36 bar | 5,1 % |
| funil + entrada (tudo o que mora **antes** do land) | 6,73 bar | 25,2 % |
| total (v27.0/v30 de hoje) | 26,68 bar | 100 % |

Só o trecho **de baixo** (25,2 %) é onde o desequilíbrio centro×ponta nasce, porque o land é igual para todos os
`y`. Contando o pior caso (toda a perda do funil como se fosse a mais nas pontas), a ponta cairia a **44 %** da
vazão do centro. É um limite, não uma previsão — mas é do tamanho certo do problema que ele descreve.

## 4. As três alavancas, com o preço de cada uma

1. **Abrir passagem nas pontas** (alívio/rebaixo nas costas, a matriz velha dele: IMG-11 é uma janela rasa e
   corrida atrás da fenda). Reduz `R` da ponta. **Ganho colateral: sobra produção.** No pior caso acima, levar as
   pontas ao nível do centro vale **+39 % de vazão na mesma pressão** (ou a mesma produção com menos pressão na
   extrusora).
2. **Frear o centro** (cantoneira/"bolacha" que ele ofereceu). Aumenta `R` do centro até o nível das pontas.
   **Custo: −39 % de produção** para equalizar o mesmo desequilíbrio — e a extrusora não avisa, a linha é que
   anda mais devagar. Por isso ele serve como **teste de causa**, não como projeto.
3. **Programa de asas de verdade** (coat-hanger: altura decrescente do centro para as pontas). É o remédio de
   projeto e o único com margem para 75 mm de largura; o D3 mediu o preço (+141 % de ΔP no modelo dele), e isso
   exige CFD 3D antes, porque encosta no dimensionamento da extrusora.

**Bloqueio que a gente não pode contornar:** a folha padrão de matrizaria — variar a **folga** da saída
(more open in the middle...) — não serve, porque a peça é 1,500 +0,010/−0,000 em toda a largura. Para equalizar
por folga no pior caso acima, a ponta precisaria de **1,76 mm** contra 1,50 no centro. Está fora de cogitação: a
cota é contrato. O "sorriso" dele é a mesma ideia, mas aplicada ao **contorno** (perímetro dentro de um círculo),
não à espessura — por isso ele é ajustável e por isso ele é feito a mão, na bancada.

## 5. O número que falta não vem de CFD: vem de um paquímetro na manta

Como `q` na saída é proporcional à espessura que a chapa traz, **medir a espessura (e a largura) ao longo da
manta mede o desequilíbrio**. E a correção necessária é pequena, por causa do `n = 0,32`:

| ponta medida com | k que falta | `R_ponta` precisa cair para | leitura |
|---:|---:|---:|---|
| 5 % menos que o centro | 1,053 | **−1,6 %** | raspagem de bancada, meia passada de fresa |
| 10 % menos | 1,111 | **−3,3 %** | raspagem de bancada |
| 15 % menos | 1,176 | **−5,1 %** | raspagem de bancada |
| 20 % menos | 1,250 | **−6,9 %** | alívio dedicado no desenho, ainda sem CFD |
| 30 % menos | 1,429 | **−10,8 %** | alívio dedicado, com CFD de confirmação |

`k^-n` é a lei; a tabela é só ela aplicada. **Prática: 5 pontos na largura (centro, ±18,75, ±37,5 encostando no
raio), 0,01 mm de resolução, na manta deitada e fria** — e a gente sabe o tamanho do alívio sem discutir
teoria. Isso também é o critério de aceite da revisão nova, no lugar do "< 2 % centro×bordas" inventado no plano
antigo: **espalha de espessura ao longo da largura ≤ o que a sua manta boa de PVC aceita hoje** (número que só
você pode dar).

## 6. O que eu proporia como rev. 31 (discutir antes de desenhar)

Mantendo intactos os invioláveis (fenda 75,00 × 1,500, R 0,75, boca de entrada Ø75,60, envelope 3 estágios,
collete EX-031, sem furo/flange/partição):

1. **Chanfro de saída 1,50 → 0,50 × 45°** (o land paralelo vira 9,50). Já está calculado no PRP-0002:
   **27,96 bar (+4,8 %)** e a **parede de aço do lábio sobe de 0,75 para 1,75 mm** — que por si só mata o P7 da
   triagem (risco de robustez do lábio). E a fatia do land sobe de 69,7 % para 74,3 %, ou seja, **o desequilíbrio
   tem menos espaço para existir**.
2. **Janela de alívio na face de entrada**, rasa, de cantos arredondados, correndo atrás da fenda, **mais funda
   nas pontas que no centro** — a versão de projeto do que ele faz na bancada, com **profundidade inicial definida
   pela medição da §5** (não por estimativa minha). Fica aço sobrando: se a medição pedir mais, alivia-se mais
   tarde sem refazer a matriz. Isto é o "recurso" que ele disse ser impossível num corpo cônico.
3. **O freio dele vira opcional e removível**: em vez de metal soldado no canal, a janela do item 2 é o ajuste;
   se um dia quiser freio no centro, ele é feito **estreitando o fundo da janela no centro** (o "mais fechado"
   que ele descreveu).
4. Antes disso: o **teste físico** na matriz em uso (freio dele), porque se a manta não responder a nada, o
   problema é a extrusora (pulsação/temperatura), e nenhuma matriz resolve isso.

Nada disso é número de conversa: os itens 1 e 2 só entram no SSOT como **PRP-0007** com os cálculos do método do
projeto, e o CFD 3D (adiado em 22/09 por você) é o que decide se o item 2 precisa de asa de verdade.

## 7. Frase para levar para a reunião com ele

> A v30 é uma matriz limpa, mas não é uma matriz equilibrada. Você tem razão: ela não tem nada que abra as pontas
> nem que freie o centro. Vamos querer a matriz nova **com o alívio nas pontas já desenhado** (janela rasa na face
> de entrada, mais funda nas pontas, com aço sobrando para ajustar depois), land um pouco mais paralelo (chanfro
> de 0,50) e a fenda e a boca de entrada intocadas. Me diga o que você usinaria nisso e quanto custa; e se o seu
> freio na matriz atual melhorar a manta, isso vira a cota do alívio definitivo.
