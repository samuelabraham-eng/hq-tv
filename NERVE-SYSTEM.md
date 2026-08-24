# The nerve system — what the TV is actually for

> Captured verbatim-intent from Samuel's 2026-08-13 voice message. This is the biggest
> architectural idea he has described for hq-tv and it is NOT yet built. Everything here is
> his design; my job is to build it and to think ahead of it.
>
> His framing: *"this is the type of stuff... I really want you to really listen to what I'm
> saying, log everything I'm saying, push it to GitHub so it's on all devices."*

---

## The thesis

The TV is not a dashboard. It is the **status board for a distributed system that he owns**,
and the thing it must answer at a glance is: **is my system actually working right now, and is
there anything I have to do before I leave the house?**

A dashboard shows data. This shows **whether the machinery that produces the data is alive.**
That distinction is the whole idea and it is the part I had not understood before.

---

## The concrete example he gave (build to this, not to an abstraction)

- His school portal (**NovaSIS**) makes him re-authenticate roughly **every 8 hours**.
- A scheduled job on the **always-on home MacBook** pre-pulls from it so Claude can read it later.
- If that session is dead, the pull fails, and **he only finds out when he needs the data and is
  not home** — at which point he cannot log in and it is too late.
- So the TV must show: **NovaSIS — authenticated, last pulled 40 minutes ago.** Or:
  **NovaSIS — session expired, log in before you leave.**
- Same for **Canvas**, email, calendar, and every other source.
- His words: *"if it says not pulled, or if it says not live, now I know I need to log in before I
  leave the house... if it says it hasn't been pulled in like 10 hours, that's obviously an issue."*

**The point is pre-emption.** The screen exists to make him act *while acting is still possible*.

---

## Three states that must be distinguishable, and are usually conflated

1. **The job ran.** A scheduled task fired.
2. **The data is fresh.** The pull actually succeeded and returned something recent.
3. **The credential is still valid.** The session has not expired.

All three can disagree. A job can run every 30 minutes and produce nothing because the session
died. Showing only "last run" would be a lie of exactly the kind he has told me never to put on
screen. **Show freshness as an age, and show credential expiry BEFORE it expires.**

---

## The home MacBook is the hub

- It is **always on**. The M5 is not the hub; the home MacBook is.
- It holds the **iMessage account of his work phone**, so it can text his personal phone. That is
  the existing notification path (`~/imessage-bridge`).
- It should **pre-pull everything on a schedule** (~every 30 minutes) so that data is warm before
  anyone asks for it.
- It publishes a curated payload that the TV reads. **The TV never pulls from sources directly.**
- ~~Future:~~ **CONFIRMED THE PLAN, 2026-08-24.** His words: *"this has to run on the home
  macbook running hdmi to the fire TV since this is always going to be on."* Stop designing for
  Silk. The dashboard (and the Monday voice overlay, see `idea-lab/research/08` v2 section)
  runs ON the home MacBook, output over **HDMI as an always-on second display**. This removes
  every Fire TV constraint (the 20-minute sleep, Silk quirks, kiosk apps) and makes the machine
  showing the screen the same machine holding the data — and the same machine listening.

---

## What belongs on the screen, from his own examples

He was explicit that he is giving **ideas, not specs**, and expects me to extrapolate:

- **Subscriptions ending or renewing soon** — so nothing auto-renews by surprise.
- **Bills coming up, past due items, renewals.**
- **Return windows.** His example: the **M5 MacBook**, which he wants to return before the window
  closes. He never told me this before; he mentioned it in passing and expects it to now be
  tracked. It is, in `life/COMMITMENTS.md`, with the deadline derived from disk evidence.
- Anything with a **date and a consequence** that email knows about and he does not.

**The standing rule this creates:** a passing mention is an instruction. Emails are a data source
for deadlines he has forgotten, and the home MacBook pre-pulling them is what makes that possible.

---

## Status tile spec (first draft, to refine against the research)

Each row: **source · state · age · the action if any.**

| state | meaning | what it says |
|---|---|---|
| live | authenticated, pulled recently | `NovaSIS · live · 12m ago` |
| stale | authenticated but the data is old | `Canvas · stale · 6h ago` |
| expiring | credential dies soon | `NovaSIS · log in before you leave · expires 2h` |
| dead | expired or failing | `NovaSIS · session expired · log in` |

Colour follows meaning, never decoration. **The action is the headline, not the state** — he needs
to know what to *do*, not what is *true*. Anything that cannot be acted on gets no colour.

---

## Not built yet

Everything on this page. What exists today is the dashboard shell with **sample** data, which he
called out directly: *"it still says sample, it's not showing live information, which is not good,
which means you're not pushing information to it."*

**The blocking dependency is the home MacBook publishing a payload.** That is a separate build on a
different machine, and it is the single thing that turns this from a mockup into his nerve system.
