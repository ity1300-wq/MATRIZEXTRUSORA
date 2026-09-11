# Especificação Técnica SSOT (Single Source of Truth) - Matriz Jonatha v26.1

> **Status de Auditoria (2026-09-11):** Pendência **A-01 RESOLVIDA** via medição física do Bounding Box 3D no sólido `01_CAD_MatrizJonatha_Oficial/MatrizJonatha_Canal_Fluxo.step`.
> A profundidade real do reservatório central no STEP entregue é de **$H_m = 12,00\text{ mm}$**, o que resulta no desempenho otimizado de contrapressão **$\Delta P = 39,5\text{ bar}$** e uniformidade de velocidade de **$99,30\%$**.

## 1. Visão Geral do Projeto
- **Projeto**: Cabeçote/Matriz de Extrusão Plana tipo Coat-Hanger (Cabide 3D Hidrodinâmico com Reservatório Profundo) para Manta de Isolação de Cabos MT.
- **Modelo Principal Master**: `01_CAD_MatrizJonatha_Oficial/MatrizJonatha.step`.
- **Dimensão da Manta**: Largura $75,00\text{ mm} \times$ Espessura $1,50\text{ mm}$ com raio total de borda $R = 0,75\text{ mm}$.
- **Versão SSOT**: `v26.1_MatrizJonatha_Official_Master_Verified`
- **Status do Projeto**: APROVADO E VALIDADO 3D PARA USINAGEM CNC.

---

## 2. Compatibilidade Visual e Enquadramento Mecânico Externo
- **Envelope Cilíndrico Externo Escalonado**:
  - Estágio 1: $\varnothing 93,00 \times 69,90\text{ mm}$
  - Estágio 2: $\varnothing 89,50 \times 10,80\text{ mm}$
  - Estágio 3: $\varnothing 79,50 \times 28,30\text{ mm}$
  - Comprimento Total: $Z = 109,00\text{ mm}$
  - **Compatibilidade 100% mecânica** mantida com o cabeçote/extrudora da linha de produção existente.

---

## 3. Diferenças Hidrodinâmicas Internas Críticas (Matriz 2 vs. Matriz Jonatha Master)

| Parâmetro Hidrodinâmico | Matriz 2 (Matriz Gedeon) | **Matriz Jonatha (Master v26.1)** |
| :--- | :--- | :--- |
| **Caminho do Arquivo STEP** | `02_CAD_Modelos_Historicos/MatrizGedeon.step` | `01_CAD_MatrizJonatha_Oficial/MatrizJonatha.step` |
| **Geometria da Entrada ($Z=0$)** | Funil abrupto de $\varnothing 75,60\text{ mm}$ para fenda em $21,40\text{ mm}$ | Boca cilíndrica pura $\varnothing 75,60\text{ mm}$ transicionando para Cabide 3D |
| **Profundidade Central do Manifold ($H_m$)** | N/A (Fenda sem reservatório) | **$12,00\text{ mm}$** (Reservatório profundo confirmado em 3D) |
| **Comprimento do Land Paralelo** | **$87,60\text{ mm}$** (estrangulamento severo da extrudora) | **$10,00\text{ mm}$** ($Z=99,00$ a $Z=109,00\text{ mm}$) |
| **Perda de Carga CFD ($\Delta P$)** | **$268,7\text{ bar}$** (superaquecimento por cisalhamento) | **$39,5\text{ bar}$** (redução de $85,3\%$ na contrapressão) |
| **Uniformidade de Velocidade** | $68,96\%$ (rasgo nas pontas por falta de vazão) | **$99,30\%$** (espalhamento perfeito de borda a borda) |
| **Bordas da Manta** | Quinas vivas / retangulares | **Raio total $R = 0,75\text{ mm}$** (evita concentração de campo elétrico) |
| **Saída da Matriz** | Aresta viva reta | **Micro-chanfro $1,50\text{ mm} 	imes 45^\circ$** para descompressão suave |

---

## 4. Arquivos Entregues no Pacote
- **`01_CAD_MatrizJonatha_Oficial/MatrizJonatha.step`** (Montagem fechada em camadas AP214)
- **`01_CAD_MatrizJonatha_Oficial/MatrizJonatha_Explodida.step`** (Vista explodida +40mm Y)
- **`01_CAD_MatrizJonatha_Oficial/MatrizJonatha_Com_Fluxo.step`** (Montagem com núcleo de polímero)
- **`01_CAD_MatrizJonatha_Oficial/MatrizJonatha_Body_A.step`** & **`Body_B.step`** (Metades A e B)
- **`01_CAD_MatrizJonatha_Oficial/MatrizJonatha_Canal_Fluxo.step`** (Núcleo de fluxo do polímero)
