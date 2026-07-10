# Czech·Swiss Schedule Detail Enrichment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 체코·스위스 일정표의 모든 상세창을 행동 가능한 여행 안내로 채우고, 설명이 약한 본문만 선별 보강한 뒤 기존 일정·예약·지도·웹/앱 구조를 보존했음을 검증한다.

**Architecture:** 기존 `.calendar-event`와 `assets/schedule-detail.js` 인터페이스를 유지하고 각 이벤트의 `data-detail` 콘텐츠를 완성한다. 체코와 스위스 HTML은 격리된 작업트리에서 병렬 편집하고, 관리자가 두 커밋을 현재 기능 브랜치에 통합한 뒤 공용 캐시·지도·브라우저 회귀검증을 수행한다.

**Tech Stack:** 정적 HTML/CSS/JavaScript, Node.js ESM 검증 스크립트, PowerShell 로컬 서버 래퍼, Playwright CLI, Google Maps Routes 런타임

## Global Constraints

- 체코 46개와 스위스 39개 `.calendar-event` 모두 비어 있지 않은 `data-detail`을 가져야 한다.
- 각 `data-detail`은 `|`로 나뉜 비어 있지 않은 설명 2개 이상을 가져야 한다.
- 현재 날짜, 예약 시간, 확정 숙소, 확정 이동 순서, 지도 번호와 장소 키를 변경하지 않는다.
- 원본에 있는 일정, 예약, 숙소, 사진, 지도 경로를 삭제하거나 재배치하지 않는다.
- `이건 엑셀에서 가져왔습니다`, `엑셀 기준`, `스프레드시트에서 가져옴` 같은 출처 노출 문구를 콘텐츠에 넣지 않는다.
- 웹과 앱은 같은 HTML 본문을 사용하며 별도 `*_mobile.html` 또는 `*_app.html`을 만들지 않는다.
- 일정표 셀은 짧게 유지하고 설명은 기존 상세창과 선별 본문에 넣는다.
- 공용 `assets/map-data.json`과 `service-worker.js`는 관리자가 통합 단계에서만 수정한다.
- 실제 Google Maps API 키를 출력, 문서화, 캡처 또는 커밋하지 않는다.

---

### Task 1: Schedule Detail Coverage Validator

**Files:**
- Create: `scripts/validate-schedule-details.mjs`
- Test: `czech_honeymoon_guide.html`
- Test: `switzerland_honeymoon_guide.html`

**Interfaces:**
- Consumes: 두 가이드의 `.calendar-event` 시작 태그와 `data-detail` 속성
- Produces: 파일별 `events`, `withDetail`, `missingDetail`, `invalidSegments` 집계와 성공/실패 종료 코드

- [ ] **Step 1: 검증 스크립트를 추가한다**

```js
import fs from "node:fs";

const guides = [
  { file: "czech_honeymoon_guide.html", expected: 46 },
  { file: "switzerland_honeymoon_guide.html", expected: 39 },
];

const forbidden = /이건 엑셀에서 가져왔습니다|엑셀 기준|스프레드시트에서 가져옴/i;
const errors = [];
const summaries = [];

for (const guide of guides) {
  const html = fs.readFileSync(guide.file, "utf8");
  const tags = html.match(/<div\b(?=[^>]*\bclass="[^"]*\bcalendar-event\b[^"]*")[^>]*>/g) || [];
  let withDetail = 0;
  let invalidSegments = 0;

  tags.forEach((tag, index) => {
    const match = tag.match(/\bdata-detail="([^"]*)"/);
    if (!match) {
      errors.push(`${guide.file}: calendar event ${index + 1} is missing data-detail`);
      return;
    }
    withDetail += 1;
    const segments = match[1].split("|").map((value) => value.trim()).filter(Boolean);
    if (segments.length < 2) {
      invalidSegments += 1;
      errors.push(`${guide.file}: calendar event ${index + 1} has ${segments.length} detail segment(s)`);
    }
  });

  if (tags.length !== guide.expected) {
    errors.push(`${guide.file}: expected ${guide.expected} events, found ${tags.length}`);
  }
  if (forbidden.test(html)) {
    errors.push(`${guide.file}: forbidden source wording found`);
  }

  summaries.push({
    file: guide.file,
    events: tags.length,
    withDetail,
    missingDetail: tags.length - withDetail,
    invalidSegments,
  });
}

console.log(JSON.stringify(summaries, null, 2));
if (errors.length) {
  console.error(errors.join("\n"));
  process.exit(1);
}
console.log("SCHEDULE_DETAIL_VALIDATION_PASS");
```

- [ ] **Step 2: 실패 기준선을 확인한다**

Run: `node scripts/validate-schedule-details.mjs`

Expected: exit code `1`, 체코 `withDetail: 4`, `missingDetail: 42`, 스위스 `withDetail: 14`, `missingDetail: 25`.

- [ ] **Step 3: 스크립트 구문과 형식을 확인한다**

Run: `node --check scripts/validate-schedule-details.mjs`

Expected: exit code `0`.

Run: `git diff --check -- scripts/validate-schedule-details.mjs`

Expected: exit code `0`.

- [ ] **Step 4: 검증기만 커밋한다**

```powershell
git add -- scripts/validate-schedule-details.mjs
git commit -m "test: validate schedule detail coverage"
```

### Task 2: Czech Calendar And Narrative Enrichment

**Files:**
- Modify: `czech_honeymoon_guide.html:1298-2348`
- Test: `scripts/validate-schedule-details.mjs`

**Interfaces:**
- Consumes: 체코 본문 일정 카드의 확정 시간·장소·예약·대안 문구
- Produces: 체코 46/46 일정 상세, 본문 최소 검토 대상의 보강 문장

- [ ] **Step 1: 체코 42개 누락 이벤트에 `data-detail`을 추가한다**

모든 속성은 아래 형식을 사용한다.

```html
<div class="calendar-event transit" style="grid-column:2; grid-row:10 / span 7;" data-detail="KE969 도착 뒤 입국심사와 수하물 수령을 마치고 호텔 이동을 시작|여권·수하물·교통권을 확인하고 Hotel Paris Prague 체크인을 먼저 진행|도착이 늦으면 저녁만 유지하고 추가 산책은 생략">
```

아래 일정은 날짜별로 빠짐없이 처리한다.

- 07.11: `KE969 인천→프라하`, `대중교통 약 44분·호텔 체크인`, `Pilsnerka Národní`
- 07.12: `호텔조식`, `Charles Bridge`, `존 레논 벽`, `Prague Castle 핵심 코스`, `Kuchyň 점심`, `Strahov 수도원·도서관·양조장`, `Pork’s`, `리에그로비 사디 일몰`
- 07.13: `호텔조식`, `프라하→체스키크롬로프 버스`, `세미나르니 정원·Horní·스보르노스티 광장`, `Travellers Restaurant`, `강변·Café Kolektiv·성 탑·망토다리`, `Krčma Šatlava`, `터미널 오르막 이동·프라하 복귀`
- 07.14: `호텔조식`, `화약탑·시민회관·바츨라프 광장`, `Alma Café · Sisters Bistro 대안`, `하벨시장·구시가지·천문시계·타워`, `Kantýna 저녁`, `프라하 스냅 촬영`
- 07.15: `호텔조식`, `42번 빈티지 트램(선택)`, `유대인 지구`, `Kozlovna·Café Savoy·쇼핑`, `레트나·홀리쇼비체`, `Naše maso`, `Devil’s Channel 크루즈`
- 07.16: `체크아웃·공항 이동 준비`, `호텔→PRG 공항`
- 07.26: `프라하 공항→호텔 이동`, `Charles Bridge Palace Hotel 체크인`, `Čapadlo Summer Terrace 피자 저녁`, `댄싱하우스·비셰흐라드 일몰`
- 07.27: `까를교 일출`, `Charles Bridge Restaurant 포토스팟·레서 타운 기념품`, `점심`, `수하물 픽업·프라하 공항 이동`, `KE970 프라하→인천`

설명은 같은 날짜의 본문 카드에 이미 적힌 정보만 우선 재사용한다. `예약완료`, 버스 출발 시각, 촬영 집합 장소, 공항 도착 여유, 비·피로 시 축소안이 본문에 있으면 상세에도 유지한다.

- [ ] **Step 2: 체코 본문 최소 검토 대상을 보강한다**

다음 항목을 읽고 `무엇/왜/현장 행동/대안` 중 빠진 요소만 2~3문장 안에서 추가한다.

- `KE969 인천공항 → 프라하`: 입국·수하물 뒤 이동 시작 기준과 지연 시 저녁 축소
- `공항 → Hotel Paris Prague · 체크인`: 교통 표지판 확인, 체크인·짐 정리 우선순위
- 마지막 날 `점심`: 공항 이동에 부담 없는 메뉴와 종료 시각 기준
- `수하물 픽업·프라하 공항 이동`: 호텔 복귀·수하물 확인·공항 도착 목표

- [ ] **Step 3: 체코 범위 검증을 실행한다**

Run: `node scripts/validate-schedule-details.mjs`

Expected while Swiss work is not integrated: exit code `1`, 체코 `events: 46`, `withDetail: 46`, `missingDetail: 0`, `invalidSegments: 0`; 실패는 스위스 누락 25개뿐이다.

Run: `git diff --check -- czech_honeymoon_guide.html`

Expected: exit code `0`.

- [ ] **Step 4: 체코 파일만 커밋한다**

```powershell
git add -- czech_honeymoon_guide.html
git commit -m "feat: enrich Czech schedule details"
```

### Task 3: Swiss Calendar And Narrative Enrichment

**Files:**
- Modify: `switzerland_honeymoon_guide.html:2560-3988`
- Test: `scripts/validate-schedule-details.mjs`

**Interfaces:**
- Consumes: 스위스 본문 일정 카드의 확정 시간·플랫폼·예약·대안 문구
- Produces: 스위스 39/39 일정 상세, 본문 최소 검토 대상의 보강 문장

- [ ] **Step 1: 스위스 25개 누락 이벤트에 `data-detail`을 추가한다**

Task 2와 같은 2~4개 `|` 구간 형식을 사용하며 아래 일정을 빠짐없이 처리한다.

- 07.16: `Hotel Luzernerhof 체크인`, `호프교회·빈사의 사자상`, `호텔 체크인·휴식`, `카펠교·구시가지·로이스강변`, `Rathaus 또는 Des Alpes`, `카펠교 야경 짧게`, `숙소 복귀`
- 07.17: `역·베이커리 아침`, `호텔 출발`, `Luzern→Vitznau`, `호텔 휴식`, `퐁듀 또는 Des Alpes`, `카펠교 야경·짧은 산책`
- 07.18: `루체른역 아침`, `숙소 이동·짐 정리`, `인터라켄 점심`, `Höhematte·Hoheweg·숙소 복귀`
- 07.19: `하산·Interlaken 복귀`, `저녁·숙소 휴식`
- 07.20: `Interlaken→Grindelwald`, `호텔 글레처블릭 이동`, `숙소 복귀·저녁·휴식`, `호텔 글레처블릭 복귀`
- 07.21: `아침식사`, `체크아웃·플랫폼 확인`

플랫폼 번호, 열차 예약, 숙소명, 패러글라이딩·융프라우요흐·BelAqua 주의사항은 현재 본문의 확정 표현을 그대로 유지한다. 새로운 시간표나 영업시간을 추정하지 않는다.

- [ ] **Step 2: 스위스 본문 최소 검토 대상을 보강한다**

- `호텔 → Luzern Station`: 역 도착 목표, 플랫폼·물·간식 확인 목적
- `Hotel Luzernerhof 이동·체크인`: 역에서 숙소 이동과 짐·휴식 우선순위
- `인터라켄 점심`: 패러글라이딩 전 가벼운 메뉴와 종료 기준
- `호텔 글레처블릭 이동`: 캐리어 상태에 따른 버스·택시 판단과 체크인 순서
- `체크아웃·플랫폼 확인`: 긴 환승일의 간식·티켓 QR·승강장 확인

- [ ] **Step 3: 스위스 범위 검증을 실행한다**

Run: `node scripts/validate-schedule-details.mjs`

Expected while Czech work is not integrated: exit code `1`, 스위스 `events: 39`, `withDetail: 39`, `missingDetail: 0`, `invalidSegments: 0`; 실패는 체코 누락 42개뿐이다.

Run: `git diff --check -- switzerland_honeymoon_guide.html`

Expected: exit code `0`.

- [ ] **Step 4: 스위스 파일만 커밋한다**

```powershell
git add -- switzerland_honeymoon_guide.html
git commit -m "feat: enrich Swiss schedule details"
```

### Task 4: Integration, Map Audit, And Cache Refresh

**Files:**
- Modify: `service-worker.js:1`
- Inspect and modify only on semantic mismatch: `assets/map-data.json`
- Test: `scripts/validate-schedule-details.mjs`
- Test: `scripts/verify-local-route-maps-cdp.mjs`

**Interfaces:**
- Consumes: Task 2와 Task 3의 콘텐츠 커밋
- Produces: 통합된 가이드, 최신 캐시 버전, 지도 의미 일치 증거

- [ ] **Step 1: 체코·스위스 커밋을 현재 기능 브랜치에 통합한다**

```powershell
$czechCommit = (git -C '.superpowers/worktrees/czech-schedule-details' rev-parse HEAD).Trim()
$swissCommit = (git -C '.superpowers/worktrees/swiss-schedule-details' rev-parse HEAD).Trim()
git cherry-pick $czechCommit
git cherry-pick $swissCommit
```

각 cherry-pick 뒤 `git show --stat --oneline HEAD`로 예상 HTML 한 파일만 포함됐는지 확인한다.

- [ ] **Step 2: 전달된 원본 일정 파일과 현재 체코·스위스 내용을 다시 대조한다**

`C:\Users\hcchoi\Desktop\🤵👰신혼여행.xlsx`를 번들 Node.js와 `@oai/artifact-tool`로 읽는다. `신혼여행(일정)`과 체코·스위스 관련 시트의 사용 영역을 검사해 날짜, 도시, 숙소, 교통, 시간, 식당, 예약, 추가 준비사항이 현재 두 HTML의 본문 또는 일정 상세에 존재하는지 확인한다. 누락이 있으면 해당 날짜의 HTML에 추가하되 출처를 드러내는 문장은 넣지 않는다.

- [ ] **Step 3: 일정 상세 검증기를 통과시킨다**

Run: `node scripts/validate-schedule-details.mjs`

Expected: 체코 `46/46`, 스위스 `39/39`, `missingDetail: 0`, `invalidSegments: 0`, `SCHEDULE_DETAIL_VALIDATION_PASS`, exit code `0`.

- [ ] **Step 4: 지도 의미를 교차 감사한다**

`assets/map-data.json`을 파싱해 `dailyMaps` 20개, 체코 7개, 스위스 6개, 이탈리아 7개를 확인한다. HTML의 `data-route-map-card`, `data-place-key`, `data-place-keys`가 모두 지도 데이터에 존재하고 route의 `from`/`to`가 같은 지도 point key를 가리키는지 확인한다.

문장 보강으로 경로·순서·장소 의미가 바뀌지 않았다면 `assets/map-data.json`은 수정하지 않는다. 불일치가 발견된 경우 해당 summary/note만 현재 HTML의 확정 정보에 맞춘다.

- [ ] **Step 5: 서비스 워커 캐시 버전을 한 번 올린다**

```js
const CACHE_VERSION = "czech-swiss-italy-honeymoon-guide-v20260710-schedule-detail-enrichment";
```

Run: `node --check service-worker.js`

Expected: exit code `0`.

- [ ] **Step 6: 통합 정적 검증을 실행하고 커밋한다**

Run: `git diff --check`

Expected: exit code `0`.

Run: `node --check scripts/validate-schedule-details.mjs`

Expected: exit code `0`.

```powershell
git add -- service-worker.js assets/map-data.json
git commit -m "chore: refresh schedule detail cache"
```

`assets/map-data.json`에 실제 변경이 없으면 스테이징하지 않는다.

### Task 5: Browser Regression And Repair Loop

**Files:**
- Verify: `czech_honeymoon_guide.html`
- Verify: `switzerland_honeymoon_guide.html`
- Verify: `italy_honeymoon_guide.html`
- Verify: `assets/schedule-detail.js`
- Verify: `assets/map-data.json`
- Verify: `service-worker.js`

**Interfaces:**
- Consumes: 통합된 HTML·지도·캐시와 로컬 Google Maps 설정
- Produces: 12개 화면 조합, 상세창, 지도 20개에 대한 최신 통과 증거

- [ ] **Step 1: 브라우저 도구와 로컬 지도 설정을 확인한다**

Run: `command -v npx >/dev/null 2>&1`

Expected: exit code `0`.

Run: `.\scripts\write-local-google-maps-config.ps1`

Run: `node -e "(async()=>{const r=await fetch('http://localhost:8000/assets/google-maps-config.local.json'); const j=await r.json(); console.log(r.status, !!j.apiKey, j.googleRouteEngine, j.googleMapMonthlyLimit)})()"`

Expected: `200 true routes 990`. API 키 값은 출력하지 않는다.

- [ ] **Step 2: 12개 웹/앱·뷰포트 조합을 검증한다**

대상은 체코·스위스·이탈리아 × 393×852·402×874 × `?view=web`·`?view=app`이다. 각 화면에서 `documentElement.scrollWidth - clientWidth === 0`, 토글 노출, `html.app-view` 상태, 상단바·탭·본문 비겹침, 지도 버튼 탭 가능 여부를 확인한다.

- [ ] **Step 3: 일정 상세창 상호작용을 검증한다**

체코·스위스에서 transit, tour, food, stay, prep 유형별 대표 이벤트를 클릭하고 제목, 날짜·시간, 요약, 2개 이상의 세부 구간을 확인한다. 클릭, Enter, Space로 열리고 닫기 버튼, Escape, 배경 클릭으로 닫히며 닫은 뒤 원래 이벤트로 포커스가 돌아오는지 확인한다.

- [ ] **Step 4: 지도 20개를 검증한다**

Run: `node scripts/verify-local-route-maps-cdp.mjs`

Expected: 체코 7개, 스위스 6개, 이탈리아 7개 지도 카드가 열리고 치명적 브라우저 콘솔 오류가 없으며 Google route panel이 정상 상태를 보고한다.

- [ ] **Step 5: 실패를 수정하고 전체 검증을 처음부터 반복한다**

실패가 있으면 파일·날짜·일정명·뷰포트 단위로 원인을 수정한다. 수정 뒤 Task 4 Step 2부터 Task 5 Step 4까지 다시 실행한다. 모든 최신 출력이 통과할 때만 다음 단계로 이동한다.

- [ ] **Step 6: 최종 변경을 커밋한다**

```powershell
git add -- czech_honeymoon_guide.html switzerland_honeymoon_guide.html italy_honeymoon_guide.html assets/map-data.json assets/schedule-detail.js service-worker.js scripts/validate-schedule-details.mjs
git commit -m "fix: close honeymoon guide detail regressions"
```

검증 과정에서 실제로 수정된 파일만 스테이징하며 빈 커밋은 만들지 않는다.
