def corpo_da_matriz(m):
    """A peça como o medidor a monta: união dos arquivos quando ela é bipartida (A ∪ B). Lidos só para
    medir - `02_CAD_Modelos_Historicos/` não é modificado (regra 2)."""
    paths = []
    for nome in m["arquivos_lidos"]:
        p = next((os.path.join(d, nome) for d in (DIR_HIS, DIR_OFF) if os.path.exists(os.path.join(d, nome))),
                 None)
        if p is None:
            sys.exit("não acho %s em %s nem em %s" % (nome, os.path.relpath(DIR_HIS, RAIZ),
                                                     os.path.relpath(DIR_OFF, RAIZ)))
        paths.append(p)
    wp = cq.importers.importStep(paths[0])
    for pt in paths[1:]:
        wp = wp.union(cq.importers.importStep(pt))
    return maior(wp.val()), [os.path.relpath(x, RAIZ) for x in paths]


def secao(solido):
    """(curvas, área de material, perfil medido fatia a fatia, platos) de um sólido - é o que o desenho
    traça. Nada aqui vem de memória: é tudo medido no sólido que chegou."""
    c, a = curvas_de_corte(solido)
    bb = solido.BoundingBox()
    pf = perfil_corte(c, bb.zmin, bb.zmax)
    return c, a, pf, escada(pf)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--saida", default=os.path.join(DIR_CAB, "DESENHO_2D_CABECOTE_X_MATRIZES.pdf"))
    ap.add_argument("--png", action="store_true", help="um PNG por página, ao lado do PDF, para conferência")
    ap.add_argument("--cabecote", default=os.path.join(DIR_CAB, "Cabecote_EX-030_desenhado.step"))
    ap.add_argument("--matrizes", default="matriz_1_copo,matriz_2_gedeon",
                    help="chaves de perfis_matrizes_x_cabecote.json, separadas por vírgula")
    a = ap.parse_args()

    if not os.path.exists(PERFIS):
        sys.exit("falta %s\nrode antes: python 04_Dados_SSOT_e_Scripts/medir_perfis_matrizes_x_cabecote.py --json"
                 % os.path.relpath(PERFIS, RAIZ))
    prof_mat = json.load(open(PERFIS, encoding="utf-8"))
    chaves = [c.strip() for c in a.matrizes.split(",") if c.strip()]
    tem = {x["chave"]: x for x in prof_mat["matrizes"]}
    fora = [c for c in chaves if c not in tem]
    if fora:
        sys.exit("chave(s) de matriz desconhecida(s): %s - as medidas são %s"
                 % (", ".join(fora), ", ".join(sorted(tem))))
    mats = [tem[c] for c in chaves]

    cab = json.load(open(os.path.join(AQUI, "cabecote_ex030.json"), encoding="utf-8"))["corpo"]
    chan = cab["chanfro_corpo_flange"]
    head = max(cq.importers.importStep(a.cabecote).val().Solids(), key=lambda s: s.Volume())
    SC = secao(head)
    for m in mats:
        corpo, rels = corpo_da_matriz(m)
        m["_corpo"], m["_arquivos"] = corpo, rels
        m["_secao"] = secao(corpo)
        print("%-22s STEP %-46s seção: %d curvas, material %8.1f mm2"
              % (m["chave"], rels[0], len(m["_secao"][0]), m["_secao"][1]))
    print("cabeçote              STEP %-46s seção: %d curvas, material %8.1f mm2"
          % (os.path.relpath(a.cabecote, RAIZ), len(SC[0]), SC[1]))

    L_H = Z_FACE_NARIZ
    bores = sorted([(2 * r, za, zb) for (r, za, zb) in BORES], key=lambda t: -t[1])
    fl, pil, corpo_c = CORPO[1], CORPO[2], CORPO[0]
    rc0, zc0, rc1, zc1 = CHAMFRO
    XL = (-272.0, 252.0)

    def monta(ax, titulo, nota):
        ax.set_xlim(*XL)
        ax.set_aspect("equal", adjustable="datalim")
        ax.axis("off")
        ax.set_title(titulo, fontsize=10.5, loc="left", pad=7)
        ax.text(0.0, -0.155, nota, transform=ax.transAxes, fontsize=7.0, va="top", color="0.2")

    def figura(n_faixas):
        fig, axs = plt.subplots(n_faixas, 1, figsize=(16.54, 11.69))
        plt.subplots_adjust(left=0.025, right=0.985, top=0.965, bottom=0.03,
                            hspace=0.66 if n_faixas >= 3 else 0.95)
        return fig, ([axs] if n_faixas == 1 else list(axs))

    # ============================================================== FAIXA 1  CABECOTE
    def faixa_cabecote(ax):
        curvas, area, perfil, es = SC
        desenha_corte(ax, perfil)
        desenha_arestas(ax, curvas)
        col = Coluna(118.0, passo=6.5)
        for i, (d, za, zb) in enumerate(bores):
            chamada_diametro(ax, d / 2.0, 0.5 * (max(za, 0.0) + min(zb, L_H)),
                             "Ø %s   furo %d do cabeçote" % (n(d, 2), i + 1), col, cor="tab:blue")
        chamada_diametro(ax, corpo_c[0], 0.5 * (corpo_c[1] + corpo_c[2]),
                         "Ø %s   corpo" % n(2 * corpo_c[0], 2), col)
        chamada_diametro(ax, fl[0], 0.5 * (fl[1] + fl[2]), "Ø %s   flange" % n(2 * fl[0], 2), col)
        chamada_diametro(ax, pil[0], 0.5 * (pil[1] + pil[2]),
                         "Ø %s   piloto de centragem" % n(2 * pil[0], 2), col, cor="tab:purple")
        # as correntes de comprimento vao para a ESQUERDA: a direita e dos rotulos de diametro, e as duas
        # coisas se cortavam quando ficavam no mesmo lado
        xais = [-126.0, -142.0, -158.0, -174.0]
        for i, (d, za, zb) in enumerate(bores[:3]):
            cota_v(ax, max(za, 0.0), min(zb, L_H), xais[i], n(min(zb, L_H) - max(za, 0.0), 2),
                   cor="tab:blue", ha="right")
        cota_v(ax, fl[1], fl[2], -190.0, "%s   flange" % n(fl[2] - fl[1], 2), ha="right")
        cota_v(ax, pil[1], pil[2], -126.0, n(pil[2] - pil[1], 2), cor="tab:purple")
        cota_v(ax, 0.0, L_H, -206.0, "%s   comprimento total" % n(L_H, 2), ha="right")
        ax.plot([-rc0, -rc1], [zc0, zc1], color="tab:red", lw=0.7, ls=(0, (2, 2)))
        ax.text(-rc1 + 6.0, 0.5 * (zc0 + zc1) + 6.0,
                "chanfro %s × %s°\nØ %s → Ø %s (cota do desenho)" % (
                    n(chan["cateto_mm"], 2), n(chan["angulo_graus"], 0),
                    n(chan.get("de_D_mm", 2 * rc1), 2), n(chan.get("para_D_mm", 2 * rc0), 2)),
                ha="center", va="bottom", color="tab:red", fontsize=7.0)
        print("cabeçote: %d platos, área de material %.1f mm²" % (len(es), area))
        nota = ("geometria: seção do STEP `%s` (arestas reais, cinza fino) e perfil de corte medido dele fatia "
                "a fatia (preto, hachurado). Z = 0 no plano mais\ntraseiro da peça; face do nariz em Z = %s. "
                "Cotas: `cabecote_ex030.json` e `verificar_interface_cabecote.py` - os mesmos dados com que este "
                "STEP foi construído.\nNão aparecem neste corte por acaso do plano, não por omissão: as 6 fendas "
                "do flange e os 6 × Ø16,50 (M12) em C.C. Ø180,00." % (os.path.basename(a.cabecote), n(L_H, 2)))
        monta(ax, "1   CABEÇOTE EX-030 — vista lateral em corte pelo plano do eixo", nota)

    # ============================================================== FAIXA n  MATRIZ SOLTA
    def faixa_matriz(ax, m, i):
        curvas, area, perfil, es = m["_secao"]
        desenha_corte(ax, perfil)
        desenha_arestas(ax, curvas)
        col = Coluna(80.0, passo=7.0)
        for j, (z0, z1, d) in enumerate(m["escala_Ø_x_Z_mm"]):
            chamada_diametro(ax, d / 2.0, 0.5 * (z0 + z1),
                             "Ø %s   estágio %d  (Z %s → %s)" % (n(d, 2), j + 1, n(z0, 2), n(z1, 2)),
                             col, cor="tab:blue")
        for j, (z0, z1, d) in enumerate(m["escala_Ø_x_Z_mm"]):
            cota_v(ax, z0, z1, -124.0 - 16 * j, n(z1 - z0, 2), cor="tab:blue", ha="right")
        fb = m["transições_refinadas_mm"].get("fim_da_banda_093_em_Z")
        if fb is not None:
            cota_v(ax, 0.0, fb, -156.0 - 16 * len(m["escala_Ø_x_Z_mm"]),
                   "%s   banda até o ombro" % n(fb, 3), cor="0.1", ha="right")
        cota_v(ax, 0.0, m["comprimento_medido_mm"], -196.0,
               "%s   comprimento da matriz" % n(m["comprimento_medido_mm"], 2), ha="right")
        canal = 2 * (perfil[len(perfil) // 2][2] or 0.0)
        print("%s: %d platos, área de material %.1f mm², Ø máx %.2f"
              % (m["chave"], len(es), area, m["Ø_máximo_medido_mm"]))
        nota = ("geometria e cotas: seção e escada medidas no STEP `%s` (aberto só para leitura; "
                "`02_CAD_Modelos_Historicos/` não é modificado - regra 2), publicadas em `%s`.\nA peça é %s; "
                "o corte passa pelo centro do canal da fenda: o canal de %s mm aparece como faixa vazia e as "
                "duas metades se sobrepõem nesta\nvista. Ø máx medido %s; comprimento %s; ombro (fim da banda) "
                "em Z = %s." % (", ".join(os.path.basename(x) for x in m["_arquivos"]), os.path.basename(PERFIS),
                                "bipartida (A ∪ B)" if m["fonte_do_corpo"] == "A U B" else "de corpo único",
                                n(canal, 2), n(m["Ø_máximo_medido_mm"], 2), n(m["comprimento_medido_mm"], 2),
                                n(m["z_do_ombro_mm"], 2)))
        monta(ax, "%d   %s — vista lateral em corte pelo plano do eixo" % (i, m["nome"]), nota)

    # ============================================================== FAIXA n  MONTAGEM
    def faixa_montagem(ax, m, i):
        curvas_h, area_h, perfil_h, _ = SC
        curvas, area, perfil, es = m["_secao"]
        desenha_corte(ax, perfil_h, cor="0.2", preenche=False, hachura=False)
        desenha_corte(ax, perfil, cor="tab:blue", espessura=1.7, hachura=True)
        dz = m["encostos"][m["encosto_usado"]]["deslocamento_aplicado_mm"]
        saida = m["comprimento_medido_mm"] + dz
        prot = saida - L_H
        interf = vol_intersecao(m["_corpo"], head)
        col = Coluna(118.0, passo=8.0)
        for j, (d, za, zb) in enumerate(bores):
            chamada_diametro(ax, d / 2.0, 0.5 * (max(za, 0.0) + min(zb, L_H)),
                             "cabeçote  Ø %s" % n(d, 2), col, cor="0.15")
        for j, (z0, z1, d) in enumerate(m["escala_Ø_x_Z_mm"]):
            chamada_diametro(ax, d / 2.0 + 3.0, 0.5 * (z0 + z1) + dz, "matriz  Ø %s" % n(d, 2), col,
                             cor="tab:blue")
        cota_v(ax, min(saida, L_H), L_H, 196.0,
               "%s   saída da matriz %s da face do nariz" % (n(abs(prot), 2), "FORA" if prot > 0 else "DENTRO"))
        cota_v(ax, 0.0, min(saida, L_H), -206.0, "%s   matriz dentro do bolso" % n(min(saida, L_H), 2),
               ha="right")
        cota_h(ax, -pil[0], pil[0], 0.0, -21.0,
               "encosto %s: %s\ninterferência medida matriz ∩ cabeçote: %s mm³ (o STEP da montagem é "
               "composto, sem booleano)"
               % (m["encosto_usado"], "traseira da matriz rasa com o plano mais traseiro do cabeçote"
                  if abs(dz) < 1e-6 else "deslocamento aplicado de %s mm" % n(dz, 2), n(interf, 4)), cor="0.1")
        folga_b = (bores[-1][0] - m["Ø_máximo_medido_mm"]) / 2.0
        nota = ("posição axial definida pelo cabeçote (degrau + fundo do bolso), não pela máquina: folga radial "
                "banda↔bolso %s mm e folga axial no\ndegrau %s mm; encosto usado = `%s` (deslocamento %s mm). "
                "Saída da matriz em Z = %s, ou %s %s da face do nariz (%s).\nCada número desta faixa é medido "
                "nos dois STEP: a matriz por `%s`, o assento por `medir_perfis_matrizes_x_cabecote.py`.\n"
                "Os Ø aqui são os MEDIDOS no STEP da peça - no DXF a banda da matriz coincide com o bolso Ø95 "
                "e o canal é desenhado com 17,00 mm\n(versus os 11,00 mm do furo): ver "
                "`cabecote_ex030.json:matriz_copo_desenhada_no_dxf`."
                % (n(folga_b, 3),
                   n(m["transições_refinadas_mm"]["folga_axial_banda_x_degrau_do_cabecote_mm"], 3),
                   m["encosto_usado"], n(dz, 2), n(saida, 2), n(abs(prot), 2),
                   "para fora" if prot > 0 else "para dentro", n(L_H, 2), ", ".join(m["_arquivos"])))
        monta(ax, "%d   MONTAGEM — %s: cabeçote (contorno) + matriz (azul, hachurada), mesmo referencial axial"
              % (i, m["nome"].split("(")[0].strip()), nota)

    from matplotlib.backends.backend_pdf import PdfPages
    os.makedirs(os.path.dirname(a.saida), exist_ok=True)
    paginas = []
    fig, axs = figura(1 + len(mats))
    faixa_cabecote(axs[0])
    for k, m in enumerate(mats):
        faixa_matriz(axs[1 + k], m, 2 + k)
    paginas.append(fig)
    fig, axs = figura(len(mats))
    for k, m in enumerate(mats):
        faixa_montagem(axs[k], m, 1 + k)
    paginas.append(fig)

    with PdfPages(a.saida) as pdf:
        for fig in paginas:
            pdf.savefig(fig)
    print("PDF ->", a.saida, "(%d páginas)" % len(paginas))
    if a.png:
        for k, fig in enumerate(paginas, 1):
            pth = "%s_p%d.png" % (os.path.splitext(a.saida)[0], k)
            fig.savefig(pth, format="png", dpi=120)
            print("PNG ->", pth)
    for fig in paginas:
        plt.close(fig)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
