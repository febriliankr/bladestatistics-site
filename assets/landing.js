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

  function show(step) {
    previews.forEach(function (preview) {
      preview.hidden = preview.id !== step.dataset.preview;
    });
    clearInterval(galleryTimer);
    if (inView && step.dataset.preview === "preview-ask") playDemo();
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
        demoTimers.forEach(clearTimeout);
      }
    }, { threshold: 0.35 }).observe(stage);
  }
})();
