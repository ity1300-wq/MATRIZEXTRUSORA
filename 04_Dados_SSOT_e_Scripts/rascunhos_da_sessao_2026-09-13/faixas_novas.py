def faixa(ax, solido, titulo, nota):
    """Traça a seção medida de `solido` no escalonamento comum e anota o que a própria seção mede.

    Nada aqui vem de memória: Ø máximo, comprimento e raio interno saem do perfil de corte, fatia a fatia
    (`dd.secao` -> `perfil` = [(z, r_externo, r_interno_ou_None)]).
    """
    curvas, area, perfil, platos, plano = dd.secao(solido)
    dd.desenha_corte(ax, perfil)
    dd.desenha_arestas(ax, curvas)
    rmax = max((p[1] or 0.0) for p in perfil)
    rmin = min((p[2] for p in perfil if p[2]), default=0.0)
    zmin, zmax = perfil[0][0], perfil[-1][0]
    col = dd.Coluna(rmax + 30.0, passo=7.0)
    dd.chamada_diametro(ax, rmax, 0.5 * (zmin + zmax), "Ø %s   máximo medido nesta seção" % n(2 * rmax, 2),
                        col, cor="tab:blue")
    dd.chamada_diametro(ax, 0.0, zmax, "Z %s   face da saída" % n(zmax, 2), col, cor="0.1")
    dd.chamada_diametro(ax, 0.0, zmin, "Z %s   plano traseiro — corte em %s" % (n(zmin, 2), plano), col,
                        cor="0.1")
    if rmin:
        dd.chamada_diametro(ax, rmin, 0.5 * (zmin + zmax) - 14.0, "Ø %s   vazio mais interno da seção"
                            % n(2 * rmin, 2), col, cor="tab:orange")
    dd.cota_v(ax, zmin, zmax, -(rmax + 40.0), "%s   comprimento" % n(zmax - zmin, 2), ha="right")
    ax.set_xlim(*LIM_X)
    ax.set_ylim(*LIM_Y)
    ax.set_aspect("equal", adjustable="datalim")
    ax.axis("off")
    ax.set_title(titulo, fontsize=10.0, loc="left", pad=6)
    ax.text(0.0, -0.17, nota, transform=ax.transAxes, fontsize=6.8, va="top", color="0.2")
    return dict(área_material_mm2=round(area, 1), D_máximo_mm=round(2 * rmax, 3), z_min=round(zmin, 3),
                z_max=round(zmax, 3), raio_interno_mín_mm=round(rmin, 3), plano=plano, platos=len(platos))


def faixa_diferenca(ax, par, jona, titulo, nota):
    """Faixa 5: as duas sobrepostas, com o aço que só uma delas tem hachurado em cor própria.

    As diferenças são os booleanos nos dois sentidos, medidos aqui — os mesmos números que
    `gerar_gedeon_corrigida.py` publica em `gedeon_corrigida.json`.
    """
    curvas, area, perfil, platos, plano = dd.secao(par)
    dd.desenha_corte(ax, perfil, hachura=False, cor="0.5", preenche=True)
    med = {}
    for rot, d, cor, hatch in (("só a Gedeon tem", maior(par.cut(jona)), "tab:red", "///"),
                               ("só a Jonatha tem", maior(jona.cut(par)), "tab:blue", "\\\\\\\\")):
        cc, aa, pp, ee, pl = dd.secao(d)
        for (zz, re, ri) in pp:
            if re and re > 0:
                ax.fill_between([-re, re], [zz - 0.5 * dd.SOLIDO_CORTE] * 2,
                                [zz + 0.5 * dd.SOLIDO_CORTE] * 2, color=cor, alpha=0.22, hatch=hatch, lw=0.0)
        bs = [q.BoundingBox() for q in d.Solids()] or [d.BoundingBox()]
        med[rot] = dict(volume_mm3=round(d.Volume(), 1), solido_valido=True,
                        z=[round(min(b.zmin for b in bs), 2), round(max(b.zmax for b in bs), 2)],
                        raio_atingido_mm=round(max(b.xmax for b in bs), 2))
    col = dd.Coluna(72.0, passo=9.0)
    dd.chamada_diametro(ax, 46.5, 118.0, "Ø 93,00   envelope comum às duas (exigência de projeto)", col,
                        cor="0.1")
    dd.chamada_diametro(ax, 46.5, 126.0, "vermelho = aço que só a Gedeon tem (%s mm³)   |   azul = só a "
                                        "v27 (%s mm³)" % (n(med["só a Gedeon tem"]["volume_mm3"], 1),
                                                          n(med["só a Jonatha tem"]["volume_mm3"], 1)),
                        col, cor="tab:red")
    ax.set_xlim(*LIM_X)
    ax.set_ylim(*LIM_Y)
    ax.set_aspect("equal", adjustable="datalim")
    ax.axis("off")
    ax.set_title(titulo, fontsize=10.0, loc="left", pad=6)
    ax.text(0.0, -0.17, nota, transform=ax.transAxes, fontsize=6.8, va="top", color="0.2")
    return med


