"""The adjudicator's path (F4, 2026-09-28): a label is refused as a dispute;
a claim on a reservation without a prior lapsed notice is refused; an
unnotified accused cannot lose by silence; a cure within the deadline ends
the matter; a notified accused silent through the evidence period is ruled
against ex parte; late evidence goes to the merits with B5's flag. A
dispute of a live assertion takes no notice (Peter, 2026-09-28): the
dispute is the notice, and concession its cheap ending."""

import pytest

from factbond.policy import ClassRule, PolicyDocument, PolicyError, Rung, shipped
from factbond.procedure import (EX_PARTE, MERITS, PENDING, REFUSED, Accusation, Case, Cure, Notice, Submission,
                                decide)
from factbond.sim.records import Claim

DAY = 86400
POLICY = shipped("credential")
RULE = POLICY.rule("self-knowable")
WANTER, DENTIST, OTHER = "0xwanter", "0xdentist", "0xother"
T0 = 1_000_000                                                   # the notice is sent


def _claim(claim_type="self-knowable", policy_ref=None):
    return Claim("cred/0xdentist/licence-1", "root:register@1", claim_type, policy_ref or POLICY.policy_ref)


CLAIM = _claim()
NOTICE = Notice(WANTER, DENTIST, CLAIM.claim_id, POLICY.policy_ref, T0, T0 + RULE.cure_period)
ACT = T0 + RULE.cure_period + DAY                                # the bonded act, after the cure deadline


def _case(claim=CLAIM, notices=(NOTICE,), cures=(), submissions=(), act=ACT, refs=None, **kw):
    """The wanter's claim on the reservation the dentist's statement backed."""
    acc = Accusation(WANTER, DENTIST, claim.claim_id if claim else "label:fraudster", act,
                     tuple(n.ref for n in notices) if refs is None else refs, **kw)
    return Case(POLICY, acc, claim, tuple(notices), tuple(cures), tuple(submissions), reservation="escrow:leg-1")


def test_a_label_is_refused_as_a_dispute():
    for case in (_case(claim=None),                                          # names no claim record
                 _case(claim=_claim("entity-exists")),                       # a type the policy does not cover
                 _case(claim=_claim(policy_ref="00" * 32))):                 # under another policy
        d = decide(case, ACT)
        assert (d.kind, d.against, d.rule) == (REFUSED, "accuser", "specific"), d
    # a dispute of a live assertion names the fact that assertion asserts
    other = Case(POLICY, _case().accusation, CLAIM, (NOTICE,), disputed_claim=_claim("attribute-matches-source").claim_id)
    assert decide(other, ACT).rule == "specific"
    assert decide(Case(POLICY, _case().accusation, CLAIM, (NOTICE,), disputed_claim=CLAIM.claim_id), ACT).kind != REFUSED


def test_a_claim_on_a_reservation_without_a_prior_lapsed_notice_is_refused():
    assert decide(_case(notices=()), ACT).reason == "no notice to the giver precedes the claim on its reservation"
    assert decide(_case(refs=()), ACT).rule == "B1"                          # a notice exists but is not cited
    early = decide(_case(act=T0 + RULE.cure_period), T0 + RULE.cure_period)
    assert early.kind == REFUSED and "cure deadline had not passed" in early.reason
    expired = decide(_case(act=T0 + RULE.notice_expiry + 1), T0 + RULE.notice_expiry + 1)
    assert (expired.kind, expired.rule) == (REFUSED, "A2")
    for bad, words in ((Notice(OTHER, DENTIST, CLAIM.claim_id, POLICY.policy_ref, T0, T0 + RULE.cure_period),
                        "not the accuser's"),
                       (Notice(WANTER, OTHER, CLAIM.claim_id, POLICY.policy_ref, T0, T0 + RULE.cure_period),
                        "another key"),
                       (Notice(WANTER, DENTIST, "ff" * 32, POLICY.policy_ref, T0, T0 + RULE.cure_period),
                        "another fact"),
                       (Notice(WANTER, DENTIST, CLAIM.claim_id, POLICY.policy_ref, T0, T0 + DAY),
                        "less than the cure period")):
        d = decide(_case(notices=(bad,)), ACT)
        assert d.kind == REFUSED and words in d.reason, d
    # one valid notice among the cited ones suffices, and the decision names it
    stray = Notice(OTHER, DENTIST, CLAIM.claim_id, POLICY.policy_ref, T0, T0 + RULE.cure_period)
    assert decide(_case(notices=(stray, NOTICE)), ACT).notice_ref == NOTICE.ref


def test_an_unnotified_accused_cannot_lose_by_silence():
    long_after = ACT + 365 * DAY
    d = decide(_case(notices=()), long_after)                                # silent for a year, never notified
    assert d.kind == REFUSED and d.upheld(accuser_is_asserter=True) is False
    # and no class can drop the notice step a claim on a reservation takes
    rec = POLICY.to_record()
    rec["classes"]["self-knowable"].update(cure_period=0)
    with pytest.raises(PolicyError, match="cure period"):
        PolicyDocument.from_record(rec)


def test_a_cure_within_the_deadline_ends_the_matter():
    cure = Cure(NOTICE.ref, DENTIST, T0 + DAY, "tx:refund")
    d = decide(_case(cures=(cure,)), ACT)
    assert d.kind == REFUSED and "cured within the deadline" in d.reason
    late = Cure(NOTICE.ref, DENTIST, NOTICE.cure_deadline + 1)
    assert decide(_case(cures=(late,)), ACT).kind != REFUSED                 # past the deadline it is no cure
    impostor = Cure(NOTICE.ref, OTHER, T0 + DAY)
    assert decide(_case(cures=(impostor,)), ACT).kind != REFUSED             # only the accused cures
    contested = decide(_case(cures=(cure,), contests_cure=True), ACT)
    assert contested.kind in (PENDING, MERITS, EX_PARTE)                     # whether it cured is now the question


def test_silence_after_notice_is_ruled_against_ex_parte():
    due = ACT + RULE.evidence_period
    running = decide(_case(), due)
    assert (running.kind, running.against, running.rule) == (PENDING, None, "A5")
    lapsed = decide(_case(), due + 1)
    assert (lapsed.kind, lapsed.against, lapsed.rule) == (EX_PARTE, "accused", "A5")
    assert lapsed.notice_ref == NOTICE.ref
    # the two shapes on chain: a claim's accuser asserted it; a dispute's accuser is the challenger
    assert lapsed.upheld(accuser_is_asserter=True) is True
    assert lapsed.upheld(accuser_is_asserter=False) is False
    in_time = decide(_case(submissions=(Submission(DENTIST, due, "hash:licence-confirmation"),)), due + 1)
    assert (in_time.kind, in_time.late_evidence) == (MERITS, False) and in_time.upheld(True) is None
    late = decide(_case(submissions=(Submission(DENTIST, due + 1, "hash:licence-confirmation"),)), due + 2)
    assert (late.kind, late.late_evidence) == (MERITS, True)                 # weighed; B5 returns E
    # the accuser's own submissions are not the accused's evidence
    assert decide(_case(submissions=(Submission(WANTER, ACT, "hash:complaint"),)), due + 1).kind == EX_PARTE


def test_a_dispute_of_a_live_assertion_takes_no_notice():
    """A hunter disputes the pool's locker hours at once, with no notice the
    pool could cure by retracting; the asserter of a self-knowable claim,
    disputed, is ruled against on its silence after the evidence period."""
    rung = Rung("arbitrator", "key", 28 * DAY, id="0x" + "22" * 20, deposit=1)
    lockers = PolicyDocument("osm.lockers", "eip155:100/slip44:700",
                             (ClassRule("attribute-matches-world", (rung,), DAY, 30 * DAY, 5000, 5000,
                                        notice_expiry=30 * DAY),))
    hours = Claim("locker/mall-x/opening_hours", "root:osm@1", "attribute-matches-world", lockers.policy_ref)
    hunter = Case(lockers, Accusation("0xvolunteer", "0xpool", hours.claim_id, ACT), hours,
                  disputed_claim=hours.claim_id)
    d = decide(hunter, ACT)
    assert (d.kind, d.against, d.notice_ref) == (MERITS, None, "")
    silent = Case(POLICY, Accusation(WANTER, DENTIST, CLAIM.claim_id, ACT), CLAIM, disputed_claim=CLAIM.claim_id)
    assert decide(silent, ACT + RULE.evidence_period).kind == PENDING
    d = decide(silent, ACT + RULE.evidence_period + 1)
    assert (d.kind, d.against) == (EX_PARTE, "accused") and d.upheld(accuser_is_asserter=False) is False
    # the same accusation routed from a reservation needs the notice it does not cite
    routed = Case(POLICY, silent.accusation, CLAIM, reservation="escrow:leg-1")
    assert decide(routed, ACT + RULE.evidence_period + 1).rule == "B1"


def test_a_ruling_record_names_its_fact_its_notices_and_its_rule():
    """F6's gate off chain: a ruling missing the referred fact, or the notice
    refs a claim on a reservation rests on, is not a ruling; a label is
    recorded by its hash, never repeated; a lapse is recorded as such."""
    from factbond.policy import PolicyError
    from factbond.procedure import RulingRecord, ruling_record
    case = _case()
    d = decide(case, ACT + RULE.evidence_period + 1)
    r = ruling_record(case, d, adjudicator="0xadj", outcome="upheld", time=ACT + RULE.evidence_period + 2,
                      dispute_ref="assertion:7", pack_root="root:pack@1")
    assert r.referred_fact == CLAIM.claim_id and r.notices == ((NOTICE.ref, NOTICE.sent_at, NOTICE.cure_deadline),)
    assert r.submissions == ("lapse",) and r.reason.startswith("A5:") and r.category == "self-knowable"
    assert RulingRecord.from_record(r.to_record()) == r and r.policy_version == POLICY.policy_ref
    rec = r.to_record()
    for bad, words in (({**rec, "referred_fact": ""}, "no referred fact"),
                       ({**rec, "notices": []}, "rests on notices"),
                       ({k: v for k, v in rec.items() if k != "notices"}, "lacks"),
                       ({**rec, "reason": ""}, "names no rule"),
                       ({**rec, "submissions": []}, "neither submissions nor their lapse")):
        with pytest.raises(PolicyError, match=words):
            RulingRecord.from_record(bad)
    # a dispute of a live assertion took no notice step, and its record needs none
    live = Case(POLICY, Accusation(WANTER, DENTIST, CLAIM.claim_id, ACT), CLAIM, disputed_claim=CLAIM.claim_id,
                submissions=(Submission(DENTIST, ACT + DAY, "hash:confirmation"),))
    r2 = ruling_record(live, decide(live, ACT + DAY), adjudicator="0xadj", outcome="upheld", time=ACT + 2 * DAY,
                       dispute_ref="assertion:8")
    assert r2.notices == () and r2.reservation is None and r2.submissions == ("hash:confirmation",)
    label = Case(POLICY, Accusation(WANTER, DENTIST, "label:unlicensed quack", ACT), None)
    r3 = ruling_record(label, decide(label, ACT), adjudicator="0xadj", outcome="upheld", time=ACT, dispute_ref="a:9")
    assert "quack" not in str(r3.to_record()) and r3.category == "" and r3.reason.startswith("specific:")
