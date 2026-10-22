// Resolve the device theme, with an explicit choice remembered across visits.
(function () {
  var root = document.documentElement;
  var toggle = document.querySelector('.theme-toggle');
  var system = matchMedia('(prefers-color-scheme: dark)');
  var preference;
  try { preference = localStorage.getItem('bladeTheme'); } catch (e) {}
  if (preference !== 'light' && preference !== 'dark') preference = null;
  function apply(theme) {
    root.dataset.theme = theme;
    if (toggle) toggle.setAttribute('aria-pressed', String(theme === 'dark'));
    var meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.content = theme === 'dark' ? '#10141c' : '#f8f7f3';
  }
  apply(preference || (system.matches ? 'dark' : 'light'));
  if (toggle) {
    toggle.hidden = false;
    toggle.addEventListener('click', function () {
      preference = root.dataset.theme === 'dark' ? 'light' : 'dark';
      try { localStorage.setItem('bladeTheme', preference); } catch (e) {}
      // Crossfade the page, hero landscape included, where the browser can.
      var next = preference;
      if (document.startViewTransition && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
        document.startViewTransition(function () { apply(next); });
      } else {
        apply(next);
      }
    });
  }
  system.addEventListener('change', function (event) {
    if (!preference) apply(event.matches ? 'dark' : 'light');
  });
})();
