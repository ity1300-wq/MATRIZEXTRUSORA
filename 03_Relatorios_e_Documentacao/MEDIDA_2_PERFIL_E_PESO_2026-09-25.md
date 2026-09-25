# 2ª medição na linha: espessura **e** peso, e o número que fecha a saga (2026-09-25)

Ele remedeu os 5 pontos e pesou as amostras: espessura **1,5 · 2,5 · 2,5 · 2,0 · 1,5 mm** e massa
**0,8 · 1,3 · 1,4 · 1,1 · 0,8 g** em `y = −37,5 / −18,75 / 0 / +18,75 / +37,5 mm`. Este documento é a leitura
disso. **Nada no SSOT foi tocado**; no fim está a cota que a medição produz, para virar PRP-0007 se ele quiser.

---

## 1. As duas medições concordam — o perfil é real, não é o paquímetro afundando

| y (mm) | t (mm) | m (g) | t/t_max | m/m_max | desvio peso vs paquímetro |
|---:|---:|---:|---:|---:|---:|
| −37,50 | 1,50 | 0,80 | 0,600 | 0,571 | −4,8 % |
| −18,75 | 2,50 | 1,30 | 1,000 | 0,929 | −7,1 % |
| 0,00 | 2,50 | 1,40 | 1,000 | 1,000 | 0,0 % |
| +18,75 | 2,00 | 1,10 | 0,800 | 0,786 | −1,8 % |
| +37,50 | 1,50 | 0,80 | 0,600 | 0,571 | −4,8 % |

`m/t` nas cinco estações: média **0,539 g/mm** com desvio-padrão de **2,9 %** — se as amostras foram cortadas
do mesmo tamanho, os dois métodos estão contando a mesma história, e é o que os números mostram (afastamento
máximo de 7 %). **Então o perfil não é artefato de medição.** E a 2ª medição confirma a 1ª também na forma:
borda = 1,5 nas duas, centro gordo nas duas.

Subproduto útil: com a densidade de literatura do repo (ρ = 1,25 g/cm³, `04_/masti_epdm_reologia.py`), a área da
sua amostra saiu **≈ 431 mm² (~20,8 × 20,8 mm)**. **Se você me der a área real cortada, eu devolvo a densidade
medida do seu mastique** — que hoje é número de prateleira, nunca foi medido neste projeto, e destravaria
qualquer cálculo de massa por metro.

## 2. O que a manta é, em seção

Integrando o seu perfil pelos 5 pontos (trapézios, passo de 18,75 mm):

| grandeza | medida | nominal do contrato | diferença |
|---|---:|---:|---:|
| seção da manta | **159,4 mm²** | 112,5 mm² (75,00 × 1,50) | **+42 %** |
| velocidade de saída com a vazão de referência (Q = 15.000 mm³/s) | 94 mm/s = **5,6 m/min** | 133 mm/s = **8,0 m/min** | **−30 %** |

Cuidado com o enquadramento, e eu quase errei aqui: a extrusora entrega a vazão que a rosca empurra — com seção
159,4 mm² os mesmos 67,5 kg/h saem a 5,6 m/min. **Você não está queimando material; está vendendo 30 % menos
metro por hora do que a máquina poderia entregar**, porque a seção gorda no meio não deixa a linha correr.
Igualizar em 1,50 nos 75 mm é, além de qualidade, **~42 % mais metro com a mesma extrusora** (se o puxador
acompanhar).

## 3. A assimetria piorou — e isso mudou de diagnóstico

−18,75 mm mede **2,50** e +18,75 mm mede **2,00**: **25 % de diferença entre os dois lados, mesma distância do
centro** (na medição passada: 2,00 × 1,80 = 10 %). E o máximo não está mais no centro: **2,50 aparece em dois
pontos (−18,75 e 0,00)** — a "barriga" está deslocada para o lado A.

Funil simétrico com fenda reta **não faz isso**: no modelo, os dois lados são o mesmo sólido espelhado, seção a
seção (o `avaliacao_matriz3_uniformidade.py` mostra centroide do canal a −0,0071 mm do plano de simetria).
Portanto **tem metal ou alinhamento fora do eixo**: matriz montada girada/fora do centro, assento com cavaco ou
amassado de um lado, bucha/nariz gasto de um lado, alimentação deslocada, ou a manta saindo torcida e você
medindo numa trena que não é perpendicular ao extrudado.

Isto é a pendência nº 1, à frente de qualquer desenho novo: **gire a matriz 180° e remeça os 5 pontos.** Se a
barriga viajar com a matriz, é matriz/assento. Se ficar no mesmo lado da máquina, é máquina — e nenhuma revisão
de matriz resolve.

## 4. A cota que a sua medição produz (e por que ela sai do "sorriso", não do freio)

Assumindo vazão local proporcional à espessura (com a ressalva do §5), com `n = 0,32` do SSOT:

| estação | q / q_máx | resistência local a mais |
|---:|---:|---:|
| ±37,50 | 0,600 | **+17,8 %** |
| +18,75 | 0,800 | +7,4 % |
| −18,75 e 0,00 | 1,000 | — |

Para o centro sair de **2,50 → 1,50 mm** ele precisa passar **1,67× menos material**, o que exige **+18 % de
resistência local = +4,74 bar**, que com o gradiente medido do land (**2,187 bar/mm**) são **2,2 mm de land a
mais no centro**.

E aqui está por que a solução é a **fenda em arco** (a primeira foto dele) e não a janela nas costas nem o tampo
no meio: o arco faz as duas coisas ao mesmo tempo — **afasta o meio da entrada** (mais caminho = mais
resistência onde sobra material) **e aproxima as pontas** (menos caminho onde falta). O alívio nas costas só
abre as pontas, o que neste caso empurraria todo o perfil para 2,5 mm e você teria de esticar a manta no
puxador para voltar a 1,50.

| sagita do arco | land extra no centro | fenda desenvolvida (corda 75,00 intacta) | raio do arco |
|---:|---:|---:|---:|
| 1,00 mm | ~1,00 mm | 75,04 mm (+0,05 %) | 704 mm |
| **2,00 mm** | ~2,00 mm | **75,14 mm (+0,19 %)** | **353 mm** |
| 2,20 mm | ~2,20 mm (o número do §4) | 75,17 mm (+0,22 %) | 326 mm |
| 3,00 mm | ~3,00 mm | 75,32 mm (+0,43 %) | 236 mm |

Ou seja: **o remédio que a sua própria medição pede é um arco de flecha ~2 mm, raio ~350 mm, corda 75,00
inalterada** — a largura da peça não muda, a área da fenda contratada (112,0171 mm²) não muda, o R 0,75 das
pontas não muda, e o custo de usinagem é **a trajetória do fio EDM**, não uma forma nova. É a maior alavanca por
milímetro que existe neste projeto, e veio de um paquímetro e uma balança, não de CFD.

## 5. O que este documento **não** garante

- **q ∝ t** só vale com a velocidade de linha igual na largura. Se a manta cai solta, sem puxador, o swelling
  (que é maior onde sai mais material) infla a diferença de espessura: o centro pode estar passando 1,35× e não
  1,67× o material. Isso não invalida o sinal, mas **faz 2,2 mm ser teto, não alvo** — primeiro passo **1,5 mm de
  flecha**, remeça os 5 pontos, e só abra o arco se o perfil continuar gordo no meio. É iteração com régua, e é
  assim que ele faz na bancada dele.
- O gradiente de 2,187 bar/mm e o ΔP de 26,68 bar são do **método 1D do projeto**, o mesmo dos PRP-0002/0004 —
  ordem de grandeza, não CFD. O número de 203,6 bar do pacote é de outro modelo (com o anel de fuga medido); os
  dois convivem no repo e nenhum dos dois substitui a medição na chapa.
- O arco **não conserta assimetria A≠B** (§3). Se o giro de 180° mostrar que a barriga fica no mesmo lado da
  máquina, a flecha não deve ser desenhada antes de resolver isso.
- Espessura medida com o material "sendo massa", como ele disse: ±0,05 mm por ponto, o que dá ~±3 % no perfil —
  aceitável para dimensionar 1,5–2,0 mm de flecha, insuficiente para discutir 0,1 mm.

## 6. Se ele aprovar, a rev. 31 entra como PRP-0007 com isto dentro

1. **Fenda em arco**: corda 75,00, flecha **1,50 mm** como cota de projeto, com nota de fabricação "ajustável até
   3,00 mm na bancada, só com o perfil de 5 pontos medido em mãos"; raio resultante 469,5 mm (flecha 1,50), R 0,75
   nas pontas preservado.
2. **Chanfro de saída 1,50 → 0,50 × 45°** (land paralelo 9,50): já calculado no repo (PRP-0002) — 27,96 bar
   (+4,8 %) e a parede do lábio de 0,75 para 1,75 mm, o que fecha o P7 da triagem. Mais land também significa
   que a flecha de 1,50 mm entrega um pouco menos de resistência do que a tabela de cima — por isso o começo
   conservador.
3. **Sem janela nas costas e sem freio removível** nesta revisão: com o seu perfil medido, abrir as pontas é o
   remédio errado (empurra tudo para 2,5 mm). Fica registrado como a alternativa, caso o giro de 180° mostre que
   a máquina está limpa e o meio continua gordo mesmo com o arco.
4. Invioláveis confirmados: 75,00 de largura, 1,500 +0,010/−0,000, boca Ø75,60, três estágios, collete EX-031 +
   degrau, sem furo/flange/partição.
