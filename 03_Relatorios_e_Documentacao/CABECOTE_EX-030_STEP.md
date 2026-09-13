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

## O cabeçote com cada matriz sentada (montagens entregues)

Dois arquivos compostos, no mesmo referencial axial (Z = 0 no plano mais traseiro), **sem booleano
nenhum**: cada sólido é o que está no arquivo de origem, no lugar onde a medição o põe.** A montagem da
Copo tem 2 sólidos (ela é de corpo único) e a da Gedeon tem 3 (cabeçote + Body_A + Body_B). Isso foi
corrigido depois da primeira versão, que entregava a matriz unida (A ∪ B): a união é válida e é com
ela que a folga é medida, mas ela conserva as cavidades internas seladas dos sólidos de origem - e
sólido com casca interna é o que abre como "peça quebrada" na maioria dos visualizadores de STEP.
Medido hoje, nos arquivos tais como estão no repositório: `MatrizGedeon_Body_A.step` é **1 sólido com
3 cascas** (duas cavidades fechadas dentro dele), o `Body_B` tem 1, e a união fica com 3. Numa
montagem, a bipartição é o dado, não um detalhe a esconder: as metades vão separadas. As duas se
tocam no plano de partição e não se sobrepõem (A ∪ B = 469.156,8 mm³ contra A + B = 469.156,7 mm³),
então somar a interferência peça a peça dá o mesmo número que o booleano sobre a união.

O `[3, 1]` do `MatrizJonatha.step` (v27, master) é a mesma moléstia, e é o G-03 da auditoria: bolsões de
pino selados num corpo e ausentes no outro. A v28.1 é o remédio proposto - 4 bolsões abertos no plano
de partição e cegos sob o fundo nos DOIS corpos, com parede mínima medida de 2,391 a 2,483 mm até o
canal e 0,000000 mm³ de comunicação com o fluxo.
partição e não se sobrepõem (medido: A ∪ B = 469.156,8 mm³ contra A + B = 469.156,7 mm³), então somar a
interferência peça a peça dá o mesmo número que o booleano sobre a união.

As matrizes são lidas de `02_CAD_Modelos_Historicos/` / `01_CAD_MatrizJonatha_Oficial/` **sem
modificar** (regra 2). A medição da folga usa A ∪ B — o mesmo corpo que
`medir_perfis_matrizes_x_cabecote.py` mede, para o STEP entregue e a medição não divergirem;
a entrega usa as metades separadas, como explicado acima.

| montagem | sólidos no arquivo | encosto usado | interferência com o cabeçote | saída em Z | protrusão |
| :--- | ---: | :--- | ---: | ---: | ---: |
| `Cabecote_EX-030_com_Matriz_Copo.step` | 2 (1 + 1) | `B_ombro_no_degrau` (0,00 mm) | **0,0000 mm³** | 80,70 | -14,30 mm |
| `Cabecote_EX-030_com_Matriz_Gedeon.step` | 3 (1 + 2) | `B_ombro_no_degrau` (0,00 mm) | **0,0000 mm³** | 109,00 | 14,00 mm |
| `Cabecote_EX-030_com_Matriz_Gedeon_Certa.step` | 2 (1 + 1) | `B_ombro_no_degrau` (0,00 mm) | **0,0000 mm³** | 109,00 | 14,00 mm |
| `Cabecote_EX-030_com_Matriz_Desenvolvimento.step` | 3 (1 + 2) | `B_ombro_no_degrau` (0,00 mm) | **0,0000 mm³** | 109,00 | 14,00 mm |
| `Cabecote_EX-030_com_Matriz_Jonatha_v27.step` | 3 (1 + 2) | `B_ombro_no_degrau` (0,00 mm) | **0,0000 mm³** | 109,00 | 14,00 mm |
| `Cabecote_EX-030_com_Matriz_Jonatha_v28_1.step` | 3 (1 + 2) | `B_ombro_no_degrau` (0,00 mm) | **0,0000 mm³** | 109,00 | 14,00 mm |

### O que cada arquivo de matriz realmente contém (medido, não narrado)

Isto existe porque a pergunta 'a Gedeon está corrompida?' só se responde abrindo os arquivos. Nenhum
deles é inválido — o que corrompe a leitura é *quantos* sólidos tem cada um e o que eles são:

| arquivo | sólidos | volume total | sólidos válidos | cascas por sólido |
| :--- | ---: | ---: | :--- | :--- |
| `MatrizGedeon.step (inteira)` | 5 | 683,248.4 mm³ | [True, True, True, True, True] | [1, 1, 1, 1, 1] |
| `MatrizGedeon_Body_A.step` | 1 | 234,332.8 mm³ | [True] | [3] |
| `MatrizGedeon_Body_B.step` | 1 | 234,823.9 mm³ | [True] | [1] |
| `MatrizGedeon_Canal_Fluxo.step` | 1 | 213,790.0 mm³ | [True] | [1] |
| `Matriz1_Original_Copo_Solido.step` | 1 | 224,289.0 mm³ | [True] | [1] |
| `MatrizJonatha.step (master v27)` | 2 | 469,001.7 mm³ | [True, True] | [3, 1] |

`MatrizGedeon.step` (a inteira) são **5 sólidos**: as duas metades **sem o canal escavado**
(320.090,4 mm³ cada), o sólido do canal de plástico (43.017,9 mm³, boca Ø75,60, Z 0..109) e dois pinos
de 24,9 mm³. Aberto num visualizador, isso é corpo + corpo dentro do corpo + vazio virando sólido dentro
dos dois — daí o aspecto de arquivo quebrado. Os STEP que o projeto usa são os outros:
`MatrizGedeon_Body_A.step` e `_Body_B.step`, as metades **com** o canal escavado (234.332,8 + 234.823,9
= 469.156,7 mm³, e a união dá 469.156,8: elas se tocam, não se sobrepõem).

E o achado velho, re-confirmado por medida: `MatrizGedeon_Canal_Fluxo.step` tem **213.790,0 mm³** contra
os **43.017,9 mm³** do sólido de canal que está dentro de `MatrizGedeon.step` — o arquivo do canal da
Gedeon não é o canal da Gedeon (é a P5 da triagem; é por isso que toda comparação desta tacada usa as
metades, nunca esse arquivo).

### A fenda não está no cabeçote — e o 'copo' que se vê é o bolso dele

`Cabecote_EX-030_sem_flange.step` tem **1 sólido, 1 casca, 11 faces, 610.588,2 mm³** (medido
reimportando o arquivo): não há matriz nenhuma ali dentro. A fenda 75,00 × 1,50 vive na matriz, não no
cabeçote. O que se vê por dentro é a escada de furos do próprio cabeçote — Ø80 (nariz, 14,02) → Ø90
(degrau, 11,00) → Ø95 × 70,00 (o bolso onde a banda da matriz entra) — que é exatamente o copo da matriz
em negativo, e é isso que faz a matriz passar pelo nariz sem tocar a fenda.

### Por que a Gedeon montada parece a Jonatha

Porque são gêmeas de envelope: Gedeon (A ∪ B) 469.156,8 mm³, Jonatha v27 469.001,7 mm³ (0,03 % de
diferença) e Jonatha v28.1 456.796,5 mm³, com a caixa externa idêntica (±46,50 × Z 0..109,00). O que as
separa é interno - funil, canal e bolsões de pino - e não aparece na silhueta lateral. É também por isso
que a exigência do projeto é 'envelope externo idêntico': é o que faz as duas entrarem no mesmo cabeçote.

| `06_CAD_Cabecote_EX-030/STEP/Cabecote_EX-030_com_Matriz_Copo.step` | `B_ombro_no_degrau` (0,00 mm) | **0,0000 mm³** | 80,70 | -14,30 mm |
| `06_CAD_Cabecote_EX-030/STEP/Cabecote_EX-030_com_Matriz_Gedeon.step` | `B_ombro_no_degrau` (0,00 mm) | **0,0000 mm³** | 109,00 | 14,00 mm |
| `06_CAD_Cabecote_EX-030/STEP/Cabecote_EX-030_com_Matriz_Gedeon_Certa.step` | `B_ombro_no_degrau` (0,00 mm) | **0,0000 mm³** | 109,00 | 14,00 mm |
| `06_CAD_Cabecote_EX-030/STEP/Cabecote_EX-030_com_Matriz_Desenvolvimento.step` | `B_ombro_no_degrau` (0,00 mm) | **0,0000 mm³** | 109,00 | 14,00 mm |
| `06_CAD_Cabecote_EX-030/STEP/Cabecote_EX-030_com_Matriz_Jonatha_v27.step` | `B_ombro_no_degrau` (0,00 mm) | **0,0000 mm³** | 109,00 | 14,00 mm |
| `06_CAD_Cabecote_EX-030/STEP/Cabecote_EX-030_com_Matriz_Jonatha_v28_1.step` | `B_ombro_no_degrau` (0,00 mm) | **0,0000 mm³** | 109,00 | 14,00 mm |

A diferença de sinal entre as duas linhas é o ponto que o usuário observou na máquina: a Copo termina
**14,30 mm antes** da face do nariz (falta o nariz de 28,30 mm que a Gedeon tem), e a Gedeon desemboca
fora dele. Os dois valores são comprimentos medidos nos STEP das próprias peças: 80,70, 109,00, 109,00, 109,00, 109,00, 109,00 mm.

## O que foi removido, e como isso foi definido

Remover = intersectar pelo cilindro Ø130 do corpo. A definição não é arbitrária: a junta
cabeçote↔extrusora é exatamente o que está fora do corpo, medido em anéis:

* Ø220 (d 52.00..92.00);
* os 6 furos Ø16,500 em C.C. Ø180,000 ficam a 90,000 mm do eixo, **todos** fora de r = 65,000 mm — o corte leva os seis junto com o flange, sem precisar de furo novo e sem tocar em nenhuma face de centragem.

## O que a medição do sólido prova

* volume 1570339 → 610588 mm³; massa **12,327 → 4,793 kg**, foram **7,534 kg** de aço a menos (61,1 % do volume) — a conta do material e do tempo de usinagem muda de verdade;
* **0,0000 mm³** de metal removido até r = 46,50 mm, que é a banda Ø93 em que a matriz é apertada: o bolso Ø95, o degrau Ø90→Ø95 (a face que reage os 29,8 kN de empuxo) e o nariz Ø80 continuam os do desenho, milímetro por milímetro;
* comprimento axial **95,000 mm**, igual ao do desenho (95,000 mm), e a bounding box ficou Ø130,000 × Ø130,000: corpo redondo, sem nada sobrando da junta;
* na parede do bolso (entre a banda Ø93 e o furo Ø95): 0,000 mm³ removidos pelo corte — o Ø12 do M12, se ele for transversal, abre 1,00 mm além da banda da matriz, na parede onde o collete EX-031 encosta, e não na matriz;
* interferência com `MatrizJonatha_v28.step`: **0,0000 mm³** (no cabeçote com flange: 0,0000 mm³) — a matriz entra, senta no degrau e sai da mesma maneira na variante sem flange.

## O que o corte NÃO resolve (lê antes de mandar usinar)

1. **Sem o flange, a peça não se fixa em lugar nenhum.** Os 6 × M12 eram a única interface mecânica com a extrusora, e é o aperto deles que segura o conjunto contra o empuxo do fundido. Este STEP serve para ver montagem, volume, massa e interface com a matriz. Para fabricar, a junta precisa de substituto (flange de outro diâmetro, grampos no corpo, ou apoio direto na boca da extrusora usando os centragens que já existem).
2. **O M12 transversal ficou fora do modelo.** Medido: par de círculos concêntricos Ø10,500/Ø12,000 com marca de centro sobre o eixo a 72,020 mm da face do nariz (= 20,000 mm da face do flange — é daí que sai o '20' cotado, e é por isso que aquele '20' não é a protrusão da matriz). No arquivo que chegou ele não tem aresta de seção correspondente em parte nenhuma, então a natureza exata (furo roscado transversal, abrindo na banda onde o collete aperta, ou furo coaxial no fundo do bolso para o pushador EX-032) não é determinável. Modelar `--com-m12` abre o Ø12 atravessando as duas paredes no ângulo que você especifar (padrão 90°) para você ver o cenário — e nada neste STEP depende dele.
3. Nada aqui mexe na matriz: `MatrizJonatha.step` continua o v27.0 aprovado e a v28.1 continua proposta (decisão D4).

*Gerado por `gerar_cabecote_ex030.py`; medições em `04_Dados_SSOT_e_Scripts/cabecote_step.json`.*
