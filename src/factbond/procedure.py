"""The adjudicator's path (step F4 of the development sequence, 2026-09-28;
`assertion-extensions.md` §3, `credentials-cover-and-options.md` D2 with
A2, A5 and B1). These are the rules a rung applies before it weighs any
evidence, as pure functions of the case file and the clock. `Assertions.sol`
knows none of them (D2: the contract gains the windows and the escalation
value, nothing else); the adjudicator's key applies them and carries the
decision to chain with `rule`.

- **Specific and refutable.** A contest names a claim record the pinned
  policy covers. For a dispute of a live assertion, that is the claim the
  assertion asserts. A label ("fraudster") is not a claim record, so it is
  refused: it cannot be adjudicated, and it would be defamation on a
  permanent public store (THREATS T17).
- **Notice and cure, for a claim on a reservation** (B1, A2; scoped by
  Peter, 2026-09-28). The claimant relied on the giver and lost, and a cure
  (delivery, a refund, a correction) can make it whole, so the claim cites
  a prior notice from the claimant to the giver about the same fact. The
  notice's cure deadline must have passed, the claim must come before the
  notice expires, and the giver must not have cured in time, unless the
  claimant contests the cure. The notice and the cure pass between the
  parties (loopmarket's `notice/` sidecar) and reach a public store only as
  part of a claim's case file, so a cured matter leaves nothing public
  through this path. A dispute of a live assertion takes no notice: the
  challenger is usually a hunter with no loss to cure, a cure would let the
  asserter keep its bond and leave her unpaid, and the dispute on chain is
  itself the notice to an asserter that posted a bonded public claim. Its
  cheap ending is the asserter's `concede`.
- **Silence counts only after notice, and only through a ruling** (D2,
  A5). For a class that shifts the burden, the accused delivers evidence
  within the evidence period from the bonded act. If none has arrived when
  the period lapses, the rung rules against the accused, ex parte, on the
  record. The accused was notified either way: by the notice before a claim
  on its reservation, or as a party to the contest on chain. Evidence that
  arrives late is still weighed, and the case goes to the merits with
  `late_evidence` set: B5 then returns E to the challenger even if the
  claim holds.

Whatever is left goes to the merits: the rung weighs the evidence, which
is outside this module. The decision names the rule it applied, and F6's
ruling record takes it as its `reason`.

The contest's shapes (D2): a **dispute** of a live assertion, where the
accuser is the on-chain challenger and the accused the asserter; a
**claim** against the accused's reservation (loopmarket's escrow, D1),
where the accuser is the on-chain asserter and the accused, the giver,
disputes it; and a **bonded negation** about a key that asserted nothing,
an ordinary assertion the accused disputes. Only the claim names a
`reservation`, so only it takes the notice step. `Decision.upheld` maps a
decision to `rule`'s argument for each shape."""

from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass

from .policy import PolicyDocument, canonical_bytes

REFUSED, PENDING, EX_PARTE, MERITS = "refused", "pending", "ex-parte", "merits"


def _ref(rec) -> str:
    return hashlib.sha256(canonical_bytes(asdict(rec))).hexdigest()


@dataclass(frozen=True)
class Notice:
    """Rung zero (B1): the accuser tells the accused which fact is wrong and
    gives it until `cure_deadline` to cure (to deliver, refund or correct)."""
    notifier: str
    accused: str
    referred_fact: str          # the claim ref the notice is about
    policy_ref: str
    sent_at: int
    cure_deadline: int          # at least `sent_at` plus the class's cure period
    v: int = 1
    kind: str = "notice"

    @property
    def ref(self) -> str:
        return _ref(self)


@dataclass(frozen=True)
class Cure:
    """The accused's answer to a notice: what it did (a refund's transaction,
    the corrected statement), by reference."""
    notice_ref: str
    author: str
    time: int
    evidence_ref: str = ""
    v: int = 1
    kind: str = "cure"

    @property
    def ref(self) -> str:
        return _ref(self)


@dataclass(frozen=True)
class Submission:
    """Evidence delivered to the rung. It is disclosed to every rung on the
    path, and its hash is public (D2)."""
    author: str
    time: int
    evidence_ref: str
    v: int = 1
    kind: str = "submission"

    @property
    def ref(self) -> str:
        return _ref(self)


@dataclass(frozen=True)
class Accusation:
    """The bonded act that opened the contest, as the rung reads it: who
    accuses whom of what, when, citing which notices."""
    accuser: str
    accused: str
    referred_fact: str          # the claim ref at issue
    time: int                   # when the bonded act was made (the dispute, or the claim's assertion)
    notice_refs: tuple = ()
    contests_cure: bool = False  # the accuser says a cure on record did not cure


@dataclass(frozen=True)
class Case:
    """The case file. `claim` is the referred fact's claim record (the
    records-and-anchoring §1 shape, `factbond.sim.records.Claim`), or None
    when the accusation names no claim record. `disputed_claim` is set for a
    dispute of a live assertion: the claim that assertion asserts.
    `reservation` names the reservation a claim is routed from (the escrow's
    key), and only a claim that names one takes the notice step."""
    policy: PolicyDocument
    accusation: Accusation
    claim: object = None
    notices: tuple = ()
    cures: tuple = ()
    submissions: tuple = ()
    disputed_claim: str | None = None
    reservation: str | None = None


@dataclass(frozen=True)
class Decision:
    kind: str                   # refused | pending | ex-parte | merits
    against: str | None         # accuser | accused, when the procedure alone decides
    rule: str                   # the rule applied: specific, B1, A2, A5, merits
    reason: str
    notice_ref: str = ""        # the notice that opened the bonded stage (for the ruling record, C5)
    late_evidence: bool = False  # B5: E returns to the challenger even if the claim holds

    def upheld(self, accuser_is_asserter: bool) -> bool | None:
        """`Assertions.rule`'s `upheld` for this decision, or None when the
        merits decide or the clock has not run. A claim's accuser is the
        on-chain asserter; a dispute's accuser is the challenger."""
        if self.against is None:
            return None
        return (self.against == "accused") if accuser_is_asserter else (self.against == "accuser")


def _refused(rule: str, reason: str) -> Decision:
    return Decision(REFUSED, "accuser", rule, reason)


def _specific(case: Case) -> str:
    """Why the accusation is not specific and refutable, or ''."""
    acc, claim, policy = case.accusation, case.claim, case.policy
    if claim is None:
        return "the accusation names no claim record: a label is not a dispute"
    if getattr(claim, "claim_id", None) != acc.referred_fact:
        return "the referred fact is not the claim record in the case file"
    if claim.policy_ref != policy.policy_ref:
        return "the claim pins another policy"
    if claim.claim_type not in {c.claim_type for c in policy.classes}:
        return f"the policy has no {claim.claim_type!r} class to adjudicate it under"
    if case.disputed_claim is not None and acc.referred_fact != case.disputed_claim:
        return "a dispute names the fact its assertion asserts"
    return ""


def _notice_faults(case: Case, n: Notice, rule) -> list[str]:
    acc = case.accusation
    faults = []
    if n.notifier != acc.accuser:
        faults.append("the notice is not the accuser's")
    if n.accused != acc.accused:
        faults.append("the notice went to another key")
    if n.referred_fact != acc.referred_fact or n.policy_ref != case.policy.policy_ref:
        faults.append("the notice names another fact")
    if n.cure_deadline < n.sent_at + rule.cure_period:
        faults.append("the notice gave less than the cure period")
    if acc.time <= n.cure_deadline:
        faults.append("the cure deadline had not passed")
    if acc.time > n.sent_at + rule.notice_expiry:
        faults.append("the notice had expired (A2)")
    cured = any(c.notice_ref == n.ref and c.author == acc.accused and c.time <= n.cure_deadline
                for c in case.cures)
    if cured and not acc.contests_cure:
        faults.append("the accused cured within the deadline")
    return faults


def decide(case: Case, now: int) -> Decision:
    """What the procedure alone decides about `case` at `now`."""
    if why := _specific(case):
        return _refused("specific", why)
    acc = case.accusation
    rule = case.policy.rule(case.claim.claim_type)
    notice = None
    if case.reservation is not None:                       # a claim on a reservation: the notice step
        cited = [n for n in case.notices if n.ref in acc.notice_refs]
        if not cited:
            return _refused("B1", "no notice to the giver precedes the claim on its reservation")
        faults = {n.ref: _notice_faults(case, n, rule) for n in cited}
        notice = next((n for n in cited if not faults[n.ref]), None)
        if notice is None:
            listed = sorted({f for fs in faults.values() for f in fs})
            only_expiry = listed == ["the notice had expired (A2)"]
            return _refused("A2" if only_expiry else "B1", "; ".join(listed))
    ref = notice.ref if notice else ""
    if rule.burden_shifts:
        # the accused was notified: by the notice before a claim, or as a party to the contest on chain
        due = acc.time + rule.evidence_period
        evidence = [s for s in case.submissions if s.author == acc.accused]
        if not evidence:
            if now <= due:
                return Decision(PENDING, None, "A5", f"the accused's evidence period runs until {due}", ref)
            return Decision(EX_PARTE, "accused", "A5",
                            "the accused, notified, produced no evidence in the evidence period: ruled on the "
                            "record", ref)
        late = all(s.time > due for s in evidence)
        return Decision(MERITS, None, "merits", "the accused's evidence is on the record", ref, late)
    return Decision(MERITS, None, "merits", "admissible: the burden is the accuser's", ref)


# ---- the ruling record (F6; D2's C5; records-and-anchoring §2) ----------------

OUTCOMES = ("upheld", "refuted")


@dataclass(frozen=True)
class RulingRecord:
    """A ruling as a record: what makes a fast ruling survive challenge
    (the referred fact, the notices it rests on) and what makes it reusable
    as precedent (the category and the versions applied, the rule named).
    `notices` carries each cited notice as (ref, sent_at, cure_deadline); it
    is empty only for a contest that took no notice step (no
    `reservation`). `submissions` carries both parties' evidence hashes, or
    ("lapse",) where none came. `supersedes` names the ruling below when the
    arbiter rules on appeal."""
    dispute_ref: str             # the contest ruled: the assertion id on chain, or the dispute record's ref
    adjudicator: str             # the resolver's key
    rung: int                    # 0: the first rung; 1: the arbiter, on appeal
    outcome: str                 # upheld | refuted, the disputed assertion's fate
    referred_fact: str           # the claim ref ruled on
    notices: tuple
    reservation: str | None
    submissions: tuple
    category: str                # the claim type ruled under ("" where the contest named no claim)
    policy_version: str          # the policy ref applied
    pack_root: str               # the vocabulary pack's root the claim was read against
    reason: str                  # the rule applied, named
    time: int
    supersedes: str = ""
    v: int = 1
    kind: str = "ruling"

    @property
    def ref(self) -> str:
        return _ref(self)

    def to_record(self) -> dict:
        rec = asdict(self)
        rec["notices"] = [list(n) for n in self.notices]
        rec["submissions"] = list(self.submissions)
        return rec

    @classmethod
    def from_record(cls, rec: dict) -> "RulingRecord":
        """A record that is not a ruling does not load: one missing its
        referred fact, its notices (where the contest took the notice step),
        its submissions or the lapse, or the rule it applied."""
        from .policy import CLAIM_TYPES, PolicyError
        need = {"dispute_ref", "adjudicator", "rung", "outcome", "referred_fact", "notices", "reservation",
                "submissions", "category", "policy_version", "pack_root", "reason", "time"}
        if missing := need - rec.keys():
            raise PolicyError(f"not a ruling: it lacks {sorted(missing)}")
        if not rec["referred_fact"]:
            raise PolicyError("not a ruling: it names no referred fact")
        if rec["reservation"] and not rec["notices"]:
            raise PolicyError("not a ruling: a claim on a reservation rests on notices it does not cite")
        if not rec["submissions"]:
            raise PolicyError("not a ruling: it records neither submissions nor their lapse")
        if not rec["reason"]:
            raise PolicyError("not a ruling: it names no rule")
        if rec["outcome"] not in OUTCOMES or rec["rung"] not in (0, 1):
            raise PolicyError("not a ruling: the outcome is upheld or refuted, the rung 0 or 1")
        if rec["category"] and rec["category"] not in CLAIM_TYPES:
            raise PolicyError(f"not a ruling: no claim type {rec['category']!r}")
        if not rec["policy_version"] or not rec["dispute_ref"] or not rec["adjudicator"]:
            raise PolicyError("not a ruling: it names the contest, the adjudicator and the policy applied")
        fields = {k: rec[k] for k in need | {"supersedes", "v", "kind"} if k in rec}
        fields["notices"] = tuple(tuple(n) for n in rec["notices"])
        fields["submissions"] = tuple(rec["submissions"])
        return cls(**fields)


def ruling_record(case: Case, decision: Decision, *, adjudicator: str, outcome: str, time: int,
                  dispute_ref: str, rung: int = 0, pack_root: str = "", supersedes: str = "") -> RulingRecord:
    """The record of a ruling on `case`, the procedure's `decision` naming
    the rule. A contest that named no claim record (a label) is recorded by
    the hash of what it said, so the ruling never repeats the label."""
    acc = case.accusation
    referred = case.claim.claim_id if case.claim is not None else \
        hashlib.sha256(acc.referred_fact.encode("utf-8")).hexdigest()
    cited = [n for n in case.notices if n.ref in acc.notice_refs]
    notices = tuple((n.ref, n.sent_at, n.cure_deadline) for n in cited)
    submissions = tuple(s.evidence_ref for s in case.submissions) or ("lapse",)
    category = case.claim.claim_type if case.claim is not None else ""
    return RulingRecord.from_record(RulingRecord(
        dispute_ref, adjudicator, rung, outcome, referred, notices, case.reservation, submissions, category,
        case.policy.policy_ref, pack_root, f"{decision.rule}: {decision.reason}", time, supersedes).to_record())
