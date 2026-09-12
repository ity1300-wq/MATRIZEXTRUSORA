# Protocolo de Auditoria — Engenheiro IA ⇄ Auditor IA

**Versão:** 1.0 · **Data:** 12/09/2026 · **Alteração deste documento:** só o humano (ver §8)

Este documento é o **contrato**. Ele define como a IA que projeta (Engenheiro) e a IA que audita
(Auditor) trocam informação através do GitHub, sem ambiguidade e sem depender de conversa.

> **Regra fundadora:** *nenhum número entra no projeto sem um script que o reproduza.*
> Toda afirmação numérica é uma **proposta**; todo número medido é um **veredito**.

---

## 1. Papéis

| Papel | Quem | Pode escrever em | Nunca pode |
| :--- | :--- | :--- | :--- |
| **Engenheiro** | IA de projeto (ChatGPT/Claude/etc.) | `01_CAD_MatrizJonatha_Oficial/`, `05_.../propostas/`, `03_.../` (relatórios novos) | alterar `04_.../` (SSOT e scripts de auditoria), alterar `PROTOCOLO_AUDITORIA.md` |
| **Auditor** | IA de auditoria (esta sessão / CI) | `05_.../vereditos/`, `05_.../baseline/` | alterar CAD, SSOT, ou o objeto auditado |
| **Humano** | você | tudo | — |

**Separação de poderes:** quem projeta não afrouxa o critério; quem audita não mexe no objeto
auditado. Os scripts de medição e este protocolo são **zona congelada** (ver §8).

---

## 2. O ciclo (uma iteração = ~6 minutos)

```
 ENGENHEIRO                          GITHUB                            AUDITOR
     │                                  │                                  │
 (1) │ escreve propostas/PRP-XXXX.json ─▶│                                  │
     │ + STEP novo (se houver)          │                                  │
     │                                  │ (2) push do branch               │
     │                                  │     proposta/PRP-XXXX            │
     │                                  │                                  │
     │                                  │◀─ (3) auditar_proposta.py ───────│
     │                                  │        (automático no CI)        │
     │                                  │                                  │
     │◀─ (4) vereditos/PRP-XXXX.json ───│                                  │
     │       + vereditos/PRP-XXXX.md    │                                  │
     │       + comentário no PR         │                                  │
     │                                  │                                  │
 (5) │ lê o veredito, corrige, volta ao passo (1)                           │
```

**Convenção de nomes**

| Item | Formato |
| :--- | :--- |
| Branch da proposta | `proposta/PRP-XXXX` |
| Arquivo da proposta | `05_Interface_Auditoria/propostas/PRP-XXXX-<slug>.json` |
| Veredito JSON | `05_Interface_Auditoria/vereditos/PRP-XXXX.json` |
| Veredito legível (comentário do PR) | `05_Interface_Auditoria/vereditos/PRP-XXXX.md` |

Uma proposta **nunca** é editada depois de auditada: muda-se o conteúdo e cria-se `PRP-XXXX-r2`.
Assim o histórico mostra a evolução (é isso que permite medir "melhorou ou não"). **Exceção:** o
`base_commit` pode ser atualizado quando o repositório anda (o auditor bloqueia propostas cuja base
ficou para trás), desde que o motivo fique registrado em `observacoes`.

---

## 3. A proposta (o que o Engenheiro entrega)

Arquivo JSON validado por `esquema/proposta.schema.json`. Campos:

| Campo | Obrigatório | Descrição |
| :--- | :--- | :--- |
| `protocolo` | sim | versão do protocolo que o Engenheiro está seguindo (`"1.0"`) |
| `id` | sim | `PRP-XXXX` |
| `titulo` | sim | uma linha |
| `autor` | sim | quem propõe (nome do modelo/IA) |
| `data` | sim | ISO 8601 |
| `tipo` | sim | `calculo` \| `geometria` \| `processo` |
| `base_commit` | sim | commit do qual a proposta parte (o Auditor compara com ele) |
| `objetivo` | sim | o que melhora e por quê |
| `arquivos` | se `tipo=geometria` | caminho + `sha256` de cada arquivo entregue |
| `parametros` | sim | o que muda, com valor novo (ver §5) |
| `esperado` | sim | **previsão numérica** do que vai acontecer (é isto que será conferido) |
| `nao_muda` | sim | lista de métricas que devem permanecer iguais ao baseline |
| `justificativa` | sim | física/cálculo que sustenta a previsão |
| `riscos` | sim | o que pode dar errado |
| `cfd_requerido` | não | `true` se a proposta exige auditoria com CFD (mais lenta) |

**Tipos de proposta**

| Tipo | Quando usar | Como o Auditor verifica |
| :--- | :--- | :--- |
| `calculo` | mudança ainda não modelada (previsão) | recalcula com o **modelo paramétrico** (§5) e compara com `esperado` |
| `geometria` | entrega STEP novo | **mede o arquivo** com `verify_geometry_ssot.py` + `verify_legacy_dies.py` + calcs |
| `processo` | sem mudança de CAD (puxada, temperatura, torque) | confere consistência com o baseline e os limites operacionais |

---

## 4. O veredito (o que o Auditor devolve)

Arquivo JSON validado por `esquema/veredito.schema.json`, mais um `.md` curto para o comentário do PR.

| Campo | Descrição |
| :--- | :--- |
| `estado` | `APROVADO` \| `APROVADO_COM_RESSALVAS` \| `REPROVADO` \| `BLOQUEADO` |
| `resumo` | uma frase, em português, dizendo o que fazer |
| `checks[]` | cada requisito: `o_que`, `nominal`, `medido`, `tolerancia`, `severidade`, `resultado` |
| `comparacao_baseline[]` | métrica a métrica: baseline → proposto, `delta_pct`, `direcao`, `aceitavel` |
| `bloqueios[]` | o que impede seguir (só quando `BLOQUEADO`) |
| `recomendacoes[]` | o que o Auditor sugere |
| `nao_auditavel[]` | o que **não** foi verificado e por quê (silêncio nunca é aprovação) |
| `reproduzir` | comandos exatos usados nesta auditoria |
| `hashes` | `sha256` do STEP, dos JSONs medidos e dos scripts usados |

### Severidades e o que cada uma faz

| Severidade | Significado | Efeito no estado |
| :--- | :--- | :--- |
| **BLOCKER** | requisito duro violado (não é questão de opinião) | → `BLOQUEADO` |
| **ALERTA** | degradação além da tolerância, ou número declarado ≠ medido | → `REPROVADO` |
| **INFO** | dado registrado, sem julgamento | não altera o estado |

### Critérios de aceite (tolerâncias v1.0)

| Verificação | Tolerância | Severidade |
| :--- | :--- | :--- |
| Largura da fenda = 75,00 mm | ± 0,05 mm | BLOCKER |
| Espessura da fenda = 1,50 mm | ± 0,02 mm | BLOCKER |
| Raio de borda = 0,75 mm | ± 0,02 mm | BLOCKER |
| Boca de entrada ≤ Ø75,60 mm | + 0,00 / − 0,10 mm | BLOCKER |
| Envelope externo (Ø93 / Ø89,5 / Ø79,5 × 109) | ± 0,05 mm | BLOCKER |
| Interferência entre as metades | ≤ 0,01 mm³ | BLOCKER |
| Canal isolado × corpo (consistência) | ≤ 0,5 % | BLOCKER |
| Arquivos entregues são `.step` e `02_CAD_Modelos_Historicos/` intacto | — | BLOCKER |
| SSOT alterado sem estar declarado na proposta | — | BLOCKER |
| Métrica declarada em `esperado` × recalculada pelo Auditor | ± 15 % | ALERTA |
| Δp total piora vs baseline | + 15 % (máx.) | ALERTA |
| Uniformidade do núcleo piora vs baseline | − 5 % relativo | ALERTA |
| τ de parede no land | ≤ 200 kPa | ALERTA |
| Residência de parede piora vs baseline | + 30 % | ALERTA |
| Qualquer métrica em `nao_muda` que mudou | 0 % | BLOCKER |
| Métricas não medidas (ex.: CFD não rodado) | — | → `nao_auditavel[]` |

---

## 5. Modelo paramétrico do Auditor (v1.0)

Para propostas do tipo `calculo`, o Auditor não "acredita": ele recalcula por um modelo declarado,
calibrado no próprio v27 medido. **Parâmetros aceitos:**

| Parâmetro | Faixa | Significado |
| :--- | :--- | :--- |
| `land_total_mm` | 8,5 – 12,0 | comprimento total do trecho de saída (Z = 99 → 109) |
| `chanfro_mm` | 0,5 – 1,5 | comprimento do chanfro de saída a 45° |

**Relações (todas calibradas no v27 medido):**

```
land_util_mm    = land_total_mm − chanfro_mm            (v27: 10,0 − 1,5 = 8,5 ✔ medido)
parede_labio_mm = 2,25 − chanfro_mm                     (v27: 2,25 − 1,50 = 0,75 ✔ medido)
dp_total_bar    = 6,73 + 2,187·land_util_mm + 0,907·chanfro_mm
                   └─ 6,73 bar = entrada + funil + aproximação (constante, do perfil 1D medido)
                   └─ 2,187 bar/mm = gradiente do land (analítico; CFD 2D confere em 0,6 %)
                   └─ 0,907 bar/mm = gradiente médio do chanfro (medido no v27)
```

**Limites conhecidos (registrados no veredito, não escondidos):** o modelo não captura a perda
extensional da convergência (−4 a +15 bar, ver relatório de avaliação), não modela o alívio de borda
(esse exige `cfd_edge_relief.py`) e não prevê inchamento/superfície livre.

**Métricas fora do modelo:** se a proposta declara uma métrica que o Auditor não sabe recalcular,
ela entra em `nao_auditavel[]` — nunca é tratada como aprovada.

---

## 6. Requisitos duros (o que bloqueia sempre)

1. Largura 75,00 mm constante, espessura 1,50 mm com R0,75 nas bordas;
2. Boca de entrada restrita a Ø75,60 mm;
3. Envelope externo idêntico à Matriz 2;
4. Todos os entregáveis CAD em `.step`;
5. `02_CAD_Modelos_Historicos/` **nunca** editado;
6. `01_CAD_MatrizJonatha_Oficial/MatrizJonatha.step` é o master oficial (SSOT v27);
7. Métrica marcada em `nao_muda` não pode ter mudado;
8. Nada auditável pode ficar sem verificação silenciosa — ou é medido, ou entra em `nao_auditavel[]`.

---

## 7. Modos de operação (todos implementados neste repositório)

| Modo | Ferramenta | Como funciona | Latência |
| :--- | :--- | :--- | :--- |
| **A — CI** | `.github/workflows/auditoria.yml` | push numa proposta dispara a auditoria e o veredito volta como comentário no PR | ~6 min |
| **B — vigilância git** | `scripts/monitor_auditoria.py` | observa o ramo; commit que toca `propostas/` é auditado e o veredito é gravado (e publicado com `--push`) | ~2 min por proposta |
| **B — painel vivo** | `scripts/painel_auditoria.py` | navegador + API: vigia a pasta, permite colar uma proposta e auditar na hora | segundos a minutos |
| **C — ponte humana** | o próprio auditor | você cola o JSON no chat; o auditor devolve o `veredito.md` para colar de volta | minutos |

O conteúdo é o mesmo nos quatro: o `.json` é o contrato, o `.md` é a cortesia.

### Modo B — vigilância git

```bash
python 05_Interface_Auditoria/scripts/monitor_auditoria.py                 # vigia o ramo atual
python 05_Interface_Auditoria/scripts/monitor_auditoria.py --remoto --push # busca no origin e publica
python 05_Interface_Auditoria/scripts/monitor_auditoria.py --modo rapido --uma-vez
```
Pega propostas commitadas **e** as que estão apenas na árvore de trabalho (basta gravar o arquivo);
pula o que já tem veredito para o mesmo conteúdo; registra o batimento de cada ciclo.

### Modo B — painel vivo (sem git, sem GitHub)

```bash
python 05_Interface_Auditoria/scripts/painel_auditoria.py --porta 8000 --modo completo
```
Abre em `http://localhost:8000` e mostra: baseline congelado, vereditos em disco, histórico da
sessão, log e um formulário para colar propostas. A IA engenheira pode falar direto com a API:

```bash
curl -X POST 'http://localhost:8000/api/auditar?modo=completo&sincrono=1' \
     -H 'Content-Type: application/json' --data-binary @proposta.json
# -> 200 OK com o veredito completo em JSON  (modo=rapido reaproveita medições, ~2 s)
```

Rotas: `/`, `/veredito/<ID>`, `/api/estado`, `/api/vereditos`, `/api/vereditos/<ID>`,
`/api/auditar`, `/auditar`, `/log`.

## 8. Zona congelada (ninguém, nem IA, mexe sem você)

`05_Interface_Auditoria/PROTOCOLO_AUDITORIA.md`, `05_Interface_Auditoria/esquema/`,
`05_Interface_Auditoria/scripts/`, `04_Dados_SSOT_e_Scripts/verify_*.py`,
`04_Dados_SSOT_e_Scripts/cad_die_parameters.json`.

Se o Auditor errou a régua, **você** corrige e sobe a versão (1.0 → 1.1) com uma nota do que mudou.
Uma IA nunca afrouxa o próprio critério para passar na própria proposta.

### O selo da régua (aprendido na prática)

Quem altera qualquer arquivo protegido invalida o **selo** do baseline — e a partir daí **toda**
proposta é bloqueada no check `I5`, inclusive as que nada têm a ver com a mudança. Isso aconteceu
três vezes enquanto esta interface era construída (o próprio auditor editando os próprios scripts) e
é o comportamento **desejado**: régua alterada exige re-selo consciente.

```bash
python 05_Interface_Auditoria/scripts/auditar_proposta.py --atualizar-hashes
# re-sela a zona congelada (NÃO refaz medições) e registra quem/o quê/quando em "selos"
```

O re-selo é ato **humano** (ou do Auditor agindo em nome do humano) e fica auditável no histórico do
baseline: `selos[]` guarda data, commit e a lista de arquivos alterados. Uma IA que altera a régua
para se autoaprovar aparece nesse registro.

Vereditos emitidos antes de um re-selo ficam **superados**: apague o arquivo de veredito do ID
correspondente para forçar a reauditoria com a régua nova.

---

## 9. Histórico de versões

| Versão | Data | Mudança |
| :--- | :--- | :--- |
| 1.0 | 12/09/2026 | Primeira versão: contrato, esquemas, tolerâncias, modelo paramétrico, CI |
