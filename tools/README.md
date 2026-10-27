# Build tools

`index.html` is generated from the original Google Slides deck, exported as a PDF.
These scripts do the generating, so a change to the source deck can be rebuilt
rather than patched by hand.

## Running it

Needs Python 3 with `pdfplumber`, `pypdf` and `Pillow`, plus `pdftotext` and
`pdfimages` from poppler-utils.

```
pip install pdfplumber pypdf Pillow

# 1. text, bold runs and link targets, page by page
python3 extract3.py "DGS Express Knowledgebase.pdf" ./kb

# 2. diagrams, composited and compressed
python3 images.py "DGS Express Knowledgebase.pdf" ../img

# 3. the page itself
python3 build.py ./kb ..
```

## What each file does

| File | Job |
|---|---|
| `extract3.py` | Pulls text, bold runs and hyperlink targets out of the PDF. |
| `lines.py` | Splits each slide into columns, drops display type, decides where paragraphs break. |
| `images.py` | Extracts diagrams, composites soft masks, skips solid background blocks, compresses to JPEG. |
| `outline.py` | The map from PDF pages to sections and entries, plus the term aliases that make cross-links resolve. |
| `drills.py` | The Drills & Resources section. Hand-maintained, not extracted from the PDF. |
| `build.py` | Turns the extracted content into the page. |
| `template.html` | The shell: styling, search and navigation. `build.py` fills in `<!--NAV-->` and `<!--BODY-->`. |

## Adding a drill

Open `drills.py`, find the group it belongs in, and add one line:

```python
{"title": "Shell Drill, 4 on 4", "url": "https://youtu.be/XXXXXXXXXXX"},
```

Then rebuild step 3 above. A YouTube link gets a Play button that runs the
video on the page; anything else becomes an "Open link" button. Optional
extras are `note` for a line of description, `source` for a credit tag, and
`see` to point at a knowledgebase entry by slug.

Nothing else needs touching. The nav, the search index and the anchors all
pick it up on the next build.

## Changing things

- **Reordering or renaming entries:** edit `outline.py`. `PARTS` is the whole
  structure; `SKIP_PAGES` lists divider slides that carry no content.
- **A term that should link somewhere but doesn't:** add it to `ALIASES` in
  `outline.py`, mapping the term to an entry slug.
- **Styling, search, navigation:** edit `template.html`.
- **The About section** is hand-built in `build.py` (`ABOUT_CONTENTS`,
  `ABOUT_DEFENSE`, `ABOUT_USE`) because the original slide is one long list.
