(function () {
  const sections = Array.from(document.querySelectorAll("[data-collapsible-section]"));
  if (!sections.length) return;

  const storagePrefix = "honeymoonGuideSection:";

  function getStored(id) {
    try {
      return window.localStorage.getItem(storagePrefix + id);
    } catch {
      return null;
    }
  }

  function setStored(id, value) {
    try {
      window.localStorage.setItem(storagePrefix + id, value);
    } catch {
      return;
    }
  }

  function setCollapsed(section, button, collapsed) {
    section.classList.toggle("is-collapsed", collapsed);
    button.setAttribute("aria-expanded", String(!collapsed));
    button.textContent = collapsed ? "열기" : "닫기";
  }

  sections.forEach((section) => {
    const id = section.id || section.dataset.collapsibleSection;
    const inner = section.querySelector(":scope > .section-inner");
    const head = inner?.querySelector(":scope > .section-head");
    if (!id || !inner || !head) return;

    const body = document.createElement("div");
    body.className = "collapsible-section-body";
    body.id = `${id}-collapsible-body`;

    while (head.nextSibling) {
      body.appendChild(head.nextSibling);
    }
    inner.appendChild(body);

    const button = document.createElement("button");
    button.className = "collapsible-section-toggle";
    button.type = "button";
    button.setAttribute("aria-controls", body.id);
    head.appendChild(button);

    section.classList.add("collapsible-section");
    const stored = getStored(id);
    const defaultCollapsed = section.dataset.defaultCollapsed !== "false";
    const collapsed = stored ? stored === "collapsed" : defaultCollapsed;
    setCollapsed(section, button, collapsed);

    button.addEventListener("click", () => {
      const nextCollapsed = !section.classList.contains("is-collapsed");
      setCollapsed(section, button, nextCollapsed);
      setStored(id, nextCollapsed ? "collapsed" : "expanded");
    });
  });
}());
