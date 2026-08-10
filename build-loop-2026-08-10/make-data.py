#!/usr/bin/env python3
"""
make-data.py — the whole data layer for the TV01..TV06 dashboards.

Run it:      python3 make-data.py
Live mode:   python3 make-data.py --live
With a TODO: python3 make-data.py --todo ../../../life/TODO.md

It writes two files next to itself, from ONE source of truth:

  data.json   the canonical file. Read by fetch() when the page is served over http.
  data.js     the exact same object as `window.HQ_DATA = {...}`. Read by <script src>
              when the page is opened by double-click, because a browser refuses to
              fetch() a local .json file off file:// and would leave a blank screen.

Nothing is imported that does not ship with Python. No pip, no node, no build step.

WHY THIS FILE EXISTS
Samuel's complaint, 2026-08-09: "It says a bill is late 8 days as a sample... the 8 days
has been already a day and hasn't changed." The old page stored the STRING "8d". This
generator never stores a computed number. It stores the due DATE. The page subtracts.
Tomorrow the screen says 12 days on its own, with nobody touching anything.

THE RIBBON
Every page shows a SAMPLE DATA ribbon while `mode` is "sample". It disappears only when
this file writes `"mode": "live"`, which happens only when you pass --live. Read
SCHEMA.md, section "turning the ribbon off", before you do that on a public repo.
"""

import argparse, json, os, re, sys
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
NOW = datetime.now().astimezone()


def iso(dt):
    return dt.replace(microsecond=0).isoformat()


def ago(**kw):
    return iso(NOW - timedelta(**kw))


def day(offset):
    """A bare YYYY-MM-DD, offset in days from today. Dates, never durations."""
    return (NOW + timedelta(days=offset)).strftime("%Y-%m-%d")


def at(offset_days, hour, minute=0):
    d = (NOW + timedelta(days=offset_days)).replace(
        hour=hour, minute=minute, second=0, microsecond=0)
    return iso(d)


# ── the TODO list, if this machine has the HQ tree next to it ────────────────
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
    # Pass --todos-from-hq when you are generating for a private, gated deployment.
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

    # ── SOURCES ──────────────────────────────────────────────────────────────
    # Each one carries the moment it last told the truth. Everything on screen
    # points at one of these, and inherits its age. Three ages are seeded on
    # purpose so all three freshness states are visible in one screenshot:
    #   money    2 hours old   → fresh, full colour
    #   turo    30 hours old   → stale, drained of colour, wears an age chip
    #   health   5 days old    → too old to show, becomes a question mark
    #   calendar never         → no source at all, says what it needs
    sources = {
        "money": {
            "label": "money",
            "kind": "typed by hand into HQ",
            "as_of": ago(hours=2),
            "needs": None,
        },
        "turo": {
            "label": "turo",
            "kind": "typed by hand into HQ",
            "as_of": ago(hours=30),
            "needs": None,
        },
        "todo": {
            "label": "to do list",
            "kind": "life/TODO.md" if not sampled else "sample, TODO.md not found",
            "as_of": ago(minutes=6) if not sampled else ago(hours=9),
            "needs": None,
        },
        "commitments": {
            "label": "commitments",
            "kind": "life/COMMITMENTS.md",
            "as_of": ago(hours=11),
            "needs": None,
        },
        "projects": {
            "label": "projects",
            "kind": "typed by hand into HQ",
            "as_of": ago(hours=20),
            "needs": None,
        },
        "calendar": {
            "label": "calendar",
            "kind": "not connected",
            "as_of": None,
            "needs": "pick one calendar as the hub, then publish a read only feed to it",
        },
        "bank": {
            "label": "bank and cards",
            "kind": "not connected",
            "as_of": None,
            "needs": "a bank connection, or a weekly export you drop into HQ",
        },
        "health": {
            "label": "sleep and health",
            "kind": "typed by hand into HQ",
            "as_of": ago(days=5),
            "needs": "nothing is writing this. it is old enough that the screen hides it",
        },
        "weather": {
            "label": "weather",
            "kind": "not connected",
            "as_of": None,
            "needs": "one free forecast call for Arlington, once an hour",
        },
    }

    # ── MONEY ────────────────────────────────────────────────────────────────
    # Every amount below is INVENTED so this file can live in a public repo.
    # `sample: true` makes each one say so on screen, on top of the ribbon.
    # Real dates are used where HQ already knows them, because dates are not secret.
    bills = [
        {"id": "cashapp", "name": "Cash App Borrow", "amount": None, "sample": False,
         "due": day(-11), "paid": False, "source": "money",
         "why": "late fees started already. the date that costs real money is the 30 day mark, "
                "when it can reach the credit bureaus",
         "hard_date": day(19), "hard_label": "can reach the credit bureaus"},
        {"id": "rent", "name": "rent", "amount": None, "sample": False,
         "due": day(22), "paid": False, "source": "money",
         "why": "no amount is stored in HQ for this yet"},
        {"id": "phone", "name": "phone bill", "amount": 84.0, "sample": True,
         "due": day(4), "paid": False, "source": "money", "why": ""},
        {"id": "card", "name": "credit card minimum", "amount": 35.0, "sample": True,
         "due": day(9), "paid": False, "source": "money", "why": ""},
        {"id": "insurance", "name": "car insurance", "amount": 162.0, "sample": True,
         "due": day(16), "paid": False, "source": "money", "why": ""},
        {"id": "turorenew", "name": "Turo listing renewal", "amount": None, "sample": False,
         "due": day(14), "paid": False, "source": "turo",
         "why": "from COMMITMENTS, 2026-08-24. no amount stored"},
    ]

    declines = [
        {"name": "Adobe Creative Cloud", "amount": 59.99, "at": ago(days=1, hours=3),
         "reason": "card expired", "sample": True, "source": "bank"},
        {"name": "Turo host insurance", "amount": 47.0, "at": ago(days=3, hours=7),
         "reason": "insufficient funds", "sample": True, "source": "bank"},
        {"name": "iCloud+ 2TB", "amount": 9.99, "at": ago(days=6, hours=2),
         "reason": "retried and went through", "sample": True, "source": "bank",
         "resolved": True},
    ]

    subscriptions = [
        {"name": "Adobe Creative Cloud", "amount": 59.99, "renews": day(21),
         "status": "failing", "sample": True, "source": "bank"},
        {"name": "Claude Pro", "amount": 20.0, "renews": day(6),
         "status": "paid", "sample": True, "source": "bank"},
        {"name": "iCloud+ 2TB", "amount": 9.99, "renews": day(12),
         "status": "paid", "sample": True, "source": "bank"},
        {"name": "domain renewals", "amount": None, "renews": day(48),
         "status": "unknown", "sample": False, "source": "bank"},
        {"name": "Squarespace", "amount": 23.0, "renews": day(2),
         "status": "due", "sample": True, "source": "bank"},
    ]

    money_in = [
        {"name": "Turo booking", "amount": 68.0, "on": day(21), "sample": True,
         "source": "turo", "state": "blocked",
         "why": "the car is unlisted, so nothing can book. this is what a booking would look like"},
        {"name": "Karrina retainer", "amount": None, "on": day(20), "sample": False,
         "source": "money", "state": "expected"},
    ]

    # ── THE WEEK ─────────────────────────────────────────────────────────────
    # No calendar is connected, so every block here is a SHAPE, not an appointment,
    # except the two that HQ genuinely knows from COMMITMENTS.md. Each block says
    # which it is. TV02 will not pretend otherwise.
    monday_offset = -NOW.weekday() - 1 if NOW.weekday() != 6 else 0   # week starts Sunday
    events = [
        {"title": "Turo cancellations webinar", "start": at(monday_offset + 0, 14),
         "end": at(monday_offset + 0, 15, 30), "kind": "money", "source": "commitments",
         "real": True, "why": "COMMITMENTS.md, the car earns $0 until this is done"},
        {"title": "Submit the review removal form", "start": at(monday_offset + 0, 15, 45),
         "end": at(monday_offset + 0, 16, 15), "kind": "money", "source": "commitments",
         "real": True, "why": "one submission only, and it is final. do it after the webinar"},
        {"title": "deep work", "start": at(monday_offset + 1, 9),
         "end": at(monday_offset + 1, 12), "kind": "work", "source": "calendar", "real": False},
        {"title": "client call", "start": at(monday_offset + 1, 14),
         "end": at(monday_offset + 1, 15), "kind": "client", "source": "calendar", "real": False},
        {"title": "class", "start": at(monday_offset + 2, 10),
         "end": at(monday_offset + 2, 12, 30), "kind": "school", "source": "calendar", "real": False},
        {"title": "edit pass", "start": at(monday_offset + 2, 15),
         "end": at(monday_offset + 2, 18), "kind": "work", "source": "calendar", "real": False},
        {"title": "shoot", "start": at(monday_offset + 3, 11),
         "end": at(monday_offset + 3, 16), "kind": "client", "source": "calendar", "real": False},
        {"title": "class", "start": at(monday_offset + 4, 10),
         "end": at(monday_offset + 4, 12, 30), "kind": "school", "source": "calendar", "real": False},
        {"title": "Turo handover window", "start": at(monday_offset + 5, 8),
         "end": at(monday_offset + 5, 10), "kind": "money", "source": "calendar", "real": False},
        {"title": "gym", "start": at(monday_offset + 5, 18),
         "end": at(monday_offset + 5, 19), "kind": "personal", "source": "calendar", "real": False},
        {"title": "reset the week", "start": at(monday_offset + 6, 10),
         "end": at(monday_offset + 6, 11, 30), "kind": "personal", "source": "calendar", "real": False},
    ]

    deadlines = [
        {"name": "Turo cancellations webinar", "on": day(-1), "source": "commitments",
         "why": "the car is unlisted until this is done. every day it is unlisted is $0"},
        {"name": "Cash App Borrow can reach the credit bureaus", "on": day(19),
         "source": "commitments", "why": "30 days past due is the line that matters"},
        {"name": "Turo renewal", "on": day(14), "source": "commitments",
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
         "source": "commitments", "repeat": None},
        {"text": "wind down, screens off", "at": at(0, 22), "source": "todo",
         "repeat": "every night"},
        {"text": "pull the week's numbers into HQ", "at": at(monday_offset + 0, 19),
         "source": "todo", "repeat": "every Sunday"},
    ]

    return {
        "schema": 1,
        "mode": "live" if live else "sample",
        "generated_at": iso(NOW),
        "generator": "make-data.py",
        "sample_note": (
            "Every amount in this file is invented. hq-tv is a public repo, so no real "
            "figure is ever committed to it. Dates that HQ genuinely knows are real, "
            "because a date is not a secret."
        ),
        "todo_note": todo_note,
        "sources": sources,
        "alarm": {"hour": 6, "minute": 30, "sunrise_minutes": 25},
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true",
                    help="write mode=live, which removes the SAMPLE DATA ribbon. "
                         "Read SCHEMA.md first.")
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

    with open(os.path.join(HERE, "data.json"), "w", encoding="utf-8") as f:
        f.write(blob + "\n")

    with open(os.path.join(HERE, "data.js"), "w", encoding="utf-8") as f:
        f.write("/* generated by make-data.py. do not edit by hand, it is overwritten.\n"
                "   this exists so the pages still work when opened by double-click,\n"
                "   where a browser will not fetch a local data.json. */\n")
        f.write("window.HQ_DATA = " + blob + ";\n")

    print("wrote data.json and data.js   mode=%s   generated_at=%s"
          % (data["mode"], data["generated_at"]))
    if data.get("todo_note"):
        print("note: " + data["todo_note"])


if __name__ == "__main__":
    main()
