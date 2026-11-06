#!/usr/bin/env python3
"""Build thoughtsinthevortex.com from _src/site.json.
Run from the repo root: python3 _src/build.py
Writes index.html, writeups/index.html, r/<slug>/index.html, foia/index.html, downloads/index.html, feedback/index.html, 404.html.
PDFs live in files/, cover thumbnails in assets/covers/.
"""
import json, html, os, re as _re
from urllib.parse import quote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = json.load(open(os.path.join(ROOT, '_src', 'site.json'), encoding='utf-8'))
E = lambda x: html.escape(str(x), quote=True)

CSS = '''
:root{--bg:#fbf7ee;--paper:#fffdf7;--ink:#211d1c;--muted:#5d6b69;--teal:#2f4a4c;--teal2:#466567;--line:#d8d0bb;--gold:#c47f0e;--blue:#2b6cb0;--red:#a82828;--green:#2f6b3a}
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
.tiles{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;max-width:1040px;margin:0 auto}
.tile{display:flex;flex-direction:column;gap:8px;background:var(--teal);color:#f2ead3;text-decoration:none;border-radius:6px;padding:20px 18px 16px;border:2px solid var(--teal);transition:transform .12s,border-color .12s}
.tile:hover{transform:translateY(-2px);border-color:var(--gold);color:#fff}
.tile .tk{font-family:"Poppins",sans-serif;font-weight:600;font-size:22px;color:#fff;letter-spacing:-.3px}
.tile .td{font-size:14px;line-height:1.45;color:#dfe8e5;flex:1}.tile .tg{font-family:"Poppins",sans-serif;font-weight:600;font-size:13.5px;color:#f4c86a}
.tile.hot{background:var(--gold);border-color:var(--gold)}.tile.hot .td{color:#fff6e0}.tile.hot .tg{color:#fff}.tile.hot:hover{border-color:var(--teal)}
.fbnote{text-align:center;font-size:15px;color:var(--muted);margin:22px auto 0;max-width:880px}
.notice{background:var(--paper);border:1px solid var(--line);border-left:4px solid var(--gold);border-radius:6px;padding:14px 18px;margin:14px 0 6px;font-size:15.5px;max-width:880px}.notice p{margin:0}.notice p+p{margin-top:8px}
.fbgrid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px;margin:8px 0 34px}
.fbox{background:var(--paper);border:1px solid var(--line);border-radius:6px;padding:20px 20px 18px;scroll-margin-top:16px}.fbox h2{margin:0 0 4px;font-size:21px}.fbox>p{margin:0 0 14px;font-size:15px;color:#4a4644}
.fbox label{display:block;font-family:"Poppins",sans-serif;font-size:13px;font-weight:600;color:var(--teal);margin:12px 0 5px}
.fbox select,.fbox textarea,.akey input{width:100%;font:16px/1.5 "Lora",Georgia,serif;color:var(--ink);background:#fff;border:1.5px solid var(--line);border-radius:5px;padding:9px 11px}
.fbox textarea{min-height:170px;resize:vertical}.fbox select:focus,.fbox textarea:focus,.akey input:focus{outline:none;border-color:var(--teal)}
.fbox .row{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-top:12px;flex-wrap:wrap}.fbox .cnt{font-family:"Poppins",sans-serif;font-size:12px;color:var(--muted)}
.fbox button,.akey button,.arow button{font-family:"Poppins",sans-serif;font-size:14px;font-weight:500;background:var(--teal);color:#fff;border:0;padding:10px 16px;border-radius:5px;cursor:pointer}
.fbox button:hover,.akey button:hover{background:var(--gold)}.fbox button:disabled{opacity:.6;cursor:default}
.hp{position:absolute;left:-9999px;width:1px;height:1px;overflow:hidden}
.fmsg{font-family:"Poppins",sans-serif;font-size:13.5px;margin-top:10px;min-height:1.4em}.fmsg.ok{color:#2f6b3a}.fmsg.err{color:var(--red)}
.akey{display:flex;gap:10px;flex-wrap:wrap;margin:10px 0}.akey input{flex:1;min-width:220px}.akey button.alt,.arow button.alt{background:transparent;color:var(--teal);border:1.5px solid var(--teal)}
.afil{display:flex;gap:8px;flex-wrap:wrap;align-items:center;font-family:"Poppins",sans-serif;font-size:13.5px;margin:10px 0}.afil select{font:14px "Poppins",sans-serif;padding:6px 8px;border:1.5px solid var(--line);border-radius:5px;background:#fff}
.aitem{background:var(--paper);border:1px solid var(--line);border-radius:6px;padding:14px 16px;margin:10px 0}.aitem.read{opacity:.75}.aitem.archived{opacity:.5}
.aitem .meta b{color:var(--teal)}.aitem .msg{white-space:pre-wrap;margin:8px 0 10px;overflow-wrap:anywhere}.arow{display:flex;gap:8px;flex-wrap:wrap}.arow button{font-size:12.5px;padding:6px 10px}

/* FOIA Tracker styles */
.foia-stats{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:18px 0 22px}
.fstat{background:var(--paper);border:1px solid var(--line);border-top:3.5px solid var(--teal);border-radius:6px;padding:14px 16px}
.fstat.gold{border-top-color:var(--gold)}.fstat.blue{border-top-color:var(--blue)}.fstat.green{border-top-color:var(--green)}.fstat.red{border-top-color:var(--red)}
.fstat .num{font-family:"Poppins",sans-serif;font-size:28px;font-weight:600;color:var(--teal);line-height:1.1}
.fstat.gold .num{color:var(--gold)}.fstat.blue .num{color:var(--blue)}.fstat.green .num{color:var(--green)}.fstat.red .num{color:var(--red)}
.fstat .lbl{font-family:"Poppins",sans-serif;font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:.8px;color:var(--muted);margin-top:4px}
.fstat .subl{font-size:13px;color:var(--muted);margin-top:2px}
.foia-bar{display:flex;flex-wrap:wrap;gap:10px;align-items:center;justify-content:space-between;background:var(--paper);border:1px solid var(--line);border-radius:6px;padding:12px 14px;margin:12px 0 16px;font-family:"Poppins",sans-serif;font-size:13px}
.foia-pills{display:flex;flex-wrap:wrap;gap:6px}
.fpill{font-family:"Poppins",sans-serif;font-size:12.5px;font-weight:500;background:#efe8d3;color:var(--teal);border:1px solid transparent;border-radius:20px;padding:5px 12px;cursor:pointer;transition:all .12s}
.fpill:hover{border-color:var(--gold);color:var(--ink)}
.fpill.active{background:var(--teal);color:#fff}
.foia-ctrls{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.foia-ctrls input,.foia-ctrls select{font:13px "Poppins",sans-serif;color:var(--ink);background:#fff;border:1.5px solid var(--line);border-radius:5px;padding:6px 10px}
.foia-ctrls input{min-width:210px}
.foia-ctrls input:focus,.foia-ctrls select:focus{outline:none;border-color:var(--teal)}
.foia-ctrls button{font:500 12.5px "Poppins",sans-serif;background:transparent;color:var(--teal);border:1.5px solid var(--teal);border-radius:5px;padding:6px 11px;cursor:pointer}
.foia-ctrls button:hover{border-color:var(--gold);color:var(--gold)}
.foia-list{display:flex;flex-direction:column;gap:14px;margin:10px 0 28px}
.fcard{background:var(--paper);border:1px solid var(--line);border-radius:6px;overflow:hidden;transition:border-color .15s}
.fcard:hover{border-color:#b8ad93}
.fcard.open{border-color:var(--teal2);box-shadow:0 2px 10px rgba(47,74,76,.07)}
.fhead{display:grid;grid-template-columns:1fr 195px;gap:20px;padding:18px 20px;cursor:pointer;align-items:center}
.fbadges{display:flex;flex-wrap:wrap;gap:7px;align-items:center;margin-bottom:7px;font-family:"Poppins",sans-serif;font-size:11.5px}
.fbadge{display:inline-flex;align-items:center;gap:5px;font-weight:600;padding:3px 9px;border-radius:4px;letter-spacing:.3px;text-transform:uppercase;font-size:11px}
.fbadge.gold{background:#fef3c7;color:#92400e;border:1px solid #f59e0b}
.fbadge.blue{background:#dbeafe;color:#1e40af;border:1px solid #93c5fd}
.fbadge.green{background:#dcfce7;color:#166534;border:1px solid #86efac}
.fbadge.red{background:#fee2e2;color:#991b1b;border:1px solid #fca5a5}
.fbadge.teal{background:#e6efee;color:var(--teal);border:1px solid #9fb6b2;text-transform:none;font-weight:500;font-size:11.5px}
.fhead h3{margin:0 0 5px;font-size:18px;line-height:1.3;color:var(--teal)}
.fhead .ftarget{font-family:"Poppins",sans-serif;font-size:12.5px;color:var(--muted)}
.fhead .fwhy-preview{margin:8px 0 0;font-size:14.5px;color:#4a4644;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.fcard.open .fhead .fwhy-preview{display:none}
.ftoggle{font-family:"Poppins",sans-serif;font-size:12.5px;font-weight:600;color:var(--teal);margin-top:9px;display:inline-flex;align-items:center;gap:5px}
.fcard:hover .ftoggle{color:var(--gold)}
.fclock{background:var(--bg);border:1.5px solid var(--line);border-radius:6px;padding:12px 14px;text-align:center;display:flex;flex-direction:column;justify-content:center;gap:2px}
.fclock .days-num{font-family:"Poppins",sans-serif;font-size:28px;font-weight:600;color:var(--teal);line-height:1.05}
.fclock.warn .days-num{color:var(--gold)}
.fclock.overdue .days-num{color:var(--red)}
.fclock.done .days-num{color:var(--green)}.fclock.denied .days-num{color:var(--red)}
.fclock .days-lbl{font-family:"Poppins",sans-serif;font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.7px;color:var(--muted)}
.fclock .days-sub{font-family:"Poppins",sans-serif;font-size:11.5px;color:var(--muted);margin-top:3px}
.fclock .bar-wrap{height:5px;background:#e2dac7;border-radius:3px;overflow:hidden;margin-top:6px}
.fclock .bar-fill{height:100%;background:var(--teal);border-radius:3px;transition:width .3s}
.fclock.warn .bar-fill{background:var(--gold)}
.fclock.overdue .bar-fill{background:var(--red)}
.fclock.done .bar-fill{background:var(--green)}.fclock.denied .bar-fill{background:var(--red)}
.fbody{display:none;border-top:1px solid var(--line);background:#fdfbf5;padding:18px 20px 20px}
.fcard.open .fbody{display:block}
.fbody-grid{display:grid;grid-template-columns:1fr 1fr;gap:22px;margin-bottom:14px}
.fbody h4{font-family:"Poppins",sans-serif;font-size:12px;text-transform:uppercase;letter-spacing:1.2px;color:var(--teal2);margin:0 0 6px}
.fbody p{margin:0 0 10px;font-size:15px;line-height:1.55}
.fbody ol,.fbody ul{margin:0;padding-left:20px;font-size:14.5px;line-height:1.55}
.fbody li{margin-bottom:6px}
.foutcome{background:var(--paper);border:1px solid var(--line);border-left:3.5px solid var(--gold);border-radius:5px;padding:11px 14px;margin-top:12px;font-size:14.5px}.foutcome.blue{border-left-color:var(--blue)}.foutcome.red{border-left-color:var(--red)}.foutcome.green{border-left-color:var(--green)}
.foutcome b{font-family:"Poppins",sans-serif;font-size:12.5px;color:var(--teal);text-transform:uppercase;letter-spacing:.5px;display:block;margin-bottom:2px}
.fmeta-foot{display:flex;flex-wrap:wrap;gap:12px 20px;align-items:center;justify-content:space-between;margin-top:14px;padding-top:12px;border-top:1px dashed var(--line);font-family:"Poppins",sans-serif;font-size:12.5px;color:var(--muted)}
.foia-empty{text-align:center;padding:36px 20px;background:var(--paper);border:1px dashed var(--line);border-radius:6px;color:var(--muted);font-family:"Poppins",sans-serif;display:none}
@media (max-width:860px){.tiles{grid-template-columns:repeat(2,1fr)}.foia-stats{grid-template-columns:repeat(2,1fr)}.fhead{grid-template-columns:1fr}.fclock{flex-direction:row;align-items:baseline;justify-content:space-between;text-align:left;padding:10px 14px;gap:10px}.fclock .bar-wrap{display:none}.fbody-grid{grid-template-columns:1fr}}
@media (max-width:760px){.fbgrid{grid-template-columns:1fr}}
@media (max-width:600px){.tiles{grid-template-columns:1fr}.foia-stats{grid-template-columns:1fr}.home .hero{padding-top:18px}header.top .wrap{flex-wrap:wrap;gap:4px 16px}.brand{white-space:nowrap;font-size:15px}nav a:first-child{margin-left:0}.feature,.rp{grid-template-columns:1fr}.feature .tcard,.rp .tcard{max-width:340px}.chips{grid-template-columns:1fr}nav a{margin-left:12px;font-size:13px}.tl{flex-direction:column;align-items:flex-start}.tl .go{margin-left:0}}
'''
FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,600;1,400&family=Poppins:wght@500;600&display=swap">'

def page(title, desc, body, depth=0, og_img=None):
  up = '../' * depth
  og = f'<meta property="og:image" content="https://{S["domain"]}/{og_img}">' if og_img else ''
  return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title><meta name="description" content="{E(desc)}">
<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}"><meta property="og:type" content="website">{og}
<link rel="icon" href="{up}assets/vortex_logo.jpg">{FONTS}<link rel="stylesheet" href="{up}assets/site.css"></head><body>
<header class="top"><div class="wrap"><a class="brand" href="{up or './'}">THOUGHTS IN THE VORTEX</a><nav><a href="{up}writeups/">Write-ups</a><a href="{up}timeline/">Timeline</a><a href="{up}downloads/">FBI Files</a><a href="{up}foia/">FOIA</a><a href="{up}feedback/">Feedback</a></nav></div></header>
<main class="wrap">{body}</main>
<footer><div class="wrap">Thoughts in the Vortex · Research on NORJAK / Northwest Orient Flight 305 from the <a href="https://vault.fbi.gov/D-B-Cooper%20">FBI Vault D.B. Cooper files</a>. Citations read Vault part / PDF page / Bates number.</div></footer>
</body></html>'''

def rd(f, title, up=''):
  return f'{up}read/?f={quote(f)}&t={quote(title)}'

def tcard(it, href=None, cls='tcard'):
  ch = ''.join(f'<div class="ch {c}"><b>{E(a)}</b>{E(b)}</div>' for a, b, c in it.get('chips', []))
  tag = 'a' if href else 'div'
  h = f' href="{href}"' if href else ''
  return f'<{tag} class="{cls}"{h}><div class="in"><div class="ser">{E(it.get("series",""))}</div><div class="tt">{E(it["title"])}</div><div class="st">{E(it["subtitle"])}</div>{ch}</div></{tag}>'

def card(it):
  return f'''<a class="card" href="r/{it["slug"]}/">{tcard(it)}<div class="meta">{"Report" if it["kind"]=="report" else "Source packet"} · {E(it["date"])}</div></a>'''

items = S['items']
feat = next(i for i in items if i.get('featured'))
chips = ''.join(f'<div class="chip"><b>{E(a)}</b>{E(b)}</div>' for a, b in feat.get('points', []))
U = '../'
fbtn = ''.join(f'<a class="btn{" alt" if k else ""}" href="{rd(f, feat["title"] if k==0 else feat["title"]+" · Companion", U)}">{E(lbl)}</a>' for k, (lbl, f) in enumerate(feat['files']))
def card2(it): return card(it).replace('href="r/', 'href="../r/')
packets = (f'<div class="kicker" id="packets">Source packets: the FBI pages, highlighted</div><div class="grid">' + ''.join(card2(i) for i in items if i['kind'] == 'packet') + '</div>') if any(i['kind'] == 'packet' for i in items) else ''
wbody = f'''<div class="crumb"><a href="../">Home</a> › Write-ups</div>
<h1>Write-ups</h1><p class="lede">{E(S["intro"])}</p>
<div class="kicker">Latest report</div>
<div class="feature">{tcard(feat, "../r/"+feat["slug"]+"/") }<div>
<div class="meta">Report · {E(feat["date"])}</div><h2 style="margin:4px 0 2px;font-size:26px"><a href="../r/{feat["slug"]}/" style="text-decoration:none">{E(feat["title"])}</a></h2><p class="sub">{E(feat["subtitle"])}</p>
<p>{E(feat["summary"])}</p><div class="btns">{fbtn}<a class="btn alt" href="../r/{feat["slug"]}/">More about this report</a></div></div></div>
<div class="kicker" id="reports">All reports</div><div class="grid">{"".join(card2(i) for i in items if i["kind"]=="report")}</div>
{packets}
<div class="kicker" id="about">About the write-ups</div>
<div class="about"><p style="margin-top:0">Everything here comes from the FBI's own NORJAK file as released on the <a href="https://vault.fbi.gov/D-B-Cooper%20">FBI Vault</a>, plus clearly marked outside sources. A citation like <code>110 / 267 / 566</code> means Vault Part 110, PDF page 267, Bates stamp DB Cooper-566, so you can open the page and read it yourself.</p>
<p style="margin-bottom:0">Each report comes with its sources: the Elsinore Ghost and Oscillations reports have companion PDFs reproducing every FBI page they cite, each page labeled with its Part, PDF page and Bates number.</p></div>'''

os.makedirs(os.path.join(ROOT, 'writeups'), exist_ok=True)
nfoia = len(S.get('foia', {}).get('requests', []))
body = f'''<section class="home"><div class="hero"><div class="fr"><div><img src="assets/vortex_logo.jpg" alt="Thoughts in the Vortex"></div></div></div>
<p class="tagl">D.B. Cooper research from the FBI Vault files</p>
<nav class="tiles">
<a class="tile" href="writeups/"><span class="tk">Write-ups</span><span class="td">Long form summaries on key Cooper topics</span><span class="tg">Read →</span></a>
<a class="tile hot" href="{S["timeline"]["href"]}"><span class="tk">Timeline</span><span class="td">Flight 305 minute by minute: 246 entries from Portland to Reno, each beside the FBI page it comes from</span><span class="tg">Open the wheel →</span></a>
<a class="tile" href="downloads/"><span class="tk">FBI Files</span><span class="td">All 44,238 pages of the FBI's Cooper file as searchable OCR text, with links to every scan</span><span class="tg">Download →</span></a>
<a class="tile" href="foia/"><span class="tk">FOIA Tracker</span><span class="td">{nfoia} FOIA requests hunting missing serials, DNA bench notes, radio tapes, and unredacted files, with live daily wait counters</span><span class="tg">Track requests →</span></a>
</nav>
<p class="fbnote">Thoughts on a write-up, or a topic you'd like covered next? <a href="feedback/">Leave feedback or a suggestion →</a></p></section>'''

os.makedirs(os.path.join(ROOT, 'assets'), exist_ok=True)
open(os.path.join(ROOT, 'assets', 'site.css'), 'w', encoding='utf-8').write(CSS)
open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8').write(page(S['site_title'] + ' · D.B. Cooper research', S['tagline'], body, 0, 'assets/vortex_logo.jpg'))
open(os.path.join(ROOT, 'writeups', 'index.html'), 'w', encoding='utf-8').write(page('Write-ups · Thoughts in the Vortex', S['intro'], wbody, 1, 'assets/vortex_logo.jpg'))

for it in items:
  pts = ''.join(f'<li><b>{E(a)}.</b> {E(b)}</li>' for a, b in it.get('points', []))
  btn = ''.join(f'<a class="btn{" alt" if k else ""}" href="{rd(f, it["title"] if k==0 else it["title"]+" · "+lbl.split(" (")[0], "../../")}">{E(lbl)}</a>' for k, (lbl, f) in enumerate(it['files']))
  dls = ' · '.join(f'<a href="../../files/{f}" download>{E(lbl.split(" (")[0].replace("Read the report","the report"))}</a>' for lbl, f in it['files'])
  lnk = ''.join(f'<a class="btn alt" href="{E(u)}">{E(l)}</a>' for l, u in it.get('links', []))
  lnk += f'<a class="btn alt" href="../../feedback/?w={quote(it["slug"])}">Leave feedback on this report</a>'
  b = f'''<div class="crumb"><a href="../../">Home</a> › <a href="../../writeups/">Write-ups</a></div>
<div class="rp">{tcard(it, rd(it["files"][0][1], it["title"], "../../"))}<div>
<div class="meta">{"Report" if it["kind"]=="report" else "Source packet"} · {E(it["date"])}</div><h1>{E(it["title"])}</h1><p class="sub">{E(it["subtitle"])}</p>
<p>{E(it["summary"])}</p>{f"<h3>Key findings</h3><ul>{pts}</ul>" if pts else ""}<div class="btns">{btn}{lnk}</div>
<p class="meta" style="margin-top:18px">Download the PDF: {dls}.<br>Citations read Vault part / PDF page / Bates number; every FBI page is in the <a href="https://vault.fbi.gov/D-B-Cooper%20">FBI Vault</a>.</p></div></div>'''
  d = os.path.join(ROOT, 'r', it['slug'])
  os.makedirs(d, exist_ok=True)
  open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(page(f'{it["title"]} · Thoughts in the Vortex', it['summary'][:200], b, 2, 'assets/covers/' + it['cover']))

# Build /foia/index.html if foia section exists in site.json
if 'foia' in S:
  foia_cfg = S['foia']
  reqs = foia_cfg.get('requests', [])
  live_slugs = {i['slug'] for i in items}
  cards_html = []
  for r in reqs:
    req_items_html = ''.join(f'<li>{E(x)}</li>' for x in r.get('requested_items', []))
    rslug = r.get('related_slug', '')
    rtitle = r.get('related_title', '')
    if rslug and rslug in live_slugs:
      rel_link = f'<a class="fbadge teal" href="../r/{E(rslug)}/" onclick="event.stopPropagation()">Report: {E(rtitle)} ↗</a>'
      foot_rel = f'<a href="../r/{E(rslug)}/">Read {E(rtitle)} →</a> · '
    elif rtitle:
      rel_link = f'<span class="fbadge teal">Series: {E(rtitle)} (Forthcoming)</span>'
      foot_rel = f'<span>Series: {E(rtitle)} (Forthcoming)</span> · '
    else:
      rel_link = ''
      foot_rel = ''
    tone = r.get('status_tone', 'gold')
    ref_tag = f'<span class="fbadge teal" style="font-weight:600">{E(r["ref"])}</span>' if r.get('ref') else ''
    appeal_str = r.get('appeal_deadline', '')
    appeal_meta = f' · <b>OIP Appeal Deadline:</b> {E(appeal_str)}' if appeal_str else ''
    cards_html.append(f'''<article class="fcard" id="{E(r["id"])}" data-filed="{E(r["filed_date"])}" data-closed="{E(r.get("closed_date",""))}" data-appeal="{E(appeal_str)}" data-tone="{E(tone)}" data-slug="{E(rslug)}" data-track="{E(r.get("track",""))}" data-status="{E(r.get("status",""))}" data-title="{E(r["title"])}">
  <div class="fhead" role="button" tabindex="0" aria-expanded="false" onclick="toggleFoiaCard('{E(r["id"])}')" onkeydown="if(event.key==='Enter'||event.key===' '){{event.preventDefault();toggleFoiaCard('{E(r["id"])}');}}">
    <div>
      <div class="fbadges">
        {ref_tag}
        <span class="fbadge {E(tone)}">{E(r["status"])}</span>
        <span class="fbadge blue">{E(r["agency"])} · {E(r.get("track",""))}</span>
        {rel_link}
      </div>
      <h3>{E(r["title"])}</h3>
      <div class="ftarget"><b>Target File:</b> <code>{E(r["target_file"])}</code> · <b>Case #:</b> <b>{E(r.get("case_no","Pending"))}</b></div>
      <p class="fwhy-preview">{E(r["why"])}</p>
      <div class="ftoggle"><span class="ftoggle-lbl">Why we filed &amp; exact records requested ↓</span></div>
    </div>
    <div class="fclock" data-clock-for="{E(r["id"])}">
      <div>
        <div class="days-num" data-days-num>—</div>
        <div class="days-lbl" data-days-lbl>Days Since Submission</div>
      </div>
      <div>
        <div class="days-sub" data-days-sub>Filed {E(r["filed_date"])}</div>
        <div class="bar-wrap" title="Progress against 20-business-day statutory FOIA response window"><div class="bar-fill" data-days-bar style="width:0%"></div></div>
      </div>
    </div>
  </div>
  <div class="fbody">
    <div class="fbody-grid">
      <div>
        <h4>Why This Request Was Filed</h4>
        <p>{E(r["why"])}</p>
        <div class="foutcome {E(tone)}">
          <b>Current Status &amp; Latest FBI Response ({E(r.get("updated_date", r["filed_date"]))})</b>
          {E(r["outcome"])}
        </div>
      </div>
      <div>
        <h4>Exact Records &amp; Serials Requested</h4>
        <ol>{req_items_html}</ol>
      </div>
    </div>
    <div class="fmeta-foot">
      <span><b>Date Submitted:</b> {E(r["filed_date"])} · <b>Last Updated:</b> {E(r.get("updated_date", r["filed_date"]))}{appeal_meta} · <b>Queue:</b> {E(r.get("track",""))}</span>
      <span>{foot_rel}<a href="../feedback/?w=foia">Have a tip on these records? →</a></span>
    </div>
  </div>
</article>''')

  n_total = len(reqs)
  n_active = sum(1 for r in reqs if not r.get("closed_date"))
  n_ack = sum(1 for r in reqs if r.get("status_tone") == "blue" and not r.get("closed_date"))
  n_intake = sum(1 for r in reqs if r.get("status_tone") == "gold" and not r.get("closed_date"))
  n_denied = sum(1 for r in reqs if r.get("status_tone") == "red")
  n_released = sum(1 for r in reqs if r.get("closed_date") and r.get("status_tone") != "red")

  foia_body = f'''<div class="crumb"><a href="../">Home</a> › FOIA Tracker</div>
<h1>FOIA Tracker</h1>
<p class="sub">Primary-source requests for unreleased NORJAK serials, lab bench notes, physical exhibits, and unredacted files</p>
<p class="lede">{E(foia_cfg.get("intro",""))}</p>

<div class="foia-stats">
  <div class="fstat">
    <div class="num" id="stat-total">{n_total}</div>
    <div class="lbl">Requests Filed</div>
    <div class="subl">{n_ack} acknowledged · {n_intake} awaiting intake · {n_denied} denied</div>
  </div>
  <div class="fstat gold">
    <div class="num" id="stat-pending">{n_active}</div>
    <div class="lbl">Active in FBI Queue</div>
    <div class="subl">{n_ack} in RIDS processing · {n_intake} awaiting FOIPA #</div>
  </div>
  <div class="fstat blue">
    <div class="num" id="stat-max-days">—</div>
    <div class="lbl">Longest Active Wait</div>
    <div class="subl" id="stat-avg-days">Calculated live each day</div>
  </div>
  <div class="fstat {"red" if n_denied and not n_released else "green"}">
    <div class="num" id="stat-resolved">{n_denied + n_released}</div>
    <div class="lbl">{"Denied / Appeal Pending" if n_denied and not n_released else "Closed / Resolved"}</div>
    <div class="subl">{"#1763828-000 · OIP appeal due Feb 2, 2027" if n_denied else "Processed or final determination"}</div>
  </div>
</div>

<div class="foia-bar">
  <div class="foia-pills" role="group" aria-label="Filter by investigation">
    <button type="button" class="fpill active" data-filter-slug="all" onclick="setFoiaSlug('all', this)">All Requests ({n_total})</button>
    <button type="button" class="fpill" data-filter-slug="elsinore-ghost" onclick="setFoiaSlug('elsinore-ghost', this)">Elsinore Ghost ({sum(1 for r in reqs if r.get('related_slug')=='elsinore-ghost')})</button>
    <button type="button" class="fpill" data-filter-slug="splitting-hairs-slides" onclick="setFoiaSlug('splitting-hairs-slides', this)">Splitting Hair(s) Slides / DNA ({sum(1 for r in reqs if r.get('related_slug')=='splitting-hairs-slides')})</button>
    <button type="button" class="fpill" data-filter-slug="oscillations" onclick="setFoiaSlug('oscillations', this)">Oscillations / Flight 305 Tape ({sum(1 for r in reqs if r.get('related_slug')=='oscillations')})</button>
  </div>
  <div class="foia-ctrls">
    <input type="search" id="foia-q" placeholder="Search FOIPA #, Bates, name…" aria-label="Search FOIA requests" oninput="filterFoia()">
    <select id="foia-sort" aria-label="Sort requests" onchange="sortFoia()">
      <option value="wait-desc">Sort: Longest wait first</option>
      <option value="date-desc">Sort: Newest filed first</option>
      <option value="status-asc">Sort: Acknowledged / Status first</option>
      <option value="title-asc">Sort: Title (A–Z)</option>
    </select>
    <button type="button" id="foia-exp-btn" onclick="toggleAllFoia()">Expand all</button>
  </div>
</div>

<div class="foia-list" id="foia-list">
{''.join(cards_html)}
</div>
<div class="foia-empty" id="foia-empty">No FOIA requests match that filter or search query.</div>

<div class="kicker" id="about-foia">How the FOIA clock &amp; privacy waivers work</div>
<div class="about">
  <p style="margin-top:0"><b>Live "Days Since Submission" Counter:</b> Under the Freedom of Information Act (<code>5 U.S.C. § 552(a)(6)(A)(i)</code>), federal agencies have <b>20 business days</b> (roughly 28 calendar days, excluding weekends and federal holidays) to make an initial determination on a request. Each card above calculates the exact elapsed calendar days and estimated business days in your browser every day until a final determination is logged.</p>
  <p><b>Why Requests Are Split by Track:</b> The FBI's Record/Information Dissemination Section (RIDS) routes requests by page volume and subject type. Narrow paper requests under 50 pages qualify for the <b>Small Track</b> queue, whereas requests for physical evidence envelopes (such as Bulky Exhibit <code>LA 164-497-1B1</code>) or Laboratory bench-note packets (<code>SE 164A-81-1D890</code>) require a manual Evidence Control Center or case-file pull. Deceased-individual requests attach official proof of death or birth records over 100 years old so RIDS analysts can lift Exemption <code>(b)(6)</code> and <code>(b)(7)(C)</code> personal-privacy redactions.</p>
  <p style="margin-bottom:0">Spot an unreleased serial citation in the Vault that should be requested next? <a href="../feedback/?w=foia">Send a suggestion →</a></p>
</div>

<script>
(function(){{
  var activeSlug = 'all';
  var allOpen = false;

  function parseLocalDate(str) {{
    if (!str) return null;
    var p = str.split('-');
    return new Date(parseInt(p[0],10), parseInt(p[1],10)-1, parseInt(p[2],10));
  }}

  function countBusinessDays(d1, d2) {{
    if (!d1 || !d2 || d2 < d1) return 0;
    var cnt = 0, cur = new Date(d1.getTime());
    cur.setDate(cur.getDate() + 1);
    while (cur <= d2) {{
      var day = cur.getDay();
      if (day !== 0 && day !== 6) cnt++;
      cur.setDate(cur.getDate() + 1);
    }}
    return cnt;
  }}

  function fmtDateShort(str) {{
    var d = parseLocalDate(str);
    if (!d) return str;
    var m = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][d.getMonth()];
    return m + ' ' + d.getDate() + ', ' + d.getFullYear();
  }}

  function updateClocks() {{
    var now = new Date();
    var today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    var cards = document.querySelectorAll('.fcard');
    var maxActiveDays = 0, sumActiveDays = 0, activeCount = 0;

    cards.forEach(function(card) {{
      var filedStr = card.getAttribute('data-filed');
      var closedStr = card.getAttribute('data-closed');
      var appealStr = card.getAttribute('data-appeal');
      var tone = card.getAttribute('data-tone');
      var filed = parseLocalDate(filedStr);
      var end = closedStr ? parseLocalDate(closedStr) : today;
      var diffDays = filed ? Math.max(0, Math.round((end - filed) / 86400000)) : 0;
      var bizDays = countBusinessDays(filed, end);
      card.setAttribute('data-days', diffDays);

      var clock = card.querySelector('.fclock');
      var numEl = card.querySelector('[data-days-num]');
      var lblEl = card.querySelector('[data-days-lbl]');
      var subEl = card.querySelector('[data-days-sub]');
      var barEl = card.querySelector('[data-days-bar]');

      if (closedStr) {{
        numEl.textContent = diffDays + (diffDays === 1 ? ' day' : ' days');
        if (tone === 'red') {{
          lblEl.textContent = 'Closed (Denied)';
          subEl.textContent = appealStr ? ('Appeal due ' + fmtDateShort(appealStr)) : ('Closed ' + fmtDateShort(closedStr));
          clock.className = 'fclock denied';
        }} else {{
          lblEl.textContent = 'Total Turnaround';
          subEl.textContent = 'Closed ' + fmtDateShort(closedStr);
          clock.className = 'fclock done';
        }}
        if (barEl) barEl.style.width = '100%';
      }} else {{
        numEl.textContent = diffDays + (diffDays === 1 ? ' day' : ' days');
        lblEl.textContent = 'Days Since Submission';
        subEl.textContent = bizDays + ' business ' + (bizDays === 1 ? 'day' : 'days') + ' · Filed ' + fmtDateShort(filedStr);
        var pct = Math.min(100, Math.round((bizDays / 20) * 100));
        if (barEl) barEl.style.width = Math.max(6, pct) + '%';
        clock.className = 'fclock' + (bizDays > 20 ? ' overdue' : (bizDays >= 15 ? ' warn' : ''));
        if (diffDays > maxActiveDays) maxActiveDays = diffDays;
        sumActiveDays += diffDays;
        activeCount++;
      }}
    }});

    var maxEl = document.getElementById('stat-max-days');
    var avgEl = document.getElementById('stat-avg-days');
    if (maxEl) maxEl.textContent = activeCount ? (maxActiveDays + (maxActiveDays === 1 ? ' day' : ' days')) : '0 days';
    if (avgEl && activeCount) {{
      var avg = (sumActiveDays / activeCount).toFixed(1).replace(/\\.0$/, '');
      avgEl.textContent = 'Avg ' + avg + ' days across ' + activeCount + ' active';
    }}
  }}

  window.toggleFoiaCard = function(id) {{
    var card = document.getElementById(id);
    if (!card) return;
    var isOpen = card.classList.toggle('open');
    var head = card.querySelector('.fhead');
    var lbl = card.querySelector('.ftoggle-lbl');
    if (head) head.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    if (lbl) lbl.textContent = isOpen ? 'Hide request details ↑' : 'Why we filed & exact records requested ↓';
  }};

  window.toggleAllFoia = function() {{
    allOpen = !allOpen;
    document.querySelectorAll('.fcard').forEach(function(card) {{
      card.classList.toggle('open', allOpen);
      var head = card.querySelector('.fhead');
      var lbl = card.querySelector('.ftoggle-lbl');
      if (head) head.setAttribute('aria-expanded', allOpen ? 'true' : 'false');
      if (lbl) lbl.textContent = allOpen ? 'Hide request details ↑' : 'Why we filed & exact records requested ↓';
    }});
    var btn = document.getElementById('foia-exp-btn');
    if (btn) btn.textContent = allOpen ? 'Collapse all' : 'Expand all';
  }};

  window.setFoiaSlug = function(slug, btn) {{
    activeSlug = slug;
    document.querySelectorAll('.fpill').forEach(function(p) {{ p.classList.remove('active'); }});
    if (btn) btn.classList.add('active');
    filterFoia();
  }};

  window.filterFoia = function() {{
    var q = (document.getElementById('foia-q').value || '').toLowerCase().trim();
    var visible = 0;
    document.querySelectorAll('.fcard').forEach(function(card) {{
      var slugMatch = (activeSlug === 'all') || (card.getAttribute('data-slug') === activeSlug);
      var textMatch = !q || card.textContent.toLowerCase().indexOf(q) !== -1;
      var show = slugMatch && textMatch;
      card.style.display = show ? '' : 'none';
      if (show) visible++;
    }});
    var emp = document.getElementById('foia-empty');
    if (emp) emp.style.display = visible === 0 ? 'block' : 'none';
  }};

  window.sortFoia = function() {{
    var mode = document.getElementById('foia-sort').value;
    var list = document.getElementById('foia-list');
    var cards = Array.prototype.slice.call(list.querySelectorAll('.fcard'));
    var toneRank = {{'blue': 1, 'red': 2, 'gold': 3, 'green': 4}};
    cards.sort(function(a, b) {{
      if (mode === 'wait-desc') {{
        var ca = a.getAttribute('data-closed') ? -1 : parseInt(a.getAttribute('data-days')||'0',10);
        var cb = b.getAttribute('data-closed') ? -1 : parseInt(b.getAttribute('data-days')||'0',10);
        if (cb !== ca) return cb - ca;
        return (b.getAttribute('data-filed') || '').localeCompare(a.getAttribute('data-filed') || '');
      }} else if (mode === 'date-desc') {{
        return (b.getAttribute('data-filed') || '').localeCompare(a.getAttribute('data-filed') || '');
      }} else if (mode === 'status-asc') {{
        var ta = toneRank[a.getAttribute('data-tone')] || 9;
        var tb = toneRank[b.getAttribute('data-tone')] || 9;
        if (ta !== tb) return ta - tb;
        return (a.getAttribute('data-title') || '').localeCompare(b.getAttribute('data-title') || '');
      }} else {{
        return (a.getAttribute('data-title') || '').localeCompare(b.getAttribute('data-title') || '');
      }}
    }});
    cards.forEach(function(c) {{ list.appendChild(c); }});
  }};

  updateClocks();
  sortFoia();
  setInterval(updateClocks, 60000);
}})();
</script>'''

  os.makedirs(os.path.join(ROOT, 'foia'), exist_ok=True)
  open(os.path.join(ROOT, 'foia', 'index.html'), 'w', encoding='utf-8').write(
      page('FOIA Tracker · Thoughts in the Vortex', foia_cfg.get('intro', ''), foia_body, 1, 'assets/vortex_logo.jpg')
  )

rb_path = os.path.join(ROOT, '_src', 'reader_body.html')
if os.path.exists(rb_path):
  rb = open(rb_path, encoding='utf-8').read()
  os.makedirs(os.path.join(ROOT, 'read'), exist_ok=True)
  open(os.path.join(ROOT, 'read', 'index.html'), 'w', encoding='utf-8').write(page('Reader · Thoughts in the Vortex', 'Read Thoughts in the Vortex reports in your browser.', rb, 1))

tlp = os.path.join(ROOT, 'timeline', 'index.html')
if os.path.exists(tlp):
  t = open(tlp, encoding='utf-8').read()
  t = _re.sub(r'<!--tv-bar-->.*?<!--/tv-bar-->', '', t, flags=_re.S)
  bar = '<!--tv-bar--><div style="background:#2f4a4c;padding:9px 16px;font:600 13.5px Poppins,Arial,sans-serif;letter-spacing:.4px;display:flex;flex-wrap:wrap;gap:6px 18px;align-items:center"><a href="../" style="color:#f2ead3;text-decoration:none">THOUGHTS IN THE VORTEX</a><span style="flex:1"></span><a href="../writeups/" style="color:#dfe8e5;text-decoration:none;font-weight:500">Write-ups</a><a href="../timeline/" style="color:#fff;text-decoration:none;font-weight:500">Timeline</a><a href="../downloads/" style="color:#dfe8e5;text-decoration:none;font-weight:500">FBI Files</a><a href="../foia/" style="color:#dfe8e5;text-decoration:none;font-weight:500">FOIA</a><a href="../feedback/" style="color:#dfe8e5;text-decoration:none;font-weight:500">Feedback</a></div><!--/tv-bar-->'
  t = _re.sub(r'(<body[^>]*>)', lambda m: m.group(1) + bar, t, count=1)
  open(tlp, 'w', encoding='utf-8').write(t)

parts_path = os.path.join(ROOT, '_src', 'parts.json')
if os.path.exists(parts_path):
  PARTS = json.load(open(parts_path, encoding='utf-8'))
  rows = ''.join(f'<tr><td>Part {p}</td><td>{n:,}</td><td><a href="{E(u)}">Scans on the FBI Vault ↗</a></td></tr>' for p, u, n in PARTS)
  total = sum(n for _, _, n in PARTS)
  dl = f'''<div class="crumb"><a href="../">Home</a> › FBI Files</div>
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
  dl = dl.replace('<tr><td>', '<tr style="border-bottom:1px solid var(--line)"><td>')
  os.makedirs(os.path.join(ROOT, 'downloads'), exist_ok=True)
  open(os.path.join(ROOT, 'downloads', 'index.html'), 'w', encoding='utf-8').write(page('The FBI files, searchable · Thoughts in the Vortex', 'OCR text of all 44,238 pages of the FBI Vault D.B. Cooper file, labeled by Part, PDF page and Bates number.', dl, 1))

API = S.get('feedback_api', '')
opts = ''.join(f'<option value="{E(i["slug"])}">{E(i["title"])}</option>' for i in items if i['kind'] == 'report')
pk = [i for i in items if i['kind'] == 'packet']
if pk:
  opts += '<optgroup label="Source packets">' + ''.join(f'<option value="{E(i["slug"])}">{E(i["title"])}</option>' for i in pk) + '</optgroup>'
opts += f'<optgroup label="Elsewhere on the site"><option value="foia">FOIA Tracker</option><option value="timeline">{E(S["timeline"]["title"])}</option><option value="downloads">FBI Files (OCR text and database)</option><option value="site">The site in general</option></optgroup>'

fb_path = os.path.join(ROOT, '_src', 'feedback_body.html')
if os.path.exists(fb_path):
  fb = open(fb_path, encoding='utf-8').read().replace('{{API}}', E(API)).replace('{{OPTIONS}}', opts)
  os.makedirs(os.path.join(ROOT, 'feedback'), exist_ok=True)
  open(os.path.join(ROOT, 'feedback', 'index.html'), 'w', encoding='utf-8').write(page('Feedback & suggestions · Thoughts in the Vortex', 'Leave anonymous feedback on a Thoughts in the Vortex write-up, or suggest a topic for a future one.', fb, 1, 'assets/vortex_logo.jpg'))

fa_path = os.path.join(ROOT, '_src', 'feedback_admin_body.html')
if os.path.exists(fa_path):
  fa = open(fa_path, encoding='utf-8').read().replace('{{API}}', E(API))
  os.makedirs(os.path.join(ROOT, 'feedback', 'admin'), exist_ok=True)
  open(os.path.join(ROOT, 'feedback', 'admin', 'index.html'), 'w', encoding='utf-8').write(page('Feedback inbox · Thoughts in the Vortex', 'Private', fa, 2).replace('<meta charset="utf-8">', '<meta charset="utf-8"><meta name="robots" content="noindex,nofollow">'))

open(os.path.join(ROOT, '404.html'), 'w', encoding='utf-8').write(page('Not found · Thoughts in the Vortex', 'Page not found', '<h1 style="margin-top:40px">Lost in the vortex</h1><p>That page isn\'t here. <a href="/">Back to the home page</a>.</p>', 0).replace('href="assets/', 'href="/assets/').replace('href="#', 'href="/#').replace('href="timeline/', 'href="/timeline/').replace('href="writeups/', 'href="/writeups/').replace('href="downloads/', 'href="/downloads/').replace('href="foia/', 'href="/foia/').replace('href="feedback/', 'href="/feedback/').replace('href="./"', 'href="/"'))
print('built', len(items), 'item pages and foia tracker')
