# CI da auditoria (Modo A) — pronto, mas desativado

O workflow existe neste diretório (`auditoria.yml`) e **não** está em `.github/workflows/`
de propósito: a credencial que opera este repositório no Arena é um GitHub App **sem a
permissão `workflows`**, e o GitHub recusa qualquer push que crie ou altere arquivos dentro de
`.github/workflows/`. Tentar empurrar de lá devolve:

```
! [remote rejected] ... (refusing to allow a GitHub App to create or update workflow
`.github/workflows/auditoria.yml` without `workflows` permission)
```

Mantendo o arquivo aqui o repositório fica íntegro e o CI é ligado com um copiar-e-colar,
na hora que você quiser.

## Ligar o CI (2 minutos)

1. Copie o arquivo para o lugar que o GitHub executa:

   ```bash
   mkdir -p .github/workflows
   cp 05_Interface_Auditoria/ci/auditoria.yml .github/workflows/auditoria.yml
   git add .github/workflows/auditoria.yml
   git commit -m "Ativa o CI da auditoria (Modo A)"
   git push
   ```

   > O push precisa ser feito por uma credencial com a permissão `workflows` (o usuário dono do
   > repositório no próprio GitHub, ou um token com escopo `workflow`). Se o push for recusado
   > pelo mesmo motivo, use a interface web do GitHub: *Add file → Create new file* →
   > `.github/workflows/auditoria.yml` → cole o conteúdo.

2. Confira em **Actions** que o workflow aparece na lista.

## O que ele faz

Em cada pull request que toca `05_Interface_Auditoria/propostas/`, ele roda o auditor
(`scripts/auditar_proposta.py`) no runner do GitHub, guarda o veredito como artefato e comenta o
resultado no PR. É o mesmo auditor do Modo B — muda só quem executa.

## Alternativa sem CI

O `monitor_auditoria.py` já faz o serviço no seu computador, sem GitHub nenhum:

```bash
python 05_Interface_Auditoria/scripts/monitor_auditoria.py --uma-vez --modo completo   # uma passada
python 05_Interface_Auditoria/scripts/monitor_auditoria.py                             # vigília contínua
python 05_Interface_Auditoria/scripts/monitor_auditoria.py --remoto --push              # versiona o veredito
```
