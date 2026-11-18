# Rebuild of the DECODE companion website (originally phone-only, by Ler Shan & Danikh)
# as a responsive site: the original phone layout plus a desktop layout, one locked/unlocked
# version per station page, and a pop-up when a page unlocks. Copy is the original's.
# Output: media/demos/decodinglife/*.html, style.css, site.js
import html, pathlib
OUT = pathlib.Path('/home/claude/site/media/demos/decodinglife')
NUM = ['one', 'two', 'three', 'four', 'five', 'six', 'seven']
ORD = ['first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh']

S = {
 'one': dict(hint="how do the different backgrounds affect your phone's ability to scan?", title=['contrast'],
   sub='there was sufficient contrast between the background and the code for it to be scanned',
   sec=[('what you just experienced', 'QR codes work because scanners can tell the difference between light and dark. With high contrast, your camera easily separates the pattern from the background. If the colours are too similar, the code disappears into the background.'),
        ('just like us', 'Just like our eyes need clear light and shadow to see shapes, machines also need clarity to “see.” The simplest black-and-white design turns out to be the most reliable form of communication.')]),
 'two': dict(hint='how does the visibility percentage affect whether the code is scannable?', title=['error', 'correction'],
   sub='enough of the code was visible for it to rebuild the rest and be scanned',
   sec=[('what you just experienced', 'QR codes can self-correct errors — meaning even if up to 30% of the code is damaged or covered, it can still be read.<br><br>Every QR code stores extra redundant data using Reed-Solomon error correction. Depending on the level (L, M, Q, H), it can recover 7%, 15%, 25%, or 30% of lost data. This makes it reliable for use in harsh or messy environments.'),
        ('in our everyday life', 'Why do you think QR codes on delivery boxes, stickers, or receipts still work even when scratched or folded?')]),
 'three': dict(hint='qr codes need some space(bar)', title=['quiet', 'space'],
   sub='qr codes require some empty space around the code for it to be scanned.',
   sec=[('what you just experienced', 'Every QR code needs a small white border — called a quiet zone — to mark where it begins and ends. Without that space, the scanner gets confused and can’t tell where the pattern stops.<br><br>The quiet zone should be at least 4 modules wide on all sides. Without it, the scanner might misinterpret surrounding patterns as part of the code. It’s like punctuation marks separating a sentence from its surroundings.'),
        ('deeper thoughts', 'Empty space isn’t wasted space. Whether in design or in life, leaving room around something helps us notice and understand it more clearly.')]),
 'four': dict(hint='two halves make a whole, but only the right one can complete it', title=['uniqueness'],
   sub='qr codes have a unique set of patterns, which means it cannot mix-and-match random halves.',
   sec=[('what you just experienced', 'Each QR code holds a unique pattern of black and white squares — its own fingerprint. The design is so precise that there’s only one possible match that works. Each QR pattern corresponds to a unique binary sequence derived from encoded text. When halves from two codes mix, the pattern logic (alignment, timing, data modules) breaks, making it unreadable.'),
        ('like other unique identifiers', 'Every pattern represents something different, and even tiny changes can mean a whole new message. Like the thumbprints on our fingers, no two are exactly the same.')]),
 'five': dict(hint='try every one you see', title=['univer-', 'sality'],
   sub='all qr codes have these 3 markers that help your phone to identify these visuals as codes',
   sec=[('what you just experienced', 'Every QR code has three position markers that help scanners detect the code instantly — no matter its size, rotation, or angle. The 3 large squares (finder patterns) tell the algorithm where the corners of the code are, while the smaller alignment and timing patterns fine-tune distortion. This universal geometry makes QR codes readable anywhere in the world.'),
        ('think about it', 'Three corners are always marked — but one is always blank. Why might the system leave one corner out?')]),
 'six': dict(hint='where do all these different-looking codes lead you to?', title=['digital', 'eyes'],
   sub='these qr codes look different from one another but all lead back here. find out more about the scanning algorithm in six: part ii',
   sec=[('what you just experienced', 'Humans see images, color, and composition — but the scanner sees binary contrast patterns. What looks different to us can be identical to the algorithm. QR readers process images by converting them to black-and-white pixel maps. They ignore texture, color, and decoration as long as the data modules remain intact and contrast is high enough.'),
        ('who is really seeing', 'Machines don’t see what we see — yet we rely on them to translate visual language into meaning. Who’s really reading the image?')]),
 'seven': dict(hint='what did you expect to see before you scanned?', title=['meaning-', 'making'],
   sub='the surrounding information affects our perceptions and expectations from the qr code',
   sec=[('what you just experienced', 'QR codes themselves are neutral — they just store data. The meaning arises from human context: signage, location, and call-to-action.<br><br>The surrounding text, image, or situation tells us what to think it does: “Scan to pay,” “Scan for menu,” “Scan to enter.” The same pattern becomes a different experience each time.'),
        ('different perspectives, one language', 'The QR code is both machine-readable and human-interpreted — a shared language between us and technology.')]),
}
CSS = r'''@font-face{font-family:Alumni;src:url(fonts/alumni-sans-latin-wght-normal.woff2) format("woff2");font-weight:100 900}
@font-face{font-family:Inter;src:url(fonts/inter-latin-wght-normal.woff2) format("woff2");font-weight:100 900}
:root{--acc:#00FFAE;--bg:#111}
*{padding:0;margin:0;box-sizing:border-box}
html,body{background:var(--bg);color:#fff;font-family:Inter,sans-serif;font-size:15px;font-weight:400}
a{color:inherit;text-decoration:none}
img{display:block;max-width:100%}
[hidden]{display:none!important}
.kicker,.sub,.header-type,.next-step,#footer,.header-links,.index{font-family:Alumni,sans-serif;text-transform:uppercase;letter-spacing:.1rem}
/* ---------- phone (the original layout) ---------- */
#wrapper{width:min(100vw,500px);min-height:100vh;margin:0 auto;display:flex;flex-direction:column}
main{flex:1}
#logo-container{display:flex;justify-content:center;margin:3rem 0 1rem}
#logo-container a{width:40%}
#links-container{display:flex;justify-content:space-evenly;padding:1rem;border-top:1px solid var(--acc);border-bottom:1px solid var(--acc)}
.header-links{font-weight:200;font-size:1rem;opacity:.75}
.header-links .no{display:none}
.header-links.highlighted{opacity:1;border-bottom:1px solid #fff}
.hero{min-height:80vh;display:flex;flex-direction:column;justify-content:center;align-items:center;gap:4px;padding:0 1rem;margin:1rem 0;text-align:center}
.kicker,.sub{font-weight:200;font-size:1.5rem;line-height:1.75rem}
.mark{display:flex;align-items:center;margin:.75rem 0}
.mark .sq{width:32px;flex:none}
.page-title{font-family:Alumni,sans-serif;font-weight:400;text-transform:uppercase;letter-spacing:.1rem;font-size:4rem;line-height:4rem;margin-left:2rem;text-align:left}
.page-title span{display:block}
.home-logo{width:320px;max-width:80vw;margin:.5rem 0}
.home-logo img{width:100%}
.dud-image{width:75%;margin-top:1rem}
.secs{display:block}
.header-type{font-weight:300;font-size:1.25rem;margin:1rem 2.5rem;border-top:1px solid #fff;border-bottom:1px solid #fff}
.body-type{font-size:14px;font-weight:200;line-height:1.25rem;margin:0 2.5rem 3rem}
.next-step{display:block;text-align:center;font-weight:300;font-size:1.5rem;padding:.5rem 2.5rem;margin:2rem 0;border-top:1px solid #fff;border-bottom:1px solid #fff;transition:color .2s,border-color .2s}
a.next-step:hover{color:var(--acc);border-color:var(--acc)}
.next-step.dim{opacity:.6}
#footer{padding:.5rem 2.5rem;margin:1rem 0;font-weight:200;font-size:1rem;text-align:center;border-top:1px solid #fff;border-bottom:1px solid #fff;opacity:.75}
/* ---------- desktop (new) ---------- */
@media (min-width:760px){
  #wrapper{width:100%;max-width:1360px;padding:0 clamp(28px,4vw,64px)}
  #header{display:flex;align-items:center;justify-content:space-between;gap:32px;padding:28px 0 22px;border-bottom:1px solid var(--acc)}
  #logo-container{margin:0}
  #logo-container a{width:150px;display:block}
  #links-container{border:0;padding:0;gap:clamp(14px,2.2vw,34px)}
  .header-links{font-size:1.15rem;display:flex;align-items:baseline;gap:6px;padding-bottom:3px;border-bottom:1px solid transparent;transition:opacity .2s,border-color .2s}
  .header-links .no{display:inline;font-size:.75rem;color:var(--acc)}
  .header-links:hover{opacity:1}
  .hero{min-height:min(72vh,680px);display:grid;grid-template-columns:minmax(0,1.35fr) minmax(0,1fr);grid-template-rows:auto 1fr;align-items:end;justify-items:start;text-align:left;padding:clamp(40px,7vh,90px) 0 clamp(36px,6vh,70px);margin:0;column-gap:clamp(32px,5vw,80px);border-bottom:1px solid rgba(255,255,255,.25)}
  .hero .kicker{grid-column:1/-1;align-self:start;font-size:1.35rem;color:var(--acc)}
  .hero .mark{grid-column:1;margin:0;align-items:flex-end}
  .mark .sq{width:clamp(48px,6vw,84px);margin-bottom:clamp(10px,1.4vw,22px)}
  .page-title{font-size:clamp(88px,12vw,190px);line-height:.86;margin-left:clamp(18px,2.4vw,36px);font-weight:300}
  .hero .sub{grid-column:2;font-size:clamp(1.5rem,2vw,2rem);line-height:1.15;max-width:420px}
  .hero.home{grid-template-columns:1fr}
  .hero.home .home-logo{width:min(760px,70%);max-width:none;margin:0}
  .hero.home .sub{grid-column:1;max-width:620px}
  .dud{}
  .dud .hero{grid-template-columns:minmax(0,1fr) minmax(0,1fr);align-items:center}
  .dud .dud-image{grid-column:1;width:min(380px,100%);margin:0}
  .secs{display:block}
  .sec{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.6fr);gap:clamp(24px,5vw,80px);padding:clamp(28px,4vw,48px) 0;border-bottom:1px solid rgba(255,255,255,.25)}
  .header-type{margin:0;border:0;font-size:1.5rem;font-weight:300;line-height:1.1}
  .header-type::before{content:"";display:inline-block;width:10px;height:10px;background:var(--acc);margin-right:12px;vertical-align:2px}
  .body-type{margin:0;font-size:17px;line-height:1.6;font-weight:300;max-width:680px}
  .next-step{margin:clamp(28px,5vh,56px) 0;padding:18px 0;font-size:clamp(1.5rem,2.4vw,2.2rem)}
  #footer{margin:0 0 28px}
}
'''

HOW = {
 'one': 'Slide the engraved acrylic across the backgrounds until one gives enough contrast to scan.',
 'two': 'Scratch away the grey layer until enough of the code shows for error correction to fill in the rest.',
 'three': 'Keep pressing space to grow the white border around the code until it is wide enough to scan.',
 'four': 'Find the one half on the wall that completes your piece, and line it up.',
 'five': 'Slide the three markers over each code until every one of them scans.',
 'six': 'Step through how a scanner reads a code, all the way to the decoded link.',
}
TITLES = {n: ' '.join(S[n]['title']).replace('univer- sality', 'universality').replace('- ', '-') for n in NUM}

def head(title):
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
            f'<title>{title}</title><link rel="stylesheet" href="style.css"></head><body>\n<div id="wrapper">')

def header(active=None):
    links = ''.join(f'<a class="header-links{" highlighted" if n == active else ""}" href="{n}.html"><span class="no">0{i + 1}</span>{n}</a>' for i, n in enumerate(NUM))
    return ('<header id="header"><div id="logo-container"><a href="index.html"><img src="assets/decode_logo.svg" alt="DECODE"></a></div>'
            f'<nav id="links-container">{links}</nav></header>')

FOOT = '<footer id="footer">did platforms: coded life — ler shan &amp; danikh</footer></div>'

POP = ('<div class="pop" id="pop" hidden><div class="pop-card" role="dialog" aria-modal="true" aria-labelledby="pop-t">'
       '<p class="kicker">successfully scanned</p><div class="mark"><img class="sq" src="assets/square_logo.svg" alt=""><p class="pop-n" id="pop-n"></p></div>'
       '<p class="pop-t" id="pop-t"></p><div class="pop-b"><a class="pop-go" id="pop-go" href="#">view the page</a><button type="button" id="pop-x">close</button></div></div></div>')

def end():
    return '</main>' + FOOT + POP + '<script src="site.js"></script></body></html>'

def hero(kicker, title, sub):
    t = ''.join(f'<span>{html.escape(x)}</span>' for x in title)
    return (f'<section class="hero"><p class="kicker">{kicker}</p>'
            f'<div class="mark"><img class="sq" src="assets/square_logo.svg" alt=""><h1 class="page-title">{t}</h1></div>'
            f'<p class="sub">{sub}</p></section>')

def sections(sec):
    return '<div class="secs">' + ''.join(f'<section class="sec"><h2 class="header-type">{h}</h2><div class="body-type"><p>{b}</p></div></section>' for h, b in sec) + '</div>'

def next_link(href, label):
    return f'<a class="next-step" href="{href}">&lt; {label} &gt;</a>' if href else f'<span class="next-step dim">&lt; {label} &gt;</span>'

def station(i, n):
    d = S[n]
    nxt = ('completion.html', 'to completion') if n == 'seven' else (f'{NUM[i + 1]}.html', f'move to task {NUM[i + 1]}')
    b = head(f'Decode · {n}').replace('<body>', f'<body data-key="{n}">') + header(n) + '<main>'
    if n == 'seven':
        task = ('<div class="posters"><img src="assets/poster-complaint.webp" alt="Poster: scan here to file a complaint"><img src="assets/poster-menu.webp" alt="Poster: scan and order, our menu"></div>'
                '<p>At the exhibition, posters like these promised one thing and their codes delivered another. Scan one with your phone: does it take you where you expected?</p>')
    else:
        task = (f'<p><b>At the exhibition:</b> {HOW[n]} The station then gives you a code that unlocks this page.</p>'
                f'<p><b>Here:</b> complete Station 0{i + 1} in the DECODE case study and this page unlocks by itself.</p>')
    b += (f'<div class="state" id="not-scanned">{hero("head to the " + ORD[i] + " task", ["???"], "hint: " + d["hint"])}'
          f'<section class="sec how"><h2 class="header-type">how to unlock this page</h2><div class="body-type">{task}'
          f'<button class="unlock" type="button" data-unlock="{n}"><img src="assets/square_logo.svg" alt="">unlock this page</button></div></section>'
          f'{next_link(None, "complete this before the next")}</div>')
    b += f'<div class="state" id="scanned" hidden>{hero("successfully scanned", d["title"], d["sub"])}{sections(d["sec"])}{next_link(*nxt)}</div>'
    (OUT / f'{n}.html').write_text(b + end())

def index_grid(cls=''):
    return (f'<div class="index {cls}">' + ''.join(f'<a href="{n}.html" data-st="{n}"><span class="no">0{i + 1}</span><span class="nm">{n}</span><span class="q">???</span></a>' for i, n in enumerate(NUM)) + '</div>')

def home():
    b = head('Decode') + header() + '<main>'
    b += ('<section class="hero home"><p class="kicker">welcome to</p><div class="home-logo"><img src="assets/decode_logo.svg" alt="DECODE"></div>'
          '<p class="sub">an exhibition on decoding how qr codes work and interact with us</p></section>')
    b += sections([('what decode is about', 'QR codes are everywhere — on walls, screens, receipts, and menus — yet we rarely pause to think about how they work. This exhibition invites you to slow down and explore the hidden design behind these everyday squares.'),
                   ('what you can expect', 'Through a series of 7 interactive stations, you’ll learn how QR codes see, correct, adapt, and communicate. Each task challenges you to make a code scannable, revealing something new about how technology reads the world, and how we, in turn, read technology.'),
                   ('how this site works', 'Every station has a page on this site, and each page starts locked. Complete a station and the page unlocks to explain what you just experienced. On the DECODE case study, finishing a station’s interactive unlocks its page here, or you can press unlock on any page.')])
    b += '<p class="count" id="count"></p>' + index_grid()
    b += next_link('one.html', 'move to the first station')
    (OUT / 'index.html').write_text(b + end())

def completion():
    b = head('Decode · completion') + header() + '<main>'
    b += ('<section class="hero"><p class="kicker">congratulations on completing</p><div class="home-logo"><img src="assets/decode_logo.svg" alt="DECODE"></div>'
          '<p class="sub">thank you for participating<br>stay curious, about anything and everything seemingly mundane!</p></section>')
    b += '<p class="count" id="count"></p>' + index_grid('done')
    b += sections([('what we hope you took away', 'The QR code may be simple — just black and white squares — yet it holds a quiet intelligence that connects people, places, and information.<br><br>As you leave this exhibition, may you notice these small patterns differently — not just as tools of convenience, but as everyday symbols of how we read, make, and share meaning together.'),
                   ('let us know about your experience', 'Feel free to chat with us at the exhibition! :D')])
    b += '<button class="next-step reset" type="button" id="reset-progress">&lt; lock every page again &gt;</button>'
    (OUT / 'completion.html').write_text(b + end())

JS = r"""(() => {
  const NUM = ['one', 'two', 'three', 'four', 'five', 'six', 'seven'];
  const TITLE = __TITLES__;
  const KEY = 'decode-unlocked';
  let mem = [];
  const get = () => { try { return JSON.parse(localStorage.getItem(KEY) || '[]'); } catch (e) { return mem.slice(); } };
  const set = a => { mem = a.slice(); try { localStorage.setItem(KEY, JSON.stringify(a)); } catch (e) {} };
  const key = document.body.dataset.key, params = new URLSearchParams(location.search);
  // the original exhibition links still work, e.g. one.html?success_one=true
  NUM.forEach(n => { if (params.get('success_' + n) && !get().includes(n)) set(get().concat(n)); });
  function paint() {
    const done = get();
    if (key) {
      const open = done.includes(key);
      document.getElementById('scanned').hidden = !open;
      document.getElementById('not-scanned').hidden = open;
    }
    document.querySelectorAll('.header-links').forEach(a => a.classList.toggle('open', done.includes(a.getAttribute('href').replace('.html', ''))));
    document.querySelectorAll('[data-st]').forEach(el => {
      const n = el.dataset.st, open = done.includes(n);
      el.classList.toggle('open', open);
      el.querySelector('.q').textContent = open ? TITLE[n] : '???';
    });
    const c = document.getElementById('count'); if (c) c.textContent = done.length + ' / 7 pages unlocked';
  }
  // the pop-up, shown when a page unlocks here or from a station on the case-study page
  const pop = document.getElementById('pop');
  function announce(n) {
    const i = NUM.indexOf(n);
    document.getElementById('pop-n').textContent = TITLE[n];
    document.getElementById('pop-t').textContent = 'station 0' + (i + 1) + ' complete. the ' + n + ' page is now unlocked.';
    const go = document.getElementById('pop-go');
    go.href = n + '.html'; go.hidden = n === key;
    pop.hidden = false; requestAnimationFrame(() => requestAnimationFrame(() => pop.classList.add('on')));
  }
  const close = () => { pop.classList.remove('on'); setTimeout(() => { pop.hidden = true; paint(); window.scrollTo(0, 0); }, 260); };
  document.getElementById('pop-x').onclick = close;
  pop.addEventListener('click', e => { if (e.target === pop) close(); });
  addEventListener('keydown', e => { if (e.key === 'Escape' && !pop.hidden) close(); });
  document.querySelectorAll('[data-unlock]').forEach(b => b.addEventListener('click', () => {
    const n = b.dataset.unlock; if (!get().includes(n)) set(get().concat(n)); announce(n);
  }));
  addEventListener('storage', e => {
    if (e.key !== KEY) return;
    let before = [], now = [];
    try { before = JSON.parse(e.oldValue || '[]'); now = JSON.parse(e.newValue || '[]'); } catch (x) {}
    const fresh = now.filter(n => !before.includes(n));
    if (fresh.length) announce(fresh[fresh.length - 1]); else paint();
  });
  const reset = document.getElementById('reset-progress');
  if (reset) reset.onclick = () => { set([]); paint(); };
  paint();
})();
"""

CSS_EXTRA = r'''
/* lock / unlock */
.how .body-type p+p{margin-top:.9rem}
.how b{font-weight:500}
.unlock{appearance:none;display:inline-flex;align-items:center;gap:12px;margin-top:1.4rem;padding:12px 18px 12px 12px;border:1px solid var(--acc);background:transparent;color:#fff;font-family:Alumni,sans-serif;font-size:1.25rem;letter-spacing:.1rem;text-transform:uppercase;cursor:pointer;transition:background .2s,color .2s}
.unlock img{width:22px}
.unlock:hover{background:var(--acc);color:#111}
.posters{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:0 0 1.2rem}
.posters img{width:100%;border-radius:4px}
.header-links.open{color:var(--acc);opacity:1}
.count{font-family:Alumni,sans-serif;text-transform:uppercase;letter-spacing:.1rem;font-size:1.1rem;text-align:center;color:var(--acc);margin:1rem 0 .4rem}
.index{display:grid;grid-template-columns:1fr 1fr;margin:0 2.5rem;border-top:1px solid rgba(255,255,255,.25)}
.index a{display:flex;align-items:baseline;gap:8px;padding:12px 0;border-bottom:1px solid rgba(255,255,255,.18)}
.index .no{color:var(--acc);font-size:.85rem}
.index .nm{font-size:1.25rem;font-weight:300}
.index .q{margin-left:auto;padding-right:10px;font-size:.85rem;opacity:.5}
.index a.open .q{opacity:1;color:var(--acc)}
button.next-step{appearance:none;width:100%;background:transparent;color:#fff;cursor:pointer;border-left:0;border-right:0}
button.next-step:hover{color:var(--acc);border-color:var(--acc)}
.pop{position:fixed;inset:0;z-index:20;display:flex;align-items:center;justify-content:center;padding:24px;background:rgba(0,0,0,.6);opacity:0;transition:opacity .26s}
.pop.on{opacity:1}
.pop-card{width:min(420px,100%);background:#111;border:1px solid var(--acc);padding:26px 24px 22px;text-align:center;transform:translateY(14px) scale(.98);transition:transform .32s cubic-bezier(.2,.8,.2,1)}
.pop.on .pop-card{transform:none}
.pop-card .kicker{color:var(--acc);font-size:1.15rem}
.pop-card .mark{justify-content:center;margin:14px 0}
.pop-n{font-family:Alumni,sans-serif;text-transform:uppercase;letter-spacing:.1rem;font-size:2.6rem;line-height:1;margin-left:1rem;text-align:left}
.pop-t{font-family:Alumni,sans-serif;text-transform:uppercase;letter-spacing:.1rem;font-weight:200;font-size:1.2rem;line-height:1.4}
.pop-b{display:flex;gap:10px;justify-content:center;margin-top:18px}
.pop-b a,.pop-b button{appearance:none;font-family:Alumni,sans-serif;text-transform:uppercase;letter-spacing:.1rem;font-size:1.1rem;padding:8px 16px;border:1px solid #fff;background:transparent;color:#fff;cursor:pointer}
.pop-b a{background:var(--acc);border-color:var(--acc);color:#111}
@media (min-width:760px){
  .how .body-type{max-width:620px}
  .posters{max-width:520px}
  .count{text-align:left;margin:28px 0 10px}
  .index{grid-template-columns:repeat(7,minmax(0,1fr));margin:0;border-top:0;border-bottom:1px solid rgba(255,255,255,.25)}
  .index a{flex-direction:column;gap:8px;padding:22px 14px 26px;border-bottom:0;border-left:1px solid rgba(255,255,255,.18);transition:background .2s}
  .index a:first-child{border-left:0;padding-left:0}
  .index a:hover{background:rgba(0,255,174,.06)}
  .index .nm{font-size:1.6rem}
  .index .q{margin:0;padding:0}
  .pop-n{font-size:3.2rem}
}
'''

for i, n in enumerate(NUM): station(i, n)
home(); completion()
import json
(OUT / 'site.js').write_text(JS.replace('__TITLES__', json.dumps(TITLES)))
(OUT / 'style.css').write_text(CSS + CSS_EXTRA)
for old in ('menu.webp', 'survey.webp', 'paynow-hidden.webp'):
    f = OUT / 'assets' / old
    if f.exists(): f.unlink()
print('ok', sorted(p.name for p in OUT.glob('*.html')))
