// Anfahrt: Karte (OpenStreetMap erst nach Einwilligung)
(function () {
  var data = JSON.parse((document.getElementById('anfahrt-data') || {}).textContent || '{}');
  var pos = data.lehsen || [53.4873, 11.0181];
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
  function init() {
    consent.hidden = true;
    loadLeaflet(function () {
      var L = window.L;
      var map = L.map('map', { scrollWheelZoom: false }).setView(pos, 12);
      L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 18,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a>-Mitwirkende'
      }).addTo(map);
      L.circleMarker(pos, { radius: 10, color: '#fff', weight: 3, fillColor: '#1f2124', fillOpacity: 1 })
        .bindTooltip('Grabmale aus Lehsen', { permanent: true, direction: 'right', offset: [12, 0], className: 'tip-home' })
        .addTo(map);
      map.on('click focus', function () { map.scrollWheelZoom.enable(); });
      map.on('mouseout', function () { map.scrollWheelZoom.disable(); });
    });
  }
  if (loadBtn) loadBtn.addEventListener('click', function () {
    if (remember && remember.checked) { try { localStorage.setItem(KEY, '1'); } catch (e) {} }
    init();
  });
  if (consent && storedOk()) init();
})();
