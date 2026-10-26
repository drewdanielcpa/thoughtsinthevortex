#!/usr/bin/env python3
"""Build thoughtsinthevortex.com from _src/site.json.
Run from the repo root:  python3 _src/build.py
Writes index.html, r/<slug>/index.html, 404.html. PDFs live in files/, cover thumbnails in assets/covers/.
"""
import json, html, os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S=json.load(open(os.path.join(ROOT,'_src','site.json'),encoding='utf-8'))
E=lambda x: html.escape(x, quote=True)

CSS='''
:root{--bg:#fbf7ee;--paper:#fffdf7;--ink:#211d1c;--muted:#5d6b69;--teal:#2f4a4c;--teal2:#466567;--line:#d8d0bb;--gold:#c47f0e;--blue:#2b6cb0;--red:#a82828}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.6 "Lora",Georgia,serif}
a{color:var(--teal);text-decoration-thickness:1px;text-underline-offset:3px}a:hover{color:var(--gold)}
.wrap{max-width:1080px;margin:0 auto;padding:0 20px}
header.top{background:var(--teal);color:#f2ead3}
header.top .wrap{display:flex;align-items:center;justify-content:space-between;gap:16px;padding-top:12px;padding-bottom:12px}
.brand{font-family:"Poppins",sans-serif;font-weight:600;letter-spacing:.5px;color:#f2ead3;text-decoration:none;font-size:17px}
.brand:hover{color:#fff}
nav a{font-family:"Poppins",sans-serif;font-size:14px;color:#dfe8e5;text-decoration:none;margin-left:18px}nav a:hover{color:#fff}
.hero{padding:28px 0 8px}.hero img{width:100%;max-width:760px;display:block;border-radius:3px;border:2px solid var(--teal2)}
.kicker{font-family:"Poppins",sans-serif;font-size:12px;letter-spacing:2.4px;text-transform:uppercase;color:var(--teal2);font-weight:600;margin:28px 0 8px;display:flex;align-items:center;gap:12px}
.kicker:after{content:"";flex:1;height:1px;background:#9fb6b2}
h1,h2,h3{font-family:"Poppins",sans-serif;color:var(--teal);font-weight:600;letter-spacing:-.3px}
h1{font-size:clamp(28px,4.4vw,40px);line-height:1.12;margin:6px 0 4px}
.sub{font-style:italic;color:var(--teal2);font-size:clamp(18px,2.4vw,22px);margin:0 0 12px}
.lede{font-size:17px;max-width:760px;color:#3c3836}
.feature{display:grid;grid-template-columns:260px 1fr;gap:28px;background:var(--paper);border:1px solid var(--line);border-radius:6px;padding:22px;margin:10px 0 6px}
.feature img,.card img,.rp img{width:100%;display:block;border:1px solid var(--line);border-radius:3px;background:#fff}
.chips{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:14px 0}
.chip{border-radius:5px;padding:9px 12px;color:#fff;font-family:"Poppins",sans-serif;font-size:13px;line-height:1.4}.chip b{display:block;font-size:14px;font-weight:600;margin-bottom:2px}
.chip:nth-child(1){background:var(--blue)}.chip:nth-child(2){background:var(--gold)}.chip:nth-child(3){background:var(--red)}
.btns{display:flex;flex-wrap:wrap;gap:10px;margin-top:12px}
.btn{font-family:"Poppins",sans-serif;font-size:14px;font-weight:500;background:var(--teal);color:#fff;text-decoration:none;padding:9px 14px;border-radius:5px;display:inline-block}
.btn:hover{background:var(--gold);color:#fff}.btn.alt{background:transparent;color:var(--teal);border:1.5px solid var(--teal)}.btn.alt:hover{border-color:var(--gold);color:var(--gold)}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:18px;margin:8px 0 10px}
.card{background:var(--paper);border:1px solid var(--line);border-radius:6px;padding:14px;text-decoration:none;color:var(--ink);display:flex;flex-direction:column;gap:10px;transition:border-color .15s}
.card:hover{border-color:var(--gold);color:var(--ink)}.card h3{margin:2px 0 0;font-size:17px;line-height:1.25}.card p{margin:0;font-size:14.5px;color:#4a4644}
.card .meta,.meta{font-family:"Poppins",sans-serif;font-size:12px;color:var(--muted);letter-spacing:.3px}
.card img{aspect-ratio:17/22;object-fit:cover;object-position:top}
.tl{display:flex;gap:20px;align-items:center;background:var(--teal);color:#f2ead3;border-radius:6px;padding:20px 22px;text-decoration:none;margin:8px 0}
.tl h3{color:#fff;margin:0 0 4px}.tl p{margin:0;color:#dfe8e5}.tl:hover{background:#26403f;color:#fff}
.tl .go{margin-left:auto;font-family:"Poppins",sans-serif;font-weight:600;white-space:nowrap}
.about{background:var(--paper);border:1px solid var(--line);border-radius:6px;padding:18px 22px;margin:10px 0 30px;font-size:15.5px}
code{font-family:ui-monospace,Menlo,monospace;font-size:.9em;background:#efe8d3;padding:1px 5px;border-radius:3px}
footer{border-top:1px solid var(--line);padding:18px 0 34px;color:var(--muted);font-size:14px}
.crumb{font-family:"Poppins",sans-serif;font-size:13px;margin:22px 0 0}
.rp{display:grid;grid-template-columns:300px 1fr;align-items:start;gap:32px;margin:14px 0 30px}
.rp ul{padding-left:20px}.rp li{margin-bottom:6px}

.tcard{display:block;background:var(--bg);border:2.5px solid var(--teal2);border-radius:4px;padding:5px;text-decoration:none;color:var(--ink)}
.tcard .in{border:1px solid #9fb6b2;border-radius:2px;padding:16px 15px 15px;height:100%}
.tcard .ser{font-family:"Poppins",sans-serif;font-size:9.5px;letter-spacing:1.8px;text-transform:uppercase;color:var(--teal2);font-weight:600;line-height:1.5}
.tcard .tt{font-family:"Poppins",sans-serif;font-weight:600;color:var(--teal);font-size:21px;line-height:1.12;letter-spacing:-.4px;margin:8px 0 4px}
.tcard .st{font-style:italic;color:var(--teal2);font-size:14.5px;line-height:1.35;margin-bottom:12px}
.tcard .ch{border-radius:4px;padding:7px 10px;color:#fff;font-family:"Poppins",sans-serif;font-size:11.5px;line-height:1.4;margin-top:7px}
.tcard .ch b{display:block;font-size:13px;font-weight:600}
.ch.blue{background:var(--blue)}.ch.gold{background:var(--gold)}.ch.red{background:var(--red)}
a.tcard:hover{border-color:var(--gold)}
.hero{padding:26px 0 6px}.hero .fr{max-width:720px;background:var(--bg);border:2.5px solid var(--teal2);border-radius:4px;padding:6px}.hero .fr div{border:1px solid #9fb6b2;padding:12px;border-radius:2px}.hero img{border:0;border-radius:2px;max-width:100%}
.card .tcard{pointer-events:none;flex:1}.card{padding:12px}
.rbar{position:sticky;top:0;z-index:5;display:flex;align-items:center;gap:14px;flex-wrap:wrap;background:var(--paper);border:1px solid var(--line);border-radius:6px;padding:8px 12px;margin:16px 0 14px;font-family:"Poppins",sans-serif;font-size:13.5px}
.rbar .rt{font-weight:600;color:var(--teal);flex:1;min-width:180px}.rbar .rp2{color:var(--muted);white-space:nowrap}.rbar a.rb{text-decoration:none;white-space:nowrap}
.rbar button{font:600 15px "Poppins",sans-serif;width:30px;height:28px;border:1px solid var(--teal);background:transparent;color:var(--teal);border-radius:4px;cursor:pointer;margin-left:4px}
#pages{display:flex;flex-direction:column;align-items:center;gap:14px;padding-bottom:40px;overflow-x:auto}
.pg{position:relative;background:#fff;box-shadow:0 1px 4px rgba(0,0,0,.18);flex:none}.pg canvas{display:block}.pg a.lk{position:absolute;display:block}.pg a.lk:hover{background:rgba(196,127,14,.15)}
.home{padding:10px 0 30px}.home .hero{display:flex;justify-content:center;padding-top:34px}.home .hero .fr{max-width:820px;width:100%}
.tagl{text-align:center;font-family:"Poppins",sans-serif;font-size:13px;letter-spacing:2.6px;text-transform:uppercase;color:var(--teal2);font-weight:600;margin:20px 0 22px}
.tiles{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;max-width:880px;margin:0 auto}
.tile{display:flex;flex-direction:column;gap:8px;background:var(--teal);color:#f2ead3;text-decoration:none;border-radius:6px;padding:22px 20px 18px;border:2px solid var(--teal);transition:transform .12s,border-color .12s}
.tile:hover{transform:translateY(-2px);border-color:var(--gold);color:#fff}
.tile .tk{font-family:"Poppins",sans-serif;font-weight:600;font-size:24px;color:#fff;letter-spacing:-.3px}
.tile .td{font-size:14.5px;line-height:1.45;color:#dfe8e5;flex:1}.tile .tg{font-family:"Poppins",sans-serif;font-weight:600;font-size:14px;color:#f4c86a}
.tile.hot{background:var(--gold);border-color:var(--gold)}.tile.hot .td{color:#fff6e0}.tile.hot .tg{color:#fff}.tile.hot:hover{border-color:var(--teal)}
@media (max-width:760px){.tiles{grid-template-columns:1fr}.home .hero{padding-top:18px}header.top .wrap{flex-wrap:wrap;gap:4px 16px}.brand{white-space:nowrap;font-size:15px}nav a:first-child{margin-left:0}.feature,.rp{grid-template-columns:1fr}.feature .tcard,.rp .tcard{max-width:340px}.chips{grid-template-columns:1fr}nav a{margin-left:12px;font-size:13px}.tl{flex-direction:column;align-items:flex-start}.tl .go{margin-left:0}}
'''
FONTS='<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,600;1,400&family=Poppins:wght@500;600&display=swap">'

def page(title, desc, body, depth=0, og_img=None):
    up='../'*depth
    og=f'<meta property="og:image" content="https://{S["domain"]}/{og_img}">' if og_img else ''
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title><meta name="description" content="{E(desc)}">
<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}"><meta property="og:type" content="website">{og}
<link rel="icon" href="{up}assets/vortex_logo.jpg">{FONTS}<link rel="stylesheet" href="{up}assets/site.css"></head><body>
<header class="top"><div class="wrap"><a class="brand" href="{up or './'}">THOUGHTS IN THE VORTEX</a><nav><a href="{up}writeups/">Write-ups</a><a href="{up}timeline/">Timeline</a><a href="{up}downloads/">FBI Files</a></nav></div></header>
<main class="wrap">{body}</main>
<footer><div class="wrap">Thoughts in the Vortex · Research on NORJAK / Northwest Orient Flight 305 from the <a href="https://vault.fbi.gov/D-B-Cooper%20">FBI Vault D.B. Cooper files</a>. Citations read Vault part / PDF page / Bates number.</div></footer>
</body></html>'''

from urllib.parse import quote
def rd(f,title,up=''):
    return f'{up}read/?f={quote(f)}&t={quote(title)}'
def tcard(it, href=None, cls='tcard'):
    ch=''.join(f'<div class="ch {c}"><b>{E(a)}</b>{E(b)}</div>' for a,b,c in it.get('chips',[]))
    tag='a' if href else 'div'; h=f' href="{href}"' if href else ''
    return f'<{tag} class="{cls}"{h}><div class="in"><div class="ser">{E(it.get("series",""))}</div><div class="tt">{E(it["title"])}</div><div class="st">{E(it["subtitle"])}</div>{ch}</div></{tag}>'
def card(it):
    return f'''<a class="card" href="r/{it["slug"]}/">{tcard(it)}<div class="meta">{"Report" if it["kind"]=="report" else "Source packet"} · {E(it["date"])}</div></a>'''

items=S['items']; feat=next(i for i in items if i.get('featured'))
chips=''.join(f'<div class="chip"><b>{E(a)}</b>{E(b)}</div>' for a,b in feat.get('points',[]))
U='../'
fbtn=''.join(f'<a class="btn{" alt" if k else ""}" href="{rd(f, feat["title"] if k==0 else feat["title"]+" · Companion", U)}">{E(lbl)}</a>' for k,(lbl,f) in enumerate(feat['files']))
def card2(it): return card(it).replace('href="r/','href="../r/')
packets=(f'<div class="kicker" id="packets">Source packets: the FBI pages, highlighted</div><div class="grid">'+''.join(card2(i) for i in items if i['kind']=='packet')+'</div>') if any(i['kind']=='packet' for i in items) else ''
wbody=f'''<div class="crumb"><a href="../">Home</a> › Write-ups</div>
<h1>Write-ups</h1><p class="lede">{E(S["intro"])}</p>
<div class="kicker">Latest report</div>
<div class="feature">{tcard(feat, "../r/"+feat["slug"]+"/")}<div>
<div class="meta">Report · {E(feat["date"])}</div><h2 style="margin:4px 0 2px;font-size:26px"><a href="../r/{feat["slug"]}/" style="text-decoration:none">{E(feat["title"])}</a></h2><p class="sub">{E(feat["subtitle"])}</p>
<p>{E(feat["summary"])}</p><div class="btns">{fbtn}<a class="btn alt" href="../r/{feat["slug"]}/">More about this report</a></div></div></div>
<div class="kicker" id="reports">All reports</div><div class="grid">{"".join(card2(i) for i in items if i["kind"]=="report")}</div>
{packets}
<div class="kicker" id="about">About the write-ups</div>
<div class="about"><p style="margin-top:0">Everything here comes from the FBI's own NORJAK file as released on the <a href="https://vault.fbi.gov/D-B-Cooper%20">FBI Vault</a>, plus clearly marked outside sources. A citation like <code>110 / 267 / 566</code> means Vault Part 110, PDF page 267, Bates stamp DB Cooper-566, so you can open the page and read it yourself.</p>
<p style="margin-bottom:0">Each report comes with its sources: the Oscillations report has a companion PDF reproducing every FBI page it cites, with a header on each page naming the sections that use it.</p></div>'''
os.makedirs(os.path.join(ROOT,'writeups'),exist_ok=True)
nrep=sum(1 for i in items if i['kind']=='report')
body=f'''<section class="home"><div class="hero"><div class="fr"><div><img src="assets/vortex_logo.jpg" alt="Thoughts in the Vortex"></div></div></div>
<p class="tagl">D.B. Cooper research from the FBI Vault files</p>
<nav class="tiles">
<a class="tile" href="writeups/"><span class="tk">Write-ups</span><span class="td">Long form summaries on key Cooper topics</span><span class="tg">Read →</span></a>
<a class="tile hot" href="{S["timeline"]["href"]}"><span class="tk">Timeline</span><span class="td">Flight 305 minute by minute: 246 entries from Portland to Reno, each beside the FBI page it comes from</span><span class="tg">Open the wheel →</span></a>
<a class="tile" href="downloads/"><span class="tk">FBI Files</span><span class="td">All 44,238 pages of the FBI's Cooper file as searchable OCR text, with links to every scan</span><span class="tg">Download →</span></a>
</nav></section>'''
os.makedirs(os.path.join(ROOT,'assets'),exist_ok=True)
open(os.path.join(ROOT,'assets','site.css'),'w').write(CSS)
open(os.path.join(ROOT,'index.html'),'w',encoding='utf-8').write(page(S['site_title']+' · D.B. Cooper research', S['tagline'], body, 0, 'assets/vortex_logo.jpg'))
open(os.path.join(ROOT,'writeups','index.html'),'w',encoding='utf-8').write(page('Write-ups · Thoughts in the Vortex', S['intro'], wbody, 1, 'assets/vortex_logo.jpg'))

for it in items:
    pts=''.join(f'<li><b>{E(a)}.</b> {E(b)}</li>' for a,b in it.get('points',[]))
    btn=''.join(f'<a class="btn{" alt" if k else ""}" href="{rd(f, it["title"] if k==0 else it["title"]+" · "+lbl.split(" (")[0], "../../")}">{E(lbl)}</a>' for k,(lbl,f) in enumerate(it['files']))
    dls=' · '.join(f'<a href="../../files/{f}" download>{E(lbl.split(" (")[0].replace("Read the report","the report"))}</a>' for lbl,f in it['files'])
    lnk=''.join(f'<a class="btn alt" href="{E(u)}">{E(l)}</a>' for l,u in it.get('links',[]))
    b=f'''<div class="crumb"><a href="../../">Home</a> › <a href="../../writeups/">Write-ups</a></div>
<div class="rp">{tcard(it, rd(it["files"][0][1], it["title"], "../../"))}<div>
<div class="meta">{"Report" if it["kind"]=="report" else "Source packet"} · {E(it["date"])}</div><h1>{E(it["title"])}</h1><p class="sub">{E(it["subtitle"])}</p>
<p>{E(it["summary"])}</p>{f"<h3>Key findings</h3><ul>{pts}</ul>" if pts else ""}<div class="btns">{btn}{lnk}</div>
<p class="meta" style="margin-top:18px">Download the PDF: {dls}.<br>Citations read Vault part / PDF page / Bates number; every FBI page is in the <a href="https://vault.fbi.gov/D-B-Cooper%20">FBI Vault</a>.</p></div></div>'''
    d=os.path.join(ROOT,'r',it['slug']); os.makedirs(d,exist_ok=True)
    open(os.path.join(d,'index.html'),'w',encoding='utf-8').write(page(f'{it["title"]} · Thoughts in the Vortex', it['summary'][:200], b, 2, 'assets/covers/'+it['cover']))
rb=open(os.path.join(ROOT,'_src','reader_body.html'),encoding='utf-8').read()
os.makedirs(os.path.join(ROOT,'read'),exist_ok=True)
open(os.path.join(ROOT,'read','index.html'),'w',encoding='utf-8').write(page('Reader · Thoughts in the Vortex','Read Thoughts in the Vortex reports in your browser.',rb,1))
tlp=os.path.join(ROOT,'timeline','index.html'); t=open(tlp,encoding='utf-8').read()
import re as _re
t=_re.sub(r'<!--tv-bar-->.*?<!--/tv-bar-->','',t,flags=_re.S)
bar='<!--tv-bar--><div style="background:#2f4a4c;padding:9px 16px;font:600 13.5px Poppins,Arial,sans-serif;letter-spacing:.4px;display:flex;flex-wrap:wrap;gap:6px 18px;align-items:center"><a href="../" style="color:#f2ead3;text-decoration:none">THOUGHTS IN THE VORTEX</a><span style="flex:1"></span><a href="../writeups/" style="color:#dfe8e5;text-decoration:none;font-weight:500">Write-ups</a><a href="../timeline/" style="color:#fff;text-decoration:none;font-weight:500">Timeline</a><a href="../downloads/" style="color:#dfe8e5;text-decoration:none;font-weight:500">FBI Files</a></div><!--/tv-bar-->'
t=_re.sub(r'(<body[^>]*>)',lambda m:m.group(1)+bar,t,count=1)
open(tlp,'w',encoding='utf-8').write(t)
PARTS=json.load(open(os.path.join(ROOT,'_src','parts.json')))
rows=''.join(f'<tr><td>Part {p}</td><td>{n:,}</td><td><a href="{E(u)}">Scans on the FBI Vault ↗</a></td></tr>' for p,u,n in PARTS)
total=sum(n for _,_,n in PARTS)
dl=f'''<div class="crumb"><a href="../">Home</a> › FBI Files</div>
<h1>The FBI files, searchable</h1><p class="sub">All {len(PARTS)} Vault parts, {total:,} pages, as OCR text</p>
<p class="lede">The FBI Vault's D.B. Cooper release is a set of scanned PDFs whose built-in text is unusable. Every page was re-read with OCR (Tesseract, 300 dpi). Two downloads hold the result; the scans themselves stay on the FBI Vault, linked below.</p>
<div class="grid" style="grid-template-columns:repeat(auto-fill,minmax(300px,1fr))">
<div class="card"><div class="meta">ZIP · 18 MB · {len(PARTS)} text files</div><h3>OCR text pack</h3><p>One plain-text file per Vault part. Every page starts with a header line, <code>==== Part 64 · PDF page 304 · Bates DB Cooper-27170 ====</code>, so any search hit tells you exactly which page to open. Search it with any editor that searches across files, or with grep.</p><div class="btns"><a class="btn" href="norjak-fbi-ocr-text.zip">Download the OCR text</a></div></div>
<div class="card"><div class="meta">ZIP · 37 MB · SQLite</div><h3>Searchable database</h3><p>The same text in a SQLite database with a full-text index, plus a small Python search tool for phrases, words near each other and sound-alike matches, e.g. <code>python3 search.py '"Tena Bar"'</code>. No extra packages needed.</p><div class="btns"><a class="btn alt" href="norjak-fbi-database.zip">Download the database</a></div></div></div>
<h3>Before you quote anything</h3><ul>
<li>OCR is imperfect. Much of the file is 1970s teletypes, carbons and handwriting, and photos and clippings often come through poorly. A search that finds nothing doesn't prove the file is silent; try spelling variants.</li>
<li>"PDF page" is the page number in the Vault's PDF viewer. The Bates number is the FBI's stamp in the bottom-right corner. It was read by OCR, so it is missing on some pages and occasionally off by a digit.</li>
<li>Names the FBI redacted appear as blanks or exemption codes (b6, b7C).</li>
<li>Always check the scan on the FBI Vault before quoting.</li></ul>
<h3>The {len(PARTS)} parts</h3><table style="width:100%;border-collapse:collapse;font-size:15px;margin:6px 0 30px"><tr style="text-align:left;border-bottom:1.5px solid var(--teal)"><th>Part</th><th>Pages</th><th>Scans</th></tr>{rows}</table>'''
dl=dl.replace('<tr><td>','<tr style="border-bottom:1px solid var(--line)"><td>')
open(os.path.join(ROOT,'downloads','index.html'),'w',encoding='utf-8').write(page('The FBI files, searchable · Thoughts in the Vortex', 'OCR text of all 44,238 pages of the FBI Vault D.B. Cooper file, labeled by Part, PDF page and Bates number.', dl, 1))
open(os.path.join(ROOT,'404.html'),'w',encoding='utf-8').write(page('Not found · Thoughts in the Vortex','Page not found','<h1 style="margin-top:40px">Lost in the vortex</h1><p>That page isn\'t here. <a href="/">Back to the home page</a>.</p>',0).replace('href="assets/','href="/assets/').replace('href="#','href="/#').replace('href="timeline/','href="/timeline/').replace('href="./"','href="/"'))
print('built', len(items), 'item pages')
