#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
painel_auditoria.py — Modo B sem GitHub: painel vivo + auditoria automática
============================================================================

Sobe um servidor local (preview no navegador) que:

  * VIGIA a pasta `05_Interface_Auditoria/propostas/`: proposta nova ou alterada é auditada
    automaticamente e o veredito aparece na tela em segundos;
  * permite COLAR uma proposta no formulário e auditar na hora (ponte humana, Modo C);
  * expõe uma API para a IA engenheira: `POST /api/auditar` com o JSON da proposta devolve
    o veredito (não precisa de git, nem de token do GitHub).

Uso:
    python 05_Interface_Auditoria/scripts/painel_auditoria.py --porta 8000
    python .../painel_auditoria.py --modo rapido      # auditorias em ~2 s (reaproveita medições)

Rotas:
    GET  /                      painel (status, propostas, vereditos, log)
    GET  /veredito/<ID>         veredito renderizado
    GET  /api/estado            estado do painel (JSON)
    GET  /api/vereditos         lista de vereditos (JSON)
    GET  /api/vereditos/<ID>    veredito completo (JSON)
    POST /api/auditar           corpo = proposta; ?modo=rapido|completo|cfd&sincrono=1|0
    POST /auditar               formulário do painel
    GET  /log                   log em texto
"""

import argparse
import datetime
import hashlib
import html
import json
import os
import queue
import re
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

RAIZ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
DIR_INTERFACE = os.path.join(RAIZ, "05_Interface_Auditoria")
DIR_PROP = os.path.join(DIR_INTERFACE, "propostas")
DIR_VER = os.path.join(DIR_INTERFACE, "vereditos")
DIR_BASE = os.path.join(DIR_INTERFACE, "baseline")
AUDITOR = os.path.join(DIR_INTERFACE, "scripts", "auditar_proposta.py")
ARQ_BASELINE = os.path.join(DIR_BASE, "MATRIZ_3_v27.json")

TRAVA = threading.Lock()          # só uma auditoria por vez (CPU)
FILA = queue.Queue()
ESTADO = {
    "iniciado_em": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "executando": None,
    "historico": [],              # {id, estado, quando, modo, segundos, origem}
    "log": [],
    "ciclos": 0,
    "ultima_varredura": None,
    "modo_padrao": "completo",
}
LOG_MAX = 400


def registrar(msg):
    linha = f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}"
    ESTADO["log"].append(linha)
    del ESTADO["log"][:-LOG_MAX]
    print(linha, flush=True)


def sha256(caminho):
    h = hashlib.sha256()
    with open(caminho, "rb") as fh:
        for bloco in iter(lambda: fh.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


# ------------------------------------------------------------------ auditoria
def auditar_proposta(texto, origem, modo):
    """Roda o auditor num subprocesso. Devolve (id, estado, veredito_dict, saida)."""
    tmp = os.path.join(DIR_INTERFACE, ".proposta_em_auditoria.json")
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(texto)
    try:
        identificador = json.loads(texto).get("id", "?")
    except Exception:
        identificador = "?"
    cmd = [sys.executable, AUDITOR, tmp, "--json", "--md", "--saida-dir", DIR_VER]
    if modo == "rapido":
        cmd.append("--reusar-medicoes")
    if modo == "cfd":
        cmd.append("--com-cfd")
    t0 = time.time()
    if not TRAVA.acquire(blocking=False):
        registrar(f"{identificador}: aguardando a auditoria em curso terminar...")
        TRAVA.acquire()
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=3600, cwd=RAIZ)
    finally:
        TRAVA.release()
    segundos = round(time.time() - t0, 1)
    caminho_ver = os.path.join(DIR_VER, f"{identificador}.json")
    veredito = None
    if os.path.exists(caminho_ver):
        with open(caminho_ver, encoding="utf-8") as fh:
            veredito = json.load(fh)
    situacao = (veredito or {}).get("estado", "ERRO")
    registrar(f"{identificador}: {situacao} em {segundos} s (modo {modo}, origem {origem})")
    if veredito is None:
        registrar("   a auditoria não produziu veredito; veja o log abaixo")
        for linha in ((r.stdout or "") + (r.stderr or "")).splitlines()[-6:]:
            registrar("   | " + linha[:220])
    return identificador, situacao, veredito, (r.stdout or "") + (r.stderr or ""), segundos


def trabalhador():
    while True:
        trabalho, evento = FILA.get()
        ESTADO["executando"] = {"origem": trabalho["origem"], "modo": trabalho["modo"],
                                "desde": datetime.datetime.now().strftime("%H:%M:%S")}
        try:
            trabalho["resultado"] = auditar_proposta(trabalho["texto"], trabalho["origem"], trabalho["modo"])
            with TRAVA:
                ESTADO["historico"].insert(0, {
                    "id": trabalho["resultado"][0], "estado": trabalho["resultado"][1],
                    "quando": datetime.datetime.now().strftime("%d/%m %H:%M:%S"),
                    "modo": trabalho["modo"], "segundos": trabalho["resultado"][4],
                    "origem": trabalho["origem"]})
                del ESTADO["historico"][40:]
        except Exception as exc:                                    # pragma: no cover
            trabalho["resultado"] = ("?", "ERRO", None, str(exc), 0)
            registrar(f"ERRO na auditoria: {exc}")
        finally:
            ESTADO["executando"] = None
            evento.set()
            FILA.task_done()


def vigia(intervalo=10.0):
    """Varre a pasta de propostas; audita o que for novo (ou tiver mudado)."""
    vistos = {}
    while True:
        try:
            os.makedirs(DIR_PROP, exist_ok=True)
            alteradas = []
            for nome in sorted(os.listdir(DIR_PROP)):
                if not nome.endswith(".json") or nome.startswith("."):
                    continue
                caminho = os.path.join(DIR_PROP, nome)
                try:
                    assinatura = sha256(caminho)
                except OSError:
                    continue
                if vistos.get(caminho) == assinatura:
                    continue
                vistos[caminho] = assinatura
                alteradas.append((nome, caminho, assinatura))
                if not ESTADO.get("_primeira_varredura"):
                    continue        # primeira varredura só registra, não re-audita o que já existe
                if ja_auditada(caminho, assinatura):
                    registrar(f"{nome}: já existe veredito para este conteúdo, pulando")
                    continue
                with open(caminho, encoding="utf-8") as fh:
                    texto = fh.read()
                registrar(f"{nome}: proposta detectada, auditando (modo {ESTADO['modo_padrao']})")
                enfileirar(texto, f"vigia:{nome}", ESTADO["modo_padrao"])
            ESTADO["_primeira_varredura"] = True
            ESTADO["ultima_varredura"] = datetime.datetime.now().strftime("%H:%M:%S")
            ESTADO["ciclos"] += 1
        except Exception as exc:                                    # pragma: no cover
            registrar(f"ERRO na varredura: {exc}")
        time.sleep(intervalo)


def ja_auditada(caminho_proposta, assinatura):
    try:
        with open(caminho_proposta, encoding="utf-8") as fh:
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


def enfileirar(texto, origem, modo, sincrono=False, espera=1800):
    evento = threading.Event()
    trabalho = {"texto": texto, "origem": origem, "modo": modo, "resultado": None}
    FILA.put((trabalho, evento))
    if sincrono:
        evento.wait(timeout=espera)
    return trabalho


def info_baseline():
    if not os.path.exists(ARQ_BASELINE):
        return None
    with open(ARQ_BASELINE, encoding="utf-8") as fh:
        d = json.load(fh)
    return {"matriz": d.get("matriz"), "congelado_em": d.get("congelado_em"),
            "metricas": {k: d.get("metricas", {}).get(k) for k in
                         ("dp_total_bar", "land_util_mm", "area_fenda_mm2", "parede_labio_mm",
                          "tau_parede_land_kpa", "forca_abertura_kN", "uniformidade_nucleo_pct")},
            "modelo": d.get("modelo_parametrico")}


# ------------------------------------------------------------------ markdown -> html
def md_para_html(md):
    linhas = md.splitlines()
    saida, i = [], 0
    while i < len(linhas):
        linha = linhas[i]
        if linha.startswith("```"):
            bloco = []
            i += 1
            while i < len(linhas) and not linhas[i].startswith("```"):
                bloco.append(linhas[i]); i += 1
            saida.append("<pre>" + html.escape("\n".join(bloco)) + "</pre>")
        elif linha.startswith("|"):
            tabela = []
            while i < len(linhas) and linhas[i].startswith("|"):
                tabela.append([c.strip() for c in linhas[i].strip("|").split("|")]); i += 1
            cab = tabela[0]
            corpo = [l for l in tabela[2:]] if len(tabela) > 1 and set(tabela[1][0]) <= set(":- ") else tabela[1:]
            t = ["<table><thead><tr>" + "".join(f"<th>{inline(c)}</th>" for c in cab) + "</tr></thead><tbody>"]
            for l in corpo:
                t.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in l) + "</tr>")
            t.append("</tbody></table>")
            saida.append("".join(t))
            continue
        elif linha.startswith("<") and any(linha.startswith(x) for x in ("<details", "</details", "<summary")):
            saida.append(linha)
        elif linha.startswith("#### "):
            saida.append(f"<h5>{inline(linha[5:])}</h5>")
        elif linha.startswith("### "):
            saida.append(f"<h4>{inline(linha[4:])}</h4>")
        elif linha.startswith("## "):
            saida.append(f"<h3>{inline(linha[3:])}</h3>")
        elif linha.startswith("# "):
            saida.append(f"<h2>{inline(linha[2:])}</h2>")
        elif linha.startswith("- "):
            itens = []
            while i < len(linhas) and linhas[i].startswith("- "):
                itens.append(f"<li>{inline(linhas[i][2:])}</li>"); i += 1
            saida.append("<ul>" + "".join(itens) + "</ul>")
            continue
        elif linha.startswith("> "):
            saida.append(f"<blockquote>{inline(linha[2:])}</blockquote>")
        elif linha.strip() == "---":
            saida.append("<hr>")
        elif not linha.strip():
            pass
        else:
            saida.append(f"<p>{inline(linha)}</p>")
        i += 1
    return "\n".join(saida)


def inline(txt):
    txt = html.escape(txt)
    txt = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", txt)
    txt = re.sub(r"`(.+?)`", r"<code>\1</code>", txt)
    txt = re.sub(r"\[(.+?)\]\((.+?)\)", r"<a href='\2'>\1</a>", txt)
    return txt


COR_ESTADO = {"APROVADO": "#1a7f37", "APROVADO_COM_RESSALVAS": "#9a6700",
              "REPROVADO": "#bc4c00", "BLOQUEADO": "#b42318", "ERRO": "#6e7781"}


def pagina(conteudo, titulo="Auditoria — Matriz 3"):
    recarrega = "<meta http-equiv='refresh' content='5'>" if ESTADO["executando"] or not FILA.empty() else ""
    return f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
{recarrega}<title>{html.escape(titulo)}</title><style>
 body{{font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;margin:0;background:#f6f7f9;color:#1f2328}}
 header{{background:#0d1117;color:#e6edf3;padding:14px 22px}}
 header b{{font-size:17px}} header span{{color:#8b949e;font-size:13px;margin-left:10px}}
 main{{max-width:1100px;margin:0 auto;padding:18px 22px 60px}}
 .cart{{background:#fff;border:1px solid #d0d7de;border-radius:10px;padding:14px 16px;margin-bottom:14px}}
 .grade{{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px}}
 .k{{font-size:12px;color:#57606a;text-transform:uppercase;letter-spacing:.04em}}
 .v{{font-size:19px;font-weight:600;margin-top:2px}}
 table{{border-collapse:collapse;width:100%;font-size:14px}}
 th,td{{border:1px solid #d0d7de;padding:6px 9px;text-align:left;vertical-align:top}}
 th{{background:#f6f8fa}} code{{background:#eff1f3;padding:1px 5px;border-radius:4px;font-size:12.5px}}
 pre{{background:#0d1117;color:#e6edf3;padding:11px;border-radius:8px;overflow:auto;font-size:12.5px}}
 .selo{{display:inline-block;padding:2px 9px;border-radius:20px;color:#fff;font-weight:600;font-size:12.5px}}
 textarea{{width:100%;min-height:190px;font-family:ui-monospace,Menlo,Consolas,monospace;font-size:12.5px;
          border:1px solid #d0d7de;border-radius:8px;padding:9px}}
 button{{background:#1f6feb;color:#fff;border:0;border-radius:8px;padding:9px 16px;font-size:14px;cursor:pointer}}
 button.sec{{background:#eaeef2;color:#1f2328}}
 blockquote{{margin:8px 0;padding:6px 12px;border-left:4px solid #d0d7de;color:#57606a;background:#f6f8fa}}
 a{{color:#0969da}}</style></head><body>
<header><b>🤖 Auditoria — Matriz 3 (Jonatha)</b>
<span>Protocolo v1.0 · painel vivo do Modo B · iniciado {ESTADO['iniciado_em']}</span></header>
<main>{conteudo}</main></body></html>"""


def vereditos_em_disco():
    lista = []
    if os.path.isdir(DIR_VER):
        for nome in sorted(os.listdir(DIR_VER)):
            if not nome.endswith(".json"):
                continue
            try:
                with open(os.path.join(DIR_VER, nome), encoding="utf-8") as fh:
                    v = json.load(fh)
                lista.append({"id": v.get("proposta_id"), "estado": v.get("estado"),
                              "data": (v.get("data") or "")[:16].replace("T", " "),
                              "resumo": v.get("resumo", ""), "reutilizadas": v.get("medicoes_reutilizadas"),
                              "nao_auditavel": len(v.get("nao_auditavel") or []),
                              "bloqueios": len(v.get("bloqueios") or [])})
            except Exception:
                pass
    return sorted(lista, key=lambda x: str(x["id"]))


def tela_painel():
    base = info_baseline()
    exec_ = ESTADO["executando"]
    linhas_hist = "".join(
        f"<tr><td><a href='/veredito/{html.escape(h['id'])}'>{html.escape(h['id'])}</a></td>"
        f"<td><span class='selo' style='background:{COR_ESTADO.get(h['estado'],'#57606a')}'>"
        f"{html.escape(h['estado'])}</span></td><td>{h['quando']}</td><td>{h['modo']}</td>"
        f"<td>{h['segundos']} s</td><td>{html.escape(str(h['origem']))}</td></tr>"
        for h in ESTADO["historico"][:12]) or "<tr><td colspan='6'>nenhuma auditoria ainda</td></tr>"
    log = "<br>".join(html.escape(l) for l in ESTADO["log"][-14:])
    vs = vereditos_em_disco()
    linhas_ver = "".join(
        f"<tr><td><a href='/veredito/{html.escape(str(v['id']))}'>{html.escape(str(v['id']))}</a></td>"
        f"<td><span class='selo' style='background:{COR_ESTADO.get(v['estado'],'#57606a')}'>"
        f"{html.escape(str(v['estado']))}</span></td><td>{html.escape(v['data'])}</td>"
        f"<td>{'reutilizadas' if v['reutilizadas'] else 'do zero'}</td><td>{v['nao_auditavel']}</td>"
        f"<td>{html.escape(v['resumo'][:90])}</td></tr>" for v in vs
    ) or "<tr><td colspan='6'>nenhum veredito gravado</td></tr>"
    metricas = base["metricas"] if base else {}
    cartoes = "".join(
        f"<div class='cart'><div class='k'>{html.escape(k)}</div><div class='v'>{v}</div></div>"
        for k, v in metricas.items())
    return pagina(f"""
<div class='cart'>
  <div class='k'>Situação</div>
  <div class='v'>{'⏳ auditando agora…' if exec_ else '✅ em espera — vigiando a pasta de propostas'}</div>
  <div style='color:#57606a;font-size:13px;margin-top:5px'>
    ciclos de varredura: {ESTADO['ciclos']} · última: {ESTADO['ultima_varredura'] or '—'} ·
    modo padrão: <code>{ESTADO['modo_padrao']}</code> · fila: {FILA.qsize()}
  </div>
</div>
<div class='cart'>
  <div class='k'>Baseline congelado</div>
  <div style='font-size:14px;margin:5px 0 10px'>{html.escape((base or {}).get('matriz','—'))} —
     congelado em {html.escape((base or {}).get('congelado_em','—'))}</div>
  <div class='grade'>{cartoes}</div>
</div>
<div class='cart'>
  <h3 style='margin:0 0 10px'>Vereditos em disco</h3>
  <table><thead><tr><th>proposta</th><th>veredito</th><th>data</th><th>medições</th><th>não auditado</th>
  <th>resumo</th></tr></thead><tbody>{linhas_ver}</tbody></table>
</div>
<div class='cart'>
  <h3 style='margin:0 0 10px'>Auditorias desta sessão</h3>
  <table><thead><tr><th>proposta</th><th>veredito</th><th>quando</th><th>modo</th><th>duração</th>
  <th>origem</th></tr></thead><tbody>{linhas_hist}</tbody></table>
</div>
<div class='cart'>
  <h3 style='margin:0 0 6px'>Colar uma proposta para auditar agora</h3>
  <div style='color:#57606a;font-size:13px;margin-bottom:8px'>
    Cole o JSON do engenheiro (ou de outra IA). O auditor mede o repositório e devolve o veredito.
  </div>
  <form method='post' action='/auditar'>
    <textarea name='proposta' placeholder='{ "{ ... proposta PRP-XXXX ... }" }'></textarea>
    <div style='margin-top:9px'>
      <label><input type='radio' name='modo' value='completo' checked> completo (medições do zero, ~2 min)</label>
      &nbsp;&nbsp;<label><input type='radio' name='modo' value='rapido'> rápido (reaproveita medições, ~2 s)</label>
      &nbsp;&nbsp;<label><input type='radio' name='modo' value='cfd'> com CFD (~8 min)</label>
      &nbsp;&nbsp;<button type='submit'>Auditar</button>
    </div>
  </form>
</div>
<div class='cart'>
  <h3 style='margin:0 0 6px'>Como a IA engenheira fala com este painel</h3>
  <pre>POST /api/auditar?modo=rapido&amp;sincrono=1
Content-Type: application/json

{{ "protocolo": "1.0", "id": "PRP-0007", ... }}

-&gt; 200 OK  com o veredito completo em JSON</pre>
</div>
<div class='cart'><div class='k'>Log</div><div style='font-size:12.5px;line-height:1.6'>{log}</div></div>
""")


class Tratador(BaseHTTPRequestHandler):
    server_version = "PainelAuditoria/1.0"

    def log_message(self, *args):
        pass

    def _responder(self, codigo, corpo, tipo="text/html; charset=utf-8"):
        dados = corpo.encode("utf-8") if isinstance(corpo, str) else corpo
        self.send_response(codigo)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(dados)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(dados)

    def do_GET(self):
        caminho = urlparse(self.path).path
        if caminho == "/":
            return self._responder(200, tela_painel())
        if caminho == "/log":
            return self._responder(200, "\n".join(ESTADO["log"]), "text/plain; charset=utf-8")
        if caminho == "/api/estado":
            return self._responder(200, json.dumps({
                "executando": ESTADO["executando"], "ciclos": ESTADO["ciclos"],
                "ultima_varredura": ESTADO["ultima_varredura"], "fila": FILA.qsize(),
                "historico": ESTADO["historico"], "baseline": info_baseline()},
                ensure_ascii=False, indent=2), "application/json; charset=utf-8")
        if caminho == "/api/vereditos":
            lista = []
            if os.path.isdir(DIR_VER):
                for nome in sorted(os.listdir(DIR_VER)):
                    if nome.endswith(".json"):
                        try:
                            with open(os.path.join(DIR_VER, nome), encoding="utf-8") as fh:
                                v = json.load(fh)
                            lista.append({"id": v.get("proposta_id"), "estado": v.get("estado"),
                                          "data": v.get("data"), "resumo": v.get("resumo")})
                        except Exception:
                            pass
            return self._responder(200, json.dumps(lista, ensure_ascii=False, indent=2),
                                   "application/json; charset=utf-8")
        m = re.match(r"^/(api/)?veredito/([A-Za-z0-9_\-]+)$", caminho)
        if m:
            identificador = m.group(2)
            arq_json = os.path.join(DIR_VER, f"{identificador}.json")
            arq_md = os.path.join(DIR_VER, f"{identificador}.md")
            if m.group(1):
                if os.path.exists(arq_json):
                    with open(arq_json, encoding="utf-8") as fh:
                        return self._responder(200, fh.read(), "application/json; charset=utf-8")
                return self._responder(404, json.dumps({"erro": "veredito não encontrado"}),
                                       "application/json; charset=utf-8")
            if os.path.exists(arq_md):
                with open(arq_md, encoding="utf-8") as fh:
                    corpo = md_para_html(fh.read())
                return self._responder(200, pagina(f"<div class='cart'><a href='/'>&larr; painel</a>"
                                                   f"</div>{corpo}", f"Veredito {identificador}"))
            return self._responder(404, pagina("<div class='cart'>veredito não encontrado</div>"))
        return self._responder(404, pagina("<div class='cart'>rota não encontrada</div>"))

    def do_POST(self):
        parsed = urlparse(self.path)
        q = parse_qs(parsed.query)
        tamanho = int(self.headers.get("Content-Length") or 0)
        corpo = self.rfile.read(tamanho).decode("utf-8", "replace")
        modo = (q.get("modo", ["completo"])[0] or "completo").lower()
        if modo not in ("rapido", "completo", "cfd"):
            modo = "completo"
        if parsed.path == "/api/auditar":
            sincrono = q.get("sincrono", ["1"])[0] not in ("0", "false", "nao")
            trabalho = enfileirar(corpo, "api", modo, sincrono=sincrono)
            if not sincrono:
                return self._responder(202, json.dumps({"aceito": True, "modo": modo},
                                                        ensure_ascii=False), "application/json; charset=utf-8")
            resultado = trabalho["resultado"]
            if not resultado or resultado[2] is None:
                saida = (resultado or ("", "", None, "sem resultado", 0))[3]
                return self._responder(500, json.dumps(
                    {"erro": "a auditoria não produziu veredito", "log": saida[-1500:]},
                    ensure_ascii=False, indent=2), "application/json; charset=utf-8")
            return self._responder(200, json.dumps(resultado[2], ensure_ascii=False, indent=2),
                                   "application/json; charset=utf-8")
        if parsed.path == "/auditar":
            campos = parse_qs(corpo)
            texto = (campos.get("proposta", [""])[0] or "").strip()
            if not texto:
                return self._responder(400, pagina("<div class='cart'>proposta vazia</div>"))
            enfileirar(texto, "painel", modo)
            ESTADO["_ultima_colagem"] = datetime.datetime.now().strftime("%H:%M:%S")
            return self._redirecionar("/")
        return self._responder(404, pagina("<div class='cart'>rota não encontrada</div>"))

    def _redirecionar(self, destino):
        self.send_response(303)
        self.send_header("Location", destino)
        self.send_header("Content-Length", "0")
        self.end_headers()


def main():
    ap = argparse.ArgumentParser(description="Painel vivo de auditoria (Modo B)")
    ap.add_argument("--porta", type=int, default=8000)
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--modo", choices=["rapido", "completo", "cfd"], default="completo",
                    help="modo das auditorias automáticas da pasta de propostas")
    ap.add_argument("--intervalo", type=float, default=10.0)
    args = ap.parse_args()

    ESTADO["modo_padrao"] = args.modo
    registrar(f"painel iniciado em http://{args.host}:{args.porta} (modo padrão: {args.modo})")
    registrar(f"vigiando {os.path.relpath(DIR_PROP, RAIZ)}/ a cada {args.intervalo:.0f} s")

    threading.Thread(target=trabalhador, daemon=True).start()
    threading.Thread(target=vigia, args=(args.intervalo,), daemon=True).start()

    servidor = ThreadingHTTPServer((args.host, args.porta), Tratador)
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        registrar("painel encerrado")
    return 0


if __name__ == "__main__":
    sys.exit(main())
