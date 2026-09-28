"""The calibration ledger's views, read from the contract's events alone
(`mechanism-design.md` §3 and §4; `credentials-cover-and-options.md` D2's
C3 and D9's G3–G4; F6 and F5 of the development sequence, 2026-09-28).

The ledger is append-only underneath (the chain's logs) and every view is a
derivation over it, never a stored score. Two rules hold throughout:

- **Negatives only, and absolute.** Nothing positive flows from a ruling
  count or from surviving a dispute: both are for sale at the fees
  (loopmarket's U12; THREATS T11, T16). A view returns entries, never a
  ratio over activity, and a clean record on a new key means nothing (T8).
- **Nothing counts forever by default** (G3): a view takes a look-back
  and drops what is older, while the events stay.

`adjudicator_view` is F6's: an adjudicator's reversals by the arbiter, each
with the deposit it forfeited, and the one positive entry C3 allows — a
ruling appealed at the doubled stake to the final rung and confirmed there,
which cost the appellant a real review."""

from __future__ import annotations


def _recent(time: int, now: int | None, max_age: int | None) -> bool:
    return now is None or max_age is None or time >= now - max_age


def adjudicator_view(ruled: list, confirmed: list, reversed_: list, *, now: int | None = None,
                     max_age: int | None = None) -> dict:
    """Per first-rung adjudicator, from the `Ruled`, `Confirmed` and
    `Reversed` events (dicts with `id`, `adjudicator`, `time`, and for a
    reversal `forfeited`): its `reversals` and its `confirmed_on_appeal`,
    each a list of entries within the look-back. Its rulings are read only
    to name who ruled; how many it made is never returned."""
    out: dict = {}
    for e in ruled:
        out.setdefault(e["adjudicator"], {"reversals": [], "confirmed_on_appeal": []})
    for e in reversed_:
        if _recent(e["time"], now, max_age):
            out.setdefault(e["adjudicator"], {"reversals": [], "confirmed_on_appeal": []})["reversals"].append(
                {"id": e["id"], "forfeited": e["forfeited"], "time": e["time"]})
    for e in confirmed:
        if _recent(e["time"], now, max_age):
            out.setdefault(e["adjudicator"], {"reversals": [], "confirmed_on_appeal": []})[
                "confirmed_on_appeal"].append({"id": e["id"], "time": e["time"]})
    return out


def adjudicator_view_from_chain(client, *, from_block: int = 0, now: int | None = None,
                                max_age: int | None = None) -> dict:
    """`adjudicator_view` over an `AssertionsClient`'s events."""
    return adjudicator_view(client.events("Ruled", from_block), client.events("Confirmed", from_block),
                            client.events("Reversed", from_block), now=now, max_age=max_age)
