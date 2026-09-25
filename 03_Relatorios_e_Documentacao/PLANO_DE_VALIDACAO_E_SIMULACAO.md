# PLANO DE VALIDAÇÃO CIENTÍFICA E SIMULAÇÃO PREVENTIVA

> **⚠️ Nota de correção — 2026-09-25.** Este é o plano como foi escrito no começo do projeto, e ele **promete o
> que não foi medido**. As frases "Prova matematicamente que a fita sairá perfeitamente retilínea, sem arrasto
> nas pontas e sem o efeito serrilhado (*sharkskin*)", "NÃO haverá refluxo pelo funil de alimentação" e "NÃO
> ocorrerão os rasgos de borda" **não têm resultado atrás**: o CFD com o critério de "diferença de velocidade
> centro×bordas < 2 %" nunca foi rodado (e em 2026-09-22 o dono do projeto adiou o CFD de propósito), e os
> números de ΔP que este plano citava já estavam marcados como não reproduzíveis em
> `TRIAGEM_DE_PROBLEMAS_DAS_MATRIZES.md` (P6). Some a isso um erro de conceito: o denteado que aparece na manta
> é **rasgo de borda**, não *sharkskin* (fratura de superfície do fundido), e têm remédios diferentes. O estado
> real, medido, está em `AVALIACAO_V30_X_FLUXO_2026-09-25.md`. O texto abaixo fica **como estava**, sem edição,
> para que se veja de onde o projeto partiu — leia as "Promessas" deste arquivo como hipóteses de plano, não
> como resultados.
>
**Projeto**: MatrizJonatha Master  
**Objetivo**: Eliminar o "achismo" e validar matematicamente/computacionalmente a `MatrizJonatha.step` antes do investimento em usinagem CNC de aço.  

---

## 1. SIMULAÇÃO REOLÓGICA CFD (COMPUTATIONAL FLUID DYNAMICS)

A ferramenta mais conclusiva para eliminar qualquer dúvida na indústria de extrusão é a simulação de escoamento não-newtoniano via **CFD Reológico** (softwares como *ANSYS Fluent*, *Moldex3D*, *OpenFOAM* ou *Cadmould*), utilizando diretamente o arquivo **`MatrizJonatha_Canal_Fluxo.step`**:

### O que o mapa de simulação CFD comprova numericamente:
1. **Mapa de Perfil de Velocidade ($v_z$) na Fenda de Saída**:
   - **Critério de Sucesso**: Diferença de velocidade entre o centro ($X=0$) e as bordas ($X = \pm 37,50\text{ mm}$) menor que $2\%$.
   - **Resultado**: Prova matematicamente que a fita sairá perfeitamente retilínea, sem arrasto nas pontas e **sem o efeito serrilhado (*sharkskin*)**.
2. **Mapa de Pressão Hidráulica Interna ($\Delta P$)**:
   - **Critério de Sucesso**: Contrapressão total na entrada ($Z=0$) dentro da faixa nominal operacional da extrusora ($< 100\text{ bar}$).
   - **Resultado**: Garante que o motor e a rosca trabalharão aliviados, **comprovando que NÃO haverá refluxo pelo funil de alimentação**.
3. **Mapa de Taxa de Cisalhamento nas Paredes ($\dot{\gamma}$)**:
   - **Critério de Sucesso**: Tensão de cisalhamento na parede $\tau_w$ inferior à tensão crítica de fratura do fundido do mastique ($\tau_{crit}$).
   - **Resultado**: Confirma que **NÃO ocorrerão os rasgos de borda (*edge tearing*)**.

---

## 2. PROTOTIPAGEM RÁPIDA 3D E TESTE DE MARCADOR REOLÓGICO

Método físico prático e de baixíssimo custo antes de cortar o aço:

1. **Impressão 3D das Metades**:
   - Imprimir os arquivos **`MatrizJonatha_Body_A.step`** e **`MatrizJonatha_Body_B.step`** em impressora 3D (escala 1:1) utilizando PETG ou Resina Tough.
2. **Teste com Plastilina / Argila Colorida Marcadora**:
   - Montar a matriz impressa com parafusos e injetar argila com viscosidade calibrada contendo listras coloridas verticais.
   - Abrir a matriz bipartida e analisar a frente de avanço do fluido (*flow front*): se o padrão de cores avançar de forma perfeitamente paralela, o distribuidor Coat-Hanger está 100% validado.

---

## 3. CÁLCULO ANALÍTICO REOLÓGICO DE MANIFOLD (HAGEN-POISEUILLE MODIFICADO)

Demostração analítica do balanço de perda de carga do distribuidor Coat-Hanger:
$$\Delta P_{centro} = \Delta P_{borda} \implies \int_{0}^{L_c} \left(\frac{2\tau_w}{H_c}\right) dZ = \int_{0}^{L_e} \left(\frac{2\tau_w}{H_e}\right) dS$$

O perfil rabo-de-peixe ajusta o comprimento geométrico do caminho $S(X)$ e a altura da fenda $H(X,Z)$ para que a resistência hidráulica seja idêntica para qualquer molécula de mastique, independente da sua posição na largura.

---

## 4. ANÁLISE DE ELEMENTOS FINITOS (FEA) E ESTRUTURAL DO AÇO

Aplicação da contrapressão calculada ($100\text{ bar}$) no modelo **`MatrizJonatha.step`**:
- Confirma que a deflexão mecânica (afastamento) no plano de partição $Y=0$ é inferior a $0,005\text{ mm}$, garantindo que a fita não apresentará rebarbas de fechamento.
