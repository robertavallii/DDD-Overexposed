"""
generate_thumbnails.py — Pre-genera thumbnail per il viewer 3D

COME USARE:
1. Esegui DOPO generate_data.py
2. python3 generate_thumbnails.py
3. Crea cartella thumbnails/ con versioni ridotte (150px) di tutte le foto
4. In index.html, imposta IMG_BASE = '' (le foto vengono cercate in thumbnails/)

Lo script aggiorna anche data.json per puntare ai thumbnail.
"""

import json
from pathlib import Path
from PIL import Image

THUMB_SIZE = 150          # px, lato del quadrato
THUMB_QUALITY = 70        # qualità JPEG (0-100)
THUMB_DIR = Path("thumbnails")
DATA_FILE = Path("data.json")

def make_thumbnail(src_path, dst_path):
    """Crea un thumbnail quadrato crop-center."""
    try:
        with Image.open(src_path) as img:
            # Converti a RGB se necessario
            if img.mode in ('RGBA', 'P', 'LA'):
                img = img.convert('RGB')
            
            # Crop quadrato al centro
            w, h = img.size
            side = min(w, h)
            left = (w - side) // 2
            top = (h - side) // 2
            img = img.crop((left, top, left + side, top + side))
            
            # Ridimensiona
            img = img.resize((THUMB_SIZE, THUMB_SIZE), Image.LANCZOS)
            
            # Salva
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            img.save(dst_path, 'JPEG', quality=THUMB_QUALITY, optimize=True)
            return True
    except Exception as e:
        print(f"  ⚠️  Errore {src_path}: {e}")
        return False

def main():
    if not DATA_FILE.exists():
        print("❌ data.json non trovato. Esegui prima generate_data.py")
        return

    with open(DATA_FILE) as f:
        data = json.load(f)

    total = 0
    created = 0
    skipped = 0

    for loc in data["locations"]:
        print(f"\n📍 {loc['name']}")
        for cl in loc["clusters"]:
            # Thumbnail per la cover
            cover_src = Path(cl["cover"])
            cover_dst = THUMB_DIR / cover_src
            if not cover_dst.exists():
                if make_thumbnail(cover_src, cover_dst):
                    created += 1
                else:
                    skipped += 1
            total += 1
            # Aggiorna path cover nel JSON
            cl["cover_thumb"] = str(THUMB_DIR / cover_src)

            # Thumbnail per ogni foto
            for photo in cl["photos"]:
                src = Path(photo["path"])
                dst = THUMB_DIR / src
                total += 1
                if dst.exists():
                    continue
                if make_thumbnail(src, dst):
                    created += 1
                else:
                    skipped += 1
                # Aggiungi path thumbnail
                photo["thumb"] = str(THUMB_DIR / src)

        print(f"  ✅ {loc['name']}: processato")

    # Salva data.json aggiornato
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"\n{'='*50}")
    print(f"Totale: {total} immagini")
    print(f"Creati: {created} thumbnail")
    print(f"Saltati: {skipped} (errori)")
    print(f"Salvati in: {THUMB_DIR}/")
    print(f"data.json aggiornato con percorsi thumbnail")

if __name__ == "__main__":
    main()
