    f = gc["fenda"]; ce = gc["cone_entrada"]; dv = gc["defeito_cavidade_selada"]; en = gc["entrega"]
    med["3 Gedeon certa"] = faixa(
        axs[2], consertada,
        "3   GEDEON CERTA — o SEU arquivo, inteiro — fenda atravessada, cone de entrada, sem funil",
        f"geometria: `02_CAD_Modelos_Historicos/matrizGedeonCerta.step` lido SÓ PARA LEITURA e medido face por "
        f"face por `gerar_gedeon_certa.py`: {n(gc['inventario']['faces'], 0)} faces, "
        f"{n(gc['inventario']['volume'], 1)} mm³ de aço, {n(gc['inventario']['cascas'], 0)} cascas. Nesta vista "
        f"está a fenda: {f['n_planos']} faces planas de largura {n(f['largura_mm'], 2)} × espessura "
        f"{n(f['espessura_mm'], 2)} com R {n(f['raio_ponta_mm'], 2)} nos dois topos, atravessando de Z = "
        f"{n(f['z_de_mm'], 2)} a Z = {n(f['z_ate_mm'], 2)} — sai pela face de saída, e é por ela que o plástico "
        f"vem. O cone de entrada abre em Ø {n(2 * ce['raio_max'], 2)} na face traseira e fecha em Z = "
        f"{n(ce['z'][1], 2)}; caminho de fluxo medido (cone + fenda) {n(gc['cavidade']['volume_cavidade_mm3'], 1)} mm³.\n"
        f"O único defeito do arquivo dele é este: os {n(dv['furos_sem_acesso'], 0)} furos de pino são "
        f"CAVIDADES SELADAS — {n(dv['parede_ate_o_externo_mm'], 2)} mm de aço até o Ø "
        f"{n(dv['diametro_externo_na_zona'], 2)} externo, sem por onde entrar ferramenta (é isso que faz o sólido "
        f"ter {n(dv['cascas_no_solido'], 0)} cascas). O conserto entregue é só partir em Y = 0: "
        f"A {n(en['volume_A_mm3'], 1)} + B {n(en['volume_B_mm3'], 1)} = o bloco com diferença de "
        f"{n(en['soma_menos_o_bloco_mm3'], 4)} mm³, cada metade com 1 casca, BRepCheck válido, "
        f"A ∩ B = {n(en['interseccao_A_B_mm3'], 4)} mm³. NENHUM aço foi escavado do arquivo dele.")
    # as caixas verdes sao as medidas dos furos de pino no arquivo certo (gedeon_certa.json, nao decoradas)
    for cxi in cx3:
        axs[2].add_patch(plt.Rectangle((cxi["x"][0] - 1.6, cxi["z"][0] - 1.6), cxi["x"][1] - cxi["x"][0] + 3.2,
                                       cxi["z"][1] - cxi["z"][0] + 3.2, fill=False, ec="tab:green", lw=1.2,
                                       ls=(0, (3, 2))))
        axs[2].plot([cxi["x"][1] + 1.6, 62.0], [0.5 * (cxi["z"][0] + cxi["z"][1])] * 2, color="tab:green",
                    lw=0.5, ls=(0, (2, 2)))
    axs[2].text(-70.0, 126.0, "Z %s → %s, a |x| %s mm: no arquivo inteiro o furo é cavidade SELADA; nas duas "
                "metades entregues ele sai aberto no plano de partição (meia-cana)"
                % (n(fzp["z"][0], 2), n(fzp["z"][1], 2), n(abs(fzp["x"][1][1]), 2)),
                fontsize=7.0, color="tab:green", ha="left", va="top")
    med["3 Gedeon certa"]["furos_marcados"] = cx3

