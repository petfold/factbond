# factbond: the loopmarket coupling

> **Vocabulary (2026-09-07).** loopmarket renamed its atomic commit from "settlement" to **clearing** (`clearing.py`, `MockClearing`, U3 "clearing trusts no solver"); *settlement* now means the makers delivering, which is exactly the P3 territory this coupling secures. This document and the rest of factbond's docs follow: clearing roots, clearing-weighted centrality, clearing-attached insurance, `P2-clearing-pricing.md`.

Status: design, 2026-08-07. Decided here: the shipping gate (Phase-0 green
AND loopmarket's P2 record-format freeze, jointly necessary); witness
telemetry as the early, ungated feed and the pool's demand stream;
clearing-weighted centrality (cleared fee-paid loops only) as the sole
centrality input to bond sizing; the three product couplings —
clearing-attached indemnity-exact insurance with payout→sibling-dispute
auto-filing, the per-edge/per-maker premium feed consumed as solver edge
weights, solver registration bonds as the pool's second customer; the
no-assumption boundary (B1, F6, `annotations.factbond` gating); the
correction-feed lanes. Open here: reliance denomination under U14;
centrality epoching; witness-replay sampling; cap-griefing via farmed
reliance; the correction-to-catalogue intervention policy.

This is factbond's half of the coupling with its first structured
consumer — the contract seen from the pool's side; `INTEGRATION.md` §8
records the underlying fit. The mirror document is
`../../../loopmarket/docs/plans/P3-guarantee-coupling.md`, which owns
everything solver- and clearing-side: witness instrumentation
mechanics, leg-oracle enforcement, risk-priced routing. Companions:
`mechanism-design.md` (bond sizing consumes §2's measure),
`insurance-products.md` (the products §3 attaches),
`records-and-anchoring.md` (record shapes, `annotations.factbond`,
anchored time), `evidence-policy.md` (the oracle roster's primary home),
`phase0-simulation.md` (the gate §5 waits on), and `THREATS.md` (T4
adjudication capture, T5 insurance arson, T6 catalogue capture and T9
basis-risk disputes primary here; T1 wash loops, T2 sybil spam, T3 solver
collusion, T7 lemons routing and T8 reputation gaming primary in
loopmarket's `docs/plans/THREATS.md`).

## 1. Why loopmarket first

loopmarket is the one deployment where reliance is provable for free. A
settling loop relied on specific catalogue ⊑ edges — `satisfies` walked
them, clearing re-verified every leg against pinned roots — and the
clearing root pins exactly which paying transactions depended on which
edge. So **F3: indemnity (payout ≤ provable reliance; payout-cap proxy
where unprovable)** is enforceable *exactly* here, not by proxy: insured
edge, relying legs, and cleared value are one auditable object. Everywhere
else — the agents-first wedge — reliance is private and the product runs
on payout caps until OP-1 (`insurance-products.md`) is solved. loopmarket
arrives as the flagship: insurable facts with natural consumers, carrying
their own reliance proofs.

It is also the pool's second bond customer: catalogue-edge stakes and
hedges are the first customer class, loopmarket's P2 solver registration
bonds (§3) the second — one pool, one LP interface, one loss ledger. Two
consumers pricing off one loss experience must agree on what counts as
experience; §2 is that agreement.

## 2. The witness feed and the only honest centrality

**Witness telemetry jumps every gate.** loopmarket instruments
`satisfies`/`is_below` at clearing re-verification and emits, per
cleared loop, the deduplicated ⊑ edge list its *own* verifier walked,
keyed by `(loop_id, ontology_root)` — the verifier's walk, never the
solver's, because a reliance proof built from an untrusted walk would be
no proof. This is pure telemetry with **no factbond dependency**:
derived, recomputable by anyone from the pinned `{book_root,
ontology_root}`, published beside the book, never in it. It lands
loopmarket-side ahead of any factbond phase (mirror §2, gate G1) so the
sizing term — bond = max(adjudication-cost floor, k × clearing-weighted
reliance/centrality), `mechanism-design.md` §2 — starts from accumulated
data rather than priors (consumption decided 2026-08, lands with Phase 1).

**Clearing-weighted centrality, precisely.** The centrality of a claim
subject over an epoch is the aggregate cleared value of the legs whose
clearing re-verification walked an edge reducing to that subject —
computed by joining witness records against the book's fill and receipt
records under pinned roots, counting **cleared, fee-paid loops only**.
This is loopmarket's planned **U12: reward/reputation statistics count
cleared fee-paid loops only**, mirrored into bond sizing; the join is
well-defined only because U11 (no partially-filled loop survives a merge)
holds on the book — a loop half-present after a merge would be half a
reliance proof. Per-maker keying inherits U8 (two-layer offer
authenticity) when it lands.

**Cleared, not delivered (decided 2026-09-07).** The measure counts a loop
at clearing and never at settlement. Reliance is created when the loop
commits under a root that pinned the edge; delivery discharges it, it does
not add to it. Counting delivered legs instead would buy no sybil
resistance — countersign is optimistic, mutual silence confirms, so
colluders manufacture a delivered loop exactly as cheaply as a cleared
one — and would cost determinism, since a statistic that waits on liveness
windows and oracle events is no longer recomputable from pinned roots. The
settlement layer enters the ledger in two ways only: negatively, as
adjudicated failures (lost disputes, paid claims, slashed bonds — the
events that are expensive to fake), and as the *exit* of exposure (the
epoching resolution under open problems). A maker's standing is cleared
volume against loss experience; nothing positive ever flows from delivery.

Static graph centrality was rejected, and the rejection is load-bearing.
Degree or betweenness in the offer/catalogue graph costs only postage to
manufacture (T2); wash loops are graph-indistinguishable from real ones —
every legitimate loop *is* a self-financing cycle (Victor & Weintraud,
WWW'21), so loop-shaped traffic proves nothing; and any liquid measure of
structural importance spawns a farming market (the Curve-wars lesson —
`mechanism-design.md` §2). Clearing-weighted reliance is farmable only
by paying real external-asset fees on real cleared loops — loopmarket's
U13 (wash-loop budget-balance by construction, fees external-asset only)
keeps the farm strictly negative-sum, and **F9: no volume-linked
emissions anywhere** guarantees factbond never mints the subsidy that
would flip that sign.

The same feed is the **assertion demand stream**: which KB slices the
pool auto-asserts, at what confidence, is read off real reliance traffic,
and pool policies name their coverage as batch root-claims over it
(`mechanism-design.md` §7; `records-and-anchoring.md` §5). One
translation is factbond's alone: the telemetry is edge-shaped, but **F2:
bonds attach to claim subjects** — transitive reduction can prune an
asserted edge whose claim stays entailed, orphaning an edge-attached bond
on an innocent catalogue commit — so witness edges are reduced to claim
subjects before any money attaches (`records-and-anchoring.md` §2).

## 3. The three product couplings

**1. Clearing-attached insurance** (decided 2026-08, lands with
Phase 2, gated by §5). Clearing offers each participant a verification
bet on the witness edges its loop relied on, priced per
`insurance-products.md` §3. F3 binds exactly: payout ≤ the value of the
cleared legs that provably pinned the edge — which kills insurance arson
(T5) at the pricing desk, because breaking an edge you insured returns at
most what you provably had at stake, minus premium. A payout **auto-funds
and auto-files** the sibling `attribute-matches-source` dispute
(`DESIGN.md` §7; `insurance-products.md` §6), whose structural half
settles free under **F8: structural claims settle by certificate only** —
an `is_below` certificate or trie inclusion/absence proof, the same proof
family loopmarket P2 uses for offer inclusion (one proof path, two
consumers; `../../../loopmarket/docs/plans/proof-fabric.md`). Aggregate
exposure obeys **F4: reliance-bounded adjudication + fail-closed caps**:
when open insurance on an edge approaches its ladder's final-rung
integrity cost, sales stop — the $750-bond-versus-$7M-reliance lesson
(Polymarket/UMA, March 2025) applied before the fact.

**2. The premium feed** (decided 2026-08; loss tables begin as Phase-0
outputs, the feed lands with Phase 2). The pool's per-edge and per-maker
loss experience — the loss tables of `insurance-products.md` §3, which
double as the catalogue's reliability audit — is published back to
loopmarket, where solvers consume it as edge weights:
`rate × (1 − expected-loss premium)`. Consumption is strictly
loopmarket-side and strictly solver-side — `Match.rate` and everything
clearing re-verifies stay premium-free, so loopmarket's U3 checklist is
untouched (mirror §5 owns routing, acceptance limits and concentration
fee; here, only what the numbers mean). Rejected: pricing the feed off
asserters' stated confidence alone — self-quoted premia would let
asserters print cheap insurance on their own claims
(`insurance-products.md` §3). Cold-start discipline carries over: silence
is thin data, never safe edges (T8's mirror pathology); premiums start
wide and narrow only on cleared history.

**3. Solver registration bonds** (decided 2026-08; custody lands with
Phase 1's pool, activates when loopmarket's P2 auction does). loopmarket's
batch auction requires solver bonds; they route through the factbond bond
pool rather than a bespoke escrow, which would split the loss ledger the
premium feed depends on. The sizing precedent is CoW's production record
— the founding doctrine independently deployed: bonds sized to damage and
adjudication, never to notional volume. CoW's full bonding pool is
$500,000 in yield-bearing stables + 1,500,000 COW, and both real slashes
in its history were operational negligence cured at exact damages —
$166,182.97 (CIP-22, hacked solver infrastructure) and $76,783 (CIP-55,
bad token allowances, drained over 67 txs, detected in ~1 minute) — with
a 72-hour cure window before slashing. Strategic manipulation is handled
by loopmarket's mechanism shape (marginal-contribution rewards, fairness
filter, reserve bid), so the bond targets residual channels: winning and
failing to clear, proposal spam, wash-loop score inflation (T1, T3). F9
binds both customer classes: no reward proportional to assertion or
clearing volume anywhere — assertion-mining and solver-emission farming
are the same FCoin, and one pool refuses both.

## 4. What factbond must not assume

The boundary keeps the coupling adoptable; written from factbond's side,
it is a list of forbidden assumptions:

- **loopmarket's core runs with no fabric present.** B1 is loopmarket's
  oldest invariant: `import loopmarket` and the whole model function with
  no pool, no premium feed, no factbond records anywhere — raw rates and
  P0 semantics, bit-for-bit; absence is not thinness. factbond must never
  design a mechanism whose correctness requires loopmarket to consult it.
- **factbond state never enters offers or book roots.** **F6: factbond
  state never enters canonical knowledge** — bonds, confidence, status,
  premiums live beside the book in the provenance-store pattern; two
  books with identical offers and different bonding must keep identical
  roots, or agreement-by-fingerprint dies. §2's derived-never-canonical
  rule is this clause applied to telemetry.
- **Nothing agent-facing claims bond status before the schema ships.**
  The reserved `annotations.factbond` namespace is the only surface
  guarantee status may ride on; `records-and-anchoring.md` §8 owns its
  schema, and until that is published no loopmarket answer, receipt, or
  MCP envelope may carry bond or insurance standing. **F1: status derived
  never merged** governs whatever rides there.
- **Composition is one-directional and numeraire-free.** loopmarket
  consumes factbond's records and read APIs; factbond never imports
  loopmarket, neither imports the other at module load (the B2 shape),
  and factbond consumes *published artifacts* only — witness records, fee
  ledgers, roots. U14 (numeraire-free scoring) means no external price of
  personal tokens exists: reliance denomination rests on declared
  coverage under per-leg/per-edge caps — a shared open problem.

## 5. Sequencing: two gates, jointly necessary

Mirrored, verbatim in substance, with the mirror's §8: **the coupling
ships only after factbond Phase-0 is green AND loopmarket's P2 record
formats are frozen.** Neither alone suffices:

- **Phase-0 green without the P2 freeze** wires a working mechanism to
  moving subjects. The reliance proof consumes P2's inclusion artifacts —
  the four-element pins **U10: {book_root, ontology_root,
  REGISTRY_VERSION, CONTRACT_VERSION}** and `proof-fabric.md`'s trie
  proofs — and the hash-pinned policy references need the v2 offer
  record; coupling before the freeze churns every policy hash and claim
  subject on every format bump, and churned wording is how basis-risk
  disputes are manufactured (T9).
- **The P2 freeze without Phase-0 green** sells hedges through a fabric
  that has not shown it can make honest verification profitable —
  clearing would auto-attach insurance that certifies nothing, the
  lazy-verification silent failure (`DESIGN.md` §5) deployed at flagship
  scale. The go/no-go is factbond's alone to declare
  (`phase0-simulation.md` §9); no loopmarket milestone accelerates it.

One piece deliberately jumps the gate: §2's witness telemetry. And one
path flows back before any product does: the **correction feed** (lands
with Phase 1, `records-and-anchoring.md` §6). loopmarket consumes
`Refuted` events on catalogue edges through three lanes: (a) *pricing* —
loss tables widen the edge's premium and solvers re-route, no write
access needed; (b) *clearing* — the correction bites the moment a
clearing operator adopts a corrected catalogue root, since U3
re-verifies against its own ontology; (c) *the catalogue* — a
reclassify-shaped intervention (retraction + motivating evidence +
keep-list, tracking ontodag EVOLUTION.md §5's discussion draft, never
forking it) under loopmarket's catalogue governance
(`catalogue-bootstrap.md`), yielding a new pinned root. The feed carries
evidence hashes and adjudicated value — an authenticated correction feed,
never a corrected catalogue; lane (c)'s last mile is governance, T6's home.

## Gates

- **G-LC1 (Phase 1 entry for the sizing term).** From loopmarket's
  published witness telemetry and fee ledger alone, factbond recomputes
  §2's measure; replaying sampled loops from their pinned `{book_root,
  ontology_root}` reproduces witness lists byte-for-byte (consuming the
  mirror's G1); loops without fee-paid clearing contribute zero.
- **G-LC2 (the coupling proper; mirrors loopmarket's G3).** Both owner
  sign-offs recorded: Phase-0's four pre-registered panels passed
  (owner: factbond, `phase0-simulation.md` §1–§2, half-life first among
  them), and the P2 record-format
  freeze declared (owner: loopmarket, `proof-fabric.md` +
  `P2-batch-auction.md`). Either absent blocks; Peter signs both mirrors.
- **G-LC3 (Phase 2, shared harness).** Indemnity exactness in the
  provable-reliance regime: no clearing-attached payout exceeds the
  cleared-leg value that pinned the insured edge under any T5 playbook,
  and arson ROI < 0 with reliance proofs on (G-I1 extended past the
  payout-cap proxy).
- **G-LC4 (continuous).** The no-fabric regression: loopmarket's suite
  green with zero factbond records present, and two books identical
  except for factbond side-records produce identical book roots — F6
  checked mechanically, the B1 discipline extended to the coupling.
- **G-LC5 (Phase 1).** Correction round-trip: a fresh client holding only
  the correction-feed owner address (G-REC2's follower) retrieves a
  `Refuted` catalogue-edge event carrying evidence hashes and adjudicated
  value sufficient to construct lane (c)'s intervention, no other state.

## Open problems

- **Reliance denomination under U14** (work package:
  `insurance-products.md` OP-1, jointly with loopmarket's
  `P2-clearing-pricing.md`; the mirror registers it as leg valuation).
  The structural half of the indemnity cap is free; the monetary half is
  not — legs have no external price, so caps rest on declared coverage
  plus ceilings, honest only while overstatement costs premium.
- **Centrality epoching and decay** — *shape resolved 2026-09-07,
  calibration open* (work package unchanged: `mechanism-design.md` §2's k
  calibration + `phase0-simulation.md` §6). The question was how fast
  cleared reliance stops counting: a stale hub keeps an inflated bond, a
  fresh hub sits underbonded, and any decay constant interacts with fact
  rot. Resolution: open reliance on a subject grows when a loop clears
  relying on it and shrinks when the relying legs *settle* — attested by
  their oracle, or their liveness window closes undisputed. Once a leg has
  settled, the harm a wrong edge could do to it can no longer land, so the
  bond stops carrying it. That replaces an arbitrary decay rate with an
  event the coupling already records, and makes the bond track live
  exposure rather than lifetime volume. Still open: legs whose settlement
  is disputed stay counted until the ruling (the disputed share is itself
  a reliability signal); edges whose consumers never settle anything —
  out-of-clearing reliance, `insurance-products.md` OP-1 — get no exit
  event and fall back to a calibrated decay.
- **Witness-replay sampling** (work package: this document +
  `phase0-simulation.md` adversary playbooks). Recomputable in principle,
  but replay costs real fetches against a published book; the pool cannot
  replay everything before pricing bonds, and the sampling rate that
  bounds statistics poisoning (T2) at acceptable cost is unknown.
- **Cap-griefing via farmed reliance** (work package: `THREATS.md`,
  T2 × T5 residual, with `phase0-simulation.md`). F4 fails closed on
  aggregate open reliance, so an attacker paying real fees to pump
  apparent reliance on a rival's edge freezes insurance sales on it;
  U13's fee floor prices the attack, and whether high enough — without
  the designed failure mode becoming a denial-of-service — is open.
- **The correction-to-catalogue intervention policy** (work package:
  `records-and-anchoring.md` §6's upstream tracking + loopmarket's
  `catalogue-bootstrap.md`). When a `Refuted` edge justifies lane (c)'s
  intervention versus a premium-only response is a governance judgment
  over an unbuilt upstream operation (a discussion draft upstream).

## What this document does not promise

- **Certified ≠ true (F7), on every coupled surface.** A bonded, insured,
  premium-priced edge is not a true edge; a cleared loop certifies
  re-verification under pinned roots, not delivery; a hedge is a priced
  promise to pay under stated caps, not a guarantee the leg happens — and
  no loopmarket surface (receipts, envelopes, `annotations.factbond`) may
  say otherwise.
- **Premiums are prices, not probabilities** — quotes under capital
  constraints, adverse selection, and attack. The loss tables measure
  adjudicated, dispute-adjusted experience; a captured rung poisons the
  audit exactly as it poisons payouts.
- **Centrality measures paid reliance, not importance.** An edge nobody
  clears across stays cheap to assert — that is the design (verification
  effort allocates with consumption), not a defect awaiting a patch.
- **CoW's numbers are another system's measurements** — calibration
  anchors and precedent for damage-sizing, never results about this
  pool's solvency or slash behavior.
- **Nothing here makes loopmarket need factbond, and nothing promises the
  coupling ships.** Every mechanism in this document can be absent and
  loopmarket must still import, match, solve and clear exactly as it
  does today; both halves of §5's gate sit outside this document's
  control, and a no-go on either is the process working, not failing.
