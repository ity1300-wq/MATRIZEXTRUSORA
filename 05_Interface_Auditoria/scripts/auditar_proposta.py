#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
auditar_proposta.py — Auditor automático (Protocolo de Auditoria v1.0)
======================================================================

Lê uma proposta de engenharia (05_Interface_Auditoria/propostas/PRP-XXXX-*.json), refaz todas as
medições do zero pelos scripts do próprio repositório e escreve um veredito:

    05_Interface_Auditoria/vereditos/PRP-XXXX.json   (contrato, lido pela IA engenheira)
    05_Interface_Auditoria/vereditos/PRP-XXXX.md     (comentário curto para o PR)

O auditor NUNCA altera o objeto auditado (CAD, SSOT, scripts de medição).

Uso:
    python auditar_proposta.py propostas/PRP-0001-*.json --json --md
    python auditar_proposta.py <proposta.json> --com-cfd          # inclui CFD 2D (mais lento)
    python auditar_proposta.py --congelar-baseline                # registra o estado atual

Código de saída: 0 aprovado/ressalvas | 2 reprovado | 3 bloqueado | 4 erro de execução
"""

import argparse
import datetime
import hashlib
import json
import os
import subprocess
import sys

RAIZ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
DIR_INTERFACE = os.path.join(RAIZ, "05_Interface_Auditoria")
DIR_DADOS = os.path.join(RAIZ, "04_Dados_SSOT_e_Scripts")
DIR_STUB = os.path.join(DIR_DADOS, ".headless_gl")
DIR_BASELINE = os.path.join(DIR_INTERFACE, "baseline")
DIR_VEREDITOS = os.path.join(DIR_INTERFACE, "vereditos")
DIR_CAD = os.path.join(RAIZ, "01_CAD_MatrizJonatha_Oficial")
DIR_HISTORICOS = os.path.join(RAIZ, "02_CAD_Modelos_Historicos")
ARQ_BASELINE = os.path.join(DIR_BASELINE, "MATRIZ_3_v27.json")

PROTOCOLO = "1.0"
AUDITOR = "Auditor IA (Protocolo v1.0)"
PY = sys.executable

# ---------------------------------------------------------------- tolerâncias (protocolo §4)
TOL_METRICA = {
    "dp_total_bar": 0.15,
    "dp_land_bar_mm": 0.10,
    "uniformidade_nucleo_pct": 0.05,
    "uniformidade_dentro_5pct": 0.05,
    "tau_parede_land_kpa": 0.10,
    "forca_abertura_kN": 0.20,
    "residencia_media_s": 0.20,
    "residencia_parede_min": 0.30,
    "volume_canal_mm3": 0.005,
    "area_fenda_mm2": 0.01,
    "land_util_mm": 0.02,
    "parede_labio_mm": 0.05,
    "largura_fenda_mm": 0.001,
    "espessura_fenda_mm": 0.02,
    "raio_borda_mm": 0.03,
    "boca_entrada_mm": 0.001,
    "massa_aco_kg": 0.005,
}
FILOSOFIA_DELTA = {   # como interpretar o sinal de cada métrica
    "dp_total_bar": "menor_melhor", "dp_land_bar_mm": "neutro", "uniformidade_nucleo_pct": "maior_melhor",
    "uniformidade_dentro_5pct": "maior_melhor", "tau_parede_land_kpa": "menor_melhor",
    "forca_abertura_kN": "menor_melhor", "residencia_media_s": "menor_melhor",
    "residencia_parede_min": "menor_melhor", "parede_labio_mm": "maior_melhor",
    "land_util_mm": "maior_melhor", "volume_canal_mm3": "neutro",
    "area_fenda_mm2": "neutro", "largura_fenda_mm": "neutro", "espessura_fenda_mm": "neutro",
    "raio_borda_mm": "neutro", "boca_entrada_mm": "neutro", "massa_aco_kg": "neutro",
}
ARQ_GEOM = "auditoria_geometrica.json"
ARQ_HIST = "auditoria_matrizes_historicas.json"
ARQ_CALC = "avaliacao_matriz_3_calculos.json"
ARQ_SECOES = "avaliacao_matriz_3_secoes.json"
ARQ_UNIF = "avaliacao_matriz_3_uniformidade.json"


# ---------------------------------------------------------------- utilidades
def arquivos_protegidos():
    """Arquivos cuja alteração exige revisão humana (Protocolo §8) e os STEP do projeto."""
    lista = []
    for pasta, filtro in ((os.path.join(RAIZ, "01_CAD_MatrizJonatha_Oficial"), ".step"),
                          (os.path.join(RAIZ, "02_CAD_Modelos_Historicos"), ".step"),
                          (DIR_DADOS, None)):
        if not os.path.isdir(pasta):
            continue
        for nome in sorted(os.listdir(pasta)):
            caminho = os.path.join(pasta, nome)
            if not os.path.isfile(caminho) or nome.startswith("."):
                continue
            if filtro and not nome.lower().endswith(filtro):
                continue
            if pasta == DIR_DADOS:
                # no SSOT só o núcleo protegido: SSOT + scripts de medição
                if not (nome == "cad_die_parameters.json" or nome.startswith(("verify_", "cfd_", "setup_"))):
                    continue
            if os.path.exists(caminho):
                lista.append(caminho)
    for sub in ("PROTOCOLO_AUDITORIA.md", "esquema", "scripts"):
        alvo = os.path.join(DIR_INTERFACE, sub)
        if os.path.isfile(alvo):
            lista.append(alvo)
        elif os.path.isdir(alvo):
            for nome in sorted(os.listdir(alvo)):
                caminho = os.path.join(alvo, nome)
                if os.path.isfile(caminho) and not nome.startswith(("__", ".")):
                    lista.append(caminho)
    return lista


def agora():
    return datetime.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")


def sha256(caminho):
    h = hashlib.sha256()
    with open(caminho, "rb") as fh:
        for bloco in iter(lambda: fh.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def git(*args, obrigatorio=False):
    try:
        r = subprocess.run(["git", "-C", RAIZ, *args], capture_output=True, text=True, timeout=60)
        if r.returncode != 0:
            if obrigatorio:
                raise RuntimeError(r.stderr.strip())
            return None
        return r.stdout.strip()
    except Exception:
        if obrigatorio:
            raise
        return None


def ambiente():
    env = dict(os.environ)
    if os.path.isdir(DIR_STUB):
        env["LD_LIBRARY_PATH"] = DIR_STUB + ":" + env.get("LD_LIBRARY_PATH", "")
    env["PYTHONPATH"] = DIR_DADOS + os.pathsep + env.get("PYTHONPATH", "")
    return env


def rodar_script(nome, *args, timeout=1800):
    """Roda um script de medição do repositório e devolve (ok, saida)."""
    cmd = [PY, os.path.join(DIR_DADOS, nome), *args]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=ambiente(), cwd=RAIZ)
        return r.returncode == 0, (r.stdout or "") + (r.stderr or "")
    except subprocess.TimeoutExpired:
        return False, f"timeout de {timeout}s ao rodar {nome}"


def ler_json(caminho):
    if not os.path.exists(caminho):
        return None
    with open(caminho, encoding="utf-8") as fh:
        return json.load(fh)


def raio_da_secao(area_mm2, esp_mm, largura_mm=75.0):
    """Inverte A = esp*(L - 2R) + pi*R^2 (seção do land com as duas bordas arredondadas)."""
    alvo = area_mm2
    lo, hi = 0.0, esp_mm
    for _ in range(80):
        R = 0.5 * (lo + hi)
        A = esp_mm * (largura_mm - 2 * R) + 3.141592653589793 * R * R
        if A < alvo:
            lo = R
        else:
            hi = R
    return 0.5 * (lo + hi)


def perto(a, b, tol_rel, minimo_abs=1e-9):
    if a is None or b is None:
        return None
    escala = max(abs(b), minimo_abs)
    return abs(a - b) <= tol_rel * escala


# ---------------------------------------------------------------- medição
def medir(com_cfd=False, reusar=False):
    """Roda a bateria de medição e devolve as métricas + registro do que foi executado."""
    passos, reproduzir = [], []
    comandos = [
        ("verify_geometry_ssot.py", ["--json"], ARQ_GEOM),
        ("verify_legacy_dies.py", ["--json"], ARQ_HIST),
        ("avaliacao_matriz3_calculos.py", ["--json"], ARQ_CALC),
    ]
    if com_cfd:
        comandos.append(("cfd_land_crosssection.py", ["--secoes", "99.5", "103", "107", "--json"], ARQ_SECOES))
        comandos.append(("avaliacao_matriz3_uniformidade.py", ["--json"], ARQ_UNIF))

    for nome, args, saida in comandos:
        caminho_saida = os.path.join(DIR_DADOS, saida)
        if reusar and os.path.exists(caminho_saida):
            passos.append({"script": nome, "ok": True, "segundos": 0.0, "codigo_saida": "reutilizado",
                           "artefato": saida})
            reproduzir.append(f"python 04_Dados_SSOT_e_Scripts/{nome} {' '.join(args)}")
            continue
        mtime_antes = os.path.getmtime(caminho_saida) if os.path.exists(caminho_saida) else 0
        t0 = datetime.datetime.now()
        rc_ok, log = rodar_script(nome, *args)
        dt = (datetime.datetime.now() - t0).total_seconds()
        # alguns scripts (ex.: verify_geometry_ssot.py) devolvem código != 0 quando ENCONTRAM
        # não conformidades - isso é resultado, não falha. O que vale é o artefato gerado.
        artefato_novo = (os.path.exists(caminho_saida) and os.path.getmtime(caminho_saida) > mtime_antes
                         and os.path.getsize(caminho_saida) > 0)
        ok = artefato_novo or (rc_ok and os.path.exists(caminho_saida))
        passos.append({"script": nome, "ok": ok, "segundos": round(dt, 1),
                       "codigo_saida": 0 if rc_ok else "!=0 (achados)", "artefato": saida})
        reproduzir.append(f"python 04_Dados_SSOT_e_Scripts/{nome} {' '.join(args)}")
        if not ok:
            print(f"   [FALHA] {nome} não gerou {saida}\n{log[-1200:]}", file=sys.stderr)
    return passos, reproduzir


def extrair_metricas(geom, hist, calc, secoes=None, unif=None):
    itens = {it["item"]: it for it in (geom or {}).get("itens", [])}

    def item(trecho):
        for nome, it in itens.items():
            if trecho.lower() in nome.lower():
                return it.get("medido")
        return None

    m = {}
    m["largura_fenda_mm"] = item("Largura do land")
    m["espessura_fenda_mm"] = item("Espessura do land")
    m["area_fenda_mm2"] = item("Área da seção do land")
    m["land_util_mm"] = item("Comprimento do land reto e paralelo")
    m["boca_entrada_mm"] = item("boca de entrada (acoplamento")
    m["parede_labio_mm"] = item("Parede de aço no lábio")
    m["interferencia_mm3"] = item("Interferência entre Body_A")
    m["volume_canal_mm3"] = item("Volume do núcleo de polímero")
    m["z_total_mm"] = item("Comprimento total Z")
    m["diametro_externo_mm"] = item("Diâmetro externo máximo")
    m["envelope_residuo_mm3"] = item("Envelope - (aço + canal")
    larg, esp = m["largura_fenda_mm"], m["espessura_fenda_mm"]
    m["raio_borda_mm"] = (round(raio_da_secao(m["area_fenda_mm2"], esp, larg), 4)
                          if m["area_fenda_mm2"] and esp else None)

    j = next((x for x in (hist or {}).get("matrizes", []) if "Jonatha" in x.get("matriz", "")), {})
    m["canal_consistente"] = j.get("canal_consistente")
    m["dp_land_1d_bar_mm"] = None

    if calc:
        m["dp_total_bar"] = calc.get("dp_total_bar")
        m["forca_abertura_kN"] = (calc.get("forca_abertura") or {}).get("forca_kN")
        res = calc.get("residencia_s") or {}
        m["residencia_media_s"] = res.get("media")
        par = res.get("parede_0_05mm")
        m["residencia_parede_min"] = round(par / 60.0, 2) if par else None
        m["dp_land_bar_mm"] = calc.get("gradiente_land_bar_mm")

    if secoes:
        sec = next((s for s in secoes.get("secoes", []) if abs(s.get("altura_max_mm", 0) - 1.5) < 0.02), None)
        if sec:
            m["dp_land_bar_mm"] = round(sec["G_bar_por_mm"], 4)
            m["uniformidade_nucleo_pct"] = round(100 * sec["q_min_mm3_s_por_mm"] / sec["q_max_mm3_s_por_mm"], 2)
            m["tau_parede_land_kpa"] = sec["tau_medio_parede_kpa"]
    if unif:
        land = next((s for s in unif.get("secoes", []) if abs(s.get("altura_max_mm", 0) - 1.5) < 0.02), None)
        if land:
            m["uniformidade_dentro_5pct"] = land.get("core_dentro_5pct")
    return m


# ---------------------------------------------------------------- modelo paramétrico (protocolo §5)
def modelo_parametrico(parametros, baseline, medido):
    """Recalcula a previsão para propostas tipo 'calculo'. Devolve (metricas_previstas, modelo_usado)."""
    base = (baseline or {}).get("modelo_parametrico")
    if not base:
        return {}, "modelo indisponível (baseline sem 'modelo_parametrico')"
    land_total = float(parametros.get("land_total_mm", medido.get("land_total_mm") or 10.0))
    chanfro = float(parametros.get("chanfro_mm", 1.5))
    land_util = land_total - chanfro
    parede = 2.25 - chanfro
    dp = base["dp_fora_do_land_bar"] + base["G_land_bar_mm"] * land_util + base["G_chanfro_bar_mm"] * chanfro
    previsto = {
        "land_total_mm": round(land_total, 3),
        "chanfro_mm": round(chanfro, 3),
        "land_util_mm": round(land_util, 3),
        "parede_labio_mm": round(parede, 3),
        "dp_total_bar": round(dp, 2),
    }
    texto = (f"dp_total = {base['dp_fora_do_land_bar']:.2f} (entrada+funil+aproximação, medido) "
             f"+ {base['G_land_bar_mm']:.3f}·land_util + {base['G_chanfro_bar_mm']:.3f}·chanfro; "
             f"land_util = land_total − chanfro; parede_labio = 2,25 − chanfro")
    return previsto, texto


# ---------------------------------------------------------------- verificações
def checar_requisitos_duros(medido, geom):
    itens = {it["item"]: it for it in (geom or {}).get("itens", [])}
    duros = [
        ("largura_fenda_mm", "Largura da fenda = 75,00 mm", 75.0, 0.05, "mm"),
        ("espessura_fenda_mm", "Espessura da fenda = 1,50 mm", 1.5, 0.02, "mm"),
        ("raio_borda_mm", "Raio de borda = 0,75 mm", 0.75, 0.02, "mm"),
        ("boca_entrada_mm", "Boca de entrada ≤ Ø75,60 mm", 75.6, 0.001, "mm"),
        ("interferencia_mm3", "Interferência entre as metades = 0", 0.0, 0.01, "mm³"),
    ]
    checks = []
    for i, (chave, nome, nominal, tol, un) in enumerate(duros, start=1):
        v = medido.get(chave)
        if v is None:
            checks.append(dict(id=f"D{i}", o_que=nome, nominal=nominal, medido=None, tolerancia=f"±{tol} {un}",
                               unidade=un, severidade="BLOCKER", resultado="NAO_VERIFICADO",
                               fonte="verify_geometry_ssot.py", observacao="valor não medido"))
            continue
        if chave == "boca_entrada_mm":
            ok = v <= nominal + tol
        else:
            ok = abs(v - nominal) <= tol
        checks.append(dict(id=f"D{i}", o_que=nome, nominal=nominal, medido=v, tolerancia=f"±{tol} {un}",
                           unidade=un, severidade="BLOCKER", resultado="OK" if ok else "FALHA",
                           fonte="verify_geometry_ssot.py"))
    # envelope e consistência do canal
    z, d = medido.get("z_total_mm"), medido.get("diametro_externo_mm")
    ok = (z is not None and abs(z - 109.0) <= 0.05) and (d is not None and abs(d - 93.0) <= 0.05)
    checks.append(dict(id="D6", o_que="Envelope externo (Ø93 × 109 mm)", nominal="93 × 109", medido=f"{d} × {z}",
                       tolerancia="±0,05 mm", severidade="BLOCKER", resultado="OK" if ok else "FALHA",
                       fonte="verify_geometry_ssot.py"))
    cons = medido.get("canal_consistente")
    checks.append(dict(id="D7", o_que="Canal isolado × corpo (consistência)", nominal=True, medido=cons,
                       tolerancia="≤ 0,5%", severidade="BLOCKER",
                       resultado="OK" if cons else ("FALHA" if cons is False else "NAO_VERIFICADO"),
                       fonte="verify_legacy_dies.py"))
    return checks


def _listas_de_arquivos(base):
    """Devolve (mudados, novos) considerando commits desde o base E a árvore de trabalho.

    'mudados' = arquivos versionados que diferem do base/HEAD (inclui o que não foi commitado);
    'novos'   = arquivos ainda não versionados (untracked).
    """
    status = {}
    for args in ((["--name-status", f"{base}..HEAD"] if base else []), ["--name-status", "HEAD"]):
        if not args:
            continue
        for linha in (git("diff", *args) or "").splitlines():
            partes = linha.split("\t")
            if len(partes) >= 2:
                codigo, caminho = partes[0][0], partes[-1].strip()
                if "R" in codigo or "C" in codigo:
                    codigo = "M"
                status.setdefault(caminho, codigo)
    novos = {a.strip() for a in (git("ls-files", "--others", "--exclude-standard") or "").splitlines()
             if a.strip()}
    return status, sorted(novos)


def _protegido(caminho):
    if caminho == "04_Dados_SSOT_e_Scripts/cad_die_parameters.json":
        return True
    if caminho.startswith("04_Dados_SSOT_e_Scripts/") and (
            os.path.basename(caminho).startswith(("verify_", "cfd_", "setup_"))):
        return True
    return caminho.startswith(("05_Interface_Auditoria/PROTOCOLO",
                               "05_Interface_Auditoria/esquema/",
                               "05_Interface_Auditoria/scripts/"))


def checar_imutabilidade(proposta, baseline=None):
    """Compara os arquivos protegidos com os hashes do baseline congelado.

    Não depende do histórico do git: se o repositório for re-clonado, os hashes do
    baseline continuam sendo a referência. O git entra apenas como informação extra.
    """
    checks, novos_protegidos = [], []
    hashes_base = (baseline or {}).get("hashes") or {}
    declarados = {a["caminho"] for a in proposta.get("arquivos", [])}

    atual = {os.path.relpath(p, RAIZ): sha256(p) for p in arquivos_protegidos()}

    alterados_04, alterados_05, alterados_02, alterados_01, ausentes = [], [], [], [], []
    for caminho, h in hashes_base.items():
        if caminho not in atual:
            ausentes.append(caminho)
            continue
        if atual[caminho] == h:
            continue
        if caminho.startswith("04_"):
            alterados_04.append(caminho)
        elif caminho.startswith("05_"):
            alterados_05.append(caminho)
        elif caminho.startswith("02_"):
            alterados_02.append(caminho)
        elif caminho.startswith("01_"):
            alterados_01.append(caminho)
    for caminho in atual:
        if caminho not in hashes_base:
            novos_protegidos.append(caminho)

    def add(id_, o_que, medido, ok, sev="BLOCKER", obs=""):
        checks.append(dict(id=id_, o_que=o_que, nominal="idêntico ao baseline congelado", medido=medido,
                           severidade=sev,
                           resultado="OK" if ok else ("FALHA" if sev == "BLOCKER" else "ATENCAO"),
                           fonte="sha256 × baseline", observacao=obs))

    add("I1", "02_CAD_Modelos_Historicos/ intacto", alterados_02 or "nenhuma alteração", not alterados_02,
        obs="" if not alterados_02 else "modelos históricos nunca podem ser editados")
    nao_step = [c for c in atual if c.startswith("01_") and not c.lower().endswith(".step")]
    add("I2", "Entregáveis CAD em .step", nao_step or "todos .step", not nao_step)
    cad_nao_declarados = [c for c in alterados_01 if c not in declarados]
    add("I3", "STEP alterados estão declarados na proposta",
        cad_nao_declarados or (alterados_01 or "nenhuma alteração"), not cad_nao_declarados,
        obs="" if not cad_nao_declarados else "arquivo CAD mudou sem estar declarado em 'arquivos'")
    add("I4", "SSOT e scripts de medição não alterados", alterados_04 or "nenhuma alteração",
        not alterados_04, obs="" if not alterados_04 else "zona congelada (§8 do protocolo)")
    add("I5", "Protocolo, esquemas e scripts do auditor não alterados",
        alterados_05 or "nenhuma alteração", not alterados_05,
        obs="" if not alterados_05 else "zona congelada (§8 do protocolo)")
    add("I6", "Sem arquivos protegidos ausentes", ausentes or "nenhum", not ausentes)
    if novos_protegidos:
        checks.append(dict(id="I7", o_que="Arquivos protegidos novos (não estavam no baseline)",
                           nominal="—", medido=novos_protegidos, severidade="INFO", resultado="ATENCAO",
                           fonte="sha256 × baseline",
                           observacao=("arquivos novos na zona protegida; o baseline precisa ser "
                                       "recongelado pelo responsável antes de valerem como referência")))
    if not hashes_base:
        checks.append(dict(id="I0", o_que="Baseline congelado disponível", nominal="sim", medido="não",
                           severidade="BLOCKER", resultado="NAO_VERIFICADO", fonte="baseline/",
                           observacao="rode --congelar-baseline uma vez, com o modelo aprovado"))

    # informação extra: o que o git vê na árvore de trabalho (se disponível)
    base = proposta.get("base_commit")
    if base and git("cat-file", "-t", base):
        mudados = [a.strip() for a in (git("diff", "--name-only", f"{base}..HEAD") or "").splitlines() if a.strip()]
        nao_declarados_git = [a for a in mudados if a.startswith("01_") and a not in declarados]
        if nao_declarados_git:
            checks.append(dict(id="I8", o_que="git: arquivos CAD alterados desde base_commit",
                               nominal="declarados", medido=nao_declarados_git, severidade="INFO",
                               resultado="ATENCAO", fonte=f"git diff {base[:8]}..HEAD"))
    return checks, sorted(atual)


def conferir_declarado(proposta, previsto, medido):
    """Compara o que a proposta promete (esperado) com o que o auditor calculou/mediu."""
    checks, nao_auditavel = [], []
    fontes = {"previsto": previsto, "medido": medido}
    for chave, declarado in (proposta.get("esperado") or {}).items():
        tol = TOL_METRICA.get(chave)
        calc = previsto.get(chave, medido.get(chave))
        if calc is None or tol is None:
            nao_auditavel.append({"item": f"esperado.{chave}",
                                  "motivo": ("o auditor não sabe recalcular esta métrica"
                                             if tol is None else "métrica não medida nesta auditoria")})
            continue
        ok = perto(declarado, calc, tol)
        desvio = None if calc in (None, 0) else round(100 * (declarado - calc) / calc, 2)
        checks.append(dict(id=f"E:{chave}", o_que=f"Declarado × recalculado: {chave}",
                           nominal=declarado, medido=round(calc, 4) if isinstance(calc, float) else calc,
                           tolerancia=f"±{100 * tol:.1f}%", severidade="ALERTA",
                           resultado="OK" if ok else "FALHA", fonte="auditor (modelo/medição)",
                           observacao=f"desvio {desvio}%" if desvio is not None else ""))
    return checks, nao_auditavel


def comparar_baseline(metricas_propostas, baseline, nao_muda):
    if not baseline:
        return [], [{"item": "baseline", "motivo": "baseline não congelado (rode --congelar-baseline)"}]
    comp = []
    b = baseline.get("metricas", {})
    for chave, novo in metricas_propostas.items():
        antigo = b.get(chave)
        if antigo is None or novo is None or not isinstance(antigo, (int, float)):
            continue
        delta = None if antigo == 0 else round(100 * (novo - antigo) / antigo, 2)
        filo = FILOSOFIA_DELTA.get(chave, "neutro")
        if filo == "menor_melhor":
            direcao = "melhor" if novo < antigo else ("pior" if novo > antigo else "igual")
        elif filo == "maior_melhor":
            direcao = "melhor" if novo > antigo else ("pior" if novo < antigo else "igual")
        else:
            direcao = "igual" if delta == 0 else "neutro"
        bloqueia = chave in (nao_muda or [])
        tol_baseline = {"dp_total_bar": 0.15, "uniformidade_nucleo_pct": 0.05,
                        "residencia_parede_min": 0.30, "tau_parede_land_kpa": 0.25,
                        "parede_labio_mm": 0.0}.get(chave, 0.05)
        if bloqueia:
            aceitavel = delta == 0
        elif direcao == "pior":
            aceitavel = abs(delta) <= 100 * tol_baseline
        else:
            aceitavel = True
        comp.append({"metrica": chave, "baseline": antigo, "proposto": novo, "delta_pct": delta,
                     "direcao": direcao, "aceitavel": bool(aceitavel), "bloqueia_se_mudar": bool(bloqueia)})
    return comp, []


def classificar(checks, comp, nao_auditavel=None):
    bloqueios, alertas = [], []
    declarados_sem_auditoria = [n["item"] for n in (nao_auditavel or []) if n["item"].startswith("esperado.")]
    for c in checks:
        if c["resultado"] == "FALHA":
            (bloqueios if c["severidade"] == "BLOCKER" else alertas).append(
                f"{c['id']}: {c['o_que']} (nominal {c.get('nominal')} / medido {c.get('medido')})")
        elif c["resultado"] == "NAO_VERIFICADO" and c["severidade"] == "BLOCKER":
            bloqueios.append(f"{c['id']}: {c['o_que']} — não verificado")
    for c in comp:
        if not c["aceitavel"]:
            alertas.append(f"{c['metrica']}: {c['baseline']} → {c['proposto']} ({c['delta_pct']}%, "
                           f"{c['direcao']})")
    if bloqueios:
        return "BLOQUEADO", bloqueios, alertas
    if alertas:
        return "REPROVADO", bloqueios, alertas
    if declarados_sem_auditoria:
        return "APROVADO_COM_RESSALVAS", bloqueios, alertas
    return "APROVADO", bloqueios, alertas


# ---------------------------------------------------------------- veredito
def montar_markdown(v):
    linhas = [f"## Veredito `{v['proposta_id']}` — **{v['estado']}**", "",
              f"**{v['resumo']}**", "",
              f"`commit auditado:` `{v['commit_auditado'][:12]}` · `protocolo:` {v['protocolo']} · "
              f"`data:` {v['data']}", "", "### Requisitos e conferências", "",
              "| id | o que | nominal | medido | tol. | severidade | resultado |",
              "| :-- | :-- | --: | --: | :-- | :-- | :-- |"]
    for c in v["checks"]:
        linhas.append(f"| `{c['id']}` | {c['o_que']} | {c.get('nominal','')} | {c.get('medido','')} | "
                      f"{c.get('tolerancia','')} | {c['severidade']} | **{c['resultado']}** |")
    if v["comparacao_baseline"]:
        linhas += ["", "### Comparação com o baseline (v27 aprovado)", "",
                   "| métrica | baseline | proposto | Δ | direção | aceitável |",
                   "| :-- | --: | --: | --: | :-- | :-- |"]
        for c in v["comparacao_baseline"]:
            d = "—" if c["delta_pct"] is None else f"{c['delta_pct']:+.2f}%"
            linhas.append(f"| `{c['metrica']}` | {c['baseline']} | {c['proposto']} | {d} | "
                          f"{c['direcao']} | {'sim' if c['aceitavel'] else '**não**'} |")
    if v["bloqueios"]:
        linhas += ["", "### 🚫 Bloqueios"] + [f"- {b}" for b in v["bloqueios"]]
    if v["recomendacoes"]:
        linhas += ["", "### Recomendações"] + [f"- {r}" for r in v["recomendacoes"]]
    if v["nao_auditavel"]:
        linhas += ["", "### ⚠️ Não auditado (silêncio não é aprovação)"]
        linhas += [f"- `{n['item']}` — {n['motivo']}" for n in v["nao_auditavel"]]
    if v.get("modelo_parametrico"):
        linhas += ["", f"**Modelo usado:** {v['modelo_parametrico']}"]
    linhas += ["", "<details><summary>Reproduzir</summary>", ""]
    linhas += [f"```bash\n{c}\n```" for c in v["reproduzir"]]
    linhas += ["</details>", ""]
    return "\n".join(linhas)


def congelar_baseline(com_cfd=False):
    print("Congelando baseline do estado atual...")
    passos, reproduzir = medir(com_cfd=False)
    geom = ler_json(os.path.join(DIR_DADOS, ARQ_GEOM))
    hist = ler_json(os.path.join(DIR_DADOS, ARQ_HIST))
    calc = ler_json(os.path.join(DIR_DADOS, ARQ_CALC))
    m = extrair_metricas(geom, hist, calc)
    perfil = (calc or {}).get("perfil_pressao", {})
    if not perfil:
        print("ERRO: perfil de pressão ausente; não é possível congelar o baseline.", file=sys.stderr)
        return 4
    z, G = perfil["z_mm"], perfil["G_bar_mm"]
    zonas = (calc or {}).get("zonas_bar") or (calc or {}).get("zonas")
    if not zonas:
        print("ERRO: zonas de perda de carga ausentes no JSON de cálculos.", file=sys.stderr)
        return 4
    dp_fora = zonas["entrada_e_funil_z0_90"] + zonas["aproximacao_do_land_z90_99"]
    dp_land = zonas["land_paralelo_z99_107_5"]
    dp_chanfro = zonas["chanfro_saida_z107_5_109"]
    land_util = m.get("land_util_mm") or 8.5
    chanfro = round(10.0 - land_util, 3)
    baseline = {
        "matriz": "Matriz 3 — Jonatha v27 (oficial)",
        "congelado_em": agora(),
        "metodo": ("medição dos STEP oficiais por verify_geometry_ssot.py / verify_legacy_dies.py / "
                   "avaliacao_matriz3_calculos.py"),
        "hashes": {os.path.relpath(p, RAIZ): sha256(p) for p in arquivos_protegidos() if os.path.exists(p)},
        "metricas": {k: v for k, v in m.items() if isinstance(v, (int, float, bool)) or v is None},
        "modelo_parametrico": {
            "dp_fora_do_land_bar": round(dp_fora, 3),
            "G_land_bar_mm": round(dp_land / land_util, 4) if land_util else None,
            "G_chanfro_bar_mm": round(dp_chanfro / chanfro, 4) if chanfro else None,
            "land_util_mm": land_util,
            "chanfro_mm": chanfro,
            "observacao": ("calibrado no v27 medido; relações: land_util = land_total − chanfro; "
                           "parede_labio = 2,25 − chanfro"),
        },
        "perfil_1d": perfil,
        "reproduzir": reproduzir,
    }
    os.makedirs(DIR_BASELINE, exist_ok=True)
    with open(ARQ_BASELINE, "w", encoding="utf-8") as fh:
        json.dump(baseline, fh, ensure_ascii=False, indent=2)
    print(f"Baseline salvo em {os.path.relpath(ARQ_BASELINE, RAIZ)}")
    print(f"   dp_fora_do_land = {dp_fora:.2f} bar | G_land = {baseline['modelo_parametrico']['G_land_bar_mm']} "
          f"bar/mm | G_chanfro = {baseline['modelo_parametrico']['G_chanfro_bar_mm']} bar/mm")
    return 0


def atualizar_hashes():
    """Re-sela a zona congelada sem refazer medições.

    É um ato deliberado: quem altera a régua (protocolo, esquemas, scripts de medição) precisa
    re-selar o baseline, e isso fica registrado em `selos`. Caso contrário o próprio auditor
    bloqueia todas as propostas - o que aconteceu na prática e é o comportamento desejado.
    """
    if not os.path.exists(ARQ_BASELINE):
        print("ERRO: baseline inexistente; rode --congelar-baseline primeiro.", file=sys.stderr)
        return 4
    with open(ARQ_BASELINE, encoding="utf-8") as fh:
        d = json.load(fh)
    antes = d.get("hashes", {})
    agora = {os.path.relpath(p, RAIZ): sha256(p) for p in arquivos_protegidos() if os.path.exists(p)}
    mudados = [k for k in set(antes) & set(agora) if antes[k] != agora[k]]
    novos = [k for k in agora if k not in antes]
    ausentes = [k for k in antes if k not in agora]
    d["hashes"] = agora
    d.setdefault("selos", []).append({
        "quando": agora_data(), "commit": git("rev-parse", "HEAD") or "?",
        "motivo": "re-selo da zona congelada (--atualizar-hashes)",
        "arquivos_alterados": sorted(mudados), "arquivos_novos": sorted(novos),
        "arquivos_removidos": sorted(ausentes)})
    d["hashes_atualizados_em"] = agora_data()
    with open(ARQ_BASELINE, "w", encoding="utf-8") as fh:
        json.dump(d, fh, ensure_ascii=False, indent=2)
    print(f"Re-selo registrado em {os.path.relpath(ARQ_BASELINE, RAIZ)}")
    print(f"   alterados: {mudados or 'nenhum'}")
    print(f"   novos:     {novos or 'nenhum'}")
    print(f"   removidos: {ausentes or 'nenhum'}")
    return 0


def agora_data():
    return datetime.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")


def main():
    ap = argparse.ArgumentParser(description="Auditor de propostas (Protocolo v1.0)")
    ap.add_argument("proposta", nargs="?", help="caminho do JSON da proposta")
    ap.add_argument("--json", action="store_true", help="escreve o veredito JSON")
    ap.add_argument("--md", action="store_true", help="escreve o veredito Markdown")
    ap.add_argument("--com-cfd", action="store_true", help="inclui CFD 2D na auditoria")
    ap.add_argument("--congelar-baseline", action="store_true", help="registra o estado atual como baseline")
    ap.add_argument("--atualizar-hashes", action="store_true",
                    help="re-sela a zona congelada (obrigatório depois de alterar os scripts do auditor; "
                         "NÃO refaz as medições)")
    ap.add_argument("--saida-dir", default=DIR_VEREDITOS)
    ap.add_argument("--reusar-medicoes", action="store_true",
                    help="DESENVOLVIMENTO APENAS: reaproveita os últimos JSONs medidos "
                         "(o CI e as auditorias oficiais nunca usam esta opção)")
    args = ap.parse_args()

    if args.congelar_baseline:
        return congelar_baseline()
    if args.atualizar_hashes:
        return atualizar_hashes()
    if not args.proposta:
        ap.error("informe o caminho da proposta (ou use --congelar-baseline)")

    caminho = args.proposta if os.path.isabs(args.proposta) else os.path.join(os.getcwd(), args.proposta)
    if not os.path.exists(caminho):
        candidatos = [os.path.join(DIR_INTERFACE, "propostas", args.proposta)]
        caminho = next((c for c in candidatos if os.path.exists(c)), caminho)
    if not os.path.exists(caminho):
        print(f"ERRO: proposta não encontrada: {args.proposta}", file=sys.stderr)
        return 4

    with open(caminho, encoding="utf-8") as fh:
        proposta = json.load(fh)

    print("=" * 100)
    print(f"AUDITORIA — {proposta['id']}: {proposta['titulo']}")
    print(f"Protocolo {PROTOCOLO} | tipo: {proposta['tipo']} | autor: {proposta['autor']}")
    print("=" * 100)

    # 1) validação mínima do contrato
    obrigatorios = ["protocolo", "id", "titulo", "autor", "data", "tipo", "base_commit", "objetivo",
                    "parametros", "esperado", "nao_muda", "justificativa", "riscos"]
    faltando = [c for c in obrigatorios if c not in proposta]
    if faltando:
        print(f"ERRO: proposta fora do contrato, faltam campos: {faltando}", file=sys.stderr)
        return 4
    if proposta["protocolo"] != PROTOCOLO:
        print(f"ERRO: proposta declara protocolo {proposta['protocolo']}, auditor usa {PROTOCOLO}",
              file=sys.stderr)
        return 4

    # 2) medições independentes
    com_cfd = bool(args.com_cfd or proposta.get("cfd_requerido"))
    print(f"\n[1/5] Medindo o repositório (CFD: {'sim' if com_cfd else 'não'})...")
    passos, reproduzir = medir(com_cfd=com_cfd, reusar=args.reusar_medicoes)
    for p in passos:
        print(f"      {'ok ' if p['ok'] else 'FALHA'} {p['script']:34s} {p['segundos']:7.1f} s "
              f"(saída {p['codigo_saida']}, artefato {p['artefato']})")
    if not all(p["ok"] for p in passos):
        print("ERRO: a bateria de medição falhou; veredito não pode ser emitido.", file=sys.stderr)
        return 4

    geom = ler_json(os.path.join(DIR_DADOS, ARQ_GEOM))
    hist = ler_json(os.path.join(DIR_DADOS, ARQ_HIST))
    calc = ler_json(os.path.join(DIR_DADOS, ARQ_CALC))
    secoes = ler_json(os.path.join(DIR_DADOS, ARQ_SECOES))
    unif = ler_json(os.path.join(DIR_DADOS, ARQ_UNIF))
    medido = extrair_metricas(geom, hist, calc, secoes, unif)

    baseline = ler_json(ARQ_BASELINE)

    # 3) verificações
    print("[2/5] Requisitos duros...")
    checks = checar_requisitos_duros(medido, geom)
    print("[3/5] Imutabilidade e arquivos...")
    ch_imut, arquivos_diff = checar_imutabilidade(proposta, baseline)
    checks += ch_imut

    previsto, modelo_txt = {}, "não aplicável"
    if proposta["tipo"] == "calculo":
        print("[4/5] Modelo paramétrico...")
        previsto, modelo_txt = modelo_parametrico(proposta.get("parametros", {}), baseline, medido)
        for k, v in previsto.items():
            print(f"      {k} = {v}")
        if not baseline:
            modelo_txt = "baseline ausente: previsão não conferida"
    else:
        print("[4/5] Proposta com objeto entregue: usando medição direta.")
        previsto = medido

    ch_decl, nao_auditavel = conferir_declarado(proposta, previsto, medido)
    checks += ch_decl

    print("[5/5] Comparando com o baseline...")
    metricas_propostas = dict(medido)
    for k, v in previsto.items():
        if k in metricas_propostas or k in ("dp_total_bar", "land_util_mm", "parede_labio_mm"):
            metricas_propostas[k] = v
    comp, nao_aud_baseline = comparar_baseline(metricas_propostas, baseline, proposta.get("nao_muda"))
    nao_auditavel += nao_aud_baseline

    estado, bloqueios, alertas = classificar(checks, comp, nao_auditavel)

    if proposta["tipo"] == "calculo" and not any(a["caminho"].endswith(".step") for a in proposta.get("arquivos", [])):
        nao_auditavel.append({
            "item": "geometria proposta (STEP ainda não entregue)",
            "motivo": ("proposta do tipo 'calculo': os valores de geometria são previsão do modelo, "
                       "não medição de arquivo; quando o STEP for entregue, reenviar como tipo "
                       "'geometria' para auditoria dimensional")})

    resumo = {
        "APROVADO": "Requisitos duros OK e previsões conferem: proposta pode seguir para o CAD.",
        "APROVADO_COM_RESSALVAS": "Requisitos duros OK, com itens não auditados listados.",
        "REPROVADO": "Passa os requisitos duros, mas há divergência ou degradação fora da tolerância.",
        "BLOQUEADO": "Requisito duro violado ou não verificado: corrigir antes de continuar.",
    }[estado]

    veredito = {
        "protocolo": PROTOCOLO,
        "proposta_id": proposta["id"],
        "commit_auditado": git("rev-parse", "HEAD") or "(desconhecido)",
        "proposta_sha256": sha256(caminho),
        "data": agora(),
        "auditor": {"nome": AUDITOR, "tipo": "IA", "tipo_proposta": proposta["tipo"]},
        "estado": estado,
        "resumo": resumo,
        "checks": checks,
        "metricas": {k: v for k, v in metricas_propostas.items() if isinstance(v, (int, float, bool))},
        "comparacao_baseline": comp,
        "bloqueios": bloqueios,
        "recomendacoes": [],
        "nao_auditavel": nao_auditavel,
        "modelo_parametrico": modelo_txt,
        "medicoes_reutilizadas": bool(args.reusar_medicoes),
        "hashes": {
            "proposta": sha256(caminho),
            "head": git("rev-parse", "HEAD"),
            **{k: v for k, v in (baseline or {}).get("hashes", {}).items() if os.path.exists(os.path.join(RAIZ, k))},
        },
        "reproduzir": reproduzir + [f"python 05_Interface_Auditoria/scripts/auditar_proposta.py {args.proposta}"],
    }

    # recomendações automáticas
    if estado == "BLOQUEADO":
        veredito["recomendacoes"].append("Corrigir os bloqueios acima e reenviar como PRP-XXXX-r2.")
    if estado == "REPROVADO":
        veredito["recomendacoes"].append("Revisar os itens divergentes ou declarar a divergência com "
                                         "justificativa física; tolerâncias só mudam por revisão do protocolo (§8).")
    if estado == "APROVADO_COM_RESSALVAS":
        veredito["recomendacoes"].append(
            "A proposta declara métricas que o auditor não sabe recalcular (ver 'Não auditado'): "
            "enviar evidência própria (rodada de CFD, medição) ou reformular a proposta sem elas.")
    if estado == "APROVADO" and proposta["tipo"] == "calculo":
        veredito["recomendacoes"].append("Enviar o STEP da alteração como proposta tipo 'geometria' para "
                                         "auditoria dimensional antes de usinar.")

    os.makedirs(args.saida_dir, exist_ok=True)
    if args.json:
        destino = os.path.join(args.saida_dir, f"{proposta['id']}.json")
        with open(destino, "w", encoding="utf-8") as fh:
            json.dump(veredito, fh, ensure_ascii=False, indent=2)
        print(f"\nVeredito JSON: {os.path.relpath(destino, RAIZ)}")
    if args.md:
        destino = os.path.join(args.saida_dir, f"{proposta['id']}.md")
        with open(destino, "w", encoding="utf-8") as fh:
            fh.write(montar_markdown(veredito))
        print(f"Veredito MD:   {os.path.relpath(destino, RAIZ)}")

    print("\n" + "=" * 100)
    print(f"ESTADO: {estado} — {resumo}")
    for b in bloqueios:
        print(f"   BLOQUEIO: {b}")
    for a in alertas:
        print(f"   ALERTA:   {a}")
    print("=" * 100)
    return {"APROVADO": 0, "APROVADO_COM_RESSALVAS": 0, "REPROVADO": 2, "BLOQUEADO": 3}[estado]


if __name__ == "__main__":
    sys.exit(main())
