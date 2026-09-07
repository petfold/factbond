# factbond: mechanism design — odds-weighted bonds and the adjudication constitution

Status: design, 2026-08-07. Decided here: the odds-weighted bond primitive
with its stake direction fixed (the asserter's capital scales with stated
confidence) and coarse buckets as the only confidence surface; the revised
two-term sizing doctrine — bond = max(adjudication-cost floor,
k × clearing-weighted reliance/centrality), final-rung integrity cost ≥
aggregate open reliance, per-claim caps failing closed (F4) — amending the
founding adjudication-cost-only doctrine; the four-rung escalation ladder as
a written constitution: certificate rung zero (F8), policy-bound evidence
check, staked panel with per-round stake-base growth, an independent top
rung with soulbound stake (F5), no incoherence-only slashing, retroactive
bond refunds on reversal, reopenability on new evidence, conduct and removal
rules — including the evidence-class demotion authority — written before the
first dispute; size-capped dispute-triggered markets settled on the ruling;
pool-funded disputes and appeal fees as the wearing-down countermeasure;
assertion fees accruing to the pool with no volume-linked emissions anywhere
(F9); withdrawal pricing; batch-claim slashing shape. Open here: the
odds-weighted equilibrium (the design's main risk and its paper), the safe
dispute-market size curve, the batch exhaustion bound, ruling-supersession
confluence, the top rung's existence at the scale F4 demands, the systemic
adjudicator-failure loading.

This is the deepest document of the programme: it expands `DESIGN.md` §3,
§4, §6.4 and §8 into full mechanism, and carries in full the two 2026-08-07
flagged revisions those sections announce — the sizing doctrine (§3's
note; ratified 2026-08-20) and the top rung's non-negotiable properties
(§6.4's note). Companions:
`evidence-policy.md` (what the ladder's evidence rung admits),
`insurance-products.md` (the products these bonds secure; the auto-dispute
coupling), `netting-and-reserves.md` (the capital behind the pool; the
pm-AMM instrument), `records-and-anchoring.md` (the record shapes and the
clock every window here runs on), `phase0-simulation.md` (where every
number below is fixed or killed), `loopmarket-coupling.md` (the first
structured consumer), and `THREATS.md` (T4 adjudication capture & dispute
griefing, T5 insurance arson, T6 catalogue governance capture, T9
basis-risk disputes — all primary here; T1–T3, T7, T8 primary in
loopmarket's `docs/plans/THREATS.md`). Everything below implies unbuilt
mechanism and carries its phase marker per `DESIGN.md` §10's clock.

## 1. The primitive: an assertion is a limit order against the world

The bonded assertion (`DESIGN.md` §3) already beats the prediction market
at millions-of-facts scale: one bond, one side, counterparty capital only
on dispute, settlement only on dispute (~1%). What it lacks, stock, is
odds-expressiveness: a UMA dispute is bond-against-equal-bond regardless of
the claim's probability — challenging a 99.9% claim and a 60% claim cost
the same (`DESIGN.md` §4). The fix, and this design's most novel mechanism:
**the asserter states a confidence, and the stated confidence sets the
dispute stake ratio** (decided 2026-08, lands with Phase 1).

Precisely: an assertion carries `(claimId, confidence c, bond B)`. The
bond's two floors are §2's business; the *ratio* rule is this section's.
Opening a dispute requires the challenger to stake

    B_challenger = max( B × (1−c)/c ,  D_rung )

where `D_rung` is the dispute floor of §3 (the cheapest applicable rung's
adjudication cost plus the delay externality). The asserter's side is the
heavy side: asserting at 0.99 means your bond faces the challenger's at
99:1, pro-rated on bond size — exactly the natural asymmetry of a market
bet on a 99% claim ($99 against $1), recovered without a market. At that
point an assertion literally *is* a limit order: "I offer to bet at these
odds, world" — a standing, priced, one-sided quote that the world may hit
at any time by posting the other side. Losing side pays per `DESIGN.md`
§8's slashing split: the majority of the loser's stake to the winner, a
slice burned or to the adjudication treasury (UMA's production analog:
winner takes own bond back plus half the loser's, the other half burned to
UMA's Store).

The stake direction is a design decision with teeth, so it is stated as
one: **the asserter's capital at risk grows with stated confidence.**
`DESIGN.md` §11.2 names the founding worry — assert at 0.999 to make
challenges maximally expensive — and under this direction that worry
*inverts*: at 0.999 an honest challenge is maximally cheap to open (1/999
of the bond) and maximally lucrative to win (the majority of the whole
bond), while the overconfident asserter has concentrated their own capital
exactly where challengers profit most. Confidence-scaled stakes are the
design's hypothesis for closing the griefing vector; whether the hypothesis
survives equilibrium play — including the two residual shapes §8 names
(dispute-spam against honest high-confidence claims, which the `D_rung`
floor exists to price, and capital-cost pooling that degrades the
confidence signal) — is the paper (§8). Nobody has published an optimistic
oracle with asserter-quoted odds (`DESIGN.md` §4); the game theory is open
and gates real stakes (Gate G-M1).

Stated confidence does four jobs, and only four: it sets the dispute ratio
above; it is the system's price signal on undisputed claims (`DESIGN.md`
§4); it *seeds* the insurance prior — never prices the premium alone, which
would let asserters print cheap insurance on their own claims
(`insurance-products.md` §3's rejected alternative, referring back to this
section's open problem); and it accrues to the asserter's calibration
ledger (§4's fast-path gate). Withdrawal is priced, not free (decided
2026-08, lands with Phase 1): an undisputed assertion may be retracted at
the cost of the assertion fee (never refunded) plus a recorded retraction
in the ledger — a capital-free renege would make the assertion a free
option, the exact failure the bond exists to prevent (`DESIGN.md` §3); once
a dispute is open the bond is locked to the outcome. The retraction record
shape is upstream's, unchanged (`records-and-anchoring.md` §2).

**Buckets, coarse, four:** confidence is quotable only as
{0.9, 0.97, 0.99, 0.999} (`DESIGN.md` §8) — roughly log-spaced odds of
9:1, ~32:1, 99:1, 999:1. Why coarse: false precision invites gaming of the
odds ratio, and every extra bucket thins the calibration ledger's cells —
four cells accumulate statistically meaningful track records at Phase-1
volumes; forty never would. Why floored at 0.9: below it the asserter is
not near-certain, and the right instrument for a genuinely contested
proposition is a two-sided market, which the dispute path provides on
demand (§5) — a dormant bonded claim is the capital-efficient encoding of a
*near-1* market (`DESIGN.md` §3), not of a coin flip. The bucket set is
swept in Phase 0 against coarser and finer alternatives
(`phase0-simulation.md` §6); the four values are the prior, not a result.

## 2. Bond sizing, revised: the reliance term (flagged doctrine revision)

The founding doctrine — bond sized to the cost of forcing and running a
dispute, not to the value riding on the claim (`DESIGN.md` §3) — survives
as the *floor* and is empirically excellent there: ~99% of UMA assertions
since 2021 settle undisputed (crypto.news), Polymarket alone averaged ~545
resolutions/month in 2024 (UMA blog), and UMA's total value secured stood
at ~$1.84B in August 2025 (pricediscoveries.com) — the happy path really is
secured by small bonds ($750 USDC and 2 hours' liveness in Polymarket's
OOv2 regime, $2–5 proposer reward; 10,000 USDC both sides in generic OOv3;
factbond's template-claim prior is $1–10, `DESIGN.md` §8, swept $0.5–$20 in
Phase 0).

As a *ceiling*, 2025 falsified it. In March 2025 a $7M Polymarket market
("Ukraine agrees to Trump mineral deal before April?") resolved YES though
no deal was signed: a single UMA whale cast 5M UMA across 3 accounts — 25%
of the DVM vote in the dispute round — and Polymarket called it an
unprecedented governance attack and did not refund (The Block, CoinDesk).
The attack's profit was in the market position, not the oracle game: a
notional-to-bond ratio near 10^4 meant a ~$750 bond gated disputes on ~$7M
of open reliance, and the last rung's integrity cost was decoupled from
what rode on the answer. Bonds priced to adjudication cost are safe
*only while attacker profit outside the oracle game is capped*.

The revised doctrine (decided 2026-08, ratified by owner sign-off
2026-08-20, lands with Phase 1; amends `DESIGN.md` §3 per its note),
three clauses:

1. **bond = max( adjudication-cost floor , k × clearing-weighted
   reliance/centrality of the claim ).** The floor keeps template claims
   cheap; the reliance term makes a hub claim — one that much cleared value
   walks through — expensive to assert casually and expensive to attack.
   Centrality is **clearing-weighted, never static graph degree**: a
   liquid measure of structural importance invites farming (the Curve-wars
   lesson — liquid governance weight spawned Votium's industrialized
   vote-buying), whereas clearing-weighted reliance is farmable only by
   paying real fees on real cleared loops — loopmarket's U12
   (*reward/reputation statistics count cleared fee-paid loops only*)
   applied to bond sizing. The measure is supplied by loopmarket's
   witness-edge telemetry (loopmarket `docs/plans/P3-guarantee-coupling.md`
   §2; `loopmarket-coupling.md` §1), which lands before any bond exists
   precisely so this term starts from data. `k` and the floor are Phase-0
   outputs (Gate G-M2).
2. **The ladder's final rung must have integrity cost ≥ the aggregate open
   reliance on the claim.** Reliance means everything that pays out or
   re-prices on the answer: open insurance, dispute-market open interest
   (§5), clearing exposure in the coupling. Nexus Mutual's quorum rule is
   the production precedent for scaling adjudication weight with what rides
   on the ruling: a claims-assessment result stands only if the assessing
   stake exceeds 5× the claim amount, else it escalates.
3. **Per-claim caps fail closed.** When the cap — or clause 2's condition —
   would be breached, new reliance-bearing sales on that claim stop, with
   no override and no manual step. This is invariant **F4:
   reliance-bounded adjudication + fail-closed caps** (its insurance
   instantiation: `insurance-products.md` §5; its reserve instantiation:
   `netting-and-reserves.md` §7). A cap that fails open is not a cap; a
   stopped market is the designed failure mode, not an outage.

Cheap bonds still secure the ~99% undisputed path; what the revision
changes is that reliance can no longer silently accumulate past what the
ladder can defend. Phase 0 must be able to *express* the failure before it
can certify the fix: with the reliance term switched off, the harness
reproduces the $750-versus-$7M capture in miniature; with it on, the same
scenario is unprofitable (`phase0-simulation.md` §6, calibration gate).

Dispute-side sizing is symmetric in spirit: the challenger's floor `D_rung`
covers the invoked rung's adjudication cost plus the **delay externality**
— a dispute freezes the claim's status (`Contested`) and everything priced
on it, and disputer bonds must at least cover what that freeze inflicts, or
dispute-spam becomes a free option against every honest high-confidence
claim (§1's inversion; T4's griefing half). Spamming disputes to exhaust
the pool's auto-funding (§6) is priced by the same floor and checked as a
design-time inequality across the whole Phase-0 grid, not at the design
point (`phase0-simulation.md` §5).

## 3. Assertion spam, laundering, and the no-emission rule

Anyone may assert; assertions cost a fee that accrues to the bond pool
(`DESIGN.md` §7). The fee is the spam price, the pool's revenue beside
yield, and — deliberately — the *only* thing an assertion generates.
Invariant **F9: no volume-linked emissions anywhere**. The precedents are
terminal: FCoin's trans-fee mining refunded 100% of trading fees in its own
token and reached, with its copycats, ~40% of global reported exchange
volume before insolvency inside 20 months with a $130M shortfall;
LooksRare's volume-linked LOOKS emissions produced a measured 1.34% daily
return on wash capital ($6.2M rewards against $3.7M fees on one day).
Assertion-mining would be the FCoin of facts: any reward proportional to
assertion volume is farmable by asserting garbage at scale, and the farm's
statistics would poison the one dataset the system exists to produce. So:
no reward for asserting, ever. An asserter's income paths are exactly:
yield on pool stake, a share of assertion fees as a pool LP, slash winnings
from disputes won, and the underwriting business itself. Nothing else
exists to farm, and Phase 0 asserts this by construction — the F9 check
fails loudly if a future mechanism change introduces a volume-linked path
(`phase0-simulation.md` §5).

**Self-dispute laundering** — disputing your own assertion from a second
identity to wash stake through the winner's share — is strictly negative
under the slashing split's burned slice (`DESIGN.md` §8): the launderer
pays the burn on every cycle. The burn is load-bearing; any future split
change must re-verify this inequality.

**The calibration ledger counts what cannot be farmed.** A track record
built from certified-by-timeout claims nobody watched is free to
manufacture — assert trivialities at 0.999, wait out liveness, collect a
reputation. So the ledger that gates §4's fast path counts only resolutions
that carried consumption (insured, or clearing-pinned in the coupling)
or survived a real dispute — the U12 shape again, applied to reputation.
Silence remains uninformative (`insurance-products.md` §3's cold-start
discipline); an unwatched certification is a non-event in the ledger.

**No token voting anywhere.** The token-curated-registry pattern died
empirically — AdChain's post-mortem: no shared judging criteria, mercenary
voters without domain knowledge, per-entry voting that scales in neither
gas nor attention — and factbond's curation layer is structurally its
replacement: usage (paid insurance loss experience) generates the signal,
insurers are paid domain specialists, and nothing is voted on in the happy
path. `DESIGN.md` §9's no-token stance is generalized here to: no
mechanism in this document may acquire an always-on vote, and no
adjudication or governance weight may be a liquid transferable asset (§4).

## 4. The adjudication constitution

The ladder (`DESIGN.md` §6.4, its top rung revised per the flagged note)
is written as a constitution — structural properties fixed before any
dispute exists, because every deployed system's worst failures were
rules-about-rulers failures discovered mid-dispute. Four rungs, cheap to
expensive (decided 2026-08, lands with Phase 1; dispute markets and pool
funding, §5–§6, land with Phase 2):

- **Rung 0 — the proof checker.** Invariant **F8: structural claims settle
  by certificate only**. Every `attribute-matches-source` dispute — batch
  or single — terminates here mechanically: an `is_below` certificate or a
  recordstore trie inclusion/absence proof, verified by anyone holding 32
  bytes (`INTEGRATION.md` §5; `records-and-anchoring.md` §5). No jurors,
  no evidence problem, no discretion. The entire matches-source half of
  the dispute space never touches anything below this line.
- **Rung 1 — the automated evidence check.** A bot verifies the dispute's
  evidence bundle against the claim's hash-pinned policy
  (`evidence-policy.md` §2–§3): signed feeds, zkTLS transcripts, attested
  capture with live revocation checks. The policy hash is the contract;
  ambiguity — empirically the cheapest attack in every deployed system
  (Augur's chronic invalid-market tax; Proof-of-Humanity's photo-angle
  literalism; the Zelenskyy suit) — is fought at wording time, not here.
- **Rung 2 — the staked panel, growing every round.** Drawn, staked
  adjudicators rule; an appeal re-runs the question before a strictly
  larger stake base — Kleros's shape: each round has 2n+1 jurors (double
  plus one) with exponentially rising fees. The growth rule is the p+ε
  defense: a briber who credibly promises payment only if the attack loses
  makes bribery free on success (Buterin 2015), and the standard counter
  is that every appeal enlarges the jury and therefore the bribe bill —
  the attacker's liability must grow *faster* than the bond ladder it is
  chasing. Escalation stakes follow reality.eth's exponential
  bond-doubling, maintained at §1's odds ratio.
- **Rung 3 — the independent arbitrator.** Escalation ends at an
  arbitrator whose incentive base is independent of the system's own
  economics — never a vote of a token that can hold positions in the
  disputed outcome. Invariant **F5: tribunal independence + soulbound
  stake**. UMA's DVM is the disqualifying counterexample (the same token
  votes on disputes it can trade against — §2's capture); reality.eth's
  composition is the model: a cheap exponential-bond fast path escalating
  into an independent arbitrator contract, expected to be invoked rarely
  and allowed to be slow and expensive. Rarely-invoked is the design
  intent: expensive rungs exist mainly as deterrence (`DESIGN.md` §6.4).

Constitutional clauses, binding across all rungs:

- **Adjudicator stake is soulbound**: non-transferable, time-locked,
  retroactively slashable. A liquid adjudication token spawns a bribe
  market by default — Convex accumulated over a third of veCRV, Votium
  industrialized the vote-buying, and the Mochi governance attack was
  stopped only by a discretionary nine-member Emergency DAO. Soulbound
  stake means no market can *price* capture; it raises the cost, it does
  not zero it (see closing section).
- **No incoherence-only slashing.** Slashing minority voters for
  disagreeing with the majority manufactures conformity cascades: in the
  2025 Zelenskyy-suit market ($160–237M volume) UMA voters resolved NO
  twice against the photographic record because voting the perceived
  majority was the stake-preserving move, and the YES-side disputers were
  slashed both times. Adjudicators here are slashed for provable
  misconduct (rule violations, revealed collusion), never for voting the
  losing side alone.
- **Retroactive bond refunds on reversal.** When a ruling is later
  reversed (reopening, below), every party slashed under the reversed
  ruling is made whole from the slash proceeds and the treasury slice.
  Without this, one bad ruling teaches every future disputer the
  wearing-down lesson (§6) permanently.
- **Rulings are reopenable on evidence that did not exist at ruling time,
  within a window.** Nexus Mutual's bZx claim is the precedent: first
  denied, then reversed and paid ~$31K after the post-mortem changed the
  facts. Evidence-class fleet revocations (the Nikon Z6III pattern)
  qualify by construction (`evidence-policy.md` §5). Reopening interacts
  with status derivation — several rulings standing on one dispute — and
  the supersession order must be proven confluent
  (`records-and-anchoring.md` §3; registered open problem below).
- **Conduct and removal rules are written before the first dispute** — for
  adjudicators at every rung *and* for the evidence-class demotion
  authority (`evidence-policy.md` §5 assigns its constitution here; the
  authority holds soulbound stake like any adjudicator, demotions are
  signed attributable speech acts, wrongful demotion is a conduct
  violation triable on this same ladder, and the removal path never
  requires the misbehaving party's cooperation). The empirical case is
  Croatian Wikipedia, 2011–2020: a small admin cabal held an entire
  project for nine years, and the comparative CSCW study (TeBlunthuis et
  al., CSCW 2024) attributes the capture to missing constitutional
  constraints on administrators — no local removal mechanism existed.
  Capture is a rules-about-rulers failure; the rules exist before the
  rulers matter. T6's long-horizon defense lives here and in `THREATS.md`.
- **The fast path is track-record-gated; the dispute path is
  permissionless, forever.** UMA's own retreat is instructive: UMIP-189
  (passed 2025-08-06) moved Polymarket to Managed OOv2, restricting
  *proposals* to 37 whitelisted addresses — Risk Labs, Polymarket staff,
  and proposers with more than 20 proposals at over 95% accuracy — while
  keeping disputes open to anyone. factbond adopts the asymmetry without
  the fiat whitelist: high-volume auto-assertion privileges (the pool
  policy surface, §7) and reduced-friction proposal lanes are earned by
  calibration-ledger track record (§3's farming-resistant ledger), and
  no track record is ever required to *dispute*. Permissionlessness is
  kept exactly where adversaries are needed.
- **The load condition is constitutional law**: §2's clause 2 — final-rung
  integrity cost ≥ aggregate open reliance — binds every rung
  configuration change. A ladder reorganization that would breach it on
  any live claim fails closed: the reorganization waits, or sales stop.

## 5. Dispute-triggered markets: priced discovery, capped

A contested claim opens a real two-sided market for the dispute window
(`DESIGN.md` §4), so third parties with information can take positions;
the market settles on the adjudicator's ruling. Price discovery is
purchased only for the ~1% of claims worth its cost (decided 2026-08,
lands with Phase 2). The instrument is `netting-and-reserves.md` §8's:
pm-AMM / distribution-market machinery (Paradigm, Nov 2024 / Dec 2024),
whose constant-L2-norm invariant runs cheaply on-chain and whose dynamic
variant withdraws liquidity as resolution nears — the anti-manipulation
shape a thin market needs. The market's refined odds — never raw asserter
confidence — feed escalation stake sizing and insurance premia
(`netting-and-reserves.md` §8: stated confidence is a gameable input).

**Size caps are not prudence; they are contamination control.** The market
settles on the ruling, so every unit of open interest is incentive load on
the adjudicator — the dispute market re-creates, in miniature and *inside*
the dispute window, exactly the notional-to-bond mismatch §2 just closed:
a large enough market on the ruling makes capturing the ruling profitable
regardless of bond arithmetic, and the adjudicator's
incentive-compatibility then carries trading stakes it was never sized for
(`DESIGN.md` §4's design note, honored). The v1 rule: a dispute market's
open interest counts toward the claim's aggregate open reliance under §2
clause 2, and new positions stop — fail closed, F4 — when total reliance
approaches the ruling rung's integrity cost. What the *safe curve* is —
how open interest may scale as the dispute climbs to more expensive rungs,
and whether the cap should price in the market's own information value —
is a registered open problem below.

## 6. The pool funds the fight: the wearing-down countermeasure

The observed failure this section answers: honest disputers lose bonds to
a captured or conformist tribunal, learn not to dispute, and the system
chills — the Zelenskyy-suit market resolved wrongly twice and slashed the
honest side both times, once publicly is enough to teach the lesson. The
structural answer (decided 2026-08, lands with Phase 2; full pipeline in
`insurance-products.md` §6): a paid-out verification bet **auto-funds and
auto-files** the sibling matches-source dispute, and the pool — a repeat
player with a booked loss and a slash claim to recover — **pays the appeal
fees up the ladder**. Kleros's crowdfunded appeals are the deployed
precedent for third-party appeal funding. Under this coupling no
individual ever posts a dispute bond from their own pocket on the claims
that matter most: corrections are prosecuted by a capitalized repeat
player with aggregated stakes — the one party a wearing-down attack cannot
exhaust one bond at a time. Combined with §4's retroactive refunds on
reversal, losing an honest dispute to a bad ruling is a recoverable event,
not an exit condition. The metric under test is challenger-population
survival after an unjust ruling (`phase0-simulation.md` §7, T4's
wearing-down variant).

## 7. The pool as asserter: the policy surface and batch stakes

The bulk asserter is the pool itself (`DESIGN.md` §7), auto-asserting
whole KB slices per policy, and the policy is a first-class, published
object (decided 2026-08, lands with Phase 1). A pool policy names: the
coverage subject — a `(root, key-prefix)` pair per
`records-and-anchoring.md` §5's batch root-claims ("all OSM opening_hours
in Prague") — the confidence bucket, the per-record bond density
(`DESIGN.md` §7's "0.5 DAI each"), the resolution policy hash
(`evidence-policy.md` §2), and its refusal record: slices the pool
declines to assert are recorded, because **refusal is signal**
(`phase0-simulation.md` §4). Individual asserters matter at the margins —
private knowledge asserting against the pool's blanket confidence — and
the odds-weighted primitive is what makes that a trade rather than an
argument.

Batch stakes slash surgically and exhaust statistically (decided 2026-08;
record fields land with Phase 1 per `records-and-anchoring.md` §5, the
economics activate with Phase 2): each successful leaf refutation —
localized by an inclusion proof — slashes the per-record density `d` from
the root stake, paid per the §1 split. The root claim as a whole is a
claim about an *error rate* (confidence 0.93 over N leaves), so the
exhaustion rule is statistical inconsistency, not stake depletion: when
accumulated refutations are inconsistent with the stated bucket's implied
rate, the whole root claim flips to `Refuted`, the remaining stake is
exposed to the ladder, and the reserve treats the slice as one exposure
cluster (`netting-and-reserves.md` §7). The exact inconsistency test — and
how it composes with drift, since facts rot mid-coverage
(`phase0-simulation.md` §3) — is a registered open problem below.

Two-pool discipline holds throughout: the bond pool underwrites *process*
(this document's stakes), the payout reserve underwrites *claims*
(`insurance-products.md`); conflating them is the classic error
(`DESIGN.md` §6.3). The pool asserting and the reserve insuring the same
slice is not a conflict but a correlation — both books fail together on a
captured rung — and that correlation is exactly the systemic term the
reserve carries explicitly (`netting-and-reserves.md` §7, its open
problem shared here).

## 8. The game-theory work package: the paper

`DESIGN.md` §11.2 names odds-weighted bond game theory as simultaneously
the design's main risk and its paper; this section is its work package.
The questions, each mapped to a Phase-0 experiment
(`phase0-simulation.md` §5, §7 — the confidence-misstatement,
challenger-entry-threshold, and asserter–challenger-collusion runs feed
here; deliverable 5 is the empirical half):

1. **Equilibrium of asserter-quoted odds under asymmetric stakes.** Does
   a separating equilibrium exist in which stated buckets track true
   belief, given that higher stated confidence costs proportionally more
   capital (the 99-cent problem at the assertion layer, mitigated but not
   erased by pool yield, `DESIGN.md` §6.3)? Or do rational asserters pool
   at low buckets, degrading the price signal the whole §1 design exists
   to produce? Existence, uniqueness, comparative statics over bucket
   sets.
2. **The assert-at-0.999 griefing vector, both directions.** The founding
   worry (§1) and its inversion: with the asserter on the heavy side,
   does confidence-scaling close the make-challenges-expensive vector as
   hypothesized — and does the `D_rung` floor close the inverted
   cheap-dispute-spam vector without pricing out the honest marginal
   challenger (panel 2 of `phase0-simulation.md` §1)?
3. **p+ε under per-round stake-base growth, formally.** The Kleros 2n+1
   counter is folklore-plus-deployment; the formal question is the
   condition under which the briber's cumulative liability provably
   outruns the doubling bond ladder at §1's odds ratios, and whether
   soulbound stake (no bribe market to coordinate through) changes the
   attainable ε.
4. **Asserter–challenger collusion.** Self-dispute laundering is priced by
   the burn slice (§3); the general form — colluding to manufacture a
   dispute history, farm the calibration ledger, or launder through the
   dispute market — needs treatment jointly with §5's caps.
5. **The pool-as-asserter equilibrium.** Does blanket pool assertion crowd
   out the private asserters whose marginal information the system wants,
   and is the refusal signal (§7) informative in equilibrium?

Deliverables, in order: the Phase-0 simulation results (equilibrium
observations, entry-collapse maps, bucket-set sensitivity —
`phase0-simulation.md` §8), then **an equilibrium analysis note before any
real stakes** — the analytical half, at working-paper standard, whose
publishable core is the odds-weighted optimistic oracle itself. The
decision rule is Gate G-M1: if flat bonds dominate odds-weighted bonds
across the defensible parameter region, factbond ships flat bonds and
keeps stated confidence as a pure signal — the mechanism must beat the
UMA baseline it generalizes, or it is complexity without a customer.

## Gates

- **G-M1 (Phase 0 → Phase 1, blocks real stakes).** The §8 equilibrium
  note and the Phase-0 simulation *agree* that odds-weighted bonds are not
  dominated by flat bonds on the pre-registered panels (planted-error
  half-life, honest-challenger ROI, arson/spam ROI —
  `phase0-simulation.md` §1). Disagreement or domination ⇒ flat bonds
  ship; confidence stays signal-only.
- **G-M2 (Phase 0).** Sizing parameters fixed from simulation outputs: the
  bond floor and `k` chosen such that the capture replay
  (`phase0-simulation.md` §6) is unprofitable with the reliance term on,
  and the honest-path dispute rate stays in the UMA-anchored ~1–2% band.
- **G-M3 (Phase 1 entry).** The constitution is ratified before the first
  dispute: conduct and removal rules for adjudicators and the demotion
  authority written and hash-pinned; the ladder's top rung names a
  concrete independent arbitrator; soulbound stake enforced in the staking
  contract (non-transferability mechanically checkable); the refusal of
  incoherence-only slashing encoded in the slashing conditions.
- **G-M4 (Phase 2).** Cap enforcement end-to-end: in the harness, a
  dispute market approaching the reliance bound stops accepting positions
  with no manual intervention, and a ladder reconfiguration that would
  breach the load condition on a live claim is refused.
- **G-M5 (Phase 2).** The wearing-down drill: a scripted unjust ruling
  followed by pool-funded appeal and reversal — challenger-population
  survival above the pre-registered threshold, refunds paid retroactively,
  the reversed ruling's supersession deriving cleanly (G-REC1's
  replay-invariance extended to reopening).
- **G-M6 (continuous).** The F9 audit: enumeration of every payment path
  in the mechanism shows nothing proportional to assertion volume;
  re-run on every mechanism change, failing loudly (the
  `phase0-simulation.md` §5 check, kept forever).

## Open problems

**The odds-weighted equilibrium** (work package: §8 + `phase0-simulation.md`
§5/§7/§8). The design's main risk and its paper, per `DESIGN.md` §11.2:
nobody has published an optimistic oracle with asserter-quoted odds, and
until G-M1 passes, every mechanism in §1 is a hypothesis with a fallback.

**The safe dispute-market size curve** (work package: §5 +
`phase0-simulation.md` adversary playbooks + `netting-and-reserves.md` §8).
V1's cap folds market open interest into aggregate reliance and fails
closed; how open interest may safely scale with ladder height — and whether
an information-value credit is ever safe — is unsolved, and a wrong curve
either re-opens §2's capture or strangles the one price-discovery channel
contested claims have.

**The batch exhaustion bound** (work package: §7 +
`records-and-anchoring.md` §5 + `phase0-simulation.md` §3). The statistical
inconsistency test that flips a root claim must distinguish asserted-wrong
from rotted-since-assertion under type-specific drift, or the pool is
slashed for entropy; the record fields are fixed first so batch-claim ids
don't churn when the test lands.

**Ruling supersession confluence** (work package: `records-and-anchoring.md`
§3, jointly here). Reopening means several rulings can stand on one dispute
after a union merge; the derivation's total order must be proven confluent
or stored status sneaks back in disguised as "the latest ruling" — and §4's
retroactive refunds inherit whatever order is chosen.

**The top rung's existence** (work package: §4 + `THREATS.md` T4). The
constitution demands an independent arbitrator whose integrity cost can
exceed aggregate open reliance; the deployed candidates are small — Kleros
totals low thousands of cases in eight years, largest claim ~£6,400 — so at
the scale F4 contemplates the required rung may simply not exist yet.
Fail-closed caps are the honest interim: reliance stops accumulating past
what the ladder can actually defend, which bounds the system's size until
the rung matures. Naming a concrete arbitrator is G-M3's problem; making
one exist at scale is nobody's yet, and this document says so.

**The systemic adjudicator-failure loading** (work package:
`netting-and-reserves.md` §7 + `phase0-simulation.md` §7, jointly here).
All claims sharing a final rung fail together if that rung is captured;
whether the explicit reserve loading for that shock dominates at realistic
ladder concentration — making adjudicator *diversity* a capital
requirement rather than a governance nicety — needs the capture scenarios,
and the answer feeds back into how many independent top rungs the
constitution must eventually name.

## What this document does not promise

**Certified ≠ true (F7), here most of all**: this document designs the
procedure behind the word "Certified," and the word still means only that
nobody found it profitable to dispute, under this adjudication procedure,
at these bond and subsidy levels (`DESIGN.md` §12). A bond prices the
forcing of a dispute, never the truth of a claim; stated confidence is a
stake schedule and a signal, not a probability, and must never be rendered
as one on any surface. The constitution constrains procedures, not
outcomes: soulbound stake and independence raise the cost of capturing the
top rung — they do not make it incorruptible, which is exactly why F4 caps
what any rung is ever asked to defend. Fail-closed caps trade liveness for
safety by design: a claim on which sales have stopped is the mechanism
working, and no consumer surface may dress it as an outage. The empirical
numbers here — UMA's rates and bonds, Polymarket's captures, Kleros's
volumes, Nexus's rules — are other systems' measurements of other systems'
risks, used as calibration anchors and disqualifying counterexamples,
never as results about factbond; Phase 0 exists to replace them with our
own. And a green Phase 0 certifies nothing about model risk: the go/no-go
can only kill, never prove (`phase0-simulation.md`), and the equilibrium
note of §8 will be a model of play, not a guarantee of it.
