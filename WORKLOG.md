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
