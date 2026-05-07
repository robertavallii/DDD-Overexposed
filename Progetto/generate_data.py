"""
generate_data.py — Genera data.json per il viewer 3D

COME USARE:
1. Aggiungi le tue location nel dizionario LOCATIONS qui sotto
2. Assicurati di avere per ogni location:
   - output/<nome>/hotspots.json
   - output/<nome>/cluster_photos.json
3. Esegui: python3 generate_data.py
4. Verrà generato data.json nella cartella corrente

Per aggiungere una nuova location basta copiare il blocco
e cambiare nome, coordinate e cluster.
"""

import json
import numpy as np
from pathlib import Path

# ============================================================
# CONFIGURAZIONE — MODIFICA QUI PER AGGIUNGERE LOCATION
# ============================================================

LOCATIONS = {
    "parcociani": {
        "name": "Parco Ciani",
        "lat": 46.004846,
        "lng": 8.958590,
        "clusters": {
            14: {"lat": 46.004134, "lng": 8.956928, "model": "models/gate.glb"},
            9:  {"lat": 46.003871, "lng": 8.959087, "model": "models/sfera.glb"},
            16: {"lat": 46.004242, "lng": 8.958053, "model": "models/monte_bre.glb"},
            8:  {"lat": 46.004610, "lng": 8.956560, "model": "models/villa_ciani.glb"},        }
    },
    "montebre": {
        "name": "Monte Brè",
        "lat": 46.010229,
        "lng": 8.985617,
        "clusters": {
            23: {"lat": 46.008211, "lng": 8.984329},
            11: {"lat": 46.008217, "lng": 8.982977},
            10: {"lat": 46.008815, "lng": 8.984893},
            9:  {"lat": 46.011476, "lng": 8.996901},
            0:  {"lat": 46.007327, "lng": 8.973154},
        }
    },
        # --- AGGIUNGI NUOVE LOCATION QUI ---
     "cattedralesanlorenzo": {
         "name": "Cattedrale San Lorenzo",
         "lat": 46.00466752255938,
         "lng": 8.94891186982558,
         "clusters": {
            8: {"lat": 46.004894040707875, "lng": 8.948203457086864},
            10: {"lat": 46.00466282476093, "lng": 8.948915248632568},
            11: {"lat": 46.00466282476093, "lng": 8.948915248632568},
            7: {"lat": 46.00466282476093, "lng": 8.948915248632568},
            3: {"lat": 46.00466282476093, "lng": 8.948915248632568},
         12: {"lat": 46.004894040707875, "lng": 8.948203457086864},
            1: {"lat": 46.00466282476093, "lng": 8.948915248632568},
            9: {"lat": 46.00466282476093, "lng": 8.948915248632568},
            2: {"lat": 46.00466282476093, "lng": 8.948915248632568},
            6: {"lat": 46.00466282476093, "lng": 8.948915248632568},
            0: {"lat": 46.00466282476093, "lng": 8.948915248632568},
         }
     },

     "montesansalvatore": {
         "name": "Monte San Salvatore",
        "lat": 45.9770378, 
        "lng": 8.9475965910,
         "clusters": {
            10: { "lat": 45.97695764, "lng": 8.94729867 },
            7:  { "lat": 45.9769247,  "lng": 8.9472481 },
            3:  { "lat": 45.99053207, "lng": 8.94540646 },
            2:  { "lat": 45.98229791, "lng": 8.94100529 },
            8:  { "lat": 45.97900052, "lng": 8.94712408 },
            11: { "lat": 45.976970,   "lng": 8.947210 },
            1:  { "lat": 45.98234329, "lng": 8.94114903 },
            4:  { "lat": 45.976944,   "lng": 8.946944 },
            9:  { "lat": 45.9768656,  "lng": 8.94670772 },
            6:  { "lat": 45.97715777, "lng": 8.94736864 },
         }
     },

"morcote": {

  "name": "Morcote",

  "lat": 45.92755442213635,

  "lng": 8.907973901193312,

  "clusters": {

    21: { "lat": 45.923046520363656, "lng": 8.91419836826197 },

    18: { "lat": 45.92262132453823, "lng": 8.916195036439525 },

    12: { "lat": 45.92377583915566, "lng": 8.914465136545406 },

    16: { "lat": 45.927130291003515, "lng": 8.916108730826634 },

    9: { "lat": 45.92371331871414, "lng": 8.910495356677908 },

    17: { "lat": 45.923338813505936, "lng": 8.918010412274036 },

    8: { "lat": 45.922899247058396, "lng": 8.914093309119833 },

    13: { "lat": 45.92275547, "lng": 8.91646369 },

    4: { "lat": 45.92384885, "lng": 8.91060383 },

    19: { "lat": 45.922876, "lng": 8.917128 },

    1: { "lat": 45.92322187, "lng": 8.91408558 },

    15: { "lat": 45.92322187, "lng": 8.91408558 },

    14: { "lat": 45.97695764, "lng": 8.94729867 }
  },
}}

OUTPUT_DIR = Path("output")
SPREAD_M = 15  # raggio dispersione foto attorno al centroide (metri)

# ============================================================
# GENERAZIONE — NON MODIFICARE SOTTO
# ============================================================

M_TO_DEG_LAT = 1 / 111000
M_TO_DEG_LNG = 1 / (111000 * np.cos(np.radians(46.0)))

np.random.seed(42)

data = {
    "locations": []
}

for loc_key, loc_config in LOCATIONS.items():
    hotspots_path = OUTPUT_DIR / loc_key / "hotspots.json"
    cluster_photos_path = OUTPUT_DIR / loc_key / "cluster_photos.json"

    if not hotspots_path.exists():
        print(f"⚠️  {hotspots_path} non trovato, salto {loc_key}")
        continue
    if not cluster_photos_path.exists():
        print(f"⚠️  {cluster_photos_path} non trovato, salto {loc_key}")
        continue

    with open(hotspots_path) as f:
        hotspots = json.load(f)
    with open(cluster_photos_path) as f:
        all_photos = json.load(f)

    # Indicizza hotspots per cluster_id
    hotspot_map = {h["cluster_id"]: h for h in hotspots}

    location_entry = {
        "key": loc_key,
        "name": loc_config["name"],
        "lat": loc_config["lat"],
        "lng": loc_config["lng"],
        "total_photos": 0,
        "clusters": []
    }

    for cid, coords in loc_config["clusters"].items():
        if cid not in hotspot_map:
            print(f"  ⚠️  {loc_key} cluster {cid} non trovato in hotspots.json, salto")
            continue

        h = hotspot_map[cid]
        cid_str = str(cid)
        photos_list = all_photos.get(cid_str, [])

        if not photos_list:
            print(f"  ⚠️  {loc_key} cluster {cid} non ha foto in cluster_photos.json, salto")
            continue

        # Genera coordinate disperse per ogni foto
        photos_with_coords = []
        for photo_path in photos_list:
            offset_lat = np.random.normal(0, SPREAD_M / 2) * M_TO_DEG_LAT
            offset_lng = np.random.normal(0, SPREAD_M / 2) * M_TO_DEG_LNG
            photos_with_coords.append({
                "path": photo_path,
                "lat": coords["lat"] + offset_lat,
                "lng": coords["lng"] + offset_lng,
            })

        cluster_entry = {
            "cluster_id": cid,
            "label": h["label"],
            "description": h["description"],
            "cover": h["representative_photos"][0] if h["representative_photos"] else photos_list[0],
            "lat": coords["lat"],
            "lng": coords["lng"],
            "size": len(photos_list),
            "photos": photos_with_coords,
        }

        # Aggiungi modello 3D se specificato
        if "model" in coords:
            cluster_entry["model"] = coords["model"]

        location_entry["clusters"].append(cluster_entry)
        location_entry["total_photos"] += len(photos_list)

    if location_entry["clusters"]:
        data["locations"].append(location_entry)
        print(f"✅ {loc_config['name']}: {len(location_entry['clusters'])} cluster, {location_entry['total_photos']} foto")

# Salva
with open("data.json", "w") as f:
    json.dump(data, f, indent=2)

print(f"\n{'='*50}")
print(f"data.json generato: {len(data['locations'])} location")
print(f"Totale foto: {sum(l['total_photos'] for l in data['locations'])}")