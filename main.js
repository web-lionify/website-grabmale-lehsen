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

  // Lightbox für Galerien
  var links = Array.prototype.slice.call(document.querySelectorAll('a[data-lb]'));
  if (!links.length) return;
  var lb = document.createElement('div');
  lb.className = 'lb';
  lb.setAttribute('role', 'dialog');
  lb.setAttribute('aria-modal', 'true');
  lb.setAttribute('aria-label', 'Bildansicht');
  lb.innerHTML = '<img alt=""><button class="lb-close" aria-label="Schließen">×</button>' +
    '<button class="lb-prev" aria-label="Vorheriges Bild">‹</button>' +
    '<button class="lb-next" aria-label="Nächstes Bild">›</button><div class="lb-count"></div>';
  document.body.appendChild(lb);
  var img = lb.querySelector('img');
  var count = lb.querySelector('.lb-count');
  var idx = 0, lastFocus = null;

  function show(i) {
    idx = (i + links.length) % links.length;
    img.src = links[idx].getAttribute('href');
    img.alt = links[idx].querySelector('img').alt;
    count.textContent = (idx + 1) + ' / ' + links.length;
  }
  function open(i) { lastFocus = document.activeElement; show(i); lb.classList.add('open'); document.body.style.overflow = 'hidden'; lb.querySelector('.lb-close').focus(); }
  function close() { lb.classList.remove('open'); document.body.style.overflow = ''; if (lastFocus) lastFocus.focus(); }

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
