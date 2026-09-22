# Pacote de usinagem — MATRIZ JONATHA v29.0 (peça única)

Pasta pronta para enviar ao fornecedor. **Toda cota aqui é medida no STEP** por
`04_Dados_SSOT_e_Scripts/gerar_pacote_usinagem_v29.py`; re-gerar é um comando.

| arquivo | para quem | o que é |
|---|---|---|
| `01_FICHA_DE_FABRICA.md` | chão de fábrica | o resumo de uma página, com as três cotas que valem ouro |
| `02_MATERIAL_E_TRATAMENTO.md` | compras / metalurgia | qualidade, dureza, alívio de tensões, o que não usar, estoque |
| `03_SEQUENCIA_DE_USINAGEM.md` | programação | 12 operações, com as armadilhas que já aconteceram no projeto |
| `04_TOLERANCIAS_E_INSPECAO.md` | qualidade | tabela de 22 cotas com tolerância e método, 11 linhas de inspeção, critério de rejeição |
| `05_O_QUE_O_STEP_NAO_DIZ.md` | todos | as 10 linhas que evitam a primeira peça errada |
| `06_PEDIDO_DE_COTACAO_RFQ.md` | fornecedor | o pedido de cotação pronto para copiar e enviar (1 matriz) |
| `07_EMAIL_DE_PRIMEIRO_CONTATO.md` | você | a carta de capa do e-mail ao fornecedor — fica fora do zip |
| `PRANCHA_2D_TOLERANCIADA.pdf` / `.png` | todos | 4 vistas cotadas, geradas das seções medidas no STEP (o PNG é só para abrir rápido) |
| `3D/` | CAM | o STEP da peça, o do canal (ferramenta de medição) e a montagem no cabeçote |
| `pacote_usinagem.json` | projeto | os números e as cotas em máquina-legível |
| `CHECKSUMS_SHA256.txt` | recebimento | o que a fábrica deve conferir no arquivo que ela baixar |

## O que mudou em relação à v27.0, em uma frase

As duas metades (`Body_A` + `Body_B`, 759,5 mm² de contato e uma costura de 372,8 mm passando nas bordas da
manta) viraram **um sólido**: 469.303,2 mm³ de aço (3.6840 kg), 213.945,1 mm³ de canal (**idêntico ao master**), 22 faces,
1 casca, BRepCheck limpo, e 0,00 % de sombra no canal — ou seja, nada se perde e a junta do plano de partição
acaba.

## Como conferir o pacote antes de enviar

    cd /home/user/MATRIZEXTRUSORA
    sha256sum -c 08_Pacote_Usinagem_v29/CHECKSUMS_SHA256.txt
    python3 04_Dados_SSOT_e_Scripts/verificar_cadeia.py --rapido       # o portao do repo
    python3 04_Dados_SSOT_e_Scripts/auditar_step_correlacoes.py         # as correlacoes C1..C7

O zip para envio: `PACOTE_MATRIZ_V29_PARA_ENVIO.zip` — os 12 arquivos do pacote, sem o e-mail de capa
(que é do remetente, não material de fábrica). O sha256 do zip está anotado em
`07_EMAIL_DE_PRIMEIRO_CONTATO.md`, fora do arquivo que ele哈希 — um arquivo não pode carregar o próprio hash.

`CHECKSUMS_SHA256.txt` cobre exatamente os arquivos que vão no zip, então `sha256sum -c` funciona nos dois
lados: na pasta do repo e na pasta que o fornecedor extraiu.
