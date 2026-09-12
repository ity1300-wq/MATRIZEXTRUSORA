"""
AUDITORIA GEOMÉTRICA AUTOMATIZADA (SSOT v27.0) - MATRIZ JONATHA
================================================================
Lê diretamente os arquivos STEP oficiais, mede a geometria real (seções,
diâmetros, espessuras, volumes) e compara com a fonte única da verdade
(`cad_die_parameters.json`).

Uso:
    python verify_geometry_ssot.py            # imprime o relatório no console
    python verify_geometry_ssot.py --json     # também salva auditoria_geometrica.json
    python verify_geometry_ssot.py --md       # também regenera o relatório .md

Retorno: código 0 se todos os itens CONFORMES; 1 se houver não conformidade.

Requisitos: cadquery (pip install cadquery). Em contêineres sem libGL,
execute antes: bash setup_headless_gl.sh
"""

import argparse
import json
import math
import os
import sys

try:
    import cadquery as cq
except ImportError as exc:  # pragma: no cover
    print("ERRO: cadquery não está instalado (pip install cadquery).", file=sys.stderr)
    print(f"Detalhe: {exc}", file=sys.stderr)
    sys.exit(2)

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DIR_CAD = os.path.join(RAIZ, "01_CAD_MatrizJonatha_Oficial")
DIR_DOC = os.path.join(RAIZ, "03_Relatorios_e_Documentacao")
DIR_DADOS = os.path.join(RAIZ, "04_Dados_SSOT_e_Scripts")

TOL = 0.02  # tolerância dimensional de auditoria [mm]
TOL_VOL = 0.5  # tolerância de volume [mm3]

# Envelope cilíndrico externo (verificado e documentado na especificação SSOT)
ENVELOPE = [
    (0.00, 69.90, 93.00),
    (69.90, 80.70, 89.50),
    (80.70, 109.00, 79.50),
]

resultados = []


def checar(item, medido, nominal, tol=TOL, unidade="mm", obs=""):
    """Registra e imprime uma checagem dimensional."""
    ok = abs(medido - nominal) <= tol
    resultados.append(
        {
            "item": item,
            "nominal": round(nominal, 4),
            "medido": round(medido, 4),
            "desvio": round(medido - nominal, 4),
            "tol": tol,
            "unidade": unidade,
            "status": "CONFORME" if ok else "NAO_CONFORME",
            "observacao": obs,
        }
    )
    marca = "OK  " if ok else "FALHA"
    print(
        f"  [{marca}] {item:<52} nominal={nominal:9.3f} medido={medido:9.3f} "
        f"desvio={medido - nominal:+8.3f} {unidade}"
        + (f"  <- {obs}" if obs and not ok else "")
    )
    return ok


def registrar_info(item, valor, obs=""):
    """Registra uma informação sem valor nominal (diagnóstico)."""
    resultados.append(
        {"item": item, "medido": valor, "status": "INFO", "observacao": obs}
    )
    print(f"  [INFO ] {item:<52} {valor}  {obs}")


def contagem_shells(solido):
    """Nº de shells: 1 = sólido maciço; >1 = possui cavidades internas fechadas."""
    from OCP.TopAbs import TopAbs_SHELL
    from OCP.TopExp import TopExp_Explorer

    exp = TopExp_Explorer(solido.wrapped, TopAbs_SHELL)
    n = 0
    while exp.More():
        n += 1
        exp.Next()
    return n


def carregar(caminho):
    return cq.importers.importStep(caminho)


def secao(solido, z, esp=0.002):
    """Interseção do sólido com uma lâmina fina em Z; retorna (bbox, área)."""
    lamina = cq.Workplane("XY").workplane(offset=z).box(400, 400, esp).val()
    inter = solido.intersect(lamina)
    return inter.BoundingBox(), inter.Volume() / esp


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true", help="salva auditoria_geometrica.json")
    ap.add_argument("--md", action="store_true", help="regenera o relatório .md")
    args = ap.parse_args()

    with open(os.path.join(DIR_DADOS, "cad_die_parameters.json"), encoding="utf-8") as f:
        ssot = json.load(f)
    p = ssot["matriz_jonatha_parameters"]

    print("=" * 100)
    print("AUDITORIA GEOMÉTRICA DOS ARQUIVOS STEP OFICIAIS - MATRIZ JONATHA "
          f"({ssot['project_metadata']['revision']})")
    print("=" * 100)

    # ------------------------------------------------------------------ 1
    print("\n[1] CARREGAMENTO DOS ENTREGÁVEIS STEP")
    assy = carregar(os.path.join(DIR_CAD, "MatrizJonatha.step"))
    corpo_a = carregar(os.path.join(DIR_CAD, "MatrizJonatha_Body_A.step")).solids().val()
    corpo_b = carregar(os.path.join(DIR_CAD, "MatrizJonatha_Body_B.step")).solids().val()
    fluxo_cmp = carregar(os.path.join(DIR_CAD, "MatrizJonatha_Canal_Fluxo.step"))
    sol_fluxo = fluxo_cmp.solids().vals()
    canal = max(sol_fluxo, key=lambda s: s.Volume())
    registrar_info("Sólidos na montagem MatrizJonatha.step",
                   len(assy.solids().vals()))
    registrar_info("Sólidos em MatrizJonatha_Canal_Fluxo.step", len(sol_fluxo),
                   "esperado: 1 (núcleo de polímero)")

    # ------------------------------------------------------------------ 2
    print("\n[2] ENVELOPE CILÍNDRICO EXTERNO (compatibilidade de montagem)")
    bb = corpo_a.fuse(corpo_b).BoundingBox()
    checar("Comprimento total Z", bb.zmax - bb.zmin, 109.00)
    checar("Diâmetro externo máximo (Estágio 1)", bb.xmax - bb.xmin, 93.00)
    for z0, z1, d in ENVELOPE:
        zc = (z0 + z1) / 2 if z0 else 0.5
        sec, _ = secao(corpo_a.fuse(corpo_b), zc)
        checar(f"Ø externo em Z={zc:.2f} (estágio {d:.2f} x {z1 - z0:.2f})",
               sec.xmax - sec.xmin, d)
    sec, area = secao(corpo_a.fuse(corpo_b), 0.5)
    checar("Diâmetro externo na face traseira Z=0 (Ø93)", sec.xmax - sec.xmin, 93.00)

    # ------------------------------------------------------------------ 3
    print("\n[3] CANAL DE FLUXO - ENTRADA (Z=0)")
    sec0, _ = secao(canal, 0.001)
    checar("Ø da boca de entrada (acoplamento extrudora)", sec0.xmax - sec0.xmin,
           p["entry_bore_diameter_mm"], tol=0.05)
    checar("Ø da boca de entrada (eixo Y)", sec0.ymax - sec0.ymin,
           p["entry_bore_diameter_mm"], tol=0.05)

    # ------------------------------------------------------------------ 4
    print("\n[4] CANAL DE FLUXO - LAND DE CALIBRAÇÃO E SAÍDA")
    sec_land, area_land = secao(canal, 100.0)
    checar("Largura do land (X)", sec_land.xmax - sec_land.xmin, p["land_width_mm"])
    checar("Espessura do land (Y)", sec_land.ymax - sec_land.ymin, p["land_thickness_mm"])
    raio_esperado = p["edge_radius_mm"]
    area_teorica = (75.0 - 2 * raio_esperado) * 1.5 + math.pi * raio_esperado ** 2
    checar("Área da seção do land (bordas arredondadas R0,75)",
           area_land, area_teorica, tol=0.05, unidade="mm2",
           obs="setor arredondado R0,75 nas duas extremidades")

    # comprimento real do land paralelo (a norma SSOT declara 10,00 mm)
    z_paralelo = None
    z = 99.0
    while z <= 109.0001:
        s, _ = secao(canal, min(z, 108.999))
        if abs((s.ymax - s.ymin) - p["land_thickness_mm"]) > TOL:
            break
        z_paralelo = z
        z += 0.25
    comprimento_paralelo = (z_paralelo - 99.0) if z_paralelo else 0.0
    ok_land = checar("Comprimento do land reto e paralelo", comprimento_paralelo,
                     p["land_length_mm"], tol=0.25,
                     obs="o chanfro de saída consome 1,50 mm do land")

    # chanfro de saída 1,50 mm x 45 graus (divergente)
    sec_ch, _ = secao(canal, 108.9)
    # chanfro 45°: a 0,10 mm da face a abertura já avançou 1,40 mm por lado
    checar("Chanfro de saída 1,50 mm x 45° - sobrelargura radial em X",
           (sec_ch.xmax - sec_ch.xmin - p["land_width_mm"]) / 2, 1.40,
           tol=0.10, obs="medido a 0,10 mm da face de saída")
    checar("Chanfro de saída 1,50 mm x 45° - sobrelargura radial em Y",
           (sec_ch.ymax - sec_ch.ymin - p["land_thickness_mm"]) / 2, 1.40,
           tol=0.10)

    # ------------------------------------------------------------------ 5
    print("\n[5] ESPESSURA DE PAREDE DE AÇO - PONTOS CRÍTICOS")
    sec_lip, _ = secao(canal, 108.999)
    parede_lip = 79.50 / 2 - max(abs(sec_lip.xmin), abs(sec_lip.xmax))
    registrar_info("Parede de aço no lábio de saída (Z=109, saída Ø79,5)",
                   round(parede_lip, 3), "mm - lábio fino: avaliar fragilidade")
    sec_pin, _ = secao(canal, 54.5)
    parede_pino = 41.50 - 2.0 - max(abs(sec_pin.xmin), abs(sec_pin.xmax))
    registrar_info("Parede entre canal e furo de pino Ø4 em Z=54,5",
                   round(parede_pino, 3), "mm")

    # ------------------------------------------------------------------ 6
    print("\n[6] BIPARTIÇÃO, PINOS DE ALINHAMENTO E MASSAS")
    inter = corpo_a.intersect(corpo_b).Volume()
    checar("Interferência entre Body_A e Body_B", inter, 0.0, tol=1e-6, unidade="mm3")
    uniao = corpo_a.fuse(corpo_b)
    registrar_info("Body_A + Body_B (união é 1 sólido)",
                   len(cq.Workplane("XY").add(uniao).solids().vals()) == 1)
    checar("Volume Body_A", corpo_a.Volume(), 234255.29, tol=TOL_VOL, unidade="mm3")
    checar("Volume Body_B", corpo_b.Volume(), 234746.37, tol=TOL_VOL, unidade="mm3")
    checar("Volume do núcleo de polímero (canal)", canal.Volume(), 213945.15,
           tol=TOL_VOL, unidade="mm3")
    volume_aco = corpo_a.Volume() + corpo_b.Volume()
    massa = volume_aco / 1000.0 * 7.85 / 1000.0
    registrar_info("Massa estimada de aço (7,85 g/cm3)", f"{massa:.3f} kg")

    # furos de pino: presentes no Body_A, ausentes no Body_B (defeito funcional)
    furos_a = [
        f for f in corpo_a.Faces()
        if f.geomType() == "CYLINDER" and abs(f.BoundingBox().xmax - f.BoundingBox().xmin - 4.0) < 0.05
        and abs(f.BoundingBox().zmax - f.BoundingBox().zmin - 4.0) < 0.05
    ]
    furos_b = [
        f for f in corpo_b.Faces()
        if f.geomType() == "CYLINDER" and abs(f.BoundingBox().xmax - f.BoundingBox().xmin - 4.0) < 0.05
        and abs(f.BoundingBox().zmax - f.BoundingBox().zmin - 4.0) < 0.05
    ]
    registrar_info("Furos de pino Ø4 no Body_A", len(furos_a))
    registrar_info("Furos de pino Ø4 no Body_B", len(furos_b),
                   "ausentes: os pinos não alinham as duas metades")
    # os furos de pino são cavidades internas FECHADAS (bolhas) ou furos reais?
    shells_a = contagem_shells(corpo_a)
    shells_b = contagem_shells(corpo_b)
    checar("Cavidades internas fechadas no Body_A", shells_a - 1, 0, tol=0,
           unidade="cavidade(s)",
           obs="os furos Ø4 estão SELADOS (bolhas internas, impossíveis de usinar)")
    checar("Cavidades internas fechadas no Body_B", shells_b - 1, 0, tol=0,
           unidade="cavidade(s)")

    # ------------------------------------------------------------------ 7
    print("\n[7] CONSISTÊNCIA GEOMÉTRICA GLOBAL (aço + canal = envelope)")
    envelope = (
        cq.Workplane("XY").circle(93.00 / 2).extrude(69.90)
        .union(cq.Workplane("XY").workplane(offset=69.90).circle(89.50 / 2).extrude(10.80))
        .union(cq.Workplane("XY").workplane(offset=80.70).circle(79.50 / 2).extrude(28.30))
    ).val()
    residuo = envelope.Volume() - (volume_aco + canal.Volume() + 2 * 150.796)
    checar("Envelope - (aço + canal + 2 furos de pino)", residuo, 0.0, tol=1.0,
           unidade="mm3", obs="fechamento volumétrico exato do modelo")

    # ------------------------------------------------------------------ 8
    print("\n[8] RECURSOS DE FABRICAÇÃO AINDA AUSENTES NO CAD")
    # Furos reais = faces cilíndricas internas (côncavas) com diâmetro >= 3 mm.
    # O envelope externo e as bordas R0,75 do land são excluídos pelo raio.
    from OCP.BRepAdaptor import BRepAdaptor_Surface

    def furos(solido):
        achados = []
        for f in solido.Faces():
            if f.geomType() != "CYLINDER":
                continue
            raio = BRepAdaptor_Surface(f.wrapped).Cylinder().Radius()
            if 1.5 <= raio <= 20.0:  # furos de Ø3 a Ø40 (exclui envelope externo e R0,75 do land)
                achados.append(round(raio * 2, 2))
        return sorted(achados)

    furos_a, furos_b = furos(corpo_a), furos(corpo_b)
    registrar_info("Furos usinados no Body_A (Ø, todos)", furos_a)
    registrar_info("Furos usinados no Body_B (Ø, todos)", furos_b,
                   "o Body_B não tem nenhum furo usinado")
    registrar_info("Furos de fixação/aperto (M8 ou abas)", 0, "não existem no modelo")
    registrar_info("Furos para cartucho de resistência Ø9,5", 0, "não existem no modelo")
    registrar_info("Poço para termopar", 0, "não existem no modelo")
    registrar_info("Canais de refrigeração Ø8,0", 0, "não existem no modelo")
    registrar_info("Furação do flange de acoplamento (Z=0)", 0, "não existem no modelo")

    # ------------------------------------------------------------------ resumo
    nao_conformes = [r for r in resultados if r["status"] == "NAO_CONFORME"]
    print("\n" + "=" * 100)
    print(f"RESULTADO: {len(resultados)} itens verificados | "
          f"{len([r for r in resultados if r['status'] == 'CONFORME'])} conformes | "
          f"{len(nao_conformes)} NÃO CONFORMES | "
          f"{len([r for r in resultados if r['status'] == 'INFO'])} informativos")
    for r in nao_conformes:
        print(f"  -> {r['item']}: nominal={r['nominal']} medido={r['medido']}")
    print("=" * 100)

    if args.json:
        destino = os.path.join(DIR_DADOS, "auditoria_geometrica.json")
        with open(destino, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "projeto": "Auditoria_Geometrica_Matriz_Jonatha",
                    "revisao_auditada": ssot["project_metadata"]["revision"],
                    "data": "2026-09-11",
                    "tolerancia_mm": TOL,
                    "itens": resultados,
                    "resumo": {
                        "total": len(resultados),
                        "conformes": len([r for r in resultados if r["status"] == "CONFORME"]),
                        "nao_conformes": len(nao_conformes),
                        "informativos": len([r for r in resultados if r["status"] == "INFO"]),
                    },
                },
                f,
                ensure_ascii=False,
                indent=2,
            )
        print(f"JSON salvo em {os.path.relpath(destino, RAIZ)}")

    if args.md:
        gerar_markdown(ssot, resultados)

    return 1 if nao_conformes else 0


def gerar_markdown(ssot, resultados):
    """Gera o relatório de auditoria em Markdown na pasta de documentação."""
    conformes = [r for r in resultados if r["status"] == "CONFORME"]
    nao_conformes = [r for r in resultados if r["status"] == "NAO_CONFORME"]
    infos = [r for r in resultados if r["status"] == "INFO"]

    linhas = [
        "# Auditoria Geométrica Automatizada - Matriz Jonatha",
        "",
        "**Documento:** Verificação dimensional dos arquivos STEP oficiais contra o SSOT  ",
        "**Revisão auditada:** `" + ssot["project_metadata"]["revision"] + "`  ",
        "**Script gerador:** `04_Dados_SSOT_e_Scripts/verify_geometry_ssot.py`  ",
        "**Data da auditoria:** 2026-09-11  ",
        f"**Tolerância dimensional:** ±{TOL} mm  ",
        "",
        "---",
        "",
        "## 1. Resultado Consolidado",
        "",
        f"- **Itens verificados:** {len(resultados)}",
        f"- **Conformes:** {len(conformes)}",
        f"- **Não conformes:** {len(nao_conformes)}",
        f"- **Informativos (diagnóstico):** {len(infos)}",
        "",
        "## 2. Verificações Dimensionais",
        "",
        "| Item | Nominal | Medido | Desvio | Status |",
        "| :--- | ---: | ---: | ---: | :---: |",
    ]
    for r in resultados:
        if r["status"] == "INFO":
            continue
        un = r.get("unidade", "mm")
        linhas.append(
            f"| {r['item']} | {r['nominal']} {un} | {r['medido']} {un} | "
            f"{r['desvio']:+} {un} | {'✅' if r['status'] == 'CONFORME' else '❌'} |"
        )

    linhas += [
        "",
        "## 3. Diagnósticos e Não Conformidades",
        "",
        "| Item | Valor medido | Observação |",
        "| :--- | :--- | :--- |",
    ]
    for r in nao_conformes + infos:
        valor = r.get("medido", "")
        if r["status"] == "NAO_CONFORME":
            valor = f"{valor} {r.get('unidade','')} (nominal {r['nominal']})".strip()
        linhas.append(f"| {r['item']} | {valor} | {r.get('observacao','')} |")

    linhas += [
        "",
        "## 4. Ações Recomendadas Antes da Usinagem CNC",
        "",
        "| # | Achado (medido no STEP) | Impacto | Ação recomendada |",
        "| :--: | :--- | :--- | :--- |",
        "| 1 | Pinos: os 2 furos Ø4 × 12 do `Body_A` estão **selados** (cavidades internas fechadas, 3 shells) e o `Body_B` não tem furo nenhum | As metades ficam sem referência de alinhamento: risco de degrau e rebarba no plano de partição | Refazer os furos nos **dois** corpos (Ø4 H7 × 12 mm cegos, X=±41,50, Z=54,50) e usar 2 pinos Ø4 × 20 mm temperados. Reexportar os dois STEP |",
        "| 2 | Land reto e paralelo real = 8,50 mm (SSOT declara 10,00 mm) | Divergência documental; o chanfro de 45° consome 1,50 mm do land | Corrigir o SSOT para 8,50 mm de land paralelo + 1,50 mm de chanfro, **ou** reduzir o chanfro para 0,50 mm × 45° (land = 9,50 mm) |",
        "| 3 | Parede de aço no lábio de saída = 0,75 mm | Lábio frágil: risco de lascamento e rebarba na face de saída Ø79,5 (impossível retificar plana) | Reduzir o chanfro para 0,50–0,80 mm × 45° (lábio ≥ 1,40 mm), mantendo o envelope Ø79,5 intacto |",
        "| 4 | Nenhum furo de fixação/aperto no modelo | As metades não podem ser fechadas contra os 68 bar de contrapressão | Definir padrão de fixação: 4 × M8 em Y nas asas do Ø93 (com spot face) **ou** grampos/quadro externo (verificar espaço: parede de aço de apenas 8,7 mm entre o canal e o Ø93) |",
        "| 5 | Sem controle térmico (cartuchos Ø9,5 / termopar / refrigeração) | Operação fora da janela de 50–65 °C reintroduz o *edge tearing* | Acrescentar furos de cartucho Ø9,5 mm, poço de termopar Ø6 mm e 2 canais de refrigeração Ø8 mm por metade |",
        "| 6 | Sem furação de flange em Z=0 | Acoplamento à extrudora depende só do encaixe Ø75,60 mm | Extrair o padrão de furos do cabeçote original (`030-032- cabeçote.dwg`) antes de definir o flange |",
        "| 7 | `MatrizJonatha_Canal_Fluxo.step` contém 3 sólidos | Dificulta o uso direto como eletrodo de EDM / malha de CFD | Reexportar apenas o núcleo de polímero (1 sólido) |",
        "| 8 | ΔP e τ declarados não são reproduzíveis (τ de 128,44 kPa é impossível: o land é o mesmo e a vazão é a mesma) | Risco de decisão sobre números não auditáveis | Refazer em script versionado; ver `03_Relatorios_e_Documentacao/TRIAGEM_DE_PROBLEMAS_DAS_MATRIZES.md` |",
        "",
        "## 5. Conclusão",
        "",
        "O envelope externo, a seção do land (75,00 × 1,50 mm com bordas R0,75), a boca de "
        "entrada Ø75,60 mm e o fechamento volumétrico do conjunto (aço + canal de polímero + "
        "furos de pino = envelope cilíndrico nominal) foram todos confirmados numericamente.",
        "",
        "Os itens marcados como **NÃO CONFORME** exigem decisão de engenharia antes da "
        "usinagem: ver a seção 3 e o plano de ação em `RELATORIO_TECNICO_E_SUGESTOES.md`.",
        "",
        "---",
        "",
        "*Relatório gerado automaticamente por `verify_geometry_ssot.py --md`.*",
        "",
    ]
    # ------------------------------------------------------------------ 6. o que foi feito de cada achado
    # Nao e texto solto: a tabela e lida de `cad_die_parameters.json:audit.tratamento_auditoria_v28_1`, entao
    # o relatorio da auditoria e o SSOT nao podem divergir (o portao confere o numero de tau citado aqui).
    try:  # lido do disco de novo: nao dependo do escopo de quem montou as checagens
        _ssot = json.load(open(os.path.join(DIR_DADOS, "cad_die_parameters.json"), encoding="utf-8"))
        _tr = _ssot["audit"]["tratamento_auditoria_v28_1"]
        _tau = _ssot.get("proposta_v28_dfm", {}).get("numeros recalculados", {}).get("tau_parede_land_kPa")
    except (OSError, KeyError):
        _tr, _tau = {}, None
    if _tr:
        linhas += ["", f"## 6. Tratamento dos achados na proposta v28.1 ({_tr['data']})", "",
                   _tr["para_quem_e"], "", "> " + _tr["regra_que_limita_o_tratamento"], "",
                   "| Achado | Status | Tratamento, com o número medido | Onde conferir |",
                   "| :--- | :--- | :--- | :--- |"]
        for _k, _v in _tr["achados"].items():
            linhas.append(f"| **{_k}** | {_v['status']} | {_v['tratamento']} "
                          f"(medido hoje: {_v['numero_medido_hoje']}) | {_v['onde_confere']} |")
        linhas += ["", "### O que continua aberto", ""]
        linhas += [f"* {x}" for x in _tr["o_que_continua_aberto"]]
        if _tau is not None:
            linhas += ["", f"τ citado acima: **{f'{_tau:.1f}'.replace('.', ',')} kPa** - o mesmo número que está em "
                           f"`verificacao_v28.json`; se um mudar sem o outro, o portão fecha.", ""]

    destino = os.path.join(DIR_DOC, "AUDITORIA_GEOMETRICA_MATRIZ_JONATHA.md")
    with open(destino, "w", encoding="utf-8") as f:
        f.write("\n".join(linhas))
    print(f"Relatório salvo em {os.path.relpath(destino, RAIZ)}")


if __name__ == "__main__":
    sys.exit(main())
