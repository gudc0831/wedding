import fs from "node:fs/promises";
import path from "node:path";
import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { fileURLToPath, pathToFileURL } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const execFileAsync = promisify(execFile);
const root = path.resolve(__dirname, "..");
const layersDir = path.join(root, "output", "mymaps", "layers");
const assetsDir = path.join(root, "assets");
const outputMapsDir = path.join(root, "output", "maps");
const overridesPath = path.join(outputMapsDir, "geocode-overrides.json");
const cachePath = path.join(outputMapsDir, "geocoded-places.json");
const mapDataPath = path.join(assetsDir, "map-data.json");

const WIDTH = 2400;
const HEIGHT = 1440;
const USER_AGENT = "WeddingGuideMapGenerator/1.0 (local project map asset generation)";

const defaultOverrides = {
  base_una_hotels_century_milano: {
    lat: 45.4844476,
    lon: 9.200165,
    display_name: "UNA HOTELS Century Milano, Via Fabio Filzi 25, Milan, Italy",
    reason: "Nominatim resolves the address more reliably than the hotel brand name"
  },
  base_milano_centrale: {
    lat: 45.4858786,
    lon: 9.2042617,
    display_name: "Milano Centrale, Milan, Italy",
    reason: "OSM station node"
  },
  day2_duomo_di_milano: {
    lat: 45.4641669,
    lon: 9.1916121,
    display_name: "Duomo di Milano, Milan, Italy",
    reason: "OSM relation"
  },
  day2_galleria_vittorio_emanuele_ii: {
    lat: 45.4656113,
    lon: 9.1900062,
    display_name: "Galleria Vittorio Emanuele II, Milan, Italy",
    reason: "OSM pedestrian way"
  },
  day2_rinascente_milano_duomo: {
    lat: 45.4652946,
    lon: 9.1919035,
    display_name: "Rinascente Milano Duomo, Milan, Italy",
    reason: "OSM point inside Rinascente building"
  },
  day3_via_montenapoleone: {
    lat: 45.4685811,
    lon: 9.1948277,
    display_name: "Via Monte Napoleone, Milan, Italy",
    reason: "OSM road centroid"
  },
  day3_quadrilatero_della_moda: {
    lat: 45.46982,
    lon: 9.19488,
    display_name: "Quadrilatero della Moda, Milan, Italy",
    reason: "District centroid for the fashion quarter"
  },
  day2_brera: {
    lat: 45.47195,
    lon: 9.18783,
    display_name: "Brera, Milan, Italy",
    reason: "District centroid"
  },
  day5_bergamo_citta_alta: {
    lat: 45.70442,
    lon: 9.66268,
    display_name: "Citta Alta, Bergamo, Italy",
    reason: "Historic upper town centroid"
  },
  day3_maio_restaurant_terrace: {
    lat: 45.46458,
    lon: 9.19179,
    display_name: "Maio Restaurant & Terrace, Rinascente Milano Duomo, Milan, Italy",
    reason: "Rinascente rooftop location"
  },
  day3_ceresio_7: {
    lat: 45.4835174,
    lon: 9.1803112,
    display_name: "Ceresio 7, Milan, Italy",
    reason: "OSM bar node"
  },
  day4_varenna: {
    lat: 46.0099785,
    lon: 9.2831593,
    display_name: "Varenna, Italy",
    reason: "OSM administrative relation"
  },
  day4_bellagio: {
    lat: 45.9872549,
    lon: 9.2613001,
    display_name: "Bellagio, Italy",
    reason: "OSM administrative relation"
  },
  day6_milan_bergamo_airport: {
    lat: 45.6708936,
    lon: 9.6987542,
    display_name: "Aeroporto internazionale il Caravaggio di Bergamo-Orio al Serio",
    reason: "OSM aerodrome way"
  },
  day6_milan_malpensa_airport: {
    lat: 45.6296273,
    lon: 8.7235475,
    display_name: "Aeroporto internazionale Milano Malpensa - Silvio Berlusconi",
    reason: "OSM aerodrome relation"
  }
};

const maps = [
  {
    id: "basecamp",
    title: "Basecamp Strategy",
    subtitle: "Hotel, Centrale, day trips, and airport exits",
    output: path.join(assetsDir, "basecamp-map.png"),
    points: [
      { key: "base_una_hotels_century_milano", label: "UNA HOTELS", role: "Hotel", color: "#17372f", labelDx: -430, labelDy: -128 },
      { key: "base_milano_centrale", label: "Milano Centrale", role: "Rail hub", color: "#4b635a", labelDx: 42, labelDy: -124 },
      { key: "day2_duomo_di_milano", label: "Duomo", role: "Milan core", color: "#cda16a", labelDx: 42, labelDy: -66 },
      { key: "day4_varenna", label: "Varenna", role: "Lake Como", color: "#78917e", labelDx: 42, labelDy: -78 },
      { key: "day4_bellagio", label: "Bellagio", role: "Lake Como", color: "#78917e", labelDx: 42, labelDy: -24 },
      { key: "day5_bergamo_citta_alta", label: "Bergamo Citta Alta", role: "Day trip", color: "#d6a090" },
      { key: "day6_milan_bergamo_airport", label: "BGY", role: "Airport", color: "#7c8a99" },
      { key: "day6_milan_malpensa_airport", label: "MXP", role: "Airport backup", color: "#7c8a99" }
    ],
    routes: [
      { label: "Milan core", color: "#cda16a", keys: ["base_una_hotels_century_milano", "base_milano_centrale", "day2_duomo_di_milano"] },
      { label: "Lake Como", color: "#78917e", keys: ["base_una_hotels_century_milano", "base_milano_centrale", "day4_varenna", "day4_bellagio"] },
      { label: "Bergamo / BGY", color: "#d6a090", keys: ["base_una_hotels_century_milano", "base_milano_centrale", "day5_bergamo_citta_alta", "day6_milan_bergamo_airport"] },
      { label: "MXP backup", color: "#657fbd", dashArray: "16 18", keys: ["base_una_hotels_century_milano", "base_milano_centrale", "day6_milan_malpensa_airport"] }
    ]
  },
  {
    id: "shopping",
    title: "Birthday Shopping Circuit",
    subtitle: "Duomo start, fashion quarter focus, Brera finish",
    output: path.join(assetsDir, "shopping-map.png"),
    points: [
      { key: "day2_duomo_di_milano", label: "Duomo", role: "Photo start", color: "#d6a090", labelDx: -385, labelDy: 28 },
      { key: "day2_galleria_vittorio_emanuele_ii", label: "Galleria", role: "Arcade", color: "#cda16a", labelDx: -385, labelDy: -32 },
      { key: "day2_rinascente_milano_duomo", label: "Rinascente", role: "Beauty / gifts", color: "#cda16a", labelDx: -385, labelDy: -92 },
      { key: "day3_via_montenapoleone", label: "Via Montenapoleone", role: "Jewelry / luxury", color: "#cda16a", labelDx: 76, labelDy: -32 },
      { key: "day3_quadrilatero_della_moda", label: "Quadrilatero", role: "Fashion district", color: "#cda16a", labelDx: 76, labelDy: -92 },
      { key: "day2_brera", label: "Brera", role: "Small design gifts", color: "#78917e" },
      { key: "day3_maio_restaurant_terrace", label: "Maio", role: "Birthday dinner", color: "#d6a090", labelDx: 76, labelDy: 28 },
      { key: "day3_ceresio_7", label: "Ceresio 7", role: "Dinner backup", color: "#7c8a99" }
    ],
    routes: [
      { label: "Main walking flow", color: "#cda16a", keys: ["day2_duomo_di_milano", "day2_rinascente_milano_duomo", "day2_galleria_vittorio_emanuele_ii", "day3_via_montenapoleone", "day3_quadrilatero_della_moda", "day2_brera"] },
      { label: "Duomo dinner close", color: "#d6a090", keys: ["day2_brera", "day3_maio_restaurant_terrace", "day2_duomo_di_milano"] },
      { label: "Rooftop backup", color: "#657fbd", dashArray: "14 16", keys: ["day2_brera", "day3_ceresio_7"] }
    ]
  }
];

function parseCsv(text) {
  const rows = [];
  let row = [];
  let field = "";
  let quoted = false;

  for (let i = 0; i < text.length; i += 1) {
    const char = text[i];
    const next = text[i + 1];

    if (quoted) {
      if (char === "\"" && next === "\"") {
        field += "\"";
        i += 1;
      } else if (char === "\"") {
        quoted = false;
      } else {
        field += char;
      }
      continue;
    }

    if (char === "\"") {
      quoted = true;
    } else if (char === ",") {
      row.push(field);
      field = "";
    } else if (char === "\n") {
      row.push(field.replace(/\r$/, ""));
      rows.push(row);
      row = [];
      field = "";
    } else {
      field += char;
    }
  }

  if (field.length > 0 || row.length > 0) {
    row.push(field.replace(/\r$/, ""));
    rows.push(row);
  }

  const header = rows.shift().map((key) => key.replace(/^\uFEFF/, "").trim());
  return rows
    .filter((values) => values.some((value) => value.trim() !== ""))
    .map((values) => Object.fromEntries(header.map((key, index) => [key, (values[index] ?? "").trim()])));
}

async function readPlaces() {
  const files = (await fs.readdir(layersDir)).filter((file) => file.endsWith(".csv")).sort();
  const places = new Map();

  for (const file of files) {
    const text = await fs.readFile(path.join(layersDir, file), "utf8");
    for (const row of parseCsv(text)) {
      places.set(row.place_key, row);
    }
  }

  return places;
}

async function readJson(filePath, fallback) {
  try {
    return JSON.parse(await fs.readFile(filePath, "utf8"));
  } catch (error) {
    if (error.code === "ENOENT") return fallback;
    throw error;
  }
}

function collectTargetKeys() {
  return [...new Set(maps.flatMap((map) => map.points.map((point) => point.key)))];
}

async function geocodePlace(place, overrides, cache) {
  const cached = cache.places?.[place.place_key];
  if (cached?.lat && cached?.lon) return cached;

  const override = overrides[place.place_key];
  if (override?.lat && override?.lon) {
    return {
      place_key: place.place_key,
      query: place.query,
      name: place.name,
      category_ko: place.category_ko,
      lat: Number(override.lat),
      lon: Number(override.lon),
      display_name: override.display_name ?? place.query,
      source: "override",
      resolved_at: new Date().toISOString()
    };
  }

  const url = new URL("https://nominatim.openstreetmap.org/search");
  url.searchParams.set("format", "jsonv2");
  url.searchParams.set("limit", "1");
  url.searchParams.set("q", place.query);

  const response = await fetch(url, {
    headers: {
      "User-Agent": USER_AGENT,
      "Accept-Language": "en"
    }
  });

  if (!response.ok) {
    throw new Error(`Nominatim failed for ${place.place_key}: HTTP ${response.status}`);
  }

  const results = await response.json();
  const result = results[0];
  if (!result?.lat || !result?.lon) {
    throw new Error(`No geocode result for ${place.place_key} (${place.query})`);
  }

  await new Promise((resolve) => setTimeout(resolve, 1100));

  return {
    place_key: place.place_key,
    query: place.query,
    name: place.name,
    category_ko: place.category_ko,
    lat: Number(result.lat),
    lon: Number(result.lon),
    display_name: result.display_name,
    osm_type: result.osm_type,
    osm_id: result.osm_id,
    source: "nominatim",
    resolved_at: new Date().toISOString()
  };
}

function buildMapData(places, resolvedPlaces) {
  const byKey = new Map(resolvedPlaces.map((place) => [place.place_key, place]));
  return {
    generated_at: new Date().toISOString(),
    source: "output/mymaps/layers/*.csv",
    tile_attribution: "OpenStreetMap contributors",
    maps: maps.map((map) => ({
      id: map.id,
      title: map.title,
      subtitle: map.subtitle,
      points: map.points.map((point, index) => {
        const place = places.get(point.key);
        const resolved = byKey.get(point.key);
        return {
          place_key: point.key,
          label: point.label,
          role: point.role,
          color: point.color,
          label_dx: point.labelDx ?? null,
          label_dy: point.labelDy ?? null,
          visit_order: place?.visit_order || String(index + 1),
          query: place?.query,
          category_ko: place?.category_ko,
          short_desc_ko: place?.short_desc_ko,
          lat: resolved.lat,
          lon: resolved.lon
        };
      }),
      routes: map.routes
    }))
  };
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll("\"", "&quot;");
}

function mercatorPoint(lat, lon, zoom) {
  const scale = 256 * 2 ** zoom;
  const sinLat = Math.sin((lat * Math.PI) / 180);
  return {
    x: ((lon + 180) / 360) * scale,
    y: (0.5 - Math.log((1 + sinLat) / (1 - sinLat)) / (4 * Math.PI)) * scale
  };
}

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function chooseZoom(points, mapId) {
  const maxZoom = mapId === "shopping" ? 17 : 12;
  const minZoom = mapId === "shopping" ? 13 : 7;
  const usableWidth = WIDTH - 340;
  const usableHeight = HEIGHT - 320;

  for (let zoom = maxZoom; zoom >= minZoom; zoom -= 1) {
    const projected = points.map((point) => mercatorPoint(point.lat, point.lon, zoom));
    const xs = projected.map((point) => point.x);
    const ys = projected.map((point) => point.y);
    if (Math.max(...xs) - Math.min(...xs) <= usableWidth && Math.max(...ys) - Math.min(...ys) <= usableHeight) {
      return zoom;
    }
  }

  return minZoom;
}

function buildStaticLayout(mapConfig) {
  const zoom = chooseZoom(mapConfig.points, mapConfig.id);
  const projected = mapConfig.points.map((point) => ({ ...point, world: mercatorPoint(point.lat, point.lon, zoom) }));
  const xs = projected.map((point) => point.world.x);
  const ys = projected.map((point) => point.world.y);
  const bounds = {
    minX: Math.min(...xs),
    maxX: Math.max(...xs),
    minY: Math.min(...ys),
    maxY: Math.max(...ys)
  };
  const center = {
    x: (bounds.minX + bounds.maxX) / 2,
    y: (bounds.minY + bounds.maxY) / 2
  };
  const topLeft = {
    x: center.x - WIDTH / 2,
    y: center.y - HEIGHT / 2
  };
  const points = projected.map((point) => ({
    ...point,
    x: point.world.x - topLeft.x,
    y: point.world.y - topLeft.y
  }));
  const tileMinX = Math.floor(topLeft.x / 256) - 1;
  const tileMaxX = Math.floor((topLeft.x + WIDTH) / 256) + 1;
  const tileMinY = Math.floor(topLeft.y / 256) - 1;
  const tileMaxY = Math.floor((topLeft.y + HEIGHT) / 256) + 1;
  const tileCount = 2 ** zoom;
  const tiles = [];

  for (let x = tileMinX; x <= tileMaxX; x += 1) {
    for (let y = tileMinY; y <= tileMaxY; y += 1) {
      if (y < 0 || y >= tileCount) continue;
      const wrappedX = ((x % tileCount) + tileCount) % tileCount;
      const subdomain = ["a", "b", "c", "d"][Math.abs(x + y) % 4];
      tiles.push({
        x,
        y,
        left: Math.round(x * 256 - topLeft.x),
        top: Math.round(y * 256 - topLeft.y),
        src: `https://${subdomain}.basemaps.cartocdn.com/rastertiles/voyager/${zoom}/${wrappedX}/${y}.png`
      });
    }
  }

  return { zoom, topLeft, points, tiles };
}

function renderLabel(point) {
  const labelWidth = clamp(point.label.length * 18 + 46, 138, 390);
  const labelHeight = 46;
  const nearRight = point.x > WIDTH * 0.68;
  const nearBottom = point.y > HEIGHT * 0.72;
  const x = clamp(
    point.label_dx === null ? (nearRight ? point.x - labelWidth - 30 : point.x + 30) : point.x + point.label_dx,
    34,
    WIDTH - labelWidth - 34
  );
  const y = clamp(
    point.label_dy === null ? (nearBottom ? point.y - 76 : point.y - 34) : point.y + point.label_dy,
    34,
    HEIGHT - labelHeight - 34
  );

  return `
    <rect x="${x}" y="${y}" width="${labelWidth}" height="${labelHeight}" rx="23" fill="rgba(255,250,241,0.94)" stroke="rgba(23,55,47,0.18)" />
    <text x="${x + 20}" y="${y + 30}" fill="#17372f" font-size="22" font-weight="800">${escapeHtml(point.label)}</text>`;
}

function renderHtml(mapConfig) {
  const layout = buildStaticLayout(mapConfig);
  const pointByKey = new Map(layout.points.map((point) => [point.place_key, point]));
  const tileHtml = layout.tiles
    .map((tile) => `<img src="${tile.src}" style="left:${tile.left}px;top:${tile.top}px" alt="">`)
    .join("");
  const routeHtml = mapConfig.routes
    .map((route) => {
      const points = route.keys
        .map((key) => pointByKey.get(key))
        .filter(Boolean)
        .map((point) => `${point.x.toFixed(1)},${point.y.toFixed(1)}`)
        .join(" ");
      return `<polyline points="${points}" fill="none" stroke="${route.color}" stroke-width="12" stroke-linecap="round" stroke-linejoin="round" stroke-opacity="0.9" ${route.dashArray ? `stroke-dasharray="${route.dashArray}"` : ""} />`;
    })
    .join("");
  const labelHtml = layout.points.map(renderLabel).join("");
  const markerHtml = layout.points
    .map((point, index) => `
      <circle cx="${point.x}" cy="${point.y}" r="27" fill="${point.color}" stroke="#fffaf3" stroke-width="7" />
      <text x="${point.x}" y="${point.y + 8}" text-anchor="middle" fill="#fffaf3" font-size="22" font-weight="900">${index + 1}</text>`)
    .join("");

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=${WIDTH}, initial-scale=1">
  <style>
    html, body { width: ${WIDTH}px; height: ${HEIGHT}px; margin: 0; }
    body { background: #f7f2e8; font-family: "Noto Sans KR", "Segoe UI", sans-serif; overflow: hidden; }
    .map-root { position: relative; width: ${WIDTH}px; height: ${HEIGHT}px; background: #eef0e9; overflow: hidden; }
    .tile-layer { position: absolute; inset: 0; filter: saturate(0.72) contrast(0.94) brightness(1.04); opacity: 0.9; }
    .tile-layer img { position: absolute; width: 256px; height: 256px; }
    .wash { position: absolute; inset: 0; background: rgba(247, 242, 232, 0.22); }
    svg { position: absolute; inset: 0; width: ${WIDTH}px; height: ${HEIGHT}px; }
    text { font-family: "Noto Sans KR", "Segoe UI", sans-serif; letter-spacing: 0; }
    .map-title {
      position: absolute;
      z-index: 3;
      top: 64px;
      left: 72px;
      max-width: 930px;
      padding: 26px 32px;
      border-radius: 28px;
      color: #fff8f0;
      background: rgba(23, 55, 47, 0.93);
      box-shadow: 0 24px 70px rgba(23, 55, 47, 0.26);
    }
    .map-title h1 { margin: 0 0 10px; font-size: 54px; line-height: 1; }
    .map-title p { margin: 0; font-size: 24px; color: rgba(255, 248, 240, 0.84); }
    .map-legend {
      position: absolute;
      z-index: 3;
      right: 72px;
      bottom: 64px;
      display: grid;
      gap: 12px;
      min-width: 360px;
      padding: 24px 28px;
      border-radius: 26px;
      color: #17372f;
      background: rgba(255, 250, 241, 0.94);
      box-shadow: 0 24px 70px rgba(23, 55, 47, 0.18);
    }
    .legend-row { display: flex; align-items: center; gap: 14px; font-size: 22px; font-weight: 700; }
    .legend-swatch { width: 42px; height: 8px; border-radius: 99px; flex: none; }
    .attribution {
      position: absolute;
      right: 24px;
      top: 22px;
      z-index: 3;
      padding: 6px 10px;
      border-radius: 999px;
      color: rgba(23, 55, 47, 0.78);
      background: rgba(255, 250, 241, 0.78);
      font-size: 14px;
    }
    .map-ready { position: absolute; left: 0; top: 0; width: 1px; height: 1px; opacity: 0; }
  </style>
</head>
<body>
  <div class="map-root">
    <div class="tile-layer">${tileHtml}</div>
    <div class="wash"></div>
    <svg viewBox="0 0 ${WIDTH} ${HEIGHT}" role="img" aria-label="${escapeHtml(mapConfig.title)}">
      <rect x="34" y="34" width="${WIDTH - 68}" height="${HEIGHT - 68}" rx="34" fill="none" stroke="rgba(23,55,47,0.18)" stroke-width="3" />
      ${routeHtml}
      ${labelHtml}
      ${markerHtml}
    </svg>
    <div class="map-title">
      <h1>${escapeHtml(mapConfig.title)}</h1>
      <p>${escapeHtml(mapConfig.subtitle)}</p>
    </div>
    <div class="map-legend">
      ${mapConfig.routes.map((route) => `<div class="legend-row"><span class="legend-swatch" style="background:${route.color}"></span>${escapeHtml(route.label)}</div>`).join("")}
    </div>
    <div class="attribution">Tiles © CARTO · Map data © OpenStreetMap contributors · z${layout.zoom}</div>
    <div class="map-ready"></div>
  </div>
</body>
</html>`;
}

async function renderPngs(mapData) {
  const runner = process.platform === "win32" ? "cmd.exe" : "npx";

  for (const mapConfig of mapData.maps) {
    const tempHtml = path.join(outputMapsDir, `${mapConfig.id}-render.html`);
    const output = maps.find((map) => map.id === mapConfig.id).output;
    await fs.writeFile(tempHtml, renderHtml(mapConfig), "utf8");
    const playwrightArgs = [
      "--yes",
      "playwright",
      "screenshot",
      "--browser",
      "chromium",
      "--timeout",
      "45000",
      "--viewport-size",
      `${WIDTH},${HEIGHT}`,
      "--wait-for-selector",
      ".map-ready",
      "--wait-for-timeout",
      "8000",
      pathToFileURL(tempHtml).href,
      output
    ];
    const args = process.platform === "win32" ? ["/d", "/s", "/c", "npx", ...playwrightArgs] : playwrightArgs;

    try {
      await execFileAsync(
        runner,
        args,
        { cwd: root, maxBuffer: 1024 * 1024 * 4 }
      );
      console.log(`Wrote ${path.relative(root, output)} (${WIDTH}x${HEIGHT})`);
    } finally {
      await fs.unlink(tempHtml).catch(() => {});
    }
  }
}

async function main() {
  await fs.mkdir(outputMapsDir, { recursive: true });
  await fs.mkdir(assetsDir, { recursive: true });

  const places = await readPlaces();
  const existingOverrides = await readJson(overridesPath, {});
  const overrides = { ...defaultOverrides, ...existingOverrides };
  await fs.writeFile(overridesPath, `${JSON.stringify(overrides, null, 2)}\n`, "utf8");

  const cache = await readJson(cachePath, { generated_at: null, places: {} });
  cache.places ??= {};

  const resolvedPlaces = [];
  for (const key of collectTargetKeys()) {
    const place = places.get(key);
    if (!place) throw new Error(`Missing place_key in CSV layers: ${key}`);
    const resolved = await geocodePlace(place, overrides, cache);
    cache.places[key] = resolved;
    resolvedPlaces.push(resolved);
  }

  cache.generated_at = new Date().toISOString();
  await fs.writeFile(cachePath, `${JSON.stringify(cache, null, 2)}\n`, "utf8");

  const mapData = buildMapData(places, resolvedPlaces);
  await fs.writeFile(mapDataPath, `${JSON.stringify(mapData, null, 2)}\n`, "utf8");
  console.log(`Wrote ${path.relative(root, mapDataPath)}`);
  console.log(`Wrote ${path.relative(root, cachePath)}`);
  console.log(`Wrote ${path.relative(root, overridesPath)}`);

  await renderPngs(mapData);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
