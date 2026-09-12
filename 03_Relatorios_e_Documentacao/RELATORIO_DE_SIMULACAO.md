# Relatório de Simulação Reológica e Térmica CFD - Matriz Jonatha

**Documento:** Relatório Técnico Executivo de Simulação de Escoamento de Polímero  
**Projeto:** Matriz de Extrusão Plana (Modelo Master Aprovado v27.0 - Funil V Restrito)  
**Produto Final:** Manta de Isolação para Acessórios de Cabos de Média Tensão (MT)  
**Dimensões da Manta:** Largura $75,00\text{ mm} \times$ Espessura $1,50\text{ mm}$ (Bordas Arredondadas $R = 0,75\text{ mm}$)  
**Modelo Oficial Master:** `01_CAD_MatrizJonatha_Oficial/MatrizJonatha.step` (Aço P20 / AISI H13 Nitretado)  
**Versão SSOT:** `v27.0_MatrizJonatha_Approved_Master`  
**Data:** 11 de Setembro de 2026

---

## 1. Resumo Executivo

Este relatório apresenta os resultados completos da simulação de Dinâmica dos Fluidos Computacional (CFD) reológica e térmica para a **Matriz Jonatha**. O objetivo principal da simulação foi validar o canal de fluxo tridimensional do tipo **Funil Hidrodinâmico em V Restrito na Entrada Cilíndrica ($arnothing 75,60\text{ mm}$)**, eliminando definitivamente os graves problemas observados nas versões anteriores (Matriz 1 e Matriz 2), tais como:
1. **Estrangulamento e sobrepressão** da extrudora ($268,7\text{ bar}$ na Matriz 2).
2. **Rasgo e afinamento nas bordas da manta** ("a manta sai pior conforme vai esquentando").
3. **Concentração de campo elétrico** provocada por quinas vivas retangulares.

A simulação CFD comprovou que a **Matriz Jonatha** equalizou a distribuição de velocidade ao longo de toda a largura de $75,00\text{ mm}$ com **99,10% de uniformidade**, mantendo a contrapressão em níveis seguros (**$68,2\text{ bar}$**, redução de **$74,6\%$** em relação à Matriz 2) e eliminando as tensões residuais nas bordas.

---

## 2. Modelagem Reológica e Condições de Contorno

### 2.1. Propriedades do Polímero Extrudado
- **Material:** Composto Polimérico Elastomérico para Isolação Elétrica (EPR / XLPE / PVC Modificado).
- **Vazão Volumétrica de Extrusão ($Q$):** $15,0\text{ cm}^3/\text{s}$ ($54,0\text{ kg/h}$).
- **Temperatura Nominal de Processamento:** $190^\circ\text{C}$ ($463,15\text{ K}$).
- **Densidade ($ho$):** $1,40\text{ g/cm}^3$

### 2.2. Modelo Não-Newtoniano de Lei das Potências (Power-Law)
Para a análise de perda de carga e perfil de velocidade na cavidade 3D:
$$\eta(\dot{\gamma}) = K \cdot \dot{\gamma}^{n-1}$$
- **Índice de Consistência ($K$):** $18.500\text{ Pa}\cdot\text{s}^n$
- **Índice de Comportamento do Fluxo ($n$):** $0,32$ (Comportamento fortemente pseudoplástico / *shear-thinning*)

### 2.3. Modelo Viscoelástico e Térmico de Carreau-Yasuda com Arrhenius
Para avaliar a influência da temperatura na viscosidade e no rasgo de borda:
$$\eta(\dot{\gamma}, T) = a_T \cdot \eta_0 \left[ 1 + (\lambda \cdot a_T \cdot \dot{\gamma})^a \right]^{\frac{n-1}{a}}$$
$$a_T = \exp \left[ \frac{E_a}{R} \left( \frac{1}{T} - \frac{1}{T_{ref}} \right) \right]$$
- **Viscosidade de Cisalhamento Zero ($\eta_0$):** $42.000\text{ Pa}\cdot\text{s}$
- **Tempo de Relaxação ($\lambda$):** $0,85\text{ s}$
- **Parâmetro Yasuda ($a$):** $1,25$
- **Energia de Ativação Térmica ($E_a / R$):** $4.250\text{ K}$

---

## 3. Resultados Comparativos das Matrizes (CFD Reológico)

> Dados unificados e verificados conforme `04_Dados_SSOT_e_Scripts/dados_simulacao_reologica.json`.

| Parâmetro Reológico / Hidrodinâmico | Matriz 1 (Copo Oco Original) | Matriz 2 (Matriz Gedeon) | **Matriz Jonatha Master (v27.0)** |
| :--- | :--- | :--- | :--- |
| **Geometria do Canal Interno** | Cavidade cônica em copo | Funil reto + Fenda paralela longa | **Funil V Restrito na Entrada Cilíndrica** |
| **Encaixe no Plano $Z=0$** | Irregular | Sofrer refluxo no funil | **Restrito ao diâmetro nominal $\varnothing 75,60\text{ mm}$** |
| **Comprimento do Land de Calibração** | Irregular | $87,60\text{ mm}$ (Fenda $75 \times 1,5\text{ mm}$) | **$10,00\text{ mm}$** ($Z=99,00$ a $109,00\text{ mm}$) |
| **Perda de Carga Total ($\Delta P$)** | $185,4\text{ bar}$ | **$268,7\text{ bar}$** (Estrangulamento) | **$68,2\text{ bar}$** (Alívio de $74,6\%$) |
| **Uniformidade de Velocidade na Saída** | $54,73\%$ | $68,96\%$ (Falta vazão nas pontas) | **$99,10\%$** (Perfil plano perfeito) |
| **Tensão de Cisalhamento na Parede ($\tau_w$)** | $160,12\text{ kPa}$ | $157,11\text{ kPa}$ | **$128,44\text{ kPa}$** (Longe do estresse crítico) |
| **Perfil da Borda da Manta** | Irregular | Quina viva retangular | **Raio Total $R = 0,75\text{ mm}$** |
| **Risco de Fratura do Fundido (*Melt Fracture*)** | Altíssimo | Crítico nas quinas | **Zero / Eliminado** |

---

## 4. Análise Térmica e Degradação Reológica por Aquecimento

### 4.1. Variação da Viscosidade e Contrapressão com a Temperatura
A simulação computacional explicou quantitativamente o relato operacional: *"a manta sai pior conforme vai esquentando"*.

> Dados unificados com `04_Dados_SSOT_e_Scripts/dados_simulacao_carreau_yasuda.json`.

| Temperatura do Bloco da Matriz | Viscosidade Aparente no Land ($\eta$) | Contrapressão ($\Delta P$) | Resistência de Fundido (*Melt Strength*) | Estabilidade de Borda |
| :---: | :---: | :---: | :---: | :---: |
| **$50^\circ\text{C}$ (Frio / Início)** | $1.850\text{ Pa}\cdot\text{s}$ | $68,2\text{ bar}$ | Alta ($100\%$) | **Estável (Sem rasgo)** |
| **$65^\circ\text{C}$ (Ideal)** | $1.420\text{ Pa}\cdot\text{s}$ | $52,4\text{ bar}$ | Boa ($88\%$) | **Estável (Excelente acabamento)** |
| **$80^\circ\text{C}$ (Aquecido)** | $1.080\text{ Pa}\cdot\text{s}$ | $39,8\text{ bar}$ | Média ($65\%$) | Vibração leve nas bordas |
| **$100^\circ\text{C}$ (Superaquecido)** | $720\text{ Pa}\cdot\text{s}$ | $26,5\text{ bar}$ | Baixa ($43\%$) | **Rasgo de Borda (*Edge Tearing*)** |

### 4.2. Explicação Científica do Fenômeno
1. Conforme a matriz aquece além de $80^\circ\text{C}-100^\circ\text{C}$, a viscosidade aparente do polímero cai em mais de **60%**.
2. Essa queda abrupta reduz a **resistência do fundido (*melt strength*)**, tornando o polímero incapaz de suportar a tensão de estiramento na saída da matriz.
3. Nas bordas laterais, onde o gradiente de resfriamento em contato com o ar é maior, ocorre um diferencial de tensão de cisalhamento que inicia o **rasgo na borda (*edge tearing*)**.

---

## 5. Diretrizes para Projeto do Sistema de Refrigeração e Usinagem CNC

Para manter a **Matriz Jonatha** operando na janela térmica ideal de $50^\circ\text{C} - 60^\circ\text{C}$:

1. **Canais Internos de Circulação Térmica:**
   - Furar canais longitudinais de $\varnothing 8,0\text{ mm}$ no corpo de aço dos Blocos A e B para circulação de água/óleo aquecido a $50^\circ\text{C}-55^\circ\text{C}$.
2. **Poço para Termopar:**
   - Instalar um poço de sensoriamento de temperatura a $5,0\text{ mm}$ da parede da cavidade do land ($Z = 100,0\text{ mm}$).
3. **Usinagem CNC e Polimento Espelhado:**
   - **Rugosidade Superficial Target:** $Ra \le 0,4\,\mu\text{m}$ na cavidade.
   - **Polimento Espelhado:** Executado **rigorosamente no sentido longitudinal do fluxo** ($Z$), evitando riscos transversais que iniciem acúmulo de material envelhecido (*degradation spots*).

---

## 6. Conclusão da Simulação

A **Matriz Jonatha (`01_CAD_MatrizJonatha_Oficial/MatrizJonatha.step`)** é a **solução definitiva e otimizada** para a fabricação da manta de isolação de Média Tensão. Seu canal de fluxo do tipo **Funil V Restrito na Entrada Cilíndrica ($arnothing 75,60\text{ mm}$)** garante distribuição perfeitamente uniforme do elastômero ($99,10\%$), elimina os rasgos de borda, reduz a contrapressão em **$74,6\%$** (de $268,7\text{ bar}$ para $68,2\text{ bar}$) em relação à Matriz 2 e preserva a integridade mecânica e dielétrica do cabo elétrico.
