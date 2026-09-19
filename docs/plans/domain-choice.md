# Which facts first: a survey of what people edit and report (2026-09-19)

Status: research note, one evening's data. Question (Peter): opening hours
were chosen as the test domain; are there facts more important to people,
and something that would catch the interest of the Wikidata and
OpenStreetMap communities? Method: three live samples pulled on
2026-09-19 — 500 random Wikidata items with all their statements, 1,500
recent non-bot Wikidata edits, the 100 latest OSM changesets, taginfo's key
counts, and 321 OSM notes (open or closed within a week) from Ljubljana,
Vienna, London and Berlin. Raw tallies in the session scratchpad; the
numbers below are rough (regex classification; one snapshot).

## 1. What Wikidata is made of, and what humans touch

The random sample: 7,328 statements over 500 items, 588 distinct
properties. 216 of the 500 items are scholarly articles; stars, taxa,
proteins and Wikimedia housekeeping pages follow; 45 are humans. The
statements are correspondingly bibliographic and astronomical — "cites
work", "author name string", "title", "publication date", DOIs, magnitudes
— plus external identifiers. Almost all of it is bot-imported from a
source and **structurally verifiable against that source**: the
`attribute-matches-source` claim type, rung 0, cents to adjudicate,
nobody's daily life riding on it.

The recent human edits (1,500, 146 users, the top five users making 63 %
— a snapshot minute, dominated by a few WikiCite and cataloguing
sessions): author strings and series ordinals first, then **instance of,
occupation, image, employer, educated at, sex or gender, date of birth,
citizenship, cast member, official website, location** — biographical and
organisational facts about people and institutions. That is where human
attention is on Wikidata, and it is also where vandalism, edit wars and
reliance concentrate (infoboxes, search-engine knowledge panels).

**Wikidata candidate:** the *current state* of people and organisations —
position held and its end date, employer, head of an organisation,
headquarters, official website, dissolved-or-not. Churny, consequential,
disputable with a named source (an official page, a press release), so a
hash-pinned evidence policy fits, and every WikiProject that maintains
"is this still current?" lists is a community with a standing chore.

## 2. What OpenStreetMap is made of, and what people report as wrong

taginfo's top keys are buildings, roads, **addresses** (housenumber,
street, city, postcode — four of the top seven), names, then amenities,
access, speed limits, operators, lit, wheelchair further down. The latest
changeset comments are what mappers *did*: adding and updating shops,
restaurants, charging stations, childcare, benches, reverting.

The notes — what users *report* — are the useful signal. Two apps file
most of them: **StreetComplete** (90 of 321: "unable to answer" quests —
*what are the opening hours here*, *is this still here*, *is this road
completed*, wheelchair access, how many chargers) and **Organic Maps /
CoMaps** (23: "the place has gone or never existed", a POI-name mismatch,
a booking-only listing). By rough category: road works, access and
construction changes lead; then **a place's identity** (its name, what it
actually is), **a place that is gone, closed or never existed**, new or
missing objects, and **opening hours** (16 explicit). Addresses and phone
numbers barely appear — not because they are right, but because nobody
notices until a delivery fails.

## 3. What this says about the domain

- **Opening hours is not a wrong choice — it is the single most-asked
  StreetComplete quest and a steady note category — but it is the
  smaller half of one proposition.** The error that costs people a wasted
  trip is *the place is gone, moved, renamed or was never there*; hours
  are a refinement of a place that exists. The domain should be **POI
  liveness**: one subject (a place at a location) carrying three linked
  claims — it exists, it is what the record says (name, category), it is
  open when the record says. The plan's fact types (existence, category,
  opening hours, address, phone) already cover this; the ordering of
  importance is existence ≻ identity ≻ hours ≻ accessibility ≻ address.
- **Accessibility (wheelchair) is the highest-stakes attribute per
  consumer** — a wrong "yes" strands someone — and StreetComplete already
  asks it. It belongs in the first domain as a fourth claim, priced
  higher.
- **More important than any of these to people, but a different
  product:** healthcare and public services — the pharmacy on duty, a
  clinic's hours, an emergency department's status, transport
  disruptions. These have official feeds, so they are the *parametric*
  product (insurance-products.md §1), not the verification bet; a second
  domain once feeds are wired, not the first.
- **Wikidata's bulk is the cheap half of the ladder** (rung 0, matches
  source) and its human half is biographical currency. The two projects
  therefore test different things: OSM tests the expensive
  matches-world rung with physical verification; Wikidata tests
  certificate settlement at scale and the current-state churn of public
  facts. Start with OSM POI liveness for the go/no-go, keep Wikidata's
  current-state facts as the second, cheaper test.

## 4. Catching the communities' interest

The gamification Peter asked for already exists in both communities, and
factbond should attach to it rather than invent a game:

- **StreetComplete is a quest game.** A quest answered is a consumption
  event with an on-the-spot witness; a quest *unable to be answered* is a
  note. Bonded quests: the pool's standing assertion on a POI is the
  quest's prior, a contradicting answer with a photo is a dispute, and a
  **bounty per adjudicated correction** (the one reward F9 permits) pays
  the player who caught it. The app's users are exactly the marginal
  challengers with personal knowledge — the edge §CLAUDE.md's finding
  says the challenger needs.
- **Organic Maps' "place has gone" button** is a one-tap existence
  dispute. Same wiring.
- **The OSM notes backlog** is a queue of unresolved disputes with no
  stakes: a bounty for *closing* a note with evidence turns it into
  adjudicated corrections, and the note's history is the evidence
  bundle.
- **Wikidata WikiProjects** keep maintenance lists ("no end date on a
  position held since before 2020"); a bonded "still current?" campaign
  over one list, with the calibration ledger as the leaderboard, is a
  contained first campaign.
- **The calibration ledger as the score** (mechanism-design §1): visible,
  non-transferable, per district or per WikiProject — the reputation that
  cannot be bought, which is what these communities already run on.

## 5. Decided (Peter, 2026-09-19): POI liveness, and three threads to pursue

The domain is POI liveness; the plans and the harness follow it (§6). Three
threads Peter opened with the decision, each with a shape and a caveat:

1. **StreetComplete and its community.** The app is open source
   (github.com/streetcomplete/StreetComplete; quests are declared per tag,
   photos attach to notes) and its people are on the OSM community forum
   (community.openstreetmap.org, the StreetComplete category), the app's
   GitHub discussions, and the OSM Slack/Matrix channels. The proposal to
   take there, once the harness has a curve to show: **bonded quests** —
   the pool's standing assertion is the quest's prior, a contradicting
   answer with a photo opens a dispute the pool funds, a bounty per
   adjudicated correction pays the player, and the calibration ledger is
   the district leaderboard. Nothing in the app changes first: a
   companion service reading the notes feed and the changeset stream can
   run the whole loop beside it, which is how to arrive with something
   working rather than a request.
2. **Automated sources checked and bonded — the crawler as asserter.**
   Wikidata's bulk and much of OSM's hours are imported from sources; a
   crawler that finds a business's hours on its own website and compares
   them with the record is rung 1 of the ladder (the automated evidence
   check, `evidence-policy.md`) run *pre-emptively*: the pool asserts
   with a bond on the records that check out, at a confidence the
   crawler's own calibration earns, and refuses the ones that do not —
   refusal being signal. This is `DESIGN.md` §7's pool-as-asserter with
   an evidence policy behind it, and it seeds the loss tables before any
   human verifies anything. Caveat: a website is a source, not the world
   (the record matches the source; the shop may still be closed) — the
   claim type is `attribute-matches-source`, priced as such, and the
   matches-world claim stays the quest apps' job.
3. **Abstract knowledge, missing high-level statements, and a browser
   plugin for editors' own bonds.** The subsumption edges ontodag carries
   (`X ⊑ A`) and Wikidata's `subclass of` / `instance of` are the
   high-level statements most often missing or wrong, and they are the
   claims factbond's structural rung settles by certificate. A browser
   plugin letting a Wikidata editor attach a bond to a statement they
   just made is the natural asserter surface. Peter's caveat is the
   binding one: **most editors have no crypto.** Two answers that keep
   F9: (a) the *score* needs no money — the calibration ledger is a
   signed speech act plus outcomes, so an editor can assert at a stated
   confidence and be scored without staking, and a bond can be *sponsored*
   by the pool on the editor's calibration record (the pool stakes, the
   editor's reputation is at risk, the slash is the pool's and priced
   into the editor's future sponsorship); (b) a fiat on-ramp is a product
   decision for later, not a mechanism one. The plugin is therefore a
   reputation-first surface: sponsored bonds for scored editors, real
   stakes for those who have them. Not started.

## 6. What changed in the plans and the harness (2026-09-19)

`phase0-simulation.md` §3 (the domain), §2 (λ as the curve's axis, D\* as
verification plus adjudication); `DESIGN.md` §10 (Phase 1's target);
`insurance-products.md` §1 (the parametric first domain);
`loopmarket-coupling.md` §3c (the quest apps as the consumption channel).
The harness: the five fact types with realistic verification costs, a
bounty per adjudicated correction, and `python -m factbond.sim curve` —
half-life against consumption rate from launch values up, T marked when
the block names it.

## 7. The first number (harness, 2026-09-19 night)

At a launch consumption rate no consumption reaches the cold errors; the
half-life of the seeded error population exceeds a 120-day run at every
rate on the axis. Sweeps do reach them: on a 2,000-fact KB, 100 facts
verified a day (each fact revisited every ~20 days) gives an 11-day
half-life and holds drift down; 30 a day corrects a quarter of the
errors; half a fact a day — five people, three facts a month — corrects
nothing. Scaled: ~1,800 verifications a day for a 50,000-POI city at
T = 14, about 60 person-hours a day at a street a time. That is the
participation the product needs, and why thread 2 (the crawler as
asserter on sources) is not optional: it is the only verifier that scales
without people.

## 8. Start with the boxes (Peter, 2026-09-19)

Within POI liveness, the first target is the **automated boxes** —
parcel lockers and pickup stations. Three reasons, all Peter's:

- **No person speaks for a box.** A shop that has a person at the
  loopmarket interface reports its own state through that person; a box
  is unattended, so its liveness is exactly the fact nobody is
  responsible for and a guarantee is for.
- **The claims are few and crisp:** it exists at the mapped place; when
  it is accessible (24/7, a host's hours, a locked lobby); and its
  **handover model** — whether one private person can hand a thing to
  another through it, at what fee, through which app. That last claim is
  the one loopmarket needs: most networks admit only their own carrier's
  parcels, a few allow peer drop-off, and the map does not say which.
- **Use produces the verification.** Once boxes carry loopmarket
  handovers, every handover is a report: the operator's signed event (the
  parametric feed class of `insurance-products.md` §1) and the
  counterparty's *received* act say whether and when the box worked. The
  box's loss table writes itself from traffic, and sweeps are only for
  boxes nobody has used yet.

Sizing (OSM, 2026-09-19, Ljubljana bbox): **203 mapped lockers**
(Pošta Slovenije 101, GLS 68, DPD 30), of which 29 carry opening hours,
48 a check date, 16 a reference, **1 any payment tag**, and 185/160 the
mail-in/pickup flags. The record is present but thin exactly on the two
claims that matter for handover, hours and model — the gap a bonded
campaign fills. (The Vienna query timed out; other cities to follow.)

The harness carries a `lockers` preset (`--preset lockers`): three fact
types with cheap verification (a box is visible and its app answers, ~$5
of a person's time; the handover model needs one attempted drop-off),
low drift, and consumption events that are loopmarket handovers reporting
back — the feed-driven regime, where the population half-life falls with
traffic rather than with sweeps.

Plans this touches: loopmarket's `P3-guarantee-coupling.md` §4b–§4c
(the ranked claims a counterparty relies on; the boxes as the first
bonded handover points; `countersign` split into *received* and *as
described*), `P1-spacetime-terms.md` §4 (the seal rides in the same box).

## What this document does not promise

That any of these communities will adopt bonded quests; that one
evening's samples are representative (the Wikidata edit snapshot in
particular was five users' sessions); that the category counts are
precise (a regex over free text, in four languages).
