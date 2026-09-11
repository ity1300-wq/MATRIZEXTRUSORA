# ESPECIFICAÇÃO TÉCNICA DEFINITIVA DA MATRIZ 3
**Projeto**: Matriz de Extrusão Bipartida Otimizada para Mastique Resistivo (Média Tensão)  
**Data**: 2026-09-10  
**Versão da Especificação**: `v1.0_Final_Aprovação`  
**Normas**: ABNT NBR 10067 / ISO 128 / STEP AP214/AP242  

---

## 1. OBJETIVO DO PROJETO E DIAGNÓSTICO REOLÓGICO

### 1.1 Objetivo Industrial
Projetar e entregar o modelo CAD 3D parametrizado de nível de manufatura (STEP AP214) para a **Matriz 3 (Bipartida e Otimizada)**, visando a extrusão contínua da fita de mastique resistivo de controle de campo para acessórios de Média Tensão (MT), erradicando falhas de qualidade e gargalos de produção.

### 1.2 Problemas da Produção Solucionados
1. **Eliminação do *Sharkskin* e *Edge Tearing* (Falhas a Frio e a Quente da Matriz 1)**:
   - A Matriz 1 possuía parede cega de $90^\circ$ na entrada e cantos vivos de $90^\circ$ na saída, rasgando as bordas do mastique e exigindo o paliativo manual de empilhar peso morto sobre a manta fora da linha.
2. **Eliminação do Refluxo Hidráulico (Falha da Matriz 2)**:
   - A Matriz 2 (copo oco) gerou restrição de área abrupta, estrangulando o fluxo e fazendo o material retornar pelo funil de alimentação da extrusora.

---

## 2. ESPECIFICAÇÕES GEOMÉTRICAS RIGOROSAS (SSOT)

### 2.1 Envelope Cilíndrico Externo (100% Fidedigno à Matriz Documentada)
- **Comprimento Total Z**: $109,00\text{ mm}$
- **Estágio 1** ($Z = 0,00$ a $69,90\text{ mm}$): Cilindro de $\varnothing 93,00\text{ mm}$.
- **Estágio 2** ($Z = 69,90$ a $80,70\text{ mm}$): Cilindro de $\varnothing 89,50\text{ mm}$ (alívio de canal).
- **Estágio 3** ($Z = 80,70$ a $109,00\text{ mm}$): Cilindro de $\varnothing 79,50\text{ mm}$.
- **Face Traseira de Entrada ($Z = 0,00\text{ mm}$)**: Boca circular perfeita de $\varnothing 75,60\text{ mm}$ acoplada ao canhão da extrusora.

### 2.2 Canal de Fluxo Interno (Distribuidor Coat-Hanger / Rabo-de-Peixe Hydrodinâmico)
- **Geometria de Transição**: Transição reológica contínua do furo circular de entrada ($\varnothing 75,60\text{ mm}$ em $Z=0$) até a fenda retangular de $75,00\text{ mm} \times 1,50\text{ mm}$ em $Z=99,00\text{ mm}$.
- **Balanço de Pressão e Vazão**: Perfil com variação progressiva de perda de carga que iguala a velocidade de saída do mastique nas bordas ($X = \pm 37,50\text{ mm}$) e no centro ($X = 0$), zerando as tensões de cisalhamento causadoras do *sharkskin*.

### 2.3 Land Paralelo de Calibração Final ($Z = 99,00$ a $109,00\text{ mm}$)
- **Dimensão da Seção**: $75,00\text{ mm}$ de largura por $1,50\text{ mm}$ de espessura.
- **Formato das Bordas Laterais**: **Semicírculo Pleno de Raio $R = 0,75\text{ mm}$** ($R0,75\text{ mm}$ contínuo).
  - *Justificativa Elétrica*: Elimina quinas vivas para impedir a concentração de campo elétrico na isolação de Média Tensão do cliente.
- **Comprimento Axial**: **Exatos $10,00\text{ mm}$** de canal reto e paralelo de calibração.

### 2.4 Micro-Chanfro de Alívio na Saída Frontal ($Z = 109,00\text{ mm}$)
- **Ângulo e Dimensão**: Chanfro de **$1,50\text{ mm} \times 45^\circ$** divergente (abrindo para fora).
- *Justificativa Reológica*: Alivia o atrito do atrito *stick-slip* durante o inchaço do polímero (*Die Swell*).

### 2.5 Bipartição e Sistema de Alinhamento ($Y = 0$)
- **Plano de Partição**: Divisão perfeitamente horizontal no plano $Y = 0$, resultando em dois corpos independentes:
  - **`Body_A`** (Metade Inferior, $Y \le 0$)
  - **`Body_B`** (Metade Superior, $Y \ge 0$)
- **Furos de Alinhamento**: 2 furos cegos de $\varnothing 4,00\text{ mm} \times 12,00\text{ mm}$ de profundidade na face $Y=0$ do `Body_A`, posicionados em $Z = 54,50\text{ mm}$ e $X = \pm 41,50\text{ mm}$ (distância entre centros de $83,00\text{ mm}$).

---

## 3. FORMATO DOS ARQUIVOS E ENTREGÁVEIS DE CAD/CAM

O projeto será entregue **exclusivamente em arquivos CAD tridimensionais no padrão industrial STEP AP214/AP242**:
1. **`MatrizDesenvolvimento.step`**: Montagem STEP da matriz usinada fechada com a cavidade oca e os furos de alinhamento.
2. **`MatrizDesenvolvimento_Explodida.step`**: Montagem com a metade superior deslocada $+40\text{ mm}$ em $Y$ para inspeção tridimensional direta da calha interna usinada.
3. **`MatrizDesenvolvimento_Com_Fluxo.step`**: Montagem incluindo o sólido do canal de polímero (útil para fabricação do eletrodo de Eletroerosão por Penetração - EDM).
4. **`MatrizDesenvolvimento_Body_A.step`** e **`MatrizDesenvolvimento_Body_B.step`**: Arquivos individuais das metades usinadas de aço.
5. **`MatrizGedeon.step`**: Mantida 100% intacta como matriz máster original de referência.
