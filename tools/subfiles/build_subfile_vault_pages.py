#!/usr/bin/env python3
"""
Thoughts in the Vortex — Subfile Explorer Page-Scan Generator & Privacy Redactor
================================================================================
Renders all 2,062 unique FBI Vault pages referenced across NORJAK Subfiles 1–1,062
into fast, crisp grayscale .webp scans (subfiles/pages/pNNN_PPPP.webp) for
thoughtsinthevortex.com/subfiles/, applying automated Ground Rule #6 blackouts
(SSNs, third-party DOBs, home street addresses, phone numbers, driver's license
numbers, and individual DNA STR allele rows) using Tesseract word_positions/*.tar.

Usage (auto-detects paths when placed in Website or Subfile Explorer folder):
    python build_subfile_vault_pages.py
    python build_subfile_vault_pages.py --pdf-dir "C:\\path\\to\\FBI Vault PDFs" --words-dir "C:\\path\\to\\word_positions"
"""

import argparse
import gzip
import io
import json
import os
import re
import subprocess
import sys
import tarfile
from collections import defaultdict
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageOps
except ImportError:
    print("Installing Pillow...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
    from PIL import Image, ImageDraw, ImageOps

PDF_BACKEND = None
try:
    import pypdfium2 as pdfium
    PDF_BACKEND = "pdfium"
except ImportError:
    try:
        import fitz  # PyMuPDF
        PDF_BACKEND = "pymupdf"
    except ImportError:
        print("Installing pypdfium2 for fast PDF page rendering...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pypdfium2"])
        import pypdfium2 as pdfium
        PDF_BACKEND = "pdfium"


# Master Subfile Index & ACS table pages contain no SSNs/DOBs/addresses/phones
SAFE_INDEX_PAGES = (
    {(90, p) for p in range(17, 39)}
    | {(106, p) for p in range(16, 55)}
    | {(106, p) for p in range(107, 110)}
)

# Tolerates OCR noise inside SSNs (e.g. 423~-50-2846, §33-10-3322, 531+16<2565); FBI serials 164-81-NNNN excluded
SSN_TOKEN_RE = re.compile(r"(?<![\d/])(?![14]64[-.~\s]*81)[0-9§$]\d{2}\s?[-.~–—=+_\s]{0,3}\s?\d{2}\s?[-.~–—=+_<\s]{0,3}\s?\d{4}(?![\d/])")
PHONE_LINE_RE = re.compile(r"(?:\(\d{3}\)\s*|\b\d{3}[-.])\d{3}[-.\s]\d{4}\b")
LOCAL_PHONE_AFTER_KW_RE = re.compile(r"\b(?:TEL|TELEPHONE|PHONE|PH|CALL)\b.*?\b\d{3}[-.\s]\d{4}\b", re.I)
SSN_KW_RE = re.compile(r"\b(?:SSAN|SSAU|SSN|S\.S\.N|SSA\s*NO|SOC\.?\s*SEC|SOCIAL\s+S[EÉ]CURITY|SECURITY\s+(?:ACCOUNT\s+)?(?:NO|NUMBER))\b", re.I)
DOB_KW_RE = re.compile(r"\b(?:DOB|D\.O\.B|BIRTH|BORN|BIRTHDATE)\b", re.I)
ADDR_KW_RE = re.compile(r"\b(?:RESIDENCE|HOME\s+ADDRESS|STREET\s+ADDRESS|MAILING\s+ADDRESS|P\.?\s*O\.?\s*BOX)\b", re.I)
PO_BOX_RE = re.compile(r"\b(?:P\.?\s*O\.?\s*BOX|BOX\s+\d+|RT\.?\s*\d+\s+BOX)\b", re.I)
STREET_LINE_RE = re.compile(
    r"\b\d{2,5}\s+(?![0-9]+\s*(?:FEET|FT|LBS|MILES|BILLS|DOLLARS))[A-Z0-9.\-'\s]{2,28}\b"
    r"(?:ST|STREET|AVE|AVENUE|RD|ROAD|DR|DRIVE|BLVD|WAY|PL|PLACE|LN|LANE|CT|COURT|APT|PKWY|TERR)\b",
    re.I,
)
SAFE_GOV_ADDR_RE = re.compile(r"PEACHTREE|PENNSYLVANIA|FEDERAL\s+BUREAU|SECOND\s+AVE|AIRPORT| COURTHOUSE", re.I)
STR_LOCI_RE = re.compile(r"\b(?:D3S1358|VWA|FGA|D8S1179|D21S11|D18S51|D5S818|D13S317|D7S820|CSF1PO|TPOX|TH01|D16S539)\b", re.I)
DATE_OR_NUM_TOKEN_RE = re.compile(r"\d")
DMV_PAGE_RE = re.compile(r"(?:D|O)RIVER\s*LICENS|MOTOR\s*VEHIC|DEPARTMENT\s+OF\s+LICENSING|OPERATOR.*\d{5}|\bADULT\b.*\d{2}-\d{2}-\d{2}", re.I)
ZIP_CITY_RE = re.compile(r",\s*(?:WA|CA|CAL|CALIF|OR|ORE|ID|MT|FLA|FL|CO|COLORADO|MINN|MN|TX|NJ|NY|OH|GA|VA)\b.*\b\d{5}\b|\b(?:WA|FLA|CAL)\s+\d{5}\b", re.I)


def find_existing_dir(candidates):
    for p in candidates:
        if p and Path(p).is_dir():
            return Path(p).resolve()
    return None


def find_pdf_file(pdf_dirs, part):
    names = [
        f"DB Cooper Part {part:03d}.pdf",
        f"DB_Cooper_Part_{part:03d}.pdf",
        f"DB Cooper Part {part:02d}.pdf",
        f"DB_Cooper_Part_{part:02d}.pdf",
        f"Part_{part:03d}.pdf",
    ]
    for d in pdf_dirs:
        for nm in names:
            cand = Path(d) / nm
            if cand.is_file():
                return cand
    return None


def parse_tsv_words(tsv_text):
    tsv_w, tsv_h = None, None
    words = []
    for idx, line in enumerate(tsv_text.splitlines()):
        if idx == 0:
            continue
        cols = line.split("\t")
        if len(cols) < 12:
            continue
        lvl = cols[0]
        if lvl == "1":
            tsv_w = int(cols[8]) or 1
            tsv_h = int(cols[9]) or 1
        elif lvl == "5":
            txt = cols[11].strip()
            if not txt:
                continue
            words.append({
                "block": int(cols[2]),
                "par": int(cols[3]),
                "line": int(cols[4]),
                "left": int(cols[6]),
                "top": int(cols[7]),
                "width": int(cols[8]),
                "height": int(cols[9]),
                "text": txt,
            })
    return tsv_w, tsv_h, words


def detect_privacy_boxes(part, page, tsv_w, tsv_h, words):
    """Returns list of normalized (x0, y0, x1, y1, reason) boxes to black out under Ground Rule #6."""
    if not words or not tsv_w or not tsv_h:
        return []
    # Index pages skip the address/DOB/phone rules but still get the SSN rule
    # (Part 90 p.23 lists an SSN beside a name).
    safe_index = (part, page) in SAFE_INDEX_PAGES

    full_text = " ".join(w["text"] for w in words)
    is_dmv = bool(DMV_PAGE_RE.search(full_text))

    lines_map = defaultdict(list)
    for w in words:
        lines_map[(w["block"], w["par"], w["line"])].append(w)

    sorted_lines = []
    for k, wlist in lines_map.items():
        wlist.sort(key=lambda z: z["left"])
        l_txt = " ".join(z["text"] for z in wlist)
        x0 = min(z["left"] for z in wlist)
        y0 = min(z["top"] for z in wlist)
        x1 = max(z["left"] + z["width"] for z in wlist)
        y1 = max(z["top"] + z["height"] for z in wlist)
        sorted_lines.append({"key": k, "words": wlist, "text": l_txt, "box": (x0, y0, x1, y1)})

    sorted_lines.sort(key=lambda item: (item["box"][1], item["box"][0]))
    red_boxes = []

    def add_words_box(w_subset, reason):
        if not w_subset:
            return
        bx0 = max(0.0, (min(w["left"] for w in w_subset) - 6) / tsv_w)
        by0 = max(0.0, (min(w["top"] for w in w_subset) - 4) / tsv_h)
        bx1 = min(1.0, (max(w["left"] + w["width"] for w in w_subset) + 6) / tsv_w)
        by1 = min(1.0, (max(w["top"] + w["height"] for w in w_subset) + 4) / tsv_h)
        red_boxes.append((bx0, by0, bx1, by1, reason))

    for i, ln in enumerate(sorted_lines):
        txt = ln["text"]
        wlist = ln["words"]

        # 1. Explicit SSN pattern or SSN label
        if SSN_TOKEN_RE.search(txt) or SSN_KW_RE.search(txt):
            num_words = [w for w in wlist if DATE_OR_NUM_TOKEN_RE.search(w["text"]) and "164" not in w["text"]]
            if num_words:
                add_words_box(num_words, "SSN")
            # Also check immediately below form header (e.g., "Social Security No." with value on next line)
            if SSN_KW_RE.search(txt):
                lx0, ly0, lx1, ly1 = ln["box"]
                for nxt in sorted_lines[i+1:i+5]:
                    nx0, ny0, nx1, ny1 = nxt["box"]
                    if 0 <= (ny0 - ly1) < int(0.045 * tsv_h) and abs(nx0 - lx0) < int(0.18 * tsv_w):
                        n_nums = [w for w in nxt["words"] if DATE_OR_NUM_TOKEN_RE.search(w["text"])]
                        if n_nums:
                            add_words_box(n_nums, "SSN-Below")

        if safe_index:
            continue

        # 2. Phone numbers
        if PHONE_LINE_RE.search(txt) or LOCAL_PHONE_AFTER_KW_RE.search(txt):
            ph_words = [w for w in wlist if DATE_OR_NUM_TOKEN_RE.search(w["text"]) and "164" not in w["text"] and "197" not in w["text"]]
            if ph_words:
                add_words_box(ph_words, "Phone")

        # 3. Date of Birth (DOB)
        if DOB_KW_RE.search(txt):
            # Redact numeric/month tokens after DOB/Born/Birth keyword
            dob_idx = next((idx for idx, w in enumerate(wlist) if DOB_KW_RE.search(w["text"])), 0)
            after_w = [w for w in wlist[dob_idx:] if (DATE_OR_NUM_TOKEN_RE.search(w["text"]) or re.match(r"^(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)", w["text"], re.I)) and "164" not in w["text"]]
            if after_w:
                add_words_box(after_w, "DOB")
            lx0, ly0, lx1, ly1 = ln["box"]
            for nxt in sorted_lines[i+1:i+4]:
                nx0, ny0, nx1, ny1 = nxt["box"]
                if 0 <= (ny0 - ly1) < int(0.04 * tsv_h) and abs(nx0 - lx0) < int(0.16 * tsv_w):
                    n_nums = [w for w in nxt["words"] if DATE_OR_NUM_TOKEN_RE.search(w["text"])]
                    if n_nums:
                        add_words_box(n_nums, "DOB-Below")

        # 4. Street addresses & P.O. Boxes
        if not SAFE_GOV_ADDR_RE.search(txt):
            if PO_BOX_RE.search(txt) or STREET_LINE_RE.search(txt) or ADDR_KW_RE.search(txt):
                if ADDR_KW_RE.search(txt):
                    kw_i = next((idx for idx, w in enumerate(wlist) if ADDR_KW_RE.search(w["text"])), 0)
                    tail = wlist[kw_i+1:]
                    if tail:
                        add_words_box(tail, "Address")
                else:
                    add_words_box(wlist, "Address")
            elif is_dmv and ZIP_CITY_RE.search(txt):
                add_words_box(wlist, "DMV-CityZip")

        # 5. DMV license numbers, spaced DOBs & directional addresses on DMV sheets
        if is_dmv:
            if re.search(r"\b\d{3,5}\s+(?:NW|NE|SW|SE|N|S|E|W)\s+\d+", txt, re.I) or re.search(r"\b(?:0[1-9]|1[0-2])\s+[0-3]\d\s+[1-5]\d\b", txt):
                add_words_box([w for w in wlist if DATE_OR_NUM_TOKEN_RE.search(w["text"]) or len(w["text"]) <= 3], "DMV-DOB/Addr")
            for w in wlist:
                wt = w["text"]
                if re.match(r"^(?:[A-Z]{1,2}[-*][A-Z0-9]{2,}[-*][A-Z0-9-]{2,}|[A-Z]\d{2,4}[-.]\d{2,4}.*|[A-Z]\d{5,9}|\d{6,8})$", wt) and not wt.startswith("3859"):
                    add_words_box([w], "DMV-ID/DOB")

        # 6. DNA STR Allele tables
        if STR_LOCI_RE.search(txt):
            allele_w = [w for w in wlist if not STR_LOCI_RE.search(w["text"]) and DATE_OR_NUM_TOKEN_RE.search(w["text"])]
            if allele_w:
                add_words_box(allele_w, "STR-Genotype")

    return red_boxes


def render_pdf_page(doc_tuple, page_1based, target_width=1150):
    backend, doc = doc_tuple
    if backend == "pdfium":
        page_obj = doc[page_1based - 1]
        w_pt = page_obj.get_width() or 612
        scale = target_width / float(w_pt)
        return page_obj.render(scale=scale).to_pil().convert("L")
    else:
        page_obj = doc.load_page(page_1based - 1)
        w_pt = page_obj.rect.width or 612
        scale = target_width / float(w_pt)
        pix = page_obj.get_pixmap(matrix=fitz.Matrix(scale, scale), colorspace=fitz.csGRAY)
        return Image.frombytes("L", [pix.width, pix.height], pix.samples)


def main():
    script_dir = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="Render & privacy-screen NORJAK Subfile Vault pages")
    parser.add_argument("--manifest", default=None, help="Path to pages_manifest.json")
    parser.add_argument("--pdf-dir", default=None, help="Folder containing DB Cooper Part NNN.pdf files")
    parser.add_argument("--words-dir", default=None, help="Folder containing partNNN.tar word_positions")
    parser.add_argument("--out-dir", default=None, help="Output folder for pNNN_PPPP.webp files")
    parser.add_argument("--width", type=int, default=1020, help="Rendered image width in pixels (default: 1020)")
    parser.add_argument("--quality", type=int, default=60, help="WebP quality 1-100 (default: 60)")
    parser.add_argument("--force", action="store_true", help="Re-render pages even if .webp already exists")
    args = parser.parse_args()

    # Locate pages_manifest.json
    manifest_candidates = [
        args.manifest,
        script_dir / "subfiles" / "pages_manifest.json",
        script_dir / "pages_manifest.json",
        script_dir / "staged_updates" / "subfiles" / "pages_manifest.json",
        script_dir / "site_repo" / "subfiles" / "pages_manifest.json",
        script_dir / "intermediate_pages" / "pages_manifest.json",
    ]
    manifest_path = next((Path(p) for p in manifest_candidates if p and Path(p).is_file()), None)
    if not manifest_path:
        print("[ERROR] Could not find pages_manifest.json!", file=sys.stderr)
        sys.exit(1)

    home = Path.home()
    pdf_dirs = [p for p in [
        args.pdf_dir,
        script_dir / "FBI Vault PDFs",
        script_dir.parent / "FBI Vault PDFs",
        script_dir.parent.parent / "FBI Vault PDFs",
        home / "OneDrive - Baird & Stallings" / "Desktop" / "Claude Files" / "DBC FBI" / "FBI Vault PDFs",
        home / "Downloads",
        Path("G:/My Drive/DBC FBI/FBI Vault PDFs"),
        script_dir / "downloads",
    ] if p and Path(p).is_dir()]

    words_dir = find_existing_dir([
        args.words_dir,
        script_dir / "word_positions",
        script_dir.parent / "word_positions",
        script_dir.parent.parent / "word_positions",
        home / "OneDrive - Baird & Stallings" / "Desktop" / "Claude Files" / "DBC FBI" / "word_positions",
        Path("G:/My Drive/DBC FBI/word_positions"),
        script_dir / "downloads",
    ])

    if args.out_dir:
        out_dir = Path(args.out_dir)
    elif (script_dir / "site_repo" / ".git").exists():
        out_dir = script_dir / "site_repo" / "subfiles" / "pages"
    elif (script_dir / "staged_updates").is_dir():
        out_dir = script_dir / "staged_updates" / "subfiles" / "pages"
    else:
        out_dir = manifest_path.parent / "pages"
    out_dir.mkdir(parents=True, exist_ok=True)

    with open(manifest_path, encoding="utf-8") as f:
        manifest = json.load(f)
    pages = manifest["pages"]

    by_part = defaultdict(list)
    for rec in pages:
        by_part[int(rec["part"])].append(rec)

    print(f"Manifest loaded: {len(pages)} unique pages across {len(by_part)} Vault parts.")
    print(f"PDF search dirs: {[str(d) for d in pdf_dirs]}")
    print(f"Word-box dir   : {words_dir}")
    print(f"Output folder  : {out_dir}")

    rendered_count = 0
    skipped_existing = 0
    missing_parts = []
    redacted_pages_sample = []
    total_redaction_bars = 0

    for part in sorted(by_part.keys()):
        recs = by_part[part]
        if not args.force and all((out_dir / f"{r['key']}.webp").is_file() for r in recs):
            skipped_existing += len(recs)
            continue

        pdf_path = find_pdf_file(pdf_dirs, part)
        if not pdf_path:
            missing_parts.append(part)
            continue

        doc_tuple = ("pdfium", pdfium.PdfDocument(str(pdf_path))) if PDF_BACKEND == "pdfium" else ("pymupdf", fitz.open(str(pdf_path)))
        tar_path = (words_dir / f"part{part:03d}.tar") if words_dir else None
        tf = tarfile.open(tar_path, "r") if (tar_path and tar_path.is_file()) else None

        for rec in recs:
            pg = int(rec["page"])
            out_file = out_dir / f"{rec['key']}.webp"
            if out_file.is_file() and not args.force:
                skipped_existing += 1
                continue

            im = render_pdf_page(doc_tuple, pg, target_width=args.width)
            im = ImageOps.autocontrast(im, cutoff=1)

            # Load word boxes from partNNN.tar if available
            tsv_w, tsv_h, words = None, None, []
            if tf is not None:
                member_name = f"{part:03d}/p{pg:04d}.tsv.gz"
                try:
                    raw_tsv = gzip.decompress(tf.extractfile(member_name).read()).decode("utf-8", errors="replace")
                    tsv_w, tsv_h, words = parse_tsv_words(raw_tsv)
                except Exception:
                    pass

            boxes = detect_privacy_boxes(part, pg, tsv_w, tsv_h, words)
            if boxes:
                draw = ImageDraw.Draw(im)
                W, H = im.size
                for bx0, by0, bx1, by1, _reason in boxes:
                    draw.rectangle(
                        [int(bx0 * W), int(by0 * H), int(bx1 * W), int(by1 * H)],
                        fill=18,
                    )
                total_redaction_bars += len(boxes)
                if len(redacted_pages_sample) < 24:
                    thumb = im.copy()
                    thumb.thumbnail((360, 460))
                    card = Image.new("RGB", (372, 492), (248, 244, 235))
                    card.paste(thumb.convert("RGB"), ((372 - thumb.width)//2, 26))
                    cd = ImageDraw.Draw(card)
                    cd.text((8, 6), f"Part {part} p.{pg} ({len(boxes)} Rule#6 bars)", fill=(160, 20, 20))
                    redacted_pages_sample.append(card)

            im.save(out_file, format="WEBP", quality=args.quality, method=4)
            rendered_count += 1

        if tf is not None:
            tf.close()

    if redacted_pages_sample:
        cols = 6
        rows_n = (len(redacted_pages_sample) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * 376, rows_n * 496), (255, 255, 255))
        for idx, c in enumerate(redacted_pages_sample):
            r, col = divmod(idx, cols)
            sheet.paste(c, (col * 376, r * 496))
        audit_path = out_dir.parent / "PRIVACY_BLACKOUT_AUDIT_SHEET.jpg"
        sheet.save(audit_path, quality=84)
        print(f"Saved Ground Rule #6 visual audit sheet: {audit_path}")

    total_bytes = sum(p.stat().st_size for p in out_dir.glob("*.webp"))
    print(
        f"Done! Rendered={rendered_count}, AlreadyCached={skipped_existing}, "
        f"Rule#6BlackoutBars={total_redaction_bars}, FolderSize={total_bytes/1024/1024:.2f} MB"
    )
    if missing_parts:
        print(f"Note: {len(missing_parts)} Vault parts not in local PDF dir yet: {missing_parts[:15]}...")


if __name__ == "__main__":
    main()
