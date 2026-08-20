# factbond: netting and reserves

Status: design, 2026-08-07. Decided here: the graph layer's claim fragment
(subsumption plus exact dimensions — closing `DESIGN.md` §6.5's "open research
question", ratified by owner sign-off 2026-08-20); consistency as an O(E)
difference-constraint
pass; the Picard min-cut margin engine with the cut as its certificate;
disjointness admitted only as local bonded sibling partitions; polarity-aware
cross-margin rules; complexity-priced structural axioms; the v0 reserve
formula inside a Nexus-style collapsed capital model with per-fact notional
caps; dispute odds priced by pm-AMM machinery, never raw asserter confidence.
Open here: the two catalogue measurements gating every pricing feature, the
systemic adjudicator-failure loading, cold-start loading, and the
partition-refutation unwind.

This document makes `DESIGN.md` §6.5 (the graph layer) and §6.3 (the capital
layer) concrete: what the netting engine computes, on what fragment, with what
capital behind it, and which measurements decide what ships. Companions:
`mechanism-design.md` (bond sizing; the adjudication constitution the reserve
leans on), `insurance-products.md` (what the payout reserve backs),
`phase0-simulation.md` (loss tables, pre-registered thresholds), `THREATS.md`
(T4, T5, T6, T9), `loopmarket-coupling.md` (the first structured consumer of
netted exposure), and factbond's `INTEGRATION.md` §6 (the ontodag fragment all
of this stands on).

## 1. The fragment, declared (revises DESIGN.md §6.5)

§6.5 asked for "a restricted claim/implication language for knowledge-base
verification where worst-case collateral and price propagation are polynomial"
and called it the open research question. The research resolves it in
principle, and this document commits to the answer — §6.5's framing is revised
from *open* to *resolved-in-principle, empirically gated* (ratified by
owner sign-off 2026-08-20).
The bridge claim, stated once in `INTEGRATION.md` §6 and adopted verbatim:
**subsumption-plus-exact-dimensions is a tractable, canonically-identified,
monotone claim/implication fragment for knowledge-base collateral netting.**

Why this fragment. The consistent worlds of a subsumption DAG (A⊑B forces
"A true ⇒ B true") are exactly the upward-closed 0/1 assignments — the up-sets
of the poset — and Stanley's order polytope (Stanley 1986) has as vertices
precisely their indicator vectors, turning every question below into linear
programming over a polytope whose facets are single-variable bounds and
pairwise differences. Hardness in combinatorial markets comes from the
*language*, not the market size: LMSR pricing is #P-hard even for bets on
conjunctions of two events (Chen–Fortnow–Lambert–Pennock–Wortman, EC 2008,
arXiv:0802.1362). Polymarket's mutual-exclusion world is the hard fragment;
pure implication is the easy one. factbond sits in the easy fragment by luck
of ontology design — ontodag's one primitive *is* the implication order — and
the discipline this document imposes is refusing to let hard constraints creep
in globally (§5).

The fragment is also the only one that survives merge: ontodag entailments
only grow under union merge (`is_below` is monotone), so new implication edges
shrink the set of consistent worlds and the worst case over them can only fall
— margin computed at a pinned root stays sound at every merged descendant of
that root (`INTEGRATION.md` §6). Anything non-monotone — negation, closed-world
exhaustiveness, global exclusion — voids this property: the second,
independent reason §5 refuses it.

## 2. Consistency is O(E), never a solver (decided 2026-08, lands with Phase 3)

A price (or odds) vector over facts is arbitrage-free with respect to pure
implication **iff** 0 ≤ p ≤ 1 everywhere and p_A ≤ p_B along every ⊑ edge.
These are difference constraints: consistency checking, tightest-arbitrage
extraction, and projection back onto the polytope are all shortest-path-family
computations, O(E) per pass — no integer program, no sampling, no #P anywhere.
The pass runs on every quote the pool publishes and every pocket it opens.

The empirical case for native consistency: "Unravelling the Probabilistic
Forest" (AFT 2025, arXiv:2508.03474) mined 86M Polymarket bids and found ≥$40M
of realized arbitrage extracted from logical-consistency violations — 62% of
its LLM-detected dependencies failing to yield profit only through execution
barriers.
That is the measured cost of listing logically related facts as independent
markets. factbond's facts arrive with their relations already canonical;
leaving consistency to arbitrageurs would re-create Polymarket's forest on a
substrate that knows better.

## 3. The margin engine: one min-cut, with a certificate (decided 2026-08, lands with Phase 3)

The collateral question for a book of fact positions (signed worst-case
payouts per fact, from sold YES/NO fact-insurance and matched disputes) is:
maximize the pool's loss over consistent worlds. Maximizing a linear function
over the order polytope's vertices is the **maximum-weight closure problem**,
one min-cut/max-flow by Picard 1976 (the project-selection construction:
source arcs to positive-weight nodes, negative-weight nodes to sink, infinite
arcs along implications). One max-flow on |V| facts and |E| edges —
polynomial, exact, deterministic.

Two properties make this the engine rather than merely an algorithm. **The
cut is the certificate**: by LP duality the min-cut proves its own optimality,
and the cut is small — a set of arcs, not a computation trace — so a contract
or counterparty verifies the margin figure without re-running the flow (the
doctrine of F8, "structural (matches-source) claims settle by
certificate/inclusion-proof only", and of ontodag's `is_below` certificates).
And **it slots into the interface DESIGN.md reserved**: §6.5 requires layers
2–3 to accept a *portfolio* collateral requirement from day one, even while
v1's calculator is the per-claim sum — the min-cut replaces the calculator
without migrating capital. The TradFi contrast: SPAN margining (CME) is
precomputed loss vectors, linear aggregation, and a max over 16 scenarios
targeting ~99% one-day VaR — an approximation by scenario sampling. In the
pure-implication fragment the exact worst case is computable: SPAN's
architecture with the scenario array replaced by the min-cut's worst world.

## 4. Polarity-aware cross-margin, stated exactly

A subsumption edge A ⊑ B gives the pointwise dominance YES_A ≤ YES_B in every
consistent world. The rules follow mechanically and are committed as stated:

- **Long YES(general) fully collateralizes short YES(specific).** Net payout
  YES_B − YES_A ∈ {0, 1}, never negative: zero additional margin.
- **Long NO(specific) fully collateralizes short NO(general).** NO_A − NO_B =
  YES_B − YES_A ∈ {0, 1}: zero additional margin. Relief flows *down* the DAG
  for YES exposure and *up* for NO exposure.
- **Reverse polarities get zero relief.** Long YES(specific) against short
  YES(general) pays YES_A − YES_B ∈ {−1, 0}: full unit margin. No partial
  credit — partial credit is where hidden model assumptions enter.
- **Conversions only run from dominating to dominated.** Burning YES_B to mint
  YES_A destroys value and is safe; the reverse mints value and is forbidden.
  The value-preserving primitive is not conversion but cross-margining itself:
  the portfolio's worst case over consistent worlds (§3), not per-market sums.

## 5. Disjointness policy: local bonded partitions, never global axioms

**No global mutual-exclusion or exhaustiveness axioms enter the pricing layer,
ever.** Any constraint mixing polarities — sibling exclusion (x_A + x_B ≤ 1),
exhaustiveness (Σ children ≥ parent), negation, securities on conjunctions of
incomparable nodes — steps out of the order polytope into the general marginal
polytope: membership NP-hard, pricing #P-hard (CFLPW). The pricing layer
refuses them, fail closed. This is ontodag's own wall arriving from the
economic side — disjointness assertions merge as ordinary claims, enforcement
is local policy, `get(A, B)` non-empty *is* the violation check; factbond is
the second independent consumer of that wall shape (`INTEGRATION.md` §6).

What is admitted instead (decided 2026-08, lands with Phase 3): **the local
bonded sibling partition.** "These children partition the parent" — mutually
exclusive and exhaustive, conditional on the parent — is itself a bondable
factbond assertion: a claim subject like any other (F2: "bonds attach to claim
subjects, never edges"), asserted at a confidence, priced, disputable,
slashable. While the partition certificate stands, it unlocks Polymarket's
NegRisk convert *verbatim* inside that sibling set: burn 1 NO on each of k
chosen siblings → receive 1 YES on every sibling outside the set plus (k−1)
units of collateral, conditional on the parent (Polymarket NegRiskAdapter; the
identity is Σ YES = 1 in every world). Practitioner-measured effect on
multi-outcome markets: **~9.5× capital efficiency** versus raw positions —
the direct capital value of a bonded catalogue claim, and the cleanest bridge
between factbond assertions and money anyone has to show. If the partition
assertion is `Refuted`, the pocket collapses: positions re-margin at §4's
pure-implication rules, fail closed, before any new exposure is written; the
unwind path is a registered open problem below.

Escape hatches beyond partitions, ranked, each behind §Gates: (1) local
tree-structured partitions keep the constraint graph a hypertree, so
junction-tree pricing stays polynomial in the largest sibling set (the
SciCast/DAGGRE graphical-model market maker, JAIR; ~500–1,200 live questions
in production); (2) bounded treewidth overall, with structure-adding edits
priced (§6); (3) constraint generation with an integer-program separation
oracle for the rare global query (Dudík–Lahaie–Pennock, EC 2012;
Kroer–Dudík–Lahaie–Balakrishnan, EC 2016) — arbitrage-bounded rather than
arbitrage-free until constraints accumulate; (4) bounded-VC cone-event
families for any future AMM (§8).

## 6. Complexity pricing: authors pay for structure (decided 2026-08, lands with Phase 3)

SciCast allowed edits that grew the dependency structure but **priced the edit
by the computational load it induced** — users paid for the complexity they
created, in production. factbond adopts the rule: an axiom that increases the
constraint graph's treewidth (a partition, a cross-link between pockets) is
bonded at a premium tied to the netting and pricing cost it imposes on
everyone else. Flat facts stay cheap; structure costs. This is simultaneously
the tractability defense (the island stays an island under careless or
adversarial authorship) and an economic defense against T6
catalogue-governance capture (`THREATS.md`): structure is where capture
concentrates, so structure is where the bonds concentrate.

## 7. Reserves v0 (decided 2026-08, lands with Phase 2; Phase 1's naive pool uses per-claim sums)

The two-pool split, because conflating them is the classic error (`DESIGN.md`
§6.3): the **bond pool** underwrites *process* — rare, idiosyncratic
successful refutations plus one correlated adjudicator-failure term; the
**payout reserve** underwrites *claims* — the insurance business, sized
actuarially. This section is the payout reserve's model; bond-pool sizing
doctrine lives in `mechanism-design.md`.

**The v0 formula:**

    u = max( worst correlated claim cluster , ln(1/ε) / R )

- **The cluster term is structural correlation, computed rather than
  assumed.** Claims on a subsumption DAG are not independent: if an edge's
  claim is adjudicated false, every insured fact whose derivation used it
  fails together. Worst-case cluster = maximum insured exposure over any
  *logically consistent* failure set = max-weight closure of the DAG weighted
  by insured exposure — one Picard min-cut per candidate root edge (§3).
  Clusters are additionally defined by shared source, region, and adjudicator
  (`DESIGN.md` §8): those failure modes correlate outside the DAG's logic.
- **The Lundberg term covers the residual independent flow.** Cramér–Lundberg:
  with claim rate λ, claim-size MGF M_X, premium rate c = (1+θ)λμ, ruin
  probability satisfies ψ(u) ≤ e^(−Ru), where R > 0 solves c·r = λ(M_X(r) − 1);
  the reserve rule for target ruin probability ε is u ≥ ln(1/ε)/R. The anchor
  for ε is Solvency II's 99.5% one-year survival (a 1-in-200-year event).

**Per-fact notional caps are load-bearing.** The Lundberg bound dies two
deaths: heavy tails (no MGF → no R → the exponential bound is simply invalid;
only subexponential asymptotics remain) and correlation (Poisson independence
is the whole assumption). The formula's arms answer the deaths: hard per-fact
insured notional caps *force* the tail to be bounded — finite MGF by
construction, the model's assumption enforced rather than hoped for — and the
closure term handles the correlation the DAG can express. The caps do double
duty: they are the arson bound (`DESIGN.md` §5.3 — payouts small enough that
arson-for-profit doesn't pay; T5 in `THREATS.md`) and the per-claim arm of F4:
"reliance-bounded adjudication — final rung integrity cost ≥ aggregate open
reliance, per-claim insurance caps fail closed." At the cap the pool stops
selling — it does not re-price and carry on.

**The Nexus wrapper.** A full Solvency-II internal model is not implementable
on-chain; Nexus Mutual collapsed theirs to MCR = Total Active Cover / 4.8,
calibrated offline to the 99.5% level, with a global capacity factor (1 NXM
staked → 2 NXM cover capacity) and a **concentration cap of ~20% of MCR per
single listing**. factbond v0 adopts the shape: gearing on active insured
amount (Nexus's 4.8 as a prior, re-calibrated by Phase-0 loss tables before
real stakes — G4), a capacity factor on stake, and the concentration cap
applied per catalogue subtree/root edge, with subtree exposure read directly
off the closure computation. Crude gearing plus structural caps beats an
unimplementable internal model; the caps admit that the model is crude.

**The systemic term the min-cut cannot see.** Adjudicator failure respects no
DAG structure: every claim whose escalation path ends at the same final rung
fails together if that rung is captured (T4). It enters the reserve as an
explicit cluster — all open exposure sharing a final rung — with a loading
whose size is a registered open problem below. The upstream defense is
`mechanism-design.md`'s final-rung condition (F4); the reserve survives the
residual.

## 8. Pricing instruments (dispute odds land with Phase 2; cone AMMs with Phase 3, behind the gates)

- **Dispute odds by pm-AMM, never raw confidence.** Stated confidence is a
  gameable input (it sets the asserter's own dispute ratio); the odds that
  size bond escalation and insurance premia must be market-refined.
  Dispute-triggered markets run on pm-AMM / distribution-market machinery
  (Paradigm, Nov 2024 / Dec 2024): the constant-L2-norm density invariant
  collapses to a few scalars for Normal/lognormal families and runs cheaply
  on-chain; pm-AMM's dynamic variant shrinks liquidity as resolution nears,
  holding loss-versus-rebalancing constant — the anti-manipulation shape a
  thin dispute market needs. Size-capped in v1, settled by the adjudicator's
  ruling (`DESIGN.md` §4: the cap bounds the incentive load the ruling
  carries).
- **LMSR only over descendant-cone events, only if the VC gate opens.**
  Sublinear AMM operations over a combinatorial security family exist iff its
  set system has bounded VC dimension (Hossain–Wang–Yu, SODA 2025,
  arXiv:2411.08972); descendant cones of a DAG of bounded width have low VC
  dimension — a property of *our actual catalogue*, not of DAGs in general,
  hence G1. Worst-case subsidy stays the LMSR bound b·ln N.
- **Cross-fact joint bets by parametric joint models, never outcome
  enumeration.** ParlayMarket (Rana–Nadkarni–Moshrefi–Viswanath,
  arXiv:2603.22596) prices conjunction contracts in one pool via a parametric
  joint updated by trades, market-maker loss at most quadratic in the number
  of base markets — the pattern for any "this derivation chain holds" bet.

## 9. Soundness at a pinned root

Every netting and margin figure above is computed against a pinned pair of
roots (knowledge root, provenance root) and stamped with them. Monotonicity
(§1) makes the figure conservative at every merged descendant of the pinned
knowledge root — new edges only shrink the feasible worlds, so a computed
margin remains an upper bound. The one deliberate exception is the partition
pocket: its extra relief hangs on a live factbond assertion, not on canonical
knowledge (F6: "factbond state never enters canonical knowledge" — a partition
claim is priced and slashable precisely because it is *not* graph structure),
so pocket relief is revocable and re-margining on refutation is fail-closed
(§5). Everything else only gets safer as the catalogue grows.

## Gates

Numeric thresholds for G1/G2 are pre-registered in `phase0-simulation.md`
*before* the measurements run — the planted-error-half-life discipline: a
threshold chosen after seeing the number is not a gate.

- **G1 — cone VC/width measurement (gates cone-event AMMs, Phase 3).** Measure
  the VC dimension (equivalently the width bound driving it) of the
  descendant-cone set system on the actually-seeded catalogue — the corpus
  loopmarket's `docs/plans/catalogue-bootstrap.md` imports (GS1 GPC, UNSPSC,
  Google Product Taxonomy, Wikidata), per release. Decision rule: bounded by
  the pre-registered constant across releases and growth → cone-event AMMs
  admissible; growing with catalogue size → that island is closed, the pool
  prices by min-cut margining and difference constraints only, no cone AMM
  ships.
- **G2 — post-partition treewidth (gates pocket pricing, Phase 3).** Measure
  the treewidth of the pricing constraint graph after local sibling partitions
  on the same catalogue; junction-tree pricing is exponential in the largest
  clique, so the measured distribution of partition sizes sets the pocket-size
  cap. Decision rule: partitions within the cap price by junction tree; above
  it, refused or admitted only with §6 complexity premia plus per-claim-sum
  margining inside the oversized pocket (correct, merely capital-inefficient —
  the failure mode is extra margin, never mispricing).
- **G3 — netting under simulation (gates the min-cut engine, Phase 3 entry).**
  In the Phase-0 harness, planted-error and adversary playbooks
  (`phase0-simulation.md`; `THREATS.md` T5 arson scenarios) run with netting
  enabled and disabled; the engine ships only if enabled netting does not
  degrade pool survival versus per-claim sums at equal capital. Netting that
  buys efficiency by hiding correlated ruin fails by construction.
- **G4 — gearing calibration (gates Phase 2 real stakes).** Nexus's 4.8 is
  calibrated to Nexus's book. Before the reserve sells under real stakes,
  Phase-0 loss tables must show ≥99.5% one-year survival at the chosen gearing
  under the full adversary playbook; if 4.8 fails, tighten until it passes.
  The gearing is a simulation output, not an adopted constant.
- **G5 — certificate verification cost (gates any on-chain margin check).**
  The min-cut certificate must verify within an acceptable gas envelope on
  Gnosis before any contract relies on it; unbenchmarked today. Benchmark
  owned by `records-and-anchoring.md`.

## Open problems

**The two catalogue numbers** (work package: G1/G2; corpus from loopmarket's
`docs/plans/catalogue-bootstrap.md`). Everything in §8 is conditional on
measurements nobody has run: the VC dimension of descendant-cone set systems
and the post-partition treewidth of the real seeded catalogue. Theory says
bounded width ⇒ low VC and local partitions ⇒ hypertree; whether the imported
taxonomies have those shapes is an empirical fact about GS1 and Wikidata.

**The systemic adjudicator-failure loading** (work package:
`mechanism-design.md` + `phase0-simulation.md`). The min-cut cluster captures
DAG-structural correlation but not "all claims sharing a final rung fail
together." How large the explicit loading must be — and whether it dominates
the reserve at realistic ladder concentration, which would make adjudicator
diversity a capital requirement rather than a governance nicety — needs the
simulation's capture scenarios.

**Cold-start pricing under adverse selection** (work package:
`insurance-products.md` + `phase0-simulation.md`). With empty loss tables and
adversely-selected buyers, Lundberg with guessed λ and M_X is only a starting
bracket; the safety loading θ and premium floors that keep the pool survivable
while loss data accumulates are unknown.

**The partition-refutation unwind** (work package: this document, Phase 3;
threat surface in `THREATS.md` T5/T9). When a partition certificate is slashed
while pocket positions are open, §5 says re-margin fail-closed — but the order
of operations, the grace window, and who bears the margin call mid-flight are
undesigned. An attacker who can force a partition dispute at a chosen moment
holds a timing option against every position in the pocket; the unwind must
make that option worthless.

## What this document does not promise

**Consistency is not truth** (F7: "certified ≠ true on every surface"). The
margin engine computes worst cases over *logically consistent* worlds. A
corrupted import that lies consistently — a subtree wrong in a way that
respects every ⊑ edge — is invisible to the min-cut; that is what the
concentration caps and per-source clusters are for, and they are blunt.

**Premiums and odds are prices under capital constraints and attack, not
probabilities.** The pool's quoted rate reflects its reserves, caps,
adversaries, and ignorance; reading it as a calibrated probability is a
category error this document refuses to license.

**A green simulation certifies nothing about model risk.** G3/G4 passing means
the model survives the adversaries we wrote down, under the distributions we
planted. Lundberg holds under assumptions the notional caps *enforce* rather
than the world providing; the closure term sees only the correlation the DAG
can express; the gearing is calibrated to synthetic loss tables until real
ones exist.

**Borrowed numbers are borrowed.** The ~9.5× is a practitioner measurement of
Polymarket's book; 4.8 and the ~20% cap are Nexus's calibration of Nexus's
risks. They are priors and shapes, not results about factbond; G1–G4 exist to
replace them with our own numbers.

**Polynomiality is not throughput.** O(E) consistency and one-max-flow
margining are complexity classes, not latency budgets; nothing here promises
the engine keeps up with any particular assertion volume until someone
benchmarks it on the measured catalogue.
