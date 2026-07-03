"""Bank0 LABEL-branch finish gate (sibling skeleton steps 8-9), exact.

For every B-connected gamma-min max cut with ALL bad edges length 5:
  * search a C5-homomorphism lambda: V -> Z5 (every edge maps to adjacent
    classes; backtracking, N <= 11 so trivial);
  * if one exists, verify the TEMPLATE-CUT inequalities m <= e_i for all five
    cyclic class pairs (e_i = edges between class i and i+1), which is the
    sound step: cut(T_i) = e - e_i <= maxcut = e - m;
  * verify the AM-GM chain end: 25 m <= (sum n_i)^2 <= N^2;
  * separately check ROW MONOTONICITY: does the found hom make every certified
    row class-monotone (lambda(p_j) = lambda(p_0) +- j)? The sibling voltage
    model assumes this; if homs exist that are NOT row-monotone, the voltage
    lemma needs the monotone form proven or the constraint relaxed.
Counts: labelable cuts (hom exists) vs non-C5-colorable (CROSS/OSC/NCH domain).
FAIL only if a hom exists but a template inequality fails (would falsify the
finish); everything else is reporting.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import subprocess
from fractions import Fraction as F

with contextlib.redirect_stdout(io.StringIO()):
    from _bdef_construct import Cn, mycielski, union_disjoint
    from _codex_rowcap_non5_half_gate import adj_of
    from _h import Bconn, GENG, dec
    from _satzmu_conn import struct_for_side
    from _stark1 import gmins


def norm(e):
    u, v = e
    return (u, v) if u < v else (v, u)


def c5_hom(n, edges):
    """Backtracking C5-homomorphism search. Returns labels list or None."""
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    lab = [None] * n
    order = sorted(range(n), key=lambda v: -len(adj[v]))

    def ok(v, c):
        for w in adj[v]:
            if lab[w] is not None and (lab[w] - c) % 5 not in (1, 4):
                return False
        return True

    def bt(k):
        if k == len(order):
            return True
        v = order[k]
        cands = range(5) if all(lab[w] is None for w in adj[v]) and k > 0 else range(5)
        for c in (cands if k else [0]):
            if ok(v, c):
                lab[v] = c
                if bt(k + 1):
                    return True
                lab[v] = None
        return False

    return lab if bt(0) else None


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
    if any(ell_raw[g] != 5 for g in M_raw):
        return
    m = len(M)
    acc["pure_cuts"] += 1

    lab = acc["hom_cache"].get(name)
    if name not in acc["hom_cache"]:
        lab = c5_hom(n, list(map(norm, edges)))
        acc["hom_cache"][name] = lab
    if lab is None:
        acc["no_hom_cuts"] += 1
        return
    acc["hom_cuts"] += 1

    # template inequalities
    e_pair = [0] * 5
    for u, v in map(norm, edges):
        d = (lab[v] - lab[u]) % 5
        i = lab[u] if d == 1 else lab[v]
        e_pair[i] += 1
    if any(m > e_pair[i] for i in range(5)):
        acc["template_fails"] += 1
        if acc["first_template_fail"] is None:
            acc["first_template_fail"] = (name, "".join(map(str, side)), m, e_pair)
    tmargin = min(e_pair) - m
    if tmargin < acc["min_template_margin"][0]:
        acc["min_template_margin"] = (tmargin, name, m, tuple(e_pair))

    # AM-GM end: 25m <= N^2 (implied; assert exactly)
    if 25 * m > n * n:
        acc["amgm_fails"] += 1

    # row monotonicity under this hom
    cyc = {norm(g): [tuple(P) for P in rows] for g, rows in cyc_raw.items()}
    mono_ok = True
    for f in M:
        for P in cyc[f]:
            if len(P) != 5:
                continue
            d1 = all((lab[P[j + 1]] - lab[P[j]]) % 5 == 1 for j in range(4))
            d4 = all((lab[P[j + 1]] - lab[P[j]]) % 5 == 4 for j in range(4))
            if not (d1 or d4):
                mono_ok = False
    if not mono_ok:
        acc["nonmono_cuts"] += 1
        if acc["first_nonmono"] is None:
            acc["first_nonmono"] = (name, "".join(map(str, side)))


def run_gmins(name, n, edges, acc):
    _a, cuts = gmins(n, edges)
    for side_l in cuts:
        side = [int(c) for c in side_l]
        check_cut(name, n, edges, side, acc)


def bridge(b1, b2, u, v):
    n, edges = union_disjoint(b1, b2)
    return n, edges + [(u, b1[0] + v)]


def c5blow(t):
    n = 5 * t
    edges = []
    for i in range(5):
        for a in range(t):
            for b in range(t):
                edges.append((i * t + a, ((i + 1) % 5) * t + b))
    return n, edges


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-n", type=int, default=8)
    ap.add_argument("--max-n", type=int, default=9)
    args = ap.parse_args()

    acc = {
        "pure_cuts": 0, "hom_cuts": 0, "no_hom_cuts": 0,
        "template_fails": 0, "amgm_fails": 0, "nonmono_cuts": 0,
        "first_template_fail": None, "first_nonmono": None,
        "min_template_margin": (10**9, None, None, None),
        "hom_cache": {},
    }

    for name, (n, edges) in [
        ("Grotzsch", mycielski(5, Cn(5))),
        ("M(C7)", mycielski(7, Cn(7))),
        ("C7|Grotzsch", bridge((7, Cn(7)), mycielski(5, Cn(5)), 0, 0)),
        ("C5[2]", c5blow(2)),
        ("C5[3]", c5blow(3)),
    ]:
        run_gmins(name, n, edges, acc)

    for nn in range(args.min_n, args.max_n + 1):
        out = subprocess.run([GENG, "-tc", str(nn)], capture_output=True,
                             text=True, check=True).stdout
        for g6 in out.split():
            n, edges = dec(g6)
            run_gmins(f"cen:{g6}", n, edges, acc)

    print("=== Bank0 LABEL-chain gate ===")
    for k in ("pure_cuts", "hom_cuts", "no_hom_cuts", "template_fails",
              "amgm_fails", "nonmono_cuts"):
        print(f"{k}: {acc[k]}")
    print("min_template_margin:", acc["min_template_margin"])
    print("first_template_fail:", acc["first_template_fail"])
    print("first_nonmono:", acc["first_nonmono"])
    print("VERDICT:", "FAIL" if (acc["template_fails"] or acc["amgm_fails"]) else "PASS")


if __name__ == "__main__":
    main()
