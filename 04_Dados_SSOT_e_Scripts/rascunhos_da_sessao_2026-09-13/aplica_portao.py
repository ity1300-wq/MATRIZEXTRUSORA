import ast

# ---------------------------------------------------- 1) decimals pt-BR na tabela de folgas por estagio
P = "04_Dados_SSOT_e_Scripts/medir_perfis_matrizes_x_cabecote.py"
s = open(P, encoding="utf-8").read()
ant = """        out.append({"estagio": f"Ø{d:.2f} em Z {z0:.2f}..{z1:.2f}",
                    "furo": f"Ø{f['Ø_mm']:.2f} (Z {f['de_Z']:.2f}..{f['ate_Z']:.2f})",
                    "folga_radial_mm": round((f["Ø_mm"] - d) / 2.0, 3),
                    "pode_entrar": bool(f["Ø_mm"] >= d - 1e-9)})"""
nvo = """        out.append({"estagio": f"Ø{n(d, 2)} em Z {n(z0, 2)}..{n(z1, 2)}",
                    "furo": f"Ø{n(f['Ø_mm'], 2)} (Z {n(f['de_Z'], 2)}..{n(f['ate_Z'], 2)})",
                    "folga_radial_mm": round((f["Ø_mm"] - d) / 2.0, 3),
                    "pode_entrar": bool(f["Ø_mm"] >= d - 1e-9)})"""
assert s.count(ant) == 1, "folgas_por_estagio"
s = s.replace(ant, nvo)
ant = '''            out.append({"estagio": f"Ø{d:.2f} em Z {z0:.2f}..{z1:.2f}",
                        "furo": "fora do cabecote (protende ou fica no vao traseiro)", "folga_radial_mm": None})'''
nvo = """            out.append({"estagio": f"Ø{n(d, 2)} em Z {n(z0, 2)}..{n(z1, 2)}",
                        "furo": "fora do cabeçote (protende além da face, ou fica no vão traseiro)",
                        "folga_radial_mm": None})"""
assert s.count(ant) == 1, "ramo fora-do-cabecote"
s = s.replace(ant, nvo)
open(P, "w", encoding="utf-8").write(s)
ast.parse(s)
print("1) decimal pt-BR na tabela de estagios")

# ------------------------------------------------- 2) portao da cadeia: roda o medidor e cobra seus numeros
P = "04_Dados_SSOT_e_Scripts/verificar_cadeia.py"
s = open(P, encoding="utf-8").read()
ant = '''                  "medir_perfil_cabecote.py --json 04_Dados_SSOT_e_Scripts/cabecote_perfil.json"]'''
nvo = '''                  "medir_perfil_cabecote.py --json 04_Dados_SSOT_e_Scripts/cabecote_perfil.json",
                  "medir_perfis_matrizes_x_cabecote.py --json --md"]'''
assert s.count(ant) == 1, "CADEIA_ESTUDOS"
s = s.replace(ant, nvo)

ant = '''PARES_DOC_JSON = [("INTERFASE_CABECOTE_EX030.md", "numeros/acesso_furacao_cenarios/desenho DXF medido/metal_no_caminho_mm3", 3),
                  ("INTERFASE_CABECOTE_EX030.md", "numeros/cartuchos_z_min_mm", 2),
                  ("INTERFASE_CABECOTE_EX030.md", "numeros/area_contato_degrau_mm2", 1),
                  ("PROJETO_DFM_V28_MATRIZ_JONATHA.md", "numeros/dp_1d_bar", 1)]'''
nvo = '''# o 4o elemento opcional e o nome do JSON de onde o numero vem (padrao: interface_cabecote.json)
PARES_DOC_JSON = [("INTERFASE_CABECOTE_EX030.md", "numeros/acesso_furacao_cenarios/desenho DXF medido/metal_no_caminho_mm3", 3),
                  ("INTERFASE_CABECOTE_EX030.md", "numeros/cartuchos_z_min_mm", 2),
                  ("INTERFASE_CABECOTE_EX030.md", "numeros/area_contato_degrau_mm2", 1),
                  ("PROJETO_DFM_V28_MATRIZ_JONATHA.md", "numeros/dp_1d_bar", 1),
                  ("INTERFASE_INTERNA_CABECOTE_X_MATRIZES.md", "diferença_copo_x_gedeon_medida/diferença_mm", 2,
                   "perfis_matrizes_x_cabecote.json"),
                  ("INTERFASE_INTERNA_CABECOTE_X_MATRIZES.md",
                   "o_que_um_chanfro_interno_muda/metal_removido_do_cabeçote_mm3", 3,
                   "perfis_matrizes_x_cabecote.json")]'''
assert s.count(ant) == 1, "PARES_DOC_JSON"
s = s.replace(ant, nvo)

ant = '''    for arq, chave, casas in PARES_DOC_JSON:
        if arq not in doc:
            no(f"{arq} não existe")
            continue
        valor = fmt(pega(i, chave), casas)'''
nvo = '''    cache_json = {"interface_cabecote.json": i}
    for par in PARES_DOC_JSON:
        arq, chave, casas = par[0], par[1], par[2]
        nome_json = par[3] if len(par) > 3 else "interface_cabecote.json"
        if arq not in doc:
            no(f"{arq} não existe")
            continue
        if nome_json not in cache_json:
            cache_json[nome_json] = json.load(open(os.path.join(AQUI, nome_json), encoding="utf-8"))
        valor = fmt(pega(cache_json[nome_json], chave), casas)'''
assert s.count(ant) == 1, "laco [5]"
s = s.replace(ant, nvo)
open(P, "w", encoding="utf-8").write(s)
ast.parse(s)
print("2) portao: medidor na cadeia de estudos + 2 pares doc<->json novos")

# --------------------------------------------------- 3) README raiz e o mapa de arquivos do AUTO_PROMPT
P = "README.md"
s = open(P, encoding="utf-8").read()
ant = "### 🔧 Cabeçote em STEP (peça da máquina, não da matriz)"
nvo = """### 📐 Parte interna do cabeçote × as cinco matrizes (comparado por medida)

`03_Relatorios_e_Documentacao/INTERFASE_INTERNA_CABECOTE_X_MATRIZES.md`, gerado por
`04_Dados_SSOT_e_Scripts/medir_perfis_matrizes_x_cabecote.py`, mede a escada de cada matriz nos STEP
dela (Copo original, Gedeon, Desenvolvimento, Jonatha v27.0, v28.1) e o posiciona no cabeçote pelos três
encostos possíveis, com interferência medida por booleano. Resultado central, medido hoje: as cinco têm o
fim da banda Ø93 no **mesmo Z** e a mesma folga axial no degrau; a Copo não tem nariz e por isso fica com a
face de saída **enterrada**, enquanto Gedeon/Desenvolvimento/Jonatha protrudem — a diferença de comprimento
é exatamente o nariz, somada aos dois deslocamentos de face. O relatório traz também o que-if do chanfro no
canto interno Ø90 → Ø80, medido contra as cinco, como proposta (não é mudança aprovada no desenho).

### 🔧 Cabeçote em STEP (peça da máquina, não da matriz)"""
assert s.count(ant) == 1, "README"
open(P, "w", encoding="utf-8").write(s.replace(ant, nvo))

P = "04_Dados_SSOT_e_Scripts/generate_auto_prompt.py"
s = open(P, encoding="utf-8").read()
ant = """- `06_CAD_Cabecote_EX-030/STEP/` — os desenhos STEP do **cabeçote**: o sem a junta da extrusora (corpo"""
nvo = """- `04_Dados_SSOT_e_Scripts/medir_perfis_matrizes_x_cabecote.py` →
  `03_Relatorios_e_Documentacao/INTERFASE_INTERNA_CABECOTE_X_MATRIZES.md` — mede a escada das cinco
  matrizes nos STEP delas e o encaixe no cabeçote pelos três encostos, com interferência por booleano e o
  que-if do chanfro interno. Roda no `--com-estudos` do portão; dados em
  `04_Dados_SSOT_e_Scripts/perfis_matrizes_x_cabecote.json`
- `06_CAD_Cabecote_EX-030/STEP/` — os desenhos STEP do **cabeçote**: o sem a junta da extrusora (corpo"""
assert s.count(ant) == 1, "auto_prompt"
s = s.replace(ant, nvo)
open(P, "w", encoding="utf-8").write(s)
ast.parse(s)
print("3) README raiz e mapa de arquivos do AUTO_PROMPT atualizados")
