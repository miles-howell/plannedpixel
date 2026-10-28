// Planned Pixel extras. The site works without JavaScript; this only adds
// NEW badges and project image previews.
(function () {
  var DAY = 24 * 60 * 60 * 1000;
  var NEW_WINDOW = 45 * DAY;
  var now = Date.now();

  // NEW badges on anything updated in the last 45 days.
  document.querySelectorAll('[data-updated]').forEach(function (el) {
    var updated = Date.parse(el.getAttribute('data-updated'));
    var badge = el.querySelector('.new');
    if (badge && !isNaN(updated) && now - updated <= NEW_WINDOW) badge.hidden = false;
  });

  // Hovering or focusing a project link shows that project's image beside it.
  // Only on devices that can hover; a tap goes straight to the project page.
  var links = document.querySelectorAll('a[data-preview]');
  if (!links.length || !window.matchMedia('(hover: hover) and (pointer: fine)').matches) return;

  var GAP = 18;
  var tip = document.createElement('div');
  tip.className = 'preview';
  tip.setAttribute('aria-hidden', 'true');
  document.body.appendChild(tip);

  // One <img> per project image, kept in the tip. Reusing a single <img> and
  // changing its src leaves the previous project's image on screen until the
  // new one has loaded, so each image gets its own element and only the one
  // for the hovered link is shown, and only once it has loaded.
  var shots = {};
  var shown = null;   // the shot whose <img> is currently unhidden
  var wanted = null;  // the shot for the link being hovered or focused, if any

  function shot(src) {
    var s = shots[src];
    if (s) return s;
    var el = document.createElement('img');
    el.alt = '';
    el.width = 1600;
    el.height = 1000;
    el.hidden = true;
    s = shots[src] = { el: el, ready: false };
    el.addEventListener('load', function () {
      s.ready = true;
      if (wanted === s) reveal();
    });
    el.src = src;
    tip.appendChild(el);
    return s;
  }

  function reveal() { tip.classList.toggle('is-visible', !!wanted && wanted.ready); }

  // Keep the preview inside the viewport: right of and below the point if it
  // fits, otherwise flipped to the other side (above `above`, when given).
  function place(x, y, above) {
    var w = tip.offsetWidth, h = tip.offsetHeight;
    var vw = document.documentElement.clientWidth, vh = window.innerHeight;
    var left = x + GAP + w > vw ? x - GAP - w : x + GAP;
    var top = y + GAP + h > vh ? (above === undefined ? y : above) - GAP - h : y + GAP;
    tip.style.left = Math.max(8, left) + 'px';
    tip.style.top = Math.max(8, top) + 'px';
  }

  function show(link) {
    wanted = shot(link.getAttribute('data-preview'));
    if (shown !== wanted) {
      if (shown) shown.el.hidden = true;
      wanted.el.hidden = false;
      shown = wanted;
    }
    reveal();
  }

  function hide() { wanted = null; reveal(); }

  links.forEach(function (link) {
    link.addEventListener('mouseenter', function (e) { show(link); place(e.clientX, e.clientY); });
    link.addEventListener('mousemove', function (e) { place(e.clientX, e.clientY); });
    link.addEventListener('mouseleave', hide);
    link.addEventListener('focus', function () {
      var r = link.getBoundingClientRect();
      show(link);
      place(r.left, r.bottom, r.top);
    });
    link.addEventListener('blur', hide);
  });
  window.addEventListener('scroll', hide, { passive: true });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') hide(); });

  // Warm the cache once the page has loaded and the browser is idle, so the
  // first hover on each project doesn't wait on the network. The images are
  // created here, not listed in the HTML, so crawlers and the initial page
  // load never see them; skipped when the visitor has asked to save data.
  function preload() {
    links.forEach(function (link) { shot(link.getAttribute('data-preview')); });
  }
  var connection = navigator.connection;
  if (!(connection && connection.saveData)) {
    var idle = window.requestIdleCallback || function (fn) { setTimeout(fn, 200); };
    if (document.readyState === 'complete') idle(preload);
    else window.addEventListener('load', function () { idle(preload); });
  }
})();
