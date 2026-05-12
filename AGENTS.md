# AGENTS.md

Mandatory repository instructions for future agents and maintainers.

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
