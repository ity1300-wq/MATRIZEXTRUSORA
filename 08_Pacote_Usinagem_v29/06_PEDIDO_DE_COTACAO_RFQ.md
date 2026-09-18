# RFQ — MATRIZ JONATHA v29.0, peça única, em 1.2344 temperado

> Copiar e enviar. Os anexos estão nesta pasta; nada aqui depende de conversa posterior.

**Peça**: matriz de extrusão plana, sólido único (sem bipartição, sem furo de fixação, sem flange).
**Quantidade para cotação**: 1 peça piloto + 4 peças de série (lote único), com a piloto aprovada antes do resto.
**Prazo pedido**: piloto em 15 dias úteis; série em +10.

**Arquivos enviados**
| arquivo | o que é | sha256 (16 primeiros) |
|---|---|---|
| `3D/MATRIZ_V29_PECA_UNICA.step` | o sólido único, geometria de referência | ffa6cc4baa6496c4... |
| `3D/MATRIZ_V29_CANAL_DE_FLUXO.step` | o sólido do canal (a ferramenta de medição e de verificação do volume) | 922073408b1b3a50... |
| `3D/CONJUNTO_MATRIZ_V29_NO_CABECOTE_EX-030.step` | a matriz montada no cabeçote EX-030, para o senhor ver onde ela encosta | 70658e978cccf9cc... |
| `PRANCHA_2D_TOLERANCIADA.pdf` | desenho cotado com as tolerâncias e as notas | — |
| `02_MATERIAL_E_TRATAMENTO.md` | qualidade, dureza, alívio de tensões, o que não usar | — |
| `03_SEQUENCIA_DE_USINAGEM.md` | sequência proposta (aceitamos sugestão da fábrica, sem ferir as notas) | — |
| `04_TOLERANCIAS_E_INSPECAO.md` | tabela de tolerâncias e o plano de inspeção | — |

**Condições de aceite (resumo)**
1. material 1.2344 forjado, fibra no eixo, ESR se houver; certificado EN 10204 3.1;
2. dureza 50-52 HRC após têmpera a vácuo e 2 revénios, com relatório;
3. fenda 1.5000 +0,010/−0,000 mm medida no plano Z = face de saída − 2,00, largura 75.00 ±0,05;
4. Ø89,50 e Ø79,50 em 0/−0,02, coaxialidade Ø0,02 em A = Ø93,00;
5. área da seção do canal no land = 112.0171 mm² ±0,5 % (rejeição se passar);
6. Ra ≤ 0,4 µm no canal, camada REC do EDM removida, sem trinca (LP se aplicável);
7. **nenhum furo, rosca ou rebaixo adicionado**; qualquer elemento de aperto feito no estoque e removido;
8. dossiê de primeiro artigo com todos os itens acima assinado e datado, junto da peça.

**O que não entra no preço nem no prazo**: ajuste de cota da fenda depois do tratamento térmico (a peça é
refugada e refeita), revestimento, e retrabalho que altere o volume do canal.

*Documento gerado automaticamente por `04_Dados_SSOT_e_Scripts/gerar_pacote_usinagem_v29.py` — os shas e as
cotas acima são lidos dos arquivos desta pasta, não digitados.*
