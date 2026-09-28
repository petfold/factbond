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
which cost the appellant a real review.

`loss_view` is F5's, the asserter-indexed negative half: `Refuted` joined
to `Asserted` on `id` (the refutation carries no asserter or bond; the
assertion does). A dispute the asserter won leaves nothing, since
`Certified` is never read. Each loss says how it came (G4, so an honest
misdescription is not read as fraud): `conceded`, the asserter's own act;
`refuted` on the merits; `silent`, ruled against on the record after the
evidence period, a party that did not perform in the proceeding rather
than one shown wrong; or `procedural`, a contest refused on its form
(a claimant's missing notice). Without ruling records a ruled loss reads
`ruled`. `corrections` is the same join, flat: the correction feed's
payload, the asserter in it (records-and-anchoring §6)."""

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


def corrections(asserted: list, refuted: list) -> list:
    """`Refuted` joined to `Asserted` on `id`, in the order refuted: each a
    correction with who asserted it and what it lost."""
    by_id = {e["id"]: e for e in asserted}
    out = []
    for r in sorted(refuted, key=lambda e: (e["time"], e["id"])):
        a = by_id.get(r["id"])
        if a is None:
            continue                     # an event from another contract, or a truncated read: nothing to join
        out.append({"id": r["id"], "subject": r["subject"], "asserter": a["asserter"], "bond": a["bond"],
                    "confidence": a["confidence"], "ruled": r["ruled"], "time": r["time"]})
    return out


PROCEDURAL = ("specific", "B1", "A2")


def _kind(c: dict, rulings: dict | None) -> str:
    if not c["ruled"]:
        return "conceded"
    rec = (rulings or {}).get(c["id"])
    if rec is None:
        return "ruled"
    rule = rec.reason.split(":", 1)[0]
    return "silent" if rule == "A5" else "procedural" if rule in PROCEDURAL else "refuted"


def loss_view(asserted: list, refuted: list, *, now: int | None = None, max_loss_age: int | None = None,
              rulings: dict | None = None) -> dict:
    """Per asserter, its losses within the look-back (`max_loss_age`
    seconds before `now`): each entry with its kind, and the bond lost in
    all, an absolute sum and never a rate. `rulings` maps an assertion id
    to its `RulingRecord`, where one was published."""
    out: dict = {}
    for c in corrections(asserted, refuted):
        if not _recent(c["time"], now, max_loss_age):
            continue
        row = out.setdefault(c["asserter"], {"losses": [], "bond_lost": 0})
        row["losses"].append({**{k: c[k] for k in ("id", "subject", "bond", "confidence", "time")},
                              "kind": _kind(c, rulings)})
        row["bond_lost"] += c["bond"]
    return out


def loss_view_from_chain(client, *, from_block: int = 0, now: int | None = None, max_loss_age: int | None = None,
                         rulings: dict | None = None) -> dict:
    """`loss_view` over an `AssertionsClient`'s events."""
    return loss_view(client.events("Asserted", from_block), client.events("Refuted", from_block), now=now,
                     max_loss_age=max_loss_age, rulings=rulings)
