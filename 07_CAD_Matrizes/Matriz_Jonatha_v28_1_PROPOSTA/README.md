# M02 — Matriz Jonatha v28.1 (proposta DFM, NÃO promovida)

É uma proposta em auditoria, não o modelo de trabalho. O master continua o v27.0 em `../Matriz_Jonatha_v27_OFICIAL/`.

Conteúdo: corpo inteiro, A, B, canal, pinos de alinhamento (os `_Explodida.step` e `_Com_Fluxo.step` que
existiam aqui saíram do repositório como derivados; `python 04_Dados_SSOT_e_Scripts/gerar_matriz_v28.py`
recria os sete, e o portão os regenera a cada rodada — estão no `.gitignore` de propósito).

O que a v28.1 muda, medido: fenda 75,00 × 1,50 com R 0,75 (112,0171 mm²), entrada restrita a Ø 75,60 em
Z = 0, land paralelo real 8,500 + chanfro 1,500 × 45°, lâmina de 0,750 mm no lábio, envelope Ø 93,00 × 69,90 /
Ø 89,50 × 10,80 / Ø 79,50 × 28,30 (Z total 109,000), 3,586 kg, ΔP 1D 41,9 bar, τ no land 163,8 kPa, abertura
da bipartição 55,7 kN.

**Consequência da mudança de pasta, avisada:** `05_Interface_Auditoria/propostas/PRP-0005-v28-1-fabricacao.json`
lista `arquivos[]` com `caminho` apontando para `01_CAD_MatrizJonatha_Oficial/MatrizJonatha_v28*.step`. esses
caminhos não têm atalho (só o v27 tem). Quando a auditoria for reaberta, isso se resolve nascendo `PRP-0006`
com os caminhos de `07_CAD_Matrizes/Matriz_Jonatha_v28_1_PROPOSTA/` — proposta auditada não se edita.
