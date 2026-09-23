# E-mail objetivo para a fábrica — matriz v30 (2026-09-23)

Pronto para copiar e colar. Os números abaixo são transcritos do `08_Pacote_Usinagem_v30/`
(medidos no STEP `3D/MATRIZ_V30_PECA_UNICA.step`, sha256 `b42ee2e50a10d43d…`), não de memória.
O sha256 do anexo citado no corpo é o do zip publicado hoje — se o pacote for re-gerado, conferir
o valor em `08_Pacote_Usinagem_v30/07_EMAIL_DE_PRIMEIRO_CONTATO.md` antes de enviar.

---

## O e-mail

**Assunto:** Pedido de fabricação — 1 matriz de extrusão JONATHA v27.0 (rev. 30) · aço 1045 · fenda 1,500 mm a fio EDM pós-T.T.

**Anexo:** `PACOTE_MATRIZ_V30_PARA_ENVIO.zip` (588.274 bytes)

Boa tarde,

Seguimos do orçamento para o pedido. Preciso de **1 (uma) matriz de extrusão**, peça única, sem lote,
para o cabeçote EX-030. Geometria, tolerâncias e sequência estão no pacote anexo; o que segue é o resumo
que precisa estar bater com a proposta.

**A peça.** Ø94,00 × 95,00 mm, 3,442 kg, em **aço 1045** (SAE J404 / EN 10083-2, barra forjada, fibra no
eixo, normalizada ≤ 220 HB).

| cota | valor | tolerância |
|---|---:|---|
| 1º estágio (datum A) | Ø94,00, Z 0 → 69,90 | ±0,5 · micrômetro em 3 posições a 120° |
| 2º estágio | Ø89,00, Z 69,90 → 80,70 | ±0,5 |
| 3º estágio / pescoço | Ø79,00, Z 80,70 → 95,00 | ±0,5 |
| comprimento total | 95,00 | ±0,5 (ver pergunta 1) |
| posição dos dois degraus | 69,90 / 80,70 | ±0,05 · CMM |
| coaxialidade dos estágios 2 e 3 em relação a A | — | Ø0,02 |
| face de saída | — | planeza 0,01 e ⟂ 0,01 em A |
| **land paralelo** | 8,500 (Z 85,00 → 93,50) | ±0,05 |
| **fenda no land** | largura 75,000 × **abertura 1,500** | largura ±0,05 · **abertura +0,010 / −0,000** |
| raio nas pontas da fenda | R 0,75 | +0,05 / −0,00 · aresta viva, sem raio extra |
| área da seção no land | 112,0171 mm² | **±0,5 % — rejeição fora disso** |
| chanfro de saída | 1,50 × 45° (Z 93,50 → 95,00), boca 78,00 × 4,50 | ±0,20 / ângulo ±0,5° |
| boca de entrada do canal | Ø75,60 | +0,05 / −0,00 — **não alargar** |
| raio no fundo do funil | R 3,0 ±0,5 | sem aresta viva |
| rugosidade | Ra ≤ 0,4 µm no canal e land (polir **na direção da extrusão**); ≤ 0,8 µm nos Ø de envelope | |
| rebarba / quebra de aresta | máx. 0,1 × 45°, inclusive na boca de saída | |

**As quatro condições que não são negociáveis.**

1. **Sem furo de fixação, sem flange, sem rosca, sem pino.** A matriz é segurada pelo collete EX-031 e pelo
   degrau do furo do cabeçote. Qualquer furo "para ajudar a segurar" é rejeição — ele entra na zona de aperto
   do degrau. Elemento de aperto só em estoque, fora do envelope final e antes do tratamento térmico.
2. **Peça única, 1 sólido, sem linha de partição.** Não usinar em duas metades e colar: a costura no plano
   Y = 0 é exatamente o defeito que estamos eliminando.
3. **Canal aberto por fio EDM de um lado só**, com o arame entrando pela boca de Ø75,60; sombra de usinagem
   medida no modelo: 0,00 % (não há face sem acesso reto).
4. **Sequência: T.T. do corpo → retífica do land → fio EDM do canal → remoção da camada REC (≥ 0,02 mm) →
   indução/nitretação → medição final.** A fenda não pode existir antes do tratamento térmico do corpo
   (risco de trinca: 1,500 mm atravessando 95 mm de 1045 temperado), e a camada REC do EDM tem de sair toda.

**Tratamento superficial na fenda (pedido nosso).** Corpo revenido **30-36 HRC**; arestas do land
**55-60 HRC em camada de 0,6-1,0 mm por indução**, **ou** nitretação a plasma 520 °C (600-700 HV0,2, camada
branca 8-18 µm) se vocês preferirem tratar a fenda inteira — escolha da fábrica, declarada no relatório.
Atenção à cota: 8-18 µm por face come 0,016-0,036 mm de uma abertura que tolera +0,010/−0,000, e a indução
move 0,005-0,020 mm na zona tratada. Portanto **medir a abertura da fenda antes e depois do tratamento e
gravar os dois números** no relatório dimensional; se a abertura cair de 1,500, o retrabalho é passar o fio
de novo na região e re-medir — não é "aceitar como está". Sem revestimento PVD/DLC: não foi pedido.

**Documentos que acompanham a peça.** Certificado EN 10204 3.1 do calor (composição, granulometria,
inclusões, resultado de têmpera/revenimento); relatório dimensional com os números medidos de todas as linhas
da tabela, inclusive as três leituras da fenda (entrada, meio, saída) antes e depois do tratamento; registro
de microdureza em seção (corpo de prova do mesmo lote); marcação a laser na **face traseira**, fora do furo e
fora da face de assentamento: `JONATHA v27.0 · EX-031 · 1045 · rev. 30 (2026-09-22) · lote · nº de série · data`.

**Três respostas antes de eu emitir a ordem de compra.**

1. **Comprimento.** A cota está liberada como 95,00 ±0,5, mas com +0,5 a face de saída passaria 0,5 mm para
   fora do nariz do cabeçote. Nossa intenção é fechar em **95,00 −0,50 / +0,00**. Vocês concordam com o
   aperto ou precisam de mais folga para o comprimento faceado à máquina?
2. **Tratamento.** Indução nas arestas ou nitretação a plasma na fenda inteira — qual caminho vocês dominam
   melhor com controle de camada em peça de 3,4 kg com fenda passante, e é interno ou terceirizado?
3. **Prazo e preço** para 1 matriz com o dossiê completo (usinar + T.T. + fio EDM + tratamento + medição).
   Nossa referência é 20 dias úteis. Se o tratamento terceirizado mandar no prazo, digam o número real.

O pacote anexo tem: STEP AP214 da peça (o modelo é a definição; o desenho cotado é a régua de aceitação),
STEP do sólido do canal para o fio EDM, montagem no cabeçote EX-030, prancha 2D toleranciada em PDF, ficha
de fábrica, material e tratamento, sequência de usinagem, plano de inspeção, RFQ e `CHECKSUMS_SHA256.txt`
com os 13 arquivos. Conferência do anexo: `sha256sum` deve dar
**`0738c4683c80efdb6f3db4903c1d7febe8126ac147d9025c8cfdfbc2dd6fac6e`** em 588.274 bytes. Se o hash não
bater, não abram — peçam reenvio.

É uma peça só, sem lote; o projeto está em patenteamento, então precisamos de NDA assinado antes da difusão
interna do desenho.

Att,
[nome] · [telefone] · [empresa]

---

## O que mandar — e o que não mandar

**Mande exatamente isto (duas peças, nada mais):**

1. O zip `08_Pacote_Usinagem_v30/PACOTE_MATRIZ_V30_PARA_ENVIO.zip` (**588.274 B**, sha256
   `0738c4683c80efdb6f3db4903c1d7febe8126ac147d9025c8cfdfbc2dd6fac6e`) — é o anexo canônico, dentro dele já
   estão os 13 arquivos + `CHECKSUMS_SHA256.txt`.
2. Se o servidor de e-mail deles estrangular anexo ou se a primeira conversa for por WhatsApp/telefone,
   mande **só** a prancha para o orçamento sair: `08_Pacote_Usinagem_v30/PRANCHA_2D_TOLERANCIADA.pdf`
   (**49.582 B**, sha256 `4b0e6ef12bc2058293186dd6032593389c0c29b710158a1769695df83a458b60`). O zip vai depois,
   com a ordem de compra.

**Antes de apertar em enviar**, nesta ordem: (a) `sha256sum` no arquivo que você anexou e comparar com o
número acima; (b) confirmar que você está mandando o pacote **v30**, não o v29 (o v29 é a variante de
109,00 mm que ficou no disco para comparação — ela **não** vai para a fábrica); (c) NDA enviado antes do
desenho, se eles ainda não assinaram.

**Não mande:** o modelo paramétrico/scripts de `04_Dados_SSOT_e_Scripts/`, as planilhas e bandas de
simulação, os relatórios internos de auditoria (`03_`), o STEP do cabeçote EX-030 completo com o furação do
flange (a interface que a peça precisa respeitar já está descrita na prancha e na ficha), o STEP da Gedeon ou
de qualquer matriz histórica, e o DXF original do cabeçote. Nada disso é preciso para orçar ou usinar esta
peça, e o que não circula não precisa de NDA.

**Duas coisas que continuam suas, não da fábrica:** a resposta à pergunta 1 (deixar 95,00 ±0,5 ou fechar em
−0,50/+0,00) e à pergunta 2 (indução × nitretação) — a fábrica pode opinar, mas a decisão vai para o SSOT
aqui dentro antes de a gente responder "pode usinar". E se eles pedirem alteração de qualquer cota do produto
(fenda, land, chanfro, boca de entrada), a resposta é "me enviem por escrito o motivo" — é isso que o portão
do repo compara, linha por linha, contra o STEP.
