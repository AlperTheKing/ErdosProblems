"""Deletion profile of Flat5 bank peels in positive Slack-CAGE prebank cases."""

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
    for key in ("prebank", "pre_after", "raw_drop", "bank", "delD", "sigma_diff", "eta"):
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
    first = None
    max_deleted = None
    max_raw = None
    for _f, Q in q_rows:
        qset = set(Q)
        for mask in range(1, allmask):
            lhs = sum(tw[mask][v] for v in Q)
            if lhs <= 0:
                continue
            prebank = lhs - popcount(mask) - slack[mask]
            if prebank <= 0:
                continue
            U = mask_to_set(mask, n)
            rows = counted_rows(Q, U, M, cyc)
            _switches, zero, strict, flat = classify_case(n, E, B, Mset, Q, U, rows)
            if strict:
                continue

            best = None
            for _sig, _dg, Stuple in zero:
                if not is_flat5_switch(n, E, B, Mset, Stuple):
                    continue
                smask = set_to_mask(Stuple)
                after = mask & ~smask
                U2 = mask_to_set(after, n)
                pre_after = sum(tw[after][v] for v in Q) - popcount(after) - slack[after]
                deleted = []
                delD = F(0)
                for g, P, pset in rows:
                    if pset <= U and not pset <= U2:
                        mass = F(1, len(cyc[g]))
                        inter = len(set(P) & qset)
                        delD += mass * inter
                        deleted.append((g, tuple(P), mass, inter))
                sigma_diff = slack[mask] - slack[after]
                raw_drop = prebank - pre_after
                bank = prebank - max(F(0), pre_after)
                rec = {
                    "name": name,
                    "n": n,
                    "m": len(M),
                    "eta": eta,
                    "Q": tuple(Q),
                    "U": tuple(sorted(U)),
                    "S": tuple(sorted(Stuple)),
                    "prebank": prebank,
                    "pre_after": pre_after,
                    "raw_drop": raw_drop,
                    "bank": bank,
                    "delD": delD,
                    "sigma_diff": sigma_diff,
                    "deleted_count": len(deleted),
                    "deleted_profile": tuple(sorted((len(P), fmt_frac(mass), inter) for _g, P, mass, inter in deleted)),
                    "deleted_edges": tuple((g, P) for g, P, _mass, _inter in deleted),
                }
                if best is None or max(F(0), pre_after) < max(F(0), best["pre_after"]):
                    best = rec
            if best is None:
                stats["no_flat5"] += 1
                continue
            stats["cases"] += 1
            stats[f"deleted:{best['deleted_profile']}"] += 1
            stats[f"raw:{best['raw_drop']}"] += 1
            stats[f"delD:{best['delD']}"] += 1
            stats[f"sigma_diff:{best['sigma_diff']}"] += 1
            if first is None:
                first = best
            if max_deleted is None or best["deleted_count"] > max_deleted["deleted_count"]:
                max_deleted = best
            if max_raw is None or best["raw_drop"] > max_raw["raw_drop"]:
                max_raw = best
    return {"stats": stats, "first": first, "max_deleted": max_deleted, "max_raw": max_raw}


def worker(g6):
    n, edges = dec(g6)
    _adj, cuts = gmins(n, edges)
    stats = Counter()
    first = None
    max_deleted = None
    max_raw = None
    for idx, side in enumerate(cuts):
        r = check_side(f"cen{g6}#cut{idx}", n, edges, side)
        if r is None:
            continue
        stats.update(r["stats"])
        if first is None and r["first"] is not None:
            first = r["first"]
        if r["max_deleted"] is not None and (
            max_deleted is None or r["max_deleted"]["deleted_count"] > max_deleted["deleted_count"]
        ):
            max_deleted = r["max_deleted"]
        if r["max_raw"] is not None and (max_raw is None or r["max_raw"]["raw_drop"] > max_raw["raw_drop"]):
            max_raw = r["max_raw"]
    return {"stats": stats, "first": first, "max_deleted": max_deleted, "max_raw": max_raw}


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
    ap.add_argument("--chunksize", type=int, default=8)
    args = ap.parse_args()

    graphs = subprocess.run([GENG, "-tc", str(args.n)], capture_output=True, text=True, check=True).stdout.split()
    stats = Counter()
    first = None
    max_deleted = None
    max_raw = None
    done = 0
    with mp.Pool(processes=args.workers) as pool:
        for r in pool.imap_unordered(worker, graphs, chunksize=args.chunksize):
            done += 1
            stats.update(r["stats"])
            if first is None and r["first"] is not None:
                first = r["first"]
            max_deleted = choose_max(max_deleted, r["max_deleted"], "deleted_count")
            max_raw = choose_max(max_raw, r["max_raw"], "raw_drop")
            if done % 500 == 0:
                print(f"progress graphs={done}/{len(graphs)} cases={stats['cases']}", flush=True)

    print("=== Flat5 deletion profile ===")
    print("n:", args.n)
    print("graphs:", len(graphs))
    print("cases:", stats["cases"])
    for k, v in sorted(stats.items()):
        if k != "cases":
            print(k, ":", v)
    print("first:", fmt_rec(first))
    print("max_deleted:", fmt_rec(max_deleted))
    print("max_raw:", fmt_rec(max_raw))
    print("VERDICT:", "PROFILED" if stats["cases"] else "CHECK")


if __name__ == "__main__":
    main()
