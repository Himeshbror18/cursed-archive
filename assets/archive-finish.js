/* Cursed Archive — editorial interaction layer. */
(() => {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const fine = matchMedia('(pointer: fine)').matches;
  const root = document.documentElement;
  const body = document.body;

  // Progressive reveal: motion communicates hierarchy, not decoration.
  const revealTargets = document.querySelectorAll('.section-head,.system-poster,.cast-feature,.cast-mini,.domain-card,.incident-grid,.support-frame');
  revealTargets.forEach((el, i) => {
    if (reduce) return;
    el.classList.add('js-reveal');
    el.dataset.delay = String(i % 4);
  });

  if (!reduce && 'IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries, obs) => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-visible');
        obs.unobserve(entry.target);
      });
    }, {threshold:.12, rootMargin:'0px 0px -8% 0px'});
    revealTargets.forEach(el => observer.observe(el));
  } else {
    revealTargets.forEach(el => el.classList.add('is-visible'));
  }

  // Scroll position becomes a physical reading cue in the top rule and hero image.
  let scrollRaf = 0;
  const updateScroll = () => {
    const max = Math.max(1, document.documentElement.scrollHeight - innerHeight);
    const p = Math.min(1, Math.max(0, scrollY / max));
    root.style.setProperty('--scroll-progress', p.toFixed(4));

    if (!reduce) {
      const hero = document.querySelector('.hero-media img');
      if (hero && scrollY < innerHeight * 1.15) {
        const drift = Math.min(42, scrollY * .055);
        hero.style.transform = `scale(1.06) translate3d(0, ${drift}px, 0)`;
      }
    }
    scrollRaf = 0;
  };
  addEventListener('scroll', () => {
    if (!scrollRaf) scrollRaf = requestAnimationFrame(updateScroll);
  }, {passive:true});
  updateScroll();

  if (!fine || reduce) return;
  body.classList.add('js-pointer');

  // Quiet geometric cursor marker. It enlarges only over interactive targets.
  let raf = 0, x = innerWidth * .5, y = innerHeight * .35;
  addEventListener('pointermove', e => {
    x = e.clientX; y = e.clientY;
    if (!raf) raf = requestAnimationFrame(() => {
      root.style.setProperty('--mx', `${x}px`);
      root.style.setProperty('--my', `${y}px`);
      raf = 0;
    });
  }, {passive:true});

  document.querySelectorAll('a,button,.domain-card,.cast-feature,.mini').forEach(el => {
    el.addEventListener('pointerenter', () => {
      root.style.setProperty('--cursor-size', '30px');
      document.body.dataset.pointerHot = '1';
    });
    el.addEventListener('pointerleave', () => {
      root.style.setProperty('--cursor-size', '22px');
      delete document.body.dataset.pointerHot;
    });
  });

  // Keep any existing tilt interactions from getting stuck when the pointer leaves.
  document.querySelectorAll('.tilt').forEach(el => {
    el.addEventListener('pointerleave', () => el.style.removeProperty('transform'));
  });
})();
