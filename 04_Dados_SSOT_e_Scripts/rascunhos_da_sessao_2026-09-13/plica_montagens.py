import ast

P = "04_Dados_SSOT_e_Scripts/gerar_cabecote_ex030.py"
s = open(P, encoding="utf-8").read()

# ---------------------------------------------------------------- constantes e importacoes
ant = 'DIR_ESTUDO = os.path.join(DIR_CAB, "estudos")\n'
nvo = ('DIR_ESTUDO = os.path.join(DIR_CAB, "estudos")\n'
       'DIR_HIS = os.path.join(RAIZ, "02_CAD_Modelos_Historicos")   # lido, nunca escrito (regra 2)\n'
       'DIR_OFF = os.path.join(RAIZ, "01_CAD_MatrizJonatha_Oficial")\n'
       'PERFIS = os.path.join(AQUI, "perfis_matrizes_x_cabecote.json")\n'
       '# as montagens que o usuario pediu: o cabecote com a matriz original e com a Gedeon sentadas\n'
       'MONTAGENS = [("matriz_1_copo", "Matriz_Copo"), ("matriz_2_gedeon", "Matriz_Gedeon")]\n')
assert s.count(ant) == 1, "DIR_ESTUDO"
s = s.replace(ant, nvo)

ant = "from verificar_v28 import ENVELOPE  # noqa: E402"
nvo = "from verificar_v28 import ENVELOPE, maior  # noqa: E402"
assert s.count(ant) == 1, "import maior"
s = s.replace(ant, nvo)

# ---------------------------------------------------------------- bloco das montagens
ant = "    if not a.sem_relatorio:\n        escreve_relatorio(med, p1, p2)\n"
nvo = '''    # ------------------------------------------------- montagens: cabecote + matriz sentada, num STEP so
    # Composto de 2 solidos no MESMO referencial axial (Z = 0 no plano mais traseiro da pecas), SEM booleano:
    # e assim que o CAD mede folga e interferencia, e assim que o arquivo continua valido como montagem. As
    # matrizes sao lidas de 02_/01_ sem modificar (regra 2), unidas A U B quando a peca e bipartida - o mesmo
    # corpo que `medir_perfis_matrizes_x_cabecote.py` mede, para o STEP entregue e a medicao nao divergirem.
    med["montagens"] = {}
    falhas_m = ""
    if os.path.exists(PERFIS):
        pf = json.load(open(PERFIS, encoding="utf-8"))
        for chave, curto in MONTAGENS:
            e = next((x for x in pf["matrizes"] if x["chave"] == chave), None)
            if e is None:
                falhas_m = "chave %s ausente em perfis_matrizes_x_cabecote.json" % chave
                print("FALHOU:", falhas_m)
                continue
            paths = []
            for nome in e["arquivos_lidos"]:
                pt = next((os.path.join(d, nome) for d in (DIR_HIS, DIR_OFF)
                           if os.path.exists(os.path.join(d, nome))), None)
                if pt is None:
                    falhas_m = "nao acho o STEP da matriz %s" % nome
                    print("FALHOU:", falhas_m)
                    break
                paths.append(pt)
            else:
                wp = cq.importers.importStep(paths[0])
                for pt in paths[1:]:
                    wp = wp.union(cq.importers.importStep(pt))
                corpo = maior(wp.val())
                dz = e["encostos"][e["encosto_usado"]]["deslocamento_aplicado_mm"]
                if abs(dz) > 1e-9:
                    corpo = corpo.translate(cq.Vector(0.0, 0.0, dz))
                comp = cq.Workplane("XY").newObject([cq.Compound.makeCompound([cheio, corpo])])
                pm = os.path.join(a.saida, f"Cabecote_EX-030_com_{curto}{sufixo}.step")
                cq.exporters.export(comp, pm, cq.exporters.ExportTypes.STEP)
                relido = cq.importers.importStep(pm).val()
                vs = [x.Volume() for x in relido.Solids()] or [vol(relido)]
                saida = e["comprimento_medido_mm"] + dz
                med["montagens"][chave] = {
                    "arquivo": os.path.relpath(pm, RAIZ),
                    "arquivos_da_matriz": [os.path.relpath(x, RAIZ) for x in paths],
                    "encosto_usado": e["encosto_usado"], "deslocamento_aplicado_mm": round(dz, 3),
                    "solidos_no_arquivo": len(relido.Solids()),
                    "volume_somado_mm3": round(sum(vs), 3),
                    "desvio_round_trip_mm3": round(sum(vs) - (cheio.Volume() + corpo.Volume()), 6),
                    "interferencia_matriz_x_desenhado_mm3": round(vol(corpo.intersect(cheio)), 4),
                    "interferencia_matriz_x_sem_flange_mm3": round(vol(corpo.intersect(novo)), 4),
                    "face_de_saida_da_matriz_em_Z": round(saida, 3),
                    "protusao_adem_da_face_do_nariz_mm": round(saida - Z_FACE_NARIZ, 3),
                    "massa_somada_kg": round((cheio.Volume() + corpo.Volume()) * ACO, 4),
                }
                m = med["montagens"][chave]
                print(f"MONTAGEM {curto:13s} -> {os.path.relpath(pm, RAIZ)} | {m['solidos_no_arquivo']} solidos"
                      f" | interferencia com o cabecote {n(m['interferencia_matriz_x_desenhado_mm3'], 4)} mm3"
                      f" | saida da matriz em Z = {n(m['face_de_saida_da_matriz_em_Z'], 2)}"
                      f" (protrusao {n(m['protusao_adem_da_face_do_nariz_mm'], 2)} mm)")
                if m["solidos_no_arquivo"] != 2 or abs(m["desvio_round_trip_mm3"]) > 1e-3:
                    falhas_m = ("montagem %s nao reimporta como 2 solidos de volume fiel (solidos %d, desvio "
                                "%s mm3)" % (chave, m["solidos_no_arquivo"], m["desvio_round_trip_mm3"]))
                    print("FALHOU:", falhas_m)
                json.dump(med, open(cam_json, "w", encoding="utf-8"), indent=1)
    else:
        print("aviso: falta perfis_matrizes_x_cabecote.json - montagens nao geradas "
              "(rode medir_perfis_matrizes_x_cabecote.py --json)")

''' + ant
assert s.count(ant) == 1, "antes do relatorio"
s = s.replace(ant, nvo, 1)

open(P, "w", encoding="utf-8").write(s)
ast.parse(s)
print("montagens entraram no gerador do STEP")
