#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# restaurar_workspace.sh - devolve o repo ao estado de trabalho depois de o sandbox ser recriado
# ---------------------------------------------------------------------------
# Porque este script existe: o ambiente desta conversa e efemero. Ja custou trabalho duas vezes -
# o `cadquery` sumir (e o portao parar no primeiro script) e, em 2026-09-13, os ATALHOS de `01_/` e `02_/`
# nao voltarem do snapshot, o `git add -A` interpretar isso como "apagaram os modelos" e cometeu a remocao.
# Este script e idempotente e faz as seis coisas que a gente vinha fazendo a mao, na ordem:
#
#   bash 04_Dados_SSOT_e_Scripts/restaurar_workspace.sh          # so prepara e confere
#   bash 04_Dados_SSOT_e_Scripts/restaurar_workspace.sh --portao # prepara e roda o portao rapido
#
set -uo pipefail

AQUI="$(cd "$(dirname "$0")" && pwd)"
RAIZ="$(cd "$AQUI/.." && pwd)"
cd "$RAIZ"
[ -d .headless_gl ] 2>/dev/null || true
export LD_LIBRARY_PATH="$AQUI/.headless_gl:${LD_LIBRARY_PATH:-}"
RODA_PORTAO=0
[ "${1:-}" = "--portao" ] && RODA_PORTAO=1

passo() { printf '\n\033[1m> %s\033[0m\n' "$1"; }
ok()    { printf '   ok: %s\n' "$1"; }
aviso() { printf '   ATENCAO: %s\n' "$1"; }

passo "1/6  identidade do git (o sandbox novo nao traz .git/config)"
if [ -z "$(git config user.email 2>/dev/null)" ]; then
    git config user.name  "Arena Agent"
    git config user.email "agent@arena.local"
    ok "configurada no escopo do repo (nao global): $(git config user.name) <$(git config user.email)>"
else
    ok "ja havia: $(git config user.name) <$(git config user.email)>"
fi

passo "2/6  remoto 'origem' (tambem nao sobrevive; o push usa o token que esta no ambiente)"
git remote get-url origem >/dev/null 2>&1 && ok "origem = $(git remote get-url origem)" \
    || { git remote add origem https://github.com/ity1300-wq/MATRIZEXTRUSORA && ok "origem adicionada"; }
if [ -n "${GH_TOKEN:-}${GITHUB_TOKEN:-}" ]; then
    ok "ha token no ambiente; para empurrar: git push \"https://x-access-token:\${GH_TOKEN:-$GITHUB_TOKEN}@github.com/ity1300-wq/MATRIZEXTRUSORA\" <branch>:<branch>"
elif [ -n "${GH_HOST_TOKEN_FILE:-}" ] && [ -s "${GH_HOST_TOKEN_FILE:-/dev/null}" ]; then
    ok "token lido de \$GH_HOST_TOKEN_FILE"
else
    aviso "sem token a vista: o push precisa de credencial (nao a grave no repo nem em .git/config)"
fi

passo "3/6  arquivos rastreados que sumiram da arvore (e assim que os atalhos de 01_/ e 02_/ voltam)"
mapfile -t SUMIDOS < <(git ls-files -d)
if [ "${#SUMIDOS[@]}" -gt 0 ]; then
    printf '   %d ausentes: %s...\n' "${#SUMIDOS[@]}" "${SUMIDOS[0]}"
    # cuidado restaurado por caminho, NUNCA `git checkout HEAD -- .`: com trabalho na area isso jogaria
    # fora as mudancas nao comitadas (foi exatamente assim que dois patches meus se perderam em 2026-09-13)
    git checkout HEAD -- "${SUMIDOS[@]}" && ok "restaurados do HEAD, um caminho por vez"
else
    ok "nenhum arquivo rastreado ausente"
fi
QUEBRADOS=$(find . -xtype l 2>/dev/null | wc -l)
[ "$QUEBRADOS" -gt 0 ] && aviso "$QUEBRADOS atalho(s) quebrado(s) - rode 'git checkout HEAD -- 01_CAD_MatrizJonatha_Oficial 02_CAD_Modelos_Historicos'" \
    || ok "todos os atalhos resolvem"

passo "4/6  dependencias python (cadquery modela; ezdxf le o DXF; gmsh+scikit-fem sao a malha 3D)"
FALTAM=""
for m in cadquery ezdxf gmsh skfem; do
    python3 -c "import $m" 2>/dev/null || FALTAM="$FALTAM $m"
done
if [ -n "${FALTAM# }" ]; then
    echo "   faltam:$FALTAM - instalando (leva ~1 min):"
    python3 -m pip install --quiet $FALTAM 2>&1 | tail -2
    for m in $FALTAM; do python3 -c "import $m" 2>/dev/null && ok "$m instalada" || aviso "$m continua fora"; done
else
    ok "todas ja presentes: $(python3 -c "import cadquery,gmsh,skfem,ezdxf;print('cadquery',cadquery.__version__,'| gmsh',gmsh.__version__ if hasattr(gmsh,'__version__') else '4.x','| skfem',skfem.__version__)" 2>/dev/null)"
fi

passo "5/6  stubs de GL/GLU (sem root nao ha apt install; sem eles o cadquery e o gmsh nem importam)"
tem_stub=0
for f in libGL.so.1 libGLU.so.1; do [ -e "$AQUI/.headless_gl/$f" ] || tem_stub=1; done
if [ "$tem_stub" = "1" ]; then
    bash "$AQUI/setup_headless_gl.sh" >/dev/null 2>&1 || true
    bash "$AQUI/setup_headless_glu.sh" >/dev/null 2>&1 || true
    ok "stubs gerados em $AQUI/.headless_gl (export LD_LIBRARY_PATH ja apontado neste script)"
else
    ok "stubs ja existem em .headless_gl/"
fi

passo "6/6  estado do repo"
printf '   branch: %s | HEAD %s | sujo: %s arquivo(s)\n' "$(git rev-parse --abbrev-ref HEAD)" \
    "$(git rev-parse --short HEAD)" "$(git status --porcelain | wc -l)"
git log --oneline -1 | sed 's/^/   ultimo commit: /'
if [ "$RODA_PORTAO" = "1" ]; then
    echo
    python3 "$AQUI/verificar_cadeia.py" --rapido 2>&1 | tail -6
else
    echo "   (rode 'bash 04_Dados_SSOT_e_Scripts/restaurar_workspace.sh --portao' para conferir o portao agora)"
fi

echo
echo "Pronto. Se o portao abriu, o proximo passo e o que estava pendente no CONTINUIDADE.md - nao re-meça"
echo "geometria ja medida: os numeros estao em 04_/auditoria_step_correlacoes.json e nos JSON gerados."
