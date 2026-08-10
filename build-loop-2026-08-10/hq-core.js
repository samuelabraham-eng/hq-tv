/* ══════════════════════════════════════════════════════════════════════════
   hq-core.js — the freshness engine shared by TV01 through TV06.

   THE WHOLE POINT, in one paragraph.
   Samuel's complaint on 2026-08-09 was that the TV said a bill was "8 days late"
   and it still said 8 days a day later. That happened because "8d" was typed into
   the page as text. Nothing in this engine stores a computed number. It stores
   DATES and TIMESTAMPS, and every number you see is subtracted at the moment the
   pixel is drawn, then re-drawn every 20 seconds. Tomorrow the screen counts up
   on its own with nobody touching anything.

   THE SECOND POINT: every value carries its own age.
     under 24 hours   normal
     24 to 72 hours   drained of colour, wears a small chip like "30h old"
     over 72 hours    the value is hidden and replaced with "?" plus what it needs
     no source at all "?" plus what it needs
   His standing correction, and the reason for all of it: "you should put a
   question mark or something" beats showing a stale number as if it were true.

   Load order in every page:
     <script src="data.js"></script>      window.HQ_DATA, works on file://
     <script src="hq-core.js"></script>
     ...then HQ.boot(render)
   ══════════════════════════════════════════════════════════════════════════ */
"use strict";

var HQ = (function () {

  var HOUR = 3600e3, DAY = 864e5;
  var D = null;
  var loadedFrom = "nothing";
  var tickers = [];

  /* ── loading ────────────────────────────────────────────────────────────
     data.js is the floor: a classic script tag, so it works when the file is
     opened by double-click. Then we TRY data.json, which is the canonical file
     and will be newer on a real server. A browser blocks fetch of a local .json
     off file://, so that attempt is expected to fail there, and failing is fine. */
  function boot(render) {
    if (window.HQ_DATA) { D = window.HQ_DATA; loadedFrom = "data.js"; }
    start(render);
    try {
      fetch("data.json", { cache: "no-store" })
        .then(function (r) { return r.ok ? r.json() : null; })
        .then(function (j) {
          if (!j) return;
          if (D && j.generated_at && D.generated_at && new Date(j.generated_at) <= new Date(D.generated_at)) {
            loadedFrom = "data.json"; return;
          }
          D = j; loadedFrom = "data.json"; render();
        })
        .catch(function () { /* file:// . expected. data.js already carried us. */ });
    } catch (e) { }
  }

  function start(render) {
    if (!D) {
      document.body.innerHTML =
        '<div style="font:600 18px/1.6 system-ui;color:#d0402e;padding:8vw;max-width:40ch">' +
        'No data file loaded.<br>data.js is missing next to this page. ' +
        'Run <b>python3 make-data.py</b> in this folder and reopen.</div>';
      return;
    }
    ribbon();
    render();
    // Re-render on a slow beat. Every relative number recomputes itself here.
    setInterval(function () { render(); }, 20000);
    setInterval(function () { tickers.forEach(function (f) { f(); }); }, 1000);
    tickers.forEach(function (f) { f(); });
  }

  function data() { return D; }

  /* ── ages ─────────────────────────────────────────────────────────────── */
  function ageMs(iso) {
    if (!iso) return Infinity;
    var t = new Date(iso).getTime();
    if (isNaN(t)) return Infinity;
    return Math.max(0, Date.now() - t);
  }

  function ageText(ms) {
    if (!isFinite(ms)) return "no source";
    var m = Math.floor(ms / 60000);
    if (m < 1) return "just now";
    if (m < 60) return m + "m old";
    var h = Math.floor(ms / HOUR);
    if (h < 48) return h + "h old";
    return Math.floor(ms / DAY) + "d old";
  }

  /* fresh | stale | unknown, for one source key */
  function fresh(key) {
    var s = (D.sources || {})[key] || {};
    var ms = ageMs(s.as_of);
    var state = ms < 24 * HOUR ? "fresh" : ms < 72 * HOUR ? "stale" : "unknown";
    return {
      key: key, state: state, ms: ms,
      age: ageText(ms),
      label: s.label || key,
      kind: s.kind || "",
      needs: s.needs || (state === "unknown"
        ? "nothing has written this in over three days"
        : ""),
      // 0 to 1 across the 24 hour fresh window. drives the drain bars.
      left: Math.max(0, Math.min(1, 1 - ms / (24 * HOUR)))
    };
  }

  /* ── dates. always subtracted, never stored ───────────────────────────── */
  function midnight(d) { var x = new Date(d); x.setHours(0, 0, 0, 0); return x; }

  function daysFromToday(dateStr) {
    if (!dateStr) return null;
    var s = String(dateStr).length <= 10 ? dateStr + "T00:00:00" : dateStr;
    var t = new Date(s);
    if (isNaN(t.getTime())) return null;
    return Math.round((midnight(t) - midnight(new Date())) / DAY);
  }

  /* "11 days late" · "today" · "tomorrow" · "in 4 days" — computed, every time */
  function dueText(dateStr) {
    var d = daysFromToday(dateStr);
    if (d === null) return "?";
    if (d < -1) return (-d) + " days late";
    if (d === -1) return "1 day late";
    if (d === 0) return "today";
    if (d === 1) return "tomorrow";
    return "in " + d + " days";
  }

  function dueTone(dateStr) {
    var d = daysFromToday(dateStr);
    if (d === null) return "unknown";
    if (d < 0) return "late";
    if (d <= 2) return "now";
    if (d <= 7) return "soon";
    return "later";
  }

  function shortDate(dateStr) {
    if (!dateStr) return "";
    var s = String(dateStr).length <= 10 ? dateStr + "T00:00:00" : dateStr;
    var t = new Date(s);
    if (isNaN(t.getTime())) return "";
    return t.toLocaleDateString(undefined, { month: "short", day: "numeric" }).toLowerCase();
  }

  function clockOf(iso) {
    var t = new Date(iso);
    if (isNaN(t.getTime())) return "";
    var h = t.getHours(), m = t.getMinutes();
    var mer = h >= 12 ? "pm" : "am";
    h = h % 12 || 12;
    return h + (m ? ":" + String(m).padStart(2, "0") : "") + mer;
  }

  /* ── money. a null amount is never a zero ─────────────────────────────── */
  function money(n) {
    if (n === null || n === undefined) return null;
    return "$" + Number(n).toLocaleString(undefined,
      { minimumFractionDigits: n % 1 ? 2 : 0, maximumFractionDigits: 2 });
  }

  function esc(s) {
    return String(s === null || s === undefined ? "" : s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  /* ── the field renderer. THIS is where the three states happen ──────────
     field("money", "$59.99")          → the value, plus its state
     field("bank", null, {needs:"..."}) → a question mark that says what it needs */
  function field(sourceKey, value, opts) {
    opts = opts || {};
    var f = fresh(sourceKey);
    var missing = (value === null || value === undefined || value === "");
    if (f.state === "unknown" || missing) {
      var why = opts.needs || f.needs || "no source";
      return '<span class="hq-un" title="' + esc(why) + '">?<span class="hq-why">' +
        esc(why) + '</span></span>';
    }
    var chip = f.state === "stale"
      ? '<span class="hq-chip" title="' + esc(f.label) + ' last updated ' + f.age + '">' + f.age + '</span>'
      : "";
    return '<span class="hq-v hq-' + f.state + '">' + esc(value) + '</span>' + chip;
  }

  /* mark any container with the state of its source, so CSS can drain it */
  function mark(el, sourceKey) {
    if (!el) return;
    var f = fresh(sourceKey);
    el.classList.remove("hq-s-fresh", "hq-s-stale", "hq-s-unknown");
    el.classList.add("hq-s-" + f.state);
    el.style.setProperty("--hq-left", (f.left * 100).toFixed(1) + "%");
    return f;
  }

  /* ── the sample ribbon. it is not decorative, it is a guard rail ──────── */
  function ribbon() {
    if (!D || D.mode === "live") return;
    if (document.getElementById("hq-ribbon")) return;
    var b = document.createElement("div");
    b.id = "hq-ribbon";
    b.innerHTML = '<b>SAMPLE DATA</b><span>every amount on this screen is invented. ' +
      'it disappears when data.json says mode: live.</span>';
    document.body.appendChild(b);
    document.documentElement.classList.add("hq-sample");
  }

  /* ── the live refresh line. counts up by itself, once a second ────────── */
  function refreshLine(el) {
    if (!el) return;
    var f = function () {
      var ms = ageMs(D.generated_at);
      var s = Math.floor(ms / 1000);
      var t = s < 60 ? s + "s ago"
        : s < 3600 ? Math.floor(s / 60) + "m " + (s % 60) + "s ago"
          : ageText(ms);
      var stale = ms > 24 * HOUR;
      el.innerHTML = '<i class="hq-dot ' + (stale ? "bad" : "ok") + '"></i>' +
        'data written&nbsp;<b>' + t + '</b>&nbsp;· from ' + esc(loadedFrom) +
        (stale ? ' · nothing has refreshed this in over a day' : '');
    };
    tickers.push(f); f();
  }

  function everySecond(fn) { tickers.push(fn); fn(); }

  return {
    boot: boot, data: data, fresh: fresh, field: field, mark: mark,
    ageMs: ageMs, ageText: ageText, daysFromToday: daysFromToday,
    dueText: dueText, dueTone: dueTone, shortDate: shortDate, clockOf: clockOf,
    money: money, esc: esc, refreshLine: refreshLine, everySecond: everySecond,
    source: function () { return loadedFrom; }
  };
})();

/* ── shared CSS for the three freshness states + the ribbon ───────────────
   Injected rather than duplicated into six stylesheets, so a fix lands once.
   Everything else about how a page looks stays in that page. */
(function () {
  var css = document.createElement("style");
  css.textContent = [
    "#hq-ribbon{position:fixed;left:0;right:0;bottom:0;z-index:900;display:flex;gap:.9em;",
    "align-items:baseline;justify-content:center;padding:.5em 1em;",
    "background:repeating-linear-gradient(135deg,#3a2a08 0 14px,#2e2106 14px 28px);",
    "border-top:2px solid #c9a96a;color:#e8d5a8;font:600 clamp(9px,1vw,15px)/1.3 inherit;",
    "letter-spacing:.06em;pointer-events:none}",
    "#hq-ribbon b{color:#ffd98a;letter-spacing:.22em;font-weight:800}",
    "#hq-ribbon span{opacity:.72;font-weight:500;letter-spacing:.02em}",
    ".hq-sample body{padding-bottom:0}",
    ".hq-v{transition:filter .6s,opacity .6s}",
    ".hq-stale{filter:saturate(.12) contrast(.92);opacity:.66}",
    ".hq-chip{display:inline-block;margin-left:.45em;padding:.12em .5em;border-radius:999px;",
    "border:1px solid currentColor;opacity:.5;font-size:.52em;font-weight:700;",
    "letter-spacing:.08em;vertical-align:.28em;white-space:nowrap}",
    ".hq-un{position:relative;display:inline-block;font-weight:800;opacity:.5;cursor:help}",
    ".hq-why{position:absolute;left:50%;bottom:125%;transform:translateX(-50%);",
    "width:max-content;max-width:26ch;padding:.5em .7em;border-radius:6px;",
    "background:#0b0908;border:1px solid #4a3f2e;color:#cdbfa5;font-size:.42em;",
    "font-weight:500;letter-spacing:0;line-height:1.4;opacity:0;pointer-events:none;",
    "transition:opacity .2s;z-index:80;text-transform:none}",
    ".hq-un:hover .hq-why{opacity:1}",
    ".hq-s-stale{--hq-drain:#6b6155}",
    ".hq-dot{display:inline-block;width:.6em;height:.6em;border-radius:50%;",
    "margin-right:.5em;background:#7e9b7a;vertical-align:middle}",
    ".hq-dot.bad{background:#d0402e}",
    "@media (max-width:700px){.hq-why{left:auto;right:0;transform:none;max-width:70vw}}",
    "@media (prefers-reduced-motion:reduce){.hq-v{transition:none}}"
  ].join("");
  document.head.appendChild(css);
})();
