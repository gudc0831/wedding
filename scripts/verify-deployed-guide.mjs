import { chromium } from "playwright";

const rootUrl = (process.env.DEPLOYED_URL || "").replace(/\/$/, "");
if (!rootUrl) {
  throw new Error("DEPLOYED_URL is required.");
}

const pageSpecs = [
  {
    label: "czech",
    path: "/czech_honeymoon_guide.html",
    routeIds: [],
    requiredSectionIds: [
      "czech-overview",
      "czech-first-leg",
      "czech-return-divider",
      "czech-return-leg",
      "czech-sources"
    ]
  },
  {
    label: "switzerland",
    path: "/switzerland_honeymoon_guide.html",
    routeIds: ["swiss-day1", "swiss-day2", "swiss-day3", "swiss-day6"],
    requiredSectionIds: ["switzerland", "swiss-day-4", "swiss-day-5", "swiss-day-6"]
  },
  {
    label: "italy",
    path: "/italy_honeymoon_guide.html",
    routeIds: ["day1", "day2", "day3", "day4", "day5", "day5-1-verona", "day6"],
    requiredSectionIds: [
      "italy",
      "overview",
      "practical-info",
      "hotel-base",
      "day-1",
      "day-2",
      "day-3",
      "birthday-special",
      "day-4",
      "day-5",
      "day-5-1",
      "day-6",
      "shopping-map",
      "architecture-picks",
      "sight-notes",
      "prague-transfer",
      "checklist",
      "sources",
      "italy-excel-schedule"
    ]
  }
];

const googleAccountOverlayPattern = /Google 지도를 제대로 로드할 수 없습니다|This page (?:can't|didn't) load Google Maps correctly/;
const mobileGuideViewports = [
  { label: "iphone15-pro", width: 393, height: 852 },
  { label: "iphone17-pro", width: 402, height: 874 }
];
const mobileGuideViews = ["web", "app"];
const horizontalOverflowThreshold = 20;

const diagnostics = {
  consoleErrors: [],
  pageErrors: []
};

let currentStep = "startup";

function pageUrl(path, view) {
  return `${rootUrl}${path}?verify=${Date.now()}&view=${view}`;
}

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

async function verifyIndex(page, label, view = label) {
  currentStep = `${label}-index`;
  await gotoGuidePage(page, pageUrl("/index.html", view), `${label} index`);
  await requireVisible(page.locator("h1", { hasText: "Czechia, Swiss & Italy Honeymoon Guide" }), `${label} index heading`);
  await requireVisible(page.locator("a[href='./czech_honeymoon_guide.html']"), `${label} czech link`);
  await requireVisible(page.locator("a[href='./switzerland_honeymoon_guide.html']"), `${label} swiss link`);
  await requireVisible(page.locator("a[href='./italy_honeymoon_guide.html']"), `${label} italy link`);
}

async function verifyGuideStructure(page, spec, label, options = {}) {
  const {
    view = label,
    expectedAppView = null,
    enforceHorizontalOverflow = label === "mobile"
  } = options;

  currentStep = `${label}-${spec.label}-structure`;
  await gotoGuidePage(page, pageUrl(spec.path, view), `${label} ${spec.label} structure`);

  if (expectedAppView !== null) {
    try {
      await page.waitForFunction(
        (expected) => document.documentElement.classList.contains("app-view") === expected,
        expectedAppView,
        { timeout: 5000 }
      );
    } catch {
      // The structure snapshot below reports the actual final state.
    }
  }

  await requireVisible(page.locator(".country-tabs"), `${label} ${spec.label} country tabs`);
  await requireVisible(page.locator("a[href='./czech_honeymoon_guide.html']"), `${label} ${spec.label} czech tab`);
  await requireVisible(page.locator("a[href='./switzerland_honeymoon_guide.html']"), `${label} ${spec.label} swiss tab`);
  await requireVisible(page.locator("a[href='./italy_honeymoon_guide.html']"), `${label} ${spec.label} italy tab`);

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
    const appViewApplied = document.documentElement.classList.contains("app-view");

    return {
      missingSections,
      missingAnchors,
      duplicateIds: Array.from(new Set(duplicateIds)),
      horizontalOverflow,
      manifestHref,
      appViewApplied
    };
  }, spec.requiredSectionIds);

  if (structure.missingSections.length) {
    throw new Error(`${label} ${spec.label} missing sections: ${structure.missingSections.join(", ")}`);
  }
  if (structure.missingAnchors.length) {
    throw new Error(`${label} ${spec.label} missing anchor targets: ${structure.missingAnchors.join(", ")}`);
  }
  if (structure.duplicateIds.length) {
    throw new Error(`${label} ${spec.label} duplicate IDs: ${structure.duplicateIds.join(", ")}`);
  }
  if (!structure.manifestHref) {
    throw new Error(`${label} ${spec.label} manifest link was not found.`);
  }
  if (expectedAppView !== null && structure.appViewApplied !== expectedAppView) {
    throw new Error(`${label} ${spec.label} expected html.app-view to be ${expectedAppView ? "applied" : "absent"}.`);
  }
  if (enforceHorizontalOverflow && structure.horizontalOverflow > horizontalOverflowThreshold) {
    throw new Error(`${label} ${spec.label} horizontal overflow is ${structure.horizontalOverflow}px.`);
  }

  console.log(`Verified ${label} ${spec.label} structure.`);
}

async function verifyPwaOffline(page, context) {
  currentStep = "pwa-offline";
  await gotoGuidePage(page, pageUrl("/index.html", "pwa"), "PWA offline");

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
      "./index.html",
      "./czech_honeymoon_guide.html",
      "./switzerland_honeymoon_guide.html",
      "./italy_honeymoon_guide.html",
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
  if (pwa.manifestName !== "Czechia, Swiss & Italy Honeymoon Guide") {
    throw new Error(`Unexpected manifest name: ${pwa.manifestName}`);
  }
  if (!pwa.activeServiceWorker) {
    throw new Error("Service worker did not become active.");
  }
  if (!pwa.cacheKeys.some((key) => key.startsWith("czech-swiss-italy-honeymoon-guide-"))) {
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
    await page.goto(`${rootUrl}/czech_honeymoon_guide.html?offline=${Date.now()}`, {
      waitUntil: "domcontentloaded",
      timeout: 30000
    });
    await requireVisible(page.locator("#czech-overview"), "offline Czech overview");

    await page.goto(`${rootUrl}/czech_honeymoon_guide.html?offline=${Date.now()}`, {
      waitUntil: "domcontentloaded",
      timeout: 30000
    });
    await requireVisible(page.locator("#czech-return-divider"), "offline Czech return divider");

    await page.goto(`${rootUrl}/switzerland_honeymoon_guide.html?offline=${Date.now()}`, {
      waitUntil: "domcontentloaded",
      timeout: 30000
    });
    await requireVisible(page.locator("#switzerland"), "offline Switzerland guide");

    await page.goto(`${rootUrl}/italy_honeymoon_guide.html?offline=${Date.now()}`, {
      waitUntil: "domcontentloaded",
      timeout: 30000
    });
    await requireVisible(page.locator("#overview"), "offline Italy overview");

    const offlineMapData = await page.evaluate(async () => {
      const response = await fetch("./assets/map-data.json");
      const data = await response.json();
      return {
        ok: response.ok,
        hasDailyMaps: Array.isArray(data.dailyMaps) && data.dailyMaps.length >= 9,
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
  const selector = `[data-route-map-card="${routeId}"] [data-google-route-map-status], [data-route-map-card="${routeId}"] [data-route-map-status]`;
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

  const googlePanel = card.locator("[data-google-route-map-target], [data-route-map-target]");
  await googlePanel.locator(".gm-style").waitFor({ timeout: 90000 });
  await waitForRouteStatus(page, routeId);

  const status = await card.locator("[data-google-route-map-status], [data-route-map-status]").innerText({ timeout: 30000 });
  const routeMeta = await page.evaluate(async (id) => {
    const response = await fetch("./assets/map-data.json", { cache: "no-cache" });
    const data = await response.json();
    const mapConfig = (data.dailyMaps || []).find((item) => item.id === id);
    return {
      hasMapConfig: Boolean(mapConfig),
      routeCount: mapConfig?.routes?.length || 0,
      hasCoordinateRoutes: Boolean(mapConfig?.routes?.some((segment) =>
        segment.useCoordinateRouting ||
        String(segment.mapTravelMode || segment.travelMode || "DRIVING").toUpperCase() !== "DRIVING"
      )),
      usesOfficialCoordinateAxis: Boolean(mapConfig?.officialCoordinateAxis || mapConfig?.useCoordinateRouting)
    };
  }, routeId);
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
  if (!routeMeta.hasMapConfig || !routeMeta.routeCount) {
    throw new Error(`${routeId}: map-data.json route configuration was not found.`);
  }

  if (routeMeta.usesOfficialCoordinateAxis) {
    if (!/공식 시간표로 확인한 교통축/.test(status)) {
      throw new Error(`${routeId}: expected official coordinate transport-axis status. Status: ${status}`);
    }
  } else if (routeMeta.hasCoordinateRoutes) {
    if (!/^최단\/최적 경로|좌표 기반 보조선/.test(status)) {
      throw new Error(`${routeId}: expected clean route or intentional coordinate helper status. Status: ${status}`);
    }
  } else if (!/^최단\/최적 경로/.test(status)) {
    throw new Error(`${routeId}: expected Google Routes API clean route status. Status: ${status}`);
  }

  console.log(`Verified ${routeId} route map.`);
}

async function verifyRouteMaps(page) {
  for (const spec of pageSpecs) {
    currentStep = `route-page-${spec.label}`;
    await gotoGuidePage(page, pageUrl(spec.path, `routes-${spec.label}`), `${spec.label} route maps`);
    for (const routeId of spec.routeIds) {
      await verifyRouteMap(page, routeId);
    }
  }
}

async function verifyMobileGuideMatrix(browser) {
  for (const viewport of mobileGuideViewports) {
    for (const view of mobileGuideViews) {
      const label = `mobile-${viewport.label}-${view}`;
      const context = await browser.newContext({
        viewport: { width: viewport.width, height: viewport.height },
        isMobile: true,
        serviceWorkers: "allow"
      });
      try {
        const page = await context.newPage();
        attachDiagnostics(page);

        await verifyIndex(page, label, view);
        for (const spec of pageSpecs) {
          await verifyGuideStructure(page, spec, label, {
            view,
            expectedAppView: view === "app",
            enforceHorizontalOverflow: true
          });
        }
      } finally {
        await context.close();
      }
    }
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

    await verifyIndex(desktopPage, "desktop");
    for (const spec of pageSpecs) {
      await verifyGuideStructure(desktopPage, spec, "desktop");
    }
    await verifyPwaOffline(desktopPage, desktopContext);
    await verifyRouteMaps(desktopPage);
    await desktopContext.close();

    await verifyMobileGuideMatrix(browser);

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
