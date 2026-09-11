# Auditoria Geométrica Automatizada - Matriz Jonatha

**Documento:** Verificação dimensional dos arquivos STEP oficiais contra o SSOT  
**Revisão auditada:** `v27.0_MatrizJonatha_Approved_Master`  
**Script gerador:** `04_Dados_SSOT_e_Scripts/verify_geometry_ssot.py`  
**Data da auditoria:** 2026-09-11  
**Tolerância dimensional:** ±0.02 mm  

---

## 1. Resultado Consolidado

- **Itens verificados:** 34
- **Conformes:** 18
- **Não conformes:** 1
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
| Envelope - (aço + canal + 2 furos de pino) | 0.0 mm3 | 0.0009 mm3 | +0.0009 mm3 | ✅ |

## 3. Diagnósticos e Não Conformidades

| Item | Valor medido | Observação |
| :--- | :--- | :--- |
| Comprimento do land reto e paralelo | 8.5 mm (nominal 10.0) | o chanfro de saída consome 1,50 mm do land |
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
| 1 | Pinos de alinhamento Ø4 × 12 apenas no `Body_A` | As duas metades ficam sem referência de alinhamento: risco de degrau e rebarba no plano de partição da manta | Usinar os furos conjugados Ø4 H7 (cegos de 12 mm) no `Body_B` e montar 2 pinos Ø4 × 20 mm temperados |
| 2 | Land reto e paralelo real = 8,50 mm (SSOT declara 10,00 mm) | Divergência documental; o chanfro de 45° consome 1,50 mm do land | Corrigir o SSOT para 8,50 mm de land paralelo + 1,50 mm de chanfro, **ou** reduzir o chanfro para 0,50 mm × 45° (land = 9,50 mm) |
| 3 | Parede de aço no lábio de saída = 0,75 mm | Lábio frágil: risco de lascamento e rebarba na face de saída Ø79,5 (impossível retificar plana) | Reduzir o chanfro para 0,50–0,80 mm × 45° (lábio ≥ 1,40 mm), mantendo o envelope Ø79,5 intacto |
| 4 | Nenhum furo de fixação/aperto no modelo | As metades não podem ser fechadas contra os 68 bar de contrapressão | Definir padrão de fixação: 4 × M8 em Y nas asas do Ø93 (com spot face) **ou** grampos/quadro externo (verificar espaço: parede de aço de apenas 8,7 mm entre o canal e o Ø93) |
| 5 | Sem controle térmico (cartuchos Ø9,5 / termopar / refrigeração) | Operação fora da janela de 50–65 °C reintroduz o *edge tearing* | Acrescentar furos de cartucho Ø9,5 mm, poço de termopar Ø6 mm e 2 canais de refrigeração Ø8 mm por metade |
| 6 | Sem furação de flange em Z=0 | Acoplamento à extrudora depende só do encaixe Ø75,60 mm | Extrair o padrão de furos do cabeçote original (`030-032- cabeçote.dwg`) antes de definir o flange |
| 7 | `MatrizJonatha_Canal_Fluxo.step` contém 3 sólidos | Dificulta o uso direto como eletrodo de EDM / malha de CFD | Reexportar apenas o núcleo de polímero (1 sólido) |

## 5. Conclusão

O envelope externo, a seção do land (75,00 × 1,50 mm com bordas R0,75), a boca de entrada Ø75,60 mm e o fechamento volumétrico do conjunto (aço + canal de polímero + furos de pino = envelope cilíndrico nominal) foram todos confirmados numericamente.

Os itens marcados como **NÃO CONFORME** exigem decisão de engenharia antes da usinagem: ver a seção 3 e o plano de ação em `RELATORIO_TECNICO_E_SUGESTOES.md`.

---

*Relatório gerado automaticamente por `verify_geometry_ssot.py --md`.*
