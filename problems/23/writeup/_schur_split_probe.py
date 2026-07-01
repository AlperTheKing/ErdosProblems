"""Diagnostics for the Schur minority-current split.

For each minority overloaded vertex o, write

    a = T(o) - N
    A = sum_{p in O} (T(p)-N)
    rho = row sum of the Schur complement S at o
    cU = sum_{u in U} -H[o,u]
    e = cU - a
    g = A - 2*a

The pointwise target is 25*rho >= g.  Current probes suggest:

    25*rho >= 4*e

globally, which proves the target when g <= 4e.  This script records the
largest ratios g/e and the weakest harvest margins 25*rho-4e.
"""

import random
import subprocess
from fractions import Fraction as F

from _bdef_construct import Cn, add_edges, is_triangle_free, mycielski, union_disjoint
from _h import Bconn, GENG, dec
from _hardy_gate import BETA, build_H, maxcut_ls
from _Klocal_gate import glued_c5_chain
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _wf_deficit_farkas import odd_blowup
from _schur_absorption_hall_gate import adj_from_edges, schur_on_O


def push_top(items, rec, key, limit=20, reverse=True):
    items.append((key, rec))
    items.sort(key=lambda x: x[0], reverse=reverse)
    del items[limit:]


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
        return
    U = [v for v in range(n) if T[v] <= N]
    H = build_H(n, M, ell, T, cyc, BETA)
    S = schur_on_O(H, O, U)
    acc["Ocuts"] += 1
    if S is None:
        acc["singular"] += 1
        return

    a = [T[o] - N for o in O]
    A = sum(a)
    rho = [sum(S[i]) for i in range(len(O))]
    side_s = "".join(map(str, side))

    for i, o in enumerate(O):
        if a[i] > A - a[i]:
            acc["majority"] += 1
            continue
        acc["minority"] += 1
        cU = sum(-H[o][u] for u in U)
        e = cU - a[i]
        g = A - 2 * a[i]
        target = 25 * rho[i] - g
        harvest = 25 * rho[i] - 4 * e
        static = 5 * e - g
        rec = {
            "name": name,
            "n": n,
            "side": side_s,
            "o": o,
            "O": tuple(O),
            "a": a[i],
            "A": A,
            "rho": rho[i],
            "cU": cU,
            "e": e,
            "g": g,
            "target": target,
            "harvest": harvest,
            "static": static,
            "Hdiag": H[o][o],
            "Sdiag": S[i][i],
            "cO": sum(-S[i][j] for j in range(len(O)) if j != i),
        }
        if e > 0:
            push_top(acc["top_ratio"], rec, g / e, reverse=True)
        push_top(acc["weak_harvest"], rec, harvest, reverse=False)
        push_top(acc["weak_target"], rec, target, reverse=False)
        if g > 4 * e:
            acc["high_ratio"].append(rec)
        if harvest < 0:
            acc["harvest_fail"].append(rec)
        if target < 0:
            acc["target_fail"].append(rec)


def gfam(name, n, edges, acc):
    adj = adj_from_edges(n, edges)
    try:
        _gamma, cuts = gmins(n, edges)
    except Exception:
        return
    for side in cuts:
        test_cut(name, n, adj, side, acc)


def fmt_rec(rec):
    return {
        "name": rec["name"],
        "n": rec["n"],
        "side": rec["side"],
        "o": rec["o"],
        "O": rec["O"],
        "a": float(rec["a"]),
        "A": float(rec["A"]),
        "rho": float(rec["rho"]),
        "cU": float(rec["cU"]),
        "e": float(rec["e"]),
        "g": float(rec["g"]),
        "g_over_e": float(rec["g"] / rec["e"]) if rec["e"] else None,
        "target": float(rec["target"]),
        "harvest": float(rec["harvest"]),
        "static": float(rec["static"]),
        "Hdiag": float(rec["Hdiag"]),
        "Sdiag": float(rec["Sdiag"]),
        "cO": float(rec["cO"]),
    }


def main():
    acc = {
        "Ocuts": 0,
        "singular": 0,
        "minority": 0,
        "majority": 0,
        "top_ratio": [],
        "weak_harvest": [],
        "weak_target": [],
        "high_ratio": [],
        "harvest_fail": [],
        "target_fail": [],
    }

    for nn in range(5, 11):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, edges = dec(g6)
            gfam(f"cen{nn}", n, edges, acc)
        print(f"census N={nn}: Ocuts={acc['Ocuts']} minority={acc['minority']}", flush=True)

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

    rng = random.Random(917)
    made = 0
    tries = 0
    while made < 120 and tries < 40000:
        tries += 1
        nn = rng.choice([11, 12])
        p = rng.uniform(0.14, 0.34)
        edges = [(a0, b0) for a0 in range(nn) for b0 in range(a0 + 1, nn) if rng.random() < p]
        if not edges or not is_triangle_free(nn, edges):
            continue
        adj = adj_from_edges(nn, edges)
        if any(len(adj[v]) == 0 for v in range(nn)):
            continue
        made += 1
        gfam(f"rand{made}", nn, edges, acc)

    print("=" * 72)
    print("Ocuts", acc["Ocuts"], "singular", acc["singular"], "random", made)
    print("minority", acc["minority"], "majority", acc["majority"])
    print("harvest_fail", len(acc["harvest_fail"]), "target_fail", len(acc["target_fail"]))
    print("high_ratio_count", len(acc["high_ratio"]))
    for rec in acc["high_ratio"]:
        print("HIGH_RATIO", fmt_rec(rec), "g/e", float(rec["g"] / rec["e"]))
    print("TOP_RATIO")
    for ratio, rec in acc["top_ratio"][:10]:
        print(float(ratio), fmt_rec(rec))
    print("WEAK_HARVEST")
    for val, rec in acc["weak_harvest"][:10]:
        print(float(val), fmt_rec(rec))
    print("WEAK_TARGET")
    for val, rec in acc["weak_target"][:10]:
        print(float(val), fmt_rec(rec))


if __name__ == "__main__":
    main()
