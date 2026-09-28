"""Evidence policy as data (`docs/plans/evidence-policy.md` §1–§2 and §6;
`credentials-cover-and-options.md` D2 and D10; step F3 of the development
sequence, 2026-09-28). A policy document is per domain and
content-addressed: its hash is the `policy_ref` a claim pins, the contract
its disputes run under. For each fact-type class it names the clocks, the
costs and the judges. The shapes are fixed here; the numbers are
placeholders until the first real disputes and the Phase-0 harness, and
they are tuned in policy records, never in code.

A document that breaks a rule the plans fixed does not load:

- every class names a **final rung**, a named and bonded adjudicator or
  panel, never a token vote (D2's C2). A class without one may not back a
  `requires` gate, so it is refused here, before anything reads it;
- a structural class (`attribute-matches-source`) settles by certificate
  alone (F8), and a certificate is rung zero or nothing;
- only `self-knowable` shifts the burden, and only it has an **evidence
  period** (A5);
- every rung has a **ruling period** (A3); every class has a **notice with a
  cure deadline** (B1), a **finality window** (A4) and a **challenger cap**
  k < 1 of the reserved slice (B3);
- the **escalation value** is a share of the outcome in bps or
  `"unresolved"` (D10), which is what `Assertions.assert_` takes as
  `escalation` (`ClassRule.escalation_arg`).

The `suspended/` register record (D2) is here too. It is the view entry an
issuer's register (for a self-bonded statement, the giver's own book)
carries from the lapse of a self-knowable claim's evidence period until its
ruling; loopmarket's gate reads its presence as "meets nothing"
(`counterparty-gate.md` §4 step 7). `suspended()` derives when one is due
from the dispute's facts and the clock alone, as status always is
(`records-and-anchoring.md` §3)."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field

from .assertions import UNRESOLVED

#: the claim-type vocabulary (`records-and-anchoring.md` §1), with the
#: class D2 added for facts the asserter can prove and a challenger may not
#: be able to disprove
CLAIM_TYPES = ("attribute-matches-source", "attribute-matches-world", "entity-exists", "self-knowable")

#: who sits at a rung (mechanism-design §4; D2's C3 adjudicator class):
#: the proof checker, a bot over the policy, holders of the same credential
#: under the same root, the issuer's register itself, one named key, a named
#: panel. There is no token vote to name.
ADJUDICATORS = ("certificate", "automated", "peers", "register", "key", "panel")

#: what a final rung may be: someone to name at policy start, bond and remove
NAMED = ("key", "panel")

#: evidence weights, ordinal to start (evidence-policy.md, "weight semantics")
WEIGHTS = ("sole", "corroboration", "dispute-input")


class PolicyError(ValueError):
    """A policy document that does not load, with the rule it breaks."""


def canonical_bytes(obj) -> bytes:
    """recordstore's canonical encoding (equal values, equal bytes), kept here
    so that factbond stays dependency-free."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                      allow_nan=False).encode("utf-8")


def _count(value, what: str, *, positive: bool = False) -> int:
    if type(value) is not int or value < (1 if positive else 0):
        raise PolicyError(f"{what} is a {'positive' if positive else 'non-negative'} integer, not {value!r}")
    return value


def _fields(rec: dict, required: set, optional: set, what: str) -> None:
    if not isinstance(rec, dict):
        raise PolicyError(f"{what} is a record, not {type(rec).__name__}")
    if missing := required - rec.keys():
        raise PolicyError(f"{what} lacks {sorted(missing)}")
    if unknown := rec.keys() - required - optional:
        raise PolicyError(f"{what} has unknown fields {sorted(unknown)}: a policy is a contract, so a new "
                          "field comes with a new version")


@dataclass(frozen=True)
class Rung:
    """One rung of a class's escalation path. Amounts are in the document's
    `unit`, periods in seconds."""
    name: str                   # the ladder's name for it: certificate, automated, panel, arbitrator, ...
    adjudicator: str            # one of ADJUDICATORS
    ruling_period: int          # A3: at lapse the claim moves up and this rung forfeits its fee
    id: str = ""                # the key, panel, bot, or credential@root the peers hold
    fee: int = 0                # paid per ruling (C3)
    deposit: int = 0            # at risk on a reversal at the final rung (C3)
    admits: dict = field(default_factory=dict)  # evidence class ref -> weight

    def to_record(self) -> dict:
        return {"name": self.name, "adjudicator": self.adjudicator, "ruling_period": self.ruling_period,
                "id": self.id, "fee": self.fee, "deposit": self.deposit, "admits": dict(self.admits)}

    @classmethod
    def from_record(cls, rec: dict) -> "Rung":
        _fields(rec, {"name", "adjudicator", "ruling_period"}, {"id", "fee", "deposit", "admits"}, "a rung")
        rung = cls(rec["name"], rec["adjudicator"], rec["ruling_period"], rec.get("id", ""),
                   rec.get("fee", 0), rec.get("deposit", 0), dict(rec.get("admits", {})))
        rung.check()
        return rung

    def check(self) -> None:
        where = f"rung {self.name!r}"
        if not isinstance(self.name, str) or not self.name:
            raise PolicyError("a rung has a name")
        if self.adjudicator not in ADJUDICATORS:
            raise PolicyError(f"{where}: the adjudicator is one of {ADJUDICATORS}, never a token vote "
                              f"(D2's C2), not {self.adjudicator!r}")
        if not isinstance(self.id, str):
            raise PolicyError(f"{where}: the id is a string")
        if self.adjudicator not in ("certificate", "register") and not self.id:
            raise PolicyError(f"{where}: a {self.adjudicator} rung names who sits there")
        _count(self.ruling_period, f"{where}: the ruling period (A3)", positive=True)
        _count(self.fee, f"{where}: the fee")
        _count(self.deposit, f"{where}: the deposit")
        if not isinstance(self.admits, dict):
            raise PolicyError(f"{where}: admits maps evidence classes to weights")
        for cls_, weight in self.admits.items():
            if not isinstance(cls_, str) or not cls_ or weight not in WEIGHTS:
                raise PolicyError(f"{where}: admits {cls_!r} at {weight!r}; weights are {WEIGHTS}")


@dataclass(frozen=True)
class ClassRule:
    """What a dispute on one fact-type class runs under. Periods in seconds,
    amounts in the document's `unit`."""
    claim_type: str
    rungs: tuple                # of Rung, cheap to expensive; the last is the final rung
    cure_period: int            # B1: the notice's cure deadline, before any bonded dispute
    finality_window: int        # A4: reopen on new evidence, or at double the stake, until it ends
    cap_bps: int                # B3: stake plus evidence fee at most this share of the reserved slice
    escalation: int | str       # D10: bps of the outcome resolved when no ruling comes, or "unresolved"
    evidence_period: int | None = None  # A5: the asserter's time to produce evidence (self-knowable only)
    evidence_fee: int = 0       # E: the challenger's, beside its stake; to the asserter if the claim holds

    @property
    def burden_shifts(self) -> bool:
        return self.claim_type == "self-knowable"

    @property
    def final_rung(self) -> Rung:
        return self.rungs[-1]

    def escalation_arg(self) -> int:
        """The value `Assertions.assert_` takes as `escalation`."""
        return UNRESOLVED if self.escalation == "unresolved" else self.escalation

    def to_record(self) -> dict:
        return {"rungs": [r.to_record() for r in self.rungs], "cure_period": self.cure_period,
                "finality_window": self.finality_window, "cap_bps": self.cap_bps,
                "escalation": self.escalation, "evidence_period": self.evidence_period,
                "evidence_fee": self.evidence_fee}

    @classmethod
    def from_record(cls, claim_type: str, rec: dict) -> "ClassRule":
        _fields(rec, {"rungs", "cure_period", "finality_window", "cap_bps", "escalation"},
                {"evidence_period", "evidence_fee"}, f"class {claim_type!r}")
        if not isinstance(rec["rungs"], list):
            raise PolicyError(f"class {claim_type!r}: rungs is a list")
        rule = cls(claim_type, tuple(Rung.from_record(r) for r in rec["rungs"]), rec["cure_period"],
                   rec["finality_window"], rec["cap_bps"], rec["escalation"], rec.get("evidence_period"),
                   rec.get("evidence_fee", 0))
        rule.check()
        return rule

    def check(self) -> None:
        where = f"class {self.claim_type!r}"
        if self.claim_type not in CLAIM_TYPES:
            raise PolicyError(f"the claim type is one of {CLAIM_TYPES}, not {self.claim_type!r}")
        if not self.rungs:
            raise PolicyError(f"{where} names no rungs, so no final rung (D2's C2)")
        for r in self.rungs:
            r.check()
        _count(self.cure_period, f"{where}: the cure period (B1)", positive=True)
        _count(self.finality_window, f"{where}: the finality window (A4)")
        if type(self.cap_bps) is not int or not 0 < self.cap_bps < 10000:
            raise PolicyError(f"{where}: the challenger cap is a share k < 1 of the reserved slice, "
                              f"in bps (B3), not {self.cap_bps!r}")
        if self.escalation != "unresolved" and (type(self.escalation) is not int
                                                 or not 0 <= self.escalation <= 10000):
            raise PolicyError(f"{where}: the escalation value is bps of the outcome or 'unresolved' (D10), "
                              f"not {self.escalation!r}")
        _count(self.evidence_fee, f"{where}: the evidence fee")
        if self.burden_shifts:
            if self.evidence_period is None:
                raise PolicyError(f"{where} shifts the burden, so it names an evidence period (A5)")
            _count(self.evidence_period, f"{where}: the evidence period (A5)", positive=True)
        elif self.evidence_period is not None:
            raise PolicyError(f"{where}: only a self-knowable class shifts the burden, so only it has an "
                              "evidence period")
        if any(r.adjudicator == "certificate" for r in self.rungs[1:]):
            raise PolicyError(f"{where}: a certificate is rung zero or nothing")
        if self.claim_type == "attribute-matches-source":
            if [r.adjudicator for r in self.rungs] != ["certificate"]:
                raise PolicyError(f"{where}: a structural claim settles by certificate alone (F8)")
            return
        final = self.final_rung
        if final.adjudicator not in NAMED or final.deposit <= 0:
            raise PolicyError(f"{where} names no final rung: its last rung must be a named key or panel "
                              f"with a deposit (D2's C2), not a {final.adjudicator} with deposit {final.deposit}")


@dataclass(frozen=True)
class PolicyDocument:
    """One domain's policy (evidence-policy.md §2): the classes its claims
    may take and what a dispute on each runs under. `unit` is what every
    amount counts, in its smallest unit (e.g. `eip155:100/slip44:700`, wei
    of xDAI on Gnosis)."""
    domain: str
    unit: str
    classes: tuple              # of ClassRule, one per claim type
    ext: dict = field(default_factory=dict)
    v: int = 1

    def rule(self, claim_type: str) -> ClassRule:
        for c in self.classes:
            if c.claim_type == claim_type:
                return c
        raise KeyError(f"{self.domain} has no {claim_type!r} class")

    def to_record(self) -> dict:
        return {"v": self.v, "domain": self.domain, "unit": self.unit, "ext": dict(self.ext),
                "classes": {c.claim_type: c.to_record() for c in self.classes}}

    def canonical_bytes(self) -> bytes:
        return canonical_bytes(self.to_record())

    @property
    def policy_ref(self) -> str:
        """The content address a claim pins: SHA-256 of the canonical encoding."""
        return hashlib.sha256(self.canonical_bytes()).hexdigest()

    @classmethod
    def from_record(cls, rec: dict) -> "PolicyDocument":
        _fields(rec, {"v", "domain", "unit", "classes"}, {"ext"}, "a policy document")
        if rec["v"] != 1:
            raise PolicyError(f"unknown policy version {rec['v']!r}")
        if not isinstance(rec["classes"], dict) or not rec["classes"]:
            raise PolicyError("a policy document names at least one class")
        doc = cls(rec["domain"], rec["unit"],
                  tuple(ClassRule.from_record(t, c) for t, c in sorted(rec["classes"].items())),
                  dict(rec.get("ext", {})), rec["v"])
        doc.check()
        return doc

    def check(self) -> None:
        if not isinstance(self.domain, str) or not self.domain or not isinstance(self.unit, str) or not self.unit:
            raise PolicyError("a policy document names its domain and its unit")
        if not isinstance(self.ext, dict):
            raise PolicyError("ext is a record")
        types = [c.claim_type for c in self.classes]
        if len(set(types)) != len(types):
            raise PolicyError("one rule per class")
        for c in self.classes:
            c.check()


def load(data: bytes, ref: str | None = None) -> PolicyDocument:
    """A policy document from its bytes. With `ref`, the pin: the bytes must
    hash to it and be the canonical encoding, so that one ref names exactly
    one spelling of one policy (evidence-policy.md §6)."""
    try:
        rec = json.loads(data)
    except (ValueError, UnicodeDecodeError) as exc:
        raise PolicyError(f"a policy document is JSON: {exc}") from exc
    doc = PolicyDocument.from_record(rec)
    if ref is not None:
        if hashlib.sha256(data).hexdigest() != ref:
            raise PolicyError("the bytes do not hash to the pinned ref")
        if data != doc.canonical_bytes():
            raise PolicyError("a pinned policy is in canonical encoding")
    return doc


def shipped(name: str) -> PolicyDocument:
    """A policy document shipped with the package (`factbond/policies/`),
    placeholders to code against until real ones are published."""
    from importlib import resources
    return load(resources.files("factbond").joinpath("policies", f"{name}.json").read_bytes())


# ---- the suspended/ register record (D2) ------------------------------------

@dataclass(frozen=True)
class Suspension:
    """`suspended/<statement>` in the issuer's register: a self-knowable
    claim was disputed and its evidence period lapsed with no evidence. It
    leaves the register's view when the claim is ruled, and its history
    stays in the log (D7's G1)."""
    statement: str              # the statement id the gate would otherwise admit
    dispute_ref: str            # the dispute whose evidence period lapsed
    policy_ref: str             # the policy document the claim pinned
    evidence_due: int           # unix seconds: the dispute's time plus the class's evidence period
    v: int = 1

    @property
    def key(self) -> str:
        return f"suspended/{self.statement}"

    def to_record(self) -> dict:
        return {"v": self.v, "statement": self.statement, "dispute_ref": self.dispute_ref,
                "policy_ref": self.policy_ref, "evidence_due": self.evidence_due}

    @classmethod
    def from_record(cls, rec: dict) -> "Suspension":
        _fields(rec, {"v", "statement", "dispute_ref", "policy_ref", "evidence_due"}, set(), "a suspension")
        if rec["v"] != 1:
            raise PolicyError(f"unknown suspension version {rec['v']!r}")
        for k in ("statement", "dispute_ref", "policy_ref"):
            if not isinstance(rec[k], str) or not rec[k]:
                raise PolicyError(f"a suspension names its {k}")
        return cls(rec["statement"], rec["dispute_ref"], rec["policy_ref"],
                   _count(rec["evidence_due"], "evidence_due"), rec["v"])


def evidence_due(rule: ClassRule, disputed_at: int) -> int:
    """When the asserter's evidence is due: the dispute's time plus the
    class's evidence period."""
    if not rule.burden_shifts:
        raise ValueError(f"a {rule.claim_type} claim does not shift the burden")
    return disputed_at + rule.evidence_period


def suspended(rule: ClassRule, disputed_at: int, now: int, *, evidence_at: int | None = None,
              ruled_at: int | None = None) -> bool:
    """D2: a disputed self-knowable claim is suspended from the lapse of
    its evidence period until it is ruled, unless the evidence arrived in
    time. Late evidence does not lift the suspension; only the ruling does,
    since silence moves nothing except through a ruling. No other class is
    ever suspended."""
    if not rule.burden_shifts:
        return False
    due = evidence_due(rule, disputed_at)
    if evidence_at is not None and evidence_at <= due:
        return False
    return due < now and (ruled_at is None or now < ruled_at)
