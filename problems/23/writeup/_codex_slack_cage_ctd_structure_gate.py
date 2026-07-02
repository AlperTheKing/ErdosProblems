"""Structure gate for the Slack-CAGE CTD frontier.

For each positive proper-counted prebank case (Q,U), this distinguishes:

  * subset residuals using the fixed counted row family R_Q(U):
        pre_R(S) = mu_R(S) - |S| - sigma(S),
    where mu_R only counts rows already counted inside U;

  * peel consumption:
        consume(S;U) = pre_R(U) - max(0, pre_R(U-S)).

The point is to test which form a canonical-terminal-decomposition lemma can
honestly use.  A Flat5 bank switch may consume all positive prebank even when
pre_R(S) itself is not positive.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import multiprocessing as mp
import subprocess
from collections import Counter
from fractions import Fraction as F

with contextlib.redirect_stdout(io.StringIO()):
    from _h import GENG, dec
    from _stark1 import gmins
    from _codex_slack_cage_parallel_census import edge_mask, iter_supermasks, popcount
    from _codex_slack_cage_prebank_classifier import classify_case, counted_rows
    from _codex_slack_cage_switch_gate import build_data, sigma_of
    from _codex_slack_cage_banked_flat_gate import is_flat5_switch
    from _codex_slack_cage_xi2_gate import xi2_for_switch


def mask_to_set(mask, n):
    return frozenset(i for i in range(n) if (mask >> i) & 1)


def set_to_mask(S):
    out = 0
    for v in S:
        out |= 1 << v
    return out


def submasks(mask):
    cur = mask
    while cur:
        yield cur
        cur = (cur - 1) & mask


def fmt_frac(x):
    if isinstance(x, F):
        return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"
    return str(x)


def fmt_rec(rec):
    if rec is None:
        return ""
    out = dict(rec)
    for key in (
        "eta",
        "pre_U",
        "pre_S",
        "pre_after",
        "consume",
        "max_subset_pre",
        "best_flat5_pre_S",
        "best_flat5_pre_after",
    ):
        if key in out:
            out[key] = fmt_frac(out[key])
    return out


def fixed_mu_vector(n, M, cyc, rows, Q):
    qset = set(Q)
    weights = [F(0) for _ in range(n)]
    for g, P, pset in rows:
        mass = F(1, len(cyc[g]))
        for v in pset & qset:
            weights[v] += mass
    return weights


def sum_mask(weights, mask):
    total = F(0)
    i = 0
    while mask:
        if mask & 1:
            total += weights[i]
        mask >>= 1
        i += 1
    return total


def analyze_case(n, E, B, Mset, M, cyc, Q, umask, pre_U, eta):
    U = mask_to_set(umask, n)
    rows = counted_rows(Q, U, M, cyc)
    weights = fixed_mu_vector(n, M, cyc, rows, Q)
    switches, zero, strict, flat = classify_case(n, E, B, Mset, Q, U, rows)

    max_subset_pre = None
    max_subset_mask = None
    positive_subset_count = 0
    for smask in submasks(umask):
        S = mask_to_set(smask, n)
        pre_S = sum_mask(weights, smask) - popcount(smask) - sigma_of(S, B, Mset)
        if pre_S > 0:
            positive_subset_count += 1
        if max_subset_pre is None or pre_S > max_subset_pre:
            max_subset_pre = pre_S
            max_subset_mask = smask

    best_flat5 = None
    for sig, dg, Stuple in zero:
        S = frozenset(Stuple)
        smask = set_to_mask(S)
        if not is_flat5_switch(n, E, B, Mset, Stuple):
            continue
        after = umask & ~smask
        pre_S = sum_mask(weights, smask) - popcount(smask) - sigma_of(S, B, Mset)
        pre_after = sum_mask(weights, after) - popcount(after) - sigma_of(mask_to_set(after, n), B, Mset)
        consume = pre_U - max(F(0), pre_after)
        xi2, _info = xi2_for_switch(n, B, Mset, rows, S)
        rec = {
            "S": tuple(sorted(S)),
            "pre_S": pre_S,
            "pre_after": pre_after,
            "consume": consume,
            "DeltaGamma": dg,
            "Xi2": xi2,
        }
        if best_flat5 is None or max(F(0), pre_after) < max(F(0), best_flat5["pre_after"]):
            best_flat5 = rec

    return {
        "positive_subset_count": positive_subset_count,
        "max_subset_pre": max_subset_pre,
        "max_subset": tuple(sorted(mask_to_set(max_subset_mask, n))) if max_subset_mask is not None else (),
        "zero_count": len(zero),
        "strict_count": len(strict),
        "flat_count": len(flat),
        "best_flat5": best_flat5,
    }


def check_side(name, n, edges, side):
    data = build_data(n, edges, [int(c) for c in side])
    if data is None:
        return None
    E, B, M, Mset, cyc = data
    if not M:
        return None

    allmask = (1 << n) - 1
    subset_count = 1 << n
    eta = F(n * n, 25) - len(M)

    blue = list(B)
    bad_edges = list(Mset)
    slack = [0] * subset_count
    for mask in range(subset_count):
        dB = sum(1 for u, v in blue if popcount(mask & edge_mask(u, v)) == 1)
        dM = sum(1 for u, v in bad_edges if popcount(mask & edge_mask(u, v)) == 1)
        slack[mask] = dB - dM

    tw = [[F(0) for _ in range(n)] for _ in range(subset_count)]
    q_rows = []
    for g in M:
        den = len(cyc[g])
        mass = F(1, den)
        for P in cyc[g]:
            ptuple = tuple(P)
            pmask = 0
            for v in ptuple:
                pmask |= 1 << v
            q_rows.append((g, ptuple))
            for umask in iter_supermasks(pmask, allmask):
                row = tw[umask]
                for v in ptuple:
                    row[v] += mass

    stats = Counter()
    first_case = None
    first_no_positive_subset = None
    first_flat5_nonpositive = None
    max_subset_pre_rec = None
    min_flat5_pre_rec = None

    for _f, Q in q_rows:
        for umask in range(1, allmask):
            lhs = sum(tw[umask][v] for v in Q)
            if lhs <= 0:
                continue
            pre_U = lhs - popcount(umask) - slack[umask]
            if pre_U <= 0:
                continue
            stats["positive"] += 1
            res = analyze_case(n, E, B, Mset, M, cyc, Q, umask, pre_U, eta)
            rec = {
                "name": name,
                "n": n,
                "m": len(M),
                "eta": eta,
                "Q": tuple(Q),
                "U": tuple(sorted(mask_to_set(umask, n))),
                "pre_U": pre_U,
                "positive_subset_count": res["positive_subset_count"],
                "max_subset_pre": res["max_subset_pre"],
                "max_subset": res["max_subset"],
                "zero_count": res["zero_count"],
                "strict_count": res["strict_count"],
                "flat_count": res["flat_count"],
            }
            bf = res["best_flat5"]
            if bf is not None:
                rec.update(
                    {
                        "best_flat5": bf["S"],
                        "best_flat5_pre_S": bf["pre_S"],
                        "best_flat5_pre_after": bf["pre_after"],
                        "consume": bf["consume"],
                        "Xi2": bf["Xi2"],
                    }
                )
                if bf["pre_S"] <= 0:
                    stats["flat5_pre_S_nonpositive"] += 1
                    if first_flat5_nonpositive is None:
                        first_flat5_nonpositive = rec
                else:
                    stats["flat5_pre_S_positive"] += 1
                if min_flat5_pre_rec is None or bf["pre_S"] < min_flat5_pre_rec["best_flat5_pre_S"]:
                    min_flat5_pre_rec = rec
            else:
                stats["no_flat5"] += 1
            if res["positive_subset_count"] == 0:
                stats["no_positive_subset"] += 1
                if first_no_positive_subset is None:
                    first_no_positive_subset = rec
            if first_case is None:
                first_case = rec
            if max_subset_pre_rec is None or res["max_subset_pre"] > max_subset_pre_rec["max_subset_pre"]:
                max_subset_pre_rec = rec

    return {
        "stats": stats,
        "first_case": first_case,
        "first_no_positive_subset": first_no_positive_subset,
        "first_flat5_nonpositive": first_flat5_nonpositive,
        "max_subset_pre": max_subset_pre_rec,
        "min_flat5_pre": min_flat5_pre_rec,
    }


def worker(g6):
    n, edges = dec(g6)
    _adj, cuts = gmins(n, edges)
    stats = Counter()
    first_case = None
    first_no_positive_subset = None
    first_flat5_nonpositive = None
    max_subset_pre = None
    min_flat5_pre = None
    for idx, side in enumerate(cuts):
        r = check_side(f"cen{g6}#cut{idx}", n, edges, side)
        if r is None:
            continue
        stats.update(r["stats"])
        if first_case is None and r["first_case"] is not None:
            first_case = r["first_case"]
        if first_no_positive_subset is None and r["first_no_positive_subset"] is not None:
            first_no_positive_subset = r["first_no_positive_subset"]
        if first_flat5_nonpositive is None and r["first_flat5_nonpositive"] is not None:
            first_flat5_nonpositive = r["first_flat5_nonpositive"]
        if r["max_subset_pre"] is not None and (
            max_subset_pre is None or r["max_subset_pre"]["max_subset_pre"] > max_subset_pre["max_subset_pre"]
        ):
            max_subset_pre = r["max_subset_pre"]
        if r["min_flat5_pre"] is not None and (
            min_flat5_pre is None or r["min_flat5_pre"]["best_flat5_pre_S"] < min_flat5_pre["best_flat5_pre_S"]
        ):
            min_flat5_pre = r["min_flat5_pre"]
    return {
        "stats": stats,
        "first_case": first_case,
        "first_no_positive_subset": first_no_positive_subset,
        "first_flat5_nonpositive": first_flat5_nonpositive,
        "max_subset_pre": max_subset_pre,
        "min_flat5_pre": min_flat5_pre,
    }


def choose_max(cur, val, field):
    if val is None:
        return cur
    if cur is None or val[field] > cur[field]:
        return val
    return cur


def choose_min(cur, val, field):
    if val is None:
        return cur
    if cur is None or val[field] < cur[field]:
        return val
    return cur


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=10)
    ap.add_argument("--workers", type=int, default=60)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--chunksize", type=int, default=8)
    args = ap.parse_args()

    graphs = subprocess.run([GENG, "-tc", str(args.n)], capture_output=True, text=True, check=True).stdout.split()
    if args.limit is not None:
        graphs = graphs[: args.limit]

    stats = Counter()
    first_case = None
    first_no_positive_subset = None
    first_flat5_nonpositive = None
    max_subset_pre = None
    min_flat5_pre = None
    done = 0
    with mp.Pool(processes=args.workers) as pool:
        for r in pool.imap_unordered(worker, graphs, chunksize=args.chunksize):
            done += 1
            stats.update(r["stats"])
            if first_case is None and r["first_case"] is not None:
                first_case = r["first_case"]
            if first_no_positive_subset is None and r["first_no_positive_subset"] is not None:
                first_no_positive_subset = r["first_no_positive_subset"]
            if first_flat5_nonpositive is None and r["first_flat5_nonpositive"] is not None:
                first_flat5_nonpositive = r["first_flat5_nonpositive"]
            max_subset_pre = choose_max(max_subset_pre, r["max_subset_pre"], "max_subset_pre")
            min_flat5_pre = choose_min(min_flat5_pre, r["min_flat5_pre"], "best_flat5_pre_S")
            if done % 500 == 0:
                print(f"progress graphs={done}/{len(graphs)} positive={stats['positive']}", flush=True)

    print("=== Slack-CAGE CTD structure gate ===")
    print("n:", args.n)
    print("graphs:", len(graphs))
    print("stats:", dict(stats))
    print("first_case:", fmt_rec(first_case))
    print("first_no_positive_subset:", fmt_rec(first_no_positive_subset))
    print("first_flat5_nonpositive:", fmt_rec(first_flat5_nonpositive))
    print("max_subset_pre:", fmt_rec(max_subset_pre))
    print("min_flat5_pre:", fmt_rec(min_flat5_pre))
    print("VERDICT:", "PASS_STRUCTURE_SCAN" if stats["positive"] else "CHECK")


if __name__ == "__main__":
    main()
