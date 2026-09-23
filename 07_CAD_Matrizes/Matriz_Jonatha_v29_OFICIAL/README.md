# Matriz JONATHA — v29 (revisão de 2026-09-22)


Peça única (1 sólido, 1 casca, 22 faces, BRep válido). **Não é a v27.0 bipartida**: é o mesmo canal de fluxo do master, com o envelope alterado por decisão do dono em 2026-09-22 e tolerância **±0,5** em toda cota alterada.

| cota | medida no STEP |
|---|---|
| Ø 1º estágio (datum A) | 94,00 mm em Z 0,00 → 69,90 |
| Ø 2º estágio | 89,00 mm em Z 69,90 → 80,70 |
| Ø 3º estágio | 79,00 mm em Z 80,70 → 109,00 |
| comprimento total | 109,00 mm |
| fenda no land | 75,0000 × 1,500 mm, R 0,75 nas pontas (área 112,0171 mm²) |
| land paralelo | 8,500 mm (Z 99,00 → 107,50) |
| chanfro de saída | 1,50 × 45°, cone medido em Z 107,50 → 109,00 |
| boca de entrada | Ø75,60 (restrita por contrato) |
| volume de aço | 477050,9 mm³ → 3,7448 kg |
| canal de fluxo | 213945,1 mm³ (267,4 g de mastique dentro) |
| material | aço 1045 + indução (ou nitretação a plasma) nas arestas do land |

## Interface com o EX-030 (medida na montagem)

| estágio da matriz | furo do cabeçote | folga radial | Z congruente |
|---:|---:|---:|---|
| Ø94,00 | Ø95,00 | 0,50 mm | 0,00 → 69,90 |
| Ø89,00 | Ø90,00 | 0,50 mm | 70,00 → 80,70 |
| Ø79,00 | Ø80,00 | 0,50 mm | 81,00 → 95,00 |

Encosto face a face, `deslocamento_aplicado_mm` = 0,00 · **interferência 0,0000 mm³** · face de saída no Z 109,00 · **protrusão além do nariz +14,00 mm** (a face do nariz está em Z 95,00).

## Arquivos

| arquivo | o que é | sha256 |
|---|---|---|
| `MATRIZ_V29_PECA_UNICA.step` | **a peça** (o que a fábrica usina) | `107d166874b7ab71` |
| `MATRIZ_V29_CANAL_DE_FLUXO.step` | o sólido do canal de fluxo (para o fio EDM e para conferir o volume) | `922073408b1b3a50` |
| `CONJUNTO_MATRIZ_V29_NO_CABECOTE_EX-030.step` | a matriz sentada no cabeçote completo, com flange (leitura/medida, sem booleano) | `d7cb3c3ea294e8e2` |
| `08_Pacote_Usinagem_v29/` | pacote de usinagem vigente (ficha, material, cotas, sequência, RFQ, prancha) | zip `da72d8ac9f2a9437` |

O que mudou em relação à revisão anterior está anotado em `03_Relatorios_e_Documentacao/MATRIZ_V27_PECA_UNICA.md` (seção de 2026-09-22) e no SSOT (`decisoes_usuario` D10 a D12). Para a fábrica, a peça continua se chamando **JONATHA v27.0**; 'v29'/'v30' é carimbo interno de revisão do projeto.
