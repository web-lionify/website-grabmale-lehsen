// Friedhofssatzungen: Ortssuche und Karte (OpenStreetMap erst nach Einwilligung)
(function () {
  var markersData = window.SATZUNG_MARKERS || [];
  var input = document.getElementById('ortsuche');
  var info = document.getElementById('search-info');
  var empty = document.getElementById('search-empty');
  var items = Array.prototype.slice.call(document.querySelectorAll('.satzungen li[data-search]'));
  var regions = Array.prototype.slice.call(document.querySelectorAll('[data-region]'));
  var map = null, layers = {}, mapReady = false;

  function norm(s) {
    return (s || '').toLowerCase()
      .replace(/ä/g, 'ae').replace(/ö/g, 'oe').replace(/ü/g, 'ue').replace(/ß/g, 'ss')
      .replace(/[^a-z0-9]+/g, ' ').trim();
  }
  items.forEach(function (li) { li._s = norm(li.getAttribute('data-search')); });

  // ---------- Suche ----------
  function search() {
    var q = norm(input.value);
    var hits = 0;
    items.forEach(function (li) {
      var ok = !q || li._s.indexOf(q) !== -1;
      li.hidden = !ok;
      li.classList.toggle('hit', !!q && ok);
      if (ok) hits++;
    });
    regions.forEach(function (r) {
      if (!r.querySelector('.satzungen li[data-search]')) return; // Kirchenkreis-Block immer zeigen
      r.hidden = !r.querySelector('.satzungen li[data-search]:not([hidden])');
    });
    empty.hidden = !q || hits > 0;
    info.textContent = q ? (hits === 1 ? '1 Eintrag gefunden' : hits + ' Einträge gefunden') : '';
    highlightMarkers(q);
  }
  Array.prototype.forEach.call(document.querySelectorAll('[data-quick]'), function (b) {
    b.addEventListener('click', function () { input.value = b.getAttribute('data-quick'); search(); input.focus(); });
  });
  if (input) {
    input.addEventListener('input', search);
    input.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') {
        e.preventDefault();
        var first = items.filter(function (li) { return !li.hidden; })[0];
        if (first) focusEntry(first.id, true);
      }
    });
  }

  function focusEntry(id, fromSearch) {
    var li = document.getElementById(id);
    if (!li) return;
    items.forEach(function (x) { x.classList.remove('active'); });
    li.classList.add('active');
    if (!fromSearch || window.innerWidth < 900) li.scrollIntoView({ behavior: 'smooth', block: 'center' });
    if (mapReady) {
      var pts = markersData.filter(function (m) { return m.id === id; });
      if (pts.length === 1) map.flyTo(pts[0].p, 12, { duration: 0.6 });
      else if (pts.length > 1) map.flyToBounds(pts.map(function (m) { return m.p; }), { padding: [40, 40], maxZoom: 12, duration: 0.6 });
    }
  }

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

  function initMap() {
    consent.hidden = true;
    loadLeaflet(function () {
      var L = window.L;
      map = L.map('map', { scrollWheelZoom: false, zoomControl: true }).setView(window.LEHSEN, 9);
      var ring = L.circle(window.LEHSEN, { radius: 30000 });
      L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 18,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a>-Mitwirkende'
      }).addTo(map);

      ring.addTo(map); map.fitBounds(ring.getBounds(), { padding: [10, 10] }); map.removeLayer(ring);
      L.circle(window.LEHSEN, { radius: 30000, color: '#8a6a3f', weight: 1.5, dashArray: '6 6', fill: true, fillColor: '#8a6a3f', fillOpacity: 0.04, interactive: false }).addTo(map);

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
        mk.on('click', function () { items.forEach(function (x) { x.classList.toggle('active', x.id === m.id); }); });
        (layers[m.id] = layers[m.id] || []).push(mk);
        mk._name = norm(m.n + ' ' + m.e);
        mk._own = norm(m.n);
      });

      L.circleMarker(window.LEHSEN, { radius: 9, color: '#fff', weight: 3, fillColor: '#1f2124', fillOpacity: 1 })
        .bindTooltip('Lehsen – Grabmale aus Lehsen', { permanent: true, direction: 'right', offset: [10, 0], className: 'tip-home' })
        .addTo(map);

      map.on('popupopen', function (e) {
        var a = e.popup.getElement().querySelector('.pop-more');
        if (a) a.addEventListener('click', function (ev) { ev.preventDefault(); focusEntry(a.getAttribute('data-id')); });
      });
      // Scrollrad erst nach Klick in die Karte aktivieren
      map.on('click focus', function () { map.scrollWheelZoom.enable(); });
      map.on('mouseout', function () { map.scrollWheelZoom.disable(); });

      mapReady = true;
      highlightMarkers(norm(input ? input.value : ''));
    });
  }

  function highlightMarkers(q) {
    if (!mapReady) return;
    var hitPts = [];
    // Erst nach Ortsnamen suchen; nur wenn kein Ort passt, ganze Einträge hervorheben
    var byName = false;
    if (q) Object.keys(layers).forEach(function (id) { layers[id].forEach(function (mk) { if (mk._own.indexOf(q) !== -1) byName = true; }); });
    Object.keys(layers).forEach(function (id) {
      layers[id].forEach(function (mk) {
        var li = document.getElementById(id);
        var on = !q || (byName ? mk._own.indexOf(q) !== -1 : (mk._name.indexOf(q) !== -1 || (li && li._s.indexOf(q) !== -1)));
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

  // Klick auf Eintrag in der Liste -> Karte zentrieren
  items.forEach(function (li) {
    li.addEventListener('click', function (e) {
      if (e.target.closest('a')) return;
      focusEntry(li.id, true);
      if (mapReady) {
        var mk = (layers[li.id] || [])[0];
        if (mk && (layers[li.id] || []).length === 1) mk.openPopup();
        document.getElementById('map').scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    });
  });
})();
