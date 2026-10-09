// Planned Pixel extras. The site works without JavaScript; this only adds
// NEW! badges, the random ring stop and the per-browser visit counter.
(function () {
  var DAY = 24 * 60 * 60 * 1000;
  var NEW_WINDOW = 45 * DAY;
  var now = Date.now();

  // NEW! badges on anything updated in the last 45 days.
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

  // Visit counter: counted by your browser, once per session. Nothing is sent anywhere.
  var counter = document.querySelector('[data-visits]');
  if (counter) {
    var visits = 1;
    try {
      visits = parseInt(localStorage.getItem('pp-visits') || '0', 10) || 0;
      if (!sessionStorage.getItem('pp-counted')) {
        visits += 1;
        localStorage.setItem('pp-visits', String(visits));
        sessionStorage.setItem('pp-counted', '1');
      }
      visits = Math.max(visits, 1);
    } catch (err) {
      visits = 1;
    }
    var digits = ('000000' + visits).slice(-6).split('');
    counter.querySelectorAll('.digit').forEach(function (digit, i) {
      digit.textContent = digits[i];
    });
    counter.setAttribute('aria-label', 'You have visited ' + visits + (visits === 1 ? ' time' : ' times'));
  }
})();
