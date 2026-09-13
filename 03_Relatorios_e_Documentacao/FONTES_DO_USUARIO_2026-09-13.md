# Fontes do usuário em 2026-09-13 — o que chegou por fora do git, e por que fica fora

As oito capturas abaixo são o material que ele mandou pela conversa (o app salvou em `~/uploads/` do sandbox).
**Não entram no repositório porque ele é público**: duas delas eu abri e conferi agora — são tela do navegador
com o **endereço da sessão do agente** (`arena.ai/agent/…`), o texto da própria conversa e a barra de status do
celular (hora, bateria, operadora). Isso não é coisa de repositório público. O que interessa delas já foi
extraído e está medido/transcrito no repo (coluna final).

Se você quiser as imagens no git mesmo assim, o caminho é um só: tornar o repo privado
(`gh repo edit --visibility private` ou no site) e aí eu subo as oito com os hashes abaixo conferidos.

| arquivo (em `~/uploads/`) | tamanho | sha256 | o que é, e o que rendeu |
|---|---|---|---|
| `Screenshot_20260911-223424.Chrome.png` | 270.922 B | `44d47492b388feee…5e5bbc87` | print da conversa em que ele **desenhou por cima**: azul = extrusora, vermelho = cabeçote, branco = matriz, com a peça em traço branco no meio. Origem declarada de `decisoes_usuario` no SSOT (D1 fixação fechada pela máquina, D2 lábio de saída) — conferido visualmente nesta data |
| `Screenshot_20260911-235016.Chrome.png` | 211.474 B | `bddb09638ab85206…6ca73e97` | mesma noite, continuação das anotações sobre o mesmo print (não re-inspecionado nesta tacada; usado na rodada das perguntas D1–D4 reescritas em termos simples) |
| `Screenshot_20260911-235056.Chrome.png` | 244.870 B | `8c84ebe9b14c72b4…74b01080` | idem ao de cima |
| `Screenshot_20260912-120223.Visualizador 3D e CAD.png` | 191.970 B | `1a8299c566cbb875…d2215ed0` | visão dele no visualizador 3D do celular, na rodada em que apareceu a correção "o cabeçote é só esta parte do desenho" (não re-inspecionado nesta tacada) |
| `Screenshot_20260912-121529.Fotos.png` | 333.570 B | `7a7361b7cdf8c0ff…8f2880ed` | a galeria dele aberta no **meu render** `cab_vista_esq.png` — dá para ler a legenda no topo (`/home/user/cab_vista_esq.png (grade = 1,000 unidade do DXF; k = 21,28 mm/un)`), a vista esquerda do cabeçote com `CHANF. 10X45°`, Ø130/Ø80, Ø90 +0,1 e os 11 / 20 / 40 / 70 / 81 do desenho. Conferido visualmente nesta data. É a pista de que a escala lida por ele era `k = 21,28` num recorte e `25,534` na folha inteira — a que vale é a da folha, calibrada no centro dos furos da junta |
| `Screenshot_20260912-132414.Visualizador 3D e CAD.png` | 123.087 B | `c7107ef1bd79ea11…65c17762` | visualizador 3D, rodada do backup `matrizGedeonCerta.step` (não re-inspecionado) |
| `Screenshot_20260912-132436.Visualizador 3D e CAD.png` | 117.382 B | `07022845603475d0…f8747db8` | idem ao de cima |
| `Screenshot_20260912-190254.Visualizador 3D e CAD.png` | 198.040 B | `6f797d3ac6fed43e…b9d634bd` | visualizador 3D na noite em que ele disse que a nossa "Gedeon corrigida" estava errada e que o arquivo dele é a matriz certa (não re-inspecionado) |

## O que já está no git, vindo desses arquivos

* o **croquis em DWG** em si: `030-032- cabeçote.dwg` (148.494 B, na raiz do repo) — este sim versionado;
* o **DXF convertido** dele: `04_Dados_SSOT_e_Scripts/cabecote.dxf.xz` (603.476 B, round-trip conferido por
  sha256), de onde `medir_perfil_cabecote.py` tira o meio-corte em mm (`04_/cabecote_perfil.json`,
  k = 25,534 mm/unidade);
* as **cotas lidas nas capturas** com traço colorido: registradas como decisões em
  `04_/cad_die_parameters.json` → `decisoes_usuario` (D1 fixação pelo collete EX-031 + degrau, D2 chanfro
  1,50 × 45° do master mantido, D3 funil, D4 promover em aberto, D5 a Gedeon dele é a certa, D6 uma pasta por
  matriz, D7 método de auditoria v1.0 encerrado, D8 sessão no GitHub) — que é de onde o `AUTO_PROMPT` é gerado;
* as **medidas da matriz dele** (`matrizGedeonCerta.step`) que as capturas ajudaram a interpretar:
  `07_CAD_Matrizes/Matriz_Gedeon_Certa/` + `03_/RELATORIO_GEDEON_CERTA.md` + `04_/gedeon_certa.json`.

Nada disso depende de ter a imagem no git para ser conferido — o hash acima serve para provar que um arquivo
restaurado depois é exatamente o mesmo que a sessão usou.
