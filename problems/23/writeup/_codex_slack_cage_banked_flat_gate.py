"""Parallel gate for the banked flat-cell exception in Slack-CAGE.

This scans positive proper-counted prebank cases:

    Pi_Q(U) = D_Q(U) - |U| - sigma(U) > 0,

then classifies GPT-Pro cage-switch core sets inside U.  It tests the
eta-bank branch:

    if no strict Gamma-drop zero-slack cage exists, then
      Pi_Q(U) <= eta and at least one flat zero-slack cage exists.

All arithmetic is exact Fraction arithmetic.  This is a verifier/stress tool,
not a proof.
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
    from _codex_slack_cage_switch_gate import build_data, delta, flip_blue, shortest_distance, sigma_of
    from _codex_slack_cage_prebank_classifier import classify_case, counted_rows


def mask_to_set(mask, n):
    return frozenset(i for i in range(n) if (mask >> i) & 1)


def fmt_frac(x):
    if x is None:
        return ""
    if isinstance(x, F):
        return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"
    return str(x)


def fmt_rec(rec):
    if rec is None:
        return ""
    out = dict(rec)
    for key in ("eta", "lhs", "prebank", "margin", "prebank_minus_eta"):
        if key in out:
            out[key] = fmt_frac(out[key])
    return out


def ell_in_blue(n, blue_edges, edge):
    d = shortest_distance(n, blue_edges, edge[0], edge[1])
    return None if d is None else d + 1


def is_flat5_switch(n, E, B, Mset, switch_tuple):
    S = frozenset(switch_tuple)
    old_crossing = delta(Mset, S)
    new_bad_edges = delta(B, S)
    BS = flip_blue(E, B, S)
    if not old_crossing or not new_bad_edges:
        return False
    for e in old_crossing:
        if ell_in_blue(n, B, e) != 5:
            return False
    for e in new_bad_edges:
        if ell_in_blue(n, BS, e) != 5:
            return False
    return True


def classify_positive_case(n, E, B, Mset, M, cyc, Q, mask, lhs, sigma, eta):
    U = mask_to_set(mask, n)
    rows = counted_rows(Q, U, M, cyc)
    switches, zero, strict, flat = classify_case(n, E, B, Mset, Q, U, rows)
    flat5 = [item for item in flat if is_flat5_switch(n, E, B, Mset, item[2])]
    prebank = lhs - len(U) - sigma
    rec = {
        "n": n,
        "m": len(M),
        "eta": eta,
        "Q": tuple(Q),
        "U": tuple(sorted(U)),
        "lhs": lhs,
        "sigma": sigma,
        "prebank": prebank,
        "prebank_minus_eta": prebank - eta,
        "margin": eta - prebank,
        "zero_count": len(zero),
        "strict_count": len(strict),
        "flat_count": len(flat),
        "flat5_count": len(flat5),
        "zero": zero[:6],
        "strict": strict[:6],
        "flat": flat[:6],
        "flat5": flat5[:6],
        "counted": [(g, tuple(P)) for g, P, _pset in rows[:8]],
    }
    return rec, bool(strict), bool(flat), bool(flat5)


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
    max_prebank = None
    max_nostrict_prebank = None
    max_nostrict_diff = None
    first_over_eta = None
    first_no_flat = None
    first_no_flat5 = None
    first_positive = None

    for _f, Q in q_rows:
        for mask in range(1, allmask):
            lhs = sum(tw[mask][v] for v in Q)
            if lhs <= 0:
                continue
            prebank = lhs - popcount(mask) - slack[mask]
            if prebank <= 0:
                continue
            stats["positive"] += 1
            rec, has_strict, has_flat, has_flat5 = classify_positive_case(
                n, E, B, Mset, M, cyc, Q, mask, lhs, slack[mask], eta
            )
            rec["name"] = name
            stats[f"value:{prebank}"] += 1
            if first_positive is None:
                first_positive = rec
            if max_prebank is None or prebank > max_prebank["prebank"]:
                max_prebank = rec
            if has_strict:
                stats["strict"] += 1
                continue
            stats["no_strict"] += 1
            if max_nostrict_prebank is None or prebank > max_nostrict_prebank["prebank"]:
                max_nostrict_prebank = rec
            if max_nostrict_diff is None or prebank - eta > max_nostrict_diff["prebank_minus_eta"]:
                max_nostrict_diff = rec
            if prebank > eta:
                stats["no_strict_over_eta"] += 1
                if first_over_eta is None:
                    first_over_eta = rec
            if not has_flat:
                stats["no_strict_no_flat"] += 1
                if first_no_flat is None:
                    first_no_flat = rec
            else:
                stats["no_strict_flat"] += 1
            if not has_flat5:
                stats["no_strict_no_flat5"] += 1
                if first_no_flat5 is None:
                    first_no_flat5 = rec
            else:
                stats["no_strict_flat5"] += 1

    return {
        "positive": stats["positive"],
        "stats": stats,
        "max_prebank": max_prebank,
        "max_nostrict_prebank": max_nostrict_prebank,
        "max_nostrict_diff": max_nostrict_diff,
        "first_positive": first_positive,
        "first_over_eta": first_over_eta,
        "first_no_flat": first_no_flat,
        "first_no_flat5": first_no_flat5,
    }


def worker(g6):
    n, edges = dec(g6)
    _adj, cuts = gmins(n, edges)
    stats = Counter()
    cut_count = 0
    max_prebank = None
    max_nostrict_prebank = None
    max_nostrict_diff = None
    first_positive = None
    first_over_eta = None
    first_no_flat = None
    first_no_flat5 = None

    for idx, side in enumerate(cuts):
        r = check_side(f"cen{g6}#cut{idx}", n, edges, side)
        if r is None:
            continue
        cut_count += 1
        stats.update(r["stats"])
        for key in ("max_prebank", "max_nostrict_prebank", "max_nostrict_diff"):
            val = r[key]
            if val is None:
                continue
            if key == "max_nostrict_diff":
                field = "prebank_minus_eta"
            else:
                field = "prebank"
            cur = locals()[key]
            if cur is None or val[field] > cur[field]:
                locals()[key] = val
                if key == "max_prebank":
                    max_prebank = val
                elif key == "max_nostrict_prebank":
                    max_nostrict_prebank = val
                else:
                    max_nostrict_diff = val
        if first_positive is None and r["first_positive"] is not None:
            first_positive = r["first_positive"]
        if first_over_eta is None and r["first_over_eta"] is not None:
            first_over_eta = r["first_over_eta"]
        if first_no_flat is None and r["first_no_flat"] is not None:
            first_no_flat = r["first_no_flat"]
        if first_no_flat5 is None and r["first_no_flat5"] is not None:
            first_no_flat5 = r["first_no_flat5"]

    return {
        "g6": g6,
        "cuts": cut_count,
        "stats": stats,
        "max_prebank": max_prebank,
        "max_nostrict_prebank": max_nostrict_prebank,
        "max_nostrict_diff": max_nostrict_diff,
        "first_positive": first_positive,
        "first_over_eta": first_over_eta,
        "first_no_flat": first_no_flat,
        "first_no_flat5": first_no_flat5,
    }


def choose_max(cur, val, field):
    if val is None:
        return cur
    if cur is None or val[field] > cur[field]:
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
    cuts = 0
    done = 0
    max_prebank = None
    max_nostrict_prebank = None
    max_nostrict_diff = None
    first_positive = None
    first_over_eta = None
    first_no_flat = None
    first_no_flat5 = None

    with mp.Pool(processes=args.workers) as pool:
        for r in pool.imap_unordered(worker, graphs, chunksize=args.chunksize):
            done += 1
            cuts += r["cuts"]
            stats.update(r["stats"])
            max_prebank = choose_max(max_prebank, r["max_prebank"], "prebank")
            max_nostrict_prebank = choose_max(max_nostrict_prebank, r["max_nostrict_prebank"], "prebank")
            max_nostrict_diff = choose_max(max_nostrict_diff, r["max_nostrict_diff"], "prebank_minus_eta")
            if first_positive is None and r["first_positive"] is not None:
                first_positive = r["first_positive"]
            if first_over_eta is None and r["first_over_eta"] is not None:
                first_over_eta = r["first_over_eta"]
            if first_no_flat is None and r["first_no_flat"] is not None:
                first_no_flat = r["first_no_flat"]
            if first_no_flat5 is None and r["first_no_flat5"] is not None:
                first_no_flat5 = r["first_no_flat5"]
            if done % 250 == 0:
                print(f"progress graphs={done}/{len(graphs)} cuts={cuts} positive={stats['positive']}", flush=True)

    print("=== banked flat-cell gate ===")
    print("n:", args.n)
    print("graphs:", len(graphs))
    print("cuts:", cuts)
    print("positive_cases:", stats["positive"])
    print("strict_cases:", stats["strict"])
    print("no_strict_cases:", stats["no_strict"])
    print("no_strict_flat:", stats["no_strict_flat"])
    print("no_strict_flat5:", stats["no_strict_flat5"])
    print("no_strict_over_eta:", stats["no_strict_over_eta"])
    print("no_strict_no_flat:", stats["no_strict_no_flat"])
    print("no_strict_no_flat5:", stats["no_strict_no_flat5"])
    value_counts = {k: v for k, v in sorted(stats.items()) if k.startswith("value:")}
    print("prebank_values:", value_counts)
    print("max_prebank:", fmt_rec(max_prebank))
    print("max_nostrict_prebank:", fmt_rec(max_nostrict_prebank))
    print("max_nostrict_prebank_minus_eta:", fmt_rec(max_nostrict_diff))
    print("first_positive:", fmt_rec(first_positive))
    print("first_no_strict_over_eta:", fmt_rec(first_over_eta))
    print("first_no_strict_no_flat:", fmt_rec(first_no_flat))
    print("first_no_strict_no_flat5:", fmt_rec(first_no_flat5))
    verdict = (
        "PASS_BANKED_FLAT5"
        if stats["positive"] and stats["no_strict_over_eta"] == 0 and stats["no_strict_no_flat5"] == 0
        else "CHECK"
    )
    print("VERDICT:", verdict)


if __name__ == "__main__":
    main()
