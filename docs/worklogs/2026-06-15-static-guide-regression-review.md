# Static guide regression review

Date: 2026-06-15
Mode: harness-engineering Standard

## Scope

- Reviewed the current Czechia, Switzerland, and Italy static guide changes for local runtime errors, PWA/offline regressions, mobile overflow, and deployment smoke-test risk.
- Treated existing dirty files as user work and only changed confirmed issues.

## Findings and fixes

### Offline country-page fallback

- failure: Offline navigation to a country page with a query string could fall back to `index.html`.
- cause: `networkFirstNavigation()` returned the guide fallback before trying to match the requested cached document with `ignoreSearch`.
- fix: `service-worker.js` now checks `caches.match(request, { ignoreSearch: true })` before falling back to `index.html`.
- evidence: CDP verification installed the service worker, confirmed the Czech page was cached, switched offline, opened `/czech_honeymoon_guide.html?offline=...`, and found both `#czech-overview` and `#czech-return-divider`.
- prevention: For PWA navigation tests, include at least one offline country-page URL with a cache-busting query string.

### Blocked Swiss card image

- failure: The local browser reported `net::ERR_BLOCKED_BY_ORB` for the Switzerland card background image.
- cause: The index card used a Wikimedia `Special:FilePath` redirect URL that resolved through a blocked redirect path.
- fix: `index.html` now uses the direct `upload.wikimedia.org` image URL already used by the Switzerland guide.
- evidence: CDP recheck reported no relevant console or network errors after the URL change.
- prevention: Prefer direct static image asset URLs over redirect-style image URLs for first-viewport cards.

### Stale deployment wording

- failure: README still described the deployment smoke as opening "both country pages" after the guide became a three-country selector.
- fix: Updated the wording to "each route-map country page" so it matches the current verifier scope.

### Missing deployed country pages

- failure: The GitHub Pages artifact step copied only `index.html` and redirect/PWA files, so country links could deploy as 404s even though they worked locally.
- cause: The workflow copy list had not been updated for separate Czechia, Switzerland, and Italy HTML pages.
- fix: `.github/workflows/pages.yml` now copies all country HTML pages into `_site`.
- evidence: The workflow diff now includes `czech_honeymoon_guide.html`, `switzerland_honeymoon_guide.html`, and `italy_honeymoon_guide.html` in the Pages artifact copy command.

## Verification

- `node --check service-worker.js`
- `node --check scripts/verify-deployed-guide.mjs`
- JSON parse check for `manifest.webmanifest` and `assets/map-data.json`
- Static HTML anchor/duplicate-id check for `index.html`, `czech_honeymoon_guide.html`, `switzerland_honeymoon_guide.html`, and `italy_honeymoon_guide.html`
- Local Google Maps config procedure:
  - Ran `.\scripts\write-local-google-maps-config.ps1`
  - Verified HTTP config response shape: `200 true routes 990`
- Local CDP browser verification without clicking route-map buttons:
  - Desktop and mobile structure checks passed for index, Czechia, Switzerland, and Italy pages.
  - No missing internal anchors or duplicate IDs.
  - Mobile horizontal overflow was within tolerance.
  - Service worker installed, controlled the page, cached country pages and map data, and served Czechia offline.
  - No relevant console or network errors after the image URL fix.

## Not run

- Full route-map button verification was not run because it triggers live Google Maps/Routes API usage. The local config was verified over HTTP first, but route opening should be run only when API usage is acceptable for the session.
