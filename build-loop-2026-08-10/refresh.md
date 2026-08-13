# refresh.md, how a scheduled Claude session regenerates the real numbers

> Written for an AGENT, not for Samuel. He never runs any of this.
> This file is the difference between a demo and a dashboard. Round 1 built a
> generator that produced a well designed fixture. This is the instruction set
> that makes the fixture unnecessary.

## The one rule that outranks everything here

**hq-tv is a PUBLIC GitHub repository.** `samuelabraham-eng/hq-tv`, and the pages are
served from it. Nothing you write from a real source goes into `data.json` or `data.js`.
Real numbers go only into `data.local.json` and `data.local.js`, which are listed in this
folder's `.gitignore` and must never be committed. Every page in this folder prefers those
two files and silently falls back to the committed sample when they are absent, so a fresh
clone on any other machine shows the sample and nothing of his.

Check before you finish, every time:

```
cd <this folder>
git status --porcelain | grep data.local    # must print NOTHING
git check-ignore -v data.local.json         # must print the .gitignore line
```

If `git status` ever shows `data.local.json` as untracked-but-listed, the .gitignore was
lost. Stop and restore it before committing anything.

## What to run

From this folder, on the machine that has the `Samuel-HQ` tree above it:

```
python3 make-data.py --live --todos-from-hq
```

That writes `data.local.json` and `data.local.js`, sets `"mode": "live"` which removes the
SAMPLE DATA ribbon, and sets `"self_dating": false` so no age is ever staged. On a live
file every age is the real age of the real source. That is the entire point.

But `make-data.py` alone only knows the to do list. Everything below has to be gathered by
the session and handed to it, or written into the JSON directly. Until a section here is
wired, leave its source `as_of: null` with its `needs` sentence filled in, and the screens
will draw a question mark that says what it needs. **A missing value becomes a question
mark. It never becomes a zero, an empty list, or a guess.** That rule is the whole reason
Samuel trusts these screens at all.

## The sources, one at a time

### 1. `todo`, his to do list

- **Where:** `~/Samuel-HQ/life/TODO.md`, read directly off disk.
- **Format:** `- [ ] item | when | area`. `when` is `today`, `this week` or `later`.
- **Rule:** only `today` and `this week` reach a screen. `later` stays in HQ. His words,
  2026-08-08, recorded in BRIEF.md: the screen must never become a wall he stops reading.
- **Already wired.** `make-data.py --todos-from-hq` does this with no help.
- `as_of` is the file's own modification time. Do not invent a fresher one.

### 2. `commitments`, dated things that cost money if missed

- **Where:** `~/Samuel-HQ/life/COMMITMENTS.md`.
- **Format:** `dates | commitment | area | watch for`.
- **Map to:** the `deadlines` array. `name` from the commitment, `on` from the date,
  `why` from the "watch for" column, which is the sentence the screens print underneath.
- If a row says "ASAP" rather than a date, do NOT invent one. Either leave the deadline out
  or set `on: null`, which renders as a question mark.
- `as_of` is the file's modification time.

### 3. `calendar`, the schedule

- **Where:** Google Calendar, through the Google Calendar connector in the session.
  BRIEF.md, 2026-08-08: Google Calendar is the hub because it is the only one Claude can
  connect to. Both iCloud accounts publish a feed that Google subscribes to.
- **Call:** list events from midnight of the current week's Sunday to 21 days ahead.
- **Map to:** the `events` array. `title`, `start`, `end` as local ISO strings with the
  offset, `kind` from the calendar or the title (`money`, `client`, `school`, `work`,
  `personal`), `source: "calendar"`, and **`real: true`**.
- **`real` is load bearing.** `true` means HQ actually knows this event. `false` means it is
  a drawn shape. TV02, TV06, TV10 and TV12 all draw a shape differently from a fact, and
  TV02 hatches it. Never mark a fabricated block `real: true`.
- **Honest limit to keep saying out loud:** the iCloud feed Google subscribes to is read
  only and Apple refreshes it on its own schedule, often 12 to 24 hours. So a fresh Google
  read can still be a day-old iCloud truth. If only the iCloud side is available, set
  `as_of` to Google's last sync time, not to now.
- If the connector is unavailable: leave `events: []`, set
  `sources.calendar.as_of: null` and keep the existing `needs` sentence. Every page already
  handles an empty calendar and says so on screen.

### 4. `money`, bills, and what he must cover

- **Where, primary:** `~/Samuel-HQ/hub/money.html`.
- **Read this carefully before trusting it.** That page keeps its expense list in the
  browser's `localStorage` under the key `shq-expenses`, on whichever machine he last typed
  into. **There is no file on disk to read.** A scheduled session cannot see it. So either:
  1. ask him once to export it (the page can print the JSON to the console with
     `localStorage.getItem('shq-expenses')`) and drop that into
     `~/Samuel-HQ/life/expenses.json`, then read that file here; or
  2. leave `money` with an honest `needs` string until it exists.
  Do not read the HTML and guess. Do not assume the sample amounts in this repo are his.
- **Map to:** the `bills` array. `name`, `due` (a date, never a duration), `amount`,
  `paid`, `source: "money"`, `sample: false`.
- Amounts that HQ genuinely does not hold stay `amount: null`. The screens print `?` plus
  the sentence in `why`. Rent and Cash App Borrow are both `null` in the sample for exactly
  this reason: HQ has the DATES, which are real, and does not have the FIGURES.
- `hard_date` and `hard_label` are the second, worse deadline behind a bill. Cash App Borrow
  uses them for the 30 day mark. Only set them when a real one exists.

### 5. `bank`, declines and subscription status

- **Not connected, and it is the one that would change the most.** BRIEF.md, v2 review:
  bank accounts are a later connection.
- **Interim source:** Gmail, through the Gmail connector.
  - Declines: search `from:(no-reply OR noreply) subject:(declined OR "payment failed" OR
    "could not process" OR "card was declined") newer_than:14d`.
  - Renewals: search `subject:(receipt OR invoice OR "your subscription") newer_than:35d`.
  - Read the message, take the vendor, the amount and the date from the message body.
    **Never infer an amount from the subject line alone.**
- **Map to:** `declines` and `subscriptions`. Every entry from a real email is
  `sample: false` and carries `source: "bank"`.
- **The hard rule here, learned the expensive way.** Round 1's sample invented that a real
  named vendor's card was refused for insufficient funds on a specific date. That is a false
  fact about his money that looks exactly like a true one. If you cannot read a real email
  saying it, do not write it. Leave the array empty. The empty state on TV03 already says
  "Nothing has declined that HQ can see. That is not the same as nothing declining."
- `as_of` is the timestamp of the newest message you actually read, not the time you ran.

### 6. `projects`, what each build is doing

- **Where:** `~/Samuel-HQ/projects/<name>/CURRENT.md` for each project he cares about.
  Every one is machine generated on autosave and carries a `Stamped` row.
- **Map to:** the `projects` array. `name`, `status` in his own plain words, `tone` one of
  `live`, `warn`, `idle`.
- **Never a bare count.** BRIEF.md, v2: projects show name plus status, never a number.
- `as_of` is the OLDEST `Stamped` value across the projects you read, not the newest. The
  panel is only as fresh as its stalest row.

### 7. `weather`, one line for Arlington

- Not connected. One free forecast call, once an hour, for 38.8816, -77.0910.
- Until then leave `weather.value: null` and `sources.weather.as_of: null`. Every page
  prints `Arlington ?` followed by the sentence saying what it needs.
- **Note:** TV11 needs no weather source and never will. Sunrise, sunset, day length and
  the moon are computed from the date and those two coordinates in the browser.

### 8. `turo` and `health`

- `turo`: typed into HQ by hand today. There is no API in play. `as_of` is the moment he
  last said something about the car, not the moment the script ran.
- `health`: nothing is writing it. Leave it old on purpose. It is the sample's demonstration
  of a source that has aged out, and on a live file it should simply carry its real, old
  timestamp and be hidden by the 72 hour rule.

## The schema

`schema: 2`. Full field list and the freshness contract live in `SCHEMA.md` next to this
file. The short version:

```jsonc
{
  "schema": 2,
  "mode": "live",             // "sample" keeps the ribbon. "live" removes it.
  "self_dating": false,       // NEVER true on a live file. staging a real age is a lie.
  "generated_at": "2026-08-13T06:00:00-04:00",
  "sources": {
    "<key>": {
      "label": "money",                    // what a person calls it
      "kind": "life/COMMITMENTS.md",       // where it came from, in plain words
      "as_of": "2026-08-13T05:58:00-04:00",// when it last told the truth. null = never.
      "needs": null                        // the sentence a question mark prints. required
                                           // whenever as_of is null.
    }
  },
  "place":  { "name": "Arlington", "lat": 38.8816, "lon": -77.0910 },
  "alarm":  { "hour": 6, "minute": 30, "sunrise_minutes": 25 },
  "bills":  [{ "id","name","amount","due","paid","source","sample","why",
               "hard_date","hard_label" }],
  "declines":[{ "name","amount","at","reason","source","sample","resolved" }],
  "subscriptions":[{ "name","amount","renews","status","source","sample" }],
  "money_in":[{ "name","amount","on","state","source","sample","why" }],
  "events": [{ "title","start","end","kind","source","real","why" }],
  "deadlines":[{ "name","on","source","why" }],
  "todos":  [{ "text","when","area","source" }],
  "reminders":[{ "text","at","repeat","source" }],
  "projects":[{ "name","status","tone","source" }],
  "whiteboard":[ "an open question, in his words" ]
}
```

Every dated field is a DATE or a TIMESTAMP. Never a duration, never a count of days, never
the string "8 days late". The pages subtract at render. This is the entire fix for the thing
he complained about on 2026-08-09.

## When a source is unavailable

In order of preference:

1. **Keep the last good values and their real `as_of`.** The pages drain the colour out of
   anything over 24 hours old and hide anything over 72 hours behind a question mark. That
   already IS the graceful degradation. Do not refresh a timestamp you did not refresh the
   data behind.
2. **If there are no last good values,** write the array empty, set `as_of: null`, and write
   a `needs` sentence in plain words that says what would fix it. It gets printed on screen
   next to the question mark, at a readable size, because a TV has no hover.
3. **Never write a zero.** `$0` and `0 items` are claims. A question mark is not.
4. **Never write a guess, an estimate, a rounded number, or a figure from a previous run
   presented as current.**

## After the run

- Confirm `data.local.json` is gitignored and `git status` is clean of it.
- Open one page and read the refresh line. On a live file it counts up in real seconds and
  names the file it loaded from. If it says `from data.js` the local file did not load.
- If nothing has rebuilt the file in three days, every page prints
  "the data file has not been rebuilt in N days. run make-data.py, see refresh.md" in place
  of each hidden value, so the failure names itself instead of showing nine blank question
  marks with no cause. That behaviour is in `hq-core.js`, `coldFile()`.

## What is still not solved

- The bank is the big one, and it is his decision, not a build task.
- Cloudflare Access is the gate that lets real numbers be served at all rather than only
  living on one machine. BRIEF.md records it verified on 2026-08-08 and waiting on him.
  Until that happens, `data.local.*` is a local-only file and the deployed page is sample
  only. That is correct and should stay correct.
