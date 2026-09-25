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

· **MATERIAL: aço 1045** (SAE J404 / EN 10083-2), barra forjada, fibra no eixo, normalizada ≤ 220 HB; corpo revenido
30-36 HRC; **arestas do land 55-60 HRC em camada 0,6-1,0 mm por indução**, ou nitretação a plasma 600-700 HV0,2
— escolha de vocês, declarada no relatório; sem PVD/DLC.

· **Ø94,00 ±0,5** (datum A, Z 0 → 69,90) · **Ø89,00 ±0,5** (69,90 → 80,70) · **Ø79,00 ±0,5** (80,70 → 95,00) ·
comprimento **95,00 ±0,5** · degraus com ±0,05 · coaxialidade dos três estágios **Ø0,02** · face de saída
planeza 0,01 e perpendicularidade 0,01 em A.
· **land 8,50 ±0,05** (Z 85,00 → 93,50) · fenda **75,00 × 1,500 +0,010/−0,000** com **R 0,75** nas pontas,
aresta viva · área da seção no land **112,0171 mm² ±0,5 %** (fora disso é rejeição) · chanfro 1,50 × 45°
(boca 78,00 × 4,50) · boca de entrada **Ø75,60 +0,05/−0,00, não alargar** · Ra ≤ 0,4 µm no canal e no land,
polido na direção da extrusão · Ra ≤ 0,8 µm nos Ø de envelope · rebarba ≤ 0,1 × 45°.
· **Sequência:** T.T. do corpo → retífica do land → **fio EDM do canal** (arame pela boca de Ø75,60, de um lado
só) → remover camada REC ≥ 0,02 mm → indução/nitretação → medição final. **Meçam a abertura da fenda antes e
depois do tratamento e gravem os dois números**; camada de 8-18 µm por face come 0,016-0,036 mm de uma
tolerância de +0,010/−0,000.
· **Proibido:** furo de fixação, flange, rosca, pino e linha de partição. A peça é 1 sólido e é segurada pelo
collete EX-031 e pelo degrau do furo do cabeçote.
· **Desenho em CAD, como você pediu:** vão junto dois DXF da mesma folha A3 (três vistas, 8 cotas, tabela de
anatomia, MATERIAL em destaque) — `MATRIZ_V30_DESENHO_COTADO_AC1015.dxf` para CAD antigo e
`MATRIZ_V30_DESENHO_COTADO.dxf` (AC1024) para AutoCAD recente — mais o `MATRIZ_V30_DESENHO_COTADO_PREVIEW.pdf`
para ver no celular. Os `.STEP` são texto ASCII `ISO-10303-21`: se abriu como "binário", foi o visualizador.
DWG você tira deles em Abrir → Salvar como, a geometria não muda. **O que vincula continuam sendo os STEP** —
o desenho é convenção de leitura, se divergir de mim avise antes de usinar.

Preciso de: prazo, preço, e a confirmação de se vocês fecham o comprimento em **95,00 −0,50/+0,00** (com +0,5
a face passaria 0,5 mm para fora do nariz). Dossiê na entrega: certificado EN 10204 3.1 do calor + relatório
dimensional com as cotas acima + microdureza em seção. Marcação a laser na face traseira:
`JONATHA v27.0 · EX-031 · 1045 · rev. 30 (2026-09-22) · lote · nº de série · data`. NDA antes de o desenho
circular internamente — o projeto está em patenteamento.

Att,
[nome] · [telefone]

---

## A folha em PDF é opcional — para o celular dele já basta o `PREVIEW.pdf` do DXF

`08_Pacote_Usinagem_v30/FOLHA_DE_COTAS_V30.pdf` — uma página, refeita hoje (23/09) para o tamanho de letra e o
pouco texto que você pediu. Cinco blocos: **faixa de MATERIAL no topo** — o aço 1045 em corpo grande, com a
norma (SAE J404 / EN 10083-2, barra forjada, fibra no eixo, normalizada ≤ 220 HB), a dureza do corpo e do land,
indução × nitretação como escolha de vocês, e o "sem PVD/DLC e sem trocar de aço"; **meia-seção no plano da
abertura** (é onde aparece o funil/cone interno, que na versão anterior não aparecia); **DETALHE A ampliado do
fim do canal** com a abertura 1,500 +0,010/−0,000 escrita grande; **face de saída** com largura e abertura da
fenda; e **regras** em três colunas curtas (ordem de fabricação, proibido, aceitação). Saíram da folha a prancha
densa, os balões numerados e o quadro de notas — nada de número chutado: a folha é gerada do mesmo
`pacote_usinagem.json` medido no STEP (`desenhar_folha_de_cotas_v30.py`), e por isso bate com as cotas deste
e-mail. Não está dentro do `PACOTE_MATRIZ_V30_PARA_ENVIO.zip` (o zip e os hashes publicados não mudaram). Se
você anexar a folha, mande junto o `CHECKSUMS_SHA256.txt`? Não — ela é informativa; o que vincula é o STEP e o
que está escrito acima.

## O DXF cotado da matriz — foi exatamente o que a matrizaria pediu (24/09, 10:01)

`08_Pacote_Usinagem_v30/MATRIZ_V30_DESENHO_COTADO.dxf` — A3, **1:1, milímetros, 8 cotas** e mais nada de
texto solto. A folha é geometria: três vistas (**seção no plano da abertura 1:1** — é aí que o funil aparece;
**face de saída 1:1** com a fenda e a boca do chanfro com os raios de verdade; **DETALHE A 6:1** do fim do
canal, onde a `ABERTURA 1,500 +0,010/-0,000` está escrita grande) e uma **tabela de anatomia de 13 linhas**
com três colunas: região / cota de contrato / o que a medição no STEP achou. As 13 linhas, na ordem: face de
entrada (planicidade do datum), Ø dos 3 estágios, posição dos degraus 1→2 e 2→3, coaxialidade, boca de
entrada, funil em spline, raio da junção funil-fenda, land com a faixa axial, abertura da fenda, largura da
fenda, raio das duas pontas, chanfro com a boca, comprimento total. O **material** é a linha de topo, em corpo grande: `MATERIAL: AÇO 1045 · SEM PVD ·
SEM DLC · SEM OUTRO AÇO`, com a norma e a dureza logo abaixo; e ele volta em vermelho no carimbo. Da
fabricação ficou **uma** linha no rodapé da tabela (fio EDM pelo Ø75,60 de um lado só depois do tratamento,
medir a abertura antes e depois, sem furo/flange/rosca/pino/linha de partição, certificado EN 10204 3.1 e
relatório dimensional) — o passo a passo está no `03_SEQUENCIA_DE_USINAGEM.md` do pacote, não na folha.
As 8 cotas são `DIMENSION` verdadeiras: eles medem, editam e importam no CAD. A geometria é a nominal exata
medida no STEP, então o número lido no arquivo bate com o texto da cota; o `audit()` do ezdxf fechou em zero
erros e nenhuma etiqueta da folha se sobrepõe a outra. Dois avisos: o `Ø` pode não aparecer se a fonte do
texto do CAD não tiver Latin-1 (trocaram para Arial, o arquivo não muda), e o desenho é informativo — o que
vincula continuam sendo os STEPs. Saíram junto, para ver sem abrir CAD: `_PREVIEW.png` e `_PREVIEW.pdf`.
Há dois arquivos da mesma folha, e a escolha é pela idade do CAD deles: `MATRIZ_V30_DESENHO_COTADO_AC1015.dxf`
(AutoCAD 2000, acentos em cp1252 de um byte, sem escape `\U+`) abre em qualquer coisa que exista na oficina;
`MATRIZ_V30_DESENHO_COTADO.dxf` (AC1024) é o padrão para CAD recente. **Se você tiver de mandar um só, mande
o AC1015.** Os dois passam as mesmas travas (0 erros de `audit()`, 8/8 cotas conferidas, 0 etiquetas
sobrepostas) e o conteúdo é byte a byte a mesma folha; quem os gerou foi o mesmo script, `DXF_SERIE=R2000` no
segundo caso. E por escrito o pedido dele: "se não abrir o DXF aí, diga qual versão de AutoCAD vocês usam que
eu te mando a mesma folha nela" — nós não inventamos DWG, mas DXF em qualquer versão do AC1015 para cima é só
rodar o script.
Nada disso está dentro do `PACOTE_MATRIZ_V30_PARA_ENVIO.zip` (o zip e os hashes publicados não mudaram).
A v29 tem o desenho dela na pasta `_v29` (comprimento 109,00, land de 99,00 a 107,50, protrusão 14,00).

**Não mande:** o resto do pacote (a prancha grande, os relatórios, o `pacote_usinagem.json`), os modelos
históricos, a v29, o DXF do cabeçote (só a matriz tem desenho cotado) e qualquer script daqui. Peça só 1 matriz — se eles oferecerem lote,
recuse por escrito.
