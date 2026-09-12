# TRIAGEM DAS MATRIZES — O QUE É PROBLEMA REAL E O QUE NÃO É

**Projeto:** Matrizes de extrusão plana de manta isolante MT — Matriz 1 (Copo), Matriz 2 (Gedeon), Matriz Desenvolvimento e Matriz Jonatha v27 (oficial)
**Data:** 11 de setembro de 2026
**Método:** medição direta das seções e volumes dentro dos arquivos STEP — não a leitura dos relatórios. Cada afirmação abaixo traz a medida e o arquivo de origem. Scripts: `04_Dados_SSOT_e_Scripts/verify_geometry_ssot.py` (matriz oficial) e `verify_legacy_dies.py` (as quatro matrizes).

> **Resumo em uma frase:** os problemas reais da Matriz Jonatha são de **fabricação** (fixação, pinos e controle térmico inexistentes) e de **entrega** (um arquivo de canal errado e números de CFD não reproduzíveis); a geometria do canal aprovado — envelope, funil, land e fenda — **está correta e é melhor que a da Matriz 2 de fato**, o que ficou comprovado por medição.

---

## 1. O que cada matriz realmente é (medido nos STEP)

| | **Matriz 1 — Copo** | **Matriz 2 — Gedeon** | **Matriz Desenvolvimento** | **Matriz Jonatha v27** |
| :--- | :--- | :--- | :--- | :--- |
| Comprimento / envelope | Ø93 × 80,70 mm (só 2 estágios) | Ø93 × 69,9 + Ø89,5 × 10,8 + Ø79,5 × 28,3 = 109 mm | idem Matriz 2 | idem Matriz 2 |
| Entrada (Z=0) | disco Ø75,60 | disco Ø75,57 que já em Z=1 tem 75,0 × 72,1 | retângulo 75,0 × 40,0 | disco Ø75,60 |
| Funil de distribuição | **não existe** (degrau de 90°) | **21,0 mm** (de 74 mm para 1,5 mm) | 99,0 mm linear | 99,0 mm linear |
| Land (fenda 75 × 1,5) | 9,95 mm | **88,00 mm** | 10,00 mm | 10,00 mm (8,50 paralelos + 1,50 de chanfro) |
| Canal de polímero (real) | 318.480 mm³ | 43.018 mm³ | 155.370 mm³ | 213.945 mm³ |
| Arquivo "Canal_Fluxo" × corpo | ✅ confere | ❌ **4,96× maior** | ✅ confere | ✅ confere |
| Pinos de alinhamento | (não tem) | Ø1,78 × 10 mm atravessando as duas metades | — | 2 furos Ø4 × 12, só no `Body_A`, **selados** |
| ΔP por lei das potências (1D, medido) | 23,8 bar | **194,2 bar** | 31,3 bar | **26,6 bar** |
| ΔP declarado no relatório | 185,4 bar | 268,7 bar | — | 68,2 bar |
| Razão medido/declarado | 0,13× ❌ | 0,72× | — | 0,39× ❌ |

Cálculo próprio: lei das potências com **K = 18.500 Pa·s^n, n = 0,32, Q = 15 cm³/s** (os mesmos parâmetros do SSOT), integrada sobre a geometria medida. É um modelo 1D de escoamento desenvolvido: válido para comparar matrizes e checar ordem de grandeza, **não** substitui CFD.

> **Correção de 11/09/2026** — a fórmula da fenda larga usada na primeira versão desta tabela tinha um fator extra `(1+n)/n`, que inflava o ΔP em `((1+n)/n)^n = 1,573×`. Valores antigos (37,1 / 305,5 / 49,3 / 41,9 bar) foram substituídos pelos corretos (23,8 / 194,2 / 31,3 / 26,6 bar). O fator de correção foi verificado contra o CFD 2D da seção do land da Jonatha: **2,1761 bar/mm** medidos no CFD contra **2,19 bar/mm** na fórmula — 0,6%. A razão medido/declarado da Jonatha passa de 0,61× para 0,39×, ou seja, o ΔP do canal é **ainda menor** do que se supunha, e a folga da extrusora é maior.

---

## 2. 🔴 PROBLEMAS REAIS

### P1 — A Matriz Jonatha não tem nenhum meio de fixação · **BLOQUEADOR DE FABRICAÇÃO**

**Medido:** 0 furos de fixação/aperto no `Body_A` e no `Body_B` (os únicos furos usinados são os de pino).

**Por que é problema:** com 68,2 bar dentro do canal, a força que empurra as duas metades uma contra a outra é da ordem de **30 kN (≈3,1 tf)** — pressão de 6,82 MPa × área projetada da cavidade no plano de partição (≈4.489 mm², a seção da entrada). Sem parafusos ou grampos, a matriz **abre no plano Y=0** durante o trabalho: sai rebarba no meio da manta, vaza polímero e a espessura de 1,50 mm perde controle.

**Restrição geométrica (medida):** entre a parede do canal e a superfície externa sobram só **1,9 mm** de aço na região do pino e ~2,2 mm perto do land; o 3º estágio é Ø79,5. Por isso **não há espaço para parafusos axiais** atravessando o corpo: a fixação M8 tem de ser radial (em Y), nas asas do Ø93, com rebaixo (spot face) na superfície cilíndrica — ou por grampos/quadro externo.

---

### P2 — Os pinos de alinhamento não existem de verdade · **BLOQUEADOR DE MONTAGEM**

**Medido no `MatrizJonatha_Body_A.step`:** o sólido tem **3 shells** (1 externo + 2 cavidades internas). Cada "furo" Ø4 × 12 é formado por **duas tampas planas de 12,566 mm²** (em Y = 0 e Y = −12) mais uma face cilíndrica de 150,796 mm² — ou seja, é uma **bolha fechada dentro do aço**, invisível em qualquer visualizador e impossível de usinar.

**E o `Body_B` tem 1 shell: nenhum furo.**

**Impacto:** as metades não têm referência de alinhamento. O plano de partição pode deslocar lateralmente e criar degrau/rebarba no meio da manta justamente na espessura mais crítica (1,5 mm).

**Comparação com a Matriz 2:** nela o pino atravessa as duas metades — sólido medido de 24,88 mm³ = **Ø1,78 × 10 mm** em X = ±41,50, Z = 54,50 a 64,50. Ou seja, a Jonatha **regrediu** exatamente no item que a Matriz 2 acertava.

**Ação:** refazer os furos nos dois corpos, com a mesma referência (X = ±41,50, Z = 54,50), Ø4 H7 × 12 mm cegos em cada metade, e usar 2 pinos Ø4 × 20 mm temperados.

---

### P3 — Sem controle térmico · **RISCO DE REPETIR O DEFEITO QUE ORIGINOU O PROJETO**

**Medido:** 0 furos para cartucho de resistência Ø9,5; 0 poço de termopar; 0 canais de refrigeração.

**Por que é problema:** os próprios relatórios do projeto dizem que o rasgo de borda (*edge tearing*) aparece quando a matriz esquenta — porque a resistência do fundido cai. Sem controle térmico, a matriz acompanha passivamente a temperatura do canhão e a janela de 50–65 °C não fica garantida ao longo do turno.

**Ação:** acrescentar no CAD **antes** da têmpera/nitretação. Depois disso, furar aço a 52 HRC é caro e arriscado.

---

### P4 — Sem padrão de acoplamento na face Z=0 · **DEPENDE DE DADO EXTERNO**

**Medido:** nenhum furo na face traseira; o assentamento é apenas o encaixe Ø75,60.

**Ação:** extrair o padrão de furos do cabeçote original (`030-032- cabeçote.dwg`) ou medir o flange na máquina. Sem esse dado, qualquer flange projetado é palpite.

---

### P5 — O arquivo `MatrizGedeon_Canal_Fluxo.step` está errado · **RISCO DE ENGENHARIA / EDM**

**Medido:** o arquivo tem **213.790,03 mm³**, mas o vazio real da Matriz 2 é **43.017,90 mm³** (medido dentro da própria montagem `MatrizGedeon.step`) — **4,96 vezes menor**. E o pior: as seções do arquivo são **idênticas às da Matriz Jonatha** (boca Ø75,6, funil que chega na fenda em Z = 99). O arquivo descreve outro canal, não o da Matriz 2.

**Impacto:** qualquer CFD, eletrodo de EDM ou análise feita sobre esse arquivo não representa a Matriz 2. Se alguém comparar "antes × depois" usando esse arquivo, os dois canais ficam iguais e a melhoria desaparece da análise.

**Ação:** reexportar o canal da Matriz 2 a partir do sólido real da montagem (o script `verify_legacy_dies.py` já o identifica automaticamente) ou marcar o arquivo como inválido no repositório.

---

### P6 — Os números de CFD não são reproduzíveis · **RISCO DE DECISÃO**

Recalculado com os **mesmos parâmetros reológicos do SSOT** sobre a geometria medida:

| Alegação | Medição independente | Veredito |
| :--- | :--- | :--- |
| Matriz 2: ΔP = 268,7 bar | 194,2 bar | ⚠️ mesma ordem (0,72×), mas o declarado é 38% maior |
| Jonatha: ΔP = 68,2 bar | 26,6 bar | ❌ 0,39×: o declarado é 2,6× o medido |
| Matriz 1: ΔP = 185,4 bar | 23,8 bar | ❌ 0,13× — o 1D não captura a contração de 90°, que é o defeito real dela; esse número não sai do método declarado |
| τ na parede: Gedeon 157,11 kPa → Jonatha 128,44 kPa | **164,0 kPa nas duas** (γ̇ = 915 s⁻¹) | ❌ impossível: o land é o **mesmo** (75 × 1,5) e a vazão é a **mesma** — a tensão de cisalhamento na parede não pode diferir entre as duas |
| Uniformidade 99,10% / 68,96% / 54,73% | — | ⚠️ não auditável: não existe definição (variação de quê, medida onde) nem planilha no repositório |

**O que é verdade na física:** a direção do ganho é correta e comprovável. A Matriz 2 comprime o fluxo de 74 mm para 1,5 mm em 21 mm (funil quase cego) e depois o mantém 88 mm num land fino; a Jonatha faz a mesma compressão em 99 mm e mantém apenas 8,5 mm de land. Como a perda de carga no land é proporcional ao comprimento, a diferença medida (194,2 → 26,6 bar) é explicada por geometria, não por narrativa.

**Ação:** refazer os números em script versionado (ou rotular os atuais como "estimativa a confirmar"). O número de 99,10% precisa de definição explícita antes de ser usado como critério de aceitação.

---

### P7 — Lábio de saída com 0,75 mm de aço · **RISCO DE ROBUSTEZ (decisão de engenharia)**

**Medido:** no plano Z = 109 a face é um anel Ø79,5 cuja abertura já é 78,0 × 4,5 (o chanfro de 1,5 × 45°). Sobram **0,75 mm de aço** de cada lado.

**Não é problema de escoamento** (nessa região a pressão já caiu para a atmosfera), mas é uma lâmina frágil: risco de lascar na limpeza ou no transporte, e impossível de refacear plana depois.

**Ação sugerida:** chanfro de **0,8 mm × 45°** → lábio de ≈1,45 mm e land paralelo subindo de 8,50 para ≈9,20 mm (as duas coisas boas ao mesmo tempo).

---

### P8 — Documentação: o land não tem 10 mm paralelos · **CORREÇÃO DE SSOT**

**Medido:** o chanfro ocupa Z = 107,50 a 109,00; logo o **land reto e paralelo é 8,50 mm**, e não os 10,00 mm que constam no SSOT. Em escoamento isso vale ≈6 bar (≈9%) — não muda a aprovação —, mas quebra a rastreabilidade: qualquer verificação futura vai acusar divergência.

**Ação:** corrigir o SSOT para "8,50 mm paralelos + 1,50 mm de chanfro" (ou reduzir o chanfro conforme P7).

---

## 3. 🟢 O QUE NÃO É PROBLEMA (verificado e aprovado)

| # | Item | Evidência da medição |
| :--: | :--- | :--- |
| **N1** | Envelope externo escalonado (Ø93 × 69,90 / Ø89,50 × 10,80 / Ø79,50 × 28,30; Z = 109,000) | Medido na Jonatha **e** na Matriz 2: são iguais. A compatibilidade de montagem na máquina está comprovada. |
| **N2** | Fenda 75,00 × 1,50 com bordas semicirculares R0,75 | Área medida 112,017 mm² — exatamente o valor analítico `(75 − 1,5) × 1,5 + π × 0,75²`. O arquivo é fiel à especificação. |
| **N3** | Desenho do canal da Jonatha (nada de arestas frágeis ou paredes de espessura zero na entrada) | Varredura seção a seção: a boca Ø75,60 é o **envelope máximo** do canal e todas as seções seguintes ficam dentro dela — o aço em volta é contínuo. |
| **N4** | Bipartição em Y = 0 | Interferência 0,000 mm³; `aço + canal + furos` fecham o envelope com **0,001 mm³** de resíduo. |
| **N5** | Volumes e massa | Body_A 234.255,29 mm³, Body_B 234.746,37 mm³, canal 213.945,15 mm³ → **3,682 kg** de aço. Bate com o SSOT na casa dos milésimos. |
| **N6** | Consistência dos arquivos entregues | Matriz 1, Matriz Desenvolvimento e Matriz Jonatha têm o "canal isolado" igual ao vazio do corpo. **Só** o da Matriz 2 está errado (P5). |
| **N7** | A Matriz 1 não perdia carga por atrito | O trecho reto Ø75,6 mais os ~10 mm de fenda dão ≈24 bar em 1D — praticamente o mesmo da Jonatha (26,6 bar). O defeito dela é o **degrau de 90°** (parede cega que rasga o fundido), e não "185,4 bar de contrapressão". A troca da matriz continua certa; o motivo apontado nos relatórios é que estava errado. |
| **N8** | O ganho da Jonatha sobre a Matriz 2 é real | Land medido: **88,0 mm → 8,5 mm**. Perda de carga medida: **194,2 → 26,6 bar**. A redução declarada (268,7 → 68,2 bar) é **conservadora** em relação à medição — o ganho não é marketing, é geometria. |

---

## 4. 🟡 O QUE PRECISA SER REFAZER (alegações que não se sustentam)

| Alegação nos relatórios | O que a medição mostra | Ação |
| :--- | :--- | :--- |
| "τ na parede cai de 157,11 para 128,44 kPa" | Seção do land e vazão idênticas ⇒ τ é o mesmo nas duas: **164,0 kPa** | Recalcular; o ganho real está no ΔP, não em τ |
| "Matriz 1: 185,4 bar / 54,73% de uniformidade" | 1D sobre a geometria medida dá **23,8 bar** (o degrau de 90° não é capturado por 1D) | Se o número for necessário, rodar CFD 2D/3D de verdade; senão, marcar como não verificado |
| "Uniformidade de 99,10%" | Sem definição nem planilha no repositório | Publicar a definição (variação de quê, medida em qual plano) e o cálculo |
| "Land: 87,60 → 10,00 mm (−88,6%)" | Medido **88,0 → 10,0 mm** ✅, mas o "10,00" inclui 1,50 mm de chanfro ⇒ paralelos = 8,50 mm | Confirmar o ganho e corrigir o valor do land paralelo (P8) |

---

## 5. Plano de ação priorizado (antes de cortar o aço)

| Prioridade | Ação | Motivo | Observação de custo |
| :--: | :--- | :--- | :--- |
| **1** | Definir e usinar a fixação (M8 radial nas asas com spot face, ou grampos externos) | P1 | barato agora, retrabalho caro depois da têmpera |
| **2** | Refazer os furos de pino nos **dois** corpos e providenciar os pinos | P2 | idem |
| **3** | Furação térmica: cartuchos Ø9,5, termopar, 2 canais de refrigeração Ø8 por metade | P3 | idem |
| **4** | Corrigir os arquivos: reexportar o canal da Matriz 2 e deixar o canal da Jonatha com 1 sólido | P5 | sem custo de usinagem |
| **5** | Decidir chanfro/lábio (0,8 × 45°) e atualizar o SSOT (land 8,50 paralelos) | P7 / P8 | decisão de engenharia |
| **6** | Refazer os números reológicos em script versionado e definir "uniformidade" | P6 | ~1 dia de trabalho |
| **7** | Flange de entrada (aguarda DWG do cabeçote ou medição na máquina) | P4 | depende de dado externo |

---

## 6. Como reproduzir esta triagem

```bash
bash 04_Dados_SSOT_e_Scripts/setup_headless_gl.sh
export LD_LIBRARY_PATH="$PWD/04_Dados_SSOT_e_Scripts/.headless_gl:$LD_LIBRARY_PATH"

# 1) Matriz oficial: 34 checagens dimensionais contra o SSOT
python 04_Dados_SSOT_e_Scripts/verify_geometry_ssot.py --json --md

# 2) As quatro matrizes: envelope, entrada, funil, land, consistência dos arquivos e ΔP 1D
python 04_Dados_SSOT_e_Scripts/verify_legacy_dies.py --json
```

Saídas: `04_Dados_SSOT_e_Scripts/auditoria_geometrica.json`, `auditoria_matrizes_historicas.json` e `03_Relatorios_e_Documentacao/AUDITORIA_GEOMETRICA_MATRIZ_JONATHA.md`.

---

*Documento gerado a partir de medições nos arquivos STEP em 11/09/2026. Os valores marcados como ❌ ou ⚠️ devem ser refeitos antes de qualquer decisão de investimento.*
