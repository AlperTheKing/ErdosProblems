"""Quotient diagnostics for pure-K full-inverse cond3 on odd-cycle blow-ups.

For C_m[n_0,...,n_{m-1}] with one monochromatic minimum-product edge
(b,b+1), every bad-edge geodesic follows the complementary B-path and
hits every part exactly once.  By part symmetry, the full inverse

    A_QQ g = (N-T)_Q,  A=N I-K

collapses to one scalar S=sum_{Q parts} g_i:

    P_i = sum_f p_f(v) for v in part i,
    T_i = m * P_i,       m = odd cycle length,
    g_i = (N-T_i + P_i*S)/N,
    S = sum_{i in Q} (N-T_i) / (N - sum_{i in Q} P_i).

Then cond3 for overloaded part i is simply:

    N - T_i + P_i*S >= 0.

This script stress-tests that exact quotient inequality and reports the
worst margin.  It also reports the diagonal ROWSUM margin for comparison.
"""
from __future__ import annotations

import argparse
import random
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction as F
from itertools import combinations


def p_values(parts, bad):
    m = len(parts)
    a = bad
    b = (bad + 1) % m
    nbad = parts[a] * parts[b]
    out = []
    for i, ni in enumerate(parts):
        if i == a:
            out.append(F(parts[b]))
        elif i == b:
            out.append(F(parts[a]))
        else:
            out.append(F(nbad, ni))
    return out


def check_instance(parts, bad, require_gamma_gt_n2=False):
    m = len(parts)
    N = sum(parts)
    nbad = parts[bad] * parts[(bad + 1) % m]
    Gamma = m * m * nbad
    if require_gamma_gt_n2 and Gamma <= N * N:
        return None
    P = p_values(parts, bad)
    a = bad
    b = (bad + 1) % m
    spec_row = F(parts[a] + parts[b])
    for i in range(m):
        if i not in (a, b):
            spec_row += F(nbad, parts[i])
    T = [F(m) * x for x in P]
    O = [i for i, t in enumerate(T) if t > N]
    if not O:
        return None
    Q = [i for i in range(m) if i not in O]
    denom = F(N) - sum(P[i] for i in Q)
    if denom <= 0:
        return {
            "parts": tuple(parts),
            "bad": bad,
            "fail": "denom",
            "denom": denom,
        }
    S = sum(F(N) - T[i] for i in Q) / denom
    full_margins = {i: F(N) - T[i] + P[i] * S for i in O}

    # Diagonal ROWSUM surrogate for comparison.  For a vertex in O part i,
    # K[i,j] per target vertex equals P_i*P_j/nbad in this quotient.
    rowsum_margins = {}
    for i in O:
        lhs = F(0)
        for j in Q:
            Rj = F(N) - T[j]
            if Rj <= 0:
                continue
            kij = P[i] * P[j] / nbad
            sj = parts[i] * kij if len(O) == 1 else sum(parts[o] * (P[o] * P[j] / nbad) for o in O)
            lhs += parts[j] * kij * Rj / (Rj + sj)
        rowsum_margins[i] = lhs - (T[i] - N)

    min_full = min(full_margins.values())
    min_row = min(rowsum_margins.values())
    return {
        "parts": tuple(parts),
        "bad": bad,
        "N": N,
        "Gamma": Gamma,
        "O": tuple(O),
        "T": tuple(T),
        "S": S,
        "full_min": min_full,
        "row_min": min_row,
        "spec_row": spec_row,
        "spec_margin": F(N) - spec_row,
        "full_margins": full_margins,
        "rowsum_margins": rowsum_margins,
    }


def random_parts(m, total, rng):
    # Heavy-tailed composition: start positive, then drop mass in random bins.
    parts = [1] * m
    for _ in range(total - m):
        if rng.random() < 0.75:
            idx = rng.randrange(m)
        else:
            idx = int(rng.random() ** 3 * m) % m
        parts[idx] += 1
    rng.shuffle(parts)
    return parts


def worker(args):
    m, total_min, total_max, count, seed, targeted, require_gamma_gt_n2 = args
    rng = random.Random(seed)
    worst_full = None
    worst_row = None
    worst_spec = None
    row_fails = 0
    full_fails = 0
    spec_fails = 0
    seen = 0
    for _ in range(count):
        if targeted and m == 7:
            # Obstruction-shaped C7 family:
            #   (x,A,B,y,C,y,A), bad edge index 2 with product B*y.
            # Keep x,y small and A large; B,C medium/large.
            x = rng.randint(1, 12)
            y = rng.randint(1, 12)
            A = rng.randint(max(10, total_min // 5), max(20, total_max // 2))
            B = rng.randint(max(2, total_min // 20), max(5, total_max // 4))
            C = rng.randint(max(2, total_min // 20), max(5, total_max // 4))
            parts = [x, A, B, y, C, y, A]
        else:
            total = rng.randint(total_min, total_max)
            parts = random_parts(m, total, rng)
        products = [parts[i] * parts[(i + 1) % m] for i in range(m)]
        minprod = min(products)
        for bad in [i for i, p in enumerate(products) if p == minprod]:
            r = check_instance(parts, bad, require_gamma_gt_n2=require_gamma_gt_n2)
            if r is None:
                continue
            seen += 1
            if r.get("fail") == "denom":
                full_fails += 1
                continue
            if r["full_min"] < 0:
                full_fails += 1
            if r["row_min"] < 0:
                row_fails += 1
            if r["spec_margin"] < 0:
                spec_fails += 1
            if worst_full is None or r["full_min"] < worst_full["full_min"]:
                worst_full = r
            if worst_row is None or r["row_min"] < worst_row["row_min"]:
                worst_row = r
            if worst_spec is None or r["spec_margin"] < worst_spec["spec_margin"]:
                worst_spec = r
    return seen, full_fails, row_fails, spec_fails, worst_full, worst_row, worst_spec


def fmt_frac(x):
    return f"{x} ({float(x):.6g})"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--m", type=int, default=7, help="odd cycle length")
    ap.add_argument("--samples", type=int, default=20000)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--min-n", type=int, default=20)
    ap.add_argument("--max-n", type=int, default=1500)
    ap.add_argument("--seed", type=int, default=23)
    ap.add_argument("--check-c7", action="store_true")
    ap.add_argument("--target-c7", action="store_true", help="sample the C7 obstruction-shaped family")
    ap.add_argument("--active-only", action="store_true", help="only keep instances with Gamma>N^2")
    args = ap.parse_args()
    if args.check_c7:
        r = check_instance([3, 423, 173, 7, 176, 7, 423], 2)
        print("C7 GPT-Pro instance")
        print("  full_min", fmt_frac(r["full_min"]))
        print("  row_min", fmt_frac(r["row_min"]))
        print("  SPEC row", fmt_frac(r["spec_row"]), "margin", fmt_frac(r["spec_margin"]))
        print("  O", r["O"], "S", fmt_frac(r["S"]))
    jobs = []
    per = (args.samples + args.workers - 1) // args.workers
    for w in range(args.workers):
        c = min(per, max(0, args.samples - w * per))
        if c:
            jobs.append((args.m, args.min_n, args.max_n, c, args.seed + 1009 * w, args.target_c7, args.active_only))
    total_seen = total_full = total_row = total_spec = 0
    worst_full = worst_row = worst_spec = None
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        for seen, ff, rf, sf, wf, wr, ws in ex.map(worker, jobs):
            total_seen += seen
            total_full += ff
            total_row += rf
            total_spec += sf
            if wf is not None and (worst_full is None or wf["full_min"] < worst_full["full_min"]):
                worst_full = wf
            if wr is not None and (worst_row is None or wr["row_min"] < worst_row["row_min"]):
                worst_row = wr
            if ws is not None and (worst_spec is None or ws["spec_margin"] < worst_spec["spec_margin"]):
                worst_spec = ws
    print(f"m={args.m} samples={args.samples} quotient_instances={total_seen}")
    print(f"full_inverse_fails={total_full} diagonal_rowsum_fails={total_row} spec_rowsum_fails={total_spec}")
    if worst_full:
        print("worst_full:")
        print("  parts", worst_full["parts"], "bad", worst_full["bad"], "N", worst_full["N"], "Gamma", worst_full["Gamma"], "O", worst_full["O"])
        print("  full_min", fmt_frac(worst_full["full_min"]), "row_min", fmt_frac(worst_full["row_min"]))
        print("  spec_margin", fmt_frac(worst_full["spec_margin"]))
    if worst_row:
        print("worst_rowsum:")
        print("  parts", worst_row["parts"], "bad", worst_row["bad"], "N", worst_row["N"], "Gamma", worst_row["Gamma"], "O", worst_row["O"])
        print("  full_min", fmt_frac(worst_row["full_min"]), "row_min", fmt_frac(worst_row["row_min"]))
        print("  spec_margin", fmt_frac(worst_row["spec_margin"]))
    if worst_spec:
        print("worst_SPEC_rowsum:")
        print("  parts", worst_spec["parts"], "bad", worst_spec["bad"], "N", worst_spec["N"], "Gamma", worst_spec["Gamma"], "O", worst_spec["O"])
        print("  spec_row", fmt_frac(worst_spec["spec_row"]), "spec_margin", fmt_frac(worst_spec["spec_margin"]))
        print("  full_min", fmt_frac(worst_spec["full_min"]), "row_min", fmt_frac(worst_spec["row_min"]))


if __name__ == "__main__":
    main()
