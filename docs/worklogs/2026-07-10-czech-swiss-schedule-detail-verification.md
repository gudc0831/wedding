# Czech·Swiss schedule-detail verification — 2026-07-10

## Scope

Runtime implementation range: `374a5e0..ed7e80b`

Verification tooling and persisted evidence range: `ed7e80b..faf5b1c`

Primary changed runtime files:

- `czech_honeymoon_guide.html`
- `switzerland_honeymoon_guide.html`
- `assets/schedule-detail.js`
- `service-worker.js`
- `scripts/validate-schedule-details.mjs`

`assets/map-data.json` was audited but not changed because the itinerary places, route order, and map semantics did not change.

## Static content validation

Command:

```powershell
node scripts/validate-schedule-details.mjs
```

Fresh result after integration:

| Guide | Events | Valid detail | Missing | Invalid segments |
|---|---:|---:|---:|---:|
| Czech | 46 | 46 | 0 | 0 |
| Switzerland | 39 | 39 | 0 | 0 |

The command printed `SCHEDULE_DETAIL_VALIDATION_PASS` and exited `0`.

The validator checks the complete forbidden-token set `엑셀|Excel|스프레드시트|가져왔` in the Czech and Swiss guide content. A separate `rg` check returned no matches in those two HTML files.

All three country pages retained exactly one `data-view-toggle`, `html.app-view`, `honeymoonGuideView`, and one `assets/schedule-detail.js` reference.

## 07.16 Prague airport correction

The previous Czech calendar showed `호텔→PRG 공항` at `08:00 전후`, while the supplied itinerary image and both Czech and Swiss narratives require arrival at Prague Airport by `07:00` before LX1485 at 09:30.

The stale calendar row now shows:

- preparation: `출발 전`
- airport transfer/arrival: `07:00까지 도착`
- flight: `09:30-10:55 LX1485`

A post-change search found no stale `08:00 전후` associated with Prague Airport. The only remaining `08:00 전후` is the unrelated Jungfraujoch terminal arrival in the Swiss guide. `assets/map-data.json` contains the Zurich arrival and onward Lucerne route but no stale Prague hotel-to-airport time.

## Schedule-detail race diagnosis and fix

Original Playwright reproduction opened a calendar detail and immediately pressed Escape. Five of five runs ended with a hidden layer that still had `is-open`, and focus did not return. The stale class could intercept the next calendar click.

The shared module now cancels a pending opening animation frame and closing timer before a new state transition. It also verifies that the same event is still active before adding `is-open`.

Fresh regression results:

- immediate open → Escape: 5/5 closed, no stale `is-open`, body lock removed, focus returned
- Czech and Swiss event types `transit`, `tour`, `food`, `stay`, `prep`: non-empty title and summary, at least two detail lines, Escape focus return
- Enter → close button → focus return: passed for Czech and Swiss
- Space → fully opened backdrop click → focus return: Czech 3/3 and Swiss 3/3

## Web/app mobile matrix

Command:

```powershell
node scripts/verify-guide-app-web-ui-cdp.mjs
```

The final run covered Czech, Switzerland, and Italy at `393×852` and `402×874` in both `?view=web` and `?view=app`: 12 combinations.

Final result:

- document overflow: 0 for every combination
- timeline overflow: 0
- clipped captions: 0
- untappable route-map buttons: 0
- web/app canonical text hashes matched per country
- all six toggle-persistence cases passed
- `failures: []`

## Local Google Maps and route maps

The local config was regenerated through `scripts/write-local-google-maps-config.ps1` and verified through HTTP without printing the key:

```text
CONFIG_HTTP=200
HAS_API_KEY=True
ROUTE_ENGINE=routes
MONTHLY_LIMIT=990
```

Command:

```powershell
node scripts/verify-local-route-maps-cdp.mjs
```

Final result:

- Czech: 7/7
- Switzerland: 6/6
- Italy: 7/7
- total: 20/20
- every map: `gmStyle=true`, `hasError=false`, `hasIframe=false`, `hasAccountOverlay=false`
- relevant browser logs: empty

The verifier left one temporary Chrome profile because of an initial Windows `EPERM`; the exact profile directory was subsequently removed after the browser exited.

## Syntax and repository checks

The following completed with exit code `0`:

```powershell
node --check scripts/validate-schedule-details.mjs
node --check assets/schedule-detail.js
node --check service-worker.js
git diff --check
```

The final cache version is:

```text
czech-swiss-italy-honeymoon-guide-v20260710-schedule-detail-race-fix
```

## Remaining source-workbook evidence gap

`C:\Users\hcchoi\Desktop\🤵👰신혼여행.xlsx` exists and is 79,811 bytes. The required bundled `@oai/artifact-tool` loads, but `SpreadsheetFile.importXlsx` stops with:

```text
Person displayName is required.
```

The exact help query returned no import option, and the single allowed reformulation returned unrelated chart APIs. No alternate spreadsheet library was used. A comment-free copy or corrected comment/person metadata is still required for a fresh cell-by-cell workbook comparison.
