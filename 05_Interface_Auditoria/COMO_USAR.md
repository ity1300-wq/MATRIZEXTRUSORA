# Como usar a interface de auditoria (guia rápido)

> Contrato completo: `PROTOCOLO_AUDITORIA.md`. Este arquivo é só o "manual de botão".
> Tudo funciona **sem GitHub** (Modo B). O GitHub (Modo A) só acrescenta o registro remoto.

## Papéis

| Papel | Escreve | Lê |
| :--- | :--- | :--- |
| **IA engenheira** | `propostas/PRP-XXXX-<apelido>.json` | `vereditos/PRP-XXXX.json` e `.md` |
| **IA auditora** | `vereditos/…` (gerados pelos scripts) | `propostas/…` |
| **Humano** | — | painel no navegador (porta 8000) |

## Passo 1 — a IA engenheira escreve a proposta

Um arquivo JSON em `propostas/`, seguindo `esquema/proposta.schema.json`.
A **fonte da verdade** dos campos é `esquema/proposta.schema.json`; hoje os obrigatórios são: `protocolo, id, titulo, autor, data, tipo, base_commit, objetivo,`
`parametros, esperado, nao_muda, justificativa, riscos`.
Opcionais: `arquivos` (o que a mudança tocaria no CAD), `cfd_requerido`, `observacoes`.

Regras de ouro:

- A proposta **não edita nada** em `01_CAD_*` nem em `02_*` — ela *descreve* a mudança.
- `esperado` é a previsão numérica da IA engenheira. É isso que o auditor confere.
- `nao_muda` lista o que tem de continuar idêntico (largura, espessura, boca, envelope…).
- Declarar uma grandeza que o auditor não consegue verificar não é proibido — mas o veredito sai
  como `APROVADO_COM_RESSALVAS`, nunca como aprovação silenciosa.
- Mudar a **régua** (scripts do auditor, baseline, SSOT) não é proposta: é re-selo
  (§8 do protocolo, via `--atualizar-hashes`); sem isso, o gate I5 bloqueia todo mundo.

## Passo 2 — submeter a auditoria

Três caminhos, mesmo resultado:

```bash
export LD_LIBRARY_PATH="$PWD/04_Dados_SSOT_e_Scripts/.headless_gl:$LD_LIBRARY_PATH"
PY=/home/user/.venv/bin/python

# a) linha de comando, síncrono, com veredito em JSON e Markdown
$PY 05_Interface_Auditoria/scripts/auditar_proposta.py \
    05_Interface_Auditoria/propostas/PRP-0005-<apelido>.json --json --md

# b) monitor: audita o que estiver na pasta (uma passada ou vigília contínua)
$PY 05_Interface_Auditoria/scripts/monitor_auditoria.py --uma-vez --modo completo

# c) painel/API (útil para outra IA ou para script remoto; o corpo é a proposta)
curl -sS -X POST "http://<host>:8000/api/auditar?modo=completo&sincrono=1" \
     -H "Content-Type: application/json" \
     --data-binary @05_Interface_Auditoria/propostas/PRP-0005-<apelido>.json
```

Modos: `rapido` (reutiliza medições em cache) · `completo` (mede do zero — é o padrão) ·
`cfd` (acrescenta as rodadas de CFD, minutos em vez de segundos, requer o ambiente do `setup_cfd_env.sh`).

## Passo 3 — a IA engenheira lê o veredito

`vereditos/PRP-XXXX.json` (+ `.md` para leitura humana). Campos-chave: `estado`, `resumo`,
`checks` (I1–I8), `metricas`, `comparacao_baseline`, `bloqueios`, `alertas`, `recomendacoes`,
`nao_auditavel`, `hashes` e `reproduzir` (comandos para refazer a conta do zero).

| Estado | Código de saída | O que a IA engenheira faz |
| :--- | :--- | :--- |
| `APROVADO` | 0 | pode seguir para o CAD |
| `APROVADO_COM_RESSALVAS` | 3 | seguir, mas responder item por item o que ficou não auditado |
| `REPROVADO` | 2 | a previsão não bateu ou degradou fora da tolerância: revisar a proposta |
| `BLOQUEADO` | 4 | a proposta ou a régua foi adulterada (hash/histórico): parar e avisar o humano |

Veredito emitido em modo `rapido` fica marcado com `medicoes_reutilizadas: true` — serve para
triagem, não para fechar o ciclo.

## Onde estão os números que decidem

- Tolerâncias e critérios de aceitação: §4 do protocolo.
- Requisitos duros (largura 75,00 · espessura 1,50 com R0,75 · boca Ø75,60 · envelope da Matriz 2):
  §5, e são verificados por `04_Dados_SSOT_e_Scripts/verify_geometry_ssot.py`.
- Régua atual (35 hashes da zona congelada + selos): `baseline/MATRIZ_3_v27.json`.
- Parâmetros oficiais do projeto: `04_Dados_SSOT_e_Scripts/cad_die_parameters.json`.

## Modo A (GitHub)

O `CODEOWNERS` e o template de PR já estão no lugar. O workflow do CI está **pronto mas
desativado**: mora em `ci/auditoria.yml` porque o app do Arena não tem a permissão `workflows`
para criar arquivos dentro de `.github/workflows/`. Para ligar, copie o arquivo para
`.github/workflows/auditoria.yml` (passo a passo em `ci/LEIA-ME.md`) — nada mais muda.

Mesmo sem o CI, o `monitor_auditoria.py` roda com `--remoto --push` e cada veredito vira um
commit rastreável no repositório.
