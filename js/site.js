// Planned Pixel extras. The site works without JavaScript; this only adds
// NEW badges.
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
})();
