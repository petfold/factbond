# factbond: Phase-0 simulation — the go/no-go instrument

Status: design, 2026-08-07. Decided here: the four-panel pre-registered
go/no-go and its kill-only interpretation; the frozen-domain synthetic KB;
the agent populations and adversary scenario suite; the parameter grid and
its calibration anchors; the deliverables (loss tables, equilibrium
observations, sensitivity analysis); the shared-harness clause with
loopmarket; the plain-Python tooling ruling. Open here: the threshold T
itself (owner: Peter; pre-registration block in §2, deliberately unset),
the fabrication-cost curve, the agent-rationality model.

This document expands `DESIGN.md` §10's one-paragraph Phase 0 into the
full specification of the agent-based simulation that gates everything
factbond builds — written before any contract exists, because the point of
pre-registration is that the instrument is fixed before the data arrives.
Companions: `mechanism-design.md` (consumes the equilibrium observations),
`insurance-products.md` and `netting-and-reserves.md` (consume the loss
tables), `THREATS.md` (supplies the adversaries), `evidence-policy.md`
(owns the fabrication-cost model this simulation can only parameterize),
`records-and-anchoring.md` (the record shapes the harness uses natively),
`loopmarket-coupling.md` (sequences the coupling on this gate), and
loopmarket's `docs/plans/P2-clearing-pricing.md` (the shared harness's
second consumer, §9).

## 1. What the simulation must decide

`DESIGN.md` §10 states the go/no-go question: **at what dispute cost and
consumption rate does planted-error half-life become acceptable?** If
honest verification of a mundane false claim cannot be made profitable,
the system looks healthy while quietly certifying nothing — the
lazy-verification problem (`DESIGN.md` §5) as silent failure. Quantified
into four panels, all evaluated over the swept grid of §6, all fixed
before the first run:

1. **Half-life.** Median planted-error half-life ≤ T at the reference
   dispute cost D* and consumption rate λ* (all three set in §2).
2. **Honest-challenger ROI > 0** on mundane false claims — somewhere in
   the grid an ordinary profit-driven challenger, paying real verification
   costs, earns money finding planted errors. Not a whale, not a
   subsidized agent: the marginal challenger.
3. **Arson and fabrication ROI < 0 across the entire grid** — no swept
   cell makes the T5 arsonist or the evidence fabricator profitable (§7);
   one profitable cell is a no-go, not an outlier.
4. **Pool solvency ≥ 99.5%** over the horizon (the Solvency II
   one-year-survival calibration the reserve model inherits —
   `netting-and-reserves.md`), under §7's correlated shocks, not just
   independent claims.

If panel 2 fails everywhere, the verdict is **no-go for the vision — not
a parameter hunt**. That sentence is why this document exists: the
temptation after a failed run is to widen the grid, soften a cost model,
or re-derive T; §2 makes that visible as the methodological failure it
would be. Secondary outputs the run must fix (inputs to Phase 1, not
gates): the bond floor, the confidence bucket set, and the seed premium
rule the pool quotes before it has loss experience.

## 2. Pre-registration: the threshold, its owner, the rules

The acceptability threshold T is a **product judgment, not a simulation
output**. No run can say how long a false opening-hours entry may
acceptably survive in a KB people act on; that is a statement about what
the product is for. Therefore:

- **Owner: Peter.** T is fixed by the owner, recorded in the block below,
  **before the first scored run**. Exploratory runs to debug the harness
  are permitted before T is set; no run whose outputs feed the verdict is.
- **Never tuned post-hoc.** Once scored runs begin, T does not move. A
  no-go at T is not escaped by editing T but by a redesign substantial
  enough to justify a new pre-registration — a new block appended below,
  the old one never deleted.
- D* and λ* are fixed in the same block, anchored to the frozen domain's
  measured consumption statistics (§3).

```
PRE-REGISTRATION BLOCK (append-only)
  T   (median planted-error half-life) : ⟨unset — Peter, before first scored run⟩
  D*  (reference dispute cost)         : ⟨unset⟩
  λ*  (reference consumption rate)     : ⟨unset⟩
  set by / date                        : ⟨unset⟩
```

## 3. The synthetic KB: a frozen domain, planted errors, real rot

The KB is not abstract. Per `DESIGN.md` §10 Phase 1, the target domain is
**OSM `opening_hours` in one city** — high error base rate, cheap physical
verification, crisp evidence — and Phase 0 simulates over a **frozen
snapshot of that same domain**, so the sim-to-testnet comparison in
Phase 1 is apples-to-apples rather than a change of subject.

- **Scale:** 10⁵–10⁶ facts across 3–5 fact-types (opening hours, address,
  phone, category membership, existence), each with its own error base
  rate and verification cost. The `opening_hours` error prior is
  high-single-digit percent (consistent with `DESIGN.md` §5.4's
  illustrative "~92% reliable"); actual base rates are **measured at
  snapshot time and frozen** — priors never survive the snapshot.
- **Planted errors** at those base rates seed the initial state, plus a
  **drift process**: facts decay true→false at type-specific hazard rates
  mid-run, so `Certified` status can silently rot — the regime the design
  exists for; a driftless sim flatters every mechanism under test.
- **Consumption is Zipf-distributed**, so most facts are never consumed.
  The lazy-verification regime is the point, not a corner case: the
  mechanism's claim is that verification effort allocates in proportion
  to consumption (`DESIGN.md` §5); uniform consumption would assume the
  conclusion.

## 4. Agent populations

- **Asserters.** The **pool-as-asserter** is the bulk case (`DESIGN.md`
  §7): auto-asserts KB slices at bucketed confidence per policy, with its
  *refusals* recorded (refusal is signal). Independent asserters carry
  private signals and assert against the pool's blanket confidence.
- **Challengers.** Profit-driven, heterogeneous per-fact-type
  verification costs, free entry/exit. The marginal challenger is panel 2.
- **Insurance buyers**, three kinds: **honest** (consumption-driven, both
  products of the `DESIGN.md` §5.1 split — parametric convenience vs
  verification bet); **informed** (the adverse-selection knob: a swept
  fraction who know something, `DESIGN.md` §5.4); **adversarial** (fronts
  for the §7 playbooks).
- **Adjudicators.** Honest ones have per-rung cost and error rate;
  **capturable** ones sell their ruling above a price; a **conformist**
  variant votes the perceived majority rather than truth (the cascade in
  the 2025 Zelenskyy-suit episode — Forbes, Decrypt, CoinDesk). The
  structural rung runs at ~zero cost: F8, "structural (matches-source)
  claims settle by certificate/inclusion-proof only", so only
  matches-world claims load the expensive rungs (`INTEGRATION.md` §5).

Status is computed in-harness exactly as F1 demands in production —
"status derived from signed speech acts plus a clock, never
stored-and-merged" — the simulation is the record schema's first consumer,
not a parallel implementation of a different one.

## 5. Mechanisms under test

The full claim lifecycle of `DESIGN.md` §7, plus every economic mechanism
the plan documents commit to, runs in silico before any of it is code:
**odds-weighted disputes** over swept bucket sets (the empirical half of
the game theory `mechanism-design.md` names as the design's main risk and
its paper, `DESIGN.md` §11.2); **indemnity-bounded insurance** — F3,
"indemnity — payout ≤ provable reliance, payout-cap proxy where reliance
is unprovable"; the sim's consumers sit outside clearing, so it runs on
payout caps, exactly the wedge product's operating condition
(`insurance-products.md`); **the escalation ladder** with F4 enforced —
"reliance-bounded adjudication — final rung integrity cost ≥ aggregate
open reliance, per-claim insurance caps fail closed" — and F5 constraining
the adjudicator model — "tribunal independence — the incentive asset never
holds positions in disputed outcomes; adjudicator stake soulbound";
**premium updating from own loss experience** from a cold start (the
trajectory matters as much as the fixed point); **the slashing split**
(`DESIGN.md` §8: majority to the winner, a slice burned or to the
adjudication treasury); and **auto-funded disputes** (a paid-out
verification bet auto-files the sibling matches-source dispute,
`DESIGN.md` §7).

Four design-time inequalities are checked **across the whole grid, not at
the design point**: the indemnity cap (F3), the final-rung reliance
condition (F4), dispute-spam unprofitability (§7), and F9 — "no
volume-linked emissions anywhere" — which holds by construction (nothing
volume-linked exists to emit; the check fails loudly if a future
mechanism change introduces one).

## 6. Parameter grid and calibration anchors

Swept: **bond floors** $0.5–$20 (bracketing `DESIGN.md` §8's $1–10
prior); **confidence bucket sets** ({0.9, 0.97, 0.99, 0.999} and coarser/
finer alternatives); **liveness windows** days–weeks; **dispute cost per
rung**; **insurance premium/payout ratios**; **consumption rates** λ per
fact-type; the **fabrication cost curve** E(t), declining over time (the
generative-media parameter); **yield rate** on pool collateral (the
99-cent term at pool level, `DESIGN.md` §6.3); **adverse-selection
intensity**.

Calibration anchors — these must **emerge from the model, never be
assumed into it**:

- UMA's empirical record: ~98–99% of assertions undisputed, a mature
  dispute rate around 1–2% (crypto.news; UMA blog; ~545 Polymarket
  resolutions/month in 2024). A model whose honest-path dispute rate sits
  at 20% or 0.01% is miscalibrated whatever its panels say.
- **Capture replay as validation**: with F4's reliance term switched
  *off*, the sim must reproduce the Polymarket/UMA March-2025 episode in
  miniature — a $750-scale bond guarding $7M-scale open reliance, flipped
  by an actor with ~25% of final-rung power (The Block; CoinDesk). A model
  that cannot express the failure cannot certify the fix. With F4 on, the
  same scenario must be unprofitable.

## 7. The adversary suite: THREATS entries as scripted agents

Every register entry factbond owns (`THREATS.md`: T4, T5, T6, T9) plus
the adjacent griefing modes becomes a scripted attacker with a budget and
a stop rule, run against every grid cell:

- **T5 insurance arson.** Buy policies on facts you control, break the
  facts, collect. Negative-ROI under F3's caps everywhere — including the
  aggregation variant: many small legit-looking policies across sybil
  buyers on one cluster.
- **T4 adjudication capture.** Buy the final rung when aggregate open
  reliance exceeds capture cost; tests F4 and F5 jointly. Includes the
  **wearing-down** variant (dispute honestly, lose to a captured or
  conformist tribunal, exit — the Zelenskyy-suit pattern, resolved NO
  twice with honest disputers slashed both times): the metric is
  challenger-population survival after an unjust ruling; the
  countermeasure under test is the auto-funded dispute channel.
- **Assert-at-0.999 griefing.** Maximal stated confidence to make
  challenges maximally expensive (`DESIGN.md` §11.2); probed via the
  confidence-misstatement, challenger-entry-threshold, and
  asserter–challenger-collusion runs that feed `mechanism-design.md`.
- **Self-dispute laundering.** Dispute your own assertion from a second
  identity to wash stake through the winner's share; strictly negative
  under the slash-split's burned slice (`DESIGN.md` §8).
- **Dispute-spam griefing.** Spam disputes to freeze claims and exhaust
  auto-funding; disputer bonds must cover the delay externality.
- **T9 basis-risk fixtures.** Ambiguous-policy scenarios (world deviates
  from record vs record wrong; the Augur invalid-market and
  Proof-of-Humanity photo-angle pattern: the policy text is the contract)
  — the two-product split must price the two propositions separately or
  the product is mis-sold.
- **Evidence-layer shocks.** Collusive countersigning on fabricated
  events; the E(t) curve; a **mass certificate revocation** (the Nikon
  Z6III pattern, Sept 2025: one exploit revoked a fleet) as a correlated
  evidence-class shock — admissibility weights collapse mid-run and the
  ladder must degrade, not certify garbage.
- **T6 governance capture** is longer-horizon than the sim (the
  Croatian-Wikipedia timescale is years); the harness instruments its
  tripwires (assertion-power concentration over hub subjects); the
  defense is constitutional, owned by `THREATS.md`.
- **Cluster shocks.** Correlated failure of claims sharing a source,
  region, or adjudicator (`DESIGN.md` §8): the ruin runs validating
  `netting-and-reserves.md`'s reserve formula — u = max(min-cut
  worst-case cluster, Lundberg residual ln(1/ε)/R) — against simulated
  shocks rather than the independence the Lundberg term assumes.

## 8. Deliverables

1. **Loss tables per fact-type** — frequency, severity, correlation: the
   pool's founding actuarial data, pricing input for
   `insurance-products.md`, reserve input for `netting-and-reserves.md`.
   `DESIGN.md` §5.4 calls the production version of this dataset plausibly
   the most valuable thing the system generates; this is its bootstrap.
2. **Planted-error half-life curves** vs dispute cost and consumption
   rate — the go/no-go surface, with T marked on it.
3. **Arson/fabrication ROI surfaces** over the grid (panel 3).
4. **Ruin probability vs reserve u**, correlated-shock validated.
5. **Odds-weighted-bond equilibrium observations** — the empirical half
   of `mechanism-design.md`'s paper: where bucket granularity invites
   odds-ratio gaming, where challenger entry collapses.
6. **Premium-vs-realized-loss calibration plots** and cold-start premium
   trajectories under adverse selection.
7. **Sensitivity analysis**: which parameters the verdict is fragile to.
   A go that flips on a ±20% move in an unmeasurable parameter (E(t)
   foremost) is reported as fragile, and fragility is a gate.

## 9. The shared harness: one harness, two consumers

The same simulation core runs loopmarket's clearing-pricing **shading
experiments** (loopmarket's `docs/plans/P2-clearing-pricing.md`): maker
agents shade stated rates under candidate pricing rules, testing whether
the equal log-surplus split keeps truthful pricing undominated — the Roth
safety criterion applied to loop clearing. One harness because the
populations overlap (makers are insurance consumers in the coupled
system), the record shapes are shared, and two divergent harnesses would
make the eventual coupling (`loopmarket-coupling.md`) untestable as a
whole. loopmarket's design-time checks (the wash-loop inequality, U13)
run in the same regression suite. Boundary discipline: **the go/no-go
gate is factbond's alone** — loopmarket experiments neither delay nor
dilute the verdict, and a shading result never offsets a failed panel.

## 10. Tooling ruling

**Plain Python, plus the repo's own record shapes** (decided 2026-08,
lands with Phase 0). Assertions, disputes, rulings, and policies are the
signed speech-act records `records-and-anchoring.md` specifies — the
simulation is the schema's first consumer, so schema mistakes surface
here, not on a testnet. Deterministic seeds throughout: the same seed
yields the same verdict on every machine (loopmarket's U6 replica
discipline applied to simulation). **cadCAD is optional and never
load-bearing**: usable for exploration, but no result that exists only
inside cadCAD counts toward any panel — scored runs execute in the plain
harness. Results are versioned, content-addressed artifacts. The harness
survives Phase 0 as the **permanent regression suite**: after the gate,
no parameter or mechanism change ships in any phase without a green run.

## Gates

- **Pre-registration gate.** T, D*, λ*, and the four panels recorded in
  §2 with owner sign-off (Peter). No scored run before the block is filled.
- **Calibration gate.** The UMA-anchored dispute rate (~1–2% mature)
  emerges without being tuned to; the capture replay reproduces with F4
  off and fails with F4 on. Fail → the model is not yet an instrument.
- **The go/no-go itself.** All four §1 panels pass → Phase 1 (layers 1–2
  on testnet, `DESIGN.md` §10) may start. Any panel fails → no-go;
  redesign and re-register, or stop.
- **Fragility gate.** A go that reverses within the stated sensitivity
  bounds of an unmeasurable parameter is treated as no-go pending better
  measurement (owned by `evidence-policy.md` for E(t)).
- **Deliverable gate.** Loss tables, equilibrium observations, and
  sensitivity analysis delivered to their consumer documents before
  Phase 1 parameters are fixed.
- **Permanence gate.** From Phase 1 onward, every parameter or mechanism
  change requires a green regression run in this harness.

## Open problems

- **The threshold T.** A product judgment nobody can outsource to the
  sim; owner Peter; work package: this document's §2 block, before the
  first scored run.
- **The fabrication-cost curve E(t).** No defensible empirical anchor for
  the price of fabricating admissible evidence over time; the sim sweeps
  it and reports fragility; the measurement problem is owned by
  `evidence-policy.md`.
- **The agent-rationality model.** Half-life depends on challenger entry
  behavior; rational-entry and behavioral (imitation, exit-after-loss)
  models can disagree. Both run; a verdict that differs between them is
  itself a reported result. Work package: the §8 sensitivity analysis,
  feeding `mechanism-design.md`.
- **Reliance measurement outside clearing.** The sim models only the
  payout-cap proxy, mirroring the product's own limitation (F3); provable
  reliance exists only in the loopmarket coupling. Work package:
  `insurance-products.md`, with the registered open problem it inherits.
- **Long-horizon capture (T6).** Governance capture operates on
  timescales the sim cannot reach; instrumented here, defended
  constitutionally. Work package: `THREATS.md`.

## What this document does not promise

A green simulation certifies nothing about model risk: not the agent
rationality assumptions, not the fabrication cost model, not the absence
of attacks nobody scripted, and nothing about real-world evidence quality.
**The go/no-go can only kill, never prove** — a no-go is decisive; a go
means only "the design survived the adversaries we could imagine at the
parameters we could defend." Simulated premiums, like real ones, are
prices under capital constraints and attack, not probabilities; the loss
tables are priors for Phase 1, not guarantees about production behavior.
And on every surface F7 stands: certified ≠ true — in the simulation as
in the product, "Certified" means nobody found it profitable to dispute,
under this procedure, at these levels (`DESIGN.md` §12), and no panel here
measures anything stronger.
