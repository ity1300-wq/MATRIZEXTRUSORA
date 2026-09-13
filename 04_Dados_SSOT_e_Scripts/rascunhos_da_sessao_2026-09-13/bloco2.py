    passos = []
    for k in ("estagio_1", "estagio_2", "estagio_3"):
        d, z0, z1 = env[k]["diametro_mm"], env[k]["z_de_mm"], env[k]["z_ate_mm"]
        r = round(d / 2.0, 3)
        medido = (inv["cilindros_z"].get(r) or {}).get("z")
        passos.append(dict(nome=k, diametro_ssot=d, z_ssot=(z0, z1), raio_cilindro_mm=r,
                           z_medido=medido, diametro_medido=round(2 * r, 2) if medido else None,
                           n_caras=(inv["cilindros_z"].get(r) or {}).get("n", 0)))
        print(f"    {k}: Ø {d:5.2f} Z {z0:6.2f}..{z1:6.2f}  ->  cilindro r={r} medido em Z {medido}")

    # fenda: os dois planos de normal Y + os dois topos semicirculares, juntos
    fe = inv["fenda_planos"]
    ou = inv["cil_eixos_outros"]
    x_min = min([p[1] for p in fe] + [q[1] for q in ou])
    x_max = max([p[2] for p in fe] + [q[2] for q in ou])
    y_min = min([p[3] for p in fe] + [q[3] for q in ou])
    y_max = max([p[4] for p in fe] + [q[4] for q in ou])
    larg = round(x_max - x_min, 3)
    esp = round(y_max - y_min, 3)
    z_fen = (min([p[5] for p in fe] + [q[5] for q in ou]), max([p[6] for p in fe] + [q[6] for q in ou]))
    r_ponta = round(min(q[0] for q in ou), 3) if ou else None
    # furos de pino: cilindros de eixo Z com raio pequeno (os estagios do envelope tem Ø 79,5 pra cima)
    fur = {r: v for r, v in inv["cilindros_z"].items() if r < 5.0}
    furos = sorted((r, v["x"][0], v["x"][1], v["z"][0], v["z"][1]) for r, v in fur.items())
    y_meia = round(max(max(abs(v["y"][0]), abs(v["y"][1])) for v in fur.values()), 3) if fur else None
    # furo transversal de fixacao: cilindro de eixo != Z que NAO seja o topo arredondado da propria fenda
    trav = [q for q in ou if (q[6] - q[5]) < b.zlen - 0.5]
    med["fenda"] = dict(largura_mm=larg, espessura_mm=esp, raio_ponta_mm=r_ponta,
                        z_de_mm=round(z_fen[0], 2), z_ate_mm=round(z_fen[1], 2), n_planos=len(fe),
                        y_planos=[round(y_min, 2), round(y_max, 2)],
                        atravessa=round(z_fen[1], 2) == round(b.zmax, 2))
    med["cone_entrada"] = inv["cone"]
    med["furos_pino"] = dict(qtd=sum(v["n"] for v in fur.values()), diametro_mm=round(2 * (furos[0][0] if furos else 0.0), 2),
                            z=(furos[0][3], furos[0][4]) if furos else None,
                            x=[(q[1], q[2]) for q in furos], y_meia_largura_mm=y_meia,
                            n_caras_por_furo=[inv["cilindros_z"][q[0]]["n"] for q in furos])
    med["furos_transversais"] = [dict(raio=q[0], x=(q[1], q[2]), z=(q[5], q[6])) for q in trav]
    print(f"    fenda: largura {larg:,.2f} x espessura {esp:,.2f} com R {r_ponta} nos topos - "
          f"Z {z_fen[0]:.2f}..{z_fen[1]:.2f} ({len(fe)} planos + {len(ou)} topos)")
    print(f"    cone de entrada: abre em Ø {2 * inv['cone']['raio_max']:.2f} em Z {inv['cone']['z'][0]:.2f}, "
          f"fecha em Z {inv['cone']['z'][1]:.2f}")
    print(f"    furos de pino: {len(furos)} x Ø {med['furos_pino']['diametro_mm']:.2f}, "
          f"Z {furos[0][3]:.2f}..{furos[0][4]:.2f}, |x| ate {abs(furos[0][2]):.2f}, y +-{y_meia:.2f}")
    print(f"    furos transversais que nao sejam o topo da fenda: {len(trav)}")
