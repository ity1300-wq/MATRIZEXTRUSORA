import ast

P = "04_Dados_SSOT_e_Scripts/gerar_cabecote_ex030.py"
s = open(P, encoding="utf-8").read()

# ---------------------------------------------------------------- 1) montagens: sem booleano na entrega
ini = s.index("    # ------------------------------------------------- montagens: cabecote + matriz sentada")
fim = s.index("    if not a.sem_relatorio:")
novo = '''    # ------------------------------------------------- montagens: cabecote + matriz sentada, num STEP so
    # Composto de N solidos no MESMO referencial axial (Z = 0 no plano mais traseiro), SEM booleano nenhum na
    # entrega. Isso e deliberado e custou uma correcao: a primeira versao entregava a matriz como A U B, que e
    # valido (BRepCheck: True) e e o que a MEDICAO precisa, mas fecha cascas internas - a uniao da Gedeon tem 3
    # shells contra as 2 do Body_A e as 2 do Body_B - e solido com casca interna abre como "pecas
    # quebradas/corrompidas" em visualizador de STEP. Num arquivo de montagem, a biparticao e o dado: as metades
    # vao la separadas, iguais ao que o arquivo de origem tem.
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
                # cada solido de origem, no lugar em que a medicao o poe (dz = encosto escolhido no medidor)
                pedacos = []
                for pt in paths:
                    v = cq.importers.importStep(pt).val()
                    for so in (v.Solids() or [v]):
                        pedacos.append(so)
                dz = e["encostos"][e["encosto_usado"]]["deslocamento_aplicado_mm"]
                if abs(dz) > 1e-9:
                    pedacos = [x.translate(cq.Vector(0.0, 0.0, dz)) for x in pedacos]
                comp = cq.Workplane("XY").newObject([cq.Compound.makeCompound([cheio] + pedacos)])
                pm = os.path.join(a.saida, f"Cabecote_EX-030_com_{curto}{sufixo}.step")
                cq.exporters.export(comp, pm, cq.exporters.ExportTypes.STEP)
                relido = cq.importers.importStep(pm).val()
                vs = [x.Volume() for x in relido.Solids()] or [vol(relido)]
                saida = e["comprimento_medido_mm"] + dz
                # a interferencia e medida peca a peca e somada (mesmo numero do booleano sobre a uniao, porque
                # as metades se tocam no plano de particao e nao se sobrepoe - medido: A U B = A + B ao bitola)
                interf_c = sum(vol(x.intersect(cheio)) for x in pedacos)
                interf_n = sum(vol(x.intersect(novo)) for x in pedacos)
                shells_cab = len(cheio.Shells())
                med["montagens"][chave] = {
                    "arquivo": os.path.relpath(pm, RAIZ),
                    "entrega_sem_booleano": True,
                    "arquivos_da_matriz": [os.path.relpath(x, RAIZ) for x in paths],
                    "solidos_da_matriz_no_arquivo": len(pedacos),
                    "encosto_usado": e["encosto_usado"], "deslocamento_aplicado_mm": round(dz, 3),
                    "solidos_no_arquivo": len(relido.Solids()),
                    "volume_somado_mm3": round(sum(vs), 3),
                    "desvio_round_trip_mm3": round(sum(vs) - (cheio.Volume() + sum(x.Volume() for x in pedacos)), 6),
                    "interferencia_matriz_x_desenhado_mm3": round(interf_c, 4),
                    "interferencia_matriz_x_sem_flange_mm3": round(interf_n, 4),
                    "face_de_saida_da_matriz_em_Z": round(saida, 3),
                    "protusao_adem_da_face_do_nariz_mm": round(saida - Z_FACE_NARIZ, 3),
                    "massa_somada_kg": round((cheio.Volume() + sum(x.Volume() for x in pedacos)) * ACO, 4),
                }
                m = med["montagens"][chave]
                print(f"MONTAGEM {curto:13s} -> {m['arquivo']} | {m['solidos_no_arquivo']} solidos "
                      f"(1 cabecote + {m['solidos_da_matriz_no_arquivo']} da matriz, sem booleano) | "
                      f"interferencia somada {n(m['interferencia_matriz_x_desenhado_mm3'], 4)} mm3 | "
                      f"saida da matriz em Z = {n(m['face_de_saida_da_matriz_em_Z'], 2)} "
                      f"(protrusao {n(m['protusao_adem_da_face_do_nariz_mm'], 2)} mm)")
                if m["solidos_no_arquivo"] != 1 + m["solidos_da_matriz_no_arquivo"]:
                    falhas_m = ("montagem %s nao reimporta com o numero de solidos esperado (%d vs %d)"
                                % (chave, m["solidos_no_arquivo"], 1 + m["solidos_da_matriz_no_arquivo"]))
                    print("FALHOU:", falhas_m)
                if abs(m["desvio_round_trip_mm3"]) > 1e-3:
                    falhas_m = "montagem %s nao reimporta com volume fiel" % chave
                    print("FALHOU:", falhas_m)
                json.dump(med, open(cam_json, "w", encoding="utf-8"), indent=1)
    else:
        print("aviso: falta perfis_matrizes_x_cabecote.json - montagens nao geradas "
              "(rode medir_perfis_matrizes_x_cabecote.py --json)")

    # ------------------------------------------- inventario medido dos arquivos de matriz (o "corrompida")
    # Medido, nao opinado: quantos solidos ha em cada arquivo de origem, se cada um e valido e o que ele e. E
    # isto que responde "a Gedeon parece corrompida" sem pedir a ninguem que confie em mim.
    inv = {}
    for rot, caminho in (("MatrizGedeon.step (inteira)", os.path.join(DIR_HIS, "MatrizGedeon.step")),
                         ("MatrizGedeon_Body_A.step", os.path.join(DIR_HIS, "MatrizGedeon_Body_A.step")),
                         ("MatrizGedeon_Body_B.step", os.path.join(DIR_HIS, "MatrizGedeon_Body_B.step")),
                         ("MatrizGedeon_Canal_Fluxo.step", os.path.join(DIR_HIS, "MatrizGedeon_Canal_Fluxo.step")),
                         ("Matriz1_Original_Copo_Solido.step", os.path.join(DIR_HIS, "Matriz1_Original_Copo_Solido.step")),
                         ("MatrizJonatha.step (master v27)", os.path.join(DIR_OFF, "MatrizJonatha.step"))):
        if not os.path.exists(caminho):
            continue
        v = cq.importers.importStep(caminho).val()
        ss = v.Solids() or [v]
        inv[rot] = {
            "solidos": len(v.Solids()) or 1,
            "validos_por_solido": [bool(BRepCheck_Analyzer(x.wrapped).IsValid()) for x in ss],
            "shells_por_solido": [len(x.Shells()) for x in ss],
            "volume_mm3": round(sum(x.Volume() for x in ss), 1),
            "volumes_por_solido_mm3": [round(x.Volume(), 1) for x in ss],
        }
    med["inventario_dos_arquivos_de_matriz"] = inv
    print("inventario medido dos arquivos de origem:")
    for k, v in inv.items():
        print(f"   {k:36s} {v['solidos']} solido(s) | vol {v['volume_mm3']:11.1f} mm3 | "
              f"validos {all(v['validos_por_solido'])} | shells {v['shells_por_solido']}")

'''
s = s[:ini] + novo + s[fim:]

# import do BRepCheck
ant = "import cadquery as cq\n"
nvo = ("import cadquery as cq\n"
       "from OCP.BRepCheck import BRepCheck_Analyzer  # e isto que diz se um solido abre 'corrompido' no CAD\n")
assert s.count(ant) == 1, "import BRepCheck"
s = s.replace(ant, nvo, 1)
open(P, "w", encoding="utf-8").write(s)
ast.parse(s)
print("gerador do cabecote: montagem sem booleano + inventario medido dos arquivos")
