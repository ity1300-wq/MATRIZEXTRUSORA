# Rascunhos da sessão de 2026-09-12/13 — o que foi feito a mão, guardado por integridade

Nada aqui faz parte da cadeia do portão (`04_Dados_SSOT_e_Scripts/verificar_cadeia.py`). São os **scripts
descartáveis** com que a sessão leu o croquis dele, mediu, desenhou e remendou documentos. Entram no
repositório porque ele mandou atualizar o GitHub com o workspace inteiro — e porque, sem eles, a próxima
sessão teria de adivinhar como certos números foram lidos do DXF. Estão aqui como estão: alguns já foram
sobrescritos pela versão final que virou script de verdade (coluna "o que vale hoje").

| grupo | arquivos | o que vale hoje |
|---|---|---|
| **ler o croquis** (DWG/DXF do cabeçote) | `le_dwg.py`, `textos_dxf.py`, `por_camada.py`, `render_dxf.py`, `corte_cabecote.py`, `cotas_do_desenho.py`, `procura_chanfro.py`, `olhar_visao.py` | o que saiu disso virou `medir_perfil_cabecote.py` (k = 25,534 mm/unidade, meio-corte em mm) e o DXF compactado `04_/cabecote.dxf.xz` |
| **vistas e silhueta** | `render_vistas.py`, `so_contorno.py`, `so_contorno_vista1.py`, `traseira.py`, `perfil_contorno.py`, `dxf_folha.png`, `vista1.png`, `vista1_zoom.png`, `vista2.png` | as PNGs são recortes do meu render `cab_vista_esq.png` da folha dele (a vista esquerda do cabeçote, com o chanfro `CHANF. 10X45°`, Ø130/Ø80/Ø90 +0,1 e os "11/20/40/70/81" lidos ali). O `cab_*.png` que gerou isto foi apagado do workspace na limpeza de espaço; estas três cópias são o que restou |
| **as faixas da prancha** | `faixa3.py`, `faixa5.py`, `faixas_curtas.py`, `faixas_novas.py`, `cantos.py`, `cantos_finais.py`, `canto_do_passo.py`, `fim_da_peca.py` | a versão final mora em `desenhar_gedeon_consertada.py` (5 faixas no mesmo escalonamento) |
| **montagens e medições da matriz no cabeçote** | `matriz_desenhada.py`, `matriz_no_desenho.py`, `corte_cabecote.py` | `gerar_cabecote_ex030.py`, `verificar_interface_cabecote.py`, `medir_perfis_matrizes_x_cabecote.py` |
| **remendos de documento** | `plica_auditoria.py`, `plica_face_a_face.py`, `plica_montagens.py`, `plica_montagens_sem_booleano.py`, `novo_bloco_md.py`, `main_desenho.py`, `novo_main_desenho.py`, `aplica_portao.py`, `secao7.py`, `bloco1.py`, `bloco2.py`, `bk.py`, `fim_da_peca.py` | texto aplicado a `03_/` e ao `README.md` da raiz; só úteis para ver a ordem em que as correções entraram |

Aprendizados embutidos nesses arquivos, que custaram tempo e valem repetir:

* hachurar a figura de `−r_ext` a `+r_ext` **apaga** furos fora do eixo — o `perfil` é radial, não é silhueta;
* rótulo dentro da figura colide com geometria: legenda vai acima (`y ≈ 122..133`);
* `MemoryError: std::bad_alloc` em `fig.canvas.draw()` → salvar a figura inteira em dpi baixo, não prantar por partes;
* tolerância de planaridade `1e-9` descarta cara resultante de booleano — usar `1e-6`;
* em `cadquery` 2.8 não existe `Solid.union` nem `Shape.slice`/`Edge.discretize`: `BRepAlgoAPI_Common` +
  `TopExp_Explorer` + `GCPnts_UniformDeflection(0.05)`.

**O que NÃO veio de propósito:** `/home/user/tmp/.gh` (o token de acesso ao GitHub — jamais entra no git, e ele
deve ser revogado por ser público o repo e o token ter circulado no chat) e as capturas dele em `uploads/`,
listadas com hash e origem em `03_Relatorios_e_Documentacao/FONTES_DO_USUARIO_2026-09-13.md`.
