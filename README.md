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
- `subfiles/`: the NORJAK Subfiles 1–1,062 Explorer, a self-contained drop-in page (not built by build.py) with `photos/` (40 portraits), `ocr/partNNN.json` (privacy-scrubbed OCR for the 2,086 linked pages), `pages/pNNN_PPPP.webp` (page scans) and `pages_manifest.json`. It carries its own copy of the site header, so a nav change in build.py must also be made in `subfiles/index.html`.
- `tools/subfiles/`: `build_subfile_vault_pages.py` and `3_BUILD_SUBFILE_VAULT_PAGES.bat`, the local PC generator that renders the remaining `subfiles/pages/*.webp` scans from the FBI Vault PDFs with privacy blackouts. Not linked from the site. Run it with `--out-dir <repo>/subfiles/pages --manifest <repo>/subfiles/pages_manifest.json`, then check `PRIVACY_BLACKOUT_AUDIT_SHEET.jpg` before publishing.
- Home (`index.html`) is the logo plus five tiles: Write-ups (`writeups/`), Timeline, Subfiles (`subfiles/`), FBI Files (`downloads/`) and FOIA Tracker (`foia/`).
- `feedback/`: the anonymous Feedback & suggestions page (templates `_src/feedback_body.html`; the write-up dropdown is built from site.json) and `feedback/admin/`, the private inbox (enter the admin key; view, mark read/archived, download CSV).
- `_feedback-worker/`: the Cloudflare Worker + D1 database that stores submissions (`tv-feedback`). Its URL is `feedback_api` in site.json. It keeps no name, email, IP or user agent; rate limiting uses a one-way daily hash.
- `CNAME` (thoughtsinthevortex.com) and `.nojekyll`: leave these in place.

## Adding or updating a write-up
1. Copy the PDF into `files/` and render its cover into `assets/covers/`.
2. Add or edit the entry in `_src/site.json`. `kind` is `report` (or `packet` for a source packet, which adds a Source packets section); `featured: true` marks the one shown as "Latest report" (only one).
3. Add the mobile-friendly web article (see below).
4. Run `python3 _src/build.py`, check the pages, then commit and push to `main`. Pages redeploys in a minute or two.

## Web articles (mobile-friendly reading)
Each write-up can also be read as a responsive web page at `r/<slug>/read/`, which is now the primary "Read article" button; the PDF stays as "Print PDF".
- Source: `_src/articles/<slug>.html`, one `<article class="wart">` fragment (hero with banner, kicker, title, subtitle, lede, chips; then `<h2 id="...">` sections). build.py wraps it with the section-jump menu, A−/A/A+ text size, tap-to-zoom lightbox and footer links. If the file exists, the article page and button appear automatically.
- Images: `assets/articles/<slug>/`, referenced as `../../../assets/articles/<slug>/<file>`; add `data-zoomable="1"` and `loading="lazy"`.
- Wrap wide tables in `<div class="tbl-wrap">`. Avoid inline pt font sizes and fixed widths carried over from the print layout.
- Before publishing, check at 390 px width that nothing scrolls sideways, and keep personal identifiers out (e.g. old FAA/rigger certificate numbers, which were often SSNs).
- The PDF reader (`read/`) loads pdf.js from `assets/pdfjs/`; keep it self-hosted rather than on a CDN.

The source of truth for every PDF is Drew's research folder, `DBC FBI\Projects\<Project>\`. The site holds published copies only.

## Feedback & suggestions
Submissions go to the `tv-feedback` Worker and its D1 database `tv-feedback`, both in Drew's Cloudflare account.
- Read them at `thoughtsinthevortex.com/feedback/admin/` with the admin key, or from a terminal in `_feedback-worker/`:
  `npx wrangler d1 execute tv-feedback --remote --command "SELECT * FROM entries ORDER BY id DESC"`
- New write-ups appear in the dropdown automatically after `python3 _src/build.py`.
- Redeploy the Worker after changing it: `cd _feedback-worker && npx wrangler deploy`. Change the key with `npx wrangler secret put ADMIN_KEY`.

### First-time Worker setup
```
cd _feedback-worker
npx wrangler d1 create tv-feedback          # already done; database_id is in wrangler.jsonc
npx wrangler d1 execute tv-feedback --remote --file=schema.sql
npx wrangler secret put ADMIN_KEY           # any long random string; it unlocks the inbox
npx wrangler deploy                         # URL must match feedback_api in site.json
```
