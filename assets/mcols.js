/* Phones: rows of cards scroll sideways (like the desktop columns) with dots showing where you are. */
(function () {
  function init() {
    if (!window.matchMedia || !matchMedia('(max-width:760px)').matches) return;
    document.querySelectorAll('.mcols').forEach(function (row) {
      if (row.nextElementSibling && row.nextElementSibling.classList.contains('mdots')) return;
      var items = [].filter.call(row.children, function (c) { return c.offsetWidth > 0; });
      if (items.length < 2) return;
      var dots = document.createElement('div');
      dots.className = 'mdots'; dots.setAttribute('aria-hidden', 'true');
      items.forEach(function (_, i) { var d = document.createElement('i'); if (!i) d.className = 'on'; dots.appendChild(d); });
      row.parentNode.insertBefore(dots, row.nextSibling);
      var t;
      row.addEventListener('scroll', function () {
        clearTimeout(t);
        t = setTimeout(function () {
          var step = items.length > 1 ? items[1].offsetLeft - items[0].offsetLeft : 1;
          var i = Math.max(0, Math.min(items.length - 1, Math.round(row.scrollLeft / step)));
          [].forEach.call(dots.children, function (d, k) { d.className = k === i ? 'on' : ''; });
        }, 60);
      }, { passive: true });
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
