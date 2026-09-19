# Changelog

Releases are tag-driven (`v*` tags run `.github/workflows/publish.yml`, PyPI
trusted publishing).

## [Unreleased]

### Added

- **The Phase-0 simulation harness, v0** (`factbond.sim`,
  `docs/plans/phase0-simulation.md`; 2026-09-19): the synthetic KB with
  planted errors, drift and Zipf consumption; the pool as asserter,
  profit-driven challengers, honest and informed buyers, the adjudicator;
  the mechanism (fee, floor, odds-weighted stakes, liveness, the slashing
  split, F3 caps, F4 fail-closed sales, premium updating from own losses,
  the payout→dispute coupling); the adversary suite as scripted agents,
  each in its own world; the four panels, the calibration anchors, the
  loss tables; deterministic seeds and content-addressed artifacts; a
  scored run refused until the pre-registration block is filled. Status
  is a pure derivation from the speech-act records (F1), the schema's
  first consumer. Seven tests. Then the reliance term (bond = max(floor,
  k × open reliance), top-ups by retraction and re-assertion) and
  consumption-targeted challengers with the loss table as prior; finding:
  challengers who follow consumption verify the clean records, since the
  coupling corrects the consumed errors first — the marginal challenger's
  edge has to be information, not search.
- **POI liveness** as the domain (Peter, 2026-09-19; `domain-choice.md`,
  a survey of Wikidata's random statements and human edits and OSM's
  notes and changesets): the harness's five fact types on one place with
  realistic verification costs, `bounty` per adjudicated correction,
  `LAMBDA_AXIS` and `curve` (half-life against participation, §2's
  amended deliverable), the v2 pre-registration block. Plans updated:
  phase0-simulation §2–§3, DESIGN §10, insurance-products §1,
  loopmarket-coupling §3c. Then the population half-life (censored when
  the run ends first), escrowed bonds as pool assets, and the sweep
  population with `sweeps` — half-life against sweep capacity at a launch
  consumption rate; finding: no consumption rate reaches the cold errors,
  sweeps do.

## [0.1.0] — 2026-09-19

### Added

- **The assertion primitive's consumer-facing edge** (2026-09-19, the
  first code; decided with Peter the same day: custody in loopmarket,
  adjudication here, one level). `contracts/Assertions.sol`: assert with a
  bond at a stated confidence bucket, the fee to the treasury (F9);
  dispute at max(B·(1−c)/c, floor); certify by timeout; the adjudicator
  rules a contested claim with DESIGN §8's slashing split; escalation
  when no ruling comes (both stakes back, the outcome at a fixed share —
  v0's stand-in for the ladder's next rung); retraction returns the bond,
  never the fee; a consumer contract is told `hold(subject)` and
  `resolve(subject, outcome)` and nothing else, and may refuse the hold
  (no registration). `factbond.assertions.AssertionsClient`, the shipped
  artifact, `scripts/build.py`, `scripts/deploy_assertions.py`; seven
  tests on a local EVM, and loopmarket's cross-repo gate running a claim
  on a real escrow reservation. Deployed on Gnosis at
  `0xfa6f9367A283A8c53AA876C1416D4B49027bBF99` the same evening, and gated
  live that night: assertion 1 on a loopmarket reservation, held, certified
  by timeout, resolved and paid through the escrow.
