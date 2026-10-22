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
      apply(preference);
    });
  }
  system.addEventListener('change', function (event) {
    if (!preference) apply(event.matches ? 'dark' : 'light');
  });
})();

(function () {
  var steps = [].slice.call(document.querySelectorAll(".feature-step"));
  var previews = [].slice.call(document.querySelectorAll(".app-preview"));
  var stage = document.querySelector(".product-layout");
  var demo = document.getElementById("preview-ask");
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var ADVANCE = { "preview-ask": 13000, "preview-results": 10000, "preview-script": 10000 };
  var auto = !reduce;
  var inView = false;
  var advanceTimer = null;
  var remaining = 0;
  var startedAt = 0;
  var held = false;
  var demoTimers = [];

  function openStep() {
    return steps.filter(function (step) { return step.open; })[0] || steps[0];
  }

  function advance() {
    var next = steps[(steps.indexOf(openStep()) + 1) % steps.length];
    next.open = true;
  }

  function stopTimer() {
    clearTimeout(advanceTimer);
    steps.forEach(function (step) { step.classList.remove("timing", "held"); });
  }

  function runTimer() {
    startedAt = Date.now();
    advanceTimer = setTimeout(advance, remaining);
  }

  // The open step carries a bar that fills until the next slide; it pauses
  // with the slideshow and resumes from where it stopped.
  function schedule() {
    stopTimer();
    if (!auto || !inView) return;
    var step = openStep();
    remaining = ADVANCE[step.dataset.preview] || 10000;
    step.style.setProperty("--step-duration", remaining + "ms");
    void step.offsetWidth;
    step.classList.add("timing");
    if (held) step.classList.add("held");
    else runTimer();
  }

  function hold(on) {
    if (on === held) return;
    held = on;
    var step = openStep();
    if (!step.classList.contains("timing")) return;
    step.classList.toggle("held", on);
    if (on) {
      clearTimeout(advanceTimer);
      remaining = Math.max(0, remaining - (Date.now() - startedAt));
    } else {
      runTimer();
    }
  }

  // The Ask preview plays a short session: the question types out, the
  // pointer clicks send, Blade thinks, then the R result arrives.
  function playDemo() {
    if (!demo || reduce) return;
    demoTimers.forEach(clearTimeout);
    demoTimers = [];
    var input = demo.querySelector(".ask-input");
    var send = demo.querySelector(".send");
    var pointer = demo.querySelector(".m-pointer");
    var win = demo.querySelector(".mw");
    var prompt = input.getAttribute("data-prompt");
    var at = function (ms, fn) { demoTimers.push(setTimeout(fn, ms)); };

    demo.setAttribute("data-stage", "type");
    input.textContent = "";
    pointer.className.baseVal = "m-pointer";
    send.classList.remove("press");

    for (var i = 1; i <= prompt.length; i++) {
      (function (n) {
        at(700 + n * 34, function () { input.textContent = prompt.slice(0, n); });
      })(i);
    }
    var typed = 700 + prompt.length * 34;

    at(typed + 200, function () {
      var w = win.getBoundingClientRect();
      var b = send.getBoundingClientRect();
      pointer.style.transition = "none";
      pointer.style.setProperty("--px", w.width * 0.78 + "px");
      pointer.style.setProperty("--py", w.height * 1.05 + "px");
      void pointer.getBoundingClientRect();
      pointer.style.transition = "";
      pointer.classList.add("show");
      pointer.style.setProperty("--px", b.left - w.left + b.width * 0.45 + "px");
      pointer.style.setProperty("--py", b.top - w.top + b.height * 0.4 + "px");
    });
    at(typed + 1100, function () {
      pointer.classList.add("press");
      send.classList.add("press");
    });
    at(typed + 1250, function () {
      pointer.classList.remove("press");
      send.classList.remove("press");
      input.textContent = "";
      demo.setAttribute("data-stage", "sent");
    });
    at(typed + 1600, function () {
      pointer.classList.remove("show");
      demo.setAttribute("data-stage", "think");
    });
    at(typed + 4200, function () { demo.setAttribute("data-stage", "done"); });
  }

  // The results preview steps through the figures R saved, about every two
  // seconds, so all five pass within one slide.
  var gallery = document.getElementById("preview-results");
  var galleryTimer = null;
  function playGallery() {
    clearInterval(galleryTimer);
    if (!gallery) return;
    var shots = [].slice.call(gallery.querySelectorAll(".shot-stack img"));
    var thumbs = [].slice.call(gallery.querySelectorAll(".m-strip span"));
    var name = gallery.querySelector(".shot-name");
    var size = gallery.querySelector(".shot-size");
    var index = 0;
    function select(n) {
      index = n;
      shots.forEach(function (img, k) { img.classList.toggle("on", k === n); });
      thumbs.forEach(function (thumb, k) { thumb.classList.toggle("on", k === n); });
      name.textContent = thumbs[n].getAttribute("data-name");
      size.textContent = thumbs[n].getAttribute("data-size");
    }
    select(0);
    if (reduce) return;
    galleryTimer = setInterval(function () {
      if (!held) select((index + 1) % shots.length);
    }, 1900);
  }

  // The script preview writes framingham_linear.R line by line, presses Run,
  // and streams the real console output. Its tabs work like an editor's.
  var script = document.getElementById("preview-script");
  var scriptTimers = [];
  function clearScript() {
    scriptTimers.forEach(clearTimeout);
    scriptTimers = [];
  }
  function takeOver() {
    auto = false;
    stopTimer();
  }
  if (script) {
    var tabs = [].slice.call(script.querySelectorAll('[role="tab"]'));
    var codeLines = [].slice.call(script.querySelectorAll(".m-code .cl"));
    var outLines = [].slice.call(script.querySelectorAll(".m-console .ol"));
    var runBtn = script.querySelector(".run-btn");
    var consoleBox = script.querySelector(".m-console pre");
    var later = function (ms, fn) { scriptTimers.push(setTimeout(fn, ms)); };

    var selectTab = function (tab, focus) {
      tabs.forEach(function (other) {
        var on = other === tab;
        other.setAttribute("aria-selected", on ? "true" : "false");
        other.tabIndex = on ? 0 : -1;
        document.getElementById(other.getAttribute("aria-controls")).hidden = !on;
      });
      if (focus) tab.focus();
    };

    var run = function () {
      runBtn.classList.add("press");
      later(130, function () { runBtn.classList.remove("press"); });
      if (reduce) {
        script.setAttribute("data-run", "done");
        return;
      }
      script.setAttribute("data-run", "busy");
      consoleBox.scrollTop = 0;
      outLines.forEach(function (line) { line.classList.remove("on"); });
      outLines.forEach(function (line, n) {
        later(700 + n * 55, function () {
          line.classList.add("on");
          var below = line.offsetTop + line.offsetHeight - consoleBox.clientHeight;
          if (below > consoleBox.scrollTop) consoleBox.scrollTop = below + 6;
        });
      });
      later(700 + outLines.length * 55 + 150, function () {
        script.setAttribute("data-run", "done");
      });
    };

    script.playScript = function () {
      clearScript();
      selectTab(tabs[0]);
      if (reduce) return;
      script.setAttribute("data-run", "idle");
      script.setAttribute("data-type", "");
      codeLines.forEach(function (line) { line.classList.remove("on", "cur"); });
      codeLines.forEach(function (line, n) {
        later(500 + n * 260, function () {
          if (n) codeLines[n - 1].classList.remove("cur");
          line.classList.add("on", "cur");
        });
      });
      var typed = 500 + codeLines.length * 260;
      later(typed + 350, function () {
        codeLines[codeLines.length - 1].classList.remove("cur");
        run();
      });
    };

    tabs.forEach(function (tab, n) {
      tab.addEventListener("click", function () {
        takeOver();
        selectTab(tab);
      });
      tab.addEventListener("keydown", function (event) {
        var step = event.key === "ArrowRight" ? 1 : event.key === "ArrowLeft" ? -1 : 0;
        if (!step) return;
        event.preventDefault();
        takeOver();
        selectTab(tabs[(n + step + tabs.length) % tabs.length], true);
      });
    });

    runBtn.addEventListener("click", function () {
      takeOver();
      clearScript();
      codeLines.forEach(function (line) { line.classList.add("on"); line.classList.remove("cur"); });
      run();
    });
  }

  function show(step) {
    previews.forEach(function (preview) {
      preview.hidden = preview.id !== step.dataset.preview;
    });
    clearInterval(galleryTimer);
    clearScript();
    if (inView && step.dataset.preview === "preview-ask") playDemo();
    if (inView && step.dataset.preview === "preview-script" && script) script.playScript();
    if (inView && step.dataset.preview === "preview-results") playGallery();
    schedule();
  }

  steps.forEach(function (step) {
    var bar = document.createElement("span");
    bar.className = "step-timer";
    bar.setAttribute("aria-hidden", "true");
    step.appendChild(bar);
    step.addEventListener("toggle", function () {
      if (!step.open) return;
      steps.forEach(function (other) {
        if (other !== step) other.open = false;
      });
      show(step);
    });
    // A visitor choosing a step takes over from the slideshow.
    step.querySelector("summary").addEventListener("click", function () {
      auto = false;
      stopTimer();
    });
  });

  // Replay restarts whichever preview is showing, entrance and all.
  var replay = document.querySelector(".replay");
  if (replay) {
    replay.addEventListener("click", function () {
      takeOver();
      var step = openStep();
      var panel = document.getElementById(step.dataset.preview);
      panel.hidden = true;
      void panel.offsetWidth;
      inView = true;
      show(step);
    });
  }

  // Hold the slideshow while someone is pointing at or tabbing through it.
  if (stage) {
    stage.addEventListener("mouseenter", function () { hold(true); });
    stage.addEventListener("mouseleave", function () { hold(false); });
    stage.addEventListener("focusin", function () { hold(true); });
    stage.addEventListener("focusout", function () { hold(false); });
  }

  if (demo && !reduce) {
    demo.setAttribute("data-stage", "type");
  }

  // The /demo deck plays the same previews, one per slide.
  window.BladePreview = {
    ask: playDemo,
    gallery: playGallery,
    script: function () { if (script) script.playScript(); },
    stop: function () {
      demoTimers.forEach(clearTimeout);
      clearInterval(galleryTimer);
      clearScript();
    },
  };

  if (stage && "IntersectionObserver" in window) {
    new IntersectionObserver(function (entries) {
      var visible = entries[0].isIntersecting;
      if (visible === inView) return;
      inView = visible;
      if (inView) {
        show(openStep());
      } else {
        stopTimer();
        clearInterval(galleryTimer);
        clearScript();
        demoTimers.forEach(clearTimeout);
      }
    }, { threshold: 0.35 }).observe(stage);
  }
})();

// Intro video: a poster that links to YouTube, swapped for the privacy-mode
// player on click, so the page loads no YouTube code until someone asks.
(function () {
  var link = document.querySelector(".video-play");
  if (!link) return;
  link.addEventListener("click", function (e) {
    if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || e.button !== 0) return;
    e.preventDefault();
    var frame = document.createElement("iframe");
    frame.src = "https://www.youtube-nocookie.com/embed/" + link.dataset.video + "?autoplay=1&rel=0&playsinline=1";
    frame.title = link.getAttribute("aria-label");
    frame.allow = "autoplay; encrypted-media; picture-in-picture; fullscreen";
    frame.allowFullscreen = true;
    link.replaceWith(frame);
    frame.focus();
  });
})();
