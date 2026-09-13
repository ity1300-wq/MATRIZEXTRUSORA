#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# setup_headless_gl.sh - Ambiente CAD headless (CadQuery/OCCT em contêiner)
# ---------------------------------------------------------------------------
# Os binários do CadQuery (OCP/OCCT) linkam dinamicamente contra libGL.so.1,
# biblioteca de renderização que normalmente não existe em servidores/contêineres
# sem interface gráfica. Como a modelagem geométrica (booleans, medições e
# exportação STEP) NÃO usa OpenGL, basta um stub vazio para satisfazer o linker.
#
# Este script compila o stub e informa como usá-lo:
#
#     bash setup_headless_gl.sh                 # compila o stub em .headless_gl/
#     export LD_LIBRARY_PATH="$PWD/.headless_gl:$LD_LIBRARY_PATH"
#     python verify_geometry_ssot.py
#
# Obs.: em estações de trabalho com driver de vídeo instalado, o libGL real já
# existe e este script é desnecessário.
# ---------------------------------------------------------------------------
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)/.headless_gl"
mkdir -p "$DIR"

if [ ! -x "$(command -v gcc 2>/dev/null || true)" ]; then
    echo "ERRO: gcc não encontrado. Instale o compilador (apt install build-essential)."
    exit 1
fi

# Coleta todos os símbolos GL/GLX exigidos pelos binários instalados
SYMS="$(python - <<'PY'
import glob, os, re, site, subprocess

# Somente símbolos da API OpenGL/GLX: glX..., gl + Maiúscula (glClear, glGenLists),
# egl..., OSMesa... (descarta globfree@GLIBC, glibc versionado etc.)
PADRAO = re.compile(r"^(gl[A-Z]|glX|egl[A-Z]|OSMesa|wgl[A-Z]|glu[A-Z])")

raizes = [os.path.dirname(os.path.dirname(p)) for p in site.getsitepackages()]
padroes = []
for r in raizes:
    padroes += glob.glob(os.path.join(r, "**", "*.so*"), recursive=True)

syms = set()
for lib in padroes:
    try:
        out = subprocess.run(["nm", "-D", "--undefined-only", lib],
                             capture_output=True, text=True, timeout=30).stdout
    except Exception:
        continue
    for linha in out.splitlines():
        partes = linha.split()
        if len(partes) == 2:
            base = partes[1].split("@")[0]
            if PADRAO.match(base):
                syms.add(base)
print("\n".join(sorted(syms)))
PY
)"

if [ -z "$SYMS" ]; then
    echo "Nenhum símbolo GL pendente encontrado - libGL provavelmente disponível."
    exit 0
fi

{
    echo "/* Stub de libGL.so.1 - uso exclusivo para modelagem CAD headless */"
    echo "#include <stddef.h>"
    while IFS= read -r s; do
        [ -n "$s" ] && echo "void *$s(void) { return NULL; }"
    done <<< "$SYMS"
} > "$DIR/glstub.c"

gcc -shared -fPIC -Wl,-soname,libGL.so.1 -o "$DIR/libGL.so.1" "$DIR/glstub.c"

echo "Stub compilado: $DIR/libGL.so.1"
echo "Símbolos resolvidos: $(wc -l < "$DIR/glstub.c")"
echo
echo "Use assim:"
echo "  export LD_LIBRARY_PATH=\"$DIR:\$LD_LIBRARY_PATH\""
echo "  python 04_Dados_SSOT_e_Scripts/verify_geometry_ssot.py"
