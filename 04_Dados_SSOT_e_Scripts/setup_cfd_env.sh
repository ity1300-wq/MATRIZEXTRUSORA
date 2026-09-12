#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# setup_cfd_env.sh - Ambiente completo de CAD + CFD headless (servidor/CI)
# ---------------------------------------------------------------------------
# Instala e prepara, sem interface gráfica:
#   cadquery   -> leitura dos STEP, medições e extração de seções
#   gmsh       -> geração de malhas 3D/2D a partir da própria geometria STEP
#   scikit-fem -> solver de elementos finitos (Stokes generalizado / p-Laplaciano)
#   pyamg      -> solvers algébricos multigrid
#   meshio     -> troca de formatos de malha
#
# Além do pip, compila stubs das bibliotecas gráficas (libGL, libGLU, libX*),
# que os binários linkam mesmo quando usados apenas para cálculo. Elas nunca são
# chamadas em modo headless; os stubs existem só para satisfazer o linker.
#
# Uso:
#     bash setup_cfd_env.sh
#     export LD_LIBRARY_PATH="$PWD/04_Dados_SSOT_e_Scripts/.headless_gl:$LD_LIBRARY_PATH"
#     python 04_Dados_SSOT_e_Scripts/verify_geometry_ssot.py
#     python 04_Dados_SSOT_e_Scripts/cfd_land_crosssection.py
#
# Obs.: em estação de trabalho com driver de vídeo, o libGL real já existe e os
# stubs são inofensivos (ficam por último no LD_LIBRARY_PATH).
# ---------------------------------------------------------------------------
set -euo pipefail

DIR_DADOS="$(cd "$(dirname "$0")" && pwd)"
DIR_STUB="$DIR_DADOS/.headless_gl"
VENV="${VENV:-$HOME/.venv}"
mkdir -p "$DIR_STUB"

echo "== 1/3 Interpretador Python =="
if [ ! -x "$VENV/bin/python" ]; then
    echo "  criando ambiente virtual em $VENV"
    python3 -m venv "$VENV" --system-site-packages
fi
"$VENV/bin/python" -m pip install --quiet --upgrade pip >/dev/null 2>&1 || true
"$VENV/bin/python" --version

echo "== 2/3 Bibliotecas de CAD e CFD =="
"$VENV/bin/python" -m pip install --quiet cadquery gmsh scikit-fem meshio pyamg

echo "== 3/3 Stubs das bibliotecas gráficas (linkagem headless) =="
"$VENV/bin/python" - "$DIR_STUB" <<'PY'
import glob, os, re, subprocess, sys

destino = sys.argv[1]
PADRAO = re.compile(r"^(gl[A-Z]|glX|glu[A-Z]|egl[A-Z]|OSMesa|wgl[A-Z]|"
                    r"Xcursor|XRender|Xrender|Xft|Xinerama|XFixes|Xkb|XInput|Xi[A-Z])")
raiz = os.path.dirname(os.path.dirname(sys.executable))

syms = set()
for lib in glob.glob(os.path.join(raiz, "**", "*.so*"), recursive=True):
    try:
        out = subprocess.run(["nm", "-D", "--undefined-only", lib],
                             capture_output=True, text=True, timeout=60).stdout
    except Exception:
        continue
    for linha in out.splitlines():
        p = linha.split()
        if len(p) == 2:
            s = p[1].split("@")[0]
            if PADRAO.match(s):
                syms.add(s)

if not syms:
    print("  nenhum símbolo gráfico pendente encontrado")
    sys.exit(0)

syms = sorted(syms)
fonte = os.path.join(destino, "stubs.c")
with open(fonte, "w") as f:
    f.write("/* Stubs de linkagem headless - não usados em cálculo */\n#include <stddef.h>\n")
    for s in syms:
        f.write(f"void *{s}(void){{return NULL;}}\n")

for lib in ["libGL.so.1", "libGLU.so.1", "libXrender.so.1", "libXcursor.so.1",
            "libXfixes.so.3", "libXft.so.2", "libXinerama.so.1"]:
    subprocess.run(["gcc", "-shared", "-fPIC", f"-Wl,-soname,{lib}",
                    "-o", os.path.join(destino, lib), fonte], check=True)
print(f"  {len(syms)} símbolos gráficos resolvidos por stub em {destino}")
PY

echo
echo "== Verificação rápida =="
LD_LIBRARY_PATH="$DIR_STUB:${LD_LIBRARY_PATH:-}" "$VENV/bin/python" -c "
import cadquery, gmsh, skfem, meshio, pyamg
gmsh.initialize(['-nopopup'])
print('  cadquery ', cadquery.__version__)
print('  scikit-fem', skfem.__version__)
print('  meshio   ', meshio.__version__)
print('  gmsh     ', gmsh.option.getString('General.Version'))
gmsh.finalize()
print('  pyamg    OK')
"
echo
echo "Ambiente pronto. Use sempre:"
echo "  export LD_LIBRARY_PATH=\"$DIR_STUB:\$LD_LIBRARY_PATH\""
