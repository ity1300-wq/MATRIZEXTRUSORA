import json

# Update SSOT JSON
with open("cad_die_parameters.json", "r", encoding="utf-8") as f:
    data = json.load(f)

data["project_metadata"]["version"] = "v26.0_MatrizJonatha_Official_Master"
data["project_metadata"]["status"] = "APPROVED_MASTER_DESIGN"
data["project_metadata"]["selected_die"] = "MatrizJonatha.step"

if "jonatha_alternative_parameters" in data:
    del data["jonatha_alternative_parameters"]

if "jonatha_alternative_files" in data:
    del data["jonatha_alternative_files"]

data["matriz_jonatha_parameters"] = {
    "manifold_type": "Coat-Hanger (Cabide 3D Hidrodinâmico com Asas Diagonais)",
    "entry_bore_diameter_mm": 75.60,
    "manifold_central_depth_mm": 6.00,
    "pre_land_transition_depth_mm": 3.50,
    "land_length_mm": 10.00,
    "land_width_mm": 75.00,
    "land_thickness_mm": 1.50,
    "edge_radius_mm": 0.75,
    "exit_chamfer": "1.50 mm x 45°",
    "pressure_drop_bar": 68.2,
    "velocity_uniformity_percent": 99.1,
    "material": "Aço Ferramenta P20 / AISI H13 Nitretado"
}

with open("cad_die_parameters.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("cad_die_parameters.json atualizado para v26.0 MatrizJonatha Unificada!")
