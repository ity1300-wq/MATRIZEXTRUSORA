# PROJETO DFM v28.0 — Matriz Jonatha (revisão para fabricação)

**Projeto:** matriz de extrusão plana para manta isolante de acessórios de cabos MT
**Modelo base (aprovado):** `01_CAD_MatrizJonatha_Oficial/MatrizJonatha.step` — SSOT v27.0
**Esta revisão:** v28.0 — **PROPOSTA, pendente de aprovação do usuário**. O v27.0 não foi alterado.
**Data:** 2026-09-11
**Verificação:** `04_Dados_SSOT_e_Scripts/verificar_v28.py` → **64 itens, 64 conformes, 0 não conformes**
**Conferência visual:** `V28_CONFERENCIA_VISUAL.png` (6 vistas, lidas dos STEP)

---

## 1. Resumo em seis linhas

1. O funil de fluxo aprovado **não foi tocado**: a distância máxima entre a superfície do funil
   v28.0 e a do v27.0 medida nos sólidos é **0,000000 mm**.
2. **P7 e P8 fechados**: chanfro de saída passou de 1,50 → **0,80 × 45°**, o que devolve 0,70 mm
   de land reto (**land paralelo = 9,20 mm**, era 8,50) e engrossa a lâmina do
   lábio de 0,75 → **1,450 mm**.
3. **P2 fechado**: os 4 bolsões de pino Ø4 × 12 agora são **abertos no plano de partição e
   conjugados nas duas metades** (o v27.0 tinha 2 bolsões selados só no Body_A e nada no Body_B),
   com kit de pinos modelado em `MatrizJonatha_v28_Pinos_Alinhamento.step`.
4. **P3 parcialmente fechado**: 6 cartuchos Ø9,5 e 4 poços de termopar Ø4,8 na zona do land,
   com paredes reais medidas de 8,20–17,03 mm. A refrigeração
   **não cabe no corpo** (item 5) e vai para o adaptador.
5. **P1 continua sem solução dentro do envelope** — e agora com a prova geométrica: sobram
   apenas 8,70 mm de aço entre o canal Ø75,60 e o Ø93, menos do que Ø9,5 + 2 × 4 mm de parede.
6. **P5 fechado**: o arquivo do canal é **1 único sólido** (o v27 entregava 3). Os números de CFD
   permanecem não reproduzíveis e foram re-marcados como "estimativa a confirmar" (item 7).

---

## 2. O que é e o que não é esta revisão

| | Situação |
| :--- | :--- |
| `MatrizJonatha.step` (v27.0) | **Continua sendo o master aprovado.** Nenhum byte foi alterado; a auditoria do v27 (`verify_geometry_ssot.py`) continua acusando os mesmos 2 não conformes históricos. |
| `MatrizJonatha_v28*.step` | Proposta DFM gerada por `gerar_matriz_v28.py`, verificada por `verificar_v28.py`. Vira oficial só depois do "aprova" do usuário. |
| `02_CAD_Modelos_Historicos/` | Intocada (regra 2 do projeto). |
| Produto (a manta) | Intocado e re-verificado: fenda **75,00 × 1,50 mm**, bordas **R0,75**, área da seção **112,02 mm²**, boca de entrada **Ø75,60**, envelope **Ø93 × 69,90 / Ø89,5 × 10,80 / Ø79,5 × 28,30**, comprimento **109,00 mm**. |

**Como reproduzir** (em container sem GPU/libGL, rode o `setup_headless_gl.sh` primeiro):

```bash
bash 04_Dados_SSOT_e_Scripts/setup_headless_gl.sh
export LD_LIBRARY_PATH="$PWD/04_Dados_SSOT_e_Scripts/.headless_gl:$LD_LIBRARY_PATH"
python 04_Dados_SSOT_e_Scripts/explorar_acomodo_furos.py --json   # onde existe aço para furos
python 04_Dados_SSOT_e_Scripts/gerar_matriz_v28.py                # gera os STEP v28.0
python 04_Dados_SSOT_e_Scripts/verificar_v28.py --json --md        # mede e prova (63 itens)
python 04_Dados_SSOT_e_Scripts/gerar_relatorio_v28.py            # este relatório
python 04_Dados_SSOT_e_Scripts/renderizar_v28.py --saida v28.png  # conferência visual
```

---

## 3. Tabela antes × depois (tudo medido nos STEP)

| Item | v27.0 (aprovado) | v28.0 (proposta) | Como foi medido |
| :--- | ---: | ---: | :--- |
| Land reto e paralelo | 8,50 mm | **9,20 mm** | varredura de seção em Z (passo 0,05 mm) até abs(Y) ≠ 1,50 |
| Chanfro de saída | 1,50 × 45° | **0,80 × 45°** | folga radial a 0,10 mm da face |
| Lâmina do lábio (ponto mais fino) | 0,75 mm | **1,450 mm** | Ø79,5/2 − abs(X) da seção na face Z=109 |
| Furos de pino Ø4 × 12 | 2, selados no Body_A; 0 no Body_B | **4 abertos e conjugados (2 por lado)** | volume do furo ∩ corpo = 0 e aço sob o fundo presente |
| Cavidades internas fechadas | Body_A: 2 | **0** (1 shell em cada metade) | contagem de `TopAbs_SHELL` |
| Cartuchos de aquecimento | 0 | **6 × Ø9,5**, fundo a 8,20 mm do canal | booleano + `BRepExtrema` |
| Poços de termopar | 0 | **4 × Ø4,8**, fundo a 17,03 mm | idem |
| Arquivo do canal | 3 sólidos | **1 sólido** | contagem de sólidos no STEP |
| Massa de aço | 3,682 kg | **3,587 kg** | volume × 7,85 g/cm³ |
| Fechamento volumétrico | resíduo 0,001 mm³ | **resíduo 0,0115 mm³** (env − aço − canal = Σ furos) | booleano |
| ΔP 1D sobre a geometria | 41,9 bar | **v28.0 = 43,9 bar · v27.0 = 41,9 bar** | `dp_total()` do próprio projeto |
| τ na parede do land | 164,0 kPa | **163,8 kPa (γ̇_ap = 911 s⁻¹)** | `tau_parede()` do próprio projeto |
| Fixação das metades | inexistente | **ainda inexistente — decisão necessária** | item 4 |
| Refrigeração | inexistente | **não cabe no corpo** | item 5 |

---

## 4. P1 — fixação das metades: por que não há furo que resolva isso

A força que empurra uma metade contra a outra é a pressão sobre a área projetada do canal no plano XZ.
Medindo essa área no sólido: **8168 mm²** (não é a área da boca; é a integral da largura do canal ao longo de Z).

| Cenário de pressão | Força de abertura |
| :--- | ---: |
| ΔP de projeto do CFD (68,2 bar) atuando sobre **toda** a área projetada (limite superior) | **55,7 kN** |
| 68,2 bar atuando só sobre a boca Ø75,60 (o número citado no relatório de triagem) | 30,6 kN |
| ΔP 1D medido na geometria (43,9 bar) sobre a área projetada | ≈ 35,9 kN |

A geometria não oferece onde ancorar isso:

* faixa de aço entre o canal e o Ø93: (93,00 − 75,60)/2 = **8,70 mm**;
* um furo radial Ø9 (M8) com parede de 4 mm de cada lado exigiria **9 + 8 = 17 mm**;
* no 3º estágio (Ø79,5) a faixa cai para **1,95 mm** — ali não entra nem pino;
* consequência: **parafusos radiais ou axiais no corpo são geometricamente impossíveis** sem
  alterar o envelope, e o envelope é a regra que garante a montagem na extrusora.

**Três caminhos viáveis, em ordem de preferência de quem já viu isso abrir em produção:**

1. **Monobloco por EDM.** Eliminar a bipartição: abrir o canal por EDM a partir da face de saída
   (o `MatrizJonatha_v28_Canal_Fluxo.step` de 1 sólido é exatamente o arquivo para isso) e
   trepanar a boca Ø75,60 por trás. Sem plano de partição, não há força de abertura para
   reagir, e os pinos deixam de ser necessários. Custo: eletrodo + tempo de EDM.
2. **Aro de retração (shrink ring)** no degrau Ø93 → Ø89,50 (Z = 69,90). O aro coloca o corpo em
   compressão circunferencial e fecha o plano de partição por atrito, pré-carregada. Vantagem: não
   fura a peça. Necessita: verificar no cabeçote o espaço axial de 0,8 mm do degrau.
3. **Grampos externos usando o cabeçote.** O cabeçote já tem 6 × M12 em BC Ø150 com curso angular
   de ±15° (item 6) — se o nariz do cabeçote tiver ombro, a própria união cabeçote-matriz
   pré-carrega o plano de partição. Requer confirmar o desenho de execução (item 6, escala).

Recomendação: **opção 1 (monobloco + EDM)** para a matriz de produção e manter a bipartição só no
protótipo de bancada. As duas outras são remendo; a 1 remove a causa.

---

## 5. Furação da v28.0 — cotas de usinagem e paredes reais

Estas são as coordenadas do modelo; o `matriz_v28_features.json` é a fonte.

| Furo | Ø (mm) | X (mm) | Z (mm) | Y (mm) | Compr. (mm) | Parede real medida |
| :--- | ---: | ---: | ---: | :--- | ---: | ---: |
| cartucho | 9,50 | -22,00 | 97,00 | ±12,03 … 35,11 (1 por metade) | 23,08 | 8,20 mm |
| cartucho | 9,50 | 0,00 | 97,00 | ±12,03 … 41,75 (1 por metade) | 29,72 | 8,20 mm |
| cartucho | 9,50 | +22,00 | 97,00 | ±12,03 … 35,11 (1 por metade) | 23,08 | 8,20 mm |
| pino_alinhamento | 4,00 | -42,10 | 60,00 | -12,00 … 12,00 (nas duas metades) | 24,00 | 2,39 mm |
| pino_alinhamento | 4,00 | +42,10 | 60,00 | -12,00 … 12,00 (nas duas metades) | 24,00 | 2,39 mm |
| pino_alinhamento | 4,00 | -42,10 | 30,00 | -12,00 … 12,00 (nas duas metades) | 24,00 | 2,39 mm |
| pino_alinhamento | 4,00 | +42,10 | 30,00 | -12,00 … 12,00 (nas duas metades) | 24,00 | 2,39 mm |
| termopar | 4,80 | -11,00 | 103,00 | ±18,20 … 40,20 (1 por metade) | 22,00 | 17,03 mm |
| termopar | 4,80 | +11,00 | 103,00 | ±18,20 … 40,20 (1 por metade) | 22,00 | 17,03 mm |

Regras de fabricação aplicadas no desenho:

* **parede mínima até o canal**: pino 2,39 mm (alvo ≥ 2,0), cartucho 8,20 mm (alvo ≥ 4,0),
  termopar 17,03 mm (alvo ≥ 3,0) — todas medidas com `BRepExtrema`, não estimadas;
* **web mínima entre furos**: 5,380 mm — nenhum furo encosta em outro;
* todo furo de aquecimento é **cego** e **abre na face externa**; nenhum rompe a face de entrada
  (Z=0) nem a de saída (Z=109) — verificado por interseção com lâminas nas duas faces;
* furação só de um lado do plano de partição por vez: cada metade é usinada sozinha e os bolsões
  são conjugados (mesmo X, Z e profundidade nos dois corpos), o que o verificador confirma;
 * os furos de alavanca de desmontagem (Ø5) que estavam no rascunho foram **suprimidos**: na faixa
   de 8,70 mm eles deixariam < 1,0 mm de parede na superfície externa. Desmontar pelo chanfro de
   1 × 45° a pedir na aresta do plano de partição.

**Refrigeração:** o mapeamento sistemático do aço (`acomodo_furos.json`) não encontrou **nenhuma**
posição para Ø8,0 com parede ≥ 3,5 mm. Axial ou radial, o furo atravessa a peça ou encosta no
funil. Portanto refrigeração vai para o **adaptador/cabeçote** (que é onde o `COMPARATIVO_SIMULACOES_E_SISTEMA_DE_REFRIGERACAO.md`
já a colocava), não para a matriz. Isso não é escolha de projeto: é consequência do envelope
Ø93 com boca Ø75,60.

---

## 6. Cabeçote — o dado externo que destravou P4 (lido do DWG)

`030-032- cabeçote.dwg` (AutoCAD R2004, AC1018, desenhos EX-030/031/032 da Hideall) foi convertido
para DXF e as entidades medidas numericamente — não lidas no olho. O DXF não preserva texto
(as cotas viraram polilinhas), então o que segue vem da **geometria**:

| Medido no desenho (unidades do DXF) | Valor | Leitura |
| :--- | ---: | :--- |
| 6 círculos de Ø0,6266 u em BC Ø7,050 u, ângulos 30°/90°/150°/210°/270°/330° | passo exato de 60° | **6 furos em círculo primitivo** |
| cada um com um lobo maior tangente (formato "fechadura") + anotação "15°" com arco | — | **slots com curso angular de ±15°** para ajuste de giro da matriz |
| 6 círculos de Ø0,2350/0,1960 u em BC Ø3,603 u | razão BC/furo = 15,3 | outra furação (rosqueada) menor, num dos itens 031/032 |
| ressalto retangular tangente à borda externa, em 0° | — | **chave/ressalto de anti-rotação** |
| anéis concêntricos com razões 1,00 / 1,167 / 1,358 / 1,400 / 1,533 / 1,750 / 2,167 / 2,333 / 3,067 / 3,667 | — | furação do nariz do cabeçote |

Calibração de escala: a anotação legível "**C/G Ø150**" sobre o círculo dos 6 furos dá
21,28 mm/unidade; com a mesma escala, o círculo de Ø3,29 u vira **Ø70,0 mm** (bate com a cota "70"
do desenho) e o furo de Ø0,6266 u vira **Ø13,33 mm** (Ø de folga para M12, 13,5 pela ISO 273 grossa,
±1,3 %). Três cotas independentes fechando com um único fator é o que sustenta a escala; a
incerteza nos diâmetros absolutos é de ~1 %.

**O que fazer com isso:** a matriz **não** se fixa com furos próprios (item 4); ela é retida pelo
cabeçote, e o cabeçote é fixado por **6 × M12 em BC Ø150, passo 60° a partir de 30°, com curso
angular de ±15° e chave a 0°**. Isso é suficiente para: (a) prever no projeto da matriz um
assentamento e uma folga angular compatíveis com ajuste de ±15°; (b) projetar os 6 furos da matriz
no mesmo BC, se a opção de grampos for escolhida.

**O que ainda falta (e não dá para tirar deste arquivo):** profundidade do nariz, diâmetro e
tolerância do furo de assentamento, e se o Ø150 é furação passante no cabeçote. Isso se resolve com
paquímetro na máquina, não com CAD. O DWG é um raster de avaliação (marca d'água "Evaluation only"),
portanto **confirmar na máquina antes de usinar**.

---

## 7. Duas descobertas sobre o modelo que valem decisão

**7.1 O "coat-hanger" não está no sólido aprovado.** A medição seção a seção do canal aprovado
(`MatrizJonatha_Canal_Fluxo.step`) mostra que a **largura em X é ~constante de 75,6 → 75,0 mm**
do Z=0 ao Z=99, enquanto a **altura em Y fecha linearmente de ±37,61 para ±0,75 mm**:

| Z (mm) | 0,5 | 25 | 50 | 70 | 90 | 99 | 109 |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| X (mm) | ±37,80 | ±37,72 | ±37,65 | ±37,59 | ±37,53 | ±37,50 | ±39,0 |
| Y (mm) | ±37,61 | ±28,44 | ±19,09 | ±11,60 | ±4,12 | ±0,75 | ±2,24 |

Ou seja: o funil do modelo é um **reduzor cônico linear (V em Y)**, não um manifold de cabide com
reservatório central de 6,00 mm e asas em Z=25/Z=70 como descreve o `AUTO_PROMPT` e o script
`generate_true_coathanger_jonatha.py`. O loft daquele script interpola **só a primeira e a última
seção** (as seções intermediárias do `slot2D` não entram no loft sem `throughAll=True` com
arestas compatíveis), de modo que o modelo aprovado e o texto que o descreve divergem. A boa
notícia: o funil linear em V **também** distribui por toda a largura (a largura nunca afunila), o
que é coerente com a uniformidade alta alegada — mas o projeto não pode alegar "cabide" enquanto o
sólido é um cone. Escolha: (a) admitir no SSOT "funil cônico linear com largura constante";
(b) refazer de fato o coat-hanger com `loft(throughAll=True)` e re-medir ΔP e uniformidade.

**7.2 As duas metades não são espelhos.** O volume do canal acima e abaixo de Y=0 difere
**|A-B| = 199,22 mm³ (0,093 % do canal)** (0,093 % do volume do canal), herança do loft do v27.0. Se a manta apresentar
diferença entre as faces superior e inferior, este é o suspeito número um — antes de culpar o
termopar ou o polímero.

---

## 8. Reologia: o que a v28.0 muda e o que continua em aberto

* Com o land paralelo indo de 8,50 para 9,20 mm, a estimativa 1D sobre a geometria medida sobe de
  41,9 para **43,9 bar** (o ΔP do land é proporcional ao seu comprimento). Continua sendo
  **~35 % menor que os 68,2 bar do relatório de CFD** — a direção do erro é a mesma desde a
  triagem: os números de CFD do projeto não são reproduzíveis a partir do repositório.
* A tensão de cisalhamento na parede **não mudou e não mudaria**: **163,8 kPa (γ̇_ap = 911 s⁻¹)**,
  porque a fenda e a vazão são as mesmas. Qualquer material que afirme queda de τ por causa do
  novo chanfro deve ser corrigido.
* Antes de usar "99,10 % de uniformidade" como critério de aceite, é preciso publicar a definição
  (σ/U do perfil de velocidade medido em que plano) e a planilha. Sem isso, não é especificação.
* A matriz nova **exige CFD novo** só se a opção coat-hanger (7.1b) for adotada; para a v28.0 como
  está, a variação de land (0,70 mm) cabe na incerteza do método 1D.

---

## 9. O que eu preciso da sua decisão (3 itens, na ordem)

| # | Decisão | Consequência se aprovar | Consequência se não decidir |
| :-: | :--- | :--- | :--- |
| **D1** | Aprovar **monobloco + EDM** (recomendado) **ou** aro de retração **ou** grampos no BC Ø150 | libera corte do aço | a matriz de 30-56 kN vai abrir no plano de partição na primeira subida de vazão |
| **D2** | Manter chanfro **0,80 × 45°** (land 9,20) ou voltar a 1,50 × 45° (land 8,50) | lâmina de 1,45 mm não lasca na limpeza | risco de lascamento no lábio e face de saída irreparável |
| **D3** | Aceitar a descrição "**funil cônico linear de largura constante**" ou pedir o coat-hanger de verdade | SSOT e CAD voltam a dizer a mesma coisa | qualquer CFD futuro vai divergir do CAD por 0,70-6,00 mm de seção |

Aprovados D1-D3, eu: atualizo o SSOT promovendo a v28.0 para oficial, renumero o `AUTO_PROMPT`
com os valores novos e entrego o `MatrizJonatha_v28.step` como `MatrizJonatha.step` com o v27.0
arquivado em `02_CAD_Modelos_Historicos/MatrizJonatha_v27.0_Aprovado/` (cópia, sem tocar em nada
histórico existente).

---

*Gerado por `gerar_relatorio_v28.py` a partir de `matriz_v28_features.json` e `verificacao_v28.json`.
Todas as grandezas desta página foram medidas nos arquivos STEP desta pasta; nenhuma foi copiada
de relatório anterior.*
