// Animationen im Konfigurator: Nach jeder HTMX-Vorschau gleiten Dose und Zahlen
// vom alten zum neuen Zustand, statt hart umzuspringen.
(() => {
  const DURATION = 500;
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const number = (decimals) =>
    new Intl.NumberFormat("de-DE", {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
      useGrouping: false,
    });
  let before = null;

  function snapshot() {
    const state = { layers: {}, counts: {}, fills: [] };
    document.querySelectorAll("#summary [data-layer]").forEach((el) => {
      state.layers[el.dataset.layer] = { y: el.getAttribute("y"), height: el.getAttribute("height") };
    });
    document.querySelectorAll("[data-count-key]").forEach((el) => {
      state.counts[el.dataset.countKey] = parseFloat(el.dataset.count);
    });
    document.querySelectorAll("#summary [data-fill]").forEach((el) => {
      state.fills.push(el.getAttribute(el.dataset.fill));
    });
    return state;
  }

  // Startwert setzen, Layout erzwingen, dann Zielwert: so greift die CSS-Transition
  function transition(el, className, from, to) {
    Object.assign(el.style, from);
    el.getBoundingClientRect();
    el.classList.add(className);
    Object.assign(el.style, to);
  }

  function animateCan(prev) {
    let changed = false;
    document.querySelectorAll("#summary [data-layer]").forEach((el) => {
      const old = prev.layers[el.dataset.layer];
      const y = el.getAttribute("y");
      const height = el.getAttribute("height");
      if (!old) {
        el.classList.add("layer-in");
        changed = true;
      } else if (old.y !== y || old.height !== height) {
        transition(el, "layer-move", { y: `${old.y}px`, height: `${old.height}px` }, { y: `${y}px`, height: `${height}px` });
        changed = true;
      }
    });
    if (Object.keys(prev.layers).some((key) => !document.querySelector(`#summary [data-layer="${key}"]`))) {
      changed = true;
    }
    document.querySelectorAll("#summary [data-fill]").forEach((el, i) => {
      const prop = el.dataset.fill;
      const color = el.getAttribute(prop);
      if (prev.fills[i] && prev.fills[i] !== color) {
        transition(el, "fill-move", { [prop]: prev.fills[i] }, { [prop]: color });
        changed = true;
      }
    });
    const can = document.querySelector("#summary svg");
    if (changed && can) can.classList.add("can-bump");
  }

  function animateCounts(prev) {
    document.querySelectorAll("[data-count-key]").forEach((el) => {
      const from = prev.counts[el.dataset.countKey];
      const to = parseFloat(el.dataset.count);
      if (from === undefined || from === to) return;
      const format = number(Number(el.dataset.decimals || 0));
      const start = performance.now();
      const step = (now) => {
        const t = Math.min((now - start) / DURATION, 1);
        const eased = 1 - Math.pow(1 - t, 3);
        el.textContent = format.format(from + (to - from) * eased);
        if (t < 1) requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
    });
  }

  document.addEventListener("htmx:beforeSwap", (event) => {
    if (event.detail.target.id === "summary") before = snapshot();
  });

  document.addEventListener("htmx:afterSettle", (event) => {
    if (event.detail.target.id !== "summary" || !before || reduceMotion) return;
    animateCan(before);
    animateCounts(before);
    before = null;
  });
})();
