import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import path from "node:path";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(scriptDir, "..");
const dataPath = path.join(root, "assets", "milan-restaurant-map-data.json");
const htmlPath = path.join(root, "italy_honeymoon_guide.html");
const serviceWorkerPath = path.join(root, "service-worker.js");

const [rawData, html, serviceWorker] = await Promise.all([
  readFile(dataPath, "utf8"),
  readFile(htmlPath, "utf8"),
  readFile(serviceWorkerPath, "utf8")
]);

const data = JSON.parse(rawData);
const restaurants = data.restaurants || [];
const regions = data.regions || [];
const allowedCities = new Set(["Milano", "Varenna"]);
const removedRestaurantPattern = /tiello|lomilan/i;
const removedPlacePattern = /\b(?:venezia|venice|firenze|florence|roma|rome|polignano|capri)\b/i;

assert.equal(data.summary?.total, 35, "summary.total must be 35");
assert.equal(data.summary?.milan, 34, "summary.milan must be 34");
assert.equal(data.summary?.lakeComo, 1, "summary.lakeComo must be 1");
assert.equal(restaurants.length, 35, "restaurant list must contain 35 places");
assert.equal(regions.length, 8, "region list must contain 8 groups");
assert.equal(restaurants.filter((place) => place.city === "Milano").length, 34, "Milano count must be 34");
assert.equal(restaurants.filter((place) => place.city === "Varenna").length, 1, "Varenna/Lake Como count must be 1");

assert.equal(new Set(restaurants.map((place) => place.id)).size, restaurants.length, "restaurant ids must be unique");
assert.equal(new Set(restaurants.map((place) => place.number)).size, restaurants.length, "restaurant numbers must be unique");
assert.equal(new Set(regions.map((region) => region.id)).size, regions.length, "region ids must be unique");
assert.equal(new Set(regions.map((region) => region.code)).size, regions.length, "region codes must be unique");

const regionById = new Map(regions.map((region) => [region.id, region]));
for (const place of restaurants) {
  const region = regionById.get(place.region);
  assert.ok(region, `${place.name}: unknown region ${place.region}`);
  assert.ok(place.number.startsWith(`${region.code}-`), `${place.name}: number must use ${region.code} prefix`);
  assert.ok(allowedCities.has(place.city), `${place.name}: disallowed city ${place.city}`);
  assert.ok(!removedRestaurantPattern.test(place.name), `${place.name}: removed closure-risk candidate is present`);
  assert.ok(!removedPlacePattern.test(`${place.city} ${place.address}`), `${place.name}: excluded destination is present`);
  assert.ok(Number.isFinite(place.lat) && place.lat >= 45 && place.lat <= 47, `${place.name}: invalid latitude`);
  assert.ok(Number.isFinite(place.lng) && place.lng >= 8 && place.lng <= 10, `${place.name}: invalid longitude`);
  assert.ok(place.address && place.mapsQuery, `${place.name}: address and mapsQuery are required`);
}

const restaurantSectionIndex = html.indexOf('<section id="restaurant-map">');
const excelSectionIndex = html.indexOf('<section id="italy-excel-schedule">');
assert.ok(restaurantSectionIndex >= 0, "restaurant-map section is missing");
assert.ok(excelSectionIndex >= 0, "italy-excel-schedule section is missing");
assert.ok(restaurantSectionIndex < excelSectionIndex, "restaurant map must appear before the Excel schedule");
assert.ok(html.includes('<a href="#restaurant-map">음식점 지도</a>'), "restaurant map navigation link is missing");
assert.ok(html.includes('fetch("./assets/milan-restaurant-map-data.json"'), "restaurant map data fetch is missing");
assert.ok(html.includes("data-restaurant-region-filters"), "region filters are missing");
assert.ok(html.includes("data-restaurant-map-list"), "restaurant list host is missing");
assert.ok(serviceWorker.includes('"./assets/milan-restaurant-map-data.json"'), "restaurant data is not pre-cached");

const inlineScripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map((match) => match[1]);
for (const [index, source] of inlineScripts.entries()) {
  try {
    new Function(source);
  } catch (error) {
    throw new Error(`inline script ${index + 1} has invalid JavaScript: ${error.message}`);
  }
}

console.log("PASS Milan restaurant atlas validation");
console.log(`  restaurants=${restaurants.length} regions=${regions.length} Milano=34 Varenna=1`);
console.log("  excluded destinations and closure-risk candidates are absent");
console.log("  section order, navigation, JavaScript syntax, and offline precache are valid");
