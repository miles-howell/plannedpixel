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
  var img = document.createElement('img');
  img.alt = '';
  img.width = 1600;
  img.height = 1000;
  tip.appendChild(img);
  document.body.appendChild(tip);

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
    var src = link.getAttribute('data-preview');
    if (img.getAttribute('src') !== src) img.src = src;
    tip.classList.add('is-visible');
  }

  function hide() { tip.classList.remove('is-visible'); }

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
})();
