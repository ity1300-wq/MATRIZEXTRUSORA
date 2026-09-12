# Régua v1.1 — mudança proposta (ato humano, §8 do Protocolo)

**Data:** 12/09/2026 · **Autor:** IA engenheira (sessão `arena/01a096e3-matrizextrusora`)
**Destinatário:** responsável humano pelo projeto (`@ity1300-wq`, dono da zona congelada no CODEOWNERS)
**Gatilho:** veredito `PRP-0006` (`05_Interface_Auditoria/vereditos/PRP-0006.md`) — **BLOQUEADO**

> **Nenhum arquivo da zona congelada foi alterado por esta IA.** O que segue é a correção
> *proposta*, com o código exato, para você aplicar (ou recusar). O §8 do protocolo é explícito:
> *"Uma IA nunca afrouxa o próprio critério para passar na própria proposta."* Nada aqui afrouxa
> critério — os três itens **aumentam** o que a régua consegue verificar.

---

## Resumo executivo

A interface de auditoria está hoje **inoperante para propostas novas**, por três motivos
independentes, todos reproduzíveis:

| # | Defeito | Efeito | Onde |
| :-- | :--- | :--- | :--- |
| **1** | Selo do baseline vencido | **toda** proposta nova ou re-auditada sai `BLOQUEADA` em `I5` | `baseline/MATRIZ_3_v27.json` |
| **2** | O auditor não consegue medir um STEP candidato | proposta `tipo=geometria` é julgada pelos números do **master**, nunca do objeto entregue | `verify_geometry_ssot.py`, `auditar_proposta.py`, `esquema/proposta.schema.json` |
| **3** | Métrica de baseline nulo em `nao_muda` marca "aceitável: não" mesmo sem mudança | `REPROVADO` espúrio | `auditar_proposta.py::comparar_baseline` |

O item 1 se resolve com **um comando**. Os itens 2 e 3 exigem edição da zona congelada e re-selo.

---

## Item 1 — selo vencido (bloqueia tudo; resolve em 30 segundos)

### Evidência

```
arquivo: 05_Interface_Auditoria/PROTOCOLO_AUDITORIA.md
  hash no baseline congelado : 1fc0aa5e26f26c6d9a78329484ce087eae98dd81ff4d22fedba805683bc4c065
  hash em disco e em main    : 702d5f2fb7494f3bdc71f78646b76937a0520d6f0076e53084fe59cc38713704
                               (idêntico em 3afcd7c, b065d68, 75b7153, eaf47d0, 00dca9b)
  último re-selo             : 2026-09-12T17:58:21+0000, commit c4371d7b2b81
  hashes_atualizados_em      : 2026-09-12T17:58:21+0000
```

Dos **35** hashes da zona congelada, **exatamente 1** diverge: o do protocolo. Os outros 34
(incluindo os 16 STEP, o SSOT, os `verify_*`, `cfd_*`, `setup_*`, esquemas e scripts do auditor)
conferem byte a byte.

### O que mudou no protocolo (diff legítimo, já está na `main`)

Commit `b065d68` — *"Tira o workflow de .github/workflows (o app do Arena não tem permissão
'workflows')"*:

```diff
-| **A — CI** | `.github/workflows/auditoria.yml` | push numa proposta dispara ...
+| **A — CI** | `.github/workflows/auditoria.yml` (arquivo pronto em `05_Interface_Auditoria/ci/auditoria.yml`, ver `ci/LEIA-ME.md`) | push numa proposta dispara ...
...
+| 1.0.1 | 12/09/2026 | Modos B implementados (`monitor_auditoria.py`, `painel_auditoria.py` com API); ...
```

Ou seja: **documentação**, não critério. O §8 prevê exatamente isso — *"régua alterada exige
re-selo consciente"* — e o re-selo ficou pendente quando o PR #2 foi mesclado.

Os cinco vereditos que estão na `main` (PRP-0000 a PRP-0004) foram emitidos **antes** dessa edição
do protocolo, por isso não acusaram `I5`. Se qualquer um deles for re-auditado hoje — ou se uma
proposta nova for submetida — o resultado é `BLOQUEADO`. Foi o que aconteceu com a PRP-0006.

### Confirmação independente (importante)

O **PR #3** (`proposta/PRP-0005`, "v28.1: fabricação corrigida", 61 arquivos, aberto 26 min antes
desta proposta por outra sessão) chegou **sozinho ao mesmo diagnóstico, com os mesmos hashes**:

> *"`I5` — é do processo, não meu: o hash de `05_Interface_Auditoria/PROTOCOLO_AUDITORIA.md` gravado
> no baseline é `1fc0aa5e…`, e o arquivo no topo da `main` é `702d5f2f…`. Ou seja, o selo ficou para
> trás na própria `main` (os `selos` registrados param em 17:42; `b065d68` mexeu no protocolo depois
> disso). Qualquer proposta, inclusive uma sem nenhuma relação com isso, sai bloqueada por isso hoje."*

Duas sessões independentes, duas propostas sem relação entre si, mesmo bloqueio. Isso encerra a
discussão sobre ser ou não um caso isolado: **a interface está parada na `main`**.

### A régua também já ficou para trás em outro ponto

Em `82666ac` ("Add files via upload", já na `main`) entrou
`02_CAD_Modelos_Historicos/matrizGedeonCerta.step`. A pasta `02_` é protegida e o baseline tem 35
hashes — esse arquivo **não está entre eles**. `checar_imutabilidade()` só compara o que está no
baseline, então ele passa silenciosamente em `I1`; quem acusa é `arquivos_protegidos()`, que o
reportaria em `I7` (INFO) como "arquivo protegido novo (não estava no baseline)". Um modelo
histórico novo sem re-congelamento é exatamente o que o §8 quer evitar: **a régua precisa ser
recongelada também por isso**, não só pelo selo do protocolo.

### E o PR #3 editou a zona congelada (declarado, sem re-selo)

O próprio corpo do PR #3 registra: alterou `04_Dados_SSOT_e_Scripts/cad_die_parameters.json` (blocos
novos) e `04_Dados_SSOT_e_Scripts/verify_geometry_ssot.py` (seção 6, "Tratamento dos achados"), e
**não** rodou `--atualizar-hashes` — corretamente, pois "quem propõe não re-sela a régua pela qual
vai ser medido". Isso dispara `I4`. Ou seja, há **duas** propostas abertas exigindo decisão sua sobre
a zona congelada, por motivos diferentes:

| PR | O que pede da zona congelada | Gate |
| :-- | :--- | :-- |
| **#3** (`proposta/PRP-0005`, v28.1) | aceitar 2 edições já feitas no SSOT e no `verify_geometry_ssot.py`, ou mandá-las para fora da zona protegida | `I4` + `I5` |
| **#4** (este, `PRP-0006`) | nada — não editou a régua; pede que **você** aplique os itens 2 e 3 (medição de candidato) e re-sele | `I5` só |

Se os dois forem mesclados como estão, eles se sobrescrevem em
`05_Interface_Auditoria/propostas/PRP-0005-*` vs `PRP-0006-*` (resolvido: esta proposta foi
renumerada) **e** em `vereditos/`, além de apontarem para direções diferentes da mesma peça: o PR #3
mantém `chanfro_mm = 1,50` (o do master) e ataca fabricação/fixação/cabeçote; esta proposta muda o
chanfro para `0,80` (a previsão aprovada da PRP-0001). **Não são incompatíveis, mas precisam de uma
decisão de ordem sua** — ver §8 do relatório `PRP-0006_STEP_LAND10_CHANFRO080.md`.

### Correção (ato humano)

```bash
python 05_Interface_Auditoria/scripts/auditar_proposta.py --atualizar-hashes
```

O comando **não refaz medições**: só registra o hash corrente e acrescenta uma entrada em
`baseline.selos[]` com data, commit e a lista de arquivos alterados — fica auditável quem re-selou
e por quê. Como `baseline/` está no CODEOWNERS, o commit precisa da sua aprovação.

### Consequência a observar (§8, último parágrafo)

> *"Vereditos emitidos antes de um re-selo ficam superados: apague o arquivo de veredito do ID
> correspondente para forçar a reauditoria com a régua nova."*

Depois do re-selo, para a PRP-0006 valer:

```bash
rm 05_Interface_Auditoria/vereditos/PRP-0006.json 05_Interface_Auditoria/vereditos/PRP-0006.md
python 05_Interface_Auditoria/scripts/auditar_proposta.py \
    05_Interface_Auditoria/propostas/PRP-0006-step-land-10-chanfro-080.json --json --md
```

**Aviso:** só o re-selo **não** aprova a PRP-0006 — ela passaria a sair `REPROVADO` por causa do
item 2 (a régua compara o declarado com o master). Os dois itens precisam entrar juntos.

---

## Item 2 — o auditor não mede o objeto entregue (o mais importante)

### Evidência

`04_Dados_SSOT_e_Scripts/verify_geometry_ssot.py`, linhas 33-34:

```python
RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DIR_CAD = os.path.join(RAIZ, "01_CAD_MatrizJonatha_Oficial")     # <- fixo, sem opção de caminho
```

`05_Interface_Auditoria/scripts/auditar_proposta.py::medir()` chama a bateria sempre sem caminho:

```python
comandos = [
    ("verify_geometry_ssot.py", ["--json"], ARQ_GEOM),
    ("verify_legacy_dies.py",   ["--json"], ARQ_HIST),
    ("avaliacao_matriz3_calculos.py", ["--json"], ARQ_CALC),
]
```

E `main()`, para proposta com objeto entregue, apenas reaproveita a medição do repositório:

```python
else:
    print("[4/5] Proposta com objeto entregue: usando medição direta.")
    previsto = medido          # <- "medição direta" é a do MASTER, não a do STEP da proposta
```

**Resultado medido na PRP-0006:** o STEP entregue tem `land_util = 9,20 mm` e
`parede_labio = 1,45 mm` (medidos nos arquivos gravados, 10/10 conformes — ver
`01_CAD_MatrizJonatha_Oficial/PRP-0001-r2_land10_chanfro080/medicao_variante_prp0006.json`), mas o
veredito registrou `medido 8.5` e `medido 0.75` — os valores do v27 — e marcou `FALHA` nos dois.

O §3 do protocolo promete outra coisa:

| Tipo | Como o Auditor verifica |
| :--- | :--- |
| `geometria` | **mede o arquivo** com `verify_geometry_ssot.py` + `verify_legacy_dies.py` + calcs |

Hoje ele não mede o arquivo. Enquanto isso não mudar, **nenhuma proposta `tipo=geometria` pode ser
aprovada** — a não ser que declare os números do master, o que seria esconder a mudança (e é
exatamente o que esta proposta se recusa a fazer).

### Correção proposta (3 arquivos)

**(a) `04_Dados_SSOT_e_Scripts/verify_geometry_ssot.py`** — aceitar a pasta do candidato e não
sobrescrever o artefato oficial quando estiver medindo candidato:

```diff
 def main():
     ap = argparse.ArgumentParser()
     ap.add_argument("--json", action="store_true", help="salva auditoria_geometrica.json")
     ap.add_argument("--md", action="store_true", help="regenera o relatório .md")
+    ap.add_argument("--cad-dir", default=None,
+                    help="pasta com os STEP a medir (padrão: 01_CAD_MatrizJonatha_Oficial/). "
+                         "Usado para auditar um STEP candidato sem tocar no master oficial.")
+    ap.add_argument("--saida", default=None,
+                    help="caminho do JSON de saída (padrão: 04_Dados_SSOT_e_Scripts/"
+                         "auditoria_geometrica.json). Candidato: grave fora da pasta do SSOT.")
     args = ap.parse_args()
+
+    global DIR_CAD
+    if args.cad_dir:
+        DIR_CAD = args.cad_dir if os.path.isabs(args.cad_dir) \
+            else os.path.join(RAIZ, args.cad_dir)
+        if not os.path.isdir(DIR_CAD):
+            print(f"ERRO: --cad-dir não existe: {DIR_CAD}", file=sys.stderr)
+            return 2
+        print(f"[objeto auditado] STEP lidos de: {os.path.relpath(DIR_CAD, RAIZ)}")
```

e, no bloco que grava o JSON (linhas 287-289 do arquivo atual):

```diff
     if args.json:
-        destino = os.path.join(DIR_DADOS, "auditoria_geometrica.json")
+        destino = args.saida or os.path.join(DIR_DADOS, "auditoria_geometrica.json")
+        if args.saida and not os.path.isabs(destino):
+            destino = os.path.join(RAIZ, destino)
+        os.makedirs(os.path.dirname(destino), exist_ok=True)
         with open(destino, "w", encoding="utf-8") as f:
```

Duas notas do mesmo arquivo:

* `--md` escreve sempre em `03_Relatorios_e_Documentacao/AUDITORIA_GEOMETRICA_MATRIZ_JONATHA.md`
  (linha 396). Ao auditar candidato, **não** usar `--md`, ou o relatório oficial do v27 é
  sobrescrito — a menos que se queira exatamente isso, e aí o caminho também deve virar parâmetro.
* Os nominais do chanfro no bloco `[4]` são **hard-coded em 1,40 mm** ("medido a 0,10 mm da face de
  saída", isto é, chanfro 1,50 × 45°). Medindo um candidato com chanfro 0,80, esses dois itens saem
  `NAO_CONFORME` com razão. O certo é derivar o nominal do SSOT:

```diff
-    checar("Chanfro de saída 1,50 mm x 45° - sobrelargura radial em X",
-           (sec_ch.xmax - sec_ch.xmin - p["land_width_mm"]) / 2, 1.40,
-           tol=0.10, obs="medido a 0,10 mm da face de saída")
-    checar("Chanfro de saída 1,50 mm x 45° - sobrelargura radial em Y",
-           (sec_ch.ymax - sec_ch.ymin - p["land_thickness_mm"]) / 2, 1.40,
-           tol=0.10)
+    chanfro_nom = float(str(p["exit_chamfer"]).split("mm")[0].strip().replace(",", "."))
+    checar(f"Chanfro de saída {chanfro_nom:.2f} mm x 45° - sobrelargura radial em X",
+           (sec_ch.xmax - sec_ch.xmin - p["land_width_mm"]) / 2, chanfro_nom - 0.10,
+           tol=0.10, obs="medido a 0,10 mm da face de saída")
+    checar(f"Chanfro de saída {chanfro_nom:.2f} mm x 45° - sobrelargura radial em Y",
+           (sec_ch.ymax - sec_ch.ymin - p["land_thickness_mm"]) / 2, chanfro_nom - 0.10,
+           tol=0.10)
```

  Isso só funciona depois que o SSOT declarar o chanfro real da peça auditada
  (`exit_chamfer`), que hoje diz `"1.50 mm x 45°"` — ou seja, a medição de candidato exige um SSOT
  de referência por variante, ou o nominal do chanfro passa a vir da proposta. Decisão sua.

**(b) `05_Interface_Auditoria/esquema/proposta.schema.json`** — campo novo, opcional:

```diff
   "cfd_requerido": {
    "type": "boolean"
   },
+  "objeto": {
+   "type": "object",
+   "description": "Onde está o objeto entregue, para propostas tipo 'geometria'. Sem isto o "
+                  "Auditor mede os STEP oficiais de 01_CAD_MatrizJonatha_Oficial/ (o master).",
+   "properties": {
+    "dir_cad": {
+     "type": "string",
+     "description": "pasta (relativa à raiz) com a família de seis STEP: "
+                    "<nome>.step, _Explodida, _Com_Fluxo, _Body_A, _Body_B, _Canal_Fluxo"
+    },
+    "prefixo": {
+     "type": "string",
+     "description": "prefixo dos arquivos, ex.: MatrizJonatha_L10_C0.8"
+    }
+   },
+   "required": ["dir_cad"],
+   "additionalProperties": false
+  },
```

**(c) `05_Interface_Auditoria/scripts/auditar_proposta.py`** — passar o objeto para a bateria e
registrar o que foi medido no veredito:

```diff
-def medir(com_cfd=False, reusar=False):
+def medir(com_cfd=False, reusar=False, objeto=None):
     """Roda a bateria de medição e devolve as métricas + registro do que foi executado."""
     passos, reproduzir = [], []
+    dir_cad = (objeto or {}).get("dir_cad")
     comandos = [
-        ("verify_geometry_ssot.py", ["--json"], ARQ_GEOM),
+        ("verify_geometry_ssot.py",
+         ["--json"] + ([f"--cad-dir={dir_cad}"] if dir_cad else []), ARQ_GEOM),
         ("verify_legacy_dies.py", ["--json"], ARQ_HIST),
         ("avaliacao_matriz3_calculos.py", ["--json"], ARQ_CALC),
     ]
```

```diff
-    passos, reproduzir = medir(com_cfd=com_cfd, reusar=args.reusar_medicoes)
+    objeto = proposta.get("objeto")
+    if proposta["tipo"] == "geometria" and not objeto:
+        print("AVISO: proposta tipo 'geometria' sem campo 'objeto': o Auditor vai medir os STEP "
+              "oficiais (o master), não o arquivo entregue. Declare 'objeto.dir_cad'.",
+              file=sys.stderr)
+    passos, reproduzir = medir(com_cfd=com_cfd, reusar=args.reusar_medicoes, objeto=objeto)
```

```diff
     veredito = {
         "protocolo": PROTOCOLO,
         "proposta_id": proposta["id"],
+        "objeto_medido": objeto or {"dir_cad": "01_CAD_MatrizJonatha_Oficial",
+                                    "nota": "master oficial v27 (nenhum candidato declarado)"},
```

Regras que valem junto (para não abrir brecha):

1. `objeto.dir_cad` **só** é aceito para `tipo = "geometria"`;
2. os seis STEP declarados em `arquivos` precisam existir dentro de `objeto.dir_cad`, com os
   `sha256` batendo — se não bater, `BLOQUEADO`;
3. `objeto.dir_cad` **não** pode ser `01_CAD_MatrizJonatha_Oficial/` raiz nem
   `02_CAD_Modelos_Historicos/` (o master e o histórico só mudam por re-congelamento humano);
4. o veredito passa a trazer `objeto_medido`, para ninguém confundir medição de candidato com
   medição de master;
5. **nenhuma tolerância do §4 muda.** O que muda é *o que se mede*, não *quanto se aceita*.

Com isso, a PRP-0006 fica auditável de verdade:

```json
"objeto": {
  "dir_cad": "01_CAD_MatrizJonatha_Oficial/PRP-0001-r2_land10_chanfro080",
  "prefixo": "MatrizJonatha_L10_C0.8"
}
```

e o esperado é que os `E:` passem a conferir (9,20 / 1,45 / 27,57 medidos no STEP entregue).

---

## Item 3 — `nao_muda` com métrica nula gera reprovação espúria

### Evidência

`auditar_proposta.py::comparar_baseline`:

```python
delta = None if antigo == 0 else round(100 * (novo - antigo) / antigo, 2)
...
if bloqueia:
    aceitavel = delta == 0          # <- com delta None, isto é False
```

Para `interferencia_mm3` (baseline `0.0`), `delta` é `None` e `None == 0` é `False` → a linha sai
como **"aceitável: não"** mesmo sem qualquer mudança. Apareceu no primeiro veredito da PRP-0006:

```
| `interferencia_mm3` | 0.0 | 0.0 | — | neutro | **não** |
```

Como `nao_muda` é gatilho de `REPROVADO`, qualquer proposta que liste uma métrica de baseline nulo
(`interferencia_mm3`, `envelope_residuo_mm3`…) é reprovada por nada. Na prática isso *ensina* o
Engenheiro a omitir métricas de `nao_muda` — o oposto do que o protocolo quer.

### Correção proposta

```diff
         if bloqueia:
-            aceitavel = delta == 0
+            # baseline nulo: não há base percentual; exige igualdade absoluta (com folga numérica)
+            aceitavel = (delta == 0) if delta is not None else (abs(novo - antigo) <= 1e-9)
```

Critério continua **zero mudança** — só deixa de depender de uma divisão que não existe.

---

## Observações menores (não bloqueiam, mas valem registro)

**A. O nome `-r2` não cabe no schema.** O §2 manda criar `PRP-XXXX-r2` para a revisão de uma
proposta, mas `esquema/proposta.schema.json` restringe `id` a `^PRP-[0-9]{4}$` e o `id` nomeia o
arquivo de veredito. Ou o padrão passa a `^PRP-[0-9]{4}(-r[0-9]+)?$` (e o auditor sanitiza o nome
do arquivo), ou o §2 passa a prescrever **novo número** com a linhagem no título/observações. A
PRP-0006 seguiu a segunda leitura.

**B. `modo cfd` empobrece artefatos versionados.** `medir(com_cfd=True)` chama
`cfd_land_crosssection.py --secoes 99.5 103 107`, enquanto
`04_Dados_SSOT_e_Scripts/avaliacao_matriz_3_secoes.json` commitado tem **5** seções
(70 / 95 / 99,5 / 103 / 107), incluindo o funil. Rodar o modo `cfd` sobrescreve o artefato mais
rico com um mais pobre (e o mesmo vale para `avaliacao_matriz_3_uniformidade.json`). Sugestão: o
auditor gravar os artefatos de CFD em pasta própria da proposta, ou reproduzir as 5 seções do
baseline. Nesta sessão os dois arquivos foram restaurados com `git checkout` depois de uma rodada
de verificação — nada foi commitado empobrecido.

**C. `arquivos_protegidos()` não é recursivo.** `os.listdir` na raiz de
`01_CAD_MatrizJonatha_Oficial/` ignora subpastas. Isso é *conveniente* (STEP candidato em subpasta
não entra na zona congelada e não dispara `I7`), mas é implícito. Vale explicitar no §8 que
candidato vive em subpasta e que STEP solto na raiz de `01_` exige re-congelamento.

**D. O CI continua desligado** por falta da permissão `workflows` na credencial (documentado em
`05_Interface_Auditoria/ci/LEIA-ME.md`). Só você consegue ligar: criar
`.github/workflows/auditoria.yml` pela interface web do GitHub, ou dar push com credencial que
tenha o escopo `workflow`.

---

## Checklist para você (na ordem)

- [ ] 1. `python 05_Interface_Auditoria/scripts/auditar_proposta.py --atualizar-hashes` (item 1)
- [ ] 2. Aplicar os diffs dos itens 2 e 3 (ou recusá-los, registrando o motivo)
- [ ] 3. Acrescentar a linha `1.1` no histórico de versões do §9 do protocolo, dizendo o que mudou
- [ ] 4. Re-selar de novo (`--atualizar-hashes`), já com os scripts editados
- [ ] 5. `rm 05_Interface_Auditoria/vereditos/PRP-0006.*` e reauditar a PRP-0006
- [ ] 6. Se o veredito vier `APROVADO`: decidir a promoção da variante a master (sobrescrever os
      seis STEP oficiais é ato seu) **e** atualizar o SSOT
      (`cad_die_parameters.json`: `land_paralelo_real_mm` 8,50 → 9,20, `exit_chamfer`
      `1.50 mm x 45°` → `0.80 mm x 45°`) — que também é zona congelada
- [ ] 7. (Opcional) Ligar o CI (item D)

Enquanto os itens 1 e 2 não forem feitos, o estado real do projeto é: **a interface de auditoria
existe e funciona, mas não consegue aprovar nenhuma proposta nova** — nem a de controle.
