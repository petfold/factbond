"""`python -m factbond.sim run [--facts N] [--ticks N] [--seed S] [--scored] [--out DIR]`
runs one cell and prints its panels; `... grid [--seeds 1,2,3] [--out DIR]`
sweeps §6's grid and prints one line per cell."""

from __future__ import annotations

import argparse
import json
import sys

from .params import GRID, Params
from .run import artifact, preregistration, run, run_grid


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="factbond.sim")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("run", "grid"):
        s = sub.add_parser(name)
        s.add_argument("--facts", type=int, default=Params.facts)
        s.add_argument("--ticks", type=int, default=Params.ticks)
        s.add_argument("--seed", type=int, default=1)
        s.add_argument("--seeds", default="1")
        s.add_argument("--scored", action="store_true")
        s.add_argument("--out", default=None)
        s.add_argument("--set", action="append", default=[], metavar="KEY=VALUE")
    args = ap.parse_args(argv)
    over = {}
    for kv in args.set:
        k, v = kv.split("=", 1)
        cur = getattr(Params, k)
        over[k] = type(cur)(v) if not isinstance(cur, bool) else v.lower() in ("1", "true", "on")
    base = Params(facts=args.facts, ticks=args.ticks, seed=args.seed, **over)
    if args.cmd == "run":
        r = run(base, scored=args.scored)
        ref, path = artifact(r, args.out)
        print(json.dumps({k: v for k, v in r.items() if k not in ("params", "loss_tables")}, indent=1, default=str))
        print("loss tables:", json.dumps(r["loss_tables"], default=str))
        print("artifact", ref, path or "(not written)")
        print("pre-registration:", "filled" if preregistration() else "UNSET — exploratory only (§2)")
        return 0
    seeds = tuple(int(s) for s in args.seeds.split(","))
    for row in run_grid(base, GRID, scored=args.scored, seeds=seeds, out_dir=args.out):
        v = row["verdict"]
        print(f"{row['cell']} seed {row['seed']}: half-life {row['half_life']} challenger ROI {row['challenger_roi']} "
              f"adv {row['adversary_roi']} disputes {row['dispute_rate']} solvent {row['solvent']} "
              f"| p2 {v['panel2_challenger_roi_positive']} p3 {v['panel3_arson_and_fabrication_negative']} "
              f"p4 {v['panel4_solvent']} cal {v['calibration_dispute_rate_1_to_2pct']}/{v['calibration_capture_replay']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
