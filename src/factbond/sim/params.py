"""The parameters the plan sweeps (§6) and the fixed model constants, one
frozen record so a run's artifact names exactly what produced it."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass(frozen=True)
class FactType:
    name: str
    error_rate: float        # measured-style base rate at snapshot time (§3)
    verify_cost: float       # a challenger's cost to check one fact, $
    drift_hazard: float      # per tick, true -> false
    consumption_share: float # of consumption events
    claim_type: str = "attribute-matches-world"


#: POI liveness (domain-choice.md, decided 2026-09-19): one place, five linked
#: claims. Error priors are placeholders until measured at snapshot time (§3);
#: verification costs are a person's time for a physical check ($10–30), a call
#: for the cheap ones; consumption shares follow what people ask (hours most,
#: existence and identity the wasted trip, wheelchair the highest stakes).
FACT_TYPES = (
    FactType("existence", 0.04, 20.0, 0.0004, 0.25, "entity-exists"),
    FactType("identity", 0.05, 20.0, 0.0003, 0.20, "attribute-matches-world"),
    FactType("opening_hours", 0.08, 20.0, 0.0008, 0.35),
    FactType("wheelchair", 0.06, 20.0, 0.0001, 0.10),
    FactType("address", 0.03, 15.0, 0.0002, 0.10),
)


@dataclass(frozen=True)
class Params:
    # the world (§3)
    facts: int = 4000
    ticks: int = 360                       # days
    zipf_s: float = 1.1
    consumption_rate: float = 0.05         # λ: consumption events per fact per tick, on average
    seed: int = 1
    # the mechanism (§5–§6)
    bond_floor: float = 2.0                # $0.5–$20 swept
    k_reliance: float = 0.5                # bond = max(floor, k × open reliance) (mechanism-design §2 clause 1); 0 = floor only
    target_consumption: bool = True        # challengers scan where consumption is, with the loss table as prior
    fee: float = 0.05
    buckets: tuple = (900, 970, 990, 999)
    pool_confidence: int = 990
    liveness: int = 14                     # ticks
    rung_cost: float = 8.0                 # D.adjudication: the automated evidence rung; a person reading is 30–60
    bounty: float = 0.0                    # paid per *adjudicated* correction to the challenger (the one reward F9 permits)
    sweep_capacity: float = 0.0            # facts verified per tick by volunteers walking a district (domain-choice §4)
    sweep_cost: float = 1.5                # a sweeper's cost per fact — batched, a street at a time, not a trip each
    delay_externality: float = 1.0
    winner_share: float = 0.75             # of the loser's stake; the rest burned/treasury
    ruling_error: float = 0.02             # honest adjudicator's error rate
    # insurance (§5, insurance-products.md)
    payout_cap: float = 20.0               # F3's proxy cap per policy
    premium_prior: float = 0.10            # cold-start base loss rate per fact-type
    premium_load: float = 1.5              # adverse-selection × capital load
    buy_rate: float = 0.30                 # honest consumers buying the verification bet
    informed_share: float = 0.05           # buyers who know the fact is wrong
    detect_rate: float = 0.9               # a consumer of a wrong fact notices
    control_exclusion: float = 0.9         # a policy on a fact the buyer controls is refused
    pool_stake: float = 20000.0
    reserve_gearing: float = 4.8           # Nexus's MCR gearing prior (netting-and-reserves §7)
    ruin_epsilon: float = 0.005            # Solvency II 99.5 %
    # challengers (§4)
    challengers: int = 20
    scan_per_tick: int = 40                # facts a challenger looks at per tick
    entry_threshold: float = 0.0           # expected profit per tick to stay
    # evidence (§7)
    fabrication_cost0: float = 40.0        # E(0)
    fabrication_decay: float = 0.002       # E(t) = E0 · e^(−decay·t)
    fabrication_catch: float = 0.7         # a fabricated bundle fails admissibility
    # F4 and capture (§6 calibration replay)
    f4: bool = True
    capture_cost: float = 750.0            # the final rung's integrity cost when F4 is off
    fact_types: tuple = FACT_TYPES

    def to_dict(self) -> dict:
        d = asdict(self)
        d["fact_types"] = [asdict(t) for t in self.fact_types]
        return d

    def replace(self, **kw) -> "Params":
        return Params(**{**{k: getattr(self, k) for k in self.__dataclass_fields__}, **kw})


#: the sweep of §6, small enough to run in minutes; the full grid is the same call with more values
GRID = {
    "bond_floor": (0.5, 2.0, 8.0, 20.0),
    "rung_cost": (8.0, 30.0, 60.0),
    "consumption_rate": (0.001, 0.01, 0.05, 0.2),
    "k_reliance": (0.0, 0.5),
}

#: the curve's axis (§2 as amended): from launch — a handful of people, a few
#: facts a month over the whole KB — up to a steady state where most facts are
#: acted on within days
LAMBDA_AXIS = (0.0002, 0.001, 0.003, 0.01, 0.03, 0.1, 0.3)

#: the launch regime's other axis: sweep capacity in facts verified per tick —
#: five people doing three facts a month is 0.5/day; one afternoon a week
#: walking a district is ~30/day averaged
SWEEP_AXIS = (0.0, 0.5, 2.0, 5.0, 10.0, 30.0, 100.0)
