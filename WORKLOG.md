# Worklog

## 2026-07-07

- 검토 결과 07.26 이탈리아 이동일에 남아 있던 Porta Nuova / Piazza Gae Aulenti 산책 문구를 제거하고, 이탈리아·체코 캘린더를 외부 아침식사, 체크아웃, Centrale 주변 대기, BGY 공항버스 버퍼 기준으로 맞췄다. Day 2 Mercato Centrale 아침 동선은 HTML 하이라이트 키와 지도 경로를 맞추고, 루체른 HEINI Bahnhof Luzern / Bachmann Gleis 3 조식 후보는 스위스 Day 2·Day 3 지도 포인트와 경로에 추가했다.
- 밀라노 UNA HOTELS Century Milano와 루체른 Hotel Luzernerhof 모두 조식 미포함 기준으로 정정했다. 이탈리아 가이드는 Mercato Centrale Milano 06:30 오픈을 8시 전 아침 1순위로 반영하고, 스위스 가이드는 HEINI Bahnhof Luzern과 Confiserie Bachmann Bahnhof UG / Gleis 3를 루체른 아침 후보로 추가했다.
- 07.26 이탈리아 → 프라하 항공편을 예약완료한 `Milan(Bergamo)=BGY 15:10 → Prague=PRG 16:35` 기준으로 고정했다. 이탈리아·체코 공용 가이드 본문과 캘린더 일정표에 예약완료 상태를 반영했다.
- 이탈리아 Day 6의 MXP/LIN 항공 대안, Skyscanner/Flight.info 항공 검색 링크, Malpensa 지도 포인트와 대안 경로를 삭제했다. 마지막 날 지도는 BGY 공항 이동과 Centrale 주변 대기/짐 보관 백업만 표시한다.
- 변경된 HTML과 `assets/map-data.json`이 오래된 서비스워커 캐시에 묶이지 않도록 `service-worker.js` 캐시 버전을 갱신했다.
- 첫날에 넣었던 Porta Nuova / Piazza Gae Aulenti 산책은 최종적으로 07.22 Day 2 점심 동선으로 이동했다. 07.26 Day 6는 외부 아침식사, 체크아웃, Centrale 주변 대기, BGY 공항버스 이동으로 단순화했다.
- `codex/unconfirmed-schedule` 브랜치에서 이탈리아 Day 2 미확정안을 호텔조식, M3 두오모 이동, 두오모 광장·내부·테라스, Galleria, Brera, 선택 CityLife/휴식/카페, Navigli 저녁 순서로 재구성했다.

## 2026-07-02

- 07.26 밀라노/베르가모 → 프라하 이동 기준을 체코 페이지의 `Milan(Bergamo) 15:10 → Prague 16:35`로 통일했다. 이탈리아 페이지의 기존 `BGY 06:35 → PRG 08:00` 새벽 이동 문구, 셔틀 역산, Day 6 요약표를 오후 이동 기준으로 정리했다.
- Swiss Half Fare Card는 구매 완료 상태로 닫고, 스위스 페이지의 운영 기준과 교통 비용/예약 표를 “구매 완료, 여권 원본과 티켓 QR 보관” 기준으로 수정했다.
- 인터라켄 숙소를 `65 Hauptstrasse, Unterseen, BE 3800`으로 확정하고, 07.18 이동은 Interlaken West 하차 후 숙소 이동으로 정리했다. 스위스 Day 3 지도 데이터에도 숙소 마커와 West→숙소 구간을 추가했다.
- 07.16 LX1485 프라하 09:30 → 취리히 10:55는 예약 완료로 닫고, 취리히 공항 → 루체른은 Swiss public transport 조회 기준 `12:15 Zürich Flughafen → 13:25 Luzern` 추천 구매 후보와 12:39/13:15 백업을 스위스·체코 페이지 및 Day 1 지도 데이터에 반영했다.
- 07.21 스위스 → 이탈리아 이동은 사용자가 확정한 `Grindelwald 11:17 → Domodossola 14:32` 예약 완료 구간을 한 구간씩 나눠 스위스 Day 6 일정에 반영했다. Domodossola → Milano Centrale은 Trenord Quadro 40 기준 `14:48 → 16:35` 추천 구매 후보, `15:48 → 17:35` 백업으로 표시하고 Day 6 지도 데이터를 새로 추가했다.
- 위 변경이 로컬/배포 캐시에서 즉시 반영되도록 `service-worker.js` 캐시 버전을 갱신했다.
- 체코·스위스·이탈리아 가이드 상단바에 작은 `앱` 보기 토글을 추가했다. `?view=app` 또는 버튼 클릭으로 같은 배포 URL에서 app-view 레이아웃을 켜고, 버튼은 상단 우측 38px 원형 토글로 콘텐츠 공간을 차지하지 않게 했다.
- 체코·스위스·이탈리아 각 탭의 맨 마지막 일정표를 국가별 캘린더형 시간표로 교체했다. 각 탭에는 해당 국가 일정만 보이고, 시간축은 06:00-22:00이며 이동/교통, 투어/관광, 식사/카페, 숙소/체크인, 준비/예약필요를 색상 블록으로 구분한다.
- 스위스 탭의 아침 표기를 정리했다. Hotel Luzernerhof 숙박 구간만 `호텔조식`으로 표시하고, Interlaken/Grindelwald 등 조식을 신청하지 않은 숙박 구간은 `아침식사` 또는 개별 준비 기준으로 바꿨다.
- 숙소별 조식 신청 여부를 체코·이탈리아 탭에 반영했다. Hotel Paris Prague와 UNA HOTELS Century Milano는 `조식 포함/호텔조식`, Charles Bridge Palace Hotel은 `조식 없음/아침식사 개별` 기준으로 일정표와 본문을 구분했다.
- 체코 07.27 Charles Bridge Palace Hotel 조식 없음 구간에 호텔 근처 아침식사 기본안으로 Café Slavia를 일정표에 넣었다. 추가 옵션은 Café Louvre와 Bakeshop Praha로 리스트업하고 공식 조식/운영시간 링크를 출처에 추가했다.
- 세 나라 캘린더형 일정표의 모바일 사용성을 위해 공통 `assets/schedule-detail.css`/`assets/schedule-detail.js`를 추가했다. 일정 카드를 탭하면 날짜·도시·숙소·준비사항·상태·세부 구간을 바텀시트로 보여주며, 스위스 장거리 이동과 체코 조식 대체안에는 구간별 상세 데이터를 붙였다.
- 모바일에서 초반 히어로와 설명 블록이 과하게 크게 보이는 문제를 줄이기 위해 공통 `assets/guide-compact.css`를 추가했다. 세 나라 탭의 히어로, 설명문, 카드, 가로 스크롤 표 글자와 칸 폭을 조정했고, 스위스 히어로 사진은 중복 없이 작은 썸네일 그리드로 재구성했다. 깨진 Bachalpsee/First 계열 사진은 200 확인된 Wikimedia `Special:FilePath` URL과 안정적으로 내려오는 철도 이동 이미지로 교체했다.
- 이탈리아 모바일 쇼핑맵 섹션이 공통 압축 CSS 안에서 좁게 눌려 제목과 지도 이미지가 덮어쓴 것처럼 보이는 문제를 보정했다. `#shopping-map` 전용으로 섹션 헤더를 세로 배치하고, 지도 SVG는 최소 폭을 둔 가로 스크롤 프레임으로 바꿔 라벨이 서로 겹쳐 보이지 않게 했다.
- 세 나라 하단 Sources 영역에서 긴 URL이 옆 칸으로 넘어가지 않도록 900px 이하에서 정보원 목록을 1열로 전환하고, 링크 텍스트 크기와 줄바꿈 규칙을 조정했다.
- 이탈리아 `Checklist`와 `Sources` 섹션을 접이식으로 바꿨다. 기본은 닫힘이며, 사용자가 열기/닫기를 누른 상태는 `localStorage`에 저장되어 같은 브라우저에서 계속 유지된다. Sources는 641-900px 구간에서 2열을 유지하고 링크 글씨와 줄바꿈만 줄여 스크롤 길이를 줄였다.

## 2026-06-17

- 스위스 가이드의 07.18 Luzern-Interlaken Express 문구를 보강했다. 공식 일반 패턴과 별개로 사용자가 결제한 09:24 -> 11:17 티켓을 우선한다는 점을 명확히 했다.
- 스위스 교통·산악권 비용/예약 표를 추가했다. Swiss Half Fare Card, Lake Lucerne boat, Rigi, Luzern-Interlaken Express 좌석 예약, Harder Railway, Grindelwald-First, Jungfraujoch 옵션을 공식 공개 정보 기준으로 정리했다.
- 식당 운영 확인 카드를 추가했다. 루체른 저녁, 리기산 식사, 인터라켄·하더쿨름, 그린델발트·피르스트별로 예약/영업 확인 링크와 당일 판단 기준을 보강했다.
- `switzerland_honeymoon_guide.html`이 service worker precache 대상이므로 `service-worker.js` 캐시 버전을 갱신했다.
- 스위스 레스토랑·카페 추천을 옵션 전용 섹션으로 추가했다. Mill'Feuille, Confiserie Bachmann, Wirtshaus Taube, Velo Cafe, Grand Cafe Schuh, Husi Bierhaus, First Mountain Restaurant, Barry's Grindelwald, Cafe 3692를 일정 동선과 지도 데이터에는 넣지 않고 후보 카드로만 노출했다.

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
- 2026-05-11 업데이트: 로컬 Google Maps 확인은 `scripts/start-local-server.ps1`로 시작한다. 이 스크립트가 `.env` 또는 환경변수의 `GOOGLE_MAPS_API_KEY`를 읽어 `assets/google-maps-config.local.json`을 생성한 뒤 `http://localhost:8000/` 정적 서버를 띄운다. 해당 JSON은 git ignore 대상이다.
- 2026-05-11 업데이트: API 키 누락/인증 실패/Google Maps JS 로드 실패 시 번호 마커 없는 Google 기본 iframe으로 조용히 fallback하지 않도록 막았다. 이 경우 지도 영역에 설정 오류가 직접 표시되어야 한다.
- 2026-05-11 업데이트: Places API (New)가 활성화된 키에서는 Google 지도 번호 마커 클릭 시 Text Search로 해당 장소만 조회해 주소, 영업 상태, Google Maps/길찾기 링크를 보강한다. 고비용 필드인 평점, 리뷰 수, 영업시간, 공식 사이트는 기본 요청에서 제외했다. Places가 제한되어도 지도와 경로는 유지된다.
- 2026-05-11 업데이트: 과금 방지를 위해 로컬/배포 config에 Google Maps, Routes, Places 월간 soft limit 기본값을 각각 990회로 둔다. 이 제한은 브라우저 localStorage 기반 보조 장치일 뿐이므로 실제 과금 방지는 Google Cloud Console에서 API별 quota 제한을 별도로 걸어야 한다.
- 전체 Day 1-6 Google route geometry를 점검했다. 기존 구현은 Google Routes API 호출은 성공했지만, 대부분의 일일 지도 구간이 좌표가 아니라 장소명 `query`로 route origin/destination을 넘겨 일부 구간에서 마커와 실제 경로 시작·끝점이 수백 m-수 km 벌어졌다. 이 차이를 직선 커넥터가 잇기 때문에 Navigli, Bellagio, Fondazione Prada, MXP 같은 구간이 꼬인 선처럼 보일 수 있었다.
- 재발 방지를 위해 `milano_honeymoon_guide.html`의 route origin/destination을 항상 `assets/map-data.json`의 정확한 마커 좌표로 넘기도록 수정했고, `distanceMeters`가 있는 복수 route 후보는 더 짧은 거리 순으로 선택하도록 보강했다. 운전 구간은 기존처럼 `SHORTER_DISTANCE` reference route를 우선 사용한다.
- 공항 구간의 긴 직선 커넥터를 줄이기 위해 BGY와 MXP 좌표를 Google route가 실제 도착하는 터미널/접근 지점 쪽으로 보정했다.
- 검증 기준: Google Routes REST API로 Day 1-6의 56개 구간을 재계산해 `polyline` 포인트 수, route distance, 마커와 경로 시작·끝점 간격을 확인했다. 수정 전에는 큰 endpoint gap이 다수 있었고, 수정 후에는 문제 목록이 0건이었다. 브라우저에서도 Day 1-6 `지도 열기`를 모두 다시 눌러 지도 DOM, iframe, 타일 이미지, canvas, 성공 상태 문구를 확인했다.

## 2026-05-25

- 배포 확인 사이트는 `https://gudc0831.github.io/wedding/milano_honeymoon_guide.html`로 고정한다. Google Maps API 지도와 Routes API 루트 최종 확인은 이 URL의 Day 1-6 `지도 열기` 동작을 기준으로 판단한다.
- 배포 URL `https://gudc0831.github.io/wedding/`에서 Day 1 `지도 열기`를 실제 브라우저로 재현했고, 콘솔의 핵심 오류가 `BillingNotEnabledMapError`임을 확인했다. API 키는 배포 자산에 주입되어 있었지만, Google Cloud 프로젝트 billing이 비활성화된 키는 Maps JavaScript API 지도를 정상 렌더링하지 못한다.
- production 기준은 API 기반 지도와 route line이므로 GitHub Pages 기본 배포 엔진은 `GOOGLE_MAPS_ROUTE_ENGINE=routes`로 유지한다. GitHub에는 API 키를 커밋하지 않고 Secret 또는 Repository Variable `GOOGLE_MAPS_API_KEY`로만 주입한다.
- Google Cloud Console에서 billing, Maps JavaScript API, Routes API, 필요 시 Places API (New)를 활성화해야 한다. 이 중 하나라도 누락되면 배포 URL에서 API 기반 지도와 루트가 정상 표시되지 않는다.
- `auth_referrer_policy=origin`은 더 이상 강제로 넣지 않는다. 이 옵션을 켜려면 Cloud Console referrer 제한이 `https://gudc0831.github.io/*`처럼 origin 단위여야 한다. `https://gudc0831.github.io/wedding/*`처럼 path가 있는 제한을 쓸 때는 `GOOGLE_MAPS_AUTH_REFERRER_POLICY`를 비워둔다.
- `routes` 엔진에서 billing/auth/quota 문제가 발생하면 Google Maps iframe으로 조용히 대체하지 않고 설정 오류를 표시한다. API 기반 지도와 루트 표시가 production 요구사항이기 때문에, 오류를 숨기면 검증이 잘못 통과할 수 있다.
- GitHub Pages 배포 후 Playwright smoke test를 실행해 Day 1 `지도 열기`가 Maps JavaScript API 지도와 Routes API 루트를 정상 표시하는지 확인한다. iframe fallback, Google account/billing overlay, route fallback 문구, Google API 콘솔 오류가 있으면 workflow를 실패시킨다.
