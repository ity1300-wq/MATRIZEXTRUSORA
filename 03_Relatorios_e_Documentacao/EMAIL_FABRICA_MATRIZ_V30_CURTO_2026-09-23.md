# E-mail curto para a fábrica — matriz v30, anexando só os STEP (2026-09-23)

Você vai mandar a pasta `08_Pacote_Usinagem_v30/3D/` (3 arquivos). Sem o desenho, as cotas têm de ir no corpo
do e-mail — é o que está abaixo. Cole o bloco do e-mail inteiro, sem cortar as linhas de `·`: cada uma delas é
uma cota que a fábrica precisa ter por escrito para poder ser cobrada depois.

Antes de enviar, confira os três arquivos (tamanho e sha256). Se algum bater diferente, você está mandando
outra revisão:

| arquivo | bytes | sha256 (SHA-256) |
|---|---:|---|
| `MATRIZ_V30_PECA_UNICA.step` | 97.198 | `b42ee2e50a10d43db4b91a22f62e3e4e0aacfdcd8e3ebbacf3eb6cf4a39b818e` |
| `MATRIZ_V30_CANAL_DE_FLUXO.step` | 85.455 | `77497bf86c989b23d8eb121c5318904c7ca506a3b580c89ecde134f0873f2154` |
| `Cabecote_EX-030_com_Matriz_Jonatha_v30.step` | 151.083 | `725c2f83f26cc6e85331182e8e86d60d5fe9cd172405271228f0b03fbd7128a5` |

Comando: `cd 08_Pacote_Usinagem_v30/3D && sha256sum *`.

---

## O e-mail

**Assunto:** 1 matriz JONATHA v27.0 (rev. 30) · aço 1045 · fenda 1,500 +0,010/−0,000 aberta a fio EDM depois do T.T.

Boa tarde,

Pedido de fabricação de **1 (uma) matriz de extrusão**, peça única, sem lote, para o cabeçote EX-030. Os três
STEP anexos definem a geometria: `MATRIZ_V30_PECA_UNICA.step` é a peça, `MATRIZ_V30_CANAL_DE_FLUXO.step` é o
sólido do canal (para o fio EDM) e `Cabecote_EX-030_com_Matriz_Jonatha_v30.step` mostra como a peça senta no
cabeçote. O que tem de sair:

· **Ø94,00 ±0,5** (datum A, Z 0 → 69,90) · **Ø89,00 ±0,5** (69,90 → 80,70) · **Ø79,00 ±0,5** (80,70 → 95,00) ·
comprimento **95,00 ±0,5** · degraus com ±0,05 · coaxialidade dos três estágios **Ø0,02** · face de saída
planeza 0,01 e perpendicularidade 0,01 em A.
· **land 8,50 ±0,05** (Z 85,00 → 93,50) · fenda **75,00 × 1,500 +0,010/−0,000** com **R 0,75** nas pontas,
aresta viva · área da seção no land **112,0171 mm² ±0,5 %** (fora disso é rejeição) · chanfro 1,50 × 45°
(boca 78,00 × 4,50) · boca de entrada **Ø75,60 +0,05/−0,00, não alargar** · Ra ≤ 0,4 µm no canal e no land,
polido na direção da extrusão · Ra ≤ 0,8 µm nos Ø de envelope · rebarba ≤ 0,1 × 45°.
· **Aço 1045** (SAE J404 / EN 10083-2), barra forjada, fibra no eixo, normalizada ≤ 220 HB; corpo revenido
30-36 HRC; **arestas do land 55-60 HRC em camada 0,6-1,0 mm por indução**, ou nitretação a plasma 600-700 HV0,2
— escolha de vocês, declarada no relatório; sem PVD/DLC.
· **Sequência:** T.T. do corpo → retífica do land → **fio EDM do canal** (arame pela boca de Ø75,60, de um lado
só) → remover camada REC ≥ 0,02 mm → indução/nitretação → medição final. **Meçam a abertura da fenda antes e
depois do tratamento e gravem os dois números**; camada de 8-18 µm por face come 0,016-0,036 mm de uma
tolerância de +0,010/−0,000.
· **Proibido:** furo de fixação, flange, rosca, pino e linha de partição. A peça é 1 sólido e é segurada pelo
collete EX-031 e pelo degrau do furo do cabeçote.

Preciso de: prazo, preço, e a confirmação de se vocês fecham o comprimento em **95,00 −0,50/+0,00** (com +0,5
a face passaria 0,5 mm para fora do nariz). Dossiê na entrega: certificado EN 10204 3.1 do calor + relatório
dimensional com as cotas acima + microdureza em seção. Marcação a laser na face traseira:
`JONATHA v27.0 · EX-031 · 1045 · rev. 30 (2026-09-22) · lote · nº de série · data`. NDA antes de o desenho
circular internamente — o projeto está em patenteamento.

Att,
[nome] · [telefone]

---

## Opcional, e só se você quiser uma folha na mão deles

`08_Pacote_Usinagem_v30/FOLHA_DE_COTAS_V30.pdf` — uma página, meia-seção + face de saída + regras, sem o bloco
de notas da prancha completa (que você achou densa). É gerada a partir do mesmo JSON medido do STEP
(`desenhar_folha_de_cotas_v30.py`), e por isso bate com as cotas do e-mail. Não está dentro do
`PACOTE_MATRIZ_V30_PARA_ENVIO.zip` (o zip e os hashes publicados não mudaram). Se você anexar a folha, mande
junto o `CHECKSUMS_SHA256.txt`? Não — ela é informativa; o que vincula é o STEP e o que está escrito acima.

**Não mande:** o resto do pacote (a prancha grande, os relatórios, o `pacote_usinagem.json`), os modelos
históricos, a v29, o DXF do cabeçote e qualquer script daqui. Peça só 1 matriz — se eles oferecerem lote,
recuse por escrito.
