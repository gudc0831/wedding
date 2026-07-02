# AGENTS.md

Mandatory repository instructions for future agents and maintainers.

## Web/App Content Rule

The web version and app version must use the same guide content.

Do not create or maintain separate mobile-only itinerary pages such as:

```text
*_mobile.html
*_app.html
```

The app version is a display mode of the existing country guide pages, enabled through the shared `html.app-view` state and the `앱` / `웹` toggle. When itinerary text, links, route-map cards, schedules, hotels, restaurants, reservations, source links, or warnings are changed, the same change must be visible in both:

```text
?view=web
?view=app
```

If a change requires app-specific layout CSS, keep the content in the shared HTML and scope only the layout override under:

```css
html.app-view
```

## App View Size And Ratio

The app view is optimized for iPhone portrait use, especially:

```text
iPhone 15 Pro: 393 x 852 CSS px target viewport
iPhone 17 Pro: 402 x 874 CSS px target viewport
```

Use the iPhone 17 Pro width as the upper app canvas target:

```css
max-width: 402px;
width: 100%;
```

The iPhone 15 Pro width, `393px`, is the minimum required proof width. The app layout must not rely on extra width beyond `393px`.

The app view should preserve the practical iPhone portrait ratio, roughly `19.5:9`, but do not hard-code page height. Content must scroll naturally, respect safe-area padding, and avoid horizontal page overflow.

## App View Verification

Before claiming an app-view layout change is complete, verify both web and app modes on the country guide pages.

Required static marker check:

```powershell
$files = 'czech_honeymoon_guide.html','switzerland_honeymoon_guide.html','italy_honeymoon_guide.html'
foreach ($file in $files) {
  $raw = Get-Content -Raw -Path $file
  [pscustomobject]@{
    file = $file
    toggleButtons = ([regex]::Matches($raw, '<button\b[^>]*\bdata-view-toggle\b[^>]*>')).Count
    appViewCss = $raw.Contains('html.app-view')
    storageKey = $raw.Contains('honeymoonGuideView')
  }
}
```

Expected result:

```text
toggleButtons = 1
appViewCss = True
storageKey = True
```

Required browser viewports for layout verification:

```text
393 x 852  (?view=web and ?view=app)
402 x 874  (?view=web and ?view=app)
```

At each viewport, verify:

1. The page has no horizontal document overflow.
2. The sticky topbar, country tabs, and section navigation do not cover the main content.
3. Text does not overlap buttons, cards, maps, or adjacent sections.
4. The `앱` / `웹` toggle persists and switches the same page content, not a duplicated page.
5. Route-map buttons remain tappable.

## Local Google Maps Rule

The local Google Maps route maps must never be tested with a raw static server.

Do not run either of these as the primary local server for route-map testing:

```powershell
python -m http.server
npx serve
```

Always start or restart the local site through the wrapper:

```powershell
.\scripts\start-local-server.ps1
```

This wrapper is required because browsers cannot read `.env` directly. It first generates:

```text
assets/google-maps-config.local.json
```

from `.env`, then serves the site at:

```text
http://localhost:8000/
```

If `assets/google-maps-config.local.json` is missing, deleted, ignored by git, or stale, the page will fall back to `assets/google-maps-config.js`, whose checked-in API key is intentionally empty. The visible symptom is:

```text
Google Maps API key is not available locally.
```

## Required Verification Before Browser Testing

Before opening, refreshing, or debugging route maps in the browser, verify the generated local config exists and is being served.

Run:

```powershell
.\scripts\write-local-google-maps-config.ps1
```

Then verify through HTTP, not only the filesystem:

```powershell
node -e "(async()=>{const r=await fetch('http://localhost:8000/assets/google-maps-config.local.json'); const j=await r.json(); console.log(r.status, !!j.apiKey, j.googleRouteEngine, j.googleMapMonthlyLimit)})()"
```

Expected output shape:

```text
200 true routes 990
```

Only after that check should an agent claim the local Google Maps config is available.

## If The Error Reappears

Follow this order exactly:

1. Check that `.env` exists and contains `GOOGLE_MAPS_API_KEY`, but do not print the key value.
2. Run `.\scripts\write-local-google-maps-config.ps1`.
3. Verify `http://localhost:8000/assets/google-maps-config.local.json` returns HTTP 200 and has `apiKey`.
4. If the browser still shows the old error, refresh the page and click the route-map open button again.
5. If it still fails, check whether port `8000` is being served by an old process or from the wrong directory.
6. Restart the server with `.\scripts\start-local-server.ps1`.

Do not guess at API-key, referrer, billing, or quota causes until the local config URL has been verified over HTTP.

## Secret Handling

Never commit, paste, log, or summarize actual Google Maps API key values.

These files are intentionally ignored by git:

```text
.env
.env.local
assets/google-maps-config.local.json
```

It is acceptable to report only boolean/redacted checks such as:

```text
GOOGLE_MAPS_API_KEY=set
hasApiKey=true
```

Do not include the raw key in issues, worklogs, screenshots, terminal summaries, or final responses.

## Billing Guardrail Note

The repository includes browser-side soft limits:

```text
googleMapMonthlyLimit
googleRouteComputeMonthlyLimit
googlePlacesMonthlyLimit
```

These are convenience guards only. Real billing protection must be configured in Google Cloud Console with API key restrictions, HTTP referrer restrictions, API quotas, and budget alerts.
