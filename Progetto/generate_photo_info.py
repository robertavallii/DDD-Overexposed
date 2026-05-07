"""
generate_photo_info.py — Converte i file Excel in photo_info.json

COME USARE:
1. Metti i file .xlsx in info/<location>/ (es. info/montebre/data.xlsx)
   Oppure direttamente in info/ (es. info/montebre.xlsx)
2. Esegui: python3 generate_photo_info.py
3. Genera photo_info.json nella cartella corrente

Il frontend lo carica e usa photo_id per collegare ogni foto ai suoi metadati.
"""

import json
import pandas as pd
from pathlib import Path

INFO_DIR = Path("info")
OUTPUT_FILE = Path("photo_info.json")

# Colonne da esportare nel JSON (le più utili per il pannello)
EXPORT_COLUMNS = [
    "photo_id",
    "username",
    "caption",
    "taken_at",
    "like_count",
    "comment_count",
    "view_count",
    "location_name",
    "location_lat",
    "location_lng",
    "post_url",
    "image_url",
    "carousel_index",
    "carousel_total",
    "is_verified",
    "product_type",
]

def main():
    if not INFO_DIR.exists():
        print(f"❌ Cartella {INFO_DIR}/ non trovata.")
        print(f"   Crea la cartella e mettici i file .xlsx")
        return

    # Trova tutti gli xlsx
    xlsx_files = list(INFO_DIR.rglob("*.xlsx"))
    if not xlsx_files:
        print(f"❌ Nessun file .xlsx trovato in {INFO_DIR}/")
        return

    all_photos = {}
    total = 0

    for xlsx_path in sorted(xlsx_files):
        print(f"📄 {xlsx_path}")
        try:
            df = pd.read_excel(xlsx_path, dtype={"photo_id": str})
        except Exception as e:
            print(f"  ⚠️  Errore lettura: {e}")
            continue

        if "photo_id" not in df.columns:
            print(f"  ⚠️  Colonna 'photo_id' mancante, salto")
            continue

        # Filtra colonne disponibili
        available = [c for c in EXPORT_COLUMNS if c in df.columns]
        df_export = df[available].copy()

        # Pulisci
        df_export = df_export.fillna("")
        df_export["photo_id"] = df_export["photo_id"].astype(str).str.strip()

        for _, row in df_export.iterrows():
            pid = row["photo_id"]
            if not pid:
                continue
            record = {}
            for col in available:
                val = row[col]
                if isinstance(val, (pd.Timestamp,)):
                    val = val.isoformat()
                elif isinstance(val, float) and val == int(val):
                    val = int(val)
                record[col] = val
            all_photos[pid] = record
            total += 1

        print(f"  ✅ {len(df_export)} foto")

    # Salva
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_photos, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*50}")
    print(f"photo_info.json generato: {total} foto da {len(xlsx_files)} file")

if __name__ == "__main__":
    main()
