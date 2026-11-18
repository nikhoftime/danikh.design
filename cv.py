"""Builds src/files/Danikh_Nizam_CV.pdf from the same data as the Information page,
in the website's style on white. Run: python3 cv.py (needs Playwright + Chromium)."""
import html, importlib.util, os
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('site_build', os.path.join(ROOT, 'build.py'))
B = importlib.util.module_from_spec(spec); spec.loader.exec_module(B)
esc = lambda s: html.escape(s, quote=True)
FONTS = os.path.join(ROOT, 'src', 'fonts')
OUT = os.path.join(ROOT, 'src', 'files', 'Danikh_Nizam_CV.pdf')

MARK = B.mark_svg()


def wordmark_svg():
    """The DANIKH.DESIGN pixel wordmark, core pixels only."""
    WM = B.WORDMARK
    rects = ''.join(f'<rect x="{i + .08}" y="{j + .08}" width=".84" height=".84"/>'
                    for j, r in enumerate(WM['rows']) for i, c in enumerate(r) if c == '1')
    return f'<svg class="wm" viewBox="0 0 {WM["w"]} {WM["h"]}" fill="currentColor">{rects}</svg>'


def label(t): return f'<h2 class="lbl"><span>{t}</span></h2>'


def xp(e):
    org = esc(e['org'])
    if e.get('url'): org = f'<a href="{e["url"]}">{org} ↗</a>'
    pts = ''.join(f'<li>{esc(p)}</li>' for p in e['points'])
    now = '<span class="now">Now</span>' if e.get('now') else ''
    note = f'<p class="note">{esc(e["note"])}</p>' if e.get('note') else ''
    return f'''<article class="xp"><div class="when">{e["when"]}{now}</div><div>
<h3>{org}</h3><p class="role">{esc(e["role"])} <span>· {esc(e["where"])}</span></p><ul>{pts}</ul>{note}</div></article>'''


edu = ''.join(f'<div class="it"><h4>{esc(a)}</h4><p>{esc(b)}</p><p class="cap">{c}</p></div>' for a, b, c, d in B.EDUCATION)
exh = ''.join(f'<div class="it"><p class="tag">{esc(v)}</p><a class="ul" href="{u}"><h4>{esc(t)} ↗</h4></a><p class="m">{esc(r)}</p><p class="cap">{esc(d)}</p></div>'
              for v, t, r, d, u in B.EXHIBITIONS)
pubs = ''.join(f'<div class="it"><p class="tag">{esc(v)}</p><a class="ul" href="{u}">{esc(t)} ↗</a><p class="m">{esc(r)}</p></div>' for v, t, r, u in B.PUBLICATIONS)
ment = ''.join(f'<div class="it"><a class="ul" href="{u}"><h4>{esc(a)} ↗</h4></a><p>{esc(b)}</p><p class="m">{esc(c)}</p></div>' for a, b, c, u in B.MENTORSHIP)
skills = ''.join(f'<div class="it"><h4>{esc(a)}</h4><p class="m">{esc(b)}</p></div>' for a, b in B.SKILLS)
chips = ''.join(f'<li>{esc(x)}</li>' for x in B.INTERESTS)
PROJ = [
        ('DECODE', 'decode', 'Seven-station exhibition that makes the hidden mechanics of the QR code tangible through physical and digital interactions.', 'Interaction Design · UX/UI Design · HCI'),
        ('PATH: AI x (Super-Aged) Society', 'path', 'Speculative AI service for a 2040 Singapore that scores how families care for their elders, told through a film and three interactive artefacts.', 'Speculative Design · Human-AI Interaction · UX/UI Design'),
        ('Simon', 'simon', 'AI companion and on-call simulator for junior doctors on Apple Vision Pro, with digital twins of NUH wards and AI-generated scenarios.', 'Spatial Computing · 3D UX/UI · Generative AI')]
proj = ''.join(f'<div class="pj"><a class="ul" href="https://danikh.design/projects/{s}"><h4>{esc(t)} ↗</h4></a><p>{esc(d)}</p><p class="cap">{esc(k)}</p></div>' for t, s, d, k in PROJ)


ICON = {
    'web': '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.3"><circle cx="8" cy="8" r="6.3"/><path d="M1.7 8h12.6M8 1.7c1.9 1.8 2.8 3.9 2.8 6.3S9.9 12.5 8 14.3M8 1.7C6.1 3.5 5.2 5.6 5.2 8s.9 4.5 2.8 6.3"/></svg>',
    'in': '<svg viewBox="0 0 16 16" fill="currentColor"><path d="M2 1.5h12a.5.5 0 0 1 .5.5v12a.5.5 0 0 1-.5.5H2a.5.5 0 0 1-.5-.5V2a.5.5 0 0 1 .5-.5Zm2 4.7v6.1h1.9V6.2H4Zm.95-3a1.1 1.1 0 1 0 0 2.2 1.1 1.1 0 0 0 0-2.2Zm2.6 3v6.1h1.9V9.3c0-.8.15-1.6 1.15-1.6.98 0 1 .92 1 1.66v2.95h1.9V8.97c0-1.64-.35-2.9-2.27-2.9-.92 0-1.54.5-1.79.98h-.03V6.2H7.55Z"/></svg>',
    'mail': '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.3"><rect x="1.7" y="3.2" width="12.6" height="9.6" rx="1"/><path d="m2.2 4 5.8 4.6L13.8 4"/></svg>',
}
CONTACT = (f'<a href="https://danikh.design">{ICON["web"]}danikh.design</a>'
           f'<a href="https://www.linkedin.com/in/danikhnizam/">{ICON["in"]}linkedin.com/in/danikhnizam</a>'
           f'<a href="mailto:danikhnizam@gmail.com">{ICON["mail"]}danikhnizam@gmail.com</a>')

TOP = f'''<div class="top"><a class="brand" href="https://danikh.design">{MARK}<span>Danikh Nizam</span></a><nav>{CONTACT}</nav></div>'''

exp = B.EXPERIENCE
P1 = f'''<section class="page">
<header class="band"><div class="band-top"><a class="brand" href="https://danikh.design">{MARK}<span>Curriculum Vitae</span></a><nav>{CONTACT}</nav></div>
<div class="band-main"><div><h1>Danikh Nizam</h1><p class="role-l">Designer &amp; HCI Researcher · Industrial Design, NUS</p></div>
<div><p class="lead">{esc(B.ABOUT)}</p><p class="cap focus">{esc(B.FOCUS)}</p></div></div></header>
<div class="grid"><div class="main">{label('Experience')}{''.join(xp(e) for e in exp[:2])}</div>
<aside>{label('Education')}{edu}{label('Exhibitions')}{exh}{label('Publication')}{pubs}</aside></div>
<div class="foot"><span class="cap">01 / 02</span>{wordmark_svg()}</div></section>'''

P2 = f'''<section class="page">{TOP}
<div class="grid g2"><div class="main">{label('Experience')}{''.join(xp(e) for e in exp[2:])}</div>
<aside>{label('Mentorship')}{ment}{label('Skills &amp; tools')}{skills}{label('Research interests')}<ul class="chips">{chips}</ul></aside></div>
<div class="foot"><span class="cap">02 / 02</span>{wordmark_svg()}</div></section>'''

CSS = f'''
@font-face{{font-family:Switzer;font-weight:400;src:url(file://{FONTS}/switzer-latin-400-normal.woff2)}}
@font-face{{font-family:Switzer;font-weight:500;src:url(file://{FONTS}/switzer-latin-500-normal.woff2)}}
@font-face{{font-family:Switzer;font-weight:600;src:url(file://{FONTS}/switzer-latin-600-normal.woff2)}}
@page{{size:A4;margin:0}}
*{{box-sizing:border-box;margin:0;padding:0}}
:root{{--fg:#0F0E0E;--m:#6F6D69;--d:#9A9893;--line:#E3E1DD}}
body{{font-family:Switzer,sans-serif;color:var(--fg);font-size:9.5pt;line-height:1.6;-webkit-print-color-adjust:exact}}
a{{color:inherit;text-decoration:none}}
.page{{position:relative;width:210mm;height:297mm;padding:10mm 13mm 0;overflow:hidden;page-break-after:always}}
.page:last-child{{page-break-after:auto}}
.cap,.top,.lbl,.when,.tag{{font-size:6.6pt;font-weight:500;letter-spacing:.03em;text-transform:uppercase}}
.top{{display:flex;justify-content:space-between;align-items:center}}
.brand{{display:flex;align-items:center;gap:6px}} .brand svg{{width:8.5px;height:auto}}
.top nav a{{color:var(--fg)}}
.hero{{padding:11mm 0 6mm;border-bottom:1px solid var(--line)}}
h1{{font-weight:500;font-size:46pt;letter-spacing:-.055em;line-height:.9;margin-left:-.04em}}
.hero-grid{{display:grid;grid-template-columns:1fr 54mm;gap:12mm;margin-top:6mm;align-items:end}}
.lead{{font-size:10.6pt;line-height:1.45;letter-spacing:-.005em}}
.focus{{color:var(--m);line-height:1.7}}
.grid{{display:grid;grid-template-columns:1fr 54mm;gap:12mm;padding-top:5mm}}
.g2{{padding-top:9mm}}
.lbl{{display:flex;align-items:center;gap:10px;color:var(--m);margin:0 0 4mm}}
.lbl::after{{content:"";flex:1;height:1px;background:var(--line)}}
aside .lbl:not(:first-child),.main .lbl:not(:first-child){{margin-top:8mm}}
.xp{{display:grid;grid-template-columns:26mm 1fr;gap:4mm;padding-bottom:4.6mm;margin-bottom:4.6mm;border-bottom:1px solid var(--line)}}
.xp:last-of-type{{border-bottom:0}}
.when{{color:var(--m);line-height:1.5}}
.now{{display:flex;align-items:center;gap:5px;color:var(--fg);margin-top:3px}}
.now::before{{content:"";width:4px;height:4px;background:var(--fg)}}
h3{{font-weight:500;font-size:12.6pt;letter-spacing:-.02em;line-height:1.2}}
h3 a{{border-bottom:1px solid var(--line)}}
.role{{margin:2px 0 6px;font-weight:500}} .role span{{color:var(--m);font-weight:400}}
.xp ul{{list-style:none}}
.xp li{{position:relative;padding-left:9px;margin-bottom:4.5px;color:#3B3936}}
.xp li::before{{content:"";position:absolute;left:0;top:.62em;width:3px;height:3px;background:var(--d)}}
.note{{color:var(--m);margin-top:4px}}
.it{{margin-bottom:6mm}} .it:last-child{{margin-bottom:0}}
h4{{font-weight:500;font-size:9.8pt;letter-spacing:-.01em;line-height:1.3}}
.it p{{margin-top:1px}} .m{{color:var(--m)}} .it .cap{{color:var(--m);margin-top:3px}}
.tag{{margin-bottom:3px}}
.ul{{display:inline;border-bottom:1px solid var(--line)}}
.ul h4{{display:inline}}
.chips{{list-style:none;display:flex;flex-wrap:wrap;gap:4px}}
.chips li{{border:1px solid var(--line);border-radius:2px;padding:3px 6px;font-size:7.6pt}}
.pj{{margin-bottom:4.5mm}} .pj p{{color:#3B3936;margin-top:2px}} .pj .cap{{color:var(--m);margin-top:3px}}

.top nav,.band-top nav{{display:flex;gap:14px}}
.top nav a,.band-top nav a{{display:inline-flex;align-items:center;gap:5px;border:0;padding:0}}
.top nav svg,.band-top nav svg{{width:9px;height:9px;flex:none}}
.band{{position:relative;margin:-10mm -13mm 0;padding:9mm 13mm 9mm;height:99mm;display:flex;flex-direction:column;background:#0F0E0E;color:#F2F1EE;overflow:hidden}}
.band-top{{display:flex;justify-content:space-between;align-items:center;font-size:6.6pt;font-weight:500;letter-spacing:.03em;text-transform:uppercase;position:relative;z-index:1}}
.band .brand svg{{color:#F2F1EE}}
.band-main{{position:relative;z-index:1;display:grid;grid-template-columns:1fr 92mm;gap:10mm;align-items:stretch;margin-top:auto}}
.band-main>div:first-child{{display:flex;flex-direction:column;justify-content:space-between}}
.band h1{{font-size:57pt;line-height:.86;margin-top:-1.9mm}}
.band h1{{color:#F2F1EE}}
.role-l{{margin-top:3.5mm;font-size:8pt;font-weight:500;letter-spacing:.03em;text-transform:uppercase;color:#B9B7B2}}
.band .lead{{font-size:9.2pt;line-height:1.5;color:#E6E4DF}}
.band .focus{{color:#8E8C88;margin-top:3mm}}
.band-wm{{position:absolute;right:-6mm;top:4mm;width:150mm;opacity:.07;z-index:0}}
.band-wm .wm{{width:100%;color:#F2F1EE}}
.band + .grid{{padding-top:7mm}}
.projs{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:0 7mm}}
.foot{{position:absolute;left:13mm;right:13mm;bottom:8mm;display:flex;justify-content:space-between;align-items:flex-end;color:var(--d)}}
.wm{{display:block;width:30mm;height:auto;color:var(--fg)}}
'''

DOC = f'<!doctype html><html><head><meta charset="utf-8"><title>Danikh Nizam — CV</title><style>{CSS}</style></head><body>{P1}{P2}</body></html>'

if __name__ == '__main__':
    tmp = os.path.join(ROOT, 'cv.html')
    open(tmp, 'w').write(DOC)
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page()
        pg.goto('file://' + tmp); pg.wait_for_timeout(600)
        print(pg.evaluate("[...document.querySelectorAll('.page')].map(s=>[s.scrollHeight,s.clientHeight,Math.max(...[...s.querySelectorAll('.grid>*')].map(e=>e.getBoundingClientRect().bottom-s.getBoundingClientRect().top))])"))
        pg.pdf(path=OUT, format='A4', print_background=True)
        b.close()
    os.remove(tmp)
    print('wrote', OUT)
