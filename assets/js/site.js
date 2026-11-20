/* ExTrEMe Collaboration — small progressive enhancements (no dependencies). */
(function () {
  "use strict";

  /* ---------- Mobile navigation ---------- */
  var toggle = document.querySelector("[data-nav-toggle]");
  var nav = document.getElementById("site-nav");
  if (toggle && nav) {
    var setOpen = function (open) {
      toggle.setAttribute("aria-expanded", String(open));
      nav.classList.toggle("is-open", open);
    };
    toggle.addEventListener("click", function () {
      setOpen(toggle.getAttribute("aria-expanded") !== "true");
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && nav.classList.contains("is-open")) {
        setOpen(false);
        toggle.focus();
      }
    });
    document.addEventListener("click", function (e) {
      if (nav.classList.contains("is-open") && !nav.contains(e.target) && !toggle.contains(e.target)) {
        setOpen(false);
      }
    });
  }

  /* ---------- Filterable lists (talks, publications) ---------- */
  function normalize(s) {
    return (s || "").toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "");
  }

  function setupFilter(root) {
    var kind = root.getAttribute("data-filter");
    var list = document.querySelector("[data-filter-list]");
    if (!list) return;

    var itemSelector = kind === "talks" ? ".talk" : ".pub";
    var chipAttr = kind === "talks" ? "data-type" : "data-category";
    var chipParam = kind === "talks" ? "type" : "category";
    var noun = kind === "talks" ? "talks" : "publications";

    var items = Array.prototype.slice.call(list.querySelectorAll(itemSelector));
    var groups = Array.prototype.slice.call(list.querySelectorAll("[data-filter-group]"));
    var search = root.querySelector("[data-filter-search]");
    var select = root.querySelector("[data-filter-select]");
    var selectParam = select ? select.getAttribute("data-filter-select") : null;
    var chips = Array.prototype.slice.call(root.querySelectorAll("[data-filter-chip]"));
    var status = root.querySelector("[data-filter-status]");
    var empty = document.querySelector("[data-filter-empty]");

    var texts = items.map(function (el) { return normalize(el.textContent); });
    var state = { q: "", chip: "", select: "" };

    // Restore state from the URL (?q=…&type=…&speaker=…)
    var params = new URLSearchParams(window.location.search);
    state.q = params.get("q") || "";
    state.chip = params.get(chipParam) || "";
    if (select && params.get(selectParam)) {
      var wanted = params.get(selectParam);
      for (var i = 0; i < select.options.length; i++) {
        if (select.options[i].value === wanted) { state.select = wanted; break; }
      }
    }
    if (search) search.value = state.q;
    if (select) select.value = state.select;

    function syncUrl() {
      var p = new URLSearchParams(window.location.search);
      [["q", state.q], [chipParam, state.chip], [selectParam, state.select]].forEach(function (kv) {
        if (!kv[0]) return;
        if (kv[1]) p.set(kv[0], kv[1]); else p.delete(kv[0]);
      });
      var qs = p.toString();
      history.replaceState(null, "", window.location.pathname + (qs ? "?" + qs : "") + window.location.hash);
    }

    function apply() {
      var terms = normalize(state.q).split(/\s+/).filter(Boolean);
      var shown = 0;
      items.forEach(function (el, idx) {
        var ok = (!state.chip || el.getAttribute(chipAttr) === state.chip) &&
          (!state.select || el.getAttribute("data-speaker") === state.select) &&
          terms.every(function (t) { return texts[idx].indexOf(t) !== -1; });
        el.hidden = !ok;
        if (ok) shown++;
      });
      groups.forEach(function (g) {
        g.hidden = !g.querySelector(itemSelector + ":not([hidden])");
      });
      chips.forEach(function (c) {
        c.setAttribute("aria-pressed", String(c.getAttribute("data-filter-chip") === state.chip));
      });
      var filtered = state.q || state.chip || state.select;
      if (status) status.textContent = filtered ? "Showing " + shown + " of " + items.length + " " + noun + "." : "";
      if (empty) empty.hidden = shown !== 0;
      syncUrl();
    }

    if (search) {
      search.addEventListener("input", function () { state.q = search.value.trim(); apply(); });
    }
    if (select) {
      select.addEventListener("change", function () { state.select = select.value; apply(); });
    }
    chips.forEach(function (c) {
      c.addEventListener("click", function () {
        var value = c.getAttribute("data-filter-chip");
        state.chip = state.chip === value ? "" : value;
        apply();
      });
    });

    apply();
  }

  Array.prototype.forEach.call(document.querySelectorAll("[data-filter]"), setupFilter);
})();
