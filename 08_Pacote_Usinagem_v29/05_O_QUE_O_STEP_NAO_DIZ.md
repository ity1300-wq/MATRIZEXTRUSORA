# O que o STEP não diz — e a fábrica precisa saber

O STEP é cego para tudo que não é geometria. Estas são as dez linhas que evitam a primeira peça errada:

1. **Unidade e convenção**: mm, Z = eixo da matriz, Z crescente no sentido do produto (Z = 109.00 é a face de
   saída, Z = -0.00 é a face de entrada que olha para o cabeçote). A manta sai em +Y/−Y com largura em X
   (x = ±37,50 são as bordas do produto).
2. **A matriz não é fixada por furo nem flange** — decisão do projeto, registrada no SSOT. O aperto é o collete
   EX-031 e o encosto face a face no rebaixo do cabeçote (rebaixo de 3,00 mm em Ø > 105,00). Ver
   `3D/CONJUNTO_MATRIZ_V29_NO_CABECOTE_EX-030.step`: a montagem tem interseção **0,0000 mm³** com o cabeçote.
3. **Folgas funcionais, não dimensionais**: Ø93,00 em Ø95,00 (radial 1,00), Ø89,50 em Ø90,00 e Ø79,50 em Ø80,00
   (radial 0,25 nos dois estágios de produto). O STEP traz os diâmetros; a *razão* de por que 0,25 está aqui:
   é o anel que segura o material voltando pelo funil. A conta está em
   `03_Relatorios_e_Documentacao/SIMULACAO_ROTAS_E_COMPRIMENTO.md` (0,06 % de vazão escapando pelo anel nesta
   matriz, contra 8,71 % na matriz que o projeto está substituindo).
4. **Comprimento 109,00, e não 100**: encurtar a peça não alivia a pressão (o funil e o land ficam intactos) e
   encurta a rota de fuga → aumenta a fração que volta. A alavanca de verdade é o land (8,50) e a folga do anel.
5. **O canal inteiro é usinável por uma face só** (0,00 % de sombra) → não criar recurso de acesso, não abrir
   janela, não partir a peça.
6. **Espessura 1,50 com R 0,75 nas bordas é geometria de produto, não de fábrica**: a largura 75,00 é
   constante do contrato (não "aproximadamente 75").
7. **Tratamento antes do acabamento**: as duas cotas de 0,02 mm saem na retífica, depois do último revenido.
8. **Nada de revestimento** sem teste: 10 µm de PVD mudam a espessura da manta.
9. **Marcação fora da zona de 69 MPa**: face traseira, e sem gravação profunda.
10. **Se qualquer cota sair fora, refugar, não retocar**: a fenda e o land definem vazão; "acertar" depois do
    tratamento muda o volume do canal (213.945,1 mm³) e o produto sai em outra gramatura.
