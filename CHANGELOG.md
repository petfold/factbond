# Changelog

Releases are tag-driven once a publish workflow exists; until then this is
the record of what landed.

## [Unreleased]

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
  `0xfa6f9367A283A8c53AA876C1416D4B49027bBF99` the same evening.
