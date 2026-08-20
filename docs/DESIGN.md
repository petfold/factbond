# factbond: Design

Status: **design draft, 2026-08-01. Nothing implemented, several things not
yet decided.** Distilled from the founding transcript
(`prediction-markets-transcript.pdf` in this directory); the literature
citations below are the transcript's. The go/no-go criterion is in §10; the
two hardest open problems are named in §11 so they land in the right work
package rather than being discovered mid-build.

Companion: `INTEGRATION.md` — how this composes with ontodag (claims,
proofs), recordstore/Swarm (evidence, roots), and loopmarket (the first
structured consumer).

**Update 2026-08-07.** A research sweep (optimistic-oracle empirics,
combinatorial netting, insurance, market integrity) turned several of this
draft's positions into work packages and revised three of them; the
revisions are flagged inline below at §3, §5, §6.4 and §6.5. **The §3,
§5.3 and §6.5 revisions were ratified by owner sign-off on 2026-08-20
(discussion agenda item 1) and are settled doctrine**; §6.4's note is a
design decision that was never contested. The work
packages live under `docs/plans/`: `mechanism-design.md` (odds-weighted
bonds, revised sizing, the adjudication constitution — the deepest
document), `insurance-products.md`, `netting-and-reserves.md`,
`evidence-policy.md` (§11.1's home), `records-and-anchoring.md`,
`phase0-simulation.md` (§10's Phase-0 instrument), `loopmarket-coupling.md`
and `THREATS.md`. Design invariants F1–F9 are stated across those docs;
F7 is §12 of this file, promoted from documentation discipline to
invariant.

## 1. The problem

Knowing what is actually true has always been hard; in the age of generated
content it is nearly impossible to know cheaply. The goal: make it possible
to attach economic truth-guarantees to **millions of ordinary statements** —
supermarket opening hours, Wikidata statements, OpenStreetMap attributes,
knowledge-graph edges — not the thousands of high-value events existing
prediction markets cover. Payoffs if it works: an incentive to *find* false
data in public knowledge bases, a funding mechanism for unpopular-but-correct
positions, and a reliability price on every fact anyone acts on.

## 2. Why prediction markets don't scale down

A standard on-chain market bet (conditional-token design) has three
unavoidable costs, each fatal at millions-of-facts scale:

1. **Full-notional collateral for the entire lifetime.** A $100 position on
   a 99% claim locks ~$100 of combined capital from bet to resolution.
   This is the **99-cent problem** (Daniel A. Nagy): paying 99 cents today
   to win 1 cent in a year is dominated by yield elsewhere, so rational
   capital never shows up on the "yes" side of near-certain facts. The
   transcript cites direct academic support: capital lock-up and settlement
   discounting explain much of the apparent long-horizon miscalibration in
   real markets (arXiv:2605.31431), consistent with the older
   favorite-longshot literature (Snowberg & Wolfers 2010; Ottaviani &
   Sørensen 2009) and recent Polymarket trade-tape analysis.
2. **A matched counterparty at bet time.** No disputant, no bet, no price,
   no information. Millions of markets on mundane facts would have zero
   traders each.
3. **Mandatory settlement.** Every market must be resolved by an oracle at
   expiry even if nobody ever disagreed — a million adjudications to
   confirm a million things nobody doubted.

Leverage and shorting machinery (perp-style margin) does not fix this and
actively hurts: path-dependent liquidation on thin, manipulable fact-markets
lets a manipulator liquidate honest verifiers before resolution. What
"shorting the NO at 1 cent" actually wants is **underwriting** (§5).

## 3. The primitive: the bonded assertion

In the optimistic pattern (UMA's optimistic oracle; token-curated
registries; Kleros Curate), one party posts a claim backed by a bond, a
challenge window opens, and undisputed claims resolve true by timeout.
Empirically ~98–99% of assertions settle undisputed, and small bonds secure
large open interest because **the bond collateralizes the honesty of the
process, not the payout**: it is sized to the cost of forcing and running a
dispute, not to the value riding on the claim.

| | prediction market | bonded assertion |
|---|---|---|
| capital committed | full notional, both sides | one bond, one side |
| when committed | at bet time | bond upfront; counterparty capital only on dispute |
| sized by | value at stake | cost of adjudication |
| counterparty | must be matched | the world, latently |
| settlement | always, per market | only on dispute (~1%) |
| output | continuous price | binary status: certified / contested |

The two mechanisms are ends of one spectrum: a prediction market is an
assertion system where every claim is disputed instantly and continuously;
a bonded assertion is a market whose price is pinned at ~1 and which only
activates when someone pays to cross. A dormant bonded claim *is* the
capital-efficient encoding of a near-1 market. The project framing is
therefore: **take the optimistic-assertion primitive and add back the
missing market properties where they earn their cost** — prices where
wanted, tradability, pooled underwriting, graph-structured netting — rather
than scaling markets down to trivial facts.

A bond is also what makes a standing offer *credible*: a capital-free
assertion would be a free option (post, watch, renege). The bonded
assertion is "the cheapest credible standing bet-offer."

**Update 2026-08-07 — the sizing doctrine is revised at the top of the
ladder (flagged: this amends a founding position).** "Sized to the cost of
adjudication, not the value riding on the claim" survives as the *floor*,
but 2025 practice falsified it as a ceiling: Polymarket/UMA captures
succeeded precisely because a ~$750 bond gated disputes on ~$7M of open
reliance — the last rung's integrity cost was decoupled from what rode on
the answer. The revised doctrine (full mechanism in
`docs/plans/mechanism-design.md`): bond = max(adjudication-cost floor,
k × settlement-weighted reliance/centrality of the claim); the dispute
ladder's *final* rung must have integrity cost ≥ the aggregate open
reliance on the claim; and per-claim insurance exposure is capped, with
sales stopping — failing closed — when the cap or the final-rung condition
would be breached (invariant F4). Cheap bonds still secure the ~99%
undisputed happy path; what changes is that reliance can no longer
accumulate past what the ladder can defend.

## 4. What the assertion side gives up, and how to recover it

**The price.** An unchallenged assertion says "nobody paid to dispute
this," which is not a probability. Two recovery mechanisms, both selective:

- the **underwriting premium** (§5): the pool's quoted insurance rate on a
  fact is a market-generated reliability price, produced without any bet
  occurring;
- **dispute-triggered markets**: a contested claim spins up a real
  two-sided market for the duration of the dispute window, so third parties
  with information can take positions, settled by the adjudicator's ruling.
  Price discovery is purchased only for the ~1% of claims worth its cost.
  (Design note: the dispute-market settles on the adjudicator's ruling, so
  the adjudicator's incentive-compatibility then carries trading stakes —
  size-cap dispute-markets in v1.)

**Odds-expressiveness.** A market bet on a 99% claim is naturally
asymmetric ($99 vs $1); a stock UMA dispute is bond-against-equal-bond
regardless of the claim's probability — challenging a 99.9% claim and a 60%
claim cost the same. The fix, and this design's most novel mechanism:
**odds-weighted bonds** — the asserter states a confidence, which sets the
dispute stake ratio (asserting at 99% means your bond faces the
challenger's at 99:1, pro-rated on bond size) and doubles as the system's
price signal. At that point an assertion literally *is* a limit order ("I
offer to bet at these odds, world"). Nobody has published an optimistic
oracle with asserter-quoted odds; its game theory is open (§11).

## 5. Information insurance: coupling verification to consumption

The deepest objection to bonded assertions at scale is the
**lazy-verification / marginal-challenger problem**: a bond only certifies
truth if someone would profitably catch a lie, and for a false statement
about a small shop's hours, nobody spends the effort — "unchallenged" stops
meaning "true" silently. UMA works because its claims are few, high-value,
and watched; millions of low-value claims are watched by nobody.

The answer (Peter's mechanism, and the design's center of gravity):
**sell insurance on facts at the point of consumption.** The person about
to act on a fact — drive to the shop — buys a cheap hedge ($1 to win $100)
against it being wrong. If the shop is closed, they are: (a) the discoverer
of the error at zero marginal cost (they're standing in front of it), (b)
holder of a private financial claim on reporting it, (c) present at the
right place and time to gather evidence. The public good — a corrected
entry for everyone — is produced as a byproduct of a private transaction.
Verification effort automatically allocates in proportion to how much each
fact actually *matters*; unconsumed facts stay uncertified, and that is a
feature (an unverified fact nobody acts on causes no harm).

Second elegance: **the premium is the epistemic signal.** If the pool
insures "the record is right about this shop" at 1 cent per dollar, that is
a market-priced 99% reliability claim — on every fact, without anyone
betting on most of them. Prior art: parametric micro-insurance (Etherisc's
on-chain flight-delay product); this is "parametric insurance on database
accuracy," which the transcript believes nobody has built.

The honest complications, in order of severity:

1. **The payout event and the database fact are different propositions.**
   The shop can be closed although the record is *correct* (illness, burst
   pipe) — and the record can be wrong in a way that didn't bite today. So
   there are **two products**: a *parametric convenience* hedge (pays on
   the experienced outcome; cheap, automatic, no epistemic claim) and a
   *verification bet* (pays on the recorded fact being wrong; triggers the
   correction machinery). The premium difference between them is itself
   informative — it prices "the world deviates from the record" separately
   from "the record is wrong."
2. **Evidence quality in the LLM era is the hardest engineering problem.**
   A timestamped photo of a closed shopfront was evidence in 2020 and is
   nearly worthless in 2026; a $100 payout is a $100 bounty on fabricating
   one. The dispute layer needs proof-of-physical-fact machinery
   (hardware-attested capture / C2PA, location attestations, independent
   witnesses, or Schelling-point adjudication discounting photographic
   evidence entirely). The cost lands only on *disputed* claims, but the
   honest-looking-fraudulent-claimant is the attack to model first — unlike
   oracle capture it scales as thousands of small independent attacks.
3. **Moral hazard** where the insured can influence the fact (a shop owner
   insuring against their own posted hours). Insurance has centuries of
   answers (insurable interest, exclusions), but they are identity-heavy;
   the pseudonymous minimum is: exclude claims where the buyer plausibly
   controls the source, and keep payouts small enough that arson-for-profit
   doesn't pay. This caps the mechanism at micro-insurance scale —
   acceptable for the use case. *(Update 2026-08-07, ratified by owner
   sign-off 2026-08-20:
   payout-smallness is demoted from primary defense to belt-and-braces. The
   primary structural defense is now the **indemnity principle**, invariant
   F3: a payout never exceeds the buyer's provable reliance on the fact.
   Where consumption is a loopmarket settlement, the settlement root proves
   reliance for free and the bound is exact; where reliance is unprovable —
   the agents-first wedge of §5.5 — payout caps remain the proxy, and
   out-of-settlement reliance measurement is a registered open problem.
   See `docs/plans/insurance-products.md`.)*
4. **Adverse selection is the pool's core pricing problem — and tolerable.**
   The $1-to-win-$100 buyer disproportionately knows something. Real
   insurers price this daily; it requires actuarial loss data per
   fact-type. The pool's loss experience then becomes a continuously
   updated **reliability audit of the knowledge base per attribute type**
   ("OSM opening hours are ~92% reliable") — plausibly the most valuable
   dataset the whole system generates.
5. **Friction and distribution.** Nobody consciously buys a $1 hedge before
   a grocery run; the product only works auto-attached at the point of
   consumption by an app — which is why **the natural first customers are
   AI agents**, not humans: an agent planning a delivery route consumes
   thousands of database facts, can price each fact's value to its plan,
   transacts at zero psychological cost, and files evidence-backed disputes
   automatically. "Machine-to-machine information insurance for agent
   workflows" is likely the wedge product. (See `INTEGRATION.md` §7 — this
   converges with the ontodag agents-first decision.)

## 6. The architecture: five layers, deliberately decoupled

1. **Claim layer — the semantic anchor.** A registry mapping `claimId` to a
   precise, versioned, machine-interpretable proposition. Holds no money;
   most underrated layer: essentially every real prediction-market dispute
   is about *wording*, not facts, so the claim schema is the primary
   defense. A claim carries: a **versioned** subject pointer (never
   "whatever the database says now"), a claim *type* from a small
   controlled vocabulary (`attribute-matches-source`,
   `attribute-matches-world`, `entity-exists`, …), temporal scope
   (asserted-as-of, validity window), and its resolution procedure
   (admissible evidence types, escalation path). v1 admits only
   machine-generated claims from templates over KB entries; free text is a
   v2 luxury. The §5.1 distinction is encoded here as the two claim types.
   *(ontodag is a candidate implementation of this layer for
   knowledge-graph claims — `INTEGRATION.md` §2.)*
2. **Assertion layer — the optimistic core.** Attaches bonded truth-status
   to claims: `(claimId, asserter, confidence, bondRef, livenessWindow,
   status)`. Two departures from stock UMA: **stated confidence** (sets the
   odds-weighted dispute ratio, doubles as the price signal) and bonds as
   **references into a shared pool** rather than per-assertion escrow.
   Undisputed assertions resolve to `Certified` by timeout at zero marginal
   cost. Main read API: for any claim, `status ∈ {Unasserted, Asserted,
   Contested, Certified, Refuted, Expired}` plus confidence and the capital
   behind it.
3. **Capital layer — two pools with different math; conflating them is the
   classic error.** The **bond pool** underwrites *process*: LPs deposit
   yield-bearing collateral (sDAI-style — the fix for the 99-cent problem
   applied at pool level: idle stake on true facts earns yield plus
   assertion fees, turning "irrational lock-up" into an underwriting
   business), and the pool programmatically backs assertions matching its
   policy. Its risk is "how often are our assertions successfully refuted"
   — rare, idiosyncratic, **except** the systemic adjudicator-failure term,
   which must be modeled as a correlated shock. The **payout reserve** is
   the insurance business: sells the consumer hedge, holds actuarial
   reserves sized by notional × loss rate × correlation loading
   (Cramér–Lundberg-style solvency, with per-fact-type loss tables it
   learns from its own claims history). v1: a single mutual with hard
   per-claim and per-cluster exposure caps; tranching later.
4. **Adjudication layer — pluggable, escalating.** Each claim's resolution
   procedure names an escalation path: automated evidence check (bot
   verifies a signed feed or C2PA provenance) → staked human panel
   (Kleros-style drawn jurors) → full vote as court of last resort. Cheap
   rungs handle volume; expensive rungs exist mainly as deterrence. This
   layer must be an *interface* — evidence norms differ per domain and
   evolve. Evidence itself goes to content-addressed decentralized storage
   with only hashes on-chain (Swarm's postage model fits evidence that must
   outlive a dispute — `INTEGRATION.md` §9). *(Update 2026-08-07 — flagged
   revision: the interface stays pluggable, but the top rung's structural
   properties become non-negotiable, learned from deployed-system failures:
   escalation ends at an **independent** arbitrator, never a vote of the
   system's own incentive token (UMA's DVM is the counterexample); the
   juror/stake base grows each round (Kleros' 2n+1) so p+ε bribery
   liability outruns the bond; adjudicator stake is soulbound —
   non-transferable, time-locked, retroactively slashable — so no bribe
   market can price capture; minority voters are never slashed for
   incoherence alone; rulings are reopenable on evidence that did not exist
   at ruling time; and arbitrator conduct + removal rules are written
   before the first dispute. The constitution: `docs/plans/
   mechanism-design.md`; the "full vote as court of last resort" wording
   above is superseded accordingly.)*
5. **Graph layer — the netting engine (deferred, designed-for).** The
   generalized-negRisk component: a constraint store of logical relations
   between claims (`A implies B`, `A excludes B`, `exactly-one-of {…}`) in
   a restricted language, plus a collateral calculator computing worst-case
   exposure over the feasible-outcome polytope instead of per-claim sums.
   Polymarket's NegRiskAdapter (mutual exclusion within one event, ~9.5×
   capital efficiency) is the embryonic live version; general combinatorial
   pricing is #P-hard (Chen–Fortnow–Lambert–Pennock–Wortman), tractability
   comes from restricting structure (graphical-model market makers —
   SciCast/DAGGRE; Dudík–Lahaie–Pennock constraint generation). **The open
   research question: a restricted claim/implication language for
   knowledge-base verification where worst-case collateral and price
   propagation are polynomial** — nobody has worked this fragment out.
   *(ontodag is a concrete candidate — `INTEGRATION.md` §6.)* Critically:
   layers 2–3 accept a *portfolio* collateral requirement from day one,
   even while v1's calculator is the trivial per-claim sum, so this layer
   slots in without migrating capital. *(Update 2026-08-07, ratified by
   owner sign-off 2026-08-20: the question above is **resolved in
   principle**. Over pure
   fits-within edges, price consistency is an O(E) difference-constraint
   pass on the order polytope (Stanley), and worst-case collateral is the
   maximum-weight closure of the subsumption DAG — one min-cut (Picard
   1976), polynomial, with the cut itself a compact optimality certificate.
   What flips the problem to #P-hard is admitting *global*
   mutual-exclusion or exhaustiveness axioms — so those stay out forever;
   disjointness is admitted only as local, bonded sibling partitions, each
   unlocking a NegRisk-style netting pocket. The remaining open item is
   empirical, not theoretical: the measured treewidth and cone-system VC
   width of the actually-seeded catalogue decide which pricing features
   ship. See `docs/plans/netting-and-reserves.md`.)*

## 7. The claim lifecycle, and the decisions inside it

```
Unasserted → Asserted → (liveness expires) → Certified → (validity expires) → Stale
                 ↓ dispute
             Contested → adjudication → Certified (challenger slashed)
                                      → Refuted  (asserter slashed,
                                                  correction event emitted)
```

- **Who asserts, and what stops spam?** Anyone; assertions cost a fee
  accruing to the bond pool. For the bulk case **the pool itself is the
  asserter**, auto-asserting over whole KB slices per policy ("all OSM
  opening_hours in Prague, confidence 0.93, bond 0.5 DAI each").
  Individual asserters matter at the margins: private knowledge asserting
  *against* the pool's blanket confidence, or claims the pool declines —
  and the pool's *refusal* to assert is itself signal.
- **What does a dispute unlock?** Minimal: odds-weighted bond match, single
  adjudication. Recommended: the dispute **opens a market** (§4) for the
  window's duration.
- **What happens on `Refuted`?** The contract can't fix Wikidata. It emits
  a correction event carrying the evidence hash and adjudicated truth — an
  oracle *output* that downstream consumers (KB-edit bots, overlay apps)
  subscribe to. Honesty point for all documentation: the system produces an
  **authenticated correction feed, not corrected databases**; the last mile
  is social.
- **What does `Certified` license?** The insurance product attaches here:
  hedges are sold only against `Asserted`/`Certified` claims, priced off
  the stated confidence plus the reserve's own loss tables. Key wiring: a
  paid-out insurance claim on an `attribute-matches-world` product
  **automatically funds and files a dispute** on the sibling
  `attribute-matches-source` claim when the evidence suggests the record
  (not just the day) was wrong. That coupling is what turns consumers into
  the verification workforce without them ever thinking about it.

## 8. Parameters (transcript priors, to be validated in simulation)

- **Bond size:** calibrated to adjudication cost at the cheapest escalation
  rung, not claim value — order of $1–10 for template claims.
- **Liveness window:** long for cold claims (days–weeks; nobody is
  watching, give the world time). The insurance coupling shortens
  *effective* discovery time to "next consumption event," which is the real
  safety mechanism.
- **Confidence granularity:** coarse buckets (0.9 / 0.97 / 0.99 / 0.999) —
  false precision invites gaming of the odds ratio.
- **Slashing split:** majority of the loser's stake to the winner, a slice
  burned or to the adjudication treasury (makes self-dispute laundering
  non-free).
- **Per-cluster exposure caps** in the reserve, derived from the constraint
  graph: claims sharing a source, region, or adjudicator are one cluster.

## 9. Explicitly not in v1

No continuous markets on uncontested claims. No leverage or liquidation
machinery anywhere. No free-text claims. No cross-chain anything. **No
token** — fees and yield are sufficient incentive plumbing to test the
mechanism, and adding a token before the loss tables exist just adds a
reflexive attack surface. *(Hardened 2026-08-07 from a v1 scoping to a
standing stance, and generalized as invariant F9: no volume-linked
emissions anywhere — assertion-mining would be the FCoin of facts, and
FCoin's fee-mining reached, with its copycats, ~40% of global reported
exchange volume before terminal insolvency inside 20 months. Revisiting the stance requires
modelling that scenario first; see `docs/plans/THREATS.md`.)*

## 10. Build order (de-risking fastest)

- **Phase 0 — simulation, not contracts.** Agent-based model (cadCAD or
  plain Python) of the assertion/dispute/insurance loop over a synthetic KB
  with planted errors. Deliverables: loss tables, and the answer to the
  **go/no-go question: at what dispute cost and consumption rate does
  planted-error half-life become acceptable?** If honest verification of a
  mundane false claim can't be made profitable, the system would look
  healthy while quietly certifying nothing — this is the criterion for the
  whole vision. *(Now fully specified — populations, parameter sweeps,
  adversary playbooks keyed to the threat register, the pre-registered
  acceptability threshold and its owner — in
  `docs/plans/phase0-simulation.md`. The same harness runs loopmarket's
  settlement-pricing shading experiments: one instrument, two consumers.)*
- **Phase 1** — layers 1–2 plus a naive bond pool on a testnet, against a
  frozen snapshot of one narrow domain (OSM `opening_hours` in one city:
  high error base rate, cheap physical verification, crisp evidence).
- **Phase 2** — the insurance product and the dispute-triggered mini-market.
- **Phase 3** — the graph layer, once real correlation data makes netting
  mean something.

## 11. The two hardest open problems (named so they land in a work package)

1. **The evidence-admissibility spec** for the automated adjudication rung:
   what counts as proof a shop was closed, in a world of generative
   imagery. A moving target — a versioned, per-domain *policy document*,
   not code. *(Work package assigned 2026-08-07:
   `docs/plans/evidence-policy.md` — evidence classes as versioned
   catalogue data with weights and revocation, per-domain hash-pinned
   policies, first 2026 rulings encoded.)*
2. **Odds-weighted bond game theory**: asymmetric bonds create a new
   strategic surface (assert at 0.999 to make challenges maximally
   expensive). Needs an equilibrium analysis before real stakes; nobody has
   published this — simultaneously the design's main risk and its paper.
   *(Work package assigned 2026-08-07: the game-theory section of
   `docs/plans/mechanism-design.md`, with the empirical half in
   `docs/plans/phase0-simulation.md`.)*

## 12. What the system actually certifies

Not truth. "Certified" means: *nobody found it profitable to dispute this,
under this adjudication procedure, at these bond and subsidy levels.* That
is genuinely more than most databases offer, and the "put your money where
your mouth is" mechanism is a real social technology — but prices are
signals under capital constraints and attack, not oracles. Every consumer
document, API status name, and pitch must preserve this distinction.

*(Promoted 2026-08-07 from documentation discipline to invariant **F7**,
binding every consumer surface — API field names, MCP annotations,
loopmarket receipts, pitches. Each plan document under `docs/plans/`
carries its own "what this document does not promise" section in the same
spirit.)*

## 13. Reading list (as collected in the transcript)

Optimistic oracles and curated lists: UMA OO design and empirical record;
Goldin's token-curated registry pattern; Kleros Curate. Capital efficiency:
"When Certainty Is Not Worth It" (arXiv:2605.31431); Snowberg & Wolfers
2010; Ottaviani & Sørensen 2009; Polymarket NegRiskAdapter. Combinatorial
markets: Hanson 2003/2007 (LMSR, combinatorial information markets);
Chen–Fortnow–Lambert–Pennock–Wortman (#P-hardness); Dudík–Lahaie–Pennock
(constraint generation); SciCast/DAGGRE graphical-model market maker. Peer
prediction / elicitation without verification: Miller–Resnick–Zeckhauser
2005; Prelec's Bayesian Truth Serum; Kong & Schoenebeck;
Srinivasan–Karger–Chen, "Self-Resolving Prediction Markets for Unverifiable
Outcomes" (EC 2025). Market making: Paradigm's pm-AMM and distribution
markets. Insurance: Cramér–Lundberg ruin theory; SPAN portfolio margining;
Nexus Mutual; Etherisc parametric flight-delay insurance. Evidence: C2PA
hardware-attested capture.
