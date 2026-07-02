# 2026-07-02 App View Canvas And Verification

## Req

- Align the repository with `AGENTS.md` app-view rules.
- Keep web/app guide content shared.
- Optimize app view for iPhone 15 Pro and iPhone 17 Pro portrait widths.
- Use multi-agent review/implementation where practical.

## Diff

- `assets/guide-compact.css`
  - Added shared `html.app-view` app canvas sizing.
  - Set app canvas max width to `402px`.
  - Scoped mobile-like structural layout rules under `html.app-view` so `?view=app` behaves consistently even in a wider browser.
  - Added shared mobile width constraints so wide internal scrollers such as the Czech calendar remain inside their own scroll container instead of expanding the document width.
- `AGENTS.md`
  - Narrowed the static verification regex so it counts only actual `<button data-view-toggle>` elements.
- `scripts/verify-deployed-guide.mjs`
  - Replaced the old single mobile `390x844` pass with `393x852` and `402x874`.
  - Added `?view=web` and `?view=app` matrix checks.
  - Added assertions that `html.app-view` is present only in app mode.

## Why

The previous implementation had the app toggle and shared content model, but `?view=app` did not enforce the documented `402px` app canvas. The deployed verifier also did not test `?view=app`, and the documented static check counted the JavaScript selector string as a second toggle.

## Verify

- Static guide marker check confirmed for:
  - `czech_honeymoon_guide.html`
  - `switzerland_honeymoon_guide.html`
  - `italy_honeymoon_guide.html`
- Static result:
  - `toggleButtons = 1`
  - `appViewCss = true`
  - `storageKey = true`
  - `compactCssLinked = true`
- CSS marker check confirmed:
  - `--app-width: 402px`
  - `max-width: var(--app-width)`
  - `html.app-view .hero-grid`
  - `html.app-view .route-map-button`
- Verifier marker check confirmed:
  - `393x852`
  - `402x874`
  - `web/app` view matrix
  - `html.app-view` assertion
- `node --check scripts\verify-deployed-guide.mjs` passed.
- Local Google Maps config was regenerated and verified over HTTP before browser testing:
  - `200 true routes 990`
- Real local Chrome browser check passed for:
  - `czech_honeymoon_guide.html`
  - `switzerland_honeymoon_guide.html`
  - `italy_honeymoon_guide.html`
  - `?view=web`
  - `?view=app`
  - `393x852`
  - `402x874`
- Browser result:
  - `failures = []`
  - all web/app pairs had matching normalized text, HTML, sections, headings, route-card counts, and route-button counts
  - all web/app mobile checks had `horizontalOverflow = 0`
  - app shell width was `393px` on iPhone 15 Pro viewport and `402px` on iPhone 17 Pro viewport
- Browser artifacts:
  - `output/browser-check/20260702-app-view-layout/summary.json`
  - `output/browser-check/20260702-app-view-layout/*.png`

## Not Verified

- Route-map open/click behavior was not part of this pass. The local Google Maps config URL was verified over HTTP, but route map buttons were not opened.

## Time

- 2026-07-02 KST
