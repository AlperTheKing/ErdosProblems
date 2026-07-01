"""Probe bottlenecks for coefficient-free Schur Absorption-Hall.

The positive-coefficient Schur strengthenings are false on larger C5 blowups.
This probe records only the live coefficient-free quantities:

    singleton:  a_o <= A-a_o  ==>  rho_o >= 0
    subset:     a(X) <= A-a(X) ==>  rho(X) >= 0.

It also prints the exact quotient value for the canonical C5 blowup family
sizes [k+1,k,k+1,k,k+1], where the positive-coefficient targets fail but bare
rho tends to 5/2.
"""

import argparse
import random
import subprocess
from itertools import combinations
from fractions import Fraction as F

from _bdef_construct import Cn, add_edges, is_triangle_free, mycielski, union_disjoint
from _h import Bconn, GENG, dec
from _hardy_gate import BETA, build_H, maxcut_ls
from _Klocal_gate import glued_c5_chain
from _satzmu_conn import struct_for_side
from _schur_absorption_hall_gate import adj_from_edges, schur_on_O
from _stark1 import gmins
from _wf_deficit_farkas import odd_blowup


def push_min(items, key, rec, limit=10):
    items.append((key, rec))
    items.sort(key=lambda x: x[0])
    del items[limit:]


def fmt_rec(rec):
    out = dict(rec)
    for key in ["rho", "a", "A", "aset", "rhoset"]:
        if key in out:
            out[key] = float(out[key])
    return out


def test_cut(name, n, adj, side, acc):
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    M, ell, T, _mu, cyc = st
    if not M:
        return
    N = F(n)
    O = [v for v in range(n) if T[v] > N]
    if not O:
        acc["noO"] += 1
        return
    U = [v for v in range(n) if T[v] <= N]
    H = build_H(n, M, ell, T, cyc, BETA)
    S = schur_on_O(H, O, U)
    acc["Ocuts"] += 1
    if S is None:
        acc["singular"] += 1
        return

    side_s = "".join(map(str, side))
    a = [T[o] - N for o in O]
    A = sum(a)
    rho = [sum(S[i]) for i in range(len(O))]
    R = [i for i, r in enumerate(rho) if r < 0]
    acc["Rhist"][len(R)] = acc["Rhist"].get(len(R), 0) + 1

    for i, o in enumerate(O):
        if a[i] <= A - a[i]:
            rec = {
                "name": name,
                "n": n,
                "side": side_s,
                "o": o,
                "O": tuple(O),
                "a": a[i],
                "A": A,
                "rho": rho[i],
            }
            push_min(acc["singleton"], rho[i], rec)
            if rho[i] < 0:
                acc["singleton_fail"] += 1

    m = len(O)
    for r in range(1, m + 1):
        for X in combinations(range(m), r):
            aset = sum(a[i] for i in X)
            if aset > A - aset:
                continue
            rhoset = sum(rho[i] for i in X)
            rec = {
                "name": name,
                "n": n,
                "side": side_s,
                "X": tuple(O[i] for i in X),
                "O": tuple(O),
                "aset": aset,
                "A": A,
                "rhoset": rhoset,
            }
            push_min(acc["subset"], rhoset, rec)
            acc["subset_checks"] += 1
            if rhoset < 0:
                acc["subset_fail"] += 1


def gfam(name, n, edges, acc):
    adj = adj_from_edges(n, edges)
    try:
        _gamma, cuts = gmins(n, edges)
    except Exception:
        return
    for side in cuts:
        test_cut(name, n, adj, side, acc)


def c5_quotient_rho(k):
    b = BETA[5]
    return b * (k + 1) * (F(3, 3) / (1 + b * k / 3) + F(3, 3) / (1 + 2 * b * k / 3)) - 2


def c5_quotient_rho_clean(k):
    b = BETA[5]
    return b * (k + 1) * (F(3, 1) / (3 + b * k) + F(3, 1) / (3 + 2 * b * k)) - 2


def run(args):
    acc = {
        "Ocuts": 0,
        "noO": 0,
        "singular": 0,
        "Rhist": {},
        "singleton": [],
        "subset": [],
        "singleton_fail": 0,
        "subset_fail": 0,
        "subset_checks": 0,
    }

    for nn in range(args.min_n, args.max_n + 1):
        g6s = subprocess.run(
            [GENG, "-tc", str(nn)], capture_output=True, text=True
        ).stdout.split()
        for g6 in g6s[:: args.census_stride]:
            n, edges = dec(g6)
            gfam(f"cen{nn}", n, edges, acc)
        print(f"census N={nn}: Ocuts={acc['Ocuts']}", flush=True)

    grN, grE = mycielski(5, Cn(5))
    gfam("Grotzsch", grN, grE, acc)
    m2N, m2E = mycielski(grN, grE)
    adj23 = adj_from_edges(m2N, m2E)
    test_cut("MycGrotzsch_N23", m2N, adj23, maxcut_ls(m2N, adj23), acc)

    for q in range(2, 16):
        n, edges, side = glued_c5_chain(q)
        test_cut(f"chain{q}", n, adj_from_edges(n, edges), side, acc)

    for sizes in [
        (2, 1, 2, 1, 2),
        (2, 1, 2, 1, 3),
        (3, 2, 3, 2, 3),
        (4, 3, 4, 3, 4),
        (5, 4, 5, 4, 5),
        (2, 2, 2, 2, 2),
        (3, 3, 3, 3, 3),
    ]:
        n, edges = odd_blowup(5, list(sizes))
        if n <= 24:
            gfam(f"blow{sizes}", n, edges, acc)

    island = (5, Cn(5))
    g15 = mycielski(7, Cn(7))
    n, edges = union_disjoint(island, g15)
    n, edges = add_edges((n, edges), [(0, 5)])
    gfam("island", n, edges, acc)

    rng = random.Random(args.seed)
    made = 0
    tries = 0
    while made < args.random and tries < args.random * 400:
        tries += 1
        nn = rng.choice([11, 12])
        p = rng.uniform(0.14, 0.34)
        edges = [
            (a, b)
            for a in range(nn)
            for b in range(a + 1, nn)
            if rng.random() < p
        ]
        if not edges or not is_triangle_free(nn, edges):
            continue
        adj = adj_from_edges(nn, edges)
        if any(len(adj[v]) == 0 for v in range(nn)):
            continue
        made += 1
        gfam(f"rand{made}", nn, edges, acc)

    print("=" * 72)
    print("Ocuts", acc["Ocuts"], "noO", acc["noO"], "singular", acc["singular"])
    print("Rhist", dict(sorted(acc["Rhist"].items())))
    print("singleton_fail", acc["singleton_fail"])
    print("subset_fail", acc["subset_fail"], "subset_checks", acc["subset_checks"])
    print("weak_singletons")
    for val, rec in acc["singleton"][:8]:
        print(float(val), fmt_rec(rec))
    print("weak_subsets")
    for val, rec in acc["subset"][:8]:
        print(float(val), fmt_rec(rec))

    print("c5_quotient_rho")
    best = None
    for k in [4, 5, 10, 16, 20, 50, 100, 500, 1000]:
        rho = c5_quotient_rho_clean(k)
        if best is None or rho < best[0]:
            best = (rho, k)
        print("k", k, "N", 5 * k + 3, "rho", float(rho), "exact", rho)
    print("c5_quotient_best_listed", best[1], float(best[0]), best[0])


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-n", type=int, default=5)
    parser.add_argument("--max-n", type=int, default=10)
    parser.add_argument("--census-stride", type=int, default=1)
    parser.add_argument("--random", type=int, default=120)
    parser.add_argument("--seed", type=int, default=119)
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
