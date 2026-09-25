# A matriz copo dentro do cabeçote — o que dá para resfriar, e onde

**2026-09-25, 9ª rodada.** Pediu: *olhe como a matriz copo fica no cabeçote e pense no resfriamento.*
Alvo dele continua sendo o **serrilhado nas pontas** (rodada 8ª). Espessura não é o problema dele, e este
documento não trata de espessura.

**De onde saem os números:** todos os mm abaixo foram medidos nesta rodada, com `cadquery`, no arquivo
`06_CAD_Cabecote_EX-030/STEP/Cabecote_EX-030_com_Matriz_Copo.step` (montagem real: cabeçote + matriz copo,
cada um no seu sólido, sem booleano) e nos STEP das outras matrizes montadas no mesmo cabeçote. Distância de
peça a peça é `BRepExtrema`. Volume é `GProp`. A conta de calor usa o land medido no STEP e a vazão
Q = 15.000 mm³/s, K = 18.500, n = 0,32 do `04_Dados_SSOT_e_Scripts/verify_legacy_dies.py`, com a lei do
gradiente 2,187 bar/mm do `05_Interface_Auditoria/propostas/PRP-0002`. Densidade do aço 7,85e-6 kg/mm³,
cp do aço 486 J/kg·K, cp do mastique 2 J/g·K, ρ do mastique 1,25e-3 g/mm³
(`04_Dados_SSOT_e_Scripts/masti_epdm_reologia.py:59`), k do aço 45 W/m·K, k da borracha 0,25 W/m·K.

**Para conferir sem depender da minha palavra:** `python3 04_Dados_SSOT_e_Scripts/verificar_resfriamento_copo_2026_09_25.py`
re-mede os STEP e re-faz cada conta deste documento, comparando com o valor escrito. Estado na rodada:
**54 conformes, 0 divergentes**.

---

## 1. O que é a matriz copo (medido)

| o quê | medido |
|---|---|
| corpo | Ø93,00 × 80,70 mm (volume 224.289,0 mm³ = **1,761 kg**) |
| o "copo" | furo **Ø75,60 × 70,70 mm** de fundo, entrando pela **traseira** |
| a fenda | 75,00 × 1,500, R 0,75, atravessando o fundo do copo: land = **10,00 mm** (Z 70,70 → 80,70) |
| boca | **sem chanfro** e **sem funil**: o fundo do copo é um degrau reto de 90° contra a fenda |
| casca total | **55.129,7 mm²**, face por face: banda Ø93 **20.422,6** (37,0 %) · furo do copo Ø75,60 **16.791,6** (30,5 %) · face frontal **6.179,2** (11,2 %) · fundo do copo **4.376,8** (7,9 %) · estágio Ø89,5 **3.036,7** (5,5 %) · face traseira **2.304,1** (4,2 %) · paredes do land **1.517,1** (2,8 %) · ombro **501,7** (0,9 %) |
| onde ela toca massa | furo + fundo + face frontal + land = **28.864,7 mm² = 52,4 %** da casca. Os outros 47,6 % estão em vão de 0,10–1,00 mm. **Nada dela toca o ar.** |

Referencial: **Z = 0** é o plano mais traseiro do cabeçote; a **face do nariz** do cabeçote (por onde a manta
sai para o ar) está em **Z = 95,00**.

## 2. Como ela fica sentada — face a face, enterrada

| parte da matriz | onde cai no cabeçote | folga medida (BRepExtrema) |
|---|---|---|
| banda Ø93,00, Z 0,00 → 69,90 | bolso Ø95,00 (Z 0,00 → 70,00) | **1,00 mm** radial — ar parado; e é a banda que o collete aperta |
| ombro (anel Ø89,5→Ø93) em Z 69,90 | degrau em Z 70,00 | **0,10 mm** axial; anel de 501,7 mm², contato real 431,2 mm² quando a pressão fecha |
| estágio Ø89,50, Z 69,90 → 80,70 | furo Ø90,00 (Z 70,00 → 81,00) | **0,25 mm** |
| **face de saída**, Z 80,70 (anel de 6.179,2 mm²) | o metal mais próximo é a parede do furo Ø90,00; o plano do degrau está 0,30 mm à frente | **0,25 mm** radial / **0,30 mm** axial |
| face traseira, Z 0,00 (anel de 2.304,1 mm²) | rasa com a traseira do cabeçote → no canal de massa | — |

As três consequências, todas medidas:

1. **A boca da matriz está 14,30 mm para dentro do cabeçote** (80,70 contra 95,00). À frente dela há
   **70.371,7 mm³** de furo Ø80,00 × 14,00 mm, e esse vão fica **cheio de massa** — a manta nasce dentro de
   um túnel do cabeçote e só vê ar depois de 14,30 mm.
2. **Nenhuma parte da matriz vê o ar.** Os 55.129,7 mm² da casca estão todos ou molhados de massa (52,4 %) ou
   num vão de 0,10–1,00 mm (47,6 %). A banda, que é 37,0 % da casca, está no vão de 1,00 mm de ar **e** é a
   banda de aperto do collete: não dá para encostar nada ali.
3. **A copo não pode ser feita protruir.** Para a boca sair do túnel faltariam 1,50 mm de raio: a banda
   Ø93,00 não passa do degrau Ø90,00, e a folga axial de encosto no degrau é de 0,10 mm (0,091 mm na varredura de 0,20 mm do `medir_perfis_matrizes_x_cabecote.py`).
   *Comparação medida nas outras montagens do mesmo cabeçote:*

| matriz | comprimento | face de saída | boca em relação à face do nariz |
|---|---|---|---|
| **copo (a que está na máquina)** | 80,70 | Z 80,70 | **14,30 mm para dentro** |
| JONATHA **v30** | 95,00 | Z 95,00 | **rasa (0,00)** — a boca fica no plano da face, alcançável |
| JONATHA v29 / v27 | 109,00 | Z 109,00 | **14,00 mm para fora** — boca livre, mas o túnel não é resfriado |

## 3. Por que ela "enche de calor" mais rápido que a v30

- A copo tem **855,7 J/K** de capacidade térmica (1,761 kg × 486). A v30 tem 1.673 J/K: **o dobro de aço
  para esfriar**. Ou seja, a copo esquenta o dobro mais rápido com o mesmo watt.
- Dentro do copo ficam **318.480,7 mm³ de massa** (medido no `Matriz1_Original_Copo_Canal_Fluxo.step`):
  **398 g** de borracha, outros **796 J/K** a 90 °C, trocados a cada **21,2 s** (V/Q). Essa massa dentro do copo
  toca o furo e o fundo: **21.168,4 mm² = 38,4 %** da casca da matriz. O copo é banho-maria por dentro, e por
  fora o vão de 1,00 mm de ar não deixa sair nada.
- Calor que a fenda gera: ΔP_land = 2,187 bar/mm × 10,00 = **21,87 bar** → 21,87e5 Pa × 15,0e-6 m³/s =
  **32,8 W**. O teto da rodada 8ª (simulação do pacote, 203,6 bar) foi **305 W**.
- Com esse calor preso: **33 W sobem o lábio 20 °C em 8,7 min**; **300 W em 0,95 min**. Isso é o sintoma dele:
  sai boa no começo, e "aos poucos, quando acelera a produção, vai enchendo de calor".

## 4. Os caminhos que o calor tem — e o gargalo de verdade

Resistência térmica = espessura ÷ (k × área). Folgas medidas na tabela 2:

| caminho da boca da matriz para fora | R (K/W) | 300 W custam |
|---|---|---|
| filme de **massa** de 0,30 mm na face frontal (6.179,2 mm²) | **0,194** | 58 K |
| o mesmo vão de 0,30 mm cheio de **ar** | 1,867 | 560 K |
| filme de 0,25 mm no estágio Ø89,50 (3.036,7 mm²) | 0,329 | 99 K |
| filme de 1,00 mm de ar na banda do collete (20.422,6 mm²) | 1,883 | 565 K |
| 18,50 mm de aço do nariz até a banda Ø130 (17.153,1 mm²) | 0,024 | 7 K |
| água com h = 2.000 W/m²·K num colar de 28,00 mm (11.435,4 mm²) | 0,044 | 13 K |

**Ler isso em português:** o caminho curto existe. A face da matriz está a **0,25–0,30 mm** do aço do
cabeçote, e o vão de 1,00 mm da banda (onde o collete aperta) é o que não vale nada. Como a matriz trabalha a
20–200 bar, esse vão de 0,30 mm está cheio de massa, não de ar — e é por esse filme que o aquecimento entra
**e** por ele que dá para o calor sair.

## 5. A conclusão da rodada: com a copo, o resfriamento é no cabeçote — na faixa do degrau

Isso é a decisão que ele já tinha tomado (refrigeração no `06_CAD_Cabecote_EX-030`, não na matriz), e agora
tem número:

- O corpo do cabeçote tem uma **banda lisa Ø130,00 de Z 53,00 a 95,00** (42,00 mm, 17.153,1 mm² de aço),
  a **18,50 mm** da banda da matriz. É a única superfície de aço grande, limpa e alcançável do conjunto.
- Furos no corpo do cabeçote, medidos na montagem: os 6 furos Ø16,5 da junta passam a **35,25 mm** da matriz
  e ficam em Z 3,00–43,00; o único furo transversal na região útil é o **M12 do pushador, em Z 22,98** —
  ambos **fora** da faixa 53–95. Então a banda está livre para receber um colar.
- **Não fure o cabeçote para passar água:** ele é SAE8620 cementado 0,4–0,6 mm e temperado a 52–55 HRC
  (`04_Dados_SSOT_e_Scripts/cabecote_ex030.json`). Furo/rosca nessa carepa é trabalho de EDM, não de furadeira.
- **Capacidade:** se a faixa 53–81 ficar 40 °C mais fria que a matriz, os filmes de 0,30 e 0,25 mm puxam
  40/0,194 + 40/0,329 ≈ **330 W**. Isso é mais que os 33 W do land e da mesma ordem do teto de 305 W.
- **Quanta água:** 300 W = **+4,3 °C** de elevação em **1 L/min** (0,2 L/min = 21,5 °C; 3 L/min = 1,4 °C).
  Uma torneira de tanque chega. Chiller não é necessário.
- **Limite honesto:** o gargalo é o filme de 0,30 mm, não a água. Ele leva ~150 W com 30 °C de diferença.
  Se o vão de 0,30 mm estiver com ar (matriz parada, ou massa que não entra no vão), a conta cai 10×.

## 6. O que fazer, do de graça para o que custa um dia

**A. Pano encharcado + gotejador na banda Ø130 (Z 53 → 81).** Custo zero, teste para hoje. Uma faixa de
pano/algodão molhado dada de volta a cada tanda, ou um pano passado por um fio gotejando. h de evaporação em
pano molhado é da ordem de 100–300 W/m²·K sobre os 11.435,4 mm² da faixa → **0,3 a 0,9 K/W**. Traduzindo: o
pano leva os **33 W do land com 10 a 30 °C de diferença** — que é o que se consegue a céu aberto. Os 300 W do
pior caso não saem por pano, só por água. **Regra do teste:** cronometre o tempo até o primeiro dente de serra,
com e sem o pano, na mesma velocidade. Se o tempo dobrar, é térmico.

**B. Faca de ar na manta, 3–5 cm depois da FACE DO NARIZ — não na boca.** Com a copo a boca está a 14,30 mm
para dentro do túnel, então nada de tentar soprar na matriz: o ar tem de pegar a manta **depois** que ela sai
do Z = 95,00. Fenda de 0,5–1,0 mm nos 75 mm, ar a 0,3–0,5 bar. Isso resfria a pele **e** segura a borda
contra o puxamento do centro — é o item que mexe nos dois lados do serrilhado.

**C. Colar d'água partido na banda Ø130, faixa Z 53 → 81 (28,00 mm).** Duas conchas com canal de 3 mm e
O-ring, abraçadeira de corona. Não fura o cabeçote, não encosta na matriz, não pega o pushador (Z 22,98) nem
os furos da junta (Z 3–43). **Por que parar em Z 81,00:** Z 81–95 é o nariz, o túnel por onde a manta sai.
Resfriar o túnel é o caminho mais rápido para a massa congelar na parede do furo Ø80 e virar incrustração —
que é exatamente o motivo pelo qual o projeto evita boca dentro do cabeçote. Resfrie **atrás** do degrau e
deixe os 14 mm do nariz do jeito que estão. Usinagem: meia hora de torno na matrizaria, sem EDM.

**D. Mastique chegando mais frio (a alavanca mais forte, e é de graça).** A vazão mássica é 15.000 × 1,25e-3
= **18,75 g/s** → cada **1 °C** a menos na massa que entra no copo leva embora **37,5 W**. Ou seja: para
compensar os 33 W do land bastaria a massa entrar **0,9 °C** mais fria. O preço é justo saber: sobe a pressão
(já alta) e a casca solda pior no R 0,75, que é onde a manta arrebenta.

**E. O que não fazer, com o motivo medido:**
- **furo de água dentro da copo: a conta nem abre.** Entre o furo do copo (Ø75,60 → raio 37,80) e o corpo
  (Ø93,00 → raio 46,50) há **8,70 mm** de aço. Um furo Ø4,00 com a parede mínima de **4,00 mm** exigiria o
  centro entre 37,80 + 6,00 = **43,80** e 46,50 − 6,00 = **40,50** mm de raio. Faixa vazia: **não existe
  posição** para furo de água na copo. (Na v30, com corpo Ø94,00, a janela existe e é de 1,2 mm — rodada 8ª.)
  E na altura do land seria pior ainda: da fenda até o Ø89,50 há **44,00 mm** de aço, longe da boca onde o
  calor nasce.
- **usar o furo M12 (Z 22,98) como entrada de ar/água:** ele dá no bolso onde o collete aperta, não na
  matriz; e é pelo mesmo furo que a matriz é expulsa (pushador EX-032).
- **espaçador para a copo protruir:** bloqueado pela geometria — faltam 1,50 mm de raio (item 2.3).

## 7. Como controlar, sem ver a boca

O termômetro de infravermelho **não alcança a boca** na copo: ela está enterrada 14,30 mm dentro de um furo.
O ponto alcançável mais quente e mais ligado a ela é a **face do nariz do cabeçote (Z 95,00, anel
Ø80→Ø130, 8.246,7 mm² de aço, a 14,30 mm da boca e ligada a ela pelo filme de 0,30 mm)**. Então:

1. Rode e meça `T_limiar` na **face do nariz** (não na matriz) no instante do primeiro dente de serra.
2. Uma vez só, pare uma tanda, espere esfriar o suficiente para abrir e meça a boca com termopar de ponteira;
   isso dá o offset boca↔face, que é constante enquanto a folga for a mesma.
3. Regra operacional: **segurar a face em `T_limiar − 10 °C`** com o pano ou com o colar, ligando e desligando.
4. Confirmação do mecanismo: tempo até o primeiro dente em 100 / 80 / 60 % da velocidade. Se escalar
   ~1× / 2,0× / 4,6× (o escalonamento 1/v³ da rodada 8ª), é aquecimento viscoso mandando, e o colar resolve.
5. Não congele demais: o lábio frio sobe a pressão e impede a casca de soldar no R 0,75 — alvo 10–25 °C
   abaixo da cabeça de aquecimento, não água gelada contínua.

## 8. O que isto tem a ver com o serrilhado (e o que não tem)

- **Tem:** borda serrilhada é a ponta sendo arrancada pelo centro. Uma casca fria e endurecida na saída segura
  a ponta (itens B e C). E o túnel de 14,30 mm da copo é onde a borda ainda está apoiada — resfriar atrás do
  degrau endurece essa região sem incrustrar o túnel.
- **Não tem:** resfriar não tira a tração da borda, só ganha tempo. O par continua sendo a refrigeração +
  **gotas nos extremos da fenda + arco do sorriso (flecha 1,50 mm) com chanfro 0,50×45°**, que é a rev. 31 /
  PRP-0007 e depende de ele dizer sim. Detalhe medido que joga a favor: **a copo não tem chanfro nenhum** na
  boca e o land dela é de 10,00 mm — mais agressivo que os 8,50 mm + chanfro 1,50×45 da v30.

## 9. Pendências desta rodada

*Atualizadas depois das fotos dele (§10): das quatro perguntas que eu tinha aberto, três foram respondidas pela
própria máquina — a banda está **livre** (item 1), **não existe água** no cabeçote (item 3, e a linha de água
passa a ser serviço novo, pequeno) e **não existe puxador** (o que eu tinha lido como puxador é a estação de
papel siliconado; a manta sai da matriz e entra na esteira). Sobram as de baixo — e a do `T_limiar` agora usa o
mostrador que já existe, não um termômetro comprado.*

1. **O que é o cano curto (Ø ~25 mm) apontando para baixo** na faixa sem tinta da frente do cabeçote? Se for
   respiro/dreno de camisa, a refrigeração já existe fundida na máquina e o trabalho é ligar uma mangueira.
2. **A que °C o mostrador de 0-150 fica em produção**, e em que faixa ele é mantido? Baixar a zona dianteira é
   meia resposta sem fabricar nada.
3. **O rolo de papel siliconado fica encostado em parte quente?** Afastá-lo é de graça e é a única coisa na linha
   que hoje toca a face da manta logo depois da boca.
4. Continuam valendo da 8ª: `T_limiar` com o teste das três velocidades (100/80/60 %), o giro de 180° da matriz
   antes de cortar, e a área real da amostra (para eu devolver a densidade medida).

---

## 10. O que as fotos da máquina respondem (repo `ity1300-wq/ACESS`, 25/09 14:08)

Ele mandou ver o repo `ACESS` — seis fotos e um vídeo da extrusora. Lidas uma a uma, com as sete mídias
baixadas e conferidas por sha256. **Procedência** (o arquivo fica no repo dele; a cópia local está em
`/home/user/uploads/ACESS_2026-09-25/`, que não é versionada):

| arquivo | bytes | sha256 (16 primeiros) |
|---|---|---|
| `WhatsApp Image 2026-09-25 at 14.08.52.jpeg` | 123.600 | `d79c7707ba13acae` |
| `WhatsApp Image 2026-09-25 at 14.08.53.jpeg` | 115.007 | `aa009a98e66acbc6` |
| `WhatsApp Image 2026-09-25 at 14.08.531.jpeg` | 125.383 | `7bfb59b74a92abba` |
| `WhatsApp Image 2026-09-25 at 14.08.54.jpeg` | 78.476 | `80d7641f777f9977` |
| `WhatsApp Image 2026-09-25 at 14.08.542.jpeg` | 106.625 | `09508b24f2b7b8e0` |
| `WhatsApp Image 2026-09-25 at 5.jpeg` | 67.229 | `e8116319be8f0181` |
| `WhatsApp Video 2026-09-25 at 14.08.52.mp4` | 7.731.854 | `ee4a17a249b9efb5` |

**Regra que eu mesmo me dei depois do erro do disco de corte:** foto responde *o que está onde*; foto não
responde *como o processo roda*. Tudo abaixo está escrito como "aparece na foto", e onde há dedução ela está
marcada como hipótese.

### 10.1 O que aparece, e o que isso fecha

1. **A boca enterrada está confirmada.** Na ponta do cabeçote aparece uma **face plana de aço sem tinta com um
   furo redondo**, e é por esse furo que a chapa passa. No vídeo (~22 s) há uma tira cinza atravessada ali, e
   **ele respondeu o que é: resquício de manta velha**, com a máquina parada — não é produto em processo e não
   vale como evidência. **Nenhuma boca de matriz aparece fora do cabeçote.** É exatamente o que a medição do CAD deu: face da matriz em Z 80,70 contra a face
   do nariz em Z 95,00, e um túnel Ø80,00 × 14,00 mm na frente.
2. **A faixa onde eu propus o colar d'água está livre.** A faixa de aço sem tinta na ponta (o corpo do
   cabeçote) está **sem abraçadeira de aquecimento e sem manta térmica**; o que há em volta é o garfo azul onde
   o papel é aplicado, à frente da matriz — **a distância não dá para medir nessas fotos**, então quem fabricar o
   colar mede na máquina. Então o colar pode ser abraçado ali, sem tirar nada de lugar. **Atenção a
   um item só:** aparece um **cano curto, de Ø ~25 mm, apontando para baixo** na borda dessa faixa (fotos
   14.08.53 e 14.08.531) — ver §10.3.
3. **Não precisa comprar termômetro de infravermelho.** Existe um **mostrador redondo de 0 a 150 °C (classe 1)**
   rosqueado no corpo azul, logo atrás do flange da matriz. Ele é a régua do teste da §7. Nas fotos ele marca
   ~25–30 °C, ou seja, **máquina fria**: nenhuma temperatura de processo pode ser lida nessas imagens.
4. **Não há água no cabeçote.** As mangueiras pretas que aparecem em cima dos corpos azuis entram por **cupom
   de aperto tipo prensa-cabo (conduíte)**, não por conexão de água; não há torneira, mangueira de água nem
   dreno no conjunto da matriz. Ou seja: se a opção C (colar d'água) for escolhida, a linha de água é trabalho
   novo — mas pequeno: 1 L/min, §5.
5. **O que eu li como puxador é a estação de papel — e a manta vai para a esteira.** Correção dada por ele nesta
   rodada: a primeira versão desta §10 dizia "existe puxador", e estava errado. O que aparece: um **par de rolos de aço nus** num garfo azul com fuso e mola, e uma **bobina de papel
   siliconado** guiada por roletes de nylon. **A manta sai da matriz e entra na esteira**, com o papel aplicado
   sobre ela. O que muda:
   * **não há puxador fechando ciclo de estiramento.** Então volta a valer o que estava na 7ª: o inchaço acontece
     livre depois da boca. O teto de 2,20 mm que usei para a flecha do sorriso — justificado por "sem puxador" —
     **continha**, e eu retiro a frase que escrevi na primeira versão desta seção dizendo que ele caía.
   * papel siliconado é **papel de liberação**, não tecido colado: ele cobre uma face da manta logo na saída. É
     um contato de resfriamento que já existe na linha, de graça. **Não li nas fotos a que temperatura papel e
     rolos chegam** e não vou deduzir isso de pixel — mas é regulável: ver a pergunta 4 da §10.3.
6. **O que controla a rosca é inversor.** O painel tem keypad WEG com "ajuste de velocidade", botão de esteira e
   alerta; o outro painel (caixa bege na plataforma) tem chave rotativa e um controlador digital — presumo ser
   o de temperatura. Isso importa para o teste da §7.4: baixar a velocidade em 80/60 % é só mexer no keypad, e
   o tempo até o dente pode ser cronometrado com o painel na mão.

### 10.2 Correção que as fotos fazem no meu plano

* **Item da §7 que muda:** eu tinha escrito "compre um IR e aponte na face do nariz". Não precisa: use o
  mostrador que já está no corpo, atrás do flange, e marque o valor no instante do primeiro dente. Se ele quiser
  saber a diferença entre o mostrador e a boca, aí sim um IR (ou termopar de contato) na face da matriz numa
  parada — e a calibração fica para sempre.
* **Item da §6 que ganha detalhe:** o colar (opção C) tem que **terminar antes do cano de Ø ~25** e **não pode
  estorvar o garfo onde o papel é aplicado**. Faixa útil provável: da face do flange azul para trás, na parte lisa do corpo.
* **Hipótese que eu levantei e ele derrubou (registrada para ninguém ressuscitar):** eu escrevi que a tira do
  vídeo encostava no fio do furo e que, se a manta corresse descentrada, a quina raspava no furo do nariz — o que
  daria ao serrilhado uma causa mecânica além da térmica. **Resposta dele: "ignore isso, é resquício de manta
  velha, é filme papel siliconado, a manta sai da matriz e entra na esteira".** A peça do vídeo não é produto em
  processo. A folga medida no CAD (2,50 mm por lado) continua sem contra-evidência, e o diagnóstico da 8ª
  permanece com as duas causas dele: tração na borda e saturação térmica. É a segunda vez nesta conversa que
  pixel de mídia da máquina vira afirmação de processo — a regra fica: **mídia da máquina parada não prova nada
  sobre o que acontece na saída.**

### 10.3 As perguntas que sobraram (agora são três, todas de resposta curta)

1. **O que é o cano curto que aponta para baixo na faixa sem tinta na frente do cabeçote?** Se for respiro ou
   dreno de camisa, **a refrigeração que eu propus já existe fundida na máquina** e o trabalho passa a ser ligar
   uma mangueira nela — que é outro patamar de custo. Se for alça de girar, ignora.
2. **A que °C o mostrador de 0-150 fica com a linha em produção**, e em que faixa ele é mantido hoje?
3. ~~O branco da bobina é tecido laminado ou filme de transporte?~~ **Respondido por ele: papel siliconado, e a
   manta sai da matriz e entra na esteira.**
4. Uma nova, e é a única pergunta de foto que ainda vale: **o rolo de papel siliconado fica encostado em alguma
   parte quente da máquina?** Se ficar, o papel chega quente e a face da manta que ele cobre não esfria nada na
   saída — e afastar o rolo é de graça.
