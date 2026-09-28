"""The calibration ledger's views (F6, F5; 2026-09-28): entries, never
counts or ratios; a look-back that drops what is older, the events kept."""

from factbond.ledger import adjudicator_view

ADJ, OTHER = "0xadj", "0xother"


def test_an_adjudicators_entries_are_its_reversals_and_its_confirmations_never_a_count():
    ruled = [{"id": i, "adjudicator": ADJ, "time": 10 * i} for i in range(1, 6)] + \
            [{"id": 9, "adjudicator": OTHER, "time": 5}]
    confirmed = [{"id": 2, "adjudicator": ADJ, "time": 25}]
    reversed_ = [{"id": 3, "adjudicator": ADJ, "forfeited": 30, "time": 35},
                 {"id": 4, "adjudicator": ADJ, "forfeited": 30, "time": 300}]
    escalated = [{"id": 7, "lapsed": OTHER, "time": 60}]
    view = adjudicator_view(ruled, confirmed, reversed_, escalated)
    assert view[ADJ] == {"reversals": [{"id": 3, "forfeited": 30, "time": 35}, {"id": 4, "forfeited": 30, "time": 300}],
                         "confirmed_on_appeal": [{"id": 2, "time": 25}], "lapses": []}
    assert view[OTHER] == {"reversals": [], "confirmed_on_appeal": [], "lapses": [{"id": 7, "time": 60}]}
    recent = adjudicator_view(ruled, confirmed, reversed_, escalated, now=310, max_age=100)
    assert recent[ADJ] == {"reversals": [{"id": 4, "forfeited": 30, "time": 300}], "confirmed_on_appeal": [],
                           "lapses": []}
    assert recent[OTHER]["lapses"] == []                                   # older than the look-back


def _asserted(id_, asserter, bond=10, time=0):
    return {"id": id_, "subject": b"s%d" % id_, "asserter": asserter, "bond": bond, "confidence": 990, "time": time}


def test_the_loss_view_joins_refuted_to_asserted_and_keeps_only_negatives():
    """F5's gate on synthetic events: the view is Refuted ⋈ Asserted on id;
    a won dispute (a Certified, never read) leaves nothing; an entry older
    than the look-back is not returned; losses are absolute sums; with
    ruling records, a ruled loss says whether it was on the merits, on
    silence, or on form."""
    from types import SimpleNamespace
    from factbond.ledger import corrections, loss_view
    asserted = [_asserted(1, "0xa"), _asserted(2, "0xa", bond=30), _asserted(3, "0xb"), _asserted(4, "0xa")]
    refuted = [{"id": 1, "subject": b"s1", "ruled": True, "time": 100},
               {"id": 2, "subject": b"s2", "ruled": False, "time": 200},
               {"id": 4, "subject": b"s4", "ruled": True, "time": 400},
               {"id": 99, "subject": b"x", "ruled": True, "time": 50}]      # no Asserted to join: dropped
    feed = corrections(asserted, refuted)
    assert [c["id"] for c in feed] == [1, 2, 4] and all(c["asserter"] == "0xa" for c in feed)
    view = loss_view(asserted, refuted)
    assert set(view) == {"0xa"} and view["0xa"]["bond_lost"] == 50                   # 0xb won or was never disputed
    assert [(e["id"], e["kind"]) for e in view["0xa"]["losses"]] == [(1, "ruled"), (2, "conceded"), (4, "ruled")]
    assert [e["id"] for e in loss_view(asserted, refuted, now=450, max_loss_age=300)["0xa"]["losses"]] == [2, 4]
    rulings = {1: SimpleNamespace(reason="A5: the accused, notified, produced no evidence"),
               4: SimpleNamespace(reason="merits: the accused's evidence is on the record")}
    kinds = [e["kind"] for e in loss_view(asserted, refuted, rulings=rulings)["0xa"]["losses"]]
    assert kinds == ["silent", "conceded", "refuted"]
    assert loss_view(asserted, refuted, rulings={1: SimpleNamespace(reason="B1: no notice")})["0xa"]["losses"][0][
        "kind"] == "procedural"


def test_a_claim_counts_against_a_key_only_if_it_named_it():
    """The bonded-negation rule: readers count against K only the claims
    whose `Named` event told K."""
    from factbond.ledger import claims_about
    named = [{"id": 3, "about": "0xk"}, {"id": 5, "about": "0xother"}, {"id": 8, "about": "0xk"}]
    assert claims_about("0xk", named) == [3, 8] and claims_about("0xnobody", named) == []
