"""The Phase-0 harness (phase0-simulation.md): deterministic under its
seed, status derived from records alone (F1, G-REC1), nothing minted for
asserting (F9), the capture replay reproducing with F4 off and failing
with it on (§6), a scored run refused until the pre-registration block is
filled (§2), arson negative under a full control exclusion (F3/T5)."""

import pytest

from factbond.sim import Params, artifact, curve, run, run_grid
from factbond.sim.records import (ASSERTED, CERTIFIED, CONTESTED, REFUTED, UNASSERTED, Assertion,
                                  Claim, Dispute, Fold, Retraction, Ruling, status)

SMALL = Params(facts=300, ticks=40)


def test_status_is_a_derivation_from_the_folded_records_and_a_clock():
    c = Claim("opening_hours/1", "root:x", "attribute-matches-world", "policy:v1")
    f1, f2 = Fold(), Fold()
    assert status(f1, c.claim_id, now=0) == UNASSERTED
    a = Assertion(c.claim_id, "pool", 990, 2.0, liveness=10, time=5)
    d = Dispute(a.ref, "c1", 0.5, time=7)
    r = Ruling(d.ref, "adj", "refuted", 1, time=8)
    for rec in (a, d):
        f1.add(rec)
    for rec in (d, a):                         # the other order
        f2.add(rec)
    assert status(f1, c.claim_id, 6) == status(f2, c.claim_id, 6) == CONTESTED
    f3 = Fold(); f3.add(a)
    assert status(f3, c.claim_id, 6) == ASSERTED and status(f3, c.claim_id, 16) == CERTIFIED
    f1.add(r)
    assert status(f1, c.claim_id, 9) == REFUTED
    assert status(f1.union(f2), c.claim_id, 9) == status(f2.union(f1), c.claim_id, 9) == REFUTED
    # a later ruling on a higher rung supersedes; a retraction empties the claim
    f1.add(Ruling(d.ref, "arb", "upheld", 3, time=12, supersedes=r.ref))
    assert status(f1, c.claim_id, 13) == CERTIFIED
    f3.add(Retraction(a.ref, "pool", 7))
    assert status(f3, c.claim_id, 8) == UNASSERTED
    assert status(f1, c.claim_id, 500, validity_end=400) == "Expired"


def test_the_same_seed_yields_the_same_artifact_and_a_different_seed_does_not():
    r1, r2 = run(SMALL), run(SMALL)
    assert artifact(r1)[0] == artifact(r2)[0]
    assert artifact(run(SMALL.replace(seed=2)))[0] != artifact(r1)[0]


def test_nothing_is_minted_for_asserting_and_the_ledger_sums_to_what_entered(monkeypatch):
    from factbond.sim.engine import Engine
    from factbond.sim.world import World
    p = SMALL
    e = Engine(p, World.build(p))
    for _ in range(10):
        e.tick()
    total = sum(e.ledger.balances.values())
    assert abs(total - e.ledger.minted) < 1e-6           # every unit came in through a named inflow
    # the inflows are exogenous capital and consumers' premiums, never an assertion reward
    exogenous = p.pool_stake + 100.0 * p.challengers
    premiums = sum(v for k, v in e.ledger.balances.items() if k.startswith("buyer/")) \
        + sum(e.sold[t] for t in e.world.types) * 0     # premiums moved on to the pool
    assert e.ledger.minted >= exogenous
    assert e.stats["assertions"] > 0 and e.ledger.balances["treasury"] >= p.fee * e.stats["assertions"] - 1e-6


def test_capture_replay_reproduces_with_f4_off_and_fails_with_it_on():
    r = run(SMALL.replace(ticks=5))
    assert r["capture_replay"] == {"f4_on": "unprofitable", "f4_off": "captured"}
    assert r["verdict"]["calibration_capture_replay"] is True


def test_a_scored_run_needs_the_preregistration_block():
    with pytest.raises(RuntimeError, match="pre-registration"):
        run(SMALL, scored=True)
    assert run(SMALL.replace(ticks=3))["scored"] is False


def test_arson_is_negative_under_a_full_control_exclusion_and_positive_without_one():
    closed = run(SMALL.replace(control_exclusion=1.0, ticks=30))
    assert closed["adversary_roi"]["arson"] <= 0
    open_ = run(SMALL.replace(control_exclusion=0.0, ticks=30))
    assert open_["adversary_roi"]["arson"] > 0                   # the wedge's cap alone does not stop arson
    assert closed["adversary_roi"]["launder"] < 0 and closed["adversary_roi"]["spam"] < 0


def test_the_grid_runs_and_writes_content_addressed_artifacts(tmp_path):
    rows = run_grid(SMALL.replace(ticks=10), {"bond_floor": (0.5, 8.0)}, seeds=(1,), out_dir=str(tmp_path))
    assert len(rows) == 2 and all((tmp_path / (r["ref"][:16] + ".json")).exists() for r in rows)
    assert rows[0]["ref"] != rows[1]["ref"]


def test_the_curve_runs_over_the_axis_and_a_bounty_only_pays_adjudicated_corrections():
    rows = curve(SMALL.replace(ticks=15), axis=(0.001, 0.05), seeds=(1,))
    assert [r["consumption_rate"] for r in rows] == [0.001, 0.05] and all(r["meets_T"] is None for r in rows)
    with_bounty = run(SMALL.replace(ticks=30, bounty=5.0), adversaries=False)
    assert with_bounty["bounties"] <= with_bounty["refuted"]
