# CONTINUIDADE — retome daqui, sem a conversa

**Este arquivo + `git log` = a sessão.** Se a conversa do agente for perdida, qualquer pessoa ou outra IA
com acesso a este repositório consegue continuar exatamente de onde paramos lendo este arquivo e o histórico
dos commits. Nada de decisão vive só no chat: o que vale está aqui, nos relatórios de
`03_Relatorios_e_Documentacao/` e nos JSON de `04_Dados_SSOT_e_Scripts/`.

Atualizado em **2026-09-13 (fim do dia)**, na rodada que promoveu a peça única a v29.0 e montou o pacote
de usinagem `08_Pacote_Usinagem_v29/`.

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
   Ø79,50 × 28,30** (Z total 109,00).
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
