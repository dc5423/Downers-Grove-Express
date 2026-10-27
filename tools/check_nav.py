"""Click nav links in a real browser and report where the page lands."""
import sys
from playwright.sync_api import sync_playwright

SITE = sys.argv[1]
ONLY = sys.argv[2] if len(sys.argv) > 2 else ""

with sync_playwright() as pw:
    b = pw.chromium.launch(args=["--disable-lcd-text"])
    pg = b.new_page(viewport={"width": 1400, "height": 900})
    errs = []
    pg.on("pageerror", lambda e: errs.append("pageerror: " + str(e)))
    pg.on("console", lambda m: errs.append("console: " + m.text) if m.type == "error" else None)
    pg.route("**fonts.googleapis.com**", lambda r: r.abort())
    pg.route("**fonts.gstatic.com**", lambda r: r.abort())
    pg.goto("file://" + SITE + "/index.html", wait_until="domcontentloaded")
    pg.add_style_tag(content="html{scroll-behavior:auto !important}")
    pg.wait_for_timeout(300)

    links = pg.eval_on_selector_all(
        "nav a", "els => els.map(e => e.dataset.slug)")
    if ONLY:
        links = [s for s in links if s and s.startswith(ONLY)]
    print("testing", len(links), "links | js errors so far:", errs[:3], flush=True)

    bad = []
    for slug in links:
        pg.evaluate("window.scrollTo(0,0)")
        pg.click(f'nav a[data-slug="{slug}"]')
        pg.wait_for_timeout(120)
        box = pg.evaluate(
            """(s) => { const el = document.getElementById(s);
                 if (!el) return null;
                 const r = el.getBoundingClientRect();
                 return {top: Math.round(r.top), h: Math.round(r.height),
                         y: Math.round(window.scrollY),
                         disp: getComputedStyle(el).display}; }""", slug)
        ok = bool(box) and box["h"] > 0 and -5 <= box["top"] <= 240
        if not ok:
            bad.append((slug, box))
        print(f"  {'ok ' if ok else 'BAD'} {slug:<26} {box}", flush=True)

    print("\nfailures:", len(bad))
    for s, box in bad:
        print("   ", s, box)
    if errs:
        print("js errors:", errs[:6])
    b.close()
