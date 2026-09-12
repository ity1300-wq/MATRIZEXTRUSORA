# MATRIZEXTRUSORA — Matriz Jonatha (Extrusão Plana Master Aprovado)

![Status](https://img.shields.io/badge/Status-Modelo%20Master%20Aprovado-success)
![Versão SSOT](https://img.shields.io/badge/SSOT-v27.0_Master-blue)
![Formato CAD](https://img.shields.io/badge/Formato-STEP%20AP214-orange)
![Linguagem](https://img.shields.io/badge/Python-CadQuery%202.0-green)

Projeto de engenharia mecânica, reologia computacional (CFD) e modelagem 3D CAD para fabricação da **Matriz Jonatha**: matriz de extrusão plana otimizada para manta de isolação de acessórios de cabos elétricos de Média Tensão (MT).

---

## 📌 Especificação Resumida do Produto Final
- **Largura da Manta ($X$):** $75,00\text{ mm}$ (Constante de ponta a ponta)
- **Espessura da Manta ($Y$):** $1,50\text{ mm}$
- **Perfil das Bordas Laterais:** Raio Total $R = 0,75\text{ mm}$ (elimina concentração de campo elétrico em cabos MT)
- **Chanfro de Saída:** Micro-chanfro divergente de $1,50\text{ mm} \times 45^\circ$
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
│   └── MatrizJonatha_Canal_Fluxo.step     -> Sólido individual do núcleo de fluxo do polímero
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
│   ├── AVALIACAO_MELHORIA_MATRIZ_3_JONATHA.md -> Avaliação independente: a Matriz 3 pode melhorar?
│   └── figuras/aresta_R075_intuicao.png   -> Por que a aresta R0,75 recebe pouco material
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
    ├── setup_headless_gl.sh               -> Ambiente CAD headless (stub libGL para servidores/CI)
    ├── setup_cfd_env.sh                   -> Ambiente CAD+CFD completo (cadquery, gmsh, scikit-fem, pyamg)
    ├── cfd_land_crosssection.py           -> CFD 2D por seção transversal (p-Laplaciano, P2) — validado 0,6%
    ├── cfd_edge_relief.py                 -> Canal paramétrico com alívio de borda (estudo de sensibilidade)
    ├── avaliacao_matriz3_calculos.py      -> Perfil de pressão, mecânica, residência, inchamento, sensibilidade
    ├── avaliacao_matriz3_uniformidade.py  -> Uniformidade transversal da vazão a partir do CFD
    ├── avaliacao_matriz_3_secoes.json     -> CFD 2D das seções (Matriz 3)
    ├── avaliacao_matriz_3_calculos.json   -> Cálculos de engenharia consolidados (Matriz 3)
    ├── avaliacao_matriz_3_uniformidade.json -> Métricas de uniformidade transversal (Matriz 3)
    ├── avaliacao_matriz_3_alivio_borda.json -> Estudo paramétrico de alívio de borda
    ├── dados_simulacao_reologica.json     -> Dados numéricos de simulação em JSON
    └── dados_simulacao_carreau_yasuda.json -> Dados numéricos térmicos em JSON
```

---

## 🤝 Interface de Auditoria (IA engenheira ⇄ IA auditora)

O projeto tem um **contrato versionado** para que uma IA de projeto proponha melhorias e uma IA
auditora verifique — sem conversa, sem ambiguidade e sem número sem lastro:

```
05_Interface_Auditoria/
├── PROTOCOLO_AUDITORIA.md        contrato: papéis, ciclo, estados, severidades, tolerâncias
├── esquema/proposta.schema.json  o que a IA engenheira entrega
├── esquema/veredito.schema.json  o que a IA auditora devolve
├── scripts/auditar_proposta.py   auditor: mede os STEP, recalcula e emite o veredito
├── propostas/PRP-XXXX-*.json     propostas de engenharia (uma por iteração)
├── vereditos/PRP-XXXX.{json,md}  vereditos (contrato + comentário de PR)
└── baseline/MATRIZ_3_v27.json    estado aprovado congelado, para comparar evolução
```

**Regra fundadora:** *nenhum número entra no projeto sem um script que o reproduza.* Toda afirmação
numérica é uma **proposta**; todo número medido é um **veredito**.

```bash
# congelar o estado atual como baseline (só quando o modelo muda de versão)
python 05_Interface_Auditoria/scripts/auditar_proposta.py --congelar-baseline

# auditar uma proposta (leve, ~2 min)
python 05_Interface_Auditoria/scripts/auditar_proposta.py \
       05_Interface_Auditoria/propostas/PRP-0001-land-10-chanfro-08.json --json --md

# com CFD 2D na auditoria (~8 min)
python 05_Interface_Auditoria/scripts/auditar_proposta.py <proposta.json> --com-cfd --json --md
```

Estados do veredito: **APROVADO** · **APROVADO_COM_RESSALVAS** · **REPROVADO** (número declarado ≠
recalculado, ou métrica degradou) · **BLOQUEADO** (requisito duro violado: largura, espessura, borda,
envelope, arquivos, zona congelada).

Quatro formas de operar, todas implementadas (detalhes no `PROTOCOLO_AUDITORIA.md` §7):

| Modo | Ferramenta | Latência |
| :--- | :--- | :--- |
| A — CI | `.github/workflows/auditoria.yml` — pronto em `05_Interface_Auditoria/ci/auditoria.yml`, aguardando permissão `workflows` do app (comenta no PR) | ~6 min |
| B — vigilância git | `python 05_Interface_Auditoria/scripts/monitor_auditoria.py [--remoto --push]` | ~2 min/proposta |
| B — painel vivo | `python 05_Interface_Auditoria/scripts/painel_auditoria.py --porta 8000` | segundos |
| C — ponte humana | colar a proposta no chat e receber o veredito | minutos |

O painel vivo é também uma API para a IA engenheira:

```bash
curl -X POST 'http://localhost:8000/api/auditar?modo=completo&sincrono=1' \
     -H 'Content-Type: application/json' --data-binary @proposta.json   # -> veredito em JSON
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

## 💧 CFD próprio (validado)

O repositório traz um solucionador próprio de CFD 2D de escoamento desenvolvido (p-Laplaciano de lei
das potências, elemento P2), com a malha gerada do STEP oficial pelo gmsh:

```bash
bash 04_Dados_SSOT_e_Scripts/setup_cfd_env.sh
export LD_LIBRARY_PATH="$PWD/04_Dados_SSOT_e_Scripts/.headless_gl:$LD_LIBRARY_PATH"
python 04_Dados_SSOT_e_Scripts/cfd_land_crosssection.py --secoes 70 95 99.5 103 107 --json
python 04_Dados_SSOT_e_Scripts/avaliacao_matriz3_calculos.py --json
python 04_Dados_SSOT_e_Scripts/avaliacao_matriz3_uniformidade.py --json
```

Validação: gradiente no land medido em **2,1761 bar/mm** contra **2,189 bar/mm** da solução analítica
de lei das potências (0,6%) — o mesmo valor é reproduzido pelo integrador 1D do STEP e pelo canal
paramétrico. Limitações (viscoelasticidade, superfície livre e canal 3D completo) estão declaradas em
`03_Relatorios_e_Documentacao/AVALIACAO_MELHORIA_MATRIZ_3_JONATHA.md`.

Última execução (v27.0): **36 itens verificados, 19 conformes, 2 não conformes, 15 informativos**.
Resultado completo em `03_Relatorios_e_Documentacao/AUDITORIA_GEOMETRICA_MATRIZ_JONATHA.md` e
diagnóstico comparativo em `03_Relatorios_e_Documentacao/TRIAGEM_DE_PROBLEMAS_DAS_MATRIZES.md`.
