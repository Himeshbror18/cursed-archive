/* ═══════════════════════════════════════════════════════════
   JUJUTSU KAISEN — Cursed Energy Engine
   Vanilla JS · no frameworks · 60fps everywhere
   ═══════════════════════════════════════════════════════════ */

(() => {
  'use strict';

  /* ── State ────────────────────────────── */
  const state = {
    mouse: { x: 0, y: 0, lx: 0, ly: 0, v: 0, moving: false },
    scroll: { y: 0, last: 0, dir: 1 },
    reduced: window.matchMedia('(prefers-reduced-motion: reduce)').matches,
    loaded: false,
  };

  /* ── DOM cache ─────────────────────────── */
  const $ = (s, p = document) => p.querySelector(s);
  const $$ = (s, p = document) => [...p.querySelectorAll(s)];

  const preloader   = $('#preloader');
  const preBar      = $('#preBar');
  const preNum      = $('#preNum');
  const cursorDot   = $('#cursorDot');
  const cursorRing  = $('#cursorRing');
  const fxCanvas    = $('#fx');
  const energyBar   = $('#energyBar');
  const nav         = $('#nav');
  const burger      = $('#burger');
  const drawer      = $('#drawer');
  const roster      = $('#roster');
  const domainVisual= $('#domainVisual');
  const domainOverlay = $('#domainOverlay');
  const doCanvas    = $('#domainCanvas');
  const toTop       = $('#toTop');

  /* ═══════════════════════════════════════════════════════════
     PRELOADER
     ═══════════════════════════════════════════════════════════ */
  const initPreloader = () => {
    const t0 = performance.now();
    const dur = 2200;
    const tick = () => {
      const elapsed = Math.min(1, (performance.now() - t0) / dur);
      const eased = 1 - Math.pow(1 - elapsed, 3);
      preBar.style.width = (eased * 100).toFixed(2) + '%';
      preNum.textContent = Math.round(eased * 100);
      if (elapsed < 1) requestAnimationFrame(tick);
    };
    tick();

    // wait for everything (images, fonts) then fade
    const finish = () => {
      state.loaded = true;
      preBar.style.width = '100%';
      preNum.textContent = '100';
      preloader.classList.add('done');
      setTimeout(() => {
        preloader.style.display = 'none';
        document.body.classList.remove('loading');
      }, 900);
    };
    if (document.readyState === 'complete') {
      setTimeout(finish, 400);
    } else {
      window.addEventListener('load', () => setTimeout(finish, 400));
    }
  };

  /* ═══════════════════════════════════════════════════════════
     CUSTOM CURSOR  +  ripple / slash FX
     ═══════════════════════════════════════════════════════════ */
  const initCursor = () => {
    if (state.reduced) return;
    let rf = 0;
    const move = (e) => {
      state.mouse.x = e.clientX;
      state.mouse.y = e.clientY;
      state.mouse.moving = true;
      clearTimeout(state.mouse._t);
      state.mouse._t = setTimeout(() => state.mouse.moving = false, 80);

      // velocity for slash intensity
      const dx = e.clientX - state.mouse.lx;
      const dy = e.clientY - state.mouse.ly;
      state.mouse.v = Math.hypot(dx, dy);
      state.mouse.lx = e.clientX;
      state.mouse.ly = e.clientY;

      cursorDot.style.transform = `translate(${e.clientX}px,${e.clientY}px)`;
      cursorRing.style.transform = `translate(${e.clientX}px,${e.clientY}px)`;

      if (!rf) rf = requestAnimationFrame(() => {
        rf = 0;
        // subtle scale by velocity
        const s = Math.min(1.18, 1 + state.mouse.v / 520);
        cursorDot.style.transform = `translate(${state.mouse.x}px,${state.mouse.y}px) scale(${s})`;
      });
    };
    window.addEventListener('mousemove', move, { passive: true });

    // hover state
    const hoverables = $$('[data-cursor="link"]');
    hoverables.forEach(el => {
      el.addEventListener('mouseenter', () => cursorRing.classList.add('hover'));
      el.addEventListener('mouseleave', () => cursorRing.classList.remove('hover'));
    });

    // click ripple
    const ripple = (e) => {
      const r = document.createElement('div');
      r.className = 'ripple';
      r.style.left = (e.clientX - 120) + 'px';
      r.style.top = (e.clientY - 120) + 'px';
      document.body.appendChild(r);
      setTimeout(() => r.remove(), 900);
    };
    window.addEventListener('mousedown', ripple);

    // slash on fast movement
    let lastSlash = 0;
    const slash = (e) => {
      if (state.mouse.v < 620 || performance.now() - lastSlash < 160) return;
      lastSlash = performance.now();
      const s = document.createElement('div');
      s.className = 'ripple';
      s.style.border = '1px solid rgba(255,77,94,.7)';
      s.style.width = '140px';
      s.style.height = '6px';
      s.style.left = (e.clientX - 70) + 'px';
      s.style.top = (e.clientY - 3) + 'px';
      s.style.transform = `rotate(${state.mouse.v / 12}deg)`;
      s.style.animation = 'rip .7s var(--ease) forwards';
      document.body.appendChild(s);
      setTimeout(() => s.remove(), 700);
    };
    window.addEventListener('mousemove', slash);
  };

  /* ═══════════════════════════════════════════════════════════
     CANVAS — Cursed Energy Particles (optimized)
     ═══════════════════════════════════════════════════════════ */
  const initCanvas = () => {
    const canvas = fxCanvas;
    const ctx = canvas.getContext('2d', { alpha: true });
    let W, H, dpr;
    const particles = [];
    const embers = [];
    const COLORS = ['#6ee7ff', '#7c5cff', '#ff4d5e', '#fff'];
    let canvasVisible = true;

    // adaptive particle count based on screen size + device capability
    const isMobile = window.matchMedia('(max-width:820px)').matches;
    const isLowPerf = navigator.hardwareConcurrency && navigator.hardwareConcurrency <= 4;
    const PARTICLE_COUNT = isMobile ? 60 : (isLowPerf ? 90 : 130);
    const CONNECT_DIST = isMobile ? 70 : 90;
    const MAX_CONNECTIONS = isMobile ? 3 : 5; // cap per-particle line draws

    const resize = () => {
      dpr = Math.min(window.devicePixelRatio || 1, isMobile ? 1.3 : 1.8);
      W = canvas.offsetWidth;
      H = canvas.offsetHeight;
      canvas.width = W * dpr;
      canvas.height = H * dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    };
    resize();
    let resizeTimer;
    window.addEventListener('resize', () => {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(resize, 150);
    }, { passive: true });

    // pause rendering when tab hidden (saves battery + CPU)
    document.addEventListener('visibilitychange', () => {
      canvasVisible = !document.hidden;
    });

    const spawn = (n) => {
      for (let i = 0; i < n; i++) {
        particles.push({
          x: Math.random() * W,
          y: Math.random() * H,
          vx: (Math.random() - .5) * .35,
          vy: (Math.random() - .5) * .35,
          r: Math.random() * 1.6 + .4,
          c: COLORS[Math.floor(Math.random() * COLORS.length)],
          a: Math.random() * .5 + .25,
        });
      }
    };
    spawn(PARTICLE_COUNT);

    let last = 0;
    const animate = (t) => {
      if (!canvasVisible) { requestAnimationFrame(animate); return; }
      if (!last) last = t;
      const dt = Math.min(24, t - last);
      last = t;

      ctx.clearRect(0, 0, W, H);

      // drift toward mouse
      const mx = state.mouse.x;
      const my = state.mouse.y;
      const mouseActive = state.mouse.moving;

      // batch particle drawing
      for (let i = particles.length - 1; i >= 0; i--) {
        const p = particles[i];
        const dx = mx - p.x;
        const dy = my - p.y;
        const dist2 = dx * dx + dy * dy;
        if (dist2 < 25600 && mouseActive) { // 160^2
          const dist = Math.sqrt(dist2);
          const f = (160 - dist) / 160;
          p.vx += (dx / dist) * .02 * f;
          p.vy += (dy / dist) * .02 * f;
        }
        p.vx *= .93; p.vy *= .93;
        p.x += p.vx; p.y += p.vy;

        // wrap
        if (p.x < -2 || p.x > W + 2) p.vx *= -1, p.x = p.x < 0 ? W : 0;
        if (p.y < -2 || p.y > H + 2) p.vy *= -1, p.y = p.y < 0 ? H : 0;

        // draw
        ctx.globalAlpha = p.a;
        ctx.fillStyle = p.c;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fill();
      }

      // optimized connection pass — early-exit + capped connections
      ctx.strokeStyle = '#6ee7ff';
      ctx.lineWidth = .5;
      const cd2 = CONNECT_DIST * CONNECT_DIST;
      for (let i = 0; i < particles.length; i++) {
        const p = particles[i];
        let connections = 0;
        for (let j = i + 1; j < particles.length && connections < MAX_CONNECTIONS; j++) {
          const q = particles[j];
          const ddx = p.x - q.x;
          const ddy = p.y - q.y;
          const d2 = ddx * ddx + ddy * ddy;
          if (d2 < cd2) {
            const d = Math.sqrt(d2);
            ctx.globalAlpha = (1 - d / CONNECT_DIST) * .18;
            ctx.beginPath();
            ctx.moveTo(p.x, p.y);
            ctx.lineTo(q.x, q.y);
            ctx.stroke();
            connections++;
          }
        }
      }

      // embers (throttled on mobile)
      if (Math.random() < (isMobile ? .08 : .18)) {
        embers.push({
          x: Math.random() * W,
          y: H,
          vx: (Math.random() - .5) * .6,
          vy: -Math.random() * 1.2 - .4,
          r: Math.random() * 2.2 + .6,
          life: 1,
        });
      }
      for (let i = embers.length - 1; i >= 0; i--) {
        const e = embers[i];
        e.vx *= .94; e.vy *= .96;
        e.x += e.vx; e.y += e.vy;
        e.life -= dt * .0009;
        if (e.life <= 0) { embers.splice(i, 1); continue; }
        ctx.globalAlpha = e.life;
        ctx.fillStyle = COLORS[Math.floor(Math.random() * 2)];
        ctx.beginPath();
        ctx.arc(e.x, e.y, e.r * e.life, 0, Math.PI * 2);
        ctx.fill();
      }

      requestAnimationFrame(animate);
    };
    requestAnimationFrame(animate);
  };

  /* ═══════════════════════════════════════════════════════════
     SCROLL REVEALS  +  ENERGY RAIL  +  NAV HIDE
     ═══════════════════════════════════════════════════════════ */
  const initScroll = () => {
    const reveals = $$('.reveal, .reveal-chars');
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(e => {
        if (e.isIntersecting) {
          e.target.classList.add('in');
          observer.unobserve(e.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px' });
    reveals.forEach(r => observer.observe(r));

    // energy rail
    const updateRail = () => {
      const scrollY = window.scrollY;
      const docHeight = document.body.scrollHeight - window.innerHeight;
      const pct = Math.min(100, (scrollY / docHeight) * 100);
      energyBar.style.width = pct + '%';
    };
    updateRail();
    let railTick = 0;
    const onScroll = () => {
      state.scroll.y = window.scrollY;
      state.scroll.dir = window.scrollY > state.scroll.last ? 1 : -1;
      state.scroll.last = window.scrollY;

      // nav hide on scroll down
      if (state.scroll.dir > 0 && state.scroll.y > 160) {
        nav.classList.add('hide');
      } else {
        nav.classList.remove('hide');
      }
      // nav stuck
      if (state.scroll.y > 80) nav.classList.add('stuck');
      else nav.classList.remove('stuck');

      if (!railTick) {
        railTick = requestAnimationFrame(() => {
          updateRail();
          railTick = 0;
        });
      }
    };
    window.addEventListener('scroll', onScroll, { passive: true });
  };

  /* ═══════════════════════════════════════════════════════════
     COUNTERS  +  TEXT SCRAMBLE
     ═══════════════════════════════════════════════════════════ */
  const initCounters = () => {
    const nums = $$('[data-count]');
    const io = new IntersectionObserver((entries) => {
      entries.forEach(e => {
        if (e.isIntersecting) {
          const el = e.target;
          const target = +el.dataset.count;
          const start = 0;
          const dur = 1400;
          const t0 = performance.now();
          const step = (now) => {
            const p = Math.min(1, (now - t0) / dur);
            el.textContent = Math.round(start + (target - start) * (1 - Math.pow(1 - p, 3)));
            if (p < 1) requestAnimationFrame(step);
          };
          requestAnimationFrame(step);
          io.unobserve(el);
        }
      });
    }, { threshold: 0.8 });
    nums.forEach(n => io.observe(n));
  };

  const initScramble = () => {
    const el = $('#typeLine');
    if (!el) return;
    const phrases = [
      'Domain Expansion · Infinite Void',
      'Black Flash · 0.000001 seconds',
      'Hollow Purple · Cursed Technique',
      'Malevolent Shrine · Sukuna\'s domain',
      'Limitless · Six Eyes · Infinity',
    ];
    const chars = 'アァカサタナハマヤラワガザダバパジュストロング';
    let idx = 0;
    const type = () => {
      const full = phrases[idx];
      let i = 0;
      const tick = () => {
        const done = full.slice(0, i);
        const remaining = full.slice(i);
        const noise = remaining.split('').map(() => chars[Math.floor(Math.random() * chars.length)]).join('');
        el.innerHTML = `<span class="done">${done}</span><span class="noise">${noise}</span>`;
        if (i < full.length) {
          i++;
          setTimeout(tick, 55);
        } else {
          el.classList.add('done');
          setTimeout(() => {
            el.classList.remove('done');
            idx = (idx + 1) % phrases.length;
            type();
          }, 2600);
        }
      };
      tick();
    };
    setTimeout(type, 1200);
  };

  /* ═══════════════════════════════════════════════════════════
     MAGNETIC BUTTONS  +  TILT CARDS
     ═══════════════════════════════════════════════════════════ */
  const initMagnetic = () => {
    const items = $$('.magnetic');
    items.forEach(el => {
      el.addEventListener('mousemove', (e) => {
        if (state.reduced) return;
        const r = el.getBoundingClientRect();
        const x = e.clientX - r.left;
        const y = e.clientY - r.top;
        const cx = r.width / 2;
        const cy = r.height / 2;
        const dx = (x - cx) / cx;
        const dy = (y - cy) / cy;
        el.style.transform = `translate(${dx * 6}px,${dy * 6}px)`;
      });
      el.addEventListener('mouseleave', () => {
        el.style.transform = '';
      });
    });
  };

  const initTilt = () => {
    const cards = $$('[data-tilt]');
    cards.forEach(card => {
      card.addEventListener('mousemove', (e) => {
        if (state.reduced) return;
        const r = card.getBoundingClientRect();
        const x = e.clientX - r.left;
        const y = e.clientY - r.top;
        const cx = r.width / 2;
        const cy = r.height / 2;
        const rx = (y - cy) / cy * 6;
        const ry = (x - cx) / cx * 6;
        card.style.transform = `perspective(800px) rotateX(${rx}deg) rotateY(${-ry}deg)`;
        card.style.setProperty('--mx', (x / r.width) * 100 + '%');
        card.style.setProperty('--my', (y / r.height) * 100 + '%');
      });
      card.addEventListener('mouseleave', () => {
        card.style.transform = '';
      });
    });
  };

  /* ═══════════════════════════════════════════════════════════
     SORCERERS ROSTER  (data-driven)
     ═══════════════════════════════════════════════════════════ */
  const SORCERERS = [
    {
      id: 'gojo', name: 'SATORU GOJO', jp: '五条悟', grade: 'SPECIAL',
      tech: 'Limitless · Six Eyes', c: '#6ee7ff', c2: '#7c5cff',
      p: '96%',
      domain: { jp: '無量空処', en: 'INFINITE VOID', desc: 'Infinite information floods the mind. Nothing can act.' },
      bio: 'The strongest sorcerer of his generation. Infinity bends space around him, and his domain leaves opponents drowned in the totality of existence.',
    },
    {
      id: 'yuji', name: 'YUJI ITADORI', jp: '虎杖悠仁', grade: 'SPECIAL',
      tech: 'Divergent Fist · Black Flash', c: '#ff4d5e', c2: '#ffb020',
      p: '84%',
      domain: { jp: '伏魔御厨子', en: 'MALEVOLENT SHRINE', desc: 'Sukuna\'s shrine. Dismantle and Cleave rend everything within.' },
      bio: 'A human blessed with inhuman strength, housing the King of Curses. His right fist splits reality itself.',
    },
    {
      id: 'megumi', name: 'MEGUMI FUSHIGURO', jp: '伏黒恵', grade: 'GRADE 1',
      tech: 'Ten Shadows · Chimera Shadow Garden', c: '#7c5cff', c2: '#6ee7ff',
      p: '72%',
      domain: { jp: '神宝鏡舞', en: 'CHIMERA SHADOW GARDEN', desc: 'Shadows bloom into a garden of divine beasts.' },
      bio: 'A prodigy who summons shadow beasts. His domain is a garden where shadows take on divine, deadly forms.',
    },
    {
      id: 'nobara', name: 'NOBARA KAMITO', jp: '神森野々香', grade: 'GRADE 1',
      tech: 'Hammer & Nail · Straw Doll', c: '#ffb020', c2: '#ff4d5e',
      p: '68%',
      domain: { jp: '呪女郎', en: 'MAIDEN\'S CURSE', desc: 'A vengeful spirit doll that strikes without mercy.' },
      bio: 'Fearless and loud, she fights with a steel hammer and nails that carry her will straight into a curse\'s heart.',
    },
    {
      id: 'sukuna', name: 'RYOMEN SUKUNA', jp: '両面薔夜', grade: 'SPECIAL',
      tech: 'Dismantle · Cleave · Malevolent Shrine', c: '#ff4d5e', c2: '#7c5cff',
      p: '100%',
      domain: { jp: '伏魔御厨子', en: 'MALEVOLENT SHRINE', desc: 'No barriers, no escape. The shrine razes everything to nothing.' },
      bio: 'The King of Curses. Twenty fingers, four arms, and a domain that needs no shrine — it simply is.',
    },
    {
      id: 'nanami', name: 'KENTA NANAMI', jp: '七海建太', grade: 'GRADE 1',
      tech: 'Ratio Technique · Blunt Trauma', c: '#ffb020', c2: '#6ee7ff',
      p: '78%',
      domain: { jp: '金科玉鋼', en: 'IRON MOUNTAIN', desc: 'A blade of absolute precision that never misses its mark.' },
      bio: 'A salaryman who returned to sorcery. His ratio technique finds the one weak point in any defense.',
    },
  ];

  const renderRoster = () => {
    roster.innerHTML = SORCERERS.map(s => `
      <article class="sorc" style="--c:${s.c};--c2:${s.c2};--p:${s.p}" data-sorc="${s.id}">
        <div class="sorc__aura"></div>
        <div class="sorc__grid"></div>
        <div class="sorc__kanji">${s.jp}</div>
        <span class="sorc__grade">${s.grade}</span>
        <span class="sorc__id">#${String(SORCERERS.indexOf(s)+1).padStart(2,'0')}</span>
        <h3 class="sorc__name">${s.name}</h3>
        <div class="sorc__jp">${s.jp}</div>
        <div class="sorc__tech"><em>Cursed Technique</em>${s.tech}</div>
        <div class="meter"><i></i></div>
        <div class="sorc__reveal"><p>${s.bio}</p></div>
        <button class="sorc__btn" data-domain="${s.id}">Expand Domain</button>
      </article>
    `).join('');

    // energy meter fill on view
    const meterObs = new IntersectionObserver((entries) => {
      entries.forEach(e => {
        if (e.isIntersecting) {
          e.target.classList.add('in');
          meterObs.unobserve(e.target);
        }
      });
    }, { threshold: 0.6 });
    $$('.sorc').forEach(s => meterObs.observe(s));

    // domain buttons
    $$('[data-domain]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const id = btn.dataset.domain;
        const s = SORCERERS.find(x => x.id === id);
        openDomain(s);
      });
    });
  };

  /* ═══════════════════════════════════════════════════════════
     DOMAIN EXPANSION  (overlay + canvas FX)
     ═══════════════════════════════════════════════════════════ */
  let domainRaf = 0;
  const openDomain = (s) => {
    if (!s) return;
    document.body.classList.add('locked');
    domainOverlay.classList.add('on');
    domainOverlay.style.setProperty('--dc', s.c);

    $('#doCaster').textContent = s.name;
    $('#doJp').textContent = s.domain.jp;
    $('#doEn').textContent = s.domain.en;
    $('#doDesc').textContent = s.domain.desc;

    // reset animations
    $$('.do-slashes i').forEach(i => i.style.animation = 'none');
    void document.querySelector('.do-slashes').offsetWidth;
    $$('.do-slashes i').forEach(i => i.style.animation = '');

    // canvas FX
    drawDomainCanvas(s);

    // close
    const close = () => {
      domainOverlay.classList.remove('on');
      document.body.classList.remove('locked');
      if (domainRaf) cancelAnimationFrame(domainRaf);
      doCanvas.width = 0; doCanvas.height = 0;
    };
    $('#doClose').onclick = close;
    domainOverlay.onclick = (e) => { if (e.target === domainOverlay) close(); };
    document.onkeydown = (e) => { if (e.key === 'Escape') close(); };
  };

  const drawDomainCanvas = (s) => {
    const canvas = doCanvas;
    const ctx = canvas.getContext('2d');
    let W, H, dpr;
    const isMobile = window.matchMedia('(max-width:820px)').matches;
    const resize = () => {
      dpr = Math.min(window.devicePixelRatio || 1, isMobile ? 1.2 : 1.6);
      W = canvas.offsetWidth; H = canvas.offsetHeight;
      canvas.width = W * dpr; canvas.height = H * dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    };
    resize();
    // note: listener removed on close via clone — keep simple here
    const onResize = () => resize();
    window.addEventListener('resize', onResize, { passive: true });

    const particles = [];
    const COLORS = [s.c, s.c2, '#fff', '#000'];
    const PCOUNT = isMobile ? 60 : 120;
    for (let i = 0; i < PCOUNT; i++) {
      particles.push({
        x: Math.random() * W,
        y: Math.random() * H,
        vx: (Math.random() - .5) * 1.2,
        vy: (Math.random() - .5) * 1.2,
        r: Math.random() * 2.2 + .5,
        a: Math.random() * .6 + .2,
        c: COLORS[Math.floor(Math.random() * COLORS.length)], // set once
      });
    }

    const animate = () => {
      ctx.clearRect(0, 0, W, H);
      for (let i = 0; i < particles.length; i++) {
        const p = particles[i];
        p.vx *= .97; p.vy *= .97;
        p.x += p.vx; p.y += p.vy;
        if (p.x < 0 || p.x > W) p.vx *= -1;
        if (p.y < 0 || p.y > H) p.vy *= -1;
        ctx.globalAlpha = p.a;
        ctx.fillStyle = p.c;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fill();
      }
      // radial pulse
      const t = performance.now() * .001;
      ctx.save();
      ctx.globalCompositeOperation = 'lighter';
      ctx.globalAlpha = .08 + Math.sin(t * 2) * .03;
      const grd = ctx.createRadialGradient(W / 2, H / 2, 0, W / 2, H / 2, Math.min(W, H) / 2);
      grd.addColorStop(0, s.c);
      grd.addColorStop(1, 'transparent');
      ctx.fillStyle = grd;
      ctx.fillRect(0, 0, W, H);
      ctx.restore();

      domainRaf = requestAnimationFrame(animate);
    };
    animate();

    // cleanup resize listener when domain closes
    const origClose = $('#doClose').onclick;
    if (origClose) {
      $('#doClose').onclick = () => {
        window.removeEventListener('resize', onResize);
        origClose();
      };
    }
  };

  /* ═══════════════════════════════════════════════════════════
     DRAWER MENU  +  TOP BUTTON
     ═══════════════════════════════════════════════════════════ */
  const initDrawer = () => {
    burger.addEventListener('click', () => {
      burger.classList.toggle('on');
      drawer.classList.toggle('open');
      document.body.classList.toggle('locked');
    });
    // close drawer on nav link click
    $$('#drawer a').forEach(a => {
      a.addEventListener('click', () => {
        burger.classList.remove('on');
        drawer.classList.remove('open');
        document.body.classList.remove('locked');
      });
    });
  };

  const initToTop = () => {
    toTop.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  };

  /* ═══════════════════════════════════════════════════════════
     PARALLAX (subtle, lerp-based)
     ═══════════════════════════════════════════════════════════ */
  const initParallax = () => {
    if (state.reduced) return;
    const items = $$('[data-par]');
    let latest = 0;
    const update = () => {
      const scrollY = window.scrollY;
      items.forEach(el => {
        const speed = parseFloat(el.dataset.par);
        const y = scrollY * speed;
        el.style.transform = `translate3d(0,${y}px,0)`;
      });
      latest = 0;
    };
    let ticking = false;
    const onScroll = () => {
      if (!ticking) {
        ticking = true;
        requestAnimationFrame(() => {
          update();
          ticking = false;
        });
      }
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    update();
  };

  /* ═══════════════════════════════════════════════════════════
     RANDOM DOMAIN BUTTON
     ═══════════════════════════════════════════════════════════ */
  const initRandomDomain = () => {
    const btn = $('#randomDomain');
    if (!btn) return;
    btn.addEventListener('click', () => {
      const s = SORCERERS[Math.floor(Math.random() * SORCERERS.length)];
      openDomain(s);
    });
  };

  /* ═══════════════════════════════════════════════════════════
     INIT
     ═══════════════════════════════════════════════════════════ */
  const init = () => {
    document.body.classList.add('loading');
    initPreloader();
    initCursor();
    initCanvas();
    initScroll();
    initCounters();
    initScramble();
    initMagnetic();
    initTilt();
    renderRoster();
    initDrawer();
    initToTop();
    initParallax();
    initRandomDomain();

    // hero domain button
    const heroDomain = $('#heroDomain');
    if (heroDomain) {
      heroDomain.addEventListener('click', () => {
        const s = SORCERERS[0]; // Gojo
        openDomain(s);
      });
    }

    // domain visual click
    if (domainVisual) {
      domainVisual.addEventListener('click', () => {
        const s = SORCERERS[Math.floor(Math.random() * SORCERERS.length)];
        openDomain(s);
      });
    }
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
