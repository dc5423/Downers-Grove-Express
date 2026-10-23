"""Build the DGS Express Knowledgebase page from the extracted PDF content."""
import html
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from outline import PARTS, SKIP_PAGES, ALIASES, VIDEOS  # noqa: E402

KB = sys.argv[1]
SITE = sys.argv[2]

content = json.load(open(os.path.join(KB, "content.json"), encoding="utf-8"))
PAGES = {p["page"]: p for p in content["pages"]}
manifest = json.load(open(os.path.join(SITE, "img", "manifest.json"), encoding="utf-8"))
IMAGES = {int(k): v for k, v in manifest.items()}

LABELS = ("Definition:", "Synonyms:", "See Also:", "Pairs well with:", "Also known as:")
QUADS = {"strengths": "Strengths", "weaknesses": "Weaknesses",
         "opportunities": "Opportunities", "threats": "Threats"}
CHROME = {"defense learning", "offense learning", "module", "swot", "analysis",
          "swot analysis", "learning module", "defense learning module"}
MARKERS = "✅✔❌💡⚠️⚠🔹▶•"


def nb(s):
    return s.replace("\u00b6", "")


def norm(s):
    s = nb(s)
    s = re.sub(r"[’']", "'", s.lower())
    s = re.sub(r"[^a-z0-9 /()+-]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


# ---------- slug lookup for cross-references ----------
SLUG_BY_NAME = {}
for part_slug, part_title, topics in PARTS:
    for slug, title, pages in topics:
        SLUG_BY_NAME[norm(title)] = slug
for k, v in ALIASES.items():
    SLUG_BY_NAME.setdefault(norm(k), v)

ALL_SLUGS = {slug for _, _, topics in PARTS for slug, _, _ in topics}
SLUG_BY_NAME = {k: v for k, v in SLUG_BY_NAME.items() if v in ALL_SLUGS}


def lookup(term):
    t = norm(term)
    if t in SLUG_BY_NAME:
        return SLUG_BY_NAME[t]
    t2 = re.sub(r"\s*\(.*?\)\s*", " ", t).strip()
    return SLUG_BY_NAME.get(t2)


# ---------- inline formatting ----------
def esc(s):
    return html.escape(s, quote=False)


URL_RE = re.compile(r"(https?://[^\s<>\"]+)")


def linkify(frag):
    return URL_RE.sub(
        lambda m: f'<a href="{m.group(1)}" target="_blank" rel="noopener">{m.group(1)}</a>',
        frag)


def apply_bold(text, bolds):
    """Wrap the page's bold runs in <strong>, longest first, without nesting."""
    if not bolds:
        return linkify(esc(text))
    spans = []
    for b in bolds:
        if len(b) < 3:
            continue
        start = 0
        low_t, low_b = text.lower(), b.lower()
        while True:
            i = low_t.find(low_b, start)
            if i < 0:
                break
            j = i + len(b)
            if not any(i < e and j > s for s, e in spans):
                spans.append((i, j))
            start = i + 1
    if not spans:
        return linkify(esc(text))
    spans.sort()
    out, pos = [], 0
    for s, e in spans:
        if s < pos:
            continue
        out.append(esc(text[pos:s]))
        out.append("<strong>" + esc(text[s:e]) + "</strong>")
        pos = e
    out.append(esc(text[pos:]))
    return linkify("".join(out))


def link_terms(frag_html, terms_text):
    """Turn a comma-separated list of terms into links where a topic exists."""
    parts = re.split(r",| and ", terms_text)
    out = []
    for raw in parts:
        term = raw.strip().strip(".")
        if not term:
            continue
        slug = lookup(term)
        out.append(f'<a href="#{slug}">{esc(term)}</a>' if slug else esc(term))
    return ", ".join(out)


# ---------- page parsing ----------
def strip_chrome(lines, title):
    title_words = set(norm(title).split())
    out = list(lines)
    # trailing chrome
    while out and norm(out[-1]) in CHROME:
        out.pop()
    # leading title fragments
    while out:
        first = out[0]
        n = norm(first)
        if n in CHROME:
            out.pop(0)
            continue
        words = n.split()
        is_fragment = (
            len(words) <= 6
            and not first.endswith(".")
            and not first.startswith(tuple(MARKERS))
            and not first.startswith(LABELS)
            and (
                n in CHROME
                or (words and all(w in title_words or w in {"swot", "analysis", "key", "concepts",
                                                            "when", "to", "use", "final", "thoughts",
                                                            "coverage", "the", "of", "and", "a", "vs"}
                                  for w in words))
            )
        )
        if is_fragment:
            out.pop(0)
        else:
            break
    return out


def items_from(lines):
    """Collapse wrapped lines into bullet items and paragraphs."""
    items, cur = [], None

    def flush():
        nonlocal cur
        if cur is not None and cur.strip(" .•"):
            items.append(cur.strip())
        cur = None

    for raw in lines:
        brk = raw.endswith("\u00b6")
        ln = raw[:-1] if brk else raw
        if ln in ("•", "-", "–"):
            flush()
            cur = ""
            continue
        m = re.match(r"^[••]\s+(.*)$", ln)
        if m:
            flush()
            cur = m.group(1)
            if brk:
                flush()
            continue
        if ln[:1] in MARKERS and ln[:1] != "•":
            flush()
            cur = ln
            if brk:
                flush()
            continue
        if cur is None or cur == "":
            cur = ln
            if brk:
                flush()
            continue
        if cur.endswith(("-",)):
            cur = cur[:-1] + ln
        elif cur.endswith((".", "!", "?", ":")) and not cur.endswith(("e.g.", "i.e.", "etc.")):
            flush()
            cur = ln
        else:
            cur = cur + " " + ln
        if brk:
            flush()
    flush()
    return [re.sub(r"\s+", " ", i).strip() for i in items if i and i.strip(" .")]


def parse_quadrants(lines):
    """A single SWOT slide holds all four quadrants as labelled runs."""
    idx = [(i, QUADS[norm(l)]) for i, l in enumerate(lines) if norm(l) in QUADS]
    if len(idx) < 3:
        return None
    out = {}
    for n, (i, label) in enumerate(idx):
        end = idx[n + 1][0] if n + 1 < len(idx) else len(lines)
        body = lines[i + 1:end]
        if body:
            out[label] = body
    return out or None


def render_items(items, bolds):
    out, open_list = [], False

    def close():
        nonlocal open_list
        if open_list:
            out.append("</ul>")
            open_list = False

    items = list(items)
    i = -1
    while True:
        i += 1
        if i >= len(items):
            break
        it = items[i]
        label = next((l for l in LABELS if it.startswith(l)), None)
        if label:
            close()
            rest = it[len(label):].strip()
            if label in ("See Also:", "Pairs well with:"):
                if not rest:
                    terms = []
                    while i + 1 < len(items):
                        nxt = items[i + 1]
                        if len(nxt) > 60 or nxt.endswith(":") or nxt.startswith(LABELS):
                            break
                        terms.append(nxt.strip(" ."))
                        i += 1
                    rest = ", ".join(terms)
                body = link_terms(None, rest)
            else:
                body = apply_bold(rest, bolds)
            out.append(f'<p class="lbl"><span>{esc(label.rstrip(":"))}</span> {body}</p>')
            continue
        if it.endswith(":") and len(it) <= 70:
            close()
            out.append(f"<h4>{apply_bold(it.rstrip(':'), bolds)}</h4>")
            continue
        if not open_list:
            out.append("<ul>")
            open_list = True
        marker = ""
        body = it
        if body[:1] in MARKERS:
            marker = body[0]
            body = body[1:].lstrip()
            if body[:1] == "️":
                body = body[1:].lstrip()
        cls = ""
        if marker in "✅✔":
            cls = ' class="yes"'
        elif marker == "❌":
            cls = ' class="no"'
        elif marker == "💡":
            cls = ' class="idea"'
        elif marker in "⚠":
            cls = ' class="warn"'
        elif marker == "🔹":
            cls = ' class="note"'
        out.append(f"<li{cls}>{apply_bold(body, bolds)}</li>")
    close()
    return "\n".join(out)


def video_figure(page):
    v = VIDEOS[page]
    poster = (IMAGES.get(page) or [None])[0]
    watch = f'https://www.youtube.com/watch?v={v["id"]}'
    if v.get("list"):
        watch += f'&list={v["list"]}'
    embed = f'https://www.youtube-nocookie.com/embed/{v["id"]}'
    if v.get("list"):
        embed += f'?list={v["list"]}'
    img = (f'<img src="img/{poster}" alt="Video thumbnail: {esc(v["label"])}" loading="lazy">'
           if poster else "")
    return (
        f'<figure class="video">'
        f'<button class="playbox" data-embed="{embed}" aria-label="Play the {esc(v["label"])} video">'
        f'{img}<span class="play" aria-hidden="true">▶</span></button>'
        f'<figcaption>Video: {esc(v["label"])} · '
        f'<a href="{watch}" target="_blank" rel="noopener">Watch on YouTube</a>'
        f'</figcaption></figure>'
    )


def figures(page):
    if page in VIDEOS:
        return video_figure(page)
    out = []
    for name in IMAGES.get(page, []):
        out.append(
            f'<figure><img loading="lazy" src="img/{name}" '
            f'alt="Diagram from slide {page}"></figure>'
        )
    return "".join(out)


def page_kind(rec):
    """Classify a slide from its display type (title lines)."""
    titles = [norm(t) for t in rec.get("title_lines", [])]
    joined = " ".join(titles)
    lines = rec["lines"]
    for t in titles:
        if t in QUADS:
            return ("quad", QUADS[t])
    if "when to use" in joined:
        return ("when", "When to Use")
    if "final thoughts" in joined:
        return ("final", "Final Thoughts")
    if "key concepts" in joined:
        return ("keys", "Key Concepts")
    if any(l.startswith("Definition:") or l.startswith("• Definition:") for l in lines):
        return ("def", None)
    return ("other", None)


def is_overview(rec):
    """The 2x2 summary slides repeat the detail pages; detect and drop them."""
    blob = norm(" ".join(rec.get("title_lines", []) + rec["lines"]))
    return sum(1 for q in QUADS if re.search(r"\b" + q + r"\b", blob)) >= 3


def swot_block(quads, bolds):
    out = ['<h3 class="swot-head">SWOT Analysis</h3><div class="swot">']
    for label in ("Strengths", "Weaknesses", "Opportunities", "Threats"):
        if label not in quads:
            continue
        items = quads[label] if isinstance(quads[label], list) else []
        out.append(f'<div class="quad {label.lower()}"><h4>{label}</h4>'
                   f'{render_items(items, bolds)}</div>')
    out.append("</div>")
    return "".join(out)


def build_topic(slug, title, pages):
    body = []
    live = [p for p in pages if p not in SKIP_PAGES and p in PAGES]
    kinds = {p: page_kind(PAGES[p]) for p in live}
    detail_quads = {lbl: p for p in live for k, lbl in [kinds[p]] if k == "quad"}

    pending_quads, pending_bolds = {}, []
    for p in live:
        rec = PAGES[p]
        bolds = rec["bold"]
        kind, label = kinds[p]

        if kind == "other" and is_overview(rec) and detail_quads:
            continue  # summary grid, superseded by the detail pages

        clean_lines = strip_chrome(rec["lines"], title)

        if kind == "quad":
            items = items_from([l for l in clean_lines if norm(l) not in QUADS])
            if items:
                pending_quads[label] = items
                pending_bolds = pending_bolds + bolds
            continue

        single = parse_quadrants(clean_lines) if not detail_quads else None
        if single:
            body.append(swot_block({k: items_from(v) for k, v in single.items()}, bolds))
            continue

        items = items_from(clean_lines)
        if not items and not IMAGES.get(p):
            continue

        if pending_quads:
            body.append(swot_block(pending_quads, pending_bolds))
            pending_quads, pending_bolds = {}, []

        if label and kind in ("when", "final", "keys"):
            body.append(f"<h3>{label}</h3>")
        elif kind == "other":
            head = next((t for t in rec.get("title_lines", []) if 3 < len(t) < 60
                         and norm(t) not in CHROME and norm(t) != norm(title)), None)
            if head:
                body.append(f"<h3>{esc(head)}</h3>")
        body.append(render_items(items, bolds))
        fig = figures(p)
        if fig:
            body.append(f'<div class="figs">{fig}</div>')

    if pending_quads:
        body.append(swot_block(pending_quads, pending_bolds))

    first_page = next((p for p in pages if p not in SKIP_PAGES), pages[0])
    return (f'<section class="topic" id="{slug}" data-title="{esc(title)}">'
            f'<h2>{esc(title)}<a class="anchor" href="#{slug}" aria-label="Link to this entry">#</a></h2>'
            + "\n".join(body) + "</section>")


# ---------- glossary: link each term to its entry ----------
def build_glossary(slug, title, pages):
    rows = []
    for p in pages:
        rec = PAGES[p]
        lines = strip_chrome(rec["lines"], title)
        for it in items_from(lines):
            m = re.match(r"^([^:]{2,60}):\s*(.+)$", it)
            if m:
                term, desc = m.group(1).strip(), m.group(2).strip()
                tslug = lookup(term)
                name = f'<a href="#{tslug}">{esc(term)}</a>' if tslug else esc(term)
                rows.append(f'<div class="gterm"><dt>{name}</dt><dd>{apply_bold(desc, rec["bold"])}</dd></div>')
            else:
                rows.append(f'<div class="gterm"><dd class="plain">{apply_bold(it, rec["bold"])}</dd></div>')
    figs = "".join(figures(p) for p in pages)
    figs = f'<div class="figs">{figs}</div>' if figs else ""
    return (f'<section class="topic" id="{slug}" data-title="{esc(title)}">'
            f'<h2>{esc(title)}<a class="anchor" href="#{slug}" aria-label="Link to this entry">#</a></h2>'
            f'<dl class="glossary">{"".join(rows)}</dl>{figs}</section>')



ABOUT_CONTENTS = [
    ("Actions and Concepts", None, [
        ("80+ Actions / Concepts with Definitions, How it Works and Why it Works", None),
        ("Dribble Hand Off – How to Execute and How to guard", "dho-overview"),
    ]),
    ("SWOT Analysis - Offense", "Strengths, Weaknesses, Opportunities and Threats", [
        ("Flex Offense", "flex-offense"),
        ("Horns Offense", "horns-offense"),
        ("Pistol Offense", "pistol-offense"),
        ("Princeton Offense", "princeton-offense"),
        ("5-Out Offense", "five-out-offense"),
        ("Circle Motion Offense", "circle-motion-offense"),
    ]),
]

ABOUT_DEFENSE = [
    ("Ball Screen Coverages: On-Ball Defender", [
        ("Over (Zero Man Removed)", "zero-man-removed"),
        ("Under (One Man Removed)", "one-man-removed"),
        ("Press Up (Two Man Removed)", "two-man-removed"),
    ]),
    ("Ball Screen Coverages: Off-Ball Defender", [
        ("Drop", "drop"), ("Hedge", "hard-hedge"), ("Shadow", "shadow"),
        ("Switch", "switch"), ("Trap", "trapping"),
    ]),
    ("Off- Ball Screen Coverages: Off-Ball Defender", [
        ("Zero Man Removed", "zero-man-removed"),
        ("One Man Removed", "one-man-removed"),
        ("Two Man Removed", "two-man-removed"),
    ]),
]

ABOUT_USE = [
    ("Players", [
        "This presentation is a repository of basketball information to help develop and strengthen your basketball IQ",
        "Be a student of the game. Study actions and concepts that are in this document",
        "Doing so will help “slow the game” down for you",
        "Helping you process what you are seeing faster; allowing you to make better in game decisions",
    ]),
    ("Coaches", [
        "Use this presentation as a template to build / demonstrate your team identity",
        "Choose or Add to existing actions / concepts or offenses / defenses that pertain to your team and what you want to accomplish this upcoming season",
        "Delete any actions / concepts or offenses / defenses that do not pertain to your team",
        "The result is your team’s offense and defensive philosophies / scheme + actions and concepts that your players will need to know and utilize.",
    ]),
]


def link_or_text(text, slug):
    return f'<a href="#{slug}">{esc(text)}</a>' if slug else esc(text)


def build_about(slug, title, pages):
    cards = []
    for head, sub, rows_ in ABOUT_CONTENTS:
        inner = f'<p class="cardsub">{esc(sub)}</p>' if sub else ""
        lis = "".join(f"<li>{link_or_text(t, sl)}</li>" for t, sl in rows_)
        cards.append(f'<div class="acard"><h4>{esc(head)}</h4>{inner}<ul>{lis}</ul></div>')

    cols = []
    for head, rows_ in ABOUT_DEFENSE:
        lis = "".join(f"<li>{link_or_text(t, sl)}</li>" for t, sl in rows_)
        cols.append(f"<div><h5>{esc(head)}</h5><ul>{lis}</ul></div>")
    cards.append(
        '<div class="acard wide"><h4>SWOT Analysis - Defense</h4>'
        '<p class="cardsub">Strengths, Weaknesses, Opportunities and Threats</p>'
        '<ul class="flat"><li>Gap Defense</li></ul>'
        f'<div class="subcols">{"".join(cols)}</div></div>'
    )

    use = []
    for head, rows_ in ABOUT_USE:
        lis = "".join(f"<li>{esc(t)}</li>" for t in rows_)
        use.append(f'<div class="acard"><h4>{esc(head)}</h4><ul>{lis}</ul></div>')

    return (
        f'<section class="topic about" id="{slug}" data-title="{esc(title)}" data-nosearch="1">'
        f'<h2>{esc(title)}<a class="anchor" href="#{slug}" aria-label="Link to this entry">#</a></h2>'
        '<h3>What is in this document?</h3>'
        f'<div class="agrid">{"".join(cards)}</div>'
        '<p class="andmore">AND MORE</p>'
        '<h3>How do I use this document?</h3>'
        f'<div class="agrid two">{"".join(use)}</div>'
        '<p class="anote"><span>Example</span> Horns Offense + One Man Removed and Hedge Ball '
        'Screens + Switch Off-Ball Screens. Will utilize the following actions: Miami, Veer, '
        'Stampede, … , … etc</p>'
        '<p class="anote"><span>Links</span> Any word with a hyperlink – click on the word and '
        'then the link that appears. This will direct you to the action / concept. '
        'Example: <a href="#veer-screen">Veer</a></p>'
        '</section>'
    )


GLOSSARY_SLUGS = {"concepts", "screens-list", "cuts-list", "ball-terminology"}

sections_html, nav_html = [], []
for part_slug, part_title, topics in PARTS:
    nav_html.append(f'<div class="navpart"><h3>{esc(part_title)}</h3><ul>')
    sections_html.append(f'<div class="part" id="part-{part_slug}"><h1 class="parthead">{esc(part_title)}</h1>')
    for slug, title, pages in topics:
        nav_html.append(f'<li><a href="#{slug}" data-slug="{slug}">{esc(title)}</a></li>')
        if slug == "about":
            sections_html.append(build_about(slug, title, pages))
        elif slug in GLOSSARY_SLUGS:
            sections_html.append(build_glossary(slug, title, pages))
        else:
            sections_html.append(build_topic(slug, title, pages))
    sections_html.append("</div>")
    nav_html.append("</ul></div>")

TEMPLATE = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "template.html"),
                encoding="utf-8").read()
out = TEMPLATE.replace("<!--NAV-->", "\n".join(nav_html)).replace("<!--BODY-->", "\n".join(sections_html))
os.makedirs(SITE, exist_ok=True)
with open(os.path.join(SITE, "index.html"), "w", encoding="utf-8") as fh:
    fh.write(out)

n_topics = sum(len(t) for _, _, t in PARTS)
n_links = out.count('href="#')
print("topics:", n_topics)
print("internal links:", n_links)
print("size: %.0f KB" % (len(out) / 1024))
