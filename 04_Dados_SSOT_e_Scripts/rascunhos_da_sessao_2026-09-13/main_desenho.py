def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--saida", default=os.path.join(DIR_CAB, "DESENHO_2D_CABECOTE_X_MATRIZ_COPO.pdf"))
    ap.add_argument("--png", action="store_true")
    ap.add_argument("--cabecote", default=os.path.join(DIR_CAB, "Cabecote_EX-030_desenhado.step"))
    ap.add_argument("--matriz", default=os.path.join(DIR_HIS, "Matriz1_Original_Copo_Solido.step"))
    ap.add_argument("--chave-matriz", default="matriz_1_copo")
    a = ap.parse_args()

    if not os.path.exists(PERFIS):
        sys.exit("falta %s\nrode antes: python 04_Dados_SSOT_e_Scripts/medir_perfis_matrizes_x_cabecote.py --json"
                 % os.path.relpath(PERFIS, RAIZ))
    prof_mat = json.load(open(PERFIS, encoding="utf-8"))
    m = next(x for x in prof_mat["matrizes"] if x["chave"] == a.chave_matriz)
    cab = json.load(open(os.path.join(AQUI, "cabecote_ex030.json"), encoding="utf-8"))["corpo"]
    chan = cab["chanfro_corpo_flange"]

    head = max(cq.importers.importStep(a.cabecote).val().Solids(), key=lambda s: s.Volume())
    die = max(cq.importers.importStep(a.matriz).val().Solids(), key=lambda s: s.Volume())
    ch_c, ch_a = curvas_de_corte(head)
    cd_c, cd_a = curvas_de_corte(die)
    bh, bd = head.BoundingBox(), die.BoundingBox()
    ph = perfil_corte(ch_c, bh.zmin, bh.zmax)
    pd_ = perfil_corte(cd_c, bd.zmin, bd.zmax)
    eh, ed = escada(ph), escada(pd_)
    print("cabeçote (seção: %d curvas, material %.1f mm2) platos:" % (len(ch_c), ch_a))
    for p in eh:
        print("   Z %7.2f..%7.2f  r_ext %7.3f  r_furo %s" % (p[0], p[1], p[2],
                                                              "-" if p[3] is None else "%6.3f" % p[3]))
    print("matriz (seção: %d curvas, material %.1f mm2) platos:" % (len(cd_c), cd_a))
    for p in ed:
        print("   Z %7.2f..%7.2f  r_ext %7.3f  r_furo %s" % (p[0], p[1], p[2],
                                                              "-" if p[3] is None else "%6.3f" % p[3]))

    L_H = Z_FACE_NARIZ
    bores = sorted([(2 * r, za, zb) for (r, za, zb) in BORES], key=lambda t: -t[1])
    fl, pil, corpo = CORPO[1], CORPO[2], CORPO[0]
    rc0, zc0, rc1, zc1 = CHAMFRO
    fig, axs = plt.subplots(3, 1, figsize=(16.54, 11.69))
    plt.subplots_adjust(left=0.025, right=0.985, top=0.965, bottom=0.03, hspace=0.66)
    XL = (-212.0, 252.0)

    def monta(ax, titulo, nota):
        ax.set_xlim(*XL)
        ax.set_aspect("equal", adjustable="datalim")
        ax.axis("off")
        ax.set_title(titulo, fontsize=10.5, loc="left", pad=7)
        ax.text(0.0, -0.155, nota, transform=ax.transAxes, fontsize=7.0, va="top", color="0.2")

    # ============================================================== 1  CABECOTE
    ax = axs[0]
    desenha_corte(ax, ph)
    desenha_arestas(ax, ch_c)
    col = Coluna(118.0, passo=6.5)
    for i, (d, za, zb) in enumerate(bores):
        chamada_diametro(ax, d / 2.0, 0.5 * (max(za, 0.0) + min(zb, L_H)),
                         "Ø %s   furo %d do cabeçote" % (n(d, 2), i + 1), col, cor="tab:blue")
    chamada_diametro(ax, corpo[0], 0.5 * (corpo[1] + corpo[2]),
                     "Ø %s   corpo" % n(2 * corpo[0], 2), col)
    chamada_diametro(ax, fl[0], 0.5 * (fl[1] + fl[2]), "Ø %s   flange" % n(2 * fl[0], 2), col)
    chamada_diametro(ax, pil[0], 0.5 * (pil[1] + pil[2]),
                     "Ø %s   piloto de centragem" % n(2 * pil[0], 2), col, cor="tab:purple")
    for i, (d, za, zb) in enumerate(bores):
        cota_v(ax, max(za, 0.0), min(zb, L_H), 178.0 + 13 * i,
               n(min(zb, L_H) - max(za, 0.0), 2), cor="tab:blue")
    cota_v(ax, fl[1], fl[2], 178.0 + 13 * len(bores),
           "%s   flange" % n(fl[2] - fl[1], 2))
    cota_v(ax, pil[1], pil[2], 178.0 + 13 * (len(bores) + 1), n(pil[2] - pil[1], 2), cor="tab:purple")
    cota_v(ax, corpo[1], corpo[2], 178.0 + 13 * (len(bores) + 2),
           "%s   corpo" % n(corpo[2] - corpo[1], 2))
    cota_v(ax, 0.0, L_H, -188.0, "%s   comprimento total" % n(L_H, 2), ha="right")
    ax.plot([-rc0, -rc1], [zc0, zc1], color="tab:red", lw=0.7, ls=(0, (2, 2)))
    ax.text(-rc1 - 4.0, 0.5 * (zc0 + zc1) + 4.0,
            "chanfro %s × %s°\nØ %s → Ø %s" % (n(chan["cateto_mm"], 2), n(chan["angulo_graus"], 0),
                                               n(2 * rc0, 2), n(2 * rc1, 2)),
            ha="right", va="center", color="tab:red", fontsize=7.0)
    nota1 = ("geometria: seção do STEP `%s` (arestas reais, cinza fino) e perfil de corte medido dele fatia "
             "a fatia (preto, hachurado). Z = 0 no plano mais\ntraseiro da peça; face do nariz em Z = %s. "
             "Cotas: `cabecote_ex030.json` e `verificar_interface_cabecote.py` - os mesmos dados com que este "
             "STEP foi construído.\nNão aparecem neste corte por acaso do plano, não por omissão: as 6 fendas "
             "do flange e os 6 × Ø16,50 (M12) em C.C. Ø180,00." % (os.path.basename(a.cabecote), n(L_H, 2)))
    monta(ax, "1   CABEÇOTE EX-030 — vista lateral em corte pelo plano do eixo", nota1)

    # ============================================================== 2  MATRIZ
    ax = axs[1]
    desenha_corte(ax, pd_)
    desenha_arestas(ax, cd_c)
    col = Coluna(80.0, passo=7.0)
    for i, (z0, z1, d) in enumerate(m["escala_Ø_x_Z_mm"]):
        chamada_diametro(ax, d / 2.0, 0.5 * (z0 + z1),
                         "Ø %s   estágio %d  (Z %s → %s)" % (n(d, 2), i + 1, n(z0, 2), n(z1, 2)),
                         col, cor="tab:blue")
    for i, (z0, z1, d) in enumerate(m["escala_Ø_x_Z_mm"]):
        cota_v(ax, z0, z1, 150.0 + 13 * i, n(z1 - z0, 2), cor="tab:blue")
    fb = m["transições_refinadas_mm"].get("fim_da_banda_093_em_Z")
    if fb is not None:
        cota_v(ax, 0.0, fb, 150.0 + 13 * len(m["escala_Ø_x_Z_mm"]),
               "%s   banda até o ombro" % n(fb, 3), cor="0.1")
    cota_v(ax, 0.0, m["comprimento_medido_mm"], 196.0,
           "%s   comprimento da matriz" % n(m["comprimento_medido_mm"], 2))
    cota_v(ax, 0.0, m["comprimento_medido_mm"], -188.0, n(m["comprimento_medido_mm"], 2), ha="right")
    canal = 2 * (pd_[len(pd_) // 2][2] or 0.0)
    nota2 = ("geometria e cotas: seção e escada medidas no STEP `%s` (aberto só para leitura; "
             "`02_CAD_Modelos_Historicos/` não é modificado - regra 2), publicadas em `%s`.\nA peça é "
             "bipartida e o corte passa pelo centro do canal da fenda: o canal de %s mm aparece como faixa "
             "vazia e as duas metades se sobrepõem nesta\nvista. Ø máx medido %s; comprimento %s; ombro (fim "
             "da banda) em Z = %s." % (os.path.basename(a.matriz), os.path.basename(PERFIS), n(canal, 2),
                                       n(m["Ø_máximo_medido_mm"], 2), n(m["comprimento_medido_mm"], 2),
                                       n(m["z_do_ombro_mm"], 2)))
    monta(ax, "2   %s — vista lateral em corte pelo plano do eixo" % m["nome"], nota2)

    # ============================================================== 3  MONTAGEM
    ax = axs[2]
    desenha_corte(ax, ph, cor="0.2", preenche=False, hachura=False)
    desenha_corte(ax, pd_, cor="tab:blue", espessura=1.7, hachura=True)
    dz = m["encostos"][m["encosto_usado"]]["deslocamento_aplicado_mm"]
    saida = m["comprimento_medido_mm"] + dz
    prot = saida - L_H
    col = Coluna(118.0, passo=8.0)
    for i, (d, za, zb) in enumerate(bores):
        chamada_diametro(ax, d / 2.0, 0.5 * (max(za, 0.0) + min(zb, L_H)),
                         "cabeçote  Ø %s" % n(d, 2), col, cor="0.15")
    for i, (z0, z1, d) in enumerate(m["escala_Ø_x_Z_mm"]):
        chamada_diametro(ax, d / 2.0 + 3.0, 0.5 * (z0 + z1) + dz, "matriz  Ø %s" % n(d, 2), col,
                         cor="tab:blue")
    cota_v(ax, min(saida, L_H), L_H, 200.0,
           "%s   saída da matriz %s da face do nariz" % (n(abs(prot), 2),
                                                          "FORA" if prot > 0 else "DENTRO"))
    cota_v(ax, 0.0, min(saida, L_H), -188.0, "%s   matriz dentro do bolso" % n(min(saida, L_H), 2),
           ha="right")
    cota_h(ax, -pil[0], pil[0], 0.0, -13.0,
           "encosto face a face: traseira da matriz rasa com o plano mais traseiro do cabeçote (medido "
           "0,000 mm)\no piloto Ø %s × %s protrai atrás da face do flange - é aí que a máquina precisa do "
           "rebaixo correspondente" % (n(2 * pil[0], 2), n(pil[2] - pil[1], 2)), cor="0.1")
    dif = prof_mat["diferença_copo_x_gedeon_medida"]
    nota3 = ("a posição axial da matriz é definida pelo cabeçote (degrau + fundo do bolso), não pela máquina: "
             "folga radial banda↔bolso %s mm e folga axial no degrau\n%s mm. A Copo desemboca %s mm %s da "
             "face do nariz - é o que você observou na saída, e o valor é a diferença de comprimento entre as "
             "matrizes:\nna Copo falta o nariz de %s mm que a Gedeon, a Desenvolvimento e a Jonatha têm "
             "(medido em `perfis_matrizes_x_cabecote.json`)."
             % (n((bores[-1][0] - m["Ø_máximo_medido_mm"]) / 2.0, 3),
                n(m["transições_refinadas_mm"]["folga_axial_banda_x_degrau_do_cabecote_mm"], 3),
                n(abs(prot), 2), "para fora" if prot > 0 else "para dentro",
                n(dif["diferença_mm"], 2)))
    monta(ax, "3   MONTAGEM — cabeçote (contorno) + matriz (azul, hachurada), no mesmo referencial axial",
          nota3)

    print("chanfro desenhado: Z %.2f..%.2f de r %.2f a r %.2f" % (zc0, zc1, rc0, rc1))
    os.makedirs(os.path.dirname(a.saida), exist_ok=True)
    fig.savefig(a.saida, format="pdf")
    print("PDF ->", a.saida)
    if a.png:
        pth = a.saida[:-4] + ".png"
        fig.savefig(pth, format="png", dpi=120)
        print("PNG ->", pth)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
