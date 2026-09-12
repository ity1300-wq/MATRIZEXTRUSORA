# Interface matriz v28 × cabeçote EX-030

O sólido do cabeçote foi montado do perfil lido no DWG 030-032 (escala calibrada pelas próprias cotas: 25,534 mm por unidade DXF, cinco fechos independentes batendo em 0,012 %). Todos os números abaixo saem de booleanos e `BRepExtrema` contra `MatrizJonatha_v28.step`.

| item | medido | nominal | desvio | status | observação |
|---|---|---|---|---|---|
| Interferência matriz ∩ cabeçote | 0.0 | 0.0 | 0.0 | CONFORME | a matriz tem de entrar e sair sem tocar |
| Folga radial - Ø93×69,90 no bolso Ø95×70,0 | 1.0 | 1.0 | -0.0 | CONFORME |  |
| Folga radial - Ø89,5×10,80 no Ø90×11,0 | 0.25 | 0.25 | -0.0 | CONFORME |  |
| Folga radial - Ø79,5×28,30 no Ø80×14,0 | 0.25 | 0.25 | -0.0 | CONFORME |  |
| Folga axial no degrau de apoio (ombro) | 0.1 | 0.1 | -0.0 | CONFORME | o ombro da matriz encosta no degrau: é o apoio da força |
| Folga axial entre o ombro Ø89,5→Ø79,5 da matriz e o degrau Ø90→Ø80 | 0.3 | 0.3 | -0.0 | CONFORME | o canto do Ø89,5 passa a 0,30 do degrau do nariz: é a folga que evita o encunhamento |
| Face de entrada da matriz rasa com a traseira do cabeçote | -0.0 | 0.0 | -0.0 | CONFORME | a boca Ø75,60 fica exposta ao canal de massa do flange |
| Protrusão da face de saída além da face do nariz | 14.0 | 14.0 | 0.0 | CONFORME | a fenda trabalha fora do cabeçote: nada de filme congelado na frente da matriz |
| Anel da face (Ø90 → Ø130) | 20.0 | 20.0 | 0.0 | CONFORME | confere com o '~20 mm' descrito |
| Menor distância parafuso M12 (C.C Ø180) → corpo da matriz | 35.25 | 35.25 | 0.0 | CONFORME | nenhum furo da junta cabeçote↔extrusora alcança a matriz |
| Curso livre da manta após sair da matriz até o cabeçote | 14.2201 | — | — | CONFORME | a manta nasce 14 mm à frente da face do nariz e sai pela diagonal do furo Ø80: não há contato possível |
| Folga do nariz Ø79,5 no furo Ø80 (a 1 mm das bordas do degrau) | 0.25 | 0.25 | -0.0 | CONFORME |  |
| Folga do PRODUTO (75,00) no furo Ø80 - o que voce mediu na maquina | 2.5 | 2.5 | 0.0 | CONFORME | 'sobra 2,5 mm em cada extremidade da fenda' - reproduzido pelo modelo medido |
| Folga da BOCA da matriz (com o chanfro de D2) no furo Ø80 | 1,000 mm por lado  (boca medida: 78,000 × 4,500 mm) | — | — | CONFORME | consequência de manter o chanfro 1,50 × 45: a boca abre para 78,000 mm e a folga cai de 2,50 para 1,000 mm se o bico do cabeçote chegar até a face da matriz - é por isso que o comprimento do bico (14,00 mm no desenho) é a única medida que falta |
| Interferência matriz ∩ cabeçote COM anel Ø68,30 | 5098,0 mm³ | — | — | PENDENTE_CONFIRMACAO | FECHADO por medição na máquina: sobram 2,5 mm/lado na fenda, entao a passagem e o proprio Ø80 do cabecote - o volume acima so vale se alguem reaproveitar o anel de 65 mm |
| Sobra na extremidade da fenda × passagem do cabeçote | Ø80,00 → sobra 2,500 mm por lado (usuário mediu ~2,5) · Ø68,30 do anel de 65 mm → faltariam 4,850 mm | — | — | PENDENTE_CONFIRMACAO | o número medido na máquina só casa com o Ø80: prova de que o anel de 65 mm não está lá |
| Passagem do anel × nariz da matriz | Ø68,300 contra Ø79,50 → 5,600 mm de interferência radial por lado | — | — | PENDENTE_CONFIRMACAO | p/ 75 mm a passagem teria de ser ≥ Ø79,6, e o furo do nariz já é Ø80: não há espaço para anel |
| Área de passagem do cabeçote × boca da matriz | 81,6 %  (3664 mm² / 4489 mm²) | — | — | PENDENTE_CONFIRMACAO | restrição de alimentação e zona morta se o anel de 65 mm for mantido |
| Furo pino_alinhamento X=-42,1 Z=30,0 não rompe o envelope | 0.0 | 0.0 | 0.0 | CONFORME | parede até o Ø93 = 0,794 mm |
| Furo pino_alinhamento X=42,1 Z=30,0 não rompe o envelope | 0.0 | 0.0 | 0.0 | CONFORME | parede até o Ø93 = 0,794 mm |
| Furo pino_alinhamento X=-42,1 Z=60,0 não rompe o envelope | 0.0 | 0.0 | 0.0 | CONFORME | parede até o Ø93 = 0,794 mm |
| Furo pino_alinhamento X=42,1 Z=60,0 não rompe o envelope | 0.0 | 0.0 | 0.0 | CONFORME | parede até o Ø93 = 0,794 mm |
| Furo cartucho X=0,0 Z=97,0 abre na banda livre | alcance 42,019 mm x r do nariz 39,750 mm -> escancara 2,269 mm | — | — | CONFORME | a 2,000 mm à frente da face do cabeçote: acesso intencional ao cartucho/termopar, sem caminho para o bolso |
| Furo cartucho X=0,0 Z=97,0 abre na banda livre | alcance 42,019 mm x r do nariz 39,750 mm -> escancara 2,269 mm | — | — | CONFORME | a 2,000 mm à frente da face do cabeçote: acesso intencional ao cartucho/termopar, sem caminho para o bolso |
| Furo cartucho X=-22,0 Z=97,0 abre na banda livre | alcance 44,137 mm x r do nariz 39,750 mm -> escancara 4,387 mm | — | — | CONFORME | a 2,000 mm à frente da face do cabeçote: acesso intencional ao cartucho/termopar, sem caminho para o bolso |
| Furo cartucho X=-22,0 Z=97,0 abre na banda livre | alcance 44,137 mm x r do nariz 39,750 mm -> escancara 4,387 mm | — | — | CONFORME | a 2,000 mm à frente da face do cabeçote: acesso intencional ao cartucho/termopar, sem caminho para o bolso |
| Furo cartucho X=22,0 Z=97,0 abre na banda livre | alcance 44,137 mm x r do nariz 39,750 mm -> escancara 4,387 mm | — | — | CONFORME | a 2,000 mm à frente da face do cabeçote: acesso intencional ao cartucho/termopar, sem caminho para o bolso |
| Furo cartucho X=22,0 Z=97,0 abre na banda livre | alcance 44,137 mm x r do nariz 39,750 mm -> escancara 4,387 mm | — | — | CONFORME | a 2,000 mm à frente da face do cabeçote: acesso intencional ao cartucho/termopar, sem caminho para o bolso |
| Furo termopar X=-11,0 Z=103,0 abre na banda livre | alcance 42,373 mm x r do nariz 39,750 mm -> escancara 2,623 mm | — | — | CONFORME | a 8,000 mm à frente da face do cabeçote: acesso intencional ao cartucho/termopar, sem caminho para o bolso |
| Furo termopar X=-11,0 Z=103,0 abre na banda livre | alcance 42,373 mm x r do nariz 39,750 mm -> escancara 2,623 mm | — | — | CONFORME | a 8,000 mm à frente da face do cabeçote: acesso intencional ao cartucho/termopar, sem caminho para o bolso |
| Furo termopar X=11,0 Z=103,0 abre na banda livre | alcance 42,373 mm x r do nariz 39,750 mm -> escancara 2,623 mm | — | — | CONFORME | a 8,000 mm à frente da face do cabeçote: acesso intencional ao cartucho/termopar, sem caminho para o bolso |
| Furo termopar X=11,0 Z=103,0 abre na banda livre | alcance 42,373 mm x r do nariz 39,750 mm -> escancara 2,623 mm | — | — | CONFORME | a 8,000 mm à frente da face do cabeçote: acesso intencional ao cartucho/termopar, sem caminho para o bolso |
| Nenhum furo dentro do cabeçote rompe o envelope | 4 de 4 conformes (os outros 10 abrem na banda livre, à frente do cabeçote) | — | — | CONFORME | nenhum caminho de massa do canal para o bolso nem para a banda de aperto |
| Menor parede de furo até a superfície apertada pela bucha | 0,794 mm  (pino_alinhamento em X=-42,1, Z=30,0) | — | — | CONFORME | é a parede que o collete vê: manter cego, sem rebaixo, e Ø93 retificado na zona de aperto |
| Pressão efetiva no limite | 6,82 MPa = 68,2 bar | — | — | CONFORME | deduzida de 55,7 kN medidos / 8169 mm² de área projetada medida |
| Empuxo axial que empurra a matriz para fora do cabeçote | 29,8 kN no limite · 18,3 kN com o ΔP 1D medido (41,9 bar) | — | — | CONFORME | p × (4489 mm² da boca − 112 mm² da fenda) |
| Área do anel de apoio - matriz (Ø89,5→Ø93) | 501,7 mm² | — | — | CONFORME |  |
| Área do anel de apoio - cabeçote (Ø90→Ø95) | 726,5 mm² | — | — | CONFORME |  |
| Área REAL de contato (interseção das duas faces, booleano) | 431.1836 | 431.1836 | 0.0 | CONFORME | só onde as duas faces existem há pressão: anel Ø90 → Ø93, não o anel inteiro da matriz |
| Pressão de contato no degrau (apoio axial) | 69,2 MPa | — | — | CONFORME | 29,8 kN sobre 431,2 mm² de contato real; margem de 20,2x sobre o escoamento da matriz temperada |
| Pressão radial do collete p/ segurar o empuxo axial só por atrito | 9,8 MPa sobre 20393 mm² | — | — | CONFORME | cenário sem o degrau; com o ombro encostando (folga axial 0,10 mm) não é necessário |
| Pressão radial do collete p/ fechar o plano de partição | 8,6 MPa | — | — | CONFORME | 55,7 kN de força de abertura equilibrados pela compressão radial aplicada pelo collete sobre a banda Ø93 - é isto que fecha a bipartição |
| Pressão radial p/ segurar só o peso na troca | 0,0115 MPa | — | — | CONFORME | matriz de 3,586 kg |
| Cone da bucha × atrito | 3,00° < arctan(0,15) = 8,5° | — | — | CONFORME | auto-travante: a matriz não sai sozinha |
| Deformação radial do canal sob a pressão do collete | ~0,0023 mm por lado | — | — | CONFORME | casca de 8,70 mm sobre o canal, E = 200 GPa - ordem de grandeza |
| Mesmo furo no cenário do desenho (protrusão 14,00 mm) | folga -2,750 mm | 1372,276 mm³ de metal do cabeçote no caminho de cartucho em X=-22,0, Z=97,0 | — | — | PENDENTE_CONFIRMACAO | ou o nariz do cabeçote ganha alívio para passar o cartucho, ou a matriz assenta 6,00 mm mais para fora - que e justamente o que a sua linha de 20,000 mm diz. Em nenhum dos dois casos a furação da matriz muda de lugar. |
| Folga axial da furação de saída à frente do metal do cabeçote | 3.25 | — | — | CONFORME | cenário medido na máquina (protrusão 20,00 mm); furo mais crítico: cartucho em X=-22,0, Z=97,0; metal do cabeçote no caminho de inserção: 0,000 mm³ |
| O que isso decide sobre os furos da matriz | nada se move na matriz nos dois cenários | — | — | CONFORME | a folga traseira mínima medida é 3,250 mm no seu número e -2,750 mm no do desenho; com folga positiva o cartucho entra por fora sem depender de furo no cabeçote |

## O que isso muda no projeto

1. **A matriz cabe no cabeçote.** Os três estágios do corpo (Ø93×69,90 / Ø89,5×10,80 / Ø79,5×28,30) caem nos três furos medidos do cabeçote (Ø95×70,0 / Ø90×11,0 / Ø80×14,0) com folga radial de 1,00 / 0,25 / 0,25 mm e folga axial de 0,10 mm no degrau de apoio. Interferência corpo-a-corpo: zero. A face de saída fica 14,00 mm além da face do nariz, então a fenda trabalha fora do cabeçote.
2. **O anel da face é de 20,00 mm** (Ø90 → Ø130) — exatamente o número descrito. O furo do nariz (Ø80) é maior que a boca da matriz (boca medida 78,000 × 4,500 mm -> 1,00 mm por lado) e menor que a matriz (Ø93): a descrição do cliente confere com o desenho — os 2,50 mm por lado medidos na máquina são do produto (Ø75.00), não da boca chanfrada.
3. **D1 se resolve na máquina, não na matriz — e sem furar nada.** O empuxo axial medido (29,8 kN no limite, 18,3 kN com o ΔP 1D de 41,9 bar) recai em compressão no degrau: 431,2 mm² de contato real a 69,2 MPa, com 20× de margem sobre o escoamento da matriz temperada (medido por booleano: a faixa de contato só existe onde as duas faces existem). A bucha cônica EX-031 (Ø95/Ø90, cone 3°, L 70 = exatamente o comprimento do bolso) é auto-travante (3,00° < 8,5°) e, ao apertar a banda Ø93, aplica compressão radial: 8,58 MPa bastam para equilibrar os 55,7 kN que abrem a bipartição, e 9,76 MPa para segurar o empuxo axial só por atrito — e a deformação do canal com isso é de 0,002 mm por lado (0,15 % da espessura da manta). **Retiro a recomendação de grampos no flange: a matriz não leva flange, nem grampo, nem furo de fixação.** O monobloco por EDM continua sendo a opção mais robusta, mas deixa de ser a única.
3b. **Atenção ao aperto:** 8,6 MPa é pouco, mas o collete é cônico e o montador aperta até encostar. A pressão que fecha o plano de partição é a mesma que prensa a parede de 8,70 mm contra o canal — exigir no desenho de execução o torque/curso de aperto da bucha, senão a banda vira a cunha que abre o canal em vez de fechá-lo.
4. **Bloqueio encontrado — o anel do nariz é de 65 mm.** O corte mostra uma passagem Ø68,30 no nariz (e o carimbo da peça é 9"×65 mm). Com esse anel montado, a matriz de 75 mm **não entra**: 5,60 mm de interferência radial por lado contra o nariz Ø79,5 da matriz. Como o furo do nariz já é Ø80, não há espaço físico para nenhum anel com passagem ≥ Ø79,6 — na variante de 75 mm o nariz tem de ficar aberto (ou o anel ter Ø80, ou seja, não restringir nada), e o centramento passa a ser feito direto no Ø80×14 do cabeçote.
5. **Padrão de furação (P4):** os 6×Ø16,5 em C.C Ø180 dentro de fendas de 23,5 (±7,2°, cotadas como 15°) são a junta cabeçote↔extrusora e passam a 35,25 mm do corpo da matriz. O posicionamento angular da matriz vem dos três centragens cilíndricos, não de pino de flange — não há nada a padronizar na matriz.
6. **Atenção na fabricação:** o furo do pino de alinhamento em X = ±42,10 (Z = 30 e 60) deixa ~0,8 mm de parede até a superfície Ø93 que a bucha aperta. Não rompe o envelope (0 mm³), mas é essa parede que o collete vê: manter o furo cego, sem rebaixo, e o Ø93 retificado na zona de aperto.
