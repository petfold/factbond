"""The Phase-0 simulation harness (`docs/plans/phase0-simulation.md`), v0
built 2026-09-19: plain Python, deterministic seeds, the repo's own record
shapes as the harness's native objects (§10), the four go/no-go panels
(§1), the calibration anchors (§6), the adversary suite as scripted
agents (§7), content-addressed results (§10). Exploratory runs are what
this version supports; a *scored* run refuses to start until the
pre-registration block (§2: T, D*, λ*, Peter's sign-off) is filled in
`preregistration.json` — the instrument is fixed before the data arrives.

What v0 models and what it leaves (each a §-reference in the plan):
- the synthetic KB (§3): fact types with measured-style base error rates,
  verification costs and drift hazards; Zipf consumption; planted errors;
- agents (§4): the pool as bulk asserter with refusals; profit-driven
  challengers with free entry and per-type verification costs; honest,
  informed and adversarial buyers of the two products; honest, capturable
  and conformist adjudicators;
- mechanisms (§5): fee, floor, odds-weighted stakes over a bucket set,
  liveness windows, the slashing split, indemnity caps (F3), F4's
  fail-closed exposure caps, premium updating from own loss experience
  from a cold start, the payout→dispute auto-funding coupling;
- adversaries (§7): arson (T5), capture and wearing-down (T4),
  assert-at-0.999 griefing, self-dispute laundering (T11), dispute spam,
  evidence fabrication under a declining E(t), cluster shocks;
- not modelled: independent asserters against the pool, the graph-layer
  netting (the cluster term is per-type and per-adjudicator, not a
  min-cut), rungs 0–2 as distinct costs (one rung cost, one error rate),
  loopmarket's shading experiments (§9; the `consumers` hook is where
  they attach).
"""

from .params import Params, GRID, LAMBDA_AXIS, SWEEP_AXIS
from .run import run, run_grid, artifact, curve, sweeps
from .panels import panels

__all__ = ["Params", "GRID", "LAMBDA_AXIS", "run", "run_grid", "artifact", "curve", "sweeps", "SWEEP_AXIS", "panels"]
