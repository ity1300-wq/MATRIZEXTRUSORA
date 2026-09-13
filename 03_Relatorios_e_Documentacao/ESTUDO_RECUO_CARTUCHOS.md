# Estudo: recuar os cartuchos para Z ≥ 99,75 mm (alternativa (a) da pendência [F])

Geometria construída pelo `construir()` real do `gerar_matriz_v28.py` (mesmo caminho que
gera os STEP oficiais) variando só o plano `Z` dos cartuchos. Medidas por `BRepExtrema` e
booleanos; o cabeçote é o sólido medido no DWG. **Nenhum arquivo oficial foi tocado.**

| cenário | Z (mm) | mín. furo→canal | abre na externa | borda→face de saída | web entre furos | rompe o canal | sai do envelope | bloqueio no cabeçote | folga traseira | massa |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| v28.1 como está | 97,00 | 8,196 | 0,000 | 7,250 | 5,380 | 0,0000 mm³ | 0,0000 mm³ | 2744,6 mm³ | -2,750 | 3,586 kg |
| mínimo que passa | 99,75 | 8,196 | 0,000 | 4,500 | 4,320 | 0,0000 mm³ | 0,0000 mm³ | 0,0 mm³ | 0,000 | 3,582 kg |
| com folga de bancada | 100,25 | 8,196 | 0,000 | 4,000 | 4,189 | 0,0000 mm³ | 0,0000 mm³ | 0,0 mm³ | 0,500 | 3,582 kg |

## Leitura

* o cenário **mínimo que passa** (Z = 99,75 mm) zera o bloqueio: 0,0 mm³ contra 2744,6 mm³ do plano atual, e a folga traseira vai de -2,750 mm para 0,000 mm;
* custo em aço: parede mínima cartucho→canal 8,196 → 8,196 mm (alvo do projeto ≥ 4,00), web entre furos 5,380 → 4,320 mm, massa -0,0040 kg;
* o lábio **não muda**: land 8,50 mm, chanfro 1,50 × 45° e volume do canal idêntico ao do cenário atual (sim) — portanto o ΔP 1D medido na geometria (41,9 bar) e o τ na parede (163,8 kPa) continuam os mesmos;
* nenhum furo sai do envelope (0,0000 mm³) e nenhum rompe o canal (0,0000 mm³);
* o plano 'com folga de bancada' (Z = 100,25 mm) dá 0,500 mm de folga em vez de 0,000 — e é o que eu recomendaria, porque 0,000 mm é contato exato entre dois sólidos de tolerância não nula.

## O que este estudo NÃO decide

1. Ele resolve só o acesso do **cartucho**. A furação dos termopares (Z = 103,00) já estava livre e não muda de lado, mas a web entre cartucho e termopar encolhe (5,380 → 4,189 mm no plano com folga) — conferir se isso é aceitável para o fabricante;
2. a escolha entre recuar os furos da matriz **ou** abrir alívio no nariz do cabeçote depende da protrusão real medida na máquina e da decisão sobre mexer ou não no cabeçote cementado;
3. a superfície de aperto do collete EX-031 continua em aberto (furo medido Ø90,00 reto não passa sobre a banda Ø93) — nada aqui depende dela, e nada aqui a resolve.

*Gerado por `estudar_recuo_cartuchos.py`; números em `04_Dados_SSOT_e_Scripts/recuo_cartuchos.json`.*
