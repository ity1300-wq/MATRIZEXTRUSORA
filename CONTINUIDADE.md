# CONTINUIDADE — retome daqui, sem a conversa

**Este arquivo + `git log` = a sessão.** Se a conversa do agente for perdida, qualquer pessoa ou outra IA
com acesso a este repositório consegue continuar exatamente de onde paramos lendo este arquivo e o histórico
dos commits. Nada de decisão vive só no chat: o que vale está aqui, nos relatórios de
`03_Relatorios_e_Documentacao/` e nos JSON de `04_Dados_SSOT_e_Scripts/`.

Atualizado em **2026-09-13**, no commit da reorganização #2 (uma pasta por matriz + apagamento da Gedeon
"corrigida").

---

## 1. Estado em uma frase

A **Matriz Jonatha v27.0** continua sendo o modelo oficial da fábrica; a variante **v28.1** está verificada
mas **não promovida** (espera aprovação explícita do dono); a **Gedeon certa é o arquivo do usuário
entregue como está**, medido face por face; e a auditoria está **pausada por ordem dele**
("`ignore auditoria agora`") até geometria e repo estarem do agrado dele.

## 2. O que está entregue agora

| peça | onde | estado |
|---|---|---|
| Matriz Jonatha v27.0 (master) | `07_CAD_Matrizes/Matriz_Jonatha_v27_OFICIAL/` | intocada; `01_CAD_MatrizJonatha_Oficial/` são 6 atalhos para cá; o sha256 do master bate o baseline do auditor |
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
git checkout continue
# o render offscreen precisa de uma biblioteca GL local que fica fora do git:
export LD_LIBRARY_PATH=$PWD/04_Dados_SSOT_e_Scripts/.headless_gl
python3 04_Dados_SSOT_e_Scripts/gerar_gedeon_certa.py        # mede o arquivo do usuario (21 checks)
python3 04_Dados_SSOT_e_Scripts/verificar_cadeia.py          # O PORTAO (roda os 9 scripts, ~4 min)
python3 04_Dados_SSOT_e_Scripts/verificar_cadeia.py --rapido # nao re-gera CAD (para consulta rapida)
```

Se o portão disser `cadquery não está instalado`, é sandbox recriada: `pip install cadquery`.

**Espaço.** O que o painel chama de workspace é o que o snapshot persiste (o `.cache` de 305 MB fica fora).
Depois da limpeza de 2026-09-13: 41 MB no total, sendo 31 MB do repo — dos quais **22 MB são `.git`**
(histórico de STEP; só encolheria reescrevendo histórico, o que não faremos sem ordem) e 8 MB de árvore.
O que é seguro apagar a qualquer momento, porque o portão recria: `04_Dados_SSOT_e_Scripts/__pycache__`,
os PNG soltos da raiz do workspace, `06_/STEP/estudos/`, os STEP derivados ignorados (`_Explodida`/
`_Com_Fluxo` da v28) e os `DESENHO_2D_*_p*.png`. Nada disso precisa ir ao git.
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

1. **Auditoria pausada.** Quando ele mandar voltar: re-selar baseline (`--atualizar-hashes`) e reabrir o
   veredito da PR #3. Nada foi feito nisso a pedido dele.
2. `03_/AUDITORIA_GEOMETRICA_MATRIZ_JONATHA.md` §6 ainda descreve a reconstrução refutada em parte do texto —
   os ponteiros foram atualizados, mas a seção não foi reescrita (zona de auditoria, congelada agora).
3. Os `arquivos[]` de `05_/propostas/PRP-0005-v28-1-fabricacao.json` apontam para
   `01_CAD_MatrizJonatha_Oficial/MatrizJonatha_v28*`, que **não tem atalho** (a v28.1 mora em
   `07_CAD_Matrizes/Matriz_Jonatha_v28_1_PROPOSTA/`). A proposta já foi auditada, então **não se edita**:
   quando a auditoria voltar nasce `PRP-0006` com os caminhos certos. Anotado aqui para não surpreender.
   A branch `proposta/PRP-0005` ficou na estrutura anterior (com o aninhamento `M01..M06`) **de propósito**:
   PR em revisão não se reescreve. Quem for olhar o diff da PR #3 veja os arquivos em
   `07_CAD_Matrizes/Matriz_Jonatha_v28_1_PROPOSTA/` na branch `continue`.
4. PR #3 (nossa) sem comentário de estado no GitHub; PR #4 (`arena/01a096e3-...`, proposta PRP-0006 de outrem:
   land 10,00 mm com chanfro 0,80) está aberta e **não** foi avaliada por nós. O chanfro do master é 1,50 e
   assim fica até ele dizer o contrário.
5. Geometria do cabeçote que ainda depende de decisão dele: o chanfro que falta no desenho dele foi conferido
   no DXF (10 × 45° na face do flange) e a cabeça do parafuso M12 no furo de 16,5 — o cenário da furação M12
   foi removido do repo; fica no disco em `06_/STEP/estudos/` e recria com
   `python3 04_Dados_SSOT_e_Scripts/gerar_cabecote_ex030.py --com-m12`.

## 9. Como ler o histórico

```bash
git log --oneline -40                 # a linha do tempo das decisoes
git log --oneline -- 07_CAD_Matrizes    # o que mudou na organizacao das matrizes
git show --stat HEAD                     # a reorganizacao #2, com a justificativa no corpo
git log origem/main..HEAD --oneline      # o que ainda nao desceu para a main
```

Branches no GitHub: `main` (oficial, só entra por PR aprovada), `master` (legado), `continue` (nosso
trabalho — é a que tem o estado atual), `proposta/PRP-0005` (a v28.1 em avaliação), e as duas
`arena/01a096e3-*` / `arena/01a091ce-*` da cerimônia de auditoria.

## 10. Recado para quem assumir

Não promova a v28.1 por conta própria, não toque em `02_/` a não ser para ler, não re-escave a Gedeon e não
recrie a "Gedeon corrigida". Se precisar escrever número em algum lugar, meça primeiro: o portão
(`verificar_cadeia.py`) compara texto de relatório contra JSON justamente para pegar número que apodreceu.
E se mudar um caminho, rode o portão completo antes de dizer que está pronto.
