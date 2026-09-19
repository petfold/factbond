"""The mechanism and its agents (§4–§5), run tick by tick over the world.

The pool asserts every fact it does not refuse (a refusal is signal: facts
with abnormal demand concentration are refused and disputed pre-emptively);
challengers scan facts, verify at cost and dispute the ones they find wrong
when the expected win pays; consumers buy the verification bet and, when the
fact bites, are paid under the cap and the pool auto-files the dispute
(insurance-products.md §6); adjudicators rule with error, or for a price, or
with the crowd; premiums update from the pool's own loss experience from a
cold-start prior; F4 stops sales when exposure would exceed the reserve's
capacity. Money is bookkept per party so ROI panels are exact sums, never
estimates. Everything observable about a claim is read through
`records.status` (F1)."""

from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass, field

from .params import Params
from .records import (ASSERTED, CERTIFIED, CONTESTED, REFUTED, Assertion, Dispute, Fold, Retraction, Ruling,
                      status)
from .world import Fact, World

POOL, TREASURY = "pool", "treasury"


@dataclass
class Ledger:
    """Who has what: every transfer is a pair of entries, so Σ = 0 always
    (the F9 check reads this: nothing is minted for asserting)."""
    balances: dict = field(default_factory=lambda: defaultdict(float))
    minted: float = 0.0

    def move(self, src: str, dst: str, amount: float) -> None:
        self.balances[src] -= amount; self.balances[dst] += amount

    def mint(self, dst: str, amount: float) -> None:
        self.balances[dst] += amount; self.minted += amount


@dataclass
class Adjudicator:
    name: str = "adj"
    kind: str = "honest"        # honest | capturable | conformist
    price: float = 1e12         # a capturable one sells above this
    error: float = 0.02
    captured_by: str = ""

    def rule(self, truth_refuted: bool, rng, majority_says_refuted: bool | None = None) -> bool:
        """True = refuted (the challenger was right)."""
        if self.captured_by:
            return False                          # rules for whoever bought it: uphold
        if self.kind == "conformist" and majority_says_refuted is not None:
            return majority_says_refuted
        return truth_refuted if rng.random() >= self.error else not truth_refuted


@dataclass
class Engine:
    p: Params
    world: World
    fold: Fold = field(default_factory=Fold)
    ledger: Ledger = field(default_factory=Ledger)
    now: int = 0
    adjudicator: Adjudicator = field(default_factory=Adjudicator)
    # what the pool has learned: per-type (policies sold, losses paid)
    sold: dict = field(default_factory=lambda: defaultdict(int))
    losses: dict = field(default_factory=lambda: defaultdict(int))
    paid: dict = field(default_factory=lambda: defaultdict(float))
    exposure: float = 0.0
    sales_stopped: int = 0
    refused: int = 0
    # challengers: name -> (profit, active)
    challengers: dict = field(default_factory=dict)
    disputes_by: dict = field(default_factory=dict)     # dispute ref -> (fact, challenger)
    stats: dict = field(default_factory=lambda: defaultdict(int))
    consumers_hook: list = field(default_factory=list)  # §9: other consumers attach here

    def __post_init__(self):
        self.ledger.mint(POOL, self.p.pool_stake)      # the pool's capital: the one exogenous stake
        for i in range(self.p.challengers):
            self.challengers[f"c{i}"] = [0.0, True]
            self.ledger.mint(f"c{i}", 100.0)             # working capital, not income (F9)
        self.adjudicator = Adjudicator("adj", error=self.p.ruling_error)

    # ---- money helpers --------------------------------------------------------

    def stake_for(self, bond: float, confidence: int) -> float:
        odds = bond * (1000 - confidence) / confidence
        return max(odds, self.p.rung_cost + self.p.delay_externality)

    def premium(self, t: str) -> float:
        """Experience-rated from a cold-start prior (insurance-products §3)."""
        n, k = self.sold[t], self.losses[t]
        rate = (self.p.premium_prior * 20 + k) / (20 + n)  # a prior worth 20 policies
        return rate * self.p.premium_load * self.p.payout_cap

    def capacity(self) -> float:
        return self.ledger.balances[POOL] * self.p.reserve_gearing

    # ---- the tick ---------------------------------------------------------------

    def tick(self, adversaries=()) -> None:
        p, w = self.p, self.world
        self.now += 1
        w.drift(self.now, retire=1.0 / max(1, p.liveness))
        self.assert_all()
        events = w.consume(p, self.now)
        self.consumers(events)
        self.challengers_act()
        self.sweep()
        for adv in adversaries:
            adv.act(self)
        self.settle()
        for hook in self.consumers_hook:
            hook(self)

    def bond_for(self, f: Fact) -> float:
        """mechanism-design §2 clause 1: bond = max(adjudication-cost floor,
        k × the reliance riding on the claim) — a hub claim is expensive to
        assert casually and lucrative to challenge; a cold one stays cheap."""
        return max(self.p.bond_floor, self.p.k_reliance * f.reliance)

    def assert_all(self) -> None:
        """The pool as asserter (§4): every fact without a live assertion gets
        one at the pool's bucket, bond by `bond_for`, fee to the treasury —
        unless the fact is refused (a demand-concentration tripwire). A live
        undisputed assertion whose bond has fallen behind the reliance on it
        is retracted (the fee is the price, §1) and re-asserted at the larger
        bond: the latest assertion stands (F1), so the record itself carries
        the bond's history."""
        p = self.p
        for f in self.world.facts:
            if f.assertion_ref is not None:
                st = status(self.fold, f.claim_id, self.now)
                if st in (CONTESTED, CERTIFIED):
                    continue
                if st == ASSERTED:
                    a = self.fold.assertions[f.assertion_ref]
                    want = self.bond_for(f)
                    if a.author != POOL or want <= a.bond * 1.5:
                        continue
                    self.fold.add(Retraction(a.ref, POOL, self.now))     # top up: retract and re-assert
                    self.ledger.move("escrow", POOL, a.bond)
                    self.stats["topups"] += 1
            if f.consumed > 50 and self.losses[f.type] > self.sold[f.type] * 0.3 + 3:
                self.refused += 1
                continue
            bond = self.bond_for(f)
            if self.ledger.balances[POOL] < bond + p.fee:
                self.stats["pool_short"] += 1
                continue
            a = Assertion(f.claim_id, POOL, p.pool_confidence, bond, p.liveness, self.now)
            self.fold.add(a)
            f.assertion_ref = a.ref
            self.ledger.move(POOL, TREASURY, p.fee)
            self.ledger.move(POOL, "escrow", bond)
            self.stats["assertions"] += 1

    def consumers(self, events) -> None:
        """Honest and informed buyers of the verification bet; a paid claim
        auto-files the dispute the pool funds (§6). Adversarial buyers are
        the adversaries' business."""
        p, rng = self.p, self.world.rng
        for f in events:
            informed = rng.random() < p.informed_share and not f.correct
            if not informed and rng.random() >= p.buy_rate:
                continue
            if f.controlled_by and rng.random() < p.control_exclusion:
                continue
            if self.exposure + p.payout_cap > self.capacity():
                self.sales_stopped += 1            # F4: fail closed
                continue
            prem = self.premium(f.type)
            buyer = f"buyer/{f.id}"
            self.ledger.mint(buyer, prem)          # the consumer's own money enters here
            self.ledger.move(buyer, POOL, prem)
            self.sold[f.type] += 1
            self.exposure += p.payout_cap
            f.reliance += p.payout_cap            # reliance counts at sale
            bites = (not f.correct) and (informed or rng.random() < p.detect_rate)
            self.exposure -= p.payout_cap
            if bites:
                self.ledger.move(POOL, buyer, p.payout_cap)   # F3: never above the cap
                self.losses[f.type] += 1; self.paid[f.type] += p.payout_cap
                self.file_dispute(f, POOL)                    # the pool prosecutes, funded

    def challengers_act(self) -> None:
        """Profit-driven challengers with free entry and exit (§4): each scans
        facts, verifies at the type's cost, disputes a wrong one when the
        expected win covers the stake at risk and the cost. With
        `target_consumption` they scan where consumption — and so reliance,
        and so the bond — is, weighting by the facts' consumption and reading
        the pool's own loss table as their prior for the type (public data:
        the loss table is the audit, insurance-products §3); without it they
        scan uniformly with the base rate as prior."""
        p, rng, w = self.p, self.world.rng, self.world
        weights = [f.weight for f in w.facts] if p.target_consumption else None
        for name, state in self.challengers.items():
            profit, active = state
            if not active:
                if rng.random() < 0.05:            # re-entry
                    state[1] = True
                continue
            k = min(p.scan_per_tick, len(w.facts))
            sample = rng.choices(w.facts, weights=weights, k=k) if weights else rng.sample(w.facts, k)
            spent = 0.0
            seen = set()
            for f in sample:
                if f.id in seen or f.assertion_ref is None or status(self.fold, f.claim_id, self.now) != ASSERTED:
                    continue
                seen.add(f.id)
                a = self.fold.assertions[f.assertion_ref]
                stake = self.stake_for(a.bond, a.confidence)
                win = p.winner_share * a.bond
                cost = w.types[f.type].verify_cost
                # the challenger's belief that this fact is wrong: the pool's realized loss
                # frequency for the type once it has data, else the type's base rate
                n, losses = self.sold[f.type], self.losses[f.type]
                prior = losses / n if (p.target_consumption and n >= 20) else w.types[f.type].error_rate
                ev = prior * ((1 - p.ruling_error) * win - p.ruling_error * stake) - cost
                if ev <= p.entry_threshold:
                    continue
                self.ledger.move(name, "spent", cost); spent += cost
                if not f.correct:
                    if self.ledger.balances[name] >= stake:
                        self.file_dispute(f, name, stake)
            state[0] -= spent
            if self.ledger.balances[name] < 1.0:
                state[1] = False                    # exit: wiped out
                self.stats["challenger_exits"] += 1

    def sweep(self) -> None:
        """Volunteers walking a district (domain-choice §4): `sweep_capacity`
        facts a tick, the least recently verified first, at `sweep_cost`
        each (their time, minted as such); a wrong one is disputed by the
        pool on their behalf (§6: the pool funds the fight) and the bounty,
        if any, is theirs. This is the launch regime's lever: it reaches the
        cold errors consumption never touches."""
        p = self.p
        if p.sweep_capacity <= 0:
            return
        self._sweep_carry = getattr(self, "_sweep_carry", 0.0) + p.sweep_capacity
        n = int(self._sweep_carry)
        if n <= 0:
            return
        self._sweep_carry -= n
        facts = sorted(self.world.facts, key=lambda f: (getattr(f, "verified_at", -1), f.id))[:n]
        for f in facts:
            f.verified_at = self.now
            self.ledger.mint("sweepers", p.sweep_cost); self.ledger.move("sweepers", "spent", p.sweep_cost)
            self.stats["swept"] += 1
            if not f.correct and f.assertion_ref is not None:
                ref = self.file_dispute(f, POOL)
                if ref:
                    self.disputes_by[ref] = (f, "sweepers")
                    self.stats["sweep_disputes"] += 1

    def file_dispute(self, f: Fact, challenger: str, stake: float | None = None) -> str | None:
        if f.assertion_ref is None:
            return None
        if status(self.fold, f.claim_id, self.now) != ASSERTED:
            return None
        a = self.fold.assertions[f.assertion_ref]
        stake = self.stake_for(a.bond, a.confidence) if stake is None else stake
        d = Dispute(a.ref, challenger, stake, self.now)
        self.fold.add(d)
        self.ledger.move(challenger, "escrow", stake)
        self.disputes_by[d.ref] = (f, challenger)
        self.stats["disputes"] += 1
        return d.ref

    def settle(self) -> None:
        """Rulings on open disputes (one rung, one tick); certification by
        timeout needs no act — status derives it."""
        p, rng = self.p, self.world.rng
        for ref, (f, challenger) in list(self.disputes_by.items()):
            d = self.fold.disputes[ref]
            if self.fold.by_dispute.get(ref):
                continue
            a = self.fold.assertions[d.assertion_ref]
            fabricated = getattr(f, "fabricated_against", None) == ref
            truth_refuted = (not f.correct) or (fabricated and rng.random() >= p.fabrication_catch)
            refuted = self.adjudicator.rule(truth_refuted, rng)
            self.fold.add(Ruling(ref, self.adjudicator.name, "refuted" if refuted else "upheld", 1, self.now))
            self.ledger.move("escrow", TREASURY, 0.0)
            if refuted:
                self.pay_out("escrow", POOL if challenger == "sweepers" else challenger, d.stake, a.bond)
                if p.bounty and challenger != POOL:
                    src = TREASURY if self.ledger.balances[TREASURY] >= p.bounty else POOL
                    self.ledger.move(src, challenger, p.bounty)   # per adjudicated correction only (F9)
                    self.stats["bounties"] += 1
                    if challenger in self.challengers:
                        self.challengers[challenger][0] += p.bounty
                self.world.correct(f, self.now)
                f.assertion_ref = None
                self.stats["refuted"] += 1
            else:
                self.pay_out("escrow", a.author, a.bond, d.stake)   # the pool's stake, lost to itself as asserter
                self.stats["upheld"] += 1
            if challenger in self.challengers:
                self.challengers[challenger][0] += (p.winner_share * a.bond if refuted else -d.stake)
            del self.disputes_by[ref]

    def pay_out(self, escrow: str, winner: str, own: float, lost: float) -> None:
        to_winner = lost * self.p.winner_share
        self.ledger.move(escrow, winner, own + to_winner)
        self.ledger.move(escrow, TREASURY, lost - to_winner)

    # ---- observations -----------------------------------------------------------

    def dispute_rate(self) -> float:
        return self.stats["disputes"] / max(1, self.stats["assertions"])

    def marginal_challenger_roi(self) -> float:
        """The median challenger's profit per unit of capital deployed."""
        rois = sorted(v[0] / 100.0 for v in self.challengers.values())
        return rois[len(rois) // 2] if rois else 0.0

    def pool_escrowed(self) -> float:
        """The pool's capital standing as bonds on live assertions — an asset,
        not a loss, until a refutation takes it."""
        total = 0.0
        for f in self.world.facts:
            if f.assertion_ref is None:
                continue
            a = self.fold.assertions[f.assertion_ref]
            if a.author == POOL and status(self.fold, f.claim_id, self.now) in (ASSERTED, CONTESTED, CERTIFIED):
                total += a.bond
        return total

    def solvent(self) -> bool:
        return self.ledger.balances[POOL] + self.pool_escrowed() > 0
