# 2026-06-15 Swiss / Italy Tabs Worklog

## Scope

- Split the guide into independent `스위스` and `이탈리아` pages with top-level navigation between them.
- Add the Switzerland itinerary for 2026-07-16 through 2026-07-18 from `C:/Users/hcchoi/Downloads/swiss_lucerne_interlaken.md`.
- Keep the Switzerland section visually consistent with the existing Italy day-card, timeline, aside-card, food-list, and route-map patterns.
- Represent Switzerland route maps as official transport axes for boats, cogwheel rail, cable car, and panorama train instead of generic Google-calculated transit paths.
- Keep `index.html` as a country selector and `milano_honeymoon_guide.html` as a compatibility redirect.

## Harness Mode

- Mode: Standard
- Coordinator: choi
- Worker ownership:
  - HTML/content: `milano_honeymoon_guide.html`
  - Route data: `assets/map-data.json`
  - Cache/docs entry points: `service-worker.js`, `index.html`, `README.md`
- Reviewer checks planned:
  - Product: country tabs answer the requested top-level structure.
  - Engineering: map-data IDs match route-map cards and JSON parses.
  - Design: Swiss section reuses existing Italy visual components and does not introduce a separate style system.

## Official Time Evidence

- Lake Lucerne Navigation summer timetable 2026:
  - Luzern to Vitznau: 09:12 to 10:09.
  - Weggis to Luzern: 17:05 to 17:47, with 16:05 and 18:05 alternatives.
  - Pier guidance: departures to Weggis and Vitznau use Pier 1.
- Rigi timetables 2026:
  - Vitznau to Rigi Kulm: 10:15 to 10:47.
  - Weggis to Rigi Kaltbad cable car: every 30 minutes, 10 minutes travel time.
- Zentralbahn Luzern-Interlaken Express:
  - Luzern to Interlaken Ost every hour from 06:06 to 21:06.
  - Journey time: 1 hour 50 minutes.
  - 09:06 to 10:56 plan is consistent.
  - Right-hand seats are recommended from Luzern toward Interlaken.
  - 2026 summer reservation fee is CHF 16.
- SBB Swiss Half Fare Card:
  - Discount/reduced fare applies to train, bus, boat, panorama trains, mountain railways, and gondola lifts.

## Decisions

- Day numbering remains scoped by country:
  - Swiss Day 1-3 for 2026-07-16 to 2026-07-18.
  - Existing Italy Day 1-6 remains unchanged for 2026-07-21 to 2026-07-26.
- Page ownership:
  - `switzerland_honeymoon_guide.html` renders only the Switzerland itinerary and Swiss route maps.
  - `italy_honeymoon_guide.html` renders only the Italy itinerary and Italy route maps.
  - `assets/map-data.json` remains shared to avoid unnecessary data duplication.
- Day 3 Switzerland now follows the paid transport already booked by the user:
  - Luzern PL15 09:24 to Interlaken Ost 11:17.
  - Interlaken Ost PL8 11:29 to Interlaken West PL1 11:32.
  - The final Airbnb leg remains pending until the exact address is provided.
- Special transport map segments use `useCoordinateRouting: true`, so the guide shows the planned transport axis rather than a potentially misleading Google route calculation.

## Verification Plan

- Parse `assets/map-data.json`.
- Confirm each Swiss `data-route-map-card` has a matching `dailyMaps` entry.
- Start local server through `scripts/start-local-server.ps1`.
- Before browser map testing, verify `assets/google-maps-config.local.json` over HTTP per `AGENTS.md`.
- Browser check:
  - Country tabs appear.
  - Switzerland section renders before Italy.
  - Swiss route-map buttons open.
  - Italy content remains accessible and visually consistent.

## Verification Results

- Static map-data check: passed.
  - `assets/map-data.json` parses as JSON.
  - Swiss route-map cards `swiss-day1`, `swiss-day2`, and `swiss-day3` all have matching `dailyMaps` entries.
  - Switzerland maps contain 9 `useCoordinateRouting` route segments for official transport-axis rendering.
- Diff hygiene: `git diff --check` passed.
- Local Google Maps browser verification: passed after `.env` was restored locally.
  - `scripts/write-local-google-maps-config.ps1` generated `assets/google-maps-config.local.json`.
  - HTTP config verification returned the expected shape: `200 true routes 990`.
  - `node scripts/verify-local-route-maps-cdp.mjs` passed on `http://localhost:8000`.
  - The same verifier passed with `LOCAL_URL=http://localhost:4000`.
  - All 9 route-map cards rendered Google Maps without iframe fallback, route-map error UI, or Google account overlay.
