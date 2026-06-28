"""Codex diagnostic: self-normalized layer prices.

For each bad edge f and layer i, define

  A[f,i] = sum_{v in I_i(f)} p_f(v) S(v)
  R[f]   = sum_i A[f,i] = (O 1)_f
  b[f,i] = R[f] / A[f,i].

Then sum_i 1/b[f,i] = 1 exactly. If the vertex budgets

  sum_{f,i: v in I_i(f)} b[f,i] p_f(v) <= N

hold, these explicit prices give a non-circular layer-price SOS certificate.
This script tests that budget inequality exactly with Fraction arithmetic.
"""

from fractions import Fraction as F
import argparse
import subprocess

from _h import GENG, blow, dec, loads
from _layerprice import layers_of


def exact_pf_and_S(info):
    pfs = {}
    S = {v: F(0) for v in range(info["n"])}
    for f in info["M"]:
        paths = info["cyc"][f]
        den = len(paths)
        cnt = {}
        for path in paths:
            for v in path:
                cnt[v] = cnt.get(v, 0) + 1
        pf = {v: F(c, den) for v, c in cnt.items()}
        pfs[f] = pf
        for v, val in pf.items():
            S[v] += val
    return pfs, S


def check_info(info):
    n = info["n"]
    pfs, S = exact_pf_and_S(info)
    budget = {v: F(0) for v in range(n)}
    edge_rows = {}
    for f in info["M"]:
        lay, _, h = layers_of(info, f)
        pf = pfs[f]
        A = []
        for i in range(h + 1):
            a = sum(pf[v] * S[v] for v in lay[i])
            if a <= 0:
                raise AssertionError((f, i, a))
            A.append(a)
        R = sum(A)
        edge_rows[f] = R
        for i, a in enumerate(A):
            b = R / a
            for v in lay[i]:
                budget[v] += b * pf[v]
    worst_v = max(range(n), key=lambda v: budget[v] - n)
    worst_gap = budget[worst_v] - n
    worst_row_f = max(edge_rows, key=lambda f: edge_rows[f] - n) if edge_rows else None
    worst_row_gap = (edge_rows[worst_row_f] - n) if worst_row_f else F(0)
    return worst_gap, worst_v, budget[worst_v], worst_row_gap, worst_row_f, edge_rows.get(worst_row_f, F(0))


def blowup_edges(n, edges, t):
    out = []
    for a, b in edges:
        for i in range(t):
            for j in range(t):
                out.append((a * t + i, b * t + j))
    return n * t, out


def run_named():
    cases = [
        ("FCp`_", 1),
        ("H?bB@_W", 1),
        ("I?BD@g]Qo", 1),
        ("I?ABCc]}?", 1),
        ("J?AEB?oE?W?", 1),
        ("J???E?pNu\\?", 2),
        ("J?`@C_W{Ck?", 1),
        ("J?AA@AW^?}?", 1),
        ("I?AAD@wF_", 1),
    ]
    for g6, t in cases:
        n, e = dec(g6)
        if t != 1:
            n, e = blowup_edges(n, e, t)
        info = loads(n, e)
        if info is None:
            print(f"{g6}[{t}] skipped", flush=True)
            continue
        wg, v, bud, rg, f, row = check_info(info)
        print(
            f"{g6}[{t}] N={n} Gamma={info['G']} |M|={len(info['M'])} "
            f"budget_gap={wg} ({float(wg):+.6f}) v={v} budget={bud} "
            f"row_gap={rg} ({float(rg):+.6f}) f={f} row={row}",
            flush=True,
        )


def run_blowups():
    for t in range(1, 8):
        n, e = blow(t)
        info = loads(n, e)
        if info is None:
            continue
        wg, v, bud, rg, f, row = check_info(info)
        print(
            f"C5[{t}] N={n} Gamma={info['G']} |M|={len(info['M'])} "
            f"budget_gap={wg} ({float(wg):+.6f}) v={v} budget={bud} "
            f"row_gap={rg} ({float(rg):+.6f}) f={f} row={row}",
            flush=True,
        )


def run_census(nmax=10, stride=1):
    count = 0
    bad_budget = 0
    bad_row = 0
    worst = None
    for n in range(5, nmax + 1):
        graphs = subprocess.run(
            [GENG, "-tc", str(n)], capture_output=True, text=True
        ).stdout.split()[::stride]
        for g6 in graphs:
            nn, e = dec(g6)
            info = loads(nn, e)
            if info is None:
                continue
            count += 1
            wg, v, bud, rg, f, row = check_info(info)
            if wg > 0:
                bad_budget += 1
            if rg > 0:
                bad_row += 1
            item = (wg, g6, nn, v, bud, rg, f, row, info["G"], len(info["M"]))
            if worst is None or wg > worst[0]:
                worst = item
        print(f"N={n} done", flush=True)
    print(
        f"census count={count} bad_budget={bad_budget} bad_row={bad_row} "
        f"worst_budget_gap={worst[0]} ({float(worst[0]):+.6f}) "
        f"g6={worst[1]} N={worst[2]} v={worst[3]} budget={worst[4]} "
        f"row_gap={worst[5]} f={worst[6]} row={worst[7]} "
        f"Gamma={worst[8]} |M|={worst[9]}",
        flush=True,
    )


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["all", "named", "blowups", "census"], default="all")
    ap.add_argument("--nmax", type=int, default=10)
    ap.add_argument("--stride", type=int, default=1)
    args = ap.parse_args()
    if args.mode in ("all", "named"):
        print("=== named / witness cases ===", flush=True)
        run_named()
    if args.mode in ("all", "blowups"):
        print("\n=== C5 blowups ===", flush=True)
        run_blowups()
    if args.mode in ("all", "census"):
        print(f"\n=== census N<={args.nmax} stride={args.stride} ===", flush=True)
        run_census(args.nmax, args.stride)
