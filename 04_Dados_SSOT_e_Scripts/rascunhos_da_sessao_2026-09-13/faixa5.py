def faixa_diferenca(ax, par, jona, titulo, nota, zmin_p, zmax_p):
    """Faixa 5: o perfil da Gedeon em cinza e, por cima, o aço que só cada uma tem — em CORTE RADIAL.

    Corte em Y = 0 para as diferenças, não no plano que a auto-escolha daria: os bolsos de pino ficam a
    |x| = 41,50 mm e atravessam Y = 0, então é nesse plano que eles aparecem. O perfil de fundo vem do plano
    que a área de material escolher (X = 0 na Gedeon), como nas faixas 2, 3 e 4.
    """
    curvas, area, perfil, platos, plano = dd.secao(par)
    dd.desenha_corte(ax, perfil, cor="0.45", preenche=True, hachura=True)
    med = {}
    for rot, d, cor, hatch in (("só a Gedeon tem", maior(par.cut(jona)), "tab:red", "////"),
                               ("só a Jonatha tem", maior(jona.cut(par)), "tab:blue", "\\\\\\\\")):
        cc, aa, pp, ee, pl = dd.secao(d, eixo="y")
        dd.desenha_corte(ax, pp, cor=cor, espessura=1.0, preenche=True, hachura=True)
        bs = [q.BoundingBox() for q in d.Solids()] or [d.BoundingBox()]
        med[rot] = dict(volume_mm3=round(d.Volume(), 1),
                        z=[round(min(b.zmin for b in bs), 2), round(max(b.zmax for b in bs), 2)],
                        raio=[round(min(abs(b.xmin) for b in bs), 2), round(max(abs(b.xmax) for b in bs), 2)],
                        área_seção_mm2=round(aa, 1))
    # legenda no espaco livre ACIMA da peca: na coluna de rotulos ela ja tem Ø maximo e os Z, e as duas
    # coisas se cortavam (e cortavam o desenho) quando ficavam no meio da figura
    ax.text(-46.0, zmax_p + 17.0, "vermelho  %s mm³  — aço que só a Gedeon tem, em Z %s → %s" % (
        n(med["só a Gedeon tem"]["volume_mm3"], 1), n(med["só a Gedeon tem"]["z"][0], 2),
        n(med["só a Gedeon tem"]["z"][1], 2)), fontsize=7.4, color="tab:red", ha="left", va="bottom")
    ax.text(-46.0, zmax_p + 10.0, "azul  %s mm³  — aço que só a Jonatha tem, em Z %s → %s" % (
        n(med["só a Jonatha tem"]["volume_mm3"], 1), n(med["só a Jonatha tem"]["z"][0], 2),
        n(med["só a Jonatha tem"]["z"][1], 2)), fontsize=7.4, color="tab:blue", ha="left", va="bottom")
    ax.text(-46.0, zmin_p - 7.0, "envelope comum: Ø 93,00 × Z 0..109,00 — as curvas de fora são as mesmas "
            "nas faixas 2, 3 e 4; a diferença é interna e nas bordas", fontsize=7.0, color="0.15",
            ha="left", va="top")
    ax.set_xlim(*LIM_X)
    ax.set_ylim(*LIM_Y)
    ax.set_aspect("equal", adjustable="datalim")
    ax.axis("off")
    ax.set_title(titulo, fontsize=10.0, loc="left", pad=6)
    ax.text(0.0, -0.17, nota, transform=ax.transAxes, fontsize=6.8, va="top", color="0.2")
    return med


