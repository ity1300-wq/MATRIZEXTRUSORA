#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# setup_headless_glu.sh - stubs de libGL.so.1 e libGLU.so.1 para o gmsh headless
# ---------------------------------------------------------------------------
# O setup_headless_gl.sh cria o stub de libGL que o CadQuery/OCP precisa. O binding python
# do gmsh (libgmsh.so.4.15) pede MAIS: as funcoes glu* (o renderizador OpenGL dele) e
# tambem gl* que o stub do OCP nao exporta (ex.: glColor3d). Sem root, `apt install
# libglu1-mesa` nao roda, então este script remontas duas bibliotecas vazias com a uniao do
# que OCP e gmsh exigem - malhar e resolver NUNCA chama nada disso, e so o loader que quer ver
# os simbolos.
#
#     bash 04_Dados_SSOT_e_Scripts/setup_headless_gl.sh      # stub do OCP (nao precisa de novo)
#     bash 04_Dados_SSOT_e_Scripts/setup_headless_glu.sh     # GL + GLU com a uniao (este)
#     export LD_LIBRARY_PATH="$PWD/04_Dados_SSOT_e_Scripts/.headless_gl:$LD_LIBRARY_PATH"
#     python3 -c "import gmsh; gmsh.initialize(); print(gmsh.VERSION)"
#
# Idempotente: se o sistema ja tem as libs reais, ele avisa e nao faz nada.
# ---------------------------------------------------------------------------
set -euo pipefail

AQUI="$(cd "$(dirname "$0")" && pwd)"
DIR="$AQUI/.headless_gl"
SP="$(python3 -c "import sysconfig;print(sysconfig.get_paths()['purelib'])")"

tem_gl() { ldconfig -p 2>/dev/null | grep -q "libGL.so.1"; }
tem_glu() { ldconfig -p 2>/dev/null | grep -q "libGLU.so.1"; }

if tem_gl && tem_glu; then
    echo "libGL e libGLU reais ja existem no sistema - nada a fazer."
    exit 0
fi
if [ ! -x "$(command -v gcc 2>/dev/null || true)" ]; then
    echo "ERRO: gcc nao encontrado (apt install build-essential)." >&2
    exit 1
fi

mkdir -p "$DIR"
LIBS=$(python3 - "$SP" <<'PY'
import glob, os, sys
sp = sys.argv[1]
alvos = sorted(glob.glob("/usr/local/lib/libgmsh*") + glob.glob("/usr/lib/libgmsh*")
               + glob.glob("/usr/lib/x86_64-linux-gnu/libgmsh*"))
for pkg in ("cadquery", "OCP"):
    alvos += sorted(glob.glob(os.path.join(sp, pkg, "**", "*.so*"), recursive=True))
print("\n".join(p for p in dict.fromkeys(alvos) if os.path.exists(p)))
PY
)

GL=$(SP="$SP" DIR="$DIR" python3 - "$LIBS" <<'PY'
import glob, os, re, subprocess, sys
libs = [l for l in sys.argv[1].split("\n") if l.strip()]
# sp = primeiro elemento de libs e o site-packages? nao: passamos via ambiente
sp = os.environ.get("SP", "")
for padrao in ("OCP*.so*", "cadquery*/**/*.so*", "_cadquery*/**/*.so*"):
    libs += sorted(glob.glob(os.path.join(sp, padrao), recursive=True))
gl, glu = set(), set()
# preserva o que o stub antigo do OCP ja exportava (nao podemos regredir o CAD)
for stub in ("libGL.so.1", "libGLU.so.1"):
    antigo = os.path.join(os.environ.get("DIR", ""), stub)
    if os.path.exists(antigo):
        out = subprocess.run(["nm", "-D", "--defined-only", antigo], capture_output=True,
                             text=True).stdout
        for nome in re.findall(r"\b(gl[A-Z]\w+|glu[A-Z]\w+|glX[A-Z]\w+)\b", out):
            (glu if nome.startswith("glu") else gl).add(nome)
for lib in libs:
    try:
        out = subprocess.run(["nm", "-D", "--undefined-only", lib], capture_output=True,
                             text=True, timeout=120).stdout
    except Exception:
        continue
    for nome in re.findall(r"\b(gl[A-Z]\w+|glu[A-Z]\w+|glX[A-Z]\w+)\b", out):
        (glu if nome.startswith("glu") else gl).add(nome)
print("GL " + " ".join(sorted(gl)))
print("GLU " + " ".join(sorted(glu)))
PY
)

GL_SYMS=$(printf '%s\n' "$GL" | awk '/^GL /{sub(/^GL /,"");print}')
GLU_SYMS=$(printf '%s\n' "$GL" | awk '/^GLU /{sub(/^GLU /,"");print}')
[ -n "${GLU_SYMS//[[:space:]]/}" ] || GLU_SYMS="gluCylinder gluDeleteQuadric gluDisk gluLookAt gluNewQuadric gluPickMatrix gluProject gluSphere gluUnProject"

gera() {  # $1 = arquivo .c, $2 = lista de simbolos
    {
        echo "/* stub gerado por setup_headless_glu.sh - satisfaz o loader; nunca e chamado no"
        echo "   caminho de modelagem/malha/solver (OpenGL e GLU so servem ao renderizador). */"
        for fcn in $2; do echo "int $fcn(void){return 0;}"; done
    } > "$1"
}

gera "$DIR/glstub_union.c" "$GL_SYMS"
gcc -shared -fPIC -O1 -o "$DIR/libGL.so.1" "$DIR/glstub_union.c"
gera "$DIR/glustub.c" "$GLU_SYMS"
gcc -shared -fPIC -O1 -o "$DIR/libGLU.so.1" "$DIR/glustub.c"
ln -sf libGL.so.1 "$DIR/libGL.so"
ln -sf libGLU.so.1 "$DIR/libGLU.so"

echo "stubs gerados em $DIR  ->  GL: $(printf '%s\n' $GL_SYMS | wc -w) simbolos, GLU: $(printf '%s\n' $GLU_SYMS | wc -w)"
echo "use:  export LD_LIBRARY_PATH=\"$DIR:\$LD_LIBRARY_PATH\""
