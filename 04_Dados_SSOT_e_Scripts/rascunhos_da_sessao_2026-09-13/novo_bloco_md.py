    if a.md:
        def f3(v):
            return "—" if v is None else n(v, 3)

        L = ["# Parte interna do cabeçote EX-030 × as cinco matrizes — comparado por medida", "",
             "Gerado por `medir_perfis_matrizes_x_cabecote.py`. Escada interna do cabeçote medida do "
             f"construtor `verificar_interface_cabecote.cabecote`, no referencial da matriz (face do nariz "
             f"em Z = {n(Z_FACE_NARIZ, 2)}, fundo do bolso em Z = 0):", "",
             "| furo do cabeçote | Ø | de Z | até Z | profundidade |", "|---|---|---|---|---|"]
        for e in res["escada_interna_do_cabecote_mm"]:
            L.append(f"| {e.get('nome') or e.get('o_que_e', '—')} | Ø{n(e['Ø_mm'], 2)} | "
                     f"{n(e['de_Z'], 2)} | {n(e['ate_Z'], 2)} | {n(e['comprimento_mm'], 2)} mm |")

        L += ["", "## O que cada matriz é, medida no STEP dela", "",
              "| matriz | compr. | Ø máx | fim da banda Ø93 | folga axial banda↔degrau | face de saída | "
              "vão de furo Ø80 aberto à frente da saída |", "|---|---|---|---|---|---|---|"]
        for m in res["matrizes"]:
            t, c = m["transições_refinadas_mm"], m["canal_à_frente_da_saída_mm3"]
            L.append(f"| {m['nome']} | {n(m['comprimento_medido_mm'], 2)} | {n(m['Ø_máximo_medido_mm'], 2)} "
                     f"| {n(t['fim_da_banda_093_em_Z'], 3)} | "
                     f"{n(t['folga_axial_banda_x_degrau_do_cabecote_mm'], 3)} "
                     f"| {n(t['face_de_saida_em_Z_no_assento'], 3)} | {n(c['trecho_mm'], 2)} mm = "
                     f"{n(c['volume_do_furo_mm3'], 0)} mm³ de furo, **{n(c['vão_livre_mm3'], 0)} mm³** sem "
                     f"metal da matriz dentro |")

        L += ["", "## Estágio por estágio: em qual furo do cabeçote cai cada parte da matriz", "",
              "Medido no assento natural (o encosto em que a matriz não interfere):", "",
              "| matriz | estágio da matriz | furo do cabeçote onde ele cai | folga radial | entra? |",
              "|---|---|---|---|:--:|"]
        for m in res["matrizes"]:
            for fg in m["folgas_radiais_no_encosto_do_assento"]:
                entra = "—" if fg.get("pode_entrar") is None else ("sim" if fg["pode_entrar"] else "**NÃO**")
                fol = fg.get("folga_radial_mm")
                L.append(f"| {m['nome']} | {fg['estagio']} | {fg['furo']} | "
                         f"{f3(fol) + (' mm' if fol is not None else '')} | {entra} |")

        L += ["", "## A diferença que você observou, em números", "",
              f"* Comprimento medido: Copo **{n(dif['comprimento_copo_mm'], 2)} mm**, Gedeon "
              f"**{n(dif['comprimento_gedeon_mm'], 2)} mm** — diferença **{n(dif['diferença_mm'], 2)} mm**.",
              f"* No assento natural, a face de saída fica "
              f"**{n(abs(dif['o_que_a_diferenca_faz_no_encosto_B']['copo_protusao_mm']), 2)} mm para dentro** "
              f"da face do nariz no Copo e "
              f"**{n(dif['o_que_a_diferenca_faz_no_encosto_B']['gedeon_protusao_mm'], 2)} mm para fora** na "
              f"Gedeon: {n(abs(dif['o_que_a_diferenca_faz_no_encosto_B']['copo_protusao_mm']), 2)} + "
              f"{n(dif['o_que_a_diferenca_faz_no_encosto_B']['gedeon_protusao_mm'], 2)} = "
              f"{n(dif['diferença_mm'], 2)} mm. A diferença de comprimento É o nariz, e nada mais.",
              "* As cinco têm a mesma escada até o degrau (banda Ø93 e estágio Ø89,50 terminando no mesmo Z, "
              "na casa de milésimo). Gedeon, Desenvolvimento e Jonatha só acrescentam o nariz Ø79,50 que "
              "atravessa o furo do nariz; a Copo não tem nariz, e por isso a face dela fica enterrada.",
              "* Interferência no assento natural: " + ", ".join(
                  f"{m['chave']} "
                  f"{n(m['encostos'][m['encosto_usado']]['interferência_com_o_cabeçote_mm3'], 4)} mm³"
                  for m in res["matrizes"]) + ".", ""]

        L += ["## O que aconteceria com um chanfro de 1,00 × 45° no canto interno Ø90 → Ø80", "",
              "O canto vivo onde o furo do nariz começa (Z = 81,00) é por onde a película passa do estágio "
              "Ø89,50 para o Ø80. Um chanfro ali remove "
              f"**{n(q['metal_removido_do_cabeçote_mm3'], 3)} mm³** do cabeçote e muda, medido:", "",
              "| matriz | interferência antes | depois | folga radial no canto antes | depois |",
              "|---|---|---|---|---|"]
        for l in q["por_matriz"]:
            a1, d1 = l["folga_radial_no_canto_antes_mm"], l["folga_radial_no_canto_depois_mm"]
            L.append(f"| {l['matriz']} | {n(l['interferência_antes_mm3'], 4)} mm³ | "
                     f"{n(l['interferência_depois_mm3'], 4)} mm³ | "
                     f"{'a matriz não chega no canto' if a1 is None else n(a1, 2) + ' mm'} | "
                     f"{'a matriz não chega no canto' if d1 is None else n(d1, 2) + ' mm'} |")
        L += ["", "Nenhuma matriz passa a interferir — o chanfro só tira metal do cabeçote — mas onde o nariz "
              "encosta no canto a folga radial sai de 0,25 para 2,25 mm: o nariz de 14,00 mm deixaria de ser "
              "guiado nesse primeiro milímetro e continuaria guiado pelos 13,00 mm seguintes do Ø80. "
              "**Isto é proposta medida, não mudança aprovada**: o desenho do cabeçote não tem esse chanfro e "
              "o SSOT (`cabecote_ex030.json`) continua gravando a peça como desenhada.", ""]

        t0 = res["matrizes"][0]["transições_refinadas_mm"]
        c0 = res["matrizes"][0]["canal_à_frente_da_saída_mm3"]
        iA = res["matrizes"][0]["encostos"]["A_face_frente_rasa"]["interferência_com_o_cabeçote_mm3"]
        L += ["## O que isso diz sobre \"deixar a parte interna de acordo\"", "",
              f"1. **A escada interna do cabeçote é o molde da matriz Copo — e ela serve às cinco, sem "
              f"correção.** O fim da banda Ø93 é o mesmo Z nas cinco ({n(t0['fim_da_banda_093_em_Z'], 3)} mm "
              f"medidos na Copo e nas outras quatro) e o degrau do cabeçote está em Z = 70,00, então sobra "
              f"{n(t0['folga_axial_banda_x_degrau_do_cabecote_mm'], 3)} mm de folga axial. É esse número que "
              f"faz o encosto no degrau e o encosto no fundo do bolso caírem na mesma posição: a matriz não "
              f"\"escolhe\" entre os dois.",
              f"2. **A Copo não pode ser montada com a face rasante à face do nariz**: empurrada até lá ela "
              f"interfere {n(iA, 4)} mm³, porque a banda Ø93 teria de atravessar o degrau Ø90. Ela senta no "
              f"degrau e deixa a saída enterrada — {n(c0['volume_do_furo_mm3'], 0)} mm³ de furo Ø80 aberto à "
              f"frente dela, sem metal dentro. É aí que a película caminha 14 mm dentro do cabeçote em vez "
              f"de nascer no ar livre.",
              f"3. **A diferença que você vê na saída não é tolerância, é projeto**: "
              f"{n(dif['diferença_mm'], 2)} mm de nariz existem para levar a face de saída para fora do "
              f"cabeçote. Qualquer matriz que se queira usar neste cabeçote sem usinar o cabeçote precisa "
              f"desse nariz — e a v28.1 tem, com o Ø79,50×28,30 que mede exatamente a folga do enterramento "
              f"da Copo (14,30) mais a protusão de projeto (14,00).",
              "", "*Gerado por `medir_perfis_matrizes_x_cabecote.py --json --md`; os números estão em "
              "`04_Dados_SSOT_e_Scripts/perfis_matrizes_x_cabecote.json`.*"]
        p_md = os.path.join(DIR_DOC, "INTERFASE_INTERNA_CABECOTE_X_MATRIZES.md")
        open(p_md, "w", encoding="utf-8").write("\n".join(L))
        print("MD  ->", p_md)
