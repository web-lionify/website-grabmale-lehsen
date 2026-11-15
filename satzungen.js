// Friedhofssatzungen: Ortssuche mit Trefferliste und Karte (OpenStreetMap erst nach Einwilligung)
(function () {
  var dataEl = document.getElementById('satz-data');
  var DATA = dataEl ? JSON.parse(dataEl.textContent) : { markers: [], search: [], lehsen: [53.49, 11.03] };
  var markersData = DATA.markers, LEHSEN = DATA.lehsen;
  var input = document.getElementById('ortsuche');
  var results = document.getElementById('search-results');
  var empty = document.getElementById('search-empty');
  var items = Array.prototype.slice.call(document.querySelectorAll('.satzungen li[data-search]'));
  var map = null, layers = {}, mapReady = false;

  function norm(s) {
    return (s || '').toLowerCase()
      .replace(/ä/g, 'ae').replace(/ö/g, 'oe').replace(/ü/g, 'ue').replace(/ß/g, 'ss')
      .replace(/[^a-z0-9]+/g, ' ').trim();
  }
  var index = DATA.search.map(function (e) { return { e: e, n: norm(e.n), k: norm(e.k) }; });

  // ---------- Trefferliste ----------
  var hits = [], active = -1;

  function score(it, q) {
    if (it.n === q) return 0;
    if (it.n.indexOf(q) === 0) return 1;
    if ((' ' + it.n).indexOf(' ' + q) !== -1) return 2;
    if (it.n.indexOf(q) !== -1) return 3;
    if ((' ' + it.k).indexOf(' ' + q) !== -1) return 4;
    if (it.k.indexOf(q) !== -1) return 5;
    return -1;
  }

  function render() {
    var q = norm(input.value);
    results.textContent = '';
    active = -1;
    if (!q) { hits = []; results.hidden = true; empty.hidden = true; input.setAttribute('aria-expanded', 'false'); highlightMarkers(''); return; }
    hits = index.map(function (it) { return { it: it, s: score(it, q) }; })
      .filter(function (x) { return x.s >= 0; })
      .sort(function (a, b) { return a.s - b.s || a.it.e.d - b.it.e.d; })
      .slice(0, 8).map(function (x) { return x.it.e; });
    hits.forEach(function (e, i) {
      var li = document.createElement('li');
      li.setAttribute('role', 'option');
      li.id = 'treffer-' + i;
      var a = document.createElement('a');
      a.href = e.u;
      var strong = document.createElement('strong'); strong.textContent = e.n;
      var small = document.createElement('small'); small.textContent = e.sub;
      a.appendChild(strong); a.appendChild(small);
      li.appendChild(a);
      results.appendChild(li);
    });
    results.hidden = hits.length === 0;
    empty.hidden = hits.length > 0;
    input.setAttribute('aria-expanded', hits.length ? 'true' : 'false');
    highlightMarkers(q);
  }

  function setActive(i) {
    var lis = results.children;
    if (!lis.length) return;
    active = (i + lis.length) % lis.length;
    for (var j = 0; j < lis.length; j++) lis[j].classList.toggle('active', j === active);
    input.setAttribute('aria-activedescendant', 'treffer-' + active);
  }

  if (input) {
    input.addEventListener('input', render);
    input.addEventListener('focus', function () { if (input.value) render(); });
    input.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowDown') { e.preventDefault(); setActive(active + 1); }
      else if (e.key === 'ArrowUp') { e.preventDefault(); setActive(active - 1); }
      else if (e.key === 'Enter') {
        var target = hits[active >= 0 ? active : 0];
        if (target) { e.preventDefault(); location.href = target.u; }
      } else if (e.key === 'Escape') { results.hidden = true; input.setAttribute('aria-expanded', 'false'); }
    });
    document.addEventListener('click', function (e) {
      if (!e.target.closest('.search-box')) { results.hidden = true; input.setAttribute('aria-expanded', 'false'); }
    });
  }
  Array.prototype.forEach.call(document.querySelectorAll('[data-quick]'), function (b) {
    b.addEventListener('click', function (e) { e.stopPropagation(); input.value = b.getAttribute('data-quick'); render(); input.focus(); });
  });

  // ---------- Karte ----------
  var consent = document.getElementById('map-consent');
  var loadBtn = document.getElementById('map-load');
  var remember = document.getElementById('map-remember');
  var KEY = 'osm-karte-erlaubt';

  function storedOk() { try { return localStorage.getItem(KEY) === '1'; } catch (e) { return false; } }

  function loadLeaflet(cb) {
    if (window.L) return cb();
    var css = document.createElement('link');
    css.rel = 'stylesheet'; css.href = 'vendor/leaflet/leaflet.css?v=1.9.4';
    document.head.appendChild(css);
    var js = document.createElement('script');
    js.src = 'vendor/leaflet/leaflet.js?v=1.9.4';
    js.onload = cb;
    document.head.appendChild(js);
  }

  function esc(t) { return String(t).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }

  function focusEntry(id) {
    var li = document.getElementById(id);
    if (!li) return;
    items.forEach(function (x) { x.classList.remove('active'); });
    li.classList.add('active');
    li.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }

  function initMap() {
    consent.hidden = true;
    loadLeaflet(function () {
      var L = window.L;
      map = L.map('map', { scrollWheelZoom: false, zoomControl: true }).setView(LEHSEN, 9);
      var ring = L.circle(LEHSEN, { radius: 30000 });
      L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 18,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a>-Mitwirkende'
      }).addTo(map);
      ring.addTo(map); map.fitBounds(ring.getBounds(), { padding: [10, 10] }); map.removeLayer(ring);
      L.circle(LEHSEN, { radius: 30000, color: '#8a6a3f', weight: 1.5, dashArray: '6 6', fill: true, fillColor: '#8a6a3f', fillOpacity: 0.04, interactive: false }).addTo(map);

      markersData.forEach(function (m) {
        var links = m.l.map(function (x) {
          return '<a href="' + esc(x[1]) + '" target="_blank" rel="noopener">' + esc(x[0]) + ' ↗</a>';
        }).join('<br>') || '<span class="muted">Keine Satzung online – bitte bei der Kirchengemeinde erfragen.</span>';
        var html = '<div class="pop"><strong>' + esc(m.n) + '</strong>' +
          (m.e !== m.n ? '<small>' + esc(m.e) + '</small>' : '') +
          (m.s ? '<a class="pop-summ" href="' + esc(m.s) + '">Zusammenfassung lesen →</a>' : '') +
          '<div class="pop-links">' + links + '</div>' +
          '<a href="#' + m.id + '" class="pop-more" data-id="' + m.id + '">In der Liste anzeigen ↓</a></div>';
        var mk = L.circleMarker(m.p, { radius: 7, color: '#fff', weight: 2, fillColor: '#6f552f', fillOpacity: 1 })
          .bindPopup(html, { maxWidth: 280 })
          .bindTooltip(m.n, { direction: 'top', offset: [0, -6] })
          .addTo(map);
        (layers[m.id] = layers[m.id] || []).push(mk);
        mk._own = norm(m.n);
        mk._name = norm(m.n + ' ' + m.e);
      });

      L.circleMarker(LEHSEN, { radius: 9, color: '#fff', weight: 3, fillColor: '#1f2124', fillOpacity: 1 })
        .bindTooltip('Lehsen – Grabmale aus Lehsen', { permanent: true, direction: 'right', offset: [10, 0], className: 'tip-home' })
        .addTo(map);

      map.on('popupopen', function (e) {
        var a = e.popup.getElement().querySelector('.pop-more');
        if (a) a.addEventListener('click', function (ev) { ev.preventDefault(); focusEntry(a.getAttribute('data-id')); });
      });
      map.on('click focus', function () { map.scrollWheelZoom.enable(); });
      map.on('mouseout', function () { map.scrollWheelZoom.disable(); });

      mapReady = true;
      highlightMarkers(norm(input ? input.value : ''));
    });
  }

  function highlightMarkers(q) {
    if (!mapReady) return;
    var hitPts = [];
    var byName = false;
    if (q) Object.keys(layers).forEach(function (id) { layers[id].forEach(function (mk) { if (mk._own.indexOf(q) !== -1) byName = true; }); });
    Object.keys(layers).forEach(function (id) {
      layers[id].forEach(function (mk) {
        var on = !q || (byName ? mk._own.indexOf(q) !== -1 : mk._name.indexOf(q) !== -1);
        mk.setStyle({ fillColor: on ? '#6f552f' : '#b9b2a6', fillOpacity: on ? 1 : 0.5, radius: q && on ? 9 : 7 });
        if (q && on) { mk.bringToFront(); hitPts.push(mk.getLatLng()); }
      });
    });
    if (q && hitPts.length) {
      if (hitPts.length === 1) map.flyTo(hitPts[0], 11, { duration: 0.5 });
      else map.flyToBounds(hitPts, { padding: [40, 40], maxZoom: 11, duration: 0.5 });
    }
  }

  if (loadBtn) {
    loadBtn.addEventListener('click', function () {
      if (remember && remember.checked) { try { localStorage.setItem(KEY, '1'); } catch (e) {} }
      initMap();
    });
  }
  if (consent && storedOk()) initMap();

  // Klick auf Eintrag in der Liste -> Karte zentrieren (falls geladen)
  items.forEach(function (li) {
    li.addEventListener('click', function (e) {
      if (e.target.closest('a') || !mapReady) return;
      var mks = layers[li.id] || [];
      if (mks.length === 1) { map.flyTo(mks[0].getLatLng(), 12, { duration: 0.6 }); mks[0].openPopup(); }
      else if (mks.length > 1) map.flyToBounds(mks.map(function (m) { return m.getLatLng(); }), { padding: [40, 40], maxZoom: 12, duration: 0.6 });
      document.getElementById('map').scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
  });
})();
