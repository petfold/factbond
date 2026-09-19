"""The synthetic KB (§3): a frozen domain of facts across types, planted
errors at the types' base rates, drift true→false at type hazards, Zipf
consumption so most facts are never consumed — the lazy-verification regime
the mechanism claims to answer. `Fact.correct` is the world's truth about the
record; nothing in the mechanism reads it except an agent that pays to."""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from .params import Params
from .records import Claim


@dataclass
class Fact:
    id: int
    type: str
    correct: bool
    weight: float                 # consumption weight (Zipf)
    claim: Claim
    planted_at: int | None = None  # when the record went wrong (0 for a seeded error)
    corrected_at: int | None = None
    assertion_ref: str | None = None
    controlled_by: str = ""       # an attacker who controls the source (T5)
    consumed: int = 0
    reliance: float = 0.0         # open insured exposure riding on this record, $ (retires over the liveness window)

    @property
    def claim_id(self) -> str:
        return self.claim.claim_id


@dataclass
class World:
    facts: list
    rng: random.Random
    types: dict
    half_lives: list = field(default_factory=list)   # (type, ticks from planting to correction)
    consumption: list = field(default_factory=list)  # per tick: number of events

    @classmethod
    def build(cls, p: Params) -> "World":
        rng = random.Random(p.seed)
        types = {t.name: t for t in p.fact_types}
        facts = []
        ranks = list(range(1, p.facts + 1)); rng.shuffle(ranks)
        # each type takes its consumption share of the facts, so the Zipf ranks mix types
        pool = []
        for t in p.fact_types:
            pool += [t] * max(1, int(round(p.facts * t.consumption_share)))
        pool = (pool * (p.facts // len(pool) + 1))[:p.facts]
        rng.shuffle(pool)
        for i in range(p.facts):
            t = pool[i]
            correct = rng.random() >= t.error_rate
            claim = Claim(f"{t.name}/{i}", "root:snapshot", t.claim_type, f"policy:{t.name}:v1")
            facts.append(Fact(i, t.name, correct, ranks[i] ** (-p.zipf_s), claim,
                              planted_at=None if correct else 0))
        return cls(facts, rng, types)

    def drift(self, now: int, retire: float = 0.0) -> int:
        """Facts decay true→false at their type's hazard; returns how many.
        Reliance retires at `retire` per tick (counts at sale, retires as
        the policies run off — mechanism-design §2)."""
        n = 0
        for f in self.facts:
            if f.reliance:
                f.reliance *= 1.0 - retire
                if f.reliance < 0.01:
                    f.reliance = 0.0
            if f.correct and self.rng.random() < self.types[f.type].drift_hazard:
                f.correct = False; f.planted_at = now; f.corrected_at = None; n += 1
        return n

    def consume(self, p: Params, now: int) -> list:
        """The tick's consumption events, Zipf-weighted: the facts people act on."""
        k = int(round(p.consumption_rate * len(self.facts)))
        events = self.rng.choices(self.facts, weights=[f.weight for f in self.facts], k=k)
        for f in events:
            f.consumed += 1
        self.consumption.append(k)
        return events

    def correct(self, f: Fact, now: int) -> None:
        """A refuted record is corrected (the correction feed's last mile, in
        the sim: immediate); the planted error's lifetime is recorded."""
        if not f.correct:
            if f.planted_at is not None:
                self.half_lives.append((f.type, now - f.planted_at))
            f.correct = True; f.corrected_at = now; f.planted_at = None

    def open_errors(self) -> int:
        return sum(1 for f in self.facts if not f.correct)
