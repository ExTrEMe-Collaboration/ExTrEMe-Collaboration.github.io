# `assets/` — styles, scripts and images

## `css/site.css`

All styles, plain CSS (no Sass). The top of the file defines the design tokens as CSS variables: colours (light theme, then dark theme under `prefers-color-scheme: dark`), fonts, spacing and the simulation-stage colours that match the simulation-chain diagram. Change a colour there and it changes everywhere.

## `js/`

| File | What it does |
| --- | --- |
| `site.js` | Mobile menu; search, filter chips and speaker menu on the Presentations and Publications pages (state is kept in the URL, e.g. `?speaker=Jorge+Noronha&type=Seminar`) |
| `collision.js` | Animated heavy-ion collision in the home-page hero, the large banner at the top of the home page (see below) |

Both are optional enhancements: without JavaScript every list is still complete.

## Hero animation (`collision.js`)

The *hero* is the large banner at the top of the home page. Its animation is an **artistic sketch, not a physics simulation**: it evokes a collision in the reaction plane (beam horizontal, impact parameter vertical) without solving any equations. The collaboration's actual model, TRENTo → KoMPoST → MUSIC → iSS → UrQMD, is on the [Simulation chain](../simulation-chain.html) page.

It draws on a `<canvas data-collision>` in `index.html`, loaded only on the home page through the page's `scripts:` front matter. Times below are in seconds; `tau` is the time since impact. Line numbers refer to `collision.js` as of November 2026.

### What happens in one event, in order

1. **Nuclei** (`newEvent()`, l. 87–118). Two nuclei of `NUCLEONS` nucleons each (l. 43). Each nucleon is sampled uniformly in a transverse disk of radius `R`, and its offset along the beam follows a sphere profile squashed by `CONTRACTION` (l. 48, l. 104), so each nucleus looks like a Lorentz-contracted pancake.
2. **Impact parameter** (l. 88). A random `b` per event, between 0.3 R and 1.15 R; the two centres sit at `cy ∓ b/2`.
3. **Participants** (l. 108). A nucleon takes part in the collision if its transverse distance, using the in-plane `y` and a hidden depth `z`, to the other nucleus's centre is below about 0.92 R. All others are spectators.
4. **Approach** (`draw()`, l. 260–276). Both nuclei travel at `speed`, set in `resize()` (l. 82) so that the left nucleus starts just off-screen and reaches the collision point at `T_HIT` (l. 44).
5. **Impact flash** (l. 210–220). A white-to-orange radial glow at the collision point that grows and fades within 0.45 s.
6. **Fireball** (l. 222–243). One radial gradient per participant, drawn with additive blending (`"lighter"`, l. 208), so the dense core is brighter.
   - Each participant gets a Gaussian "rapidity" (l. 111). `placeParticipants()` (l. 149–156), called from `update()`, uses it to spread the participants along the beam as the fireball grows (`fireballGrowth()`, l. 143). The transverse growth is milder, ×1.45 at most (l. 154).
   - The core colour cools from white-yellow to orange to red (`heat`, l. 225, 229).
   - The glow fades over 0.7 s after freeze-out (`fade`, l. 226).
7. **Freeze-out** at `tau = T_FREEZE` (l. 45; `spawnHadrons()`, l. 121–140):
   - up to 320 hadron streaks (3 per participant);
   - roughly 70% gold "pions", 17% cyan "kaons" and 13% pink "protons" (l. 137);
   - each with a random angle plus a longitudinal kick from its parent's rapidity (l. 133);
   - emitted from the participants' current fireball positions, staggered over 0.35 s, each fading over about 3 s (2.9 s, l. 249).
8. **Spectators** (l. 260–276). The non-participants keep flying at the same speed and fade out over 1.6 s. Blue for the nucleus coming from the left, peach for the one from the right.
9. **Background** (`drawDetector()`, l. 178–195). Five faint concentric "detector" rings at 1.8–6.5 R (l. 181) and a dashed beam line through the collision point.
10. **Pause and loop**. The visible part of an event is over after `T_HIT + 4.4` = 5.9 s. A calm pause of `T_REST` (l. 46; currently 10 s) follows, with only the detector rings on screen. At `T_END` (l. 47) a new event starts, with a new impact parameter and new nucleons (`update()`, l. 160–175): one collision about every 16 s.

### Common tweaks

| To change | Edit |
| --- | --- |
| Time between collisions | `T_REST` (l. 46) |
| Approach time / overall pace | `T_HIT` (the nuclei's speed follows from it), `T_FREEZE` (l. 44–45); `T_END` (l. 47) adds them up |
| Flash, fireball and fade timings | flash `0.45` (l. 211), expansion `0.55` (`fireballGrowth()`, l. 143), cooling `0.9` (l. 225), fireball fade `0.7` (l. 226), hadron lifetime `2.9` (l. 249), spectator fade `1.6` (l. 267) |
| Number of nucleons | `NUCLEONS` (l. 43) |
| Number and speed of hadrons | `count` (l. 123) and `v0` (l. 124) in `spawnHadrons()` |
| Size of the nuclei | `R` in `resize()` (l. 80) |
| Pancake thickness | `CONTRACTION` (l. 48) |
| Range of impact parameters | `rand(0.3, 1.15)` (l. 88) |
| Where the collision sits | `cx`, `cy` in `resize()` (l. 77–79): wider than 720 px it sits at 74% across and 46% down, to the right of the text; narrower, it is centred at 30% height, behind the headline |
| Colours of the animation | the `rgba(...)` strings inside `collision.js`: flash l. 215–217, fireball l. 229 and 236–238, hadrons l. 137, nuclei l. 271–272, rings and beam line l. 181–192. They do **not** use the CSS tokens. |
| Colours around it | `site.css`: `.hero` (background glow), `.hero-shade` (the dark gradient that keeps the text readable over the animation), and the `--hot-gradient` token (highlighted letters, buttons) |

After a visible change, regenerate the social preview image (`scripts/make_og_image.js`, see `scripts/README.md`).

### Accessibility and performance

- **Decorative only**: the canvas has `aria-hidden="true"`; all text is regular HTML on top of it.
- **Reduced motion**: with `prefers-reduced-motion: reduce` nothing animates; `renderStill()` (l. 303) advances one event to just after freeze-out and draws a single still frame.
- **Pausing**: the loop stops in background tabs (`visibilitychange`, l. 329) and while the hero is scrolled out of view (`IntersectionObserver`, l. 334). The time step is capped at 50 ms (l. 283), so the animation does not jump after a pause.
- **Resolution**: the device-pixel ratio is capped at 2 (l. 71) to bound the canvas size on high-density screens.
- **Resizing**: 120 ms after the window stops resizing, the canvas is re-fitted and a new event starts (l. 320), because all positions are stored in pixels.
- **Cost**: per frame at most 120 nucleon dots, one gradient per participant and 320 line segments; no libraries.

## `images/`

| File | Use |
| --- | --- |
| `simulation_chain.png` | Diagram on the Simulation chain page |
| `spacetime_particles.gif` | Animation on the Simulation chain page (from the legacy site) |
| `favicon.svg` | Browser-tab icon |
| `og-image.jpg` | Preview image when the site is shared (1200 × 630): a capture of the home-page hero at the fireball moment, made with `scripts/make_og_image.js` |
