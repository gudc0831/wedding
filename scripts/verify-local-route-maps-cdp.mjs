import { spawn } from "node:child_process";
import { existsSync, mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const rootUrl = (process.env.LOCAL_URL || "http://localhost:8000").replace(/\/$/, "");
const debugPort = Number(process.env.CHROME_DEBUG_PORT || (9300 + Math.floor(Math.random() * 1000)));
const pageSpecs = [
  {
    label: "switzerland",
    path: "/switzerland_honeymoon_guide.html",
    routeIds: ["swiss-day1", "swiss-day2", "swiss-day3", "swiss-day6"]
  },
  {
    label: "italy",
    path: "/italy_honeymoon_guide.html",
    routeIds: ["day1", "day2", "day3", "day4", "day5", "day5-1-verona", "day6"]
  }
];
const googleLogPattern = /Google Maps JavaScript API error|RefererNotAllowed|403|Routes|Invalid|ApiNotActivated|Billing|Quota/i;

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
      await new Promise((resolve) => setTimeout(resolve, 500));
    }
  }
  throw new Error("Chrome remote debugging endpoint did not become ready.");
}

function createCdpClient(wsUrl) {
  const ws = new WebSocket(wsUrl);
  let id = 0;
  const pending = new Map();
  const logs = [];

  const opened = new Promise((resolve, reject) => {
    ws.addEventListener("open", resolve, { once: true });
    ws.addEventListener("error", reject, { once: true });
  });

  ws.addEventListener("message", (event) => {
    const message = JSON.parse(event.data);
    if (message.id && pending.has(message.id)) {
      const { resolve, reject } = pending.get(message.id);
      pending.delete(message.id);
      if (message.error) reject(new Error(message.error.message));
      else resolve(message.result || {});
      return;
    }

    if (message.method === "Runtime.consoleAPICalled") {
      logs.push(message.params.args?.map((arg) => arg.value || arg.description).join(" "));
    } else if (message.method === "Log.entryAdded") {
      logs.push(message.params.entry?.text);
    }
  });

  function send(method, params = {}) {
    const callId = ++id;
    ws.send(JSON.stringify({ id: callId, method, params }));
    return new Promise((resolve, reject) => pending.set(callId, { resolve, reject }));
  }

  return { opened, send, logs, close: () => ws.close() };
}

async function evaluateSetup(cdp, spec) {
  const setupResult = await cdp.send("Runtime.evaluate", {
    awaitPromise: true,
    returnByValue: true,
    expression: `(async () => {
      if (window.GOOGLE_MAPS_CONFIG_READY) await window.GOOGLE_MAPS_CONFIG_READY;
      if (!window.GOOGLE_MAPS_CONFIG?.apiKey && typeof window.loadLocalGoogleMapsConfig === "function") {
        await window.loadLocalGoogleMapsConfig();
      }
      const expectedRouteIds = ${JSON.stringify(spec.routeIds)};
      const cfg = window.GOOGLE_MAPS_CONFIG || {};
      const data = await (await fetch("./assets/map-data.json", { cache: "no-cache" })).json();
      const dailyMaps = data.dailyMaps || [];
      const visibleRouteIds = Array.from(document.querySelectorAll("[data-route-map-card]")).map((node) => node.dataset.routeMapCard);
      const routeMeta = Object.fromEntries(expectedRouteIds.map((id) => {
        const mapConfig = dailyMaps.find((item) => item.id === id);
        return [id, {
          hasMapConfig: Boolean(mapConfig),
          routeCount: mapConfig?.routes?.length || 0,
          hasCoordinateRoutes: Boolean(mapConfig?.routes?.some((segment) =>
            segment.useCoordinateRouting ||
            String(segment.mapTravelMode || segment.travelMode || "DRIVING").toUpperCase() !== "DRIVING"
          )),
          usesOfficialCoordinateAxis: Boolean(mapConfig?.officialCoordinateAxis || mapConfig?.useCoordinateRouting)
        }];
      }));
      return {
        title: document.title,
        cfg: {
          hasApiKey: Boolean(cfg.apiKey),
          engine: cfg.googleRouteEngine,
          limit: cfg.googleMapMonthlyLimit
        },
        visibleRouteIds,
        routeMeta
      };
    })()`
  });

  return setupResult.result.value;
}

async function verifyRouteMap(cdp, routeId) {
  const routeResult = await cdp.send("Runtime.evaluate", {
    awaitPromise: true,
    returnByValue: true,
    timeout: 70000,
    userGesture: true,
    expression: `(async () => {
      const routeId = ${JSON.stringify(routeId)};
      const card = document.querySelector('[data-route-map-card="' + routeId + '"]');
      if (!card) return { routeId, missingCard: true };
      card.scrollIntoView({ block: "center" });
      await new Promise((resolve) => setTimeout(resolve, 200));
      const button = card.querySelector("[data-route-map-open]");
      if (button.textContent.includes("닫기")) button.click();
      await new Promise((resolve) => setTimeout(resolve, 100));
      button.click();

      const deadline = Date.now() + 65000;
      while (Date.now() < deadline) {
        const status = card.querySelector("[data-google-route-map-status], [data-route-map-status]")?.textContent || "";
        const hasError = Boolean(card.querySelector(".route-map-error"));
        const gmStyle = Boolean(card.querySelector("[data-google-route-map-target] .gm-style, [data-route-map-target] .gm-style"));
        if (hasError || (gmStyle && status && !/불러오는 중|준비 중/.test(status))) break;
        await new Promise((resolve) => setTimeout(resolve, 500));
      }

      const panel = card.querySelector("[data-google-route-map-target], [data-route-map-target]");
      const status = card.querySelector("[data-google-route-map-status], [data-route-map-status]")?.textContent || "";
      const panelText = panel?.innerText || "";
      const result = {
        routeId,
        gmStyle: Boolean(panel?.querySelector(".gm-style")),
        hasError: Boolean(panel?.querySelector(".route-map-error")),
        hasIframe: Array.from(panel?.children || []).some((child) => child.tagName === "IFRAME"),
        hasAccountOverlay: /Google 지도를 제대로 로드할 수 없습니다|This page (?:can't|didn't) load Google Maps correctly/.test(panelText),
        status
      };
      if (button.textContent.includes("닫기")) button.click();
      return result;
    })()`
  });

  return routeResult.result.value;
}

function collectFailures(spec, setup, hasApiScript, results) {
  const failures = [];
  if (!setup.cfg.hasApiKey || setup.cfg.engine !== "routes") failures.push(`${spec.label}: config not keyed routes`);
  if (JSON.stringify(setup.visibleRouteIds) !== JSON.stringify(spec.routeIds)) {
    failures.push(`${spec.label}: visible route ids differ from expected order`);
  }
  if (!hasApiScript) failures.push(`${spec.label}: maps js api script not requested`);

  for (const item of results) {
    const meta = setup.routeMeta[item.routeId] || {};
    if (!meta.hasMapConfig || !meta.routeCount) failures.push(`${item.routeId}: map-data route configuration missing`);
    if (!item.gmStyle) failures.push(`${item.routeId}: gm-style missing`);
    if (item.hasError) failures.push(`${item.routeId}: error rendered`);
    if (item.hasIframe) failures.push(`${item.routeId}: iframe fallback rendered`);
    if (item.hasAccountOverlay) failures.push(`${item.routeId}: account overlay rendered`);

    if (meta.usesOfficialCoordinateAxis) {
      if (!/공식 시간표로 확인한 교통축/.test(item.status)) {
        failures.push(`${item.routeId}: expected official coordinate status, got ${item.status}`);
      }
    } else if (meta.hasCoordinateRoutes) {
      if (!/^최단\/최적 경로|좌표 기반 보조선/.test(item.status)) {
        failures.push(`${item.routeId}: expected clean route or coordinate helper status, got ${item.status}`);
      }
    } else if (!/^최단\/최적 경로/.test(item.status)) {
      failures.push(`${item.routeId}: expected clean route status, got ${item.status}`);
    }
  }

  return failures;
}

async function run() {
  const profile = mkdtempSync(join(tmpdir(), "wedding-chrome-cdp-"));
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
    if (!target) throw new Error("No Chrome page target found.");

    const cdp = createCdpClient(target.webSocketDebuggerUrl);
    await cdp.opened;
    await cdp.send("Page.enable");
    await cdp.send("Runtime.enable");
    await cdp.send("Log.enable").catch(() => {});

    const summaries = [];
    const failures = [];

    for (const spec of pageSpecs) {
      await cdp.send("Page.navigate", { url: `${rootUrl}${spec.path}?routes=1&verify=${Date.now()}` });
      await new Promise((resolve) => setTimeout(resolve, 5000));

      const setup = await evaluateSetup(cdp, spec);
      const results = [];
      for (const routeId of spec.routeIds) {
        results.push(await verifyRouteMap(cdp, routeId));
      }

      const hasApiScriptResult = await cdp.send("Runtime.evaluate", {
        returnByValue: true,
        expression: `Array.from(document.scripts).some((script) => script.src.includes("maps.googleapis.com/maps/api/js"))`
      });
      const hasApiScript = hasApiScriptResult.result.value;
      const pageSummary = { label: spec.label, path: spec.path, setup, hasApiScript, results };
      summaries.push(pageSummary);
      failures.push(...collectFailures(spec, setup, hasApiScript, results));
    }

    cdp.close();
    const relevantLogs = cdp.logs.filter(Boolean).filter((line) => googleLogPattern.test(line)).slice(0, 20);
    console.log(JSON.stringify({ rootUrl, pages: summaries, relevantLogs }, null, 2));

    if (failures.length) {
      console.error(`FAILURES:\n${failures.join("\n")}`);
      process.exitCode = 1;
    }
  } finally {
    chrome.kill("SIGKILL");
    await new Promise((resolve) => {
      const timer = setTimeout(resolve, 1500);
      chrome.once("exit", () => {
        clearTimeout(timer);
        resolve();
      });
    });

    try {
      rmSync(profile, { recursive: true, force: true });
    } catch (error) {
      console.warn(`Warning: could not remove temporary Chrome profile ${profile}: ${error.code || error.message}`);
    }
  }
}

run().catch((error) => {
  console.error(error);
  process.exit(1);
});
