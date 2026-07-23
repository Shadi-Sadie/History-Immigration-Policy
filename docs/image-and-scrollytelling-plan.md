# Image Placement & Scrollytelling Enhancement Plan

Scope: the `#policy-history` timeline in `from-the-word-to-the-law (2).html` (source of truth) and `index.html` (port after). Covers: exact on-page placement of every image, the animation spec for each, whether video is needed (short answer: no), and the missing assets worth sourcing.

---

## 1. Image inventory & identification

| File | What it actually is | Date | Status |
|---|---|---|---|
| `img3.jpg` | *William Penn's Treaty with the Indians* engraving | 1775 (depicts 1681) | ✅ Era 1 bg — correct |
| `image2.webp` | *"Welcome to All!"* — Uncle Sam's U.S. Ark of Refuge (Keppler, Puck) | 1880 | ⚠️ Era 2 bg — period mismatch, thematic fit; caption will carry the honest date |
| `image.webp` | *"The Anti-Chinese Wall"* (Puck) | 1882 | ✅ Era 3 bg — correct |
| `image4.jpg` | *"The Only Way to Handle It"* — Europe funneled through 3% gate | 1921 | ✅ Era 4 bg — correct |
| `image5.jpg` | LBJ signing Hart-Celler at Liberty Island | 1965 | ✅ Era 5 bg — correct |
| `image6.jpg` | Razor wire over corrugated border fence | modern | ✅ Era 6 bg — correct |
| `pic1.png` | Nast, *"Uncle Sam's Thanksgiving Dinner"* (inclusive vision) | 1869 | ❌ misassigned to Colonial Settlement |
| `pic2.png` | Nast, *"Which Color Is To Be Tabooed Next?"* (Chinese exclusion) | 1882 | ❌ misassigned to 1790 Naturalization Act |
| `pic3.png` | *Magic Washer* ad — "The Chinese Must Go" | 1886 | ❌ misassigned to 1798 Alien & Sedition |
| `pic4.png` | Keppler, *"Looking Backward"* (immigrants' shadows block the newcomer) | 1893 | ❌ misassigned to 1808 Slave Trade Prohibition |
| `pic5.png` | *"The Mortar of Assimilation"* | 1889 | ❌ misassigned to Dred Scott |
| `pic6.webp` | *"The High Tide of Immigration — A National Menace"* (Judge) | 1903 | ❌ misassigned to 14th Amendment |
| `1917.webp` | *"The Americanese Wall"* — literacy-test cartoon | 1916 | 🆕 unused |
| `Times_1891.jpg` | Clipping: *"THE IMMIGRANT. Who Can Come, and Who Cannot, Under the New Law"* | 1891 | 🆕 unused |
| `Brooklyn_1904.jpg` | *"A Finer Screen Needed"* — emigrants shoveled at a U.S. law screen | ~1904 | 🆕 unused |
| `certchin.jpg` | **Primary document**: Chinese Certificate of Residence, "Sing Toy," Geary Act | 1894 | 🆕 unused |
| `barco.jpg` | OWI photo, Mexican farm laborers harvesting (Bracero era) | 1943 | 🆕 unused |
| `oldpaper2.png` / `oldpaper3.png` | Paper textures (warm kraft / cool fiber) | — | 🆕 unused |
| `oldpaper.png` | Paper texture — **7.5 MB, must be compressed** | — | ✅ Era 1 texture |
| `boat.png` | Ship sprite | — | ✅ in use |
| `boat.svg`, `ripple.svg` | Legacy assets | — | leave |

**Editorial principle:** every cartoon moves to the law it was drawn about, becoming evidence of *how the press saw immigrants at that moment* rather than decoration. For pre-photography policies (1600s–1860s) the *document is the artifact* — no anachronistic art; the landmark torn-paper typography carries them (until real statute scans are sourced, see §6).

---

## 2. Exact placement map — where each image appears on the page

The page is one continuous scrub. Reading top to bottom:

### 2.1 Intro viewport (`.tl-intro-section`, 0–100vh) — the hook
**New.** Above the title block, a small (~180px wide) archival cutout: the **portrait crop of Sing Toy from `certchin.jpg`** (crop the photo corner of the certificate to a new asset `images/singtoy-portrait.webp`), presented like a paper-clipped evidence photo, slightly rotated (−2.5°), with caption: *"Sing Toy, 22, laborer. Required to carry federal proof of her right to exist in the U.S. — 1894."*
This is the classic scrollytelling "open on one person, not a theme" move, and it sets up a payoff 60% down the page when the full certificate appears on the Chinese Exclusion landmark card.
**Animation:** on load (not scroll): opacity 0→1 + y 16→0, 0.8s `power2.out`, 0.2s before the title's reveal. No scroll linkage.

### 2.2 Era cover panels (`#era-world-layer`, inside the river gaps)
Existing placement (bg image behind era title/intro, duotone-filtered, top-masked) is right. Changes:
- Wire the existing-but-unrendered `caption` field: bottom-right of each panel, small caps, `--ink-soft`: e.g. era 3 → *"'The Anti-Chinese Wall,' Puck, 1882 · Library of Congress."*
- Textures: era 2 gets `oldpaper3.png`, era 3 gets `oldpaper2.png` (multiply blend at ~20% like era 1).
**Animation (Ken Burns, derived):** in `applyFrame`, while the camera is inside an era gap, map gap-progress 0→1 to the panel bg `scale 1.03→1.10` and `backgroundPositionY` drift of ~4%. Pure derived transform from `tlMasterTl.time()` — no new tween, honors the single-driver constraint. Disabled under `prefers-reduced-motion`.

### 2.3 Policy-card photos (`.tl-card-layer`, alternating left/right of the active node)
Photo sits **above the card box, same column, same side as the card** (cards alternate by index parity), max-height 200px, `object-fit: cover`, thin `--paper` mount border + 1px `--ink-faint` rule, caption bar beneath (11px, small caps, credit included). Duotone/sepia-lift filter so lithographs, newsprint, and photos sit in one system.

| Node (year · policy) | Image | Side | Notes |
|---|---|---|---|
| 1868 · 14th Amendment (landmark) | `pic1.png` | card side | Nast's one-table Thanksgiving = the amendment's visual argument |
| 1875 · Page Act | `pic4.png` | card side | gate-keeping by former immigrants opens the exclusion era |
| 1882 · Chinese Exclusion — **promote to `landmark: true`** | `certchin.jpg` | card side | the certificate IS the torn-paper document: render inside the landmark frame with wax stamp overlapping its corner, quote: *"…the coming of Chinese laborers be suspended"*, stamp: "1882" |
| 1891 · Immigration Act | `Times_1891.jpg` | card side | newsprint clipping treatment: ragged-edge mask, slight −1.5° rotation |
| 1907 · Gentlemen's Agreement | `Brooklyn_1904.jpg` | card side | |
| 1917 · Literacy Act | `1917.webp` | card side | |
| 1921–24 · Quota Acts | `pic6.webp` | card side | the 1903 "menace" panic that produced the quotas |
| 1942–64 · Bracero Program | *(none on card)* | — | gets the full-bleed interstitial instead (§2.4) |
| 1965 · Hart-Celler (landmark) | `image5.jpg` | card side | signing photo doubles from era bg; the signature = "word to law" in one frame |
| Colonial → Dred Scott | **remove `image`** | — | text-led until statute scans are sourced (§6) |

**Animation (joins the existing `revealCard()` timeline, after text):**
1. existing SplitText title/quote stagger plays;
2. photo: `clip-path: inset(100% 0 0 0)` → `inset(0)` + `y: 10→0`, 0.55s `power2.out`, starting `-=0.1` from the text tail;
3. caption: opacity 0→1, 0.25s, `+=0.05`.
Cache the built tween on the card element (like `_titleSplit`) so scrolling back doesn't re-run it. For the certificate landmark, add `scale 1.015→1` + shadow-soften over 0.6s — a "document laid on the desk" settle.
**Mobile (≤768px):** replace the current `display:none` — photo renders inside the card, full width, `max-height: 26vh`, caption below.

### 2.4 The Bracero full-bleed interstitial — the piece's one scale-change
Placed at the **Bracero Program segment (~policy 20 of 39)**, the emotional pivot between the internment low point and the 1965 opening. It's the only photograph of people the policies acted on, faces to camera — it earns the only full-viewport moment.
**Structure:** a screen-fixed overlay layer (same pattern as `#tl-recap`), `barco.jpg` full-bleed with a bottom gradient scrim, one line of text (*"Between 1942 and 1964, 4.6 million contracts brought Mexican workers north — welcomed as hands, not as neighbors."*) + credit line.
**Animation (all derived in `applyFrame` from `nav.frac` over the Bracero segment window, e.g. frac 0.56–0.66):**
- 0.56–0.585: overlay opacity 0→1; card + era layers fade to 0 (exactly how the recap handoff works)
- 0.585–0.635: image `scale 1.06→1.0` slow settle; text lines translate up 24px and fade in, staggered
- 0.635–0.66: overlay opacity 1→0, layers restore
No pinning trickery, no second driver — it's a window function on the existing scrub.

### 2.5 Dossier modal artifacts (new)
Add optional `image: [{src, caption, credit}]` to `dossiers[n]`, rendered between "What happened" and "Why it mattered" in an archival frame (paper-texture mat, tape corners, ~−1° rotation).

| Dossier | Artifacts |
|---|---|
| Chinese Exclusion Act | `pic2.png` + `pic3.png` — press *and advertising* normalizing exclusion |
| 1790 Naturalization Act | `pic5.png` — assimilation-as-mortar, the idea the 1790 text seeded |
| Hart-Celler 1965 | `image5.jpg` — signing beneath the Statue of Liberty |

**Animation (modal open, time-based — this is UI, not scroll):** `gsap.from('.dossier-artifact', {opacity: 0, y: 18, rotation: -3, duration: 0.5, ease: 'power2.out', stagger: 0.12, delay: 0.15})`.

### 2.6 Recap (`#tl-recap`)
Keep image-free. The meander recap is the data payoff; a photo would compete with it. (If an ending image is ever wanted: a naturalization-oath ceremony photo, see §6.)

---

## 3. Animation system summary

| Element | Trigger | Mechanism | Spec |
|---|---|---|---|
| Intro portrait | page load | one-shot tween | fade+rise 0.8s, before title |
| Era bg Ken Burns | scrub | derived in `applyFrame` | scale 1.03→1.10 + bgY drift across gap |
| Card photo reveal | node activation | appended to `revealCard()` tl | clip-path wipe up 0.55s after text |
| Certificate landmark | node activation | same, + settle | scale 1.015→1, shadow soften |
| Newsprint clipping | node activation | same | + rotation −3°→−1.5° settle |
| Bracero interstitial | scrub window | derived in `applyFrame` | fade in/settle/fade out over frac 0.56–0.66 |
| Dossier artifacts | modal open | time-based tween | stagger 0.12, y+rotation settle |
| Captions | after parent image | same timeline | 0.25s fade |

Global rules: one or two properties animate per beat; everything scroll-linked derives from `tlMasterTl.time()` (hard constraint #1); everything decorative respects `prefers-reduced-motion` (CSS media query + `matchMedia` guard skipping Ken Burns and SplitText staggers).

---

## 4. Do we need video? **No.**

Reasons to stay stills + canvas:
1. **The scrub is the motion.** The river, ship, and camera already provide continuous cinematic movement; time-based video fights scroll-based media — it plays at its own pace while everything else obeys the reader's thumb.
2. **Performance:** video decode on top of a full-viewport canvas redrawn every frame is the most likely thing to break 60fps on mid-range phones.
3. **Tone:** the editorial "paper archive" language (torn paper, wax stamps, newsprint) is a stills language; archival footage would introduce a second, documentary-film register.

**Optional exception (only if a "wow" beat is wanted later):** the Edison/Ellis Island arrival films (1903–1906, Library of Congress, public domain) as a muted, desaturated loop *inside* era 3's cover panel — `muted playsinline loop`, poster fallback, pause via the existing era activation hook when off-screen, hidden under `prefers-reduced-motion` and on mobile. Ship the stills version first; add this only after profiling.

---

## 5. Missing photos worth sourcing (all public domain unless noted)

Priority order — the first three fill real narrative holes:

1. **Japanese American internment, 1942** — the piece's most extreme policy (`lean: -1.00`) has no image. Dorothea Lange's WRA photographs (NARA, public domain): the Mochida family awaiting evacuation, or the Oakland *"I AM AN AMERICAN"* storefront. Card photo.
2. **"Instructions to All Persons of Japanese Ancestry" exclusion poster, 1942** (NARA) — a second primary document for the internment dossier; pairs with the certificate as the archive's twin artifacts of paper-as-control.
3. **Founding-era statute scans** — first page of the **1790 Naturalization Act** (LoC "A Century of Lawmaking"), the **Dred Scott opinion** first page, the **14th Amendment engrossed copy** (NARA). These give the pre-photography landmark cards period-honest artifacts and complete the "word to the law" thesis visually: the actual words, in ink.
4. **Vietnamese refugees, 1975** — US Navy photos of boat rescues / Operation New Life (public domain) → Indochina Refugee Act card.
5. **Alien registration fingerprinting, 1940** (LoC/FSA-OWI) → Alien Registration Act card.
6. **Ellis Island inspection hall, c. 1907** (LoC, Bain collection) → 1891 Act or Literacy Act dossier context.
7. **Modern southern border, 2019–2025** — CBP/DVIDS photos (federal works, public domain): Remain-in-Mexico encampment or Title 42 expulsion → cards in era 6, which currently has only the razor-wire texture.
8. **Naturalization oath ceremony, flags raised** (USCIS Flickr, public domain) — optional hopeful counterweight for the recap or the 1990 Immigration Act card.
9. *(Nice-to-have, licensing varies)* DACA rally 2012 — check CC-licensed news photography; skip if unclear.

---

## 6. Cross-cutting craft fixes (what was lacking)

1. **Captions + credits everywhere** — `imageCaption`/`imageCredit` on policies, `caption`/`credit` on dossier artifacts, wire era `caption`. Archival images without sourcing read as decoration and cost trust.
2. **Unified image treatment** — duotone/sepia-lift filter on card photos (era bgs already use `#tl-era-duotone`).
3. **Mobile parity** — stop hiding `.policy-photo`; render in-card (§2.3).
4. **Loading discipline** — `loading="lazy" decoding="async"` on card/dossier images; preload next era's bg on `eraCurrentIndex` change; compress `oldpaper.png` (7.5 MB→<300 KB), `certchin.jpg` (2.9 MB→~400 KB @1600px), `pic4.png`, `image5.jpg`; `barco.jpg` gets a 2200px full-bleed variant.
5. **Reduced motion** — media-query + `matchMedia` guards on Ken Burns, staggers, scroll-cue pulse.
6. **Dossier/policy index alignment** — reassignments change no ordering, so `dossiers` keys are unaffected (hard constraint #5). Verify anyway.

---

## 7. Implementation order

1. **Asset prep**: crop `singtoy-portrait.webp`; compress/resize all listed files (cwebp/imagemagick).
2. **Data pass** (both timeline files): reassign `policy.image` per §2.3, add caption/credit fields, promote Chinese Exclusion to landmark with quote/stamp.
3. **Caption rendering**: card caption bar, era caption wiring, CSS.
4. **Mobile photo layout** (replaces `display:none`).
5. **Reveal choreography**: photo joins `revealCard()`; clipping/certificate/newsprint variants; duotone CSS; tween caching.
6. **Intro hook**: Sing Toy evidence-photo block + load animation.
7. **Bracero interstitial**: recap-pattern overlay + `applyFrame` window.
8. **Ken Burns on era bgs** + all `prefers-reduced-motion` guards.
9. **Dossier artifact block**: schema, render, frame CSS, three entries, open-animation.
10. **Textures**: era 2/3; preload-next-era hook.
11. **Port to `index.html`** (everything except dossier if the modal hasn't been merged there yet).
12. **Verify** via `run-history-immigration-policy`: screenshot intro, each era cover, Page Act/1891/1917 cards, the certificate landmark, Bracero interstitial, a dossier with artifacts, recap, and a 375px-wide pass.

Deliberately not doing: video (see §4), images on founding-era policies until statute scans exist, any second animated driver, scroll hijacking, autoplaying audio.
