import os, json, subprocess, time
from playwright.sync_api import sync_playwright
A='file:///home/claude/site/plate-src/assets/'; O='file:///home/claude/site/plate-src/'; F='/home/claude/site/src/fonts/'
SIZE={'full':30,'n1':30,'n2':64,'n3':84}
PH=int(os.environ.get('PH','1350'))
def page(label, body, size, right='', extra_css=''):
    L=SIZE[size]
    if size=='n3': right=''
    return f'''<!doctype html><html><head><style>
@font-face{{font-family:S;src:url(file://{F}switzer-latin-400-normal.woff2);font-weight:400}}
@font-face{{font-family:S;src:url(file://{F}switzer-latin-500-normal.woff2);font-weight:500}}
@font-face{{font-family:S;src:url(file://{F}switzer-latin-600-normal.woff2);font-weight:600}}
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{width:2400px;height:{PH}px;overflow:hidden}}
body{{background:#F2F1EE;color:#0F0E0E;font-family:S,sans-serif;--L:{L}px;position:relative}}
.top{{position:absolute;left:88px;right:88px;top:76px;display:flex;justify-content:space-between;font-size:var(--L);font-weight:500;letter-spacing:.02em;text-transform:uppercase;color:#5E5C58;line-height:1}}
.top .r{{color:#8D8B86}}
.stage{{position:absolute;left:88px;right:88px;top:calc(76px + var(--L) + 64px);bottom:88px;display:flex;align-items:center;justify-content:center}}
.card{{border-radius:18px;background:#fff;box-shadow:0 30px 70px rgba(15,14,14,.16),0 3px 10px rgba(15,14,14,.08);display:block;max-width:100%;max-height:100%;object-fit:contain}}
.caps{{text-transform:uppercase;letter-spacing:.02em;font-weight:500}}
.mute{{color:#5E5C58}} .dim{{color:#8D8B86}}
{extra_css}
</style></head><body><div class="top"><span>{label}</span><span class="r">{right}</span></div><div class="stage">{body}</div><script>{FIT}</script></body></html>'''

FIT=r"""
addEventListener('load',()=>{const st=document.querySelector('.stage');const cs=[...st.querySelectorAll('img.card')];if(!cs.length)return;
const W=st.clientWidth,H=st.clientHeight,gap=56,n=cs.length;const tot=cs.reduce((a,c)=>a+c.naturalHeight/c.naturalWidth,0);
let w=Math.min(W,(H-gap*(n-1))/tot);cs.forEach(c=>{c.style.maxWidth='none';c.style.maxHeight='none';c.style.width=w+'px';c.style.height=(w*c.naturalHeight/c.naturalWidth)+'px'});
document.body.dataset.done=1});"""
plates={}
# ---------- Beyond Boundaries ----------
BB='Beyond Boundaries'
steps=[('Approach','Spatial planters define and guide users into the new smoking area.'),
 ('Smoke','Users occupy the space normally for smoke breaks.'),
 ('Detect','Smoking activity is registered through the bin and smoke sensing.'),
 ('Respond','The responsive panel changes as smoking activity accumulates over time.'),
 ('Dispose','Cigarettes are extinguished and discarded at the bin.'),
 ('Reflect','The visual remains visible, creating a subtle moment of reflection.')]
cells=''.join(f'<div class="c"><div class="ic"><img src="{A}j{i+1}.png"></div><div class="t"><span class="n">0{i+1}</span><div><p class="h caps">{t}</p><p class="d mute">{d}</p></div></div></div>' for i,(t,d) in enumerate(steps))
plates['bb-plate-journey']=page('User journey',f'<div class="g">{cells}</div>','full',BB,
 '.g{display:grid;grid-template-columns:repeat(3,1fr);grid-template-rows:1fr 1fr;gap:56px 72px;width:100%;height:100%}.c{display:flex;flex-direction:column;min-height:0}.ic{flex:1;min-height:0;display:flex;align-items:flex-end;justify-content:center;padding-bottom:28px}.ic img{max-height:100%;max-width:88%;object-fit:contain}.t{display:flex;gap:22px;align-items:flex-start;border-top:1.5px solid #D6D4CF;padding-top:22px}.n{font-size:calc(var(--L)*1.05);color:#8D8B86;font-weight:500;line-height:1.15}.h{font-size:calc(var(--L)*1.05);line-height:1.15;margin-bottom:8px}.d{font-size:calc(var(--L)*.95);line-height:1.35}')
for k,(n,t,d) in enumerate([('enclave','Enclave','C-shape · semi-enclosed, communal'),('nook','Nook','L-shape · compact, corner-oriented'),('trail','Trail','Linear · open, directional')]):
    plates[f'bb-plate-{n}']=page(f'Configuration 0{k+1}',f'<img class="r" src="{A}{n}.png"><div class="cap"><p class="h">{t}</p><p class="d mute">{d}</p></div>','n3',BB,
     '.stage{flex-direction:column;align-items:stretch}.r{flex:1;min-height:0;object-fit:contain;width:100%;padding:0 40px 40px}.cap{border-top:2px solid #D6D4CF;padding-top:30px}.h{font-size:calc(var(--L)*1.25);font-weight:500;line-height:1.1;margin-bottom:10px}.d{font-size:calc(var(--L)*.9)}')
pl=[('aloe','Aloe vera'),('philo','Philodendron'),('pothos','Pothos'),('snake','Snake plant'),('fern','Boston fern'),('lily','Peace lily')]
plates['bb-plate-plants']=page('Planting palette','<div class="g">'+''.join(f'<figure><img src="{A}plant-{n}.png"><figcaption>{t}</figcaption></figure>' for n,t in pl)+'</div>','n1',BB,
 '.g{display:grid;grid-template-columns:repeat(3,auto);gap:44px 56px;height:100%;align-content:center}figure{display:flex;flex-direction:column;gap:20px}figure img{height:410px;width:410px;object-fit:cover;border-radius:14px}figcaption{font-size:var(--L);font-weight:500}')
plates['bb-plate-bin']=page('Sensor-integrated bin',f'<div class="row"><figure><img src="{A}bin2.png"><figcaption><b>Exterior</b><span class="mute">Faceted cast-stone body</span></figcaption></figure><figure><img src="{A}bincut.png"><figcaption><b>Section</b><span class="mute">Smoke sensor inside the tube</span></figcaption></figure></div>','n1',BB,
 '.row{display:flex;gap:160px;height:100%;align-items:stretch}figure{display:flex;flex-direction:column;align-items:center;gap:30px;min-height:0}figure img{flex:1;min-height:0;object-fit:contain}figcaption{display:flex;flex-direction:column;align-items:center;gap:8px;font-size:var(--L)}b{font-weight:500}')
plates['bb-plate-packs']=page('Standardised packaging, Singapore',f'<img src="{A}packs.png" class="p"><p class="cr dim">Photo: Health Sciences Authority, Singapore</p>','full','Since 1 July 2020',
 '.stage{flex-direction:column}.p{width:100%;filter:drop-shadow(0 24px 30px rgba(15,14,14,.18))}.cr{position:absolute;right:0;bottom:0;font-size:calc(var(--L)*.8)}')
sys3=[('01 Detect','A smoke sensor in the bin detects and measures smoke concentration.',f'<img src="{A}bincut.png">'),
      ('02 Translate','The data becomes evolving abstract visuals, sent to a thin, flexible screen.',f'<img src="{A}screen.png">'),
      ('03 Visualise','The panel shows patterns that reflect accumulated smoke over time.',f'<img class="ph" src="{A}plaza.png">')]
plates['bb-plate-system']=page('How the panel works','<div class="g">'+''.join(f'<div class="c"><div class="im">{im}</div><div class="t"><p class="h caps">{h}</p><p class="d mute">{d}</p></div></div>' for h,d,im in sys3)+'</div>','full',BB,
 '.g{display:grid;grid-template-columns:1fr 1fr 1.25fr;gap:72px;width:100%;height:100%}.c{display:flex;flex-direction:column;min-height:0}.im{flex:1;min-height:0;display:flex;align-items:center;justify-content:center;padding-bottom:36px}.im img{max-width:100%;max-height:100%;object-fit:contain}.im img.ph{width:100%;height:100%;object-fit:cover;border-radius:14px}.t{border-top:1.5px solid #D6D4CF;padding-top:24px}.h{font-size:calc(var(--L)*1.05);margin-bottom:10px}.d{font-size:calc(var(--L)*.95);line-height:1.35}')
def sw(c,name):
    s=f'background:{c}' if c.startswith('#') or c.startswith('linear') else f'background:url({A}{c}.png) center/cover'
    return f'<div class="s"><i style="{s}"></i><span>{name}</span></div>'
STR='linear-gradient(90deg,#C8102E 0 33.3%,#2B3990 33.3% 66.6%,#F6B21B 66.6%)'
cmf=[('planters','Spatial planters','planter2',[('#3B6B5C','Dark green'),('tex-hdpe-green','HDPE'),('tex-rough-green','Rough'),('#EEEDEA','Snow white'),('tex-stone','Stone'),('tex-sand','Sandblasted')]),
     ('seats','Modular seats','seat',[(STR,'Red, blue, yellow'),('tex-hdpe-blue','HDPE'),('tex-rough-dark','Rough'),('#EEEDEA','Snow white'),('tex-stone','Stone'),('tex-sand','Sandblasted')]),
     ('bin','Sensor-integrated bin','bin2',[('#D9D9D6','Cool grey'),('tex-alu','Aluminium'),('tex-brushed','Brushed'),('#EEEDEA','Snow white'),('tex-stone','Stone'),('tex-sand','Sandblasted')]),
     ('panel','Responsive panel','panel',[('tex-clear','Clear'),('tex-glass','Glass'),('tex-frosted','Frosted')])]
for key,t,r,sws in cmf:
    plates[f'bb-plate-cmf-{key}']=page(t,f'<div class="row"><div class="rd"><img src="{A}{r}.png"></div><div class="sw"><div class="hd dim"><span>Colour</span><span>Material</span><span>Finish</span></div><div class="gr">'+''.join(sw(c,n) for c,n in sws)+'</div></div></div>','n2','CMF',
     '.row{display:flex;gap:90px;width:100%;height:100%;align-items:center}.rd{flex:0 0 36%;height:100%;display:flex;align-items:center;justify-content:center}.rd img{max-width:100%;max-height:100%;object-fit:contain}.sw{flex:1}.hd,.gr{display:grid;grid-template-columns:repeat(3,1fr);column-gap:44px}.hd{font-size:calc(var(--L)*.7);text-transform:uppercase;letter-spacing:.02em;margin-bottom:26px;font-weight:500}.gr{row-gap:48px}.s{display:flex;flex-direction:column;gap:18px}.s i{display:block;aspect-ratio:1;border-radius:12px;box-shadow:inset 0 0 0 2px rgba(15,14,14,.06)}.s span{font-size:calc(var(--L)*.72);font-weight:500;line-height:1.15}')
# ---------- PATH ----------
P='PATH'
holo=['Scoring','Audit','Overview','Rankings','Patterns','Next step']
for i,t in enumerate(holo):
    plates[f'path-plate-holo-{i+1}']=page(f'Hologram · {t}',f'<img class="card" style="background:#000" src="{O}path-web-holo3-{i+1}.png">','n3',P)
def single(name,label,files,size,stack=False):
    body=''.join(f'<img class="card" src="{O}{f}">' for f in files)
    css='.stage{flex-direction:column;gap:56px}' if stack else ''
    plates[name]=page(label,body,size,'Fictional MFS website',css)
single('path-plate-vision','Vision and values',['path-web-mfs-vision.jpg','path-web-mfs-values.jpg'],'n1',True)
single('path-plate-history','History of MFS',['path-web-mfs-history.jpg'],'n2')
single('path-plate-mfsrecord','How MFS came together',['path-web-mfs-record.jpg'],'n2')
single('path-plate-act','Integrated Care Act 2040',['path-web-act.jpg'],'n1')
single('path-plate-actparts','What the Act does',['path-web-act-parts.jpg'],'n1')
single('path-plate-rally','National Day Rally',['path-web-rally.jpg'],'n1')
single('path-plate-agent','MFS Agent',['path-web-agent.jpg'],'n2')
single('path-plate-record','Record access',['path-web-record.jpg'],'n2')
single('path-plate-report','Report a care concern',['path-web-report.jpg'],'n3')
single('path-plate-yearincare','Year in care',['path-web-yearincare.jpg'],'n3')
single('path-plate-ahma',"Ah Ma's console",['path-web-ahma.jpg'],'n3')

plates['bb-plate-poster']=page('A1 poster',f'<img class="card" src="{O}bb-poster-a1.png">','n1',BB)
plates['path-plate-qr-bg']=page('Safety check · QR intro','','n1',P)

M='file:///home/claude/site/plate-src/minda/'
MCSS='.row{display:flex;align-items:center;justify-content:center;gap:110px;height:100%}.row img{filter:drop-shadow(0 26px 34px rgba(15,14,14,.22)) drop-shadow(0 3px 6px rgba(15,14,14,.12))}.row img.ph{height:880px}.row img.wk{height:560px}'
def mrow(items):
    return '<div class="row">'+''.join(f'<img class="{c}" src="{M}{f}.png">' for f,c in items)+'</div>'
ph=lambda *fs:[(f,'ph') for f in fs]
for key,label,items in [
 ('home','Homepage',ph('home-0')),
 ('care','Caregiver card',ph('care-0','care-1','care-2')),
 ('recipes','Recipes page',ph('recipes-0','recipes-1','recipes-2')),
 ('journey','Journey page',ph('journey-0','journey-1','journey-2','journey-3')),
 ('play','Play',ph('play-0','play-1')),
 ('connect','Connect',ph('connect-0','connect-1','connect-2')),
 ('reminisce','Reminisce',ph('reminisce-0','reminisce-1','reminisce-2','reminisce-3')),
 ('nav','Smart walker · Context-aware navigation',[('nav-0','ph'),('nav-1','wk'),('nav-2','wk')]),
 ('sense','Smart walker · Sensorial engagement',[('sense-0','wk'),('sense-1','ph'),('sense-3','wk'),('sense-4','ph')]),
]:
    css=MCSS+({'sense':'.row{gap:60px}.row img.wk{height:400px}.row img.ph{height:700px}','nav':'.row{gap:70px}.row img.wk{height:500px}.row img.ph{height:760px}'}.get(key,''))
    plates[f'minda-plate-{key}']=page(label,mrow(items),'full','Minda',css)
for key,label,f in [('fmwh','Research · Finding My Way Home','gz00K075bYkC4iLcs3Qoy3rsVds.png'),('brief','Research · Brief','DlKQW7VmJE1ZALj1T1PM6M1lTA.png')]:
    plates[f'minda-plate-{key}']=page(label,f'<img class="card" src="{M}{f}">','full','Minda')

KJ='Kalian, Joget-Joget'
for key,label,f,sz in [('sketch-1','Early sketch · Shadow stage','kjj-sketch-1.jpg','n1'),('sketch-2','Early sketch · Sound wall','kjj-sketch-2.jpg','n2'),('sketch-3','Early sketch · Projection corridor','kjj-sketch-3.jpg','n2'),
 ('states','State transition diagram','kjj-states-diagram.jpg','n1'),('disco','Disco balls','kjj-disco.jpg','n2'),('spotlight','Spotlight','kjj-spotlight.jpg','n2'),
 ('ably','One channel per player','kjj-ably-code.jpg','n2'),('lobby','Phone lobby','kjj-lobby.jpg','n2'),('sparks-off','Proximity sparks · off','kjj-sparks-off.jpg','n2'),('sparks-on','Proximity sparks · on','kjj-sparks-on.jpg','n2'),
 ('birds','Big Bird · all ten states','kjj-bird-states.jpg','n1')]:
    plates[f'kjj-plate-{key}']=page(label,f'<img class="card" src="{O}{f}">',sz,KJ)

for i,n in enumerate(['Contrast','Error-correction','White space','Uniqueness','Universality','Digital eyes','Meaning-making']):
    plates[f'decode-bg-{i+1}']=page(f'Station 0{i+1} · {n}','','n2','DECODE')

plates['decode-plate-instagram']=page('Featured by NUS CDE',f'<img class="card" src="{O}decode-instagram.png">','n3','DECODE')
plates['kjj-plate-nsync']=page('Reference · No Strings Attached',f'<img class="card" src="{O}kjj-nsync.png">','n2',KJ)

QCSS='.row{display:flex;gap:150px;align-items:center;justify-content:center;height:100%}figure{display:flex;flex-direction:column;align-items:center;gap:30px}.q{background:#fff;padding:10px;border-radius:22px;box-shadow:0 30px 70px rgba(15,14,14,.14),0 3px 10px rgba(15,14,14,.06)}.q img{width:640px;height:640px;display:block}figcaption{text-align:center}figcaption b{display:block;font-weight:500;font-size:40px;margin-bottom:8px}figcaption span{font-size:28px;color:#5E5C58}'
plates['path-plate-qrcodes']=page('Scan to try the safety check','<div class="row">'+''.join(f'<figure><div class="q"><img src="{O}{f}.png"></div><figcaption><b>{t}</b><span>{d}</span></figcaption></figure>' for f,t,d in [('qr-archive','PATH Archive','From the A6 card'),('qr-website','MFS website','From the poster')])+'</div>','n1',P,QCSS)
only=os.environ.get('ONLY')
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':2400,'height':PH})
    for n,h in plates.items():
        if only and only not in n: continue
        open('/tmp/plates/p.html','w').write(h); pg.goto('file:///tmp/plates/p.html'); pg.wait_for_load_state('networkidle'); pg.wait_for_timeout(150)
        pg.screenshot(path=f'/tmp/plates/out/{n}.png')
    b.close()
print(len(plates))
