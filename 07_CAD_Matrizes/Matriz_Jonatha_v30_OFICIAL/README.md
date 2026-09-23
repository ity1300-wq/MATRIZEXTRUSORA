# Matriz JONATHA — v30 (revisão de 2026-09-22)


Peça única (1 sólido, 1 casca, 22 faces, BRep válido). **Não é a v27.0 bipartida**: é o mesmo canal de fluxo do master, com o envelope alterado por decisão do dono em 2026-09-22 e tolerância **±0,5** em toda cota alterada.

| cota | medida no STEP |
|---|---|
| Ø 1º estágio (datum A) | 94,00 mm em Z 0,00 → 69,90 |
| Ø 2º estágio | 89,00 mm em Z 69,90 → 80,70 |
| Ø 3º estágio | 79,00 mm em Z 80,70 → 95,00 |
| comprimento total | 95,00 mm |
| fenda no land | 75,0000 × 1.500 mm, R 0,75 nas pontas (área 112,0171 mm²) |
| land paralelo | 8.500 mm (Z 85,00 → 93,50) |
| chanfro de saída | 1,50 × 45°, cone medido em Z 93,50 → 95,00 |
| boca de entrada | Ø75,60 (restrita por contrato) |
| volume de aço | 438509,9 mm³ → 3,4423 kg |
| canal de fluxo | 183862,6 mm³ (229,8 g de mastique dentro) |
| material | aço 1045 + indução (ou nitretação a plasma) nas arestas do land |

## Interface com o EX-030 (medida na montagem)

| estágio da matriz | furo do cabeçote | folga radial | Z congruente |
|---:|---:|---:|---|
| Ø94,00 | Ø95,00 | 0,50 mm | 0,00 → 69,90 |
| Ø89,00 | Ø90,00 | 0,50 mm | 70,00 → 80,70 |
| Ø79,00 | Ø80,00 | 0,50 mm | 81,00 → 95,00 |

Encosto face a face, `deslocamento_aplicado_mm` = 0,00 · **interferência 0,0000 mm³** · face de saída no Z 95,00 · **protrusão além do nariz +0,00 mm** (a face do nariz está em Z 95,00).

## Arquivos

| arquivo | o que é | sha256 |
|---|---|---|
| `MATRIZ_V30_PECA_UNICA.step` | **a peça** (o que a fábrica usina) | `b42ee2e50a10d43d` |
| `MATRIZ_V30_CANAL_DE_FLUXO.step` | o sólido do canal de fluxo (para o fio EDM e para conferir o volume) | `77497bf86c989b23` |
| `CONJUNTO_MATRIZ_V30_NO_CABECOTE_EX-030.step` | a matriz sentada no cabeçote completo, com flange (leitura/medida, sem booleano) | `725c2f83f26cc6e8` |
| `08_Pacote_Usinagem_v30/` | pacote de usinagem vigente (ficha, material, cotas, sequência, RFQ, prancha) | zip `d4948ebeb2f97bb4` |

O que mudou em relação à revisão anterior está anotado em `03_Relatorios_e_Documentacao/MATRIZ_V27_PECA_UNICA.md` (seção de 2026-09-22) e no SSOT (`decisoes_usuario` D10 a D12). Para a fábrica, a peça continua se chamando **JONATHA v27.0**; 'v29'/'v30' é carimbo interno de revisão do projeto.
