import { spawn } from "node:child_process";
import { existsSync, mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const rootUrl = (process.env.LOCAL_URL || "http://localhost:8000").replace(/\/$/, "");
const debugPort = Number(process.env.CHROME_DEBUG_PORT || (9400 + Math.floor(Math.random() * 400)));
const pageSpecs = [
  { label: "czech", path: "/czech_honeymoon_guide.html" },
  { label: "switzerland", path: "/switzerland_honeymoon_guide.html" },
  { label: "italy", path: "/italy_honeymoon_guide.html" }
];
const viewports = [
  { label: "iphone15-pro", width: 393, height: 852 },
  { label: "iphone17-pro", width: 402, height: 874 }
];

function chromePath() {
  const candidates = [
    process.env.CHROME_PATH,
    "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
    "C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe",
    "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"
  ].filter(Boolean);
  const found = candidates.find((candidate) => existsSync(candidate));
  if (!found) throw new Error("Chrome or Edge executable was not found. Set CHROME_PATH.");
  return found;
}

async function getJson(url, init) {
  const response = await fetch(url, init);
  if (!response.ok) throw new Error(`${response.status} ${url}`);
  return response.json();
}

async function waitForDebugEndpoint() {
  const deadline = Date.now() + 15000;
  while (Date.now() < deadline) {
    try {
      await getJson(`http://localhost:${debugPort}/json/version`);
      return;
    } catch {
      await new Promise((resolve) => setTimeout(resolve, 250));
    }
  }
  throw new Error("Chrome remote debugging endpoint did not become ready.");
}

function createCdpClient(wsUrl) {
  const ws = new WebSocket(wsUrl);
  let id = 0;
  const pending = new Map();
  const errors = [];
  const opened = new Promise((resolve, reject) => {
    ws.addEventListener("open", resolve, { once: true });
    ws.addEventListener("error", reject, { once: true });
  });

  ws.addEventListener("message", (event) => {
    const message = JSON.parse(event.data);
    if (message.id && pending.has(message.id)) {
      const item = pending.get(message.id);
      pending.delete(message.id);
      if (message.error) item.reject(new Error(message.error.message));
      else item.resolve(message.result || {});
      return;
    }
    if (message.method === "Runtime.exceptionThrown") {
      errors.push(message.params.exceptionDetails?.text || "runtime exception");
    }
    if (message.method === "Runtime.consoleAPICalled" && message.params.type === "error") {
      errors.push((message.params.args || []).map((arg) => arg.value || arg.description || "").join(" "));
    }
    if (message.method === "Log.entryAdded" && message.params.entry?.level === "error") {
      errors.push(message.params.entry.text || "log error");
    }
  });

  function send(method, params = {}) {
    const callId = ++id;
    ws.send(JSON.stringify({ id: callId, method, params }));
    return new Promise((resolve, reject) => pending.set(callId, { resolve, reject }));
  }

  return { opened, send, errors, close: () => ws.close() };
}

async function evaluate(cdp, expression) {
  const response = await cdp.send("Runtime.evaluate", {
    expression,
    awaitPromise: true,
    returnByValue: true,
    userGesture: true
  });
  if (response.exceptionDetails) throw new Error(response.exceptionDetails.text || "evaluation failed");
  return response.result.value;
}

async function navigate(cdp, url) {
  await cdp.send("Page.navigate", { url });
  const deadline = Date.now() + 20000;
  while (Date.now() < deadline) {
    const ready = await evaluate(cdp, `document.readyState !== "loading"`);
    if (ready) break;
    await new Promise((resolve) => setTimeout(resolve, 100));
  }
  const ready = await evaluate(cdp, `document.readyState !== "loading"`);
  if (!ready) throw new Error(`Timed out waiting for DOM parsing: ${url}`);
  await evaluate(cdp, `new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve)))`);
}

const inspectExpression = `(async () => {
  const normalize = (value) => String(value || "").replace(/\\s+/g, " ").trim();
  const fnv1a = (value) => {
    let hash = 2166136261;
    for (let index = 0; index < value.length; index += 1) {
      hash ^= value.charCodeAt(index);
      hash = Math.imul(hash, 16777619);
    }
    return (hash >>> 0).toString(16).padStart(8, "0");
  };
  document.documentElement.style.scrollBehavior = "auto";
  document.body.style.scrollBehavior = "auto";
  window.scrollTo(0, 0);
  await new Promise((resolve) => requestAnimationFrame(resolve));

  const main = document.querySelector("main");
  const clone = main?.cloneNode(true);
  clone?.querySelectorAll(".app-detail-fold-toggle, script, style").forEach((node) => node.remove());
  const canonicalText = normalize(clone?.textContent);
  const nav = document.querySelector(".nav-links");
  const navAnchor = nav?.querySelector("a");
  const brandMark = document.querySelector(".brand-mark");
  const compactStylesheet = Array.from(document.styleSheets)
    .map((sheet) => sheet.href || "")
    .find((href) => href.includes("guide-compact.css")) || "";
  const timelineOverflow = Array.from(document.querySelectorAll(".timeline")).filter((node) => {
    const nodeRect = node.getBoundingClientRect();
    const parentRect = node.parentElement?.getBoundingClientRect();
    return parentRect && (nodeRect.left < parentRect.left - 1 || nodeRect.right > parentRect.right + 1);
  }).map((node) => node.closest("[id]")?.id || "unknown");
  const timelineDetails = Array.from(document.querySelectorAll(".timeline")).map((node) => {
    const nodeRect = node.getBoundingClientRect();
    const parentRect = node.parentElement?.getBoundingClientRect();
    const style = getComputedStyle(node);
    const parentStyle = node.parentElement ? getComputedStyle(node.parentElement) : null;
    return {
      section: node.closest("[id]")?.id || "unknown",
      left: nodeRect.left,
      right: nodeRect.right,
      width: nodeRect.width,
      parentLeft: parentRect?.left ?? 0,
      parentRight: parentRect?.right ?? 0,
      parentWidth: parentRect?.width ?? 0,
      minWidth: style.minWidth,
      maxWidth: style.maxWidth,
      parentGrid: parentStyle?.gridTemplateColumns || ""
    };
  }).filter((item) => timelineOverflow.includes(item.section));
  const clippedCaptions = Array.from(document.querySelectorAll(".hero-visual figcaption")).filter((node) => {
    const style = getComputedStyle(node);
    return style.overflow === "hidden" && node.scrollHeight > node.clientHeight + 1;
  }).map((node) => normalize(node.textContent).slice(0, 80));
  const collapsedFolds = document.documentElement.classList.contains("app-view")
    ? document.querySelectorAll(".app-detail-fold:not(.is-expanded) .app-detail-fold-body").length
    : 0;
  const buttons = Array.from(document.querySelectorAll("[data-route-map-open]"));
  const tapFailures = [];
  for (const button of buttons) {
    button.scrollIntoView({ block: "center", inline: "center", behavior: "instant" });
    await new Promise((resolve) => setTimeout(resolve, 40));
    const rect = button.getBoundingClientRect();
    const hit = document.elementFromPoint(rect.left + rect.width / 2, rect.top + rect.height / 2);
    if (!(hit && (hit === button || button.contains(hit)))) {
      tapFailures.push(button.closest("[data-route-map-card]")?.dataset.routeMapCard || "unknown");
    }
  }
  window.scrollTo(0, 0);

  const navStyle = navAnchor ? getComputedStyle(navAnchor) : null;
  const brandRect = brandMark?.getBoundingClientRect();
  return {
    title: document.title,
    appView: document.documentElement.classList.contains("app-view"),
    compactStylesheet,
    documentOverflow: document.documentElement.scrollWidth - window.innerWidth,
    timelineOverflow,
    timelineDetails,
    clippedCaptions,
    collapsedFolds,
    tapFailures,
    routeButtonCount: buttons.length,
    navHeight: navAnchor?.getBoundingClientRect().height || 0,
    navFontSize: navStyle ? Number.parseFloat(navStyle.fontSize) : 0,
    brandWidth: brandRect?.width || 0,
    brandHeight: brandRect?.height || 0,
    headings: main?.querySelectorAll("h1,h2,h3,h4,h5,h6").length || 0,
    links: main?.querySelectorAll("a").length || 0,
    images: main?.querySelectorAll("img").length || 0,
    canonicalTextHash: fnv1a(canonicalText)
  };
})()`;

function collectMetricFailures(item) {
  const failures = [];
  const prefix = `${item.viewport}-${item.page}-${item.view}`;
  if (item.documentOverflow !== 0) failures.push(`${prefix}: document overflow ${item.documentOverflow}px`);
  if (item.timelineOverflow.length) failures.push(`${prefix}: clipped timelines ${item.timelineOverflow.join(", ")}`);
  if (item.clippedCaptions.length) failures.push(`${prefix}: clipped captions ${item.clippedCaptions.length}`);
  if (item.tapFailures.length) failures.push(`${prefix}: untappable route buttons ${item.tapFailures.join(", ")}`);
  if (Math.abs(item.brandWidth - item.brandHeight) > 1) {
    failures.push(`${prefix}: brand mark is ${item.brandWidth.toFixed(1)}x${item.brandHeight.toFixed(1)}`);
  }
  if (item.view === "app") {
    if (item.collapsedFolds) failures.push(`${prefix}: ${item.collapsedFolds} content folds collapsed by default`);
    if (item.navHeight < 28) failures.push(`${prefix}: nav target height ${item.navHeight.toFixed(1)}px`);
    if (item.navFontSize < 10) failures.push(`${prefix}: nav font ${item.navFontSize.toFixed(1)}px`);
  }
  return failures;
}

async function verifyTogglePersistence(cdp, spec, initialView) {
  const url = `${rootUrl}${spec.path}?ui-toggle=${Date.now()}&view=${initialView}`;
  await navigate(cdp, url);
  const expectedView = initialView === "app" ? "web" : "app";
  const clicked = await evaluate(cdp, `(() => {
    document.querySelector("[data-view-toggle]").click();
    return {
      view: document.documentElement.classList.contains("app-view") ? "app" : "web",
      query: new URL(location.href).searchParams.get("view")
    };
  })()`);
  await cdp.send("Page.reload", { ignoreCache: true });
  await new Promise((resolve) => setTimeout(resolve, 1000));
  const reloadedView = await evaluate(cdp, `document.documentElement.classList.contains("app-view") ? "app" : "web"`);
  return {
    page: spec.label,
    initialView,
    expectedView,
    clickedView: clicked.view,
    queryView: clicked.query,
    reloadedView
  };
}

async function run() {
  const profile = mkdtempSync(join(tmpdir(), "wedding-ui-cdp-"));
  const chrome = spawn(chromePath(), [
    "--headless=new",
    "--disable-gpu",
    "--no-first-run",
    "--no-default-browser-check",
    `--remote-debugging-port=${debugPort}`,
    `--user-data-dir=${profile}`,
    "about:blank"
  ], { stdio: "ignore" });

  try {
    await waitForDebugEndpoint();
    const target = await getJson(`http://localhost:${debugPort}/json/new?about:blank`, { method: "PUT" });
    const cdp = createCdpClient(target.webSocketDebuggerUrl);
    await cdp.opened;
    await cdp.send("Page.enable");
    await cdp.send("Runtime.enable");
    await cdp.send("Log.enable").catch(() => {});

    const matrix = [];
    const failures = [];
    for (const viewport of viewports) {
      await cdp.send("Emulation.setDeviceMetricsOverride", {
        width: viewport.width,
        height: viewport.height,
        deviceScaleFactor: 1,
        mobile: true,
        screenWidth: viewport.width,
        screenHeight: viewport.height
      });
      for (const spec of pageSpecs) {
        const byView = {};
        for (const view of ["web", "app"]) {
          await navigate(cdp, `${rootUrl}${spec.path}?ui=${Date.now()}&view=${view}`);
          const item = {
            viewport: viewport.label,
            page: spec.label,
            view,
            ...(await evaluate(cdp, inspectExpression))
          };
          matrix.push(item);
          byView[view] = item;
          failures.push(...collectMetricFailures(item));
        }
        for (const field of ["headings", "links", "images", "routeButtonCount", "canonicalTextHash"]) {
          if (byView.web[field] !== byView.app[field]) {
            failures.push(`${viewport.label}-${spec.label}: ${field} differs between web and app`);
          }
        }
      }
    }

    await cdp.send("Emulation.setDeviceMetricsOverride", {
      width: 393,
      height: 852,
      deviceScaleFactor: 1,
      mobile: true,
      screenWidth: 393,
      screenHeight: 852
    });
    const toggles = [];
    for (const spec of pageSpecs) {
      for (const initialView of ["app", "web"]) {
        const result = await verifyTogglePersistence(cdp, spec, initialView);
        toggles.push(result);
        if (
          result.clickedView !== result.expectedView ||
          result.queryView !== result.expectedView ||
          result.reloadedView !== result.expectedView
        ) {
          failures.push(`${spec.label}-${initialView}: toggle did not persist ${result.expectedView}`);
        }
      }
    }

    if (cdp.errors.length) failures.push(...cdp.errors.map((error) => `browser error: ${error}`));
    cdp.close();
    console.log(JSON.stringify({ rootUrl, matrix, toggles, failures }, null, 2));
    if (failures.length) process.exitCode = 1;
  } finally {
    chrome.kill("SIGKILL");
    await new Promise((resolve) => setTimeout(resolve, 700));
    try { rmSync(profile, { recursive: true, force: true }); } catch {}
  }
}

run().catch((error) => {
  console.error(error);
  process.exit(1);
});
