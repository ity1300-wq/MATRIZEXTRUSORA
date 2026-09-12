# Verificação exata da revisão v28.1 — Matriz Jonatha

Medida nos STEP gerados por `gerar_matriz_v28.py` (booleanos + BRepExtrema; nada é estimado).

**64 itens verificados · 64 conformes · 0 não conformes**

| Item | Nominal | Medido | Status | Observação |
| :--- | ---: | ---: | :---: | :--- |
| Canal entregue com 1 único sólido (o v27 tinha 3) | — | 1 sólido(s) | ✅ | necessário p/ eletrodo de EDM e malha de CFD |
| Comprimento total Z | 109 | 109 | ✅ |  |
| Ø externo máximo (estágio 1) | 93 | 93 | ✅ |  |
| Ø externo em Z=0,500 (estágio Ø93,0) | 93 | 93 | ✅ |  |
| Ø externo em Z=75,300 (estágio Ø89,5) | 89,5 | 89,5 | ✅ |  |
| Ø externo em Z=94,850 (estágio Ø79,5) | 79,5 | 79,5 | ✅ |  |
| Ø da boca de entrada (Z=0) | 75,6 | 75,6 | ✅ |  |
| Largura da fenda (X) | 75 | 75 | ✅ |  |
| Espessura da fenda (Y) | 1,5 | 1,5 | ✅ |  |
| Área da seção da fenda (R0,75 nas bordas) | 112,017 | 112,017 | ✅ |  |
| Funil (Z<99) geometricamente idêntico ao master v27.0 | — | Δmáx entre superfícies = 0,000000 mm | ✅ | a revisão não mexe no aprovado |
| Volume do funil v28 vs v27 | — | diferença = 0,0278 mm³ | ✅ | mesmo sólido abaixo de Z=99 |
| Assimetria do canal em torno do plano de partição Y=0 | — | |A-B| = 199,22 mm³ (0,093 % do canal) | ✅ | herdado do loft do v27.0: as metades não são espelhos exatos |
| Arquivos STEP entregues (nomes + nº de sólidos) | — | 7/7 exatos | ✅ | mestr=2 · explodida=2 · com_fluxo=3 · pinos=4 · canal=1 · corpo=1 |
| Land reto e paralelo (v27.0: 8,50) | 8,5 | 8,5 | ✅ | P8 resolvido no modelo |
| Chanfro de saída (v27.0: 1,50) | 1,5 | 1,5 | ✅ | D2: lábio mantido como no master, sem ganho de land |
| Sobrelargura do chanfro a 0,10 mm da face | 1,4 | 1,402 | ✅ | chanfro de 45° |
| Lâmina de aço no lábio de saída (= valor decidido em D2) | 0,75 | 0,75 | ✅ | a decisão D2 aceitou a lâmina fina de 0,75 mm do master; o lascamento na limpeza passa a ser item de procedimento de manutenção, não de geometria |
| Shells no Body_A (v27.0 tinha 3 = 2 bolhas seladas) | — | 1 | ✅ | 1 = sólido limpo, sem cavidade interna |
| Shells no Body_B (v27.0 tinha 1, mas sem furo nenhum) | — | 1 | ✅ | 1 = sólido limpo |
| Interferência Body_A ∩ Body_B | 0 | 0 | ✅ |  |
| Pino em X=-42.10 Z=30.00 | — | A: bolso vazio 0.0000 mm³, aço sob o fundo 12.6/12.6 mm³ | B: 0.0000 / 12.6 mm³ | ✅ | aberto no plano de partição e cego sob o fundo nas DUAS metades |
| Pino em X=+42.10 Z=30.00 | — | A: bolso vazio 0.0000 mm³, aço sob o fundo 12.6/12.6 mm³ | B: 0.0000 / 12.6 mm³ | ✅ | aberto no plano de partição e cego sob o fundo nas DUAS metades |
| Pino em X=-42.10 Z=60.00 | — | A: bolso vazio 0.0000 mm³, aço sob o fundo 12.6/12.6 mm³ | B: 0.0000 / 12.6 mm³ | ✅ | aberto no plano de partição e cego sob o fundo nas DUAS metades |
| Pino em X=+42.10 Z=60.00 | — | A: bolso vazio 0.0000 mm³, aço sob o fundo 12.6/12.6 mm³ | B: 0.0000 / 12.6 mm³ | ✅ | aberto no plano de partição e cego sob o fundo nas DUAS metades |
| Pinos conjugados nas duas metades | — | 4/4 no Body_A e 4/4 no Body_B | ✅ | v27.0: bolsões selados só no A e nada no B (P2) |
| Fechamento: env − (aço + canal) = volume dos furos | 12506,7 | 12506,7 | ✅ | prova que todo furo removido existe no corpo e nada mais foi tirado |
| parede mínima até o canal - pino_alinhamento X=-42.10 Z=30.00 | — | 2,391 mm | ✅ | alvo ≥ 2,00 mm | invadiu o canal em 0,000000 mm³ |
|   ∩ volume do canal - pino_alinhamento X=-42.10 Z=30.00 | — | 0,000000 mm³ | ✅ | zero = o furo não comunica com o fluxo |
| parede mínima até o canal - pino_alinhamento X=+42.10 Z=30.00 | — | 2,392 mm | ✅ | alvo ≥ 2,00 mm | invadiu o canal em 0,000000 mm³ |
|   ∩ volume do canal - pino_alinhamento X=+42.10 Z=30.00 | — | 0,000000 mm³ | ✅ | zero = o furo não comunica com o fluxo |
| parede mínima até o canal - pino_alinhamento X=-42.10 Z=60.00 | — | 2,482 mm | ✅ | alvo ≥ 2,00 mm | invadiu o canal em 0,000000 mm³ |
|   ∩ volume do canal - pino_alinhamento X=-42.10 Z=60.00 | — | 0,000000 mm³ | ✅ | zero = o furo não comunica com o fluxo |
| parede mínima até o canal - pino_alinhamento X=+42.10 Z=60.00 | — | 2,483 mm | ✅ | alvo ≥ 2,00 mm | invadiu o canal em 0,000000 mm³ |
|   ∩ volume do canal - pino_alinhamento X=+42.10 Z=60.00 | — | 0,000000 mm³ | ✅ | zero = o furo não comunica com o fluxo |
| parede mínima até o canal - cartucho X=+0.00 Z=97.00 | — | 8,196 mm | ✅ | alvo ≥ 4,00 mm | invadiu o canal em 0,000000 mm³ |
|   ∩ volume do canal - cartucho X=+0.00 Z=97.00 | — | 0,000000 mm³ | ✅ | zero = o furo não comunica com o fluxo |
| parede mínima até o canal - cartucho X=+0.00 Z=97.00 | — | 8,196 mm | ✅ | alvo ≥ 4,00 mm | invadiu o canal em 0,000000 mm³ |
|   ∩ volume do canal - cartucho X=+0.00 Z=97.00 | — | 0,000000 mm³ | ✅ | zero = o furo não comunica com o fluxo |
| parede mínima até o canal - cartucho X=-22.00 Z=97.00 | — | 9,313 mm | ✅ | alvo ≥ 4,00 mm | invadiu o canal em 0,000000 mm³ |
|   ∩ volume do canal - cartucho X=-22.00 Z=97.00 | — | 0,000000 mm³ | ✅ | zero = o furo não comunica com o fluxo |
| parede mínima até o canal - cartucho X=-22.00 Z=97.00 | — | 9,324 mm | ✅ | alvo ≥ 4,00 mm | invadiu o canal em 0,000000 mm³ |
|   ∩ volume do canal - cartucho X=-22.00 Z=97.00 | — | 0,000000 mm³ | ✅ | zero = o furo não comunica com o fluxo |
| parede mínima até o canal - cartucho X=+22.00 Z=97.00 | — | 9,356 mm | ✅ | alvo ≥ 4,00 mm | invadiu o canal em 0,000000 mm³ |
|   ∩ volume do canal - cartucho X=+22.00 Z=97.00 | — | 0,000000 mm³ | ✅ | zero = o furo não comunica com o fluxo |
| parede mínima até o canal - cartucho X=+22.00 Z=97.00 | — | 9,324 mm | ✅ | alvo ≥ 4,00 mm | invadiu o canal em 0,000000 mm³ |
|   ∩ volume do canal - cartucho X=+22.00 Z=97.00 | — | 0,000000 mm³ | ✅ | zero = o furo não comunica com o fluxo |
| parede mínima até o canal - termopar X=-11.00 Z=103.00 | — | 16,349 mm | ✅ | alvo ≥ 3,00 mm | invadiu o canal em 0,000000 mm³ |
|   ∩ volume do canal - termopar X=-11.00 Z=103.00 | — | 0,000000 mm³ | ✅ | zero = o furo não comunica com o fluxo |
| parede mínima até o canal - termopar X=-11.00 Z=103.00 | — | 16,349 mm | ✅ | alvo ≥ 3,00 mm | invadiu o canal em 0,000000 mm³ |
|   ∩ volume do canal - termopar X=-11.00 Z=103.00 | — | 0,000000 mm³ | ✅ | zero = o furo não comunica com o fluxo |
| parede mínima até o canal - termopar X=+11.00 Z=103.00 | — | 16,349 mm | ✅ | alvo ≥ 3,00 mm | invadiu o canal em 0,000000 mm³ |
|   ∩ volume do canal - termopar X=+11.00 Z=103.00 | — | 0,000000 mm³ | ✅ | zero = o furo não comunica com o fluxo |
| parede mínima até o canal - termopar X=+11.00 Z=103.00 | — | 16,349 mm | ✅ | alvo ≥ 3,00 mm | invadiu o canal em 0,000000 mm³ |
|   ∩ volume do canal - termopar X=+11.00 Z=103.00 | — | 0,000000 mm³ | ✅ | zero = o furo não comunica com o fluxo |
| Furos de aquecimento: abertos na face externa, cegos, sem romper as faces | — | OK - todos os 14 | ✅ | atravessar a peça = vazamento; ficar enterrado = não usinável |
| Menor web de aço entre dois furos | — | 5,380 mm | ✅ | par: cartucho X=+0.0 Z=97.0 × termopar X=-11.0 Z=103.0 | mínimo 3.00 mm |
| Massa de aço (7,85 g/cm³) | — | 3,586 kg | ✅ | v27.0: 3,682 kg | aços: P20 pré / H13 temperado |
| Área projetada do canal no plano XZ (medida) | — | 8169 mm² | ✅ | é a área sobre a qual a pressão empurra as metades uma contra a outra |
| Força que abre a bipartição | — | 55,7 kN no limite (pressão plena em toda a área) · 30,6 kN sobre a boca Ø75,60 | ✅ | por isso a fixação não é opcional (ver relatório DFM) |
| ΔP 1D - lei das potências (método do próprio projeto) | — | v28.1 = 41,9 bar | v27.0 = 41,9 bar | ✅ | land 8,50 vs 8,50 paralelos → -0.0 bar; maior gradiente em Z≈99,2 mm |
| τ na parede do land | — | 163,8 kPa (γ̇_ap = 911 s⁻¹) | ✅ | não depende do comprimento do land: mesma fenda, mesma vazão |
| Faixa de aço entre o canal e o Ø93 | — | 8.70 mm | ✅ | sem espaço para furo de pressão: Ø9,5 + parede 4 + parede 4 = 11,5 mm |
| Cotas de usinagem do land | — | paralelo Z=99,00→107,50 mm (8,50) · chanfro 1,50×45° Z=107,50→109,00 mm | ✅ | conferir no desenho antes de cortar o aço |
