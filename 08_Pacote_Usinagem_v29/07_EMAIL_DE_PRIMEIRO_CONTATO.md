# E-mail de primeiro contato ao fornecedor — MATRIZ JONATHA v27.0 (peça única) · 1 matriz

Este arquivo **não** vai no `PACOTE_MATRIZ_V29_PARA_ENVIO.zip`: é a sua carta de capa. O zip é o anexo.
Os campos entre `{ }` são os únicos que você precisa preencher.

---

## Versão principal (e-mail)

**Assunto:** Cotação — 1 matriz de extrusão em 1.2344 temperado · fenda 1,50 mm aberta a fio EDM

> Bom dia, {nome}.
>
> A {empresa} precisa de **1 matriz** de extrusão plana para EPDM, geometria em anexo (STEP + desenho +
> tolerâncias). Resumo do que está no pacote, para o senhor orçar sem abrir tudo:
>
> | | |
> |---|---|
> | peça | **MATRIZ JONATHA v27.0 — peça única**: sólido único (sem bipartição, sem pino, **sem furo ou flange de fixação**), Ø93,00 × 109,00 mm, 3,68 kg |
> | material | **1.2344 (X37CrMoV5-1 / H13)**, barra forjada, fibra no eixo, ESR se disponível |
> | tratamento | alívio de tensões → têmpera a vácuo + 2 revénios → **50-52 HRC**; retífica e fio EDM **depois** do último revenido |
> | cota crítica | fenda **75,00 ±0,05 × 1,500 +0,010/−0,000 mm**, raios R 0,75 nas bordas, land 8,50 ±0,05, chanfro de saída 1,50 × 45° |
> | assentamento | Ø89,50 e Ø79,50 em **0/−0,02**, coaxialidade Ø0,02 em A (Ø93,00), planeza e perpendicularidade 0,01 na face de saída |
> | acabamento | canal e land polidos **Ra ≤ 0,4 µm**, camada REC do EDM removida; **sem revestimento** (sem nitretação nem PVD) |
> | documentos | certificado EN 10204 3.1, relatório de tratamento térmico e dureza, dimensional de primeiro artigo, rugosidade por réplica |
>
> É **uma peça só**, sem lote: ela vai para o teste de linha e, a partir dela, definimos a série. Por isso o que
> pesa mais que preço, aqui, é rastreabilidade da medição.
>
> **Quatro respostas objetivas, duas linhas cada, bastam:**
>
> 1. Fazem o **corte a fio da fenda de 75,00 × 1,50 mm** segurando ±0,01 na abertura, com polimento do canal
>    depois da têmpera? Qual é a capacidade real de vocês nessa tolerância?
> 2. Tratamento térmico é **interno ou terceirizado**? Como compensam a retração (prevemos 0,4–0,6 ‰ linear) e em
>    que momento re-medem a fenda?
> 3. **Prazo** (pedimos 20 dias úteis) e **preço** da peça, com o dossiê do item acima?
> 4. Trabalham com **acordo de sigilo**? O projeto é nosso e a peça não leva marca.
>
> Se a resposta for negativa nos itens 1 ou 2, diga já — preferimos não insistir, e agradecemos a indicação de
> quem faz.
>
> Anexos: `PACOTE_MATRIZ_V29_PARA_ENVIO.zip` (STEP da peça, sólido do canal, montagem no cabeçote, prancha 2D
> cotada, material e tratamento, sequência de usinagem, tabela de tolerâncias e plano de inspeção, RFQ) e, para
> leitura rápida, `PRANCHA_2D_TOLERANCIADA.pdf`. O zip traz `CHECKSUMS_SHA256.txt` para o senhor conferir o que
> baixou.
>
> Fico à disposição para 15 minutos sobre a sequência — temos preferência em fechar o fio EDM e o chanfro na
> **mesma fixação**, e há um detalhe que evita retrabalho: nenhuma cota de 0,02 mm pode ser retocada depois do
> tratamento térmico sem re-medir a fenda.
>
> Atenciosamente,
> {nome} · {empresa} · {telefone} · {e-mail}

**Anexo e integridade:** `PACOTE_MATRIZ_V29_PARA_ENVIO.zip`, 608.550 bytes, sha256 `a0d104bb29c83a7df9fda0a210f187f4d274fab0bf30131e27be0c460fa54774`. Dentro do zip vai `CHECKSUMS_SHA256.txt` cobrindo os outros 13 arquivos: rode `sha256sum -c CHECKSUMS_SHA256.txt` na pasta extraída e confira os 13 OK antes de usinar qualquer coisa.

---

## Versão de 4 linhas (WhatsApp / primeiro toque antes do e-mail)

> {Nome}, boa tarde. Cotação para a fábrica: **1 matriz de extrusão em 1.2344 temperado (50-52 HRC)**, peça única
> Ø93 × 109 mm, com **fenda 75,00 × 1,500 (+0,01/−0,00) aberta a fio EDM depois da têmpera**, canal polido
> Ra 0,4 e **sem revestimento**. Precisamos de CMM de primeiro artigo e certificado 3.1. Vocês seguram ±0,01 na
> fenda pós-tempera? Se sim, mando o pacote (STEP + desenho + tolerâncias) e peço prazo e preço.

---

## Assunto curto, para o caso de o e-mail anterior morrer na caixa

**Assunto:** Re: cotação 1 matriz 1.2344 — fenda 1,50 ±0,01 pós-tempera, prazo 20 dias

---

## O que NÃO mandar no primeiro contato

* **Não** anexe os arquivos do projeto (relatórios, cabeçote EX-030, histórico da v27.0 bipartida e da v28.1,
  nada de `02_/`). O fornecedor precisa do zip do pacote; a interface com o cabeçote está dentro dele, na
  montagem, e basta.
* **Não** dispare o STEP para 20 fornecedores pedindo "tabela de preços": a fenda é o segredo industrial desta
  matriz. Mande o zip para 3, no máximo, e só para os que responderem **sim** às perguntas 1 e 2.
* **Não** combine prazo antes de fechar quem faz o tratamento térmico: a peça passa por fora e é a etapa que
  estoura calendário.
* **Não** aceite "a gente ajusta a fenda depois da têmpera no fio, sem problema": o ajuste muda o volume do canal
  (213.945,1 mm³) e com ele a gramatura do produto. O critério de rejeição está na tabela de tolerâncias
  (área da seção do canal no land = 112,0171 mm² ±0,5 %) exatamente para cortar esse caminho.
* **Não** deixe o fornecedor transformar "1 peça" em "1 piloto + série" no orçamento: se ele cotar lote,
  responda que é **1 matriz para o teste de linha** e que a reserva só é pedida depois, se a primeira for
  aprovada. O preço unitário de 1 peça em peça única costuma vir inflado pelo setup — peça para ele separar
  setup de hora de máquina, porque isso é o que você renegocia na segunda.

## Se ele pedir "informação para usinar" que não está no pacote

A resposta padrão é: tudo que manda no resultado está em `04_TOLERANCIAS_E_INSPECAO.md` e nas 12 notas da prancha.
Se a dúvida for de capacidade (fio, polimento interno, medição da fenda de 1,50 mm), é conversa — marque 15
minutos e mande antes o `03_SEQUENCIA_DE_USINAGEM.md`, que já propõe a ordem das operações e deixa espaço para a
fábrica sugerir a dela.
