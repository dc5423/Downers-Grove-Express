"""Column-aware line extraction: split a slide at a clear vertical gutter first."""
import re
import unicodedata

LIG = {"ﬀ": "ff", "ﬁ": "fi", "ﬂ": "fl", "ﬃ": "ffi", "ﬄ": "ffl"}


def clean(s):
    for k, v in LIG.items():
        s = s.replace(k, v)
    s = unicodedata.normalize("NFC", s)
    return s.replace("​", "").replace("\xa0", " ").strip()


def rows(words, tol=3.2):
    """Group words into visual lines."""
    out = []
    for w in sorted(words, key=lambda w: (round(w["top"], 1), w["x0"])):
        if out and abs(w["top"] - out[-1][0]) <= tol:
            out[-1][1].append(w)
        else:
            out.append([w["top"], [w]])
    lines = []
    for top, ws in out:
        ws.sort(key=lambda w: w["x0"])
        lines.append((top, ws))
    return lines


def gutter(words, page_width):
    """Find an x where no word crosses, with real content on both sides."""
    if len(words) < 12:
        return None
    best = None
    lo, hi = page_width * 0.28, page_width * 0.72
    x = lo
    while x <= hi:
        crossing = sum(1 for w in words if w["x0"] < x - 1 and w["x1"] > x + 1)
        if crossing == 0:
            left = [w for w in words if w["x1"] <= x]
            right = [w for w in words if w["x0"] >= x]
            if len(left) >= 6 and len(right) >= 6:
                share = min(len(left), len(right)) / len(words)
                if share > 0.18:
                    span = min(w["top"] for w in right) if right else 0
                    score = share
                    if best is None or score > best[1]:
                        best = (x, score, span)
        x += 4
    return best[0] if best else None


def split_title(words):
    """Separate the slide's display type (titles, side labels) from body copy."""
    sizes = sorted(w.get("size", 10) for w in words)
    if not sizes:
        return [], words
    median = sizes[len(sizes) // 2]
    cut = max(median * 1.45, 13.5)
    big = [w for w in words if w.get("size", 10) >= cut]
    small = [w for w in words if w.get("size", 10) < cut]
    # if nearly everything is "big" the page has no separate title
    if len(small) < max(8, 0.25 * len(words)):
        return [], words
    return big, small


def text_lines(page, drop_title=True):
    """Lines of one PDF page in reading order, columns handled."""
    words = [w for w in page.extract_words(use_text_flow=False, keep_blank_chars=False,
                                           extra_attrs=["size"])
             if clean(w["text"])]
    if not words:
        return []
    if drop_title:
        _, words = split_title(words)
    if not words:
        return []

    # a heading band across the top stays whole; split only the body
    g = gutter(words, page.width)
    if g is None:
        groups = [words]
    else:
        left = [w for w in words if w["x1"] <= g]
        right = [w for w in words if w["x0"] >= g]
        groups = [left, right]

    out = []
    for grp in groups:
        if not grp:
            continue
        sub = gutter(grp, page.width) if len(groups) == 1 else None
        if sub is not None and len(groups) == 1:
            a = [w for w in grp if w["x1"] <= sub]
            b = [w for w in grp if w["x0"] >= sub]
            parts = [a, b]
        else:
            parts = [grp]
        for part in parts:
            rs = rows(part)
            if not rs:
                continue
            right = max(w["x1"] for _, ws in rs for w in ws)
            width = right - min(w["x0"] for _, ws in rs for w in ws)
            heights = sorted(max(w["bottom"] for w in ws) - min(w["top"] for w in ws)
                             for _, ws in rs)
            lh = heights[len(heights) // 2] or 10
            for i, (top, ws) in enumerate(rs):
                txt = re.sub(r"\s+", " ", clean(" ".join(w["text"] for w in ws)))
                if not txt:
                    continue
                short = max(w["x1"] for w in ws) < right - max(0.10 * width, 18)
                gap, starts_new = False, True
                if i + 1 < len(rs):
                    nxt_top, nxt_ws = rs[i + 1]
                    gap = (nxt_top - top) > lh * 1.75
                    nxt = clean(nxt_ws[0]["text"])[:1]
                    starts_new = bool(nxt) and (nxt.isupper() or nxt.isdigit() or nxt in "•✅✔❌💡⚠🔹▶")
                out.append(txt + ("¶" if (gap or (short and starts_new)) else ""))
    return out
