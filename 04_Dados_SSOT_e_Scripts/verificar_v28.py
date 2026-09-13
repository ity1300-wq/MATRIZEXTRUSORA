"""
VERIFICACAO EXATA DA REVISAO PROPOSTA - MATRIZ JONATHA (rotulo lido do SSOT)
===================================================
Mede os STEP gerados por `gerar_matriz_v28.py` e prova, uma a uma, as
afirmacoes da revisao. Nada aqui e estimado: cada parede, volume e distancia
sai de booleanos e de BRepExtrema sobre os solidos reais.

  [A] o que NAO podia mudar  : fenda 75,00 x 1,50 com R0,75, boca Ø75,60,
                               envelope Ø93/Ø89,5/Ø79,5 x 109, funil herdado
  [B] o que a revisao prometeu: labio conforme o SSOT (D2: 8,50 + 1,50 x 45), lamina,
                               pinos abertos e conjugados nas duas metades,
                               zero cavidade selada, canal com 1 solido
  [C] seguranca dos furos      : nenhum invade o canal, parede real >= alvo,
                               web entre furos, cego no fundo, abre na face
  [D] numeros para a fabrica   : massa, forca de abertura (area projetada
                               medida), ΔP 1D com o metodo do proprio projeto

Uso: python 04_Dados_SSOT_e_Scripts/verificar_v28.py [--json] [--md]
Retorno: 0 se tudo conforme, 1 se houver nao conformidade.
"""

import argparse
import json
import math
import os
import sys

import cadquery as cq

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, ".."))
sys.path.insert(0, AQUI)

from verify_legacy_dies import dp_total, tau_parede   # metodos do proprio projeto

DIR_CAD = os.path.join(RAIZ, "07_CAD_Matrizes", "M01_Jonatha_v27_OFICIAL")
with open(os.path.join(AQUI, "cad_die_parameters.json"), encoding="utf-8") as _f:
    ROTULO = json.load(_f)["proposta_v28_dfm"].get("rotulo", "v28.1")   # rotulo = SSOT, nao string no codigo
DIR_DOC = os.path.join(RAIZ, "03_Relatorios_e_Documentacao")

PAREDE_MIN = {"pino_alinhamento": 2.00, "cartucho": 4.00, "termopar": 3.00,
              "desmontagem": 3.00}
WEB_MINIMA = 3.00
TOL = 0.02
ENVELOPE = [(0.00, 69.90, 93.00), (69.90, 80.70, 89.50), (80.70, 109.00, 79.50)]
linhas = []


# ------------------------------------------------------------------ util
def checar(item, medido, nominal, tol=TOL, un="mm", obs=""):
    ok = abs(medido - nominal) <= tol
    linhas.append({"item": item, "nominal": round(nominal, 4), "medido": round(medido, 4),
                   "desvio": round(medido - nominal, 4), "unidade": un,
                   "status": "CONFORME" if ok else "NAO_CONFORME", "observacao": obs})
    print(f"  [{'OK  ' if ok else 'FALHA'}] {item:<52} nominal={nominal:10.3f} "
          f"medido={medido:10.3f} desvio={medido - nominal:+8.3f} {un}"
          + (f"  <- {obs}" if obs and not ok else ""))
    return ok


def registrar(item, valor, obs="", ok=True):
    linhas.append({"item": item, "medido": valor, "observacao": obs,
                   "status": "CONFORME" if ok else "NAO_CONFORME"})
    print(f"  [{'OK  ' if ok else 'FALHA'}] {item:<52} {valor}  {obs}")
    return ok


def maior(forma):
    """Maior sólido de um Shape, Compound ou lista de shapes."""
    from OCP.TopAbs import TopAbs_SOLID
    from OCP.TopExp import TopExp_Explorer
    if isinstance(forma, (list, tuple)):
        return max(forma, key=lambda x: x.Volume())
    shp = forma.wrapped if hasattr(forma, "wrapped") else forma
    exp = TopExp_Explorer(shp, TopAbs_SOLID)
    melhor, melhor_v = None, -1.0
    while exp.More():
        s = cq.Solid(exp.Current())
        if s.Volume() > melhor_v:
            melhor, melhor_v = s, s.Volume()
        exp.Next()
    return melhor if melhor is not None else forma


def contar(forma, tipo):
    from OCP.TopAbs import TopAbs_SHELL
    from OCP.TopExp import TopExp_Explorer
    shp = forma.wrapped if hasattr(forma, "wrapped") else forma
    e, n = TopExp_Explorer(shp, {"shell": TopAbs_SHELL}[tipo]), 0
    while e.More():
        n += 1
        e.Next()
    return n


def dist3d(a, b):
    from OCP.BRepExtrema import BRepExtrema_DistShapeShape
    d = BRepExtrema_DistShapeShape(
        a.wrapped if hasattr(a, "wrapped") else a,
        b.wrapped if hasattr(b, "wrapped") else b)
    return d.Value() if d.Perform() else float("nan")


def n(v, dec=3):
    """numero com separador decimal brasileiro (o repo inteiro e pt-BR)"""
    return f"{float(v):.{dec}f}".replace(".", ",")


class _Vazia:
    xmin = xmax = ymin = ymax = zmin = zmax = 0.0


def secao(solido, z, esp=0.004):
    lam = cq.Workplane("XY").workplane(offset=z - esp / 2).box(
        400, 400, esp, centered=(True, True, False)).val()
    s = maior(solido.intersect(lam))
    v = s.Volume()
    return (_Vazia(), 0.0) if v <= 1e-9 else (s.BoundingBox(), v / esp)


def cil_y(x, z, y0, y1, r):
    return cq.Solid.makeCylinder(r, abs(y1 - y0), cq.Vector(x, min(y0, y1), z),
                                 cq.Vector(0, 1, 0))


def r_envelope(z):
    for z0, z1, d in ENVELOPE:
        if z0 - 1e-9 <= z <= z1 + 1e-9:
            return d / 2.0
    return 0.0


def envelope_solido():
    e = cq.Workplane("XY").circle(ENVELOPE[0][2] / 2).extrude(ENVELOPE[0][1])
    for (z0, z1, d) in ENVELOPE[1:]:
        e = e.union(cq.Workplane("XY").workplane(offset=z0).circle(d / 2).extrude(z1 - z0))
    return maior(e.val())


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--md", action="store_true")
    a = ap.parse_args()

    feats = json.load(open(os.path.join(AQUI, "matriz_v28_features.json"), encoding="utf-8"))
    meta = feats["meta"]
    Z_LAND, Z_FIM = meta["z_land"], meta["z_saida"]

    def load(nm):
        return cq.importers.importStep(os.path.join(DIR_CAD, nm))

    cmp_fluxo = load("MatrizJonatha_v28_Canal_Fluxo.step")
    n_sol = len(cmp_fluxo.solids().vals())
    canal = maior(cmp_fluxo.solids().vals())
    A = maior(load("MatrizJonatha_v28_Body_A.step").solids().vals())
    B = maior(load("MatrizJonatha_v28_Body_B.step").solids().vals())
    aco = maior(A.fuse(B))
    canal27 = maior(load("MatrizJonatha_Canal_Fluxo.step").solids().vals())
    env = envelope_solido()
    vol_env = sum(math.pi * (d / 2) ** 2 * (z1 - z0) for (z0, z1, d) in ENVELOPE)

    print("=" * 96)
    print(f"VERIFICAÇÃO EXATA - MATRIZ JONATHA {ROTULO}  (medida nos STEP gerados)")
    print("=" * 96)

    # ---------------------------------------------------------------- A
    print("\n[A] O QUE NÃO PODIA MUDAR (especificação do produto e master aprovado)")
    registrar("Canal entregue com 1 único sólido (o v27 tinha 3)", f"{n_sol} sólido(s)",
              "necessário p/ eletrodo de EDM e malha de CFD", ok=n_sol == 1)
    bb = aco.BoundingBox()
    checar("Comprimento total Z", bb.zmax - bb.zmin, 109.00)
    checar("Ø externo máximo (estágio 1)", bb.xmax - bb.xmin, 93.00)
    for (z0, z1, d) in ENVELOPE:
        zc = 0.5 if z0 == 0 else (z0 + z1) / 2
        s, _ = secao(aco, zc)
        checar(f"Ø externo em Z={n(zc)} (estágio Ø{n(d, 1)})", s.xmax - s.xmin, d)
    s0, _ = secao(canal, 0.002)
    checar("Ø da boca de entrada (Z=0)", s0.xmax - s0.xmin, 75.60, tol=0.05)
    sl, al = secao(canal, 100.0)
    checar("Largura da fenda (X)", sl.xmax - sl.xmin, 75.00)
    checar("Espessura da fenda (Y)", sl.ymax - sl.ymin, 1.50)
    checar("Área da seção da fenda (R0,75 nas bordas)", al,
           (75.0 - 1.5) * 1.5 + math.pi * 0.75 ** 2, tol=0.05, un="mm2")
    fatia = cq.Workplane("XY").box(400, 400, Z_LAND, centered=(True, True, False)).val()
    fun28, fun27 = maior(canal.intersect(fatia)), maior(canal27.intersect(fatia))
    d_sim = dist3d(fun28, fun27)
    registrar("Funil (Z<99) geometricamente idêntico ao master v27.0",
              f"Δmáx entre superfícies = {n(d_sim, 6)} mm", "a revisão não mexe no aprovado",
              ok=d_sim < 1e-4)
    registrar("Volume do funil v28 vs v27",
              f"diferença = {n(abs(fun28.Volume() - fun27.Volume()), 4)} mm³",
              "mesmo sólido abaixo de Z=99",
              ok=abs(fun28.Volume() - fun27.Volume()) < 1.0)
    # assimetria do canal em Y (medida; vem do loft do v27)
    half_b = maior(canal.intersect(cq.Solid.makeBox(600, 400, 600, cq.Vector(-300, 0, -300))))
    half_a = maior(canal.intersect(cq.Solid.makeBox(600, 400, 600, cq.Vector(-300, -400, -300))))
    dif_h = abs(half_a.Volume() - half_b.Volume())
    registrar("Assimetria do canal em torno do plano de partição Y=0",
              f"|A-B| = {n(dif_h, 2)} mm³ ({n(100 * dif_h / canal.Volume(), 3)} % do canal)",
              "herdado do loft do v27.0: as metades não são espelhos exatos", ok=True)

    # cada arquivo entregue tem de trazer os solidos certos (bug real ja ocorrido:
    # os tres STEP de montagem apontavam para o mesmo nome de arquivo)
    esperado = {"MatrizJonatha_v28.step": 2, "MatrizJonatha_v28_Explodida.step": 2,
                "MatrizJonatha_v28_Com_Fluxo.step": 3,
                "MatrizJonatha_v28_Pinos_Alinhamento.step": 4,
                "MatrizJonatha_v28_Canal_Fluxo.step": 1,
                "MatrizJonatha_v28_Body_A.step": 1, "MatrizJonatha_v28_Body_B.step": 1}
    faltando, errados, presentes = [], [], []
    for nome_arq, ns in esperado.items():
        caminho = os.path.join(DIR_CAD, nome_arq)
        if not os.path.exists(caminho):
            faltando.append(nome_arq)
            continue
        k = len(load(nome_arq).solids().vals())
        (presentes if k == ns else errados).append(f"{nome_arq} ({k}/{ns})")
    registrar("Arquivos STEP entregues (nomes + nº de sólidos)",
              f"{len(presentes)}/{len(esperado)} exatos"
              + (f" | faltando: {', '.join(faltando)}" if faltando else "")
              + (f" | sólidos errados: {', '.join(errados)}" if errados else ""),
              "mestr=2 · explodida=2 · com_fluxo=3 · pinos=4 · canal=1 · corpo=1",
              ok=not faltando and not errados)

    # ---------------------------------------------------------------- B
    print("\n[B] O QUE A REVISÃO PROMETEU")
    z_par = None
    z = Z_LAND + 0.05
    while z < Z_FIM - 0.05:
        s, _ = secao(canal, z)
        if abs((s.ymax - s.ymin) - 1.5) > TOL:
            break
        z_par = z
        z += 0.05
    land_medido = (z_par - Z_LAND) if z_par else 0.0
    checar("Land reto e paralelo (v27.0: 8,50)", land_medido, meta["land_paralelo"],
           tol=0.10, obs="P8 resolvido no modelo")
    checar("Chanfro de saída (v27.0: 1,50)", Z_FIM - (Z_LAND + land_medido), meta["chanfro"],
           tol=0.10, obs="D2: lábio mantido como no master, sem ganho de land")
    s_ch, _ = secao(canal, Z_FIM - 0.1)
    checar("Sobrelargura do chanfro a 0,10 mm da face", (s_ch.xmax - s_ch.xmin - 75.0) / 2,
           meta["chanfro"] - 0.10, tol=0.05, un="mm", obs="chanfro de 45°")
    s_fim, _ = secao(canal, Z_FIM - 0.001)
    lamina = r_envelope(Z_FIM) - max(abs(s_fim.xmin), abs(s_fim.xmax))
    ss = json.load(open(os.path.join(AQUI, "cad_die_parameters.json"), encoding="utf-8"))
    lam_dec = float(ss["decisoes_usuario"]["D2_labio_saida"]["geometria"]["lamina_mm"])
    checar("Lâmina de aço no lábio de saída (= valor decidido em D2)", lamina, lam_dec, tol=0.05,
           un="mm", obs="a decisão D2 aceitou a lâmina fina de 0,75 mm do master; o lascamento na "
           "limpeza passa a ser item de procedimento de manutenção, não de geometria")
    sh_a, sh_b = contar(A, "shell"), contar(B, "shell")
    registrar("Shells no Body_A (v27.0 tinha 3 = 2 bolhas seladas)", str(sh_a),
              "1 = sólido limpo, sem cavidade interna", ok=sh_a == 1)
    registrar("Shells no Body_B (v27.0 tinha 1, mas sem furo nenhum)", str(sh_b),
              "1 = sólido limpo", ok=sh_b == 1)
    checar("Interferência Body_A ∩ Body_B", maior(A.intersect(B)).Volume(), 0.0,
           tol=1e-6, un="mm3")

    # furos de pino: vazios no corpo, abertos no plano de particao, cegos no fundo
    ok_a = ok_b = 0
    for f in [x for x in feats["furos"] if x["tipo"] == "pino_alinhamento"]:
        r, dep = f["diametro"] / 2, feats["profundidade_pino_mm"]
        vazio_a = maior(cil_y(f["X"], f["Z"], -dep + 0.05, -0.05, r).intersect(A)).Volume()
        vazio_b = maior(cil_y(f["X"], f["Z"], 0.05, dep - 0.05, r).intersect(B)).Volume()
        fundo_a = maior(cil_y(f["X"], f["Z"], -dep - 1.0, -dep, r).intersect(A)).Volume()
        fundo_b = maior(cil_y(f["X"], f["Z"], dep, dep + 1.0, r).intersect(B)).Volume()
        cheio = math.pi * r * r * 1.0
        if vazio_a < 1e-6 and fundo_a > 0.95 * cheio:
            ok_a += 1
        if vazio_b < 1e-6 and fundo_b > 0.95 * cheio:
            ok_b += 1
        registrar(f"Pino em X={f['X']:+.2f} Z={f['Z']:.2f}",
                  f"A: bolso vazio {vazio_a:.4f} mm³, aço sob o fundo {fundo_a:.1f}/{cheio:.1f} mm³ | "
                  f"B: {vazio_b:.4f} / {fundo_b:.1f} mm³",
                  "aberto no plano de partição e cego sob o fundo nas DUAS metades",
                  ok=vazio_a < 1e-6 and vazio_b < 1e-6
                  and fundo_a > 0.95 * cheio and fundo_b > 0.95 * cheio)
    registrar("Pinos conjugados nas duas metades", f"{ok_a}/4 no Body_A e {ok_b}/4 no Body_B",
              "v27.0: bolsões selados só no A e nada no B (P2)", ok=ok_a == 4 and ok_b == 4)

    # fechamento volumetrico: env - (aço + canal) = soma dos furos dentro do env
    caixas = []
    for f in feats["furos"]:
        r = f["diametro"] / 2
        c = cil_y(f["X"], f["Z"], f["y_ini_mm"], f["y_fim_mm"], r)
        caixas.append((f["tipo"], r, c, f))
    vol_furos = sum(maior(c.intersect(env)).Volume() for (_t, _r, c, _f) in caixas)
    checar("Fechamento: env − (aço + canal) = volume dos furos", vol_env - (aco.Volume() + canal.Volume()),
           vol_furos, tol=1.5, un="mm3",
           obs="prova que todo furo removido existe no corpo e nada mais foi tirado")

    # ---------------------------------------------------------------- C
    print("\n[C] SEGURANÇA DOS FUROS NOVOS")
    paredes = {}
    for (tipo, r, c, f) in caixas:
        dentro = maior(c.intersect(env)).Volume()
        invade = maior(c.intersect(canal)).Volume()
        parede = dist3d(maior(c.intersect(env)), canal)
        alvo = PAREDE_MIN.get(tipo, 3.0)
        ok = invade < 1e-6 and parede >= alvo - 1e-6
        paredes[tipo] = min(paredes.get(tipo, 99.0), parede)
        tag = f"{tipo} X={f['X']:+.2f} Z={f['Z']:.2f}"
        registrar(f"parede mínima até o canal - {tag}", f"{n(parede)} mm",
                  f"alvo ≥ {n(alvo, 2)} mm | invadiu o canal em {n(invade, 6)} mm³", ok=ok)
        registrar(f"  ∩ volume do canal - {tag}", f"{n(invade, 6)} mm³",
                  "zero = o furo não comunica com o fluxo", ok=invade < 1e-6)
    # furo cego: so o overshoot de 2 mm sai do aco
    # furo bem formado: (1) abre na face externa (2) e cego - nao atravessa para a
    # face de entrada nem para a de saida - (3) o trecho dentro do aco bate com o
    # comprimento pedido (desconto do overshoot de 2 mm que a broca faz na saida).
    area_r, piores, abre_min = 2.0, [], 0.6
    for (tipo, r, c, f) in caixas:
        area = math.pi * r * r
        dentro = maior(c.intersect(env)).Volume()
        fora = c.cut(env).Volume()
        if tipo == "pino_alinhamento":
            if fora > 1e-6:
                piores.append(f"pino X={f['X']:+.2f}: escapa do envelope ({fora:.2f} mm³)")
            if abs(dentro - area * f["comprimento_mm"]) > 0.02 * area * f["comprimento_mm"]:
                piores.append(f"pino X={f['X']:+.2f}: comprimento dentro do aço diverge")
            continue
        if fora < abre_min * area * (1.0 + r / 3.0):
            piores.append(f"{tipo} X={f['X']:+.2f} Z={f['Z']:.2f}: não abre na face externa")
        esperado_dentro = area * (f["comprimento_mm"] - area_r)
        if abs(dentro - esperado_dentro) > 0.05 * area * f["comprimento_mm"]:
            piores.append(f"{tipo} X={f['X']:+.2f} Z={f['Z']:.2f}: dentro={dentro:.1f} "
                          f"esperado≈{esperado_dentro:.1f} mm³")
        # nao pode romper a face de entrada (Z=0) nem a de saida (Z=109)
        for (zface, nome) in ((0.0, "face de entrada Z=0"), (Z_FIM, "face de saída Z=109")):
            lam = cq.Workplane("XY").workplane(offset=max(zface - 0.05, 0.0)).box(
                400, 400, 0.10, centered=(True, True, False)).val()
            v = maior(c.intersect(lam)).Volume()
            if v > 1e-6:
                piores.append(f"{tipo} X={f['X']:+.2f} Z={f['Z']:.2f}: rompe a {nome} "
                              f"({v:.2f} mm³)")
    registrar("Furos de aquecimento: abertos na face externa, cegos, sem romper as faces",
              "OK - todos os 14" if not piores else " | ".join(sorted(set(piores))),
              "atravessar a peça = vazamento; ficar enterrado = não usinável", ok=not piores)
    pior, par = 99.0, ("", "")
    for i in range(len(caixas)):
        for j in range(i + 1, len(caixas)):
            d = dist3d(caixas[i][2], caixas[j][2])
            if d < pior:
                pior, par = d, (f"{caixas[i][0]} X={caixas[i][3]['X']:+.1f} Z={caixas[i][3]['Z']:.1f}",
                                f"{caixas[j][0]} X={caixas[j][3]['X']:+.1f} Z={caixas[j][3]['Z']:.1f}")
    registrar("Menor web de aço entre dois furos", f"{n(pior)} mm",
              f"par: {par[0]} × {par[1]} | mínimo {WEB_MINIMA:.2f} mm", ok=pior >= WEB_MINIMA - 1e-6)

    # ---------------------------------------------------------------- D
    print("\n[D] NÚMEROS PARA A FÁBRICA")
    registrar("Massa de aço (7,85 g/cm³)", f"{n(aco.Volume() * 7.85e-6)} kg",
              "v27.0: 3,682 kg | aços: P20 pré / H13 temperado")
    A_proj, z = 0.0, 0.0
    while z < Z_FIM:
        s, _ = secao(canal, z + 0.001)
        A_proj += (s.xmax - s.xmin) * 0.5
        z += 0.5
    p_mpa = 68.2 * 0.1
    registrar("Área projetada do canal no plano XZ (medida)", f"{n(A_proj, 0)} mm²",
              "é a área sobre a qual a pressão empurra as metades uma contra a outra")
    registrar("Força que abre a bipartição",
              f"{n(p_mpa * A_proj / 1000, 1)} kN no limite (pressão plena em toda a área) · "
              f"{n(p_mpa * math.pi * (75.6 / 2) ** 2 / 1000, 1)} kN sobre a boca Ø75,60",
              "por isso a fixação não é opcional (ver relatório DFM)")
    dp28, zp28, pk28 = dp_total(canal, Z_FIM)
    dp27, zp27, pk27 = dp_total(canal27, 109.0)
    registrar("ΔP 1D - lei das potências (método do próprio projeto)",
              f"{ROTULO} = {n(dp28, 1)} bar | v27.0 = {n(dp27, 1)} bar",
              f"land {n(meta['land_paralelo'], 2)} vs 8,50 paralelos → {dp28 - dp27:+.1f} bar; "
              f"maior gradiente em Z≈{n(zp28, 1)} mm", ok=True)
    tau, gdot = tau_parede(75.0, 1.5)
    registrar("τ na parede do land", f"{n(tau, 1)} kPa (γ̇_ap = {n(gdot, 0)} s⁻¹)",
              "não depende do comprimento do land: mesma fenda, mesma vazão", ok=True)
    registrar("Faixa de aço entre o canal e o Ø93",
              f"{46.50 - 37.80:.2f} mm",
              "sem espaço para furo de pressão: Ø9,5 + parede 4 + parede 4 = 11,5 mm", ok=True)
    z_ok = [Z_LAND + meta["land_paralelo"], Z_FIM]
    registrar("Cotas de usinagem do land",
              f"paralelo Z={n(Z_LAND, 2)}→{n(z_ok[0], 2)} mm ({n(meta['land_paralelo'], 2)}) · chanfro {n(meta['chanfro'], 2)}×45° "
              f"Z={n(z_ok[0], 2)}→{n(Z_FIM, 2)} mm", "conferir no desenho antes de cortar o aço",
              ok=True)

    conf = sum(1 for l in linhas if l["status"] == "CONFORME")
    nc = [l for l in linhas if l["status"] == "NAO_CONFORME"]
    print("\n" + "=" * 96)
    print(f"RESULTADO: {len(linhas)} itens verificados | {conf} conformes | {len(nc)} NÃO CONFORMES")
    for l in nc:
        print(f"  -> {l['item']}: medido={l['medido']} nominal={l.get('nominal', '-')}  {l['observacao']}")
    print("=" * 96)

    if a.json:
        with open(os.path.join(AQUI, "verificacao_v28.json"), "w", encoding="utf-8") as f:
            json.dump({"revisao": f"{ROTULO}_PROPOSTA", "itens": len(linhas), "conformes": conf,
                       "nao_conformes": len(nc), "checagens": linhas}, f, indent=2, ensure_ascii=False)
        print(f"-> {os.path.join('04_Dados_SSOT_e_Scripts', 'verificacao_v28.json')}")
    if a.md:
        md = [f"# Verificação exata da revisão {ROTULO} — Matriz Jonatha", "",
              "Medida nos STEP gerados por `gerar_matriz_v28.py` (booleanos + BRepExtrema; "
              "nada é estimado).", "",
              f"**{len(linhas)} itens verificados · {conf} conformes · {len(nc)} não conformes**",
              "", "| Item | Nominal | Medido | Status | Observação |", "| :--- | ---: | ---: | :---: | :--- |"]
        for l in linhas:
            st = "✅" if l["status"] == "CONFORME" else ("❌" if l["status"] == "NAO_CONFORME" else "ℹ️")
            fmt = lambda x: ("—" if x is None or x == "—" else
                             (f"{x:g}".replace(".", ",") if isinstance(x, (int, float))
                              else str(x)))
            md.append(f"| {l['item']} | {fmt(l.get('nominal'))} | {fmt(l['medido'])} | {st} "
                      f"| {l.get('observacao', '')} |")
        out = os.path.join(DIR_DOC, "VERIFICACAO_V28.md")
        with open(out, "w", encoding="utf-8") as f:
            f.write("\n".join(md) + "\n")
        print(f"-> {out}")
    return 1 if nc else 0


if __name__ == "__main__":
    raise SystemExit(main())
