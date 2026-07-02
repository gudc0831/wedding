# Compact Mobile App Toggle Design

## Goal

Add a small mobile/app-view toggle to the deployed static honeymoon guide pages without taking over the layout or duplicating the guide content.

## Approved Direction

Use the existing country-guide HTML pages and add a compact top-right `앱` toggle inside the sticky topbar. The toggle should be about 34-40px tall, visually quiet, and visible without pushing the itinerary content down.

The toggle enables an app-style mobile reading mode on the same URL. It must not create separate `*_mobile.html` files because the itinerary content would then need to be maintained twice.

## Scope

Apply the toggle to:

- `czech_honeymoon_guide.html`
- `switzerland_honeymoon_guide.html`
- `italy_honeymoon_guide.html`

Keep `index.html` unchanged unless a later pass shows it needs a separate selector-page adjustment.

## Behavior

- The button label is `앱` when app view is off.
- The button label is `웹` when app view is on.
- Clicking the button toggles a class on `<html>`: `app-view`.
- The current mode is saved in `localStorage` under `honeymoonGuideView`.
- If the deployed URL contains `?view=app`, app view starts enabled.
- If the deployed URL contains `?view=web`, app view starts disabled.

## Mobile UI Changes In App View

In app view, keep the page content identical but change the reading ergonomics:

- Reduce sticky topbar padding so it uses less vertical space.
- Keep the compact app toggle aligned to the brand row.
- Make country tabs horizontally scroll instead of wrapping into a tall block.
- Make section nav chips horizontally scroll instead of wrapping into a tall block.
- Add bottom safe-area padding so lower content is not cramped on phones.
- Keep route-map buttons large enough to tap, but do not change the Google Maps loading logic.

## Verification

Do not test route maps through a raw static server. If browser route-map testing is needed, follow `AGENTS.md`: run `.\scripts\start-local-server.ps1`, generate `assets/google-maps-config.local.json`, then verify the config over HTTP before opening maps.

For the implementation pass, static checks are enough before any browser map testing:

- Confirm each country page contains one `[data-view-toggle]` button.
- Confirm each country page contains the shared app-view script.
- Confirm `.superpowers/` is ignored so brainstorming mockups are not committed.
