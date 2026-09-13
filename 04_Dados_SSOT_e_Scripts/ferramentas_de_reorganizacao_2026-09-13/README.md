# Ferramentas da reorganização (uma por vez, na ordem)

Não são parte da cadeia do portão: são os scripts **descartáveis** que executaram a mudança de organização e
de nomes, guardados para que outra sessão veja exatamente o que foi feito (e possa repetir um rename
semernovamente se precisar, por exemplo quando nascer a `PRP-0006` com os caminhos da pasta achatada).

| ordem | script | o que fez |
|---|---|---|
| 1 | `passo2_07.py` | criou `07_CAD_Matrizes/` e moveu os STEP das duas Jonatha para as pastas `M01`/`M02` (a primeira versão da organização, depois achatada) |
| 2 | `codemod_07.py` | reescreveu os caminhos `01_/…step` → `07_CAD_Matrizes/M0x/…` em 30 arquivos de código e documento |
| 3 | `readmes_07.py` | escreveu o índice `07_CAD_Matrizes/README.md` + um README por pasta, com o que foi removido do git e o comando que recria cada derivado |
| 4 | `reorg2.py` | **o achatamento**: `M0x_…` → `Matriz_…`, STEP históricos das três matrizes antigas movidos para as pastas delas com **atalho no caminho antigo de `02_/`**, apagamento da "Gedeon corrigida" por inteiro e adaptação do portão (regra 2 passou de `git status` para sha256 dos caminhos selados) |
| 5 | `docs_flat.py` | reescreveu o índice de `07_/` e o README da Gedeon entregue para a estrutura nova, e limpou ponteiros que apontavam para arquivos apagados |
| 6 | `fecha_refutada.py` | tirou a refutada da cadeia do portão e migrou os pares documento × JSON para `RELATORIO_GEDEON_CERTA.md` |
| 7 | `gate_fix.py` | última passada no portão: regra 1 e 2 por conteúdo, sem duplicar a carga do baseline |

Lição registrada aqui porque custa caro repetir: **depois de mudar caminho, rode o portão completo** — o
`verificar_v28.py` e o `renderizar_v28.py` montavam `os.path.join(DIR_CAD, nm)` com variável e o codemod por
nome literal não viu; só o portão inteiro pegou (2026-09-13). E `.gitignore` não des-rastreia: depois de
ignorar um arquivo já rastreado é preciso `git rm --cached`.
