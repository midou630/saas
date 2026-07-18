/* ==========================================================
   Système de Gestion de Cabinet Médical — Script principal
   ========================================================== */

document.addEventListener("DOMContentLoaded", function () {
  // ---- Fermeture automatique des messages flash ----
  document.querySelectorAll(".alert[data-auto-dismiss]").forEach(function (alertEl) {
    setTimeout(function () {
      alertEl.style.opacity = "0";
      setTimeout(function () { alertEl.remove(); }, 300);
    }, 4500);
  });

  document.querySelectorAll(".alert-close").forEach(function (btn) {
    btn.addEventListener("click", function () {
      btn.closest(".alert").remove();
    });
  });

  // ---- Menu mobile ----
  var menuToggle = document.querySelector(".mobile-menu-toggle");
  var sidebar = document.querySelector(".sidebar");
  if (menuToggle && sidebar) {
    menuToggle.addEventListener("click", function () {
      sidebar.classList.toggle("open");
    });
  }

  // ---- Confirmation avant suppression ----
  document.querySelectorAll("form[data-confirm]").forEach(function (form) {
    form.addEventListener("submit", function (event) {
      var message = form.getAttribute("data-confirm") || "Êtes-vous sûr de vouloir continuer ?";
      if (!window.confirm(message)) {
        event.preventDefault();
      }
    });
  });

  // ---- Recherche instantanée avec délai (debounce) ----
  var searchInput = document.querySelector("[data-live-search]");
  if (searchInput) {
    var timeoutId;
    searchInput.addEventListener("input", function () {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(function () {
        searchInput.closest("form").submit();
      }, 500);
    });
  }
});

/* ---- Ajout dynamique de lignes de médicaments dans une ordonnance ---- */
function addPrescriptionItemRow() {
  var container = document.getElementById("prescription-items-container");
  if (!container) return;

  var template = document.getElementById("prescription-item-template");
  var index = container.querySelectorAll(".prescription-item-row").length;
  var newRow = template.content.cloneNode(true);

  newRow.querySelectorAll("[name]").forEach(function (field) {
    field.name = field.name.replace("__INDEX__", index);
    field.id = field.id.replace("__INDEX__", index);
  });

  container.appendChild(newRow);
}

function removePrescriptionItemRow(button) {
  var row = button.closest(".prescription-item-row");
  if (row) row.remove();
}
