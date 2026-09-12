# MATRIZEXTRUSORA — Matriz Jonatha (Extrusão Plana Master Aprovado)

![Status](https://img.shields.io/badge/Status-Modelo%20Master%20Aprovado-success)
![Revisão proposta](https://img.shields.io/badge/DFM-v28.1_Proposta_Verificada-orange)
![Versão SSOT](https://img.shields.io/badge/SSOT-v27.0_Master-blue)
![Formato CAD](https://img.shields.io/badge/Formato-STEP%20AP214-orange)
![Linguagem](https://img.shields.io/badge/Python-CadQuery%202.0-green)

Projeto de engenharia mecânica, reologia computacional (CFD) e modelagem 3D CAD para fabricação da **Matriz Jonatha**: matriz de extrusão plana otimizada para manta de isolação de acessórios de cabos elétricos de Média Tensão (MT).

---

## 📌 Especificação Resumida do Produto Final
- **Largura da Manta ($X$):** $75,00\text{ mm}$ (Constante de ponta a ponta)
- **Espessura da Manta ($Y$):** $1,50\text{ mm}$
- **Perfil das Bordas Laterais:** Raio Total $R = 0,75\text{ mm}$ (elimina concentração de campo elétrico em cabos MT)
- **Chanfro de Saída:** $1,50\text{ mm} \times 45^\circ$ no v27.0 aprovado → **reduzido para $0,80\text{ mm} \times 45^\circ$ na proposta v28.0**, o que devolve 0,70 mm de land reto (8,50 → 9,20 mm) e engrossa a lâmina do lábio de 0,75 → 1,45 mm (medido)
- **Encaixe de Entrada ($Z=0$):** Restrito ao diâmetro de acoplamento da extrudora ($arnothing 75,60\text{ mm}$), garantindo vedação e montagem perfeita.
- **Envelope Cilíndrico Externo:** Estágio 1 ($\varnothing 93,00 \times 69,90\text{ mm}$), Estágio 2 ($\varnothing 89,50 \times 10,80\text{ mm}$), Estágio 3 ($\varnothing 79,50 \times 28,30\text{ mm}$) — 100% idêntico à Matriz 2 para montagem direta na máquina.

---

## 📊 Resultados da Simulação Reológica CFD (Matriz 2 vs. Matriz Jonatha Master Aprovado)

| Métrica Reológica | Matriz 2 (Matriz Gedeon) | **Matriz Jonatha Master (v27.0)** | Ganho / Melhoria |
| :--- | :---: | :---: | :---: |
| **Geometria do Canal Interno** | Funil abrupto + Fenda de $87,60\text{ mm}$ | **Funil V Restrito na Entrada** + Land $10\text{ mm}$ | **Redução de $88.6\%$ no land** |
| **Perda de Carga Total ($\Delta P$)** | **$268,7\text{ bar}$** | **$68,2\text{ bar}$** | **Redução de $74,6\%$ na contrapressão** |
| **Uniformidade de Velocidade** | $68,96\%$ (falta vazão nas pontas) | **$99,10\%$** | **Fluxo $100\%$ plano e homogêneo** |
| **Tensão de Cisalhamento na Parede** | $157,11\text{ kPa}$ | **$128,44\text{ kPa}$** | **Operação suave sem fratura do fundido** |
| **Qualidade da Manta** | Rasgos e afinamento nas bordas ao esquentar | **Bordas perfeitas sem rasgos** | **Eliminação de refugos de produção** |

> ⚠️ **Leitura obrigatória desta tabela (auditoria de 2026-09-11).** Os valores acima são saída de
> CFD arquivada e **não são reproduzíveis a partir dos arquivos deste repositório** (não há malha,
> caso nem planilha). Medindo a geometria real dos STEP: ΔP 1D **41,9 bar** na v27.0 e **43,9 bar** na
> v28.0 (não 68,2 bar), e a **tensão de cisalhamento na parede é a mesma nas duas matrizes
> (163,8-164,0 kPa)** — a linha "157,11 → 128,44 kPa" não se sustenta, pois fenda e vazão são
> idênticas. A **uniformidade de 99,10 %** não tem definição nem dados anexados: não usar como
> critério de aceite. Ver `03_Relatorios_e_Documentacao/TRIAGEM_DE_PROBLEMAS_DAS_MATRIZES.md`.

---

## 📐 Revisão v28.1 — proposta DFM verificada (não substitui o v27.0)

A v27.0 continua sendo o **master aprovado**; a v28.0 vive ao lado, em arquivos novos, até a
aprovação. Ela resolve o que a auditoria apontou como defeito real e prova cada número medindo os
sólidos (booleanos + `BRepExtrema`), não declarando:

| | v27.0 aprovado | v28.1 proposta |
| :--- | :--- | :--- |
| Land reto e paralelo | 8,50 mm (o SSOT declarava 10,00) | **8,50 mm — mantido** (D2); SSOT corrigido para 8,50 + 1,50 de chanfro |
| Chanfro de saída | 1,50 × 45° (lâmina de 0,75 mm) | **1,50 × 45° — mantido** (a redução para 0,80 foi rejeitada em D2); boca de saída medida 78,00 × 4,50 mm |
| Furos de pino | 2 bolsões **selados** no Body_A; nenhum no Body_B | **4 bolsões Ø4 H7 × 12 abertos no plano de partição, conjugados nas duas metades** + kit de pinos |
| Aquecimento | nenhum | **6 cartuchos Ø9,5** (Z=97,00; X=0 e ±22) e **4 poços de termopar Ø4,8** (Z=103,00; X=±11), paredes reais de 2,39-17,03 mm |
| Arquivo do canal | 3 sólidos (núcleo + 2 bolhas) | **1 sólido** (pronto para EDM e para malha de CFD) |
| Especificação do produto | 75,00 × 1,50 mm, R0,75, boca Ø75,60, envelope Ø93/89,5/79,5 × 109,00 | **idêntica e re-medida: Δ máximo = 0,000000 mm** |

- Verificação: **64 itens medidos, 64 conformes, 0 não conformes** → `03_Relatorios_e_Documentacao/VERIFICACAO_V28.md`
- Memória de cálculo, cotas de usinagem, o que **não** cabe (fixação das metades e refrigeração) e as
  decisões pendentes → `03_Relatorios_e_Documentacao/PROJETO_DFM_V28_MATRIZ_JONATHA.md`
- Conferência visual (6 vistas geradas dos STEP) → `03_Relatorios_e_Documentacao/V28_CONFERENCIA_VISUAL.png`
- Descoberta registrada: o funil do modelo aprovado é um **cônico linear de largura constante**, não o
  "coat-hanger com reservatório de 6,00 mm" descrito — as seções intermediárias do loft nunca entraram
  no sólido. Item de decisão **D3**.

### 🧪 Variantes em estudo (não são o modelo oficial)

`05_Variantes_Em_Estudo/` guarda os STEP de comparações pedidas antes de qualquer mudança de geometria.
Hoje há uma: o **funil coat-hanger** medido contra o cone linear do master (ΔP 1D, tempo de residência,
volume estacionado nas pontas, invasão do envelope e aço cortado) — tabela e leitura em
`03_Relatorios_e_Documentacao/ESTUDO_FUNIL_COATHANGER.md`, gerador em `04_Dados_SSOT_e_Scripts/estudar_funis.py`.
Nada disso substitui `MatrizJonatha.step`.

### 🔩 Interface com o cabeçote EX-030 — medida no DWG e provada nos sólidos

O `030-032- cabeçote.dwg` (HIDEALL, PED:2257) foi convertido e **medido entidade por entidade**. A
escala do desenho foi calibrada pelas próprias cotas (**25,534 mm por unidade DXF**, 5 fechos
independentes fechando em 0,012 %), e o sólido do cabeçote montado a partir dessa medição foi
enfrentado à v28.0 com booleanos: **43 itens, 39 conformes, 0 não conformes, 4 pendências do lado
da máquina** → `03_Relatorios_e_Documentacao/INTERFASE_CABECOTE_EX030.md`

| o que foi medido | resultado |
| :--- | :--- |
| furos do cabeçote para a matriz | Ø80,00 × 14,00 · Ø90,00 × 11,00 · Ø95,00 × 70,00 (profundidade da face do nariz) |
| encaixe nos 3 estágios da matriz | folga radial **1,00 / 0,25 / 0,25 mm**, folga axial no degrau de apoio **0,10 mm**, interferência **0,0000 mm³** |
| face do cabeçote | anel de **20,00 mm** (Ø90 → Ø130); nariz Ø80 maior que a fenda (75,80) e menor que a matriz (Ø93) |
| protrusão da matriz | face de saída **14,00 mm** à frente do nariz do cabeçote — a fenda trabalha fora da peça aquecida |
| fixação | bucha cônica **EX-031** (Ø95 → Ø86, cone 3,00°, L 70,00) apertando a banda Ø93: **8,58 MPa** fecham os 55,7 kN da partição; empuxo axial de 29,85 kN recai no degrau, no anel de contato real de 431,2 mm² (**69,22 MPa**, margem 20,2×) |
| padrão de flange (P4) | **não existe na matriz**: 6 × Ø16,50 em fendas de 23,50 sobre C.C. Ø180,00 (M12, ±7,20° de ajuste) é a junta cabeçote ↔ extrusora, a 35,25 mm do corpo da matriz |
| **bloqueio** | anel do nariz **Ø68,30** (carimbo 9"×65 mm) → 5,60 mm de interferência radial por lado com o nariz Ø79,50 da matriz: **a matriz de 75 mm não monta com esse anel**, e como o furo do nariz já é Ø80 não há espaço para nenhum anel não restritivo |

Correção registrada: a triagem anterior calibrou a escala em "C/G Ø150" (k = 21,28 mm/un) lido em
raster de baixa resolução e sugeriu grampos nesses furos. O desenho diz **C.C Ø180**; os furos são
da junta com a extrusora e **a recomendação de grampos no flange foi retirada** — a fixação vem do
collete da própria máquina. Nenhuma cota da matriz mudou por causa disso: o envelope
Ø93/Ø89,50/Ø79,50 × 109,00 é exatamente o centragens do cabeçote.

```bash
python 04_Dados_SSOT_e_Scripts/gerar_matriz_v28.py               # regenera os STEP v28.0
python 04_Dados_SSOT_e_Scripts/verificar_v28.py --json --md      # volta a medir e provar
python 04_Dados_SSOT_e_Scripts/explorar_acomodo_furos.py --json # onde existe aço para furos
python 04_Dados_SSOT_e_Scripts/gerar_relatorio_v28.py           # atualiza o relatório com os dados
python 04_Dados_SSOT_e_Scripts/renderizar_v28.py --saida v28.png
python 04_Dados_SSOT_e_Scripts/verificar_interface_cabecote.py --json --md  # matriz × cabeçote EX-030
```

---

## 📂 Estrutura Direta de Pastas do Repositório

```
MATRIZEXTRUSORA/
├── README.md                              -> Este arquivo guia do repositório
├── .gitignore                             -> Exclusões para repositório Git
│
├── 📂 01_CAD_MatrizJonatha_Oficial/       -> ARQUIVOS CAD MASTER OFICIAIS (SSOT v27.0)
│   ├── MatrizJonatha.step                 -> Montagem fechada bipartida oca em camadas AP214
│   ├── MatrizJonatha_Explodida.step       -> Vista explodida (+40mm Y) exibindo o canal interno
│   ├── MatrizJonatha_Com_Fluxo.step       -> Montagem completa (Aço + Macho de polímero)
│   ├── MatrizJonatha_Body_A.step          -> Sólido individual da metade inferior (Y <= 0)
│   ├── MatrizJonatha_Body_B.step          -> Sólido individual da metade superior (Y >= 0)
│   ├── MatrizJonatha_Canal_Fluxo.step     -> Sólido individual do núcleo de fluxo do polímero
│   └── MatrizJonatha_v28*.step            -> PROPOSTA DFM v28.0 (montagem, A/B, canal 1 sólido,
│                                              explodida, com fluxo e kit de 4 pinos)
│
├── 📂 02_CAD_Modelos_Historicos/          -> MODELOS CAD LEGADOS PRESERVADOS
│   ├── MatrizGedeon.step e variantes     -> Matriz 2 (Gedeon) original mantida intacta
│   ├── MatrizDesenvolvimento.step        -> Versão intermediária mantida intacta
│   └── Matriz1_Original_Copo.step        -> Matriz 1 (Copo Oco) mantida intacta
│
├── 📂 03_Relatorios_e_Documentacao/       -> DOCUMENTAÇÃO TÉCNICA E SIMULAÇÕES
│   ├── AUTO_PROMPT_CONTINUIDADE_MATRIZ_JONATHA.md -> Prompt de handover para continuidade em IA
│   ├── AUDITORIA_GEOMETRICA_MATRIZ_JONATHA.md -> Auditoria dimensional automática dos STEP vs. SSOT
│   ├── TRIAGEM_DE_PROBLEMAS_DAS_MATRIZES.md -> O que é problema real e o que não é, nas 4 matrizes
│   ├── PROJETO_DFM_V28_MATRIZ_JONATHA.md  -> Memória de cálculo e cotas da revisão v28.0
│   ├── VERIFICACAO_V28.md                 -> As 64 medições que provam a v28.0
│   └── V28_CONFERENCIA_VISUAL.png         -> 6 vistas renderizadas dos STEP v28
│   ├── RELATORIO_DE_SIMULACAO.md          -> Relatório executivo completo de CFD reológico e térmico
│   ├── CAD_SPECIFICATION_BACKUP_SSOT.md  -> Especificação técnica unificada SSOT v27.0
│   └── SIMULACAO_REOLOGICA_MATRIZ_JONATHA.md -> Detalhamento dos modelos reológicos
│
└── 📂 04_Dados_SSOT_e_Scripts/            -> PARÂMETROS NUMÉRICOS E GERADORES
    ├── cad_die_parameters.json            -> JSON da Fonte Única da Verdade (SSOT v27.0)
    ├── auditoria_geometrica.json          -> Resultado numérico da auditoria dimensional dos STEP
    ├── verify_geometry_ssot.py            -> Auditoria automática: mede os STEP e compara com o SSOT
    ├── verify_legacy_dies.py              -> Mede as 4 matrizes, confere os arquivos e recalcula o ΔP
    ├── auditoria_matrizes_historicas.json -> Resultado numérico da comparação entre as 4 matrizes
    ├── gerar_matriz_v28.py                -> Gerador da revisão v28.0 (lê o canal aprovado, não re-desenha)
    ├── verificar_v28.py                   -> Verificador exato da v28.0 (64 medições, 0 NC)
    ├── gerar_relatorio_v28.py             -> Monta o relatório DFM a partir dos JSONs medidos
    ├── explorar_acomodo_furos.py          -> Mapeia o aço disponível para furos antes de fixar cotas
    ├── renderizar_v28.py                  -> Render headless de conferência (matplotlib, sem GPU)
    ├── matriz_v28_features.json           -> Cotas de projeto dos 14 furos (fonte do verificador)
    ├── verificacao_v28.json               -> Resultado numérico das 64 medições
    ├── acomodo_furos.json                 -> Grade de posições viáveis por tipo de furo
    ├── generate_auto_prompt.py            -> Gera o prompt de handover a partir do SSOT
    ├── setup_headless_gl.sh               -> Ambiente CAD headless (stub libGL para servidores/CI)
    ├── dados_simulacao_reologica.json     -> Dados numéricos de simulação em JSON
    └── dados_simulacao_carreau_yasuda.json -> Dados numéricos térmicos em JSON
```

---

## 🔍 Auditoria Geométrica dos Arquivos STEP

Os entregáveis CAD são verificados automaticamente contra o SSOT (não por inspeção visual,
mas medindo as seções dos sólidos STEP):

```bash
bash 04_Dados_SSOT_e_Scripts/setup_headless_gl.sh   # apenas em servidores sem libGL
export LD_LIBRARY_PATH="$PWD/04_Dados_SSOT_e_Scripts/.headless_gl:$LD_LIBRARY_PATH"
python 04_Dados_SSOT_e_Scripts/verify_geometry_ssot.py --json --md
```

```bash
python 04_Dados_SSOT_e_Scripts/verify_legacy_dies.py --json   # compara as 4 matrizes
```

Última execução (v27.0): **36 itens verificados, 19 conformes, 2 não conformes, 15 informativos**
— as 2 não conformidades continuam abertas de propósito: são exatamente os itens que a v28.0 fecha
(land declarado vs. real e cavidades seladas / furos só num corpo).
Resultado completo em `03_Relatorios_e_Documentacao/AUDITORIA_GEOMETRICA_MATRIZ_JONATHA.md` e
diagnóstico comparativo em `03_Relatorios_e_Documentacao/TRIAGEM_DE_PROBLEMAS_DAS_MATRIZES.md`.
