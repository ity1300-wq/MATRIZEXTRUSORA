# Reavaliação com os olhos no serrilhado — 25/09/2026

Ele pediu isso: *"acho que você está viajando e prestando atenção em coisas que não deveria prestar…
reavalie tudo, calmamente, devagar, haja como uma outra persona… PRECISAMOS RESOLVER O SERRILHADO DA
MANTA, OBJETIVO PRIMORDIAL"*. Este documento é essa reavaliação. Escrito como quem chegou agora e só
aceita o que está medido em arquivo do repo. Nada de cota foi alterada; nenhuma revisão foi aberta.

**Veredito em uma linha:** o serrilhado é falta de material chegando nas pontas da fenda, e as três
matrizes que eu medi hoje **não têm nada que alimente a fenda ao longo dos 75,00 mm** — nem a copo, nem a
v30, e é por isso que refrigeração, espessura e ajuste de bancada só mascaram.

---

## 1. Onde eu estive olhando para o lado

* **Rounds 8ª e 9ª (refrigeração).** Eu gastei duas rodadas em como esfriar a matriz e o cabeçote, em foto
  de máquina parada, em manômetro, em alça de ferro. O que sobra disso: **refrigeração muda a hora em que a
  borda rasga, não a quantidade de material que chega na ponta.** Ela é paliativo e está estacionada no
  relatório `RESFRIAMENTO_MATRIZ_COPO_2026-09-25.md` — não jogada fora, mas não é o alvo.
* **Espessura como fim.** A igualização de espessura apareceu em vários textos como objetivo. Ela é
  *sintoma*. O fim é o denteado nas duas bordas.
* **A v30 como resposta.** Eu defendi a v30 por ela ser uma matriz limpa (peça única, boca rasa, sem junta).
  Limpa não é equilibrada. Ver §4.

## 2. O que está provado, medido hoje no STEP (rodo em `04_/medir_alivio_pontas.py`)

Método: varredura de ponto dentro do sólido, sem booleiana, sem malha, sem CFD. Para cada estação da fenda
(centro, ±18,75, ±30,00, ±36,60) e cada profundidade atrás da boca, o script mede a **abertura do canal**.

| o que foi medido | Copo (está na máquina) | Jonatha v30 (pacote publicado) | Gedeon CERTA (a que ele diz que dá certo) |
|---|---|---|---|
| abertura da fenda na boca, centro → ponta | 1,52 em todas | 1,52 em todas | 1,50 em todas |
| alívio/rebaixo nas pontas? | **não tem** | **não tem** | **não tem** |
| canal que alimenta a ponta, a 11 mm atrás da boca | **18,90 mm** | **1,52 mm** (a boca, sem abrir nada) | 1,52 mm (é a própria fenda) |
| comprimento do trecho paralelo (land) | **10,00 mm** | **8,50 mm** | **88,00 mm** (fenda paralela de Z 20,98 a Z 109,00; o corte começa em Z 0,17, mas até Z 20,98 ele está dentro do cone de entrada Ø75,60) |
| como a fenda é alimentada | de um furo Ø75,60 que tem de **espalhar de lado** | de um funil cônico que **fecha** nas pontas | **pelo comprimento inteiro de uma vez** (a boca da fenda fica na face de trás, dentro do bolso do cabeçote) |

As duas primeiras linhas já derrubam uma coisa que foi dita aqui com segurança demais: **não é o "recurso"
dele (alívio nas costas) que faz a Gedeon funcionar — ela não tem alívio nenhum.** Ela tem outra coisa.

## 3. A diferença que aparece quando se mede, e não quando se argumenta

A fenda de 75,00 mm tem de receber material. Duas maneiras de fazer isso:

1. **Alimentar por uma cavidade** (a copo, e a v30 com o funil): o material chega pelo eixo e tem de correr
   para os lados, 37,50 mm, por um canal que na v30 tem **1,52 mm de altura** na ponta. Cada milímetro dessa
   altura conta **³√** — com n = 0,32 do mastique, uma diferença pequena de caminho vira um déficit grande de
   material na borda. É o que a dele mede: **58–60 % de material na ponta contra 100 % no centro.**
2. **Alimentar ao longo do comprimento** (a Gedeon): a fenda é um corte que atravessa a peça, então a boca de
   entrada da fenda está exposta ao material **nos 75,00 mm de uma vez**. Não existe caminho lateral. Não
   existe ponta com menos pressão. **A fenda não tem para onde ser desequilibrada.**

E o land de 88,00 mm da Gedeon é o preço dessa escolha (e o reforço dela): com o atrito do land valendo
2,187 bar/mm, a conta do próprio repo dá **193 bar** para passar pelos mesmos 15.000 mm³/s. Ela compra
uniformidade com pressão — e é por isso que a boca dela é um corte reto de 1,5 atravessando a peça inteira: o
material entra na fenda **ao longo dos 75,00 mm de uma vez, num plano só**, no fundo do cone.

O script fecha a conta em uma linha: o desequilíbrio é uma resistência extra fixa (δR) que a entrada deixa
nas pontas. Alongar o land não muda δR; muda a **fração** que δR representa no total. Calibrando δR no que
ele mediu na copo (15,8 % com 10,00 mm de land):

| matriz | land | deficit que a mesma δR produz | pressão só no land |
|---|---:|---:|---:|
| Copo (hoje) | 10,00 mm | **14,3 %** | 22 bar |
| Jonatha v30 | 8,50 mm | **12,3 %** (e a δR dela é maior que a da copo, porque o funil fecha nas pontas) | 19 bar |
| land 31,60 mm | 31,60 mm | 4,5 % | 69 bar |
| land 52,70 mm | 52,70 mm | 2,7 % | 115 bar |
| Gedeon CERTA | 88,00 mm | **1,7 %** | 193 bar |

**Leia a tabela na vertical, não na horizontal.** Não existe linha "land curto e manta lisa" alimentando por
cavidade. As opções são duas, e só essas: **alimentar a fenda ao longo do comprimento** (sem pagar pressão) ou
**comprar land** (pagando de 3 a 9× a pressão de hoje).

## 4. O que isso diz da v30, sem defesa e sem ataque

* Ela tem razão quanto ao que melhora: peça única (sem junta, sem rebarba de junta), boca rasa (não enterrada
  14,30 mm como a copo), lábio mais robusto.
* Ela está errada no que ele pediu. O land foi de 10,00 (copo) para **8,50 mm**, e o funil cônico deixa a
  ponta com **1,52 mm** de canal — ou seja, na direção do serrilhado ela anda para trás, não para frente.
  Isso é medida, não opinião, e é a versão numérica do "o projeto de vocês não vai resolver a questão do
  fluxo" que ele disse em áudio. Eu li aquilo como opinião de matrizaria; é previsão correta.
* A decisão sobre a v30 continua valendo para usinagem de *outra* coisa (a peça única como forma); ela não é
  resposta para o serrilhado e não deve ser defendida como se fosse.

## 5. O que fazer, na ordem, com o custo de cada passo

1. **Medir o perfil da manta da Gedeon nos mesmos 5 pontos** (10 minutos, zero usinagem, zero risco). Se a
   Gedeon der ~1,50 nos cinco pontos com um land de 88,00 mm alimentando pelo comprimento, o princípio está
   provado **na linha dele**, com a extrusora dele. É o único experimento que decide entre as duas opções da
   tabela sem eu precisar convencer ninguém de nada.
2. **Girar a matriz 180° e remedir** (grátis, já estava pendente): se a assimetria +25 % trocar de lado, é
   assento/montagem; se ficar no mesmo lado da máquina, é a máquina, e nenhuma matriz resolve isso.
3. **Medir com régua o passo das ondinhas do centro** (grátis, 5 minutos) e comparar com o passo da rosca:
   separa pulsação da rosca de defeito de matriz. Sem isso, tudo que a matrizaria fizer vai ser avaliado com o
   ruído da extrusora dentro da amostra.
4. **Rev. 31 — o desenho muda de alvo.** Esquecer "gotas + sorriso + chanfro" como *a* solução; isso é ajuste
   fino de uma matriz que já nasce desequilibrada. O alvo passa a ser um destes dois, e só um:
   * **A. Fenda alimentada ao longo do comprimento** — a boca de entrada da fenda aberta para o bolso, como na
     Gedeon (corte atravessado: a fenda aberta até a face de trás, onde o bolso do cabeçote já enche de
     material), ou um rasgo raso correndo atrás do land nos 75,00 mm, mais alto nas pontas.
     Não paga pressão; paga usinagem (EDM atravessado, e a matrizaria dele já fez isso uma vez).
   * **B. Land comprido** — 30 a 35 mm de land paralelo em vez de 8,50, pagando ~69 bar só no land (a Gedeon
     paga 193 com 88,00 mm, e é a prova de que a extrusora dele aguenta mais do que hoje). Cabe no
     corpo de 80,70? Sim: sobram 45 mm para a cavidade. Mas **depende de quanto de pressão essa extrusora
     entrega nessa rosca** — número que eu não tenho e não vou inventar.
   O chanfro 1,50 → 0,50 que já estava na proposta continua sendo um passo *na direção certa* (land 8,50 →
   9,50, +4,8 % de ΔP), mas ele é de 12 % para 11 % — é cosmético diante do problema.
5. **Só depois disso** volta a conversa de refrigeração (§8 do relatório estacionado), porque ela passa a ser
   *set-point* de uma matriz que finally entrega material igual nas pontas, e não band-aid de uma que não
   entrega.

## 6. O que eu preciso dele, e são três números (nenhum é difícil)

1. **Perfil da manta da Gedeon, 5 pontos** (1,5 / 18,75 / centro / 18,75 / 1,5). É a peça inteira do raciocínio.
2. **Quanto de pressão a extrusora dele entrega**, manômetro da adjunta em produção, em bar. Sem isso, a
   opção B não pode nem ser cogitada — e eu não volto a propor nada que dependa dela.
3. O que ficou sem resposta das rodadas anteriores: **a área real da amostra que ele pesou** (para eu devolver
   a densidade medida do mastique dele) e **o texto do item 2** que veio vazio duas vezes.

---

*Registro de procedimento, para ele poder conferir: nenhuma linha deste arquivo usa número de memória. As
aberturas, os comprimentos de land e a fenda atravessada da Gedeon saíram de `04_Dados_SSOT_e_Scripts/medir_alivio_pontas.py`
rodado hoje contra os STEP do repo; o gradiente 2,187 bar/mm, o n = 0,32 e a vazão 15.000 mm³/s são do
método 1D do projeto (PRP-0002, SSOT). O perfil de espessura (1,5 / 2,5 / 2,5 / 2,0 / 1,5 e a 1ª medição) é
medida dele na linha, com o erro que ele mesmo declarou.*
