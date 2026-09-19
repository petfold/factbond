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

## Running tests

```bash
pip install -e ".[test,evm]"     # --break-system-packages or a venv
python3 -m pytest tests/ -v
python3 scripts/build.py          # after any change to the contract
```

Sibling repos: loopmarket (the first consumer; its `docs/plans/P3-release-and-reclearing.md` §5e is the custody/adjudication split), ontodag, recordstore.
