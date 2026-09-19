"""The speech-act records the harness is the first consumer of
(`records-and-anchoring.md` §1–§3): claims are unsigned content, assertions,
disputes, rulings and retractions are speech acts keyed by content hash,
and status is a pure function of the folded records plus a clock (F1) —
never stored. The simulation's own bookkeeping reads status through
`status()`, so a schema mistake surfaces here, not on a testnet."""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from dataclasses import asdict, dataclass, field

CLAIM_TYPES = ("attribute-matches-source", "attribute-matches-world", "entity-exists")


def content_hash(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


@dataclass(frozen=True)
class Claim:
    subject: str
    basis_root: str
    claim_type: str
    policy_ref: str
    v: int = 1

    @property
    def claim_id(self) -> str:
        return content_hash(asdict(self))


@dataclass(frozen=True)
class Assertion:
    claim_ref: str
    author: str
    confidence: int          # per mille: 900, 970, 990, 999
    bond: float
    liveness: int            # ticks after `time` a dispute may open
    time: int
    kind: str = "assertion"

    @property
    def ref(self) -> str:
        return content_hash(asdict(self))


@dataclass(frozen=True)
class Dispute:
    assertion_ref: str
    challenger: str
    stake: float
    time: int
    kind: str = "dispute"

    @property
    def ref(self) -> str:
        return content_hash(asdict(self))


@dataclass(frozen=True)
class Ruling:
    dispute_ref: str
    adjudicator: str
    outcome: str             # upheld | refuted
    rung: int
    time: int
    supersedes: str = ""
    kind: str = "ruling"

    @property
    def ref(self) -> str:
        return content_hash(asdict(self))


@dataclass(frozen=True)
class Retraction:
    assertion_ref: str
    author: str
    time: int
    kind: str = "retraction"

    @property
    def ref(self) -> str:
        return content_hash(asdict(self))


@dataclass
class Fold:
    """The union of records a reader holds — order-free, so two folds of the
    same records derive the same status (Gate G-REC1)."""
    assertions: dict = field(default_factory=dict)   # ref -> Assertion
    disputes: dict = field(default_factory=dict)     # ref -> Dispute
    rulings: dict = field(default_factory=dict)      # ref -> Ruling
    retractions: dict = field(default_factory=dict)  # ref -> Retraction
    # derived indexes (never merged, always recomputable): what `status` walks
    by_claim: dict = field(default_factory=lambda: defaultdict(list))      # claim_ref -> [Assertion]
    by_assertion: dict = field(default_factory=lambda: defaultdict(list))  # assertion_ref -> [Dispute]
    by_dispute: dict = field(default_factory=lambda: defaultdict(list))    # dispute_ref -> [Ruling]
    retracted: set = field(default_factory=set)

    def add(self, rec) -> str:
        table = {"assertion": self.assertions, "dispute": self.disputes,
                 "ruling": self.rulings, "retraction": self.retractions}[rec.kind]
        if rec.ref in table:
            return rec.ref
        table[rec.ref] = rec
        if rec.kind == "assertion":
            self.by_claim[rec.claim_ref].append(rec)
        elif rec.kind == "dispute":
            self.by_assertion[rec.assertion_ref].append(rec)
        elif rec.kind == "ruling":
            self.by_dispute[rec.dispute_ref].append(rec)
        else:
            self.retracted.add(rec.assertion_ref)
        return rec.ref

    def union(self, other: "Fold") -> "Fold":
        out = Fold()
        for f in (self, other):
            for table in (f.assertions, f.disputes, f.rulings, f.retractions):
                for rec in table.values():
                    out.add(rec)
        return out


UNASSERTED, ASSERTED, CONTESTED, CERTIFIED, REFUTED, EXPIRED = (
    "Unasserted", "Asserted", "Contested", "Certified", "Refuted", "Expired")


def status(fold: Fold, claim_id: str, now: int, validity_end: int | None = None) -> str:
    """F1: the status of a claim from the folded speech acts and the clock.
    The latest standing assertion on the claim decides; rulings are ordered
    by (rung, time, supersedes chain) — the last one stands."""
    if validity_end is not None and now > validity_end:
        return EXPIRED
    live = [a for a in fold.by_claim.get(claim_id, ()) if a.ref not in fold.retracted]
    if not live:
        return UNASSERTED
    a = max(live, key=lambda x: (x.time, x.ref))
    disputes = fold.by_assertion.get(a.ref, ())
    if not disputes:
        return CERTIFIED if now > a.time + a.liveness else ASSERTED
    d = max(disputes, key=lambda x: (x.time, x.ref))
    rulings = fold.by_dispute.get(d.ref, ())
    if not rulings:
        return CONTESTED
    superseded = {r.supersedes for r in rulings if r.supersedes}
    standing = [r for r in rulings if r.ref not in superseded]
    r = max(standing, key=lambda x: (x.rung, x.time, x.ref))
    return CERTIFIED if r.outcome == "upheld" else REFUTED
