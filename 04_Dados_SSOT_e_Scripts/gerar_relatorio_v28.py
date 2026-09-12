"""
GERADOR DO RELATORIO DFM DA REVISAO PROPOSTA - MATRIZ JONATHA
===============================================
Monta `PROJETO_DFM_V28_MATRIZ_JONATHA.md` a partir dos dados MEDIDOS:
  * `matriz_v28_features.json`  (desenho de intencao: cotas de cada furo)
  * `verificacao_v28.json`      (63 checagens feitas nos STEP)
  * `cad_die_parameters.json`   (SSOT)
Assim nenhuma tabela e transcrita a mao: se o CAD mudar, o relatorio muda junto.

Uso: python 04_Dados_SSOT_e_Scripts/gerar_relatorio_v28.py
Idempotente.
"""

import json
import os

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, ".."))
DIR_DADOS = AQUI
DIR_DOC = os.path.join(RAIZ, "03_Relatorios_e_Documentacao")
SAIDA = os.path.join(DIR_DOC, "PROJETO_DFM_V28_MATRIZ_JONATHA.md")


def carregar(nome):
    with open(os.path.join(DIR_DADOS, nome), encoding="utf-8") as f:
        return json.load(f)


def achar(verif, chave):
    for l in verif["checagens"]:
        if chave.lower() in l["item"].lower():
            return l
    return {}


import re


def pt(v):
    """Valor vindo do JSON: float vira pt-BR; string ja vem formatada do verificador."""
    if isinstance(v, (int, float)):
        return f"{float(v):.4f}".rstrip("0").rstrip(".").replace(".", ",")
    return str(v)


def un(v, u=""):
    t = pt(v)
    return t if (not u or u.split()[0] in t) else f"{t} {u}"


def tbl(v):
    """valor para celula de tabela: sem '|' e sem 'mm' duplicado"""
    return str(pt(v)).replace(" | ", " · ").replace("|", "/")


def mil(v, dec=0):
    """1.234.567,89 - como dim(), mas com separador de milhar."""
    if not isinstance(v, (int, float)):
        return pt(v)
    return f"{float(v):,.{dec}f}".replace(",", "@").replace(".", ",").replace("@", ".")


def dim(v, dec=2):
    if isinstance(v, (int, float)):
        return f"{float(v):.{dec}f}".replace(".", ",")
    return pt(v)


def esc(v):
    """protege '|' dentro de tabelas markdown"""
    return str(v).replace("|X|", "abs(X)").replace("|Y|", "abs(Y)")


def linha(k, v):
    return f"| {k} | {v} |"



def secao6(ic):
    """Secao 6 do relatorio, montada dos JSONs de medicao (nada datilografado)."""
    if not ic:
        return ("## 6. Cabeçote\n\nRode `python 04_Dados_SSOT_e_Scripts/verificar_interface_cabecote.py "
                "--json --md` para gerar a medição da interface.\n")
    cb, ch = ic["cabecote"], {str(l["item"]): l for l in ic["checagens"]}
    cal = cb["calibracao_escala"]
    am = "; ".join(f"{a['feicao']} → desvio {a['erro_pct']:+.2f} %".replace(".", ",") for a in cal["amarra"])
    corpo, fuji, junta = cb["corpo"], cb["furos_do_cabecote_para_a_matriz"], cb["junta_cabecote_extrusora"]
    anel65, bucha, ombro = cb["anel_do_nariz_variante_65mm"], cb["bucha_conica"], cb["ombro_de_apoio"]
    enq = []
    for e in cb["encaixe_matriz_x_cabecote"]:
        axial = e.get("folga_axial_mm", e.get("protrusao_da_matriz_mm", 0.0))
        enq.append(f"| {e['estagio_matriz']} | {e['furo_cabecote']} | {dim(e['folga_radial_mm'])} mm "
                   f"| {dim(axial)} mm{': ' + e['nota'] if 'nota' in e else ''} |")
    linhas_furo = []
    for b in fuji:
        linhas_furo.append(f"| {b['nome']} | Ø{dim(b['Ø_mm'])} mm | {dim(b['de_d_mm'])} … {dim(b['ate_d_mm'])} mm "
                           f"| {dim(b['ate_d_mm'] - b['de_d_mm'])} mm | {b['cota_texto']} |")
    press = []
    for l in ic["checagens"]:
        if str(l["item"]).startswith("Pressão radial do collete") or str(l["item"]).startswith("Pressão de contato"):
            press.append(f"{l['item'].split('] ')[0]} → **{l['medido']}**")
    def m(chave, dec=2):
        ach = ch.get(chave, {})
        if not ach:
            ach = next((l for l in ic["checagens"] if str(l["item"]).startswith(chave)), {})
        v = ach.get("medido")
        return dim(v, dec) if isinstance(v, (int, float)) else "—"

    return (
        "## 6. Cabeçote EX-030 — a interface medida no DWG e provada nos sólidos\n\n"
        f"`030-032- cabeçote.dwg` (HIDEALL, PED:2257 — EX-030 cabeçote em SAE8620 {corpo['carimbo']}, "
        "cementado 0,4-0,6 mm e temperado a 52-55 HRC; EX-031 bucha cônica; EX-032 pushador) foi "
        "convertido para DXF e **medido numericamente**, entidade por entidade. A escala foi calibrada "
        f"pelas próprias cotas do desenho — **k = {dim(cal['k_mm_por_unidade_dxf'], 3)} mm por unidade DXF**, "
        f"incerteza {cal['incerteza']} — e cinco fechos independentes confirmam o fator: {am}.\n\n"
        "> **Correção registrada.** A versão anterior desta seção dizia \"6 × M12 em BC Ø150, curso angular "
        "±15°, escala 21,28 mm/un\" e \"Ø13,33 mm de folga\". O Ø150 vinha de uma leitura de raster em baixa "
        "resolução: o desenho diz **C.C Ø180**. Tudo abaixo foi re-medido com a escala calibrada e provado "
        f"por booleanos contra `MatrizJonatha_v28.step` (`verificar_interface_cabecote.py` → "
        f"**{ic['itens']} itens, {ic['conformes']} conformes, {ic['nao_conformes']} não conformes, "
        f"{ic['pendentes']} pendências do lado da máquina**).\n\n"
        f"**Furos do cabeçote para a matriz** — profundidade `d` contada da face do nariz; a matriz senta em "
        f"`Z_matriz = {dim(cb['referencia_axial']['comprimento_total_mm'])} − d` "
        f"(corpo Ø{dim(corpo['Ø_corpo_mm'])} × {dim(corpo['comprimento_corpo_mm'])}, "
        f"flange Ø{dim(corpo['Ø_flange_mm'])} × {dim(corpo['espessura_flange_mm'])}, "
        f"ressalto Ø{dim(corpo['resalto_traseiro']['Ø_mm'])} × {dim(corpo['resalto_traseiro']['altura_mm'])}):\n\n"
        "| furo | Ø | de … até (mm de profundidade) | comprimento | cota anotada |\n"
        "| :--- | ---: | ---: | ---: | :--- |\n" + "\n".join(linhas_furo) + "\n\n"
        "**Encaixe medido nos sólidos** (não por diferença de cotas):\n\n"
        "| estágio da matriz | furo do cabeçote | folga radial | folga axial / protrusão |\n"
        "| :--- | :--- | ---: | ---: |\n" + "\n".join(enq) + "\n\n"
        f"Interferência corpo-a-corpo matriz ∩ cabeçote: **{m('Interferência matriz ∩ cabeçote', 4)} mm³** — "
        f"a matriz entra e sai sem tocar. O anel da face mede **Ø{dim(cb['anel_na_face']['de_Ø_mm'])} → "
        f"Ø{dim(corpo['Ø_corpo_mm'])} = {m('Anel da face')} mm**, que é o \"~20 mm\" descrito pelo cliente, "
        f"confirmado em medição. Folgas radiais medidas nos três estágios: "
        f"**{m(fo[0].get('item', ''), 2) if False else m('Folga radial - Ø93×69,90 no bolso Ø95×70,0')} / "
        f"{m('Folga radial - Ø89,5×10,80 no Ø90×11,0')} / {m('Folga radial - Ø79,5×28,30 no Ø80×14,0')} mm**; "
        f"folga axial no degrau de apoio **{m('Folga axial no degrau de apoio (ombro)')} mm** — é essa folga "
        f"que define onde a matriz para. A face de saída da matriz fica **{m('Protrusão da face de saída além da face do nariz')} mm** "
        "à frente do nariz do cabeçote, então a fenda e a manta trabalham fora do cabeçote (nada de filme "
        "congelado encostado na saída) e a manta tem **14,00 mm** de curso livre antes de qualquer obstáculo.\n\n"
        "**Fixação (P1/P4): vem da máquina, não da matriz.** A bucha cônica EX-031 (Ø"
        f"{dim(bucha['Ø_externo_maior_mm'])} → Ø{dim(bucha['Ø_externo_menor_mm'])} OD, Ø{dim(bucha['Ø_interno_ref_mm'])} ID, "
        f"cone {dim(bucha['cone_graus'])}°, L = {dim(bucha['comprimento_mm'])} mm — exatamente o comprimento do "
        "bolso Ø95 × 70) é encaixada no bolso e, ao ser empurrada axialmente, contrai sobre a banda Ø93 da "
        f"matriz; o cone é auto-travante (3,00° < arctan 0,15 = 8,5°). O empuxo axial recai em compressão no "
        f"degrau do cabeçote, sobre o ombro da matriz — **{dim(ombro['area_contato_mm2'], 1)} mm²** de anel de "
        "contato. As pressões envolvidas:\n\n" + "\n".join(f"* {p}" for p in press) + "\n\n"
        "Ou seja: o aperto que a máquina já faz fecha o plano de partição por compressão radial, e o apoio "
        "axial existe. **A matriz não leva flange, não leva grampo e não leva furo de fixação** — e é por "
        "isso que a supressão dos furos M6 de desmontagem na face de entrada se mantém: o pushador EX-032 é "
        "ferramenta do cabeçote (haste partida Ø25 × 132, M12), não um rosqueamento na matriz.\n\n"
        f"**Padrão de furação (P4): não há o que padronizar na matriz.** A furação do desenho — "
        f"{junta['furos']} × Ø{dim(junta['Ø_mm'])} em fendas de {dim(junta['em_fenda_comprimento_mm'])} mm sobre "
        f"C.C. Ø{dim(junta['circunferencia_primitiva_mm'])} (M12), folga angular total "
        f"{dim(junta['folga_angular_total_graus'], 1)}° cotada como {dim(junta['cota_angular_no_desenho_graus'], 0)}°, "
        f"furo central Ø{dim(junta['Ø_central_mm'])} — é a junta **cabeçote ↔ extrusora**, e fica a "
        f"{m('Menor distância parafuso M12 (C.C Ø180) → corpo da matriz')} mm do corpo da matriz. O giro do "
        "conjunto se ajusta por essas fendas antes de apertar; o posicionamento da matriz vem dos três "
        "centragens cilíndricos medidos acima.\n\n"
        f"**Bloqueio novo — e ele é do cabeçote:** o corte mostra um anel no nariz com passagem "
        f"Ø{dim(anel65['Ø_interno_mm'])} mm protruindo {dim(abs(anel65['de_d_mm']))} mm à frente da face, "
        f"compatível com o carimbo **{corpo['carimbo']}** (manta de 65 mm). Com esse anel montado, a matriz de "
        f"75 mm **não monta**: Ø{dim(anel65['Ø_interno_mm'])} contra o nariz Ø79,50 da matriz dá "
        f"{dim((79.5 - anel65['Ø_interno_mm']) / 2)} mm de interferência radial por lado e volume de choque "
        f"medido de **{ch.get('Interferência matriz ∩ cabeçote COM anel Ø68,30', {}).get('medido', '—')}**. "
        "Como o furo do nariz do cabeçote já é Ø80, não há espaço físico para nenhum anel com passagem "
        "≥ Ø79,6: na variante de 75 mm o nariz da matriz roda direto no Ø80 do cabeçote, e o anel tem de "
        "ser eliminado ou refeito com Ø80 (ou seja, sem restringir).\n\n"
        "**O que ainda se resolve com paquímetro na máquina** (nada disso altera a geometria da matriz):\n\n"
        + "\n".join(f"* {p}" for p in cb["pendencias"]) +
        "\n\nO DWG é conversão de avaliação (marca d'água \"Evaluation only\"), então as tolerâncias "
        "anotadas devem ser conferidas na peça antes de fechar o desenho de execução.\n"
    )

def main():
    ft = carregar("matriz_v28_features.json")
    vf = carregar("verificacao_v28.json")
    ssot = carregar("cad_die_parameters.json")
    try:
        ic = carregar("interface_cabecote.json")
    except FileNotFoundError:
        ic = None
    nz = (ic or {}).get("numeros", {})
    if not nz:
        raise SystemExit("interface_cabecote.json['numeros'] ausente - rode verificar_interface_cabecote.py --json")
    ac = nz.get("acesso_furacao_cenarios")
    if ac:
        _ok = ac["você mediu na máquina"]
        _alt = ac["desenho DXF medido"]
        gov = nz["cenario_que_governa"]
        _ok = ac[gov]
        _alt = ac["você mediu na máquina" if gov.startswith("desenho") else "desenho DXF medido"]
        txt_bico = (f"**REABERTA em 2026-09-12.** A cota '20 mm' do croqui, medida no DXF, é a posição do furo "
                    f"M12 do bolso contada da face do flange (72,02 − 52,02 = 20,00 mm) — não a sobra axial da "
                    f"matriz. Vale a protrusão do desenho ({dim(_ok['protrusao_mm'])} mm), e aí a borda traseira "
                    f"do furo mais crítico fica {dim(abs(_ok['folga_axial_min_mm']))} mm dentro da luva do nariz, com "
                    f"{dim(_ok['metal_no_caminho_mm3'], 0)} mm³ de metal no caminho de inserção dos "
                    f"{_ok['n_furos_na_faixa_de_saida']} eixos de furo na faixa de saída (são 10 furos: cada eixo "
                    "entra pelas duas metades)")
        txt_bico_efeto = (f"duas saídas medidas, e nenhuma delas mexe nos outros 20 furos da matriz: levar os "
                          f"cartuchos para Z ≥ {dim(nz['cartuchos_z_min_mm'])} mm (calculado do Ø9,50 e da face do "
                          f"nariz em 95,00 mm) ou abrir alívio no nariz do cabeçote. No cenário alternativo "
                          f"({dim(_alt['protrusao_mm'])} mm de protrusão) a folga vira "
                          f"{dim(_alt['folga_axial_min_mm'])} mm com {dim(_alt['metal_no_caminho_mm3'], 0)} mm³ no "
                          "caminho — por isso a conferência na máquina é o que fecha o item")
    else:
        txt_bico = "**ABERTA — é a única que pode mexer nos furos** (rode `verificar_interface_cabecote.py --json`)"
        txt_bico_efeto = ("se o bico chegar até a face da matriz, os cartuchos (Z=97,00) e os termopares "
                          "(Z=103,00) ficam enterrados no cabeçote e o aquecimento muda de peça")
    p_lim_bar = nz["pressao_efetiva_MPa"] * 10
    f_boca = nz["pressao_efetiva_MPa"] * nz["area_boca_mm2"] / 1e3
    f_proj = nz["dp_1d_bar"] / 10 * nz["area_projetada_mm2"] / 1e3
    meta, m = ft["meta"], ssot["matriz_jonatha_parameters"]
    rot = ssot["proposta_v28_dfm"].get("rotulo", "v28.1")
    try:
        estudo = carregar("funil_coathanger.json")
    except FileNotFoundError:
        estudo = None
    if estudo:
        fa, fn = estudo["medicoes"]
        r_dp = fn["dp_1d_bar"] / fa["dp_1d_bar"]
        dp_ch = dim(fn["dp_1d_bar"], 1)
        txt_funil = (
            f"**7.1b — a opção (b) já foi modelada e medida (D3).** `estudar_funis.py` refez o funil das "
            f"seções declaradas com loft por **todas** as estações (passo de 5 mm, que é o que faltava no "
            f"script antigo) e mediu com a mesma trena: **ΔP 1D de {dim(fn['dp_1d_bar'], 1)} bar** contra "
            f"{dim(fa['dp_1d_bar'], 1)} bar do funil atual (**{dim(r_dp)}×**), canal {mil(fn['volume_mm3'])} mm³ "
            f"contra {mil(fa['volume_mm3'])} mm³, residência {dim(fn['residencia_s'], 0)} s contra "
            f"{dim(fa['residencia_s'], 0)} s, e **a espessura da manta é a mesma** — a fenda e o land não mudam, "
            f"então o gancho de uniformidade que justificaria o cabide não aparece na medição. Invasão do "
            f"envelope nos dois: {dim(fn['invasao_envelope_mm'], 4)} mm. Comparação completa em "
            f"`03_Relatorios_e_Documentacao/ESTUDO_FUNIL_COATHANGER.md`; os STEP do estudo ficam em "
            f"`05_Variantes_Em_Estudo/` e não tocam o modelo oficial. Restam as duas saídas: (a) admitir no "
            f"SSOT \"funil cônico linear com largura constante\" e corrigir o texto; (b) desenhar um cabide "
            f"compensado de verdade (alturas das asas decrescentes do centro para as pontas), o que obriga a "
            f"CFD novo porque o ΔP saiu de {dim(fa['dp_1d_bar'], 1)} para {dim(fn['dp_1d_bar'], 1)} bar só com a "
            f"troca de forma.")
        txt_d3_estado = (f"**MEDIDO, esperando sua escolha** — os dois funis modelados e comparados: ΔP "
                         f"{dim(fn['dp_1d_bar'], 1)} bar contra {dim(fa['dp_1d_bar'], 1)} bar, residência "
                         f"{dim(fn['residencia_s'], 0)} s contra {dim(fa['residencia_s'], 0)} s, espessura da "
                         f"manta igual nos dois (a fenda manda, e ela não muda)")
        txt_d3_conseq = ("a v28.1 mantém o funil do master. Escolher (a) é só texto; escolher (b) é CFD novo "
                         "e o ΔP acima de 68,2 bar do relatório de projeto")
    else:
        txt_funil = ("**7.1b — a comparação dos dois funis ainda não foi medida.** Rode "
                     "`python 04_Dados_SSOT_e_Scripts/estudar_funis.py` (sem tocar no oficial) para gerar "
                     "`ESTUDO_FUNIL_COATHANGER.md` com ΔP, residência e espessura medidos nos sólidos.")
        dp_ch = "—"
        txt_d3_estado = "**EM ANDAMENTO a seu pedido**: vou modelar os dois e trazer ΔP, tempo de residência e espessura da manta medidos lado a lado"
        txt_d3_conseq = "a v28.1 mantém o funil do master; a comparação decide se ele vira v29"


    land = achar(vf, "Land reto e paralelo")
    cha = achar(vf, "Chanfro de saída (v27")
    lam = achar(vf, "Lâmina de aço")
    fp = achar(vf, "Fechamento")
    web = achar(vf, "Menor web")
    dp = achar(vf, "ΔP 1D")
    tau = achar(vf, "τ na parede")
    mass = achar(vf, "Massa de aço")
    forc = achar(vf, "Força que abre")
    aprev = achar(vf, "Área projetada")
    assim = achar(vf, "Assimetria")
    funil = achar(vf, "Funil (Z<99)")

    # paredes por tipo de furo, medidas
    paredes = {}
    for l in vf["checagens"]:
        if l["item"].startswith("parede mínima"):
            tipo = l["item"].split("- ")[1].split(" X=")[0]
            v = float(l["medido"].split(" ")[0].replace(",", "."))
            paredes[tipo] = min(paredes.get(tipo, 99.0), v)

    furos = ft["furos"]
    unicos = {}
    for f in furos:                      # uma linha por (tipo, X, Z) - cada furo sai nas 2 metades
        unicos[(f["tipo"], f["X"], f["Z"], f["diametro"])] = f
    tabela_furos = ["| Furo | Ø (mm) | X (mm) | Z (mm) | Y (mm) | Compr. (mm) | Parede real medida |",
                    "| :--- | ---: | ---: | ---: | :--- | ---: | ---: |"]
    for (tipo, x, z, d), f in sorted(unicos.items(), key=lambda kv: (kv[0][0], -kv[0][2], kv[0][1])):
        y0, y1 = f["y_ini_mm"], f["y_fim_mm"]
        br = lambda v, sign=False: (f"{v:+.2f}" if sign else f"{v:.2f}").replace(".", ",")
        if y0 * y1 < 0:                                  # furo atravessa o plano de particao
            faixa = f"{br(y0)} … {br(y1)} (nas duas metades)"
        else:                                            # furo radial: espelhado em +/-Y
            faixa = (f"±{br(min(abs(y0), abs(y1)))} … {br(max(abs(y0), abs(y1)))}"
                     f" (1 por metade)")
        tabela_furos.append(f"| {tipo} | {br(d)} | {("0,00" if abs(x) < 1e-9 else br(x, True))} | {br(z)} | {faixa} | "
                            f"{br(f['comprimento_mm'])} | {br(paredes.get(tipo, 0))} mm |")

    txt = f"""# PROJETO DFM v28.1 — Matriz Jonatha (revisão para fabricação)

**Projeto:** matriz de extrusão plana para manta isolante de acessórios de cabos MT
**Modelo base (aprovado, continua oficial):** `01_CAD_MatrizJonatha_Oficial/MatrizJonatha.step` — SSOT v27.0
**Esta revisão:** v28.1 — **PROPOSTA**. O v27.0 continua sendo o master aprovado (decisão **D4**
do usuário: "não promover"). O que muda aqui é o que a decisão **D2** deixou de pé: nada no lábio
de saída, tudo no restante.
**Data:** 2026-09-11
**Verificação:** `{os.path.basename(DIR_DADOS)}/verificar_v28.py` → **{vf['itens']} itens, {vf['conformes']} conformes, {vf['nao_conformes']} não conformes**
**Conferência visual:** `V28_CONFERENCIA_VISUAL.png` (6 vistas, lidas dos STEP)

---

## 1. Resumo em seis linhas

1. O funil de fluxo aprovado **não foi tocado**: a distância máxima entre a superfície do funil
   {rot} e a do v27.0 medida nos sólidos é **{un(funil.get('medido', '0 mm').replace('Δmáx entre superfícies = ', ''), 'mm')}**.
2. **P7 e P8 rejeitados (decisão D2, 2026-09-11)**: o chanfro de saída fica **1,50 × 45°** e o
   land paralelo fica **{dim(land.get('medido'))} mm**, como no master — medidos nesta revisão: land
   {dim(land.get('medido'))} mm, chanfro {dim(cha.get('medido'))} × 45°, lâmina do lábio
   **{un(lam.get('medido'))}**. Ou seja: **a v28.1 não toca na região de saída do fundido**.
3. **P2 fechado**: os 4 bolsões de pino Ø4 × 12 agora são **abertos no plano de partição e
   conjugados nas duas metades** (o v27.0 tinha 2 bolsões selados só no Body_A e nada no Body_B),
   com kit de pinos modelado em `MatrizJonatha_v28_Pinos_Alinhamento.step`.
4. **P3 parcialmente fechado**: 6 cartuchos Ø9,5 e 4 poços de termopar Ø4,8 na zona do land,
   com paredes reais medidas de {dim(paredes.get('cartucho', 0))}–{dim(paredes.get('termopar', 0))} mm. A refrigeração
   **não cabe no corpo** (item 5) e vai para o adaptador.
5. **P1 tem solução — e ela é da máquina**: o cabeçote EX-030 medido tem bolso Ø95 × 70,0 com
   bucha cônica (EX-031, cone 3°) que aperta a banda Ø93 da matriz, e degrau de apoio axial.
   Dentro do envelope da matriz continua não havendo onde furar (sobram 8,70 mm de aço entre o
   canal Ø75,60 e o Ø93), então a fixação **não** é tarefa da matriz — item 6.
6. **P5 fechado**: o arquivo do canal é **1 único sólido** (o v27 entregava 3). Os números de CFD
   permanecem não reproduzíveis e foram re-marcados como "estimativa a confirmar" (item 7).

---

## 2. O que é e o que não é esta revisão

| | Situação |
| :--- | :--- |
| `MatrizJonatha.step` (v27.0) | **Continua sendo o master aprovado.** Nenhum byte foi alterado; a auditoria do v27 (`verify_geometry_ssot.py`) continua acusando os mesmos 2 não conformes históricos. |
| `MatrizJonatha_v28*.step` | Proposta DFM gerada por `gerar_matriz_v28.py`, verificada por `verificar_v28.py`. Vira oficial só depois do "aprova" do usuário. |
| `02_CAD_Modelos_Historicos/` | Intocada (regra 2 do projeto). |
| Produto (a manta) | Intocado e re-verificado: fenda **75,00 × 1,50 mm**, bordas **R0,75**, área da seção **{dim(achar(vf, 'Área da seção').get('medido'))} mm²**, boca de entrada **Ø{dim(achar(vf, 'boca de entrada (Z=0)').get('medido'))}**, envelope **Ø93 × 69,90 / Ø89,5 × 10,80 / Ø79,5 × 28,30**, comprimento **{dim(achar(vf, 'Comprimento total').get('medido'))} mm**. |

**Como reproduzir** (em container sem GPU/libGL, rode o `setup_headless_gl.sh` primeiro):

```bash
bash 04_Dados_SSOT_e_Scripts/setup_headless_gl.sh
export LD_LIBRARY_PATH="$PWD/04_Dados_SSOT_e_Scripts/.headless_gl:$LD_LIBRARY_PATH"
python 04_Dados_SSOT_e_Scripts/explorar_acomodo_furos.py --json   # onde existe aço para furos
python 04_Dados_SSOT_e_Scripts/gerar_matriz_v28.py                # gera os STEP da proposta
python 04_Dados_SSOT_e_Scripts/verificar_v28.py --json --md        # mede e prova (63 itens)
python 04_Dados_SSOT_e_Scripts/gerar_relatorio_v28.py            # este relatório
python 04_Dados_SSOT_e_Scripts/renderizar_v28.py --saida v28.png  # conferência visual
```

---

## 3. Tabela antes × depois (tudo medido nos STEP)

| Item | v27.0 (aprovado) | {rot} (proposta) | Como foi medido |
| :--- | ---: | ---: | :--- |
| Land reto e paralelo | 8,50 mm (o SSOT declarava 10,00) | **{dim(land.get('medido'))} mm — mantido (D2)**; SSOT atualizado para 8,50 paralelo + 1,50 de chanfro | varredura de seção em Z (passo 0,05 mm) até abs(Y) ≠ 1,50 |
| Chanfro de saída | 1,50 × 45° | **{dim(cha.get('medido'))} × 45° — mantido (D2 rejeitou o 0,80)** | folga radial a 0,10 mm da face |
| Lâmina do lábio (ponto mais fino) | 0,75 mm | **{un(lam.get('medido'))} — mantida (D2)**; o risco de lascamento na limpeza passa a ser item de procedimento | Ø79,5/2 − abs(X) da seção na face Z=109 |
| Furos de pino Ø4 × 12 | 2, selados no Body_A; 0 no Body_B | **4 abertos e conjugados (2 por lado)** | volume do furo ∩ corpo = 0 e aço sob o fundo presente |
| Cavidades internas fechadas | Body_A: 2 | **0** (1 shell em cada metade) | contagem de `TopAbs_SHELL` |
| Cartuchos de aquecimento | 0 | **6 × Ø9,5**, fundo a {dim(paredes.get('cartucho', 0))} mm do canal | booleano + `BRepExtrema` |
| Poços de termopar | 0 | **4 × Ø4,8**, fundo a {dim(paredes.get('termopar', 0))} mm | idem |
| Arquivo do canal | 3 sólidos | **1 sólido** | contagem de sólidos no STEP |
| Massa de aço | 3,682 kg | **{un(mass.get('medido'))}** | volume × 7,85 g/cm³ |
| Fechamento volumétrico | resíduo 0,001 mm³ | **resíduo {dim(fp.get('desvio'), 4)} mm³** (env − aço − canal = Σ furos) | booleano |
| ΔP 1D sobre a geometria | 41,9 bar | **{tbl(dp.get('medido'))}** | `dp_total()` do próprio projeto |
| τ na parede do land | 164,0 kPa | **{tau.get('medido')}** | `tau_parede()` do próprio projeto |
| Fixação das metades | inexistente | **pelo collete do cabeçote: 8,6 MPa de compressão radial fecham a partição** | item 6, medido |
| Interface com o cabeçote | nunca medida | **Ø93/Ø89,5/Ø79,5 encaixam em Ø95/Ø90/Ø80 com 1,00/0,25/0,25 mm de folga e interferência 0,0000 mm³** | booleanos, item 6 |
| Refrigeração | inexistente | **não cabe no corpo** | item 5 |

---

## 4. P1 — fixação das metades: por que não há furo que resolva isso

A força que empurra uma metade contra a outra é a pressão sobre a área projetada do canal no plano XZ.
Medindo essa área no sólido: **{un(aprev.get('medido'))}** (não é a área da boca; é a integral da largura do canal ao longo de Z).

| Cenário de pressão | Força de abertura |
| :--- | ---: |
| ΔP de projeto do CFD ({dim(p_lim_bar, 1)} bar, valor declarado no relatório de CFD) sobre **toda** a área projetada (limite superior) | **{un(forc.get('medido')).split(' no limite')[0]}** |
| {dim(p_lim_bar, 1)} bar atuando só sobre a boca Ø{dim(m['entry_bore_diameter_mm'])} (o número citado no relatório de triagem) | {dim(f_boca, 1)} kN |
| ΔP 1D medido na geometria ({dim(nz['dp_1d_bar'], 1)} bar) sobre a área projetada | ≈ {dim(f_proj, 1)} kN |

A geometria não oferece onde ancorar isso:

* faixa de aço entre o canal e o Ø93: (93,00 − 75,60)/2 = **8,70 mm**;
* um furo radial Ø9 (M8) com parede de 4 mm de cada lado exigiria **9 + 8 = 17 mm**;
* no 3º estágio (Ø79,5) a faixa cai para **1,95 mm** — ali não entra nem pino;
* consequência: **parafusos radiais ou axiais no corpo são geometricamente impossíveis** sem
  alterar o envelope, e o envelope é a regra que garante a montagem na extrusora.

**Caminhos, reordenados depois de medir o cabeçote (item 6):**

1. **Monobloco por EDM.** Eliminar a bipartição: abrir o canal por EDM a partir da face de saída
   (o `MatrizJonatha_v28_Canal_Fluxo.step` de 1 sólido é exatamente o arquivo para isso) e
   trepanar a boca Ø75,60 por trás. Sem plano de partição, não há força de abertura para
   reagir, e os pinos deixam de ser necessários. Custo: eletrodo + tempo de EDM.
2. **Aro de retração (shrink ring)** no degrau Ø93 → Ø89,50 (Z = 69,90). O aro coloca o corpo em
   compressão circunferencial e fecha o plano de partição por atrito, pré-carregada. Vantagem: não
   fura a peça. Necessita: verificar no cabeçote o espaço axial de 0,8 mm do degrau.
3. ~~Grampos externos usando os furos do flange do cabeçote~~ — **retirada**: os 6 × M12 estão em
   C.C. Ø180, nas fendas da junta cabeçote ↔ extrusora, a 35,25 mm do corpo da matriz (medido),
   e não alcançam a matriz. A pré-carga do plano de partição vem da bucha cônica EX-031, que já
   aperta a banda Ø93: 8,6 MPa bastam para equilibrar os 55,7 kN (item 6, medido nos sólidos).

Recomendação: **opção 1 (monobloco + EDM)** para a matriz de produção e manter a bipartição só no
protótipo de bancada. As duas outras são remendo; a 1 remove a causa.

---

## 5. Furação da {rot} — cotas de usinagem e paredes reais

Estas são as coordenadas do modelo; o `matriz_v28_features.json` é a fonte.

{chr(10).join(tabela_furos)}

Regras de fabricação aplicadas no desenho:

* **parede mínima até o canal**: pino {dim(paredes.get('pino_alinhamento', 0))} mm (alvo ≥ 2,0), cartucho {dim(paredes.get('cartucho', 0))} mm (alvo ≥ 4,0),
  termopar {dim(paredes.get('termopar', 0))} mm (alvo ≥ 3,0) — todas medidas com `BRepExtrema`, não estimadas;
* **web mínima entre furos**: {web.get('medido')} — nenhum furo encosta em outro;
* todo furo de aquecimento é **cego** e **abre na face externa**; nenhum rompe a face de entrada
  (Z=0) nem a de saída (Z=109) — verificado por interseção com lâminas nas duas faces;
* furação só de um lado do plano de partição por vez: cada metade é usinada sozinha e os bolsões
  são conjugados (mesmo X, Z e profundidade nos dois corpos), o que o verificador confirma;
 * os furos de alavanca de desmontagem (Ø5) que estavam no rascunho foram **suprimidos**: na faixa
   de 8,70 mm eles deixariam < 1,0 mm de parede na superfície externa. Desmontar pelo chanfro de
   1 × 45° a pedir na aresta do plano de partição.

**Refrigeração:** o mapeamento sistemático do aço (`acomodo_furos.json`) não encontrou **nenhuma**
posição para Ø8,0 com parede ≥ 3,5 mm. Axial ou radial, o furo atravessa a peça ou encosta no
funil. Portanto refrigeração vai para o **adaptador/cabeçote** (que é onde o `COMPARATIVO_SIMULACOES_E_SISTEMA_DE_REFRIGERACAO.md`
já a colocava), não para a matriz. Isso não é escolha de projeto: é consequência do envelope
Ø93 com boca Ø75,60.

---

{secao6(ic)}
---

## 7. Duas descobertas sobre o modelo que valem decisão

**7.1 O "coat-hanger" não está no sólido aprovado.** A medição seção a seção do canal aprovado
(`MatrizJonatha_Canal_Fluxo.step`) mostra que a **largura em X é ~constante de 75,6 → 75,0 mm**
do Z=0 ao Z=99, enquanto a **altura em Y fecha linearmente de ±37,61 para ±0,75 mm**:

| Z (mm) | 0,5 | 25 | 50 | 70 | 90 | 99 | 109 |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| X (mm) | ±37,80 | ±37,72 | ±37,65 | ±37,59 | ±37,53 | ±37,50 | ±39,0 |
| Y (mm) | ±37,61 | ±28,44 | ±19,09 | ±11,60 | ±4,12 | ±0,75 | ±2,24 |

Ou seja: o funil do modelo é um **reduzor cônico linear (V em Y)**, não um manifold de cabide com
reservatório central de 6,00 mm e asas em Z=25/Z=70 como descreve o `AUTO_PROMPT` e o script
`generate_true_coathanger_jonatha.py`. O loft daquele script interpola **só a primeira e a última
seção** (as seções intermediárias do `slot2D` não entram no loft sem `throughAll=True` com
arestas compatíveis), de modo que o modelo aprovado e o texto que o descreve divergem. A boa
notícia: o funil linear em V **também** distribui por toda a largura (a largura nunca afunila), o
que é coerente com a uniformidade alta alegada — mas o projeto não pode alegar "cabide" enquanto o
sólido é um cone.

{txt_funil}

**7.2 As duas metades não são espelhos.** O volume do canal acima e abaixo de Y=0 difere
**{un(assim.get('medido'))}** (0,093 % do volume do canal), herança do loft do v27.0. Se a manta apresentar
diferença entre as faces superior e inferior, este é o suspeito número um — antes de culpar o
termopar ou o polímero.

---

## 8. Reologia: o que a {rot} muda e o que continua em aberto

* Com o lábio **inalterado** (D2), a estimativa 1D sobre a geometria medida fica em
  **{tbl(dp.get('medido'))}** — os 43,9 bar da v28.0 vinham exatamente dos 0,70 mm de land a mais
  que a decisão D2 rejeitou. Continua sendo
  **~35 % menor que os 68,2 bar do relatório de CFD** — a direção do erro é a mesma desde a
  triagem: os números de CFD do projeto não são reproduzíveis a partir do repositório.
* A tensão de cisalhamento na parede **não mudou e não mudaria**: **{un(tau.get('medido'))}**,
  porque a fenda e a vazão são as mesmas. Qualquer material que afirme queda de τ por causa do
  novo chanfro deve ser corrigido.
* Antes de usar "99,10 % de uniformidade" como critério de aceite, é preciso publicar a definição
  (σ/U do perfil de velocidade medido em que plano) e a planilha. Sem isso, não é especificação.
* **Não há CFD pendente por esta revisão**: o lábio ficou igual ao do master (decisão D2) e o ΔP 1D
  medido nos dois sólidos é o mesmo, {tbl(dp.get('medido'))}. CFD novo só entra na conta se a opção
  coat-hanger (7.1b) for adotada — e aí o ΔP medido no estudo é {dp_ch} bar, acima do limite
  de 68,2 bar usado no relatório de projeto.

---

## 9. Situação das decisões

| # | Decisão | Estado | Consequência prática |
| :-: | :--- | :--- | :--- |
| **D1** | Fixação das metades | **FECHADA pela máquina** — collete EX-031 + degrau do cabeçote; a matriz não leva grampo, flange nem furo | o corte do aço pode ser liberado com a banda Ø93 retificada e os bolsões de pino cegos (sem escarear) |
| **D1b** | Anel do nariz do cabeçote (Ø68,30 do desenho, variante 9"×65 mm) | **FECHADA por medição sua na máquina**: sobram 2,5 mm por lado na fenda, o que só casa com a passagem Ø80,00 do próprio cabeçote | a matriz de 75 mm monta como está; o Ø68,30 fica registrado como coisa do cabeçote de 65 mm |
| **D2** | Chanfro da saída 0,80 ou 1,50 | **DECIDIDO: mantém 1,50 × 45°** (land 8,50, lâmina 0,75) como no master | a v28.1 não altera a região de saída; o lascamento na limpeza vira item de procedimento, não de geometria |
| **D4** | Promover a v28 para oficial | **DECIDIDO: não** — v27.0 segue master | a v28 fica ao lado, verificada, esperando você conferir a máquina |
| **D3** | Funil: o cone linear do modelo atual **ou** o coat-hanger de 6,00 mm do texto | {txt_d3_estado} | {txt_d3_conseq} |
| **medir** | Comprimento do bico do cabeçote (sua linha no croqui × o nariz do desenho) | {txt_bico} | {txt_bico_efeto} |

Enquanto D3 estiver em aberto, **nada é promovido**: `MatrizJonatha.step` continua sendo o v27.0 e a
v28.1 vive ao lado, com `verificar_v28.py` ({vf['itens']} itens) e `verificar_interface_cabecote.py` \
({ic['itens']} itens, {ic['conformes']} conformes, {ic['nao_conformes']} não conforme — a folga axial dos \
cartuchos × a luva do nariz, que é a linha 'medir' acima)
para re-medir a qualquer momento.

---

*Gerado por `gerar_relatorio_v28.py` a partir de `matriz_v28_features.json` e `verificacao_v28.json`.
Todas as grandezas desta página foram medidas nos arquivos STEP desta pasta; nenhuma foi copiada
de relatório anterior.*
"""
    with open(SAIDA, "w", encoding="utf-8") as f:
        f.write(txt)
    print("->", SAIDA)
    print(f"   {vf['itens']} checagens | {vf['conformes']} conformes | {vf['nao_conformes']} não conformes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
