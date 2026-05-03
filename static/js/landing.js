/* ─────────────────────────────────────────────
   HEALTHAPP — landing page interactions
   Used by: templates/landing.html
   Depends on: AOS (loaded from CDN before this script)
   ───────────────────────────────────────────── */

(function () {
  'use strict';

  // 1. Animate-on-scroll
  if (window.AOS) {
    AOS.init({ duration: 700, easing: 'ease-out-cubic', once: true, offset: 80 });
  }

  // 2. Animated counters (triggered when in viewport)
  const counters = document.querySelectorAll('.counter');
  const animateCounter = (el) => {
    const target = +el.dataset.target;
    const suffix = el.dataset.suffix || '';
    const duration = 1800;
    const start = performance.now();
    const tick = (now) => {
      const p = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - p, 3);
      const value = Math.floor(target * eased);
      el.textContent = value.toLocaleString() + suffix;
      if (p < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  };
  if (counters.length && 'IntersectionObserver' in window) {
    const counterObs = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting && !entry.target.dataset.animated) {
          entry.target.dataset.animated = '1';
          animateCounter(entry.target);
        }
      });
    }, { threshold: 0.4 });
    counters.forEach((c) => counterObs.observe(c));
  }

  // 3. Smooth scroll for in-page anchors
  document.querySelectorAll('a[href^="#"]').forEach((a) => {
    a.addEventListener('click', (e) => {
      const id = a.getAttribute('href');
      if (id.length > 1) {
        const el = document.querySelector(id);
        if (el) {
          e.preventDefault();
          window.scrollTo({ top: el.offsetTop - 80, behavior: 'smooth' });
        }
      }
    });
  });

  // 4. Sticky navbar shadow on scroll
  const nav = document.getElementById('navbar');
  if (nav) {
    const onScroll = () => {
      if (window.scrollY > 8) {
        nav.classList.add('shadow-soft');
        nav.classList.remove('border-slate-100');
      } else {
        nav.classList.remove('shadow-soft');
        nav.classList.add('border-slate-100');
      }
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  // 5. Subtle parallax on hero blobs (mouse tracking)
  const blobs = document.querySelectorAll('.blob');
  if (blobs.length) {
    window.addEventListener('mousemove', (e) => {
      const x = (e.clientX / window.innerWidth - 0.5) * 12;
      const y = (e.clientY / window.innerHeight - 0.5) * 12;
      blobs.forEach((b, i) => {
        const factor = i % 2 === 0 ? 1 : -1;
        b.style.transform = `translate(${x * factor}px, ${y * factor}px)`;
      });
    });
  }

  // 6. Mobile hamburger menu toggle
  const mobileToggle = document.getElementById('mobileToggle');
  const mobilePanel  = document.getElementById('mobilePanel');
  const iconBurger   = document.getElementById('iconBurger');
  const iconClose    = document.getElementById('iconClose');
  if (mobileToggle && mobilePanel) {
    const setMenu = (open) => {
      mobilePanel.classList.toggle('hidden', !open);
      iconBurger.classList.toggle('hidden', open);
      iconClose.classList.toggle('hidden', !open);
      mobileToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      mobileToggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    };
    mobileToggle.addEventListener('click', () => {
      setMenu(mobilePanel.classList.contains('hidden'));
    });
    document.querySelectorAll('.mobile-link').forEach((a) =>
      a.addEventListener('click', () => setMenu(false))
    );
  }
})();
