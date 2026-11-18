(() => {
  const NUM = ['one', 'two', 'three', 'four', 'five', 'six', 'seven'];
  const TITLE = {"one": "contrast", "two": "error correction", "three": "quiet space", "four": "uniqueness", "five": "universality", "six": "digital eyes", "seven": "meaning-making"};
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
