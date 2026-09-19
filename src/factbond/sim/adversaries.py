"""The adversary suite (§7): every THREATS entry factbond owns as a
scripted agent with a budget, a playbook and a stop rule, each keeping its
own exact ROI. They act inside the engine's tick and pay through the same
ledger as everyone else, so a profitable cell is a fact about the
mechanism, not about the script."""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from .records import ASSERTED, Assertion, Dispute, status
from .engine import Engine, POOL


@dataclass
class Adversary:
    name: str
    budget: float = 500.0
    spent: float = 0.0
    earned: float = 0.0
    done: bool = False

    def roi(self) -> float:
        return (self.earned - self.spent) / max(self.budget, 1e-9)

    def start(self, e: Engine) -> None:
        e.ledger.mint(self.name, self.budget)

    def act(self, e: Engine) -> None:
        raise NotImplementedError


@dataclass
class Arsonist(Adversary):
    """T5: control m facts, buy the verification bet on each at the cap,
    break them, collect. F3's cap and the control exclusion are what it
    tests; the aggregation variant spreads the same over sybil buyers."""
    name: str = "arson"
    facts_controlled: int = 20
    sybils: int = 1
    targets: list = field(default_factory=list)

    def start(self, e):
        super().start(e)
        self.targets = e.world.rng.sample([f for f in e.world.facts if f.correct], self.facts_controlled)
        for f in self.targets:
            f.controlled_by = self.name

    def act(self, e):
        if self.done:
            return
        p, rng = e.p, e.world.rng
        for f in self.targets:
            for _ in range(self.sybils):
                if rng.random() < p.control_exclusion:      # the pool refuses a policy on a controlled source
                    continue
                if e.exposure + p.payout_cap > e.capacity():
                    continue
                prem = e.premium(f.type)
                if e.ledger.balances[self.name] < prem:
                    continue
                e.ledger.move(self.name, POOL, prem); self.spent += prem
                e.sold[f.type] += 1
                f.correct = False; f.planted_at = e.now              # break it (free: it is theirs)
                e.ledger.move(POOL, self.name, p.payout_cap); self.earned += p.payout_cap
                e.losses[f.type] += 1; e.paid[f.type] += p.payout_cap
                e.file_dispute(f, POOL)                               # the pool prosecutes the record
        self.done = True


@dataclass
class Capturer(Adversary):
    """T4: buy the final rung when the open reliance on a claim exceeds the
    rung's integrity cost. With F4 on, that cost is at least the reliance
    (mechanism-design §2 clause 2); with it off, the March-2025 replay: a
    $750-scale rung guarding $7M-scale reliance."""
    name: str = "capture"
    budget: float = 20000.0
    reliance: float = 7000.0     # open reliance riding on one hub claim, $ (scaled)
    outcome: str = ""

    def act(self, e):
        if self.done:
            return
        cost = max(e.p.capture_cost, self.reliance) if e.p.f4 else e.p.capture_cost
        if cost < self.reliance and e.ledger.balances[self.name] >= cost:
            e.ledger.move(self.name, "treasury", cost); self.spent += cost
            e.adjudicator.captured_by = self.name
            e.ledger.mint(self.name, self.reliance); self.earned += self.reliance   # the position pays outside the oracle
            self.outcome = "captured"
        else:
            self.outcome = "unprofitable"
        self.done = True


@dataclass
class Griefer(Adversary):
    """Assert at 0.999 on facts known wrong, hoping the odds deter challenge.
    Under §1's inversion the challenge is cheapest and most lucrative here."""
    name: str = "griefer"
    count: int = 20

    def act(self, e):
        if self.done:
            return
        p = e.p
        wrong = [f for f in e.world.facts if not f.correct][: self.count]
        for f in wrong:
            bond = p.bond_floor * 10
            if e.ledger.balances[self.name] < bond + p.fee:
                break
            a = Assertion(f.claim_id, self.name, 999, bond, p.liveness, e.now)
            e.fold.add(a); f.assertion_ref = a.ref
            e.ledger.move(self.name, "treasury", p.fee); e.ledger.move(self.name, "escrow", bond)
            self.spent += bond + p.fee
            e.stats["assertions"] += 1
        self.done = True

    def settle_income(self, e):
        # whatever came back to the griefer's account beyond its budget minus spending is income
        self.earned = e.ledger.balances[self.name] - (self.budget - self.spent)


@dataclass
class Launderer(Adversary):
    """T11: dispute your own assertion from a second identity to wash stake
    through the winner's share; strictly negative under the burned slice."""
    name: str = "launder"
    count: int = 10

    def act(self, e):
        if self.done:
            return
        p = e.p
        targets = [f for f in e.world.facts if f.correct][: self.count]
        for f in targets:
            bond = p.bond_floor
            a = Assertion(f.claim_id, self.name, 900, bond, p.liveness, e.now)
            e.fold.add(a); f.assertion_ref = a.ref
            e.ledger.move(self.name, "treasury", p.fee); e.ledger.move(self.name, "escrow", bond)
            self.spent += bond + p.fee
            stake = e.stake_for(bond, 900)
            e.ledger.move(self.name, "escrow", stake); self.spent += stake
            d = Dispute(a.ref, self.name + "/2", stake, e.now)
            e.fold.add(d)
            e.disputes_by[d.ref] = (f, self.name)          # ruled next settle; one side wins, a slice burns
            e.stats["assertions"] += 1; e.stats["disputes"] += 1
        self.done = True

    def settle_income(self, e):
        self.earned = e.ledger.balances[self.name] - (self.budget - self.spent)


@dataclass
class Spammer(Adversary):
    """Dispute spam: freeze honest claims by disputing correct facts; each
    dispute costs at least the rung cost plus the delay externality."""
    name: str = "spam"
    count: int = 30

    def act(self, e):
        if self.done:
            return
        targets = [f for f in e.world.facts if f.correct and f.assertion_ref is not None
                   and status(e.fold, f.claim_id, e.now) == ASSERTED][: self.count]
        for f in targets:
            a = e.fold.assertions[f.assertion_ref]
            stake = e.stake_for(a.bond, a.confidence)
            if e.ledger.balances[self.name] < stake:
                break
            e.file_dispute(f, self.name, stake); self.spent += stake
        self.done = True

    def settle_income(self, e):
        self.earned = e.ledger.balances[self.name] - (self.budget - self.spent)


@dataclass
class Fabricator(Adversary):
    """Evidence fabrication under E(t): dispute correct facts with fabricated
    bundles that pass admissibility with probability 1 − catch, at a cost
    that declines with time (the generative-media parameter)."""
    name: str = "fabricate"
    count: int = 20

    def act(self, e):
        if self.done:
            return
        p = e.p
        cost = p.fabrication_cost0 * math.exp(-p.fabrication_decay * e.now)
        targets = [f for f in e.world.facts if f.correct and f.assertion_ref is not None
                   and status(e.fold, f.claim_id, e.now) == ASSERTED][: self.count]
        for f in targets:
            a = e.fold.assertions[f.assertion_ref]
            stake = e.stake_for(a.bond, a.confidence)
            if e.ledger.balances[self.name] < stake + cost:
                break
            e.ledger.move(self.name, "spent", cost); self.spent += cost
            ref = e.file_dispute(f, self.name, stake)
            if ref:
                self.spent += stake
                f.fabricated_against = ref
        self.done = True

    def settle_income(self, e):
        self.earned = e.ledger.balances[self.name] - (self.budget - self.spent)


def suite(p) -> list:
    """The standard suite for a scored cell (§7); capture is run separately
    with F4 on and off as the calibration replay (§6)."""
    return [Arsonist(), Griefer(), Launderer(), Spammer(), Fabricator()]
