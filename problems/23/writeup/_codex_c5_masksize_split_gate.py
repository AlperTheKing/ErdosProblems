"""Exact gate for a fixed-mask-size strengthening of the C5 active split.

For a length-5 row Q with loads s_i, tau=5m/N, eta=N^2/25-m, test every
nonempty mask A subset {0,...,4} against:

  sum_{i in A} (s_i - tau) <= (25/N + c_|A|) eta,

where c_k = 1/10 for k<=3, c_4=1/2, c_5=2/3.

This is stronger than applying the bounds only to the actual active set.  If it
survives, the proof target can be phrased as fixed layer-set inequalities.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import subprocess
from collections import Counter
from fractions import Fraction as F

with contextlib.redirect_stdout(io.StringIO()):
    from _bdef_construct import Cn, mycielski, union_disjoint
    from _codex_c5rs_subset_profile import bits, canon, fmt, mask_s
    from _codex_dwhall_uniform_probe import components, supports_and_p
    from _codex_rowcap_non5_half_gate import adj_of
    from _h import Bconn, GENG, dec
    from _satzmu_conn import struct_for_side
    from _stark1 import gmins


def norm(e):
    u, v = e
    return (u, v) if u < v else (v, u)


def coeff_for_size(k: int) -> F:
    if k <= 3:
        return F(1, 10)
    if k == 4:
        return F(1, 2)
    if k == 5:
        return F(2, 3)
    raise ValueError(k)


def record_min(slot, rec):
    if slot[0] is None or rec["margin"] < slot[0]["margin"]:
        slot[0] = rec


def check_cut(name, n, edges, side, acc):
    adj = adj_of(n, edges)
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    M_raw, ell_raw, _T, _mu, cyc_raw = st
    if not M_raw:
        return

    M = [norm(g) for g in M_raw]
    ell = {norm(g): ell_raw[g] for g in M_raw}
    cyc = {norm(g): [tuple(P) for P in rows] for g, rows in cyc_raw.items()}
    supp, p = supports_and_p(n, M, cyc)
    comp_of = components(M, supp)

    m = len(M)
    eta = F(n * n, 25) - m
    if acc["positive_eta"] and eta <= 0:
        return
    tau = F(5 * m, n)

    acc["cuts"] += 1
    for f in M:
        comp = comp_of[f]
        if not comp or any(ell[g] != 5 for g in comp):
            continue
        for Q in cyc[f]:
            if len(Q) != 5:
                continue
            svals = tuple(sum((p[g][v] for g in comp), F(0)) for v in Q)
            acc["rows"] += 1
            for mask in range(1, 32):
                b = bits(mask)
                k = len(b)
                lhs = sum((svals[i] - tau for i in b), F(0))
                budget = (F(25, n) + coeff_for_size(k)) * eta
                margin = budget - lhs
                orb = canon(mask)
                rec = {
                    "margin": margin,
                    "name": name,
                    "n": n,
                    "m": m,
                    "eta": eta,
                    "tau": tau,
                    "f": f,
                    "Q": tuple(Q),
                    "side": "".join(map(str, side)),
                    "mask": mask,
                    "orbit": orb,
                    "mask_s": mask_s(mask),
                    "orbit_s": mask_s(orb),
                    "size": k,
                    "coeff": coeff_for_size(k),
                    "s": svals,
                    "lhs": lhs,
                    "budget": budget,
                    "active": tuple(i for i, s in enumerate(svals) if s > tau),
                }
                acc["checks"] += 1
                acc["orbit_counts"][orb] += 1
                record_min(acc["min_by_orbit"].setdefault(orb, [None]), rec)
                record_min(acc["min_by_size"].setdefault(k, [None]), rec)
                if margin < 0:
                    acc["fails"] += 1
                    if acc["first_fail"] is None:
                        acc["first_fail"] = rec
                    return


def run_gmins(name, n, edges, max_cuts, acc):
    _adj, cuts = gmins(n, edges)
    if max_cuts is not None:
        cuts = cuts[:max_cuts]
    for side_s in cuts:
        check_cut(name, n, edges, [int(c) for c in side_s], acc)
        if acc["first_fail"] is not None:
            return


def bridge(block1, block2, u, v):
    n, edges = union_disjoint(block1, block2)
    return n, edges + [(u, block1[0] + v)]


def print_rec(label, rec):
    print(label + ":")
    if rec is None:
        print("  none")
        return
    for k in ("margin", "orbit_s", "mask_s", "size", "coeff", "name", "n", "m", "eta", "tau", "lhs", "budget", "active", "s", "f", "Q", "side"):
        print(f"  {k}: {fmt(rec[k])}")


def jsonable(x):
    if isinstance(x, F):
        return fmt(x)
    if isinstance(x, tuple):
        return [jsonable(v) for v in x]
    if isinstance(x, list):
        return [jsonable(v) for v in x]
    if isinstance(x, dict):
        return {str(k): jsonable(v) for k, v in x.items()}
    return x


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-n", type=int, default=8)
    ap.add_argument("--max-n", type=int, default=10)
    ap.add_argument("--max-cuts", type=int, default=None)
    ap.add_argument("--skip-census", action="store_true")
    ap.add_argument("--skip-named", action="store_true")
    ap.add_argument("--positive-eta", action="store_true")
    ap.add_argument("--graph-shard-index", type=int, default=0)
    ap.add_argument("--graph-shard-count", type=int, default=1)
    ap.add_argument("--json-out")
    args = ap.parse_args()
    if args.graph_shard_count < 1:
        raise SystemExit("--graph-shard-count must be positive")
    if not (0 <= args.graph_shard_index < args.graph_shard_count):
        raise SystemExit("--graph-shard-index must be in [0, graph-shard-count)")

    acc = {
        "positive_eta": args.positive_eta,
        "cuts": 0,
        "rows": 0,
        "checks": 0,
        "fails": 0,
        "first_fail": None,
        "orbit_counts": Counter(),
        "min_by_orbit": {},
        "min_by_size": {},
    }

    if not args.skip_named:
        named = [
            ("Grotzsch", mycielski(5, Cn(5))),
            ("M(C7)", mycielski(7, Cn(7))),
            ("C7|Grotzsch", bridge((7, Cn(7)), mycielski(5, Cn(5)), 0, 0)),
        ]
        for name, (n, edges) in named:
            run_gmins(name, n, edges, args.max_cuts, acc)
            if acc["first_fail"] is not None:
                break

    if not args.skip_census and acc["first_fail"] is None:
        for nn in range(args.min_n, args.max_n + 1):
            out = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True, check=True).stdout
            for graph_index, g6 in enumerate(out.split()):
                if graph_index % args.graph_shard_count != args.graph_shard_index:
                    continue
                n, edges = dec(g6)
                run_gmins(f"cen:{g6}", n, edges, args.max_cuts, acc)
                if acc["first_fail"] is not None:
                    break
            if acc["first_fail"] is not None:
                break

    print("=== C5 fixed-mask-size split gate ===")
    print("graph_shard:", f"{args.graph_shard_index}/{args.graph_shard_count}")
    for k in ("cuts", "rows", "checks", "fails"):
        print(f"{k}: {acc[k]}")
    print("orbits:", {mask_s(k): v for k, v in sorted(acc["orbit_counts"].items())})
    for k in sorted(acc["min_by_size"]):
        print_rec(f"min_size_{k}", acc["min_by_size"][k][0])
    for orb in sorted(acc["min_by_orbit"]):
        print_rec(f"min_orbit_{mask_s(orb)}", acc["min_by_orbit"][orb][0])
    print_rec("first_fail", acc["first_fail"])
    print("VERDICT:", "PASS" if acc["fails"] == 0 else "FAIL")
    if args.json_out:
        payload = {
            "graph_shard_index": args.graph_shard_index,
            "graph_shard_count": args.graph_shard_count,
            "cuts": acc["cuts"],
            "rows": acc["rows"],
            "checks": acc["checks"],
            "fails": acc["fails"],
            "first_fail": acc["first_fail"],
            "orbit_counts": {mask_s(k): v for k, v in sorted(acc["orbit_counts"].items())},
            "min_by_size": {str(k): v[0] for k, v in sorted(acc["min_by_size"].items())},
            "min_by_orbit": {mask_s(k): v[0] for k, v in sorted(acc["min_by_orbit"].items())},
        }
        with open(args.json_out, "w", encoding="utf-8") as fh:
            json.dump(jsonable(payload), fh, indent=2, sort_keys=True)


if __name__ == "__main__":
    main()
