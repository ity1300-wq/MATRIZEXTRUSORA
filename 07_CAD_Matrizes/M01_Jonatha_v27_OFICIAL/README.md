# M01 — Matriz Jonatha v27.0 (o modelo oficial)

O master aprovado. Nada aqui é editado por decisão de projeto: é o ponto de partida de toda proposta.

| arquivo | o que é |
|---|---|
| `MatrizJonatha.step` | **o modelo oficial único** — 2 sólidos, 469.001,7 mm³ de aço, cascas [3, 1] |
| `MatrizJonatha_Body_A.step` · `_Body_B.step` | as duas metades, partidas no plano Y = 0 |
| `MatrizJonatha_Canal_Fluxo.step` | o funil próprio da v27, 213.945,1 mm³ |
| `MatrizJonatha_Explodida.step` · `_Com_Fluxo.step` | montagens de leitura (A + B + canal) |

sha256 do modelo oficial: `7f26c5c5ba238a12667f2bdf974bc15f001c9103fd480ffb144eb2718e67e04e` — o mesmo número registrado em
`05_Interface_Auditoria/baseline/MATRIZ_3_v27.json`; é por conteúdo (não por caminho) que o portão
`verificar_cadeia.py`, checagem [7], garante a regra 1.

`01_CAD_MatrizJonatha_Oficial/` mantém, com o mesmo nome de arquivo, um atalho (symlink) para cada um destes
seis arquivos: quem referencia o caminho oficial — auditoria, CI, CODEOWNERS — continua achando os mesmos
bytes. O arquivo físico é um só.
