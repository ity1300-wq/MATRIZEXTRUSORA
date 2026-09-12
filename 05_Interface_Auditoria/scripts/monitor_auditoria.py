#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
monitor_auditoria.py — Modo B do Protocolo de Auditoria: vigilância contínua do repositório
============================================================================================

Fica observando um ramo do git. Quando um commit novo mexe em
`05_Interface_Auditoria/propostas/`, a proposta é auditada automaticamente e o veredito é
gravado (e, se pedido, enviado ao remoto).

    python monitor_auditoria.py                       # vigia o ramo atual, de 20 em 20 s
    python monitor_auditoria.py --remoto --push       # busca no origin e publica o veredito
    python monitor_auditoria.py --uma-vez             # processa o que já está pendente e sai
    python monitor_auditoria.py --com-cfd             # auditoria completa (mais lenta)
    python monitor_auditoria.py --rapido               # reaproveita medições (~2 s por proposta)

Pensado para rodar como processo de longa duração: cada ciclo imprime uma linha de batimento,
para que o operador (ou uma tela de pré-visualização) veja que está vivo.
"""

import argparse
import datetime
import hashlib
import json
import os
import subprocess
import sys
import time

RAIZ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
DIR_INTERFACE = os.path.join(RAIZ, "05_Interface_Auditoria")
DIR_PROP = os.path.join(DIR_INTERFACE, "propostas")
DIR_VER = os.path.join(DIR_INTERFACE, "vereditos")
ARQ_ESTADO = os.path.join(DIR_INTERFACE, ".estado_monitor.json")
AUDITOR = os.path.join(DIR_INTERFACE, "scripts", "auditar_proposta.py")


def log(msg):
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def git(*args, obrigatorio=False):
    r = subprocess.run(["git", "-C", RAIZ, *args], capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        if obrigatorio:
            raise RuntimeError(f"git {' '.join(args)}: {r.stderr.strip()}")
        return None
    return r.stdout.strip()


def sha256_txt(txt):
    return hashlib.sha256(txt.encode("utf-8")).hexdigest()


def carregar_estado():
    if os.path.exists(ARQ_ESTADO):
        with open(ARQ_ESTADO, encoding="utf-8") as fh:
            return json.load(fh)
    return {"ramo": None, "ultimo_sha": None, "auditadas": {}}


def salvar_estado(estado):
    with open(ARQ_ESTADO, "w", encoding="utf-8") as fh:
        json.dump(estado, fh, ensure_ascii=False, indent=2)


def propostas_entre(sha_antigo, sha_novo):
    """Caminhos de propostas no intervalo + as que estão na árvore de trabalho.

    Incluir a árvore de trabalho é o que permite o uso sem commit: basta a IA engenheira
    gravar o JSON em `propostas/` que o monitor o pega no próximo ciclo.
    """
    if not sha_antigo:
        saida = git("ls-tree", "-r", "--name-only", sha_novo, "--", "05_Interface_Auditoria/propostas/")
        lista = [a for a in (saida or "").splitlines() if a.endswith(".json")]
    else:
        saida = git("diff", "--name-only", f"{sha_antigo}..{sha_novo}",
                    "--", "05_Interface_Auditoria/propostas/")
        lista = [a for a in (saida or "").splitlines() if a.endswith(".json")]
    if os.path.isdir(DIR_PROP):
        for nome in sorted(os.listdir(DIR_PROP)):
            if nome.endswith(".json") and not nome.startswith("."):
                lista.append(os.path.relpath(os.path.join(DIR_PROP, nome), RAIZ))
    return sorted(set(lista))


def veredito_para(caminho, assinatura):
    """Já existe veredito para exatamente este conteúdo?"""
    try:
        with open(os.path.join(RAIZ, caminho), encoding="utf-8") as fh:
            identificador = json.load(fh).get("id")
    except Exception:
        return False
    arq = os.path.join(DIR_VER, f"{identificador}.json")
    if not os.path.exists(arq):
        return False
    try:
        with open(arq, encoding="utf-8") as fh:
            return json.load(fh).get("proposta_sha256") == assinatura
    except Exception:
        return False


def auditar(conteudo, nome_origem, modo, saida_dir):
    """Grava o conteúdo da proposta num temporário, roda o auditor e devolve (estado, texto_saida)."""
    tmp = os.path.join(DIR_INTERFACE, ".proposta_em_auditoria.json")
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(conteudo)
    cmd = [sys.executable, AUDITOR, tmp, "--json", "--md", "--saida-dir", saida_dir]
    if modo == "rapido":
        cmd.append("--reusar-medicoes")
    if modo == "cfd":
        cmd.append("--com-cfd")
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=3600, cwd=RAIZ)
    estado = {0: "APROVADO/RESSALVAS", 2: "REPROVADO", 3: "BLOQUEADO"}.get(r.returncode, "ERRO")
    try:
        identificador = json.loads(conteudo).get("id", "?")
    except Exception:
        identificador = "?"
    return estado, identificador, r.returncode, (r.stdout or "") + (r.stderr or "")


def commit_publicar(mensagem, push):
    git("add", "05_Interface_Auditoria/vereditos")
    git("add", "-A", "05_Interface_Auditoria")
    if not (git("status", "--porcelain") or "").strip():
        return "nada a registrar"
    git("-c", "user.name=Auditor IA", "-c", "user.email=auditor@local", "commit", "-q", "-m", mensagem)
    if not push:
        return "veredito commitado localmente (sem --push)"
    r = subprocess.run(["git", "-C", RAIZ, "push"], capture_output=True, text=True, timeout=300)
    if r.returncode == 0:
        return "veredito publicado no remoto"
    return f"FALHA ao publicar (git push): {r.stderr.strip()[:200]} — o veredito está commitado localmente"


def main():
    ap = argparse.ArgumentParser(description="Monitor de auditoria (Modo B)")
    ap.add_argument("--ramo", default=None, help="ramo a vigiar (padrão: o ramo atual)")
    ap.add_argument("--remoto", action="store_true", help="fazer git fetch antes de cada ciclo")
    ap.add_argument("--push", action="store_true", help="publicar o veredito no remoto")
    ap.add_argument("--intervalo", type=float, default=20.0, help="segundos entre ciclos")
    ap.add_argument("--modo", choices=["rapido", "completo", "cfd"], default="completo")
    ap.add_argument("--uma-vez", action="store_true", help="um ciclo apenas (para CI/teste)")
    args = ap.parse_args()

    ramo = args.ramo or (git("rev-parse", "--abbrev-ref", "HEAD") or "HEAD")
    alvo = f"origin/{ramo}" if args.remoto else ramo
    estado = carregar_estado()
    if estado.get("ramo") != ramo:
        estado = {"ramo": ramo, "ultimo_sha": None, "auditadas": {}}
        log(f"vigiando o ramo '{ramo}' (primeira passada: só registra o ponto de partida)")

    os.makedirs(DIR_VER, exist_ok=True)
    ciclo = 0
    while True:
        ciclo += 1
        if args.remoto:
            r = subprocess.run(["git", "-C", RAIZ, "fetch", "--quiet", "origin", ramo],
                               capture_output=True, text=True, timeout=300)
            if r.returncode != 0:
                log(f"AVISO: git fetch falhou ({r.stderr.strip()[:120]}) — seguindo com o que há localmente")
        sha = git("rev-parse", alvo)
        if sha is None:
            log(f"AVISO: não consegui resolver '{alvo}'; tento de novo no próximo ciclo")
        elif sha != estado["ultimo_sha"]:
            anteriores = estado["ultimo_sha"]
            log(f"novo estado em {alvo}: {sha[:10]} (anterior {str(anteriores)[:10]})")
            alvos = propostas_entre(anteriores, sha)
            log(f"   propostas tocadas: {alvos or 'nenhuma'}")
            for caminho in alvos:
                conteudo = git("show", f"{sha}:{caminho}") if anteriores else None
                if conteudo is None:
                    with open(os.path.join(RAIZ, caminho), encoding="utf-8") as fh:
                        conteudo = fh.read()
                assinatura = sha256_txt(conteudo)
                if estado["auditadas"].get(caminho) == assinatura:
                    log(f"   {caminho}: já auditado nesta vigília com este conteúdo, pulando")
                    continue
                if veredito_para(caminho, assinatura):
                    log(f"   {caminho}: já existe veredito para este conteúdo, pulando")
                    estado["auditadas"][caminho] = assinatura
                    continue
                log(f"   auditando {caminho} (modo {args.modo})...")
                t0 = time.time()
                situacao, identificador, codigo, saida = auditar(conteudo, caminho, args.modo, DIR_VER)
                dt = time.time() - t0
                log(f"   veredito {identificador}: {situacao} em {dt:.0f} s (código {codigo})")
                for linha in saida.splitlines():
                    if linha.startswith(("   BLOQUEIO", "   ALERTA", "ESTADO:")):
                        log(f"      {linha.strip()}")
                estado["auditadas"][caminho] = assinatura
                log("   " + commit_publicar(f"auditoria: veredito {identificador} ({situacao})", args.push))
            estado["ultimo_sha"] = sha
            salvar_estado(estado)
        else:
            log(f"sem novidades ({alvo} em {str(sha)[:10]}) | {len(estado['auditadas'])} proposta(s) auditada(s)")
        if args.uma_vez:
            return 0
        time.sleep(max(2.0, args.intervalo))


if __name__ == "__main__":
    sys.exit(main())
