# thoughtsinthevortex.com

Drew Daniel's D.B. Cooper (NORJAK) research site, published with GitHub Pages from the `main` branch root.

## Layout
- `_src/site.json` holds every report, source packet and the timeline card (titles, summaries, files). **Edit this.**
- `_src/build.py` regenerates `index.html`, `r/<slug>/index.html`, `404.html` and `assets/site.css` from site.json. Run `python3 _src/build.py` from the repo root.
- `files/`: PDFs (lowercase-hyphen names; keep each under 100 MB).
- `assets/covers/`: page-1 thumbnails (render with pymupdf at 80 dpi, JPG).
- `timeline/`: the Flight 305 Timeline Wheel, a self-contained page plus its `pages/` images.
- `CNAME` (thoughtsinthevortex.com) and `.nojekyll`: leave these in place.

## Adding or updating a write-up
1. Copy the PDF into `files/` and render its cover into `assets/covers/`.
2. Add or edit the entry in `_src/site.json`. `kind` is `report` or `packet`; `featured: true` marks the one shown as "Latest report" (only one).
3. Run `python3 _src/build.py`, check the pages, then commit and push to `main`. Pages redeploys in a minute or two.

The source of truth for every PDF is Drew's research folder, `DBC FBI\Projects\<Project>\`. The site holds published copies only.
