#!/usr/bin/env python3
"""Builds the static site into dist/.

Edit content/*.txt (one file per project) and run:  python3 build.py
Line types in a project file:
  SLUG, TITLE, COVER, TAGS, CLIENT, TEAM, YEAR, MEDIUM, STATUS   – project details
  HERO <file>  big image or video shown right under the title
  VIDEO yt <id> | VIDEO vimeo <id>                                – main video
  P <text>     paragraph          H <text>   heading
  TH a | b     table header row   TR a | b   table row
  EMBED <file> interactive demo from media/demos/ (posts its height to the page)
  IMG <file>   full-width image   IMGSM <file>  smaller image for low-res pictures
    PAIR <a> <b>  two images side by side
  MP4 <file>   looping video      MP4GRID <a> <b> ...  grid of looping videos
  CAP <text>   small caption/label
  LINK <label> | <url>   outbound link button
Media: put the full-size file in originals/ and run  python3 optimize.py  first;
it writes web-sized copies to media/. GIFs are turned into small looping videos.
"""
import html, os, shutil, json

ROOT = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ROOT, 'dist')
YEAR = '2026'

# Order on the home page, and the newest-first order used on the Work page and for prev/next.
HOME_ORDER = ['decode', 'path', 'simon', 'minda', 'soundlab', 'beyondboundaries']
WORK_ORDER = ['codedlife', 'beyondboundaries', 'path', 'soundlab', 'designtype', 'kalian-joget-joget', 'decode', 'simon', 'minda', 'bistrobox', 'pickabook', 'onepoint', 'lilypad', 'meritbadges']

LINKS = [
    ('LinkedIn', 'https://www.linkedin.com/in/danikhnizam'),
    ('Behance', 'https://www.behance.net/danikh'),
    ('Instagram', 'https://www.instagram.com/danikh.design/'),
    ('danikhnizam@gmail.com', 'mailto:danikhnizam@gmail.com'),
]

# The logo: pixel D, frame 09 (dissolved), and the clean D it heals into on hover.
MARK_09 = ["████████····", "·█████████··", "███████████·", "·███····████", "███·····████", "██········█·", "·██·······██", "·██······██·", "███······██·", "·██·····████", "·███·███████", "·██████████·", "·████████···", "·██··███····"]
MARK_CLEAN = ["████████    ", "██████████  ", "███████████ ", "████████████", "███     ████", "███      ███", "███      ███", "███      ███", "███      ███", "███     ████", "████████████", "███████████ ", "██████████  ", "████████    "]
# DANIKH.DESIGN wordmark: 1 = pixel, 2 = missing pixel that fills back in on hover, 0 = empty.
WORDMARK = {"w": 154, "h": 14, "split": [74, 76], "rows": ["1111111100000000001122000000012120000110000110000110000012110001100000011000000001211111100000001111111111000001111111100001100000121111111000001100000110", "2111111111000000211111120000111110000111001111001110000111100011100000011100000002111111121000001111111111000111111111110011100000111111111000011110000111", "1111111111100001111111111000211111000211002112001110001111000011100000021100000001111111111100011100000000001111000000000011110011110000000000111110000011", "2111222211110021110000111100111111000212002111001110001111000011100000011200000002111111111110021100000000001110000000000021120021100000000000211111000011", "1110000011110011100000011100211111100211001111001120011120000011100000011100000001110000011110011100000000001110000000000011110011100000000000111111100111", "1120000002120021100000011200111111100111002111001110111100000011100000011100000001110000001100011100000000001111000000000011100011000000000000211111200111", "2110000002110011100000011200212011120111002112001111111000000011111111111100000002110000001100011111111100000111111112100011100021000000111100111211112111", "2110000001120021111111111100111011120111001111001111111000000021111111111100000001110000001110011111111110000100111111100001110011100001111100111211112111", "1110000001120021111111111100111001111111001111001110211200000011200000021200000001110000001110011100000000000000000001110001110001100000011100112002111111", "2110000011110011100000011200111001111111001111002110011120000021100000011200000000110000011110011100000000000000000001110001110001100000021200111001111112", "2111211111110021200000011100112000111112002111001110001111000011100000011200000000111111111110021100000000000000000002110001110011110000011100111000111111", "2111111111100011200000011100211000211111001111002120001111000011100000011200011001111111111000011200000000000000000001110001110011110012111100111000111112", "2111111112000011200000011100111000011111001111001110000111100011200000021200111001111111110000011111111111000111111111000011100001111111111100111000001111", "2112211100000001200000011000012000011120000110000110000011110001100000011000011001111111000000001111111111000111111100000001100000112111121000011000001000"]}
bits = lambda rows: [''.join('1' if c == '█' else '0' for c in r) for r in rows]


def mark_svg(cls='', title=None):
    rects = []
    for j, r in enumerate(MARK_09):
        for i, c in enumerate(r):
            if c == '█':
                rects.append(f'<rect x="{i*10+0.7}" y="{j*10+0.7}" width="8.6" height="8.6"/>')
    lab = f'role="img" aria-label="{title}"' if title else 'aria-hidden="true"'
    return f'<svg class="{cls}" viewBox="0 0 120 140" fill="currentColor" {lab}>{"".join(rects)}</svg>'


def esc(s): return html.escape(s, quote=True)


MANIFEST = json.load(open(os.path.join(ROOT, 'media', 'manifest.json')))


def media(name, pre, thumb=False):
    m = MANIFEST[name]
    if thumb and os.path.exists(os.path.join(ROOT, 'media', 'thumb', os.path.splitext(name)[0] + '.webp')):
        return f'{pre}media/thumb/{os.path.splitext(name)[0]}.webp'
    return f'{pre}media/{m["file"]}'


_WALL = {}
def wall_src(name, pre, gray=False):
    """A small cover for the project walls. gray=True bakes in the dimmed black and white look,
    so the browser has no filter to apply. The preview inlines it, so it adds no files."""
    import base64, io
    key = (name, gray)
    if not gray and not os.environ.get('NO_SRCSET'):
        return media(name, pre, thumb=True)
    def make():
        from PIL import Image, ImageEnhance
        im = Image.open(os.path.join(ROOT, 'media', MANIFEST[name]['file'])).convert('RGB')
        im.thumbnail((420, 420))
        if gray:
            im = ImageEnhance.Brightness(im.convert('L').convert('RGB')).enhance(0.5)
        return im
    if not os.environ.get('NO_SRCSET'):
        out = os.path.join(ROOT, 'media', 'thumb', 'g-' + os.path.splitext(name)[0] + '.webp')
        if not os.path.exists(out): make().save(out, 'WEBP', quality=70)
        return f'{pre}media/thumb/g-{os.path.splitext(name)[0]}.webp'
    if key not in _WALL:
        b = io.BytesIO(); make().save(b, 'WEBP', quality=62)
        _WALL[key] = 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode()
    return _WALL[key]


def wall_data(pre, order=None, gray=False):
    return '<script type="application/json" id="wall-data">' + json.dumps({x: wall_src(PROJECTS[x]['COVER'], pre, gray) for x in (order or WORK_ORDER) if PROJECTS[x].get('COVER')}) + '</script>'


def small_variant(name):
    """A 1000px-wide copy for phones and half-width layouts, made once and kept in media/s."""
    m = MANIFEST[name]
    if m['w'] <= 1100 or not m['file'].endswith('.webp'): return None
    out = os.path.join(ROOT, 'media', 's', m['file'])
    if not os.path.exists(out):
        try:
            from PIL import Image
        except ImportError:  # e.g. on a build server without Pillow: just serve the full image
            return None
        os.makedirs(os.path.dirname(out), exist_ok=True)
        im = Image.open(os.path.join(ROOT, 'media', m['file']))
        im = im.resize((1000, round(im.height * 1000 / im.width)), Image.LANCZOS)
        im.save(out, 'WEBP', quality=80, method=5)
    return out


def is_video(name): return MANIFEST[name]['file'].endswith('.mp4')


def visual(name, pre):
    """An <img> or a silent looping <video> (GIFs become videos)."""
    m = MANIFEST[name]
    if is_video(name):
        snd = '<button class="snd caps" type="button" aria-pressed="false">Sound on</button>' if m.get('audio') else ''
        # the file is only fetched as it nears the screen (see main.js)
        return f'<figure class="reveal{" has-snd" if snd else ""}"><video data-auto muted loop playsinline preload="none" width="{m["w"]}" height="{m["h"]}" data-src="{media(name, pre)}"></video>{snd}</figure>'
    small = None if os.environ.get('NO_SRCSET') else small_variant(name)
    ss = f' srcset="{pre}media/s/{os.path.basename(small)} 1000w, {media(name, pre)} {m["w"]}w" sizes="(max-width: 820px) 100vw, 1000px"' if small else ''
    return f'<figure class="reveal"><img src="{media(name, pre)}"{ss} width="{m["w"]}" height="{m["h"]}" alt="" loading="lazy" decoding="async"></figure>'


def parse(path):
    p = {'blocks': [], 'P_intro': []}
    seen_body = False
    for line in open(path, encoding='utf-8'):
        line = line.rstrip('\n')
        if not line.strip():
            continue
        key, _, val = line.partition(' ')
        if key in ('SLUG', 'TITLE', 'CARD', 'COVER', 'TAGS', 'CLIENT', 'TEAM', 'YEAR', 'MEDIUM', 'STATUS', 'HERO'):
            p[key] = val
        elif key == 'CREDIT':
            p.setdefault('CREDIT', []).append([x.strip() for x in val.split('|', 1)])
        elif key == 'SUMLINK':
            p['SUMLINK'] = [x.strip() for x in val.split('|', 1)]
        elif key == 'SUM':
            p.setdefault('SUM', []).append([x.strip() for x in val.split('|', 1)])
        elif key == 'EARLIER':
            p['EARLIER'] = True
        elif key == 'TITLEBREAK':
            p['TITLEBREAK'] = True
        elif key == 'VIDEO':
            p['VIDEO'] = val.split()
        elif key == 'P' and not seen_body:
            p['P_intro'].append(val)
        else:
            seen_body = True
            p['blocks'].append((key, val))
    return p


PROJECTS = {}
for f in sorted(os.listdir(os.path.join(ROOT, 'content'))):
    if f.endswith('.txt'):
        pr = parse(os.path.join(ROOT, 'content', f))
        PROJECTS[pr['SLUG']] = pr


SITE = 'https://danikh.design'
DEFAULT_DESC = 'Danikh Nizam is a multidisciplinary designer at the NUS Division of Industrial Design, working across HCI research, interaction design and spatial computing.'
JSONLD = '<script type="application/ld+json">' + json.dumps({
    '@context': 'https://schema.org', '@graph': [
        {'@type': 'WebSite', 'name': 'danikh.design', 'alternateName': 'Danikh Nizam', 'url': SITE + '/'},
        {'@type': 'Person', 'name': 'Danikh Nizam', 'url': SITE + '/', 'jobTitle': 'Designer and HCI researcher',
         'alumniOf': 'National University of Singapore',
         'sameAs': ['https://www.linkedin.com/in/danikhnizam', 'https://www.behance.net/danikh', 'https://www.instagram.com/danikh.design/']}]}) + '</script>\n'
INTRO_HEAD = '<script>try{if(!sessionStorage.getItem("intro")){document.documentElement.classList.add("intro");sessionStorage.setItem("intro","1")}}catch(e){document.documentElement.classList.add("intro")}</script>\n'


WM_HINT = '<div class="wm-hint caps" id="wm-hint"><span data-hint></span><button type="button" class="wm-btn wm-sub caps" id="wm-restart">Restart</button><button type="button" class="wm-btn wm-sub caps" id="wm-sound" aria-pressed="true">Sound on</button><button type="button" class="wm-btn caps" id="wm-game">Insert coin</button></div>'

def page(title, body, pre, current='', home=False, path='/', desc=DEFAULT_DESC, extra_head=''):
    nav = [('About', f'{pre}index.html#about', 'about'), ('Work', f'{pre}projects/index.html', 'work'), ('Info', f'{pre}information.html', 'info')]
    navh = ''.join(f'<a class="caps" href="{h}"{" aria-current=\"page\"" if k == current else ""}>{n}</a>' for n, h, k in nav)
    links = ''.join(f'<li><a href="{h}"{"" if h.startswith("mailto") else " target=\"_blank\" rel=\"noopener\""}>{esc(n)}<span aria-hidden="true">↗</span></a></li>' for n, h in LINKS)
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{SITE}{path}">
<meta property="og:site_name" content="danikh.design">
<meta property="og:type" content="website">
<meta property="og:url" content="{SITE}{path}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{SITE}/og.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0F0E0E">
<link rel="icon" href="{pre}favicon.ico" sizes="48x48">
<link rel="icon" href="{pre}favicon.svg" type="image/svg+xml">
<link rel="icon" href="{pre}favicon-96.png" type="image/png" sizes="96x96">
<link rel="apple-touch-icon" href="{pre}apple-touch-icon.png">
{JSONLD if home else ''}
<link rel="preload" href="{pre}fonts/switzer-latin-500-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{pre}style.css">
{extra_head}{INTRO_HEAD if home else ''}</head>
<body class="{'is-home' if home else 'is-sub'}">
{'<div class="wm-stage"><canvas id="wordmark" aria-hidden="true"></canvas>' + WM_HINT + '</div>' if home else ''}
<header class="site-header">
  <a class="brand caps" href="{pre}index.html">{mark_svg(title="danikh")}<span>Danikh Nizam</span></a>
  <nav aria-label="Main">{navh}</nav>
</header>
<main>
{body}
</main>
<footer class="site-footer" id="contact">
  <div class="wrap">
    <div class="foot-grid">
      <p class="big reveal">Let’s<br>connect</p>
      <ul class="foot-links reveal">{links}</ul>
    </div>
    <div class="foot-base caps">
      <a class="brand" href="{pre}index.html">{mark_svg()}<span>Danikh Nizam</span></a>
      <span>{YEAR} ® Danikh Nizam</span>
    </div>
  </div>
</footer>
<script>window.WORDMARK={json.dumps(WORDMARK)};window.MARK={json.dumps(bits(MARK_09))};</script>
<script src="{pre}main.js" defer></script>
</body>
</html>
'''


def card(p, pre, idx=None):
    wip = '<span class="wip caps"><i></i>In progress</span>' if p.get('STATUS') else ''
    num = f'<span class="card-num caps">{idx:02d}</span>' if idx else ''
    year = p.get('YEAR', '2026')
    tags = ' · '.join(t.strip() for t in p['TAGS'].split(','))
    return f'''<a class="card reveal" href="{pre}projects/{p["SLUG"]}.html">
  <div class="thumb"><img src="{media(p["COVER"], pre, thumb=True)}" width="1000" height="667" alt="{esc(p["TITLE"])} cover" loading="lazy">{wip}<span class="view caps">View project ↗</span></div>
  <div class="card-row">{num}<h3>{esc(p.get("CARD", p["TITLE"]))}</h3><span class="card-year caps">{year}</span></div>
  <p class="tags">{esc(tags)}</p>
</a>'''


def home():
    pre = ''
    ext = ' target="_blank" rel="noopener"'
    cards = ''.join(card(PROJECTS[s], pre) for s in HOME_ORDER)
    now = EXPERIENCE[0]
    recent = ''.join(f'''<a class="snap reveal" href="information.html">
  <span class="caps mute">{e["when"]}</span>
  <span class="snap-org">{esc(e["org"])}</span>
  <span class="snap-role mute">{esc(e["role"])}</span>
  <span class="snap-arrow" aria-hidden="true">→</span>
</a>''' for e in EXPERIENCE[:3])
    conn = ''.join(f'<a href="{h}"{"" if h.startswith("mailto") else ext}>{esc(n)}{"" if h.startswith("mailto") else " ↗"}</a>' for n, h in LINKS)
    body = f'''<section class="hero">
  <h1 class="sr-only">Danikh Nizam — danikh.design</h1>
  <div class="hero-bar caps">
    <p>Exploring the intersections of the human experience, design, and technology.</p>
  </div>
</section>

<section class="h-intro" id="about">
  <div class="wrap">
    <h2 class="info-h caps reveal"><span>About</span></h2>
    <div class="h-intro-grid">
      <div>
        <p class="h-big reveal">Hello, I’m Danikh. My interest lies in how people think, feel and interact with technology, and how design can make those experiences <span class="mute">clearer, kinder and more human.</span></p>
        <div class="h-cols">
          <p class="about-lead reveal">Designer and HCI researcher studying Industrial Design at NUS, with an interest in the moments where people meet technology. Design, to me, is how technology can help people grow and live better, while bringing back what makes us human: curiosity, connection, and the simple joy of being present. Whether through a screen, an object or a space, the human experience comes first.</p>
          <p class="about-lead mute reveal">2001: A Space Odyssey is a big part of why. HAL works alongside the crew as a conversational partner, speaking in a calm voice and seeming confident, capable, even emotional. More than fifty years on, those same qualities shape what we expect from the AI we talk to today. Science fiction lets us look at the hopes, fears and assumptions we bring to technology. So if yesterday’s films imagined our present, what better questions could they help us ask about the systems we are building now?</p>
        </div>
        <div class="h-actions reveal">
          <a class="btn" href="projects/index.html">{mark_svg()}<span>See project archive</span><span class="caps mute">→</span></a>
          <a class="btn ghost" href="{CV_FILE}" download="Danikh_Nizam_CV.pdf"><span>Download CV</span><span class="caps mute">PDF</span></a>
        </div>
      </div>
      <figure class="h-photo reveal"><img src="{media('byEzxvRT09h8vi3IyS6BZNsTwVA.jpg', pre)}" alt="Danikh playing bass on stage" loading="lazy"><figcaption class="caps mute">Singapore · Industrial Design, NUS</figcaption></figure>
    </div>
  </div>
</section>

<section class="h-site" id="this-site">
  <div class="wrap">
    <h2 class="info-h caps reveal"><span>About this site</span></h2>
    <div class="h-cols h-site-cols">
      <p class="about-lead reveal">This portfolio is a mix of the work I’ve done and the things I’m into. That’s why the DANIKH.DESIGN wordmark at the top doubles as an arcade game: press “Insert coin” and the letters become invaders, with my pixel logo as your ship.</p>
      <p class="about-lead mute reveal">Some project pages go a step further. Instead of only showing photos and videos, I rebuilt certain artefacts inside them so you can experience what I built, from the DECODE stations to SoundLab’s chords and the Beyond Boundaries panel. Each was redesigned specifically for this portfolio, to work in a browser on desktop and on your phone.</p>
    </div>
  </div>
</section>

<section class="h-work" id="work">
  <div class="wrap">
    <h2 class="info-h caps reveal"><span>Selected work</span></h2>
    <div class="grid-home">{cards}</div>
    {wall_data(pre, HOME_ORDER + ['codedlife'], gray=True)}
    <a class="see-all caps" href="projects/index.html">View project archive <span aria-hidden="true">→</span></a>
  </div>
</section>

<section class="h-ex" id="exhibition">
  <div class="wrap">
    <h2 class="info-h caps reveal"><span>Exhibition</span></h2>
    <a class="ex-card reveal" href="projects/codedlife.html">
      <div class="ex-img"><img src="{media('cl-pillar.jpg', pre)}" alt="The Coded Life pillar at Sengkang MRT station" loading="lazy"></div>
      <div class="ex-txt">
        <p class="caps mute">New Everyday Life, By Design · 14 Nov – 6 Dec 2026</p>
        <h3>Coded Life</h3>
        <p class="ex-lead">A QR code exhibition at Sengkang MRT station, part of New Everyday Life, By Design, presented by the DesignSingapore Council and produced by FARM. With the Interactive Materials Lab, NUS.</p>
        <p class="ex-meta caps mute">My role · Qrossword, the handwritten QR code system</p>
        <span class="link-btn caps">View the exhibition <span aria-hidden="true">→</span></span>
      </div>
    </a>
  </div>
</section>

<section class="h-now">
  <div class="wrap">
    <h2 class="info-h caps reveal"><span>Recently</span></h2>
    <div class="snaps">{recent}</div>
    <div class="h-links caps reveal">{conn}</div>
  </div>
</section>'''
    return page('danikh.design', body, pre, home=True, path='/')


# Similar tags share one filter button on the Work page (the tags shown on each project stay as written).
FILTER_GROUP = {'UX Design': ['UX/UI Design'], 'Service Design': ['Service & Experience Design'],
                'AR/VR': ['Spatial Computing'], '3D UX/UI': ['Spatial Computing', 'UX/UI Design'], 'Furniture Design': ['Product Design'], 'Editorial Design': ['Visual Communication']}


def filter_tags(tags):
    out = []
    for t in (x.strip() for x in tags.split(',')):
        for g in FILTER_GROUP.get(t, [t]):
            if g not in out: out.append(g)
    return out


def work():
    pre = '../'
    tagset = {}
    for sl in WORK_ORDER:
        for t in filter_tags(PROJECTS[sl]['TAGS']):
            tagset[t] = tagset.get(t, 0) + 1
    tags = sorted(tagset, key=lambda t: (-tagset[t], t))
    if 'Human-AI Interaction' in tags and 'Human-Computer Interaction' in tags:
        tags.remove('Human-AI Interaction'); tags.insert(tags.index('Human-Computer Interaction') + 1, 'Human-AI Interaction')
    slug = lambda t: ''.join(ch if ch.isalnum() else '-' for ch in t.lower()).strip('-')
    chips = f'<button class="chip on" type="button" data-f="all">All<span>{len(WORK_ORDER):02d}</span></button>'
    chips += ''.join(f'<button class="chip" type="button" data-f="{slug(t)}">{esc(t)}<span>{tagset[t]:02d}</span></button>' for t in tags)
    rows = ''
    first_earlier = True
    for i, sl in enumerate(WORK_ORDER):
        p = PROJECTS[sl]
        if p.get('EARLIER') and first_earlier:
            first_earlier = False
            ys = sorted(int(PROJECTS[x].get('YEAR', 0)) for x in WORK_ORDER if PROJECTS[x].get('EARLIER'))
            rows += f'<div class="earlier-h reveal"><h2>Earlier work</h2><p class="caps mute">{ys[0]} – {ys[-1]}</p></div><div class="earlier-grid">'
        ts = [t.strip() for t in p['TAGS'].split(',')]
        fs = filter_tags(p['TAGS'])
        wip = '<span class="wip caps"><i></i>In progress</span>' if p.get('STATUS') else ''
        rows += f'''<a class="proj reveal{' early' if p.get('EARLIER') else ''}" id="{p["SLUG"]}" href="../projects/{p["SLUG"]}.html" data-tags="{' '.join(slug(t) for t in fs)}">
  <div class="proj-img"><img src="{media(p["COVER"], pre)}" width="{MANIFEST[p["COVER"]]["w"]}" height="{MANIFEST[p["COVER"]]["h"]}" alt="{esc(p["TITLE"])} cover" loading="{'eager' if i < 2 else 'lazy'}" decoding="async">{wip}<span class="view caps">View project ↗</span></div>
  <div class="proj-info">
    <h2>{esc(p.get("CARD", p["TITLE"]))}</h2>
    <ul class="proj-tags">{''.join(f'<li>{esc(t)}</li>' for t in ts)}</ul>
    <span class="caps mute proj-year">{p.get('YEAR', '2026')}</span>
  </div>
</a>'''
    if not first_earlier:
        rows += '</div>'
    body = wall_data(pre) + f'''<section class="wrap work-head">
  <h1 class="reveal">Project Archive</h1>
  <p class="reveal">Everything I’ve worked on, from studio projects and research to side experiments. Feel free to explore, and use the filters to narrow things down.</p>
</section>
<div class="filters" role="toolbar" aria-label="Filter projects">
  <div class="wrap"><div class="chips-row">{chips}</div><p class="f-count caps mute" aria-live="polite">Showing {len(WORK_ORDER):02d} projects</p></div>
</div>
<section class="proj-list">
  <div class="wrap">{rows}<p class="f-empty caps mute" hidden>No projects with that tag yet.</p></div>
</section>'''
    return page('Work · danikh.design', body, pre, current='work', path='/projects')


def title_html(p):
    t = p["TITLE"]
    if p.get("TITLEBREAK") and ": " in t:
        a, b = t.split(": ", 1)
        import re as _re
        b = _re.sub(r'(\([^)]*\))', r'<span class="nw">\1</span>', esc(b))
        return f'{esc(a)}:<br><span class="nobr">{b}</span>'
    return esc(t)


def project(slug):
    pre = '../'
    p = PROJECTS[slug]
    lead = ''.join(f'<p>{esc(x)}</p>' for x in p['P_intro'])
    meta = ''
    for k, lab in (('CLIENT', 'Client'), ('TEAM', 'Team members'), ('YEAR', 'Year'), ('MEDIUM', 'Medium')):
        if p.get(k):
            meta += f'<div><dt class="caps">{lab}</dt><dd>{esc(p[k])}</dd></div>'
    wip = '<p class="wip-note caps">Case study in progress</p>' if p.get('STATUS') else ''
    combined = bool(p.get('SUM'))
    if combined:
        # one block: what it is and my role on the left, every credit on the right
        cr = ''.join(f'<div><dt class="caps">{esc(lab)}</dt><dd>{esc(v)}</dd></div>' for lab, v in p.get('CREDIT', []))
        meta = meta.replace('<div><dt class="caps">Year', cr + '<div><dt class="caps">Year', 1) if 'caps">Year' in meta else meta + cr
        for a, t in p['SUM']:
            if a.lower() == 'credits': meta += f'<div><dt class="caps">Credits</dt><dd>{esc(t)}</dd></div>'
        main = ''.join(f'<div class="ps-item{" ps-role" if a.lower() == "my role" else ""}"><p class="caps">{esc(a)}</p><p>{esc(t)}</p></div>' for a, t in p['SUM'] if a.lower() != 'credits')
        if p.get('SUMLINK'):
            lab, u = p['SUMLINK']
            main += f'<p class="p-link"><a class="link-btn caps" href="{esc(u)}" target="_blank" rel="noopener">{esc(lab)} <span aria-hidden="true">↗</span></a></p>'
        summary = f'<section class="p-all reveal"><div class="ps-main">{main}</div><dl class="meta">{meta}</dl></section>'
    else:
      summary = ('<section class="p-sum reveal"><p class="caps mute">In short</p><dl>' + ''.join(f'<div><dt class="caps">{esc(a)}</dt><dd>{esc(t)}</dd></div>' for a, t in p['SUM']) + '</dl></section>') if p.get('SUM') else ''

    out = []
    if combined and p['P_intro']:
        out.append(f'<div class="text reveal">{lead}</div>')
    if p.get('VIDEO'):
        kind, vid = p['VIDEO'][0], p['VIDEO'][1]
        if kind == 'file':
            m = MANIFEST[vid]; po = p['VIDEO'][2] if len(p['VIDEO']) > 2 else ''
            pa = f' poster="{media(po, pre)}"' if po else ''
            out.append(f'<p class="caps mute label">Demo video</p><figure class="reveal film"><video controls playsinline preload="none"{pa} width="{m["w"]}" height="{m["h"]}" src="{media(vid, pre)}"></video></figure>')
        src = None if kind == 'file' else f'https://www.youtube-nocookie.com/embed/{vid}?rel=0' if kind == 'yt' else f'https://player.vimeo.com/video/{vid}?dnt=1'
        if src: out.append(f'<p class="caps mute label">Demo video</p><div class="video reveal"><iframe src="{src}" title="{esc(p["TITLE"])} demo video" loading="lazy" allow="autoplay; fullscreen; picture-in-picture" allowfullscreen></iframe></div>')
    text = []

    def flush():
        if text:
            out.append(f'<div class="text reveal">{"".join(text)}</div>')
            text.clear()

    table = []

    def close_table():
        if table:
            head = ''.join(f'<th>{esc(c.strip())}</th>' for c in table[0][1].split('|')) if table[0][0] == 'TH' else ''
            rows = ''.join('<tr>' + ''.join(f'<td>{esc(c.strip())}</td>' for c in v.split('|')) + '</tr>' for k, v in table if k == 'TR')
            text.append(f'<div class="tbl"><table>{f"<thead><tr>{head}</tr></thead>" if head else ""}<tbody>{rows}</tbody></table></div>')
            table.clear()

    wheel = []

    def close_wheel():
        if not wheel:
            return
        n = len(wheel)
        picks = ''.join(f'<button type="button" class="wh-i" role="tab" data-i="{i}" aria-selected="{"true" if i == 0 else "false"}"><span class="wh-n">{i + 1:02d}</span><span class="wh-t">{esc(t)}</span></button>' for i, (t, im, live, tx) in enumerate(wheel))
        slides = ''
        for i, (t, im, live, tx) in enumerate(wheel):
            m = MANIFEST[im]
            src = media(im, pre)
            if is_video(im):
                img = f'<video muted loop playsinline preload="none" data-src="{src}" width="{m["w"]}" height="{m["h"]}"></video>'
            else:
                img = f'<img {"src" if i == 0 else "data-src"}="{src}"{' loading="lazy"' if i == 0 else ''} width="{m["w"]}" height="{m["h"]}" alt="{esc(t)}" decoding="async">'
            lv = (f'<div class="wh-live"><button type="button" class="wh-try caps" data-src="{pre}media/demos/path-website/index.html?part={live}">Try it live</button>'
                  f'<a class="caps" href="https://nikhoftime.github.io/MFS-Website/" target="_blank" rel="noopener">Full site ↗</a></div>') if live else ''
            slides += (f'<div class="wh-s{" on" if i == 0 else ""}{" is-live" if live else ""}" data-i="{i}" role="tabpanel" aria-label="{esc(t)}">'
                       f'<div class="wh-img{" fit" if abs(m["w"] / m["h"] - 16 / 9) > 0.05 and not live else ""}">{img}</div>'
                       f'<div class="wh-cap"><p class="caps mute wh-c"><span>{i + 1:02d}</span> / {n:02d}{" · <em>Interactive</em>" if live else ""}</p><h3>{esc(t)}</h3><p>{esc(tx)}</p>{lv}</div></div>')
        bar = ''.join(f'<button type="button" class="wh-dot{" on" if i == 0 else ""}" data-i="{i}" aria-label="{esc(t)}"></button>' for i, (t, im, live, tx) in enumerate(wheel))
        out.append(f'<div class="wheel reveal" data-n="{n}" tabindex="0" aria-roledescription="carousel" aria-label="Gallery">'
                   f'<div class="wh-stage">{slides}'
                   f'<button type="button" class="wh-arr wh-prev" aria-label="Previous"><svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path d="M14.5 6 8.5 12l6 6" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg></button><button type="button" class="wh-arr wh-next" aria-label="Next"><svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path d="M9.5 6l6 6-6 6" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg></button></div>'
                   f'<div class="wh-bar">{bar}</div></div>')
        wheel.clear()

    for key, val in p['blocks']:
        if key == 'W':
            flush()
            t, im, live, tx = [c.strip() for c in val.split('|', 3)]
            wheel.append((t, im, live, tx)); continue
        close_wheel()
        if key in ('TH', 'TR'):
            table.append((key, val)); continue
        close_table()
        if key == 'H':
            flush(); text.append(f'<h2>{esc(val)}</h2>')
        elif key == 'P':
            text.append(f'<p>{esc(val)}</p>')
        else:
            flush()
            if key in ('IMG', 'MP4'):
                out.append(visual(val, pre))
            elif key == 'IMGSM':
                out.append(visual(val, pre).replace('<figure class="reveal', '<figure class="reveal small', 1))
            elif key in ('PAIR', 'MP4GRID'):
                out.append('<div class="pair">' + ''.join(visual(n, pre) for n in val.split()) + '</div>')
            elif key == 'CAP':
                out.append(f'<p class="cap caps">{esc(val)}</p>')
            elif key == 'LINK':
                lab, _, url = val.partition('|')
                u = url.strip(); ext = u.startswith('http')
                out.append(f'<p class="p-link reveal"><a class="link-btn caps" href="{esc(u)}"{' target="_blank" rel="noopener"' if ext else ''}>{esc(lab.strip())} <span aria-hidden="true">{'↗' if ext else '→'}</span></a></p>')
            elif key == 'FILM':
                # FILM file.mp4 | poster image: a full film with player controls
                f, _, poster = [c.strip() for c in val.partition('|')]
                m = MANIFEST[f]
                po = f' poster="{media(poster, pre)}"' if poster else ''
                out.append(f'<figure class="reveal film"><video controls playsinline preload="none"{po} width="{m["w"]}" height="{m["h"]}" src="{media(f, pre)}"></video></figure>')
            elif key == 'SHOTS':
                # screenshots and other non-live media: smaller, centred, laid out symmetrically
                names = val.split()
                out.append(f'<div class="shots n{len(names)}">' + ''.join(visual(n, pre) for n in names) + '</div>')
            elif key == 'GRID':
                out.append('<div class="pair grid3">' + ''.join(visual(n, pre) for n in val.split()) + '</div>')
            elif key in ('FRAME', 'PART'):
                # FRAME <file in media/demos, or empty> | name | poster | phone poster | live url | button label
                # PART  <section of the fictional MFS website> | name | poster | phone poster | live url | button label
                # The interactive loads only when the visitor asks for it, so the page stays light.
                src, name, poster, mposter, url, lab = [c.strip() for c in val.split('|')]
                m = MANIFEST[poster]
                img = f'<img src="{pre}media/{m["file"]}" width="{m["w"]}" height="{m["h"]}" alt="{esc(name)}" loading="lazy">'
                if mposter:
                    img = f'<picture><source media="(max-width:700px)" srcset="{pre}media/{MANIFEST[mposter]["file"]}">{img}</picture>'
                if key == 'PART':
                    src = f'path-website/index.html?part={src}'
                if src:
                    # runs inline straight away (lazy: only once it scrolls near the screen)
                    full = (f'<button type="button" class="frame-full caps">Full screen ↗</button>' if url == 'FULLSCREEN'
                            else f'<a href="{esc(url)}" target="_blank" rel="noopener">Open full screen ↗</a>')
                    out.append(f'<div class="{"frame part on reveal" if key == "PART" else "frame on reveal"}"><div class="frame-top caps"><i></i><i></i><i></i><span>{esc(name)}</span><em>Live</em></div><div class="frame-view"><iframe src="{pre}media/demos/{src}" title="{esc(name)}" loading="lazy" allow="autoplay; fullscreen" allowfullscreen></iframe></div><p class="frame-bar caps"><span>Interactive · {"scroll inside to explore" if key == "PART" else "click to explore"}</span>{full}</p></div>')
                    continue
                else:
                    go = f'<a class="frame-go" href="{esc(url)}" target="_blank" rel="noopener"><span class="caps">{esc(lab)} ↗</span></a>'
                    note = '<span>Interactive · opens in a new tab</span>'
                cls = 'frame part reveal' if key == 'PART' else 'frame reveal'
                out.append(f'<div class="{cls}"><div class="frame-top caps"><i></i><i></i><i></i><span>{esc(name)}</span><em class="ext">Opens in a new tab</em></div><div class="frame-view">{img}{go}</div><p class="frame-bar caps">{note}<a href="{esc(url)}" target="_blank" rel="noopener">Open full screen ↗</a></p></div>')
            elif key == 'EMBED':
                out.append(f'<div class="embed reveal"><iframe src="{pre}media/demos/{val}" title="Interactive demo" loading="lazy" scrolling="no"></iframe></div>')
    close_wheel()
    close_table()
    flush()

    i = WORK_ORDER.index(slug)
    prv = PROJECTS[WORK_ORDER[i - 1]] if i > 0 else None
    nxt = PROJECTS[WORK_ORDER[i + 1]] if i < len(WORK_ORDER) - 1 else None
    nav = '<div class="p-nav">'
    nav += f'<a class="prev" href="{prv["SLUG"]}.html"><span class="caps">‹ Previous</span><strong>{esc(prv.get("CARD", prv["TITLE"]))}</strong></a>' if prv else '<span></span>'
    nav += f'<a class="next" href="{nxt["SLUG"]}.html"><span class="caps">Next ›</span><strong>{esc(nxt.get("CARD", nxt["TITLE"]))}</strong></a>' if nxt else '<span></span>'
    nav += '</div>'

    body = f'''<article class="wrap">
  <header class="p-head">
    <h1>{title_html(p)}</h1>
    <p class="tags caps">{esc(p["TAGS"])}</p>
  </header>
  {f'<div class="p-hero">{visual(p["HERO"], pre)}</div>' if p.get('HERO') else ''}
  {summary}
  {'' if combined else f'<div class="p-intro"><div class="lead">{lead}{wip}</div><dl class="meta">{meta}</dl></div>'}
  <div class="p-body">{"".join(out)}</div>
  {nav}
</article>'''
    desc = (p['P_intro'][0] if p['P_intro'] else p['TITLE'])[:160]
    return page(f'{p["TITLE"]} · danikh.design', body, pre, current='work', path=f'/projects/{slug}', desc=desc)


# ---------- Information page (from CV + LinkedIn, Nov 2026) ----------
CV_FILE = 'files/Danikh_Nizam_CV.pdf'
ABOUT = ('Industrial Design student at NUS exploring how people interact with emerging technologies. '
         'My work spans HCI research, interaction, UX and service design, and Agentic AI workflows, with experience across healthcare, '
         'public services and interactive systems. I’m particularly interested in understanding people, '
         'simplifying complex systems, and exploring what technology can make possible.')
FOCUS = 'Human-Computer Interaction Research · UX Design · Emerging Technologies'

EXPERIENCE = [
    dict(org='Interactive Materials Lab', url='https://interactivematerials.info/', where='NUS Department of Design',
         role='Design Researcher', when='Jul 2026 – Present', now=True,
         points=['Design Researcher for the Design Trail at Sengkang MRT Station, part of New Everyday Life, By Design (NELBD), a design journey across the North East Line presented by DesignSingapore Council and produced by FARM.',
                 'Designed and built the team’s tool for Qrossword, a handwritten QR code artefact. Instead of lettering every module by hand, the team could write letters into individual modules with an iPad or mouse, select single modules or groups, and duplicate letters with shortcuts.']),
    dict(org='Joyful Experiences in Design and Interaction (JEDI) Lab', url='https://joyfuldesignlab.com/team-1', where='NUS Department of Design',
         role='Undergraduate HCI Researcher & Designer', when='Mar 2026 – Present', now=True,
         note='Also Undergraduate Research Experience (UREx) Fellow, Aug 2026.',
         points=['Conducting HCI and UX research on human-AI interaction, AI experiences and personal informatics, exploring reflection beyond traditional self-tracking.',
                 'Applying Research through Design (RtD), UX research and interaction design to prototype and evaluate AI-powered reflective technologies.',
                 'Designing technology probes, speculative concepts and interactive artefacts that investigate emerging interactions between people, AI and everyday behaviour.']),
    dict(org='Ministry of Culture, Community and Youth (MCCY)', where='MCCY HQ & Syariah Court',
         role='Digital Transformation Intern', when='May 2026 – Aug 2026',
         points=['Contributed to public-sector digital transformation through UX research, workflow analysis and service mapping, improving citizen and officer experiences.',
                 'Designed and prototyped AI-assisted filing experiences for the Syariah Court Portal, exploring how Agentic AI can guide citizens through complex government processes.',
                 'Mapped end-to-end Syariah Court workflows and built a structured knowledge base to support Agentic AI integration, translating business logic into requirements.',
                 'Ran usability tests of the AI-assisted filing experience with participants unfamiliar with the process.'],
         # the website keeps public-sector work general; the CV keeps the detail above
         site_where='MCCY HQ',
         site_points=['Contributed to public-sector digital transformation through UX research, service design and workflow analysis.',
                      'Designed, prototyped and usability-tested new service experiences for citizens and officers, exploring how Agentic AI workflows can guide people through complex processes.']),
    dict(org='Interactive 3D Design Lab (i3D)', url='https://www.i3d.design/', where='NUS Department of Design',
         role='Undergraduate HCI Researcher & Designer', when='Jun 2025 – Jan 2026',
         points=['Designed and prototyped immersive 3D UX/UI for Apple Vision Pro, applying user research and interaction design to healthcare training.',
                 'Built visionOS and Swift prototypes with NUH’s Emergency Medicine Department and the NUS Centre for Healthcare Simulation for on-call and mass casualty incident (MCI) training.',
                 'Conducted contextual inquiry and field observations in the Emergency Department, translating clinical needs into simulation experiences.',
                 'Co-authored a paper accepted at CAADRIA 2026. Worked under Assistant Professor Gabriel Lipkowitz.']),
    dict(org='NTUC Club', where='Downtown East', role='Customer Experience Design Intern', when='Mar 2021 – Aug 2021',
         points=['Analysed guest feedback in Salesforce Service Cloud to find pain points and improve service delivery.',
                 'Worked with Guest Services Officers to improve end-to-end guest experiences across information counters.',
                 'Designed Spark AR social filters and staff engagement initiatives, reducing administrative workload by 50%.',
                 'Designed early brand assets for SG Furkids (now My Pet Kaki) and helped grow it to 700+ members.']),
]
EDUCATION = [
    ('National University of Singapore', 'Bachelor of Arts in Industrial Design', 'Aug 2024 – Present',
     ['Pioneer House Band, MalPHunction: lead singer, guitarist, bassist', 'DID FOC 2025 Gamemaster']),
    ('Nanyang Polytechnic', 'Diploma in Industrial Design', 'Apr 2019 – Apr 2022',
     ['Director’s List (2021/22)', 'NTUC Club Furniture Design, Category Winner', 'Outward Bound Singapore, Best Project Award', 'Exhibited at SDM Gradshow 2022']),
]
PUBLICATIONS = [('CAADRIA 2026', 'Development and User Evaluation of Multimodal Spatial Computing Applications for 3D Generative Workflows in Early-Stage Architectural Design Processes',
                 'Co-author', 'https://papers.cumincad.org/data/works/att/caadria2026_712.pdf')]
EXHIBITIONS = [('NELBD 2026', 'New Everyday Life, By Design', 'A Design Journey Across The North East Line. Presented by DesignSingapore Council, produced by FARM. Design Trail at Sengkang MRT Station, with the Interactive Materials Lab.', '14 Nov – 6 Dec 2026', 'https://designsingapore.org/nelbd/')]
MENTORSHIP = [('Hacking Spatial Computing', 'Design Mentor', 'The world’s first university hackathon for Apple Vision Pro.', 'https://hackspatialcomputing.com')]
SKILLS = [('Research', 'HCI · Human-AI Interaction · User Research · Research through Design · Contextual Inquiry · Usability Testing'),
          ('Design', 'Interaction Design · UX/UI Design · Service Design · Prototyping · Experience Design · 3D UX/UI · Design Research'),
          ('AI & Emerging Tech', 'Agentic AI · Generative AI · LLM Prototyping · Spatial Computing'),
          ('Tools', 'Figma · SwiftUI · visionOS · HTML/CSS/JavaScript · Rhino · Twinmotion · Adobe Creative Suite')]
INTERESTS = ['Human-Computer Interaction', 'Human-AI Interaction', 'AI & Public Services', 'Interactive Systems', 'Emerging Technologies', 'Everyday Human-Technology Interaction']


def info():
    pre = ''
    ext = ' target="_blank" rel="noopener"'
    exp = ''
    for n, e in enumerate(EXPERIENCE):
        pts = ''.join(f'<li>{esc(p)}</li>' for p in e.get('site_points', e['points']))
        exp += f'''<article class="xp reveal">
  <div class="xp-when caps">{e["when"]}{'<span class="now">Now</span>' if e.get('now') else ''}</div>
  <div class="xp-main">
    <h3>{f'<a class="ul" href="{e["url"]}"{ext}>{esc(e["org"])} ↗</a>' if e.get("url") else esc(e["org"])}</h3>
    <p class="xp-role">{esc(e["role"])} <span class="mute">· {esc(e.get("site_where", e["where"]))}</span></p>
    {f'<ul>{pts}</ul>' if pts else ''}
    {f'<p class="xp-note mute">{esc(e["note"])}</p>' if e.get('note') else ''}
  </div>
</article>'''
    edu = ''.join(f'''<div class="side-item"><h4>{esc(a)}</h4><p>{esc(b)}</p><p class="caps mute">{c}</p>
  <ul class="dots">{''.join(f'<li>{esc(x)}</li>' for x in d)}</ul></div>''' for a, b, c, d in EDUCATION)
    pubs = ''.join(f'''<div class="side-item"><p class="caps tag">{esc(v)}</p><a class="ul" href="{u}"{ext}>{esc(t)} ↗</a><p class="mute">{esc(r)}</p></div>''' for v, t, r, u in PUBLICATIONS)
    exh = ''.join(f'''<div class="side-item"><p class="caps tag">{esc(v)}</p><a class="ul" href="{u}"{ext}><h4>{esc(t)} ↗</h4></a><p>{esc(r)}</p><p class="caps mute">{esc(d)}</p></div>''' for v, t, r, d, u in EXHIBITIONS)
    ment = ''.join(f'''<div class="side-item"><a class="ul" href="{u}"{ext}><h4>{esc(a)} ↗</h4></a><p>{esc(b)}</p><p class="mute">{esc(c)}</p></div>''' for a, b, c, u in MENTORSHIP)
    skills = ''.join(f'<div class="side-item"><h4>{esc(a)}</h4><p class="mute">{esc(b)}</p></div>' for a, b in SKILLS)
    chips = ''.join(f'<li>{esc(x)}</li>' for x in INTERESTS)
    body = f'''<div class="wrap info2">
  <section class="info-hero">
    <h1 class="reveal">Information</h1>
    <div class="info-hero-grid">
      <p class="about-lead reveal">{esc(ABOUT)}</p>
      <div class="cta reveal">
        <p class="caps mute">{esc(FOCUS)}</p>
        <a class="btn" href="{pre}{CV_FILE}" download="Danikh_Nizam_CV.pdf">{mark_svg()}<span>Download CV</span><span class="caps mute">PDF</span></a>
        <div class="cta-links caps">
          <a href="https://www.linkedin.com/in/danikhnizam"{ext}>LinkedIn ↗</a>
          <a href="mailto:danikhnizam@gmail.com">danikhnizam@gmail.com</a>
        </div>
      </div>
    </div>
  </section>

  <div class="info-grid">
    <section class="info-main">
      <h2 class="info-h caps reveal"><span>Experience</span></h2>
      {exp}
    </section>
    <aside class="info-side">
      <section><h2 class="info-h caps reveal"><span>Education</span></h2><div class="reveal">{edu}</div></section>
      <section><h2 class="info-h caps reveal"><span>Exhibitions</span></h2><div class="reveal">{exh}</div></section>
      <section><h2 class="info-h caps reveal"><span>Publication</span></h2><div class="reveal">{pubs}</div></section>
      <section><h2 class="info-h caps reveal"><span>Mentorship</span></h2><div class="reveal">{ment}</div></section>
      <section><h2 class="info-h caps reveal"><span>Skills &amp; tools</span></h2><div class="reveal">{skills}</div></section>
      <section><h2 class="info-h caps reveal"><span>Research interests</span></h2><ul class="chips reveal">{chips}</ul></section>
    </aside>
  </div>
</div>'''
    return page('Information · danikh.design', body, pre, current='info', path='/information')


def favicon():
    return mark_svg().replace('<svg class=""', '<svg xmlns="http://www.w3.org/2000/svg"').replace('fill="currentColor"', 'fill="#F2F1EE"').replace('viewBox="0 0 120 140"', 'viewBox="-10 0 140 140"')


def build():
    if os.path.exists(DIST):
        shutil.rmtree(DIST)
    os.makedirs(os.path.join(DIST, 'projects'))
    w = lambda rel, s: open(os.path.join(DIST, rel), 'w', encoding='utf-8').write(s)
    w('index.html', home())
    w('information.html', info())
    w('projects/index.html', work())
    for s in PROJECTS:
        w(f'projects/{s}.html', project(s))
    for f in os.listdir(os.path.join(ROOT, 'src', 'icons')):
        shutil.copy(os.path.join(ROOT, 'src', 'icons', f), DIST)
    urls = ['/', '/projects', '/information'] + [f'/projects/{s}' for s in WORK_ORDER]
    w('sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
      + ''.join(f'  <url><loc>{SITE}{u}</loc></url>\n' for u in urls) + '</urlset>\n')
    w('robots.txt', f'User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n')
    shutil.copy(os.path.join(ROOT, 'src', 'style.css'), DIST)
    shutil.copy(os.path.join(ROOT, 'src', 'main.js'), DIST)
    shutil.copytree(os.path.join(ROOT, 'src', 'fonts'), os.path.join(DIST, 'fonts'))
    shutil.copytree(os.path.join(ROOT, 'src', 'files'), os.path.join(DIST, 'files'))
    shutil.copytree(os.path.join(ROOT, 'media'), os.path.join(DIST, 'media'), ignore=shutil.ignore_patterns('manifest.json', *(['s'] if os.environ.get('NO_SRCSET') else [])))
    print('built', len(PROJECTS), 'projects →', DIST)


if __name__ == '__main__':
    build()
