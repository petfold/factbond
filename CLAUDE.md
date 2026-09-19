# CLAUDE.md

Guidance for Claude Code in this repository.

## What this project is

**factbond** is bonded assertions and information insurance for factual
claims: attach an economic guarantee ("someone will pay if this is wrong")
to ordinary facts — knowledge-graph edges, database entries, and, first, a
delivery claim on a loopmarket fill. The design corpus under `docs/` is the
product so far (`DESIGN.md`, `INTEGRATION.md`, the work packages under
`docs/plans/`); read `DESIGN.md` §3 (the primitive), §7 (the lifecycle) and
`docs/plans/mechanism-design.md` §1–§4 before touching the contract.

## What is built (2026-09-19): the consumer-facing edge

- `contracts/Assertions.sol` — the bonded assertion on the EVM. `assert_`
  (a subject hash, an optional consumer contract, the claimed `outcome` in
  the consumer's units, a confidence bucket {0.9, 0.97, 0.99, 0.999}, the
  fee plus a bond at least the floor); `dispute` at the stake the
  confidence sets, max(B·(1−c)/c, floor); `certify` by timeout when
  undisputed; `rule` by the adjudicator on a contested claim (the loser's
  stake mostly to the winner, the rest to the treasury); `escalate` when no
  ruling arrives in the window (v0's stand-in for the next rung: both
  stakes back, the subject resolved at `escalationBps` of the outcome);
  `retract` returns the bond, never the fee. A consumer is told exactly
  twice — `hold(subject)` when the claim opens (and may refuse: no
  registration, the consumer's acceptance ties a subject to this resolver)
  and `resolve(subject, outcome)` when it closes. `Refuted` is the
  correction feed's event.
- **Deployed 2026-09-19 on Gnosis at `0xfa6f9367A283A8c53AA876C1416D4B49027bBF99`** (adjudicator and treasury the deployer's key, fee 0.001 xDAI, floor 0.01 xDAI, challenge 1 h, ruling 1 d, winner 7500 bps, escalation 5000 bps); loopmarket's redeployed escrow `0x299CE499fdDA61bCB006718E5Ac551B5006269Bf` names it as resolver. **Live gate the same night:** assertion 1 — a claim on a real reservation (subject = the escrow's key), the escrow's `hold` fired by `assert_`, certified by timeout after its hour, `resolve` paying the wanter 0.01 xDAI through the escrow, the bond returned.
- `src/factbond/assertions.py` — `AssertionsClient` (web3 lazy, the
  `chain` extra), `BUCKETS`, `abi()` reading the shipped artifact
  `src/factbond/contracts/Assertions.json` (`scripts/build.py`; solc 0.8.24,
  via IR, optimizer 200). `scripts/deploy_assertions.py`.
- `tests/test_assertions.py` on a local EVM (the `evm` extra; skips per
  test without it). The cross-repo gate lives in loopmarket:
  `tests/test_escrow.py::test_factbond_as_the_resolver` compiles this
  contract from `../factbond` and runs a claim on a real `LoopEscrow`
  reservation both ways (certified by timeout; disputed and refuted).

## The Phase-0 harness (`src/factbond/sim`, v0 built 2026-09-19)

`python -m factbond.sim run [--facts N --ticks N --seed S --set KEY=VALUE --out DIR]`
runs one cell and prints the four panels (§1), the calibration anchors
(§6) and the loss tables (§8); `... grid` sweeps `params.GRID`. Plain
Python, deterministic under its seed, results content-addressed; the
repo's record shapes (`sim/records.py`: claim, assertion, dispute, ruling,
retraction, and `status()` as F1's pure derivation) are the harness's
native objects. **A scored run refuses to start until `preregistration.json`
is filled** (T, D*, λ*, `set_by` — Peter's, §2); every run today is
exploratory. Each adversary (`sim/adversaries.py`: arson, capture, the
0.999 griefer, self-dispute laundering, dispute spam, evidence fabrication
under E(t)) runs in a world of its own so its ROI is its own. What v0
leaves out is listed in `sim/__init__.py`.

**The reliance term and consumption-targeted challengers** (built 2026-09-19,
after the first findings): `k_reliance` sizes the pool's bond as
max(floor, k × the open insured exposure riding on the record), reliance
counting at sale and retiring over the liveness window, a live assertion
topped up by retraction and re-assertion when the reliance outgrows it
(the fee is the price); `target_consumption` makes challengers scan by
consumption weight and read the pool's loss table as their prior. On one
2,000 × 120 cell the combination made challengers *act* (117 exits, median
ROI −1.04) without finding more errors (refuted 8 → 10): the consumed
records are the clean ones, since the payout→dispute coupling corrects
them first, so a challenger who follows consumption verifies clean records
at full cost while the errors that survive are the cold ones under floor
bonds. That is the lazy-verification structure seen from the other side,
and it says the marginal challenger's edge must be *information*
(personal knowledge, an informed buyer's signal) rather than search —
the launch-regime question Peter raised the same night (below).

**POI liveness (Peter's decision, 2026-09-19, `docs/plans/domain-choice.md`):**
the harness's fact types are existence, identity, opening hours,
wheelchair and address on one place (placeholder error priors until a
snapshot measures them; verification $15–20 of a person's time),
`rung_cost` is the automated evidence rung ($8; a person reading $30–60),
`bounty` pays per *adjudicated* correction from fees first (F9), and
`python -m factbond.sim curve` is §2's amended deliverable — median
half-life against consumption rate over `LAMBDA_AXIS` from launch values
up, T read off it when `preregistration.json` (v2 block: T, D\* as
verification + adjudication, the λ range, sign-off) names it. **The population half-life and the sweep axis** (the same night): the
half-life panel is measured on the errors planted at t0 — the tick by
which half were corrected, censored when the run ends first — since a
median over the corrected ones alone flattered every cell; the pool's
escrowed bonds count as its assets. The first honest curve (2,000 facts,
120 ticks): at *every* consumption rate on `LAMBDA_AXIS` the half-life
exceeds the run — consumption is Zipf, so the cold errors are never
consumed and the coupling never reaches them; a higher rate corrects more
hot errors (30 of ~200 at λ = 0.3) and leaves the population alone. That
is the launch problem in numbers, and `sweep_capacity` (`sweep()`,
`python -m factbond.sim sweeps`) is the lever it points at: volunteers
verifying the least-recently-verified facts a street at a time at
`sweep_cost` each, the pool funding the dispute, the bounty theirs. The
sweep curve at a launch consumption rate (λ = 0.001, 2,000 facts, 120
ticks): 0.5 facts/day (five people, three facts a month) corrects
nothing; 30/day corrects 27 of 98 seeded errors and the half-life still
exceeds the run; **100/day — every fact revisited about every 20 days —
gives a half-life of 11 days** and holds drift down (133 open at the end
against 203). The rule of thumb this yields: the half-life is about half
the revisit period plus drift, so a city of 50,000 POIs needs ~1,800
verifications a day for T = 14 — about 60 person-hours a day at a street
a time. That is the adoption target §2's amendment asked for, and the
argument for the crawler as asserter (`domain-choice.md` §5, thread 2):
sources are the one verifier that scales without people. **The first target is the automated boxes** (Peter, `domain-choice.md`
§8): parcel lockers' existence, access hours and peer-handover model —
no person speaks for a box, the claims are crisp, and every loopmarket
handover through one reports back; `--preset lockers` in the harness.
Three threads Peter opened with the decision — bonded quests beside
StreetComplete, the crawler as pre-emptive asserter on sources, and a
reputation-first browser plugin for editors without crypto — are
`domain-choice.md` §5, not started.

**The launch regime (Peter, 2026-09-19):** five people editing three
facts a month is where this starts, so a single λ\* is the wrong thing to
pre-register; the deliverable is the half-life-versus-consumption curve
with T marked on it, read as the participation the product needs. D\*
is verification ($10–30 of a person's time for a physical fact) plus
adjudication ($5–10 automated, $30–60 read by a person, panels and
arbitrators above); the harness's verification costs were too low. What
gets people involved, within F9: bounties per *adjudicated* correction,
the calibration ledger as a visible non-transferable score, district
sweeps, personal knowledge asserting against the pool's blanket
confidence. Written into the plan (§2 as amended) and the harness the same night.

Exploratory findings at the defaults before those two (not a verdict): the honest dispute rate sits at ~0.4 %, below the UMA anchor,
because scanning challengers find no positive expected value at
adjudication-cost floors (panel 2 fails everywhere in the small grid — the
reliance term and consumption-targeted challengers are the unmodelled
parts that would change this); arson stays profitable (~+7 % ROI) while
the control exclusion leaves any residue, so F3's proxy cap alone does not
close T5 (a real finding for `insurance-products.md` §5); the 0.999
griefer, self-dispute laundering, dispute spam and fabrication all lose;
the capture replay reproduces with F4 off and fails with F4 on; the pool
stays solvent.

## Invariants the code must keep (from the plans)

- **F7** `Certified` is a process fact, never truth — in names, events,
  docs.
- **F9** no volume-linked emissions: nothing is ever paid for asserting;
  the fee accrues to the treasury (the pool, later).
- The asserter's capital at risk grows with stated confidence
  (mechanism-design §1); the dispute floor prices dispute spam.
- The contract knows nothing of what a subject means; consumers interpret
  `outcome`. Never add loopmarket- or Wikidata-specific fields here.

## Not built (and where it is designed)

The reliance term of bond sizing and `k` (mechanism-design §2, Phase 0's
output); rungs 0–2 of the ladder and the soulbound panel (§4); dispute
markets (§5); the pool as asserter and pool funding (§6–§7); the insurance
product and the reliance proof (`insurance-products.md`,
`loopmarket-coupling.md` §3); the records and anchoring on Swarm
(`records-and-anchoring.md`); the Phase-0 simulation
(`phase0-simulation.md`), which gates the *insurance* product, not this
primitive.

## Releasing

Tag-driven: `git tag -a vX.Y.Z && git push origin vX.Y.Z` runs
`.github/workflows/publish.yml` (the suite with the `evm` extra, then PyPI
trusted publishing under the `pypi` environment). Bump `pyproject.toml` and
`src/factbond/__init__.py` together and move the changelog's Unreleased.

## Running tests

```bash
pip install -e ".[test,evm]"     # --break-system-packages or a venv
python3 -m pytest tests/ -v       # the contract on a local EVM, and the harness (~2 min)
python3 scripts/build.py          # after any change to the contract
PYTHONPATH=src python3 -m factbond.sim run --facts 2000 --ticks 120   # an exploratory cell, ~3 min
```

Sibling repos: loopmarket (the first consumer; its `docs/plans/P3-release-and-reclearing.md` §5e is the custody/adjudication split), ontodag, recordstore.
