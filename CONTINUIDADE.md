# CONTINUIDADE — retome daqui, sem a conversa

**Este arquivo + `git log` = a sessão.** Se a conversa do agente for perdida, qualquer pessoa ou outra IA
com acesso a este repositório consegue continuar exatamente de onde paramos lendo este arquivo e o histórico
dos commits. Nada de decisão vive só no chat: o que vale está aqui, nos relatórios de
`03_Relatorios_e_Documentacao/` e nos JSON de `04_Dados_SSOT_e_Scripts/`.

Atualizado em **2026-09-23**, na rodada que publicou as revisões de 2026-09-22 (v29 re-feita e v30) com o
desenho cotado a partir do STEP medido e a regra de publicação do §12 ("sempre atualize o GitHub"). O
estado anterior desta linha era **2026-09-13 (fim do dia)**, na rodada que promoveu a peça única a v29.0 e
montou o pacote de usinagem `08_Pacote_Usinagem_v29/`.

---

## 1. Estado em uma frase

A **Matriz Jonatha v29.0 (peça única)** é o modelo oficial desde 2026-09-13 e tem **pasta de fábrica pronta**
(`08_Pacote_Usinagem_v29/`); a v27.0 bipartida continua no disco byte a byte (baseline selado, portão
verificando), a variante **v28.1** está verificada mas **não promovida**; a **Gedeon certa é o arquivo do
usuário entregue como está**, medido face por face; a auditoria de correlações roda e acusa 1 divergência
conhecida (a cara PLANE degenerada do `MatrizJonatha_v28_Body_B.step`, centro [37,02; 0,56; 99,00]) e está
com o veredito **pausado por ordem dele** ("`ignore auditoria agora`").

**Rodada 2026-09-13 (fim do dia) — promoção, pacote de usinagem e a pergunta do comprimento.**
* **Promoção:** `gerar_pacote_usinagem_v29.py` copia os três STEP (peça única, canal, montagem no cabeçote) para
  `07_/Matriz_Jonatha_v29_OFICIAL/` e `08_/3D/`, cria o atalho `01_/MatrizJonatha_v29_PECA_UNICA.step`, declara
  `matriz_oficial` + `decisoes_usuario.D9` + `usinagem_v29` no SSOT e atualiza os índices. Nada do histórico foi
  reescrito — `verificar_cadeia.py` confirma o sha256 do master v27.0 (`7f26c5c5ba238a12…`) a cada rodada.
* **Pacote:** 6 documentos + prancha 2D cotada (PDF e PNG, desenhada a partir das seções medidas no STEP) +
  JSON + checksums, com as cotas críticas: Ø89,50 e Ø79,50 em 0/−0,02 (fecham o anel de 0,25 mm), fenda
  1,500 +0,010/−0,000 medida em Z = saída − 2,00, área da seção do canal 112,0171 mm² ±0,5 % como critério de
  rejeição, 1.2344 (H13) a 50-52 HRC, sem revestimento, e a proibição expressa de furo/flange/pino.
* **109 × 100:** respondido com conta (não com opinião) em `03_/SIMULACAO_ROTAS_E_COMPRIMENTO.md` — gera por
  `simular_rotas_e_comprimento.py`, que mede o **land paralelo** de cada matriz no STEP: Gedeon CERTA 88,50 mm
  (ΔP 963 bar, 9,14 % escapando pelo anel) contra 8,50 mm da Jonatha (ΔP 220 bar, 0,067 %). Encurtar a peça não
  muda o ΔP e piora a fuga; as alavancas são o land e a folga do anel.
* **Reologia:** a âncora passou de "fator sobre o K do termoplastico" (dava 820 MPa de ΔP, absurdo) para
  **η(100 s⁻¹) = 1.500 / 5.000 / 15.000 Pa·s**, com o motivo escrito no JSON.
* **Ambiente:** o sandbox foi recriado no meio da rodada e levou os atalhos e os pacotes pip de novo —
  `bash 04_Dados_SSOT_e_Scripts/restaurar_workspace.sh` refez os 6 pontos, e o portão continuou verde.

## 2. O que está entregue agora

| peça | onde | estado |
|---|---|---|
| **Matriz Jonatha v29.0 (peça única, OFICIAL)** | `07_CAD_Matrizes/Matriz_Jonatha_v29_OFICIAL/` + `08_Pacote_Usinagem_v29/` | **é o que vai para a fábrica**; gerado por `gerar_pacote_usinagem_v29.py` |
| Matriz Jonatha v27.0 (master anterior) | `07_CAD_Matrizes/Matriz_Jonatha_v27_OFICIAL/` | intocada; `01_CAD_MatrizJonatha_Oficial/` são 6 atalhos para cá; o sha256 do master bate o baseline do auditor |
| Matriz Jonatha v28.1 (proposta DFM) | `07_CAD_Matrizes/Matriz_Jonatha_v28_1_PROPOSTA/` | 64/64 conformes em `verificar_v28.py`; **aguarda aprovação**; PR #3 aberta |
| **Gedeon CERTA (o arquivo do usuário)** | `07_CAD_Matrizes/Matriz_Gedeon_Certa/` + atalho `02_CAD_Modelos_Historicos/matrizGedeonCerta.step` | entregue **como veio**, sem perder aço; o par aberto no plano de partição resolve o único defeito (furos de pino selados) |
| Gedeon entregue (histórica) | `07_CAD_Matrizes/Matriz_Gedeon_Entregue_HISTORICA/` | histórico, só serve de contraste |
| Matriz Copo, Matriz Desenvolvimento | `Matriz_Copo_HISTORICA/`, `Matriz_Desenvolvimento_HISTORICA/` | histórico, só leitura |
| Cabeçote EX-030 e as montagens | `06_CAD_Cabecote_EX-030/STEP/` | 5 STEP: sem flange, desenhado, com a Copo, com a Gedeon antiga, **com a Gedeon certa** + o PDF 2D do conjunto |
| Prancha visual (5 faixas, legível) | `07_CAD_Matrizes/Matriz_Gedeon_Certa/DESENHO_2D_GEDEON_CERTA_X_JONATHA.pdf` | gerada por `desenhar_gedeon_consertada.py` (o nome é do episódio da refutada; o que ela desenha é a CERTA) |

## 3. Regras do projeto que não se negoceiam

Vêm do dono, estão em `03_Relatorios_e_Documentacao/AUTO_PROMPT_CONTINUIDADE_MATRIZ_JONATHA.md` e são
cobradas pelo portão:

1. **Regra 1** — existe um único modelo oficial: `01_CAD_MatrizJonatha_Oficial/MatrizJonatha.step` (v27.0).
   Desde 2026-09-13 o arquivo físico mora em `07_CAD_Matrizes/Matriz_Jonatha_v27_OFICIAL/` e `01_/` tem
   atalho. A checagem é por **sha256 contra o baseline**, não por caminho.
2. **Regra 2** — `02_CAD_Modelos_Historicos/` **não se edita** (ler é permitido; foi o que fizemos para mover
   os STEP para as pastas das matrizes, deixando atalho com os mesmos bytes). O portão confere o sha256 de
   cada caminho selado no baseline e exige que cada atalho aponte para `07_CAD_Matrizes/`.
3. Entregável CAD é **STEP** (AP214). Nada de STL/SAT/"otimização" sem pedido.
4. SSOT numérico: `04_Dados_SSOT_e_Scripts/cad_die_parameters.json`. Largura **75,00 constante**, espessura
   **1,50 com R 0,75**, entrada restrita a **Ø 75,60** em Z = 0, envelope **Ø93,00 × 69,90 / Ø89,50 × 10,80 /
   Ø79,50 × 28,30** (Z total 109,00). — *o envelope deste item é o do contrato original e não vale mais desde
   2026-09-22: os Ø de envelope são **94,00 / 89,00 / 79,00** (±0,5) e a v30 tem Z total **95,00**; o que
   continua rígido é largura, espessura e a boca de entrada, porque é o que vira produto.*
5. Interface obrigatória: a matriz **casa nos estágios** do cabeçote, **passa pelo nariz sem tocar a fenda**,
   fixação por **collete EX-031 + degrau**; a matriz **não tem flange nem furo de fixação**. Encosto
   **face a face** ⇒ rebaixo de 3,00 mm onde Ø > 105,00 (é usinagem da máquina, não da matriz).
6. Zona congelada do contrato (PR #2, `05_Interface_Auditoria/PROTOCOLO_AUDITORIA.md` §8): quem propõe
   escreve em `01_/`, `05_/propostas/` e `03_/`; **não** mexe no protocolo de auditoria nem re-sela baseline
   sem ordem explícita. Uma proposta já auditada não é editada — nasce `PRP-XXXX-r2`.
7. **Todo número citado tem de vir de medição no STEP/DXF**, nunca de memória. Se um relatório e um JSON
   divergem, o JSON medido manda e o relatório é regenerado.

## 4. Como pôr o ambiente de pé (sandbox nova)

```bash
cd MATRIZEXTRUSORA
pip install cadquery numpy matplotlib ezdxf        # cadquery 2.8.x
bash 04_Dados_SSOT_e_Scripts/setup_headless_gl.sh  # compila o stub libGL (a pasta .headless_gl/ NAO vai ao git)
git checkout continue
# o render offscreen precisa de uma biblioteca GL local que fica fora do git:
export LD_LIBRARY_PATH=$PWD/04_Dados_SSOT_e_Scripts/.headless_gl
python3 04_Dados_SSOT_e_Scripts/gerar_gedeon_certa.py        # mede o arquivo do usuario (21 checks)
python3 04_Dados_SSOT_e_Scripts/verificar_cadeia.py          # O PORTAO (roda os 9 scripts, ~4 min)
python3 04_Dados_SSOT_e_Scripts/verificar_cadeia.py --rapido # nao re-gera CAD (para consulta rapida)
```

Se o portão disser `cadquery não está instalado`, é sandbox recriada: `pip install cadquery` (e
`pip install ezdxf gmsh scikit-fem` se for mexer na simulação 3D; aí rode também
`bash 04_Dados_SSOT_e_Scripts/setup_headless_glu.sh`, que fabrica os stubs `libGL`/`libGLU` que o `gmsh` exige
sem root).

**Cuidado com o `git add -A` depois de o sandbox ser recriado** (mordeu em 2026-09-13): o snapshot do workspace
não traz *atalhos*, e `01_CAD_MatrizJonatha_Oficial/` e `02_CAD_Modelos_Historicos/` são exatamente isso — 23
links para dentro de `07_CAD_Matrizes/`. Sem restaurar, o `git add -A` entende que os arquivos foram apagados e
comete a remoção. Antes de commitar, `git status` e, se faltar caminho, `git checkout <último commit bom> --
01_CAD_MatrizJonatha_Oficial 02_CAD_Modelos_Historicos`. O portão agora confere isso sozinho (checagem
"nenhum arquivo rastreado sumiu da árvore" + "os 35 caminhos selados existem no disco") e o `--rapido` já pega. E se ele reclamar
de `libGL.so.1` / o render cair, é porque o clone é novo: rode o `setup_headless_gl.sh` acima (são 36 KB de stub
compilado; o `.headless_gl/` é ignorado de propósito, então não vem do GitHub). **O atalho para tudo isso
é um comando só**: `bash 04_Dados_SSOT_e_Scripts/restaurar_workspace.sh --portao` — ele refaz a identidade do
git, o remoto, restaura por caminho os arquivos rastreados que sumiram (nunca com `checkout -- .`), instala as
quatro bibliotecas, gera os stubs GL/GLU e roda o portão. Idempotente: pode rodar duas vezes.

**Espaço.** O que o painel chama de workspace é o que o snapshot persiste (o `.cache` de 305 MB fica fora).
Depois da limpeza de 2026-09-13: 41 MB no total, sendo 31 MB do repo — dos quais **22 MB são `.git`**
(histórico de STEP; só encolheria reescrevendo histórico, o que não faremos sem ordem) e 8 MB de árvore.
O que é seguro apagar a qualquer momento, porque o portão recria: `04_Dados_SSOT_e_Scripts/__pycache__`,
os PNG soltos da raiz do workspace e `.headless_gl/`. Em 2026-09-13, no pedido de "retire as travas do
GitHub", **o resto do que estava de fora entrou no git**: `06_/STEP/estudos/` (o cabeçote com os furos M12
modelados, 4 arquivos), os dois STEP derivados da v28 (`_Explodida`, `_Com_Fluxo`, 1,2 MB) e as pranchas
`DESENHO_2D_*_p*.png` — eram 2,4 MB de material de trabalho que existia só no sandbox. As regras mortas do
`.gitignore` que os barravam foram apagadas junto (regra que não barra nada também é trava). continuem fora,
por escolha e não por omissão: `.headless_gl/` (binário regenerável), `__pycache__`, os 4 padrões de
`*Gedeon_Corrigida*` (a refutada, por ordem dele), os arquivos de estado do protocolo em `05_/`, e as fontes
do `uploads/` — ver `03_/FONTES_DO_USUARIO_2026-09-13.md` para o comando que põe as 8 capturas lá.
* **Se você quiser verificação automática no GitHub, falta um passo só — e ele é seu.** Escrevi o workflow do
  portão (`04_Dados_SSOT_e_Scripts/ci/portao.yml`: job informativo, `continue-on-error` em tudo, `permissions`
  de só-leitura, sem Modo A — veredito automático em PR continua encerrado por sua ordem) e o push para
  `.github/workflows/` foi **recusado** com `refusing to allow a Personal Access Token to create or update
  workflow ... without 'workflow' scope`. É a mesma parede que o `05_/ci/LEIA-ME.md` do auditor registrou (a
  credencial da plataforma é um App sem a permissão `workflows`; por isso as Actions desta repo têm 0 rodadas).
  Não vou contornar pelo endpoint de conteúdo, porque isso é furar o modelo de permissões do seu token, não
  remover trava do projeto. Ligar: `mkdir -p .github/workflows && cp 04_Dados_SSOT_e_Scripts/ci/portao.yml
  .github/workflows/portao.yml && git add .github/workflows && git commit -m "liga o portao de CI" && git push`
  — ou colar o conteúdo em *Actions → New workflow* na web, que não exige o escopo. Se você recriar o token com
  a marca `workflow`, eu ligo sozinho.
O `--rapido` **não** substitui a porta completa antes de um push — foi uma mudança de caminho feita sem o
portão completo que quebrou dois verificadores em 2026-09-13 (juntavam caminho com variável e foram procurar
o arquivo na pasta errada).

## 5. Números que não se discute mais (todos medidos; reimpressos a cada rodada do portão)

**Na Gedeon certa** (`04_/gedeon_certa.json`, relatório `03_/RELATORIO_GEDEON_CERTA.md`): 1 sólido, 18 faces,
**640.180,7 mm³** de aço, 3 cascas; fenda **75,000 × 1,500 com R 0,75** passante de Z 0,17 a 109,00; cone de
entrada abrindo **Ø 75,60** em Z 0,00 e fechando em Z 20,98; fluxo (cone + fenda) **43.017,9 mm³**;
**2 furos de pino Ø 1,78 × 10,00** em Z 44,50..54,50, |x| 40,61..42,39 — cavidades seladas, 4,11 mm até o
Ø 93,00 (o único defeito do arquivo dele). Conserto medido: partir em Y = 0 dá A 320.090,3617 + B
320.090,3622 (diferença para o bloco **+0,000383 mm³**), 1 casca cada, A ∩ B = 0,0000 mm³. Na colocação
medida: ∩ matriz × cabeçote = **0,0000 mm³**, aço do cabeçote dentro do fluxo = **0,0000 mm³**, face de saída
da matriz **14,00 mm** além da face do cabeçote.

**Gedeon entregue (histórica) × certa**: A ∪ B = **469.156,8 mm³** contra 640.180,7 mm³ — faltam
**171.024,0 mm³** na entregue, que é o funil da Jonatha escavado nela; seção em X = 0: 5.885,5 mm² (entregue)
× 8.776,5 mm² (certa) × 5.883,5 mm² (v27).

**Gedeon certa × v27** (peças inteiras alinhadas pela face Z = 109,00): **171.224,1 mm³** de aço só na certa,
**44,9 mm³** só na v27 (a faixa dos furos de pino). São gêmeas de envelope, não a mesma peça.

**Cabeçote EX-030** (`04_/cabecote_step.json`, `03_/INTERFASE_*`): furo em escada Ø80 | 0..14,02 → Ø90
+0,05/+0,1 | 14,02..25,00 → Ø95 | 25,00..95,00; corpo Ø130 | 0..42; chanfro 10 × 45° | 42..52; flange
Ø220 × 40 com 6 × Ø16,5 (M12) em fendas de 23,5 no C.C. Ø180; piloto Ø105,00 × 3,00. Escala do desenho
DXF: k = 25,534 mm/unidade. O DXF de entrada (6,8 MB, convertido do DWG que ele subiu) vive no repo como
`04_Dados_SSOT_e_Scripts/cabecote.dxf.xz` (0,58 MB, round-trip conferido por sha256) — `medir_perfil_cabecote.py`
compacta/descompacta sozinho, então não precisa de arquivo solto no workspace. Anel de face = (130 − 90)/2 = 20,00 mm radial. Encosto face a face ⇒ rebaixo
3,00 mm onde Ø > 105,00; cartuchos viáveis a partir de Z 99,75 (recomendado 100,25); curso livre da manta
14,220 mm; boca 78,000 × 4,500; junta 6,82 MPa / empuxo 29,843 kN; collete 8,58 MPa fecha a partição; parede
radial da matriz (93,00 − 75,60)/2 = 8,70 mm.

**v28.1** (proposta, `03_/VERIFICACAO_V28.md` + `04_/verificacao_v28.json`): fenda 75,00 × 1,50 R 0,75 (112,0171 mm²), entrada Ø 75,60,
land 8,500 + chanfro 1,500 × 45°, lâmina 0,750, 3,586 kg, abertura da bipartição 55,7 kN, ΔP 1D 41,9 bar,
τ no land 163,8 kPa, `verificar_v28.py` 64 conformes / 0 divergências. Funis alternativos: ΔP 41,9 × 100,9 bar
⇒ **mantém o funil do master**.

## 6. O que o dono do projeto disse (literal, e o que mudou por causa disso)

* *"Matriz corrigida está errada, matriz Gedeon certa.step é de fato a matriz Gedeon certa"* ⇒ a Gedeon é **o
  arquivo dele, como está**; proibido re-escavar canal/funil nele.
* *"ignore auditoria agora"* ⇒ cerimônia de auditoria (PR, veredito, re-selo de baseline, §6 do relatório)
  suspensa até geometria e repo estarem certos. Vários itens abaixo são consequência dessa pausa.
* *"não gostei da organização, cada matriz deve estar numa pasta separada"* ⇒ era o aninhamento `M01..M06` e
  as pastas só com ponteiro; hoje é `07_CAD_Matrizes/Matriz_<nome>/` com os arquivos dentro.
* *"quero que apague a matriz Gedeon corrigida"* ⇒ apaguei por inteiro (gerador, JSON, relatório, 5 STEP,
  montagem), não só do git. Não existe script que a recrie.
* *"o cabeçote é só esta parte do desenho"* (o flange é interface de montagem, não corpo) ⇒ processado; o
  "20 mm" do desenho é o furo M12 medido da face do flange, **não** protrusão livre — a protrusão da matriz
  é 14,00 mm.
* *"está demorando muito seu retorno"* ⇒ prancha e portão só rodam quando há mexida real; verificação CAD
  completa uma vez antes do push; números vindos de cache são marcados como não re-medidos.
* *"Entrei em contato com rapaz para fazer a matriz e essa foi a conversa, sempre atualize o GitHub"*
  (25/09, com o PDF `TRANSCRICAO-matrizaria-COM-IMAGENS.pdf`) ⇒ lida por inteiro e registrada em
  `03_/CONTATO_MATRIZARIA_FERNANDO_2026-09-24.md`. **A matrizaria disse que o canal em funil da v30 não
  equilibra o fluxo do mastique e que "a matriz nunca dá para garantir"; os 4 recursos que ele propõe e a
  decisão A/B que ele abriu estão lá.** Nenhuma cota foi tocada por causa da conversa - decisão é dele.

## 7. Becos fechados — não re-cave (custaram dias)

* **Não existe "Gedeon com funil".** O volume de canal de **213.790,0 mm³** é do arquivo
  `02_/MatrizGedeon_Canal_Fluxo.step` / da Copo; o vazio da Gedeon certa mede **43.017,9 mm³** (cone +
  fenda). Reconstruir a Gedeon cortando o canal histórico no bloco dele foi a tentativa refutada: tirava
  ~171.024,0 mm³ de aço que não existem para sair.
* Nunca compare meia peça: `maior(le("01_/MatrizJonatha.step"))` tem 2 sólidos; o "aço só na certa" deu
  405.459,2 mm³ por comparar uma metade contra o bloco inteiro. Compare peças inteiras alinhadas pela face de
  saída (Z = 109,00).
* `len(solido.Shells()) > 1` **é** cavidade selada, não ruído de importador. O remédio é bipartição em
  Y = 0, não corte.
* A fenda só aparece com 73,50 se você medir os planos; unindo os dois semicílios dá 75,00.
* Perfil da prancha é **radial**, não silhueta: hachurar de −r_ext a +r_ext apaga furos fora do eixo.
* `cadquery` 2.8: sem `.union` em `Solid`, sem `Shape.slice`/`Edge.discretize` (use `BRepAlgoAPI_Common` +
  `TopExp_Explorer` + `GCPnts_UniformDeflection(0,05)`); tolerância de planaridade 1e-9 descarta cara de
  booleano (use 1e-6); figura grande demais dá `MemoryError` em `canvas.draw()` — salve a figura inteira em
  dpi baixo.
* `.gitignore` **não des-rastreia**: depois de ignorar um arquivo já rastreado é preciso `git rm --cached`.
* Codemod de caminho só por nome literal é cego a `os.path.join(DIR, variavel)` — depois de mudar caminho,
  rode o portão inteiro.

## 8. Pendências abertas (com o que fecha cada uma)

0. **Peça única da v27.0 (2026-09-13, fim de tarde).** `07_CAD_Matrizes/Matriz_Jonatha_v27_Peca_Unica/` com
   `MatrizJonatha_v27_Peca_Unica.step` (1 sólido, 1 casca, 22 faces, BRepCheck limpo em 22 caras e 90 arestas),
   o JSON das medidas, o README da pasta e a montagem `06_/STEP/Cabecote_EX-030_com_Matriz_Jonatha_v27_Peca_Unica.step`.
   É **variante derivada** — o master v27.0 bipartido continua o SSOT (sha256 `7f26c5c5ba238a12…` conferido no
   fim da rodada). Números: canal idêntico (213.945,1 mm³), fenda no land idêntica (75,000 × 1,500 com R 0,75),
   boca de entrada Ø 75,60, +351,9 mm³ de aço onde havia bolha selada de pino, linha de partição zerada (a
   costura corria pelas duas bordas da manta: 372,8 mm de perímetro no plano Y = 0 e 759,5 mm² de contato
   metal-metal) e **0,00 % da superfície do canal em sombra** — usinável pelas duas faces, sem junta. Recria com
   `python3 04_Dados_SSOT_e_Scripts/gerar_matriz_v27_peca_unica.py`; relatório em `03_/MATRIZ_V27_PECA_UNICA.md`;
   a auditoria de correlações já a conhece (sétima peça do índice — e por causa dela a C1 passou a cobrar a
   fenda no land também de quem não tem `_Canal_Fluxo.step` na pasta, que antes dava falso "divergiu do SSOT").
0. **Rodada de 2026-09-13 (auditoria de correlações + montagens com flange + reologia do mastique).** O que
   entrou e o que ela achou:
   * `04_/auditar_step_correlacoes.py` → `03_/AUDITORIA_CORRELACOES_STEP.md` + JSON: **64 STEP** abertos e
     cruzados em sete correlações (C1 cota × SSOT, C2 metade × metade × peça, C3 arquivo do canal × vazio real,
     C4 matriz × cabeçote com folga radial e anel de fuga, C5 montagem × peças, C6 atalhos × baseline selado,
     C7 saúde topológica cara por cara). Está na rodada de estudos do portão (`--com-estudos`); sai com código
     0 como alerta e com `--rigoroso` vira bloqueio. Rodar: `python3 04_Dados_SSOT_e_Scripts/auditar_step_correlacoes.py --json --md`.
   * Seis montagens **cabeçote completo com flange + matriz sentada**, uma por matriz (`06_/STEP/Cabecote_EX-030_com_Matriz_*.step`:
     Copo, Gedeon entregue, Gedeon CERTA, Desenvolvimento, Jonatha v27, Jonatha v28.1), todas com ∩ = 0,0000 mm³.
   * `04_/masti_epdm_reologia.py` → `03_/REOLOGIA_MASTIC_EPDM.md`: reologia de literatura para o mastique
     resistivo de EPDM em **banda** (K 3×/8×/20× sobre o nosso K deslocado para 90 °C, n = 0,30), com os dois
     critérios numéricos que a simulação tem de responder (ΔP de matriz 2,1–9,4 MPa da linha análoga; τ_parede
     ≥ 0,14 MPa = raspado na saída) e as quatro fontes com URL.
   * **Achado 1 — defeito real na proposta v28.1:** `MatrizJonatha_v28_Body_B.step` tem uma cara PLANA
     degenerada (área ≈ 0) na transição do land com o chanfro, no plano de partição — centro medido
     [37,02; 0,56; 99,00]. Isso contamina `MatrizJonatha_v28.step` e a montagem `_com_Matriz_Jonatha_v28_1.step`
     (BRepCheck inválido = "arquivo corrompido" em muito CAD). Não é o `Body_A`, não é a v27, não é a Gedeon.
     Conserto: re-cortar o chanfro *antes* de partir em Y no `gerar_matriz_v28.py`, ou costurar a casca sem a
     cara nula; enquanto não for consertado, a v28.1 **não** vai para a fábrica com `--rigoroso` ligado.
   * **Achado 2 — o anel de fuga não é exclusivo da Gedeon:** medido na C4, o anel entre a OD da matriz e o
     furo do cabeçote tem folga 1,00/0,25/0,25 mm e está **contínuo do bico até a entrada em todas as seis
     matrizes**, área 428,4 mm² (Copo: 2.238,7 mm² porque ela é mais curta e sobra Ø75,60 no bolso). Ou seja:
     "voltar pelo funil" não é uma característica da Gedeon, é uma rota que existe para qualquer matriz — o que
     decide é a resistência hidráulica relativa das duas rotas, e é isso que a simulação 3D tem de medir.
   * **Achado 3 — a borda da saída, medida em seção:** Copo e Gedeon CERTA dão estádio 112,017 mm²
     (75,00 × 1,50 com R 0,75); v27 e v28.1 dão 346,654 mm² (o estádio já aberto pelo chanfro 1,5 × 45,
     boca 78,00 × 4,50); a `MatrizDesenvolvimento` histórica dá **351,0 mm² = retângulo puro, canto vivo** —
     sem arredondamento no canto, que é onde a serra nasce. As peças que ele usa hoje não têm canto vivo.
1. **Auditoria: o método atual está encerrado, não suspenso.** Decisão dele em 2026-09-13: *"não agora, mais
   depois iremos desenvolver novo método de auditoria"*. Então o rito velho (proposta → PR → veredito → re-selo
   de baseline, protocolo v1.0) **não será retomado**: fica como está, congelado, sem `--atualizar-hashes`, sem
   veredito na PR #3 e na PR #4, e sem editar `05_Interface_Auditoria/`. Enquanto o método novo não existir, a
   garantia de consistência é o portão (`verificar_cadeia.py`), que confere regras 1 e 2 por conteúdo e os pares
   documento × JSON. O que vale aproveitar do método velho, quando desenharmos o novo: o baseline com os 35
   sha256, a tabela de tolerâncias do protocolo (§4), os seis achados G-01..G-06 de
   `03_/AUDITORIA_GEOMETRICA_MATRIZ_JONATHA.md` (a moléstia real continua sendo G-03, cavidade selada nos dois
   `Body_A`), e `verify_geometry_ssot.py` / `verify_legacy_dies.py` como medidores — o que está morto é o
   ritual de aprovação, não a medição.
2. `03_/AUDITORIA_GEOMETRICA_MATRIZ_JONATHA.md` §6 ainda descreve a reconstrução refutada em parte do texto —
   os ponteiros foram atualizados, mas a seção não foi reescrita (zona de auditoria, congelada agora).
3. Os `arquivos[]` de `05_/propostas/PRP-0005-v28-1-fabricacao.json` apontam para
   `01_CAD_MatrizJonatha_Oficial/MatrizJonatha_v28*`, que **não tem atalho** (a v28.1 mora em
   `07_CAD_Matrizes/Matriz_Jonatha_v28_1_PROPOSTA/`). A proposta já foi auditada, então **não se edita**:
   quando a auditoria voltar nasce `PRP-0006` com os caminhos certos. Anotado aqui para não surpreender.
   A branch `proposta/PRP-0005` ficou na estrutura anterior (com o aninhamento `M01..M06`) **de propósito**:
   PR em revisão não se reescreve. Quem for olhar o diff da PR #3 veja os arquivos em
   `07_CAD_Matrizes/Matriz_Jonatha_v28_1_PROPOSTA/` na branch `continue`.
4. **Todas as PR estão fechadas** (ordem dele, 2026-09-13, repetida três vezes): a #4 (`arena/01a096e3-...`,
   PRP-0006 de outrem — land 10,00 mm com chanfro 0,80) foi fechada **sem mesclar** (`merged_at = null`) e com
   comentário de estado explicando que não houve veredito nem aprovação; #1, #2 e #3 já estavam fechadas
   (mescladas). Nada foi apagado: a branch da #4 continua no repo e `delete_branch_on_merge=false`, então
   `gh pr reopen 4` / `gh pr merge 4` resolve se ele mudar de ideia. O chanfro do master é 1,50 e assim fica
   até ele dizer o contrário — a decisão D2 não foi tocada por este fechamento.
5. Geometria do cabeçote que ainda depende de decisão dele: o chanfro que falta no desenho dele foi conferido
   no DXF (10 × 45° na face do flange) e a cabeça do parafuso M12 no furo de 16,5 — o cenário da furação M12
   foi removido do repo em setembro e **voltou rastreado** em 2026-09-13, com a rodada de "tire as travas":
   os 4 arquivos estão em `06_/STEP/estudos/` no git, e recria com
   `python3 04_Dados_SSOT_e_Scripts/gerar_cabecote_ex030.py --com-m12`.
6. **Caminho do equilíbrio de fluxo (aberto em 24/09 pela matrizaria, decisão dele).** Fecha com um "A" ou um
   "B" no `03_/CONTATO_MATRIZARIA_FERNANDO_2026-09-24.md` §5: **A** = pôr freio na matriz que está em uso hoje
   (caminho que ele chama de mais barato, e a foto do rebaixo nas costas que ele prometeu manda o exemplo);
   **B** = fabricar a v30 com canal de fluxo mesmo com ele declarando que não garante - e aí vale perguntar se
   ele orça junto o rebaixo de ajuste na face traseira, que é o "recurso" que ele diz ser impossível depois de
   cônico. Se a resposta for "refaça o desenho com o freio", isso é revisão nova (cota medida no STEP, SSOT,
   pacote, tag) - não se faz de ouvido.
7. **Enviar o DXF ao Fernando.** Ele pediu DXF/DWG em 24/09 10:01 e até hoje ninguém mandou (o Jonatha só
   respondeu "esses arquivos são .STEP"). Fecha anexando `MATRIZ_V30_DESENHO_COTADO_AC1015.dxf` (CAD velho) ou
   `MATRIZ_V30_DESENHO_COTADO.dxf` (AC1024) + o `_PREVIEW.pdf`, com o texto pronto no §7 do relatório de
   contato. Cuidado: **isso não entra no zip nem move a tag**; e o NDA continua pendente de assinatura mesmo
   com os STEP já no celular dele.

## 9. Como ler o histórico

```bash
git log --oneline -40                 # a linha do tempo das decisoes
git log --oneline -- 07_CAD_Matrizes    # o que mudou na organizacao das matrizes
git show --stat HEAD                     # a reorganizacao #2, com a justificativa no corpo
git log origem/main..HEAD --oneline      # o que ainda nao desceu para a main
```

Branches no GitHub (estado de 2026-09-13, depois do push completo): `main` **contém** `continue` e a tag
`estado-2026-09-13` — a `main` só tem à frente os merge commits da própria sessão, então quem clonar sem saber
de nada já cai em cima do trabalho inteiro (foi assim que testamos: `git clone` da `main` +
`python3 04_Dados_SSOT_e_Scripts/verificar_cadeia.py --rapido` em máquina limpa = **PORTA ABERTA**); `proposta/PRP-0005` continua na estrutura anterior (a v28.1 como foi submetida, para
não reescrever PR em revisão); `master` é o snapshot legado que ele manteve de reserva, intocado; e as duas
`arena/01a091ce-*` / `arena/01a096e3-*` são as pontas da cerimônia de auditoria velha, deixadas como estão.

Os scripts descartáveis que executaram a reorganização estão versionados em
`04_Dados_SSOT_e_Scripts/ferramentas_de_reorganizacao_2026-09-13/` (README na ordem + as duas lições que doem:
rodar o portão completo depois de mexer caminho, e `git rm --cached` depois de ignorar).

```bash
git log --oneline --graph -25 origem/main        # a linha do tempo que desceu para a main
git tag -l "estado-*"                            # os marcos empurrados
```

**Como a `main` foi atualizada em 2026-09-13:** por ordem direta dele (*"atualize o GitHub de forma completa,
você tem permissão total"*), o estado da sessão entrou na `main` num merge commit — **não** pelo rito de
proposta → veredito do protocolo v1.0. Isso não é aprovação de nada: `matriz_jonatha_master_files` no SSOT
continua apontando para `MatrizJonatha.step` (v27.0) e a v28.1 continua na pasta com `PROPOSTA` no nome. A
PR #3 passou a "merged" como efeito mecânico de a main conter os commits dela; o veredito nunca foi dado e não
será dado nesse formato (ver item 1 acima).

As duas PRs da cerimônia velha receberam comentário de estado na data: a **#3** (nossa, PRP-0005) foi fechada
pelo GitHub como "merged" por motivo mecânico — os commits dela entraram na `main` com o push do estado — e o
comentário diz que **isso não é veredito nem aprovação da v28.1**. A **#4** (PRP-0006 de outrem, land 10,00 com
chanfro 0,80) recebeu comentário apontando os três defeitos da régua como insumo do método novo e ficou aberta
até 2026-09-13, quando ele mandou fechar todas: fechada **sem mesclar** e **sem re-veredictar**, com um segundo
comentário ([pull/4#issuecomment-5654833275](https://github.com/ity1300-wq/MATRIZEXTRUSORA/pull/4#issuecomment-5654833275))
registrando o estado do projeto no momento do fechamento — master v27.0, v28.1 não promovida e com a cara
degenerada no `Body_B` a consertar antes de qualquer promoção, método v1.0 encerrado. Verificado pela API
depois do fechamento: `ABERTAS: nenhuma` (4 PR no total, todas `closed`).

**O repo é público.** Por isso as capturas dele (`uploads/`, prints de celular com o endereço da sessão e a
barra do aparelho) **não** foram para o GitHub: `03_Relatorios_e_Documentacao/FONTES_DO_USUARIO_2026-09-13.md`
guarda de cada uma o tamanho, o sha256 e o que rendeu — inclusive a que mostra a galeria dele aberta no meu
render, com o `k = 21,28 mm/un` da legenda (a escala que vale é a da folha inteira, 25,534, calibrada no
centro dos furos da junta). Se ele preferir as imagens no git, o passo é tornar o repo privado e subir as oito
conferindo os hashes. O token que passou no texto da conversa precisa ser revogado — dá escrita neste repo.

**Rascunhos da sessão versionados** (para a próxima IA não adivinhar como o croquis foi lido):
`04_Dados_SSOT_e_Scripts/rascunhos_da_sessao_2026-09-13/` (39 arquivos: leitura do DWG/DXF, vistas, faixas da
prancha, remendos de documento, com README por grupo e os erros que custaram tempo) e
`04_Dados_SSOT_e_Scripts/ferramentas_de_reorganizacao_2026-09-13/` (os 7 scripts do achatamento das pastas). A
rodada do portão que autorizou o push está transcrita em `03_Relatorios_e_Documentacao/PORTAO_ESTADO_2026-09-13.txt`.

No GitHub, além dos branches: **release** criada da tag `estado-2026-09-13` (para baixar o estado em .zip) e
descrição/tópicos do repositório apontando para este arquivo.

## 10. Recado para quem assumir

Não promova a v28.1 por conta própria, não toque em `02_/` a não ser para ler, não re-escave a Gedeon e não
recrie a "Gedeon corrigida". Se precisar escrever número em algum lugar, meça primeiro: o portão
(`verificar_cadeia.py`) compara texto de relatório contra JSON justamente para pegar número que apodreceu.
E se mudar um caminho, rode o portão completo antes de dizer que está pronto.

## 11. Revisões de 2026-09-22 (o estado atual, sem adivinhação)

O dono mudou as cotas de envelope e o material. O que está em disco agora, tudo medido nos STEP:

* **`07_/Matriz_Jonatha_v30_OFICIAL/` = a peça vigente** (`matriz_oficial` = v30.0 no SSOT): Ø94,00 / Ø89,00 /
  Ø79,00, comprimento **95,00 mm**, face de saída **faceada com o nariz do EX-030** (protrusão medida +0,00 mm;
  na v29 é +14,00 mm), interferência com o cabeçote 0,0000 mm³, folga radial 0,50 mm nos três estágios,
  1 sólido / 22 faces / BRep válido, aço 438.509,9 mm³ = 3,442 kg, canal 183.862,6 mm³.
* **`07_/Matriz_Jonatha_v29_OFICIAL/` = a v29 re-feita** com os mesmos Ø novos e comprimento 109,00 (a cota de
  comprimento não foi alterada nela), aço 477.050,9 mm³ = 3,745 kg, canal 213.945,1 mm³ (idêntico ao master).
* **Produto imutável nas duas**: land 8,500 mm (Z 85,00→93,50 na v30; 99,00→107,50 na v29), fenda
  75,00 × 1,500 entre caras com R 0,75, área 112,0171 mm², chanfro 1,50 × 45°, boca de entrada Ø75,60.
* **Tolerância ±0,5 em toda cota alterada** (os três Ø e, na v30, o comprimento), por ordem dele. As cotas do
  produto continuam apertadas (1,500 +0,010/−0,000 etc.) — o ±0,5 não se estendeu a elas.
* **Material: aço 1045** com indução (ou nitretação a plasma) na região da fenda/land. O 1.2344 50-52 HRC
  anterior está anotado como `material_anterior` no SSOT.
* **Pacotes**: `08_Pacote_Usinagem_v30/` (vigente para envio; zip `PACOTE_MATRIZ_V30_PARA_ENVIO.zip`, o sha está
  na capa `07_EMAIL_DE_PRIMEIRO_CONTATO.md`) e `08_Pacote_Usinagem_v29/` re-gerado com o STEP novo. Ordem
  respeitada em ambos: conteúdo → CHECKSUMS → zip → sha na capa (o zip e a capa nunca entram na lista; foi o zip
  ler a si mesmo que encheu o disco com 19 GB nesta sessão — `finaliza()` já exclui).
* **Simulação re-executada** com as folgas novas: v29 219,7 bar / 0,277 % escapando pelo anel; v30 203,6 bar /
  0,215 % (mesmo mastique, Q = 15.000 mm³/s, `04_/revisoes_2026_09_22_simulacao.json`).

Como re-gerar do zero (nesta ordem, é o que a sandbox perdida exige):

```bash
bash 04_Dados_SSOT_e_Scripts/restaurar_workspace.sh          # pip + symlinks + remoto
python3 04_Dados_SSOT_e_Scripts/gerar_revisoes_v29_v30.py    # STEP v29 re-feita, v30, montagens, JSON
python3 04_Dados_SSOT_e_Scripts/gerar_pacote_usinagem_v30.py # os dois pacotes (docs + prancha + zip + capa)
python3 04_Dados_SSOT_e_Scripts/aplicar_revisoes_2026_09_22.py # READMEs, SSOT, relatorios, simulacao
python3 04_Dados_SSOT_e_Scripts/verificar_cadeia.py --portao
```

Pendências que ficam explícitas: (a) o **portão de CFD 3D do funil** continua adiado por ele; (b) o
`01_/` não ganhou atalho para a v30 (symlink novo não sobrevive à recriação da sandbox e o script de
restauração teria de ser ampliado — o SSOT e o índice de `07_/` apontam para o arquivo real); (c) o PAT em
`/home/user/tmp/.gh` continua exposto e a revogação é dele.

**Rodada 2026-09-23 — o que foi publicado e o que ainda é decisão dele.**

* **Os rótulos do desenho eram fonte de erro tanto quanto a tabela.** `prancha()` carregava `Ø93,00`,
  `Ø89,50 → anel 0,25`, `109,00`, `50-52 HRC`, `1.2344` e o título "v29.0" como strings fixas: o modelo já era
  o novo e a folha discordava dele. Agora todo rótulo sai do `pacote_usinagem.json` medido (`TOL_D1`/`TOL_D`/
  `TOL_L`, `FURO = [95, 90, 80]`, folga do anel calculada, aço e dureza por revisão), as anotações do corte são
  posicionadas por `z_out` — com a peça de 95 mm elas caíam em cima do título — e o bloco de notas é **medido
  contra a altura real do painel**: com 32 linhas a 5,75 pt ele escorria por cima do rodapé e a prancha saía
  assim mesmo; hoje o gerador para com `FALHOU`.
* **`gerar_pacote_usinagem_v29.py` se recusa a rodar sozinho** (`--eu-sei` força). A documentação daquele módulo
  ainda descreve 1.2344 e 93,00; um rodar por cima traria os dois de volta para o pacote v29. Os dois pacotes
  nascem de `gerar_pacote_usinagem_v30.py`.
* **Numeração:** `_bra()` dos dois scripts estava comendo separador de milhar — a área de junta saía
  `1,513,1 mm²`. Agora número já escrito no padrão brasileiro com milhar é protegido antes da conversão
  (inclusive `Q = 15.000 mm³/s`), inteiros de 5+ dígitos são agrupados, e `1.2344`, `EN 10204 3.1`, rótulos de
  revisão seguem intactos. Não reescrevi os relatórios fechados de `03_` por causa de formatação — a auditoria
  v1.0 está encerrada.
* **O pior caso do ±0,5 foi medido** (`04_/revisoes_2026_09_22_folgas_limites.json`): os Ø não travam a
  montagem (Ø94,00 +0,5 = 94,50 num furo Ø95,00 ⇒ folga radial 0,25 mm), mas a fuga pelo anel vai de
  0,273 % / 0,212 % no nominal para **2,323 % / 1,810 %** com folga 0,75 (8,5×, porque a fuga escala com o cubo
  da folga); ΔP mal se move. Eu tinha escrito "encosta com folga 0,00" — estava errado, o texto corrigido está
  no relatório da v27.
* Estado publicado: `continue` `e823bc4`, `main` `1b5322b` (árvore idêntica, `git diff continue main` vazio),
  tag `v30.0-oficial-pacote-usinagem`, releases v30/v29 com os **quatro anexos** re-trocados e re-baixados
  idênticos ao disco — v30 zip `588.274 B` sha `d4948ebeb2f97bb4…`, v29 zip `584.850 B` sha `143ff628d9a8897f…`,
  PDFs `49.582 B` / `49.287 B`. Dentro do zip, `sha256sum -c CHECKSUMS_SHA256.txt` = 13 OK.
* **Duas decisões continuam abertas** (nenhuma muda o que está publicado hoje): o comprimento da v30 como
  **95,00 −0,50/+0,00** em vez de ±0,5 (com +0,5 a face passa 0,5 mm para fora do nariz) e
  **indução 55-60 HRC × nitretação a plasma 600-700 HV0,2** na fenda.

## 12. Regra de publicação — "sempre atualize o GitHub" (ordem dele, 2026-09-23)

Nada de trabalho termina no sandbox. **Toda rodada que mexe em arquivo acaba com o estado publicado**, nesta ordem:

```bash
python3 04_Dados_SSOT_e_Scripts/verificar_cadeia.py --rapido      # o portao abre a porta; se nao abrir, nao publica
git add -A -- <pastas tocadas>                                     # NUNCA `git add -A` solto: com sandbox
                                                                  # recriada ele comeria os atalhos de 01_/ e 02_/
git commit -F - <<'MSG'                                            # corpo explica o que estava errado e por que
...
MSG
git push "$URL" continue:continue
git checkout main && git merge --no-ff continue -m "main <- continue: ..." && git push "$URL" main:main
git tag -f -a v30.0-oficial-pacote-usinagem -m "..." && git push -f "$URL" refs/tags/v30.0-oficial-pacote-usinagem
```

Se a rodada trocou o **conteúdo de um pacote**, o push não basta: os anexos das releases são parte do estado.
DELETE no asset antigo + POST em `uploads.github.com/repos/ity1300-wq/MATRIZEXTRUSORA/releases/<rid>/assets?name=`
(`rid` **394977467** = v30, **391700106** = v29), depois `curl -sSL` do
`.../releases/download/<tag>/<nome>` e `sha256sum` do disco — tem de sair **idêntico byte a byte**, e o corpo da
release cita o tamanho/sha do zip vigente. A capa `07_EMAIL_DE_PRIMEIRO_CONTATO.md` fora do zip também cita o sha
do zip: qualquer re-geração de pacote muda os dois, e o `aplicar_revisoes_2026_09_22.py` propaga o valor para o
SSOT e para os READMEs das pastas oficiais (rodar o gerador de pacotes **sem** rodar o aplicar deixa o SSOT
atrasado — o portão pega, mas só depois de você ter publicado coisa errada).

A tag `v30.0-oficial-pacote-usinagem` fica no commit cuja árvore gerou os assets publicados; mudança só de texto
(este arquivo, relatórios) sobe nas branches e **não** move a tag. O token é repo-local (`/home/user/tmp/.gh`);
sem ele — sandbox recriada — `bash 04_Dados_SSOT_e_Scripts/restaurar_workspace.sh` refaz remoto e atalhos, e não
se faz `git config` global.

Por que a regra existe, em uma frase: em 2026-09-23 eu deixei três rodadas só no disco (a tabela dos Ø, os
rótulos do desenho, a numeração com milhar) e cada uma depois custou uma troca nova de assets; enquanto a troca
não acontecia, o GitHub servia documento velho com sha novo na capa — exatamente o par que a fábrica confere.

**Linhas de 2026-09-25 — o histórico da conversa virou arquivo próprio, por ordem dele** (*"faça um arquivo leve
que contenha toda nossa conversa histórico e seja atualizado a cada interação; este deve ser sempre atualizado no
GitHub"*). O arquivo é **`HISTORICO_DA_CONVERSA.md`**, na raiz: linha do tempo com **uma entrada por rodada**
(o que ele pediu, o que saiu, o sha), escrita no fim da seção do dia, sem reescrever entrada antiga — correção de
rodada passada entra como linha nova dizendo "corrigindo a rodada X". É `.md` solto, **fora** do zip dos pacotes:
atualizá-lo sobe nas branches mas **não** move a tag nem re-publica asset, pela mesma regra acima. Quem assumir
não troca o documento gordo pelo leve: o `CONTINUIDADE.md` continua sendo o estado do projeto; o histórico é só a
linha do tempo.


**Rodada 2026-09-23 (tarde) — a folha de uma página virou "meia-seção + detalhe", e o funil apareceu.**

* ordem dele: *"retire essa bagunça de informações e deixe somente o que é de suma importância, também
  represente a matriz melhor, em momento nenhum aparece o 'cone' interno dela"*. A folha anterior
  (perfil externo com três balões numerados + duas colunas de regras) foi jogada fora e `desenhar_folha_de_cotas_v30.py`
  reescrito com quatro blocos: **meia-seção no plano da abertura** (corte em X-Z que passa pela fenda — é a única
  vista onde o funil/cone interno aparece, porque a parede dele fecha de Ø75,60 em Z 0,00 até a abertura
  1,500 no início do land), **DETALHE A ≈ 4× do fim do canal** com `ABERTURA DA FENDA 1,500 mm +0,010/−0,000`
  em corpo grande (a cota que ele disse não estar clara), **face de saída** com largura/abertura e área do land,
  e **regras em quatro colunas** (aço/dureza, ordem, proibido, aceitação). Os balões numerados, o quadro de notas
  e a lista de tolerâncias genéricas saíram.
* o funil é desenhado como a **reta entre as seções medidas** (entrada Ø75,60 em Z 0,00, boca do chanfro
  78,00 × 4,50 em Z 94,99) e a folha diz isso: a parede real é a superfície BSpline do STEP. Não fui medir o
  perfil fatia a fatia de novo — `cadquery` não está instalado nesta sandbox (só `matplotlib`), e a folha é
  justamente o documento que não deve ter número sem medição.
* a folha e o e-mail curto continuam **fora do zip** ⇒ `CHECKSUMS_SHA256.txt` (13 arquivos) e o sha do
  `PACOTE_MATRIZ_V30_PARA_ENVIO.zip` não mudaram, a tag `v30.0-oficial-pacote-usinagem` **não se moveu** e os
  anexos publicados continuam batendo com o disco (§12) - cada release tem DOIS anexos: a `394977467` (v30)
  traz o zip de 588.274 B `0738c468…` e a prancha de 49.582 B `4b0e6ef1…`; a `391700106` (v29) traz o zip de
  584.850 B `d6966b14…` e a prancha de 49.287 B `a8f7a50a…`. Quatro anexos no total, todos conferidos no disco.
  Rodar o `gerar_pacote_usinagem_v30.py`
  para "atualizar a folha" seria o caminho errado: ela não faz parte do pacote.
* guardas do gerador que já pegaram bug real nesta rodada: `quebra()` + contagem de linhas por coluna com
  `SystemExit` se as regras descerem demais, fator de ampliado do DETALHE A **calculado** das caixas (não
  escrito à mão), e os rótulos saem todos de `pacote_usinagem.json` com vírgula decimal (`br()`), inclusive os
  de `Ø` — a string digitada no heredoc perde o `Ø`, o que já tinha virado dois espaços no desenho.

**Rodada 2026-09-23 (noite) — a folha não pode perder sinal quando alguém copia o texto do PDF.**

* `matplotlib` + DejaVu Sans desenha e imprime `−` (U+2212), `–` (U+2013), `—` (U+2014), `→`, `≥`, `≤` e `≈`,
  mas **esses sete caracteres não vão para o ToUnicode do PDF**: `extract_text()` devolve o resto e come o
  sinal. Na folha isso era perigoso de verdade: "+0,010 / −0,000" copiava como "+0,010 / 0,000" e
  "30–36 HRC" copiava como "3036 HRC". O `desenhar_folha_de_cotas_v30.py` agora só usa os que sobrevivem
  (`± × ° Ø µ ² · »` e o hífen ASCII) e escreve faixas com "a" ("0,6 a 1,0 mm"), comparação com ">=" e "<="
  e seta de sequência com "»". A checagem é automática: 29 strings (todas as cotas e sinais) são procuradas no
  texto extraído dos dois PDFs, e o teste falha se sobrar qualquer caractere U+2000–U+206F no texto extraído.
* **A prancha grande dentro do zip tem o mesmo problema tipográfico** (ela usa `→` e `≤` à vontade, gerados
  antes dessa descoberta). Não fui trocar: mexer na prancha muda o `pacote_usinagem.json`-filho → o zip → o sha
  → a tag e os quatro anexos (dois por release). Como a folha é o papel que vai no e-mail, corrigi só ela; se um dia o pacote for
  re-gerado por outro motivo, vale a mesma sanitização no `prancha()`.
* segundo erro que a checagem pegou: a coluna ACEITAÇÃO dizia "protrusão 0,00 no nariz do EX-031" escrito à mão.
  Isso é verdade na v30 e **falso na v29**, onde a face de saída sai 14,00 mm além do nariz. Agora o valor vem
  de `montagem["saida_além_da_face_do_nariz_mm"]` medido no STEP da montagem, e o gerador para com
  `SystemExit` se a chave faltar em vez de chutar zero.

**Rodada 2026-09-23 (madrugada) — o MATERIAL ganhou faixa própria no topo da folha.**

* ordem dele: *"faltou somente enfatizar com qual material se deverá ser fabricado"*. A folha agora abre com
  uma **faixa vermelha de página inteira** (`fig.text` na figura, não dentro de um eixo): rótulo "MATERIAL DA
  PEÇA - é cota de aceite, não é sugestão", o nome do aço em 20 pt (`decisoes_2026_09_22/material`), a norma
  partida do `aco/norma` no dois-pontos (padrão de um lado, "barra forjada, fibra no eixo, normalizada <= 220 HB"
  do outro), `DUREZA E TRATAMENTO NA FENDA` com o `aco/dureza` integral, e `O QUE NÃO PODE MUDAR` com o
  `aco/grupo` (que é o texto que diz que o 1045 substituiu o 1.2344 da proposta) + o certificado EN 10204 3.1.
  Nenhuma dessas frases foi redigitada: vêm todas do `pacote_usinagem.json`, e se faltar alguma chave o gerador
  para com `SystemExit("o pacote nao traz o material nestas chaves...")` em vez de escrever aço na mão.
* conseqüência no resto da folha: as regras caíram de quatro colunas para **três** (aço/dureza saiu de lá, pois
  agora está na faixa), e a coluna que sobrava foi usada para o "sem outro aço, sem outro revestimento" do
  PROIBIDO. As larguras de quebra (49/47 na faixa, 60 nas regras) e a altura da faixa são checadas por
  contador de linhas com `raise SystemExit` - foi assim que três estouro de texto foram pegos antes de sair PDF.
* o `tx()` deixou de ser convenção: ele está instalado em `matplotlib.text.Text.set_text`, então **todo** texto
  desenhado passa por ele - inclusive o que vem do JSON (`<= 220 HB`, `→`, `±`, `≥`). Se algum glifo acima de
  U+00FF sobreviver à substituição, a folha não sai. Checagem final na rodada: 32 strings (material + todas as
  cotas) presentes no `extract_text()` dos dois PDFs e zero caractere U+2000..U+2FFF no texto extraído.

**Rodada 2026-09-24 — saiu o primeiro DXF cotado da matriz (antes não existia nenhum `.dxf` no repo).**

* ordem dele: *"quero um desenho dxf com as cotas, sem poluição visual, sem excesso de informações, enfatize o
  material que deverá ser feito aço 1045"*. O `find` confirmou que o repo nunca teve DXF de matriz - a única
  referência era a linha `pacote_cabecote: desenhado DXF medido`. Então foi gerador novo:
  `04_Dados_SSOT_e_Scripts/gerar_desenho_cotado_dxf_v30.py` (ezdxf 1.4.4, já listado em
  `04_/restaurar_workspace.sh`), escrevendo `08_Pacote_Usinagem_v30/MATRIZ_V30_DESENHO_COTADO.dxf` e o
  `MATRIZ_V30_DESENHO_COTADO_PREVIEW.png/.pdf` para quem quiser ver sem abrir CAD. A v29 tem o desenho dela
  (`PACOTE=08_Pacote_Usinagem_v29 DXF=MATRIZ_V29_DESENHO_COTADO`).
* folha **A3 paisagem, 1:1, unidades mm** (`$INSUNITS=4`, `$MEASUREMENT=1`), sete camadas
  (PERFIL 0,50 mm / CANAL / EIXO CENTER2 / COTAS / MATERIAL / NOTAS / CARIMBO) e um dimstyle próprio `COTAS`.
  Conteúdo: **uma** seção simétrica no plano da abertura (a vista onde o funil aparece), a face de saída com a
  fenda, **8 cotas no total** (Ø94, Ø89, Ø79, boca de entrada Ø75,60, comprimento, land, abertura 1,500 e
  largura 75,00), 4 notas de processo e um carimbo. A abertura da fenda é a única cota em corpo grande (5,5 mm)
  e vermelha; a faixa de MATERIAL ocupa a linha de topo com 8 mm de altura de letra e `MATERIAL / AÇO 1045`
  repetido no carimbo. Nenhuma tabela de estágios, nenhum balão, nenhum CFD - o resto está no README do pacote.
* as 8 cotas são `DIMENSION` lineares **de verdade** (`add_linear_dim(...).render()`), com o texto da cota
  passado por override literal em padrão brasileiro: `text="Ø94,00 ±0,5"`. Geometria nominal exata + texto
  literal => o que a máquina medir no arquivo bate com o que está escrito. A folha confere isso no fim: reabre
  o DXF, lê `dxf.text` das 8 DIMENSION e dá `SystemExit` se alguma não estiver lá. `audit()` fecha em
  **0 erros, 0 correções** nas duas revisões.
* regra do PDF vale para o DXF também: **só Latin-1**. O `tx()` do gerador substitui `− – — → ≥ ≤ ≈ µ` e dá
  `SystemExit` em qualquer caractere acima de U+00FF; a checagem final imprime "glifos acima de Latin-1:
  nenhum". Consequência prática avisada no rodapé da própria folha e no e-mail: o `Ø` (U+00D8) é Latin-1 e vai
  como caractere mesmo, então em fonte SHX que não o tenha ele some na tela - troca-se a fonte do texto por
  Arial no CAD.
* guardas que já pegaram erro real nesta rodada, do mesmo tipo das da folha A4: (1) estimativa de largura de
  texto (`len(t) * altura * 0,68`) contra a coluna/caixa que recebe, e contagem de linhas de MTEXT com
  `SystemExit` - pegou 5 estouros (faixa de material, duas legendas de vista e o cabeçalho do carimbo) antes
  de qualquer arquivo ser gravado; (2) extensão do conteúdo conferida contra a moldura, com o comprimento dos
  TEXTOS estimado, para nada sair do papel; (3) `if not v` na checagem de chaves do JSON quase matou a v30: a
  protrusão da v30 **é** 0,00 mm, valor válido - a guarda passou a ser `v is None or v == ""`.
* três armadilhas do ezdxf 1.4.4 que quebraram o primeiro rascunho, anotadas para a próxima vez que alguém
  mexer aqui: `add_linear_dim(...).render()` **exige** um dimstyle real (com o `Standard` cru o wrapper
  explode em `AttributeError: 'DimStyleOverride' object has no attribute 'dxf'`); `render()` devolve o
  `LinearDimension` **sem** `.dxf`, então a camada se põe em `ent.dimension.dxf.layer` antes de renderizar; e
  `dimtsel`, `dimadex`, `dimahex`, `dimtht` não são atributos de DIMSTYLE - o gerador tenta um a um, engole o
  `DXFAttributeError` e avisa quais caíram, em vez de assumir que existem.
* o DXF e os previews ficam **fora do `PACOTE_MATRIZ_V30_PARA_ENVIO.zip`**, como a folha (a lista de arquivos
  do zip é explícita no `gerar_pacote_usinagem_v30.py`, não é glob do diretório, então rodar o gerador de
  pacote não puxa o DXF para dentro). Consequência: `CHECKSUMS_SHA256.txt` continua com 13 arquivos, o sha do
  zip é `0738c468…`, a tag `v30.0-oficial-pacote-usinagem` **não se move** e os dois anexos da release
  `394977467` seguem idênticos ao disco - como os dois da v29 (`d6966b14…` + `a8f7a50a…`). São DOIS anexos por
  release; "quatro" é o total das duas releases, não de uma. Se um dia ele quiser o DXF dentro do pacote para envio, isso é
  publicação inteira: adicionar ao `nomes` do gerador de pacote, re-gerar CHECKSUMS/zip/capa, mover a tag e
  re-trocar os quatro assets com `/home/user/tmp/trocar_assets.py`.

**Rodada 2026-09-24 (tarde) — o DXF virou folha de ANATOMIA: menos receita de fábrica, mais peça.**

* ordem dele, sobre a primeira versão da folha: *"tem muita informação, deixe mais objetivo, coloque mais
  informações sobre a anatomia da peça detalhes, do que de como deve ser fabricado"* (ele anexou print das
  4 notas de processo e da faixa de material). Então a folha foi reescrita: as 4 notas viraram **uma** linha
  de FABRICAÇÃO no rodapé da tabela, a faixa de material caiu de 4 linhas para **1 linha grande
  (`MATERIAL: AÇO 1045 · SEM PVD · SEM DLC · SEM OUTRO AÇO`) + 1 parágrafo curto** (norma, dureza, "troca de
  aço só com desenho novo assinado"), e entrou **uma tabela de anatomia de 13 linhas** com três colunas -
  região / cota de contrato / medido no STEP - mais o **DETALHE A 6:1** do fim do canal (o `1,500` em corpo
  grande ali, não repetido em três lugares) e a **face de saída 1:1 desenhada com os raios de verdade**
  (`stadium`: duas retas + dois semicírculos com `bulge = 1`), fenda 75,00 × 1,500 com R 0,75 e boca do
  chanfro 78,00 × 4,50. Continua com as mesmas 8 `DIMENSION`, A3, 1:1, mm.
* a coluna "cota" não é redigitada: ela vem das entradas de `pacote_usinagem.json["cotas"]`, achadas por
  trecho do `item` (`cota("land paralelo")`, `cota("Raio no fundo")`, ...), usando `nominal` + a
  `tolerancia` partida no ";" e no "/". Isso trouxe para a folha cotas que o desenho anterior não tinha e
  que ninguém tinha escrito à mão: posição dos degraus 69,90 / 80,70 ±0,05, coaxialidade Ø0,02 total,
  R 3,0 ±0,5 na junção funil-fenda "sem aresta viva", planicidade 0,01 da face de entrada. `cota()` dá
  `SystemExit` se o pacote não tiver aquele item - não inventa.
* a coluna "medido no STEP" é o que a medição achou, inclusive onde ela **não** confere com a leitura fácil:
  `fenda - largura` mostra 74,9995 contra 75,00, `boca do chanfro` 77,9986 contra 78,00, e a boca de entrada
  é reportada como "75,6000 (corte em x = 0,01)" em vez do `abertura_mm` do JSON (75,5934) - aquele número é
  a corda da seção deslocada 0,01 mm do plano, não o diâmetro, e escrito sem explicação viraria disputa com a
  fábrica. Linhas sem medição própria levam "-" e há uma nota dizendo que "-" é cota de projeto.
* duas travas novas no gerador, das que valem o trabalho: (1) **nenhuma etiqueta pode tocar a outra** - o
  script reabre o DXF, estima a caixa de cada TEXT/MTEXT e dá `SystemExit` se duas caixas se cortarem em mais
  de 0,8 mm nos dois eixos (a folha fecha com **0 sobreposições**); (2) se qualquer checagem reprovar, o
  `.dxf` e os previews **recém-escritos são apagados**, para não deixar artefato reprovado dentro da pasta do
  pacote - testado injetando texto de 9,6 mm de propósito: saiu "folha reprovada (nada publicado)" e a pasta
  ficou limpa.
* erros que essas travas e a de largura pegaram nesta rodada, todos reais: `…` (U+2026) no "sha256 ...", que
  não é Latin-1 e parou a folha; `tf.split(",")` no texto "R 3,0 ±0,5, sem aresta viva" cortando a **vírgula
  decimal** e escrevendo "R 3" na tabela (agora divide por ", sem "); a tolerância do chanfro já começava com
  o valor, então "1,50 × 45°" saía como "1,50 1,50 × 45°"; a linha de 7,5 mm do MATERIAL com a frase inteira
  media 510 mm numa folha de 400 mm; e o valor da última linha do carimbo estava ancorado no topo errado e
  caiu em cima da linha anterior.
* nada mudou de publicação: `MATRIZ_V*_DESENHO_COTADO.dxf` + `_PREVIEW.png`/`_PREVIEW.pdf` continuam **fora**
  do `PACOTE_MATRIZ_V30_PARA_ENVIO.zip` (lista explícita de arquivos, não glob), então CHECKSUMS segue com 13
  arquivos, o zip `0738c468…` não se moveu, a tag `v30.0-oficial-pacote-usinagem` está em `80167f2` e os dois
  anexos de cada release (quatro no total) batem com o disco - conferido via API `releases` no fim da rodada.

**Rodada 2026-09-25 — a conversa com a matrizaria lida, registrada, e o DXF ganhou gêmeo AC1015.**

* veio o PDF `TRANSCRICAO-matrizaria-COM-IMAGENS.pdf` (13 pág., 58 mensagens, 22.687 caracteres extraídos com
  `pypdf` e lidos por inteiro). Registrado em `03_/CONTATO_MATRIZARIA_FERNANDO_2026-09-24.md`, que separa o que
  é **fato de chat** (texto literal) do que é **áudio transcrito por whisper** e do que é **legenda de IA sobre
  foto** - o próprio documento avisa que as descrições de imagem não são medição, e de fato uma delas diz
  "JONATHA V2.0" no nosso desenho: **não existe v2.0**, é má leitura do `v27.0` (conferido nos geradores).
* o que a fábrica disse, em uma linha cada: **não abriu os STEP no celular** e pediu DWG/DXF; a matriz dele fez
  a que está em uso e o defeito é **desequilíbrio de fluxo** (pressão no centro, compactação de menos nas
  pontas); "o projeto de vocês não vai resolver"; "a matriz nunca dá para garantir, porque não é o molde";
  "se não der certo não tem recurso, não tem como pôr um freio porque está cônico"; e a alternativa mais barata
  dele: **freio na matriz atual**, depois peça nova certificada. Os 4 recursos (rebaixo nas costas, cantoneira,
  "bolacha" de disco, perfil "sorriso") estão descritos no §3 do relatório com a implicação de cada um.
* conferido antes de escrever qualquer coisa: os três `.STEP` que ele recebeu **são os do pacote publicado**
  (mesmos nomes, 97.198 / 85.455 / 151.083 bytes, shas da tabela do e-mail curto) e **são ASCII**
  `ISO-10303-21` - 0 byte não-ASCII, `head -c 22` = `ISO-10303-21;\nHEADER;`. Ou seja: "fonte binária" foi o
  visualizador do telefone. Isso estava escrito no e-mail como "Se eles preferirem CAD a PDF"; agora o pedido é
  explícito, e o bloco do e-mail foi reescrito com os dois DXF e a frase para ele.
* **`DXF_SERIE=R2000` no gerador do desenho** produz o gêmeo da mesma folha em AutoCAD 2000 (`AC1015`), para
  CAD de oficina: `08_/MATRIZ_V30_DESENHO_COTADO_AC1015.dxf` (67.519 B) e o da v29 (67.533 B), sem preview
  próprio (a folha é idêntica; o `_PREVIEW.*` da série principal serve). A trava que fiz para isso: o primeiro
  gêmeo saiu **reprovado** porque em AC1015 o ezdxf escapa todo acento (`\U+00D8`) e a cota lida no round-trip
  deixava de bater com o JSON - 1 de 8 conferidas. Correção no `novo_doc()`: `$DWGCODEPAGE = ANSI_1252` +
  `doc.saveas(..., encoding="cp1252")`, que escreve `Ø` (0xD8) e `±` (0xB1) como byte simples, do jeito que CAD
  velho espera. Depois: `audit()` 0 erros, **8/8 cotas conferidas**, 0 etiquetas sobrepostas, e verificado no
  binário que não sobrou `\U+` nenhum.
* nada de publicação se moveu, e foi decisão consciente: o `.dxf`/previews ficam **fora** do
  `PACOTE_MATRIZ_V30_PARA_ENVIO.zip`, então CHECKSUMS segue em 13 arquivos, o zip `0738c468…`/`d6966b14…` não
  mudou, a tag `v30.0-oficial-pacote-usinagem` continua em `80167f2` e os dois anexos de cada release batem com
  o disco. Detalhe que a régua de 12 bytes me obrigou a ver: **regenerar o DXF muda o arquivo mesmo sem mudar a
  folha** (o cabeçalho do ezdxf grava `$TDCREATE` com hora, e o `_PREVIEW.pdf` do matplotlib carrega metadados),
  então o `.dxf`/PDF publicados foram **revertidos ao que está no git** em vez de commitados de novo por
  churn - só entraram os dois AC1015 novos, o gerador e os documentos.
* armadilha de ambiente que repetiu: `ezdxf`/`pypdf` **não sobrevivem ao snapshot** (`pip install --quiet
  ezdxf pypdf` de novo no começo da rodada) e os **symlinks das pastas de CAD somem** (`git checkout HEAD --
  01_CAD_MatrizJonatha_Oficial 02_CAD_Modelos_Historicos` antes de rodar o portão, senão ele morre em
  `FileNotFoundError` no STEP).

**Rodada 2026-09-25 (2ª) — as fotos dentro do PDF do contato, extraídas e lidas.**

* ele reenviou a conversa sem responder à pergunta do caminho A/B, então em vez de mexer em cota eu abri o que
  faltava: `pypdf` extraiu as **13 imagens embutidas** do `TRANSCRICAO-matrizaria-COM-IMAGENS.pdf` (resolução
  real, até 1500 × 1500 px) e eu vi as cinco que importam. Registrado no §3b do relatório de contato, com o aviso
  de que **foto com perspectiva não dá cota** e de que nada disso entrou em JSON/tabela/desenho.
* o que elas decidem, em uma linha cada: o recurso 1 dele **não são duas cavidades nas pontas**, é um **rebaixo
  retangular raso, de cantos arredondados, corrido atrás da fenda** na matriz velha (IMG-11) - e a matriz velha é
  um disco **plano, sem degrau/chanfro/land**, oxidada; na face de saída os dois furos redondos simétricos são da
  ferramenta de virar a matriz (IMG-10); montada, ela fica **afundada num copo com assento cônico** (IMG-08), que
  é outro arranjo - a nossa v30 sai rasante ao nariz; e a amostra com defeito tem **denteado idêntico nas duas
  bordas** (IMG-06).
* ~~**a descoberta que pode poupar dinheiro**: o serrilhado viria do **disco de corte** da linha, não da matriz~~
  — **CONCLUSÃO RETIRADA na 4ª rodada desta data, era minha e estava errada.** O que eu vi nos dois quadros
  embutidos no PDF (lâmina encostada numa tira **branca**, com a borda esfiapada no ponto de contato) existe nos
  quadros; o que **não** existe é a inferência de que aquilo é a linha da manta. Não é: os quadros são de outra
  mídia e o material ali nem é cinza-chumbo como a amostra. Fica anotado o erro porque ele é o exemplo do que
  **não** se faz neste repo: concluir causa a partir de imagem reduzida e descrita por IA.
* publicação: só documento (relatório de contato + este bloco). **Zero arquivo de pacote, zero DXF, zero zip**,
  então CHECKSUMS, os dois zips e a tag `v30.0-oficial-pacote-usinagem` (`80167f2`) não se movem; `verificar_cadeia.py --rapido` rodou antes do push.

**Rodada 2026-09-25 (3ª) - "és a origem do projeto, avalia": a v30 resolve o serrilhado? Não, e agora está escrito.**

* pergunta dele: a v30 veio da bipartida (peça única, resto igual), eu pedi sugestão de matriz para o problema da
  manta, e o Fernando acha que não resolve — **avalia**. A avaliação está em `03_/AVALIACAO_V30_X_FLUXO_2026-09-25.md`
  **usando só o que o repo já media**, e o veredito é: **ele está certo no essencial** — nenhum elemento da v30
  redistribui vazão na largura (funil cônico + land de largura constante não são coletor), e o único mecanismo que
  faria isso — asas com altura decrescente do centro para as pontas — já estava diagnosticado no D3
  (`ESTUDO_FUNIL_COATHANGER.md`) com o preço medido de **+141% de ΔP**.
* números que rodei nesta rodada (não copiei de memória): `python3 04_/avaliacao_matriz3_uniformidade.py` dá no
  land **uniformidade q_min/q_max = 52,3%**, núcleo com **92,3% da vazão dentro de ±5%**, últimos 1,00 mm de cada
  lado levando **0,63%** da vazão com q = **23,2% do núcleo**, e **τ parede 160,9 kPa** contra o limiar de rasgo de
  borda que o projeto adota (**0,14 MPa**, `masti_epdm_reologia.py`). É o canto R 0,75 esfaimando, que é o que ele
  descreve como "falta de compactação nas extremidades" — e o modelo é **2D por seção**, que pressupõe pressão
  igual na largura e portanto **é cego** ao efeito de coletor: nem defende nem acusa a v30. Fechado por CFD 3D,
  que ele adiou.
* uma conta que a conversa não tocou, **e o limite dela**: τ na parede do land não depende da forma do funil nem
  do comprimento do land, e sim da **vazão por mm de largura** e da folga. Isso valia para a minha frase "nenhuma
  matriz derruba o rasgo de borda" — mas o q por mm **é** justamente o que o freio/alívio redistribui, então a
  frase estava errada por excesso: **o desequilíbrio é conserto de matriz sim**. Corrigido no §5 do relatório de
  avaliação. (A "assinatura de corte" que eu usava como segunda perna deste argumento caiu junto — ver acima.)
* **débito meu, registrado no §8 do relatório:** `03_/PLANO_DE_VALIDACAO_E_SIMULACAO.md` dizia "*prova
  matematicamente* ... sem o efeito serrilhado (*sharkskin*)" e "*NÃO ocorrerão os rasgos de borda*" sem nenhum
  resultado atrás (o critério de <2% centro×bordas nunca foi medido; os ΔP daquele documento já estavam marcados
  como não reproduzíveis em P6 da triagem) e ainda chamando rasgo de borda de *sharkskin*. **Não reescrevi o
  plano**: inseri uma **nota de correção datada** depois do título, com o texto original intacto abaixo — apagar o
  erro é pior do que exibi-lo. Se algum dia alguém citar "a matriz elimina o serrilhado", o documento que desmonta
  a frase é o `AVALIACAO_V30_X_FLUXO_2026-09-25.md`.
* o que a v30 continua entregando, e não é pouco (medido): junta de partição zerada (372,8 mm de costura e
  759,5 mm² de contato metal-metal a menos), 0,00% do canal em sombra, face rasante ao nariz e ΔP 8% menor que a
  v29 (203,6 × 219,7 bar com o anel de fuga medido). É matriz **limpa e reprodutível**, não matriz **equilibrada**.
* recomendação executável, do mais barato: (0) régua no período das cristas + vídeo do corte; (1) **freio na matriz
  atual** (oferta dele) como *experimento que compra informação*, não como solução; (2) se melhorar, rev. 31 = v30 +
  **janela de alívio na face traseira** (o “recurso de bancada” que ele diz ser impossível num corpo cônico); (3)
  pedir a cotação da v30 já com a ressalva escrita de que ela não promete equilíbrio; (4) CFD 3D só se formos mesmo ao
  cabide.
* publicação: `03_/AVALIACAO_V30_X_FLUXO_2026-09-25.md` (novo), nota no `PLANO_DE_VALIDACAO_E_SIMULACAO.md`,
  ponteiro no relatório de contato e este bloco. **Pacote, DXF, zip, CHECKSUMS e a tag seguem intocados**
  (`80167f2`); `verificar_cadeia.py --rapido` rodou com os documentos no lugar antes do push.

**Rodada 2026-09-25 (9ª) — "hoje usamos a matriz copo; veja como ela fica no cabeçote e pense em como resfriar".**

* medido nesta rodada, no arquivo da montagem `06_/STEP/Cabecote_EX-030_com_Matriz_Copo.step` (cadquery, distância
  de peça a peça por `BRepExtrema`, volume por `GProp`): corpo **Ø93,00 × 80,70 mm**, volume **224.289,0 mm³**
  = 1,761 kg; o "copo" é um furo **Ø75,60 × 70,70 mm** entrando pela **traseira**; a fenda 75,00 × 1,500 (R 0,75)
  atravessa o fundo, com **land de 10,00 mm** (Z 70,70 → 80,70) e **sem chanfro e sem funil** (o fundo é um degrau
  de 90°). A boca fica em **Z 80,70** contra a face do nariz do cabeçote em **Z 95,00** ⇒ **14,30 mm enterrada**
  dentro do túnel Ø80,00 × 14,00 mm, que tem **70.371,7 mm³** livres e trabalham cheios de massa.
* folgas medidas, e elas são o resultado: banda Ø93,00 no bolso Ø95,00 = **1,00 mm de ar** (e é a banda do
  collete); ombro no degrau = **0,10 mm** (anel de 501,7 mm², contato real 431,2 mm²); estágio Ø89,50 = **0,25 mm**;
  face frontal até o plano do degrau = **0,30 mm**. Casca total **55.129,7 mm²**: **37,0 %** na banda, **30,5 %** no
  furo do copo, e **52,4 %** (28.864,7 mm², contando fundo e land) molhados de massa ⇒ **nenhum ponto da copo vê o
  ar**. Consequência: não existe onde pôr
  refrigeração na matriz, e **não existe posição** para furo de água (centro teria de cair entre 43,80 e
  40,50 mm de raio — faixa vazia). Também **não dá para fazê-la protruir**: faltam 1,50 mm de raio para a banda
  Ø93,00 passar do degrau Ø90,00.
* comparado no mesmo cabeçote, medido agora: **copo boca −14,30 mm**, **v30 boca rasa com a face (0,00)**,
  **v29/v27 boca +14,00 mm para fora**. Ou seja: a refrigeração "na boca da matriz" que dá na v30/v29 **não dá**
  na copo. Escrito na §2 de `03_/RESFRIAMENTO_MATRIZ_COPO_2026-09-25.md` com as três linhas medidas.
* física do "enche de calor", agora com o número da copo: capacidade **855,7 J/K** (a metade da v30, que tem
  1.673 J/K) + **398 g** de massa parada dentro do copo (318.480,7 mm³, renovados a cada **21,2 s**) que é outro
  reservatório de 796 J/K tocando 33 % da casca. Calor do land: ΔP 2,187 bar/mm × 10,00 = **21,87 bar** ⇒
  **32,8 W** a Q = 15.000 mm³/s (teto da 8ª com a simulação do pacote: 305 W). Com o calor preso: 20 °C em
  **8,7 min** (33 W) a **0,95 min** (300 W).
* o caminho que existe é o **filme de 0,30 mm entre a face da matriz e o degrau do cabeçote** (R ≈ 0,194 K/W com
  massa no vão; 1,87 K/W se for ar) e o de 0,25 mm do estágio (0,329 K/W). Logo **resfrie o nariz do cabeçote na
  faixa lisa Ø130,00 de Z 53,00 a 81,00** (11.435,4 mm², a 18,50 mm da matriz, sem furo nenhum ali — os 6 Ø16,5
  ficam em Z 3..43 e o M12 do pushador em Z 22,98): 40 °C de diferença puxam ≈ **330 W** por esses filmes, e
  **300 W são +4,3 °C em 1 L/min de água**. Colar parado (duas conchas, canal de 3 mm) não fura o cabeçote, que
  é cementado 52-55 HRC. **Por que parar em Z 81,00:** Z 81..95 é o túnel por onde a manta sai, e gelar o túnel é
  incrustrar massa no Ø80 — o motivo pelo qual o projeto sempre quis a boca fora do cabeçote.
* **corrigindo a 8ª num ponto:** lá escrevi "IR no lábio da matriz" e "cuneta de água no nariz do cabeçote" como
  opção 3. Com a copo **o lábio não é visível** (está a 14,30 mm dentro do furo): o IR vai na **face do nariz do
  cabeçote** (anel Ø80→Ø130, 8.246,7 mm², 14,30 mm da boca e colada nela pelo filme de 0,30 mm), com o offset
  boca↔face calibrado uma vez só com termopar de ponteira. E o "furo de água na matriz", que na 8ª era "última
  opção", na copo passa a **impossível** (a faixa vazia de raio acima).
* ordem executável que ficou para ele: (A) pano encharcado/gotejador na banda (0 R/W extra, leva os 33 W com
  10-30 °C de diferença, não leva os 300 W); (B) faca de ar **depois** da face do nariz, nunca na boca;
  (C) colar d'água Z 53→81; (D) mastiche 1 °C mais frio = **37,5 W embora** (18,75 g/s × 2 J/g·K) — a alavanca
  mais forte e de graça, com o preço escrito (pressão e solda no R 0,75). Não: furo na matriz, furo M12 como
  entrada de ar, espaçador para protruir.
* **arquivo novo, por ordem dele:** `HISTORICO_DA_CONVERSA.md` na raiz — linha do tempo leve de toda a conversa
  (11/09 até aqui), **uma entrada por rodada**, atualizada e publicada a cada interação. A regra entrou no §12.
* **acréscimo da mesma rodada, com as fotos dele no repo `ity1300-wq/ACESS`** (6 JPEG + 1 MP4 de 25/09 14:08,
  baixados e conferidos por sha256; vídeo lido em quadros com ffmpeg do `imageio-ffmpeg`): a ponta do cabeçote é
  uma **face plana de aço sem tinta com furo redondo** por onde a manta passa, sem nenhuma boca de matriz para
  fora ⇒ **confirma visualmente a boca enterrada de 14,30 mm e o túnel Ø80 × 14,00**. A faixa sem tinta está
  **livre de abraçadeira de aquecimento e de manta térmica** (dá para abraçar o colar ali), há um **mostrador
  0-150 °C classe 1** rosqueado no corpo atrás do flange (não precisa de IR para o teste), **não há água** no
  conjunto (as mangueiras pretas entram por prensa-cabo, são conduíte), e **existe puxador**: par de rolos de
  aço nus com fuso e mola, mais bobina de material branco guiada por roletes de nylon ⇒ **fecha a pendência do
  puxador da 7ª** (o swelling não é livre, e o teto de 2,2 mm por falta de puxador cai). Na máquina parada o
  mostrador marca ~25-30 °C, então **nenhuma temperatura de processo foi lida nas fotos** — regra que eu me dei
  depois do erro do disco de corte: foto responde o que está onde, não como o processo roda.
* e uma checagem que **não é conclusão**, escrita como checagem: no vídeo (~22 s) a tira cinza no furo redondo
  encosta na borda do furo de um lado. Se a manta correr descentrada, a quina raspa no fio do furo do nariz e o
  serrilhado ganha uma causa mecânica além da térmica. Custo da checagem: 30 s de vídeo da saída em produção. No
  CAD o espaço é 2,50 mm por lado.
* publicação: `03_/RESFRIAMENTO_MATRIZ_COPO_2026-09-25.md` (novo, com a §10 das fotos), `HISTORICO_DA_CONVERSA.md`
  (novo) e este bloco. **Nenhuma cota tocada; pacote, DXF, zip, CHECKSUMS e a tag seguem intocados** (`80167f2`);
  `verificar_cadeia.py --rapido` rodou com os documentos no lugar antes do push.

**Rodada 2026-09-25 (8ª) — ele mudou o alvo ("PRINCIPAL PROBLEMA" = serrilhado nas pontas) e deu a pista que
fechou o diagnóstico: "sempre que esfria sai boa, depois esquenta e sai ruim".**

* **recado que fica para quem assumir:** o alvo do projeto, na cabeça dele, e **o serrilhado nas extremidades**.
  Espessura **nao** e o problema a resolver, e eu gastei duas rodadas falando de perfil de espessura. Leia
  "igualizar vazao" como *meio* para tirar tracao da borda, nunca como fim.
* o sintoma novo (limpa no comeco, piora ao longo da producao e com velocidade) **descarta defeito de forma**
  (forma serra desde o primeiro metro) e aponta para saturacao termica da matriz. Contas em
  `03_/RESFRIAMENTO_DA_MATRIZ_2026-09-25.md`: 40 W (1D do projeto, 26,68 bar) a 305 W (modelo com anel de fuga,
  203,6 bar) de dissipacao, dos quais **28 a 213 W na parede do land** (69,7% do DeltaP e land); o bolo de
  mastique sobe so **+0,7 a +5,7 K**, mas a matriz de 3,442 kg de aco tem **1,69 kJ/K** de capacidade e sobe
  **20 C em 2,6 min a 20 min** sem resfriamento nenhum. **E o "aos poucos" dele, em minutos - bate.**
* entao refrigeraçao aqui e um problema de 30 a 200 W: **1 L/min de agua de rede sobe 3 C com 213 W**. Ordem de
  opcoes, da de graca para a cara: copo de gotejamento / pano encharcado no nariz > faca de ar (air knife) na
  manta nos primeiros 30-50 cm (e o unico item que resfria E segura a borda contra a tracao) > cuneta de agua no
  nariz do **cabecote** (mexe em 06_, nao na matriz) > mastique chegando mais frio > furo de agua dentro da
  matriz.
* **por que a agua dentro da matriz e a ultima opcao, com numero:** boca do canal 075,60 em Z=0, primeiro estagio
  094,00 -> 9,20 mm de aco no raio; furo 04 mm com parede minima de 4,00 mm ate o canal (o mesmo criterio do
  `ESTUDO_RECUO_CARTUCHOS.md`) deixa **1,2 mm de janela** de posicionamento, longe do land (que e em Z 85 a
  93,50, onde o aco que sobra e o do labio), e tem de ser furado **antes** do T.T. (55-60 HRC). Carissimo para
  ganhar pouco: nao faca isso primeiro.
* controle que vale mais que equipamento: termometro de **infravermelho no labio**, cronometrar o primeiro dente
  em 3 velocidades e com/sem resfriamento -> sai o `T_limiar` dele (aposto em 55-75 C, mas o numero e medido, nao
  meu). Regra operacional: segurar o labio em `T_limiar - 10 C`. Contrapeso escrito no doc: **nao congelar
  demais** (pressao sobe e a casca pode nao soldar nos cantos R 0,75, que e justamente onde a manta arrebenta);
  alvo 10 a 25 C abaixo da cabeca.
* e o ponto que impedi de virar vendedor de matriz: **resfriar da tempo, nao tira a tracao da borda.** Os dois
  andam juntos - gotas nos extremos + arco do sorriso na fenda para tirar a carga, resfriamento para segurar a
  janela de tempo. Escrito assim no documento para o portao nao deixar alguem prometer o contrario depois.

**Rodada 2026-09-25 (7ª) - segunda medicao, agora com balanca: o perfil e real, a saga fecha em 2 mm de flecha.**

* ele remedeu 5 pontos (1,50 / 2,50 / 2,50 / 2,00 / 1,50 mm) E pesou (0,80 / 1,30 / 1,40 / 1,10 / 0,80 g).
  `m/t` nas cinco estacoes: media 0,539 g/mm, desvio-padrao **2,9%**, afastamento maximo entre os dois metodos
  7,1% -> **o perfil nao e o paquimetro afundando no mastique**. Registrado em
  `03_/MEDIDA_2_PERFIL_E_PESO_2026-09-25.md`.
* seccao integrada pelos 5 pontos: **159,4 mm2** contra 112,5 mm2 nominais = **+42% de seccao**; com a vazao de
  referencia (Q = 15.000 mm3/s) isso sai a **5,6 m/min** em vez de 8,0 m/min. Enquadramento que me corrigi no
  meio do raciocinio: com rosca fixando a vazao, ele **nao esta queimando material** - esta entregando ~30% menos
  metro por hora com a mesma maquina. Igualizar a 1,50 e tambem producao.
* **a assimetria piorou e isso e o diagnostico principal agora:** -18,75 da 2,50 e +18,75 da 2,00 (**+25%**, na
  primeira mediacao era 10%), e o maximo nao esta mais no centro (2,50 em -18,75 E em 0,00) - a barriga migrou.
  Funil simetrico + fenda reta **nao faz isso** (centroide medido a -0,0071 mm do plano de simetria). Pendencia
  nº 1, antes de qualquer desenho: **girar a matriz 180 graus e remedir os 5 pontos**.
* a conta que a medicao dele produz, com `n = 0,32` e o gradiente de land do projeto (2,187 bar/mm): centro de
  2,50 para 1,50 = 1,67x menos vazao = **+18% de resistencia local = +4,74 bar = 2,2 mm de land a mais no
  centro**. Isso e o **arco do sorriso** (flecha ~2 mm, raio ~353 mm, corda 75,00 intacta, fenda desenvolvida
  +0,19%): afasta o meio da entrada e aproxima as pontas ao mesmo tempo - o alivio nas costas so abre as pontas,
  o que neste perfil empurraria tudo para 2,5 mm e obrigaria a esticar a manta no puxador. **Primeiro passo 1,5
  mm de flecha, nao 2,2**, porque sem puxador medido o swelling infla a diferenca de espessura (teto, nao alvo).
* subproduto pedido a ele: area real da amostra (saiu ~431 mm2 com rho 1,25 de literatura) - com a area medida eu
  devolvo a **densidade medida do mastique**, numero que este projeto nunca teve.
* publicacao: dois documentos em `03_` + este bloco. **Nada de SSOT, STEP, pacote, DXF, zip ou CHECKSUMS** - a
  tag `v30.0-oficial-pacote-usinagem` segue em `80167f2`; `verificar_cadeia.py --rapido` com PORTA ABERTA antes
  do push (e as duas travas de sempre re-aplicadas no comeco: `git config user.name/user.email` e
  `git checkout HEAD -- 01_CAD_MatrizJonatha_Oficial 02_CAD_Modelos_Historicos`, sem o que o portao morre em
  `FileNotFoundError` no STEP).

**Rodada 2026-09-25 (6ª) — ele MEDEU o perfil da manta e o Fernando mandou as duas soluções em foto.**

* medição dele em 5 pontos (A→B, mm): **1,50 · 2,00 · 2,57 · 1,80 · 1,50** nos `y = -37,5 / -18,75 / 0 / +18,75
  / +37,5`. Assumindo velocidade de linha igual na largura, q/q_centro = **0,584 / 0,778 / 1,000 / 0,700 /
  0,584** - e com `n = 0,32` isso corresponde a **+18,8% de resistencia nas bordas**, nao a 71% de diferenca.
  Registrado em `03_/PERFIL_DE_ESPESSURA_E_SORRISO_2026-09-25.md`, com o limite escrito (se a manta cai solta,
  sem puxador, espessura nao e vazao e 18,8% vira teto; a ite­racão de bancada e o metodo).
* com o numero dele a conclusao fica mais dura do que a minha frase anterior: **frear o centro = +5,02 bar e a
  linha caindo a 80% da producao; abrir as bordas = -4,2 bar dentro dos 6,73 bar que o funil+entrada gastam
  (75% do orcado) e a producao subindo a 137%**. Freio compra informacao, alivio e o que se fabrica.
* as duas fotos do Fernando, vistas em zoom (nao e a legenda de IA, e o que esta na imagem): **disco azul com a
  fenda em arco de sorriso, relevo `90 x 2mm` na face e os dois furos de virar a matriz acima do arco** (cor
  azulada = tempra/oxide de revenimento), e **disco de aco com fenda reta de pontas em gota + um tampo quadrado
  em relevo no centro** (setas verdes: o tampo = freio; as gotas = "abrir mais nas pontas" feito na propria
  fenda). A conta que torna o sorriso fabricavel sem briga com a peca: **corda 75,00 nao muda** (a largura da
  manta fica a contratada) e a fenda desenvolvida cresce so **+0,19% a sagita 2,00 mm** e +0,43% a 3,00 mm -
  trajetoria de fio EDM, nao forma nova. Sagita e cota de ajuste, comecando em 1,00 mm.
* **o achado que nao e de fluxo:** -18,75 mede 2,00 e +18,75 mede 1,80 - **10% de assimetria entre os lados,
  mesma distancia do centro**, e funil simetrico + fenda reta nao produzem isso (no modelo os dois lados sao o
  solido espelhado). Antes de cortar metal: **girar a matriz 180° e remedir os 5 pontos**. Se a assimetria
  acompanha a matriz, e matriz/assento; se fica no mesmo lado da maquina, e maquina e desenho nenhum conserta.
* metrologia melhor que paquimetro em massa: 5 amostras de 50x50 mm pesadas; com rho 1,25 g/cm3 (SSOT) cada
  1,50 mm de espessura pesa 4,688 g, entao **balanca de 0,01 g resolve 0,0032 mm** sem achatar nada.
* rev. 31 proposta no documento (nada no SSOT): fenda em arco (corda 75,00, sagita 1,00 como cota de ajuste) +
  janela de alivio na face de entrada mais funda nas bordas + chanfro 1,50 -> 0,50 (PRP-0002: 27,96 bar, labio
  0,75 -> 1,75 mm, land de 69,7% para 74,3% do DeltaP). Entra como `PRP-0007` no protocolo quando ele decidir.

**Rodada 2026-09-25 (5ª) — "nosso objetivo é justamente tirar o serrilhado": a conta do centro×pontas.**

* ele cobriu o ponto: se os nossos estudos já diziam que a v30 não tiraria o serrilhado, então o projeto errou o
  alvo. Novo documento de discussão, `03_/FLUXO_CENTRO_X_PONTAS_2026-09-25.md`, com o que se pode afirmar com o
  que existe no repo e o preço de cada remédio. As três contas que ele carrega:
* **amplificação** - `n = 0,32` (`cad_die_parameters.json`), entao vazao local escala com `(1/R)^(1/n)` e
  `1/n = 3,125`: **+10% de caminho/resistencia na ponta = -26% de vazao na ponta**, +20% = -43%. E a conta ao
  contrario (a util, a que da a cota do alivio): para a ponta entregar `k` vezes mais, a resistencia dela cai para
  `k^-n` -> ponta 10% mais fina pede **apenas -3,3% de resistencia**, e 20% mais fina pede -6,9%. Daqui a
  discussao de "quanto fresar" sai de um paquimetro de 5 pontos na manta, nao de CFD.
* **para onde vai a pressao hoje** (metodo 1D do projeto, mesmo dos PRP-0002/0004): land 8,50 mm = **18,59 bar
  (69,7%)**, chanfro 1,50x45 = 1,36 bar (5,1%), funil+entrada = 6,73 bar (**25,2%**), total 26,68 bar. So o trecho
  de baixo e onde nasce o desequilibrio - e a folha nao e "a boa" so por isso.
* **preco de cada alavanca**: abrir as pontas vale **+39% de vazao na mesma pressao** (no limite de -56% da ponta);
  frear o centro ate equalizar custa **-39% de producao** - por isso o freio dele e teste, nao projeto. E a
  saida da marmitaria-padrao (variar a folga) esta **bloqueada pela peca**: equalizar por folga pediria 1,7644 mm
  na ponta contra 1,500 no centro, e 1,500 +0,010/-0,000 e contrato. O "sorriso" dele e a mesma ideia aplicada ao
  contorno, nao a espessura - por isso e ajustavel na bancada.
* proposta de rev. 31 em discussion (nada no SSOT): **chanfro 1,50 -> 0,50** (PRP-0002 ja calculado: 27,96 bar,
  +4,8%, e parede do labio 0,75 -> 1,75 mm, o que fecha o P7 da triagem) **+ janela de alivio rasa na face de
  entrada, mais funda nas pontas, com sobra de aco para ajustar depois**. Se ele topar, isso entra como
  `PRP-0007` no protocolo, com o metodo do projeto por tras, e o CFD 3D adiado decide se precisa asa de verdade.
* honestidade que o documento repete: **os 52,3% do `avaliacao_matriz3_uniformidade.py` nao sao o gradiente
  centro-ponta** (sao o R 0,75 nas pontas, com 0,63% da vazao nos ultimos 1,00 mm) e o modelo 2D por seccao
  **pressupoe pressao igual na largura**, entao e cego ao efeito de coletor. Ordem de grandeza e o que se pode
  afirmar; quem fecha e o paquimetro na manta e o teste do freio.

**Rodada 2026-09-25 (4ª) — a correção dele: "que disco de corte? não tem disco de corte nenhum, a manta sai
serrilhada da matriz".**

* lida e aplicada nos três documentos que carregavam a inferência errada: `03_/CONTATO_MATRIZARIA_FERNANDO_2026-09-24.md`
  (§3b e a pendência nº 0), `03_/AVALIACAO_V30_X_FLUXO_2026-09-25.md` (§5 reescrito, linha 0 da tabela de passos e
  a recomendação final) e este arquivo. Verifiquei antes de reescrever: recorte ampliado dos dois quadros
  (recorte ampliado na sandbox, descartavel) mostra **material branco** e uma lâmina — e o mastique das fotos ao lado é
  **cinza-chumbo**, então o quadro não é da linha dele de todo.
* o que muda no conteúdo técnico, sem rodeio: **o serrilhado nasce na saída da matriz**, portanto **a matriz
  conserta**. A parte que eu defendi com o τ (o canal não muda a fratura por cisalhamento) continua verdadeira,
  mas vale para *sharkskin*, não para rasgo por desequilíbrio — e o dado do repo que apoia o Fernando é
  justamente `q = 23,2 % do núcleo` nos últimos 1,00 mm de cada lado, com o centro a 215,5 mm³/s/mm contra 112,7
  na beirada (`avaliacao_matriz3_uniformidade.py`).
* o que muda na recomendação: sai "olhe o disco de corte" e entra, na ordem, **freio na matriz em uso** (teste
  barato que decide), depois **rev. 31 com freio/alívio embutido**; o teste de régua no período das ondinhas fica
  só para separar pulsação da rosca da parte que é de matriz.
* nada de pacote/DXF/zip/tag mexido; `verificar_cadeia.py --rapido` volta a rodar antes do push desta rodada.
* **lição de git, e ela quase me custou a rodada:** eu emendei a mensagem do commit *depois* de já ter escrito o
  sha da versão antiga na linha do merge (`git merge --no-ff aeabfdb`), e o merge foi buscar o commit **órfão** —
  deu conflito "both added" em dois arquivos porque `main` e `continue` passaram a ter duas cópias irmãs do mesmo
  conteúdo. `main` voltou a `continue` (conteúdo de `17f53a9`) e a árvore foi conferida igual ao final. Regra que
  fica: **nunca citar sha literal em comando de publicação depois de um `--amend`; use o nome do branch** — o sha
  deixa de existir como ancestral e o merge deixa de ser um merge.


