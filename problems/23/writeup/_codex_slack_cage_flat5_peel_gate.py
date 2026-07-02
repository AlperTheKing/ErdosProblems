"""Positive-part Flat5 peel gate for Slack-CAGE.

This checks the corrected bank demand from the Xi2/Flat5 plan:

    bank_i = max(0, pre(U_{i-1})) - max(0, pre(U_i)).

For every positive proper-counted prebank case, the strong finite gate asks
whether either a strict zero-slack Gamma drop exists, or a Flat5 zero-slack
core switch S has

    pre(U - S) <= 0.

Equivalently, one Flat5 peel consumes all currently positive prebank.  This is
a stress verifier, not a proof.
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
    from _codex_slack_cage_switch_gate import build_data
    from _codex_slack_cage_banked_flat_gate import is_flat5_switch


def mask_to_set(mask, n):
    return frozenset(i for i in range(n) if (mask >> i) & 1)


def set_to_mask(S):
    out = 0
    for v in S:
        out |= 1 << v
    return out


def fmt_frac(x):
    if isinstance(x, F):
        return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"
    return str(x)


def fmt_rec(rec):
    if rec is None:
        return ""
    out = dict(rec)
    for key in ("eta", "lhs", "prebank", "pre_after", "bank", "margin"):
        if key in out:
            out[key] = fmt_frac(out[key])
    return out


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
    first_fail = None
    first_pass = None
    max_prebank = None
    max_bank = None

    for _f, Q in q_rows:
        for mask in range(1, allmask):
            lhs = sum(tw[mask][v] for v in Q)
            if lhs <= 0:
                continue
            prebank = lhs - popcount(mask) - slack[mask]
            if prebank <= 0:
                continue
            stats["positive"] += 1
            U = mask_to_set(mask, n)
            rows = counted_rows(Q, U, M, cyc)
            _switches, zero, strict, flat = classify_case(n, E, B, Mset, Q, U, rows)
            if strict:
                stats["strict"] += 1
                continue

            stats["needs_bank"] += 1
            best = None
            flat5_count = 0
            for sig, dg, Stuple in zero:
                if not is_flat5_switch(n, E, B, Mset, Stuple):
                    continue
                flat5_count += 1
                smask = set_to_mask(Stuple)
                after = mask & ~smask
                pre_after = sum(tw[after][v] for v in Q) - popcount(after) - slack[after]
                bank = prebank - max(F(0), pre_after)
                rec = {
                    "name": name,
                    "n": n,
                    "m": len(M),
                    "eta": eta,
                    "Q": tuple(Q),
                    "U": tuple(sorted(U)),
                    "S": tuple(sorted(Stuple)),
                    "lhs": lhs,
                    "prebank": prebank,
                    "pre_after": pre_after,
                    "bank": bank,
                    "margin": eta - bank,
                    "zero_count": len(zero),
                    "flat_count": len(flat),
                    "flat5_count": flat5_count,
                }
                if best is None or max(F(0), pre_after) < max(F(0), best["pre_after"]):
                    best = rec

            if max_prebank is None or prebank > max_prebank["prebank"]:
                max_prebank = best or {
                    "name": name,
                    "n": n,
                    "m": len(M),
                    "eta": eta,
                    "Q": tuple(Q),
                    "U": tuple(sorted(U)),
                    "prebank": prebank,
                    "pre_after": None,
                    "bank": F(0),
                    "margin": eta,
                }
            if best is not None and (max_bank is None or best["bank"] > max_bank["bank"]):
                max_bank = best

            if best is not None and best["pre_after"] <= 0 and best["bank"] <= eta:
                stats["flat5_consumes_positive"] += 1
                if first_pass is None:
                    first_pass = best
            else:
                stats["fail"] += 1
                if first_fail is None:
                    first_fail = best or {
                        "name": name,
                        "n": n,
                        "m": len(M),
                        "eta": eta,
                        "Q": tuple(Q),
                        "U": tuple(sorted(U)),
                        "prebank": prebank,
                        "pre_after": None,
                        "bank": F(0),
                        "margin": eta,
                        "zero_count": len(zero),
                        "flat_count": len(flat),
                        "flat5_count": 0,
                    }

    return {
        "stats": stats,
        "first_fail": first_fail,
        "first_pass": first_pass,
        "max_prebank": max_prebank,
        "max_bank": max_bank,
    }


def worker(g6):
    n, edges = dec(g6)
    _adj, cuts = gmins(n, edges)
    stats = Counter()
    first_fail = None
    first_pass = None
    max_prebank = None
    max_bank = None
    for idx, side in enumerate(cuts):
        r = check_side(f"cen{g6}#cut{idx}", n, edges, side)
        if r is None:
            continue
        stats.update(r["stats"])
        if first_fail is None and r["first_fail"] is not None:
            first_fail = r["first_fail"]
        if first_pass is None and r["first_pass"] is not None:
            first_pass = r["first_pass"]
        if r["max_prebank"] is not None and (
            max_prebank is None or r["max_prebank"]["prebank"] > max_prebank["prebank"]
        ):
            max_prebank = r["max_prebank"]
        if r["max_bank"] is not None and (max_bank is None or r["max_bank"]["bank"] > max_bank["bank"]):
            max_bank = r["max_bank"]
    return {
        "g6": g6,
        "stats": stats,
        "first_fail": first_fail,
        "first_pass": first_pass,
        "max_prebank": max_prebank,
        "max_bank": max_bank,
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
    first_fail = None
    first_pass = None
    max_prebank = None
    max_bank = None
    done = 0
    with mp.Pool(processes=args.workers) as pool:
        for r in pool.imap_unordered(worker, graphs, chunksize=args.chunksize):
            done += 1
            stats.update(r["stats"])
            if first_fail is None and r["first_fail"] is not None:
                first_fail = r["first_fail"]
            if first_pass is None and r["first_pass"] is not None:
                first_pass = r["first_pass"]
            max_prebank = choose_max(max_prebank, r["max_prebank"], "prebank")
            max_bank = choose_max(max_bank, r["max_bank"], "bank")
            if done % 500 == 0:
                print(f"progress graphs={done}/{len(graphs)} positive={stats['positive']} fail={stats['fail']}", flush=True)

    print("=== positive-part Flat5 peel gate ===")
    print("n:", args.n)
    print("graphs:", len(graphs))
    print("stats:", dict(stats))
    print("max_prebank:", fmt_rec(max_prebank))
    print("max_bank:", fmt_rec(max_bank))
    print("first_pass:", fmt_rec(first_pass))
    print("first_fail:", fmt_rec(first_fail))
    verdict = "PASS_FLAT5_POSITIVE_PART_PEEL" if stats["positive"] and stats["fail"] == 0 else "CHECK"
    print("VERDICT:", verdict)


if __name__ == "__main__":
    main()
