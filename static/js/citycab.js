/* ============================================================
   CityCab — shared UI runtime
   Toasts, navbar, form validation helpers, flash bridge.
   Kept dependency-free so every page can reuse it.
   ============================================================ */
(function () {
  "use strict";

  /* ---------- Inline SVG icons (Lucide-style strokes) ---------- */
  var ICONS = {
    check: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>',
    alert: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 8v4M12 16h.01"/></svg>',
    info: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/></svg>',
    warning: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><path d="M12 9v4M12 17h.01"/></svg>'
  };

  /* ---------- Toast system ---------- */
  function ensureStack() {
    var s = document.querySelector(".toast-stack");
    if (!s) {
      s = document.createElement("div");
      s.className = "toast-stack";
      document.body.appendChild(s);
    }
    return s;
  }

  function toast(message, type, timeout) {
    type = type || "info";
    // map Flask categories -> toast types
    if (type === "error") type = "danger";
    var icon = ICONS[type === "danger" ? "alert" : type === "success" ? "check" : type === "warning" ? "warning" : "info"];
    var el = document.createElement("div");
    el.className = "toast " + type;
    el.innerHTML =
      '<span class="t-ico">' + icon + "</span>" +
      '<div class="t-body"></div>' +
      '<button class="t-close" aria-label="Dismiss">&times;</button>';
    el.querySelector(".t-body").textContent = message;
    var stack = ensureStack();
    stack.appendChild(el);

    var life = timeout == null ? 4200 : timeout;
    var timer = life ? setTimeout(dismiss, life) : null;
    el.querySelector(".t-close").addEventListener("click", dismiss);
    function dismiss() {
      if (timer) clearTimeout(timer);
      el.classList.add("hide");
      el.addEventListener("animationend", function () { el.remove(); });
    }
    return el;
  }

  /* ---------- Navbar mobile toggle ---------- */
  function initNav() {
    var toggle = document.querySelector(".nav-toggle");
    var mobile = document.querySelector(".nav-mobile");
    if (toggle && mobile) {
      toggle.addEventListener("click", function () {
        mobile.classList.toggle("open");
      });
      mobile.querySelectorAll("a").forEach(function (a) {
        a.addEventListener("click", function () { mobile.classList.remove("open"); });
      });
    }
    // highlight active link by pathname
    var path = window.location.pathname;
    document.querySelectorAll(".nav-link[data-path]").forEach(function (l) {
      if (l.getAttribute("data-path") === path) l.classList.add("active");
    });
  }

  /* ---------- Flash bridge: turn server flashes into toasts ---------- */
  function initFlashes() {
    var node = document.getElementById("flash-data");
    if (!node) return;
    try {
      var items = JSON.parse(node.textContent || "[]");
      items.forEach(function (f, i) {
        setTimeout(function () { toast(f.message, f.category, 5000); }, i * 180);
      });
    } catch (e) { /* ignore */ }
  }

  /* ---------- Small form-validation helper ---------- */
  function markInvalid(input, message) {
    var field = input.closest(".field") || input.parentElement;
    input.classList.add("invalid");
    if (field) {
      field.classList.add("has-error");
      var err = field.querySelector(".field-error");
      if (err && message) err.textContent = message;
    }
  }
  function clearInvalid(input) {
    var field = input.closest(".field") || input.parentElement;
    input.classList.remove("invalid");
    if (field) field.classList.remove("has-error");
  }
  function autoClearOnInput(scope) {
    (scope || document).querySelectorAll(".input").forEach(function (i) {
      i.addEventListener("input", function () { clearInvalid(i); });
    });
  }

  /* ---------- Expose API ---------- */
  window.CityCab = {
    toast: toast,
    icons: ICONS,
    markInvalid: markInvalid,
    clearInvalid: clearInvalid
  };

  document.addEventListener("DOMContentLoaded", function () {
    initNav();
    initFlashes();
    autoClearOnInput(document);
  });
})();
