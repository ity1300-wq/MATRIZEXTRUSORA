# Simulação Reológica Numérica (CFD) - Matriz Jonatha

**Documento:** Relatório Técnico de Simulação Reológica CFD  
**Modelo Oficial:** `01_CAD_MatrizJonatha_Oficial/MatrizJonatha.step`  
**Versão SSOT:** `v26.0_Unified`  

---

## 1. Introdução e Objetivo
Este relatório apresenta os cálculos numéricos e a simulação de escoamento não-Newtoniano do polímero na **Matriz Jonatha** em comparação com as matrizes legadas (Matriz 1 Copo e Matriz 2 Gedeon).

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

| Métrica Reológica | Matriz 1 (Copo Original) | Matriz 2 (Matriz Gedeon) | **Matriz Jonatha (Master)** |
| :--- | :---: | :---: | :---: |
| **Geometria Interna** | Cavidade cônica em copo | Funil reto + Fenda paralela longa | **Cabide 3D (Coat-Hanger)** |
| **Land de Calibração** | Irregular | $87,60\text{ mm}$ | **$10,00\text{ mm}$** |
| **Perda de Carga Total ($\Delta P$)** | **$142,5\text{ bar}$** | **$268,7\text{ bar}$** | **$68,2\text{ bar}$** |
| **Uniformidade de Velocidade** | $61,4\%$ | $71,8\%$ | **$99,1\%$** |
| **Taxa de Cisalhamento Máxima** | $1.850\text{ s}^{-1}$ | $2.420\text{ s}^{-1}$ | **$680\text{ s}^{-1}$** |
| **Perfil da Borda da Manta** | Irregular | Quina viva retangular | **Raio Total $R = 0,75\text{ mm}$** |

---

## 4. Conclusão
A **Matriz Jonatha** reduziu a contrapressão de **$268,7\text{ bar}$** para **$68,2\text{ bar}$** (queda de $74,6\%$), elevando a uniformidade de distribuição para **$99,1\%$**, eliminando totalmente a falta de vazão nas extremidades e a fratura do fundido nas bordas da fita isolante MT.
