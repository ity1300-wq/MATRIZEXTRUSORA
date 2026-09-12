# Auditoria Geométrica Automatizada - Matriz Jonatha

**Documento:** Verificação dimensional dos arquivos STEP oficiais contra o SSOT  
**Revisão auditada:** `v27.0_MatrizJonatha_Approved_Master`  
**Script gerador:** `04_Dados_SSOT_e_Scripts/verify_geometry_ssot.py`  
**Data da auditoria:** 2026-09-11  
**Tolerância dimensional:** ±0.02 mm  

---

## 1. Resultado Consolidado

- **Itens verificados:** 36
- **Conformes:** 19
- **Não conformes:** 2
- **Informativos (diagnóstico):** 15

## 2. Verificações Dimensionais

| Item | Nominal | Medido | Desvio | Status |
| :--- | ---: | ---: | ---: | :---: |
| Comprimento total Z | 109.0 mm | 109.0 mm | +0.0 mm | ✅ |
| Diâmetro externo máximo (Estágio 1) | 93.0 mm | 93.0 mm | +0.0 mm | ✅ |
| Ø externo em Z=0.50 (estágio 93.00 x 69.90) | 93.0 mm | 93.0 mm | +0.0 mm | ✅ |
| Ø externo em Z=75.30 (estágio 89.50 x 10.80) | 89.5 mm | 89.5 mm | +0.0 mm | ✅ |
| Ø externo em Z=94.85 (estágio 79.50 x 28.30) | 79.5 mm | 79.5 mm | +0.0 mm | ✅ |
| Diâmetro externo na face traseira Z=0 (Ø93) | 93.0 mm | 93.0 mm | +0.0 mm | ✅ |
| Ø da boca de entrada (acoplamento extrudora) | 75.6 mm | 75.6 mm | +0.0 mm | ✅ |
| Ø da boca de entrada (eixo Y) | 75.6 mm | 75.6 mm | +0.0 mm | ✅ |
| Largura do land (X) | 75.0 mm | 75.0 mm | +0.0 mm | ✅ |
| Espessura do land (Y) | 1.5 mm | 1.5 mm | +0.0 mm | ✅ |
| Área da seção do land (bordas arredondadas R0,75) | 112.0171 mm2 | 112.0171 mm2 | +0.0 mm2 | ✅ |
| Comprimento do land reto e paralelo | 10.0 mm | 8.5 mm | -1.5 mm | ❌ |
| Chanfro de saída 1,50 mm x 45° - sobrelargura radial em X | 1.4 mm | 1.401 mm | +0.001 mm | ✅ |
| Chanfro de saída 1,50 mm x 45° - sobrelargura radial em Y | 1.4 mm | 1.401 mm | +0.001 mm | ✅ |
| Interferência entre Body_A e Body_B | 0.0 mm3 | 0.0 mm3 | +0.0 mm3 | ✅ |
| Volume Body_A | 234255.29 mm3 | 234255.287 mm3 | -0.003 mm3 | ✅ |
| Volume Body_B | 234746.37 mm3 | 234746.369 mm3 | -0.001 mm3 | ✅ |
| Volume do núcleo de polímero (canal) | 213945.15 mm3 | 213945.1459 mm3 | -0.0041 mm3 | ✅ |
| Cavidades internas fechadas no Body_A | 0 cavidade(s) | 2 cavidade(s) | +2 cavidade(s) | ❌ |
| Cavidades internas fechadas no Body_B | 0 cavidade(s) | 0 cavidade(s) | +0 cavidade(s) | ✅ |
| Envelope - (aço + canal + 2 furos de pino) | 0.0 mm3 | 0.0009 mm3 | +0.0009 mm3 | ✅ |

## 3. Diagnósticos e Não Conformidades

| Item | Valor medido | Observação |
| :--- | :--- | :--- |
| Comprimento do land reto e paralelo | 8.5 mm (nominal 10.0) | o chanfro de saída consome 1,50 mm do land |
| Cavidades internas fechadas no Body_A | 2 cavidade(s) (nominal 0) | os furos Ø4 estão SELADOS (bolhas internas, impossíveis de usinar) |
| Sólidos na montagem MatrizJonatha.step | 2 |  |
| Sólidos em MatrizJonatha_Canal_Fluxo.step | 3 | esperado: 1 (núcleo de polímero) |
| Parede de aço no lábio de saída (Z=109, saída Ø79,5) | 0.75 | mm - lábio fino: avaliar fragilidade |
| Parede entre canal e furo de pino Ø4 em Z=54,5 | 1.865 | mm |
| Body_A + Body_B (união é 1 sólido) | True |  |
| Massa estimada de aço (7,85 g/cm3) | 3.682 kg |  |
| Furos de pino Ø4 no Body_A | 2 |  |
| Furos de pino Ø4 no Body_B | 0 | ausentes: os pinos não alinham as duas metades |
| Furos usinados no Body_A (Ø, todos) | [4.0, 4.0] |  |
| Furos usinados no Body_B (Ø, todos) | [] | o Body_B não tem nenhum furo usinado |
| Furos de fixação/aperto (M8 ou abas) | 0 | não existem no modelo |
| Furos para cartucho de resistência Ø9,5 | 0 | não existem no modelo |
| Poço para termopar | 0 | não existem no modelo |
| Canais de refrigeração Ø8,0 | 0 | não existem no modelo |
| Furação do flange de acoplamento (Z=0) | 0 | não existem no modelo |

## 4. Ações Recomendadas Antes da Usinagem CNC

| # | Achado (medido no STEP) | Impacto | Ação recomendada |
| :--: | :--- | :--- | :--- |
| 1 | Pinos: os 2 furos Ø4 × 12 do `Body_A` estão **selados** (cavidades internas fechadas, 3 shells) e o `Body_B` não tem furo nenhum | As metades ficam sem referência de alinhamento: risco de degrau e rebarba no plano de partição | Refazer os furos nos **dois** corpos (Ø4 H7 × 12 mm cegos, X=±41,50, Z=54,50) e usar 2 pinos Ø4 × 20 mm temperados. Reexportar os dois STEP |
| 2 | Land reto e paralelo real = 8,50 mm (SSOT declara 10,00 mm) | Divergência documental; o chanfro de 45° consome 1,50 mm do land | Corrigir o SSOT para 8,50 mm de land paralelo + 1,50 mm de chanfro, **ou** reduzir o chanfro para 0,50 mm × 45° (land = 9,50 mm) |
| 3 | Parede de aço no lábio de saída = 0,75 mm | Lábio frágil: risco de lascamento e rebarba na face de saída Ø79,5 (impossível retificar plana) | Reduzir o chanfro para 0,50–0,80 mm × 45° (lábio ≥ 1,40 mm), mantendo o envelope Ø79,5 intacto |
| 4 | Nenhum furo de fixação/aperto no modelo | As metades não podem ser fechadas contra os 68 bar de contrapressão | Definir padrão de fixação: 4 × M8 em Y nas asas do Ø93 (com spot face) **ou** grampos/quadro externo (verificar espaço: parede de aço de apenas 8,7 mm entre o canal e o Ø93) |
| 5 | Sem controle térmico (cartuchos Ø9,5 / termopar / refrigeração) | Operação fora da janela de 50–65 °C reintroduz o *edge tearing* | Acrescentar furos de cartucho Ø9,5 mm, poço de termopar Ø6 mm e 2 canais de refrigeração Ø8 mm por metade |
| 6 | Sem furação de flange em Z=0 | Acoplamento à extrudora depende só do encaixe Ø75,60 mm | Extrair o padrão de furos do cabeçote original (`030-032- cabeçote.dwg`) antes de definir o flange |
| 7 | `MatrizJonatha_Canal_Fluxo.step` contém 3 sólidos | Dificulta o uso direto como eletrodo de EDM / malha de CFD | Reexportar apenas o núcleo de polímero (1 sólido) |
| 8 | ΔP e τ declarados não são reproduzíveis (τ de 128,44 kPa é impossível: o land é o mesmo e a vazão é a mesma) | Risco de decisão sobre números não auditáveis | Refazer em script versionado; ver `03_Relatorios_e_Documentacao/TRIAGEM_DE_PROBLEMAS_DAS_MATRIZES.md` |

## 5. Conclusão

O envelope externo, a seção do land (75,00 × 1,50 mm com bordas R0,75), a boca de entrada Ø75,60 mm e o fechamento volumétrico do conjunto (aço + canal de polímero + furos de pino = envelope cilíndrico nominal) foram todos confirmados numericamente.

Os itens marcados como **NÃO CONFORME** exigem decisão de engenharia antes da usinagem: ver a seção 3 e o plano de ação em `RELATORIO_TECNICO_E_SUGESTOES.md`.

---

*Relatório gerado automaticamente por `verify_geometry_ssot.py --md`.*


## 6. Tratamento dos achados na proposta v28.1 (2026-09-12)

a auditoria automatizada (PR #1 / issue #1) abriu 8 achados contra a v27.0. Isto é o relato do que foi feito com cada um, com o número medido hoje e onde o número é re-medido a cada rodada do portão (`python 04_Dados_SSOT_e_Scripts/verificar_cadeia.py`). E esta seccao e a auditoria se baseando nas decisoes que tomamos juntos, nao nas que a auditoria presumiu: D1 (fixacao por collete EX-031 + degrau, sem flange e sem furo na matriz), D2 (chanfro de saida 1,50 x 45graus e lamina de 0,75 do master mantidos - a reducao para 0,80 foi rejeitada), D3 (as duas variantes de funil modeladas e comparadas, com o funil do master mantido) e D4 (o v27.0 continua o master; a v28 vive ao lado como proposta).

> nenhum achado foi 'resolvido' editando o master: `01_CAD_MatrizJonatha_Oficial/MatrizJonatha.step` (v27.0) e `02_CAD_Modelos_Historicos/` são intocados (regras 1 e 2 do projeto), e a v28.1 existe em paralelo aguardando sua aprovação explícita para promover

| Achado | Status | Tratamento, com o número medido | Onde conferir |
| :--- | :--- | :--- | :--- |
| **G-01 land reto e paralelo 8,50 vs 10,00 declarado** | RESOLVIDO NO SSOT (modelo mantido) | o SSOT passou a declarar os dois números separados: `land_length_mm` = 10,00 mm de terra total e `land_paralelo_real_mm` / `land_paralelo_mm` = 8,50 mm, com a causa escrita (`land_paralelo_observacao`). A cota de usinagem saiu da discussão de texto: paralelo Z = 99,00 → 107,50 (8,50) e chanfro 1,50 × 45° de Z = 107,50 → 109,00, conferidos item a item no sólido por `verificar_v28.py`. (medido hoje: land paralelo medido 8,50 mm (conforme o SSOT novo)) | 04_Dados_SSOT_e_Scripts/verificacao_v28.json (itens 'Land reto e paralelo' e 'Cotas de usinagem do land') |
| **G-02 lâmina do lábio de saída 0,75 mm** | MANTIDO POR DECISÃO EXPLÍCITA DO USUÁRIO (D2) | as duas variantes foram modeladas e comparadas com números, não com opinião: reduzir o chanfro para 0,80 × 45° daria land 9,20 e lâmina 1,40 mm (`proposta_v28_dfm/o_que_mudou/P7_P8_chanfro_e_land`). O usuário manteve o chanfro do master (1,50 × 45°, lâmina 0,75). O achado não é mais 'risco não tratado': virou instrução de fabricação - `fabricao_v28/tolerancias/chanfro_saida` e `/lamina_labio` exigem 1,50 × 45° (±0,05) **sem rebarba** e registram que o lascamento na limpeza é o preço aceito. (medido hoje: lâmina medida 0,750 mm; sobrelargura do chanfro a 0,10 mm da face 1,402 mm) | 04_Dados_SSOT_e_Scripts/verificacao_v28.json (itens 'Lâmina de aço no lábio' e 'Sobrelargura do chanfro') |
| **G-03 furos de pino selados no Body_A e ausentes no Body_B** | RESOLVIDO NA PROPOSTA v28.1 | os pinos passaram a atravessar as duas metades, como na Gedeon: 4 bolsões em cada lado (X = ±42,10; Z = 30,00 e 60,00), abertos no plano de partição e cegos sob o fundo. Medido em booleano por pino: bolso vazio 0,0000 mm³, aço sob o fundo 12,6 mm³ nas duas metades, parede mínima até o canal 2,391 / 2,392 / 2,482 / 2,483 mm (alvo ≥ 2,00) e interseção com o canal 0,000000 mm³ - nenhum furo comunica com o fluxo. (medido hoje: pinos conjugados 4/4 no Body_A e 4/4 no Body_B) | 04_Dados_SSOT_e_Scripts/verificacao_v28.json (itens 'Pino em ...' e 'Pinos conjugados nas duas metades') |
| **G-04 zero recursos de fabricação (fixação, cartuchos, termopar, refrigeração, flange de entrada)** | PARCIAL POR DECISÃO: o que é do cabeçote saiu medido; refrigeração continua aberta | (a) fixação: a matriz **não** leva flange nem furo de fixação - decisão explícita do usuário; ela é presa pelo collete EX-031 e apoiada no degrau do cabeçote, e as pressões necessárias foram medidas: empuxo axial 29,843 kN, pressão de contato no degrau 69,21 MPa sobre 632,7 mm², pressão radial do collete 8,58 MPa para fechar o plano de partição (força de abertura 55,7 kN) e 9,76 MPa para segurar o empuxo só por atrito. (b) cartuchos e termopar: a furação é do cabeçote EX-030, não da matriz - 6 furos de cartucho e 4 de termopar conferidos um a um, todos abrindo na banda livre e nenhum rompendo o envelope. (c) o preço disso é o acesso axial, que é o único NÃO CONFORME do projeto: folga -2,750 mm, metal no caminho 2.744,550 mm³, o cartucho deixa de esbarrar em Z ≥ 99,75 mm. (d) refrigeração Ø8 por metade: continuamos sem definição - é a única linha do G-04 que não foi tratada. (medido hoje: 52 itens de interface, 43 conformes, 1 não conforme, 8 pendências de máquina) | 04_Dados_SSOT_e_Scripts/interface_cabecote.json e 03_Relatorios_e_Documentacao/INTERFASE_CABECOTE_EX030.md |
| **G-05 MatrizJonatha_Canal_Fluxo.step com 3 sólidos** | RESOLVIDO NA PROPOSTA v28.1 | reexportado como eletrodo/de CFD: `MatrizJonatha_v28_Canal_Fluxo.step` tem 1 sólido só (213.945,1 mm³, medido reimportando o arquivo). O v27.0 continua com os 3 sólidos (canal + 2 furos de pino de 150,8 mm³) porque é o master intocado - a regra 1 não permite 'corrigir' o arquivo aprovado por dentro. (medido hoje: 1 sólido no STEP do canal da v28.1) | 04_Dados_SSOT_e_Scripts/auditoria_geometrica.json (itens 'Sólidos em ...') + contagem reimportando o STEP |
| **G-06 sem espaço para fixação axial; M8 só radial nas asas** | CONFIRMADO MEDIDO, E NAO LIGA MAIS O PROCESSO | a parede entre o canal e o Ø93 foi conferida: (93,00 − 75,60)/2 = 8,70 mm de aço radial, e por isso não há parafuso axial possível - exatamente o que a auditoria disse. Com a fixação por collete + degrau (decisão do usuário), nenhum furo radial M8 com spot face precisa ser aberto na matriz; os únicos furos que existem nela são os pinos, com 2,39 mm de parede até o canal. O que a auditoria previa como risco ('as metades não podem ser fechadas contra a contrapressão') foi tratado pelo outro lado: o fechamento é feito pelo collete, medido em 8,58 MPa. (medido hoje: parede radial do canal até o Ø93 = 8,70 mm) | 04_Dados_SSOT_e_Scripts/interface_cabecote.json (blocos [D] e [E]) |
| **ação 6 do plano: sem furação de flange em Z = 0** | RESOLVIDO COM O DWG DO CABEÇOTE | o padrão veio do `030-032- cabeçote.dwg` medido, não de palpite: 6 furos Ø16,50 (M12) dentro de 6 fendas de 23,5 mm no C.C. Ø180,00, na face do flange, mais o piloto de centragem Ø105,00 × 3,00 mm na traseira. A matriz não precisa de flange próprio porque ela é presa pelo cabeçote. Consequência nova da decisão 'encosta face a face': a face da extrusora precisa de 3,00 mm de rebaixo em Ø > 105,00. (medido hoje: piloto protrai 3,00 mm atrás da face do flange (medido no sólido)) | 04_Dados_SSOT_e_Scripts/cabecote_ex030.json e item [G] de 04_Dados_SSOT_e_Scripts/verificar_interface_cabecote.py |
| **ação 8 do plano: ΔP e τ declarados não reproduzíveis** | RESOLVIDO EM SCRIPT VERSIONADO | os números passaram a ser saída de script, e o portão os compara com os documentos. Refeitos: τ na parede do land = 163,8 kPa (γ̇_ap = 911 s⁻¹) e ΔP 1D = 41,9 bar para a v28.1 (68,2 bar na v27.0), com a observação de que τ não depende do comprimento do land - é a mesma fenda, a mesma vazão, o que é justamente o que derrubava o '128,44 kPa' do relatório antigo. A triagem dos problemas declarados está em `TRIAGEM_DE_PROBLEMAS_DAS_MATRIZES.md`. (medido hoje: τ = 163,8 kPa) | 04_Dados_SSOT_e_Scripts/verificacao_v28.json ('τ na parede do land') e interface_cabecote.json ('numeros/dp_1d_bar') |
| **Matriz historica Gedeon reconstruida** | consertada por medida, e nao e a Jonatha | Re-corte do bloco do backup do usuario (02_/matrizGedeonCerta.step, 640.180,7 mm3, que sao as duas metades brutas ao bitola: diff 0,000 mm3) com o canal proprio da Gedeon (213.790,0 mm3) e com os pinos do proprioo arquivo dele (2x D1,78 x 10,00, que ja atravessam Y = 0), partido no plano Y = 0. Sai par com 1 casca por solido (o Body_A fornecido tem 3), A n B = 0,000000 mm3, nenhum metal no caminho do plastico (0,000000 mm3 dos dois lados), envelope D93,00 x Z 0..109,00 igual ao backup, e sentado no cabecote com 0,0000 mm3 de interferencia nos dois corpos. Prancha comparativa com as cinco faixas no mesmo escalonamento: 06_CAD_Cabecote_EX-030/STEP/Gedeon_Corrigida/DESENHO_2D_GEDEON_CONSERTADA_X_JONATHA.pdf (medido hoje: aco do par 469.358,8 mm3 contra 469.001,7 mm3 da v27; booleano nos dois sentidos: par - v27 = 155,1 mm3 e v27 - par = 44,9 mm3, entao nao sao a mesma peca. O que as separa e interno e nas bordas: o canal da Gedeon esta contido no da Jonatha (Gedeon - Jonatha = 0,0 mm3; Jonatha - Gedeon = 155,1 mm3 = 0,07 %), e o desenho mede ONDE os 155,1 mm3 estao: no anel de saida, Z 107,50 a 109,00 - o chanfro de 1,50 x 45 graus que a Jonatha tem e a Gedeon nao tem - mais 44,9 mm3 na zona dos pinos (Z 44,50 a 64,50), onde a Gedeon tem bolso e a v27 e macica. Nao e o funil: a afirmacao anterior foi escrita antes de medir a posicao e esta corrigida aqui e no relatorio) | 04_Dados_SSOT_e_Scripts/gedeon_corrigida.json e 03_Relatorios_e_Documentacao/RELATORIO_GEDEON_CORRIGIDA.md, gerados por gerar_gedeon_corrigida.py que entrou na cadeia do portao |

### O que continua aberto

* G-04 (d): canais de refrigeração Ø8 por metade - sem definição, sem modelo, sem número.
* Acesso axial dos cartuchos no cabeçote EX-030: NC -2,750 mm; sai com o nariz em Z ≥ 99,75 mm (recomendado 100,25 mm, com +0,500 de folga) - é decisão sua, não minha.
* Superfície de aperto do collete EX-031 (o furo Ø90,00 reto que medimos no DXF não desce sobre a banda Ø93: faltam 1,50 mm de raio). A pressão de fechamento é condicional a isso.
* Promover ou não a v28.1: a v27.0 continua sendo o master aprovado até você dizer.
* Medições que só o paquímetro resolve: Ø90 do furo do collete, D3 do funil, M12 na face.
* Gedeon reconstruida em 06_CAD_Cabecote_EX-030/STEP/Gedeon_Corrigida/ e peca de trabalho: nao substitui o master (regra 1) nem os historicos (regra 2), e o que vale e o que o processo de auditoria aprovar

τ citado acima: **163,8 kPa** - o mesmo número que está em `verificacao_v28.json`; se um mudar sem o outro, o portão fecha.
