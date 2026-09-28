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
- **Rung zero: notice and cure** (B1, A2). Where the class has rung zero,
  the bonded act cites a prior notice from the accuser to the accused about
  the same fact. The notice's cure deadline must have lapsed, the act must
  come before the notice expires, and the accused must not have cured in
  time, unless the accuser contests the cure. The notice and the cure pass
  between the parties (loopmarket's `notice/` sidecar); they reach a public
  store only as part of a bonded act's case file. A cure within the
  deadline makes every act citing that notice inadmissible, so a cured
  matter leaves nothing public through this path.
- **Silence counts only after notice, and only through a ruling** (D2,
  A5). For a class that shifts the burden, the accused delivers evidence
  within the evidence period from the bonded act. If none has arrived when
  the period lapses, the rung rules against the accused, ex parte, on the
  record. The policy gives every such class rung zero, so an accused who
  was never notified cannot reach that ruling. Evidence that arrives late
  is still weighed, and the case goes to the merits with `late_evidence`
  set: B5 then returns E to the challenger even if the claim holds.

Whatever is left goes to the merits: the rung weighs the evidence, which
is outside this module. The decision names the rule it applied, and F6's
ruling record takes it as its `reason`.

The contest's two shapes (D2): a **dispute** of a live assertion, where
the accuser is the on-chain challenger and the accused the asserter; and a
**claim** against the accused's reservation (loopmarket's escrow, D1),
where the accuser is the on-chain asserter and the accused, the giver,
disputes it. `Decision.upheld` maps a decision to `rule`'s argument for
either shape."""

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
    dispute of a live assertion: the claim that assertion asserts."""
    policy: PolicyDocument
    accusation: Accusation
    claim: object = None
    notices: tuple = ()
    cures: tuple = ()
    submissions: tuple = ()
    disputed_claim: str | None = None


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
    if rule.cure_period:
        cited = [n for n in case.notices if n.ref in acc.notice_refs]
        if not cited:
            return _refused("B1", "no notice to the accused precedes the bonded act")
        faults = {n.ref: _notice_faults(case, n, rule) for n in cited}
        notice = next((n for n in cited if not faults[n.ref]), None)
        if notice is None:
            listed = sorted({f for fs in faults.values() for f in fs})
            only_expiry = listed == ["the notice had expired (A2)"]
            return _refused("A2" if only_expiry else "B1", "; ".join(listed))
    ref = notice.ref if notice else ""
    if rule.burden_shifts:
        # reached only through a valid notice: the policy gives every burden-shifting class rung zero
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
