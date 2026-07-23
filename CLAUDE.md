# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

A self-contained, scrollable interactive journalism piece about US immigration history and policy. It has no build system, no dependencies to install, and no test suite — open `index.html` directly in a browser to run it.

## Files

- **`index.html`** — the canonical, currently-developed entry point. It is now a **standalone, single-purpose page**: the `#policy-history` scroll-driven policy timeline (river/ship/canvas + SVG node path + GSAP-driven camera), fully self-contained with its own inline `<style>` and inline `<script>` (data, GSAP engine, dossier modal). It does not load `script.js` or `style.css`, and it no longer contains the opening/demographics/persona-cards/etymology/reasoning/pattern sections those files' JS expects — see recent commits: "drive #policy-history timeline with a single GSAP engine", "restyle policy cards, larger ship, smoother scrub".
- **`script.js`** / **`style.css`** — untracked, **not currently wired into any HTML file**. They hold the JS/CSS for a separate, not-yet-rebuilt page: named screen sections (`s-opening`, `s-demo`, `s-cards`, `s-etymology`, `s-reasoning`, `s-pattern`) toggled via `goTo(id)`, the persona-card flow, and the demographics flow (see "Architecture of `script.js`" below for what the logic does). Before assuming these run anywhere, check whether an HTML shell that includes them has been added — as of now, none exists in the repo.
- **`docs/image-and-scrollytelling-plan.md`** — a planning doc for image placement and animation in the `#policy-history` timeline (image inventory, per-node placement map, Ken Burns/reveal animation specs, sourcing gaps). Treat it as a to-do/spec against `index.html`'s timeline, not as documentation of current behavior — check the plan's status column and cross-reference against `index.html` before assuming an item is implemented.
- **`images/`** — image assets referenced by the timeline (era backgrounds, policy card photos, paper textures, ship sprite) and candidates cataloged in the plan doc above.

There is no other `.html` file in the repo — older standalone variants of the timeline (a dark-theme Lenis/RAF version, and an untracked two-column draft with a dossier-modal feature) have been removed. The dossier modal feature they prototyped (`openDossier(index)` / `.dossier-overlay`) is now merged directly into `index.html`.

## Architecture of the `#policy-history` timeline (`index.html`)

### Layout

Not a two-column split. `.tl-viz-wrapper` is a single fixed, full-viewport layer containing `<canvas id="river-canvas">` (the drawn river/ship) plus `<svg id="timeline-viz" viewBox="0 0 1200 800">` (path geometry, node positions). Everything else — policy cards, era narrative panels, the closing recap — is pre-rendered once and panned as overlay layers via CSS `transform: translateY()`, kept in sync with the camera.

- **Policy cards** (`.tl-card-layer`, built once for all policies into `tlCards[]`): alternate left/right of their node's screen X by index parity, using `CARD_GAP` / `EDGE_MARGIN` / `CARD_WIDTH`. Two treatments: `.margin-card` (quiet marginal annotation, most nodes) vs `.landmark-card` (torn-paper document with wax-stamp and statutory pull-quote, for policies flagged `landmark: true`) with a "read the dossier" affordance into the modal below.
- **Era narrative panels** (`#era-world-layer`) are placed **in SVG/world coordinates inside physical gaps opened in the river path itself** (`eraGapSVG`, `GAP_LEAD`) — the ship sails through them; they are not a fixed side column or full-screen cover.
- **Policy dossier modal** (`dossiers` object keyed by policy array index + `openDossier(index)` / `closeDossier()`): opens an archival-styled overlay (`.dossier-overlay` / `#dossierContent`) with `what/why/context/afterlife/included/excluded/links` fields, plus an "open in new tab" (`openDossierPage(index)`) that renders the same content as a standalone printable page. Falls back to an "empty/pending" state for any policy lacking an entry — dossier keys must stay index-aligned with `policies[]`.
- **Closing recap** (`#tl-recap`): a screen-fixed text overlay that fades in once the outro/estuary animation crosses `TEXT_APPEAR_AT`, alongside hiding the card/era layers.

### Scroll/animation engine (GSAP)

Loads D3 7.8.5 plus GSAP 3.13.0 with `ScrollTrigger`, `MotionPathPlugin`, `SplitText`. There is **one** animated driver: a proxy value `nav.frac` (0→1), tweened by a single master timeline —

```js
tlMasterTl = gsap.timeline({ paused: true, onUpdate: applyFrame })
```

— a **hero lead-in tween** (`nav.frac 0 → f_seam`, duration = `heroLeadDur`) prepended to the per-segment node-follow tweens (durations proportional to arc length, `segLen[i]`), plus appended outro/hold tweens. One `ScrollTrigger.create({ trigger: tlSectionEl, start:'top top', end:'bottom bottom', scrub: 1.2, animation: tlMasterTl })` — triggered on the whole `#policy-history` section (hero **and** timeline) — is the entire scroll-to-animation bridge. There is no manual scroll listener or RAF loop. `applyFrame` derives everything each frame from `tlMasterTl.time()`: ship position/rotation via `MotionPathPlugin.getPositionOnPath(rawPath, nav.frac, true)`, camera translate, river canvas redraw, and node active/passed state.

**One continuous river (hero → timeline).** There is no separate hero canvas — the removed `#hero-bridge-canvas` / `tlDrawHeroBridge` two-canvas bridge is gone. The real `#river-canvas` draws the whole river, whose geometry is `unifiedPoints = [...heroPoints, ...points]`: an upstream hero tail (`heroPoints`, arriving dead-vertical at the seam for C0/C1 continuity) prepended to the original timeline `points[]`. `points[]`/`policyPoints[]` indices are **unchanged** — node/era/gap math is preserved via `timelineStartIndex` (= `heroPoints.length`) and `timelineStartDistance`; `nodeAtLength`/`nodeFrac`/`segLen` are re-based onto the unified path but still indexed by the original point index (0 = seam). `f_seam` (= `timelineStartDistance/totalLen`) is the gate: `applyFrame` runs timeline semantics (node cosmetics, era bg, card reveals) only when `nav.frac >= f_seam`; below it is pure hero visual (river + ship + camera). The hero title/map fades are driven off `nav.frac` in `applyFrame` too, so `nav.frac` stays the single animated driver. `heroLeadDur` is sized to `HERO_SCROLL_FRAC` (intro height / total scrollable height) so the seam lands at the hero/timeline boundary with no dead-air gap. `.tl-viz-wrapper` is visible from load (opacity 1; `.is-active` gates only `pointer-events`), and `.tl-intro-section` is `background: transparent` so the fixed river shows through the hero.

**`onToggle` deliberately no-ops when deactivating with `self.progress >= 0.999`** — this is load-bearing; it prevents the sea/recap ending from being torn down the instant the pin releases at the bottom of the container. Don't "simplify" this away.

### Era system

Policies are grouped into chronological eras in the `eras` array. Each era has `id, title, intro, startIndex, endIndex, bg, narrative, periodClass, texture, image, dateRange, height` (fraction of total path length — all `height`s must sum to 1.0), `caption`.

Era-gap sizing (`eraGapSVG`) works by rendering each era's real narrative HTML into an off-screen hidden div matching the actual rendered column classes (`.era-cover-eyebrow`, `.era-cover-title`, `.era-text-body`), measuring `offsetHeight`, and sizing the river gap/panel from that. **If those class styles change, gap sizing silently breaks.**

`eraCurrentIndex` gates the background-color/counter update as the furthest-reached node's era changes; -1 when inactive.

### Key globals (timeline state)

```
tlInitialized, tlSectionEl, tlScrollTrigger, tlMasterTl, tlSectionActive
tlCardLayer, tlCards[], tlCardScaleY
eraCurrentIndex, tlEraWorldLayer, tlEraScaleY, tlEraCounter, tlVizWrapper
tlRecapLayer
riverCanvas, riverCtx
tlLastActiveIndex, tlLastPassedIndex   // dirty-check guard for node cosmetics
```
Plus locals inside `initPolicyTimeline()`: `nav = { frac }` (the GSAP-tweened driver), `T_FOLLOW_END`, `outroDur`, `recapEngaged`, `gapAnchors[]`, `eraGapSVG[]`.

### SVG coordinate system

- ViewBox: `0 0 1200 800`
- `CONNECTOR_LEN = 120` SVG units — the dashed line from node center to card edge
- Card/panel positions and `tlCardScaleY` / `tlEraScaleY` (SVG→screen Y scale) are captured **once** from `svgEl.getScreenCTM()` at init, not recomputed per frame — panning is pure `translateY`. Any resize needs a full teardown/reinit: `clearTimelineOverlays()`, kill `tlScrollTrigger` / `tlMasterTl`, `tlInitialized = false`, `ScrollTrigger.refresh()`.
- `getNodePathLengths` / `getPathDistanceToPoint` (arc-length-to-node mapping).
- The camera pans purely vertically (`camTx` stays 0); there is no horizontal-pin-to-`viewCenterX` model.

### Hard constraints (do not break)

1. **`nav.frac` is the only animated driver.** Everything else derives from `tlMasterTl.time()` inside `applyFrame`. Don't add a second animated value that also moves the ship/camera.
2. **`drawRiver()` redraws the canvas every frame** from `riverSamples`/`seaSamples` sampled once at init and pushed through the current camera transform + `getScreenCTM()`. Resizing requires both `resizeRiverCanvas()` and a full `initPolicyTimeline()` re-init.
3. **SplitText instances are cached** on the card element (`cardEl._titleSplit`, `cardEl._quoteSplit`) so scrolling back over a node doesn't re-split text. Don't drop the cache check.
4. **Landmark vs. margin card treatment is driven purely by `policy.landmark`** — it changes DOM structure and which `revealCard()` branch runs.
5. **Dossier keys must stay index-aligned with `policies[]`** — reordering/inserting policies without updating dossier keys silently misattributes dossier content.
6. **`ScrollTrigger`'s `onToggle` no-op at `progress >= 0.999`** (see above) must stay in place.

## Architecture of `script.js` (not currently wired into any page)

This file's code assumes a single-page experience with named screen sections (`s-opening`, `s-demo`, `s-cards`, `s-etymology`, `s-reasoning`, `s-pattern`) toggled via `goTo(id)`. There is no router or framework — all state is held in plain JS globals. No HTML file in the repo currently includes `script.js` or provides those section elements — treat this as logic waiting for its markup to be rebuilt, not as something you can exercise by opening a file in a browser.

**Key globals:**
- `PERSONAS` — array of 9 fictional immigrants with biography lines, a supporting fact, and a citation.
- `CA` — per-persona answer accumulator (`{emotion, immigrant, belongs, stay}`); drives card completion logic.
- `demos` — object holding user-selected demographics (age, gender, race, state, born).
- `demoStep` — which step of the 3-step demographics flow is current.
- `ci` — current card index.
- `policies` — a separate, smaller `policies` array than `index.html`'s timeline data (no `eras`, no `dossiers`, no `landmark`/`quote`/`stamp` fields) — do not assume the two are kept in sync.

**Card flow:** `startCards()` → `renderCard()` → user answers four beats (emotion + three judgment questions) → `nextCard()`. When all personas are exhausted, the app advances to etymology. `isCardComplete(index)` checks all four beats are non-null.

**Data submission:** `submitResults()` posts the completed `CA` array plus `demos` to a Google Apps Script endpoint (`SHEET_URL`) as JSON.

`style.css` holds the CSS for the same sections; it is likewise unused until an HTML shell includes it.

## Design tokens

`index.html`'s timeline uses a light "editorial" theme:
- `--ink / --ink-mid / --ink-soft / --ink-faint` — text hierarchy on light backgrounds
- `--paper / --paper-mid` — off-white backgrounds
- `--brass / --blue / --red / --green / --river / --sea` — accent colors
- `--serif` — Lora (editorial body)
- `--body` — DM Sans (UI chrome)

`style.css` (unused pending its HTML shell) defines its own token set for the persona-cards/demographics screens — check it directly rather than assuming it matches the timeline's tokens above.

## Working on the timeline

`index.html`'s `policies` array carries `landmark: true`, `quote`, `stamp` on select entries — these drive the landmark card treatment and dossier availability. The `lean` value (−1 to +1) determines lane placement (`closes` / `mixed` / `opens`, thresholds ±0.25 via `getPolicyDoorLane`) and node glow intensity; it also drives the animated path draw order. `script.js` has its own, smaller `policies` array with the same `lean` concept but not the timeline-specific fields — don't assume edits to one belong in the other unless you're deliberately syncing shared policy content.

The `eras` array currently only exists in `index.html`.

## Running locally

Open `index.html` directly in a browser to run the timeline — no server needed unless cross-origin issues arise. `script.js` / `style.css` have no HTML entry point yet, so there is nothing to open for that part of the experience.
