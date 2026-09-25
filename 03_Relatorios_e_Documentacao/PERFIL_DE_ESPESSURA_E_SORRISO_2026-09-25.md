# Perfil de espessura medido na linha + as duas soluções que o Fernando mandou (2026-09-25)

Ele mediu a manta em 5 pontos ao longo dos 75 mm, da extremidade A para a B, e mandou duas fotos do Fernando
como exemplos de solução. Este documento converte as duas coisas em número e em decisão. **Nenhuma cota do SSOT
foi tocada**; o que sai daqui é entrada para uma revisão (PRP-0007), não projeto aprovado.

---

## 1. A medição dele, como veio

| estação | A (borda) | A/2 | centro | B/2 | B (borda) |
|---|---:|---:|---:|---:|---:|
| posição `y` na largura | −37,50 | −18,75 | 0,00 | +18,75 | +37,50 |
| espessura medida | **1,50** | **2,00** | **2,57** | **1,80** | **1,50** |

Aviso dele, honesto: *"como o material é massa, não tive tanta precisão"*. É paquímetro em mastique mole, e o
material cede sob a ponta. Assumindo velocidade de linha igual em toda a largura (a manta é um sólido contínuo,
não dá para o centro correr mais que a ponta sem esticar), espessura ∝ vazão local:

| estação | q / q_centro | resistência local extra (com `n = 0,32`) |
|---|---:|---:|
| ±37,50 (bordas) | 0,584 | **+18,8 %** |
| −18,75 | 0,778 | +8,4 % |
| +18,75 | 0,700 | +12,1 % |
| 0 (centro) | 1,000 | — |

**É aqui que a coisa fecha com a conversa toda:** o centro passa **71 % mais material** que as bordas, e a
resistência que explica isso é de só **19 %**. É o efeito `1/n = 3,125` do mastique: desequilíbrio pequeno de
camino, defeito grande na peça. E o inverso também vale - uma correção de resistência de ~19 % já conserta a
peça inteira.

Limite que tem de ficar escrito: se a manta **cai solta na mesa, sem puxador**, espessura não é vazão (o swelling
varia com a taxa de cisalhamento e engorda mais onde sai mais). Nesse caso 19 % é teto, não medida - e a
iteração de bancada (abre um pouco, mede de novo) é o método, não o cálculo.

## 2. O que cada alavanca custa, com o número dele

| caminho | o que faz com a resistência | conta no ΔP do projeto (26,68 bar no método 1D) | efeito na produção |
|---|---|---|---|
| **frear o centro** (o tal bloco) | +18,8 % no centro | **+5,02 bar** | vazão média 0,729 → 0,584 = **80 % da produção atual** |
| **abrir as bordas** (o alívio) | −15,8 % em cada borda | −4,2 bar nas bordas, no orçamento dos **6,73 bar** que o funil+entrada gastam (75 % disso) | vazão média 0,729 → 1,000 = **137 % da produção atual**, ou a mesma produção com menos pressão |

Ou seja, com o número dele a regra sai mais dura do que eu disse antes: **o freio compra informação ao preço de
um quinto da linha; o alívio é o que se fabrica.** E o alívio cabe no orçamento do funil - apertado, mas cabe.
É o argumento objetivo para não mandar "só um freio" como solução definitiva.

## 3. As duas fotos do Fernando (o que eu vejo nelas, sem inventar)

* **Disco azul, fenda em "sorriso", com o relevo `90 x 2mm` na face.** Fenda **curva no plano**, os dois furos
  redondos simétricos acima do arco (a ferramenta de virar a matriz, como ele mesmo explicou). A cor azulada é
  têmpera/óxido de revenimento - peça tratada termicamente. É a solução geométrica: **curvando a fenda no plano
  você muda o caminho do material sem tocar na folga de 1,50** - as pontas chegam mais perto da entrada e o
  centro mais longe, que é exatamente o +19 %/−16 % que a tabela acima pede.
* **Disco de aço com fenda reta, termina em gota nas duas pontas, e um tampo quadrado em relevo no centro**
  (as duas setas verdes apontam o tampo e a fenda). O tampo é o freio: um calço no centro, do lado de dentro,
  obrigando o material a contornar para entrar na boca do meio. **E as pontas em gota são o "abrir mais nas
  extremidades"**, feito na própria fenda - as duas bengalas da fenda são mais largas que o corpo dela.

Sobre o sorriso, a conta que torna isso fabricável sem briga com a peça: **a corda continua 75,00**, então a
largura da manta não muda; o que cresce é o comprimento desenvolvido da fenda.

| sagita do arco | fenda desenvolvida | raio do arco |
|---:|---:|---:|
| 1,00 mm | 75,04 mm (+0,05 %) | 704 mm |
| 2,00 mm | 75,14 mm (+0,19 %) | 353 mm |
| 3,00 mm | 75,32 mm (+0,43 %) | 236 mm |
| 5,00 mm | 75,89 mm (+1,19 %) | 143 mm |

Curvar 2 ou 3 mm custa 0,2 a 0,4 % de comprimento de fenda e **zero de usinagem extra** (é trajetória do fio
EDM, não forma nova). É o ajuste com a maior alavanca por milímetro de que a gente dispõe. O valor da sagita não
é meu para escolher: é a iteração - começa-se pequeno (1 mm), mede-se o perfil de novo, abre-se mais.

## 4. O que a medição dele grita e não é sobre fluxo

**A e B são diferentes:** −18,75 mm mede **2,00** e +18,75 mm mede **1,80** - 10 % de diferença entre os dois
lados, mesma distância do centro. Funil simétrico + fenda reta **não produz assimetria**: no modelo do projeto
os dois lados são o mesmo sólido espelhado. Isso é coisa fora do eixo - matriz montada girada/fora do centro,
assento com cavaco, bucha do cabeçote gasta de um lado, alimentação do funil deslocada, ou a mesa de saída
puxando torto. **Antes de cortar metal, gire a matriz 180° e meça os mesmos 5 pontos de novo**: se a assimetria
mudar de lado com a matriz, é a matriz (ou o assento dela); se ficar no mesmo lado da máquina, é a máquina - e aí
nenhuma revisão de desenho conserta nada.

## 5. Como medir isto direito, sem paquímetro em cima de massa

Corte 5 amostras quadradas na largura (50 × 50 mm, nas mesmas posições de hoje), seque, e pese. Com
ρ = 1,25 g/cm³ (`04_/masti_epdm_reologia.py`), 50 × 50 × 1,50 mm pesa **4,688 g**:

* balança de **0,01 g** resolve **0,0032 mm** de espessura - 3 vezes melhor que um paquímetro em material mole,
  e sem achatar a amostra;
* com 30 × 30 mm (1,688 g) ainda dá 0,0089 mm.

E o critério de aceite passa a ser o que ele quer, não o que o modelo consegue: **a espessura medida nos 5 pontos
com o mesmo desvio que a boa manta de PVC dele aceita.** Esse número só ele pode dar; é a única cota nova que
preciso dele antes de desenhar a rev. 31.

## 6. Rev. 31, com tudo isso em cima da mesa (proposta, não projeto)

Invioláveis mantidos: fenda 75,00 × 1,500 +0,010/−0,000 com R 0,75, boca de entrada Ø75,60, envelope de 3
estágios, collete EX-031 + degrau, sem furo/flange/partição.

1. **Fenda em arco** (sorriso) com corda 75,00 e sagita inicial **1,00 mm**, marcada no desenho como
   *cota de ajuste*: "abrir mais, até 3,00, só na bancada e com o perfil medido na mão".
2. **Janela de alívio rasa na face de entrada**, corrida atrás da fenda, fundo **mais próximo da boca nas bordas
   que no centro** - que é o "mais abertas nas pontas, fechado no centro" dele. Profundidade inicial definida
   contra o +18,8 %, com aço sobrando para ajustar depois.
3. **Chanfro de saída 1,50 → 0,50 × 45°** (land paralelo 9,50): já calculado no repo (PRP-0002), 27,96 bar
   (+4,8 %) e a parede do lábio de 0,75 para 1,75 mm, o que também fecha o P7 da triagem. Menos espaço para o
   desequilíbrio nascer, porque o land passa de 69,7 % para 74,3 % do ΔP.
4. **Sem freio removível no desenho** - o freio é o teste dele, não a solução nossa (custa 20 % da linha).
5. Antes de fechar: **ver o §4** (assimetria). Se for máquina, a lista acima muda de prioridade: conserta-se o
   assento primeiro e talvez nem precise de arco.

Nada disso entra em `cad_die_parameters.json` nem em STEP sem virar **PRP-0007** com os cálculos do método do
projeto por trás, e sem CFD 3D quando a escolha for asa de cabide (aí sim: o D3 mostrou +141 % de ΔP).
