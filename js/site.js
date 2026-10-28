// Planned Pixel extras. The site works without JavaScript; this only adds
// NEW badges and the random ring stop.
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

  // Random ring stop: any project except the one you're on.
  var ring = window.PP_RING || [];
  var here = document.body.getAttribute('data-ring');
  var root = document.body.getAttribute('data-root') || '';
  document.querySelectorAll('[data-ring-random]').forEach(function (link) {
    link.addEventListener('click', function (event) {
      var stops = ring.filter(function (slug) { return slug !== here; });
      if (!stops.length) return;
      event.preventDefault();
      var pick = stops[Math.floor(Math.random() * stops.length)];
      window.location.href = root + 'projects/' + pick + '.html';
    });
  });

})();
