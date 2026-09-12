# Cabeçote EX-030 em STEP — sem a parte que conecta na extrusora

Os dois sólidos vêm do que foi **medido no DWG 030-032** (`cabecote_ex030.json`) e do mesmo
construtor que o verificador de interface usa, com o booleano abaixo:

``
python 04_Dados_SSOT_e_Scripts/gerar_cabecote_ex030.py        # gera, mede e prova
``

| arquivo | o que é |
| :--- | :--- |
| `06_CAD_Cabecote_EX-030/STEP/Cabecote_EX-030_sem_flange.step` | **o pedido**: corpo Ø130 × 95,000 mm com o nariz Ø80, o degrau Ø90 e o bolso Ø95 × 71,000 mm |
| `06_CAD_Cabecote_EX-030/STEP/Cabecote_EX-030_desenhado.step` | o cabeçote como está no desenho (cubo + flange + resalto), para referência e para a subtração |

## O que foi removido, e como isso foi definido

Remover = intersectar pelo cilindro Ø130 do corpo. A definição não é arbitrária: a junta
cabeçote↔extrusora é exatamente o que está fora do corpo, medido em anéis:

* Ø220 (d 51.00..93.00);
* os 6 furos Ø16,500 em C.C. Ø180,000 ficam a 90,000 mm do eixo, **todos** fora de r = 65,000 mm — o corte leva os seis junto com o flange, sem precisar de furo novo e sem tocar em nenhuma face de centragem.

## O que a medição do sólido prova

* volume 1617704 → 615202 mm³; massa **12,699 → 4,829 kg**, foram **7,870 kg** de aço a menos (62,0 % do volume) — a conta do material e do tempo de usinagem muda de verdade;
* **0,0000 mm³** de metal removido até r = 46,50 mm, que é a banda Ø93 em que a matriz é apertada: o bolso Ø95, o degrau Ø90→Ø95 (a face que reage os 29,8 kN de empuxo) e o nariz Ø80 continuam os do desenho, milímetro por milímetro;
* comprimento axial **95,000 mm**, igual ao do desenho (95,000 mm), e a bounding box ficou Ø130,000 × Ø130,000: corpo redondo, sem nada sobrando da junta;
* na parede do bolso (entre a banda Ø93 e o furo Ø95): 0,000 mm³ removidos pelo corte — o Ø12 do M12, se ele for transversal, abre 1,00 mm além da banda da matriz, na parede onde o collete EX-031 encosta, e não na matriz;
* interferência com `MatrizJonatha_v28.step`: **0,0000 mm³** (no cabeçote com flange: 0,0000 mm³) — a matriz entra, senta no degrau e sai da mesma maneira na variante sem flange.

## O que o corte NÃO resolve (lê antes de mandar usinar)

1. **Sem o flange, a peça não se fixa em lugar nenhum.** Os 6 × M12 eram a única interface mecânica com a extrusora, e é o aperto deles que segura o conjunto contra o empuxo do fundido. Este STEP serve para ver montagem, volume, massa e interface com a matriz. Para fabricar, a junta precisa de substituto (flange de outro diâmetro, grampos no corpo, ou apoio direto na boca da extrusora usando os centragens que já existem).
2. **O M12 transversal ficou fora do modelo.** Medido: par de círculos concêntricos Ø10,500/Ø12,000 com marca de centro sobre o eixo a 72,020 mm da face do nariz (= 20,000 mm da face do flange — é daí que sai o '20' cotado, e é por isso que aquele '20' não é a protrusão da matriz). No arquivo que chegou ele não tem aresta de seção correspondente em parte nenhuma, então a natureza exata (furo roscado transversal, abrindo na banda onde o collete aperta, ou furo coaxial no fundo do bolso para o pushador EX-032) não é determinável. Modelar `--com-m12` abre o Ø12 atravessando as duas paredes no ângulo que você especifar (padrão 90°) para você ver o cenário — e nada neste STEP depende dele.
3. Nada aqui mexe na matriz: `MatrizJonatha.step` continua o v27.0 aprovado e a v28.1 continua proposta (decisão D4).

*Gerado por `gerar_cabecote_ex030.py`; medições em `04_Dados_SSOT_e_Scripts/cabecote_step.json`.*
