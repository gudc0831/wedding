# Wedding Guide

밀라노 허니문 가이드를 정적 HTML로 배포하기 위한 저장소입니다.

## 주요 파일

- `index.html`: GitHub Pages 루트 주소에서 메인 가이드로 이동하는 진입점
- `milano_honeymoon_guide.html`: 실제 메인 HTML 가이드
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

Do not start the local site with `python -m http.server` directly when testing the route maps. The browser cannot read `.env` by itself, so the local Google Maps config must be generated first.

1. Copy `.env.example` to `.env`.
2. Set `GOOGLE_MAPS_API_KEY`.
3. Start the local site through the wrapper:

```powershell
.\scripts\start-local-server.ps1
```

The wrapper writes `assets/google-maps-config.local.json` from `.env` and then serves `http://localhost:8000/`. That generated JSON file is ignored by git so the API key is not committed.

For a restricted Google Maps key, allow these HTTP referrers in Google Cloud Console when testing locally:

```text
http://localhost:8000/*
```

The key also needs Maps JavaScript API enabled. Routes API should be enabled for road-following routes; if Routes is unavailable, the guide keeps the Google basemap and numbered markers visible and falls back to coordinate-based route lines.

Places API (New) is optional but recommended. When it is enabled, clicking a numbered marker can show fresher place details such as address, business status, and Google Maps links. Details are loaded on marker click only so the page does not call Places for every location on initial load.

The site includes browser-side soft limits to avoid accidental repeated usage:

```text
GOOGLE_MAPS_MAP_MONTHLY_LIMIT=990
GOOGLE_MAPS_ROUTE_COMPUTE_MONTHLY_LIMIT=990
GOOGLE_MAPS_PLACES_MONTHLY_LIMIT=990
```

These are convenience guards only. For real billing protection, set matching or lower quota limits in Google Cloud Console for the enabled APIs. Google Cloud quotas apply at the project/API level; the local browser limit cannot see usage from other browsers, devices, or referrers using the same key.
