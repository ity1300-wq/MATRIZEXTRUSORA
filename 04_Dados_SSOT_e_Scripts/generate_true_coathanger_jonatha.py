import cadquery as cq

print("=== RESTRUTURANDO MATRIZ JONATHA COM MANIFOLD CABIDE 3D (TRUE COAT-HANGER) ===")

# 1. ENVELOPE CILÍNDRICO EXTERNO (100% Fidedigno: D1=93.0, D2=89.5, D3=79.5 mm)
c1 = cq.Workplane("XY").circle(93.00 / 2.0).extrude(69.90)
c2 = cq.Workplane("XY").workplane(offset=69.90).circle(89.50 / 2.0).extrude(10.80)
c3 = cq.Workplane("XY").workplane(offset=80.70).circle(79.50 / 2.0).extrude(28.30)
outer_body = c1.union(c2).union(c3)

# 2. CONSTRUÇÃO DO MANIFOLD COAT-HANGER (CABIDE 3D HYDRODINÂMICO)
# Seção Z=0.00 mm: Círculo perfeito Ø75.60 mm na boca de entrada
s0 = cq.Workplane("XY").circle(75.60 / 2.0)

# Seção Z=25.00 mm: Reservatório central do cabide (slot2D 35.0 x 12.0 mm)
s1 = s0.workplane(offset=25.00).slot2D(35.00, 12.00)

# Seção Z=70.00 mm: Linha de espalhamento das asas do cabide (slot2D 75.0 x 3.5 mm)
s2 = s1.workplane(offset=45.00).slot2D(75.00, 3.50)

# Seção Z=99.00 mm: Início do land de calibração (slot2D 75.0 x 1.50 mm)
s3 = s2.workplane(offset=29.00).slot2D(75.00, 1.50)

# Transição Reológica Coat-Hanger Lofting 3D (Z=0 a Z=99.00 mm)
coathanger_manifold = s3.loft(ruled=False)

# 3. LAND PARALELO DE CALIBRAÇÃO FINAL (Z=99.00 a Z=109.00 mm, L=10.00 mm com R0.75 mm)
land = cq.Workplane("XY").workplane(offset=99.00).slot2D(75.00, 1.50).extrude(10.00)

# 4. MICRO-CHANFRO DE ALÍVIO DIVERGENTE DE 1,50 mm x 45° NA SAÍDA (Z=109.00 mm)
chamfer_tool = (cq.Workplane("XY")
                .workplane(offset=107.50).slot2D(75.00, 1.50)
                .workplane(offset=1.50).slot2D(78.00, 4.50)
                .loft(ruled=True))

flow_cavity = coathanger_manifold.union(land).union(chamfer_tool)

# Subtração da Cavidade no Corpo de Aço
die_solid = outer_body.cut(flow_cavity)

# 5. BIPARTIÇÃO E ALINHAMENTO NO PLANO HORIZONTAL (Y = 0)
wp = cq.Workplane("XZ").add(die_solid)
body_a = wp.split(keepTop=True, keepBottom=False)  # Body_A (Metade Inferior Y <= 0)
body_b = wp.split(keepTop=False, keepBottom=True) # Body_B (Metade Superior Y >= 0)

# 6. FUROS DE ALINHAMENTO NA METADE A
hole1 = cq.Workplane("XZ", origin=(-41.50, 0, 54.50)).circle(2.00).extrude(12.00)
hole2 = cq.Workplane("XZ", origin=(41.50, 0, 54.50)).circle(2.00).extrude(12.00)
body_a = body_a.cut(hole1).cut(hole2)

# ==============================================================================
# SALVAR ARQUIVOS STEP DA MATRIZ JONATHA (TRUE COAT-HANGER)
# ==============================================================================

# 1. Matriz Jonatha Usinada Fechada Oca (Apenas Aço)
assy_usinada = cq.Assembly(name="MatrizJonatha")
assy_usinada.add(body_a, name="Camada_01_Body_A", color=cq.Color(0.68, 0.75, 0.85))
assy_usinada.add(body_b, name="Camada_02_Body_B", color=cq.Color(0.55, 0.62, 0.72))
assy_usinada.save("/home/user/MatrizJonatha.step", "STEP")

# 2. Vista Explodida (+40 mm em Y)
assy_explodida = cq.Assembly(name="MatrizJonatha_Explodida")
assy_explodida.add(body_a, name="Camada_01_Body_A_Inferior", color=cq.Color(0.68, 0.75, 0.85))
assy_explodida.add(body_b.translate((0, 40.0, 0)), name="Camada_02_Body_B_Superior_Deslocado", color=cq.Color(0.55, 0.62, 0.72))
assy_explodida.save("/home/user/MatrizJonatha_Explodida.step", "STEP")

# 3. Montagem Completa com Macho do Polímero
assy_completa = cq.Assembly(name="MatrizJonatha_Com_Fluxo")
assy_completa.add(body_a, name="Camada_01_Body_A", color=cq.Color(0.68, 0.75, 0.85))
assy_completa.add(body_b, name="Camada_02_Body_B", color=cq.Color(0.55, 0.62, 0.72))
assy_completa.add(flow_cavity, name="Camada_03_Canal_Fluxo_Polimero", color=cq.Color(0.0, 0.55, 0.90, 0.60))
assy_completa.save("/home/user/MatrizJonatha_Com_Fluxo.step", "STEP")

# 4. Sólidos Isolados STEP
cq.exporters.export(body_a, "/home/user/MatrizJonatha_Body_A.step")
cq.exporters.export(body_b, "/home/user/MatrizJonatha_Body_B.step")
cq.exporters.export(flow_cavity, "/home/user/MatrizJonatha_Canal_Fluxo.step")

print("Volume Body_A:", body_a.val().Volume(), "mm³")
print("Volume Body_B:", body_b.val().Volume(), "mm³")
print("Volume Canal de Fluxo:", flow_cavity.val().Volume(), "mm³")
print("-> MATRIZ JONATHA TRUE COAT-HANGER GERADA COM SUCESSO!")
