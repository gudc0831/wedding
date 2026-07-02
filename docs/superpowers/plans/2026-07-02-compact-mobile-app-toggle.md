# Compact Mobile App Toggle Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a compact app-view toggle to the country guide pages so the deployed static site can be checked comfortably on mobile without large buttons or duplicate pages.

**Architecture:** Each country HTML file keeps its existing content and route-map scripts. A small topbar button toggles an `app-view` class on `<html>`, persists the state in `localStorage`, and uses query parameters for direct deployed checks. CSS under `html.app-view` adjusts only mobile ergonomics.

**Tech Stack:** Static HTML, inline CSS, inline JavaScript, GitHub Pages.

---

### Task 1: Keep brainstorm artifacts out of git

**Files:**
- Modify: `.gitignore`

- [ ] **Step 1: Add `.superpowers/` to `.gitignore`**

```text
.superpowers/
```

- [ ] **Step 2: Verify ignored state**

Run: `git status --short --ignored .superpowers`

Expected: `.superpowers/` appears as ignored, not as a normal untracked directory.

### Task 2: Add compact topbar toggle markup

**Files:**
- Modify: `czech_honeymoon_guide.html`
- Modify: `switzerland_honeymoon_guide.html`
- Modify: `italy_honeymoon_guide.html`

- [ ] **Step 1: Add a compact button in each `.brand` row**

```html
<button class="view-toggle" type="button" data-view-toggle aria-pressed="false" aria-label="앱 보기로 전환">앱</button>
```

Place it after the `.brand-copy` block inside `.brand` so it stays on the same row as the guide title.

- [ ] **Step 2: Confirm there is exactly one toggle per country page**

Run: `Select-String -Path *_honeymoon_guide.html -Pattern "data-view-toggle"`

Expected: one match in each country page.

### Task 3: Add compact app-view CSS

**Files:**
- Modify: `czech_honeymoon_guide.html`
- Modify: `switzerland_honeymoon_guide.html`
- Modify: `italy_honeymoon_guide.html`

- [ ] **Step 1: Add `.view-toggle` CSS near existing topbar styles**

```css
.view-toggle {
  flex: 0 0 auto;
  width: 38px;
  height: 38px;
  border: 1px solid rgba(23, 55, 47, 0.18);
  border-radius: 999px;
  background: rgba(23, 55, 47, 0.92);
  color: #fff9f1;
  font: inherit;
  font-size: 0.78rem;
  font-weight: 800;
  line-height: 1;
  cursor: pointer;
  box-shadow: 0 10px 22px rgba(23, 55, 47, 0.14);
}

.view-toggle[aria-pressed="true"] {
  background: #cda16a;
  color: #17372f;
}
```

- [ ] **Step 2: Add app-view CSS before `</style>`**

```css
html.app-view body {
  padding-bottom: max(28px, env(safe-area-inset-bottom));
}

html.app-view .topbar-inner {
  gap: 7px;
  padding: 8px 12px;
}

html.app-view .brand {
  align-items: center;
}

html.app-view .brand-mark {
  width: 36px;
  height: 36px;
  font-size: 1rem;
}

html.app-view .brand-copy h1 {
  font-size: 0.94rem;
  line-height: 1.25;
}

html.app-view .eyebrow {
  margin-bottom: 2px;
  font-size: 0.68rem;
}

html.app-view .country-tabs,
html.app-view .nav-links {
  flex-wrap: nowrap;
  width: 100%;
  max-height: none;
  overflow-x: auto;
  overflow-y: hidden;
  scrollbar-width: none;
}

html.app-view .country-tabs::-webkit-scrollbar,
html.app-view .nav-links::-webkit-scrollbar {
  display: none;
}

html.app-view .nav-links a {
  min-height: 34px;
  display: inline-flex;
  align-items: center;
}

html.app-view .route-map-actions {
  width: 100%;
}

html.app-view .route-map-button {
  min-height: 40px;
}
```

### Task 4: Add app-view state script

**Files:**
- Modify: `czech_honeymoon_guide.html`
- Modify: `switzerland_honeymoon_guide.html`
- Modify: `italy_honeymoon_guide.html`

- [ ] **Step 1: Add script near the other page scripts**

```html
<script>
  (function () {
    const root = document.documentElement;
    const toggle = document.querySelector("[data-view-toggle]");
    const params = new URLSearchParams(window.location.search);
    const requestedView = params.get("view");
    const storageKey = "honeymoonGuideView";

    function storedView() {
      try {
        return window.localStorage.getItem(storageKey);
      } catch {
        return null;
      }
    }

    function saveView(view) {
      try {
        window.localStorage.setItem(storageKey, view);
      } catch {
        return;
      }
    }

    function applyView(view) {
      const isAppView = view === "app";
      root.classList.toggle("app-view", isAppView);
      if (!toggle) return;
      toggle.setAttribute("aria-pressed", String(isAppView));
      toggle.setAttribute("aria-label", isAppView ? "웹 보기로 전환" : "앱 보기로 전환");
      toggle.textContent = isAppView ? "웹" : "앱";
    }

    const initialView = requestedView === "app" || requestedView === "web"
      ? requestedView
      : storedView() || "web";

    applyView(initialView);
    if (requestedView === "app" || requestedView === "web") {
      saveView(requestedView);
    }

    if (toggle) {
      toggle.addEventListener("click", () => {
        const nextView = root.classList.contains("app-view") ? "web" : "app";
        applyView(nextView);
        saveView(nextView);
      });
    }
  }());
</script>
```

- [ ] **Step 2: Verify static markers**

Run: `Select-String -Path czech_honeymoon_guide.html,switzerland_honeymoon_guide.html,italy_honeymoon_guide.html -Pattern "honeymoonGuideView|html.app-view|data-view-toggle"`

Expected: each marker exists in all three country pages.

### Task 5: Static validation

**Files:**
- Read: `czech_honeymoon_guide.html`
- Read: `switzerland_honeymoon_guide.html`
- Read: `italy_honeymoon_guide.html`

- [ ] **Step 1: Run script-count validation**

Run:

```powershell
$files = 'czech_honeymoon_guide.html','switzerland_honeymoon_guide.html','italy_honeymoon_guide.html'
foreach ($file in $files) {
  $raw = Get-Content -Raw -Path $file
  [pscustomobject]@{
    file = $file
    toggleButtons = ([regex]::Matches($raw, 'data-view-toggle')).Count
    appViewCss = $raw.Contains('html.app-view')
    storageKey = $raw.Contains('honeymoonGuideView')
  }
}
```

Expected: each file has `toggleButtons` equal to `1`, `appViewCss` equal to `True`, and `storageKey` equal to `True`.

- [ ] **Step 2: Defer route-map browser testing unless local config is verified**

If route-map browser testing is requested, first follow `AGENTS.md`:

```powershell
.\scripts\write-local-google-maps-config.ps1
node -e "(async()=>{const r=await fetch('http://localhost:8000/assets/google-maps-config.local.json'); const j=await r.json(); console.log(r.status, !!j.apiKey, j.googleRouteEngine, j.googleMapMonthlyLimit)})()"
```

Expected config output shape: `200 true routes 990`.
