# Hero Section Redesign — River/Map/Ship Intro

Status: approved for planning
Scope: `index.html` only (`.tl-intro-section` and its scroll behavior)

## Goal

Redesign the existing hero (`.tl-intro-section`, the full-height intro block that
precedes the pinned `#policy-history` timeline) so it visually introduces the
river/ship motif before the user ever reaches the pinned timeline. The map, ship,
and river should read as the *source* the timeline's river flows out of.

## Non-goals

- No changes to the pinned `#policy-history` timeline engine (`tlMasterTl`,
  `nav.frac`, `applyFrame`, the real `ship` element, `ScrollTrigger` on
  `.tl-timeline-container`). That system is out of scope and must not be touched.
- No pixel-perfect handoff between the hero's decorative ship and the timeline's
  real ship — continuity is achieved through matching color, direction, and
  vertical position, not shared state.
- No new build tooling, no new npm/CDN dependencies. Everything ships as
  additional inline `<style>`/`<script>` in `index.html` plus existing/added
  files under `images/`.

## Current state (for reference)

- `.tl-intro-section` (`index.html:42`): `min-height: 100vh`, flex-centered,
  background `linear-gradient(180deg, var(--paper) 0%, var(--paper-mid) 100%)`.
  Not pinned/scroll-jacked — it scrolls away normally.
- `.tl-intro-inner` (`index.html:55`): title block, fades/slides in once via a
  one-shot `IntersectionObserver` (`index.html:2613-2623`) toggling `.is-visible`.
  No scroll-scrubbed behavior today.
- `.tl-timeline-container` (`index.html:138`): `min-height: 1400vh`, holds the
  pinned `.tl-viz-wrapper` (canvas river + SVG node path), driven by the single
  `ScrollTrigger` + `tlMasterTl` engine described in `CLAUDE.md`.
- Design tokens already in place and reused as-is: `--paper` / `--paper-mid`
  (background), `--river` / `--sea` (`#38afcd`, both currently the same value).
- Existing assets to reuse:
  - `images/boat.png` — the exact ship image already used as `SHIP_SRC` in the
    real timeline (`index.html:1466`). Reused for the hero ship for visual
    consistency.
  - `images/cloud.png` (2000×2000 PNG) — reused for drifting clouds.
  - `images/bird.mp4` (1280×720, h264, 10s loop, 24fps) — a single illustrated
    seagull flapping in place against a flat near-white background (no alpha
    channel). Reused for birds; background removed visually via CSS blend mode
    (see Assets section) rather than server-side video editing.
  - `images/ripple.svg` — inspected, not a good fit for the water-movement
    effect (static ripple graphic, not a tileable texture); not reused.
- No existing asset for a US map silhouette. None found in `images/` matching
  that purpose — an original, simplified inline SVG path is created for this
  feature.

## Design

### 1. Structure

`.tl-intro-section` is redesigned in place — not replaced with a new section,
not moved. Its height increases from `min-height: 100vh` to `min-height: 160vh`
to create scroll room for the transition described below (the extra height is
scroll-through room, not extra visible content — the section still has one
screen-height "resting" view at its top).

New layers inside `.tl-intro-section`, back to front:

1. `.hero-sky` — absolutely positioned, full-bleed within the hero. Holds the
   drifting cloud images and the bird video wrappers.
2. `.hero-river` — an SVG (or a `<div>` containing an inline SVG) holding:
   - the US silhouette path
   - the river path that starts at the silhouette's southern edge and curves
     down to the bottom of `.tl-intro-section`
   Constrained to `max-width: 880px` (matches `.tl-intro-inner`'s existing
   `max-width`), centered.
3. `.hero-ship` — an `<img src="images/boat.png">` (or an SVG `<image>`,
   matching the real timeline's approach) positioned at the silhouette's
   center.
4. `.tl-intro-inner` — existing title/subtitle block, unchanged content,
   restyled only as needed for legibility over the new background layers
   (e.g. the map sits *behind* the title at low opacity, never competing with
   text contrast).

`.tl-scroll-cue` (existing "Scroll" affordance) is kept, repositioned if needed
to sit below the new visual stack.

### 2. Visual treatment

- **Background color**: unchanged — the hero keeps the same
  `linear-gradient(var(--paper) 0%, var(--paper-mid) 100%)` used elsewhere on
  the page. No new background color is introduced.
- **US silhouette**: an original, simplified/stylized continental-US outline
  authored as inline SVG path data (decorative, not survey-accurate). Filled
  with `var(--river)`. Width capped to the 880px text-block max-width, centered
  horizontally in the hero.
- **River**: a single path, stroked in `var(--river)`, starting inside the
  silhouette's lower edge and flowing down to the bottom edge of
  `.tl-intro-section`, so it visually continues into `.tl-timeline-container`
  below (where the real timeline's own river begins its fade-in).
- **Ship**: `images/boat.png`, centered inside the silhouette. Idle state: a
  CSS keyframe animation applying a small oscillating `rotate()` +
  `translateY()` (a gentle rock, period ~4-6s, ease-in-out, infinite) to
  simulate floating.
- **Water movement inside the map**: an SVG filter (`feTurbulence` +
  `feDisplacementMap`) applied only to the silhouette fill (via clip-path or
  filter region scoped to the shape), animated with very low frequency/scale so
  the fill subtly shimmers. Kept subtle enough not to distract from the title.
- **Clouds**: 2-3 `<img src="images/cloud.png">` instances in `.hero-sky`, each
  with its own `animation-duration` / `animation-delay` / horizontal offset /
  low opacity, drifting left-to-right (or right-to-left) via a CSS
  `translateX` keyframe looping past the section width.
- **Birds**: 1-2 wrapper `<div>`s in `.hero-sky`, each containing a small
  (~60-90px wide) `<video>` sourced from `images/bird.mp4`
  (`autoplay muted loop playsinline`), with `mix-blend-mode: multiply` (or
  `darken`, whichever tests cleaner against `var(--paper)`) so the video's flat
  near-white background visually disappears into the page background. The
  wrapper (not the video) is animated along a slow, gently curved CSS path
  (translateX/Y keyframes) across `.hero-sky`, independent of the video's own
  10s internal flap loop — the two are not synced and don't need to be.

### 3. Scroll-driven transition

A dedicated `ScrollTrigger` scoped to `.tl-intro-section` itself:

```js
ScrollTrigger.create({
  trigger: '.tl-intro-section',
  start: 'top top',
  end: 'bottom top',
  scrub: true,
  animation: heroTl, // a small GSAP timeline, local to this feature
});
```

`heroTl` drives, over that single scroll range:

- `.tl-intro-inner` opacity 1 → 0 (title fades out as the user scrolls in)
- `.hero-river` (map + river) opacity from a low resting value (map and river
  "visible but highly transparent") → fully opaque
- the ship: crossfades from its idle CSS rock (paused once the scroll-driven
  phase takes over) to being carried along the river's path via
  `MotionPathPlugin.getPositionOnPath` on the **hero's own, local** river path
  (a separate `MotionPathPlugin` call/path object from the real timeline's —
  no shared state), ending at the bottom of `.hero-river`'s path, i.e. the
  bottom of `.tl-intro-section`, timed to arrive there as `end: 'bottom top'`
  is reached.

This is a self-contained ScrollTrigger + timeline, entirely separate from
`tlScrollTrigger` / `tlMasterTl` / `nav.frac` / the real `ship` element defined
later in the file. It does not read or write any of that state. This matters
because `CLAUDE.md` calls out `nav.frac` as the *only* driver for the real
timeline's ship/camera — this feature adds a second, independent driver, but
for a completely different DOM subtree, so that constraint (which is scoped to
the pinned timeline) isn't violated.

### 4. Handoff to the pinned timeline

No shared coordinates or shared elements between `.hero-ship`/`.hero-river` and
the real timeline's `ship`/river canvas. Continuity is visual only: same
`var(--river)` color, same horizontal centering, same downward flow direction,
and the hero's river terminating right where `.tl-timeline-container` begins
(where the real timeline's own river fade-in already starts). This is
sufficient given the project's non-goal of not touching the real timeline
engine.

### 5. Responsiveness / performance

- All new elements sit inside `.tl-intro-section`, which the site already
  treats as full-width; the silhouette/river/ship group is capped at 880px so
  it degrades the same way the title text does at narrow viewports.
  Mobile-specific sizing (if the 880px cap looks cramped at very small
  viewports) is decided during implementation, following the same responsive
  pattern already used for `SHIP_SIZE` (`isMobileTimeline` ternary).
- Bird `<video>` elements: `playsinline muted loop autoplay`, small dimensions,
  to keep this cheap on mobile Safari (which requires `playsinline`+`muted`
  for autoplay). No visible audio track needed (`bird.mp4` — verify muted
  attribute suppresses any audio; if the source has no meaningful audio this
  is moot).
- The `feTurbulence` water-shimmer filter is scoped to a small, capped-width
  element — not full-viewport — to keep paint cost low.
- No new CDN scripts. Reuses GSAP/ScrollTrigger/MotionPathPlugin already
  loaded for the main timeline (`index.html:781-784`).

## Open questions / decisions deferred to implementation

- Exact rock-animation timing constants (duration, rotation degrees) — tune
  visually during implementation, keep "subtle" per the brief.
- Exact opacity resting value for the "visible but highly transparent" initial
  map/river state — tune visually (e.g. starting around 0.12-0.2, ending at
  ~0.9-1.0), not a hard product requirement.
- Whether `mix-blend-mode: multiply` or `darken` looks cleaner against
  `var(--paper)` for the bird video — decide by visual comparison during
  implementation.
