# NOTES.md, hq-tv build loop 2026-08-10

> Written for the next AGENT doing forensics, not for Samuel. He reads the launcher and
> the pages. Never open this at him.
> Required by LOOP-BRIEF.md. Round 1 did not write it. This file covers both rounds.

## What this folder is

An exploration run against `projects/hq-tv`. Nine screens, one launcher, one data layer.
Nothing here is approved, nothing here replaces `../index.html`, and neither round created,
modified, moved or deleted a single file outside this folder. The live build and its locked
noir theme are byte identical to what they were on 2026-08-10.

Build codes used: **TV01 to TV06** (round 1, 2026-08-10) and **TV10 to TV12**
(round 2, 2026-08-13). `TV07`, `TV08`, `TV09` were reserved by LOOP-BRIEF and never minted.
`TV13` to `TV16` were reserved for round 2 and are unused. Codes are permanent. Do not
recycle any of them.

| code | file | what it is |
|---|---|---|
| TV01 | `TV01-live.html` | the freshness engine made visible. warm noir. |
| TV02 | `TV02-week.html` | the Toggl week grid. cold ink. |
| TV03 | `TV03-money.html` | one money timeline, today in the middle. |
| TV04 | `TV04-console.html` | broadsheet. the most on one screen. |
| TV05 | `TV05-dayparts.html` | four screens chosen by the clock. |
| TV06 | `TV06-board.html` | printed agenda page. the only light screen. |
| TV10 | `TV10-views.html` | the calendar VIEW toggle. week, month, day, agenda. |
| TV11 | `TV11-sky.html` | the real sun and moon over Arlington. needs nothing. |
| TV12 | `TV12-mosaic.html` | the actual Metro treatment. live tiles that flip. |

## Round 1, 2026-08-10, what it built and what it got wrong

The thinking underneath was right and is kept: `hq-core.js` stores dates and subtracts at
render, so a bill counts up on its own, and every value inherits the age of the source it
came from. That is a real answer to his 2026-08-09 complaint that "8 days late" never moved.

It was then handed over without anyone opening it. An outside reviewer found, and round 2
fixed, all of the following.

### The blockers

1. **Every screen decayed to question marks after 72 hours.** `data.js` stored absolute
   `as_of` timestamps. `hq-core` hides any value whose source is over three days old. Opened
   on 2026-08-13 all nine sources read `unknown`, TV04's header band was nine identical red
   `no source` labels, and TV01's headline tile, the one built specifically to answer his
   complaint, rendered a bare `?`. The pages whose stated thesis is "nothing here is a stored
   string" were broken by the only strings that were stored.
   **Fixed** by giving the sample file offsets alongside its dates (`as_of_rel_min`,
   `due_rel`, `start_rel`, and the rest) and resolving them in `hq-core.rehydrate()` at page
   load. Source ages re-resolve every render so a wall screen left on for a week keeps
   working; content dates resolve once at load so a bill still genuinely counts up while the
   screen runs. A live file is never rehydrated. Full contract in `SCHEMA.md`.
   Also added `HQ.coldFile()`: on a live file that has not been rebuilt in three days, every
   hidden value prints "the data file has not been rebuilt in N days. run make-data.py, see
   refresh.md" instead of an unexplained question mark.
2. **TV06 printed `NaN` three times**, on every row of one of its three sections.
   `Math.abs(mm < -1440 ? ... + " days" : ...)` built the string first and then called
   `Math.abs` on it. **Fixed**, and the underlying cause fixed too: the same countdown
   ternary had been hand written five times across the loop. There is now one
   `HQ.gapText(ms)` and every page calls it.
3. **TV05 was mostly empty black** at `day` and worse at `evening`. Three short panels
   top-aligned in a full-height flex with no distribution. **Rebuilt** as two full bands and
   six panels, adding a five day shape band and a sixth panel whose content differs by
   daypart. He has said repeatedly that he wants MORE on screen because the TV is very big.
4. **TV03 clipped its own headline.** `BACK` was hard coded to 14 days and pins were placed
   with `translateX(-50%)`, so the oldest item always landed at `left:0` and always had half
   its label off the panel. Three decline labels also collided into each other and buried an
   axis label. **Fixed**: the window now sizes itself to the data with three days of air at
   each end, pins are anchored left, centre or right depending on where they land, and both
   sides run a greedy stacker so no two labels overlap.
5. **NOTES.md did not exist**, and `make-data.py` cited a `SCHEMA.md` that did not exist.
   **Fixed**: this file, plus `SCHEMA.md`, plus `refresh.md`.

### The majors that were agreed with and fixed

- **Three claims on the launcher that the work did not support.** "you wanted declines" (the
  word appears nowhere in BRIEF.md or README.md), "the Toggl style week grid you asked for
  months ago" (BRIEF.md dates that request to 2026-08-08, two days before the loop), and
  "TV06 is a denser mosaic that pushes the Metro idea" (TV06 is a cream editorial page).
  All three rewritten. The Metro one is corrected by BUILDING it as TV12 rather than by
  quietly deleting the sentence.
- **Question marks explained themselves only on hover.** There is no hover on a TV and none
  on a Fire TV remote, so every gap on the target device delivered the question mark and
  withheld the answer. `HQ.field()` now prints the reason in words next to the mark, sized to
  be read, with the tooltip kept as a bonus for a desktop.
- **TV03 printed five exact dollar figures under a header that said NO SOURCE.** The gate had
  been applied to headers and skipped on values. `HQ.amt()` now welds the word **invented**
  to the number itself so the mark travels with the figure. An invented figure is explicitly
  NOT treated as a stale figure: it never claimed to come from the source, so hiding it
  behind a question mark would be the wrong correction, and the right one is the word.
- **The sample invented failures about real named vendors on specific dates.** "Adobe
  Creative Cloud, card expired, 2026-08-09" and "Turo host insurance, insufficient funds"
  are false facts about his money that look exactly like true ones. Every decline and
  subscription row now names a CATEGORY, never a company. The "Claude Pro $20" row, which
  also contradicted a known fact since he is on Claude Max, is gone; the AI plan row now
  carries no amount at all, which is the truth.
- **TV02's hour rules painted on top of the event blocks**, striking a line through titles.
  On a calendar a line through an entry means cancelled, so this was a meaning inversion.
  Root cause was two things, not one: DOM order, and translucent `rgba` block fills that let
  the rules show through anyway. Both fixed. The now line moved under the blocks too, with
  its dot and label lifted into the gutter so it is still visible.
- **TV02's right rail did not distinguish real from invented**, while the grid did. The rail
  is the part a glance reads at ten feet, and its number one item was set largest and gold
  while being sample. Every rail node now carries `HQ knows this` or `a shape only`.
- **TV01's numbered queue started at 02** with no 01 anywhere on screen, and the panel had
  roughly 300px of void with the decorative ghost number sitting behind the text instead of
  in it. The headline is now explicitly item 01, the queue follows it, and the ghost moved to
  the lower right where it collides with nothing.
- **TV01 printed "needs nothing has written this in over three days"**, twice, in the panel
  whose job is plain words. `'needs ' + s.needs` where `s.needs` was already a sentence.
- **TV06 drew an empty checkbox** next to every to do on a screen where nothing is ever
  tapped, and its lower half was blank cream. Boxes gone, replaced with a printed rule and
  the area tag. A seven day agenda band now fills the bottom, and today's appointments fill
  the rest of the today column.
- **Five of six screens were the same component.** A row of name left, status right, hairline
  divider, recoloured six ways. Two answers: TV12 contains no row primitive at all, and TV10
  ships four genuinely different layouts inside one page. Honest current count of distinct
  structures in the folder: the week grid, the money runway, the month grid, the solar arc,
  the Metro wall, the broadsheet column set, and the row list. Seven, up from two.
- **The launcher was a generic card grid with no `?` popovers**, on the one page he opens
  first, while using words like "public repository" and "generator script". Rebuilt: two
  across so the screenshots are big enough to actually judge, a section that states plainly
  what was found wrong and what happened to it, and popovers that open on click as well as
  hover because he opens this on a phone.
- **The thumbnails disagreed with the pages.** All ten recaptured on 2026-08-13 after the
  fixes, downscaled to 960px wide. The CURRENT card now uses `prior-CURRENT.png` instead of
  the typographic fallback, and its caption explains why that screenshot is a device question
  and two buttons rather than a dashboard: the live build asks which device it is on before
  it shows anything.

### The minors that were fixed anyway

- Em dashes removed from every comment in `hq-core.js` and `make-data.py`, and from the two
  new markdown files. The whole folder greps clean for em dashes, en dashes, the banned word
  list, and absolute paths starting with a slash and Users.
- Truncated lists on TV01, TV04 and TV06 now append "and N more", matching every other capped
  list in the build. v5 shipped that convention precisely because he photographed content
  cutting off.
- TV05's daypart preview bar is no longer on the deliverable. It appears only when the
  address carries `?review=1` or `?part=`, and its caption is now legible rather than 9px
  near-background grey. On the night screen it and the sample ribbon were the two brightest
  things on a page whose entire purpose is dimness.

## Where the critic was disagreed with, and why

Three things, stated plainly rather than silently ignored.

1. **"TV05's dawn state is also mostly empty."** Not stated by the critic directly, but it
   follows from the same argument used against `day` and `evening`, and it was left alone
   deliberately. Dawn lasts ninety minutes and exists for the moment he opens his eyes with
   the sunrise ramp running. One thing to do and one number is the correct amount of content
   for that moment. Night was left minimal for the same reason and the critic agreed. Only
   `day` and `evening`, which are working screens, were filled.
2. **"All six pages load Google Fonts, and the Fire TV is the device most likely to be slow
   or offline at 6:29am."** Agreed in principle and only half acted on. TV10, TV11 and TV12
   load no web font at all and use the system stack, and TV11 in particular is the 6am screen
   so it must paint instantly. TV01 to TV06 keep the link. Reason: their type is tuned to
   Plus Jakarta Sans at specific tracking values, the fallback stack is already declared and
   degrades acceptably, and re-tuning six tested layouts to buy a first paint on a screen that
   is not the alarm surface is a worse use of the round than the blockers were. If this
   folder ever becomes the live build, inline the two faces as base64 rather than dropping
   them. **Flagged, not silently dropped.**
3. **The critic implies the sample data should simply be smaller or absent.** Disagreed. A
   screen with no data cannot be judged, and he is being asked to judge nine of them. The
   correct fix is not less sample data, it is sample data that can never be mistaken for
   real: a category instead of a company, the word `invented` welded to every figure, a
   ribbon that never leaves while `mode` is not live, and a generator that can only write
   `mode: live` into a gitignored file. That is what was built.

## What round 2 added beyond the fixes

### The data pipeline is now specified, not just designed

`refresh.md` is a copy-pasteable instruction set for a scheduled Claude session. It names
every source explicitly, says exactly where it lives, what to map it to, and what to do when
it is unavailable. Two findings in it are worth surfacing here because they are not obvious:

- **`hub/money.html` cannot be read by a scheduled session.** It keeps its expense list in
  the browser's `localStorage` under `shq-expenses`, on whichever machine he last typed into.
  There is no file on disk. Either he exports it once to `life/expenses.json` or the money
  source stays honest and unwired. Do not read the HTML and guess.
- **Google Calendar freshness is not iCloud freshness.** The iCloud feed Google subscribes to
  is read only and Apple refreshes it on its own schedule, often 12 to 24 hours, so a fresh
  Google read can still be a day-old truth. `as_of` should reflect the sync, not the fetch.

The standing rule, stated in `refresh.md` and enforced by `hq-core`: a missing value becomes
a question mark that says what it needs. It never becomes a zero, an empty list, or a guess.

### Real numbers can now live on his machine and never reach GitHub

`hq-tv` is a public repository. `make-data.py --live` now writes `data.local.json` and
`data.local.js` instead of the committed pair, both listed in this folder's new `.gitignore`.
Every page loads `data.local.js` first, then `data.js`, and `hq-core.boot()` prefers
`HQ_LOCAL_DATA` over `HQ_DATA` and tries `data.local.json` before `data.json` over http. On a
fresh clone the local script tag 404s harmlessly and the sample takes over. Verified: the
local pair was generated, TV01 loaded it, the refresh line read `from data.local.js`, the
SAMPLE ribbon disappeared, `git check-ignore` confirmed the ignore, `git status` never listed
it, and the test files were then deleted so nothing misleading was left on disk.

### The calendar view toggle he asked for on 2026-08-08, TV10

BRIEF.md has had it under "Still open" since v5. The design problem is that a toggle is a
control and nothing on the TV is ever tapped, so it is a CYCLE: four views take the stage in
turn every 24 seconds, pips show which is up and how much of its turn is left, `?view=` pins
one for a review, and left and right on a Fire TV remote steers it. Four genuinely different
layouts, not four palettes: the Toggl week grid, a real month grid with per-day density, a
single day column at size with a companion panel, and a chronological agenda that merges
events, dated commitments and bills and names the clear gaps between them.

### The thing nobody asked for, TV11

Every other screen in this folder spends surface saying what it still needs, because the
calendar, the bank and the weather are all unconnected. TV11 needs nothing and never will.
It draws the real solar elevation curve for Arlington today from NOAA's standard equations
(fractional year, equation of time, declination, hour angle), the real sunrise, solar noon
and sunset, the real length of the day, how many minutes of light today lost against
yesterday, and the moon's phase. The page background follows the actual height of the sun, so
it is a different screen at 6am, at noon and at 9pm. There is no API, no key, no network call
and nothing that can go stale or be wrong about his money. It is different every single
morning without anyone touching it, which is the thing he complained about, answered from the
opposite direction.

Two honesty notes carried on the page itself: the moon comes from the mean synodic month, and
a real lunation runs from 29.27 to 29.83 days, so the age can sit a few hours either side. It
is printed as a percentage and a name, not as an exact decimal day count. And the alarm and
the first thing today are the only two things on that screen that come from HQ, so they are
the only two that follow the sample rules. Both facts are stated in the footer.

### TV12, the Metro screen the launcher had already promised

Solid colour blocks of three sizes, no borders, white text, deep plum ground, which is the
treatment BRIEF.md records him sending as reference. Tiles with two things to say flip to the
second on a staggered timer, which is what a live tile is for. Nothing on the page is a row.
Five hues at one saturation rather than a rainbow, and every tile has a real gradient and an
inner highlight, because a flat fill with a word on it is the exact look he has rejected
twice as vibe-coded.

## Verification actually performed, 2026-08-13

- Headless Chrome at 1440x900 for all nine pages plus the launcher. Every screenshot was
  READ, not just captured, and several fixes came out of reading them: the TV02 now line was
  still visible through translucent event fills after the z-index fix, TV04's ladder column
  clipped the printed reason on every row, and TV10's day and agenda views were half empty
  before bills and commitments were merged into them.
- A true 390px iframe harness, measured inside the frame, because headless Chrome will not
  open a window under 500px and a naive `--window-size=390` capture crops a 500px layout and
  fakes both overflow and offset. Result across all ten pages:
  `clientWidth 390, scrollWidth 390, overflow false, elements past the right edge 0`.
  One real bug came out of this: the launcher's `?` popover pushed the page 89px wider than
  the screen on a phone, and now becomes a sheet pinned to the viewport instead.
- Scanned every page's rendered text for `NaN`, `undefined` and `[object`. Zero on all nine
  screens. The two hits on the launcher are the word NaN inside the sentence describing the
  bug that was fixed.
- Grepped the whole folder for em dashes, en dashes, the banned word list, and absolute paths
  starting with a slash and Users. All clean.
- The only external subresources anywhere are the Google Fonts links on TV01 to TV06, which
  is a deliberate and flagged decision, see the disagreements above.
- `make-data.py` was re-run and `data.json` and `data.js` were regenerated, so what is on
  disk is what was screenshotted.

## What is still open

- **Samuel has not seen any of this.** Nothing is approved. Nothing is deployed.
- **The bank is the big unconnected one** and it is his decision, not a build task. Until
  then TV03's declines are shapes and say so.
- **Cloudflare Access.** BRIEF.md records it verified on 2026-08-08 and waiting on him. Until
  that happens `data.local.*` is a local-only file and any deployed page is sample only.
  That is correct and should stay correct.
- **`hub/money.html` needs a one time export** before the money source can be real. See
  `refresh.md` section 4.
- **The seven day and five day bands on TV05, TV06 and TV12 are thin** because there is
  almost nothing in the sample calendar. That is data, not layout, and it will fill the
  moment a real calendar is connected. Worth re-reading those three screens after the first
  real run rather than tuning them against sample sparsity now.
- **The loop's own improvement log was not written.** The standing rule is that every session
  logs improvements and dictation slips to `projects/workflow-audit` through its `log.sh`.
  That folder is outside this loop folder and LOOP-BRIEF rule 1 forbids touching anything
  outside it, so the rules conflict. Resolved in favour of the loop contract. **The
  orchestrator should log this round's entries when it writes its own outputs.**
- **`TV07` to `TV09` and `TV13` to `TV16` are reserved and unused.** Do not reuse them, and
  do not assume a gap means a deleted build.
- The registry at `memory/BUILD-CODES.md` still needs rows for TV01 to TV06 and TV10 to TV12.
  That file is outside this folder, so the orchestrator writes them.
