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

1. **Nuclei** (`newEvent()`, l. 85–116). Two nuclei of `NUCLEONS` nucleons each (l. 42). Each nucleon is sampled uniformly in a transverse disk of radius `R`, and its offset along the beam follows a sphere profile squashed by `CONTRACTION` (l. 46, l. 102), so each nucleus looks like a Lorentz-contracted pancake.
2. **Impact parameter** (l. 86). A random `b` per event, between 0.3 R and 1.15 R; the two centres sit at `cy ∓ b/2`.
3. **Participants** (l. 106). A nucleon takes part in the collision if its transverse distance, using the in-plane `y` and a hidden depth `z`, to the other nucleus's centre is below about 0.92 R. All others are spectators.
4. **Approach** (`draw()`, l. 258–274). Both nuclei travel at `speed`, set in `resize()` (l. 80) so that the left nucleus starts just off-screen and reaches the collision point at `T_HIT` (l. 43).
5. **Impact flash** (l. 208–218). A white-to-orange radial glow at the collision point that grows and fades within 0.45 s.
6. **Fireball** (l. 220–241). One radial gradient per participant, drawn with additive blending (`"lighter"`, l. 206), so the dense core is brighter.
   - Each participant gets a Gaussian "rapidity" (l. 109). `placeParticipants()` (l. 147–154), called from `update()`, uses it to spread the participants along the beam as the fireball grows (`fireballGrowth()`, l. 141). The transverse growth is milder, ×1.45 at most (l. 152).
   - The core colour cools from white-yellow to orange to red (`heat`, l. 223, 227).
   - The glow fades over 0.7 s after freeze-out (`fade`, l. 224).
7. **Freeze-out** at `tau = T_FREEZE` (l. 44; `spawnHadrons()`, l. 119–138):
   - up to 320 hadron streaks (3 per participant);
   - roughly 70% gold "pions", 17% cyan "kaons" and 13% pink "protons" (l. 135);
   - each with a random angle plus a longitudinal kick from its parent's rapidity (l. 131);
   - emitted from the participants' current fireball positions, staggered over 0.35 s, each fading over about 3 s (2.9 s, l. 247).
8. **Spectators** (l. 258–274). The non-participants keep flying at the same speed and fade out over 1.6 s. Blue for the nucleus coming from the left, peach for the one from the right.
9. **Background** (`drawDetector()`, l. 176–193). Five faint concentric "detector" rings at 1.8–6.5 R (l. 179) and a dashed beam line through the collision point.
10. **Loop**. After `T_END` (l. 45; currently `T_HIT + 4.4` = 5.9 s) a new event starts, with a new impact parameter and new nucleons (`update()`, l. 158–173).

### Common tweaks

| To change | Edit |
| --- | --- |
| Approach time / overall pace | `T_HIT` (the nuclei's speed follows from it), `T_FREEZE`, `T_END` (l. 43–45) |
| Flash, fireball and fade timings | flash `0.45` (l. 209), expansion `0.55` (`fireballGrowth()`, l. 141), cooling `0.9` (l. 223), fireball fade `0.7` (l. 224), hadron lifetime `2.9` (l. 247), spectator fade `1.6` (l. 265) |
| Number of nucleons | `NUCLEONS` (l. 42) |
| Number and speed of hadrons | `count` (l. 121) and `v0` (l. 122) in `spawnHadrons()` |
| Size of the nuclei | `R` in `resize()` (l. 78) |
| Pancake thickness | `CONTRACTION` (l. 46) |
| Range of impact parameters | `rand(0.3, 1.15)` (l. 86) |
| Where the collision sits | `cx`, `cy` in `resize()` (l. 75–77): wider than 720 px it sits at 74% across and 46% down, to the right of the text; narrower, it is centred at 30% height, behind the headline |
| Colours of the animation | the `rgba(...)` strings inside `collision.js`: flash l. 213–215, fireball l. 227 and 234–236, hadrons l. 135, nuclei l. 269–270, rings and beam line l. 179–190. They do **not** use the CSS tokens. |
| Colours around it | `site.css`: `.hero` (background glow), `.hero-shade` (the dark gradient that keeps the text readable over the animation), and the `--hot-gradient` token (highlighted letters, buttons) |

After a visible change, regenerate the social preview image (`scripts/make_og_image.js`, see `scripts/README.md`).

### Accessibility and performance

- **Decorative only**: the canvas has `aria-hidden="true"`; all text is regular HTML on top of it.
- **Reduced motion**: with `prefers-reduced-motion: reduce` nothing animates; `renderStill()` (l. 301) advances one event to just after freeze-out and draws a single still frame.
- **Pausing**: the loop stops in background tabs (`visibilitychange`, l. 327) and while the hero is scrolled out of view (`IntersectionObserver`, l. 332). The time step is capped at 50 ms (l. 281), so the animation does not jump after a pause.
- **Resolution**: the device-pixel ratio is capped at 2 (l. 69) to bound the canvas size on high-density screens.
- **Resizing**: 120 ms after the window stops resizing, the canvas is re-fitted and a new event starts (l. 318), because all positions are stored in pixels.
- **Cost**: per frame at most 120 nucleon dots, one gradient per participant and 320 line segments; no libraries.

## `images/`

| File | Use |
| --- | --- |
| `simulation_chain.png` | Diagram on the Simulation chain page |
| `spacetime_particles.gif` | Animation on the Simulation chain page (from the legacy site) |
| `favicon.svg` | Browser-tab icon |
| `og-image.jpg` | Preview image when the site is shared (1200 × 630): a capture of the home-page hero at the fireball moment, made with `scripts/make_og_image.js` |
