#!/usr/bin/env node
/*
 * Regenerate assets/images/og-image.jpg: the 1200×630 preview image shown when
 * a page of the site is shared (Slack, e-mail, social media). It is a capture
 * of the home-page hero (the large banner at the top of the home page), taken
 * while the collision fireball glows.
 *
 * Usage, with the site served locally (e.g. `bundle exec jekyll serve`):
 *
 *   node scripts/make_og_image.js [URL] [OUTPUT]
 *
 *   URL     default http://127.0.0.1:4000/
 *   OUTPUT  default assets/images/og-image.jpg
 *
 * Requires Playwright with Chromium:
 *   npm install playwright && npx playwright install chromium
 *
 * Math.random is replaced by a seeded generator before any page script runs,
 * so every run samples the same collision event; the capture is taken about
 * 1.75 s after the page has loaded, at the fireball moment (impact is at 1.5 s,
 * see assets/js/collision.js). Timing differences between machines can still
 * shift the frame slightly: look at the result before committing it.
 */
const path = require("path");
const { chromium } = require("playwright");

const URL = process.argv[2] || "http://127.0.0.1:4000/";
const OUTPUT = process.argv[3] || path.join(__dirname, "..", "assets", "images", "og-image.jpg");
const WIDTH = 1200;
const HEIGHT = 630;
const WAIT_MS = 1750;   // after load; lands during the fireball
const SEED = 7;         // change to get a different collision
const QUALITY = 86;     // JPEG quality

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: WIDTH, height: HEIGHT }, deviceScaleFactor: 1 });

  // Seeded Park–Miller generator, so the sampled nuclei and impact parameter
  // are the same on every run.
  await page.addInitScript((seed) => {
    let state = seed;
    Math.random = () => (state = (state * 16807) % 2147483647) / 2147483647;
  }, SEED);

  await page.goto(URL, { waitUntil: "networkidle" });
  await page.waitForTimeout(WAIT_MS);
  await page.screenshot({ path: OUTPUT, type: "jpeg", quality: QUALITY });
  await browser.close();
  console.log(`Saved ${OUTPUT} (${WIDTH}×${HEIGHT}) from ${URL}`);
})().catch((err) => {
  console.error(err);
  process.exit(1);
});
