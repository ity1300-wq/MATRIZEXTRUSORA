# PRP-0005 — STEP do land 10,00 mm com chanfro de saída 0,80 mm × 45°

**Data:** 12/09/2026 · **Autor:** IA engenheira (sessão `arena/01a096e3-matrizextrusora`)
**Linhagem:** implementa a previsão aprovada da **PRP-0001** (`vereditos/PRP-0001.json`, `APROVADO`)
**Objeto:** `01_CAD_MatrizJonatha_Oficial/PRP-0001-r2_land10_chanfro080/`
**Veredito da auditoria:** `PRP-0005` → **BLOQUEADO** — *por defeito da régua, não da peça* (ver §6)

> Regra do projeto respeitada: **nenhum número deste relatório existe sem um script que o
> reproduza.** Cada valor abaixo tem o comando que o gera.

---

## 1. O que foi entregue

| Arquivo | O que é |
| :--- | :--- |
| `MatrizJonatha_L10_C0.8.step` | montagem fechada bipartida (2 sólidos) |
| `MatrizJonatha_L10_C0.8_Explodida.step` | vista explodida (+40 mm em Y) |
| `MatrizJonatha_L10_C0.8_Com_Fluxo.step` | aço + macho do polímero (3 sólidos) |
| `MatrizJonatha_L10_C0.8_Body_A.step` | metade inferior (Y ≤ 0,003217) |
| `MatrizJonatha_L10_C0.8_Body_B.step` | metade superior |
| `MatrizJonatha_L10_C0.8_Canal_Fluxo.step` | núcleo de polímero + os 2 sólidos dos furos de pino (3 sólidos, como no master) |
| `gerar_variante_prp0001r2.py` | gerador paramétrico (`--chanfro`, `--land`, `--sanidade`, `--furos-passantes`) |
| `medir_variante_prp0005.py` | medição independente dos STEP gravados (`--sanidade`, `--comparar-baseline`) |
| `medicao_variante_prp0005.json` | evidência numérica da variante |
| `medicao_v27_oficial.json` | evidência de que o medidor reproduz o master |
| `gerar_variante.log` | parâmetros e volumes da geração |

O master oficial v27 **não foi sobrescrito**: os seis STEP de `01_CAD_MatrizJonatha_Oficial/`
continuam com os hashes do baseline congelado (o auditor confirmou em `I3`/`I4`/`I6`).
`02_CAD_Modelos_Historicos/` intocado (`I1` OK). Nada da zona congelada (§8) foi editado.

---

## 2. Como a geometria foi obtida (e o que isso revelou)

### 2.1 O gerador legado do repositório não reproduz o master

`04_Dados_SSOT_e_Scripts/generate_true_coathanger_jonatha.py` é apontado como a origem do v27.
Executado neste ambiente, ele produz:

| | gerador legado | master oficial medido |
| :--- | --: | --: |
| volume do canal | 48 330,365 mm³ | **213 945,146 mm³** |
| volume Body_A | 317 280,508 mm³ | **234 255,287 mm³** |
| volume Body_B | 317 578,136 mm³ | **234 746,369 mm³** |

Ou seja: **o script versionado não gera a peça que está entregue**. Reproduzir:

```bash
export LD_LIBRARY_PATH="$PWD/04_Dados_SSOT_e_Scripts/.headless_gl:$LD_LIBRARY_PATH"
$HOME/.venv/bin/python 04_Dados_SSOT_e_Scripts/generate_true_coathanger_jonatha.py
```

Dois defeitos concretos explicam a divergência: (a) os quatro fios do loft (`s0…s3`) são criados em
cadeia, mas só o último par entra no `loft()`, e (b) os furos de pino são extrudados para **Y
positivo** (`extrude(12.00)` a partir do plano XZ), enquanto no master eles ocupam **Y = −12…0**.

Consequência prática: **o v27 não é reproduzível pelo próprio repositório.** Isso é uma pendência de
SSOT tão grave quanto qualquer divergência dimensional, e está registrada aqui para decisão sua.

### 2.2 Cirurgia booleana sobre os STEP oficiais

Por isso a variante não foi "gerada": foi **derivada do master entregue**, de modo que o que a
proposta não declara mudar permaneça idêntico.

```
canal_variante = (canal do master abaixo de Z = 107,50)  ∪  trecho_final(107,50 → 109)
trecho_final   = loft de 3 fios:  75,00 × 1,50  em Z = 107,50
                                 75,00 × 1,50  em Z = 108,20   (= 109 − 0,80)
                                 76,60 × 3,10  em Z = 109,00   (45°: +0,80 mm por lado)
aço_variante   = envelope − canal_variante − 2 furos de pino
bipartição     = plano Y = +0,003217 mm, medido no Body_A oficial
```

Três descobertas medidas no caminho, todas registradas porque mudam o que se pode afirmar:

1. **O chanfro antigo começa em Z = 107,50**, não em 108,20. Cortar o master em 108,20 deixa o cone
   velho dentro do land novo (medido: `h = 1,7040 mm` em Z = 107,60, quando deveria ser 1,5000).
2. **Um loft que começa em 108,20 sobre um canal cortado em 107,50 deixa um vazio de 104,30 mm³**
   entre o land e o chanfro. Daí o trecho final ser uma peça única de 107,50 → 109.
3. **O anel que vira aço no lábio não pertence ao `Body_A`/`Body_B` oficiais.** O chanfro de 0,80 mm
   cabe *dentro* do cone de 1,50 mm (o canal variante é subconjunto do master, medido:
   `interseção = 213 820,019 mm³ = volume do variante`), então o aço não pode ser obtido por
   booleano a partir do aço master: `delta ∩ aço_master = 0,000 mm³`. O aço precisa ser
   **reconstruído do envelope**. O gerador tem asserção de fechamento volumétrico justamente para
   isso — na primeira tentativa ela barrou a saída errada.

### 2.3 Sanidade: o gerador devolve o master

Com `--chanfro 1.5` (o valor do v27), o mesmo código reproduz o oficial:

| | master oficial | gerador com `--chanfro 1.5` | Δ |
| :--- | --: | --: | --: |
| Body_A | 234 255,287 mm³ | 234 255,288 mm³ | +0,001 |
| Body_B | 234 746,369 mm³ | 234 746,368 mm³ | −0,001 |
| canal | 213 945,146 mm³ | 213 945,146 mm³ | 0,000 |
| land paralelo | 8,50 mm | 8,50 mm | 0 |
| parede do lábio | 0,75 mm | 0,75 mm | 0 |
| Δp (modelo do auditor) | 26,680 bar | 26,680 bar | 0 |

E o medidor independente, apontado para os STEP oficiais (`--sanidade`), devolve **0,000 %** de
desvio em todas as 12 métricas comparáveis ao baseline congelado. É isso que dá licença para usar os
mesmos dois scripts como evidência da variante.

---

## 3. O que mudou (medido nos arquivos gravados)

```bash
export LD_LIBRARY_PATH="$PWD/04_Dados_SSOT_e_Scripts/.headless_gl:$LD_LIBRARY_PATH"
$HOME/.venv/bin/python 01_CAD_MatrizJonatha_Oficial/PRP-0001-r2_land10_chanfro080/medir_variante_prp0005.py --comparar-baseline
```

| grandeza | v27 (master) | variante | Δ | julgamento |
| :--- | --: | --: | --: | :--- |
| **land reto e paralelo** | 8,50 mm | **9,20 mm** | +8,24 % | era a não conformidade; some |
| **chanfro de saída** | 1,50 mm | **0,80 mm** | −46,7 % | o parâmetro da proposta |
| **parede de aço no lábio** | 0,75 mm | **1,45 mm** | +93,3 % | quase o dobro; era o risco de lascamento |
| Δp total (modelo calibrado) | 26,680 bar | **27,573 bar** | +3,35 % | dentro do teto de +15 % (§4) |
| abertura na face de saída | 78,00 × 4,50 mm | 76,60 × 3,10 mm | — | consequência do chanfro menor |
| sobrelargura a 0,10 mm da face | 1,402 mm | 0,702 mm | — | confirma os 45° |
| volume do canal | 213 945,146 mm³ | 213 820,019 mm³ | −0,058 % | neutro |
| volume de aço | 469 001,656 mm³ | 469 126,783 mm³ | +125,127 mm³ | o anel do lábio |
| massa de aço | 3,6817 kg | 3,6826 kg | +0,9 g | irrelevante |

### O que **não** mudou (e foi medido, não declarado)

| grandeza | v27 | variante |
| :--- | --: | --: |
| largura da fenda em Z = 100 | 75,0000 mm | 75,0000 mm |
| espessura da fenda em Z = 100 | 1,5000 mm | 1,5000 mm |
| área da seção do land | 112,0171 mm² | 112,0171 mm² |
| raio de borda equivalente | 0,7500 mm | 0,7500 mm |
| boca de entrada (X / Y) | 75,6000 / 75,5993 mm | 75,6000 / 75,5993 mm |
| envelope Ø externo em Z = 0,50 / 75,30 / 94,85 | 93,0 / 89,5 / 79,5 mm | 93,0 / 89,5 / 79,5 mm |
| comprimento total Z | 109,0000 mm | 109,0000 mm |
| interferência entre as metades | 0,000000 mm³ | 0,000000 mm³ |
| fechamento envelope − (aço + canal + furos) | −0,0003 mm³ | −0,0003 mm³ |
| plano de partição | Y = +0,003217 mm | Y = +0,003217 mm (herdado) |
| sólidos na montagem / no `Canal_Fluxo` | 2 / 3 | 2 / 3 |
| furos de pino (2 × 150,796 mm³) | presentes | presentes, idênticos |

**Resultado: 10 de 10 requisitos duros conformes**, com as tolerâncias do §4 do protocolo.

### CFD: por que nada precisou ser refeito

A seção transversal do land é **idêntica** à do v27 (75,00 × 1,50 com R0,75, área 112,0171 mm²). O
CFD 2D do baseline resolve exatamente essa seção, portanto continuam valendo:

| métrica | valor do baseline | por que não muda |
| :--- | --: | :--- |
| gradiente de pressão no land | 2,1761 bar/mm (CFD) / 2,1866 (1D) | mesma seção, mesma vazão |
| τ de parede no land | 160,89 kPa | idem — e continua < 200 kPa (§4) |
| uniformidade do núcleo | **92,3 %** dentro de ±5 % (97,0 % em ±10 %) | idem |
| força de abertura | 19,97 kN | Δp × área do canal; +0,893 bar ≈ +0,10 kN (~0,5 %), abaixo da tolerância de 20 % |

O que muda no campo de escoamento é só o **comprimento** do trecho paralelo (8,50 → 9,20 mm) e o
**comprimento** do chanfro (1,50 → 0,80 mm), que é justamente o que o modelo paramétrico calibrado
do auditor (§5) cobre: `6,77 + 2,1824·9,20 + 0,9067·0,80 = 27,573 bar`.

---

## 4. Reproduzir tudo, do zero

```bash
cd MATRIZEXTRUSORA
bash 04_Dados_SSOT_e_Scripts/setup_cfd_env.sh                      # ~45 s; o venv não persiste
export LD_LIBRARY_PATH="$PWD/04_Dados_SSOT_e_Scripts/.headless_gl:$LD_LIBRARY_PATH"
PY=$HOME/.venv/bin/python
cd 01_CAD_MatrizJonatha_Oficial/PRP-0001-r2_land10_chanfro080

$PY gerar_variante_prp0001r2.py --chanfro 1.5 --prefixo SANIDADE_v27 --sanidade --sem-exportar \
    --log /tmp/sanidade.log                                        # espera "REPRODUZ"
$PY gerar_variante_prp0001r2.py                                    # grava os seis STEP
$PY medir_variante_prp0005.py --sanidade --comparar-baseline       # espera 10/10 e 0,000 % de desvio
$PY medir_variante_prp0005.py --comparar-baseline                  # espera 10/10 conformes
```

---

## 5. Estado na auditoria oficial

```bash
$PY 05_Interface_Auditoria/scripts/auditar_proposta.py \
    05_Interface_Auditoria/propostas/PRP-0005-step-land-10-chanfro-080.json --json --md
```

Saída (código 3):

```
ESTADO: BLOQUEADO — Requisito duro violado ou não verificado: corrigir antes de continuar.
   BLOQUEIO: I5: Protocolo, esquemas e scripts do auditor não alterados
             (medido ['05_Interface_Auditoria/PROTOCOLO_AUDITORIA.md'])
   ALERTA:   E:land_util_mm    (nominal 9.2  / medido 8.5)
   ALERTA:   E:parede_labio_mm (nominal 1.45 / medido 0.75)
```

Nenhum dos três itens diz respeito à peça. Ver §6.

---

## 6. Por que o veredito é BLOQUEADO — e o que fazer

Três defeitos independentes da régua, todos com evidência e correção escrita em
**`REGUA_V1.1_MUDANCA_PROPOSTA.md`** (documento irmão deste). Resumo:

| # | Defeito | Por que atinge a PRP-0005 | Correção |
| :-- | :--- | :--- | :--- |
| 1 | **Selo do baseline vencido.** O hash de `PROTOCOLO_AUDITORIA.md` no baseline é `1fc0aa5e…`, o arquivo commitado na `main` é `702d5f2f…`. A diferença é o diff legítimo do commit `b065d68` (ponteiro do CI no §7 + linha 1.0.1 no §9), feito depois do último re-selo (`17:58:21`, commit `c4371d7`). Os outros **34** hashes conferem. | `I5` FALHA → `BLOQUEADO`. E isso vale para **qualquer** proposta nova, inclusive a de controle. | `auditar_proposta.py --atualizar-hashes` (ato humano, §8) |
| 2 | **A régua não mede o objeto entregue.** `verify_geometry_ssot.py` tem `DIR_CAD` fixo; `auditar_proposta.py` roda a bateria sempre sobre os STEP oficiais. Para `tipo=geometria`, `previsto = medido` — e `medido` é o **master**. | `E:land_util_mm` e `E:parede_labio_mm` comparam 9,20/1,45 declarados contra 8,50/0,75 do v27 → FALHA. O §3 promete "mede o arquivo"; hoje não mede. | `--cad-dir` no medidor + campo `objeto` no schema + repasse no auditor (diffs prontos) |
| 3 | **`nao_muda` com métrica nula reprova sozinho.** Em `comparar_baseline`, baseline `0.0` → `delta = None` → `aceitavel = (None == 0)` → `False`. | Apareceu na primeira rodada: `interferencia_mm3  0.0 → 0.0  aceitável: **não**`. Removi a métrica de `nao_muda` nesta revisão e documentei — ela continua coberta pelo requisito duro `D5`. | uma linha: `aceitavel = (delta == 0) if delta is not None else abs(novo - antigo) <= 1e-9` |

**Nenhuma tolerância precisa mudar.** Os itens 2 e 3 aumentam o que a régua verifica; o item 1 é
higiene de selo. Enquanto 1 e 2 não forem feitos, a interface **não consegue aprovar nenhuma
proposta nova** — o que torna a PRP-0005 o teste que faltava: ela é a primeira proposta
`tipo=geometria` com STEP real submetida ao auditor.

---

## 7. Pendências que esta proposta **não** resolve (herdadas do v27)

Registradas para não sumirem — e deliberadamente fora do escopo, para não misturar mudanças:

1. **SSOT divergente.** `cad_die_parameters.json` declara `land_length_mm: 10.0` e
   `land_paralelo_real_mm: 8.5`. Se a variante for promovida a master, o SSOT precisa ir junto
   (`land_paralelo_real_mm` 8,50 → 9,20; `exit_chamfer` `1.50 mm x 45°` → `0.80 mm x 45°`) — e o
   `verify_geometry_ssot.py` tem os nominais do chanfro **hard-coded em 1,40 mm**, como está
   documentado no irmão deste relatório.
2. **Furos de pino selados (não conformidade real).** Os 2 furos Ø4 × 12 mm do `Body_A` são
   **cavidades internas fechadas** (3 shells medidos, tanto no master quanto na variante) e o
   `Body_B` não tem furo nenhum: os pinos não alinham as metades. Impossível de usinar como está.
   O gerador tem `--furos-passantes` para estudar a correção em proposta própria (aí sim com
   mudança de volume de aço e nova bipartição).
3. **Recursos de fabricação ausentes no CAD** (medidos como INFO pelo auditor): fixação/aperto
   (0 furos), cartucho de resistência Ø9,5 (0), poço de termopar (0), canais de refrigeração Ø8 (0),
   furação do flange em Z=0 (0). Sem fixação, as metades não fecham contra 27,6 bar.
4. **O gerador legado não reproduz o master** (§2.1). Enquanto isso não for resolvido, o v27 só
   existe como arquivo — não como código.
5. **CI desligado** por falta da permissão `workflows` na credencial (`05_Interface_Auditoria/ci/LEIA-ME.md`).

---

## 8. Decisão pedida ao Humano

1. Re-selar o baseline (item 1) — sem isso a interface está parada.
2. Aplicar ou recusar a v1.1 da régua (itens 2 e 3), com a linha no §9 do protocolo.
3. Reauditar a PRP-0005 e ler o veredito novo.
4. Se aprovado: decidir a **promoção** da variante a master oficial (sobrescrever os seis STEP de
   `01_CAD_MatrizJonatha_Oficial/` e re-congelar o baseline) **junto** com a atualização do SSOT.
   Até lá, a variante vive na subpasta e o master continua sendo o v27.
5. Dizer se as pendências do §7 viram propostas próprias (sugestão de ordem: fixação das metades →
   furos de pino usináveis → controle térmico → flange).
