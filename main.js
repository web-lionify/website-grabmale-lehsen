// Grabmale aus Lehsen – kleine Helfer, ohne externe Bibliotheken
(function () {
  // Mobile Navigation
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.getElementById('nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  // Ausklappmenü: per Tastatur schließen
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && document.activeElement && document.activeElement.closest('.has-sub')) document.activeElement.blur();
  });

  // Jahr im Footer
  var y = document.getElementById('year');
  if (y) y.textContent = new Date().getFullYear();

  // Winterrabatt-Banner wird direkt im HTML (vor dem ersten Anzeigen) eingeblendet

  // Kontaktformular: Zeitstempel (Spam-Schutz) und Statusmeldung
  var ts = document.getElementById('ts');
  if (ts) ts.value = Math.floor(Date.now() / 1000);
  var status = new URLSearchParams(location.search).get('status');
  if (status === 'ok' || status === 'fehler') {
    var box = document.getElementById(status === 'ok' ? 'msg-ok' : 'msg-err');
    if (box) { box.hidden = false; box.scrollIntoView({ block: 'center' }); }
  }

  // FAQ: Frage aus Link (#frage-…) direkt aufklappen
  function openHash() {
    var id = decodeURIComponent(location.hash.slice(1));
    var el = id && document.getElementById(id);
    if (el && el.tagName === 'DETAILS') { el.open = true; el.scrollIntoView({ block: 'start' }); }
  }
  openHash();
  window.addEventListener('hashchange', openHash);

  // Suche im Header (Index wird erst beim ersten Öffnen geladen)
  (function () {
    var btn = document.querySelector('.search-toggle');
    var box = document.getElementById('suche');
    if (!btn || !box) return;
    var input = document.getElementById('q');
    var drop = box.querySelector('.hsearch-drop');
    var list = document.getElementById('q-treffer');
    var empty = box.querySelector('.hsearch-empty');
    var script = document.querySelector('script[src*="main.js"]');
    var base = script ? new URL('.', script.src).href : location.origin + '/';
    var index = null, loading = null, hits = [], active = -1;
    var FIELDS = [['t', 0], ['h', 2], ['a', 3], ['d', 4], ['x', 6]];

    function norm(s) {
      return (s || '').toLowerCase()
        .replace(/ä/g, 'ae').replace(/ö/g, 'oe').replace(/ü/g, 'ue').replace(/ß/g, 'ss')
        .replace(/[^a-z0-9]+/g, ' ');
    }
    function load() {
      if (index) return Promise.resolve(index);
      if (!loading) {
        loading = fetch(new URL(btn.getAttribute('data-index'), base).href)
          .then(function (r) { return r.json(); })
          .then(function (data) {
            index = data.map(function (e) {
              var n = {};
              FIELDS.forEach(function (f) { n[f[0]] = ' ' + norm(e[f[0]]); });
              return { e: e, n: n };
            });
            return index;
          })
          .catch(function () { loading = null; return []; });
      }
      return loading;
    }
    function rank(it, words) {
      var total = 0, field = null;
      for (var i = 0; i < words.length; i++) {
        var w = words[i], best = 99, bf = null;
        for (var j = 0; j < FIELDS.length; j++) {
          var k = FIELDS[j][0], txt = it.n[k], pos = txt.indexOf(w);
          if (pos === -1) continue;
          var sc = FIELDS[j][1] + (txt.indexOf(' ' + w) === -1 ? 1 : 0);
          if (k === 't' && txt.indexOf(' ' + w) === 0) sc -= 1;
          if (sc < best) { best = sc; bf = k; }
        }
        if (bf === null) return null;
        total += best;
        if (!field) field = bf;
      }
      var kindBonus = { 'Seite': 0, 'Häufige Frage': 0.5, 'Steinsorte': 0.5, 'Ort': 0.3, 'Friedhofssatzung': 1, 'Rechtliches': 3 }[it.e.s] || 0;
      return { s: total + kindBonus, f: field };
    }
    // Ausschnitt rund um den ersten Treffer im Originaltext
    function snippet(text, words) {
      if (!text) return '';
      var n = '', map = [];
      for (var c = 0; c < text.length; c++) {
        var ch = norm(text[c]) || ' ';
        for (var k = 0; k < ch.length; k++) { n += ch[k]; map.push(c); }
      }
      var pos = -1;
      for (var i = 0; i < words.length && pos === -1; i++) pos = n.indexOf(words[i]);
      if (pos === -1) return text.length > 140 ? text.slice(0, 140) + ' …' : text;
      var p = map[pos], start = Math.max(0, p - 50), end = Math.min(text.length, p + 100);
      while (start > 0 && text[start - 1] !== ' ') start--;
      while (end < text.length && text[end] !== ' ') end++;
      return (start > 0 ? '… ' : '') + text.slice(start, end).trim() + (end < text.length ? ' …' : '');
    }
    function mark(el, text, words) {
      var re = new RegExp('(' + words.map(function (w) { return w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); }).join('|') + ')', 'gi');
      text.split(re).forEach(function (part, i) {
        if (i % 2) { var m = document.createElement('mark'); m.textContent = part; el.appendChild(m); }
        else if (part) el.appendChild(document.createTextNode(part));
      });
    }
    function render() {
      var q = norm(input.value).trim();
      list.textContent = '';
      active = -1;
      input.removeAttribute('aria-activedescendant');
      if (q.length < 2) { hits = []; drop.hidden = true; input.setAttribute('aria-expanded', 'false'); return; }
      load().then(function (idx) {
        if (norm(input.value).trim() !== q) return;
        var words = q.split(' ');
        hits = idx.map(function (it) { var r = rank(it, words); return r && { it: it, r: r }; })
          .filter(Boolean)
          .sort(function (a, b) { return a.r.s - b.r.s; })
          .slice(0, 8);
        var raw = input.value.trim().split(/\s+/).filter(function (w) { return w.length > 1; });
        list.textContent = '';
        hits.forEach(function (h, i) {
          var e = h.it.e, li = document.createElement('li'), a = document.createElement('a');
          li.id = 'q-t' + i; li.setAttribute('role', 'option');
          a.href = new URL(e.u, base).href;
          var kind = document.createElement('span'); kind.className = 'kind'; kind.textContent = e.s;
          var t = document.createElement('strong'); mark(t, e.t, raw);
          var src = h.r.f === 'a' ? 'Bild: ' + snippet(e.a, words) : (h.r.f === 'x' ? snippet(e.x, words) : (h.r.f === 'h' && e.s !== 'Ort' ? snippet(e.h, words) : e.d));
          var sm = document.createElement('small'); mark(sm, src || '', raw);
          a.appendChild(kind); a.appendChild(t); a.appendChild(sm);
          a.addEventListener('click', close);
          li.appendChild(a); list.appendChild(li);
        });
        empty.hidden = hits.length > 0;
        list.hidden = hits.length === 0;
        drop.hidden = false;
        input.setAttribute('aria-expanded', hits.length ? 'true' : 'false');
      });
    }
    function setActive(i) {
      var lis = list.children;
      if (!lis.length) return;
      active = (i + lis.length) % lis.length;
      for (var j = 0; j < lis.length; j++) lis[j].classList.toggle('active', j === active);
      lis[active].scrollIntoView({ block: 'nearest' });
      input.setAttribute('aria-activedescendant', 'q-t' + active);
    }
    function open() {
      box.hidden = false;
      btn.setAttribute('aria-expanded', 'true');
      if (nav) { nav.classList.remove('open'); if (toggle) toggle.setAttribute('aria-expanded', 'false'); }
      input.focus();
      load();
      if (input.value) render();
    }
    function close() {
      box.hidden = true; drop.hidden = true;
      btn.setAttribute('aria-expanded', 'false');
      input.setAttribute('aria-expanded', 'false');
    }
    btn.addEventListener('click', function () { if (box.hidden) open(); else close(); });
    box.querySelector('.hsearch-close').addEventListener('click', function () { close(); btn.focus(); });
    box.querySelector('form').addEventListener('submit', function (e) {
      e.preventDefault();
      var h = hits[active >= 0 ? active : 0];
      if (h) { location.href = new URL(h.it.e.u, base).href; close(); }
    });
    input.addEventListener('input', render);
    input.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowDown') { e.preventDefault(); setActive(active + 1); }
      else if (e.key === 'ArrowUp') { e.preventDefault(); setActive(active - 1); }
      else if (e.key === 'Escape') { close(); btn.focus(); }
    });
    document.addEventListener('click', function (e) {
      if (!box.hidden && !e.target.closest('#suche') && !e.target.closest('.search-toggle')) close();
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === '/' && box.hidden && !/input|textarea|select/i.test((document.activeElement || {}).tagName || '')) { e.preventDefault(); open(); }
    });
  })();

  // Lightbox für Galerien
  var links = Array.prototype.slice.call(document.querySelectorAll('a[data-lb]'));
  if (!links.length) return;
  var lb = document.createElement('div');
  lb.className = 'lb';
  lb.setAttribute('role', 'dialog');
  lb.setAttribute('aria-modal', 'true');
  lb.setAttribute('aria-label', 'Bildansicht');
  lb.innerHTML = '<img alt=""><video controls playsinline muted preload="none" hidden></video><button class="lb-close" aria-label="Schließen">×</button>' +
    '<button class="lb-prev" aria-label="Vorheriges Bild">‹</button>' +
    '<button class="lb-next" aria-label="Nächstes Bild">›</button><div class="lb-count"></div>';
  document.body.appendChild(lb);
  var img = lb.querySelector('img');
  var vid = lb.querySelector('video');
  var count = lb.querySelector('.lb-count');
  var idx = 0, lastFocus = null;

  function show(i) {
    idx = (i + links.length) % links.length;
    var href = links[idx].getAttribute('href');
    var isVid = /\.mp4(\?|$)/.test(href);
    vid.pause();
    img.hidden = isVid; vid.hidden = !isVid;
    if (isVid) { img.removeAttribute('src'); vid.poster = links[idx].querySelector('img').src; vid.src = href; vid.setAttribute('aria-label', links[idx].querySelector('img').alt); vid.play().catch(function () {}); }
    else { vid.removeAttribute('src'); vid.load(); img.src = href; }
    img.alt = links[idx].querySelector('img').alt;
    count.textContent = (idx + 1) + ' / ' + links.length;
  }
  function open(i) { lastFocus = document.activeElement; show(i); lb.classList.add('open'); document.body.style.overflow = 'hidden'; lb.querySelector('.lb-close').focus(); }
  function close() { vid.pause(); lb.classList.remove('open'); document.body.style.overflow = ''; if (lastFocus) lastFocus.focus(); }

  links.forEach(function (a, i) {
    a.addEventListener('click', function (e) { e.preventDefault(); open(i); });
  });
  lb.querySelector('.lb-close').addEventListener('click', close);
  lb.querySelector('.lb-prev').addEventListener('click', function () { show(idx - 1); });
  lb.querySelector('.lb-next').addEventListener('click', function () { show(idx + 1); });
  lb.addEventListener('click', function (e) { if (e.target === lb) close(); });
  document.addEventListener('keydown', function (e) {
    if (!lb.classList.contains('open')) return;
    if (e.key === 'Escape') close();
    if (e.key === 'ArrowLeft') show(idx - 1);
    if (e.key === 'ArrowRight') show(idx + 1);
  });
  // Wischen auf dem Handy
  var sx = null;
  lb.addEventListener('touchstart', function (e) { sx = e.touches[0].clientX; }, { passive: true });
  lb.addEventListener('touchend', function (e) {
    if (sx === null) return;
    var dx = e.changedTouches[0].clientX - sx;
    if (Math.abs(dx) > 50) show(idx + (dx < 0 ? 1 : -1));
    sx = null;
  });
})();
