# Pacote de usinagem — MATRIZ JONATHA v27.0 · rev. 30 (2026-09-22)

Gerado por `04_Dados_SSOT_e_Scripts/gerar_pacote_usinagem_v30.py` a partir do STEP medido. Se o STEP mudar, o
pacote muda junto; nada aqui foi digitado de memória.

| arquivo | o que é |
|---|---|
| `01_FICHA_DE_FABRICA.md` | o que é a peça, cotas principais medidas, interface com o EX-030 |
| `02_MATERIAL_E_TRATAMENTO.md` | **1045** + indução/nitretação na fenda, com as consequências na cota de 1,500 |
| `03_SEQUENCIA_DE_USINAGEM.md` | 13 operações, do corte da barra à marcação a laser |
| `04_TOLERANCIAS_E_INSPECAO.md` | tabela de cotas (com ±0,5 nas alteradas) e plano de inspeção |
| `05_O_QUE_O_STEP_NAO_DIZ.md` | datum, polimento, REC, embalagem, o que mudou nesta revisão |
| `06_PEDIDO_DE_COTACAO_RFQ.md` | texto pronto para mandar |
| `07_EMAIL_DE_PRIMEIRO_CONTATO.md` | **capa, não vai no zip**: guarda o sha256 do zip |
| `PRANCHA_2D_TOLERANCIADA.pdf` / `.png` | 4 vistas cotadas, geradas das seções medidas no STEP |
| `3D/` | `MATRIZ_V30_PECA_UNICA.step` (a peça), `MATRIZ_V30_CANAL_DE_FLUXO.step` (o sólido do canal, para o EDM), `Cabecote_EX-030_com_Matriz_Jonatha_v30.step` (no cabeçote) |
| `pacote_usinagem.json` | os números medidos, máquina-legível |
| `CHECKSUMS_SHA256.txt` | sha256 de tudo que vai no zip |
| `PACOTE_MATRIZ_V30_PARA_ENVIO.zip` | o pacote fechado para envio |

Conferir: `cd 08_Pacote_Usinagem_v30 && sha256sum -c CHECKSUMS_SHA256.txt`
