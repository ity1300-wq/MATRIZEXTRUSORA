def inventario(s):
    """Face por face: todo cilindro de eixo Z com suas extensoes, os planos de normal Y (a fenda) e o cone.

    Cilindro de eixo Z: caixa com x e y de mesmo tamanho. E assim que se separa, pelo tamanho do raio,
    os tres estagios do envelope (Ø grandes) dos furos de pino (Ø pequenos) — sem depender de ordem de
    saida das faces, que o OCC nao garante.
    """
    cil, fenda, outros, cone = {}, [], [], None
    for f in s.Faces():
        b, g = f.BoundingBox(), f.geomType()
        if g == "CYLINDER":
            r = round(f._geomAdaptor().Cylinder().Radius(), 3)
            if abs(b.xlen - b.ylen) < 0.01:                                    # eixo em Z
                d = cil.setdefault(r, dict(n=0, z=[b.zmin, b.zmax], x=[b.xmin, b.xmax], y=[b.ymin, b.ymax],
                                           area=0.0))
                d["n"] += 1
                d["area"] += f.Area()
                d["z"] = [min(d["z"][0], b.zmin), max(d["z"][1], b.zmax)]
                d["x"] = [min(d["x"][0], b.xmin), max(d["x"][1], b.xmax)]
                d["y"] = [min(d["y"][0], b.ymin), max(d["y"][1], b.ymax)]
            else:                                                              # eixo transversal: topo da fenda
                outros.append((r, round(b.xmin, 2), round(b.xmax, 2), round(b.ymin, 2), round(b.ymax, 2),
                               round(b.zmin, 2), round(b.zmax, 2)))
        elif g == "PLANE":
            nm = f.normalAt()
            if abs(nm.y) > 0.9:
                fenda.append((round(nm.y, 2), round(b.xmin, 2), round(b.xmax, 2),
                              round(b.ymin, 2), round(b.ymax, 2), round(b.zmin, 2), round(b.zmax, 2)))
        elif g == "CONE" and cone is None:
            cone = dict(raio_max=round(max(b.xlen, b.ylen) / 2.0, 3), z=(round(b.zmin, 2), round(b.zmax, 2)),
                        area=round(f.Area(), 1))
    return dict(cilindros_z={k: dict(n=v["n"], z=(round(v["z"][0], 2), round(v["z"][1], 2)),
                                     x=(round(v["x"][0], 2), round(v["x"][1], 2)),
                                     y=(round(v["y"][0], 2), round(v["y"][1], 2)),
                                     area=round(v["area"], 1)) for k, v in cil.items()},
                fenda_planos=fenda, cil_eixos_outros=outros, cone=cone,
                cascas=len(s.Shells()), faces=len(s.Faces()), volume=round(vol(s), 1))
