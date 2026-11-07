#!/usr/bin/env python3
"""Imatges noves de la web (les fetes amb IA amb Flow, a partir dels prompts del xat).

Ús:
  python3 tools/posa-imatges.py --dades
      Fa que cada lloc de data/ apunti al nom nou de la seva imatge (segons tools/imatges-noves.json).
      Canvia només el valor de "image", sense tocar el format dels fitxers.
  python3 tools/posa-imatges.py FITXER [FITXER...]
      Prepara les imatges que arriben del Drive: les reconeix pel número del davant (01-…, 23-…),
      les passa a JPG, les retalla pel centre a la forma del lloc si cal (Flow només fa 16:9 i 9:16),
      les redueix i les desa a src/img/fotos/<nom>.jpg.

Després: python3 build.py
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
FOTOS = ROOT / "src" / "img" / "fotos"
MAP = json.loads((ROOT / "tools" / "imatges-noves.json").read_text(encoding="utf-8"))
MAP.pop("_", None)
BY_NUM = {k.split("-", 1)[0]: k for k in MAP}

IMAGE_RE = re.compile(r'"image"\s*:\s*"((?:[^"\\]|\\.)*)"')


def image_paths(obj, path=()):
    """Tots els camins de les claus "image", en l'ordre en què surten al fitxer."""
    out = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "image" and isinstance(v, str):
                out.append(path + (k,))
            out += image_paths(v, path + (k,))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out += image_paths(v, path + (i,))
    return out


def set_data():
    wanted = {}   # fitxer → {camí: valor nou}
    for name, places in MAP.items():
        for place in places:
            wanted.setdefault(place[0], {})[tuple(place[1:])] = name + ".jpg"
    changed = 0
    for rel, targets in wanted.items():
        f = DATA / rel
        text = f.read_text(encoding="utf-8")
        order = image_paths(json.loads(text))
        matches = list(IMAGE_RE.finditer(text))
        if len(order) != len(matches):
            sys.exit(f"{rel}: no puc fer correspondre les claus \"image\" ({len(order)} al JSON, {len(matches)} al text)")
        missing = set(targets) - set(order)
        if missing:
            sys.exit(f"{rel}: aquests llocs no existeixen: {sorted(missing)}")
        for i in reversed(range(len(matches))):
            new = targets.get(order[i])
            m = matches[i]
            if new and m.group(1) != new:
                text = text[:m.start(1)] + new + text[m.end(1):]
                changed += 1
        json.loads(text)
        f.write_text(text, encoding="utf-8")
    print(f"Fet: {changed} llocs de data/ apunten a les imatges noves.")


def width_for(name):
    return 1600


def ratio_for(name):
    return 4 / 3             # totes van al costat d'un text, amb forma orgànica


def crop_to(im, r):
    """Retalla pel centre si la imatge no té la forma del lloc (p. ex. Flow només fa 16:9 i 9:16)."""
    if abs(im.width / im.height - r) / r <= 0.02:
        return im
    if im.width / im.height > r:
        w = round(im.height * r)
        x = (im.width - w) // 2
        return im.crop((x, 0, x + w, im.height))
    h = round(im.width / r)
    y = (im.height - h) // 2
    return im.crop((0, y, im.width, y + h))


def add_files(files):
    from PIL import Image, ImageOps
    FOTOS.mkdir(parents=True, exist_ok=True)
    for src in files:
        src = Path(src)
        m = re.match(r"(\d{2})\D", src.name)
        if not m or m.group(1) not in BY_NUM:
            print(f"  ? {src.name}: no sé quina imatge és (ha de començar pel número, 01–04)")
            continue
        name = BY_NUM[m.group(1)]
        im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
        orig = im.size
        im = crop_to(im, ratio_for(name))
        if im.size != orig:
            print(f"  {src.name}: retallada de {orig[0]}×{orig[1]} a {im.width}×{im.height} (forma del lloc)")
        w = width_for(name)
        if im.width > w:
            im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
        out = FOTOS / (name + ".jpg")
        im.save(out, "JPEG", quality=82, optimize=True, progressive=True)
        print(f"  {src.name} → src/img/fotos/{out.name} ({im.width}×{im.height}, {out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    args = sys.argv[1:]
    if args == ["--dades"]:
        set_data()
    elif args:
        add_files(args)
    else:
        print(__doc__)
