"""PORTA DE VERIFICACAO DA CADEIA - um comando, tudo re-medido, nada confiado.

Roda a cadeia real do projeto e depois CHECA invariantes entre os arquivos. Existe porque nesta
sessao dois numeros apodreceram por copia manual: o '1372,276 mm3' do bloco [F] (corrigido para
2744,550 por um estudo independente) e o '14,3 mm' de protrusao (correto: 14,00, os 0,30 sao a
folga do degrau). Cada checagem abaixo pega uma dessas classes.

  python 04_Dados_SSOT_e_Scripts/verificar_cadeia.py [--rapido] [--com-estudos]

Checagens:
  1. a cadeia roda inteira sem erro de execucao (gerador, verificadores, relatorio, AUTO_PROMPT);
  2. matriz v28.1: 64 itens, 0 nao conformes;
  3. interface: exatamente 1 nao conforme, e ele E o conhecido (folga axial dos cartuchos);
  4. STEP do cabecote sem flange: reimporta com desvio 0 e nao tira metal da banda da matriz;
  5. os numeros que os documentos citam sao os dos JSON gerados (anti-copia-apodrecida);
  6. nenhuma chave de documento guarda numero de booleano copiado a mao;
  7. `MatrizJonatha.step` (v27.0) e `02_CAD_Modelos_Historicos/` intactos (regras 1 e 2).
"""
import argparse
import json
import os
import re
import subprocess
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, ".."))
DIR_DOC = os.path.join(RAIZ, "03_Relatorios_e_Documentacao")
sys.path.insert(0, AQUI)

CADEIA = ["gerar_matriz_v28.py", "verificar_v28.py --json --md", "verificar_interface_cabecote.py --json --md",
          "gerar_cabecote_ex030.py", "gerar_relatorio_v28.py", "generate_auto_prompt.py",
          "verify_geometry_ssot.py", "verify_legacy_dies.py --json"]
CADEIA_ESTUDOS = ["estudar_funis.py --so-texto", "estudar_recuo_cartuchos.py --so-texto",
                  "medir_perfil_cabecote.py --json 04_Dados_SSOT_e_Scripts/cabecote_perfil.json",
                  "medir_perfis_matrizes_x_cabecote.py --json --md",
                  "gerar_desenho_2d_cabecote_matriz.py"]  # o PDF 2D: 3,7 s, so le os STEP
NC_ESPERADA_INTERFACE = "Folga axial da furação de saída à frente do metal do cabeçote"
# (arquivo .md, chave no JSON de onde o numero vem, quantas casas) - o par que ja apodreceu uma vez
# casas = quantas o documento imprime (o par (chave, casas) e o que detecta copia desatualizada)
# o 4o elemento opcional e o nome do JSON de onde o numero vem (padrao: interface_cabecote.json)
PARES_DOC_JSON = [("INTERFASE_CABECOTE_EX030.md", "numeros/acesso_furacao_cenarios/desenho DXF medido/metal_no_caminho_mm3", 3),
                  ("INTERFASE_CABECOTE_EX030.md", "numeros/cartuchos_z_min_mm", 2),
                  ("INTERFASE_CABECOTE_EX030.md", "numeros/area_contato_degrau_mm2", 1),
                  ("PROJETO_DFM_V28_MATRIZ_JONATHA.md", "numeros/dp_1d_bar", 1),
                  ("AUDITORIA_GEOMETRICA_MATRIZ_JONATHA.md",
                   "proposta_v28_dfm/numeros recalculados/tau_parede_land_kPa", 1, "cad_die_parameters.json"),
                  ("INTERFASE_INTERNA_CABECOTE_X_MATRIZES.md", "diferença_copo_x_gedeon_medida/diferença_mm", 2,
                   "perfis_matrizes_x_cabecote.json"),
                  ("INTERFASE_INTERNA_CABECOTE_X_MATRIZES.md",
                   "o_que_um_chanfro_interno_muda/metal_removido_do_cabeçote_mm3", 3,
                   "perfis_matrizes_x_cabecote.json")]

falhas = []


def ok(msg):
    print(f"  [OK  ] {msg}")


def no(msg):
    print(f"  [FALHA] {msg}")
    falhas.append(msg)


def checa(cond, msg_ok, msg_no=None):
    """Helper obrigatorio: escrever (ok if c else no(m)) deixa o SUCESSO mudo, e foi assim que
    [6] e [7] passaram sem dizer nada."""
    (ok if cond else no)(msg_ok if cond else (msg_no or msg_ok))


# exit code 1 nestes dois scripts NAO e crash: e o veredito "ha nao conformes". O certo e exigir o
# numero esperado de NC - se outro numero aparecer, ou se o script morrer sem imprimir resumo, a
# porta fecha.
ESPERA_NC = {"verificar_interface_cabecote.py": 1, "verify_geometry_ssot.py": 2}


def roda(cmd, rotulo):
    r = subprocess.run(cmd.split(), cwd=RAIZ, capture_output=True, text=True, timeout=3600)
    saida = (r.stdout or "") + (r.stderr or "")
    esperado = ESPERA_NC.get(rotulo.split()[0])
    m = re.search(r"(\d+)\s+n[ãa]o\s+conformes", saida, re.I)   # o resumo e minusculo na interface
    if esperado is not None and m and int(m.group(1)) == esperado and r.returncode in (0, 1):
        ok(f"{rotulo} -> {esperado} não conforme(s) como esperado (veredito, não erro)")
    elif r.returncode != 0:
        no(f"{rotulo} terminou com erro {r.returncode}: " + saida.strip()[-300:])
    else:
        ok(f"{rotulo}")
    return r


def pega(d, caminho):
    v = d
    for parte in caminho.split("/"):
        v = v[parte]
    return v


def fmt(v, casas):
    return f"{v:.{casas}f}".replace(".", ",")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rapido", action="store_true",
                    help="só as checagens, sem re-rodar nada (nao pega crash de verificador)")
    ap.add_argument("--com-estudos", action="store_true", help="inclui os estudos (lento)")
    a = ap.parse_args()
    os.environ.setdefault("LD_LIBRARY_PATH", os.path.join(AQUI, ".headless_gl") + ":" + os.environ.get("LD_LIBRARY_PATH", ""))

    if not a.rapido:
        print("\n[1] cadeia")
        for cmd in CADEIA + (CADEIA_ESTUDOS if a.com_estudos else []):
            roda(f"python 04_Dados_SSOT_e_Scripts/{cmd}", cmd.split()[0])
    else:
        print("[1] cadeia NAO rodada (--rapido). O que segue compara documentos com os JSON que ja estao "
              "no disco: detecta numero apodrecido, nao detecta crash dentro de um script. Para isso, "
              "rode sem a flag.")

    print("\n[2] matriz v28.1")
    v = json.load(open(os.path.join(AQUI, "verificacao_v28.json"), encoding="utf-8"))
    checa(v["nao_conformes"] == 0, f"verificação {v['itens']} itens | {v['conformes']} conformes | "
          f"{v['nao_conformes']} não conformes",
          f"matriz com {v['nao_conformes']} não conformes")
    if v["nao_conformes"]:
        for l in v["checagens"]:
            if l["status"] == "NAO_CONFORME":
                print(f"         -> {l['item']} (medido {l.get('medido')})")

    print("\n[3] interface com o cabeçote")
    i = json.load(open(os.path.join(AQUI, "interface_cabecote.json"), encoding="utf-8"))
    ncs = [l["item"] for l in i["checagens"] if l["status"] == "NAO_CONFORME"]
    if len(ncs) == 1 and ncs[0].startswith(NC_ESPERADA_INTERFACE):
        ok(f"1 NC, e ela é a conhecida: {ncs[0][:60]}…")
    else:
        no(f"NC inesperada na interface: {ncs}")
    acessos = i["numeros"]["acesso_furacao_cenarios"]
    gov = i["numeros"]["cenario_que_governa"]
    ok(f"cenario que governa = '{gov}' (folga {acessos[gov]['folga_axial_min_mm']:.3f} mm, "
       f"bloqueio {acessos[gov]['metal_no_caminho_mm3']:.3f} mm³)")
    zmin = i["numeros"]["cartuchos_z_min_mm"]
    checa(abs(zmin - (95.00 + 4.75)) < 1e-6,
          f"Z mínimo dos cartuchos = {zmin:.3f} mm (face do nariz 95,00 + raio do cartucho 4,75)",
          f"Z mínimo dos cartuchos {zmin:.3f} != 99,750 mm - a conta da face do nariz mudou")

    print("\n[4] STEP do cabeçote sem flange")
    cs = json.load(open(os.path.join(AQUI, "cabecote_step.json"), encoding="utf-8"))
    checa(abs(cs["metal_removido_ate_a_banda_da_matriz_mm3"]) < 1e-6,
          f"metal removido até a banda da matriz: {cs['metal_removido_ate_a_banda_da_matriz_mm3']} mm³",
          f"o corte tirou metal da banda: {cs['metal_removido_ate_a_banda_da_matriz_mm3']} mm³")
    desvio = max(abs(cs[k]) for k in cs if k.startswith("desvio_round_trip"))
    checa(desvio < 1e-6, f"round-trip dos STEP reimportados: desvio {desvio:.6f} mm³",
          f"STEP não reimporta igual: desvio {desvio:.6f} mm³")
    checa(abs(cs["interferencia_matriz_x_sem_flange_mm3"]) < 1e-6,
          f"interferência com a matriz: {cs['interferencia_matriz_x_sem_flange_mm3']} mm³",
          f"matriz interfere no cabeçote: {cs['interferencia_matriz_x_sem_flange_mm3']} mm³")

    print("\n[5] documentos citam o número do JSON (anti-copia apodrecida)")
    doc = {}
    for nome in os.listdir(DIR_DOC):
        if nome.endswith(".md"):
            doc[nome] = open(os.path.join(DIR_DOC, nome), encoding="utf-8").read()
    cache_json = {"interface_cabecote.json": i}
    for par in PARES_DOC_JSON:
        arq, chave, casas = par[0], par[1], par[2]
        nome_json = par[3] if len(par) > 3 else "interface_cabecote.json"
        if arq not in doc:
            no(f"{arq} não existe")
            continue
        if nome_json not in cache_json:
            cache_json[nome_json] = json.load(open(os.path.join(AQUI, nome_json), encoding="utf-8"))
        valor = fmt(pega(cache_json[nome_json], chave), casas)
        checa(valor in doc[arq], f"{arq}: '{valor}' ({chave}) presente",
              f"{arq} NÃO contém '{valor}' de {chave} - documento desatualizado em relação ao JSON")

    print("\n[6] nenhuma chave guarda número de booleano copiado à mão")
    cab = json.load(open(os.path.join(AQUI, "cabecote_ex030.json"), encoding="utf-8"))
    espelho = json.dumps(cab["conferencia_com_a_medicao_do_usuario"], ensure_ascii=False)
    checa("metal_no_caminho_mm3" not in espelho, "bloco espelho sem número de booleano copiado",
          "conferencia_com_a_medicao_do_usuario voltou a copiar número de booleano")
    checa("NAO copiados aqui" in espelho, "bloco espelho aponta para o JSON gerado",
          "falta o aviso de ponteiro no bloco espelho")

    print("\n[7] regras 1 e 2 do projeto")
    st = subprocess.run(["git", "status", "--porcelain"], cwd=RAIZ, capture_output=True, text=True).stdout.splitlines()
    hist = [l for l in st if "02_CAD_Modelos_Historicos/" in l]
    checa(not hist, "02_CAD_Modelos_Historicos/ intocada (regra 2)",
          f"02_CAD_Modelos_Historicos/ FOI TOCADA: {hist}")
    mestre = [l for l in st if l.rstrip().endswith("01_CAD_MatrizJonatha_Oficial/MatrizJonatha.step")]
    checa(not mestre, "MatrizJonatha.step (v27.0) intocado (regra 1)",
          f"o master v27.0 foi modificado: {mestre}")
    ok(f"{len(st)} arquivos alterados no total (STEP regenerados contam ruído de export, não de geometria)")

    print("\n" + "=" * 78)
    if falhas:
        print(f"PORTA FECHADA: {len(falhas)} checagem(ns) falharam")
        for f in falhas:
            print(f"  - {f}")
        return 1
    print("PORTA ABERTA: cadeia verde e documentos batendo com os JSON gerados")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
