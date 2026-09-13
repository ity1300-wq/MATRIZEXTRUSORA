    med["1 cabecote sem matriz"] = faixa(
        axs[0], cab,
        "1   CABEÇOTE EX-030 SEM MATRIZ — a fenda não está aqui; o «copo» que se vê é o bolso dele",
        "seção medida no STEP `Cabecote_EX-030_sem_flange.step` (1 sólido, 1 casca, 11 faces, 610.588,2 mm³, "
        "reimportado e conferido): não há matriz alguma neste arquivo.\nO cabeçote só fura em escada Ø80 "
        "(nariz) → Ø90 (degrau) → Ø95 × 70,00 (o bolso). É essa escada que, em corte, parece o copo da matriz "
        "— é o copo em negativo, e é o que faz a matriz passar pelo nariz sem tocar a fenda.")

    med["2 Gedeon entregue"] = faixa(
        axs[1], entregue,
        "2   GEDEON COMO ENTREGUE (02_/Body_A ∪ Body_B) — 1 sólido com 3 CASCA: bolso de pino selado",
        "seção medida das duas metades de `02_CAD_Modelos_Historicos/`, abertas SÓ PARA LEITURA (regra 2) e "
        "unidas para o corte: A ∪ B = %s mm³ de aço, caixa Ø93,00 × Z 0..109,00.\nO retângulo pontilhado é a "
        "zona do pino Ø1,78: no `Body_A` é CASCA INTERNA — cavidade selada dentro do aço, o que abre como "
        "«peça corrompida» no CAD e não tem ferramenta — e no `Body_B` não há bolso nenhum."
        % n(gc["entrega_anterior_refutada"]["volume_aco_entrega_anterior_mm3"], 1))
    cx = pin["caixas_mm"]
    for c in cx:
        axs[1].add_patch(plt.Rectangle((c["x"][0] - 1.6, c["z"][0] - 1.6), c["x"][1] - c["x"][0] + 3.2,
                                       c["z"][1] - c["z"][0] + 3.2, fill=False, ec="tab:red", lw=1.2,
                                       ls=(0, (3, 2))))
        axs[1].plot([c["x"][1] + 1.6, 62.0], [0.5 * (c["z"][0] + c["z"][1])] * 2, color="tab:red", lw=0.5,
                    ls=(0, (2, 2)))
    axs[1].text(-70.0, 126.0, "Z %s → %s, a |x| %s mm: no `Body_A` o bolso é CASCA INTERNA (selada no aço); "
                "no `Body_B` não existe. E esta peça tem %s mm³ de aço contra os %s mm³ do arquivo certo"
                % (n(cx[0]["z"][0], 2), n(cx[0]["z"][1], 2), n(abs(cx[0]["x"][1]), 2),
                   n(gc["entrega_anterior_refutada"]["volume_aco_entrega_anterior_mm3"], 1),
                   n(gc["entrega_anterior_refutada"]["volume_aco_certa_mm3"], 1)),
                fontsize=7.0, color="tab:red", ha="left", va="top")
    med["2 Gedeon entregue"]["pinos_marcados"] = cx
    med["2 Gedeon entregue"]["aco_mm3"] = gc["entrega_anterior_refutada"]["volume_aco_entrega_anterior_mm3"]

    f = gc["fenda"]; ce = gc["cone_entrada"]; dv = gc["defeito_cavidade_selada"]; en = gc["entrega"]
    med["3 Gedeon certa"] = faixa(
        axs[2], consertada,
        "3   GEDEON CERTA — O SEU ARQUIVO, INTEIRO — fenda atravessada, cone de entrada, sem funil",
        "seção medida de `02_/matrizGedeonCerta.step` (SÓ LEITURA, %d faces, %s mm³ de aço, %d cascas): a fenda "
        "de largura %s × espessura %s com R %s nos topos atravessa de Z = %s a Z = %s e sai pela face de saída; "
        "o cone de entrada abre em Ø %s na face traseira.\nO único defeito do arquivo dele: os %d furos de pino "
        "são cavidades SELADAS — %s mm de aço até o Ø %s, sem entrada de ferramenta (por isso as %d cascas). O "
        "conserto é só partir em Y = 0: A %s + B %s = o bloco com diferença de %s mm³, 1 casca cada, BRepCheck "
        "válido, A ∩ B = %s mm³. NENHUM aço foi escavado."
        % (gc["inventario"]["faces"], n(gc["inventario"]["volume"], 1), gc["inventario"]["cascas"],
           n(f["largura_mm"], 2), n(f["espessura_mm"], 2), n(f["raio_ponta_mm"], 2), n(f["z_de_mm"], 2),
           n(f["z_ate_mm"], 2), n(2 * ce["raio_max"], 2), dv["furos_sem_acesso"],
           n(dv["parede_ate_o_externo_mm"], 2), n(dv["diametro_externo_na_zona"], 2), dv["cascas_no_solido"],
           n(en["volume_A_mm3"], 1), n(en["volume_B_mm3"], 1), n(en["soma_menos_o_bloco_mm3"], 4),
           n(en["interseccao_A_B_mm3"], 4)))
    for cxi in cx3:
        axs[2].add_patch(plt.Rectangle((cxi["x"][0] - 1.6, cxi["z"][0] - 1.6), cxi["x"][1] - cxi["x"][0] + 3.2,
                                       cxi["z"][1] - cxi["z"][0] + 3.2, fill=False, ec="tab:green", lw=1.2,
                                       ls=(0, (3, 2))))
        axs[2].plot([cxi["x"][1] + 1.6, 62.0], [0.5 * (cxi["z"][0] + cxi["z"][1])] * 2, color="tab:green",
                    lw=0.5, ls=(0, (2, 2)))
    axs[2].text(-70.0, 126.0, "Z %s → %s, a |x| %s mm: no arquivo inteiro o furo é cavidade SELADA; nas duas "
                "metades entregues ele sai aberto no plano de partição (meia-cana usinável)"
                % (n(fzp["z"][0], 2), n(fzp["z"][1], 2), n(abs(fzp["x"][1][1]), 2)),
                fontsize=7.0, color="tab:green", ha="left", va="top")
    med["3 Gedeon certa"]["furos_marcados"] = cx3

    med["4 Jonatha v27"] = faixa(
        axs[3], J2,
        "4   JONATHA v27 (o master aprovado) — compare com a faixa 3, no mesmo escalonamento",
        "seção medida de `01_CAD_MatrizJonatha_Oficial/MatrizJonatha.step` (2 sólidos, %s mm³ de aço, cascas "
        "[3, 1]). Vista no MESMO escalonamento da faixa 3 para a comparação não ser de memória: a silhueta "
        "externa é idêntica porque o envelope é exigência de projeto (Ø93,00 × Z 0..109,00 nas duas).\n"
        "O que as separa é medido na faixa 5: a v27 tem funil escavado no próprio aço (%s mm³ de canal contra "
        "%s mm³ de cone + fenda da Gedeon) e %s mm³ de aço a menos no total."
        % (n(gc["contra_a_jonatha"]["volume_jonatha_aco_mm3"], 1), n(gc["contra_a_jonatha"]["canal_da_v27_mm3"], 1),
           n(gc["contra_a_jonatha"]["fluxo_certa_mm3"], 1), n(gc["contra_a_jonatha"]["aco_so_na_certa_mm3"], 1)))

    _f3 = med["3 Gedeon certa"]
    med["5 diferenca"] = faixa_diferenca(
        axs[4], consertada, J2,
        "5   ONDE A GEDEON CERTA E A JONATHA v27 DIFEREM — diferença de conceito, medida nas duas peças",
        ("booleanos nos dois sentidos entre `matrizGedeonCerta.step` e `MatrizJonatha.step`, alinhados pela face "
         "de saída (Z = 109,00), re-cortados em Y = 0 — o plano onde os furos de pino aparecem. Números da PEÇA "
         "INTEIRA medida por `gerar_gedeon_certa.py`; a hachura é a meia-seção, por isso cada furo aparece uma "
         "vez.\nA diferença não é «funil ampliado»: a Gedeon não tem funil no próprio aço — a convergência a "
         "montante é do furo estagiado do cabeçote. Fluxo da Gedeon %s mm³ contra funil da v27 %s mm³."
         % (n(gc["contra_a_jonatha"]["fluxo_certa_mm3"], 1), n(gc["contra_a_jonatha"]["canal_da_v27_mm3"], 1))),
        _f3["z_min"], _f3["z_max"])

