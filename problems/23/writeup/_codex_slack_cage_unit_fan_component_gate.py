"""Group selected UNIT-FLAT5 atoms by their common 4-vertex row core.

This is a structural stress gate for the MAXCUT-FAN-COLLAPSE target.
For each unit atom (two unique length-5 rows intersecting in 4 vertices), the
common 4-set is the putative fan corridor.  A group with >=3 distinct rows is
the combinatorial shadow of a multi-leaf Flat5 fan.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import multiprocessing as mp
import subprocess
from collections import Counter, defaultdict

with contextlib.redirect_stdout(io.StringIO()):
    from _h import GENG, dec
    from _stark1 import gmins
    from _codex_slack_cage_flat5_fan_stress import build_theta
    from _codex_slack_cage_prebank_classifier import subset_tw
    from _codex_slack_cage_rowunion_unit_gate import candidate_unions_for_Q, unit_flat5_signature, fmt_frac
    from _codex_slack_cage_switch_gate import build_data, counted_rows, sigma_of


def common4_key(rows):
    if len(rows) != 2:
        return None
    p0 = tuple(rows[0][1])
    p1 = tuple(rows[1][1])
    s = frozenset(p0) & frozenset(p1)
    if len(s) != 4:
        return None
    return tuple(sorted(s))


def empty_acc():
    return {
        "graphs": 0,
        "cuts": 0,
        "positive": 0,
        "unit_cases": 0,
        "bad_groups": 0,
        "first_bad_group": None,
        "max_group_rows": 0,
        "group_row_hist": Counter(),
    }


def merge_acc(dst, src):
    for key in ("graphs", "cuts", "positive", "unit_cases", "bad_groups"):
        dst[key] += src[key]
    dst["group_row_hist"].update(src["group_row_hist"])
    if src["max_group_rows"] > dst["max_group_rows"]:
        dst["max_group_rows"] = src["max_group_rows"]
    if dst["first_bad_group"] is None and src["first_bad_group"] is not None:
        dst["first_bad_group"] = src["first_bad_group"]


def check_side(name, n, edges, side, max_union_rows=2):
    acc = empty_acc()
    data = build_data(n, edges, [int(c) for c in side])
    if data is None:
        return acc
    E, B, M, Mset, cyc = data
    if not M:
        return acc
    acc["cuts"] = 1
    all_rows = [(g, tuple(P), frozenset(P)) for g in M for P in cyc[g]]
    groups = defaultdict(set)
    seen_cases = set()
    for f in M:
        for Q in cyc[f]:
            Q = tuple(Q)
            for U in candidate_unions_for_Q(all_rows, Q, max_union_rows):
                if not U or len(U) == n:
                    continue
                case_key = (Q, tuple(sorted(U)))
                if case_key in seen_cases:
                    continue
                seen_cases.add(case_key)
                tw = subset_tw(n, M, cyc, U)
                pre = sum(tw[v] for v in Q) - len(U) - sigma_of(U, B, Mset)
                if pre <= 0:
                    continue
                acc["positive"] += 1
                rows = counted_rows(Q, U, M, cyc)
                sig = unit_flat5_signature(n, E, B, M, Mset, cyc, Q, U, rows)
                if not sig["is_unit"]:
                    continue
                acc["unit_cases"] += 1
                key = common4_key(rows)
                if key is None:
                    continue
                for _g, P, _pset in rows:
                    groups[key].add(tuple(P))

    for key, rowset in groups.items():
        row_count = len(rowset)
        acc["group_row_hist"][row_count] += 1
        acc["max_group_rows"] = max(acc["max_group_rows"], row_count)
        if row_count >= 3:
            acc["bad_groups"] += 1
            if acc["first_bad_group"] is None:
                acc["first_bad_group"] = {
                    "name": name,
                    "n": n,
                    "m": len(M),
                    "side": "".join(str(int(c)) for c in side),
                    "common4": key,
                    "rows": tuple(sorted(rowset))[:12],
                }
    return acc


def worker(payload):
    g6, max_cuts = payload
    n, edges = dec(g6)
    out = empty_acc()
    out["graphs"] = 1
    _adj, cuts = gmins(n, edges)
    for idx, side in enumerate(cuts[:max_cuts]):
        merge_acc(out, check_side(f"cen{g6}#cut{idx}", n, edges, side))
    return out


def fmt_rec(rec):
    return "" if rec is None else str(rec)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=None)
    ap.add_argument("--workers", type=int, default=60)
    ap.add_argument("--chunksize", type=int, default=8)
    ap.add_argument("--max-cuts", type=int, default=8)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--theta", action="store_true")
    ap.add_argument("--intended", action="store_true")
    ap.add_argument("--max-t", type=int, default=8)
    args = ap.parse_args()

    total = empty_acc()
    if args.theta:
        for t in range(2, args.max_t + 1):
            n, edges, intended = build_theta(t)
            if args.intended:
                cuts = [intended]
            else:
                _adj, cuts = gmins(n, edges)
                cuts = cuts[: args.max_cuts]
            local = empty_acc()
            for idx, side in enumerate(cuts):
                merge_acc(local, check_side(f"theta-t{t}#cut{idx}", n, edges, side))
            merge_acc(total, local)
            print(
                f"theta t={t} cuts={len(cuts)} positive={local['positive']} unit={local['unit_cases']} "
                f"max_group_rows={local['max_group_rows']} bad_groups={local['bad_groups']} "
                f"hist={dict(sorted(local['group_row_hist'].items()))}",
                flush=True,
            )
    else:
        if args.n is None:
            raise SystemExit("--n is required unless --theta is used")
        graphs = subprocess.run([GENG, "-tc", str(args.n)], capture_output=True, text=True, check=True).stdout.split()
        if args.limit is not None:
            graphs = graphs[: args.limit]
        payloads = [(g6, args.max_cuts) for g6 in graphs]
        with mp.Pool(processes=args.workers) as pool:
            done = 0
            for acc in pool.imap_unordered(worker, payloads, chunksize=args.chunksize):
                done += acc["graphs"]
                merge_acc(total, acc)
                if done % 1000 == 0 or done == len(graphs):
                    print(
                        f"progress graphs={done}/{len(graphs)} positive={total['positive']} "
                        f"unit={total['unit_cases']} bad_groups={total['bad_groups']}",
                        flush=True,
                    )

    print("=== UNIT-FLAT5 fan-component gate ===")
    print("graphs:", total["graphs"])
    print("cuts:", total["cuts"])
    print("positive:", total["positive"])
    print("unit_cases:", total["unit_cases"])
    print("max_group_rows:", total["max_group_rows"])
    print("bad_groups:", total["bad_groups"])
    print("group_row_hist:", dict(sorted(total["group_row_hist"].items())))
    print("first_bad_group:", fmt_rec(total["first_bad_group"]))
    print("VERDICT:", "PASS_FAN_COMPONENT_GATE" if total["bad_groups"] == 0 else "FAIL_FAN_COMPONENT_GATE")


if __name__ == "__main__":
    main()
