"""Extract diagram images per page, composite soft masks, compress for the web."""
import os
import re
import subprocess
import sys

from PIL import Image

PDF = sys.argv[1]
OUT = sys.argv[2]
os.makedirs(OUT, exist_ok=True)

listing = subprocess.run(["pdfimages", "-list", PDF], capture_output=True, text=True).stdout
want = {}
for line in listing.split("\n")[2:]:
    f = line.split()
    if len(f) < 6:
        continue
    try:
        page, kind, w, h = int(f[0]), f[2], int(f[3]), int(f[4])
    except ValueError:
        continue
    if kind != "image":
        continue
    if w * h < 30000 or w < 200:
        continue
    want.setdefault(page, 0)
    want[page] += 1

tmp = os.path.join(OUT, "_tmp")
os.makedirs(tmp, exist_ok=True)
manifest = {}

for page in sorted(want):
    for f in os.listdir(tmp):
        os.remove(os.path.join(tmp, f))
    subprocess.run(["pdfimages", "-png", "-f", str(page), "-l", str(page), PDF,
                    os.path.join(tmp, "p")], check=True)
    files = sorted(os.listdir(tmp))
    used = set()
    idx = 0
    for i, name in enumerate(files):
        if name in used:
            continue
        path = os.path.join(tmp, name)
        try:
            im = Image.open(path)
        except Exception:
            continue
        if im.width * im.height < 30000 or im.width < 200:
            continue
        # a following same-size greyscale file is this image's soft mask
        alpha = None
        if i + 1 < len(files):
            nxt = os.path.join(tmp, files[i + 1])
            try:
                cand = Image.open(nxt)
                if cand.size == im.size and cand.mode in ("L", "1", "P"):
                    alpha = cand.convert("L")
                    used.add(files[i + 1])
            except Exception:
                pass
        im = im.convert("RGB")
        # skip near-solid blocks: they are background shapes, not diagrams
        small = im.resize((48, 48))
        px = list(small.getdata())
        avg = tuple(sum(c[i] for c in px) / len(px) for i in range(3))
        spread = sum(abs(c[i] - avg[i]) for c in px for i in range(3)) / (len(px) * 3)
        if spread < 6:
            continue
        idx += 1
        out_name = f"p{page:03d}-{idx}"
        if alpha is not None:
            rgba = im.convert("RGBA")
            rgba.putalpha(alpha)
            bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
            im = Image.alpha_composite(bg, rgba).convert("RGB")
        if max(im.size) > 1100:
            ratio = 1100 / max(im.size)
            im = im.resize((int(im.width * ratio), int(im.height * ratio)), Image.LANCZOS)
        out_path = os.path.join(OUT, out_name + ".jpg")
        im.save(out_path, "JPEG", quality=78, optimize=True, progressive=True)
        manifest.setdefault(page, []).append(os.path.basename(out_path))

for f in os.listdir(tmp):
    os.remove(os.path.join(tmp, f))
os.rmdir(tmp)

import json
with open(os.path.join(OUT, "manifest.json"), "w") as fh:
    json.dump(manifest, fh, indent=1)

total = sum(len(v) for v in manifest.values())
size = sum(os.path.getsize(os.path.join(OUT, f)) for v in manifest.values() for f in v)
print("pages with diagrams:", len(manifest))
print("images:", total, "total size: %.1f MB" % (size / 1e6))
