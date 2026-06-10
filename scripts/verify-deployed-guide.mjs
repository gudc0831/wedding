import { chromium } from "playwright";

const rootUrl = (process.env.DEPLOYED_URL || "").replace(/\/$/, "");
if (!rootUrl) {
  throw new Error("DEPLOYED_URL is required.");
}

const pageUrl = `${rootUrl}/milano_honeymoon_guide.html?verify=${Date.now()}`;
const routeIds = ["day1", "day2", "day3", "day4", "day5", "day6"];
const requiredSectionIds = [
  "overview",
  "practical-info",
  "hotel-base",
  "day-1",
  "day-2",
  "day-3",
  "birthday-special",
  "day-4",
  "day-5",
  "day-6",
  "shopping-map",
  "architecture-picks",
  "sight-notes",
  "prague-transfer",
  "checklist",
  "sources",
  "master-plan"
];

const routeFailurePattern = /좌표 기반|받지 못해|전환했습니다|API 설정 문제|표시하지 못했습니다|불러오지 못했습니다|키가 로컬에 없습니다|인증에 실패|완료되지 않았습니다/;
const googleAccountOverlayPattern = /Google 지도를 제대로 로드할 수 없습니다|This page (?:can't|didn't) load Google Maps correctly/;

const diagnostics = {
  consoleErrors: [],
  pageErrors: []
};

let currentStep = "startup";

function attachDiagnostics(page) {
  page.on("console", (message) => {
    if (message.type() === "error") {
      const text = message.text();
      if (currentStep === "pwa-offline" && text.includes("net::ERR_INTERNET_DISCONNECTED")) {
        return;
      }
      diagnostics.consoleErrors.push(`[${currentStep}] ${text}`);
    }
  });

  page.on("pageerror", (error) => {
    diagnostics.pageErrors.push(`[${currentStep}] ${error.message}`);
  });
}

async function requireVisible(locator, label) {
  try {
    await locator.first().waitFor({ state: "visible", timeout: 30000 });
  } catch (error) {
    throw new Error(`${label} was not visible: ${error.message}`);
  }
}

async function gotoGuidePage(page, url, label) {
  await page.goto(url, { waitUntil: "domcontentloaded", timeout: 60000 });
  try {
    await page.waitForLoadState("load", { timeout: 15000 });
  } catch {
    console.log(`${label} load event did not settle; continuing with targeted checks.`);
  }
}

async function verifyGuideStructure(page, label) {
  currentStep = `${label}-structure`;
  await gotoGuidePage(page, `${pageUrl}&view=${label}`, `${label} structure`);

  await requireVisible(page.locator("h2", { hasText: "이탈리아 여행" }), `${label} hero heading`);
  await requireVisible(page.locator("#master-plan"), `${label} master plan`);
  await requireVisible(page.locator("#checklist"), `${label} checklist`);

  const structure = await page.evaluate((sectionIds) => {
    const missingSections = sectionIds.filter((id) => !document.getElementById(id));
    const navAnchors = Array.from(document.querySelectorAll('a[href^="#"]'))
      .map((anchor) => anchor.getAttribute("href"))
      .filter((href) => href && href.length > 1);
    const missingAnchors = navAnchors.filter((href) => {
      const id = decodeURIComponent(href.slice(1));
      return !document.getElementById(id);
    });
    const duplicateIds = Array.from(document.querySelectorAll("[id]"))
      .map((node) => node.id)
      .filter((id, index, ids) => ids.indexOf(id) !== index);
    const horizontalOverflow = document.documentElement.scrollWidth - window.innerWidth;
    const manifestHref = document.querySelector('link[rel="manifest"]')?.getAttribute("href") || "";

    return {
      missingSections,
      missingAnchors,
      duplicateIds: Array.from(new Set(duplicateIds)),
      horizontalOverflow,
      manifestHref
    };
  }, requiredSectionIds);

  if (structure.missingSections.length) {
    throw new Error(`${label} missing sections: ${structure.missingSections.join(", ")}`);
  }
  if (structure.missingAnchors.length) {
    throw new Error(`${label} missing anchor targets: ${structure.missingAnchors.join(", ")}`);
  }
  if (structure.duplicateIds.length) {
    throw new Error(`${label} duplicate IDs: ${structure.duplicateIds.join(", ")}`);
  }
  if (!structure.manifestHref) {
    throw new Error(`${label} manifest link was not found.`);
  }
  if (label === "mobile" && structure.horizontalOverflow > 20) {
    throw new Error(`mobile horizontal overflow is ${structure.horizontalOverflow}px.`);
  }

  console.log(`Verified ${label} structure.`);
}

async function verifyPwaOffline(page, context) {
  currentStep = "pwa-offline";
  await gotoGuidePage(page, `${pageUrl}&pwa=1`, "PWA offline");

  const pwa = await page.evaluate(async () => {
    const manifestHref = document.querySelector('link[rel="manifest"]')?.href;
    if (!manifestHref) {
      return { error: "missing-manifest-link" };
    }

    const manifestResponse = await fetch(manifestHref, { cache: "no-cache" });
    const manifest = await manifestResponse.json();

    if (!("serviceWorker" in navigator)) {
      return { error: "service-worker-unsupported", manifestName: manifest.name };
    }

    const registration = await navigator.serviceWorker.ready;
    const expectedUrls = [
      "./milano_honeymoon_guide.html",
      "./assets/map-data.json",
      "./assets/basecamp-map.png",
      "./assets/shopping-map.png"
    ].map((path) => new URL(path, location.href).href);
    const cached = {};
    for (const url of expectedUrls) {
      cached[url] = Boolean(await caches.match(url));
    }

    return {
      manifestName: manifest.name,
      activeServiceWorker: Boolean(registration.active),
      scope: registration.scope,
      cacheKeys: await caches.keys(),
      cached
    };
  });

  if (pwa.error) {
    throw new Error(`PWA verification failed: ${pwa.error}`);
  }
  if (pwa.manifestName !== "Milano Honeymoon Guide") {
    throw new Error(`Unexpected manifest name: ${pwa.manifestName}`);
  }
  if (!pwa.activeServiceWorker) {
    throw new Error("Service worker did not become active.");
  }
  if (!pwa.cacheKeys.some((key) => key.startsWith("milano-honeymoon-guide-"))) {
    throw new Error(`Expected offline cache was not created. Caches: ${pwa.cacheKeys.join(", ")}`);
  }
  const uncached = Object.entries(pwa.cached)
    .filter(([, present]) => !present)
    .map(([url]) => url);
  if (uncached.length) {
    throw new Error(`Expected offline assets were not cached: ${uncached.join(", ")}`);
  }

  await page.reload({ waitUntil: "domcontentloaded", timeout: 60000 });
  await page.waitForFunction(() => Boolean(navigator.serviceWorker?.controller), null, { timeout: 30000 });

  await context.setOffline(true);
  try {
    await page.goto(`${rootUrl}/milano_honeymoon_guide.html?offline=${Date.now()}`, {
      waitUntil: "domcontentloaded",
      timeout: 30000
    });
    await requireVisible(page.locator("h2", { hasText: "이탈리아 여행" }), "offline guide heading");

    const offlineMapData = await page.evaluate(async () => {
      const response = await fetch("./assets/map-data.json");
      const data = await response.json();
      return {
        ok: response.ok,
        hasDailyMaps: Array.isArray(data.dailyMaps) && data.dailyMaps.length >= 6,
        hasStaticMaps: Array.isArray(data.maps) && data.maps.length >= 2
      };
    });

    if (!offlineMapData.ok || !offlineMapData.hasDailyMaps || !offlineMapData.hasStaticMaps) {
      throw new Error(`Offline map data check failed: ${JSON.stringify(offlineMapData)}`);
    }
  } finally {
    await context.setOffline(false);
  }

  console.log("Verified PWA install cache and offline document fallback.");
}

async function waitForRouteStatus(page, routeId) {
  const selector = `[data-route-map-card="${routeId}"] [data-google-route-map-status]`;
  await page.waitForFunction((statusSelector) => {
    const text = document.querySelector(statusSelector)?.textContent || "";
    return text && !/불러오는 중|준비 중/.test(text);
  }, selector, { timeout: 90000 });
}

async function verifyRouteMap(page, routeId) {
  currentStep = `route-${routeId}`;
  const card = page.locator(`[data-route-map-card="${routeId}"]`);
  await card.scrollIntoViewIfNeeded();
  await card.locator("[data-route-map-open]").click({ timeout: 30000 });

  const googlePanel = card.locator("[data-google-route-map-target]");
  await googlePanel.locator(".gm-style").waitFor({ timeout: 90000 });
  await waitForRouteStatus(page, routeId);

  const status = await card.locator("[data-google-route-map-status]").innerText({ timeout: 30000 });
  const hasEmbedIframe = await googlePanel.evaluate((node) =>
    Array.from(node.children).some((child) => child.tagName === "IFRAME")
  );
  const hasMap = await googlePanel.locator(".gm-style").count();
  const hasConfigError = await googlePanel.locator(".route-map-error").count();
  const hasGoogleAccountOverlay = await googlePanel.getByText(googleAccountOverlayPattern).count();
  const hasApiScript = await page.evaluate(() =>
    Array.from(document.scripts).some((script) => script.src.includes("maps.googleapis.com/maps/api/js"))
  );

  if (hasEmbedIframe) {
    throw new Error(`${routeId}: expected Google Maps JavaScript API map, but iframe fallback was rendered.`);
  }
  if (!hasApiScript) {
    throw new Error(`${routeId}: Maps JavaScript API loader script was not requested.`);
  }
  if (!hasMap) {
    throw new Error(`${routeId}: Google Maps JavaScript API map container was not rendered.`);
  }
  if (hasConfigError || hasGoogleAccountOverlay) {
    throw new Error(`${routeId}: Google Maps account/API configuration error was rendered.`);
  }
  if (routeFailurePattern.test(status) || !/최단\/최적 경로/.test(status)) {
    throw new Error(`${routeId}: Routes API did not render cleanly. Status: ${status}`);
  }

  console.log(`Verified ${routeId} route map.`);
}

async function verifyRouteMaps(page) {
  currentStep = "route-page";
  await gotoGuidePage(page, `${pageUrl}&routes=1`, "route maps");

  for (const routeId of routeIds) {
    await verifyRouteMap(page, routeId);
  }
}

async function run() {
  const browser = await chromium.launch({ headless: true });
  try {
    const desktopContext = await browser.newContext({
      viewport: { width: 1366, height: 900 },
      serviceWorkers: "allow"
    });
    const desktopPage = await desktopContext.newPage();
    attachDiagnostics(desktopPage);

    await verifyGuideStructure(desktopPage, "desktop");
    await verifyPwaOffline(desktopPage, desktopContext);
    await verifyRouteMaps(desktopPage);
    await desktopContext.close();

    const mobileContext = await browser.newContext({
      viewport: { width: 390, height: 844 },
      isMobile: true,
      serviceWorkers: "allow"
    });
    const mobilePage = await mobileContext.newPage();
    attachDiagnostics(mobilePage);

    await verifyGuideStructure(mobilePage, "mobile");
    await mobileContext.close();

    if (diagnostics.pageErrors.length || diagnostics.consoleErrors.length) {
      const errors = [...diagnostics.pageErrors, ...diagnostics.consoleErrors].join("\n");
      throw new Error(`Browser console/page errors found:\n${errors}`);
    }
  } finally {
    await browser.close();
  }
}

run().catch((error) => {
  console.error(error);
  process.exit(1);
});
