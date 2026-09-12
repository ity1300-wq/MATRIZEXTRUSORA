# Auditoria PRÉVIA de `PRP-0005` — rodada de quem propõe, não o veredito oficial

**Isto NÃO é o veredito.** O veredito oficial é do Auditor e é gravado em
`05_Interface_Auditoria/vereditos/PRP-0005.{json,md}` (§1 do protocolo: quem projeta não escreve o próprio
veredito). Este arquivo existe para uma coisa só: que o estado da proposta fique legável antes de pedir
auditoria, com o comando exato que o produziu e sem edição nenhuma no resultado.

```bash
export LD_LIBRARY_PATH="$PWD/04_Dados_SSOT_e_Scripts/.headless_gl"
python 05_Interface_Auditoria/scripts/auditar_proposta.py \
       05_Interface_Auditoria/propostas/PRP-0005-v28-1-fabricacao.json --json --md \
       --saida-dir /home/user/tmp/veredito_previo            # fora dos vereditos/, de proposito
```

Leitura do resultado, em três frases: as **11 métricas declaradas em `esperado` bateram todas** (ΔP 26,68 bar
declarado × 26,68 recalculado; canal 213.945,1 mm³ declarado × 213.945,1459 medido), os **sete requisitos duros
de geometria passaram** (fenda 75,00 × 1,50 com R0,75, boca Ø75,60, envelope Ø93 × 109, interferência 0,000 mm³,
canal consistente com o corpo), e a proposta está **BLOQUEADO por dois motivos, um de cada lado**: o meu
(`I4` — mexi em `cad_die_parameters.json` e `verify_geometry_ssot.py`, zona congelada §8, declarado na
proposta) e o do processo (`I5` — o hash de `05_Interface_Auditoria/PROTOCOLO_AUDITORIA.md` gravado no
baseline é `1fc0aa5e…`, o arquivo no topo da `main` é `702d5f2f…`: o selo ficou para trás no próprio
repositório, antes de qualquer proposta minha).

O `I4` só se resolve por ato do humano: `--atualizar-hashes` (re-sela, registrando quem/o quê/quando) ou
reverter minhas edições no `04_`. Eu **não** rodei o re-selo: re-afrouxar a própria régua para passar na
própria proposta é exatamente o que o §8 proíbe.

---

## Veredito `PRP-0005` — **BLOQUEADO**

**Requisito duro violado ou não verificado: corrigir antes de continuar.**

`commit auditado:` `01ed75af7207` · `protocolo:` 1.0 · `data:` 2026-09-12T18:31:15+0000

### Requisitos e conferências

| id | o que | nominal | medido | tol. | severidade | resultado |
| :-- | :-- | --: | --: | :-- | :-- | :-- |
| `D1` | Largura da fenda = 75,00 mm | 75.0 | 75.0 | ±0.05 mm | BLOCKER | **OK** |
| `D2` | Espessura da fenda = 1,50 mm | 1.5 | 1.5 | ±0.02 mm | BLOCKER | **OK** |
| `D3` | Raio de borda = 0,75 mm | 0.75 | 0.75 | ±0.02 mm | BLOCKER | **OK** |
| `D4` | Boca de entrada ≤ Ø75,60 mm | 75.6 | 75.6 | ±0.001 mm | BLOCKER | **OK** |
| `D5` | Interferência entre as metades = 0 | 0.0 | 0.0 | ±0.01 mm³ | BLOCKER | **OK** |
| `D6` | Envelope externo (Ø93 × 109 mm) | 93 × 109 | 93.0 × 109.0 | ±0,05 mm | BLOCKER | **OK** |
| `D7` | Canal isolado × corpo (consistência) | True | True | ≤ 0,5% | BLOCKER | **OK** |
| `I1` | 02_CAD_Modelos_Historicos/ intacto | idêntico ao baseline congelado | nenhuma alteração |  | BLOCKER | **OK** |
| `I2` | Entregáveis CAD em .step | idêntico ao baseline congelado | todos .step |  | BLOCKER | **OK** |
| `I3` | STEP alterados estão declarados na proposta | idêntico ao baseline congelado | nenhuma alteração |  | BLOCKER | **OK** |
| `I4` | SSOT e scripts de medição não alterados | idêntico ao baseline congelado | ['04_Dados_SSOT_e_Scripts/cad_die_parameters.json', '04_Dados_SSOT_e_Scripts/verify_geometry_ssot.py'] |  | BLOCKER | **FALHA** |
| `I5` | Protocolo, esquemas e scripts do auditor não alterados | idêntico ao baseline congelado | ['05_Interface_Auditoria/PROTOCOLO_AUDITORIA.md'] |  | BLOCKER | **FALHA** |
| `I6` | Sem arquivos protegidos ausentes | idêntico ao baseline congelado | nenhum |  | BLOCKER | **OK** |
| `I7` | Arquivos protegidos novos (não estavam no baseline) | — | ['01_CAD_MatrizJonatha_Oficial/MatrizJonatha_v28.step', '01_CAD_MatrizJonatha_Oficial/MatrizJonatha_v28_Body_A.step', '01_CAD_MatrizJonatha_Oficial/MatrizJonatha_v28_Body_B.step', '01_CAD_MatrizJonatha_Oficial/MatrizJonatha_v28_Canal_Fluxo.step', '01_CAD_MatrizJonatha_Oficial/MatrizJonatha_v28_Com_Fluxo.step', '01_CAD_MatrizJonatha_Oficial/MatrizJonatha_v28_Explodida.step', '01_CAD_MatrizJonatha_Oficial/MatrizJonatha_v28_Pinos_Alinhamento.step'] |  | INFO | **ATENCAO** |
| `I8` | git: arquivos CAD alterados desde base_commit | declarados | ['01_CAD_MatrizJonatha_Oficial/MatrizJonatha_v28_Com_Fluxo.step', '01_CAD_MatrizJonatha_Oficial/MatrizJonatha_v28_Explodida.step', '01_CAD_MatrizJonatha_Oficial/MatrizJonatha_v28_Pinos_Alinhamento.step'] |  | INFO | **ATENCAO** |
| `E:land_util_mm` | Declarado × recalculado: land_util_mm | 8.5 | 8.5 | ±2.0% | ALERTA | **OK** |
| `E:parede_labio_mm` | Declarado × recalculado: parede_labio_mm | 0.75 | 0.75 | ±5.0% | ALERTA | **OK** |
| `E:dp_total_bar` | Declarado × recalculado: dp_total_bar | 26.68 | 26.68 | ±15.0% | ALERTA | **OK** |
| `E:largura_fenda_mm` | Declarado × recalculado: largura_fenda_mm | 75.0 | 75.0 | ±0.1% | ALERTA | **OK** |
| `E:espessura_fenda_mm` | Declarado × recalculado: espessura_fenda_mm | 1.5 | 1.5 | ±2.0% | ALERTA | **OK** |
| `E:raio_borda_mm` | Declarado × recalculado: raio_borda_mm | 0.75 | 0.75 | ±3.0% | ALERTA | **OK** |
| `E:area_fenda_mm2` | Declarado × recalculado: area_fenda_mm2 | 112.0171 | 112.0171 | ±1.0% | ALERTA | **OK** |
| `E:boca_entrada_mm` | Declarado × recalculado: boca_entrada_mm | 75.6 | 75.6 | ±0.1% | ALERTA | **OK** |
| `E:volume_canal_mm3` | Declarado × recalculado: volume_canal_mm3 | 213945.1 | 213945.1459 | ±0.5% | ALERTA | **OK** |

### Comparação com o baseline (v27 aprovado)

| métrica | baseline | proposto | Δ | direção | aceitável |
| :-- | --: | --: | --: | :-- | :-- |
| `largura_fenda_mm` | 75.0 | 75.0 | +0.00% | igual | sim |
| `espessura_fenda_mm` | 1.5 | 1.5 | +0.00% | igual | sim |
| `area_fenda_mm2` | 112.0171 | 112.0171 | +0.00% | igual | sim |
| `land_util_mm` | 8.5 | 8.5 | +0.00% | igual | sim |
| `boca_entrada_mm` | 75.6 | 75.6 | +0.00% | igual | sim |
| `parede_labio_mm` | 0.75 | 0.75 | +0.00% | igual | sim |
| `interferencia_mm3` | 0.0 | 0.0 | — | neutro | sim |
| `volume_canal_mm3` | 213945.1459 | 213945.1459 | +0.00% | igual | sim |
| `z_total_mm` | 109.0 | 109.0 | +0.00% | igual | sim |
| `diametro_externo_mm` | 93.0 | 93.0 | +0.00% | igual | sim |
| `envelope_residuo_mm3` | 0.0009 | 0.0009 | +0.00% | igual | sim |
| `raio_borda_mm` | 0.75 | 0.75 | +0.00% | igual | sim |
| `canal_consistente` | True | True | +0.00% | igual | sim |
| `dp_total_bar` | 26.68 | 26.68 | +0.00% | igual | sim |
| `forca_abertura_kN` | 19.97 | 19.97 | +0.00% | igual | sim |
| `residencia_media_s` | 14.26 | 14.26 | +0.00% | igual | sim |
| `residencia_parede_min` | 23.6 | 23.6 | +0.00% | igual | sim |
| `dp_land_bar_mm` | 2.1866 | 2.1761 | -0.48% | neutro | sim |

### 🚫 Bloqueios
- I4: SSOT e scripts de medição não alterados (nominal idêntico ao baseline congelado / medido ['04_Dados_SSOT_e_Scripts/cad_die_parameters.json', '04_Dados_SSOT_e_Scripts/verify_geometry_ssot.py'])
- I5: Protocolo, esquemas e scripts do auditor não alterados (nominal idêntico ao baseline congelado / medido ['05_Interface_Auditoria/PROTOCOLO_AUDITORIA.md'])

### Recomendações
- Corrigir os bloqueios acima e reenviar como PRP-XXXX-r2.

### ⚠️ Não auditado (silêncio não é aprovação)
- `esperado.z_total_mm` — o auditor não sabe recalcular esta métrica
- `esperado.interferencia_mm3` — o auditor não sabe recalcular esta métrica

**Modelo usado:** não aplicável

<details><summary>Reproduzir</summary>

```bash
python 04_Dados_SSOT_e_Scripts/verify_geometry_ssot.py --json
```
```bash
python 04_Dados_SSOT_e_Scripts/verify_legacy_dies.py --json
```
```bash
python 04_Dados_SSOT_e_Scripts/avaliacao_matriz3_calculos.py --json
```
```bash
python 05_Interface_Auditoria/scripts/auditar_proposta.py 05_Interface_Auditoria/propostas/PRP-0005-v28-1-fabricacao.json
```
</details>
