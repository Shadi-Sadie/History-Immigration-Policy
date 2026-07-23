# Unified River (Hero → Timeline) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans or superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the hero river and the timeline river one continuous canvas, one river geometry, and one scroll/camera system — removing the separate `#hero-bridge-canvas` two-canvas bridge.

**Architecture:** Extend the real timeline path upstream into the hero by prepending a hero tail to the geometry that feeds the SVG motion path (`rawPath`) and the canvas polyline (`riverSamples`). Keep the original `points[]` / `policyPoints[]` indices untouched; introduce `timelineStartIndex` / `timelineStartDistance` so all timeline semantics (node activation, eras, gaps, cards, progress) are measured from the old seam and remain identical. Replace the two separate ScrollTriggers (`heroST` + timeline trigger) with **one** master timeline (a hero lead-in tween prepended to the existing per-segment tweens) driven by **one** ScrollTrigger on `#policy-history`. Make the fixed `.tl-viz-wrapper` visible from page load and de-occlude it during the hero.

**Tech Stack:** Vanilla JS, D3 7.8.5, GSAP 3.13.0 (ScrollTrigger + MotionPathPlugin), single `index.html` (inline `<style>`/`<script>`). No build, no tests — verification is live browser instrumentation via the `run-history-immigration-policy` skill / a headless browser.

## Global Constraints

- **Single animated driver:** `nav.frac` (0→1) remains the ONLY animated value. The ship, camera, river, nodes, cards, eras all derive from `tlMasterTl.time()` inside `applyFrame`. Do not add a second animated value that moves the ship/camera. (CLAUDE.md Hard Constraint #1)
- **`drawRiver()` redraws every frame** from pre-sampled arrays through the camera transform + `getScreenCTM()`. Resizing requires `resizeRiverCanvas()` + full `initPolicyTimeline()` re-init. (Constraint #2)
- **Dossier keys stay index-aligned with `policies[]`** — do not reorder/insert policies. (Constraint #5)
- **`ScrollTrigger` `onToggle` no-op at `self.progress >= 0.999`** must stay. (Constraint #6)
- **`eras[].height` must still sum to 1.0**; `eraGapSVG` gap-sizing measures off-screen `.era-cover-eyebrow`/`.era-cover-title`/`.era-text-body` — do not change those class styles.
- **Timeline semantics engage only at/after the seam.** Everything before `nav.frac >= f_seam` (= `timelineStartDistance / totalLen`) is pure hero visual: river + ship + camera on the extended path, no node cosmetics, no era bg, no card reveals.
- **Mobile is in scope** — check `(max-width: 768px)` behavior, not only desktop.

---

## File Structure

Only one file changes: `index.html`. Changes cluster in four regions:

- **CSS `<style>`** (lines ~42–300): intro/viz layering + visibility (Task 4).
- **HTML `<body>`** (lines ~869–920): remove hero bridge canvas / hero SVG river+ship, keep map/clouds/title (Task 4).
- **`initPolicyTimeline()`** (lines ~1876–2930): geometry unification, frac/segLen remap, master timeline lead-in, single ScrollTrigger, `applyFrame` gating + hero fades (Tasks 1–3).
- **`DOMContentLoaded` hero engine** (lines ~2933–3060): delete `heroST` + bridge painting (Task 3).

New named variables (per prompt's implementation guidance):
`heroPoints[]`, `unifiedPoints[]`, `timelineStartIndex`, `timelineStartDistance`, `heroRiverDistance`, `timelineRiverDistance`, `heroLeadDur`, `HERO_SCROLL_FRAC`.

---

## Task 0: Branch + baseline capture

**Files:** none modified.

- [ ] **Step 1: Confirm working branch**

Run: `git rev-parse --abbrev-ref HEAD`
Expected: `refactor/gsap-timeline-engine` (already a feature branch — work here; do NOT branch off main).

- [ ] **Step 2: Capture BEFORE screenshots at the six scroll checkpoints**

Use the `run-history-immigration-policy` skill (or a headless browser) to load `index.html` and screenshot at `scrollY` = 0, 300, 600, 900, hero-end (`document.querySelector('.tl-intro-section').offsetHeight`), and first timeline activation. Save to `scratchpad/before-*.png`. These are the visual-regression reference for Task 5.

- [ ] **Step 3: Commit nothing** — this is a read-only baseline step.

---

## Task 1: Extend river geometry into the hero (one path, one river)

**Files:**
- Modify: `index.html` — `initPolicyTimeline()`, path-build region (~2002–2160) and the RIVER SAMPLES region (~2124–2133).
- Modify: `index.html` — arc-length/frac region (~2387–2395).

**Interfaces:**
- Produces: `heroPoints[]` (upstream world-coord vertices ending just above `points[0]`), `unifiedPoints = [...heroPoints, ...points]`, `timelineStartIndex = heroPoints.length`, `timelineStartDistance` (arc length of the seam on the unified path), `heroRiverDistance` (= `timelineStartDistance`), `timelineRiverDistance` (= `totalLen - timelineStartDistance`). `nodeFrac[]`, `segLen[]`, `nodeAtLength[]` are re-based onto the unified path but still indexed by the ORIGINAL `points`/`policyPoints` index (0 = seam node).
- Consumes: existing `points[]`, `pathDataCenterX`, `H`, `line` (d3 cardinal generator), `getNodePathLengths`, `animPath`.

- [ ] **Step 1: Build the hero tail as real geometry (after `const pathBottomY = ...`, before `const line = ...` at ~2004).**

The tail rises above the seam (`points[0]`, at `x=pathDataCenterX, y=H*0.15`) and arrives dead-vertical so the concatenated cardinal spline has no position/tangent kink (the seam neighborhood `points[0]→points[1]` is already vertical — both are gap waypoints at `pathDataCenterX`).

```js
  // ── HERO UPSTREAM TAIL — real geometry, prepended to the motion/visual path.
  // Ends just above points[0] (the seam) travelling dead-vertical, so the
  // cardinal spline through [...heroPoints, ...points] has C0/C1 continuity at
  // the seam (points[0]→points[1] is already vertical at pathDataCenterX).
  // NOTE: names are heroSeamPt / HERO_TAIL_UP / HERO_TAIL_STEPS (NOT heroSeam /
  // HERO_TAIL_SPAN) to avoid a duplicate-`const` collision with the old bridge
  // block below, which is not deleted until Task 3.
  const heroSeamPt = points[0];               // == (pathDataCenterX, H*0.15)
  const HERO_TAIL_UP = 640;                   // viewBox units authored ABOVE the seam
  const HERO_TAIL_STEPS = 40;
  const heroPoints = [];
  for (let i = 0; i < HERO_TAIL_STEPS; i++) {   // note: < not <=, so we do NOT duplicate the seam
    const tt = i / HERO_TAIL_STEPS;             // 0 = top of tail, →1 approaches seam
    const y = heroSeamPt.y - HERO_TAIL_UP * (1 - tt);
    const decay = (1 - tt) * (1 - tt);
    const meander = Math.sin((1 - tt) * Math.PI * 1.6) * 52 * decay;
    heroPoints.push({ x: heroSeamPt.x + meander, y, isHero: true });
  }
  const timelineStartIndex = heroPoints.length;   // index of the seam within unifiedPoints
  const unifiedPoints = [...heroPoints, ...points];
```

- [ ] **Step 2: Feed the unified points into the path `d`.**

Change the `pathData` source from `points` to `unifiedPoints` (the visual bg/overview paths and the motion path all read this `d`):

```js
  const line = d3.line().x(d => d.x).y(d => d.y).curve(d3.curveCardinal.tension(0.35));
  const pathData = line(unifiedPoints);   // was: line(points)
```

Leave `points`, `policyPoints`, `gapAnchors`, node rendering (which binds `policyPoints`) UNTOUCHED — nodes still render only for real policies.

- [ ] **Step 3: Re-base arc-length measurements onto the unified path.**

Where `totalLen` / `nodeAtLength` are computed (~2121–2122), measure per-UNIFIED-vertex then slice back to timeline-relative indices:

```js
  const totalLen = animPath.node().getTotalLength();
  const unifiedAtLength = getNodePathLengths(animPath.node(), unifiedPoints, totalLen);
  const timelineStartDistance = unifiedAtLength[timelineStartIndex];   // seam arc length
  const heroRiverDistance = timelineStartDistance;
  const timelineRiverDistance = totalLen - timelineStartDistance;
  // nodeAtLength stays indexed by ORIGINAL points index (0 = seam) — just offset
  // into the unified measurements so downstream node math is unchanged in shape.
  const nodeAtLength = points.map((_, i) => unifiedAtLength[timelineStartIndex + i]);
```

- [ ] **Step 4: Sample the river over the WHOLE unified path (~2128–2133).**

`riverSamples` now covers hero tail + timeline in one polyline — the single `#river-canvas` draws the entire river:

```js
  const riverSampleCount = Math.max(160, Math.floor(totalLen / 6));
  const riverSamples = new Array(riverSampleCount + 1);
  for (let i = 0; i <= riverSampleCount; i++) {
    const pt = animPath.node().getPointAtLength((i / riverSampleCount) * totalLen);
    riverSamples[i] = { x: pt.x, y: pt.y };
  }
```

The sea tail (`seaLast = riverSamples[last]`, `seaSamples`) is unchanged — the last sample is still the last timeline node's downstream end.

- [ ] **Step 5: Re-base `nodeFrac` / `segLen` (~2387–2395).**

`rawPath` is now the unified path. Node fractions and per-segment durations must map original point index → unified arc length:

```js
  const rawPath = MotionPathPlugin.getRawPath(animPath.node());
  MotionPathPlugin.cacheRawPathMeasurements(rawPath);
  // nodeFrac[i] is the unified-path fraction of ORIGINAL point i (i=0 is the seam).
  const nodeFrac = nodeAtLength.map(l => l / totalLen);
  const f_seam = nodeFrac[0];                          // = timelineStartDistance/totalLen

  const segLen = [];
  for (let i = 0; i < points.length - 1; i++) {
    segLen.push(Math.max(1, nodeAtLength[i + 1] - nodeAtLength[i]));
  }
```

- [ ] **Step 6: Verify geometry in-browser (instrumented).**

Open `index.html`, and in the console evaluate (via the run skill's browser eval):

```js
// timelineStartDistance must be > 0 and < totalLen; f_seam a small positive fraction.
[timelineStartDistance, totalLen, timelineStartDistance/totalLen]
```

Expected: `timelineStartDistance` ≈ a few hundred; `f_seam` roughly 0.01–0.05 (hero is a small arc-length fraction — that is expected; scroll pacing is handled in Task 2, NOT by arc length). Also confirm the SVG faint guide path visibly extends above the first node. The page will look partly broken until Task 2/3 — that is acceptable at this checkpoint; the gate is only that geometry/measurements are sane.

- [ ] **Step 7: Commit**

```bash
git add index.html docs/superpowers/plans/2026-07-23-unified-river-hero-timeline.md
git commit -m "feat(hero): extend river geometry upstream into a single unified path"
```

---

## Task 2: One master timeline with a scroll-matched hero lead-in

**Files:**
- Modify: `index.html` — MASTER GSAP TIMELINE region (~2809–2831) and SINGLE SCROLL SYSTEM region (~2833–2840).
- Modify: `index.html` — `T_FOLLOW_END` / `applyFrame` ship default (~2404, ~2422).

**Interfaces:**
- Consumes: `nodeFrac[]`, `segLen[]`, `f_seam`, `timelineStartDistance` (Task 1).
- Produces: `heroLeadDur`, `HERO_SCROLL_FRAC`; `tlMasterTl` now starts at `nav.frac = 0` (top of hero tail) and reaches `f_seam` at the hero/timeline boundary; `tlScrollTrigger` triggers on `#policy-history`.

- [ ] **Step 1: Prepend the hero lead-in tween and re-derive durations (~2809–2831).**

The hero lead-in occupies the same fraction of the master timeline as the hero section occupies of the total scrollable height, so the seam lands exactly at the hero/timeline boundary (no dead air). Read the real ratio from the CSS heights so it stays correct if they change:

```js
  // ── THE MASTER GSAP TIMELINE ─────────────────────────────────────────
  if (tlMasterTl) { tlMasterTl.kill(); tlMasterTl = null; }
  tlMasterTl = gsap.timeline({ paused: true, onUpdate: applyFrame });

  // Timeline (node-follow) segments first, to size outro/hold as before.
  const nodesDur = segLen.reduce((a, b) => a + b, 0);
  const outroDurBase = Math.max(1, nodesDur * 0.12);
  const holdDurBase  = Math.max(1, nodesDur * 0.18);

  // Hero lead-in duration: match the hero's share of total scroll height so the
  // seam (nav.frac = f_seam) is reached exactly when the hero scrolls away.
  const introH = document.querySelector('.tl-intro-section').offsetHeight;
  const containerH = containerEl.offsetHeight;
  const HERO_SCROLL_FRAC = introH / (introH + containerH);   // e.g. ~0.078
  const restDur = nodesDur + outroDurBase + holdDurBase;
  const heroLeadDur = restDur * HERO_SCROLL_FRAC / (1 - HERO_SCROLL_FRAC);

  // 1) hero lead-in: nav.frac 0 (top of hero tail) → f_seam (old timeline start)
  tlMasterTl.to(nav, { frac: f_seam, duration: heroLeadDur, ease: 'none' });

  // 2) the original per-segment node-follow tweens (unchanged shape)
  for (let i = 0; i < points.length - 1; i++) {
    const touchesGap = points[i].isGap || points[i + 1].isGap;
    tlMasterTl.to(nav, {
      frac: nodeFrac[i + 1],
      duration: segLen[i],
      ease: touchesGap ? 'none' : 'power1.inOut'
    });
  }

  T_FOLLOW_END = tlMasterTl.duration();          // = heroLeadDur + nodesDur (ship at last node)
  outroDur = outroDurBase;
  tlMasterTl.to({ _outro: 0 }, { _outro: 1, duration: outroDur, ease: 'none' });
  tlMasterTl.to({}, { duration: holdDurBase });
```

- [ ] **Step 2: Point the single ScrollTrigger at the whole section (~2835–2840).**

```js
  if (tlScrollTrigger) { tlScrollTrigger.kill(); tlScrollTrigger = null; }
  tlScrollTrigger = ScrollTrigger.create({
    trigger: tlSectionEl,        // #policy-history — spans hero + timeline container
    start: 'top top',
    end: 'bottom bottom',
    scrub: 1.2,
    animation: tlMasterTl,
    onToggle: self => {
      // (unchanged body — keep the progress>=0.999 no-op)
```

Leave the entire `onToggle` body as-is.

- [ ] **Step 3: Default the ship to the top of the hero tail (~2422).**

So the pre-follow default frame (only at `t≈0`) sits at the hero tail top, not the seam:

```js
    let shipX = unifiedPoints[0].x, shipY = unifiedPoints[0].y, shipAngle = 0;
```

- [ ] **Step 4: Verify scroll→frac mapping (instrumented).**

Load `index.html`. Via browser eval at increasing `scrollY`, read `nav.frac` and `tlMasterTl.time()`. Confirm:
- `scrollY = 0` → `nav.frac ≈ 0`.
- Scrolling through the hero → `nav.frac` rises slowly toward `f_seam`.
- At `scrollY = introH` (hero end) → `nav.frac ≈ f_seam` (within a few %).
- Node cosmetics/eras will still be mis-gated (fixed in Task 3) — the gate here is ONLY the frac mapping and seam alignment.

- [ ] **Step 5: Commit**

```bash
git add index.html
git commit -m "feat(hero): drive hero+timeline from one master timeline via a scroll-matched lead-in"
```

---

## Task 3: Gate timeline semantics behind the seam; fold in hero fades; delete the bridge

**Files:**
- Modify: `index.html` — `applyFrame` node/era/card region (~2465–2620).
- Modify: `index.html` — delete the HERO → TIMELINE RIVER BRIDGE block (`tlDrawHeroBridge`, `heroRiverSamples`, `heroCamStart`, etc.) at ~2164–2279.
- Modify: `index.html` — `DOMContentLoaded` hero engine (~2933–3060): delete `heroST`, `paintHeroBridge`, `hideHeroBridge`, `heroTick`, `sizeHeroCanvas`, `heroCanvas`/`heroCtx`.

**Interfaces:**
- Consumes: `nav.frac`, `f_seam`, `points`, `policyPoints`, hero DOM nodes (`.tl-intro-inner`, `.tl-scroll-cue`, `#hero-map-river-group`).
- Produces: `inTimeline` gate; hero DOM opacity driven by `applyFrame`.

- [ ] **Step 1: Add the seam gate at the top of the node/era work in `applyFrame`.**

Immediately after `shipX/shipY/shipAngle` are computed (~2435), derive the gate and drive the hero DOM fade from the same driver:

```js
    // Timeline semantics engage only from the seam onward. Before it we are in
    // the hero: pure river+ship+camera on the extended path.
    const inTimeline = nav.frac >= f_seam - 1e-4;

    // Hero DOM fades, driven by the SAME master timeline (no second driver).
    // heroP: 0 at page top → 1 at the seam.
    const heroP = f_seam > 0 ? Math.min(1, Math.max(0, nav.frac / f_seam)) : 1;
    if (tlHeroInner)   tlHeroInner.style.opacity = String(1 - Math.min(1, heroP / 0.5));
    if (tlHeroCue)     tlHeroCue.style.opacity   = String(1 - Math.min(1, heroP / 0.5));
    if (tlHeroMapGrp)  tlHeroMapGrp.style.opacity = String(0.16 + 0.84 * Math.min(1, heroP / 0.65));
```

(Cache `tlHeroInner = document.querySelector('.tl-intro-inner')`, `tlHeroCue = document.querySelector('.tl-scroll-cue')`, `tlHeroMapGrp = document.getElementById('hero-map-river-group')` once near the other cached layer globals in `initPolicyTimeline`, e.g. beside `tlVizWrapper` at ~2797. Guard each with `if (...)`.)

- [ ] **Step 2: Gate node activation + era sync + card reveals behind `inTimeline`.**

Wrap the NODE STATE block (`passedIndex`/`activeIndex` loop, ~2475–2486) so that when `!inTimeline` both stay `-1`:

```js
    let passedIndex = -1, activeIndex = -1;
    if (followPhase && inTimeline) {
      // ...existing passedIndex / activeIndex loops unchanged...
    }
```

The ERA SYNC block already keys off `passedIndex`/`activeIndex` and resets `eraCurrentIndex = -1` when they are `-1`, so gating the indices also suppresses era bg during the hero. Confirm the card-reveal path also keys off `activeIndex` (it does via the dirty-check + reveal). No further change needed there.

- [ ] **Step 3: Delete the HERO → TIMELINE RIVER BRIDGE block (~2164–2279).**

Remove the entire commented block that defines the OLD `heroSeam` (~2180), `HERO_TAIL_SPAN`, `HERO_TAIL_SAMPLES`, `heroRiverSamples`, `heroCamTy0`, `heroCamStart`, `heroShipImg`, and `window.tlDrawHeroBridge = function(...){...}`. Task 1 deliberately used different names (`heroSeamPt`/`HERO_TAIL_UP`/`HERO_TAIL_STEPS`), so there is no collision and nothing of Task 1's needs renaming here.

- [ ] **Step 4: Delete the hero bridge engine in `DOMContentLoaded` (~2938–3060).**

Remove `heroCanvas`/`heroCtx`, `sizeHeroCanvas`, `paintHeroBridge`, `hideHeroBridge`, `heroProgress`/`heroRAF`/`heroTick`/`startHeroTick`/`stopHeroTick`, and the `heroST = ScrollTrigger.create({ trigger: '.tl-intro-section', ... })`. Keep the resize handler and `initPolicyTimeline()` invocation. Keep hiding the legacy `#hero-ship` (it is removed from the DOM in Task 4, so this line can also go). Remove the now-dead `window.addEventListener('resize', sizeHeroCanvas)` if present.

- [ ] **Step 5: Verify semantics gate (instrumented).**

Load `index.html`. Via browser eval:
- During hero (`nav.frac < f_seam`): `eraCurrentIndex === -1`, `document.body.style.backgroundColor === ''`, no `.policy-item[data-shown="1"]`, hero title/map fading as you scroll.
- Just past the seam: first era bg appears, node 0 activates, Era 1 panel visible.
- `typeof window.tlDrawHeroBridge === 'undefined'` (bridge deleted).

- [ ] **Step 6: Commit**

```bash
git add index.html
git commit -m "feat(hero): gate timeline semantics at the seam, fold hero fades into applyFrame, remove bridge canvas"
```

---

## Task 4: Make the single river layer visible through the hero; strip hero-only river/ship

**Files:**
- Modify: `index.html` CSS (~42–300).
- Modify: `index.html` HTML body (~869–920).

**Interfaces:**
- Consumes: nothing new.
- Produces: `.tl-viz-wrapper` visible from load; intro no longer occludes the fixed canvas; hero keeps map/clouds/title only.

- [ ] **Step 1: Make the fixed viz layer visible from page load.**

The `.policy-history-section.is-active` gate (opacity 0→1) currently hides the canvas until the timeline trigger activates. With one trigger on `#policy-history`, `is-active` flips on at hero top — but to be robust, make the wrapper visible by default and keep `pointer-events` gated:

```css
.tl-viz-wrapper {
  position: fixed; top: 0; left: 0; width: 100%; height: 100vh;
  z-index: 1;                 /* behind hero text/map/clouds, above intro bg */
  display: flex; align-items: center; justify-content: center;
  opacity: 1;                 /* was 0 — visible from load */
  pointer-events: none;
}
.policy-history-section.is-active .tl-viz-wrapper { pointer-events: auto; }
```

- [ ] **Step 2: De-occlude the canvas during the hero.**

`.tl-intro-section` currently has `z-index: 50` + opaque `background: var(--paper)`, which paints over the fixed wrapper. Make its background transparent and lower it so the fixed river shows through, while its inner text/map/clouds stay above via their own `z-index`:

```css
.tl-intro-section {
  position: relative;
  min-height: 118vh;
  text-align: center;
  z-index: 2;                 /* was 50 */
  background: transparent;    /* was var(--paper) — let the river show through */
  color: var(--ink);
  font-family: 'Crimson Text', serif;
  overflow: visible;
}
```

Because the `.tl-viz-wrapper` (`z-index:1`) is inside the sibling `.tl-timeline-container` (`z-index:auto`), and `.tl-intro-section` now has `z-index:2` with a transparent background, the hero text (`.tl-intro-inner` z-index 3, `.tl-scroll-cue` z-index 3), the map/clouds (`.hero-river-wrap` z-index 2, `.hero-sky` z-index 1) still layer above the river. If the river appears ON TOP of hero text during verification, give `.tl-timeline-container` an explicit `z-index: 0` so the whole fixed layer sits under the intro's stacking context, and confirm hero text remains readable.

- [ ] **Step 3: Remove the hero bridge canvas element (~903).**

Delete: `<canvas id="hero-bridge-canvas" aria-hidden="true"></canvas>` and its CSS rule (`#hero-bridge-canvas { ... }`, ~218–226).

- [ ] **Step 4: Remove the hero's own river path + SVG ship; keep the US map, clouds, birds, title.**

In the `#hero-river-svg`, delete `<path id="hero-river-path" .../>` (~895–897) and `<image id="hero-ship" .../>` (~899–900). Keep `#hero-us-map` and the `#hero-map-river-group` wrapper (Task 3 fades the group). Delete the now-orphan CSS: `#hero-river-path { opacity: 0.35; }` (~230), `@keyframes heroShipRock` + `.hero-ship-idle` (~232–241). The real river canvas + real SVG `.tl-ship` now provide the river and boat.

- [ ] **Step 5: Verify layering (instrumented + visual).**

Load `index.html`. At `scrollY = 0`: the blue river canvas is visible with the ship near screen center; the US map (faint), clouds/birds, and the intro title are all visible and layered above the river; no opaque paper block hides the canvas. Screenshot and compare structure to the Task-0 baseline. Confirm `document.getElementById('hero-bridge-canvas') === null` and `document.getElementById('hero-river-path') === null`.

- [ ] **Step 6: Commit**

```bash
git add index.html
git commit -m "feat(hero): reveal the single river canvas through the hero; strip hero-only river/ship/bridge markup"
```

---

## Task 5: Full six-point browser verification, seam/dead-air tuning, mobile

**Files:**
- Modify (tuning only, if needed): `index.html` — `.tl-intro-section { min-height }` (~44) and/or the `heroP` fade thresholds (Task 3 Step 1).

- [ ] **Step 1: Instrument and read all six checkpoints (desktop).**

Load `index.html` at a desktop viewport. For `scrollY` ∈ {0, 300, 600, 900, hero-end, first-activation}, capture via browser eval + screenshot:
- which canvas is drawing (`#river-canvas` only; `#hero-bridge-canvas` must not exist),
- river visible? (`getComputedStyle(document.querySelector('.tl-viz-wrapper')).opacity === '1'`),
- ship screen position (`document.querySelector('.tl-ship').getBoundingClientRect()`),
- title/map/era visibility (`.tl-intro-inner` opacity; `eraCurrentIndex`; body backgroundColor),
- `nav.frac` (changing monotonically with scroll),
- Era 1 appears without a blank gap after the hero.

Record a table (checkpoint × property) in `scratchpad/verify.md`.

- [ ] **Step 2: Confirm seam continuity.**

Scroll slowly across the hero/timeline boundary and confirm: no visible jump/kink in the river at the seam, no camera snap, ship heading continuous, Era 1 panel arrives right as the hero fades (no 300–400px empty-river zone). If a dead-air gap remains, adjust `HERO_SCROLL_FRAC` alignment by tuning `.tl-intro-section { min-height }` (shorter hero) OR stretch the `heroP` fade window (Task 3 Step 1) — do not leave a blank handoff.

- [ ] **Step 3: Mobile check `(max-width: 768px)`.**

Reload at a ≤768px viewport (the code branches on `isMobileTimeline`). Repeat the six-point reads. Confirm the river is visible through the hero, the seam is continuous, `heroPoints` still meets the seam vertically (mobile `tlXSpread`/`tlYSpan` differ but the seam is at `pathDataCenterX`), and Era 1 has no dead air. Note any mobile-only issue in `scratchpad/verify.md`.

- [ ] **Step 4: Regression sweep.**

Scroll the full piece once: every era bg changes at the right node, landmark vs margin cards reveal, dossier modal opens (`openDossier(0)`), the closing recap fades in and does NOT tear down at the bottom (Constraint #6 intact), resize the window and confirm re-init still renders (Constraint #2).

- [ ] **Step 5: Remove any remaining dead code / stale comments.**

Grep `index.html` for `hero-bridge`, `tlDrawHeroBridge`, `heroRiverSamples`, `heroST`, `hero-river-path`, `hero-ship`, `heroShipRock`, `heroCamStart`. Any surviving reference is either deleted or, if intentionally retained (e.g. `#hero-ship` kept for geometry), clearly commented as deprecated. Update the CLAUDE.md "Hero" notes if they now misdescribe the architecture.

Run: `grep -nc "hero-bridge-canvas\|tlDrawHeroBridge\|heroRiverSamples" index.html`
Expected: `0`

- [ ] **Step 6: Commit**

```bash
git add index.html scratchpad/verify.md
git commit -m "verify(hero): six-point + mobile verification of unified river; tune seam/dead-air; remove dead code"
```

---

## Acceptance Criteria (from the spec) → covered by

- Only one river canvas for hero + timeline → Task 4 (Steps 3–4), Task 1 (Step 4).
- River visible hero→timeline with no canvas swap → Task 4 (Steps 1–2).
- Ship follows one continuous path hero→Era 1 → Task 1 (Steps 1–2, 5) + Task 2 (Steps 1, 3).
- No visible jump/kink/camera snap at the seam → Task 1 (Step 1, vertical arrival) + Task 5 (Step 2).
- Era 1 begins where it did, visually + semantically → Task 3 (Steps 1–2), `points[]`/`eras`/gap math untouched (Task 1 Step 2).
- Existing nodes/cards/era panels/timing work → Task 5 (Step 4).
- No blank dead-scroll gap → Task 2 (Step 1, scroll-matched lead-in) + Task 5 (Step 2).
- Mobile checked → Task 5 (Step 3).
- Bridge code removed → Task 3 (Steps 3–4) + Task 4 (Steps 3–4) + Task 5 (Step 5).
- Verified with live instrumentation → Task 5.
