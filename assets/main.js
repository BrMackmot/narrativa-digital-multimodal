/* Mejora progresiva: sin JavaScript el sitio sigue siendo legible. */
(() => {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Aparición al hacer scroll
  const els = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window && !reduce) {
    const io = new IntersectionObserver((es) => es.forEach(e => {
      if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
    }), { threshold: 0.15, rootMargin: '0px 0px -6% 0px' });
    els.forEach(el => io.observe(el));
  } else { els.forEach(el => el.classList.add('in')); }

  // Barra de progreso y barra superior
  const bar = document.querySelector('.progress'), top = document.querySelector('.topbar');
  const onScroll = () => {
    const h = document.documentElement, max = h.scrollHeight - innerHeight;
    if (bar) bar.style.transform = `scaleX(${max > 0 ? scrollY / max : 0})`;
    if (top) top.classList.toggle('solid', scrollY > innerHeight * 0.6);
  };
  addEventListener('scroll', onScroll, { passive: true }); onScroll();

  // Enlace activo en la navegación
  const links = [...document.querySelectorAll('.topbar nav a')];
  const secs = links.map(a => document.querySelector(a.getAttribute('href'))).filter(Boolean);
  if ('IntersectionObserver' in window) {
    const so = new IntersectionObserver((es) => es.forEach(e => {
      if (e.isIntersecting) links.forEach(a => a.classList.toggle('on', a.getAttribute('href') === '#' + e.target.id));
    }), { threshold: 0.5 });
    secs.forEach(s => so.observe(s));
  }

  // Contador de cifras (24 %, 79 %)
  if (!reduce && 'IntersectionObserver' in window) {
    document.querySelectorAll('[data-count]').forEach(el => {
      const m = el.dataset.count.match(/^(\d+)(.*)$/); if (!m) return;
      const end = +m[1], suf = m[2];
      new IntersectionObserver(([x], o) => {
        if (!x.isIntersecting) return; o.disconnect();
        const t0 = performance.now();
        const tick = t => { const p = Math.min(1, (t - t0) / 1200);
          el.textContent = Math.round(end * (1 - Math.pow(1 - p, 3))) + suf;
          if (p < 1) requestAnimationFrame(tick); };
        requestAnimationFrame(tick);
      }, { threshold: 0.6 }).observe(el);
    });
  }

  // Ampliar foto
  const dlg = document.getElementById('lightbox');
  if (dlg && dlg.showModal) {
    document.addEventListener('click', e => {
      const b = e.target.closest('.open'); if (!b) return;
      dlg.querySelector('img').src = b.dataset.src;
      dlg.querySelector('img').alt = b.getAttribute('aria-label') || '';
      dlg.querySelector('p').textContent = [b.dataset.cap, b.dataset.credit].filter(Boolean).join(' — ');
      dlg.showModal();
    });
    dlg.addEventListener('click', e => { if (e.target === dlg) dlg.close(); });
  }
})();
