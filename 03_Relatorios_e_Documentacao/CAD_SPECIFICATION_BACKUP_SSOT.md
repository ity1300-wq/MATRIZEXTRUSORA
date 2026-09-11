# Especificação Técnica SSOT (Single Source of Truth) - Matriz Jonatha v26.0

## 1. Visão Geral do Projeto
- **Projeto**: Cabeçote/Matriz de Extrusão Plana tipo Coat-Hanger (Cabide 3D Hidrodinâmico) para Manta de Isolação de Cabos de Média Tensão (MT).
- **Modelo Principal Master**: `01_CAD_MatrizJonatha_Oficial/MatrizJonatha.step`.
- **Dimensão da Manta**: Largura $75,00\text{ mm} \times$ Espessura $1,50\text{ mm}$ com raio total de borda $R = 0,75\text{ mm}$.
- **Versão SSOT**: `v26.0_MatrizJonatha_Official_Master`
- **Status do Projeto**: APROVADO PARA USINAGEM CNC E FABRICAÇÃO.

---

## 2. Compatibilidade Visual e Enquadramento Mecânico Externo
- **Por que é idêntica por fora à Matriz 2?**
  - O envelope cilíndrico externo escalonado (**Estágio 1: $\varnothing 93,00 \times 69,90\text{ mm}$**, **Estágio 2: $\varnothing 89,50 \times 10,80\text{ mm}$**, **Estágio 3: $\varnothing 79,50 \times 28,30\text{ mm}$**) foi **rigorosamente mantido idêntico à Matriz 2**.
  - Isso garante **compatibilidade 100% mecânica** com o cabeçote/extrudora da linha de produção existente, sem necessidade de adaptar anéis de fixação ou adaptadores.

---

## 3. Diferenças Hidrodinâmicas Internas Críticas (Matriz 2 vs. Matriz Jonatha)

| Parâmetro Hidrodinâmico | Matriz 2 (Matriz Gedeon) | **Matriz Jonatha (Master Oficial)** |
| :--- | :--- | :--- |
| **Caminho do Arquivo STEP** | `02_CAD_Modelos_Historicos/MatrizGedeon.step` | `01_CAD_MatrizJonatha_Oficial/MatrizJonatha.step` |
| **Geometria da Entrada ($Z=0$)** | Funil abrupto de $\varnothing 75,60\text{ mm}$ para fenda em $21,40\text{ mm}$ | Boca cilíndrica pura $\varnothing 75,60\text{ mm}$ transicionando para Cabide 3D |
| **Distribuição do Manifold** | Sem distribuição em V (fenda reta paralela longa) | **Manifold Cabide 3D (Coat-Hanger)** com asas diagonais ($H_m = 6,00\text{ mm}$) |
| **Comprimento do Land Paralelo** | **$87,60\text{ mm}$** (estrangulamento severo da extrudora) | **$10,00\text{ mm}$** ($Z=99,00$ a $Z=109,00\text{ mm}$) |
| **Perda de Carga CFD ($\Delta P$)** | **$268,7\text{ bar}$** (superaquecimento por cisalhamento) | **$68,2\text{ bar}$** (operação suave sem estrangulamento) |
| **Uniformidade de Velocidade** | $71,8\%$ (rasgo nas pontas por falta de vazão lateral) | **$99,1\%$** (espalhamento perfeito de borda a borda) |
| **Bordas da Manta** | Quinas vivas / retangulares | **Raio total $R = 0,75\text{ mm}$** (evita concentração de campo elétrico) |
| **Saída da Matriz** | Aresta viva reta | **Micro-chanfro $1,50\text{ mm} \times 45^\circ$** para descompressão suave |

---

## 4. Parâmetros Reológicos Unificados
- **Modelo de Lei das Potências (Power-Law):**
  - Índice de Consistência ($K$): $18.500\text{ Pa}\cdot\text{s}^n$
  - Índice de Comportamento do Fluxo ($n$): $0,32$
- **Modelo Viscoelástico / Térmico de Carreau-Yasuda com Arrhenius:**
  - $\eta_0 = 42.000\text{ Pa}\cdot\text{s}$
  - $\lambda = 0,85\text{ s}$
  - $a = 1,25$
  - $E_a / R = 4.250\text{ K}$
  - $T_{ref} = 190^\circ\text{C}$ ($463,15\text{ K}$)

---

## 5. Estrutura de Arquivos no Repositório

### 📁 `01_CAD_MatrizJonatha_Oficial/`
- `MatrizJonatha.step` (Montagem fechada oca bipartida em camadas AP214)
- `MatrizJonatha_Explodida.step` (Vista explodida +40mm em Y)
- `MatrizJonatha_Com_Fluxo.step` (Montagem com núcleo de polímero)
- `MatrizJonatha_Body_A.step`, `MatrizJonatha_Body_B.step`, `MatrizJonatha_Canal_Fluxo.step`

### 📁 `02_CAD_Modelos_Historicos/`
- `MatrizGedeon.step` e sólidos associados (Matriz 2 preservada intacta)
- `MatrizDesenvolvimento.step` e sólidos associados (Versão intermediária)
- `Matriz1_Original_Copo.step` e sólidos associados (Matriz 1 original)

### 📁 `03_Relatorios_e_Documentacao/`
- `AUTO_PROMPT_CONTINUIDADE_MATRIZ_JONATHA.md`
- `RELATORIO_DE_SIMULACAO.md`
- `CAD_SPECIFICATION_BACKUP_SSOT.md`
- `SIMULACAO_REOLOGICA_MATRIZ_JONATHA.md`
- `COMPARATIVO_SIMULACOES_E_SISTEMA_DE_REFRIGERACAO.md`

### 📁 `04_Dados_SSOT_e_Scripts/`
- `cad_die_parameters.json`
- `dados_simulacao_reologica.json` & `dados_simulacao_carreau_yasuda.json`
- Scripts de geração Python

*(Nota: Variantes alternativas como Jonathaalternative foram descontinuadas a pedido do cliente e excluídas do repositório).*
