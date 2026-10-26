# thoughtsinthevortex.com

Drew Daniel's D.B. Cooper (NORJAK) research site, published with GitHub Pages from the `main` branch root.

## Layout
- `_src/site.json` holds every report and the timeline card (titles, summaries, files). **Edit this.**
- `_src/build.py` regenerates `index.html`, `r/<slug>/index.html`, `404.html` and `assets/site.css` from site.json. Run `python3 _src/build.py` from the repo root.
- `files/`: PDFs (lowercase-hyphen names; keep each under 100 MB).
- `assets/covers/`: page-1 images, used only as link-preview (og:image) pictures. On-site thumbnails are drawn from each entry's `series`, `title`, `subtitle` and `chips` (colored boxes: blue, gold or red) in site.json.
- `read/`: the in-site PDF reader (`read/?f=<file in files/>&t=<title>`), built on Mozilla pdf.js 3.11.174, which is self-hosted in `assets/pdfjs/` (Apache-2.0). Page template: `_src/reader_body.html`.
- `downloads/`: the OCR text pack and the SQLite database ZIPs, plus `index.html` (built from `_src/parts.json`). Rebuild the ZIPs from Drew's `dbcooper.db` when the OCR changes.
- `timeline/`: the Flight 305 Timeline Wheel, a self-contained page plus its `pages/` images. build.py injects a slim site bar right after `<body>` (between `<!--tv-bar-->` markers), so a replacement timeline picks it up automatically.
- Home (`index.html`) is the logo plus three tiles: Write-ups (`writeups/`), Timeline and FBI Files (`downloads/`).
- `CNAME` (thoughtsinthevortex.com) and `.nojekyll`: leave these in place.

## Adding or updating a write-up
1. Copy the PDF into `files/` and render its cover into `assets/covers/`.
2. Add or edit the entry in `_src/site.json`. `kind` is `report` (or `packet` for a source packet, which adds a Source packets section); `featured: true` marks the one shown as "Latest report" (only one).
3. Run `python3 _src/build.py`, check the pages, then commit and push to `main`. Pages redeploys in a minute or two.

The source of truth for every PDF is Drew's research folder, `DBC FBI\Projects\<Project>\`. The site holds published copies only.
