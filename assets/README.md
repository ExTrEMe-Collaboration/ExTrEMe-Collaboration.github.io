# `assets/` — styles, scripts and images

## `css/site.css`

All styles, plain CSS (no Sass). The top of the file defines the design tokens as CSS variables: colours (light theme, then dark theme under `prefers-color-scheme: dark`), fonts, spacing and the simulation-stage colours that match the simulation-chain diagram. Change a colour there and it changes everywhere.

## `js/`

| File | What it does |
| --- | --- |
| `site.js` | Mobile menu; search, filter chips and speaker menu on the Presentations and Publications pages (state is kept in the URL, e.g. `?speaker=Jorge+Noronha&type=Seminar`) |
| `collision.js` | Animated heavy-ion collision in the home-page hero (see below) |

Both are optional enhancements: without JavaScript every list is still complete.

## Hero animation (`collision.js`)

An **artistic sketch, not a physics simulation**: it evokes a collision in the reaction plane (beam horizontal, impact parameter vertical) without solving any equations. The collaboration's actual model, TRENTo → KoMPoST → MUSIC → iSS → UrQMD, is on the [Simulation chain](../simulation-chain.html) page.

It draws on a `<canvas data-collision>` in `index.html`, loaded only on the home page through the page's `scripts:` front matter. Times below are in seconds; `tau` is the time since impact. Line numbers refer to `collision.js` as of November 2026.

### What happens in one event, in order

1. **Nuclei** (`newEvent()`, l. 84–115). Two nuclei of `NUCLEONS` nucleons each (l. 41). Each nucleon is sampled uniformly in a transverse disk of radius `R`, and its offset along the beam follows a sphere profile squashed by `CONTRACTION` (l. 45, l. 101), so each nucleus looks like a Lorentz-contracted pancake.
2. **Impact parameter** (l. 85). A random `b` per event, between 0.3 R and 1.15 R; the two centres sit at `cy ∓ b/2`.
3. **Participants** (l. 105). A nucleon takes part in the collision if its transverse distance, using the in-plane `y` and a hidden depth `z`, to the other nucleus's centre is below about 0.92 R. All others are spectators.
4. **Approach** (`draw()`, l. 245–258). Both nuclei travel at `speed`, set in `resize()` (l. 79) so that the left nucleus starts just off-screen and reaches the collision point at `T_HIT` (l. 42).
5. **Impact flash** (l. 190–200). A white-to-orange radial glow at the collision point that grows and fades within 0.45 s.
6. **Fireball** (l. 202–225). One radial gradient per participant, drawn with additive blending (`"lighter"`, l. 188), so the dense core is brighter. Each participant gets a Gaussian "rapidity" (l. 108) that spreads its glow along the beam (`growth`, l. 204, 215). The transverse growth is milder, ×1.45 at most (l. 216). The core colour cools from white-yellow to orange to red (`heat`, l. 205, 209) and the glow fades over 0.7 s after freeze-out (`fade`, l. 206).
7. **Freeze-out** at `tau = T_FREEZE` (l. 43; `spawnHadrons()`, l. 118–137):
   - up to 320 hadron streaks (3 per participant);
   - roughly 70% gold "pions", 17% cyan "kaons" and 13% pink "protons" (l. 134);
   - each with a random angle plus a longitudinal kick from its parent's rapidity (l. 130);
   - emission staggered over 0.35 s, each streak fading over about 3 s (2.9 s, l. 231).
8. **Spectators** (l. 245–258). The non-participants keep flying at the same speed and fade out over 1.6 s. Blue for the nucleus coming from the left, peach for the one from the right.
9. **Background** (`drawDetector()`, l. 158–175). Five faint concentric "detector" rings at 1.8–6.5 R (l. 161) and a dashed beam line through the collision point.
10. **Loop**. After `T_END` (l. 44; currently `T_HIT + 4.4` = 5.9 s) a new event starts, with a new impact parameter and new nucleons (`update()`, l. 141–155).

### Common tweaks

| To change | Edit |
| --- | --- |
| Approach time / overall pace | `T_HIT` (the nuclei's speed follows from it), `T_FREEZE`, `T_END` (l. 42–44) |
| Flash, fireball and fade timings | the numbers in `draw()`: flash `0.45`, expansion `0.55`, cooling `0.9`, fireball fade `0.7`, hadron lifetime `2.9`, spectator fade `1.6` |
| Number of nucleons | `NUCLEONS` (l. 41) |
| Number and speed of hadrons | `count` (l. 120) and `v0` (l. 121) in `spawnHadrons()` |
| Size of the nuclei | `R` in `resize()` (l. 77) |
| Pancake thickness | `CONTRACTION` (l. 45) |
| Range of impact parameters | `rand(0.3, 1.15)` (l. 85) |
| Where the collision sits | `cx`, `cy` in `resize()` (l. 74–76): wider than 720 px it sits at 74% across and 46% down, to the right of the text; narrower, it is centred at 30% height, behind the headline |
| Colours of the animation | the `rgba(...)` strings inside `collision.js`: flash l. 195–197, fireball l. 209 and 218–220, hadrons l. 134, nuclei l. 253–254, rings and beam line l. 161–169. They do **not** use the CSS tokens. |
| Colours around it | `site.css`: `.hero` (background glow), `.hero-shade` (the dark gradient that keeps the text readable over the animation), and the `--hot-gradient` token (highlighted letters, buttons) |

After a visible change, regenerate the social preview image (`scripts/make_og_image.js`, see `scripts/README.md`).

### Accessibility and performance

- **Decorative only**: the canvas has `aria-hidden="true"`; all text is regular HTML on top of it.
- **Reduced motion**: with `prefers-reduced-motion: reduce` nothing animates; `renderStill()` (l. 288) advances one event to just after freeze-out and draws a single still frame.
- **Pausing**: the loop stops in background tabs (`visibilitychange`, l. 314) and while the hero is scrolled out of view (`IntersectionObserver`, l. 319). The time step is capped at 50 ms (l. 265), so the animation does not jump after a pause.
- **Resolution**: the device-pixel ratio is capped at 2 (l. 68) to bound the canvas size on high-density screens.
- **Resizing**: 120 ms after the window stops resizing, the canvas is re-fitted and a new event starts (l. 305), because all positions are stored in pixels.
- **Cost**: per frame at most 120 nucleon dots, one gradient per participant and 320 line segments; no libraries.

### Known issue

In the reduced-motion still frame, the hadron streaks start from the top-left corner of the canvas instead of from the fireball. Participants' fireball positions (`px`, `py`) are only computed in `draw()`, and `renderStill()` calls only `update()` before freeze-out. The normal animation is not affected. A fix would compute those positions in `update()` (or call that part of `draw()` before `spawnHadrons()`); it has been left as is pending a decision.

## `images/`

| File | Use |
| --- | --- |
| `simulation_chain.png` | Diagram on the Simulation chain page |
| `spacetime_particles.gif` | Animation on the Simulation chain page (from the legacy site) |
| `favicon.svg` | Browser-tab icon |
| `og-image.jpg` | Preview image when the site is shared (1200 × 630): a capture of the home-page hero at the fireball moment, made with `scripts/make_og_image.js` |
