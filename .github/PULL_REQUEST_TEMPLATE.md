# Proposta de engenharia — Protocolo de Auditoria v1.0

## O que esta PR entrega

- [ ] `05_Interface_Auditoria/propostas/PRP-XXXX-<slug>.json` (obrigatório)
- [ ] STEP novo em `01_CAD_MatrizJonatha_Oficial/` (só se `tipo = "geometria"`; hash declarado na proposta)
- [ ] Relatório/diagrama novo em `03_Relatorios_e_Documentacao/` (opcional)

## Checklist do engenheiro (antes de pedir auditoria)

- [ ] `base_commit` é o commit atual da `main`
- [ ] `parametros` usa apenas as chaves documentadas no protocolo §5
- [ ] `esperado` traz números **que eu consigo defender** (o auditor vai recalcular)
- [ ] `nao_muda` lista o que eu prometo não ter tocado
- [ ] não alterei nada em `02_CAD_Modelos_Historicos/`, no SSOT nem nos scripts de auditoria

## Como ler o veredito

O comentário automático do Auditor é o veredito. Traduzindo:

| Estado | O que fazer |
| :--- | :--- |
| **APROVADO** | seguir para o CAD / para a fábrica |
| **APROVADO_COM_RESSALVAS** | seguir, mas ler a lista "Não auditado" |
| **REPROVADO** | número declarado ≠ recalculado, ou métrica degradou fora da tolerância: revisar e reenviar como `-r2` |
| **BLOQUEADO** | requisito duro violado (largura, espessura, borda, envelope, arquivos, zona congelada) |

> Regra do projeto: **nenhum número entra no projeto sem um script que o reproduza.**
