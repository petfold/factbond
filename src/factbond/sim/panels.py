"""The four go/no-go panels (§1), the calibration anchors (§6) and the
deliverables' raw material (§8), all computed from one engine's state and
its adversaries' ledgers — sums, never estimates."""

from __future__ import annotations

import statistics
from collections import defaultdict


def half_life(engine) -> dict:
    """Median lifetime of planted errors that were corrected, per type and
    overall, and the share still open at the end (censored)."""
    by = defaultdict(list)
    for t, ticks in engine.world.half_lives:
        by[t].append(ticks)
    out = {t: statistics.median(v) for t, v in by.items()}
    all_ = [x for v in by.values() for x in v]
    out["_all"] = statistics.median(all_) if all_ else None
    out["_open_at_end"] = engine.world.open_errors()
    out["_corrected"] = len(all_)
    return out


def loss_tables(engine) -> dict:
    """Per fact-type frequency and severity: the pool's founding actuarial
    data (§8 deliverable 1)."""
    out = {}
    for t in engine.world.types:
        n, k = engine.sold[t], engine.losses[t]
        out[t] = {"sold": n, "losses": k, "frequency": k / n if n else None,
                  "severity": engine.paid[t] / k if k else None, "premium_now": engine.premium(t)}
    return out


def panels(engine, adversaries, capture_on=None, capture_off=None) -> dict:
    """Panel 1 half-life (T is the pre-registration's, reported beside it),
    panel 2 the marginal honest challenger's ROI, panel 3 every adversary's
    ROI (arson and fabrication must be < 0), panel 4 pool solvency; plus the
    calibration anchors: the honest dispute rate and the capture replay."""
    adv = {a.name: round(a.roi(), 4) for a in adversaries}   # each settled in its own world (run.py)
    out = {
        "half_life": half_life(engine),
        "challenger_roi": round(engine.marginal_challenger_roi(), 4),
        "adversary_roi": adv,
        "solvent": engine.solvent(),
        "pool_balance": round(engine.ledger.balances["pool"], 2),
        "dispute_rate": round(engine.dispute_rate(), 4),
        "refuted": engine.stats["refuted"], "upheld": engine.stats["upheld"],
        "assertions": engine.stats["assertions"], "disputes": engine.stats["disputes"],
        "refusals": engine.refused, "sales_stopped": engine.sales_stopped,
        "challenger_exits": engine.stats["challenger_exits"],
        "minted": round(engine.ledger.minted, 2),
        "loss_tables": loss_tables(engine),
    }
    if capture_on is not None:
        out["capture_replay"] = {"f4_on": capture_on, "f4_off": capture_off}
    out["verdict"] = {
        "panel2_challenger_roi_positive": out["challenger_roi"] > 0,
        "panel3_arson_and_fabrication_negative": all(adv.get(k, 0) < 0 for k in ("arson", "fabricate") if k in adv),
        "panel4_solvent": out["solvent"],
        "calibration_dispute_rate_1_to_2pct": 0.005 <= out["dispute_rate"] <= 0.05,
        "calibration_capture_replay": (capture_on == "unprofitable" and capture_off == "captured")
        if capture_on is not None else None,
    }
    return out
