(function () {
  const root = document.documentElement;
  const foldRootSelector = "[data-app-detail-fold]";
  let foldIndex = 0;

  const rules = [
    { selector: ".section-head > div", foldSelector: ":scope > p", minText: 80 },
    { selector: ".day-intro", foldSelector: ":scope > p", minText: 80 },
    { selector: ".birthday-banner", foldSelector: ":scope > p", minText: 80 },
    { selector: ".editorial-card", foldSelector: ":scope > p, :scope > ul, :scope > ol", minText: 80 },
    { selector: ".route-map-copy", foldSelector: ":scope > span", minText: 60 },
    { selector: ".food-pick", foldSelector: ":scope > p", minText: 70 },
    { selector: ".aside-card", foldSelector: ":scope > p, :scope > ul, :scope > ol, :scope > .table-wrap", minText: 70 }
  ];

  function directMatches(container, selector) {
    return Array.from(container.querySelectorAll(selector))
      .filter((node) => node.parentElement === container && !node.closest(foldRootSelector));
  }

  function textLength(nodes) {
    return nodes
      .map((node) => node.textContent || "")
      .join(" ")
      .replace(/\s+/g, " ")
      .trim()
      .length;
  }

  function setExpanded(fold, expanded) {
    const button = fold.querySelector(":scope > .app-detail-fold-toggle");
    fold.classList.toggle("is-expanded", expanded);
    if (!button) return;
    button.setAttribute("aria-expanded", String(expanded));
    button.setAttribute("aria-label", expanded ? "세부정보 접기" : "세부정보 펼치기");
    button.textContent = expanded ? "접기" : "펼치기";
  }

  function createFold(container, nodes) {
    if (!nodes.length || container.dataset.appDetailFolded === "true") return;

    const fold = document.createElement("div");
    const body = document.createElement("div");
    const button = document.createElement("button");
    const id = `app-detail-fold-${++foldIndex}`;

    fold.className = "app-detail-fold";
    fold.setAttribute("data-app-detail-fold", "");
    body.className = "app-detail-fold-body";
    body.id = id;
    button.className = "app-detail-fold-toggle";
    button.type = "button";
    button.setAttribute("aria-controls", id);

    nodes[0].before(fold);
    fold.append(button, body);
    nodes.forEach((node) => body.appendChild(node));

    setExpanded(fold, true);
    button.addEventListener("click", () => {
      setExpanded(fold, !fold.classList.contains("is-expanded"));
    });

    container.dataset.appDetailFolded = "true";
  }

  function applyFolds() {
    if (!root.classList.contains("app-view")) return;

    rules.forEach((rule) => {
      document.querySelectorAll(rule.selector).forEach((container) => {
        if (container.closest(".detail-popup")) return;
        if (container.dataset.appDetailFolded === "true") return;

        const nodes = directMatches(container, rule.foldSelector)
          .filter((node) => !node.matches("script, style, dialog"));
        if (!nodes.length) return;
        if (textLength(nodes) < rule.minText && nodes.length === 1) return;

        createFold(container, nodes);
      });
    });
  }

  function scheduleApply() {
    window.requestAnimationFrame(applyFolds);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", scheduleApply, { once: true });
  } else {
    scheduleApply();
  }

  new MutationObserver(scheduleApply).observe(root, {
    attributes: true,
    attributeFilter: ["class"]
  });
}());
