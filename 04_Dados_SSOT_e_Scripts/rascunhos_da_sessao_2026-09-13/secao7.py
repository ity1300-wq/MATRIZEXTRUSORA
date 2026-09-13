    # --------------------------------------- [7] diferenca de conceito para a Jonatha v27, medida
    print("\n[7] a diferença de conceito para a Jonatha v27, medida nos dois sólidos")
    j27 = maior(le(F_J27))
    bj = j27.BoundingBox()
    dz = round(b.zmax - bj.zmax, 6)                      # alinha pela face de saida, o datum das duas
    j27m = desloca(j27, dz)
    mais_g = round(vol(certa.cut(j27m)), 1)
    mais_j = round(vol(j27m.cut(certa)), 1)
    canal_j = maior(le(F_J27_CANAL))
    med["contra_a_jonatha"] = dict(alinhamento="face de saida em Z = " + str(round(b.zmax, 2)),
                                   volume_jonatha_aco_mm3=round(vol(j27), 1),
                                   volume_certa_aco_mm3=round(vol(certa), 1),
                                   aco_so_na_certa_mm3=mais_g, aco_so_na_jonatha_mm3=mais_j,
                                   fluxo_certa_mm3=round(vol(fluxo), 1),
                                   canal_da_v27_mm3=round(vol(canal_j), 1),
                                   diferenca_de_conceito=(
                                       "a certa e um tampao com a fenda atravessada e um cone de entrada; a v27 "
                                       "tem funil proprio dentro dela. A diferenca nao e 'funil ampliado': a "
                                       "Gedeon nao tem funil no seu aco - a convergencia a montante e do furo "
                                       "estagiado do cabecote."))
    print(f"    aço só na certa {mais_g:,.1f} mm3 | só na Jonatha {mais_j:,.1f} mm3 (aço das duas alinhados "
          f"pela face de saida)")
    print(f"    caminho de fluxo da certa {vol(fluxo):,.1f} mm3 contra o funil da v27 {vol(canal_j):,.1f} mm3; "
          f"aco: certa {vol(certa):,.1f} x v27 {vol(j27):,.1f} mm3")

    # --------------------------------------------------- [8] o que a entrega anterior errou, em numero
    d_ant = os.path.join(RAIZ, "06_CAD_Cabecote_EX-030", "STEP", "Gedeon_Corrigida")
    try:
        a_ant = maior(le(os.path.join(d_ant, "MatrizGedeon_Corrigida_Body_A.step")))
        b_ant = maior(le(os.path.join(d_ant, "MatrizGedeon_Corrigida_Body_B.step")))
        v_ant = vol(uniao([a_ant, b_ant]))
        med["entrega_anterior_refutada"] = dict(
            volume_aco_entrega_anterior_mm3=round(v_ant, 1), volume_aco_certa_mm3=round(vol(certa), 1),
            aco_removido_por_engano_mm3=round(vol(certa) - v_ant, 1),
            motivo="a entrega anterior escavou no arquivo do usuario o canal historico "
                   "`MatrizGedeon_Canal_Fluxo.step` inteiro, quando a unica cavidade da matriz e o cone de "
                   "entrada + a fenda atravessada")
        print(f"    [refutada] a entrega anterior tem {v_ant:,.1f} mm3 de aco contra os {vol(certa):,.1f} mm3 "
              f"do arquivo dele: {vol(certa) - v_ant:,.1f} mm3 removidos a mais")
    except FileNotFoundError:
        med["entrega_anterior_refutada"] = None
        print("    [refutada] pasta da entrega anterior nao encontrada - nada a comparar")
