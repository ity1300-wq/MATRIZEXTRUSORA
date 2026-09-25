# Contato com a Matrizaria (Fernando Fugulin) — 23–24/09/2026

Fonte: `TRANSCRICAO-matrizaria-COM-IMAGENS.pdf` (13 pág., exportação de 25/09/2026 08:40, repositório
`ity1300-wq/ACESS`), que consolida a conversa de WhatsApp de 23–24/09/2026: 58 mensagens — 33 só texto, 11
imagens, 1 vídeo, 3 documentos, 7 áudios, 2 áudios encaminhados, 1 álbum. **Texto de chat é literal; os
áudios foram transcritos por máquina (faster-whisper, modelo small, pt-BR) e as imagens/vídeo descritos por
IA.** Nada dito em áudio vira especificação sem conferir o arquivo original — ver §7 do próprio PDF.

Este documento é registro de contato e leitura de consequências. **Nenhuma cota, geometria ou documento do
pacote publicado foi alterada por causa dele.**

---

## 1. O que ele recebeu e o que respondeu na hora

| hora | fato |
|---|---|
| 23/09 17:11 | "Gostaria de cotar uma matriz para extrusora [...] Vocês já fizeram uma pra gente a alguns anos atrás" |
| 23/09 17:12 | ele pede **desenho e material**; Engenharia manda os 3 arquivos `.STEP` do pacote v30 |
| 24/09 10:01 | "**Não consigo abrir arquivos BIN** / Teria como enviar em **DWG ou DXF**?" |
| 24/09 10:28 | "Está em fonte binária [...] Estou em uma fábrica. Um pouco mais tarde vou tentar no desktop" |
| 24/09 15:37–15:57 | Engenharia manda imagem do desenho 2D e 4 capturas do FreeCAD + vídeo da extrusão + foto da matriz em uso |

Os três nomes de arquivo que ele recebeu (`Cabecote_EX-030_com_Matriz_Jonatha_v30.step`,
`MATRIZ_V30_CANAL_DE_FLUXO.step`, `MATRIZ_V30_PECA_UNICA.step`) são exatamente os do `3D/` do pacote v30
publicado (97.198 / 85.455 / 151.083 bytes, sha256 `b42ee2e5…` / `77497bf8…` / `725c2f83…`, a tabela do
`EMAIL_FABRICA_MATRIZ_V30_CURTO_2026-09-23.md`). **A fábrica está olhando a revisão certa**, não uma cópia
antiga.

Conferido nesta rodada, e vale como resposta a ele: os nossos STEP **são texto ASCII** `ISO-10303-21`
(cabeçalho `ISO-10303-21;` + `HEADER;`, 0 bytes não-ASCII nos dois arquivos que ele abriu). "Binário" foi o
aplicativo do celular, não o arquivo. Ainda assim o pedido dele é legítimo e foi atendido: hoje existe desenho
DXF cotado (§4).

## 2. Diagnóstico dele — e ele contraria o nosso projeto

Dito em áudio (VOZ-01, 1 min 34 s, transcrição automática): foi ele quem fabricou a matriz hoje em uso. A
ondulação no centro e a falta de compactação nas extremidades, para ele, são **desequilíbrio de fluxo** — "a
gente precisa equilibrar essa questão do fluxo no centro para que chegue com pressão nas extremidades, chegando
com pressão, essa falha de compactação vai parar". E a frase que pesa: "**o projeto de vocês vai, não vai
resolver essa questão do fluxo**".

Motivo que ele dá (VOZ-02, 2 min 36 s): "assim que o perfil chega na face da matriz [...] ele sai, como ele não
encontra resistência [...] vai chegar com pressão da mesma forma [...] vai jogar no centro mais ainda, porque
vai concentrar força na massa no centro". E o aviso de escopo: "**a matriz nunca dá para garantir, porque não é
o molde**".

Comparativo que ele mesmo oferece (VOZ-04): "as matrizes de PVC são feitas parecidas com esse projeto de
vocês" — mas o PVC "sai estabilizado", e EPDM "expande, contrai", o que muda o jogo.

Custo: "não é costume de a gente fazer matrizes assim, uma pelo custo, tem um custo de usinagem maior".

Risco irreversível, e isso é o dado novo mais importante para o projeto: "se não der certo, não tem recurso,
não tem como daí pôr um freio **e por que está cônico**". Ou seja, aceitar o funil cônico da v30 fecha a porta
do ajuste corretivo depois de pronto.

## 3. As quatro alternativas que ele colocou na mesa

1. **Cavidade/rebaixo nas costas da matriz, nas extremidades** — "quanto mais espesso, mais concentra a
   pressão". Exemplo físico: a matriz velha dele (IMG-10) tem rebaixo nas costas com "as extremidades mais
   abertas, o centro mais fechado", o que dá "recurso de casa[...] abrir mais, fechar".
2. **Freio no centro** — "uma espécie [...] pode ser uma cantoneira no centro da peça para que equalize".
3. **Bolacha/disco no centro** — "é colocado um obstáculo, por exemplo, uma bolacha, um disco de 12 mm de
   espessura".
4. **Perfil "sorriso"** — "você traça um círculo no centro do perfil e faz o perfil contornando esse círculo,
   ou seja, todo o perímetro da peça está dentro desse círculo".
   E a recomendação prática dele, na ordem de custo: **aproveitar a matriz atual e pôr só um freio** — "é uma
   alternativa mais barata, talvez. Talvez não, com certeza [...] No primeiro momento é um freio, uma espécie
   de um freio que não é difícil de fazer. Vai dar resultado" — depois, se o resultado for positivo, "dá para
   fazer uma nova para já certificar o que deu certo".

Esclarecimento dele sobre a foto que ele mandou (VOZ-06/07, com correção do próprio): os rebaixos na face da
matriz **não são furos de fluxo nem de fixação pelo projeto** — "são rebaixos ali para o operador, ele coloca
uma ferramenta para virar a matriz no cabeçote". (E ele corrige: "melhor, são furos, são furos, mas não
passantes".) **Não confundir com furo de fixação**: a nossa interface continua collete EX-031 + degrau, sem
furo, sem flange — e isso não está em discussão por causa dessa foto.

## 3b. O que as fotos embutidas no PDF mostram (extraídas e abertas nesta rodada)

O PDF traz 13 imagens embutidas (`pypdf` as extraiu em resolução real, até 1500 × 1500 px; em
`/home/user/tmp/pdfimg/` na sandbox, descartável). Abri as cinco que importam para a decisão. **É leitura de
olho em fotografia com perspectiva: nenhum número abaixo é medição, e nenhum pode virar cota** - serve para
saber o que copiar quando a escolha for o caminho A.

* **IMG-11 (a matriz velha, lado das costas) - e aqui está o recurso 1 dele em forma física:** um disco de aço
  plano, **sem degrau, sem chanfro, sem land**, com um **rebaixo retangular de cantos arredondados fresado em
  volta da fenda**, do comprimento da própria fenda, raso e corrido (não são duas bolhas nas pontas: é uma
  janela larga e rasa atrás da fenda). A fenda em si é corte reto com as duas pontas arredondadas. É o
  "recurso de casa" de que ele falou: tirando material atrás, abre-se passagem onde falta pressão.
* **IMG-10 (a mesma matriz, face de saída):** disco com cara de corte a maçarico/plasma e superfície
  oxidada; a fenda passa no diâmetro e **os dois furos redondos estão nesta mesma face, acima da fenda,
  simétricos em torno do centro** - batem com a explicação dele de que servem para encaixar uma ferramenta e
  virar a matriz no cabeçote. **Não** são furo de fixação nem de fluxo, e o nosso desenho continua sem furo
  nenhum.
* **IMG-08 (a matriz montada no cabeçote):** o disco está **afundado dentro de um copo com assento cônico**,
  com uma câmara anelar em volta e a fenda bem abaixo da borda do cabeçote. É outro arranjo de interface - na
  nossa v30 a face de saída fica **rasante ao nariz** (protrusão 0,00 mm, collete EX-031 + degrau). Nada a
  mudar por causa da foto, mas fica registrado que a matriz que ele descreve não é montada como a nossa.
* **IMG-06 (a amostra com defeito):** a chapa de mástique cinza tem **denteado fino e periódico nas duas
  bordas longas** e, na face, umas **crestas transversais periódicas** - as "ondinhas". O denteado é igualzinho
  nas duas bordas, e **sai assim da matriz** (confirmado por ele, 25/09): é falta de material chegando às pontas,
  que o centro mais rápido rasga - não é um defeito de acabamento posterior.
* **Os dois quadros que o PDF guarda do vídeo de 9,7 s não são a linha dele, e eu errei ao lê-los.** Ampliados
  (recorte ampliado, gerado na sandbox e descartavel), eles mostram uma **lâmina/disco de metal encostado numa tira clara,
  de borda esfiapada** - material **branco**, enquanto a manta de mastique nas fotos ao lado é **cinza-chumbo**.
  Eu tinha concluído dali que o serrilhado vinha do corte de acabamento. **Conclusão retirada**, com a resposta
  dele na régua: *"que disco de corte? não tem disco de corte nenhum, a manta sai serrilhada da matriz"*.

Consequência, agora sem a hipótese do corte: **o serrilhado é da saída da matriz, e é a matriz que conserta.**
Rasgo de borda por **desequilíbrio** (falta vazão nas pontas, o centro arrasta e rasga) é exatamente o que freio
no centro / alívio nas pontas / "sorriso" fazem - os três recursos que ele ofereceu. Isto é diferente de
fratura de superfície por excesso de cisalhamento (*sharkskin*), essa sim pouco sensível ao canal: ver
`AVALIACAO_V30_X_FLUXO_2026-09-25.md` §5, que foi reescrito por causa desta correção. O que ainda vale dos
"20 minutos grátis" é **assistir ao vídeo completo no trecho em que a chapa sai da matriz**
(`midia_extraida/VID-20260924-WA0011.mp4`, no repo `ity1300-wq/ACESS`) e **medir com régua o espaçamento das
ondinhas do centro** - se o período bater com o passo da rosca, uma parte do defeito é pulsação da extrusora, e
freio nenhum resolve essa parte.

## 4. O que este repositório já tinha (e o que a conversa fez agora)

* O **DXF cotado da matriz** existia desde a rodada de 24/09 (`08_/MATRIZ_V30_DESENHO_COTADO.dxf`, A3, 1:1, mm,
  8 cotas, MATERIAL em ênfase) — foi exatamente o formato que ele pediu. Antes disso o repo não tinha nenhum
  `.dxf` de matriz.
* Nesta rodada o gerador ganhou o **gêmeo em AutoCAD 2000 (AC1015)**, `MATRIZ_V30_DESENHO_COTADO_AC1015.dxf`,
  escrito com `$DWGCODEPAGE = ANSI_1252` e acentos em byte simples (sem escape `\U+00D8`), porque CAD antigo e
  visualizador de oficina leem melhor AC1015. Os dois passam nas mesmas travas: `audit()` 0 erros, 8/8 cotas
  conferidas com o `pacote_usinagem.json`, 0 etiquetas sobrepostas, conteúdo dentro da moldura.
  Refazer tudo: `python3 04_Dados_SSOT_e_Scripts/gerar_desenho_cotado_dxf_v30.py` e a mesma linha com
  `DXF_SERIE=R2000`; para a v29, `PACOTE=08_Pacote_Usinagem_v29 DXF=MATRIZ_V29_DESENHO_COTADO`.
* **DWG não produzimos** (não há conversor aqui), e não precisa: o DXF abre direto no AutoCAD e ele salva como
  quiser — a geometria não muda no "salvar como".
* O `_PREVIEW.png` / `_PREVIEW.pdf` da mesma folha serve para ele ver no celular, onde o STEP não abriu.

## 5. Decisão que ficou em aberto (não é mais técnica de desenho, é de caminho)

| | A — freio na matriz atual (a sugestão dele) | B — fabricar a v30 com canal de fluxo |
|---|---|---|
| custo | o menor que existe | usinagem maior, como ele mesmo avisou |
| prazo | dias, sem peça nova | tempo de cotação + fabricação |
| risco | não resolve se a causa for outra; não é ourivesaria de precisão | ele declara que não garante; e **sem recurso depois**, porque o canal fica cônico |
| o que este repo faz | nada — é serviço na matriz que está em uso | nada — o pacote continua valendo como especificação |
| se der certo | "dá para fazer uma nova para já certificar o que deu certo" | vira referência de fluxo para a próxima revisão |

Meio-termo que a conversa sugere e que vale orçar com ele: fabricar a v30 **com um rebaixo de ajuste plano na
face traseira** (recurso 1 dele), deixando margem para abrir/fechar as extremidades sem refazer a matriz. Isso
muda a folha e o STEP (nova cota, nova revisão) — não fiz nada nesse sentido: só você decide, e aí a cota
nasce de projeto + medição, não de chute.

**Avaliação técnica completa desta seção, com os números do próprio repo (uniformidade 52,3% no land, núcleo ±5%,
τ 160,9 kPa contra o limiar de 140 kPa, +141% de ΔP do cabide de verdade), está em
`AVALIACAO_V30_X_FLUXO_2026-09-25.md` — incluindo onde o Fernando está certo, onde a comparação dele é injusta e
o que nenhum modelo deste repositório é capaz de responder.

## 6. Pendências, com dono

0. **Engenharia, antes de qualquer usinagem**: o **freio na matriz em uso**, que é o teste que decide se a
   causa é equilíbrio de fluxo (§5, caminho A). A pendência que estava aqui - "caçar o disco de corte da linha" -
   foi **retirada em 25/09** por erro meu: os quadros do vídeo embutidos no PDF não são da linha dele (§3b).
   O que sobra do teste grátis é ver o vídeo no trecho da saída da matriz e medir o período das ondinhas.
1. **Fernando → Engenharia**: foto/exemplo do rebaixo nas costas (combinado "amanhã", 25/09) - já vista aqui
   (§3b, IMG-11): é rebaixo retangular raso e corrido atrás da fenda, não duas cavidades nas pontas - e, se
   sobrar tempo, o desenho da opção "sorriso". Faltam as **cotas** do rebaixo (profundidade, largura, distância
   da fenda), que foto nenhuma dá: quem mede é ele, ou é com paquímetro na peça dele.
2. **Engenharia → Fernando**: responder qual caminho (A ou B); se B, mandar o **DXF** (AC1015 para CAD antigo,
   AC1024 se o CAD dele for recente) junto com a folha de material, e pedir a cotação da v30 que ele já se
   dispôs a fazer.
3. **NDA**: ele já tem os três STEP no celular e no desktop da fábrica. O acordo de sigilo continua pendente de
   assinatura formal antes de circular qualquer outra coisa — é a única pendência deste repo que depende só de
   papel, não de decisão técnica.
4. **Prazo/preço**: a referência de 20 dias úteis que está na cotação continua sem confirmação dele.
5. Comprimento da v30 em 95,00 −0,50/+0,00 e a escolha indução × nitretação seguem do mesmo jeito que estavam:
   decisão sua, declaração dele no relatório de fabricação.

## 7. Resposta pronta (WhatsApp)

> Fernando, obrigado pela franqueza — isso ajuda mais que um orçamento. Te mando o desenho em DXF (duas
> versões: uma para AutoCAD antigo e uma atual) e um PDF da mesma folha para você ver no celular, porque os
> .STEP são texto ASCII ISO-10303-21 — se abriu como binário foi o visualizador do telefone.
> Sobre o fluxo: entendi seu ponto do "não encontra resistência na face" e do risco de não ter recurso depois
> de cônico. Vamos seguir assim: (1) você nos manda a foto do rebaixo nas costas e, se der, o "sorriso", para
> tentarmos o freio na matriz que está em uso agora; (2) em paralelo, pode orçar a peça como mandamos, sem
> compromisso de que você garanta o resultado — a gente assume essa parte. Se o freio resolver na matriz
> atual, a peça nova já sai certificada no mesmo desenho, e aí conversamos sobre deixar um rebaixo de ajuste
> na face traseira para termos recurso de abrir/fechar extremidade sem refazer matriz.

## 8. Fidelidade

* "IPDM" na transcrição = **EPDM**; "foros" = **furos**; "encerrilhar" = **serrilhar**; "da esse programinha"
  é ruído de transcrição. A legenda da IA sobre a foto do desenho diz "JONATHA V2.0": **não existe v2.0 no
  nosso material** — o rótulo é `JONATHA v27.0 · rev. 30` (conferido nos geradores). É má leitura de "v27.0".
* Números ouvidos em áudio (ex.: "disco de 12 mm de espessura") **não** entraram em desenho, tabela ou JSON:
  são fala de conversa, não medição nem especificação.
* As cotas citadas aqui (Ø94/89/79, fenda 75,00 × 1,500) vêm do pacote publicado, não da transcrição.
* **As dez capturas que vieram com o PDF, abertas nesta rodada:** `image-1.png` e `image-2.png` são trecho do
  **nosso próprio texto** (o bullet "Proibido/sequência", com a marcação terminando em `rev. 29` — rascunho
  anterior a rev. 30 — e o bloco MATERIAL com `SAE J404 / EN 10083-2`, ≤ 220 HB, 30-36 HRC no corpo, 55-60 HRC
  nas arestas, 8-18 µm); `Screenshot_20260912-121529.Fotos.png` é uma vista em corte do **cabeçote**
  (`/home/user/cab_vista_esq.png`, "grade = 1,000 unidade do DXF · k = 21,26 mm/un", chanf. 10×45°,
  Ø130 / Ø80 / Ø90 +0,1); `Screenshot_20260912-132414.Visualizador 3D e CAD.png` é o
  `Cabecote_EX-030_desenha…` aberto no visualizador do telefone, com caixa **219,9 × 220,0 × 95,0 mm** e 732
  triângulos. As outras seis são do mesmo lote de 11–12/09 (três Chrome, três Visualizador) e não foram
  abertas uma a uma. **Nada nelas acrescenta ou contraria cota da matriz**, e nenhuma é a foto da matriz velha
  com o rebaixo nas costas: IMG-10/IMG-11 estão no repo `ity1300-wq/ACESS` (`midia_extraida/`), e é essa foto
  que falta para reproduzirmos o recurso 1 com medida - porque a foto reduzida do PDF mostra o rebaixo, não
  o dimensiona (§3b). As 13 imagens embutidas no próprio PDF foram extraídas com `pypdf` e as cinco relevantes,
  vistas: IMG-06, IMG-08, IMG-10, IMG-11 e os dois quadros do vídeo. O que elas mostram está no §3b; o que elas
  **não** mostram é qualquer cota legível, e nada delas entrou em JSON, tabela ou desenho.
