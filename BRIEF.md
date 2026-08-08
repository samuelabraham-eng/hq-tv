# BRIEF — hq-tv

The Samuel HQ dashboard on his TV, iPad, phone and monitors. Graduated out of `ipad-deck`
on 2026-08-08 when v1 code existed. History and the Fire TV constraints live in
`ipad-deck/BRIEF.md` under "The TV surface" and are not repeated here.

Live preview: https://samuelabraham-eng.github.io/hq-tv/ (public repo, sample data, noindex)

## His answers, 2026-08-08

| Q | His answer | Consequence |
|---|---|---|
| Who sees the screen | Only him, house people fine. "My space, don't worry about that." | Real numbers are allowed ON SCREEN. **Does not mean a public URL is fine** — see hosting below. |
| The six tiles | "Six is pretty good, if you can add more I'll be good. It's TV, there's a lot of space, but still you want to be able to see everything." | Density is welcome, glanceability is the ceiling. |
| Alarm noise from the TV | **Yes.** Plus his idea: a Hatch-style sunrise. | Built in v1: 25-minute sunrise ramp + ramped tone. |
| TV off overnight | **No, stays on.** | The TV alarm is viable, not decoration. Fire TV sleep fix becomes mandatory. |
| Wake-up mission | "Brainstorm it, visualize it, but don't add it yet. Maybe a mock." | Do NOT ship missions. Mock only. |
| Calendar | No single calendar today. iPhone calendar, plus Google, Notion, two Apple accounts. Wants ONE. | Research done below. Blocked on his pick. |
| Weather | Yes, "something tiny." Arlington. | Small, one line. Not a tile. |
| TV only | **No.** Wants iPad and phone too. | v1 is responsive already. |
| Q9 live tiles | "I don't know about nine, let me know." | Explained to him in chat; recommendation is calm-with-one-mover. |
| Q10 kiosk app | "Let me know more about number 10." | Explained in chat. ~$10 one-time, optional, phase 4. |

## Standing correction he issued (IMPORTANT, applies beyond this project)

The draft showed "$500 owed, Hanok" which was **already settled**. His words:
*"if that's the case, you should put a question mark or something. You could ask me that...
stuff should be closed, so it's not just in the air. It's my fault, I should update you,
but you should be asking me. You can even ask me whenever I try to work on something...
'hey, what happened with hey nook?' I'll tell you."*

**Two binding behaviours from this:**
1. **Never display an unverified number.** Blank plus a question mark beats a stale figure.
   Implemented as the `?` popovers and the "needs your word" strip in v1.
2. **Proactively ask him to close open loops**, even mid-unrelated-work. He has explicitly
   invited the interruption. Open loops belong on screen, not only in a file.

Hanok context he gave: the $500 is settled. He avoided that client because it was a bad job
they delivered and he felt ashamed, then came back and made the video nicer.

## Still open, his asks not yet built

- **iPad as the remote.** His idea: control the TV screen from the iPad, either by swiping on
  the iPad to drive the TV, or by running the same page on both and keeping them in sync.
  Not designed yet. Cheapest real path is a tiny shared-state channel; needs a decision on
  whether that state can live anywhere public.
- **Wake-up missions.** Mock only, per his instruction.
- **Weather.** Needs a source; keep it one small line for Arlington.
- **Smart home lane.** Govee lights (already in the ipad-deck brief as a wish), an Amazon Alexa
  he owns, and a HomePod Mini he is considering at $129.

## Research done 2026-08-08

**Sunrise alarms are real, not a gimmick.** Dawn simulation measurably reduces sleep inertia,
and studies show higher morning cortisol plus a reduced stress response on waking (lower heart
rate, better HRV). Separately, morning bright light therapy has been shown to advance delayed
circadian phase AND improve ADHD symptoms in pilot work — directly relevant to him. Caveat to
keep honest: long-term persistence of the benefit is weakly evidenced. **His TV is a very large
light source that is already on, so the sunrise costs $0 rather than the $130-200 a Hatch
costs.** v1 implements it.

**Calendar unification.** Three real options, all of which handle multiple Apple accounts plus
Google: **Notion Calendar** (free, connects Google + Outlook + iCloud, and he already lives in
Notion), **Morgen** (strongest cross-platform, paid tiers), **CalUnity** (free, four providers).
Recommendation to put to him: Notion Calendar, because it is free, he already uses Notion, and
it reads iCloud. Not yet his decision.

**Govee / Alexa / HomePod.** Govee has shipped Matter support since 2024, so newer devices talk
to Apple Home, Alexa, Google and SmartThings from one firmware. Older Govee gear needs a bridge
(Homebridge or Home Assistant) to reach HomeKit. There is also a documented **local API** for
Govee lights, which is the interesting one here: it means a script on his network can drive the
lights with no cloud round trip. **Verdict to give him: do not buy the HomePod Mini for this.**
The lights are the thing that matters, the bridge can be software, and a HomePod only earns its
$129 if he specifically wants Siri and Apple Shortcuts as the trigger surface. Buy Matter-capable
Govee, then decide.

## Do not repeat

- No em dashes anywhere in his surfaces.
- Do not point this page at the private brain. Only curated fields leave HQ.
- Do not ship anything he said to mock.

## v2 review, 2026-08-08 (his second pass on the live page)

**He loves the design and froze it.** *"I love this design. Say this design is the original
design, and don't change this up at all... other than the actual comments of this stuff inside."*
**noir is LOCKED.** Change content inside it freely, never its look. ink / cream / frame were
added as separate themes so noir never has to be touched to explore.

**Answers this round:**
- Q9 flip tiles: he took the recommendation. Nothing rotates. Only "do this next" animates, and
  only when it changes. He raised the objection himself: *"what if I look away and there's one
  thing?"* Do not revisit rotation without a reason.
- Q10: he did not understand the $10. It was a Fire TV kiosk app, never the website. **Dropped**
  until something actually breaks. His instruction: *"if it costs money or is complicated for
  now, we can just deploy to a site."*
- Content: owed-to-you OUT, replaced by what he must cover by the 1st with the subscription share.
  Projects show name + status, never a bare count. Subscriptions matter to him ("make sure they're
  all paid on time and I'm making enough"). Bank accounts are a later connection.
- "Needs your word" renamed **the whiteboard**, and made read only. *"realistically on a TV, I'm
  not tapping anything. I'm just looking at it."* **Nothing on the TV should require a tap.**
- He likes ring visualisations (Oura, Apple Watch, Apple Health). Month + week rings shipped, both
  real with no data source. Money ring stays dim until connected.
- He wants MORE on screen. The TV is very big and he offered to photograph it for scale.

**Hatch verdict delivered:** Restore 3 is $169.99 plus $50/yr for the full sound library. TV wins
on light and dashboard; Hatch wins on being a small bedside lamp and its sound machine. Told him
not to buy yet, run the TV sunrise two weeks first.

**Research tooling:** he has Gemini AI Pro for a year and asked what is best. Told him honestly:
Gemini Deep Research beats me on wide multi-source sweeps, I win when research must become a file
or a build, Codex is the wrong tool for it. **No automatic bridge — he pastes Gemini output to me
and I file it.** Building an integration would cost more than the paste.

**Standing instruction, reinforced hard this round:** *"everything you said after the
visualization, that's not reading because I want you to visualize it."* **He does not read prose
after a visual.** Substance goes IN the widget. Chat text stays to a few lines at most.

**Still queued:** a photo of the TV for scale, iPad-as-remote design, wake-up mission (mock only,
mocked once already), weather line, and possibly prompts for Codex and Claude Design so he can
compare their takes on the same screen.

## v4 review, 2026-08-08 (Windows 8 reference, security, calendar)

**Themes now:** noir (LOCKED), clay, espresso, oat, sage, cream, **metro**, **metrowarm**.
`ink` and `frame` are DELETED at his instruction. He sent the actual Windows 8 Start screen as
reference, so metro is a genuine Metro treatment: solid colour blocks, no borders, white text,
deep plum ground. metrowarm is the same structure in his palette. Tiles carry `data-c="1..8"`
colour slots that only the metro themes read.

**To-do tile shipped.** His words: *"Sometimes I'd be saying 'add to my to-do list' or just
'high priority things.' Having it there would be a genuine lifesaver."* Source of truth is the
new `life/TODO.md`. Only `today` and `this week` items reach the TV.

**Lock screen shipped, with the honest caveat in the code.** Per-device PIN, 5 to 6 digits, set
on first use, stored ONLY as a hash in localStorage, never in the repo. Clock stays visible and
the alarm still fires while locked. **It is a privacy curtain, not security** — on a public page
the data reaches the visitor before the PIN is asked. Told him plainly.

**THE REAL GATE, and it is his next decision: Cloudflare Access.** Free to 50 users, no card,
one-time PIN to email, session configurable up to one month, blocks at the edge so a stranger
with the URL gets nothing. Verified 2026-08-08. **Until he does this the deployed page carries
sample data only.** This same decision unlocks the iPad control panel, because once both devices
sit behind one gate they are trivially known to be him, which is what he asked for
(*"I don't need a code that we need to make... it kinda connects automatically"*).

**Calendar plan (verified 2026-08-08).** Google Calendar becomes the hub because it is the only
one Claude can connect to. Both iCloud accounts publish a public feed that Google subscribes to.
Honest limits told to him: that feed is **read-only** and Apple refreshes it on its own schedule,
often 12-24 hours, and the Apple link is readable by anyone holding it. Two-way, fast sync needs
a paid third-party service. He also wants a **calendar VIEW toggle** on the dashboard, modelled
on the Toggl week grid he sent. Not built yet.

**HQ scan (he asked me to go through everything and propose tiles).** Found and recommended:
**12 decisions waiting in the Review Room** (the single best unused tile), the **ideas board
`hub/ideas.html` built this same morning as HQ01** which should become the whiteboard's real
source, **4 dated commitments** in `life/COMMITMENTS.md` feeding On the clock, the
**workflow-audit LOG.jsonl** as the honest streak signal, and **`hub/money.html`'s existing
expense tracker** as a real money source needing no bank connection.

**Gemini handoff given** for the two-way calendar sync comparison, with a paste-ready question.

## v5, 2026-08-08 — the alarm sound, sleep mode, device roles

**The alarm voice was wrong and he called it.** *"the alarm noise is so annoying... sounds like a
fire. This is not waking anyone up."* A pulsing 523Hz sine IS how smoke detectors are built.
Replaced with a synthesised struck bell: fundamental + inharmonic partials (2.01, 3.04, 4.17,
5.43), 6ms attack, exponential decay that kills highs first the way a real bar does, played as a
**C major pentatonic** phrase (no semitones = cannot sound anxious), escalating 3 notes / 4.2s →
6 notes + octaves / 2.4s, through a 5.2kHz lowpass. **Do not replace this with a beep.**

**Sleep mode shipped** — the Hatch half, and per him the half that actually matters:
*"when I'm sleeping, it doesn't matter how the dashboard looks."* Dim amber screen, big clock,
time-until-alarm, and a **generated** sound machine (pink / brown / rain / fan / white, all
synthesised in Web Audio so nothing is downloaded and it works offline) with 15/30/60 fade-out
that glides to silence. Reached by the `sleep mode` button; a launcher pattern he asked for.

**Device roles.** *"the pin needs to be on the iPad, please, not the actual TV, because I'm not
typing a pin on a TV."* Each device answers one question on first open: TV or iPad. **A TV never
sees a PIN.** PIN seeded to **123456** at his request. The behaviour he really described (iPad
verifies → TV unlocks) needs shared state = the Cloudflare step, pinned.

**ALARM SAFETY — a real bug was found and fixed, then tested.** Browsers block audio until the
page is interacted with, so after an overnight Fire TV restart the alarm would have fired
**silently**. Fixes: any interaction arms audio (typing the PIN counts), a silent keep-alive loop
holds the audio session, the wake screen flashes the full screen so it works with no sound at all,
a red warning shows on the dashboard whenever armed-but-muted, and the wake screen sits above both
the lock and sleep mode with dismiss focused and no PIN required. Verified in-browser.

**Layout.** He photographed tiles cutting off. Type now clamps against viewport HEIGHT as well as
width (a 16:9 TV is height-constrained), and every list caps itself with an honest "and N more".
Verified zero clipped tiles and zero page overflow at 1280x720.

**Still open:** the calendar view toggle (Toggl-style week grid he sent), real cross-device
control, and the calendar unification itself, which is blocked on his two-phone setup — see below.
