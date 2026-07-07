// SmartHire AI - small UI enhancements

document.addEventListener("DOMContentLoaded", function () {
  // Auto-dismiss alerts after 4 seconds
  document.querySelectorAll(".alert").forEach(function (alertEl) {
    setTimeout(function () {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alertEl);
      bsAlert.close();
    }, 4000);
  });

  // Animate progress bars on load
  document.querySelectorAll(".progress-bar[data-value]").forEach(function (bar) {
    const value = bar.getAttribute("data-value");
    setTimeout(function () {
      bar.style.width = value + "%";
    }, 150);
  });

  // Resume file input preview
  const resumeInput = document.getElementById("resumeInput");
  if (resumeInput) {
    resumeInput.addEventListener("change", function () {
      const label = document.getElementById("resumeFileName");
      if (label && resumeInput.files.length > 0) {
        label.textContent = resumeInput.files[0].name;
      }
    });
  }
});
