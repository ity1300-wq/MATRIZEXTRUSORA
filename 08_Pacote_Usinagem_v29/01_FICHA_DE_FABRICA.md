# MATRIZ JONATHA v27.0 — ficha de fábrica (peça única)

**MATRIZ JONATHA v27.0 — peça única** · 1 matriz · revisão interna do projeto: v29.0 (sem mudança dimensional)

Aço: Aço para trabalho a quente, classe H11-H13 (EN ISO 4957 / AISI H13). A geometria é a da v27.0 aprovada, entregue num sólido só — o que mudou foi só a eliminação da
junta do plano de partição da v27.0 bipartida.

| o que | valor | de onde vem |
|---|---|---|
| desenho de referência | `08_Pacote_Usinagem_v29/3D/MATRIZ_V29_PECA_UNICA.step` | STEP único: 1 sólido, 22 face(s), 45 aresta(s), 1 casca(s), BRepCheck válido |
| volume de aço | **469.303,2 mm³** | `vol()` no STEP |
| massa usinada | **3,6840 kg** | volume × 7,85 g/cm³ |
| volume do canal (oco) | 213.945,1 mm³ | sólido do canal (`3D/MATRIZ_V29_CANAL_DE_FLUXO.step`) |
| comprimento total | **109,00 mm** | caixa do STEP (Z 0,00 → 109,00) |
| envelope máximo | Ø93,00 em X × 93,00 em Y | caixa do STEP |
| largura da manta (fenda no land) | 75,00 mm (alvo 75,00, tol ±0,05) | seção do **vazio** em Z = 107,00 (2,00 mm antes da saída, depois do chanfro) |
| espessura da manta | 1,5000 mm (alvo 1,50, tol +0,010/−0,000) | idem — é a área 112,0171 mm² que fecha a conta |
| boca de saída (chanfro 1,50 × 45°) | 77,999 × 4,500 mm | seção do vazio a 0,01 mm da face |
| boca de entrada | Ø75,60 mm | maior eixo da seção do vazio em Z = 0,01 (o Ø nominal do contrato é 75,60) |
| junta de partição | **não existe** | a peça é um sólido só — foi o motivo da v29.0 |
| sombra de usinagem no canal | **0,00 %** | 17 faces do canal, raios de 0,10 mm disparados de 0,60 mm para dentro do vazio: 0,0 mm2 de 25.181,8 mm2 sem acesso = 0,00 % |

## As três coisas que a fábrica precisa saber antes de ligar a máquina

1. **Não tem flange, não tem furo de fixação, não tem pino.** A matriz é segurada pelo collete EX-031 e pelo
   degrau do furo do cabeçote. Qualquer furo que a fábrica achar "útil" para segurar a peça **é rejeição** — o
   furo entraria na zona de 69 MPa do degrau. Se precisar de elemento de aperto, faça no **estoque**, antes do
   tratamento térmico, fora do envelope final, e remova na retífica.
2. **A peça não é bipartida, e isso é o produto.** A v27.0 era um par `Body_A` + `Body_B` colado no plano
   Y = 0: 759,5 mm² de contato metal-metal e uma costura de 372,8 mm passando exatamente nas bordas da manta
   (x = ±37,50) — a assinatura da "serra" na borda do produto vinha daí. Aqui a única superfície funcional é a
   do canal usinado, e o teste de visibilidade mede 0,00 % de área sem acesso: o canal inteiro é feito de um
   lado só, sem junta e sem alinhamento a acertar.
3. **Três cotas mandam no resultado:** Ø89,50 e Ø79,50 (elas fecham o anel de 0,25 mm que limita a fuga de
   material para trás) e a abertura da fenda (1,500 +0,010/−0,000). O resto se faz com folga de máquina comum.


## Tolerâncias que valem ouro

| Diâmetro do 2º estágio (Ø89,50 no furo Ø90,00) | 89,500 | 0 / −0,02 | define a folga anular de 0,25 mm que segura a fuga de material para trás |
| Diâmetro do 3º estágio / pescoço (Ø79,50 no furo Ø80,00) | 79,500 | 0 / −0,02 | mesma razão; os dois juntos fecham o anel de 0,25 mm nos dois estágios de product |
| Largura da fenda no land | 74,999 | ±0,05 | largura da manta: 75,00 constantes do contrato |
| Abertura da fenda no land | 1,500 | +0,010 / −0,000 | É A COTA CRÍTICA: ±0,01 mm = ±0,67 % na espessura e na vazão |
| Raio das bordas da fenda (meia-círculo nas pontas) | 0,750 | +0,05 / −0,00 | canto vivo raspa e faz sharkskin; o raio vem de h/2 por contrato |
| Comprimento do land paralelo (Z 98,50 → 107,00) | 8,500 | ±0,05 | o land é o que gera pressão; encurtá-lo é a alavanca real de vazão |
| Boca de entrada do canal (Ø em Z = 0,00) | 75,600 | +0,05 / −0,00 | entrada restrita a Ø75,60 pelo contrato; a caixa da seção em Y dá 0,02 mm a menos porque a lâmina de corte a 0,01 mm da face pega corda, não diâmetro — meça pelo X ou pelo cilindro |
| Dureza após o tratamento | 51,000 | 50-52 HRC | abaixo de 50 o land de 8,50 mm abre com 69 MPa de pressão no degrau |

## Como este pacote foi gerado, e como se re-gera

Toda cota acima é **medida no STEP** por `04_Dados_SSOT_e_Scripts/gerar_pacote_usinagem_v29.py`, usando as
mesmas funções da auditoria de correlações (`abre`, `inventario`, `vazio_da_peca`, seções finas de 0,02 mm). A
seção da fenda é tomada em Z = face de saída − 2,00, ou seja, **depois do chanfro**: medir na face dá a boca
77,999 × 4,500 e não a fenda. Para reproduzir o pacote inteiro depois de mexer no modelo:

    python3 04_Dados_SSOT_e_Scripts/gerar_pacote_usinagem_v29.py

O teste de visibilidade ("sombra") dispara raios de 0,10 mm de um ponto 0,60 mm para dentro do vazio contra as
faces do canal e conta a área onde nenhum raio chega: 0,0 mm² de 25.181,8 mm². É o que prova que o fio e a
fresa alcançam o canal inteiro por uma face só — e por que não se pode abrir janela, furo ou partição nele.
