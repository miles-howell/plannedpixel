// Animated "pixelated redaction" for the hero stat. The value is always
// random digits, re-pixelated at a changing block size; nothing real is shown.
(function () {
  var host = document.querySelector('.redacted');
  if (!host) return;
  var W = 96, H = 28, dpr = Math.min(window.devicePixelRatio || 1, 2);
  var canvas = document.createElement('canvas');
  canvas.width = W * dpr; canvas.height = H * dpr;
  canvas.style.width = W + 'px'; canvas.style.height = H + 'px';
  canvas.setAttribute('aria-hidden', 'true');
  host.appendChild(canvas);
  var ctx = canvas.getContext('2d');
  var src = document.createElement('canvas');
  src.width = W; src.height = H;
  var sctx = src.getContext('2d', { willReadFrequently: true });
  var ink = getComputedStyle(document.documentElement).getPropertyValue('--ink').trim() || '#0b0d33';
  // One loop is 26 steps x 120ms = 3.12s, the same as the old 12 x 260ms.
  var STEPS = 26, MAX_BLOCK = 18, MIN_BLOCK = 6, INTERVAL = 120;

  function rng(seed) {
    return function () { seed = (seed * 1664525 + 1013904223) >>> 0; return seed / 4294967296; };
  }

  function draw(step) {
    var r = rng(Math.floor(step / STEPS) * 7919 + 17);
    var text = '' + (1 + Math.floor(r() * 9)) + Math.floor(r() * 10) + Math.floor(r() * 10);
    sctx.clearRect(0, 0, W, H);
    sctx.fillStyle = '#000';
    sctx.font = '700 26px "Courier New", monospace';
    sctx.textAlign = 'center'; sctx.textBaseline = 'middle';
    sctx.fillText(text, W / 2, H / 2 + 1);
    var data = sctx.getImageData(0, 0, W, H).data;
    // Triangle wave: coarse -> fine -> coarse, one block-size change per step.
    var tri = 1 - Math.abs(2 * ((step % STEPS) / STEPS) - 1);
    var b = Math.round(MAX_BLOCK - (MAX_BLOCK - MIN_BLOCK) * tri);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, W, H);
    ctx.fillStyle = ink;
    for (var y = 0; y < H; y += b) {
      for (var x = 0; x < W; x += b) {
        var sum = 0, n = 0;
        for (var j = y; j < Math.min(y + b, H); j++)
          for (var i = x; i < Math.min(x + b, W); i++) { sum += data[(j * W + i) * 4 + 3]; n++; }
        var a = Math.round((sum / n / 255) * 5) / 5; // quantize to 6 levels
        // keep a faint floor so the whole block reads as one hidden patch
        ctx.globalAlpha = 0.12 + a * 0.88;
        ctx.fillRect(x, y, Math.min(b, W - x), Math.min(b, H - y));
      }
    }
    ctx.globalAlpha = 1;
  }

  window.PPRedacted = { draw: draw };
  var step = 0;
  draw(step);
  if (window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  window.PPRedacted.timer = setInterval(function () { draw(++step); }, INTERVAL);
})();
