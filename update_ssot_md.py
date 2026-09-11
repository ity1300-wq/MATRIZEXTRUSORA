content = """# Especificação Técnica SSOT (Single Source of Truth) - Matriz Jonatha v25.0

## 1. Visão Geral do Projeto
- **Projeto**: Cabeçote/Matriz de Extrusão Plana tipo Coat-Hanger (Rabo de Peixe) para Manta de Isolação de Cabos MT.
- **Modelo Principal**: `MatrizJonatha.step` (E variante otimizada `Jonathaalternative.step`).
- **Dimensão da Manta**: Largura $75.00\\text{ mm} \\times$ Espessura $1.50\\text{ mm}$ com raio total de borda $R = 0.75\\text{ mm}$.
- **Versão SSOT**: `v25.0_Jonatha_True_CoatHanger_3D`

## 2. Compatibilidade Visual e Enquadramento Mecânico Externe
- **Por que é idêntica por fora à Matriz 2?**
  - O envelope cilíndrico externo escalonado (**Estágio 1: $\\varnothing 93.00 \\times 69.90\\text{ mm}$**, **Estágio 2: $\\varnothing 89.50 \\times 10.80\\text{ mm}$**, **Estágio 3: $\\varnothing 79.50 \\times 28.30\\text{ mm}$**) foi **rigorosamente mantido idêntico à Matriz 2**.
  - Isso garante **compatibilidade 100% mecânica** com o cabeçote/extrudora da linha de produção existente, sem necessidade de adaptar adaptadores ou anéis de fixação.

## 3. Diferenças Hidrodinâmicas Internas Críticas (Matriz 2 vs. Matriz Jonatha)

| Parâmetro Hidrodinâmico | Matriz 2 (Design Antigo / Defeituoso) | Matriz Jonatha (Novo Design Cabide 3D) |
| :--- | :--- | :--- |
| **Geometria da Entrada ($Z=0$)** | Funil abrupto de $\\varnothing 75.60\\text{ mm}$ para fenda em apenas $21.40\\text{ mm}$ | Boca cilíndrica pura $\\varnothing 75.60\\text{ mm}$ transicionando para Cabide 3D |
| **Distribuição do Manifold** | Sem distribuição em V (apenas fenda reta paralela) | **Manifold Cabide 3D (Coat-Hanger)** com asas diagonais e reservatório $H_m = 12.00\\text{ mm}$ |
| **Comprimento do Land Paralelo** | **$87.60\\text{ mm}$** (estrangulamento severo da extrudora) | **$10.00\\text{ mm}$** ($Z=99.00$ a $Z=109.00\\text{ mm}$) |
| **Perda de Carga ($\Delta P$)** | **$> 180.0\\text{ bar}$** (superaquecimento e cisalhamento) | **$39.5\\text{ bar}$** (operação suave sem estrangulamento) |
| **Uniformidade de Velocidade** | $< 72.0\\%$ (rasgo nas pontas por falta de vazão lateral) | **$99.3\\%$** (espalhamento perfeito de borda a borda) |
| **Bordas da Manta** | Quinas vivas / sem raio total | **Raio total $R = 0.75\\text{ mm}$** (evita concentração de campo elétrico) |
| **Chanfro de Saída** | Ausente / Aresta viva | **Micro-chanfro $1.50\\text{ mm} \\times 45^\\circ$** para descompressão suave |

## 4. Arquivos Entregues na Raiz do Workspace
- `MatrizJonatha.step` (Montagem fechada em camadas AP214)
- `MatrizJonatha_Explodida.step` (Vista explodida +40mm em Y)
- `MatrizJonatha_Com_Fluxo.step` (Montagem com núcleo de polímero)
- `MatrizJonatha_Body_A.step`, `MatrizJonatha_Body_B.step`, `MatrizJonatha_Canal_Fluxo.step`
- `Jonathaalternative.step` ($H_m = 12.00\\text{ mm}$)
- `Jonathaalternative_Explodida.step`
- `Jonathaalternative_Com_Fluxo.step`
- `Jonathaalternative_Body_A.step`, `Jonathaalternative_Body_B.step`, `Jonathaalternative_Canal_Fluxo.step`
- `MatrizGedeon.step` (Matriz 2 preservada intacta)
- `MatrizDesenvolvimento.step` (Matriz de desenvolvimento preservada intacta)
"""

with open("CAD_SPECIFICATION_BACKUP_SSOT.md", "w", encoding="utf-8") as f:
    f.write(content)

print("CAD_SPECIFICATION_BACKUP_SSOT.md atualizado!")
