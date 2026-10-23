"""Final extraction: display text, body lines (column-aware), bold runs, link anchors."""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pdfplumber  # noqa: E402
from pypdf import PdfReader  # noqa: E402
from lines import clean, split_title, text_lines, rows  # noqa: E402

PDF = sys.argv[1]
OUT = sys.argv[2]

reader = PdfReader(PDF)
pagemap = {p.indirect_reference.idnum: i + 1 for i, p in enumerate(reader.pages)}


def link_rects(page):
    out = []
    for annot in page.get("/Annots") or []:
        obj = annot.get_object()
        if obj.get("/Subtype") != "/Link":
            continue
        rect = [float(v) for v in obj.get("/Rect", [0, 0, 0, 0])]
        action, dest, target = obj.get("/A"), obj.get("/Dest"), None
        if action is not None:
            action = action.get_object()
            if action.get("/S") == "/URI":
                target = {"kind": "uri", "uri": str(action.get("/URI"))}
            elif action.get("/S") == "/GoTo":
                dest = action.get("/D")
        if target is None and dest is not None:
            try:
                d = dest[0] if isinstance(dest, list) else dest
                target = {"kind": "page", "page": pagemap.get(d.idnum)}
            except Exception:
                target = None
        if target:
            out.append({
                "rect": [min(rect[0], rect[2]), min(rect[1], rect[3]),
                         max(rect[0], rect[2]), max(rect[1], rect[3])],
                "target": target,
            })
    return out


pages = []
with pdfplumber.open(PDF) as pdf:
    for i, plumb in enumerate(pdf.pages):
        num = i + 1
        words = [w for w in plumb.extract_words(extra_attrs=["size"]) if clean(w["text"])]
        big, _ = split_title(words)
        title_lines = [clean(" ".join(w["text"] for w in ws)) for _, ws in rows(big)] if big else []
        body = text_lines(plumb)

        bolds, cur, last = [], "", None
        for ch in plumb.chars:
            if "bold" in (ch.get("fontname") or "").lower():
                if last is not None and ch["x0"] - last > 12:
                    if len(cur.strip()) > 2:
                        bolds.append(clean(cur))
                    cur = ""
                cur += ch["text"]
                last = ch["x1"]
            else:
                if len(cur.strip()) > 2:
                    bolds.append(clean(cur))
                cur, last = "", None
        if len(cur.strip()) > 2:
            bolds.append(clean(cur))
        bolds = sorted({re.sub(r"\s+", " ", b).strip(" :–-") for b in bolds if len(b.strip()) > 2},
                       key=len, reverse=True)

        links = []
        for lk in link_rects(reader.pages[i]):
            x0, y0, x1, y1 = lk["rect"]
            top, bottom = plumb.height - y1, plumb.height - y0
            hit = [w for w in words if w["x0"] >= x0 - 2 and w["x1"] <= x1 + 2
                   and w["top"] >= top - 3 and w["bottom"] <= bottom + 3]
            text = re.sub(r"\s+", " ", clean(" ".join(w["text"] for w in hit))).strip(" .,")
            if text:
                links.append({"text": text, "target": lk["target"]})

        pages.append({"page": num, "title_lines": title_lines, "lines": body,
                      "bold": bolds, "links": links})
        if num % 50 == 0:
            print("parsed", num, flush=True)

os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "content.json"), "w", encoding="utf-8") as fh:
    json.dump({"pages": pages}, fh, ensure_ascii=False, indent=1)
print("pages:", len(pages), "anchors:", sum(len(p["links"]) for p in pages))
