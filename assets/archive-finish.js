/* Cursed Archive — restrained interaction layer. */
(() => {
  const fine = matchMedia('(pointer:fine) and (prefers-reduced-motion:no-preference)');
  if (!fine.matches) return;

  // A single, low-opacity cursor bloom gives panels a sense of depth without looking like a gaming UI.
  const root = document.documentElement;
  let raf = 0, x = innerWidth * .5, y = innerHeight * .35;
  addEventListener('pointermove', e => {
    x = e.clientX; y = e.clientY;
    if (!raf) raf = requestAnimationFrame(() => {
      root.style.setProperty('--mx', `${x}px`);
      root.style.setProperty('--my', `${y}px`);
      raf = 0;
    });
  }, {passive:true});

  // Make the existing tilt interaction settle more naturally at rest.
  document.querySelectorAll('.tilt').forEach(el => {
    el.addEventListener('pointerleave', () => {
      el.style.removeProperty('transform');
    });
  });
})();
