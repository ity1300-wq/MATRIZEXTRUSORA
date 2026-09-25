# HISTÓRICO DA CONVERSA — o resumo de tudo, atualizado a cada interação

Arquivo pedido pelo dono do projeto em 2026-09-25: *"faça um arquivo leve que contenha toda nossa conversa
histórico e seja atualizado a cada interação; este deve ser sempre atualizado no GitHub"*.

**Regra de atualização (vale para quem assumir):** a cada rodada em que se fala com ele, **acrescentar uma
entrada no fim da seção do dia**, com (a) o que ele pediu, (b) o que saiu, (c) o sha do commit. Nada de reescrever
entrada antiga — quando algo é corrigido, entra uma linha nova dizendo "corrigindo a rodada X". Este arquivo é
texto puro: **não** entra no zip dos pacotes de usinagem e, por isso, **não** move a tag (regra §12 do
`CONTINUIDADE.md`). O documento gordo continua sendo o `CONTINUIDADE.md`; este aqui é a linha do tempo.

Legenda: `sha` = commit na branch `continue`. `01_`…`08_` = `01_CAD_MatrizJonatha_Oficial` … `08_Pacote_Usinagem_v30`.

---

## 2026-09-11 — de onde o projeto veio

* O repo chegou da mão dele com a **Matriz Jonatha v27.0** (bipartida, Body_A + Body_B), relatórios de CFD,
  JSON de parâmetros e o `AUTO_PROMPT`. Os commits iniciais são dele: harmonização v26.1 → v27.0, auditoria
  A-01 (Hm 12,00 mm, ΔP 39,5 bar), organização em pastas < 24 MB.

## 2026-09-11/12 — primeiras medições e a triagem

* `211f786` Triagem das 4 matrizes: separa problema real de alegação não sustentada (nasce o
  `03_/TRIAGEM_DE_PROBLEMAS_DAS_MATRIZES.md`).
* `3b29ff8` Auditoria geométrica automatizada dos STEP oficiais (v27.0).
* `bbf50e2` v28.0 proposta DFM: chanfro 0,80 × 45 + land 9,20, pinos conjugados, 6 cartuchos + 4 termopares.
* `1a61c95` Interface com o cabeçote EX-030 medida e provada por booleanos (43 itens, 0 não conformes).
* `0878a5b` / `98f2760` v28.1 aplica D1/D2/D4; SSOT, relatório DFM, README e AUTO_PROMPT sincronizados.
* `89a559d` **D3 medida:** funil coat-hanger modelado e comparado com o cone do master.
* `1688adb` gerador: rótulos dos documentos passam a vir do SSOT, não de número chutado no código.
* `b943553` **Collete EX-031:** o furo medido é Ø90,00 reto e não passa sobre a banda Ø93,00 — a pressão radial
  do collete vira número **condicional**. (Pendência aberta, não resolvida.)
* `6a7fb36` estudo do recuo dos cartuchos + correção do volume de bloqueio.
* `5c6444b` medidor de DXF com detector de cone e registro explícito do que o arquivo **não** permite ler.
* `de4dcd8` nasce o **portão**: `04_/verificar_cadeia.py`, uma porta única que roda a cadeia e cobra invariantes.
* `6376b64` SSOT do cabeçote: protrusão 14,00 mm (não 14,3) e os dois degraus separados por 0,30 mm.
* `d22c530` / `0db8d74` o "20 mm" do corte é o **M12 do bolso**, não protrusão — item reaberto com NC medida;
  sai o STEP do cabeçote **sem** a junta da extrusora, como ele pediu.
* `e3028dd` o "ressalto Ø203 × 3" era a fenda; a traseira tem piloto Ø105 × 3,00.
* `4a71901` chanfro 10 × 45° da transição corpo→flange entra no sólido. `bd3d081` rodada de cenário não escreve
  mais em documento oficial.
* `4f7f96b` **parte interna:** as 5 matrizes medidas uma a uma contra a escada do cabeçote (é daqui que sai a
  diferença copo × Gedeon = 28,30 mm de nariz).
* `29a3545` desenho 2D em PDF do par; encosto **face a face** gravado; o modelo corrigido por ele.
* `1956991`…`5894de1` vereditos da cerimônia de auditoria: PRP-0000/0001/0002 **APROVADO/RESSALVAS**,
  PRP-0004 **REPROVADO**.

## 2026-09-13 — arrumação, auditoria grande, e o que ele mandou parar

* *"Matriz corrigida está errada, matriz Gedeon certa.step é de fato a matriz Gedeon certa"* ⇒ a Gedeon é **o
  arquivo dele, como está**. Proibido re-escavar canal/funil nele.
* *"ignore auditoria agora"* ⇒ cerimônia de auditoria suspensa; método v1.0 ENCERRADO depois.
* *"não gostei da organização, cada matriz deve estar numa pasta separada"* ⇒ `07_CAD_Matrizes/Matriz_<nome>/`.
* *"quero que apague a matriz Gedeon corrigida"* ⇒ apagada por inteiro (gerador, JSON, relatório, 5 STEP,
  montagem). Não existe script que a recrie.
* `cf8b8c2`/`6f23222` seis montagens matriz-dentro-do-cabeçote **com flange**, uma por matriz.
* `5be639f` auditoria de correlações dos 64 STEP, sete cruzamentos, todos medidos no arquivo.
* `8541613`/`13f6707` workspace inteiro no git, `restaurar_workspace.sh`, CI/portão pronto (o push do
  `.github/workflows/` foi recusado por escopo de token — medido, não opinado).
* `803a9eb` restorei os 23 atalhos de `01_`/`02_` que um commit meu tinha apagado, e o portão ganhou a checagem
  que impede a reincidência.
* `303f799` PRs fechadas (a #4 sem mesclar e sem re-veredito), com o estado registrado.

## 2026-09-14 — peça única

* `c35facf` **v27.0 como peça única:** duas metades viram um sólido, canal idêntico, sem linha de partição, sem
  bolha selada. O produto não muda nada.

## 2026-09-18 — v29 promovida e o pacote de fábrica

* `030c17e` v29.0 promovida a oficial; `08_Pacote_Usinagem_v29/` pronto para enviar; a conta que responde
  "109 × 100 mm" (`03_/SIMULACAO_ROTAS_E_COMPRIMENTO.md`: ΔP 203,6 / 219,7 bar, e encurtar a peça não muda o ΔP).

## 2026-09-22/23 — revisões, pacote, e a folha de cotas

* `02d1038` pacote: **1 matriz só**, com o nome do dono (MATRIZ JONATHA v27.0 – peça única); `1bc5fdf` e-mail de
  primeiro contato + CHECKSUMS.
* `4720027`…`d36134b` **revisões de 22/09:** v29 re-feita com Ø94/89/79 e **v30 de 95,00 faceada ao nariz**,
  aço 1045 com indução/nitretação na fenda, ±0,5 nos diâmetros de corpo; pacotes das duas, SSOT e relatórios.
* `c1a6c9e` CHECKSUMS passa a ir **dentro** do zip; `12c18c0` corrigidas três linhas de Ø que saíam 93,00/89,50/79,50;
  `e4fa646` rótulos da prancha saem do modelo medido; `e823bc4` milhar parou de virar vírgula dupla.
* `a4e233b` **nasce a regra de publicação** (`CONTINUIDADE.md` §12) por causa de *"sempre atualize o GitHub"*.
* `6c70f9d` a linha do land também passa a ser medida no pacote; sai o e-mail para a fábrica.
* `7ec613f` folha de uma página para mandar junto com os STEP + e-mail curto.
* `72623e5` → `80c8a00` folha refeita: **meia-seção com o funil visível**, detalhe A da abertura 1,500, menos
  receita de fabricação, mais anatomia, e o **aço 1045 em faixa própria no topo** (foi a correção dele:
  *"retire essa bagunça… em momento nenhum aparece o 'cone' interno dela"* / *"enfatize o material aço 1045"*).
* `8d16400` a folha só usa caracteres que o PDF devolve na cópia, e a projeção passou a ser lida da montagem.

## 2026-09-24 — o primeiro DXF e a matrizaria

* `93b2ed3` **sai o primeiro `.dxf` cotado da matriz** (A3, 1:1): 8 cotas, MATERIAL em ênfase.
* `71de1c5` o DXF vira **folha de anatomia**: tabela de 13 linhas, detalhe A 6:1, menos texto de fabricação.
* `39cbbb6` correção de precisão: cada release tem **dois** anexos, não quatro (conferido no disco e na API).

## 2026-09-25 — o dia do serrilhado (9 rodadas)

* **1ª** `a696ec7` — a conversa com a matrizaria (Fernando) lida por inteiro e registrada em
  `03_/CONTATO_MATRIZARIA_FERNANDO_2026-09-24.md`; DXF ganha gêmeo **AC1015** (para abrir no AutoCAD dele).
* **2ª** `ba4a751` — as 13 figuras embutidas no PDF do contato extraídas e lidas (as duas soluções do Fernando
  em foto).
* **3ª** `7f5aa02` — *"você é a origem do projeto, avalia"*: a v30 **não** equilibra fluxo; escrito sem defender
  autoria (`03_/AVALIACAO_V30_X_FLUXO_2026-09-25.md`).
* **4ª** `17f53a9` — **correção dele:** *"que disco de corte? não tem disco de corte nenhum, a manta sai
  serrilhada da matriz"*. Retirei a hipótese do disco dos três documentos que a carregavam. Lição gravada:
  pixel de anexo de transcrição **não é evidência de processo**.
* **5ª** `69b2d50` — *"nosso objetivo é justamente tirar o serrilhado"*: a conta centro × pontas, a lei 1/n e o
  preço de cada remédio (`03_/FLUXO_CENTRO_X_PONTAS_2026-09-25.md`).
* **6ª** `b60a819` — ele **mede** o perfil na linha (1,50/2,00/2,57/1,80/1,50 mm) e o perfil vira número: centro
  +71 % de material com +18,8 % de resistência nas bordas (`03_/PERFIL_DE_ESPESSURA_E_SORRISO_2026-09-25.md`).
* **7ª** `a7d4d8d` — segunda medição, agora com **balança**: m/t bate em 2,9 % de sd ⇒ o perfil é real; seção
  integrada 159,4 mm² (+42 % sobre o nominal); assimetria +25 % com máximo em **dois** pontos ⇒ girar 180° antes
  de cortar; flecha do sorriso fecha em **1,50 mm** (`03_/MEDIDA_2_PERFIL_E_PESO_2026-09-25.md`, PRP-0007).
* **8ª** `99d2fc6` — ele redireciona o alvo: *"PRINCIPAL PROBLEMA é o serrilhado nas extremidades, não quero
  espessura agora"*, e dá a pista do tempo ("sempre que esfria sai boa; depois que a manta esquenta sai ruim").
  Saem as contas de calor e as 5 opções de refrigeração (`03_/RESFRIAMENTO_DA_MATRIZ_2026-09-25.md`), e o
  veredito: **o serrilhado da borda é rasgo por tração, não fratura** (τ 135,5 kPa **abaixo** do limiar 140; o do
  centro 160,9 **acima**).
* **9ª** (hoje) — *"hoje usamos a matriz copo; veja como ela fica no cabeçote e pense em como resfriar"*.
  Medida a montagem `Cabecote_EX-030_com_Matriz_Copo.step`: corpo Ø93 × 80,70, copo Ø75,60 × 70,70, land
  10,00 mm sem chanfro, **boca enterrada 14,30 mm dentro do túnel Ø80 do cabeçote**, folgas 0,10/0,25/0,30/1,00 mm,
  e a casca inteira (55.129,7 mm²) sem contato com o ar. Consequência: **não há onde pôr refrigeração na matriz**
  (furo de água é geometricamente impossível: a faixa do centro seria 43,80…40,50 mm de raio, vazia), e o
  resfriamento tem de entrar **pelo nariz do cabeçote** — pano molhado, colar d'água na banda Ø130 de Z 53 a 81,
  e faca de ar depois da face. Documento: `03_Relatorios_e_Documentacao/RESFRIAMENTO_MATRIZ_COPO_2026-09-25.md`.
  **Mesma rodada, com as 6 fotos + 1 vídeo dele no repo `ity1300-wq/ACESS`** (sha256 conferidos): a ponta do
  cabeçote é uma face lisa de aço sem tinta com **furo redondo por onde a manta passa** — nada de matriz para
  fora, o que confirma a boca enterrada; a faixa está **livre** para o colar d'água; existe **mostrador 0-150 °C**
  no corpo (não precisa de IR); **não há água** no cabeçote (as mangueiras são conduíte). Eu li o par de rolos de
  aço como **puxador** e ele corrigiu: é **papel siliconado** aplicado na manta, que **sai da matriz e entra na
  esteira** ⇒ continua sem puxador, e o teto da flecha da 7ª permanece. Ele também derrubou a minha hipótese de
  raspo no furo do nariz (*"ignore isso, é resquício de manta velha"*). Registrado na §10 do documento.

---

## Ordens dele que continuam valendo

* **SSOT numérico** é `04_/cad_die_parameters.json`; nenhum número vai para documento sem medição.
* **Jamais editar `02_CAD_Modelos_Historicos/`** (só ler).
* Largura 75,00 constante; espessura 1,500 com R 0,75; entrada restrita a Ø75,60 em Z = 0.
* Matriz **sem flange, sem furo de fixação**; fixação por collete EX-031 + degrau; encosto face a face.
* Interface: a matriz casa nos 3 estágios e passa pelo nariz **sem tocar a fenda**.
* Entregável CAD só em **STEP** (+ DXF/PDF quando ele pedir desenho).
* Cada matriz em pasta separada; a Gedeon CERTA é o arquivo dele, como está; a "Gedeon corrigida" não existe mais.
* v28.1 **não** promovida; peça única é oficial; D10/D11/D12 em diâmetro inteiro ±0,5, corpo 1045 com indução/
  nitretação na fenda, **sem** PVD/DLC.
* *"Sempre atualize o GitHub"* ⇒ publicar a cada rodada (§12 do `CONTINUIDADE.md`): portão → commit → push
  `continue` → merge `--no-ff` na `main` **por nome de branch** → push → conferir pela API. Tag e re-upload de
  assets só quando o **zip** muda.
* *"Email resumido, poucos caracteres, irei enviar somente a pasta 3d arquivos steps"*.
* Resposta em **veredito de uma linha, chão de fábrica, frases curtas, sem jargão e sem tabela grande**.
* O alvo dele hoje: **serrilhado nas extremidades**. Não vender equalização de espessura como objetivo.

## Onde estamos agora (estado desta rodada)

0. **Correção de rumo (25/09, fim da rodada):** ele disse que eu estava viajando e reafirmou o alvo —
   **o serrilhado nas duas bordas da manta**. Reavaliação completa, escrita como avaliador novo, em
   `03_/REVALORACAO_FOCO_SERRILHADO_2026-09-25.md`, com as três matrizes re-medidas no STEP. Resultado em uma
   linha: **nenhuma delas tem alívio nas pontas** (nem a Gedeon CERTA), e a diferença da Gedeon é ser
   **alimentada ao longo dos 75,00 mm num plano só** com **88,00 mm de land** (193 bar) — deficit implied
   1,7 % contra 14,3 % da copo e 12,3 % da v30. Refrigeração passa a constar como paliativo estacionado.
   Primeiro passo, grátis, do lado dele: **medir a manta da Gedeon nos mesmos 5 pontos**.
0. **Fechado no fim da rodada, por ele:** a peça curta de Ø ~25 mm na frente da faixa sem tinta é **alça de
   ferro** — pega de manuseio do cabeçote, não tubo e não dreno. Só muda o desenho da abraçadeira (recorte para a
   alça passar). A pergunta que continua do lado dele, e é a que pode mudar o plano sem fabricar nada: **o
   cabeçote é aquecido hoje, ou só recebe calor da adjunta de trás?**
0b. **E ele respondeu o que faltava: o cabeçote NÃO TEM abraçadeira de aquecimento** (nem termopar, nem
   isolamento). Isso abriu a §11 do plano de resfriamento e mudou o diagnóstico: 12,327 kg de aço com **0,254
   W/K** de perda para o ar e constante de tempo de **74 min** na faixa — o "sai boa e depois piora" é o bloco
   ensopando de calor vindo da adjunta, não o atrito da fenda (a manta leva os 32,8 W embora com 0,9 °C). Não
   encapar, não aquecer; medir a face do nariz com IR (6,4 K abaixo da matriz já exporta o calor todo); e o teste
   das seis leituras aos 0/10/20/40/60/90 min decide entre "segurar temperatura" e "rev. 31".
1. A matriz oficial para a fábrica continua a **v30** (pacote `08_Pacote_Usinagem_v30`, tag `v30.0-oficial-pacote-usinagem`,
   zip 588.274 B, sha `0738c468…`) — **nenhuma cota foi tocada por causa do serrilhado**; nenhuma forma nova foi cortada.
2. O que a linha mostrou: defeito cresce com **tempo e velocidade** e some quando a matriz é resfriada. Isso é
   aquecimento viscoso, e a matriz sozinha não conserta.
3. Com a **copo** na máquina, refrigeração na matriz é impossível (medido). O caminho é o nariz do cabeçote, e a
   refrigeração **dá tempo, não tira a tração da borda**.
4. Para abrir a rev. 31 (**PRP-0007**: gotas nos extremos da fenda + arco do sorriso com flecha 1,50 mm + chanfro
   0,50 × 45) falta o **sim** dele. A escolha do caminho é dele.
5. Pendências do lado dele, depois das fotos: **o cabeçote é aquecido hoje ou só recebe calor de trás** (no que
   aparece nas fotos ele não tem instrumento, nem abraçadeira, nem isolamento — se for assim, a temperatura da
   matriz não é medida nem controlada por ninguém); `T_limiar` **com IR ou termopar de ponteira na face do nariz**
   no teste 100/80/60 % (os manômetros da máquina **não** servem: ele confirmou que ficam longe do cabeçote, e o
   IR volta a ser item do teste); se o rolo de papel siliconado fica encostado em parte quente; girar a matriz
   180° e remedir; e a área real da amostra. **Já respondidas:** a banda do cabeçote está livre para receber o
   colar, não há água no cabeçote (e o cano curto da foto não é dreno — o EX-030 tem um único furo transversal, o
   M12 do pushador, conferido no DWG), e não há puxador (é papel siliconado + esteira).