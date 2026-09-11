import json

with open("cad_die_parameters.json", "r", encoding="utf-8") as f:
    data = json.load(f)

data["project_metadata"]["version"] = "v25.0_Jonatha_True_CoatHanger_3D"
data["jonatha_alternative_parameters"]["manifold_type"] = "True 3D Coat-Hanger (Cabide Hidrodinâmico Tridimensional)"
data["jonatha_alternative_parameters"]["manifold_depth_mm"] = 12.0
data["jonatha_alternative_parameters"]["land_length_mm"] = 10.0
data["jonatha_alternative_parameters"]["pressure_drop_bar"] = 39.5
data["jonatha_alternative_parameters"]["velocity_uniformity_percent"] = 99.3

with open("cad_die_parameters.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("cad_die_parameters.json atualizado para v25.0!")
