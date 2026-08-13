#!/usr/bin/env python3
"""
make-data.py, the whole data layer for the TV dashboards in this folder.

Run it:      python3 make-data.py
Live mode:   python3 make-data.py --live --todos-from-hq
With a TODO: python3 make-data.py --todo ../../../life/TODO.md

WHAT IT WRITES

  Sample mode (the default, safe for a public repo):
    data.json        the canonical sample file, read by fetch() over http
    data.js          the same object as window.HQ_DATA, read by <script src>
                     when the page is opened by double-click, because a browser
                     refuses to fetch() a local .json off file://

  Live mode (--live), for real numbers on his own machine only:
    data.local.json  read in preference to data.json by every page
    data.local.js    sets window.HQ_LOCAL_DATA, read in preference to data.js
    Both are in .gitignore. They never reach GitHub. See refresh.md.

Nothing is imported that does not ship with Python. No pip, no node, no build step.

WHY THIS FILE EXISTS
Samuel's complaint, 2026-08-09: "It says a bill is late 8 days as a sample... the 8 days
has been already a day and hasn't changed." The old page stored the STRING "8d". This
generator never stores a computed number. It stores the due DATE. The page subtracts.

ROUND 2 FIX, 2026-08-13. That was only half done. The generator DID store absolute
timestamps for the source ages, so three days after a run every source aged past the
72 hour cutoff and every page filled with question marks. Now every date in this file
ships twice: once absolute, and once as an OFFSET that the page resolves at load.
See the "rel" keys below and the rehydrate() function in hq-core.js. A sample file
built tonight still reads correctly in November.

THE RIBBON
Every page shows a SAMPLE DATA ribbon while `mode` is "sample". It disappears only when
this file writes `"mode": "live"`, which happens only when you pass --live, which also
writes to data.local.* rather than the committed files. Read SCHEMA.md first.
"""

import argparse, json, os, re
from datetime import datetime, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
NOW = datetime.now().astimezone()


def iso(dt):
    return dt.replace(microsecond=0).isoformat()


def ago(**kw):
    return iso(NOW - timedelta(**kw))


def rel_min(**kw):
    """How many minutes before page load a thing happened. Resolved in the browser."""
    return int(timedelta(**kw).total_seconds() // 60)


def day(offset):
    """A bare YYYY-MM-DD, offset in days from today. Dates, never durations."""
    return (NOW + timedelta(days=offset)).strftime("%Y-%m-%d")


def at(offset_days, hour, minute=0):
    d = (NOW + timedelta(days=offset_days)).replace(
        hour=hour, minute=minute, second=0, microsecond=0)
    return iso(d)


# week starts Sunday, the same convention the week grid draws
SUNDAY_OFFSET = -((NOW.weekday() + 1) % 7)


def at_wd(weekday, hour, minute=0):
    """weekday 0 = this week's Sunday, 6 = Saturday."""
    return at(SUNDAY_OFFSET + weekday, hour, minute)


# --- the TODO list, if this machine has the HQ tree next to it ----------------
def read_todos(path):
    """life/TODO.md format: `- [ ] item | when | area`. Optional on purpose:
    hq-tv is a public repo and will often be cloned with no HQ tree above it."""
    out, note = [], None
    if not path or not os.path.exists(path):
        return [], "life/TODO.md was not found next to this repo, so the to do list is sample"
    with open(path, encoding="utf-8") as f:
        for line in f:
            m = re.match(r"^\s*-\s*\[( |x|X)\]\s*(.+)$", line)
            if not m:
                continue
            done = m.group(1).lower() == "x"
            parts = [p.strip() for p in m.group(2).split("|")]
            if done or len(parts) < 2:
                continue
            when = parts[1].lower()
            if when not in ("today", "this week"):
                continue          # only today + this week reach the TV, by his rule
            out.append({
                "text": parts[0],
                "when": when,
                "area": parts[2] if len(parts) > 2 else "",
                "source": "todo",
            })
    if not out:
        note = "life/TODO.md was read but had nothing marked today or this week"
    return out, note


def build(live, todo_path):
    # Default OFF. hq-tv is a public repo, and his real to do list is his business.
    if todo_path:
        todos, todo_note = read_todos(todo_path)
    else:
        todos, todo_note = [], ("the real to do list is not read by default, because this "
                                "repo is public. run with --todos-from-hq to pull it in")
    sampled = not todos
    if sampled:
        todos = [
            {"text": "Book and attend the Turo cancellations webinar", "when": "today",
             "area": "turo", "source": "todo"},
            {"text": "Pay Cash App Borrow plus the late fee", "when": "today",
             "area": "money", "source": "todo"},
            {"text": "Pick one calendar to rule them all", "when": "this week",
             "area": "systems", "source": "todo"},
            {"text": "Install the rise alarm app on the iPhone", "when": "this week",
             "area": "sleep", "source": "todo"},
            {"text": "Decide: move hq-tv off the public URL so it can carry real numbers",
             "when": "this week", "area": "systems", "source": "todo"},
        ]

    # --- SOURCES -------------------------------------------------------------
    # Each one carries the moment it last told the truth, twice: `as_of` for a
    # live file, and `as_of_rel_min` for the sample, which the page resolves at
    # load so the staged ages never rot. Four ages are staged on purpose so all
    # four states are visible in one screenshot:
    #   money    2 hours   fresh, full colour
    #   turo    30 hours   stale, drained of colour, wears an age chip
    #   health   5 days    too old to show, becomes a question mark
    #   calendar never     no source at all, says what it needs
    def src(label, kind, needs=None, **age):
        d = {"label": label, "kind": kind, "needs": needs}
        if age:
            d["as_of"] = ago(**age)
            d["as_of_rel_min"] = rel_min(**age)
        else:
            d["as_of"] = None
            d["as_of_rel_min"] = None
        return d

    sources = {
        "money": src("money", "typed by hand into HQ", hours=2),
        "turo": src("turo", "typed by hand into HQ", hours=30),
        "todo": src("to do list",
                    "life/TODO.md" if not sampled else "sample, TODO.md not found",
                    **({"minutes": 6} if not sampled else {"hours": 9})),
        "commitments": src("commitments", "life/COMMITMENTS.md", hours=11),
        "projects": src("projects", "each project CURRENT.md", hours=20),
        "calendar": src("calendar", "not connected",
                        "pick one calendar as the hub, then publish a read only feed to it"),
        "bank": src("bank and cards", "not connected",
                    "a bank connection, or a weekly export you drop into HQ"),
        "health": src("sleep and health", "typed by hand into HQ",
                      "nothing is writing this. it is old enough that the screen hides it",
                      days=5),
        "weather": src("weather", "not connected",
                       "one free forecast call for Arlington, once an hour"),
    }

    # --- MONEY ---------------------------------------------------------------
    # Every amount below is INVENTED so this file can live in a public repo.
    # `sample: true` makes each one carry a visible "invented" tag on screen, on
    # top of the ribbon. Round 2 change: no invented failure is attached to a real
    # named vendor any more. A row that says a named company's card was refused on
    # a dated Thursday looks exactly like a real one, and it is not real.
    # Real dates are used where HQ already knows them. A date is not a secret.
    bills = [
        {"id": "cashapp", "name": "Cash App Borrow", "amount": None, "sample": False,
         "due": day(-11), "due_rel": {"d": -11}, "paid": False, "source": "money",
         "why": "late fees started already. the date that costs real money is the 30 day mark, "
                "when it can reach the credit bureaus",
         "hard_date": day(19), "hard_date_rel": {"d": 19},
         "hard_label": "can reach the credit bureaus"},
        {"id": "rent", "name": "rent", "amount": None, "sample": False,
         "due": day(22), "due_rel": {"d": 22}, "paid": False, "source": "money",
         "why": "no amount is stored in HQ for this yet"},
        {"id": "phone", "name": "phone bill", "amount": 84.0, "sample": True,
         "due": day(4), "due_rel": {"d": 4}, "paid": False, "source": "money", "why": ""},
        {"id": "card", "name": "credit card minimum", "amount": 35.0, "sample": True,
         "due": day(9), "due_rel": {"d": 9}, "paid": False, "source": "money", "why": ""},
        {"id": "insurance", "name": "car insurance", "amount": 162.0, "sample": True,
         "due": day(16), "due_rel": {"d": 16}, "paid": False, "source": "money", "why": ""},
        {"id": "turorenew", "name": "Turo listing renewal", "amount": None, "sample": False,
         "due": day(14), "due_rel": {"d": 14}, "paid": False, "source": "turo",
         "why": "from COMMITMENTS. no amount stored"},
    ]

    declines = [
        {"name": "a design subscription", "amount": 59.99,
         "at": ago(days=1, hours=3), "at_rel_min": rel_min(days=1, hours=3),
         "reason": "card expired", "sample": True, "source": "bank"},
        {"name": "a car expense on autopay", "amount": 47.0,
         "at": ago(days=3, hours=7), "at_rel_min": rel_min(days=3, hours=7),
         "reason": "not enough in the account", "sample": True, "source": "bank"},
        {"name": "cloud storage", "amount": 9.99,
         "at": ago(days=6, hours=2), "at_rel_min": rel_min(days=6, hours=2),
         "reason": "retried and went through", "sample": True, "source": "bank",
         "resolved": True},
    ]

    subscriptions = [
        {"name": "design software", "amount": 59.99, "renews": day(21),
         "renews_rel": {"d": 21}, "status": "failing", "sample": True, "source": "bank"},
        {"name": "AI plan", "amount": None, "renews": day(6),
         "renews_rel": {"d": 6}, "status": "paid", "sample": False, "source": "bank"},
        {"name": "cloud storage", "amount": 9.99, "renews": day(12),
         "renews_rel": {"d": 12}, "status": "paid", "sample": True, "source": "bank"},
        {"name": "domain renewals", "amount": None, "renews": day(48),
         "renews_rel": {"d": 48}, "status": "unknown", "sample": False, "source": "bank"},
        {"name": "site hosting", "amount": 23.0, "renews": day(2),
         "renews_rel": {"d": 2}, "status": "due", "sample": True, "source": "bank"},
    ]

    money_in = [
        {"name": "Turo booking", "amount": 68.0, "on": day(21), "on_rel": {"d": 21},
         "sample": True, "source": "turo", "state": "blocked",
         "why": "the car is unlisted, so nothing can book. this is what a booking would look like"},
        {"name": "client retainer", "amount": None, "on": day(20), "on_rel": {"d": 20},
         "sample": False, "source": "money", "state": "expected"},
    ]

    # --- THE WEEK ------------------------------------------------------------
    # No calendar is connected, so every block here is a SHAPE, not an appointment,
    # except the two that HQ genuinely knows from COMMITMENTS.md. Each block says
    # which it is, and every page that draws one has to say so too.
    def ev(title, wd, h1, m1, h2, m2, kind, source, real, why=""):
        return {"title": title, "start": at_wd(wd, h1, m1), "end": at_wd(wd, h2, m2),
                "start_rel": {"wd": wd, "h": h1, "m": m1},
                "end_rel": {"wd": wd, "h": h2, "m": m2},
                "kind": kind, "source": source, "real": real, "why": why}

    events = [
        ev("Turo cancellations webinar", 0, 14, 0, 15, 30, "money", "commitments", True,
           "COMMITMENTS.md, the car earns nothing until this is done"),
        ev("Submit the review removal form", 0, 15, 45, 16, 15, "money", "commitments", True,
           "one submission only, and it is final. do it after the webinar"),
        ev("deep work", 1, 9, 0, 12, 0, "work", "calendar", False),
        ev("client call", 1, 14, 0, 15, 0, "client", "calendar", False),
        ev("class", 2, 10, 0, 12, 30, "school", "calendar", False),
        ev("edit pass", 2, 15, 0, 18, 0, "work", "calendar", False),
        ev("shoot", 3, 11, 0, 16, 0, "client", "calendar", False),
        ev("class", 4, 10, 0, 12, 30, "school", "calendar", False),
        ev("Turo handover window", 5, 8, 0, 10, 0, "money", "calendar", False),
        ev("gym", 5, 18, 0, 19, 0, "personal", "calendar", False),
        ev("reset the week", 6, 10, 0, 11, 30, "personal", "calendar", False),
    ]

    deadlines = [
        {"name": "Turo cancellations webinar", "on": day(-1), "on_rel": {"d": -1},
         "source": "commitments",
         "why": "the car is unlisted until this is done. every day it is unlisted earns nothing"},
        {"name": "Cash App Borrow can reach the credit bureaus", "on": day(19),
         "on_rel": {"d": 19},
         "source": "commitments", "why": "30 days past due is the line that matters"},
        {"name": "Turo renewal", "on": day(14), "on_rel": {"d": 14}, "source": "commitments",
         "why": "check the account standing first, it sits close to the missed trip"},
    ]

    projects = [
        {"name": "turo", "status": "unlisted, blocked on the webinar", "tone": "warn",
         "source": "turo"},
        {"name": "karrina", "status": "retainer live", "tone": "live", "source": "projects"},
        {"name": "hq tv", "status": "you are looking at it", "tone": "live", "source": "projects"},
        {"name": "firststop", "status": "design pass, not started", "tone": "idle",
         "source": "projects"},
        {"name": "sonic sound", "status": "government lane, leave behind built", "tone": "idle",
         "source": "projects"},
        {"name": "samuel hq", "status": "the brain, always on", "tone": "live",
         "source": "projects"},
    ]

    whiteboard = [
        "what you actually owe each month",
        "your Turo daily rate",
        "your Turo delivery fee",
        "which calendar is the real one",
        "which subscriptions are still running",
        "whether hq-tv moves behind Cloudflare Access",
    ]

    reminders = [
        {"text": "Turo review removal form is one shot and final", "at": at(0, 9),
         "at_rel": {"d": 0, "h": 9, "m": 0}, "source": "commitments", "repeat": None},
        {"text": "wind down, screens off", "at": at(0, 22),
         "at_rel": {"d": 0, "h": 22, "m": 0}, "source": "todo", "repeat": "every night"},
        {"text": "pull the week's numbers into HQ", "at": at_wd(0, 19),
         "at_rel": {"wd": 0, "h": 19, "m": 0}, "source": "todo", "repeat": "every Sunday"},
    ]

    return {
        "schema": 2,
        "mode": "live" if live else "sample",
        # Sample files re-date themselves in the browser. A live file never does:
        # a real number's age is the whole point and must not be faked.
        "self_dating": not live,
        "generated_at": iso(NOW),
        "generator": "make-data.py",
        "sample_note": (
            "Every amount in this file is invented, and every one of them carries an "
            "invented tag on screen. hq-tv is a public repo, so no real figure is ever "
            "committed to it. Dates that HQ genuinely knows are real, because a date is "
            "not a secret. The staged ages resolve at page load, so this file does not "
            "go stale sitting on disk."
        ),
        "todo_note": todo_note,
        "sources": sources,
        "alarm": {"hour": 6, "minute": 30, "sunrise_minutes": 25},
        "place": {"name": "Arlington", "lat": 38.8816, "lon": -77.0910},
        "weather": {"place": "Arlington", "value": None, "source": "weather"},
        "bills": bills,
        "declines": declines,
        "subscriptions": subscriptions,
        "money_in": money_in,
        "events": events,
        "deadlines": deadlines,
        "todos": todos,
        "reminders": reminders,
        "projects": projects,
        "whiteboard": whiteboard,
    }


HEADER = ("/* generated by make-data.py. do not edit by hand, it is overwritten.\n"
          "   this exists so the pages still work when opened by double-click,\n"
          "   where a browser will not fetch a local .json file. */\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true",
                    help="write real numbers to data.local.json and data.local.js, which are "
                         "gitignored, and drop the SAMPLE DATA ribbon. Read SCHEMA.md first.")
    ap.add_argument("--todos-from-hq", action="store_true",
                    help="read the real life/TODO.md above this repo. OFF by default, "
                         "because hq-tv is a public repo.")
    ap.add_argument("--todo", default=None,
                    help="path to a TODO.md. implies --todos-from-hq.")
    args = ap.parse_args()

    todo_path = args.todo
    if args.todos_from_hq and not todo_path:
        todo_path = os.path.join(HERE, "..", "..", "..", "life", "TODO.md")

    data = build(args.live, todo_path)
    blob = json.dumps(data, indent=2, ensure_ascii=False)

    json_name = "data.local.json" if args.live else "data.json"
    js_name = "data.local.js" if args.live else "data.js"
    var_name = "HQ_LOCAL_DATA" if args.live else "HQ_DATA"

    with open(os.path.join(HERE, json_name), "w", encoding="utf-8") as f:
        f.write(blob + "\n")

    with open(os.path.join(HERE, js_name), "w", encoding="utf-8") as f:
        f.write(HEADER)
        f.write("window." + var_name + " = " + blob + ";\n")

    print("wrote %s and %s   mode=%s   generated_at=%s"
          % (json_name, js_name, data["mode"], data["generated_at"]))
    if args.live:
        print("these two files are gitignored and must never be committed.")
    if data.get("todo_note"):
        print("note: " + data["todo_note"])


if __name__ == "__main__":
    main()
