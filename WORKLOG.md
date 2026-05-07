# Worklog

## 2026-04-30

- `https://github.com/gudc0831/wedding` 저장소를 `D:\wedding`에 clone하고 `main` 브랜치를 최신 상태로 pull했다.
- GitHub Pages 배포를 위해 루트 진입점 `index.html`을 추가했다.
- GitHub Pages 자동 배포용 workflow `.github/workflows/pages.yml`을 추가했다.
- GitHub Pages에서 Jekyll 처리를 피하기 위해 `.nojekyll`을 추가했다.
- `milano_honeymoon_guide.html`에서 존재하지 않는 `basecamp-map.png`, `shopping-map.png` 참조를 실제 파일인 `basecamp-map.svg`, `shopping-map.svg`로 수정했다.
- 인터랙티브 지도 버튼이 사용할 `assets/map-data.json`을 추가했다.
- 배포 방법과 주요 파일 구성을 `README.md`에 정리했다.
- `assets/map-data.json` UTF-8 JSON 파싱과 HTML의 로컬 asset 참조 존재 여부를 확인했다.
- 브라우저 주석 반영: 히어로 제목을 `이탈리아 여행`, Overview 제목을 `일정개요`, Hotel Base 제목을 `호텔개요`로 수정했다.
- `BGY Early Morning` 표기에 `베르가모 공항 새벽 출발` 한국어 설명을 괄호로 추가했다.
- UNA HOTELS 공식 페이지 기준 호텔 서비스(조식, 무료 Wi-Fi, 컨시어지, 택시, 세탁, 바/레스토랑, 제휴 주차장, Rinascente Shopping Experience, Caricami 등)를 호텔 섹션에 반영했다.
- 추상형 베이스캠프 지도를 실제 지도와 비슷한 OSM 스타일의 도로/수역/경로 배경 SVG로 교체했다.
- 전체 레이아웃의 폰트, 여백, 카드 간격, 모바일 내비게이션 크기를 줄여 화면 밀도를 높였다.
- 웹 검색으로 교통/식당/운영시간을 재검토했다. ATM 밀라노 티켓, Trenord 바렌나/베르가모 요금, Orioshuttle BGY 셔틀, Duomo 2026 여름 특별 오픈, Navigazione Laghi 꼬모 페리, Pavé, Ratanà, N'Ombra de Vin, Maio, Ceresio 7, Bellagio Restaurant & Bar, La Pergola, Caffè del Tasso, Il Circolino, Da Mimmo를 확인했다.
- 확인 결과를 `milano_honeymoon_guide.html`에 반영했다. BGY→PRG 항공편은 2026-07-26 일요일 06:35→08:00 기준으로 정리했고, Ratanà/마이오/Ceresio 7/Caffè del Tasso/Bellagio/La Pergola/Il Circolino/Da Mimmo 관련 시간과 가격 문구를 최신 공개 정보 기준으로 조정했다.
- Navigazione Laghi는 2026-04-30 확인 시점에 Lake Como 시간표가 2026-05-31까지 중심으로 공개되어 있어, 2026-07-24 바렌나-벨라지오 배편은 공식 시간표와 요금을 예약 직전 다시 확인하도록 문구를 수정했다.
- 브라우저 주석 1-16을 반영해 히어로와 Practical Info 여백을 축소하고, 섹션 제목 폰트를 본문 UI와 맞췄다.
- Overview의 `여행 템포`, `환율 기준`, `표기 원칙` 설명과 호텔 지도 하단 설명을 삭제했다.
- City Tax에 원화 환산을 병기하고, Day 1 제목을 `밀라노 첫날`로 줄였으며, Day 1 추천 톤 제목과 긴 저녁 설명을 정리했다.
- 모든 Food Picks 카드에 장소 유형 배지와 작은 주소 줄을 추가하고, 식당 설명 본문 폰트를 줄였다.
- 상단 페이지 이동 영역을 세로 내부 스크롤 방식으로 다시 조정했다. 내비게이션 칩은 여러 줄로 감싸고, 제한 높이 안에서 위아래로 스크롤되도록 `overflow-y: auto`와 얇은 스크롤바를 적용했다.

## 2026-05-07

- Day 1-6 실제 동선 지도는 `milano_honeymoon_guide.html`의 `data-route-map-card="day1"`-`"day6"` 카드와 `assets/map-data.json`의 `dailyMaps` 데이터로 이미 구현되어 있었다.
- 이전에 "구현이 안 된 것처럼" 보였던 핵심 원인은 Google Maps API 키 설정이었다. 저장소의 `assets/google-maps-config.js`는 기본값이 `apiKey: ""`라서, 로컬이나 배포 환경에 키가 없으면 `openRouteMap()`이 `missing-google-maps-key`에서 중단되고 Google Maps JavaScript API와 Routes API를 로드하지 않는다.
- GitHub Pages 배포는 `.github/workflows/pages.yml`에서 `GOOGLE_MAPS_API_KEY` Secret이 있을 때만 `assets/google-maps-config.js`를 덮어쓴다. 따라서 Secret이 비어 있거나 삭제되면 코드가 있어도 배포본에서는 지도가 열리지 않는다.
- 재발 방지 체크: 지도 관련 작업 후에는 `assets/google-maps-config.js` 또는 배포 Secret에 키가 설정된 상태인지 먼저 확인하고, `http://127.0.0.1:8000/milano_honeymoon_guide.html`에서 Day 1-6의 `지도 열기`를 각각 눌러 지도 타일/iframe/canvas 생성과 성공 상태 문구를 확인한다.
- 재발 방지 체크: `assets/map-data.json` 검증은 반드시 UTF-8로 읽는다. PowerShell 기본 인코딩으로 읽으면 한글이 깨져 JSON 파싱 오류처럼 보일 수 있으므로 `Get-Content -Raw -Encoding UTF8 assets\map-data.json | ConvertFrom-Json` 형태를 사용한다.
- API 키 값 자체는 워크로그나 커밋에 남기지 않는다. 로컬 확인용 값은 개인 작업트리에만 두고, 배포용 값은 GitHub Secret `GOOGLE_MAPS_API_KEY`로 관리한다.
- 전체 Day 1-6 Google route geometry를 점검했다. 기존 구현은 Google Routes API 호출은 성공했지만, 대부분의 일일 지도 구간이 좌표가 아니라 장소명 `query`로 route origin/destination을 넘겨 일부 구간에서 마커와 실제 경로 시작·끝점이 수백 m-수 km 벌어졌다. 이 차이를 직선 커넥터가 잇기 때문에 Navigli, Bellagio, Fondazione Prada, MXP 같은 구간이 꼬인 선처럼 보일 수 있었다.
- 재발 방지를 위해 `milano_honeymoon_guide.html`의 route origin/destination을 항상 `assets/map-data.json`의 정확한 마커 좌표로 넘기도록 수정했고, `distanceMeters`가 있는 복수 route 후보는 더 짧은 거리 순으로 선택하도록 보강했다. 운전 구간은 기존처럼 `SHORTER_DISTANCE` reference route를 우선 사용한다.
- 공항 구간의 긴 직선 커넥터를 줄이기 위해 BGY와 MXP 좌표를 Google route가 실제 도착하는 터미널/접근 지점 쪽으로 보정했다.
- 검증 기준: Google Routes REST API로 Day 1-6의 56개 구간을 재계산해 `polyline` 포인트 수, route distance, 마커와 경로 시작·끝점 간격을 확인했다. 수정 전에는 큰 endpoint gap이 다수 있었고, 수정 후에는 문제 목록이 0건이었다. 브라우저에서도 Day 1-6 `지도 열기`를 모두 다시 눌러 지도 DOM, iframe, 타일 이미지, canvas, 성공 상태 문구를 확인했다.
