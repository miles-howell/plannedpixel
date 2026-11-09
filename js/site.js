// Planned Pixel extras. The site works without JavaScript; this only adds
// a custom in-page scroll, a contact modal and project image previews.
(function () {
  // In-page links glide to their target on a parabolic ease (two quadratic
  // halves: accelerate, then decelerate), slower than the browser's default
  // smooth scroll. The skip link (#main) keeps its instant jump. Links whose
  // click is already handled (the contact modal) are left alone.
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)');
  var raf = null;

  function ease(t) { return t < 0.5 ? 2 * t * t : 1 - 2 * (1 - t) * (1 - t); }

  function stop() { if (raf) { cancelAnimationFrame(raf); raf = null; } }
  ['wheel', 'touchstart', 'keydown'].forEach(function (ev) {
    window.addEventListener(ev, stop, { passive: true });
  });

  function scrollTo(y) { window.scrollTo({ top: y, behavior: 'instant' }); }

  document.addEventListener('click', function (e) {
    if (e.defaultPrevented || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || e.button) return;
    var a = e.target.closest && e.target.closest('a[href^="#"]');
    if (!a) return;
    var hash = a.getAttribute('href');
    if (hash.length < 2 || hash === '#main') return;
    var target = document.getElementById(decodeURIComponent(hash.slice(1)));
    if (!target) return;
    e.preventDefault();
    stop();

    // Respect the target's scroll-margin-top, as the native jump does.
    var margin = parseFloat(getComputedStyle(target).scrollMarginTop) || 0;
    var maxY = document.documentElement.scrollHeight - window.innerHeight;
    var to = Math.max(0, Math.min(maxY, target.getBoundingClientRect().top + window.pageYOffset - margin));
    var from = window.pageYOffset;

    if (location.hash !== hash) history.pushState(null, '', hash);
    // Move focus like native anchor navigation, without the browser's own scroll.
    if (!target.hasAttribute('tabindex') && !/^(A|BUTTON|INPUT|SELECT|TEXTAREA)$/.test(target.tagName)) {
      target.setAttribute('tabindex', '-1');
    }
    target.focus({ preventScroll: true });

    if (reduce.matches || Math.abs(to - from) < 2) { scrollTo(to); return; }
    // ~1.4x the feel of native smooth scroll: 700ms base + distance, capped.
    var dur = Math.min(2200, 700 + Math.abs(to - from) * 0.45);
    var start = null;
    function frame(now) {
      if (start === null) start = now;
      var t = Math.min(1, (now - start) / dur);
      scrollTo(from + (to - from) * ease(t));
      raf = t < 1 ? requestAnimationFrame(frame) : null;
    }
    raf = requestAnimationFrame(frame);
  });
})();

(function () {
  // "Start a project" opens the contact card as a modal instead of jumping
  // down the page. The card itself stays in place at the bottom; the modal
  // holds a copy. Without JS (or without <dialog>) the plain #contact-title
  // anchor still scrolls there.
  var card = document.querySelector('.cta');
  var links = document.querySelectorAll('a[href="#contact-title"]');
  if (!card || !links.length || typeof HTMLDialogElement !== 'function') return;

  var dialog = document.createElement('dialog');
  dialog.className = 'contact-modal';
  dialog.setAttribute('aria-labelledby', 'contact-modal-title');

  var copy = card.cloneNode(true);
  copy.removeAttribute('aria-labelledby');
  var heading = copy.querySelector('#contact-title');
  if (heading) heading.id = 'contact-modal-title';

  var close = document.createElement('button');
  close.type = 'button';
  close.className = 'modal-close';
  close.setAttribute('aria-label', 'Close');
  close.textContent = '\u00d7';
  copy.insertBefore(close, copy.firstChild);

  dialog.appendChild(copy);
  document.body.appendChild(dialog);

  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)');
  var closing = null;

  function open(e) {
    if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || e.button) return;
    e.preventDefault();
    if (closing) { clearTimeout(closing); closing = null; dialog.classList.remove('closing'); }
    if (dialog.open) return;
    dialog.showModal();
    // Put focus on the main action rather than the close button.
    var action = copy.querySelector('.btn-primary');
    if (action) action.focus({ preventScroll: true });
  }

  function dismiss() {
    if (!dialog.open || closing) return;
    if (reduce.matches) { dialog.close(); return; }
    dialog.classList.add('closing');
    closing = setTimeout(function () {
      closing = null;
      dialog.classList.remove('closing');
      dialog.close();
    }, 550);                          // backdrop fade (0.1s delay + 0.45s)
  }

  // Esc: animate out instead of the instant native close.
  dialog.addEventListener('cancel', function (e) { e.preventDefault(); dismiss(); });
  close.addEventListener('click', dismiss);
  // A click on the dim backdrop lands on the <dialog> itself, not the card.
  dialog.addEventListener('click', function (e) { if (e.target === dialog) dismiss(); });

  links.forEach(function (a) { a.addEventListener('click', open); });
})();

// Project image previews.
(function () {
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
