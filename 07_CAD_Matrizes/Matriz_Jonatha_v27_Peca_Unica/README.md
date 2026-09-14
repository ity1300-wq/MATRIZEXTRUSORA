# Matriz Jonatha v27.0 como **peça única** (variante derivada — não é o master)

Pedido em 2026-09-13: "transforme a peça matriz JONATHA V27 em peça única, não bipartida". O master continua
`../Matriz_Jonatha_v27_OFICIAL/MatrizJonatha.step` (sha256 `7f26c5c5ba238a12…`, regra 1: nunca editado; o
portão confere isso por conteúdo). Esta pasta é a variante.

| arquivo | o que é |
|---|---|
| `MatrizJonatha_v27_Peca_Unica.step` | **1 sólido, 1 casca, 22 faces**, sha256 `ffa6cc4baa6496c48e1f985f088e605c84588e24bb1f888fc106c37eaca15295` |
| `peca_unica_v27.json` | todas as medidas, a visibilidade das 17 caras do canal e a montagem |

Recriar do zero (lê o master, junta as metades, fecha as bolhas seladas, mede, monta):

    python3 04_Dados_SSOT_e_Scripts/gerar_matriz_v27_peca_unica.py

## O que a peça única tem de diferente, medido

* **aço:** 469.303,2 mm³ (3,684 kg) contra 469.001,7 mm³ das duas metades — os **+351,9 mm³** são as duas
  cavidades seladas dos furos de pino, que deixam de existir porque não há mais o que alinhar;
* **canal idêntico:** 213.945,1 mm³ nas duas peças (funil + fenda), medido como envelope − aço;
* **produto idêntico:** fenda 75,000 × 1,500 mm com R 0,75 no land (Z = 107,00), boca de saída 78,00 × 4,50 mm
  pelo chanfro 1,50 × 45° (decisão D2 preservada), boca de entrada Ø 75,60 mm, envelope Ø 93,00 / Ø 89,50 /
  Ø 79,50 com Z total 109,00 mm;
* **topologia limpa:** BRepCheck válido no sólido e em **0** de 22 faces e **0** de 90 arestas (é o exame que
  reprovou o `Body_B` da v28.1);
* **linha de partição: zero.** Na bipartida o plano Y = 0 cruza o canal (seção de 8.204,4 mm², 78,00 × 109,00 mm,
  perímetro de costura 372,8 mm) e corre pelas **duas bordas** da manta — é o caminho por onde sai degrau e
  rebarba na borda. Somem também os 759,5 mm² de contato metal-metal entre as metades e a força de abertura de
  55,7 kN que os pinos tinham de segurar.

## Fabricabilidade (o motivo real de a peça ser bipartida)

Cada uma das 17 caras do canal foi testada contra linha reta vinda da entrada (Z < 0) e da saída (Z > 109,00),
com folga de 0,60 mm para dentro do vazio e raio de teste de 0,10 mm. **Nenhuma cara ficou em sombra: 0,0 mm² de
25.181,8 mm² de superfície de canal (0,00 %).** Os dois flancos do funil (9.184 e 9.213 mm², BSPLINE) só são
vistos pela **entrada** — passam pelo Ø 75,60 —, as paredes da fenda e o chanfro são vistos pela **saída**, e as
duas bordas em R 0,75 são vistas dos dois lados. Ou seja: a peça única é usinável com ferramenta entrando pelas
duas faces (fresa/EDM pelo lado da extrusora para o funil em V, brocha ou EDM pela face de saída para a fenda),
**sem junta**. O que a bipartição resolvia não era sombra geométrica, era conveniência de máquina: fenda de 1,5 mm
brochada ou queimada em 109 mm de profundidade é a operação cara desta peça.

## Cabeçote

`../../06_CAD_Cabecote_EX-030/STEP/Cabecote_EX-030_com_Matriz_Jonatha_v27_Peca_Unica.step` — cabeçote completo
com flange + a peça única, 2 sólidos, interferência 0,0000 mm³, saída em Z = 109,00 (protrusão +14,00 mm além da
face do nariz). O anel de fuga de 1,00/0,25/0,25 mm com a matriz continua existindo — não vem da bipartição, e é
a rota que a simulação 3D tem de fechar.
