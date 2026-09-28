"""Evidence policy as data (F3, 2026-09-28): a policy document round-trips
through its canonical encoding and its pin; a class without a named, bonded
final rung is refused at load, as is every other rule the plans fixed
(F8, A3–A5, B1, B3, D10); the `suspended/` record and when it is due."""

import json

import pytest

from factbond.assertions import UNRESOLVED
from factbond.policy import (CLAIM_TYPES, ClassRule, PolicyDocument, PolicyError, Rung, Suspension, evidence_due,
                             load, shipped, suspended)

DAY = 86400


def _record():
    return shipped("credential").to_record()


def _with(mutate):
    rec = _record()
    mutate(rec)
    return rec


def _refused(rec, words):
    with pytest.raises(PolicyError) as exc:
        PolicyDocument.from_record(rec)
    assert words in str(exc.value), str(exc.value)


def test_the_shipped_placeholder_loads():
    doc = shipped("credential")
    rule = doc.rule("self-knowable")
    assert rule.burden_shifts and rule.evidence_period == 14 * DAY
    assert rule.final_rung.adjudicator == "panel" and rule.final_rung.deposit > 0
    assert rule.escalation_arg() == UNRESOLVED                        # what Assertions.assert_ takes (D10)
    assert not doc.rule("attribute-matches-source").burden_shifts
    assert "self-knowable" in CLAIM_TYPES
    with pytest.raises(KeyError):
        doc.rule("entity-exists")


def test_a_policy_record_round_trips():
    doc = shipped("credential")
    rec = doc.to_record()
    assert PolicyDocument.from_record(rec) == doc and PolicyDocument.from_record(rec).to_record() == rec
    data = doc.canonical_bytes()
    assert load(data, ref=doc.policy_ref) == doc                      # the pin names this spelling
    assert json.loads(data) == rec
    # defaults may be left out when writing; the canonical form carries every field, so the ref is one
    sparse = _with(lambda r: r["classes"]["attribute-matches-source"]["rungs"][0].pop("admits"))
    assert PolicyDocument.from_record(sparse).policy_ref == doc.policy_ref
    pretty = json.dumps(rec, indent=1).encode()
    import hashlib
    with pytest.raises(PolicyError, match="canonical"):
        load(pretty, ref=hashlib.sha256(pretty).hexdigest())
    with pytest.raises(PolicyError, match="pinned ref"):
        load(data, ref="00" * 32)
    assert load(pretty) == doc                                        # unpinned, any spelling reads
    other = _with(lambda r: r["classes"]["self-knowable"].update(evidence_period=7 * DAY))
    assert PolicyDocument.from_record(other).policy_ref != doc.policy_ref


def test_a_class_without_a_final_rung_is_refused_at_load():
    sk = lambda f: _with(lambda r: f(r["classes"]["self-knowable"]))  # noqa: E731
    _refused(sk(lambda c: c.update(rungs=[])), "no final rung")
    _refused(sk(lambda c: c["rungs"].pop()), "no final rung")         # ends at the register: nobody named
    _refused(sk(lambda c: c["rungs"][-1].update(deposit=0)), "no final rung")   # named, not bonded
    _refused(sk(lambda c: c["rungs"][-1].update(adjudicator="token-vote")), "never a token vote")
    _refused(sk(lambda c: c["rungs"][-1].update(id="")), "names who sits there")
    # a named, bonded key is a final rung too
    ok = sk(lambda c: c["rungs"][-1].update(adjudicator="key", id="0x" + "11" * 20))
    assert PolicyDocument.from_record(ok).rule("self-knowable").final_rung.adjudicator == "key"


def test_the_plans_rules_are_refused_at_load():
    sk = lambda f: _with(lambda r: f(r["classes"]["self-knowable"]))  # noqa: E731
    src = lambda f: _with(lambda r: f(r["classes"]["attribute-matches-source"]))  # noqa: E731
    _refused(src(lambda c: c["rungs"].append(_record()["classes"]["self-knowable"]["rungs"][-1])), "certificate alone")
    _refused(src(lambda c: c["rungs"][0].update(adjudicator="panel", id="p", deposit=1)), "certificate alone (F8)")
    _refused(sk(lambda c: c["rungs"].insert(1, {"name": "c", "adjudicator": "certificate", "ruling_period": 1})),
             "rung zero or nothing")
    _refused(sk(lambda c: c.pop("evidence_period")), "evidence period (A5)")
    _refused(src(lambda c: c.update(evidence_period=DAY)), "only a self-knowable class")
    _refused(sk(lambda c: c["rungs"][0].update(ruling_period=0)), "ruling period (A3)")
    _refused(sk(lambda c: c.update(cure_period=0)), "cure period (B1)")
    for cap in (0, 10000, 0.5):
        _refused(sk(lambda c: c.update(cap_bps=cap)), "k < 1")
    for esc in (10001, -1, True, "half"):
        _refused(sk(lambda c: c.update(escalation=esc)), "(D10)")
    _refused(sk(lambda c: c.update(evidence_fee=1.5)), "evidence fee")
    _refused(sk(lambda c: c["rungs"][0]["admits"].update(photo="proof")), "weights are")
    _refused(_with(lambda r: r["classes"].update({"opinion": r["classes"]["self-knowable"]})), "claim type")
    _refused(_with(lambda r: r.update(v=2)), "unknown policy version")
    _refused(_with(lambda r: r.update(appeal="none")), "unknown fields")
    _refused(sk(lambda c: c.update(sealed=True)), "unknown fields")
    _refused(_with(lambda r: r.update(classes={})), "at least one class")
    with pytest.raises(PolicyError, match="JSON"):
        load(b"not json")


def test_a_rule_built_in_code_checks_like_a_loaded_one():
    rung = Rung("arbitrator", "key", 28 * DAY, id="0x" + "22" * 20, deposit=1)
    rule = ClassRule("attribute-matches-world", (rung,), DAY, 30 * DAY, 5000, 5000)
    PolicyDocument("osm.opening_hours", "eip155:100/slip44:700", (rule,)).check()
    assert rule.escalation_arg() == 5000 and not rule.burden_shifts
    with pytest.raises(PolicyError, match="one rule per class"):
        PolicyDocument("d", "u", (rule, rule)).check()


def test_suspended_from_the_lapse_until_the_ruling():
    rule = shipped("credential").rule("self-knowable")
    t0 = 1_000_000
    due = evidence_due(rule, t0)
    assert due == t0 + 14 * DAY
    assert not suspended(rule, t0, due)                                  # the period is still running
    assert suspended(rule, t0, due + 1)                                  # lapsed, no evidence: meets nothing
    assert not suspended(rule, t0, due + 1, evidence_at=due)             # evidence in time
    assert suspended(rule, t0, due + 1, evidence_at=due + 1)             # late evidence lifts nothing
    assert suspended(rule, t0, due + 5, ruled_at=due + 9)                # until the ruling ...
    assert not suspended(rule, t0, due + 9, ruled_at=due + 9)            # ... and not after it
    structural = shipped("credential").rule("attribute-matches-source")
    assert not suspended(structural, t0, t0 + 365 * DAY)                 # no burden shift, never suspended
    with pytest.raises(ValueError):
        evidence_due(structural, t0)


def test_the_suspension_record_round_trips():
    doc = shipped("credential")
    s = Suspension("stmt-1", "dispute-1", doc.policy_ref, evidence_due(doc.rule("self-knowable"), 1_000_000))
    assert s.key == "suspended/stmt-1"
    assert Suspension.from_record(s.to_record()) == s
    rec = s.to_record()
    for bad, words in (({**rec, "cleared": True}, "unknown fields"), ({**rec, "v": 2}, "unknown suspension version"),
                       ({**rec, "statement": ""}, "names its statement"), ({**rec, "evidence_due": -1}, "evidence_due")):
        with pytest.raises(PolicyError, match=words):
            Suspension.from_record(bad)
