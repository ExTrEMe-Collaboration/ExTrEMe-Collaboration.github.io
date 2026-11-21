/*
 * Hero animation: a stylized heavy-ion collision seen in the reaction plane.
 * Two Lorentz-contracted nuclei collide at a random impact parameter; the
 * participant nucleons form a hot fireball that expands (mostly along the
 * beam) and freezes out into hadrons, while spectators fly on.
 * Purely decorative, dependency-free; honours prefers-reduced-motion and
 * pauses when off-screen or in a background tab.
 *
 * This is an artistic sketch, not a physics simulation. The collaboration's
 * actual model (TRENTo → KoMPoST → MUSIC → iSS → UrQMD) is described on the
 * Simulation chain page. Maintainer notes: assets/README.md, "Hero animation".
 *
 * Geometry: the beam runs horizontally (x); y is the in-plane transverse
 * direction (the impact parameter is vertical); a hidden depth coordinate z is
 * used only to decide which nucleons collide. Lengths are in CSS pixels,
 * scaled by the nuclear radius R; times are in seconds.
 *
 * One event, in time order (t = seconds since the event started,
 * tau = t - T_HIT = time since impact):
 *   t < T_HIT          two nuclei approach along the beam axis
 *   tau 0 … 0.45       impact flash at the collision point
 *   tau 0 … T_FREEZE   participants glow as a fireball that grows and cools
 *   tau = T_FREEZE     freeze-out: hadron streaks are emitted
 *   tau T_FREEZE … +0.7  fireball fades; hadrons fly out for ~2.9 s
 *   tau 0 … 1.6        spectators keep flying and fade
 *   t = T_END          a new event (new impact parameter, new nucleons) starts
 *
 * The page CSS (.hero-shade in assets/css/site.css) darkens the left side so
 * the text stays readable; colours used here are written inline below and are
 * independent of the CSS colour tokens.
 */
(function () {
  "use strict";

  var canvas = document.querySelector("[data-collision]");
  if (!canvas || !canvas.getContext) return;
  var ctx = canvas.getContext("2d");
  var reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // ---- Main knobs -----------------------------------------------------------
  var NUCLEONS = 60;        // per nucleus
  var T_HIT = 1.5;          // seconds until impact
  var T_FREEZE = 1.05;      // fireball lifetime before hadronization
  var T_END = T_HIT + 4.4;  // end of one event
  var CONTRACTION = 0.16;   // pancake thickness / radius

  // Canvas size, collision point (cx, cy), nuclear radius R and the speed of
  // the incoming nuclei; all set in resize().
  var W = 0, H = 0, cx = 0, cy = 0, R = 0, speed = 0;
  var event = null;
  var running = false, visible = true, lastTime = 0, rafId = 0;

  function rand(a, b) { return a + Math.random() * (b - a); }
  // Standard normal deviate (Box–Muller).
  function gauss() {
    var u = 1 - Math.random(), v = Math.random();
    return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);
  }
  function clamp01(x) { return x < 0 ? 0 : x > 1 ? 1 : x; }

  // Fit the canvas to its box and place the collision. On wide screens the
  // collision sits right of the text (74% across, 46% down); on narrow screens
  // it is centred near the top, behind the headline. The device-pixel ratio is
  // capped at 2 to bound the canvas size on high-density screens. Every resize
  // starts a fresh event, because positions are stored in pixels.
  function resize() {
    var rect = canvas.getBoundingClientRect();
    var dpr = Math.min(window.devicePixelRatio || 1, 2);
    W = rect.width;
    H = rect.height;
    canvas.width = Math.max(1, Math.round(W * dpr));
    canvas.height = Math.max(1, Math.round(H * dpr));
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    var wide = W > 720;
    cx = wide ? W * 0.74 : W * 0.5;
    cy = wide ? H * 0.46 : H * 0.3;
    R = Math.max(28, Math.min(H * 0.2, wide ? W * 0.1 : W * 0.24));
    // The left nucleus starts just off-screen and reaches cx exactly at T_HIT.
    speed = (cx + 1.4 * R) / T_HIT;
    event = newEvent();
  }

  // Sample one event: two nuclei of NUCLEONS nucleons each.
  function newEvent() {
    var b = rand(0.3, 1.15) * R; // impact parameter (vertical offset)
    var centers = [cy - b / 2, cy + b / 2];
    var nucleons = [];
    for (var side = 0; side < 2; side++) {
      var yc = centers[side], yOther = centers[1 - side];
      for (var i = 0; i < NUCLEONS; i++) {
        // Uniform in the transverse disk of radius R (sqrt makes it uniform in area).
        var r = Math.sqrt(Math.random()) * R;
        var th = Math.random() * 2 * Math.PI;
        var ty = r * Math.cos(th);           // transverse, in the reaction plane
        var tz = r * Math.sin(th);           // transverse, out of plane (depth)
        var y = yc + ty;
        nucleons.push({
          dir: side === 0 ? 1 : -1,          // +1 moves right, -1 moves left
          // Offset along the beam: a sphere profile squashed by CONTRACTION
          // (thickest at the centre of the disk, zero at its edge).
          ux: rand(-1, 1) * Math.sqrt(Math.max(0, 1 - (r * r) / (R * R))) * R * CONTRACTION,
          y: y,
          // Participant if its transverse position (in-plane y and depth z)
          // lies within ~0.92 R of the other nucleus's centre.
          participant: Math.hypot(y - yOther, tz) < R * 0.92,
          // Gaussian "rapidity": how far this participant's glow spreads along
          // the beam, and the longitudinal kick given to its hadrons.
          rapidity: gauss(),
          // Current fireball position of a participant; written by draw().
          px: 0, py: 0
        });
      }
    }
    return { t: 0, nucleons: nucleons, hadrons: [], frozen: false };
  }

  // Freeze-out: emit hadron streaks from the participants' fireball positions.
  function spawnHadrons(ev) {
    var parts = ev.nucleons.filter(function (n) { return n.participant; });
    var count = Math.min(320, parts.length * 3);  // up to 320 streaks
    var v0 = Math.max(W, H) * 0.24;               // typical speed, px/s
    for (var i = 0; i < count; i++) {
      var p = parts[(Math.random() * parts.length) | 0];
      var phi = Math.random() * 2 * Math.PI;      // random emission angle
      var s = rand(0.35, 1) * v0;
      var species = Math.random();
      ev.hadrons.push({
        x: p.px, y: p.py,
        // Random direction plus a longitudinal kick from the parent's rapidity.
        vx: Math.cos(phi) * s * 0.9 + p.rapidity * v0 * 0.55,
        vy: Math.sin(phi) * s * 0.75,
        age: -Math.random() * 0.35,         // stagger emission a little
        // ~70% gold "pions", ~17% cyan "kaons", ~13% pink "protons" (RGB).
        color: species < 0.7 ? "253, 224, 138" : species < 0.87 ? "103, 232, 249" : "251, 113, 133"
      });
    }
  }

  // Advance the clock by dt seconds: trigger freeze-out once, move hadrons,
  // and start a new event after T_END.
  function update(dt) {
    var ev = event;
    ev.t += dt;
    var tau = ev.t - T_HIT;
    if (tau > T_FREEZE && !ev.frozen) {
      ev.frozen = true;
      spawnHadrons(ev);
    }
    for (var i = 0; i < ev.hadrons.length; i++) {
      var h = ev.hadrons[i];
      h.age += dt;
      if (h.age > 0) { h.x += h.vx * dt; h.y += h.vy * dt; }
    }
    if (ev.t > T_END) event = newEvent();
  }

  // Background: faint concentric "detector" rings and a dashed beam line.
  function drawDetector() {
    ctx.save();
    ctx.lineWidth = 1;
    var radii = [1.8, 2.6, 3.6, 4.9, 6.5];  // in units of R
    for (var i = 0; i < radii.length; i++) {
      ctx.strokeStyle = "rgba(255, 255, 255, " + (0.07 - i * 0.01) + ")";
      ctx.beginPath();
      ctx.arc(cx, cy, R * radii[i], 0, 2 * Math.PI);
      ctx.stroke();
    }
    ctx.setLineDash([2, 6]);
    ctx.strokeStyle = "rgba(255, 255, 255, 0.08)";
    ctx.beginPath();
    ctx.moveTo(0, cy);
    ctx.lineTo(W, cy);
    ctx.stroke();
    ctx.restore();
  }

  // Draw the current state of the event.
  function draw() {
    var ev = event;
    var t = ev.t;
    var tau = t - T_HIT;
    ctx.clearRect(0, 0, W, H);
    drawDetector();

    ctx.save();
    // Additive blending: overlapping glows add up, so the dense core of the
    // fireball comes out brighter than its edges.
    ctx.globalCompositeOperation = "lighter";

    // Impact flash: a white-orange glow that grows and fades within 0.45 s.
    if (tau > 0 && tau < 0.45) {
      var k = 1 - tau / 0.45;
      var fr = R * (1.2 + 2.2 * tau);
      var flash = ctx.createRadialGradient(cx, cy, 0, cx, cy, fr);
      flash.addColorStop(0, "rgba(255, 250, 235, " + 0.75 * k + ")");
      flash.addColorStop(0.4, "rgba(253, 186, 116, " + 0.35 * k + ")");
      flash.addColorStop(1, "rgba(249, 115, 22, 0)");
      ctx.fillStyle = flash;
      ctx.fillRect(cx - fr, cy - fr, 2 * fr, 2 * fr);
    }

    // Fireball from participants: one radial gradient per participant.
    if (tau > 0) {
      var growth = 1 - Math.exp(-tau / 0.55);   // 0 → 1, expansion
      var heat = Math.exp(-tau / 0.9);          // 1 → 0, cooling
      var fade = tau < T_FREEZE ? 1 : clamp01(1 - (tau - T_FREEZE) / 0.7);
      var blob = R * (0.2 + 0.3 * growth);      // glow radius
      // Core colour cools from white-yellow to orange to red.
      var rgbCore = heat > 0.55 ? "255, 244, 214" : heat > 0.3 ? "253, 186, 116" : "248, 113, 113";
      if (fade > 0) {
        for (var i = 0; i < ev.nucleons.length; i++) {
          var n = ev.nucleons[i];
          if (!n.participant) continue;
          // Strong spread along the beam (rapidity), milder transverse growth.
          n.px = cx + n.ux * 0.4 + n.rapidity * R * 1.1 * growth;
          n.py = cy + (n.y - cy) * (1 + 0.45 * growth);
          var g = ctx.createRadialGradient(n.px, n.py, 0, n.px, n.py, blob);
          g.addColorStop(0, "rgba(" + rgbCore + ", " + 0.22 * fade + ")");
          g.addColorStop(0.5, "rgba(249, 115, 22, " + 0.1 * fade + ")");
          g.addColorStop(1, "rgba(225, 29, 72, 0)");
          ctx.fillStyle = g;
          ctx.fillRect(n.px - blob, n.py - blob, 2 * blob, 2 * blob);
        }
      }
    }

    // Hadrons: short streaks along their velocity, fading out over ~2.9 s.
    for (var j = 0; j < ev.hadrons.length; j++) {
      var h = ev.hadrons[j];
      if (h.age <= 0) continue;
      var a = clamp01(1 - h.age / 2.9);
      if (a <= 0) continue;
      ctx.strokeStyle = "rgba(" + h.color + ", " + 0.75 * a + ")";
      ctx.lineWidth = 1.3;
      ctx.beginPath();
      ctx.moveTo(h.x - h.vx * 0.07, h.y - h.vy * 0.07);
      ctx.lineTo(h.x, h.y);
      ctx.stroke();
    }
    ctx.restore();

    // Incoming nuclei and outgoing spectators: before impact every nucleon is
    // drawn; afterwards only the spectators, which keep their speed and fade
    // out over 1.6 s. Blue = nucleus from the left, peach = from the right.
    var nr = R * 0.085;
    for (var m = 0; m < ev.nucleons.length; m++) {
      var nu = ev.nucleons[m];
      if (tau > 0 && nu.participant) continue;
      var alpha = tau > 0 ? clamp01(1 - tau / 1.6) : 1;
      if (alpha <= 0) continue;
      var x = cx - nu.dir * speed * (T_HIT - t) + nu.ux;
      ctx.fillStyle = nu.dir > 0
        ? "rgba(165, 190, 255, " + 0.85 * alpha + ")"
        : "rgba(255, 190, 150, " + 0.85 * alpha + ")";
      ctx.beginPath();
      ctx.arc(x, nu.y, nr, 0, 2 * Math.PI);
      ctx.fill();
    }
  }

  // Animation loop. dt is capped at 50 ms so the event does not jump ahead
  // after the tab or the canvas was paused.
  function frame(now) {
    if (!running) return;
    var dt = Math.min(0.05, (now - lastTime) / 1000 || 0);
    lastTime = now;
    update(dt);
    draw();
    rafId = requestAnimationFrame(frame);
  }

  // Runs only when motion is allowed, the canvas is on screen and the tab is visible.
  function start() {
    if (running || reduceMotion || !visible || document.hidden) return;
    running = true;
    lastTime = performance.now();
    rafId = requestAnimationFrame(frame);
  }
  function stop() {
    running = false;
    cancelAnimationFrame(rafId);
  }

  // prefers-reduced-motion: no animation, a single still frame instead.
  // Known issue: participants' fireball positions (px, py) are only computed
  // in draw(), which this loop does not call, so the hadrons of the still frame
  // start from the canvas corner (0, 0). See assets/README.md.
  function renderStill() {
    // Advance a fresh event to just after hadronization and draw one frame.
    event = newEvent();
    var target = T_HIT + T_FREEZE + 0.55;
    while (event.t < target) update(1 / 60);
    draw();
  }

  resize();
  if (reduceMotion) {
    renderStill();
  } else {
    start();
  }

  // Re-fit (and restart the event) shortly after the window stops resizing.
  var resizeTimer = 0;
  window.addEventListener("resize", function () {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function () {
      resize();
      if (reduceMotion) renderStill();
    }, 120);
  });

  // Pause in background tabs…
  document.addEventListener("visibilitychange", function () {
    if (document.hidden) stop(); else start();
  });

  // …and while the hero is scrolled out of view.
  if ("IntersectionObserver" in window) {
    new IntersectionObserver(function (entries) {
      visible = entries[0].isIntersecting;
      if (visible) start(); else stop();
    }).observe(canvas);
  }
})();
