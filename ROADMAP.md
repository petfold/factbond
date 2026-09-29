# factbond — roadmap

Phased like the sibling projects: each phase has an exit criterion, and a
phase is done when that criterion is met with tests. Keep this file updated
(mark items done with a date).

**This file is an index, not a specification.** Each item links to the
plan document under [`docs/plans/`](docs/plans/) that holds its decisions,
gates and open problems; how to use what is built is the
[User Guide](docs/USER-GUIDE.md); what each piece is and why is
[DESIGN.md](docs/DESIGN.md). The order across repositories is the
development sequence of 2026-09-25 (Track F is factbond's).

---

## Phase 1 — the assertion primitive · [mechanism](docs/plans/mechanism-design.md)

Exit: bonded assertions, disputes and rulings live on chain with the
procedure, the policy and the ledger views around them, and a consumer
(loopmarket's escrow) resolved through them.

- [x] `Assertions.sol` v0, live on Gnosis (2026-09-19): assert, dispute
      at the confidence's odds, certify by timeout, rule, retract; the
      consumer's `hold`/`resolve`; the first live claim on a loopmarket
      reservation certified and paid through the escrow.
- [x] Per-assertion challenge and ruling windows (F1, F4; 2026-09-28) ·
      [assertion-extensions §1](docs/plans/assertion-extensions.md).
- [x] A ruling fee instead of the 25% slice; the asserter's concession
      (2026-09-28) · [DESIGN §8](docs/DESIGN.md).
- [x] The second rung (F6, 2026-09-28): an arbiter named at deployment,
      first rulings held for appeal, appeal at the doubled stake, the
      first rung's deposit forfeited on reversal ·
      [mechanism §4](docs/plans/mechanism-design.md).
- [x] Only a ruling moves money (2026-09-28): a lapsed rung's case moves up
      with the stakes held; the per-assertion escalation value withdrawn.
- [x] Claims name the key they concern (`about`, `Named`; 2026-09-28).
- [x] Evidence policy as data (F3) · [evidence-policy](docs/plans/evidence-policy.md)
      — `factbond.policy`, the placeholder `credential` policy.
- [x] The adjudicator's procedure and the ruling record (F4, F6) —
      `factbond.procedure`.
- [x] The calibration ledger's views from events (F5, F6) —
      `factbond.ledger`: the loss view, the adjudicator view, claims about
      a key.
- [x] **Isolate consumer reverts** (added and DONE 2026-09-29, before the
      redeploy): `Assertions` calls the consumer's `hold` and `resolve`
      without isolating a revert, so a consumer that reverts in `resolve`
      strands the case and both stakes, and one that reverts only on 0
      makes its claims unrefutable (THREATS T18's residual, found building
      loopmarket's E1). `hold` may keep reverting (that is the consumer's
      refusal, and the assertion never opens); every close must complete
      whatever the consumer does, the consumer's failure recorded in an
      event. loopmarket's escrow no longer reverts on a claim it opened, so
      the gate is a hostile consumer in the tests.
- [x] **Redeploy on Gnosis** with an arbiter, then the adjudicator's
      deposit; loopmarket's single escrow redeploy (its E3) names the new
      address. DONE 2026-09-29: `0x3c1B4C944398bcc30890d6A6c78f1F9AA2dFe270` (adjudicator and treasury the
      deployer's key, the arbiter a stand-in key of the same operator —
      to be replaced by a named, bonded final rung at the next redeploy —
      fee 0.001, floor 0.01, challenge 1 h within [10 min, 60 d], ruling
      1 d up to 90 d, ruling and arbiter fees 0.005, appeal 1 d, the rung's
      0.01 deposit posted); loopmarket's escrow named it from `0xA49Cc9F9dab95aAB7093F138A084027ef66dD936` (E3, claim 1 live)
      and names it at `0xddDB7276F705671673F0885aEf93B99b890Eb5A9` since 2026-09-29 night. The order across the two repositories is kept in
      loopmarket's `ROADMAP.md` (P3b, "order of work", 2026-09-29).
- [ ] The evidence fee and the challenger's cap charged on a real dispute;
      B5's return of the fee · [assertion-extensions §2](docs/plans/assertion-extensions.md).
- [ ] The ladder beyond two rungs: the automated evidence rung, the staked
      panel with soulbound stake · [mechanism §4](docs/plans/mechanism-design.md).
- [ ] The correction feed on Swarm, carrying `factbond.ledger.corrections`
      · [records-and-anchoring §6](docs/plans/records-and-anchoring.md).

## Phase 1b — factbond on ontodag · [ontodag-first](docs/plans/ontodag-first.md)

Exit: a pack version's root claim bonded, and a leaf disputed and settled
by an `is_below` certificate alone.

- [ ] `factbond.claims`: batch root-claims per pack version, disputed at
      the leaf by certificate (rung 0).
- [ ] The packs' measured ~3% single-source error rate as the first real
      planted-error prior in the harness.
- [ ] The coverage give for any pack used in bonded matching.

## Phase 0 — the simulation gate · [phase0-simulation](docs/plans/phase0-simulation.md)

Exit: a scored run with all four pre-registered panels passing. Gates the
insurance product, not the primitive.

- [x] The harness v0 (2026-09-19): the synthetic knowledge base, the
      adversary suite each in its own world, the panels, content-addressed
      artifacts; the reliance term, consumption-targeted challengers, the
      half-life curve, volunteer sweeps, the parcel-locker preset.
- [x] The ruling fee and the bond floor at least the rung's cost
      (2026-09-28).
- [x] A controlled fact covered only by its controller's warranty or a
      surety (2026-09-28): arson −33% against +10% under the cap ·
      [insurance-products §5a](docs/plans/insurance-products.md).
- [ ] **The pre-registration** (T, D\*, the λ range, sign-off) — Peter's;
      until then every run is exploratory.
- [ ] How many owners warrant: the adoption the warranty rule needs, and
      notices and cures in the harness.

## Phase 2 — insurance and the pool · [insurance-products](docs/plans/insurance-products.md)

Exit: cover sold where reliance is provable or a controller warrants the
fact, the pool solvent under the harness's loss scenarios.

- [ ] Cover on loopmarket legs: the insured asserts the trigger, the
      reservation pays, assignment and netting (loopmarket's C5; milestone
      M4) · [credentials-cover-and-options D3](docs/plans/credentials-cover-and-options.md).
      *Half done 2026-09-29 on loopmarket's side:* the covered period, the
      cover-only reservation, the deductible on the deposit, assignment and
      netting in the escrow (live at `0xddDB7276F705671673F0885aEf93B99b890Eb5A9`, claims resolved
      through this contract). Open here: D-1 — a false presentation reduces
      the payout proportionately, which needs a ruling that states an amount
      (and a rule for how stakes split on it); D-3's doctrine for the
      adjudicator (an unadjudicable term construed against the insurer).
- [ ] Warranted facts and sureties as products (§5a).
- [ ] The geared reserve and the mutual as the first pooled form, with its
      rules (milestone M5) · [netting-and-reserves §7](docs/plans/netting-and-reserves.md).
- [ ] The pool as asserter and pool-funded disputes · [mechanism §6–§7](docs/plans/mechanism-design.md).
- [ ] Dispute markets · [mechanism §5](docs/plans/mechanism-design.md).
- [ ] The agents' product on facts nobody controls.

## Beyond loopmarket

factbond does not need loopmarket: a claim is a subject hash, and any
contract, or none, may be its consumer.

- [ ] Owners warranting their own facts: a listing with money behind it.
- [ ] An optimistic oracle for other contracts at small stakes.
- [ ] Knowledge-base corrections (Wikidata, OpenStreetMap) with the
      correction feed · [domain-choice](docs/plans/domain-choice.md).

## Open decisions

Recorded with their options in the plans; the ones waiting on Peter:

- The pre-registration block (Phase 0).
- Which fact types count as controllable (insurance-products OP-2; the
  harness counts every POI and locker type).
- The reliance term's `k` (mechanism §2), a Phase-0 output.

## Related repositories

- **loopmarket** — the first consumer; its escrow names this contract as
  resolver. `../loopmarket/ROADMAP.md`.
- **hansa** — attesters, registers and the insurer's product layer, which
  use these assertions.
- **ontodag** — the claim layer and the vocabulary packs (Phase 1b).
