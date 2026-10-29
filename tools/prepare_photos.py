#!/usr/bin/env python3
"""Prepara fotos de las visitas a los territorios para publicarlas.

Qué hace con cada imagen de fotos_originales/:
  1. Corrige la orientación (EXIF) y BORRA todos los metadatos, incluida la ubicación GPS.
  2. Reduce el lado largo a 2000 px y guarda JPG optimizado en assets/fotos/<territorio>/.
  3. Añade la foto a assets/fotos/fotos.json con "consent": false (tú lo cambias a true).

Uso:
    python tools/prepare_photos.py cali
    python tools/prepare_photos.py portada --max 2400
Requiere Pillow:  pip install pillow
"""
import argparse, json, re, sys
from pathlib import Path

try:
    from PIL import Image, ImageOps
except ImportError:
    sys.exit("Falta Pillow. Instálalo con:  pip install pillow")

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "fotos_originales"
DEST = ROOT / "assets" / "fotos"
EXT = {".jpg", ".jpeg", ".png", ".webp", ".heic"}
TERRITORIOS = {"portada", "cali", "tumaco", "buenaventura", "francisco-pizarro", "otros"}


def slug(name):
    s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return s or "foto"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("territorio", choices=sorted(TERRITORIOS))
    ap.add_argument("--max", type=int, default=2000, help="lado largo máximo en px (2000)")
    ap.add_argument("--quality", type=int, default=82)
    a = ap.parse_args()

    out_dir = DEST / a.territorio
    out_dir.mkdir(parents=True, exist_ok=True)
    meta_path = DEST / "fotos.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}

    files = [p for p in sorted(SRC.glob("*")) if p.suffix.lower() in EXT]
    if not files:
        sys.exit(f"No hay imágenes en {SRC}. Copia allí tus fotos originales.")
    for i, p in enumerate(files, 1):
        try:
            im = Image.open(p)
        except Exception as ex:
            print(f"  omitida {p.name}: {ex} (los .heic requieren pillow-heif)"); continue
        im = ImageOps.exif_transpose(im).convert("RGB")
        im.thumbnail((a.max, a.max))
        clean = Image.new("RGB", im.size); clean.paste(im)          # sin metadatos
        name = f"{slug(p.stem)}.jpg"
        clean.save(out_dir / name, "JPEG", quality=a.quality, optimize=True, progressive=True)
        key = f"{a.territorio}/{name}"
        meta.setdefault(key, {"alt": "[Describe qué se ve]", "caption": "", "credit": "Foto: Mackmot Pachotto Ambrose",
                              "consent": False})
        size = (out_dir / name).stat().st_size / 1024
        print(f"  ok {key}  {im.size[0]}x{im.size[1]}  {size:.0f} KB")
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\nAhora abre assets/fotos/fotos.json: escribe alt/caption y pon \"consent\": true solo si tienes permiso.")
    print("Luego:  python build.py")


if __name__ == "__main__":
    main()
