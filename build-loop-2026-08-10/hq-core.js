/* ══════════════════════════════════════════════════════════════════════════
   hq-core.js, the freshness engine shared by every TV page in this folder.

   THE WHOLE POINT, in one paragraph.
   Samuel's complaint on 2026-08-09 was that the TV said a bill was "8 days late"
   and it still said 8 days a day later. That happened because "8d" was typed into
   the page as text. Nothing in this engine stores a computed number. It stores
   DATES and TIMESTAMPS, and every number you see is subtracted at the moment the
   pixel is drawn, then re-drawn every 20 seconds.

   ROUND 2, 2026-08-13. The engine was right and the FIXTURE was wrong. The sample
   file stored absolute timestamps, so three days after it was generated every
   source aged past the 72 hour cutoff and all six screens filled with question
   marks. Two fixes, both here:

     1. rehydrate(). A sample file now ships offsets as well as dates
        (`as_of_rel_min`, `due_rel`, `start_rel`). They resolve against the clock
        at page load, so a fixture written in August still reads in November.
        Source ages re-resolve on every render, so a TV left on for a week does
        not decay. Content dates resolve once at load, so a bill genuinely counts
        up while the screen is running. A LIVE file is never rehydrated: the age
        of a real number is the whole point and must not be staged.

     2. Every question mark says what it needs IN PRINT, not on hover. There is
        no hover on a TV and none on a Fire TV remote. His words: "realistically
        on a TV, I'm not tapping anything. I'm just looking at it."

   THE FRESHNESS STATES: every value carries its own age.
     under 24 hours   normal
     24 to 72 hours   drained of colour, wears a small chip like "30h old"
     over 72 hours    the value is hidden, replaced by "?" plus what it needs
     no source at all "?" plus what it needs
   His standing correction, and the reason for all of it: "you should put a
   question mark or something" beats showing a stale number as if it were true.

   LOAD ORDER in every page. The first two are optional and 404 harmlessly:

     <script src="data.local.js"></script>   real numbers, gitignored, his machine only
     <script src="data.js"></script>         the committed sample
     <script src="hq-core.js"></script>
     ...then HQ.boot(render)

   Over http the engine also tries data.local.json first, then data.json.
   ══════════════════════════════════════════════════════════════════════════ */
"use strict";

var HQ = (function () {

  var HOUR = 3600e3, DAY = 864e5;
  var D = null;
  var loadedFrom = "nothing";
  var isLocal = false;
  var tickers = [];

  /* ── relative dates ─────────────────────────────────────────────────────
     A rel object is either {d: dayOffsetFromToday} or {wd: weekdayOfThisWeek},
     optionally with {h, m}. Sunday is weekday 0, matching the week grid. */
  function relDate(r) {
    if (!r) return null;
    var x = new Date();
    x.setHours(0, 0, 0, 0);
    if (r.wd !== undefined && r.wd !== null) x.setDate(x.getDate() - x.getDay() + r.wd);
    else x.setDate(x.getDate() + (r.d || 0));
    if (r.h !== undefined && r.h !== null) x.setHours(r.h, r.m || 0, 0, 0);
    return x;
  }

  function relDay(r) {
    var x = relDate(r);
    if (!x) return null;
    return x.getFullYear() + "-" +
      String(x.getMonth() + 1).padStart(2, "0") + "-" +
      String(x.getDate()).padStart(2, "0");
  }

  function localIso(d) {
    var off = -d.getTimezoneOffset();
    var sign = off >= 0 ? "+" : "-";
    var ah = Math.floor(Math.abs(off) / 60), am = Math.abs(off) % 60;
    return d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" +
      String(d.getDate()).padStart(2, "0") + "T" +
      String(d.getHours()).padStart(2, "0") + ":" + String(d.getMinutes()).padStart(2, "0") +
      ":" + String(d.getSeconds()).padStart(2, "0") +
      sign + String(ah).padStart(2, "0") + ":" + String(am).padStart(2, "0");
  }

  /* Resolve the staged offsets in a SAMPLE file against the real clock.
     `agesOnly` is the every-render pass: it moves the source ages forward so a
     screen that has been on for a week still demonstrates all four states, while
     leaving the content dates where they were at load so a bill counts up. */
  function rehydrate(d, agesOnly) {
    if (!d || !d.self_dating) return d;
    var now = Date.now();

    Object.keys(d.sources || {}).forEach(function (k) {
      var s = d.sources[k];
      if (s && s.as_of_rel_min !== undefined && s.as_of_rel_min !== null) {
        s.as_of = localIso(new Date(now - s.as_of_rel_min * 60000));
      }
    });
    if (agesOnly) return d;

    (d.bills || []).forEach(function (b) {
      if (b.due_rel) b.due = relDay(b.due_rel);
      if (b.hard_date_rel) b.hard_date = relDay(b.hard_date_rel);
    });
    (d.declines || []).forEach(function (x) {
      if (x.at_rel_min !== undefined && x.at_rel_min !== null)
        x.at = localIso(new Date(now - x.at_rel_min * 60000));
    });
    (d.subscriptions || []).forEach(function (s) {
      if (s.renews_rel) s.renews = relDay(s.renews_rel);
    });
    (d.money_in || []).forEach(function (m) {
      if (m.on_rel) m.on = relDay(m.on_rel);
    });
    (d.events || []).forEach(function (e) {
      if (e.start_rel) e.start = localIso(relDate(e.start_rel));
      if (e.end_rel) e.end = localIso(relDate(e.end_rel));
    });
    (d.deadlines || []).forEach(function (x) {
      if (x.on_rel) x.on = relDay(x.on_rel);
    });
    (d.reminders || []).forEach(function (r) {
      if (r.at_rel) r.at = localIso(relDate(r.at_rel));
    });
    d.rehydrated_at = localIso(new Date());
    return d;
  }

  /* ── loading ────────────────────────────────────────────────────────────
     data.local.* is preferred everywhere and is gitignored, so real numbers can
     live on his machine and never reach the public repo. The .js files are the
     floor: classic script tags, so everything works on a double-click. Then we
     TRY the .json files, which are canonical and will be newer on a real server.
     A browser blocks fetch of a local .json off file://, so that attempt is
     expected to fail there, and failing is fine. */
  function boot(render) {
    if (window.HQ_LOCAL_DATA) { D = window.HQ_LOCAL_DATA; loadedFrom = "data.local.js"; isLocal = true; }
    else if (window.HQ_DATA) { D = window.HQ_DATA; loadedFrom = "data.js"; }
    rehydrate(D);
    start(render);

    tryFetch("data.local.json", true, render, function () {
      tryFetch("data.json", false, render, function () { });
    });
  }

  function tryFetch(url, local, render, onFail) {
    try {
      fetch(url, { cache: "no-store" })
        .then(function (r) { return r.ok ? r.json() : null; })
        .then(function (j) {
          if (!j) { onFail(); return; }
          // never let a stale json overwrite a newer js
          if (D && j.generated_at && D.generated_at && !local &&
            new Date(j.generated_at) <= new Date(D.generated_at)) { onFail(); return; }
          D = rehydrate(j);
          loadedFrom = url; isLocal = local;
          render();
        })
        .catch(function () { onFail(); });
    } catch (e) { onFail(); }
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
    setInterval(function () { rehydrate(D, true); render(); }, 20000);
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

  /* How long since the FILE itself was written. When a live file goes cold this
     is the real reason every value vanished, so it has to be said out loud
     instead of leaving nine identical question marks with no cause. */
  function fileAgeDays() {
    var ms = ageMs(D && D.generated_at);
    return isFinite(ms) ? Math.floor(ms / DAY) : null;
  }

  function coldFile() {
    if (!D || D.self_dating) return null;
    var days = fileAgeDays();
    if (days === null || days < 3) return null;
    return "the data file has not been rebuilt in " + days +
      " days. run make-data.py, see refresh.md";
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
      needs: s.needs || coldFile() || (state === "unknown"
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

  /* "11 days late", "today", "tomorrow", "in 4 days". computed, every time */
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

  /* A gap in minutes, said in words. Used for every countdown on every page.
     It exists because the same ternary was written five times by hand and one of
     those copies wrapped a string in Math.abs and printed "NaN" on screen. */
  function gapText(ms) {
    var mm = Math.round(ms / 60000);
    var past = mm < 0;
    var a = Math.abs(mm);
    var t;
    if (a < 1) t = "now";
    else if (a < 60) t = a + (a === 1 ? " minute" : " minutes");
    else if (a < 1440) t = Math.floor(a / 60) + "h " + (a % 60) + "m";
    else { var d = Math.round(a / 1440); t = d + (d === 1 ? " day" : " days"); }
    if (t === "now") return "now";
    return past ? t + " ago" : "in " + t;
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

  /* ── the field renderer. THIS is where the states happen ────────────────
     field("money", "$59.99")           the value, plus its state
     field("bank", null, {needs:"..."}) a question mark that SAYS what it needs,
                                        in print, because a TV has no hover.
     Pass {note:false} when the page prints the reason somewhere itself. */
  function field(sourceKey, value, opts) {
    opts = opts || {};
    var f = fresh(sourceKey);
    var missing = (value === null || value === undefined || value === "");
    if (f.state === "unknown" || missing) {
      var why = opts.needs || f.needs || "no source";
      if (f.state === "unknown" && coldFile()) why = coldFile();
      return '<span class="hq-un" title="' + esc(why) + '">?</span>' +
        (opts.note === false ? "" : '<span class="hq-note">' + esc(why) + '</span>');
    }
    var chip = f.state === "stale"
      ? '<span class="hq-chip" title="' + esc(f.label) + ' last updated ' + f.age + '">' + f.age + '</span>'
      : "";
    return '<span class="hq-v hq-' + f.state + '">' + esc(value) + '</span>' + chip;
  }

  /* An amount, with the invented tag attached to the NUMBER rather than to a
     header three inches away. Round 2 fix: TV03 printed five exact dollar figures
     at full confidence under a header that said NO SOURCE. */
  function amt(value, sample, sourceKey, needs) {
    var key = sourceKey || "money";
    var m = money(value);
    if (m === null) return field(key, null, { needs: needs, note: false }) +
      (needs ? '<span class="hq-note">' + esc(needs) + '</span>' : "");
    // An invented figure is not a stale figure. It never claimed to come from the
    // source, so the freshness gate does not apply to it. What it needs instead is
    // the word "invented" welded to the number, which is what the tag is.
    if (sample) return '<span class="hq-v">' + m + '</span><i class="hq-inv">invented</i>';
    var f = fresh(key);
    if (f.state === "unknown")
      return field(key, null, { needs: needs || f.needs, note: false }) +
        '<span class="hq-note">' + esc(needs || f.needs) + '</span>';
    return '<span class="hq-v hq-' + f.state + '">' + m + '</span>';
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
    b.innerHTML = '<b>SAMPLE DATA</b><span>every amount is invented and tagged. ' +
      'the ages are staged against the clock you opened this at, so all four ' +
      'states show at once. it goes when data.local.json says mode: live.</span>';
    document.body.appendChild(b);
    document.documentElement.classList.add("hq-sample");
  }

  /* ── the live refresh line. counts up by itself, once a second ────────── */
  function refreshLine(el) {
    if (!el) return;
    var f = function () {
      if (D && D.self_dating) {
        el.innerHTML = '<i class="hq-dot ok"></i>sample clock&nbsp;<b>staged at load</b>' +
          '&nbsp;· from ' + esc(loadedFrom);
        return;
      }
      var ms = ageMs(D.generated_at);
      var s = Math.floor(ms / 1000);
      var t = s < 60 ? s + "s ago"
        : s < 3600 ? Math.floor(s / 60) + "m " + (s % 60) + "s ago"
          : ageText(ms);
      var stale = ms > 24 * HOUR;
      el.innerHTML = '<i class="hq-dot ' + (stale ? "bad" : "ok") + '"></i>' +
        'data written&nbsp;<b>' + t + '</b>&nbsp;· from ' + esc(loadedFrom) +
        (stale ? ' · run make-data.py, see refresh.md' : '');
    };
    tickers.push(f); f();
  }

  function everySecond(fn) { tickers.push(fn); fn(); }

  return {
    boot: boot, data: data, fresh: fresh, field: field, amt: amt, mark: mark,
    ageMs: ageMs, ageText: ageText, daysFromToday: daysFromToday,
    dueText: dueText, dueTone: dueTone, shortDate: shortDate, clockOf: clockOf,
    gapText: gapText, relDate: relDate, relDay: relDay,
    money: money, esc: esc, refreshLine: refreshLine, everySecond: everySecond,
    fileAgeDays: fileAgeDays, coldFile: coldFile,
    source: function () { return loadedFrom; },
    isLocal: function () { return isLocal; }
  };
})();

/* ── shared CSS for the freshness states, the printed notes, and the ribbon ─
   Injected rather than duplicated into every stylesheet, so a fix lands once.
   Everything else about how a page looks stays in that page. */
(function () {
  var css = document.createElement("style");
  css.textContent = [
    "#hq-ribbon{position:fixed;left:0;right:0;bottom:0;z-index:900;display:flex;gap:.9em;",
    "align-items:baseline;justify-content:center;padding:.5em 1em;",
    "background:repeating-linear-gradient(135deg,#3a2a08 0 14px,#2e2106 14px 28px);",
    "border-top:2px solid #c9a96a;color:#e8d5a8;font:600 clamp(9px,1vw,15px)/1.3 inherit;",
    "letter-spacing:.06em;pointer-events:none}",
    "#hq-ribbon b{color:#ffd98a;letter-spacing:.22em;font-weight:800;flex-shrink:0}",
    "#hq-ribbon span{opacity:.72;font-weight:500;letter-spacing:.02em}",
    ".hq-sample body{padding-bottom:0}",
    ".hq-v{transition:filter .6s,opacity .6s}",
    ".hq-stale{filter:saturate(.12) contrast(.92);opacity:.66}",
    ".hq-chip{display:inline-block;margin-left:.45em;padding:.12em .5em;border-radius:999px;",
    "border:1px solid currentColor;opacity:.5;font-size:clamp(9px,.52em,17px);font-weight:700;",
    "letter-spacing:.08em;vertical-align:.28em;white-space:nowrap}",
    ".hq-un{display:inline-block;font-weight:800;opacity:.55}",
    /* the reason, in print. there is no hover on a TV and none on a remote. */
    ".hq-note{display:inline-block;margin-left:.42em;vertical-align:.16em;white-space:normal;",
    "font-size:clamp(10px,.38em,17px);font-weight:600;letter-spacing:.01em;line-height:1.25;",
    "text-transform:none;opacity:.62;max-width:30ch;text-align:left;overflow:hidden;",
    "display:-webkit-inline-box;-webkit-line-clamp:2;-webkit-box-orient:vertical}",
    /* the invented tag rides the number itself, never a distant header */
    ".hq-inv{display:inline-block;margin-left:.4em;vertical-align:.3em;font-style:normal;",
    "font-size:clamp(8px,.34em,13px);font-weight:800;letter-spacing:.14em;text-transform:uppercase;",
    "opacity:.75;border:1px dashed currentColor;border-radius:2px;padding:0 .35em;white-space:nowrap}",
    ".hq-s-stale{--hq-drain:#6b6155}",
    ".hq-dot{display:inline-block;width:.6em;height:.6em;border-radius:50%;",
    "margin-right:.5em;background:#7e9b7a;vertical-align:middle;flex-shrink:0}",
    ".hq-dot.bad{background:#d0402e}",
    "@media (max-width:700px){.hq-note{max-width:100%;display:block;margin:.2em 0 0}",
    "#hq-ribbon{padding:.4em .7em;gap:.6em;font-size:10.5px}",
    "#hq-ribbon span{display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;",
    "overflow:hidden}}",
    "@media (prefers-reduced-motion:reduce){.hq-v{transition:none}}"
  ].join("");
  document.head.appendChild(css);
})();
