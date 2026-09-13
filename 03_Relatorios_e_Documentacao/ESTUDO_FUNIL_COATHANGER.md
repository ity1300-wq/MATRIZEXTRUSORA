# D3 — funil atual × coat-hanger, medido nos sólidos

Método: cortes do solido com secao() de verify_legacy_dies.py (a mesma que o dp_total usa, para tabela e Delta-P saírem do mesmo corte); Delta-P 1D com dp_total() de verify_legacy_dies.py (K = 18.500,00 Pa·s^n, n = 0,32, Q = 15.000 mm³/s); mesmo land 8,50 mm e chanfro 1,50 × 45 nos dois lados da comparação; lei de projeto do funil novo nas estações Z=0, Z=25, Z=70, Z=99 mm.

Nada aqui muda o arquivo oficial: é a comparação pedida antes de tocar no canal.

| grandeza | funil atual (cone linear) | variante coat-hanger | diferença |
| :--- | ---: | ---: | ---: |
| ΔP 1D até a saída (método do projeto) | 41,9 bar | 100,9 bar | +141,0 % |
| volume do canal | 213.945 mm³ | 76.010 mm³ | -64,5 % |
| tempo médio de residência (V/Q) | 14 s | 5 s | -64,5 % |
| altura da seção em Z=25,00 | 56,89 mm | 12,00 mm | -78,9 % |
| altura da seção em Z=70,00 | 23,21 mm | 3,50 mm | -84,9 % |
| menor altura de seção antes da saída | 1,50 mm | 1,50 mm | +0,0 % |
| volume estacionado com |x| > 30 mm (antes do land) | 18.337 mm³ | 2.391 mm³ | -87,0 % |
| fração desse volume | 0,086 | 0,031 | -5,4 pp |
| centroide do canal em Y (0 = simétrico) | -0,0071 mm | 0,0000 mm | Δ 0,0071 mm |
| maior invasão do envelope do master (0 = regra rígida OK) | 0,0000 mm | 0,0000 mm | Δ 0,0000 mm |
| aço cortado no mesmo envelope | 456.797 mm³ (3,586 kg) | 607.239 mm³ (4,767 kg) | 150.442 mm³ |

## O que os números dizem

1. **Custa 2,41× de pressão e não muda a manta.** 100,9 bar contra 41,9 bar integrados até a saída. A fenda e o land são os mesmos nos dois (1,50 × 75,00 mm, land 8,50 mm), então a **espessura da manta não melhora um mícron** — e os 100,9 bar já passam dos 68,2 bar que o relatório de CFD do projeto usa como limite. Não é troca neutra: mexe no dimensionamento da extrusora.
2. **O canal fica 64 % menor** (76.010 mm³ contra 213.945 mm³) e por isso a residência cai de 14 s para 5 s (-64 %). Cuidado ao ler isso como mérito do cabide: é só "tem menos plástico parado". A fração estacionada nas pontas cai de 8,6 % para 3,1 % do volume, mas em absoluto são 18.337 → 2.391 mm³, e parte da queda vem do canal inteiro menor, não da forma das asas.
3. **Nenhum dos dois é o coat-hanger descrito.** A altura da seção em Z=25,00 é 56,89 mm no funil atual e 12,00 mm na variante modelada a partir do script do projeto; o reservatório central de **6,00 mm** que o AUTO_PROMPT descreve não existe em sólido nenhum deste repositório (e 12,00 mm é o que o próprio `generate_true_coathanger_jonatha.py` pede — o texto e o script também não batem entre si).
4. **Assimetria**: o centroide do canal está a -0,0071 mm do plano de partição no funil atual e a 0,0000 mm na variante. Nenhum dos dois desloca a fenda; a assimetria de 199,22 mm³ achada na auditoria do v27.0 é do loft do land, não do funil, e não muda com esta decisão.
5. **Envelope respeitado nos dois**: a maior invasão medida seção a seção foi 0,0000 mm na variante (em Z=0,0) e 0,0000 mm no atual — nenhum encosta no Ø93/Ø89,5/Ø79,5 e a boca de entrada continua em 75,60 mm em Z=0.

6. **Aço e contabilidade fechada**: cortando o mesmo envelope, sobra 607.239 mm³ na variante contra 456.797 mm³ na v28.1 — **150.442 mm³ a mais de aço**. Isso confere com as outras duas medidas: o canal da variante é 137.936 mm³ menor e a v28.1 tem 12.507 mm³ de furação que este estudo não modela, 137.936 + 12.507 = 150.442 mm³ (diferença residual de 0,016 mm³ — FECHA: as três medições são consistentes). Portanto o número de massa aqui **não é número de corte**: o corpo do estudo não leva furos e não está bipartido.

## Recomendação (para você decidir, não apliquei nada)

Manter o funil do master e **reescrever o texto** que fala em coat-hanger com reservatório de 6,00 mm (opção 7.1a do relatório v28.1): ele descreve uma peça que não foi feita. Se você quiser um cabide de verdade, o próximo passo não é este loft: é desenhar a altura das asas decrescente do centro para as pontas (h(±37,50) < h(0)), que é o único mecanismo que compensa o caminho mais longo das bordas — e aí CFD novo é obrigatório, porque o ΔP saiu de 41,9 para 100,9 bar só com essa troca de forma.
