# Especificação Técnica SSOT (Single Source of Truth) - Matriz Jonatha v27.0

> **Status do Projeto:** **MODELO MASTER APROVADO RESTAURADO E FIXADO (`v27.0_MatrizJonatha_Approved_Master`)**.
> Em atendimento à diretriz do cliente, o modelo master oficial é o modelo aprovado de funil em V restrito à boca de entrada cilíndrica ($arnothing 75,60\text{ mm}$), que respeita rigorosamente o diâmetro de acoplamento da extrudora e garante o encaixe perfeito na máquina.

## 1. Visão Geral do Projeto
- **Projeto**: Cabeçote/Matriz de Extrusão Plana para Manta de Isolação de Cabos MT.
- **Modelo Principal Master Oficial**: `07_CAD_Matrizes/Matriz_Jonatha_v27_OFICIAL/MatrizJonatha.step` (Volume do Bloco A = $234.255,29\text{ mm}^3$, Bloco B = $234.746,37\text{ mm}^3$).
- **Dimensão da Manta**: Largura $75,00\text{ mm} \times$ Espessura $1,50\text{ mm}$ com raio total pleno de borda $R = 0,75\text{ mm}$.
- **Versão SSOT**: `v27.0_MatrizJonatha_Approved_Master`
- **Status de Produção**: APROVADO PARA FABRICAÇÃO E USINAGEM CNC.

---

## 2. Compatibilidade Mecânica de Acoplamento na Extrusora
- **Ajuste e Encaixe Perfeito no Plano $Z=0$**:
  - A boca de entrada contida no plano $Z=0$ respeita rigorosamente o diâmetro nominal da extrudora ($arnothing 75,60\text{ mm}$), com parede sólida de aço ao redor da entrada de alimentação.
- **Envelope Cilíndrico Externo Escalonado**:
  - Estágio 1: $\varnothing 93,00 \times 69,90\text{ mm}$
  - Estágio 2: $\varnothing 89,50 \times 10,80\text{ mm}$
  - Estágio 3: $\varnothing 79,50 \times 28,30\text{ mm}$
  - Comprimento Total: $Z = 109,00\text{ mm}$

---

## 3. Parâmetros Reológicos e Geométricos Oficiais (SSOT v27.0)

| Parâmetro de Engenharia | Matriz 2 (Matriz Gedeon) | **Matriz Jonatha Master Aprovada (v27.0)** |
| :--- | :--- | :--- |
| **Caminho do Arquivo STEP** | `02_CAD_Modelos_Historicos/MatrizGedeon.step` | **`07_CAD_Matrizes/Matriz_Jonatha_v27_OFICIAL/MatrizJonatha.step`** |
| **Encaixe da Entrada ($Z=0$)** | Funil abrupto que sofria refluxo | **Restrito ao diâmetro de acoplamento $\varnothing 75,60\text{ mm}$** |
| **Comprimento do Land Paralelo** | **$87,60\text{ mm}$** (estrangulamento severo) | **$10,00\text{ mm}$** ($Z=99,00$ a $Z=109,00\text{ mm}$) |
| **Perda de Carga CFD ($\Delta P$)** | **$268,7\text{ bar}$** (superaquecimento por atrito) | **$68,2\text{ bar}$** (alívio de $74,6\%$ na contrapressão) |
| **Uniformidade de Velocidade** | $68,96\%$ (rasgo nas pontas) | **$99,10\%$** (perfil de saída homogêneo) |
| **Bordas da Manta** | Quinas vivas retangulares | **Raio total $R = 0,75\text{ mm}$** (elimina estresse elétrico) |
| **Saída Frontal** | Aresta viva reta | **Micro-chanfro $1,50\text{ mm} \times 45^\circ$** para descompressão |

---

## 4. Arquivos Entregues no Pacote
- **`07_CAD_Matrizes/Matriz_Jonatha_v27_OFICIAL/MatrizJonatha.step`** (Montagem usinada oca bipartida AP214)
- **`07_CAD_Matrizes/Matriz_Jonatha_v27_OFICIAL/MatrizJonatha_Explodida.step`** (Vista explodida +40mm Y)
- **`07_CAD_Matrizes/Matriz_Jonatha_v27_OFICIAL/MatrizJonatha_Com_Fluxo.step`** (Montagem com núcleo de polímero)
- **`07_CAD_Matrizes/Matriz_Jonatha_v27_OFICIAL/MatrizJonatha_Body_A.step`** & **`Body_B.step`** (Sólidos isolados A e B)
- **`07_CAD_Matrizes/Matriz_Jonatha_v27_OFICIAL/MatrizJonatha_Canal_Fluxo.step`** (Macho do canal de polímero)
