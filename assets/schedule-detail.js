(function () {
  const events = Array.from(document.querySelectorAll(".calendar-board .calendar-event"));
  if (!events.length) return;

  const typeLabels = {
    transit: "이동/교통",
    tour: "투어/관광",
    food: "식사/카페",
    stay: "숙소/체크인",
    prep: "준비/확인"
  };

  let activeEvent = null;
  let openFrame = 0;
  let closeTimer = 0;

  function text(node) {
    return (node?.textContent || "").replace(/\s+/g, " ").trim();
  }

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function gridStart(node, property) {
    const inline = node.getAttribute("style") || "";
    const match = inline.match(new RegExp(`${property}\\s*:\\s*([^;]+)`));
    const value = match ? match[1] : "";
    const number = value.match(/\d+/);
    if (number) return number[0];

    const computed = window.getComputedStyle(node);
    const computedValue = property === "grid-column" ? computed.gridColumnStart : computed.gridRowStart;
    return computedValue && computedValue !== "auto" ? computedValue : "";
  }

  function sameGridCell(node, column, row) {
    return gridStart(node, "grid-column") === column && gridStart(node, "grid-row") === String(row);
  }

  function cellText(board, column, row, selector) {
    const node = Array.from(board.querySelectorAll(selector)).find((item) => sameGridCell(item, column, row));
    return text(node);
  }

  function eventType(event) {
    return Object.keys(typeLabels).find((type) => event.classList.contains(type)) || "event";
  }

  function detailLines(event, title) {
    const value = event.dataset.detail || "";
    const lines = value.split("|").map((item) => item.trim()).filter(Boolean);
    if (lines.length) return lines;
    if (!title.includes("→")) return [];
    return title.split("→").map((item) => item.trim()).filter(Boolean);
  }

  function badgeTone(label) {
    if (/예약완료|조식포함|구매완료/.test(label)) return "done";
    if (/예약필요|확인필요|조식없음|구매필요|구매예정/.test(label)) return "urgent";
    return "";
  }

  function inferredBadges(event, title, note, stay, prep) {
    const badges = Array.from(event.querySelectorAll(".schedule-badge")).map(text).filter(Boolean);
    const source = `${title} ${note} ${stay} ${prep}`;
    if (/조식 없음|조식없음/.test(source) && !badges.includes("조식없음")) badges.push("조식없음");
    if (/호텔조식|조식 포함|조식포함/.test(source) && !badges.includes("조식포함")) badges.push("조식포함");
    return badges;
  }

  function contextFor(event) {
    const board = event.closest(".calendar-board");
    const column = gridStart(event, "grid-column");
    if (!board || !column) return {};
    return {
      date: cellText(board, column, 1, ".calendar-date"),
      city: cellText(board, column, 2, ".calendar-meta.city"),
      stay: cellText(board, column, 3, ".calendar-meta.stay-row"),
      prep: cellText(board, column, 4, ".calendar-meta.prep-row")
    };
  }

  function createLayer() {
    const layer = document.createElement("div");
    layer.className = "schedule-detail-backdrop";
    layer.hidden = true;
    layer.innerHTML = `
      <section class="schedule-detail-sheet" role="dialog" aria-modal="true" aria-labelledby="schedule-detail-title">
        <div class="schedule-detail-grip" data-schedule-detail-grip></div>
        <header class="schedule-detail-head">
          <div>
            <div class="schedule-detail-kicker" data-schedule-detail-kicker></div>
            <h3 id="schedule-detail-title" data-schedule-detail-title></h3>
            <p class="schedule-detail-subtitle" data-schedule-detail-subtitle></p>
            <div class="schedule-detail-status" data-schedule-detail-status></div>
          </div>
          <button class="schedule-detail-close" type="button" data-schedule-detail-close aria-label="일정 상세 닫기">×</button>
        </header>
        <div class="schedule-detail-body">
          <dl class="schedule-detail-context" data-schedule-detail-context></dl>
          <section class="schedule-detail-section" data-schedule-detail-summary-section>
            <h4>요약</h4>
            <p data-schedule-detail-summary></p>
          </section>
          <section class="schedule-detail-section" data-schedule-detail-lines-section hidden>
            <h4>세부 구간</h4>
            <ol class="schedule-detail-list" data-schedule-detail-lines></ol>
          </section>
        </div>
      </section>
    `;
    document.body.appendChild(layer);
    return layer;
  }

  const layer = createLayer();
  const sheet = layer.querySelector(".schedule-detail-sheet");
  const closeButton = layer.querySelector("[data-schedule-detail-close]");
  const grip = layer.querySelector("[data-schedule-detail-grip]");

  function setHtml(selector, value) {
    const node = layer.querySelector(selector);
    if (node) node.innerHTML = value;
  }

  function openDetail(event) {
    if (openFrame) {
      window.cancelAnimationFrame(openFrame);
      openFrame = 0;
    }
    if (closeTimer) {
      window.clearTimeout(closeTimer);
      closeTimer = 0;
    }
    activeEvent = event;
    const type = eventType(event);
    const typeLabel = typeLabels[type] || "일정";
    const title = text(event.querySelector("strong")) || "일정";
    const time = text(event.querySelector(".event-time"));
    const note = text(event.querySelector(".event-note"));
    const context = contextFor(event);
    const badges = inferredBadges(event, title, note, context.stay || "", context.prep || "");
    const lines = detailLines(event, title);
    const subtitle = [context.date, time].filter(Boolean).join(" · ");
    const summary = note || context.prep || context.stay || `${typeLabel} 일정입니다.`;

    setHtml("[data-schedule-detail-kicker]", `<span class="schedule-detail-type ${type}">${escapeHtml(typeLabel)}</span>`);
    setHtml("[data-schedule-detail-title]", escapeHtml(title));
    setHtml("[data-schedule-detail-subtitle]", escapeHtml(subtitle));
    setHtml(
      "[data-schedule-detail-status]",
      badges.map((badge) => `<span class="schedule-detail-chip ${badgeTone(badge)}">${escapeHtml(badge)}</span>`).join("")
    );

    const contextRows = [
      ["날짜", context.date],
      ["도시", context.city],
      ["숙소", context.stay],
      ["준비", context.prep]
    ].filter(([, value]) => value);

    setHtml(
      "[data-schedule-detail-context]",
      contextRows.map(([label, value]) => `<div><dt>${escapeHtml(label)}</dt><dd>${escapeHtml(value)}</dd></div>`).join("")
    );
    setHtml("[data-schedule-detail-summary]", escapeHtml(summary));

    const linesSection = layer.querySelector("[data-schedule-detail-lines-section]");
    const linesList = layer.querySelector("[data-schedule-detail-lines]");
    if (lines.length && linesSection && linesList) {
      linesList.innerHTML = lines.map((line) => `<li>${escapeHtml(line)}</li>`).join("");
      linesSection.hidden = false;
    } else if (linesSection && linesList) {
      linesList.replaceChildren();
      linesSection.hidden = true;
    }

    layer.hidden = false;
    document.body.classList.add("schedule-detail-open");
    openFrame = requestAnimationFrame(() => {
      openFrame = 0;
      if (!layer.hidden && activeEvent === event) layer.classList.add("is-open");
    });
    closeButton.focus({ preventScroll: true });
  }

  function closeDetail() {
    if (openFrame) {
      window.cancelAnimationFrame(openFrame);
      openFrame = 0;
    }
    if (closeTimer) window.clearTimeout(closeTimer);
    layer.classList.remove("is-open");
    document.body.classList.remove("schedule-detail-open");
    closeTimer = window.setTimeout(() => {
      closeTimer = 0;
      layer.hidden = true;
      if (activeEvent) activeEvent.focus({ preventScroll: true });
      activeEvent = null;
    }, 180);
  }

  events.forEach((event) => {
    const title = text(event.querySelector("strong")) || "일정";
    const time = text(event.querySelector(".event-time"));
    event.setAttribute("role", "button");
    event.setAttribute("tabindex", "0");
    event.setAttribute("aria-haspopup", "dialog");
    event.setAttribute("aria-label", `${[time, title].filter(Boolean).join(" ")} 상세`);
    event.addEventListener("click", () => openDetail(event));
    event.addEventListener("keydown", (keyboardEvent) => {
      if (keyboardEvent.key !== "Enter" && keyboardEvent.key !== " ") return;
      keyboardEvent.preventDefault();
      openDetail(event);
    });
  });

  closeButton.addEventListener("click", closeDetail);
  layer.addEventListener("click", (event) => {
    if (event.target === layer) closeDetail();
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !layer.hidden) closeDetail();
  });

  let startY = null;
  grip.addEventListener("pointerdown", (event) => {
    startY = event.clientY;
    grip.setPointerCapture(event.pointerId);
  });
  grip.addEventListener("pointerup", (event) => {
    if (startY !== null && event.clientY - startY > 70) closeDetail();
    startY = null;
  });
  sheet.addEventListener("pointercancel", () => {
    startY = null;
  });
}());
