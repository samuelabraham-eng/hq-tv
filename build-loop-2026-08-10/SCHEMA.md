# SCHEMA.md, the data contract for every page in this folder

> `make-data.py` referenced this file in round 1 and it did not exist, so its instruction
> "Read SCHEMA.md, section turning the ribbon off" pointed at nothing. It exists now.
> Companion to `refresh.md`, which is the how. This is the what.

Schema version: **2**. Round 1 shipped version 1 and had no relative fields.

## The two files, and the two shadow files

| file | committed | contains | read by |
|---|---|---|---|
| `data.json` | yes | the sample | `fetch()` over http |
| `data.js` | yes | the same object as `window.HQ_DATA` | `<script src>` on `file://` |
| `data.local.json` | **NO, gitignored** | his real numbers | `fetch()`, preferred |
| `data.local.js` | **NO, gitignored** | `window.HQ_LOCAL_DATA` | `<script src>`, preferred |

Every page loads, in this order:

```html
<script src="data.local.js"></script>   <!-- absent on a fresh clone. 404s harmlessly. -->
<script src="data.js"></script>
<script src="hq-core.js"></script>
```

`hq-core.boot()` takes `HQ_LOCAL_DATA` if it exists, otherwise `HQ_DATA`, then tries
`data.local.json` and finally `data.json` over http. So the same file works by
double-click and on a server, and real numbers never need to be committed to see them.

## Freshness, which is the only rule that matters

Every value on every screen points at a key in `sources`. It inherits that source's age.

| age of `as_of` | what the screen does |
|---|---|
| under 24 hours | normal. full colour. |
| 24 to 72 hours | drained of colour, wears a chip like `30h old` |
| over 72 hours | the value is HIDDEN and replaced by `?` plus what it needs |
| `as_of: null` | `?` plus what it needs |

`needs` is required whenever `as_of` is null. It is printed on screen next to the question
mark **in plain text at a readable size**, not in a hover tooltip. There is no hover on a
TV and none on a Fire TV remote, so a tooltip delivers the question mark and withholds the
answer. Round 1 made exactly that mistake.

## Self dating, and why only the sample gets it

```jsonc
"self_dating": true    // sample files only
```

A sample file also ships every date twice: once resolved, and once as an offset.

| field | its offset twin | meaning |
|---|---|---|
| `sources.<k>.as_of` | `as_of_rel_min` | minutes before page load |
| `bills[].due` | `due_rel` | `{"d": -11}` days from today |
| `bills[].hard_date` | `hard_date_rel` | `{"d": 19}` |
| `declines[].at` | `at_rel_min` | minutes before page load |
| `subscriptions[].renews` | `renews_rel` | `{"d": 21}` |
| `money_in[].on` | `on_rel` | `{"d": 21}` |
| `events[].start` / `.end` | `start_rel` / `end_rel` | `{"wd": 0, "h": 14, "m": 0}`, weekday of the CURRENT week, Sunday is 0 |
| `deadlines[].on` | `on_rel` | `{"d": -1}` |
| `reminders[].at` | `at_rel` | `{"d": 0, "h": 9, "m": 0}` |

`hq-core.rehydrate()` resolves them at page load. **Why this exists:** round 1's sample
stored only absolute timestamps, so three days after it was generated every source had aged
past the 72 hour cutoff and all six screens rendered as walls of question marks. The pages
whose stated thesis is "nothing here is a stored string" were broken by the only strings
that were stored.

Two different beats, on purpose:

- **Source ages re-resolve on every render**, every 20 seconds. A TV that has been on for a
  week keeps demonstrating all four freshness states instead of decaying to nothing.
- **Content dates resolve once, at load.** So a bill genuinely counts up while the screen is
  running: leave the page open overnight and 11 days late becomes 12 days late by itself,
  which is precisely the behaviour he said was missing.

**`self_dating` must be `false` on a live file, and `make-data.py --live` forces it.**
Staging the age of a real number is a lie, and a worse one than any of the ones being fixed.

## Turning the ribbon off

The SAMPLE DATA ribbon is drawn by `hq-core.ribbon()` whenever `mode` is not `"live"`.
It is a guard rail, not decoration. It disappears only when the loaded file says
`"mode": "live"`, which only `make-data.py --live` writes, and which only writes to the
gitignored `data.local.*` pair.

**Do not hand edit `mode` in `data.json`.** That file is committed to a public repository.
A `mode: live` in it would remove the ribbon from a page full of invented figures, which is
the single worst outcome available in this folder.

## Marking a value as invented

Two independent marks, and both are needed:

1. `"sample": true` on the item. `HQ.amt()` welds the word **invented** to the number
   itself, so the mark travels with the figure instead of sitting in a header three inches
   away. Round 1 put `NO SOURCE` in a header and then printed five exact dollar amounts at
   full confidence underneath it.
2. `"real": false` on an event. The week grid hatches it, the agenda italicises it, and the
   rail tags it `a shape only`.

An invented figure is not a stale figure. It never claimed to come from the source, so the
freshness gate does not apply to it. What it needs is the word, not a question mark.

## The full object

```jsonc
{
  "schema": 2,
  "mode": "sample" | "live",
  "self_dating": true,          // sample only
  "generated_at": "ISO with offset",
  "generator": "make-data.py",
  "sample_note": "...",         // printed nowhere, read by the next agent
  "todo_note": "..." | null,    // why the to do list is sample, if it is

  "sources": { "<key>": { "label", "kind", "as_of", "as_of_rel_min", "needs" } },
  // keys in use: money turo todo commitments projects calendar bank health weather

  "place":  { "name", "lat", "lon" },       // TV11 computes the sun from these
  "alarm":  { "hour", "minute", "sunrise_minutes" },
  "weather":{ "place", "value", "source" },

  "bills":        [ { "id","name","amount","sample","due","due_rel","paid","source",
                      "why","hard_date","hard_date_rel","hard_label" } ],
  "declines":     [ { "name","amount","at","at_rel_min","reason","sample","source",
                      "resolved" } ],
  "subscriptions":[ { "name","amount","renews","renews_rel","status","sample","source" } ],
  "money_in":     [ { "name","amount","on","on_rel","sample","source","state","why" } ],
  "events":       [ { "title","start","end","start_rel","end_rel","kind","source",
                      "real","why" } ],
  "deadlines":    [ { "name","on","on_rel","source","why" } ],
  "todos":        [ { "text","when","area","source" } ],
  "reminders":    [ { "text","at","at_rel","repeat","source" } ],
  "projects":     [ { "name","status","tone","source" } ],
  "whiteboard":   [ "string" ]
}
```

`amount: null` is correct and expected. It means HQ holds the date but not the figure, which
is true of rent and of Cash App Borrow. It renders as `?` plus its `why`.
`amount: 0` is a claim and is almost always wrong.

`status` on a subscription is one of `paid`, `due`, `failing`, `unknown`.
`tone` on a project is one of `live`, `warn`, `idle`.
`kind` on an event is one of `money`, `client`, `school`, `work`, `personal`.
`when` on a to do is `today` or `this week`. Nothing else reaches a screen.

## Helpers every page uses, so nobody writes the ternary twice

In `hq-core.js`:

- `HQ.dueText(date)` gives `11 days late`, `today`, `tomorrow`, `in 4 days`.
- `HQ.gapText(ms)` gives `in 17h 4m`, `5h 52m ago`, `in 2 days`. Round 1 hand wrote this
  ternary five times and one copy called `Math.abs` on a string, which printed `NaN` on
  every row of a section of TV06. Use the helper.
- `HQ.field(sourceKey, value, {needs})` renders the three states.
- `HQ.amt(value, sample, sourceKey, needs)` renders a figure with its invented tag.
- `HQ.fresh(key)` gives `{state, age, needs, left}`.
- `HQ.mark(el, key)` puts `hq-s-fresh|stale|unknown` on a container so CSS can drain it.
- `HQ.coldFile()` gives the sentence to print when the whole file has gone cold.
