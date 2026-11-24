// On the live site, show clean addresses (danikh.design/projects/path, not …/path.html).
// The links point at real files so the offline preview works; the server answers the clean ones too.
(() => {
  if (!/(^|\.)danikh\.design$|\.vercel\.app$/.test(location.hostname)) return;
  const clean = location.pathname.replace(/\/index\.html$/, '/').replace(/\.html$/, '').replace(/(.)\/$/, '$1');
  if (clean !== location.pathname) try { history.replaceState(history.state, '', clean + location.search + location.hash); } catch (e) {}
})();

// Every page opens at the top: no restored scroll positions, and the logo or a tab for the page
// you are already on brings you back to the top instead of doing nothing.
(() => {
  try { if ('scrollRestoration' in history) history.scrollRestoration = 'manual'; } catch (e) {}
  const toTop = () => { const h = document.documentElement, b = h.style.scrollBehavior; h.style.scrollBehavior = 'auto'; scrollTo(0, 0); h.style.scrollBehavior = b; };
  if (!location.hash) {
    // some hosts (and some browsers) restore the old scroll position after load; keep snapping
    // back to the top until the visitor scrolls on their own
    let touched = false;
    ['wheel', 'touchstart', 'keydown', 'pointerdown'].forEach(ev => addEventListener(ev, () => { touched = true; }, { once: true, passive: true }));
    const snap = () => { if (!touched && scrollY !== 0) toTop(); };
    toTop();
    document.addEventListener('DOMContentLoaded', snap);
    addEventListener('load', snap);
    [60, 200, 500, 1000, 1600].forEach(t => setTimeout(snap, t));
  }
  addEventListener('pageshow', e => { if (e.persisted && !location.hash) toTop(); });
  document.addEventListener('click', e => {
    const a = e.target.closest && e.target.closest('a[href]');
    if (!a || a.target === '_blank' || e.metaKey || e.ctrlKey || e.shiftKey) return;
    let u; try { u = new URL(a.getAttribute('href'), location.href); } catch (err) { return; }
    if (u.origin !== location.origin || u.hash) return;
    const here = p => p.replace(/index\.html$/, '').replace(/\.html$/, '').replace(/(.)\/$/, '$1');
    if (here(u.pathname) === here(location.pathname)) { e.preventDefault(); scrollTo({ top: 0, behavior: 'smooth' }); }
  });
})();
// Header background on scroll
(() => {
  const h = document.querySelector('.site-header');
  if (!h) return;
  const on = () => h.classList.toggle('scrolled', window.scrollY > 24);
  on(); window.addEventListener('scroll', on, { passive: true });
})();

// Reveal on scroll
(() => {
  const els = document.querySelectorAll('.reveal');
  if (!('IntersectionObserver' in window)) { els.forEach(e => e.classList.add('in')); return; }
  const io = new IntersectionObserver(es => es.forEach(e => {
    if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
  }), { rootMargin: '0px 0px -8% 0px' });
  els.forEach(e => io.observe(e));
})();

// Autoplay looping videos only while visible
(() => {
  const vids = document.querySelectorAll('video[data-auto]');
  const load = v => { if (v.dataset.src && !v.getAttribute('src')) { v.src = v.dataset.src; v.preload = 'auto'; } };
  if (!vids.length) return;
  if (!('IntersectionObserver' in window)) { vids.forEach(v => { load(v); v.play().catch(() => {}); }); return; }
  // start fetching a clip a little before it scrolls into view, so it is ready when it arrives
  const near = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { load(e.target); near.unobserve(e.target); } }), { rootMargin: '900px 0px' });
  vids.forEach(v => near.observe(v));
  const io = new IntersectionObserver(es => es.forEach(e => {
    if (e.isIntersecting) load(e.target);
    const v = e.target;
    if (e.isIntersecting) { const p = v.play(); if (p && p.catch) p.catch(() => {}); } else v.pause();
  }), { threshold: 0.15 });
  vids.forEach(v => io.observe(v));
})();

// Interactive demos report their height so the frame fits them
addEventListener('message', e => {
  if (!e.data || typeof e.data.kjjHeight !== 'number') return;
  document.querySelectorAll('.embed iframe').forEach(f => { if (f.contentWindow === e.source) f.style.height = Math.ceil(e.data.kjjHeight) + 'px'; });
});

// Work page filters
(() => {
  const chips = document.querySelectorAll('.chip');
  if (!chips.length) return;
  const items = [...document.querySelectorAll('.proj')], count = document.querySelector('.f-count'), empty = document.querySelector('.f-empty');
  const apply = f => {
    chips.forEach(c => { const on = c.dataset.f === f; c.classList.toggle('on', on); c.setAttribute('aria-pressed', on); });
    let n = 0;
    items.forEach(el => {
      const show = f === 'all' || el.dataset.tags.split(' ').includes(f);
      if (show) { n++; el.classList.remove('hide'); el.classList.add('fade'); requestAnimationFrame(() => requestAnimationFrame(() => { el.classList.remove('fade'); el.classList.add('in'); })); }
      else el.classList.add('hide');
    });
    count.textContent = 'Showing ' + String(n).padStart(2, '0') + (n === 1 ? ' project' : ' projects');
    empty.hidden = n > 0;
    const eh = document.querySelector('.earlier-h'); if (eh) eh.hidden = !items.some(el => el.classList.contains('early') && !el.classList.contains('hide'));
    const top = document.querySelector('.filters').getBoundingClientRect().top;
    if (top < 80) window.scrollTo({ top: window.scrollY + document.querySelector('.proj-list').getBoundingClientRect().top - 140, behavior: 'smooth' });
  };
  chips.forEach(c => c.addEventListener('click', () => apply(c.classList.contains('on') && c.dataset.f !== 'all' ? 'all' : c.dataset.f)));
})();

// Sound toggle on videos that have audio (one plays at a time)
document.querySelectorAll('.snd').forEach(b => b.addEventListener('click', () => {
  const v = b.parentElement.querySelector('video'), on = v.muted;
  document.querySelectorAll('.snd[aria-pressed="true"]').forEach(o => { if (o !== b) { o.setAttribute('aria-pressed', 'false'); o.textContent = 'Sound on'; o.parentElement.querySelector('video').muted = true; } });
  v.muted = !on; b.setAttribute('aria-pressed', String(on)); b.textContent = on ? 'Sound off' : 'Sound on';
  if (on) { v.currentTime = 0; const p = v.play(); if (p && p.catch) p.catch(() => {}); }
}));

// Full screen for an embedded interactive (falls back to opening it in a new tab)
document.querySelectorAll('.frame-full').forEach(b => b.addEventListener('click', () => {
  const f = b.closest('.frame').querySelector('iframe');
  const go = f.requestFullscreen || f.webkitRequestFullscreen;
  if (go && document.fullscreenEnabled !== false) { try { const r = go.call(f); if (r && r.catch) r.catch(() => open(f.src, '_blank')); return; } catch (e) {} }
  open(f.src, '_blank');
}));

// Interactive frames: the embedded site only loads once the visitor asks for it.
document.querySelectorAll('button.frame-go').forEach(b => b.addEventListener('click', () => {
  const f = document.createElement('iframe');
  f.src = b.dataset.src; f.title = b.dataset.title; f.allow = 'autoplay; fullscreen'; f.setAttribute('allowfullscreen', '');
  const view = b.parentElement; const im = view.querySelector('picture') || view.querySelector('img'); im.remove(); b.remove(); view.appendChild(f);
  view.parentElement.classList.add('on');
}));

// DANIKH.DESIGN pixel wordmark, fixed behind the whole site.
// Home: plays the entrance (pixels fly in while the rest of the site waits in the dark),
// reacts to hover (pixels scatter, missing ones fill in), and dims as you scroll.
// Other pages: a faint backdrop. Everywhere when idle: single pixels blink on and off.
// Pauses in background tabs.
(() => {
  const cv = document.getElementById('wordmark');
  if (!cv || !window.WORDMARK) return;
  const WM = window.WORDMARK, root = document.documentElement;
  const home = document.body.classList.contains('is-home');
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const intro = home && root.classList.contains('intro') && !reduce;
  if (!intro) root.classList.remove('intro');
  const ctx = cv.getContext('2d');
  const N = WM.rows.join('').replace(/0/g, '').length;
  const gi = new Float32Array(N), gj = new Float32Array(N), core = new Uint8Array(N),
    hx = new Float32Array(N), hy = new Float32Array(N), x = new Float32Array(N), y = new Float32Array(N),
    vx = new Float32Array(N), vy = new Float32Array(N), ox = new Float32Array(N), oy = new Float32Array(N),
    delay = new Float32Array(N), flipUntil = new Float32Array(N);
  let n = 0, maxDelay = 0;
  for (let j = 0; j < WM.h; j++) for (let i = 0; i < WM.w; i++) {
    const v = WM.rows[j][i];
    if (v === '0') continue;
    const a = Math.random() * Math.PI * 2, r = 200 + Math.random() * 500;
    gi[n] = i; gj[n] = j; core[n] = v === '1' ? 1 : 0;
    ox[n] = Math.cos(a) * r; oy[n] = Math.sin(a) * r;
    delay[n] = intro ? i * 6 + Math.random() * 420 : 0;
    if (delay[n] > maxDelay) maxDelay = delay[n];
    n++;
  }
  let FLY = intro ? 1000 : 0, INTRO_END = maxDelay + FLY + 150;
  let W, H, CW, CH, cell, offX = 0, offY = 0, color = '#F2F1EE';
  const hintEl = document.getElementById('wm-hint');
  function size() {
    const dpr = Math.min(window.devicePixelRatio || 1, 1.5);
    const st = cv.parentElement, ps = getComputedStyle(st);
    const avail = st.clientWidth - parseFloat(ps.paddingLeft) - parseFloat(ps.paddingRight);
    const stacked = avail < 720;
    let cols = WM.w, lines = WM.h, off1 = 0, off2 = 0;
    if (stacked) {
      const w1 = WM.split[0] + 1, w2 = WM.w - WM.split[1];
      cols = Math.max(w1, w2); lines = WM.h * 2 + 4; off1 = (cols - w1) / 2; off2 = (cols - w2) / 2;
    }
    W = stacked ? Math.min(avail * 0.78, 420) : Math.min(avail, 1500); cell = W / cols; H = cell * lines;
    // home: the canvas fills the whole hero so the pixels can fly anywhere and every part of it responds
    if (home) { CW = st.clientWidth; CH = st.clientHeight; offX = Math.round((CW - W) / 2); offY = Math.round((CH - H) / 2); }
    else { CW = W; CH = H; offX = offY = 0; }
    cv.style.width = CW + 'px'; cv.style.height = CH + 'px';
    cv.width = Math.round(CW * dpr); cv.height = Math.round(CH * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, offX * dpr, offY * dpr);
    if (hintEl) hintEl.style.top = Math.round(offY + H + Math.max(56, CH * 0.09)) + 'px';
    for (let k = 0; k < n; k++) {
      if (!stacked) { hx[k] = gi[k] * cell; hy[k] = gj[k] * cell; }
      else if (gi[k] <= WM.split[0]) { hx[k] = (off1 + gi[k]) * cell; hy[k] = gj[k] * cell; }
      else { hx[k] = (off2 + gi[k] - WM.split[1]) * cell; hy[k] = (gj[k] + WM.h + 4) * cell; }
    }
    color = getComputedStyle(cv).color;
  }
  size();
  let rt; addEventListener('resize', () => { clearTimeout(rt); rt = setTimeout(size, 120); });

  // home: dim the wordmark as the page scrolls over it; hover only while it's up front
  if (home) {
    let ticking = false;
    const onScroll = () => {
      ticking = false;
      const p = Math.min(1, scrollY / (innerHeight * 0.7));
      root.style.setProperty('--wm', (1 - p * 0.7).toFixed(3));
      document.body.classList.toggle('wm-live', p < 0.35);
    };
    addEventListener('scroll', () => { if (!ticking) { ticking = true; requestAnimationFrame(onScroll); } }, { passive: true });
    onScroll();
  }

  // entrance: reveal the site once the pixels have landed (any input skips ahead)
  // game clock: follows real time, but never jumps more than 50 ms per frame, so when the phone is busy
  // (screen recording, low power mode) the animations slow down instead of skipping their stages
  let gt = performance.now(), gRaw = 0;
  let revealed = !intro, t0 = gt, introTimer = 0;
  const reveal = () => { if (revealed) return; revealed = true; clearTimeout(introTimer); root.classList.remove('intro'); };
  const armIntro = () => {
    clearTimeout(introTimer); introTimer = setTimeout(reveal, INTRO_END + 50);
    ['wheel', 'touchstart', 'keydown', 'pointerdown'].forEach(ev => addEventListener(ev, reveal, { once: true, passive: true }));
  };
  if (intro) armIntro();

  let mx = -1e4, my = -1e4, hover = false, heal = 0, idle = 0, nextFlip = 0;
  // replay the opening flight: fresh paths each time. full = the site dims again, like on first open
  function replayIntro(full) {
    if (reduce) return;
    maxDelay = 0;
    for (let k = 0; k < n; k++) {
      const a = Math.random() * Math.PI * 2, r = 200 + Math.random() * 500;
      ox[k] = Math.cos(a) * r; oy[k] = Math.sin(a) * r;
      delay[k] = gi[k] * 6 + Math.random() * 420; if (delay[k] > maxDelay) maxDelay = delay[k];
      x[k] = y[k] = vx[k] = vy[k] = 0; flipUntil[k] = 0;
    }
    FLY = 1000; INTRO_END = maxDelay + FLY + 150; t0 = gt; nextFlip = 0; idle = 0;
    if (full) { scrollTo(0, 0); revealed = false; root.classList.add('intro'); armIntro(); }
  }

  const fine = matchMedia('(hover: hover) and (pointer: fine)').matches;
  const hint = hintEl, hintText = hint && hint.querySelector('[data-hint]'), gameBtn = document.getElementById('wm-game'),
    restartBtn = document.getElementById('wm-restart'), soundBtn = document.getElementById('wm-sound');
  const HINT = fine ? 'Hover to scatter' : '';  // phones: no scatter, just the game
  if (hintText) hintText.textContent = HINT;

  // ---- arcade sound: a tiny square-wave synth, only ever started by pressing Play ----
  let ac = null, master = null, muted = false, lastPop = 0;
  try { muted = localStorage.getItem('wm-mute') === '1'; } catch (e) {}
  const audio = () => {
    try {
      if (ac) { if (ac.state === 'suspended') ac.resume(); return; }
      const AC = window.AudioContext || window.webkitAudioContext; if (!AC) return;
      ac = new AC(); master = ac.createGain(); master.gain.value = 0.16; master.connect(ac.destination);
    } catch (e) { ac = null; }
  };
  const tone = (f0, f1, dur, type, vol, at) => {
    if (!ac || muted) return;
    const t = ac.currentTime + (at || 0), o = ac.createOscillator(), g = ac.createGain();
    o.type = type || 'square'; o.frequency.setValueAtTime(f0, t);
    if (f1 !== f0) o.frequency.exponentialRampToValueAtTime(f1, t + dur);
    g.gain.setValueAtTime(vol || 0.5, t); g.gain.exponentialRampToValueAtTime(0.001, t + dur);
    o.connect(g); g.connect(master); o.start(t); o.stop(t + dur + 0.03);
  };
  let noiseBuf = null;
  const noise = (dur, vol, at, hp) => {
    if (!ac || muted) return;
    if (!noiseBuf) { noiseBuf = ac.createBuffer(1, ac.sampleRate, ac.sampleRate); const d = noiseBuf.getChannelData(0); for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1; }
    const t = ac.currentTime + (at || 0), s = ac.createBufferSource(), f = ac.createBiquadFilter(), g = ac.createGain();
    s.buffer = noiseBuf; f.type = 'highpass'; f.frequency.value = hp || 400;
    g.gain.setValueAtTime(vol || 0.5, t); g.gain.exponentialRampToValueAtTime(0.001, t + dur);
    s.connect(f); f.connect(g); g.connect(master); s.start(t); s.stop(t + dur + 0.03);
  };
  const MARCH = [98, 87, 78, 73];
  const sfx = {
    start: () => { noise(0.25, 0.3, 0, 2000); [262, 330, 392, 523, 659, 784, 1047].forEach((f, i) => tone(f, f, 0.08, 'square', 0.4, 0.05 + i * 0.06)); },
    ready: () => tone(440, 440, 0.14, 'square', 0.4),
    go: () => { tone(880, 880, 0.08, 'square', 0.45); tone(1320, 1320, 0.25, 'square', 0.4, 0.09); },
    shoot: () => tone(1200, 260, 0.08, 'square', 0.16),
    pop: () => { const t = performance.now(); if (t - lastPop < 45) return; lastPop = t; noise(0.1, 0.45, 0, 1500); tone(320, 90, 0.09, 'square', 0.18); },
    step: i => tone(MARCH[i & 3], MARCH[i & 3] * 0.98, 0.08, 'triangle', 0.9),
    hurt: () => { noise(0.4, 0.8, 0, 200); tone(260, 45, 0.45, 'sawtooth', 0.35); },
    over: () => { noise(0.9, 0.9, 0, 110); tone(160, 30, 0.9, 'sawtooth', 0.4); [392, 349, 311, 262, 196].forEach((f, i) => tone(f, f * 0.96, 0.2, 'square', 0.38, 0.7 + i * 0.18)); tone(98, 49, 0.9, 'triangle', 0.9, 1.6); },
    win: () => { [523, 659, 784, 1047, 784, 1047, 1319, 1568].forEach((f, i) => tone(f, f, 0.1, 'square', 0.4, i * 0.085)); },
    exit: () => { [784, 523, 392, 262].forEach((f, i) => tone(f, f, 0.07, 'square', 0.3, i * 0.055)); },
  };
  // sound is a bonus: if the phone refuses it (recording, silent mode, interrupted audio), carry on silently
  for (const k in sfx) { const f = sfx[k]; sfx[k] = (...a) => { try { f(...a); } catch (e) {} }; }
  const paintSound = () => { if (soundBtn) { soundBtn.textContent = muted ? 'Sound off' : 'Sound on'; soundBtn.setAttribute('aria-pressed', String(!muted)); } };
  paintSound();

  // ---- pixel font for the arcade banners (5x5) ----
  const FONT = {
    A: '0111010001111111000110001', B: '1111010001111101000111110', C: '0111110000100001000001111', D: '1111010001100011000111110',
    E: '1111110000111101000011111', G: '0111110000100111000101111', I: '1111100100001000010011111', L: '1000010000100001000011111',
    M: '1000111011101011000110001', N: '1000111001101011001110001', O: '0111010001100011000101110', P: '1111010001111101000010000',
    R: '1111010001111101001010001', S: '0111110000011100000111110', T: '1111100100001000010000100', V: '1000110001100010101000100',
    W: '1000110001101011101110001', Y: '1000101010001000010000100', '!': '0010000100001000000000100',
    0: '0111010011101011100101110', 1: '0010001100001000010001110', 2: '1111000001011101000011111', 3: '1111000001011100000111110',
    4: '1001010010111110001000010', 5: '1111110000111100000111110', 6: '0111010000111101000101110', 7: '1111100001000100010000100',
    8: '0111010001011101000101110', 9: '0111010001011110000101110',
  };
  const pixText = (str, cx, cy, ps) => {
    const pts = [], x0 = cx - (str.length * 6 - 1) * ps / 2, y0 = cy - 2.5 * ps;
    for (let c = 0; c < str.length; c++) {
      const gl = FONT[str[c]]; if (!gl) continue;
      for (let q = 0; q < 25; q++) if (gl[q] === '1') pts.push([x0 + (c * 6 + q % 5) * ps, y0 + ((q / 5) | 0) * ps]);
    }
    return pts;
  };
  const drawText = (str, cx, cy, ps) => { const gp = ps > 3 ? Math.max(1, ps * 0.14) : 0; for (const p of pixText(str, cx, cy, ps)) ctx.fillRect(Math.round(p[0]), Math.round(p[1]), ps - gp, ps - gp); };

  // ---- game mode: the wordmark becomes the invader formation and your pixel D is the ship ----
  const MARK = window.MARK || ['1'];
  const idx = new Int32Array(WM.w * WM.h).fill(-1), dead = new Uint8Array(N),
    bxo = new Float32Array(N), byo = new Float32Array(N), bdl = new Float32Array(N);
  let total = 0;
  for (let k = 0; k < n; k++) { idx[gj[k] * WM.w + gi[k]] = k; if (core[k]) total++; }
  const BOOT = 2100;
  let game = false, phase = '', phaseAt = 0, flashAt = -1e4, flashMax = 0.3, cue = 0, won = false, banner = null, stepI = 0,
    fx = 0, fy = 0, dir = 1, nextStep = 0, alive = 0, score = 0, lives = 3, best = 0, newBest = false,
    shipX = 0, shipY = 0, sc = 4, firing = false, lastShot = 0, nextBomb = 0, safeUntil = 0, keyL = false, keyR = false, hud = '';
  try { best = +localStorage.getItem('wm-best') || 0; } catch (e) {}
  const bullets = [], bombs = [], debris = [], rubble = [];
  const pad4 = v => String(v).padStart(4, '0');
  const setHud = txt => { if (txt !== hud && hintText) { hud = txt; hintText.textContent = txt; } };
  const flash = (now, a) => { flashAt = now; flashMax = a; };
  const buzz = v => { try { if (!fine && navigator.vibrate) navigator.vibrate(v); } catch (e) {} };
  const shake = big => { cv.classList.remove('shk', 'shk2'); void cv.offsetWidth; cv.classList.add(big ? 'shk2' : 'shk'); };
  cv.addEventListener('animationend', () => cv.classList.remove('shk', 'shk2'));
  const burst = (bx, by, count, power) => {
    for (let q = 0; q < count && debris.length < 420; q++) {
      const an = Math.random() * Math.PI * 2, sp = cell * power * (0.3 + Math.random());
      debris.push({ x: bx, y: by, vx: Math.cos(an) * sp, vy: Math.sin(an) * sp - cell * 0.15, life: 1 });
    }
  };
  const blast = k => {
    for (let dj = -1; dj <= 1; dj++) for (let di = -1; di <= 1; di++) {
      const i = gi[k] + di, j = gj[k] + dj;
      if (i < 0 || j < 0 || i >= WM.w || j >= WM.h) continue;
      const q = idx[j * WM.w + i];
      if (q < 0 || !core[q] || dead[q]) continue;
      dead[q] = 1; alive--; score += 10;
      burst(hx[q] + fx + cell / 2, hy[q] + fy + cell / 2, 2, 0.3);
    }
    sfx.pop();
  };
  // start or restart: flash, the formation shatters and re-assembles row by row under a scan line, READY / GO
  function startGame() {
    if (!home || root.classList.contains('intro')) return;
    audio();
    if (!game) scrollTo(0, 0);
    game = true; won = false; banner = null; fx = fy = 0; dir = 1; alive = total; score = 0; lives = 3; newBest = false;
    firing = keyL = keyR = false; stepI = 0; cue = 0;
    dead.fill(0); bullets.length = bombs.length = debris.length = rubble.length = 0;
    for (let k = 0; k < n; k++) {
      x[k] = y[k] = vx[k] = vy[k] = 0;
      const a = Math.random() * Math.PI * 2, r = cell * (3 + Math.random() * 12);
      bxo[k] = Math.cos(a) * r * 1.6; byo[k] = Math.sin(a) * r * 0.7 - cell * 3;
      bdl[k] = 300 + gj[k] * 48 + Math.random() * 240;
    }
    sc = Math.max(fine ? 3 : 4, Math.round(cell * (fine ? 0.5 : 0.7)));
    const bar = document.querySelector('.hero-bar');
    const floor = (bar ? bar.getBoundingClientRect().top : CH - 90) - cv.getBoundingClientRect().top - offY;
    shipY = floor - 22 - MARK.length * sc; shipX = W / 2;
    const now = gt; phase = 'boot'; phaseAt = now; flash(now, 0.45); shake(false);
    nextStep = now + BOOT + 250; nextBomb = now + BOOT + 1100; safeUntil = now + BOOT + 500; lastShot = 0;
    document.body.classList.add('wm-game');
    if (gameBtn) gameBtn.textContent = 'Exit game';
    hud = ''; setHud(fine ? 'Get ready' : 'Get ready · Drag anywhere to move, hold to fire');
    sfx.start();
  }
  function exitGame(quiet) {
    if (!game) return;
    game = false; phase = ''; banner = null;
    dead.fill(0); fx = fy = 0; bullets.length = bombs.length = rubble.length = 0; firing = false; hover = false; mx = my = -1e4;
    document.body.classList.remove('wm-game');
    if (gameBtn) gameBtn.textContent = 'Insert coin';
    hud = ''; setHud(HINT);
    if (!quiet) sfx.exit();
    replayIntro(!quiet);
  }
  // the end: on a loss the screen shakes, the formation crumbles to the floor, then the rubble rises into GAME OVER
  const endGame = (win, now) => {
    if (phase !== 'play') return;
    phase = 'end'; phaseAt = now; won = win; firing = false; bombs.length = bullets.length = 0;
    if (score > best) { best = score; newBest = score > 0; try { localStorage.setItem('wm-best', best); } catch (e) {} }
    if (win) { flash(now, 0.5); sfx.win(); }
    else {
      flash(now, 0.6); shake(true); sfx.over(); buzz([80, 60, 160]);
      burst(shipX, shipY + MARK.length * sc / 2, 70, 1);
      for (let k = 0; k < n; k++) if (core[k] && !dead[k])
        rubble.push({ x: hx[k] + fx, y: hy[k] + fy, vx: (Math.random() - 0.5) * cell * 0.35, vy: -Math.random() * cell * 0.3, at: now + 120 + Math.random() * 520 });
      dead.fill(1); alive = 0;
    }
    setHud((win ? 'Cleared' : 'Game over') + ' · Score ' + pad4(score) + (newBest ? ' · New best' : '') + (fine ? ' · R to restart' : ''));
  };
  const makeBanner = now => {
    const big = won ? 'CLEARED!' : 'GAME OVER';
    const ps = Math.max(4, Math.round(Math.min(cell * 1.5, (CW - 40) * 0.92 / (big.length * 6)))), cy = Math.min(H / 2, shipY * 0.42);
    const pts = pixText(big, W / 2, cy, ps).map(p => {
      let sx, sy;
      if (rubble.length) { const r = rubble[(Math.random() * rubble.length) | 0]; sx = r.x; sy = r.y; }
      else { sx = W / 2 + (Math.random() - 0.5) * CW; sy = -offY - 40 - Math.random() * 300; }
      return { tx: p[0], ty: p[1], sx, sy, d: Math.random() * 380 };
    });
    banner = { pts, ps, cy, at: now };
  };

  if (home) {
    let dragX = null, dragShip = 0;
    const at = e => {
      const b = cv.getBoundingClientRect(); mx = e.clientX - b.left - offX; my = e.clientY - b.top - offY;
      if (!fine && !game) return; hover = true;
      if (!game) return;
      if (e.pointerType === 'mouse') shipX = mx;
      else if (dragX !== null) shipX = dragShip + (e.clientX - dragX) * 1.4;  // touch: steer from anywhere, the finger never hides the ship
    };
    cv.addEventListener('pointermove', at);
    cv.addEventListener('pointerdown', e => {
      if (e.button > 0) return;
      if (game && e.pointerType !== 'mouse') { dragX = e.clientX; dragShip = shipX; try { cv.setPointerCapture(e.pointerId); } catch (_) {} }
      at(e); if (game && phase === 'play') firing = true;
    });
    const up = () => { firing = false; dragX = null; };
    addEventListener('pointerup', e => { up(); if (e.pointerType !== 'mouse' && !game) setTimeout(() => { hover = false; mx = my = -1e4; }, 600); });
    addEventListener('pointercancel', up);
    addEventListener('blur', () => { up(); keyL = keyR = false; });
    cv.addEventListener('contextmenu', e => e.preventDefault());
    cv.addEventListener('pointerleave', e => { if (e.pointerType === 'mouse') { hover = false; mx = my = -1e4; } });
    if (gameBtn) gameBtn.addEventListener('click', () => { game ? exitGame() : startGame(); gameBtn.blur(); });
    if (restartBtn) restartBtn.addEventListener('click', () => { startGame(); restartBtn.blur(); });
    if (soundBtn) soundBtn.addEventListener('click', () => {
      muted = !muted; try { localStorage.setItem('wm-mute', muted ? '1' : '0'); } catch (e) {}
      paintSound(); audio(); if (!muted) sfx.ready(); soundBtn.blur();
    });
    addEventListener('keydown', e => {
      if (!game) return;
      if (e.key === 'Escape') exitGame();
      else if (e.key === 'r' || e.key === 'R') startGame();
      else if (e.key === ' ' || e.key === 'Enter') { if (phase === 'play') firing = e.key === ' '; else if (phase === 'end' && banner && gt - banner.at > 900) startGame(); }
      else if (e.key === 'ArrowLeft') keyL = true;
      else if (e.key === 'ArrowRight') keyR = true;
      else return;
      e.preventDefault();
    });
    addEventListener('keyup', e => { if (e.key === ' ') firing = false; else if (e.key === 'ArrowLeft') keyL = false; else if (e.key === 'ArrowRight') keyR = false; });
    addEventListener('scroll', () => { if (game && scrollY > innerHeight * 0.25) exitGame(true); }, { passive: true });
    let lastW = innerWidth;
    addEventListener('resize', () => { if (Math.abs(innerWidth - lastW) > 40) { lastW = innerWidth; exitGame(true); } });
  }

  let running = false;
  const ease = t => 1 - Math.pow(1 - t, 4);
  const clamp = v => v < 0 ? 0 : v > 1 ? 1 : v;
  let lastNow = 0;
  // a failing step (a sound the phone refuses, say) must never freeze the animation: log it and keep going
  function frame(now) {
    try { frameBody(now); } catch (e) { try { console.error(e); } catch (_) {} running = true; requestAnimationFrame(frame); }
  }
  function frameBody(now) {
    if (document.hidden) { running = false; return; }
    // behind the page (scrolled past the hero): keep animating, but at half the frame rate to stay light
    if (!game && scrollY > innerHeight * 1.05 && now - (frame.last || 0) < 32) { requestAnimationFrame(frame); return; }
    frame.last = now;
    gt += Math.min(50, Math.max(0, now - (gRaw || now))); gRaw = now; now = gt;
    const t = now - t0, dt = Math.min(3, Math.max(0.5, (now - (lastNow || now - 16.7)) / 16.7)); lastNow = now;
    heal += ((hover && !game ? 1 : 0) - heal) * 0.07;
    idle += ((hover || game || reduce || t < INTRO_END + 400 ? 0 : 1) - idle) * 0.05;
    // idle: individual pixels switch off (or missing ones switch on) for a moment
    if (idle > 0.5) {
      while (t > nextFlip) {
        flipUntil[(Math.random() * n) | 0] = t + 250 + Math.random() * 900;
        nextFlip += 25 + Math.random() * 35;
      }
    } else nextFlip = t;
    const g = cell * 0.16, s = cell - g, R = cell * 5, R2 = R * R;
    const bw = Math.max(2, cell * 0.36), bh = cell * 1.5, shipW = MARK[0].length * sc, shipH = MARK.length * sc;
    const tp = now - phaseAt, boot = game && phase === 'boot';
    if (game) {
      if (boot) {
        if (cue === 0 && tp > 300) { cue = 1; sfx.ready(); }
        if (cue === 1 && tp > 1450) { cue = 2; sfx.go(); flash(now, 0.18); }
        if (tp > BOOT) { phase = 'play'; phaseAt = now; }
      }
      if (phase === 'end' && !banner && tp > (won ? 250 : 950)) makeBanner(now);
      if (phase === 'play') {
        // the formation marches sideways in steps, drops a row at each edge, and speeds up as it thins out
        if (now > nextStep) {
          const lim = Math.max(cell, offX - 10);
          if (Math.abs(fx + dir * cell) > lim) { dir = -dir; fy += cell; } else fx += dir * cell;
          nextStep = now + 90 + 420 * (alive / total);
          sfx.step(stepI++);
        }
        if (firing && now - lastShot > 110) { bullets.push({ x: shipX, y: shipY - bh }); lastShot = now; sfx.shoot(); }
        if (now > nextBomb && alive > 0) {
          for (let tries = 0; tries < 40; tries++) {
            const k = (Math.random() * n) | 0;
            if (core[k] && !dead[k]) { bombs.push({ x: hx[k] + fx + cell / 2, y: hy[k] + fy + cell }); break; }
          }
          nextBomb = now + 320 + 700 * (alive / total);
        }
        setHud('Score ' + pad4(score) + ' · Lives ' + '■'.repeat(lives) + '□'.repeat(3 - lives) + (fine ? ' · Hold to fire · Esc to exit' : ''));
      }
      if (phase === 'play' || boot) {
        if (keyL) shipX -= cell * 0.9 * dt; if (keyR) shipX += cell * 0.9 * dt;
        shipX = Math.max(-offX + shipW / 2 + 6, Math.min(CW - offX - shipW / 2 - 6, shipX));
      }
      const bv = Math.max(7, cell * 1.1);
      for (const b of bullets) { b.y -= bv * dt; b.c = -1; b.cy = -1e9; }
    }
    ctx.clearRect(-offX, -offY, CW, CH);
    ctx.fillStyle = color;
    const loading = t < INTRO_END;
    let lastA = -1, lowest = -1e9;
    for (let k = 0; k < n; k++) {
      if (game) {
        if (!core[k] || dead[k]) continue;
        let px = hx[k] + fx, py = hy[k] + fy, a = 1;
        if (boot) {
          // shatter outward, then each row snaps back in turn
          const amt = ease(clamp(tp / 260)) * (1 - ease(clamp((tp - bdl[k]) / 500)));
          px += bxo[k] * amt; py += byo[k] * amt; a = amt > 0.02 ? (Math.random() < 0.15 ? 0.3 : 0.8) : 1;
        } else {
          if (py + cell > lowest) lowest = py + cell;
          for (const b of bullets) if (b.x >= px - bw / 2 && b.x <= px + cell + bw / 2 && b.y <= py + cell && b.y + bh + cell >= py && py > b.cy) { b.c = k; b.cy = py; }
        }
        if (lastA !== a) { ctx.globalAlpha = a; lastA = a; }
        ctx.fillRect(px + g / 2, py + g / 2, s, s);
        continue;
      }
      const kk = loading && FLY ? ease(Math.min(1, Math.max(0, (t - delay[k]) / FLY))) : 1;
      if (hover) {
        const dx = hx[k] + cell / 2 + x[k] - mx, dy = hy[k] + cell / 2 + y[k] - my, d2 = dx * dx + dy * dy;
        if (d2 < R2 && d2 > 0.01) { const d = Math.sqrt(d2), f = (1 - d / R) * cell * 0.28; vx[k] += dx / d * f; vy[k] += dy / d * f; }
      }
      if (x[k] !== 0 || y[k] !== 0 || vx[k] !== 0 || vy[k] !== 0) {
        vx[k] = (vx[k] - x[k] * 0.09) * 0.78; vy[k] = (vy[k] - y[k] * 0.09) * 0.78; x[k] += vx[k]; y[k] += vy[k];
        if (Math.abs(x[k]) + Math.abs(y[k]) + Math.abs(vx[k]) + Math.abs(vy[k]) < 0.02) x[k] = y[k] = vx[k] = vy[k] = 0;
      }
      const flipped = flipUntil[k] > t && !hover;
      let a = (core[k] ? (flipped ? 0 : 1) : (flipped ? 1 : heal)) * kk;
      if (a < 0.02) continue;
      a = Math.round(a * 10) / 10;
      if (a !== lastA) { ctx.globalAlpha = a; lastA = a; }
      ctx.fillRect(hx[k] + g / 2 + x[k] + ox[k] * (1 - kk), hy[k] + g / 2 + y[k] + oy[k] * (1 - kk), s, s);
    }
    if (game) {
      ctx.globalAlpha = 1;
      if (boot) {
        // scan line sweeping down the screen, then READY (blinking) and GO!
        const sl = clamp((tp - 200) / 1300);
        if (sl > 0 && sl < 1) {
          const ly = -offY + CH * sl, lh = Math.max(2, cell * 0.2);
          ctx.globalAlpha = 0.5; ctx.fillRect(-offX, ly, CW, lh);
          ctx.globalAlpha = 0.12; ctx.fillRect(-offX, ly - cell * 3, CW, cell * 3);
          ctx.globalAlpha = 1;
        }
        const ps = Math.max(3, Math.round(cell * 0.75)), cy = (H + shipY) / 2;
        if (tp > 300 && tp < 1400 && Math.floor((tp - 300) / 180) % 2 === 0) drawText('READY', W / 2, cy, ps);
        if (tp >= 1450) drawText('GO!', W / 2, cy, Math.round(ps * (1.6 - 0.5 * ease(clamp((tp - 1450) / 250)))));
      }
      for (let i = bullets.length - 1; i >= 0; i--) {
        const b = bullets[i];
        if (b.c >= 0) { blast(b.c); bullets.splice(i, 1); continue; }
        if (b.y + bh < -offY) { bullets.splice(i, 1); continue; }
        ctx.fillRect(b.x - bw / 2, b.y, bw, bh);
      }
      const hit = now > safeUntil && phase === 'play';
      const fall = Math.max(2.4, cell * 0.32);
      for (let i = bombs.length - 1; i >= 0; i--) {
        const b = bombs[i]; b.y += fall * dt;
        if (b.y > CH - offY) { bombs.splice(i, 1); continue; }
        if (hit && b.y + cell > shipY && b.y < shipY + shipH && Math.abs(b.x - shipX) < shipW / 2) {
          bombs.splice(i, 1); lives--; safeUntil = now + 1500; burst(shipX, shipY + shipH / 2, 26, 0.6);
          if (lives <= 0) { endGame(false, now); break; }  // endGame clears the bombs: stop looping over them
          sfx.hurt(); shake(false); flash(now, 0.22); buzz(60);
          continue;
        }
        // a two-pixel bomb that flickers as it falls
        const z = Math.floor(now / 90) % 2 ? s * 0.35 : -s * 0.35;
        ctx.fillRect(b.x - s / 2 + z, b.y, s * 0.7, s * 0.7); ctx.fillRect(b.x - s / 2 - z, b.y + cell * 0.8, s * 0.7, s * 0.7);
      }
      if (phase === 'play') {
        if (alive <= 0) endGame(true, now);
        else if (lowest >= shipY) endGame(false, now);
      }
      // the ship: the pixel D logo (rises into place during the countdown)
      const lost = phase === 'end' && !won;
      if (!lost && (now > safeUntil || boot || Math.floor(now / 110) % 2)) {
        const rise = boot ? (1 - ease(clamp((tp - 900) / 700))) * (CH - offY - shipY + 10) : 0;
        const sx = shipX - shipW / 2, sg = sc > 3 ? 1 : 0.5;
        for (let j = 0; j < MARK.length; j++) for (let i = 0; i < MARK[j].length; i++)
          if (MARK[j][i] === '1') ctx.fillRect(Math.round(sx + i * sc), Math.round(shipY + rise + j * sc), sc - sg, sc - sg);
      }
      // the crumbled formation: falls, bounces on the floor, then fades as it lifts into the banner
      if (rubble.length) {
        const floorY = shipY + shipH - s, fade = banner ? 1 - clamp((now - banner.at) / 700) : 1;
        if (fade <= 0) rubble.length = 0;
        else {
          ctx.globalAlpha = Math.round(fade * 5) / 5;
          for (const r of rubble) {
            if (now > r.at) {
              r.vy += cell * 0.05 * dt; r.x += r.vx * dt; r.y += r.vy * dt;
              if (r.y > floorY) { r.y = floorY; r.vy *= -0.3; r.vx *= 0.6; }
            }
            ctx.fillRect(r.x + g / 2, r.y + g / 2, s, s);
          }
          ctx.globalAlpha = 1;
        }
      }
      if (banner) {
        const bp = banner.ps, bg = Math.max(1, bp * 0.14);
        for (const p of banner.pts) {
          const e = ease(clamp((now - banner.at - p.d) / 650));
          ctx.fillRect(Math.round(p.sx + (p.tx - p.sx) * e), Math.round(p.sy + (p.ty - p.sy) * e), bp - bg, bp - bg);
        }
        const tb = now - banner.at;
        if (tb > 900) {
          const sp = Math.max(2, Math.round(bp * 0.4));
          drawText('SCORE ' + pad4(score) + '  BEST ' + pad4(best), W / 2, banner.cy + bp * 5, sp);
          if (tb > 1300 && Math.floor(tb / 450) % 2 === 0) drawText(fine ? 'PRESS R TO RESTART' : 'TAP RESTART', W / 2, banner.cy + bp * 5 + sp * 9, sp);
        }
      }
    }
    if (debris.length) {
      const ds = Math.max(2, s * 0.45);
      for (let i = debris.length - 1; i >= 0; i--) {
        const d = debris[i];
        d.vy += cell * 0.035 * dt; d.x += d.vx * dt; d.y += d.vy * dt; d.life -= 0.03 * dt;
        if (d.life <= 0) { debris.splice(i, 1); continue; }
        ctx.globalAlpha = Math.round(d.life * 5) / 5;
        ctx.fillRect(Math.round(d.x / ds) * ds, Math.round(d.y / ds) * ds, ds, ds);
      }
    }
    // screen flash
    const fa = flashMax * (1 - (now - flashAt) / 280);
    if (fa > 0.01) { ctx.globalAlpha = fa; ctx.fillRect(-offX, -offY, CW, CH); }
    ctx.globalAlpha = 1;
    requestAnimationFrame(frame);
  }
  const start = () => { if (!running && !document.hidden) { running = true; requestAnimationFrame(frame); } };
  document.addEventListener('visibilitychange', start);
  start();
})();

// Pixel cursor: a pixel arrow in the wordmark's style, as a plain CSS cursor (no trail, nothing redrawn).
// Only on devices with a precise pointer; touch devices keep their default.
(() => {
  if (!matchMedia('(hover: hover) and (pointer: fine)').matches) return;
  const ARROW = ['11', '111', '1111', '11111', '111111', '1111111', '11111111', '111111111', '1111111111',
    '111111', '111 111', '11  1111', '     1111', '      11'];
  const c = 2, f = 1.6;
  let r = '';
  ARROW.forEach((row, y) => [...row].forEach((v, x) => { if (v === '1') r += `<rect x="${x * c + 1}" y="${y * c + 1}" width="${f}" height="${f}"/>`; }));
  const svg = (fill, stroke) => `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="32"><g fill="${fill}" stroke="${stroke}" stroke-width=".6">${r}</g></svg>`;
  const url = s => `url("data:image/svg+xml,${encodeURIComponent(s)}") 1 1`;
  const st = document.createElement('style');
  st.textContent = `html,body{cursor:${url(svg('#F2F1EE', '#0F0E0E'))},auto}a,button,[role="button"],.chip,label,summary{cursor:${url(svg('#F2F1EE', '#0F0E0E'))},pointer}`;
  document.head.appendChild(st);
})();

// Images fade in once decoded instead of painting in line by line
(() => {
  document.documentElement.classList.add('js-img');
  document.querySelectorAll('.p-body img, main figure img').forEach(img => {
    const done = () => img.classList.add('in');
    if (img.complete && img.naturalWidth) done(); else { img.addEventListener('load', done, { once: true }); img.addEventListener('error', done, { once: true }); }
  });
})();

// Work masonry + About word reveal
(() => {
// Work masonry
const first = document.querySelector('.proj-list .wrap > .proj');
if (first) {
  const box = document.createElement('div'); box.className = 'masonry'; first.before(box);
  [...document.querySelectorAll('.proj-list .wrap > .proj')].forEach(p => box.appendChild(p));
  const items = [...box.children];
  const lay = () => {
    const W = box.clientWidth, n = W > 760 ? 2 : 1, g = W > 760 ? 40 : 0, w = (W - g * (n - 1)) / n, h = Array(n).fill(0);
    const vis = items.filter(p => { p.style.width = w + 'px'; return !p.classList.contains('hide'); });
    let y = 0, gap = W > 760 ? 64 : 48;
    for (let r = 0; r < vis.length; r += n) {
      const row = vis.slice(r, r + n); let rh = 0;
      row.forEach((p, k) => { p.style.transform = `translate(${k * (w + g)}px,${y}px)`; rh = Math.max(rh, p.offsetHeight); });
      y += rh + gap;
    }
    h[0] = y;
    box.style.height = Math.max(...h) + 'px';
  };
  lay(); addEventListener('resize', lay); addEventListener('load', lay);
  items.forEach(p => p.querySelector('img').addEventListener('load', lay));
  new MutationObserver(() => requestAnimationFrame(lay)).observe(box, { subtree: true, attributes: true, attributeFilter: ['class'] });
}
// About words
const big = document.querySelector('.h-big');
if (big) {
  const wrapWords = el => [...el.childNodes].forEach(n => {
    if (n.nodeType === 3) { const f = document.createDocumentFragment(); n.textContent.split(/(\s+)/).forEach(s => { if (!s) return; if (/^\s+$/.test(s)) f.append(s); else { const sp = document.createElement('span'); sp.className = 'w'; sp.textContent = s; f.append(sp); } }); n.replaceWith(f); }
    else if (n.nodeType === 1) wrapWords(n);
  });
  wrapWords(big); big.classList.add('wr');
  const ws = [...big.querySelectorAll('.w')], ph = document.querySelector('.h-photo');
  const tick = () => { const r = big.getBoundingClientRect(), p = Math.max(0, Math.min(1, (innerHeight * .85 - r.top) / (r.height + innerHeight * .35))); const k = Math.round(p * ws.length); ws.forEach((w, i) => w.classList.toggle('on', i < k)); if (ph) ph.classList.toggle('lit', p > .55); };
  addEventListener('scroll', tick, { passive: true }); tick();
}
})();

// Project wall (desktop only): archive header band + hero backdrop
(() => {
const ph = matchMedia('(max-width: 700px)').matches, NC = ph ? 3 : 6;
const wd = document.getElementById('wall-data'), WD = wd ? JSON.parse(wd.textContent) : {};
// pause a wall while it is off screen, so it costs nothing
const io = new IntersectionObserver(es => es.forEach(e => e.target.classList.toggle('off', !e.isIntersecting)));
const mk = (list, n, rep, cls, loop) => { let s = ''; for (let k = 0; k < n; k++) { let t = ''; for (let j = 0; j < rep; j++) { const c = list[(k * 3 + j) % list.length]; t += `<a class="wl-t" ${c.href ? `href="${c.href}"` : ''}><img src="${c.src}" alt="" decoding="async"><span class="caps">${c.t}</span></a>`; } s += loop ? `<div class="wl-col${k % 2 ? ' rev' : ''}" style="--s:${60 + k * 10}s">${t + t}</div>` : `<div class="wl-col">${t}</div>`; } return `<div class="wl-wall ${cls || ''}">${s}</div>`; };
// 1 · archive band
const head = document.querySelector('.work-head');
if (head) {
  const ps = [...document.querySelectorAll('.proj')].map(p => ({ href: '#' + p.id, src: WD[p.id] || p.querySelector('img').getAttribute('src'), t: p.querySelector('h2').textContent }));
  const band = document.createElement('section'); band.className = 'wl-band'; head.before(band);
  band.innerHTML = mk(ps, NC, 6, '', true); band.appendChild(head); io.observe(band);
  head.querySelector('h1').insertAdjacentHTML('afterbegin', `<span class="caps wl-count">${String(ps.length).padStart(2, '0')} projects · 2021 – 2026</span>`);
  band.querySelectorAll('.wl-t').forEach(a => a.addEventListener('click', e => { e.preventDefault(); const t = document.querySelector(a.getAttribute('href')); if (t) scrollTo({ top: t.getBoundingClientRect().top + scrollY - 160, behavior: 'smooth' }); }));
}
// 3 · hero
const hero = document.querySelector('.hero');
if (hero) {
  const imgs = (Object.keys(WD).length ? Object.values(WD) : [...document.querySelectorAll('.h-work .card img')].map(i => i.getAttribute('src'))).map(src => ({ src, t: '' }));
  hero.classList.add('wl-hero');
  // the collage lives at the page root, so it always sits behind the wordmark and the page content
  const bg = document.createElement('div'); bg.className = 'wl-bg'; bg.innerHTML = mk(imgs, NC, 6, '', true); document.body.prepend(bg);
  const place = () => { bg.style.top = (hero.getBoundingClientRect().top + scrollY) + 'px'; bg.style.height = hero.offsetHeight + 'px'; };
  place(); addEventListener('resize', place); addEventListener('load', place); io.observe(bg);
}
})();

// Hide the project wall while the game runs; bring it back (restarted) on exit
(() => {
  const bg = document.querySelector('.wl-bg'); if (!bg) return;
  let was = document.body.classList.contains('wm-game');
  new MutationObserver(() => {
    const now = document.body.classList.contains('wm-game');
    if (was && !now) { bg.querySelectorAll('.wl-col').forEach(c => { c.style.animation = 'none'; void c.offsetHeight; c.style.animation = ''; }); bg.classList.add('back'); setTimeout(() => bg.classList.remove('back'), 1600); }
    was = now;
  }).observe(document.body, { attributes: true, attributeFilter: ['class'] });
})();

// ---------- section slider ----------
document.querySelectorAll('.wheel').forEach(W => {
  const slides = [...W.querySelectorAll('.wh-s')], dots = [...W.querySelectorAll('.wh-dot')], n = slides.length;
  const prev = W.querySelector('.wh-prev'), next = W.querySelector('.wh-next');
  let cur = 0;
  const load = i => { const im = slides[i] && slides[i].querySelector('[data-src]'); if (im) { im.src = im.dataset.src; im.removeAttribute('data-src'); } };
  const play = () => slides.forEach((s, k) => { const v = s.querySelector('video'); if (!v) return; if (k === cur && W.dataset.seen) { load(k); v.play().catch(() => {}); } else v.pause(); });
  // keep the arrows centred on the picture, whatever its height
  const mid = () => { const im = slides[cur].querySelector('.wh-img'); W.style.setProperty('--wh-mid', (im.offsetHeight / 2 - 22) + 'px'); };
  const go = i => {
    i = Math.max(0, Math.min(n - 1, i)); if (i === cur) return;
    cur = i;
    slides.forEach((s, k) => s.classList.toggle('on', k === i));
    dots.forEach((d, k) => d.classList.toggle('on', k === i));
    [i, i + 1, i - 1].forEach(load);
    prev.disabled = i === 0; next.disabled = i === n - 1; mid(); play();
  };
  prev.addEventListener('click', () => go(cur - 1)); next.addEventListener('click', () => go(cur + 1));
  dots.forEach((d, i) => d.addEventListener('click', () => go(i)));
  W.addEventListener('keydown', e => {
    if (e.key === 'ArrowRight') { e.preventDefault(); go(cur + 1); }
    if (e.key === 'ArrowLeft') { e.preventDefault(); go(cur - 1); }
  });
  let sx = null, sy = 0;
  const st = W.querySelector('.wh-stage');
  st.addEventListener('touchstart', e => { sx = e.touches[0].clientX; sy = e.touches[0].clientY; }, { passive: true });
  st.addEventListener('touchend', e => { if (sx === null) return; const dx = e.changedTouches[0].clientX - sx, dy = e.changedTouches[0].clientY - sy; if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy)) go(cur + (dx < 0 ? 1 : -1)); sx = null; });
  W.querySelectorAll('.wh-try').forEach(b => b.addEventListener('click', () => {
    const box = b.closest('.wh-s').querySelector('.wh-img');
    box.innerHTML = `<iframe src="${b.dataset.src}" title="${b.closest('.wh-s').getAttribute('aria-label')}" allow="fullscreen" allowfullscreen></iframe>`;
    b.textContent = 'Live · scroll inside'; b.disabled = true;
  }));
  prev.disabled = true; load(0); load(1); mid(); addEventListener('resize', mid);
  new IntersectionObserver(es => es.forEach(e => { W.dataset.seen = e.isIntersecting ? '1' : ''; play(); }), { rootMargin: '100px' }).observe(W);
});
