"""
EXPLORADOR DE ACOMODO DE FUROS - MATRIZ JONATHA
================================================
Nao se chuta a posicao de furo de pino, cartucho, termopar ou refrigacao:
este script MEDE o aco disponivel ao redor do canal de fluxo aprovado e devolve
as posicoes viaveis, com a parede de aco real de cada uma.

Dois tipos de furo
------------------
1. "radial"  - furo cego que entra pela face externa cilindrica (raio do
   envelope no plano Z) e para antes de tocar o canal. Vale p/ cartucho de
   resistencia, termopar, refrigeração e aperto.
       y_fundo = |Y| do canal naquele ponto + parede   (e que para a broca)
       parede lateral = distancia do cilindro ao canal, medida ACIMA do fundo
   A distancia e medida no plano XZ (o furo e paralelo a Y), mas somente dos
   pontos de canal que estao DENTRO do alcance axial do furo: usar a reta
   infinita seria conservador demais e eliminaria posicoes perfeitamente
   usinaveis ao lado do land.

2. "particao" - furo cego que abre no plano de biparticao Y=0 (pino de
   alinhamento). Aqui a condicao e puramente plana: o disco do furo no plano
   XZ nao pode alcancar a projecao do canal, e o corpo precisa ter |Y| >=
   profundidade do furo.

Saidas: tabela no console e, com --json, `acomodo_furos.json`.

Requisitos: cadquery. Em conteiner sem libGL: bash setup_headless_gl.sh
"""

import argparse
import json
import math
import os

import cadquery as cq
import numpy as np

from OCP.BRep import BRep_Tool
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.TopAbs import TopAbs_FACE
from OCP.TopExp import TopExp_Explorer
from OCP.TopLoc import TopLoc_Location
from OCP.TopoDS import TopoDS

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DIR_CAD = os.path.join(RAIZ, "07_CAD_Matrizes", "Matriz_Jonatha_v27_OFICIAL")
DIR_DADOS = os.path.join(RAIZ, "04_Dados_SSOT_e_Scripts")

MESH = 0.05     # deflexao da tesselação do canal [mm]
CELULA = 1.5    # grade espacial para vizinhança [mm]

# Envelope externo: (z_de, z_ate, diametro) - mesma fonte da auditoria
ENVELOPE = [(0.00, 69.90, 93.00), (69.90, 80.70, 89.50), (80.70, 109.00, 79.50)]

# Recursos: nome -> dict(raio, parede_min, profundidade_min, tipo, descricao)
RECURSOS = {
    "pino_alinhamento": dict(raio=2.00, parede=3.00, prof=12.0, tipo="particao",
                             desc="furo Ø4 H7 x 12 p/ pino de alinhamento"),
    "cartucho_Ø9.5": dict(raio=4.75, parede=4.00, prof=22.0, tipo="radial",
                          desc="cartucho de resistência Ø9,5 mm"),
    "termopar_Ø4.8": dict(raio=2.40, parede=3.50, prof=18.0, tipo="radial",
                          desc="poço de termopar Ø4,8 mm"),
    "refrigeração_Ø8": dict(raio=4.00, parede=3.50, prof=18.0, tipo="radial",
                            desc="canal de refrigeração Ø8,0 mm"),
    "aperto_M8": dict(raio=4.50, parede=5.00, prof=20.0, tipo="radial",
                      desc="furo radial Ø9 mm p/ M8 de aperto das metades"),
}


def r_envelope(z):
    for z0, z1, d in ENVELOPE:
        if z0 - 1e-9 <= z <= z1 + 1e-9:
            return d / 2.0
    return None


def malha(solido, deflexao=MESH):
    """Pontos da superficie do solido (X, Y, Z)."""
    shp = solido.wrapped if hasattr(solido, "wrapped") else solido
    BRepMesh_IncrementalMesh(shp, deflexao, False, 0.1, True)
    blocos, exp = [], TopExp_Explorer(shp, TopAbs_FACE)
    while exp.More():
        face = TopoDS.Face_s(exp.Current())
        loc = TopLoc_Location()
        tri = BRep_Tool.Triangulation_s(face, loc)
        if tri is not None:
            trsf = loc.Transformation()
            n = tri.NbNodes()
            arr = np.empty((n, 3))
            for i in range(1, n + 1):
                q = tri.Node(i).Transformed(trsf)
                arr[i - 1] = (q.X(), q.Y(), q.Z())
            blocos.append(arr)
        exp.Next()
    return np.vstack(blocos)


class Canal:
    """Consulta espacial do canal: |Y| maximo e distancia lateral no plano XZ."""

    def __init__(self, pts):
        self.x = np.abs(pts[:, 0])          # o canal e simetrico em X
        self.y = pts[:, 1]
        self.z = pts[:, 2]
        self.pts = pts
        ch = math.ceil(self.x.max() / CELULA) + 1
        cz = math.ceil(self.z.max() / CELULA) + 1
        self.grid = {}
        ix = (self.x / CELULA).astype(int)
        iz = (self.z / CELULA).astype(int)
        for i in range(len(ix)):
            self.grid.setdefault((ix[i], iz[i]), []).append(i)
        self.grid = {k: np.array(v) for k, v in self.grid.items()}

    def _vizinhos(self, X, Z, raio_busca):
        k = int(math.ceil(raio_busca / CELULA))
        ix, iz = int(abs(X) / CELULA), int(Z / CELULA)
        idx = []
        for i in range(max(ix - k, 0), ix + k + 1):
            for j in range(max(iz - k, 0), iz + k + 1):
                v = self.grid.get((i, j))
                if v is not None:
                    idx.append(v)
        return np.concatenate(idx) if idx else np.empty(0, dtype=int)

    def y_max_disco(self, X, Z, raio):
        """|Y| maximo do canal dentro do raio do furo (+ folga de usinagem)."""
        i = self._vizinhos(X, Z, raio + 1.0)
        if not len(i):
            return 0.0
        d = np.hypot(self.x[i] - abs(X), self.z[i] - Z)
        m = d <= raio + 0.5
        return float(np.abs(self.y[i][m]).max()) if m.any() else 0.0

    def parede_lateral(self, X, Z, raio, y_fundo, teto=12.0):
        """Menor distancia do cilindro ao canal, considerando so os pontos de
        canal que ficam ACIMA do fundo do furo (na regiao que o furo atravessa)."""
        i = self._vizinhos(X, Z, raio + teto)
        if not len(i):
            return teto
        acima = np.abs(self.y[i]) >= y_fundo
        if not acima.any():
            return teto
        d = np.hypot(self.x[i][acima] - abs(X), self.z[i][acima] - Z) - raio
        return float(np.clip(d.min(), 0.0, teto))


def avaliar(c, X, Z, r, parede, prof, tipo):
    """Retorna metricas reais de um furo paralelo a Y no ponto (X, Z)."""
    re = r_envelope(Z)
    if re is None or re <= abs(X) + r:
        return None
    y_fora = math.sqrt(re * re - X * X)          # onde a broca entra
    if tipo == "particao":
        y_c = c.y_max_disco(X, Z, r + parede)      # canal sob o disco do furo
        if y_c > 1e-6:
            return None                             # disco invade a projecao do canal
        d = min(c.parede_lateral(X, Z, r, 0.0), 12.0)
        if d < parede:
            return None
        if y_fora < prof:
            return None
        return dict(X=round(X, 2), Z=round(Z, 2), parede=round(d, 2),
                    profundidade=prof, y_fundo=0.0, y_fora=round(y_fora, 2))
    y_c = c.y_max_disco(X, Z, r)
    y_fundo = y_c + parede
    if y_fundo >= y_fora:
        return None
    L = y_fora - y_fundo
    if L < prof:
        return None
    lat = c.parede_lateral(X, Z, r, y_fundo)
    if lat < parede - 1e-6:
        return None
    return dict(X=round(X, 2), Z=round(Z, 2), parede=round(min(L, lat), 2),
                profundidade=round(L, 2), y_fundo=round(y_fundo, 2),
                y_fora=round(y_fora, 2))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--dx", type=float, default=1.0)
    ap.add_argument("--dz", type=float, default=1.0)
    args = ap.parse_args()

    canal_sol = max(cq.importers.importStep(
        os.path.join(DIR_CAD, "MatrizJonatha_Canal_Fluxo.step")
    ).solids().vals(), key=lambda s: s.Volume())
    P = malha(canal_sol)
    c = Canal(P)
    print(f"Canal tesselado: {len(P)} pontos | |X|max={np.abs(P[:,0]).max():.3f} "
          f"| |Y|max={np.abs(P[:,1]).max():.3f} | Z={P[:,2].min():.2f}..{P[:,2].max():.2f}")

    grade = {}
    saida = {}
    for nome, cfg in RECURSOS.items():
        lista = []
        for X in np.arange(2.0, 46.0, args.dx):
            for Z in np.arange(1.5, 108.0, args.dz):
                m = avaliar(c, X, Z, cfg["raio"], cfg["parede"], cfg["prof"], cfg["tipo"])
                if m:
                    lista.append(m)
        # ordena por folga disponivel (parede) e depois por proximidade do land
        lista.sort(key=lambda d: (-round(d["parede"], 1), abs(d["Z"] - 100)))
        grade[nome] = lista
        print(f"\n### {nome} - {cfg['desc']}")
        print(f"    posições viáveis: {len(lista)}")
        if not lista:
            print("      >>> NENHUMA POSICAO VIABEL dentro do envelope")
            continue
        # resumo por faixa de Z, para enxergar as zonas utilizaveis
        zonas = {}
        for d in lista:
            k = int(d["Z"] // 10) * 10
            a = zonas.setdefault(k, [0, 0.0])
            a[0] += 1
            a[1] = max(a[1], d["parede"])
        print("    zonas Z (faixa: n_posições / melhor parede): " +
              ", ".join(f"{k:3d}-{k+9}: {v[0]}/{v[1]:.1f}" for k, v in sorted(zonas.items())))
        for d in lista[:6]:
            print(f"      X=±{d['X']:6.2f}  Z={d['Z']:6.2f}  parede={d['parede']:5.2f} mm  "
                  f"prof.útil={d['profundidade']:6.2f} mm  fundo em Y={d['y_fundo']:5.2f}")

    saida = {k: {"descricao": RECURSOS[k]["desc"], "tipo": RECURSOS[k]["tipo"],
                 "raio_mm": RECURSOS[k]["raio"], "qtd_viaveis": len(v),
                 "melhores": v[:40]} for k, v in grade.items()}
    if args.json:
        out = os.path.join(DIR_DADOS, "acomodo_furos.json")
        with open(out, "w", encoding="utf-8") as f:
            json.dump({"fonte": "07_CAD_Matrizes/Matriz_Jonatha_v27_OFICIAL/MatrizJonatha_Canal_Fluxo.step",
                       "pontos_malha": int(len(P)), "deflexao_mm": MESH,
                       "envelope": ENVELOPE, "recursos": saida},
                      f, indent=2, ensure_ascii=False)
        print(f"\n-> {out}")
    return saida


if __name__ == "__main__":
    main()
