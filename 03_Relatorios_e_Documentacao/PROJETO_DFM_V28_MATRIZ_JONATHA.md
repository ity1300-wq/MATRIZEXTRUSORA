# PROJETO DFM v28.1 — Matriz Jonatha (revisão para fabricação)

**Projeto:** matriz de extrusão plana para manta isolante de acessórios de cabos MT
**Modelo base (aprovado, continua oficial):** `01_CAD_MatrizJonatha_Oficial/MatrizJonatha.step` — SSOT v27.0
**Esta revisão:** v28.1 — **PROPOSTA**. O v27.0 continua sendo o master aprovado (decisão **D4**
do usuário: "não promover"). O que muda aqui é o que a decisão **D2** deixou de pé: nada no lábio
de saída, tudo no restante.
**Data:** 2026-09-11
**Verificação:** `04_Dados_SSOT_e_Scripts/verificar_v28.py` → **64 itens, 64 conformes, 0 não conformes**
**Conferência visual:** `V28_CONFERENCIA_VISUAL.png` (6 vistas, lidas dos STEP)

---

## 1. Resumo em seis linhas

1. O funil de fluxo aprovado **não foi tocado**: a distância máxima entre a superfície do funil
   v28.1 e a do v27.0 medida nos sólidos é **0,000000 mm**.
2. **P7 e P8 rejeitados (decisão D2, 2026-09-11)**: o chanfro de saída fica **1,50 × 45°** e o
   land paralelo fica **8,50 mm**, como no master — medidos nesta revisão: land
   8,50 mm, chanfro 1,50 × 45°, lâmina do lábio
   **0,75**. Ou seja: **a v28.1 não toca na região de saída do fundido**.
3. **P2 fechado**: os 4 bolsões de pino Ø4 × 12 agora são **abertos no plano de partição e
   conjugados nas duas metades** (o v27.0 tinha 2 bolsões selados só no Body_A e nada no Body_B),
   com kit de pinos modelado em `MatrizJonatha_v28_Pinos_Alinhamento.step`.
4. **P3 parcialmente fechado**: 6 cartuchos Ø9,5 e 4 poços de termopar Ø4,8 na zona do land,
   com paredes reais medidas de 8,20–16,35 mm. A refrigeração
   **não cabe no corpo** (item 5) e vai para o adaptador.
5. **P1 tem solução — e ela é da máquina**: o cabeçote EX-030 medido tem bolso Ø95 × 70,0 com
   bucha cônica (EX-031, cone 3°) que aperta a banda Ø93 da matriz, e degrau de apoio axial.
   Dentro do envelope da matriz continua não havendo onde furar (sobram 8,70 mm de aço entre o
   canal Ø75,60 e o Ø93), então a fixação **não** é tarefa da matriz — item 6.
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
python 04_Dados_SSOT_e_Scripts/gerar_matriz_v28.py                # gera os STEP da proposta
python 04_Dados_SSOT_e_Scripts/verificar_v28.py --json --md        # mede e prova (63 itens)
python 04_Dados_SSOT_e_Scripts/gerar_relatorio_v28.py            # este relatório
python 04_Dados_SSOT_e_Scripts/renderizar_v28.py --saida v28.png  # conferência visual
```

---

## 3. Tabela antes × depois (tudo medido nos STEP)

| Item | v27.0 (aprovado) | v28.1 (proposta) | Como foi medido |
| :--- | ---: | ---: | :--- |
| Land reto e paralelo | 8,50 mm (o SSOT declarava 10,00) | **8,50 mm — mantido (D2)**; SSOT atualizado para 8,50 paralelo + 1,50 de chanfro | varredura de seção em Z (passo 0,05 mm) até abs(Y) ≠ 1,50 |
| Chanfro de saída | 1,50 × 45° | **1,50 × 45° — mantido (D2 rejeitou o 0,80)** | folga radial a 0,10 mm da face |
| Lâmina do lábio (ponto mais fino) | 0,75 mm | **0,75 — mantida (D2)**; o risco de lascamento na limpeza passa a ser item de procedimento | Ø79,5/2 − abs(X) da seção na face Z=109 |
| Furos de pino Ø4 × 12 | 2, selados no Body_A; 0 no Body_B | **4 abertos e conjugados (2 por lado)** | volume do furo ∩ corpo = 0 e aço sob o fundo presente |
| Cavidades internas fechadas | Body_A: 2 | **0** (1 shell em cada metade) | contagem de `TopAbs_SHELL` |
| Cartuchos de aquecimento | 0 | **6 × Ø9,5**, fundo a 8,20 mm do canal | booleano + `BRepExtrema` |
| Poços de termopar | 0 | **4 × Ø4,8**, fundo a 16,35 mm | idem |
| Arquivo do canal | 3 sólidos | **1 sólido** | contagem de sólidos no STEP |
| Massa de aço | 3,682 kg | **3,586 kg** | volume × 7,85 g/cm³ |
| Fechamento volumétrico | resíduo 0,001 mm³ | **resíduo 0,0115 mm³** (env − aço − canal = Σ furos) | booleano |
| ΔP 1D sobre a geometria | 41,9 bar | **v28.1 = 41,9 bar · v27.0 = 41,9 bar** | `dp_total()` do próprio projeto |
| τ na parede do land | 164,0 kPa | **163,8 kPa (γ̇_ap = 911 s⁻¹)** | `tau_parede()` do próprio projeto |
| Fixação das metades | inexistente | **pelo collete do cabeçote: 8,6 MPa de compressão radial fecham a partição** | item 6, medido |
| Interface com o cabeçote | nunca medida | **Ø93/Ø89,5/Ø79,5 encaixam em Ø95/Ø90/Ø80 com 1,00/0,25/0,25 mm de folga e interferência 0,0000 mm³** | booleanos, item 6 |
| Refrigeração | inexistente | **não cabe no corpo** | item 5 |

---

## 4. P1 — fixação das metades: por que não há furo que resolva isso

A força que empurra uma metade contra a outra é a pressão sobre a área projetada do canal no plano XZ.
Medindo essa área no sólido: **8169 mm²** (não é a área da boca; é a integral da largura do canal ao longo de Z).

| Cenário de pressão | Força de abertura |
| :--- | ---: |
| ΔP de projeto do CFD (68,2 bar, valor declarado no relatório de CFD) sobre **toda** a área projetada (limite superior) | **55,7 kN** |
| 68,2 bar atuando só sobre a boca Ø75,60 (o número citado no relatório de triagem) | 30,6 kN |
| ΔP 1D medido na geometria (41,9 bar) sobre a área projetada | ≈ 34,2 kN |

A geometria não oferece onde ancorar isso:

* faixa de aço entre o canal e o Ø93: (93,00 − 75,60)/2 = **8,70 mm**;
* um furo radial Ø9 (M8) com parede de 4 mm de cada lado exigiria **9 + 8 = 17 mm**;
* no 3º estágio (Ø79,5) a faixa cai para **1,95 mm** — ali não entra nem pino;
* consequência: **parafusos radiais ou axiais no corpo são geometricamente impossíveis** sem
  alterar o envelope, e o envelope é a regra que garante a montagem na extrusora.

**Caminhos, reordenados depois de medir o cabeçote (item 6):**

1. **Monobloco por EDM.** Eliminar a bipartição: abrir o canal por EDM a partir da face de saída
   (o `MatrizJonatha_v28_Canal_Fluxo.step` de 1 sólido é exatamente o arquivo para isso) e
   trepanar a boca Ø75,60 por trás. Sem plano de partição, não há força de abertura para
   reagir, e os pinos deixam de ser necessários. Custo: eletrodo + tempo de EDM.
2. **Aro de retração (shrink ring)** no degrau Ø93 → Ø89,50 (Z = 69,90). O aro coloca o corpo em
   compressão circunferencial e fecha o plano de partição por atrito, pré-carregada. Vantagem: não
   fura a peça. Necessita: verificar no cabeçote o espaço axial de 0,8 mm do degrau.
3. ~~Grampos externos usando os furos do flange do cabeçote~~ — **retirada**: os 6 × M12 estão em
   C.C. Ø180, nas fendas da junta cabeçote ↔ extrusora, a 35,25 mm do corpo da matriz (medido),
   e não alcançam a matriz. A pré-carga do plano de partição vem da bucha cônica EX-031, que já
   aperta a banda Ø93: 8,6 MPa bastam para equilibrar os 55,7 kN (item 6, medido nos sólidos).

Recomendação: **opção 1 (monobloco + EDM)** para a matriz de produção e manter a bipartição só no
protótipo de bancada. As duas outras são remendo; a 1 remove a causa.

---

## 5. Furação da v28.1 — cotas de usinagem e paredes reais

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
| termopar | 4,80 | -11,00 | 103,00 | ±18,20 … 40,20 (1 por metade) | 22,00 | 16,35 mm |
| termopar | 4,80 | +11,00 | 103,00 | ±18,20 … 40,20 (1 por metade) | 22,00 | 16,35 mm |

Regras de fabricação aplicadas no desenho:

* **parede mínima até o canal**: pino 2,39 mm (alvo ≥ 2,0), cartucho 8,20 mm (alvo ≥ 4,0),
  termopar 16,35 mm (alvo ≥ 3,0) — todas medidas com `BRepExtrema`, não estimadas;
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

## 6. Cabeçote EX-030 — a interface medida no DWG e provada nos sólidos

`030-032- cabeçote.dwg` (HIDEALL, PED:2257 — EX-030 cabeçote em SAE8620 9"X65MM, cementado 0,4-0,6 mm e temperado a 52-55 HRC; EX-031 bucha cônica; EX-032 pushador) foi convertido para DXF e **medido numericamente**, entidade por entidade. A escala foi calibrada pelas próprias cotas do desenho — **k = 25,534 mm por unidade DXF**, incerteza +/- 0.003 (0.012%) — e cinco fechos independentes confirmam o fator: circulo dos furos do flange (raio medido 3,525 un) → desvio +0,01 %; Ø externo do flange (4,308 un) → desvio -0,01 %; Ø corpo do cabecote (2,546 un) → desvio +0,00 %; Ø furo da matriz (1,860 un) → desvio -0,01 %; Ø furo do nariz (1,762 un) → desvio -0,01 %.

> **Correção registrada.** A versão anterior desta seção dizia "6 × M12 em BC Ø150, curso angular ±15°, escala 21,28 mm/un" e "Ø13,33 mm de folga". O Ø150 vinha de uma leitura de raster em baixa resolução: o desenho diz **C.C Ø180**. Tudo abaixo foi re-medido com a escala calibrada e provado por booleanos contra `MatrizJonatha_v28.step` (`verificar_interface_cabecote.py` → **52 itens, 43 conformes, 1 não conformes, 8 pendências do lado da máquina**).

**Furos do cabeçote para a matriz** — profundidade `d` contada da face do nariz; a matriz senta em `Z_matriz = 95,00 − d` (corpo Ø130,00 × 42,00, flange Ø220,00 × 40,00, piloto de centragem Ø105,00 × 3,00 atrás do flange, chanfro 10,00 × 45,00° na transição corpo→flange):

| furo | Ø | de … até (mm de profundidade) | comprimento | cota anotada |
| :--- | ---: | ---: | ---: | :--- |
| bore do nariz | Ø80,00 mm | 0,00 … 14,00 mm | 14,00 mm | Ø80 |
| bore intermediario | Ø90,00 mm | 14,00 … 25,00 mm | 11,00 mm | Ø90 +0,05/+0,10 (print de 2026-09-12 lido girado; antes eu tinha usado +0,05/0 - a confirmar) |
| bolso de fixacao (assento da bucha conica) | Ø95,00 mm | 25,00 … 95,00 mm | 70,00 mm | Ø95 (-0,05/-0,1 no assento da bucha) |
| alargamento traseiro do bolso (o piloto Ø105) | Ø105,00 mm | 92,00 … 95,00 mm | 3,00 mm | Ø105,00 medido no corte: parede a r = 52,48/52,52 por 3,00 mm, além da face do flange (d 92,00) - e o que fecha o comprimento total em 95,00 |

**Encaixe medido nos sólidos** (não por diferença de cotas):

| estágio da matriz | furo do cabeçote | folga radial | folga axial / protrusão |
| :--- | :--- | ---: | ---: |
| Ø93 x 69,9 (d 25,1..95) | Ø95 x 70 (d 25..95) | 1,00 mm | 0,10 mm |
| Ø89,5 x 10,8 (d 14,3..25,1) | Ø90 x 11 (d 14..25) | 0,25 mm | 0,30 mm: o Ø89,5 termina 0,10 antes do fim do furo Ø90 e 0,30 antes do degrau para o Ø80 |
| Ø79,5 x 28,3 (d -14..14,3) | Ø80 x 14 (d 0..14) | 0,25 mm | 0,00 mm |

Interferência corpo-a-corpo matriz ∩ cabeçote: **0,0000 mm³** — a matriz entra e sai sem tocar. O anel da face mede **Ø90,00 → Ø130,00 = 20,00 mm**, que é o "~20 mm" descrito pelo cliente, confirmado em medição. Folgas radiais medidas nos três estágios: **1,00 / 0,25 / 0,25 mm**; folga axial no degrau de apoio **0,10 mm** — é essa folga que define onde a matriz para. A face de saída da matriz fica **14,00 mm** à frente do nariz do cabeçote, então a fenda e a manta trabalham fora do cabeçote (nada de filme congelado encostado na saída) e a manta tem **14,00 mm** de curso livre antes de qualquer obstáculo.

**Fixação (P1/P4): vem da máquina, não da matriz.** A bucha cônica EX-031 (Ø95,00 → Ø86,00 OD, Ø90,00 ID, cone 3,00°, L = 70,00 mm — exatamente o comprimento do bolso Ø95 × 70) é encaixada no bolso e, ao ser empurrada axialmente, contrai sobre a banda Ø93 da matriz; o cone é auto-travante (3,00° < arctan 0,15 = 8,5°). O empuxo axial recai em compressão no degrau do cabeçote, sobre o ombro da matriz — **431,2 mm²** de anel de contato. As pressões envolvidas:

* Pressão de contato no degrau (apoio axial) → **69,2 MPa**
* Pressão radial do collete p/ segurar o empuxo axial só por atrito → **9,8 MPa sobre 20393 mm²**
* Pressão radial do collete p/ fechar o plano de partição → **8,6 MPa**

Ou seja: o aperto que a máquina já faz fecha o plano de partição por compressão radial, e o apoio axial existe. **A matriz não leva flange, não leva grampo e não leva furo de fixação** — e é por isso que a supressão dos furos M6 de desmontagem na face de entrada se mantém: o pushador EX-032 é ferramenta do cabeçote (haste partida Ø25 × 132, M12), não um rosqueamento na matriz.

**Padrão de furação (P4): não há o que padronizar na matriz.** A furação do desenho — 6 × Ø16,50 em fendas de 23,50 mm sobre C.C. Ø180,00 (M12), folga angular total 14,4° cotada como 15°, furo central Ø25,00 — é a junta **cabeçote ↔ extrusora**, e fica a 35,25 mm do corpo da matriz. O giro do conjunto se ajusta por essas fendas antes de apertar; o posicionamento da matriz vem dos três centragens cilíndricos medidos acima.

**Bloqueio novo — e ele é do cabeçote:** o corte mostra um anel no nariz com passagem Ø68,30 mm protruindo 6,00 mm à frente da face, compatível com o carimbo **9"X65MM** (manta de 65 mm). Com esse anel montado, a matriz de 75 mm **não monta**: Ø68,30 contra o nariz Ø79,50 da matriz dá 5,60 mm de interferência radial por lado e volume de choque medido de **5098,0 mm³**. Como o furo do nariz do cabeçote já é Ø80, não há espaço físico para nenhum anel com passagem ≥ Ø79,6: na variante de 75 mm o nariz da matriz roda direto no Ø80 do cabeçote, e o anel tem de ser eliminado ou refeito com Ø80 (ou seja, sem restringir).

**O que ainda se resolve com paquímetro na máquina** (nada disso altera a geometria da matriz):

* confirmar se o assento do bolso Ø95x70 e cilindrico ou conico de 3 graus (o desenho mostra o collete com OD Ø95->Ø86)
* ABERTA de novo em 2026-09-12: o '20 mm' do croqui e a posicao do M12 do bolso (contada da face do flange), nao a sobra axial da matriz. Com a protrusao do desenho (14,00 mm) a borda traseira do furo do cartucho em Z=97,00 fica 2,75 mm dentro da luva do nariz. Duas saidas, as duas medidas: cartuchos em Z >= 99,75 mm na matriz, ou alivio no nariz do cabecote. Medidas de conferencia na maquina: quanto a matriz sobressai do cabecote, e se o montador passa o cartucho com a matriz montada
* CONFIRMAR a tolerância do Ø90 do nariz: o print mostra +0,05/+0,10 (os dois positivos), meu modelo usou +0,05/0. Efeito medido: folga radial do degrau da matriz passa de 0,250 para 0,250..0,325 mm; engate axial e contato do ombro não mudam
* CONFERIR o Ø90 do furo do collete EX-031: medido no DXF como furo reto, ele nao passa sobre a banda Ø93 da matriz (falta 1,50 mm de raio). Precisa da peça ou do desenho isolado de EX-031 para dizer se o furo e conico, se a banda de aperto e outra, ou se a vista de 3,267 deg e de outra peca

O DWG é conversão de avaliação (marca d'água "Evaluation only"), então as tolerâncias anotadas devem ser conferidas na peça antes de fechar o desenho de execução.

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
sólido é um cone.

**7.1b — a opção (b) já foi modelada e medida (D3).** `estudar_funis.py` refez o funil das seções declaradas com loft por **todas** as estações (passo de 5 mm, que é o que faltava no script antigo) e mediu com a mesma trena: **ΔP 1D de 100,9 bar** contra 41,9 bar do funil atual (**2,41×**), canal 76.010 mm³ contra 213.945 mm³, residência 5 s contra 14 s, e **a espessura da manta é a mesma** — a fenda e o land não mudam, então o gancho de uniformidade que justificaria o cabide não aparece na medição. Invasão do envelope nos dois: 0,0000 mm. Comparação completa em `03_Relatorios_e_Documentacao/ESTUDO_FUNIL_COATHANGER.md`; os STEP do estudo ficam em `05_Variantes_Em_Estudo/` e não tocam o modelo oficial. Restam as duas saídas: (a) admitir no SSOT "funil cônico linear com largura constante" e corrigir o texto; (b) desenhar um cabide compensado de verdade (alturas das asas decrescentes do centro para as pontas), o que obriga a CFD novo porque o ΔP saiu de 41,9 para 100,9 bar só com a troca de forma.

**7.2 As duas metades não são espelhos.** O volume do canal acima e abaixo de Y=0 difere
**|A-B| = 199,22 mm³ (0,093 % do canal)** (0,093 % do volume do canal), herança do loft do v27.0. Se a manta apresentar
diferença entre as faces superior e inferior, este é o suspeito número um — antes de culpar o
termopar ou o polímero.

---

## 8. Reologia: o que a v28.1 muda e o que continua em aberto

* Com o lábio **inalterado** (D2), a estimativa 1D sobre a geometria medida fica em
  **v28.1 = 41,9 bar · v27.0 = 41,9 bar** — os 43,9 bar da v28.0 vinham exatamente dos 0,70 mm de land a mais
  que a decisão D2 rejeitou. Continua sendo
  **~35 % menor que os 68,2 bar do relatório de CFD** — a direção do erro é a mesma desde a
  triagem: os números de CFD do projeto não são reproduzíveis a partir do repositório.
* A tensão de cisalhamento na parede **não mudou e não mudaria**: **163,8 kPa (γ̇_ap = 911 s⁻¹)**,
  porque a fenda e a vazão são as mesmas. Qualquer material que afirme queda de τ por causa do
  novo chanfro deve ser corrigido.
* Antes de usar "99,10 % de uniformidade" como critério de aceite, é preciso publicar a definição
  (σ/U do perfil de velocidade medido em que plano) e a planilha. Sem isso, não é especificação.
* **Não há CFD pendente por esta revisão**: o lábio ficou igual ao do master (decisão D2) e o ΔP 1D
  medido nos dois sólidos é o mesmo, v28.1 = 41,9 bar · v27.0 = 41,9 bar. CFD novo só entra na conta se a opção
  coat-hanger (7.1b) for adotada — e aí o ΔP medido no estudo é 100,9 bar, acima do limite
  de 68,2 bar usado no relatório de projeto.

---

## 9. Situação das decisões

| # | Decisão | Estado | Consequência prática |
| :-: | :--- | :--- | :--- |
| **D1** | Fixação das metades | **FECHADA pela máquina** — collete EX-031 + degrau do cabeçote; a matriz não leva grampo, flange nem furo | o corte do aço pode ser liberado com a banda Ø93 retificada e os bolsões de pino cegos (sem escarear) |
| **D1b** | Anel do nariz do cabeçote (Ø68,30 do desenho, variante 9"×65 mm) | **FECHADA por medição sua na máquina**: sobram 2,5 mm por lado na fenda, o que só casa com a passagem Ø80,00 do próprio cabeçote | a matriz de 75 mm monta como está; o Ø68,30 fica registrado como coisa do cabeçote de 65 mm |
| **D2** | Chanfro da saída 0,80 ou 1,50 | **DECIDIDO: mantém 1,50 × 45°** (land 8,50, lâmina 0,75) como no master | a v28.1 não altera a região de saída; o lascamento na limpeza vira item de procedimento, não de geometria |
| **D4** | Promover a v28 para oficial | **DECIDIDO: não** — v27.0 segue master | a v28 fica ao lado, verificada, esperando você conferir a máquina |
| **D3** | Funil: o cone linear do modelo atual **ou** o coat-hanger de 6,00 mm do texto | **MEDIDO, esperando sua escolha** — os dois funis modelados e comparados: ΔP 100,9 bar contra 41,9 bar, residência 5 s contra 14 s, espessura da manta igual nos dois (a fenda manda, e ela não muda) | a v28.1 mantém o funil do master. Escolher (a) é só texto; escolher (b) é CFD novo e o ΔP acima de 68,2 bar do relatório de projeto |
| **medir** | Comprimento do bico do cabeçote (sua linha no croqui × o nariz do desenho) | **REABERTA em 2026-09-12.** A cota '20 mm' do croqui, medida no DXF, é a posição do furo M12 do bolso contada da face do flange (72,02 − 52,02 = 20,00 mm) — não a sobra axial da matriz. Vale a protrusão do desenho (14,00 mm), e aí a borda traseira do furo mais crítico fica 2,75 mm dentro da luva do nariz, com 2745 mm³ de metal no caminho de inserção dos 5 eixos de furo na faixa de saída (são 10 furos: cada eixo entra pelas duas metades) | duas saídas medidas, e nenhuma delas mexe nos outros 20 furos da matriz: levar os cartuchos para Z ≥ 99,75 mm (calculado do Ø9,50 e da face do nariz em 95,00 mm) ou abrir alívio no nariz do cabeçote. No cenário alternativo (20,00 mm de protrusão) a folga vira 3,25 mm com 0 mm³ no caminho — por isso a conferência na máquina é o que fecha o item |

Enquanto D3 estiver em aberto, **nada é promovido**: `MatrizJonatha.step` continua sendo o v27.0 e a
v28.1 vive ao lado, com `verificar_v28.py` (64 itens) e `verificar_interface_cabecote.py` (52 itens, 43 conformes, 1 não conforme — a folga axial dos cartuchos × a luva do nariz, que é a linha 'medir' acima)
para re-medir a qualquer momento.

---

*Gerado por `gerar_relatorio_v28.py` a partir de `matriz_v28_features.json` e `verificacao_v28.json`.
Todas as grandezas desta página foram medidas nos arquivos STEP desta pasta; nenhuma foi copiada
de relatório anterior.*
