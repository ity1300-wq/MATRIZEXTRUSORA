# Matriz JONATHA v29.0 — OFICIAL (peça única)

Promovida a master em 2026-09-13, a pedido: "a peça única vira a oficial".

É a v27.0 com as duas metades (`Body_A` + `Body_B`) unidas no sólido da peça, sem pino de alinhamento e sem a
cavidade selada: 469.303,2 mm³ de aço (3.6840 kg), canal de 213.945,1 mm³ **idêntico ao master**, 22 faces, 1 casca, BRepCheck
limpo, 0,00 % de área do canal em sombra. Os números completos e o teste estão em
`03_Relatorios_e_Documentacao/MATRIZ_V27_PECA_UNICA.md` e `07_CAD_Matrizes/Matriz_Jonatha_v27_Peca_Unica/`.

| arquivo | o que é |
|---|---|
| `MATRIZ_V29_PECA_UNICA.step` | **a matriz** — o que vai para a fábrica (byte-idêntico ao STEP da peça única da v27.0) |
| `MATRIZ_V29_CANAL_DE_FLUXO.step` | o sólido do canal: ferramenta de medição de volume/seção e de verificação do produto |
| `CONJUNTO_MATRIZ_V29_NO_CABECOTE_EX-030.step` | a matriz montada no cabeçote com flange (interseção 0,0000 mm³) |

O que estava selado **não** foi mexido: `07_/Matriz_Jonatha_v27_OFICIAL/` continua com os seis arquivos de
sempre e `01_CAD_MatrizJonatha_Oficial/MatrizJonatha.step` continua apontando para ele — o portão confere o
sha256 desse caminho contra `05_Interface_Auditoria/baseline/MATRIZ_3_v27.json`. A promoção é registrada aqui,
no `04_/cad_die_parameters.json` (`matriz_oficial`) e no índice de `07_CAD_Matrizes/`. Para a fábrica, use
`08_Pacote_Usinagem_v29/`.
