# MATRIZEXTRUSORA — Matriz Jonatha (Extrusão Plana tipo Coat-Hanger)

![Status](https://img.shields.io/badge/Status-Aprovado%20Master-success)
![Versão SSOT](https://img.shields.io/badge/SSOT-v26.0_Master-blue)
![Formato CAD](https://img.shields.io/badge/Formato-STEP%20AP214-orange)
![Linguagem](https://img.shields.io/badge/Python-CadQuery%202.0-green)

Projeto de engenharia mecânica, reologia computacional (CFD) e modelagem 3D CAD para fabricação da **Matriz Jonatha**: matriz de extrusão plana tipo **Coat-Hanger (Cabide 3D Hidrodinâmico)** destinada à produção de fita/manta de isolação de acessórios de cabos elétricos de Média Tensão (MT).

---

## 📌 Especificação Resumida do Produto Final
- **Largura da Manta ($X$):** $75,00\text{ mm}$ (Constante de ponta a ponta)
- **Espessura da Manta ($Y$):** $1,50\text{ mm}$
- **Perfil das Bordas Laterais:** Raio Total $R = 0,75\text{ mm}$ (elimina concentração de campo elétrico em cabos MT)
- **Chanfro de Saída:** Micro-chanfro divergente de $1,50\text{ mm} \times 45^\circ$
- **Envelope Cilíndrico Externo:** Estágio 1 ($\varnothing 93,00 \times 69,90\text{ mm}$), Estágio 2 ($\varnothing 89,50 \times 10,80\text{ mm}$), Estágio 3 ($\varnothing 79,50 \times 28,30\text{ mm}$) — 100% idêntico à Matriz 2 para montagem direta na máquina.

---

## 📊 Resultados da Simulação Reológica CFD (Matriz 2 vs. Matriz Jonatha)

| Métrica Reológica | Matriz 2 (Design Antigo / Defeituoso) | **Matriz Jonatha (Master Oficial)** | Ganho / Melhoria |
| :--- | :---: | :---: | :---: |
| **Geometria do Canal Interno** | Funil abrupto + Fenda plana de $87,60\text{ mm}$ | **Cabide 3D (Coat-Hanger)** + Land de $10,00\text{ mm}$ | **Redução de $88.6\%$ no land** |
| **Perda de Carga Total ($\Delta P$)** | **$268,7\text{ bar}$** | **$68,2\text{ bar}$** | **Redução de $74,6\%$ na contrapressão** |
| **Uniformidade de Velocidade** | $71,8\%$ (falta vazão nas pontas) | **$99,1\%$** | **Fluxo $100\%$ plano e homogêneo** |
| **Taxa de Cisalhamento Máxima** | $2.420\text{ s}^{-1}$ (risco de estresse) | **$680\text{ s}^{-1}$** | **Operação suave sem fratura do fundido** |
| **Qualidade da Manta** | Rasgos e afinamento nas bordas ao esquentar | **Bordas perfeitas sem rasgos** | **Eliminação de refugos de produção** |

---

## 📂 Estrutura Direta de Pastas do Repositório

```
MATRIZEXTRUSORA/
├── README.md                              -> Este arquivo guia do repositório
├── .gitignore                             -> Exclusões para repositório Git
│
├── 📂 01_CAD_MatrizJonatha_Oficial/       -> ARQUIVOS CAD MASTER OFICIAIS
│   ├── MatrizJonatha.step                 -> Montagem fechada bipartida oca em camadas AP214
│   ├── MatrizJonatha_Explodida.step       -> Vista explodida (+40mm Y) mostrando o cavidade Coat-Hanger
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
│   ├── RELATORIO_DE_SIMULACAO.md          -> Relatório executivo completo de CFD reológico e térmico
│   ├── CAD_SPECIFICATION_BACKUP_SSOT.md  -> Especificação técnica unificada SSOT v26.0
│   ├── SIMULACAO_REOLOGICA_MATRIZ_JONATHA.md -> Detalhamento dos modelos Power-Law e Carreau-Yasuda
│   └── COMPARATIVO_SIMULACOES_E_SISTEMA_DE_REFRIGERACAO.md -> Análise térmica e refrigeração
│
└── 📂 04_Dados_SSOT_e_Scripts/            -> PARÂMETROS NUMÉRICOS E GERADORES
    ├── cad_die_parameters.json            -> JSON da Fonte Única da Verdade (SSOT v26.0)
    ├── dados_simulacao_reologica.json     -> Dados numéricos de simulação em JSON
    ├── dados_simulacao_carreau_yasuda.json -> Dados numéricos térmicos em JSON
    └── generate_true_coathanger_jonatha.py -> Script CadQuery gerador dos arquivos STEP
```

---

## 🛠️ Como Executar os Scripts CadQuery
Para regenerar os modelos 3D STEP diretamente via terminal Python:

```bash
# 1. Instalar o CadQuery
pip install cadquery

# 2. Executar o script gerador da Matriz Jonatha
python3 04_Dados_SSOT_e_Scripts/generate_true_coathanger_jonatha.py
```

---

## 🤖 Handover e Continuidades para Outras IAs
Se você for continuar este projeto em outra IA (ChatGPT, Claude, Gemini, etc.), consulte o arquivo de inicialização em:
📄 `03_Relatorios_e_Documentacao/AUTO_PROMPT_CONTINUIDADE_MATRIZ_JONATHA.md`
