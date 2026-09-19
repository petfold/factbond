"""One run, one artifact (§10): deterministic under its seed, its result a
content-addressed JSON naming the parameters that produced it. `run_grid`
sweeps §6's grid. A *scored* run refuses to start until the
pre-registration block is filled (§2) — exploratory runs are the default."""

from __future__ import annotations

import hashlib
import itertools
import json
import os

from .adversaries import Capturer, suite
from .engine import Engine
from .panels import panels
from .params import GRID, Params
from .world import World

PREREG = os.path.join(os.path.dirname(__file__), "..", "..", "..", "preregistration.json")


def preregistration() -> dict | None:
    """T, D*, λ* and the owner's sign-off, or None while unset."""
    try:
        with open(PREREG, encoding="utf-8") as fh:
            block = json.load(fh)
    except FileNotFoundError:
        return None
    return block if all(block.get(k) not in (None, "", 0) for k in ("T", "D_star", "lambda_star", "set_by")) else None


def _capture_replay(p: Params) -> tuple[str, str]:
    out = []
    for f4 in (True, False):
        e = Engine(p.replace(f4=f4, ticks=1), World.build(p.replace(f4=f4)))
        c = Capturer(); c.start(e); c.act(e)
        out.append(c.outcome)
    return out[0], out[1]


def run(p: Params, *, scored: bool = False, adversaries: bool = True) -> dict:
    """Panels 1, 2 and 4 and the calibration anchors from the honest world;
    panel 3 from each adversary in a world of its own under the same seed —
    in one shared world an adversary's ROI would carry the others' money
    (a spammer's lost stakes are an asserter's income, laundering or not),
    and §7 wants every playbook's ROI attributed to that playbook."""
    if scored and preregistration() is None:
        raise RuntimeError("a scored run needs the pre-registration block (preregistration.json: "
                           "T, D_star, lambda_star, set_by) — §2; exploratory runs need nothing")
    e = Engine(p, World.build(p))
    for _ in range(p.ticks):
        e.tick()
    advs = []
    if adversaries:
        for adv in suite(p):
            ea = Engine(p, World.build(p))
            adv.start(ea)
            for _ in range(p.ticks):
                ea.tick([adv])
            if hasattr(adv, "settle_income"):
                adv.settle_income(ea)
            advs.append(adv)
    on, off = _capture_replay(p)
    result = panels(e, advs, on, off)
    result["params"] = p.to_dict()
    result["scored"] = scored
    result["preregistration"] = preregistration() if scored else None
    return result


def artifact(result: dict, out_dir: str | None = None) -> tuple[str, str | None]:
    """The result's content address, and the path it was written to."""
    body = json.dumps(result, sort_keys=True, separators=(",", ":"), default=str)
    ref = hashlib.sha256(body.encode()).hexdigest()
    path = None
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, ref[:16] + ".json")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(json.dumps(result, sort_keys=True, indent=1, default=str) + "\n")
    return ref, path


def run_grid(base: Params, grid: dict = GRID, *, scored: bool = False, seeds=(1,), out_dir=None) -> list:
    keys = list(grid)
    results = []
    for values in itertools.product(*(grid[k] for k in keys)):
        for seed in seeds:
            p = base.replace(seed=seed, **dict(zip(keys, values)))
            r = run(p, scored=scored)
            ref, path = artifact(r, out_dir)
            results.append({"cell": dict(zip(keys, values)), "seed": seed, "ref": ref, "path": path,
                            "verdict": r["verdict"], "half_life": r["half_life"]["_all"],
                            "challenger_roi": r["challenger_roi"], "adversary_roi": r["adversary_roi"],
                            "dispute_rate": r["dispute_rate"], "solvent": r["solvent"]})
    return results
