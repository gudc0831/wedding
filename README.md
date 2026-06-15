# Wedding Guide

스위스·이탈리아 허니문 가이드를 정적 HTML로 배포하기 위한 저장소입니다.

## 주요 파일

- `index.html`: GitHub Pages 루트 주소에서 메인 가이드로 이동하는 진입점
- `milano_honeymoon_guide.html`: 실제 메인 HTML 가이드. 스위스 / 이탈리아 최상위 탭과 각 날짜별 일정, 지도, 체크리스트를 포함합니다.
- `assets/`: SVG 이미지, favicon, 인터랙티브 지도 데이터
- `output/`: PDF, CSV, 브라우저 확인 이미지 등 산출물
- `.github/workflows/pages.yml`: GitHub Pages 자동 배포 workflow

## GitHub Pages 배포

1. 이 저장소를 GitHub에 push합니다.
2. GitHub 저장소의 `Settings` -> `Pages`로 이동합니다.
3. `Build and deployment`의 `Source`를 `GitHub Actions`로 설정합니다.
4. `main` 브랜치에 push하면 workflow가 자동으로 정적 파일을 배포합니다.

배포 주소는 일반적으로 아래 형식입니다.

```text
https://<GitHub아이디>.github.io/wedding/
```

현재 배포 확인 사이트는 아래 URL을 기준으로 합니다.

```text
https://gudc0831.github.io/wedding/milano_honeymoon_guide.html
```

## 로컬 확인

단순 HTML이지만 인터랙티브 지도는 `fetch()`로 `assets/map-data.json`을 읽기 때문에 `file://`로 직접 열면 일부 브라우저에서 차단될 수 있습니다. 로컬에서 전체 동작을 확인할 때는 간단한 정적 서버로 여는 편이 안정적입니다.

```powershell
.\scripts\start-local-server.ps1
```

그다음 브라우저에서 아래 주소를 엽니다.

```text
http://localhost:8000/
```

## Local Google Maps config

The deployed site defaults to `GOOGLE_MAPS_ROUTE_ENGINE=routes`, which uses the Google Maps JavaScript API and Routes API for numbered markers and route lines. `GOOGLE_MAPS_ROUTE_ENGINE=embed` is only a manual fallback mode and should not be used for the production guide unless API-based routing is intentionally disabled.

Do not start the local site with `python -m http.server` directly when testing the route maps. The browser cannot read `.env` by itself, so the local Google Maps config must be generated first.

1. Copy `.env.example` to `.env`.
2. Set `GOOGLE_MAPS_API_KEY`.
3. Start the local site through the wrapper:

```powershell
.\scripts\start-local-server.ps1
```

The wrapper writes `assets/google-maps-config.local.json` from `.env` and then serves `http://localhost:8000/`. If `.env` is missing but an existing `assets/google-maps-config.local.json` already contains an API key, the writer reuses that local JSON as the fallback source instead of replacing it with an empty config. The generated JSON file is ignored by git so the API key is not committed.

If neither `.env` nor the local JSON contains `GOOGLE_MAPS_API_KEY`, the wrapper stops instead of creating a keyless `embed` config. Restore one of those local files before verifying Google route maps in the browser.

## Offline travel mode

The guide registers `service-worker.js` and exposes `manifest.webmanifest` so the main guide can be installed or reopened as an offline-capable PWA after the first successful online visit.

The service worker pre-caches the main HTML, `index.html`, `manifest.webmanifest`, `assets/map-data.json`, and the static map/image assets used by the guide. This keeps the core itinerary, checklist text, source links, place number badges, and static route context available when the network is weak.

The service worker intentionally does not cache `assets/google-maps-config.js` or `assets/google-maps-config.local.json`, because those files may contain deployment or local Google Maps API key material. Google Maps JavaScript API, Routes API, Places enrichment, external images, Google Fonts, and Leaflet CDN assets still require network access. Offline use should therefore rely on the cached document content and static map images, not live Google route maps.

For deployment, keep the API key in GitHub Actions Secrets or Repository Variables as `GOOGLE_MAPS_API_KEY`; do not commit it to `assets/google-maps-config.js`. The key's Google Cloud project must have billing enabled and Maps JavaScript API enabled. Routes API must be enabled for road-following route lines; Places API (New) is optional for marker detail enrichment.

For a restricted Google Maps key, allow these HTTP referrers in Google Cloud Console when testing locally and on GitHub Pages:

```text
http://localhost:8000/*
http://localhost:4000/*
https://gudc0831.github.io/wedding/*
```

If you test with another local port, add that exact `http://localhost:<port>/*` referrer to the same API key before opening route maps.

To verify all route-map cards locally without installing Playwright, run the Chrome DevTools Protocol verifier after the wrapper server is running:

```powershell
$env:LOCAL_URL='http://localhost:8000'; node .\scripts\verify-local-route-maps-cdp.mjs
```

Use `http://localhost:4000` only after that exact referrer is allowed on the Google Maps API key.

Only set `GOOGLE_MAPS_AUTH_REFERRER_POLICY=origin` if the Cloud Console referrer restriction is origin-only, for example `https://gudc0831.github.io/*`. If the restriction includes `/wedding/*`, leave `GOOGLE_MAPS_AUTH_REFERRER_POLICY` blank.

If the Maps JavaScript API account, billing, referrer, or quota settings fail at runtime, the guide shows a configuration error instead of silently replacing the API route map with a non-API iframe. This keeps production verification aligned with the requirement that the deployed guide uses Google APIs for the route maps.

GitHub Pages deployment also runs a browser smoke test after publishing. It opens Day 1, clicks `지도 열기`, and fails the workflow if the page renders an iframe fallback, a Google account/billing overlay, a configuration error, or route fallback text instead of the Maps JavaScript API route map.

Places API (New) is optional but recommended. When it is enabled, clicking a numbered marker can show fresher place details such as address, business status, and Google Maps links. Details are loaded on marker click only so the page does not call Places for every location on initial load.

The site includes browser-side soft limits to avoid accidental repeated usage:

```text
GOOGLE_MAPS_MAP_MONTHLY_LIMIT=990
GOOGLE_MAPS_ROUTE_COMPUTE_MONTHLY_LIMIT=990
GOOGLE_MAPS_PLACES_MONTHLY_LIMIT=990
```

These are convenience guards only. For real billing protection, set matching or lower quota limits in Google Cloud Console for the enabled APIs. Google Cloud quotas apply at the project/API level; the local browser limit cannot see usage from other browsers, devices, or referrers using the same key.
