# Matriz Gedeon CERTA — o que o arquivo do usuário é, e o que foi entregue

Fonte: `02_CAD_Modelos_Historicos/matrizGedeonCerta.step` (aberto só para leitura). Números: `04_Dados_SSOT_e_Scripts/gedeon_certa.json`.

## Por que este relatório existe

A entrega anterior (`06_/STEP/Gedeon_Corrigida/`, apagada em 2026-09-13) re-cortou no arquivo do usuario o canal historico
da Gedeon — tirou 170772,2 mm³ de aço dele com o argumento de que o
arquivo era um bloco bruto. **Estava errado.** Medido face por face, o arquivo já é a matriz pronta:
fenda 75,00 × 1,50 mm com R 0,75 atravessando de Z = 0,17 a Z = 109,00, cone de entrada abrindo em Ø 75,60 em Z = -0,00, e os dois furos de pino Ø 1,78 × 10,00 mm.

## O que foi conferido no arquivo dele (contrato do projeto, medido, não copiado)

* Envelope: os três estágios do SSOT batem com os cilindros medidos — Ø 93,00 até Z = 69,90, Ø 89,50 até Z = 80,70, Ø 79,50 até Z = 109,00; comprimento total Z = 109,000.
* Fenda: largura 75,000 (contrato 75,00), espessura 1,500 (contrato 1,50), raio dos topos 0,750 (contrato R 0,75).
* Entrada: Ø 75,60 na face traseira (contrato Ø 75,60), fechando em cone até Z = 20,98.
* Sem flange e sem furo de fixação: os únicos cilindros de eixo diferente de Z são os dois furos de pino.
* Caminho de fluxo medido (cone + fenda): 43017,9 mm³; massa 5,0254 kg.

## O defeito que ele tem, e é um só

O sólido tem 3 cascas: 2 cavidades seladas dentro do aço, os furos de pino, com parede de 4,11 mm até o Ø 93,00 externo — não tem por onde entrar a ferramenta. Volume fechado: 49,8 mm³.

## O conserto entregue

Partir o bloco no plano Y = 0, que é onde os furos já estão centralizados (y ±0,89), e entregar as duas metades. Não foi removido aço nenhum: A + B = 640180,7239 mm³ contra o bloco 640180,7 mm³ (diferença 0,000383 mm³). Cada metade tem 1 casca, BRepCheck válido, e o furo sai como meia-cana aberta no plano de partição.
Interseção entre as metades: 0,0000 mm³.

## Interface com o cabeçote EX-030

Colocação igual à que já estava medida (deslocamento axial 0,000 mm): interseção matriz × cabeçote 0,0000 mm³, a face de saída da matriz fica 14,00 mm além da face do cabeçote (Z = 95,00), e o aço do cabeçote que cai dentro do cone+fenda é 0,0000 mm³. Como o envelope externo é o mesmo da Gedeon histórica, os vereditos [A] a [G] de `verificar_interface_cabecote.py` não mudam.

## Diferença de conceito para a Jonatha v27

Booleano medido: 171224,1 mm³ de aço só na Gedeon certa e 44,9 mm³ só na v27. A diferença não é "funil ampliado": é que a Gedeon não tem funil próprio — o fluxo dela é o cone de entrada + a fenda atravessada (43017,9 mm³), e o resto da convergência é feito pelo próprio furo estagiado do cabeçote.

## Arquivos

```
07_CAD_Matrizes/Matriz_Gedeon_Certa/MatrizGedeon_Certa_Body_A.step
07_CAD_Matrizes/Matriz_Gedeon_Certa/MatrizGedeon_Certa_Body_B.step
07_CAD_Matrizes/Matriz_Gedeon_Certa/MatrizGedeon_Certa_Canal_Fluxo.step
07_CAD_Matrizes/Matriz_Gedeon_Certa/MatrizGedeon_Certa_Explodida.step
07_CAD_Matrizes/Matriz_Gedeon_Certa/Cabecote_EX-030_com_Matriz_Gedeon_Certa.step
```

Checks: 21 executados, 0 falha(s). Nada promovido: o master continua v27.0.
