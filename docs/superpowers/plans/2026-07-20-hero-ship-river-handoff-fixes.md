# Hero Ship/River Handoff Fixes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix two visible bugs in the hero section (`.tl-intro-section` in `index.html`), before era 1 / the pinned timeline: (1) the ship's heading doesn't match the river's flow direction as it travels the hero's motion path, and (2) the river/ship visibly vanish for a stretch of scrolling right before the pinned timeline's river appears.

**Architecture:** Both bugs live inside the same existing `heroTl` GSAP timeline (`index.html`, inside the `DOMContentLoaded` listener that also builds `#hero-map-river-group` / `#hero-river-path` / `#hero-ship`). No new files, no new systems — two targeted edits to existing tween calls.

**Tech Stack:** Plain JS, GSAP 3.13.0 (`MotionPathPlugin`), already loaded — no new dependencies.

## Global Constraints

- Do not touch the pinned `#policy-history` timeline engine (`tlMasterTl`, `nav.frac`, `applyFrame`, `drawRiver`, `riverSamples`, the `tlScrollTrigger` / `onToggle` no-op) — out of scope, per `CLAUDE.md`.
- Do not touch anything outside the `heroTl` block (no changes to `.tl-intro-inner` fade, `.hero-sky` clouds/birds, the water-shimmer filter, era logic, dossier modal, etc.).
- This project has no build step and no automated test suite (`CLAUDE.md`): validation is **screenshot-based visual verification**, not unit tests. Use the `run-history-immigration-policy` skill to launch the page and capture screenshots at defined scroll depths, and follow `superpowers:verification-before-completion` before claiming any fix works — every "verify" step below has explicit, checkable pass/fail criteria and a captured screenshot as evidence, not a vague "looks right."
- Keep both fixes independently revertible: separate commits, so either can be reverted without affecting the other.

## Validation harness (set up once, before Task 1)

Because there are no automated tests, define the reusable validation procedure here and reuse it in every reproduce/verify step:

1. **Launch:** invoke the `run-history-immigration-policy` skill to serve/open `index.html` in a controllable browser.
2. **Capture the hero scroll sequence** at four scroll depths (the hero section is `min-height: 160vh`, so these are fractions of that section's scroll range) and save each as an evidence screenshot:
   - **A — top (~0%)**: hero at rest, ship idle at path start.
   - **B — mid (~40%)**: ship partway down a *curved* segment of `#hero-river-path` (good for checking heading vs. curve).
   - **C — late (~85%)**: the depth where the old fade-out used to fire — the prime suspect for the vanish gap.
   - **D — handoff (~100%, section bottom at viewport top)**: the boundary where the pinned `#policy-history` river takes over.
3. **Baseline first:** capture A–D on the **unmodified** page before editing, so each task's "reproduce" step has a before-image to compare its "verify" against. Save baselines as `hero-baseline-{A,B,C,D}.png` in the scratchpad.
4. **Pass/fail is judged from the screenshots**, not from a live glance — attach or reference the screenshot filenames in each verify step so the result is auditable at hand-off.

---

### Task 1: Fix ship heading vs. river direction misalignment

**Files:**
- Modify: `index.html:2813` (inside the `heroTl.to(heroShip, { motionPath: {...} })` call)

**Interfaces:**
- Consumes: `SHIP_ANGLE_OFFSET` constant already defined at `index.html:1586` (`const SHIP_ANGLE_OFFSET = 45;` — degrees added to the path tangent angle to align the same `boat.png` artwork with its direction of travel in the real, working pinned timeline, applied at `index.html:2325`).
- Produces: no new interface — this only changes a numeric literal inside the existing hero motion-path tween.

**Root cause:** The real timeline (which renders the ship correctly) always adds a fixed `+45°` to the raw path-tangent angle before rotating the `boat.png` sprite, because the artwork itself isn't drawn pointing straight along its long axis. The hero's motion-path tween uses GSAP's `autoRotate: 90` for the exact same sprite — a different, untuned offset — which is why the hero ship's heading doesn't match the river's local flow direction.

- [ ] **Step 1: Reproduce the bug**

Using the **Validation harness** above, capture baseline screenshot **B** (ship on a curved segment, ~40%). **Pass/fail for "bug reproduced":** in `hero-baseline-B.png`, the ship's long axis visibly does *not* lie along the river's local tangent — it reads as rotated off the flow direction (the `autoRotate: 90` vs. the real timeline's `+45` mismatch). If the heading already looks aligned in the baseline, STOP — the bug does not reproduce and Task 1 may already be resolved; do not apply the edit blindly.

- [ ] **Step 2: Change the rotation offset**

In `index.html`, change:

```js
  heroTl.to(heroShip, {
    motionPath: {
      path: '#hero-river-path',
      align: '#hero-river-path',
      alignOrigin: [0.5, 0.5],
      autoRotate: 90,
    },
    duration: 1,
  }, 0);
```

to:

```js
  heroTl.to(heroShip, {
    motionPath: {
      path: '#hero-river-path',
      align: '#hero-river-path',
      alignOrigin: [0.5, 0.5],
      autoRotate: SHIP_ANGLE_OFFSET,
    },
    duration: 1,
  }, 0);
```

(This reuses the existing `SHIP_ANGLE_OFFSET` constant from `index.html:1586` instead of a second, independent magic number — if that constant is ever retuned for the real ship sprite, the hero ship stays consistent with it automatically.)

- [ ] **Step 3: Verify the fix**

Reload the page and re-capture screenshot **B** at the same ~40% scroll depth; save as `hero-fix1-B.png`. Also capture **D** (~100%) as `hero-fix1-D.png` to compare the hero ship's heading against the pinned timeline ship. **Pass criteria (all must hold):**
1. In `hero-fix1-B.png` the ship's long axis lies along the river's local tangent — nose pointed in the direction of travel, matching the curve (contrast against `hero-baseline-B.png`).
2. Heading tracks the curve across the whole path, not just at one point — sanity-check by also capturing a second curved depth (~60%) if B is ambiguous.
3. The hero ship's heading convention matches the pinned timeline ship (same artwork, same `+45` offset), i.e. no visible inconsistency between the two rivers at the handoff.

If the ship now looks *over*-rotated the other way, do not hand-tune a new magic number — re-confirm the constant is `SHIP_ANGLE_OFFSET` (45) and re-check the path is authored top→bottom (it is: `M420 190 … 400 900`); an inverted result would mean a path-direction issue, not an offset value to guess at.

- [ ] **Step 4: Commit**

```bash
git add index.html
git commit -m "fix(hero): align ship heading with river path direction"
```

---

### Task 2: Stop the hero river/ship from vanishing before the pinned timeline appears

**Files:**
- Modify: `index.html:2795-2798` (comment) and `index.html:2807`, `index.html:2817` (the two fade-to-0 tweens)

**Interfaces:**
- Consumes: nothing new.
- Produces: nothing new — removes two tween calls from the existing `heroTl` timeline.

**Root cause (CORRECTED during implementation — the original hypothesis below was disproven by screenshot validation):**

> ~~Original hypothesis: the early opacity fade (`opacity:0` at progress 0.8) is what causes the gap; deleting the two fade tweens fixes it.~~ **Disproven.** Baseline-vs-edit screenshots at scroll 1000 were identical — the fade doesn't even run there (it starts at progress 0.8 ≈ scroll 1152), and deleting it did not close the gap.

**Actual root cause:** the gap is *structural*, not opacity. The hero river lives in `.hero-river-wrap` (`position:absolute; top:0`) and scrolls up and off the top of the `min-height:160vh` section; its path ended exactly at the section bottom. The pinned timeline's river is `position:fixed` with its drawn top parked ~40% down the viewport. So during the handoff (~scroll 900–1300) the hero river's bottom and the pinned river's fixed top never meet — a blank vertical band sits between them, and it *grows* as the section scrolls off. DOM measurement (via `scratchpad/measure.py`): at scroll 1000 the hero river bottom was at screen y≈218 while the pinned river top was fixed at ≈350 — a ~132px blank band.

**Actual fix (hero-only, per user decision "extend hero river down"):**
1. Extend the hero river *below* the section so it physically reaches the pinned river: `.hero-river-wrap` height `100%` → `calc(100% + 60vh)`, `#hero-river-svg` viewBox `0 0 800 900` → `0 0 800 1260`, `#hero-river-path` extended with one more cubic down to `400 1260`, and `.tl-intro-section` `overflow: hidden` → `visible` so the extended wrap isn't clipped at the section boundary.
2. Replace the early fade with a *late crossfade* — `heroTl.to('#hero-map-river-group', {opacity:0, duration:0.1}, 0.9)` and the same for `heroShip` — so the river stays visible long enough to bridge the gap, then dissolves over the overlap zone. This is required because the hero group paints above pinned content (`.tl-intro-section` is `z-index:50`, a positive-z sibling of the pinned container), so without the late fade the extended river lingers as a blue stub over the Era 1 cover panel.

**Tooling note:** `.claude/skills/run-history-immigration-policy/driver.py` hardcoded the deleted `word-to-law.html`; repointed it to `index.html` so validation screenshots load the current page.

**Design tradeoff to watch (why the fade existed):** the original fade was deliberate — its comment says it kept the river from being "clipped mid-flow at full brightness," which "read as disconnected." Removing it trades a soft fade-out for the river scrolling off at full opacity. That is safe from a *double-river* (verified: `.hero-river-wrap` is `position:absolute; top:0` inside a `min-height:160vh; overflow:hidden` section, so it scrolls off naturally and never overlaps the pinned `position:fixed` river), but the "verify" step below must confirm the raw scroll-off does **not** look like an abrupt clip — if it does, the correct fix is to *retime/shorten* the fade so it completes at the handoff boundary, not delete it. Flag this to the user rather than reintroducing the early gap.

- [x] **Step 1: Reproduce the bug** — DONE. Baseline `hero-baseline-C.png` (scroll ~1225) showed a blank paper band at the top of the viewport while the pinned river only appeared lower down. Confirmed with finer sweep (scroll 1000/1150) that the blank band is present throughout the handoff.

- [x] **Step 2: Diagnose (this is where the plan's original hypothesis was corrected)** — DONE. Deleting the two fade tweens was tried first and validated with screenshots; it did **not** close the gap (identical before/after at scroll 1000). DOM measurement (`scratchpad/measure.py`) revealed the structural cause above. Reverted the naive edit.

- [x] **Step 3: Implement the actual fix** — DONE (see "Actual fix" above). Committed as `1f51ebd`. Changes: `.tl-intro-section` `overflow:visible`; `.hero-river-wrap` height `calc(100% + 60vh)`; `#hero-river-svg` viewBox height `900→1260`; `#hero-river-path` extended to `400 1260`; removed the two `opacity:0 @0.8` tweens; added `opacity:0 duration:0.1 @0.9` late crossfade for both the group and the ship; updated the stale comment.

- [x] **Step 4: Verify the fix** — DONE. Screenshots at scroll 1000/1150 show a **continuous** river (hero flowing into pinned, no blank band); 1250/1300 show the hero river cleanly crossfaded out with the Era 1 panel intact (no blue stub, contrast the intermediate full-removal test `exp2-1300.png` which *did* show a stub). Scroll 0/300 confirm the viewBox rescale did not distort the top view and the ship heading (Task 1) still tracks the flow.

- [x] **Step 5: Commit** — DONE (`1f51ebd`, message documents the corrected root cause and the extend-plus-crossfade approach).

---

### Task 3: End-to-end validation gate (before hand-off)

**Files:** none — this task changes no code. It is the mandatory verification gate that runs after both fixes are committed, per `superpowers:verification-before-completion`. Do not declare the work done or hand off until every check below passes with a captured screenshot as evidence.

**Interfaces:** consumes the `run-history-immigration-policy` skill and the Validation harness above; produces a short pass/fail report (screenshot filenames + verdict) for the user.

- [ ] **Step 1: Full hero scroll pass on the combined fixes**

With both commits applied, re-run the Validation harness and capture the full sequence **A → B → C → D**, saved as `hero-final-{A,B,C,D}.png`. Confirm together:
  - Heading tracks the curve (Task 1 pass criteria) — evidence: `hero-final-B.png`.
  - No vanish gap and clean handoff (Task 2 pass criteria) — evidence: `hero-final-C.png`, `hero-final-D.png`.
  - No regression to hero rest state — evidence: `hero-final-A.png` (ship idle at start, title/scroll cue present).

- [ ] **Step 2: Regression check — pinned timeline untouched**

Continue scrolling past the handoff **into** the pinned `#policy-history` timeline and capture at least two screenshots: the first policy node/card active, and one deeper node. **Pass criteria:** the pinned river draws, the ship follows the path, nodes activate, and cards/era panels render — exactly as before these edits. This confirms the hero-only changes did not perturb `tlMasterTl` / `nav.frac` / `applyFrame` / `drawRiver`. Save as `regression-pinned-{1,2}.png`.

- [ ] **Step 3: Console + load check**

Confirm the browser console shows no new errors/warnings introduced by the edits (GSAP MotionPath warnings in particular), and that the page loads cleanly from `file://` (this repo is normally opened from disk).

- [ ] **Step 4: Report and hand off**

Produce a one-paragraph verdict listing the evidence screenshots and stating PASS/FAIL per fix + regression. Only if all pass is the branch ready to hand off (see `superpowers:finishing-a-development-branch` for merge/PR options). If anything failed, report it to the user with the offending screenshot rather than force-shipping.

---

## Self-Review Notes

- Spec coverage: both reported bugs (ship heading misalignment, river vanish-gap) each have a dedicated task with a diagnosed root cause, exact line numbers, and exact before/after code.
- No placeholders: every step shows exact code to add/remove/change.
- Scope: confirmed neither task touches `tlMasterTl`, `nav.frac`, `riverSamples`, `drawRiver`, or any code outside the `heroTl` block — matches the user's "don't touch anything else" instruction.
- Independent commits: Task 1 and Task 2 touch non-overlapping lines and are committed separately, so either can be reverted alone.
- Validation: with no automated test suite, every fix has screenshot-based, criteria-driven verification (baseline vs. fixed at fixed scroll depths via the `run-history-immigration-policy` skill), a diagnosed "reproduce" gate that stops if the bug isn't present, plus a Task 3 end-to-end gate that also runs a regression check on the untouched pinned timeline — nothing hands off on a vague visual glance.
- Code-grounded: line numbers (2807/2813/2817), `SHIP_ANGLE_OFFSET = 45` (`index.html:1586`), the real timeline's `+45` usage (`index.html:2325`), and the double-river safety of `.hero-river-wrap` (`position:absolute` in an `overflow:hidden` section) were all verified against `index.html` during this revision.
