"""Codex diagnostic: proportional overload paid by individual geodesic blocks.

This tests a possible sufficient proof of SPEC:

  N I - K = (diag(T) - K) + diag(N - T)
          = sum_f (ell(f) diag(p_f) - p_f p_f^T) - diag((T-N)_+) + PSD diagonal.

Assign each positive overload o(v)=(T(v)-N)_+ proportionally to the
edge-blocks passing through v:

  q_f(v) = o(v) * ell(f) p_f(v) / T(v).

Then sum_f q_f(v)=o(v). If every block

  ell(f) diag(p_f) - p_f p_f^T - diag(q_f)

is PSD, the sufficient certificate works.

The check is exact Fraction arithmetic using the diagonal-minus-rank-one
criterion. It is only a diagnostic; failures are expected to guide grouping.
"""

from fractions import Fraction as F
import argparse
from collections import deque
import subprocess

import numpy as np

from _h import GENG, blow, dec, loads


def pf_exact(info):
    out = {}
    for f in info["M"]:
        paths = info["cyc"][f]
        den = len(paths)
        cnt = {}
        for path in paths:
            for v in path:
                cnt[v] = cnt.get(v, 0) + 1
        out[f] = {v: F(c, den) for v, c in cnt.items()}
    return out


def block_gap(info, f, pf):
    """Return criterion value - 1 for the adjusted f-block.

    For C=diag(D)-p p^T with p supported where D>0, PSD iff
    sum_v p(v)^2/D(v) <= 1. A positive return value is a failure.
    """
    n = info["n"]
    T = info["T"]
    ell = F(info["ell"][f])
    crit = F(0)
    minD = None
    for v, pv in pf.items():
        overload = T[v] - n if T[v] > n else F(0)
        q = overload * ell * pv / T[v] if T[v] else F(0)
        D = ell * pv - q
        if minD is None or D < minD:
            minD = D
        if D <= 0:
            return None, minD
        crit += pv * pv / D
    return crit - 1, minD


def check_info(info):
    pfs = pf_exact(info)
    worst = None
    for f, pf in pfs.items():
        gap, minD = block_gap(info, f, pf)
        if gap is None:
            item = (F(10**9), f, gap, minD)
        else:
            item = (gap, f, gap, minD)
        if worst is None or item[0] > worst[0]:
            worst = item
    return worst


def support_components(pfs):
    keys = list(pfs)
    m = len(keys)
    supports = [set(pfs[f]) for f in keys]
    adj = [set() for _ in range(m)]
    for i in range(m):
        for j in range(i + 1, m):
            if supports[i] & supports[j]:
                adj[i].add(j)
                adj[j].add(i)
    seen = [False] * m
    comps = []
    for i in range(m):
        if seen[i]:
            continue
        seen[i] = True
        q = deque([i])
        comp = []
        while q:
            u = q.popleft()
            comp.append(keys[u])
            for v in adj[u]:
                if not seen[v]:
                    seen[v] = True
                    q.append(v)
        comps.append(comp)
    return comps


def group_matrix(info, pfs, comp):
    n = info["n"]
    T = info["T"]
    verts = sorted({v for f in comp for v in pfs[f]})
    ix = {v: i for i, v in enumerate(verts)}
    mat = np.zeros((len(verts), len(verts)))
    qsum = {v: F(0) for v in verts}
    for f in comp:
        ell = F(info["ell"][f])
        pf = pfs[f]
        for v, pv in pf.items():
            i = ix[v]
            mat[i, i] += float(ell * pv)
            overload = T[v] - n if T[v] > n else F(0)
            q = overload * ell * pv / T[v] if T[v] else F(0)
            qsum[v] += q
        for v, pv in pf.items():
            i = ix[v]
            for w, pw in pf.items():
                mat[i, ix[w]] -= float(pv * pw)
    for v, q in qsum.items():
        mat[ix[v], ix[v]] -= float(q)
    return mat, verts


def check_groups(info):
    pfs = pf_exact(info)
    comps = support_components(pfs)
    worst_comp = None
    for comp in comps:
        mat, verts = group_matrix(info, pfs, comp)
        mineig = float(np.linalg.eigvalsh(mat).min()) if len(verts) else 0.0
        item = (mineig, comp, len(verts))
        if worst_comp is None or mineig < worst_comp[0]:
            worst_comp = item
    mat, verts = group_matrix(info, pfs, list(pfs))
    all_min = float(np.linalg.eigvalsh(mat).min()) if len(verts) else 0.0
    return worst_comp, (all_min, len(verts))


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
            print(f"{g6}[{t}] skipped")
            continue
        gap, f, _, minD = check_info(info)
        print(
            f"{g6}[{t}] N={n} Gamma={info['G']} |M|={len(info['M'])} "
            f"worst_gap={gap} ({float(gap):+.6f}) f={f} minD={minD}",
            flush=True,
        )
        comp, all_group = check_groups(info)
        print(
            f"  support-comp min_eig={comp[0]:+.6e} "
            f"comp_size={len(comp[1])} support={comp[2]} | "
            f"all-M min_eig={all_group[0]:+.6e} support={all_group[1]}",
            flush=True,
        )


def run_census(nmax=10, stride=1):
    worst = None
    count = 0
    bad = 0
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
            gap, f, _, minD = check_info(info)
            if gap > 0:
                bad += 1
            item = (gap, g6, nn, f, minD, info["G"], len(info["M"]))
            if worst is None or gap > worst[0]:
                worst = item
        print(f"N={n} done", flush=True)
    print(
        "census "
        f"count={count} bad={bad} worst_gap={worst[0]} "
        f"({float(worst[0]):+.6f}) g6={worst[1]} N={worst[2]} "
        f"f={worst[3]} minD={worst[4]} Gamma={worst[5]} |M|={worst[6]}",
        flush=True,
    )


def run_blowups():
    for t in range(1, 8):
        n, e = blow(t)
        info = loads(n, e)
        if info is None:
            continue
        gap, f, _, minD = check_info(info)
        print(
            f"C5[{t}] N={n} Gamma={info['G']} |M|={len(info['M'])} "
            f"worst_gap={gap} ({float(gap):+.6f}) f={f} minD={minD}",
            flush=True,
        )


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--mode",
        choices=["all", "named", "blowups", "census"],
        default="all",
    )
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
