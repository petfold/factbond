"""`python -m factbond.sim run [--facts N] [--ticks N] [--seed S] [--scored] [--out DIR]`
runs one cell and prints its panels; `... grid [--seeds 1,2,3] [--out DIR]`
sweeps §6's grid and prints one line per cell."""

from __future__ import annotations

import argparse
import json
import sys

from .params import GRID, LAMBDA_AXIS, PRESETS, SWEEP_AXIS, Params
from .run import artifact, curve, preregistration, run, run_grid, sweeps


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="factbond.sim")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("run", "grid", "curve", "sweeps"):
        s = sub.add_parser(name)
        s.add_argument("--facts", type=int, default=Params.facts)
        s.add_argument("--ticks", type=int, default=Params.ticks)
        s.add_argument("--seed", type=int, default=1)
        s.add_argument("--seeds", default="1")
        s.add_argument("--scored", action="store_true")
        s.add_argument("--out", default=None)
        s.add_argument("--set", action="append", default=[], metavar="KEY=VALUE")
        s.add_argument("--preset", choices=sorted(PRESETS), default="poi", help="the fact types: poi (POI liveness) or lockers (the automated boxes)")
    args = ap.parse_args(argv)
    over = {}
    for kv in args.set:
        k, v = kv.split("=", 1)
        cur = getattr(Params, k)
        over[k] = type(cur)(v) if not isinstance(cur, bool) else v.lower() in ("1", "true", "on")
    base = Params(facts=args.facts, ticks=args.ticks, seed=args.seed, fact_types=PRESETS[args.preset], **over)
    if args.cmd == "run":
        r = run(base, scored=args.scored)
        ref, path = artifact(r, args.out)
        print(json.dumps({k: v for k, v in r.items() if k not in ("params", "loss_tables")}, indent=1, default=str))
        print("loss tables:", json.dumps(r["loss_tables"], default=str))
        print("artifact", ref, path or "(not written)")
        print("pre-registration:", "filled" if preregistration() else "UNSET — exploratory only (§2)")
        return 0
    seeds = tuple(int(s) for s in args.seeds.split(","))
    if args.cmd == "sweeps":
        block = preregistration()
        print("T:", block["T"] if block else "unset (exploratory)", "| consumption rate", base.consumption_rate)
        for row in sweeps(base, SWEEP_AXIS, seeds=seeds, scored=args.scored):
            hl = row["half_life"] if row["half_life"] is not None else f"> {base.ticks} (censored)"
            print(f"sweep {row['sweep_capacity']:<5} facts/tick seed {row['seed']}: half-life {hl} "
                  f"(seeded {row['seeded']}, corrected {row['corrected']}, open at end {row['open_at_end']}; "
                  f"swept {row['swept']}, disputes {row['sweep_disputes']}, bounties {row['bounties']}) pool {row['pool_balance']} solvent {row['solvent']}"
                  + (f" meets T: {row['meets_T']}" if block else ""))
        return 0
    if args.cmd == "curve":
        block = preregistration()
        print("T:", block["T"] if block else "unset (exploratory)")
        for row in curve(base, LAMBDA_AXIS, seeds=seeds, scored=args.scored):
            hl = row["half_life"] if row["half_life"] is not None else f"> {base.ticks} (censored)"
            print(f"λ {row['consumption_rate']:<7} seed {row['seed']}: half-life {hl} "
                  f"(seeded {row['seeded']}, corrected {row['corrected']} at median {row['corrected_median']}, open at end {row['open_at_end']}) "
                  f"challenger ROI {row['challenger_roi']} "
                  f"disputes {row['dispute_rate']} bounties {row['bounties']} solvent {row['solvent']}"
                  + (f" meets T: {row['meets_T']}" if block else ""))
        return 0
    for row in run_grid(base, GRID, scored=args.scored, seeds=seeds, out_dir=args.out):
        v = row["verdict"]
        print(f"{row['cell']} seed {row['seed']}: half-life {row['half_life']} challenger ROI {row['challenger_roi']} "
              f"adv {row['adversary_roi']} disputes {row['dispute_rate']} solvent {row['solvent']} "
              f"| p2 {v['panel2_challenger_roi_positive']} p3 {v['panel3_arson_and_fabrication_negative']} "
              f"p4 {v['panel4_solvent']} cal {v['calibration_dispute_rate_1_to_2pct']}/{v['calibration_capture_replay']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
