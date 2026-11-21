# `assets/` — styles, scripts and images

## `css/site.css`

All styles, plain CSS (no Sass). The top of the file defines the design tokens as CSS variables: colours (light theme, then dark theme under `prefers-color-scheme: dark`), fonts, spacing and the simulation-stage colours that match the simulation-chain diagram. Change a colour there and it changes everywhere.

## `js/`

| File | What it does |
| --- | --- |
| `site.js` | Mobile menu; search, filter chips and speaker menu on the Presentations and Publications pages (state is kept in the URL, e.g. `?speaker=Jorge+Noronha&type=Seminar`) |
| `collision.js` | Animated heavy-ion collision in the home-page hero. Pauses off-screen, shows a still frame when the visitor prefers reduced motion |

Both are optional enhancements: without JavaScript every list is still complete.

## `images/`

| File | Use |
| --- | --- |
| `simulation_chain.png` | Diagram on the Simulation chain page |
| `spacetime_particles.gif` | Animation on the Simulation chain page (from the legacy site) |
| `favicon.svg` | Browser-tab icon |
| `og-image.jpg` | Preview image when the site is shared (1200 × 630). It is a screenshot of the home-page hero; retake it after major changes to the hero |
