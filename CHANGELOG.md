# Changelog

Releases are tag-driven (`v*` tags run `.github/workflows/publish.yml`, PyPI
trusted publishing).

## [Unreleased]

### Changed

- **`Assertions.sol`: the challenge window and the escalation value are
  per assertion** (2026-09-28; development sequence F1 and F-esc,
  `credentials-cover-and-options.md` D10). `assert_` takes `window` (0 for
  the deployment's `challengeSeconds`, otherwise within the constructor's
  new `minChallengeSeconds`/`maxChallengeSeconds`) and `escalation` (bps
  of the outcome at most the deployment's `escalationBps`, or
  `UNRESOLVED`). An unresolved escalation returns both stakes, leaves the
  consumer's hold in place (status `Unresolved`, event `Unresolved`) and
  is resolved by a later `rule` with no clock. `Asserted` carries
  `challengeUntil` and `escalation`. Breaking for callers: the constructor
  has ten arguments and `assert_` six (`scripts/deploy_assertions.py`, the
  client, loopmarket's cross-repo test follow). The deployed
  `0xfa6f…bF99` is the old source until the redeploy.
  `AssertionsClient.assert_(…, window=, escalation=)` defaults both to
  the deployment's; `window_bounds()`, `escalation_bps()`, `UNRESOLVED`.
- **The ruling window is per assertion too** (2026-09-28, F4): `assert_`
  takes `rulingWindow` (0 for `rulingSeconds`, otherwise up to the
  constructor's new `maxRulingSeconds`, never shorter than the default),
  so that a self-knowable claim can be ruled on the asserter's silence
  before it escalates. The constructor has eleven arguments and `assert_`
  seven; `Asserted` carries `rulingWindow`; the client takes
  `ruling_window=` and reads `ruling_bounds()`.

- **The 25% slice is replaced by a ruling fee, and the asserter may
  concede** (2026-09-28, Peter: a deduction is a cost; a margin above cost
  is a price only competition may set). The constructor's `winnerBps`
  becomes `rulingFeeWei` (at most the floor, so either side's stake covers
  it): the loser pays it to the adjudicator that ruled and the winner takes
  the rest; nothing goes to the treasury but the assertion fees. `concede`
  lets the asserter of a contested claim hand the challenger the whole
  bond with no ruling and no fee; `Refuted` gains `ruled`. The client gains
  `concede()` and `ruling_fee()`. The harness follows: `winner_share` is
  gone, the loser pays `rung_cost` to the adjudicator, and the bond floor
  never falls below `rung_cost`, since a fee only one side could pay would
  pay the judge to rule against that side. Plans: DESIGN §8,
  mechanism-design §1, §3 (the calibration ledger no longer credits dispute
  survival), §4 (reversal refunds from the adjudicator's forfeited deposit)
  and open problems; THREATS T8, T10, T11, T16 and the honesty row;
  phase0-simulation; assertion-extensions §2; the cross-repository plan's
  D2 (in both repositories).

### Added

- **Evidence policy as data, `factbond.policy`** (2026-09-28; F3). A
  per-domain `PolicyDocument`, content-addressed (`policy_ref`, pinned
  loads in canonical encoding only), with a `ClassRule` per claim type:
  rungs with adjudicator class, ruling period, fee, deposit and evidence
  weights; cure period, evidence period and fee, challenger cap, finality
  window, escalation value. It refuses at load a class without a named,
  bonded final rung and the other rules fixed in D2, D10 and F8.
  `Suspension` (`suspended/<statement>`) with `suspended()` deriving it.
  The placeholder `policies/credential.json` is shipped. `CLAIM_TYPES`
  gains `self-knowable` and the harness reads the one vocabulary. With F4:
  the notice's `notice_expiry` (A2), `ruling_window()` and
  `ruling_window_fits()`.
- **The adjudicator's path, `factbond.procedure`** (2026-09-28; F4). The
  rules before the merits, as pure functions of the case file and the
  clock: labels refused, the notice step for a claim on a reservation (a
  cited notice, lapsed, unexpired, uncured; `Case.reservation`) and none
  for a dispute of a live assertion (Peter, 2026-09-28), ex parte against a notified, silent accused under a burden
  shift, late evidence to the merits with B5's flag. `Decision.upheld`
  gives `rule`'s argument for a dispute or a claim. THREATS T17
  (defamation on a permanent store) added, mirrored in loopmarket.

- **Plans: credentials, cover and options** (2026-09-25). Two documents
  entered the plan corpus from the assurance drafts:
  `docs/plans/credentials-cover-and-options.md` (the cross-repository plan
  shared with loopmarket) and `docs/plans/assertion-extensions.md` (F1, the
  `self-knowable` class, disputes with clocks, the loss view). Existing
  plans amended by dated edit: evidence-policy §1 (the class, its clocks,
  fee, cap, suspension, adjudicator class and final rung; the door witness
  types) and open problems; mechanism-design §2 (per-leg reliance), §4
  (first ruling pays, finality window, doubled-stake re-challenge, clocks
  per rung, the paid and ledgered judge, ruling counts never a signal, a
  named final rung per class) and open problems; records-and-anchoring §2
  (the ruling record's fields), §6 (the feed carries the asserter) and open
  problems; insurance-products §5 (what it rejects and does not; cover on
  legs; the mutual; negligence excluded), §8 (composed cover) and OP-1;
  netting-and-reserves §7 (the reserve applied to cover gives; the
  mutual's rules); ontodag-first (`Requires.coverage` reconciled with
  `requires.legs` and the argument-only operator; the credential pack's
  coverage give); loopmarket-coupling §3b (the escrow's new acts, the
  acceptable resolver, the clocks) and open problems; THREATS T15–T16
  mirrored from loopmarket; CLAUDE.md's decided-not-built list; the README.

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
  sweeps do. The automated boxes as the first target within the domain
  (`domain-choice.md` §8; Ljubljana: 203 mapped lockers, 1 with a payment
  tag) and the `lockers` preset.

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
