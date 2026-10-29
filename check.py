#!/usr/bin/env python3
"""Lista de verificación previa a la entrega (solo biblioteca estándar).

    python check.py            # palabras, marcadores, imágenes, enlaces
    python check.py --offline  # omite la prueba de enlaces

Esta herramienta NO verifica el contenido de las fuentes: abre cada enlace y confirma
tú mismo las cifras y citas.
"""
import argparse, json, re, sys, urllib.request, urllib.error
from pathlib import Path
from build import ROOT, pending, word_count, load_photos, FOTOS, EXT

def links(data):
    return sorted(set(re.findall(r"https?://[^\s\"<>)\]]+", json.dumps(data, ensure_ascii=False))))

def images(data):
    return sorted(set(re.findall(r"assets/img/[\w.\-]+", json.dumps(data))))

def probe(url, timeout=12):
    req = urllib.request.Request(url, method="GET", headers={"User-Agent": "Mozilla/5.0 (link-check)"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status
    except urllib.error.HTTPError as ex:
        return ex.code
    except Exception as ex:
        return type(ex).__name__

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--offline", action="store_true")
    a = ap.parse_args()
    data = json.loads((ROOT / "content.json").read_text(encoding="utf-8"))
    ok = True

    scene = next(s for s in data["scenes"] if s["type"] == "analysis")
    n = word_count(scene)
    good = scene["min_words"] <= n <= scene["max_words"]
    print(f"[{'OK' if good else 'X '}] Análisis: {n} palabras (debe estar entre {scene['min_words']} y {scene['max_words']})")
    ok &= good

    todo = pending(data)
    print(f"[{'OK' if not todo else 'X '}] Marcadores pendientes: {len(todo)}")
    for t in todo[:15]: print("      ", t[:90])
    ok &= not todo

    miss = [p for p in images(data) if not (ROOT / p).exists()]
    print(f"[{'OK' if not miss else '! '}] Imágenes faltantes: {len(miss)}")
    for p in miss: print("      ", p)

    photos, held = load_photos()
    total = sum(len(v) for v in photos.values())
    print(f"[{'OK' if total else '! '}] Fotos publicadas: {total}" + ("" if total else "  (agrega fotos en assets/fotos/)"))
    if not photos.get('portada'):
        print('[X ] Falta la foto de portada del territorio (assets/fotos/portada/ + consent:true en fotos.json)')
        ok = False
    for k, why in held: print(f"      no publicada: {k}: {why}")
    big = [f for f in FOTOS.rglob("*") if f.suffix.lower() in EXT and f.stat().st_size > 1_800_000]
    if big:
        print(f"[! ] {len(big)} foto(s) pesan más de 1,8 MB: usa tools/prepare_photos.py")
    try:
        from PIL import Image
        gps = []
        for f in FOTOS.rglob("*"):
            if f.suffix.lower() in EXT:
                ex = Image.open(f).getexif()
                if ex.get_ifd(0x8825): gps.append(f)
        print(f"[{'OK' if not gps else 'X '}] Fotos con ubicación GPS oculta: {len(gps)}")
        for f in gps: print("      ", f.relative_to(ROOT))
        ok &= not gps
    except ImportError:
        print("[! ] Instala Pillow (pip install pillow) para comprobar que las fotos no tengan GPS.")

    ai = next(s for s in data["scenes"] if s["type"] == "sources").get("ai_note", "")
    if ai.strip() and ("(herramienta)" in ai or ai.strip().startswith("[")):
        print("[X ] La nota de uso de IA sigue sin completar: debe describir exactamente lo que hiciste.")
        ok = False

    if not a.offline:
        print("Enlaces:")
        for u in links(data):
            st = probe(u)
            flag = "OK" if st == 200 else "! "
            print(f"  [{flag}] {st}  {u[:100]}")
        print("  (403/999 en periódicos o Netflix puede ser un bloqueo a scripts: ábrelos a mano.)")

    print("\nListo para entregar." if ok else "\nAún no está listo para entregar.")
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
