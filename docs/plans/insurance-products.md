# factbond: insurance products

Status: design, 2026-08-07. Decided here: the two-product split and the
premium gap between them as a published signal; F3 indemnity scoping —
enforced where reliance is provable, payout-cap proxy where it is not;
pricing from per-fact-type loss tables over an uninformative cold-start
prior; the pseudonymous moral-hazard exclusion set with fail-closed
aggregate caps; the payout→dispute auto-coupling including appeal funding.
Open here: reliance measurement outside loopmarket clearing; insurable
interest without identity; interpretive basis risk on semantic edges;
manipulation of the published premium gap.

This document makes `DESIGN.md` §5 — the design's center of gravity —
concrete: the products the payout reserve sells, their pricing, and the
selection/hazard defenses that keep a pseudonymous micro-insurer solvent.
It consumes the bond and adjudication machinery of `mechanism-design.md`,
the capital model of `netting-and-reserves.md`, and the admissibility rules
of `evidence-policy.md`; its numbers stay symbolic until
`phase0-simulation.md` fixes them; its flagship instantiation is the
loopmarket coupling (`loopmarket-coupling.md`; loopmarket's
`docs/plans/P3-guarantee-coupling.md` from the other side). Threats T4, T5
and T9 are owned in depth by `THREATS.md` here.

## 1. Two products, two triggers, never conflated

The founding observation (`DESIGN.md` §5.1): the payout event and the
database fact are different propositions — the shop can be closed though
the record is correct, and the record can be wrong in a way that didn't
bite today. So there are two products, and pricing, disputes, and basis
risk all depend on never merging them (decided 2026-08, lands with
Phase 2):

| | parametric convenience hedge | verification bet |
|---|---|---|
| trigger | the experienced outcome (shop closed for *my* visit) | the record adjudicated wrong |
| epistemic claim | none | "the record is false" |
| settlement | automatic on a named feed or evidence class | insurer assessment, then the dispute ladder |
| dispute layer | none — all scrutiny moves to feed selection | full (`mechanism-design.md` §4) |
| corrects the record | never | always (§6) |
| precedent | Etherisc FlightDelay: Chainlink nodes pull FlightStats, payout auto-triggers at ≥45 min delay/cancellation, USDC policies on Gnosis Chain ([Etherisc/Chainlink announcement](https://medium.com/@etherisc/etherisc-launches-decentralized-flight-insurance-product-using-chainlink-data-feeds-a5e9ac5e0476), [fdd.etherisc.com](https://fdd.etherisc.com/apply)) | none found — "parametric insurance on database accuracy" appears unbuilt (`DESIGN.md` §5) |

The parametric hedge is deliberately dumb: no claim about the record, a
payout on a feed event, no dispute layer at all. The Etherisc lesson: this
works exactly where a canonical digital feed exists, and concentrates all
risk in the data pipeline (loss ratios not published, note). Hence the
2026 evidence ruling — **parametric-first wherever a canonical feed
exists** (`evidence-policy.md` §2) — and all integrity scrutiny collapses
to *which feeds are admissible triggers*: zkTLS proofs of authoritative
web records and operator-signed IoT events (parcel lockers) are the feed
classes with production trust roots. Fraud is low by construction because
the trigger sits outside the insured's control; a photo-based indemnity
study found no measurable fraud or moral hazard
([Kramer, CEGA](https://cega.berkeley.edu/wp-content/uploads/2020/03/Kramer_PacDev2020.pdf)).

The verification bet is the epistemic product: it pays only when the
record — not merely the day — was wrong, its payout is the entry point of
the correction machinery (§6), and its premium is the only one that prices
the record itself.

Rejected: one conflated product ("pays if you're inconvenienced OR the
record is wrong"). Friendlier and cheaper to quote, but it makes basis
risk latent instead of explicit — the buyer cannot know which proposition
they hold (§7) — and it destroys the most informative number the system
produces:

**The premium gap.** For the same fact, quote both premiums. The
convenience premium prices "the world deviates from the record today"; the
verification premium prices "the record is wrong." The gap isolates
world-volatility from record-quality: erratic hours with a correct record
show a wide convenience premium and a thin verification premium; a stale
record widens both. Published per fact-type and per source, the gap is a
market-priced distinction between noise and error that no knowledge base
has had — produced without a bet occurring on most facts.

## 2. Indemnity — F3, scoped honestly

Any market that pays on an adverse event creates a purse for causing it
(the assassination-politics generalization; T5). The structural defense is
centuries old, promoted to invariant **F3: indemnity — payout ≤ provable
reliance, payout-cap proxy where reliance is unprovable**. If the payout
can never exceed what the buyer demonstrably stood to lose from the fact
being wrong, then making it wrong (or corrupting its adjudication) can
never net a profit on the insurance leg — arson-for-profit dies at the
pricing desk, not in the courtroom.

The honest part is the scoping — reliance is only sometimes provable:

- **Provable: the loopmarket coupling.** A settling loop *relied on*
  specific catalogue edges — `satisfies` walked them, clearing
  re-verified every leg against pinned roots (loopmarket
  `ARCHITECTURE.md` §4, §8). The clearing root *is* a reliance proof:
  insured edge, relying legs, and cleared value are one auditable object,
  so clearing-attached insurance enforces F3 exactly — payout capped by
  the value of the cleared legs that provably pinned the edge — for free
  (decided 2026-08; ships per `loopmarket-coupling.md` sequencing:
  Phase-0 green *and* loopmarket's P2 record-format freeze).
- **Unprovable: the agents-first wedge.** The first customers (§8)
  consume facts *outside* any clearing — a route plan is not a
  committed loop. There the buyer's true reliance is private and the
  interim rule is the proxy: **hard per-policy payout caps at
  micro-insurance scale**, sized so arson cannot pay even when reliance
  is wholly fabricated. Measuring reliance outside clearing is a
  registered open problem (OP-1), not a solved one wearing a cap.

Rejected: unlimited notional with reinsurance layered later. The solvency
math needs finite per-fact notionals for the Lundberg machinery to apply
(`netting-and-reserves.md` §7), and every deployed mutual that survived
caps exposure structurally (Nexus: concentration cap ~20% of MCR per
listing — [MCR docs](https://docs.nexusmutual.io/protocol/capital-pool/mcr/)).

## 3. Pricing — the loss table is the audit

Premium = base loss rate (per fact-type, per source) × adverse-selection
load (§4) × capital load (reserve cost of the marginal policy, from the
margin engine — `netting-and-reserves.md` §3) + dispute provisioning.
Decided 2026-08, lands with Phase 2; loss tables begin as Phase-0 outputs.

- **Base loss rate** comes from per-fact-type loss tables the pool learns
  from its own claims history — experience rating, the one pricing input
  that cannot be talked into existence. This is `DESIGN.md` §5.4 made
  operational: the loss table doubles as a continuously updated
  **reliability audit of the knowledge base per attribute type** ("OSM
  opening hours are ~92% reliable"), plausibly the most valuable dataset
  the whole system generates. In the coupling, the same tables keyed per
  edge and per maker feed solver rate premia (`loopmarket-coupling.md` §2).
- **Cold start**: wide uninformative priors and premium floors. A young
  system's near-zero recorded losses mean *thin data, not safe facts* —
  the mirror image of eBay's reputation inflation, where costless positive
  signals converged on uselessness (0.3% negative ratings —
  [Filippas, Horton & Golden, "Reputation Inflation," EC'18](https://john-joseph-horton.com/papers/longrun.pdf)).
  Silence is priced as ignorance, never as quality.
- **Dispute provisioning** starts from the optimistic-oracle base rate —
  ~98–99% of assertions settle undisputed (`DESIGN.md` §3;
  [crypto.news](https://crypto.news/how-prediction-markets-resolve-uma-optimistic-oracle/)),
  so ~1–2% of policies are provisioned to touch the ladder — but the tail
  that matters is the **correlated bad-ruling shock**: a captured or
  conformist final rung rules wrongly across every claim it touches at
  once (Polymarket/UMA 2025; `mechanism-design.md` §2). That term is a
  reserve-level correlation loading, never a per-policy line item
  (`netting-and-reserves.md` §7), and it is why caps fail closed under F4
  (§5). Where a dispute-triggered market exists, its odds are an extra
  input — pm-AMM-style makers keep thin markets manipulation-resistant
  and withdraw liquidity near resolution
  ([Paradigm, Nov 2024](https://www.paradigm.xyz/2024/11/pm-amm));
  size-capped in v1 per `DESIGN.md` §4.

Rejected: pricing off the asserter's stated confidence alone. Confidence
is a *bond* parameter with its own strategic surface (odds-ratio gaming,
`mechanism-design.md` §1's open problem); as a premium it would let
asserters print cheap insurance on their own claims. Stated confidence
seeds the prior; loss experience and capital cost dominate as data arrives.

F7 wording discipline on every quote surface: the premium is **a price
under capital constraints and attack, not a probability**. A 1% premium
does not mean "99% true"; it means the pool, with its current reserves,
tables, caps, and threat model, carries this risk at this price.

## 4. Adverse selection — priced, not screened

The $1-to-win-$100 buyer disproportionately knows something (`DESIGN.md`
§5.4). The classical instinct — screen the informed buyer out — is exactly
wrong here, and its rejection is a design principle: **the informed buyer
is the product working.** A consumer who suspects the record and buys the
verification bet is a verification event routed through the price system;
refusing them re-creates the lazy-verification hole the mechanism exists
to fill. So selection is priced: the load is experience-rated per
fact-type (the loss table already measures realized selection — prior loss
rate vs loss rate among *sold* policies), and abnormal demand
concentration on one fact is a tripwire, not a rejection — it raises the
quote, tightens the per-fact cap, and flags the fact for the pool's own
pre-emptive dispute, which is cheaper than selling mispriced policies on
it.

## 5. Moral hazard under pseudonymity

Identity-based insurable interest (KYC, named beneficiaries) is the
centuries-old answer and is rejected: it kills the pseudonymous
machine-to-machine wedge and imports an identity infrastructure factbond
does not otherwise need. The pseudonymous minimum (`DESIGN.md` §5.3),
accepted with its consequence — the mechanism caps at micro-insurance
scale:

1. **Controls-source exclusion.** No payout where the buyer plausibly
   controls the insured fact's source (a shop owner insuring against
   their own posted hours). "Plausibly controls" is an admissibility
   judgment, living as data in the per-domain policy documents
   (`evidence-policy.md` §3), not as code.
2. **Micro-scale payout caps** (§2's proxy), so arson cannot pay even
   where the exclusion is evaded.
3. **Per-fact and per-cluster aggregate caps, failing closed.** The
   residual is aggregation: many small, individually legit-looking
   policies across sybil buyers on one fact the attacker can break (T2 ×
   T5). Defense is invariant **F4: reliance-bounded adjudication — final
   rung integrity cost ≥ aggregate open reliance, per-claim insurance
   caps fail closed**: when open interest on a fact approaches its final
   rung's capture cost, *the pool stops selling on that fact* — no
   override, no manual step. Cluster definitions (shared source, region,
   adjudicator) come from the constraint graph
   (`netting-and-reserves.md` §7; `DESIGN.md` §8).

Classic claims fraud is thereby displaced into adjudication manipulation
and evidence fabrication — where the design wants it, because those are
surfaces `mechanism-design.md` and `evidence-policy.md` defend with bonds,
ladders, and admissibility classes rather than identity.

## 6. The payout→dispute coupling — funding the correction machinery

The wiring that turns consumers into the verification workforce
(`DESIGN.md` §7; decided 2026-08, lands with Phase 2):

1. A verification-bet claim is assessed and paid by the reserve on its
   own evidence policy — the fast path; the buyer is made whole without
   waiting on the ladder.
2. The paid-out bet **auto-funds and files the sibling
   `attribute-matches-source` dispute** against the standing bonded
   assertion on the record (`DESIGN.md` §7's sibling-claim wiring; exact
   claim-type routing is pinned in `records-and-anchoring.md` §1). The
   structural half is nearly free under **F8: structural (matches-source)
   claims settle by certificate/inclusion-proof only**; only the
   matches-world half climbs the expensive rungs.
3. The pool — a repeat player with a booked loss and a slash claim to
   recover — **pays the appeal fees** up the ladder; Kleros-style
   crowdfunded appeals are the deployed precedent for third-party appeal
   funding ([Kleros yellowpaper](https://kleros.io/yellowpaper.pdf)).

Step 3 is the structural answer to the observed **wearing-down attack**:
honest disputers lose bonds to a conformist or captured tribunal, learn
not to dispute, and the system chills — the 2025 Zelenskyy-suit market
resolved wrongly twice and slashed the honest side both times
([Forbes](https://www.forbes.com/sites/boazsobrado/2025/07/07/the-president-wears-no-suit-polymarkets-160-million-problem/),
[Decrypt](https://decrypt.co/329210/polymarket-rules-no-237m-bet-zelenskyys)).
Under this coupling no individual ever posts a dispute bond from their own
pocket: corrections are prosecuted by a capitalized repeat player with
aggregated stakes — the one party the attack cannot exhaust one bond at a
time. The public good is a byproduct of a claim the pool already paid.

## 7. Basis risk — the #1 uptake killer, named

The index-insurance literature is unambiguous: basis risk (the index pays
when you had no loss, or fails to pay when you did) — not fraud, not
price — is the dominant cause of persistently low uptake at commercial
premiums ([ScienceDirect reconsideration](https://www.sciencedirect.com/science/article/pii/S0304387822000505);
[CCAFS scaling report](https://cgspace.cgiar.org/bitstreams/76aa1b44-573f-44d7-b7d0-4314c2d7a278/download)).
A design that ignores it ships a product nobody renews.

factbond's genuine advantage over weather indices: **certificates settle
the structural half.** Whether the record at root R says X, and whether a
loop's legs pinned edge E, are machine-checkable propositions (F8) — index
and insured object coincide by construction on that half, which no
rainfall index ever achieved. The §1 split is the other half: it converts
latent basis risk into an explicit, separately priced choice — the buyer
who wants "pay if my day goes wrong" holds the hedge, the buyer who wants
"pay if the record lied" holds the bet, and neither discovers at claim
time that they held the other product.

The residual is irreducible, registered as **T9 (basis-risk disputes,
primary owner: `THREATS.md` here)**: *semantic* edges — "suitable-for-X",
quality and fitness categories — keep interpretive basis risk no
certificate can close, because the dispute is about meaning, not
structure. Defenses: hash-pinned per-domain resolution criteria
(`evidence-policy.md` §3 — the policy text is the contract; ambiguity is
empirically the cheapest attack in every deployed system) and honest
scoping — verification bets on heavily interpretive edges carry wider
premiums or are declined, the refusal to quote itself published signal.

## 8. Distribution — auto-attached, agents first

Nobody consciously buys a $1 hedge before a grocery run; the product only
exists auto-attached at the point of consumption (`DESIGN.md` §5.5). Two
channels, in order:

- **AI agents (the wedge).** An agent planning a delivery route consumes
  thousands of database facts, prices each fact's value to its plan,
  transacts at zero psychological cost, and files evidence-backed
  disputes automatically. Machine-to-machine information insurance is the
  first product; it runs entirely on the §2 payout-cap proxy. The
  read-side slot is reserved: ontodag's answer shape carries a namespaced
  annotations map, `annotations.factbond = {status, confidence, capital}`
  the worked example — "how much is this answer insured for?" becomes a
  field, not a research project (`loopmarket-coupling.md` §2;
  `INTEGRATION.md` §7) (decided 2026-08, lands with Phase 2).
- **Clearing auto-attach (the flagship).** loopmarket clearing
  attaches verification bets on the witness edges each loop relied on;
  payouts are indemnity-exact (§2), and every paid claim audits the
  shared catalogue (§6). Gated on Phase-0 green and loopmarket's P2
  format freeze (`loopmarket-coupling.md` §1).

Human-facing apps come last, wrapping the same machinery: a UX project,
not a mechanism-design one, and nothing here depends on them.

## Gates

- **G-I1 (Phase 0, pre-registered before first run).** Across the swept
  grid: arson ROI < 0 under every T5 playbook *and* honest consumer-claim
  ROI > 0 on planted errors (thresholds and owner:
  `phase0-simulation.md` §1). Fail ⇒ the product as specced is a no-go,
  not a parameter hunt.
- **G-I2 (Phase 0).** Loss-table informativeness: premiums ordered by the
  learned tables must strictly beat a flat uninformative premium at
  ranking held-out planted errors. Fail ⇒ "premium = signal" is
  unsupported and per-fact premiums are not published.
- **G-I3 (Phase 2 entry).** The §6 pipeline end-to-end on the Phase-1
  testnet domain: paid verification bets auto-file their sibling
  disputes; appeal funding survives one full ladder escalation without
  exceeding the dispute-provisioning load.
- **G-I4 (Phase 2).** Caps fail closed under test: a simulated breach of
  a per-fact aggregate cap or the F4 final-rung condition halts new sales
  on that fact with no manual intervention.
- **G-I5 (clearing-attached variant).** Ships only after Phase-0 green
  *and* loopmarket P2 record-format freeze (`loopmarket-coupling.md`);
  until then the only live product is the capped agents-first wedge.

## Open problems

- **OP-1 Out-of-clearing reliance measurement.** F3 is enforceable only
  where reliance is provable; the wedge runs on payout caps as a proxy.
  Candidate directions — declared-reliance commitments at purchase,
  plan-hash escrows, post-hoc reliance attestation — all either invite
  fabrication or reintroduce identity. Until solved, the wedge stays
  micro-capped by construction. Work package: the Phase-2 product spec
  here, jointly with `loopmarket-coupling.md` (owner of the provable case).
- **OP-2 Insurable interest without identity.** The controls-source
  exclusion is a heuristic, not a theory: under pseudonymity, "who can
  influence this fact" is estimated from structure (source ownership,
  edit history, clearing adjacency), never known. A principled
  pseudonymous insurable-interest test — or a proof that caps are the
  best attainable — is open. Work package: `THREATS.md` T5 residuals plus
  the Phase-2 spec here.
- **OP-3 Interpretive basis risk on semantic edges (T9).** Which edge
  classes are quotable at all, and at what premium widening, is empirical
  and must be answered domain-by-domain. Work package:
  `evidence-policy.md` §3/§6, with T9 tripwire metrics in `THREATS.md`.
- **OP-4 The premium gap as a manipulable surface.** Once published, the
  gap (§1) is a signal someone will trade against: buying convenience
  hedges to widen the printed world-volatility estimate, or suppressing
  verification demand so a bad record looks merely noisy. Whether caps
  plus experience rating bound this cheaply is untested. Work package:
  `phase0-simulation.md` adversary playbooks.
- **OP-5 Loss-table cold start.** How many observed consumption events
  per fact-type before the table beats the flat prior (G-I2), and what
  floor prevents underpricing meanwhile, are numbers only the simulation
  can fix. Work package: `phase0-simulation.md` §1 secondary outputs.

## What this document does not promise

**Certified ≠ true** (F7), on this surface as on every other: a sold
policy, a quoted premium, and a paid claim are statements about what the
pool would carry at a price — under its capital constraints, loss tables,
caps, and modeled attacks — never statements of fact about the world. The
premium is not a probability and must never be rendered as one in any
consumer surface or API. The loss tables measure *adjudicated,
dispute-adjusted* experience, not ground truth: a captured rung poisons
the audit exactly as it poisons payouts. Payout caps are a proxy for
indemnity, not indemnity — the wedge product bounds arson, it does not
eliminate it. The correction machinery emits an authenticated correction
feed, not corrected databases; the last mile stays social (`DESIGN.md`
§7). And a green Phase-0 simulation certifies the mechanism against the
adversaries and parameters *we thought to model* — it certifies nothing
about model risk, which is carried, not solved.
