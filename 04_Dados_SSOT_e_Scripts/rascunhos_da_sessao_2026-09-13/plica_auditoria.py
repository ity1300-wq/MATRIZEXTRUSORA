import ast
import json

# ================================================== 1) SSOT: resposta item a item ao processo de auditoria
P = "04_Dados_SSOT_e_Scripts/cad_die_parameters.json"
d = json.load(open(P, encoding="utf-8"))
d["audit"]["tratamento_auditoria_v28_1"] = {
    "data": "2026-09-12",
    "para_quem_e": ("a auditoria automatizada (PR #1 / issue #1) abriu 8 achados contra a v27.0. Isto é o "
                    "relato do que foi feito com cada um, com o número medido hoje e onde o número é re-medido "
                    "a cada rodada do portão (`python 04_Dados_SSOT_e_Scripts/verificar_cadeia.py`)."),
    "regra_que_limita_o_tratamento": ("nenhum achado foi 'resolvido' editando o master: `01_CAD_MatrizJonatha_Oficial/MatrizJonatha.step` "
                                      "(v27.0) e `02_CAD_Modelos_Historicos/` são intocados (regras 1 e 2 do projeto), e a v28.1 "
                                      "existe em paralelo aguardando sua aprovação explícita para promover"),
    "achados": {
        "G-01 land reto e paralelo 8,50 vs 10,00 declarado": {
            "status": "RESOLVIDO NO SSOT (modelo mantido)",
            "tratamento": ("o SSOT passou a declarar os dois números separados: `land_length_mm` = 10,00 mm de "
                           "terra total e `land_paralelo_real_mm` / `land_paralelo_mm` = 8,50 mm, com a causa "
                           "escrita (`land_paralelo_observacao`). A cota de usinagem saiu da discussão de "
                           "texto: paralelo Z = 99,00 → 107,50 (8,50) e chanfro 1,50 × 45° de Z = 107,50 → "
                           "109,00, conferidos item a item no sólido por `verificar_v28.py`."),
            "numero_medido_hoje": "land paralelo medido 8,50 mm (conforme o SSOT novo)",
            "onde_confere": "04_Dados_SSOT_e_Scripts/verificacao_v28.json (itens 'Land reto e paralelo' e "
                            "'Cotas de usinagem do land')",
        },
        "G-02 lâmina do lábio de saída 0,75 mm": {
            "status": "MANTIDO POR DECISÃO EXPLÍCITA DO USUÁRIO (D2)",
            "tratamento": ("as duas variantes foram modeladas e comparadas com números, não com opinião: "
                           "reduzir o chanfro para 0,80 × 45° daria land 9,20 e lâmina 1,40 mm "
                           "(`proposta_v28_dfm/o_que_mudou/P7_P8_chanfro_e_land`). O usuário manteve o chanfro "
                           "do master (1,50 × 45°, lâmina 0,75). O achado não é mais 'risco não tratado': virou "
                           "instrução de fabricação - `fabricao_v28/tolerancias/chanfro_saida` e "
                           "`/lamina_labio` exigem 1,50 × 45° (±0,05) **sem rebarba** e registram que o "
                           "lascamento na limpeza é o preço aceito."),
            "numero_medido_hoje": "lâmina medida 0,750 mm; sobrelargura do chanfro a 0,10 mm da face 1,402 mm",
            "onde_confere": "04_Dados_SSOT_e_Scripts/verificacao_v28.json (itens 'Lâmina de aço no lábio' e "
                            "'Sobrelargura do chanfro')",
        },
        "G-03 furos de pino selados no Body_A e ausentes no Body_B": {
            "status": "RESOLVIDO NA PROPOSTA v28.1",
            "tratamento": ("os pinos passaram a atravessar as duas metades, como na Gedeon: 4 bolsões em cada "
                           "lado (X = ±42,10; Z = 30,00 e 60,00), abertos no plano de partição e cegos sob o "
                           "fundo. Medido em booleano por pino: bolso vazio 0,0000 mm³, aço sob o fundo 12,6 "
                           "mm³ nas duas metades, parede mínima até o canal 2,391 / 2,392 / 2,482 / 2,483 mm "
                           "(alvo ≥ 2,00) e interseção com o canal 0,000000 mm³ - nenhum furo comunica com o "
                           "fluxo."),
            "numero_medido_hoje": "pinos conjugados 4/4 no Body_A e 4/4 no Body_B",
            "onde_confere": "04_Dados_SSOT_e_Scripts/verificacao_v28.json (itens 'Pino em ...' e 'Pinos "
                            "conjugados nas duas metades')",
        },
        "G-04 zero recursos de fabricação (fixação, cartuchos, termopar, refrigeração, flange de entrada)": {
            "status": "PARCIAL POR DECISÃO: o que é do cabeçote saiu medido; refrigeração continua aberta",
            "tratamento": ("(a) fixação: a matriz **não** leva flange nem furo de fixação - decisão explícita do "
                           "usuário; ela é presa pelo collete EX-031 e apoiada no degrau do cabeçote, e as "
                           "pressões necessárias foram medidas: empuxo axial 29,843 kN, pressão de contato no "
                           "degrau 69,21 MPa sobre 632,7 mm², pressão radial do collete 8,58 MPa para fechar o "
                           "plano de partição (força de abertura 55,7 kN) e 9,76 MPa para segurar o empuxo só "
                           "por atrito. (b) cartuchos e termopar: a furação é do cabeçote EX-030, não da matriz "
                           "- 6 furos de cartucho e 4 de termopar conferidos um a um, todos abrindo na banda "
                           "livre e nenhum rompendo o envelope. (c) o preço disso é o acesso axial, que é o "
                           "único NÃO CONFORME do projeto: folga -2,750 mm, metal no caminho 2.744,550 mm³, o "
                           "cartucho deixa de esbarrar em Z ≥ 99,75 mm. (d) refrigeração Ø8 por metade: "
                           "continuamos sem definição - é a única linha do G-04 que não foi tratada."),
            "numero_medido_hoje": "52 itens de interface | 43 conformes | 1 NC | 8 pendências de máquina",
            "onde_confere": "04_Dados_SSOT_e_Scripts/interface_cabecote.json e "
                            "03_Relatorios_e_Documentacao/INTERFASE_CABECOTE_EX030.md",
        },
        "G-05 MatrizJonatha_Canal_Fluxo.step com 3 sólidos": {
            "status": "RESOLVIDO NA PROPOSTA v28.1",
            "tratamento": ("reexportado como eletrodo/de CFD: `MatrizJonatha_v28_Canal_Fluxo.step` tem 1 sólido "
                           "só (213.945,1 mm³, medido reimportando o arquivo). O v27.0 continua com os 3 "
                           "sólidos (canal + 2 furos de pino de 150,8 mm³) porque é o master intocado - a "
                           "regra 1 não permite 'corrigir' o arquivo aprovado por dentro."),
            "numero_medido_hoje": "1 sólido no STEP do canal da v28.1",
            "onde_confere": "04_Dados_SSOT_e_Scripts/auditoria_geometrica.json (itens 'Sólidos em ...') + "
                            "contagem reimportando o STEP",
        },
        "G-06 sem espaço para fixação axial; M8 só radial nas asas": {
            "status": "CONFIRMADO MEDIDO, E NAO LIGA MAIS O PROCESSO",
            "tratamento": ("a parede entre o canal e o Ø93 foi conferida: (93,00 − 75,60)/2 = 8,70 mm de aço "
                           "radial, e por isso não há parafuso axial possível - exatamente o que a auditoria "
                           "disse. Com a fixação por collete + degrau (decisão do usuário), nenhum furo radial "
                           "M8 com spot face precisa ser aberto na matriz; os únicos furos que existem nela são "
                           "os pinos, com 2,39 mm de parede até o canal. O que a auditoria previa como risco "
                           "('as metades não podem ser fechadas contra a contrapressão') foi tratado pelo outro "
                           "lado: o fechamento é feito pelo collete, medido em 8,58 MPa."),
            "numero_medido_hoje": "parede radial do canal até o Ø93 = 8,70 mm",
            "onde_confere": "04_Dados_SSOT_e_Scripts/interface_cabecote.json (blocos [D] e [E])",
        },
        "ação 6 do plano: sem furação de flange em Z = 0": {
            "status": "RESOLVIDO COM O DWG DO CABEÇOTE",
            "tratamento": ("o padrão veio do `030-032- cabeçote.dwg` medido, não de palpite: 6 furos Ø16,50 "
                           "(M12) dentro de 6 fendas de 23,5 mm no C.C. Ø180,00, na face do flange, mais o "
                           "piloto de centragem Ø105,00 × 3,00 mm na traseira. A matriz não precisa de flange "
                           "próprio porque ela é presa pelo cabeçote. Consequência nova da decisão 'encosta face "
                           "a face': a face da extrusora precisa de 3,00 mm de rebaixo em Ø > 105,00."),
            "numero_medido_hoje": "piloto protrai 3,00 mm atrás da face do flange (medido no sólido)",
            "onde_confere": "04_Dados_SSOT_e_Scripts/cabecote_ex030.json e item [G] de "
                            "04_Dados_SSOT_e_Scripts/verificar_interface_cabecote.py",
        },
        "ação 8 do plano: ΔP e τ declarados não reproduzíveis": {
            "status": "RESOLVIDO EM SCRIPT VERSIONADO",
            "tratamento": ("os números passaram a ser saída de script, e o portão os compara com os documentos. "
                           "Refeitos: τ na parede do land = 163,8 kPa (γ̇_ap = 911 s⁻¹) e ΔP 1D = 41,9 bar para "
                           "a v28.1 (68,2 bar na v27.0), com a observação de que τ não depende do comprimento do "
                           "land - é a mesma fenda, a mesma vazão, o que é justamente o que derrubava o "
                           "'128,44 kPa' do relatório antigo. A triagem dos problemas declarados está em "
                           "`TRIAGEM_DE_PROBLEMAS_DAS_MATRIZES.md`."),
            "numero_medido_hoje": "τ = 163,8 kPa",
            "onde_confere": "04_Dados_SSOT_e_Scripts/verificacao_v28.json ('τ na parede do land') e "
                            "interface_cabecote.json ('numeros/dp_1d_bar')",
        },
    },
    "o_que_continua_aberto": [
        "G-04 (d): canais de refrigeração Ø8 por metade - sem definição, sem modelo, sem número.",
        "Acesso axial dos cartuchos no cabeçote EX-030: NC -2,750 mm; sai com o nariz em Z ≥ 99,75 mm "
        "(recomendado 100,25 mm, com +0,500 de folga) - é decisão sua, não minha.",
        "Superfície de aperto do collete EX-031 (o furo Ø90,00 reto que medimos no DXF não desce sobre a banda "
        "Ø93: faltam 1,50 mm de raio). A pressão de fechamento é condicional a isso.",
        "Promover ou não a v28.1: a v27.0 continua sendo o master aprovado até você dizer.",
        "Medições que só o paquímetro resolve: Ø90 do furo do collete, D3 do funil, M12 na face.",
    ],
}
json.dump(d, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("1) SSOT: audit.tratamento_auditoria_v28_1 com os 8 achados respondidos")

# ============================== 2) o relatorio da auditoria passa a renderizar o tratamento (gerado)
P = "04_Dados_SSOT_e_Scripts/verify_geometry_ssot.py"
s = open(P, encoding="utf-8").read()
ant = '    destino = os.path.join(DIR_DOC, "AUDITORIA_GEOMETRICA_MATRIZ_JONATHA.md")'
nvo = '''    # ------------------------------------------------------------------ 6. o que foi feito de cada achado
    # Nao e texto solto: a tabela e lida de `cad_die_parameters.json:audit.tratamento_auditoria_v28_1`, entao
    # o relatorio da auditoria e o SSOT nao podem divergir (o portao confere o numero de tau citado aqui).
    try:  # lido do disco de novo: nao dependo do escopo de quem montou as checagens
        _ssot = json.load(open(os.path.join(DIR_DADOS, "cad_die_parameters.json"), encoding="utf-8"))
        _tr = _ssot["audit"]["tratamento_auditoria_v28_1"]
        _tau = _ssot.get("proposta_v28_dfm", {}).get("numeros recalculados", {}).get("tau_parede_land_kPa")
    except (OSError, KeyError):
        _tr, _tau = {}, None
    if _tr:
        linhas += ["", f"## 6. Tratamento dos achados na proposta v28.1 ({_tr['data']})", "",
                   _tr["para_quem_e"], "", "> " + _tr["regra_que_limita_o_tratamento"], "",
                   "| Achado | Status | Tratamento, com o número medido | Onde conferir |",
                   "| :--- | :--- | :--- | :--- |"]
        for _k, _v in _tr["achados"].items():
            linhas.append(f"| **{_k}** | {_v['status']} | {_v['tratamento']} "
                          f"(medido hoje: {_v['numero_medido_hoje']}) | {_v['onde_confere']} |")
        linhas += ["", "### O que continua aberto", ""]
        linhas += [f"* {x}" for x in _tr["o_que_continua_aberto"]]
        if _tau is not None:
            linhas += ["", f"τ citado acima: **{_tau:.1f} kPa** - o mesmo número que está em "
                           f"`verificacao_v28.json`; se um mudar sem o outro, o portão fecha.", ""]

''' + ant
assert s.count(ant) == 1, "destino do MD"
s = s.replace(ant, nvo, 1)
open(P, "w", encoding="utf-8").write(s)
ast.parse(s)
print("2) verify_geometry_ssot.py renderiza a secao 6 a partir do SSOT")

# ================================================ 3) o portao passa a conferir o numero citado na auditoria
P = "04_Dados_SSOT_e_Scripts/verificar_cadeia.py"
s = open(P, encoding="utf-8").read()
ant = '''                  ("INTERFASE_INTERNA_CABECOTE_X_MATRIZES.md", "diferença_copo_x_gedeon_medida/diferença_mm", 2,
                   "perfis_matrizes_x_cabecote.json"),'''
nvo = '''                  ("AUDITORIA_GEOMETRICA_MATRIZ_JONATHA.md",
                   "proposta_v28_dfm/numeros recalculados/tau_parede_land_kPa", 1, "cad_die_parameters.json"),
''' + ant
assert s.count(ant) == 1, "PARES"
s = s.replace(ant, nvo, 1)
open(P, "w", encoding="utf-8").write(s)
ast.parse(s)
print("3) portao confere o tau citado no relatorio da auditoria contra o SSOT")
