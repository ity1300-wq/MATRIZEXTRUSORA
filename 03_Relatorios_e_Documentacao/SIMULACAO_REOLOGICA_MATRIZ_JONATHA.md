# Simulação Reológica Numérica (CFD) - Matriz Jonatha

**Documento:** Relatório Técnico de Simulação Reológica CFD  
**Modelo Oficial Master:** `07_CAD_Matrizes/Matriz_Jonatha_v27_OFICIAL/MatrizJonatha.step`  
**Versão SSOT:** `v27.0_MatrizJonatha_Approved_Master`  

---

## 1. Introdução e Objetivo
Este relatório apresenta os cálculos numéricos e a simulação de escoamento não-Newtoniano do polímero na **Matriz Jonatha** (Modelo Master Aprovado) em comparação com as matrizes legadas (Matriz 1 Copo e Matriz 2 Gedeon).

---

## 2. Parâmetros Reológicos e do Polímero
- **Polímero:** Composto Elastomérico Polimérico para Isolação Elétrica (EPR / XLPE / PVC Modificado).
- **Vazão Volumétrica de Extrusão ($Q$):** $15,0\text{ cm}^3/\text{s}$ ($54,0\text{ kg/h}$).
- **Temperatura Nominal:** $190^\circ\text{C}$ ($463,15\text{ K}$).

### Modelo de Lei das Potências (Power-Law):
$$\eta(\dot{\gamma}) = K \cdot \dot{\gamma}^{n-1}$$
- **Índice de Consistência ($K$):** $18.500\text{ Pa}\cdot\text{s}^n$
- **Índice de Comportamento do Fluxo ($n$):** $0,32$

---

## 3. Resultados da Simulação Numérica CFD

> Dados unificados e sincronizados com `04_Dados_SSOT_e_Scripts/dados_simulacao_reologica.json`.

| Métrica Reológica | Matriz 1 (Copo Original) | Matriz 2 (Matriz Gedeon) | **Matriz Jonatha Master (v27.0)** |
| :--- | :---: | :---: | :---: |
| **Geometria Interna** | Cavidade cônica em copo | Funil reto + Fenda paralela longa | **Funil V Restrito na Entrada Cilíndrica** |
| **Land de Calibração** | Irregular | $87,60\text{ mm}$ | **$10,00\text{ mm}$** ($Z=99 \to 109\text{ mm}$) |
| **Perda de Carga Total ($\Delta P$)** | **$185,4\text{ bar}$** | **$268,7\text{ bar}$** | **$68,2\text{ bar}$** (Redução de $74,6\%$) |
| **Uniformidade de Velocidade** | $54,73\%$ | $68,96\%$ | **$99,10\%$** (Espalhamento homogêneo) |
| **Tensão de Cisalhamento na Parede ($\tau_w$)** | $160,12\text{ kPa}$ | $157,11\text{ kPa}$ | **$128,44\text{ kPa}$** (Sem risco de estresse) |
| **Perfil da Borda da Manta** | Irregular | Quina viva retangular | **Raio Total Pleno $R = 0,75\text{ mm}$** |

---

## 4. Conclusão
A **Matriz Jonatha** reduziu a contrapressão de **$268,7\text{ bar}$** para **$68,2\text{ bar}$** (queda de $74,6\%$), elevando a uniformidade de distribuição para **$99,10\%$**, eliminando totalmente a falta de vazão nas extremidades e a fratura do fundido nas bordas da fita isolante MT.
