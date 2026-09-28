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
    view = adjudicator_view(ruled, confirmed, reversed_)
    assert view[ADJ] == {"reversals": [{"id": 3, "forfeited": 30, "time": 35}, {"id": 4, "forfeited": 30, "time": 300}],
                         "confirmed_on_appeal": [{"id": 2, "time": 25}]}
    assert view[OTHER] == {"reversals": [], "confirmed_on_appeal": []}     # five rulings or one: nothing to count
    recent = adjudicator_view(ruled, confirmed, reversed_, now=310, max_age=100)
    assert recent[ADJ] == {"reversals": [{"id": 4, "forfeited": 30, "time": 300}], "confirmed_on_appeal": []}
