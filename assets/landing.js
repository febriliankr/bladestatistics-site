(function () {
  var steps = [].slice.call(document.querySelectorAll(".feature-step"));
  var previews = [].slice.call(document.querySelectorAll(".app-preview"));
  steps.forEach(function (step) {
    step.addEventListener("toggle", function () {
      if (!step.open) return;
      steps.forEach(function (other) {
        if (other !== step) other.open = false;
      });
      previews.forEach(function (preview) {
        preview.hidden = preview.id !== step.dataset.preview;
      });
    });
  });
})();
