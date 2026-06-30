"""Probe Schur/effective-conductance structure for the current Hardy matrix.

This uses the *current* beta-Hardy matrix

    H = diag(N-T) + Lstar

from _hardy_gate.py, not the older _gcd.a_bar matrix.  For O={v:T(v)>N}
and Q=V\\O, PSD of H should be equivalent to PSD of the Schur complement
onto O once H_QQ is positive definite.  The goal is to identify a simpler
certificate: Stieltjes/Z-matrix structure, row sums, diagonal dominance, or
small overload-set patterns.
"""
import subprocess
import random
from fractions import Fraction as F

from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _hardy_gate import build_H, BETA, maxcut_ls
from _csmspec import is_psd
from _wf_deficit_farkas import odd_blowup
from _bdef_construct import Cn, mycielski, is_triangle_free, union_disjoint, add_edges
from _Klocal_gate import glued_c5_chain


def eliminate_to_schur(H, O):
    n = len(H)
    Oset = set(O)
    Q = [v for v in range(n) if v not in Oset]
    M = [row[:] for row in H]
    min_q_pivot = None
    for q in Q:
        d = M[q][q]
        if min_q_pivot is None or d < min_q_pivot:
            min_q_pivot = d
        if d <= 0:
            return None, min_q_pivot, False
        for i in range(n):
            if i == q or M[i][q] == 0:
                continue
            fac = M[i][q] / d
            for j in range(n):
                M[i][j] -= fac * M[q][j]
    S = [[M[o1][o2] for o2 in O] for o1 in O]
    return S, min_q_pivot, True


def z_and_dd_stats(S):
    m = len(S)
    if m == 0:
        return dict(z=True, rowsum_min=None, dd=True, dd_min=None, psd=True, minpiv=None)
    z = all(S[i][j] <= 0 for i in range(m) for j in range(m) if i != j)
    rows = [sum(S[i][j] for j in range(m)) for i in range(m)]
    rowmin = min(rows)
    dd_gaps = [S[i][i] - sum(abs(S[i][j]) for j in range(m) if j != i) for i in range(m)]
    ddmin = min(dd_gaps)
    psd, minpiv = is_psd(S)
    return dict(z=z, rowsum_min=rowmin, dd=all(g >= 0 for g in dd_gaps), dd_min=ddmin, psd=psd, minpiv=minpiv)


def scan_cut(name, n, adj, side, acc):
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    M, ell, T, cyc = st[0], st[1], st[2], st[4]
    if not M:
        return
    O = [v for v in range(n) if T[v] > n]
    if not O:
        acc["noO"] += 1
        return
    H = build_H(n, M, ell, T, cyc, BETA)
    S, qmin, qpd = eliminate_to_schur(H, O)
    acc["cuts"] += 1
    acc["O_hist"][len(O)] = acc["O_hist"].get(len(O), 0) + 1
    if not qpd:
        acc["q_fail"] += 1
        if acc["q_ex"] is None:
            acc["q_ex"] = (name, n, "".join(map(str, side)), O, str(qmin))
        return
    d = z_and_dd_stats(S)
    for key in ["z", "dd", "psd"]:
        if not d[key]:
            acc[key + "_fail"] += 1
            if acc[key + "_ex"] is None:
                acc[key + "_ex"] = (name, n, "".join(map(str, side)), O, str(d))
    if d["rowsum_min"] is not None and d["rowsum_min"] < 0:
        acc["row_fail"] += 1
        if acc["row_ex"] is None:
            acc["row_ex"] = (name, n, "".join(map(str, side)), O, str(d["rowsum_min"]), str(d))
    for key in ["rowsum_min", "dd_min", "minpiv"]:
        val = d[key]
        if val is not None and (acc[key] is None or val < acc[key][0]):
            acc[key] = (val, name, n, O, str(d))


def gfam(name, n, E, acc):
    adj = [set() for _ in range(n)]
    for a, b in E:
        adj[a].add(b)
        adj[b].add(a)
    try:
        _, cuts = gmins(n, E)
    except Exception:
        return
    for side in cuts:
        scan_cut(name, n, adj, side, acc)


def main():
    acc = dict(
        cuts=0, noO=0, O_hist={},
        q_fail=0, q_ex=None,
        z_fail=0, z_ex=None,
        dd_fail=0, dd_ex=None,
        psd_fail=0, psd_ex=None,
        row_fail=0, row_ex=None,
        rowsum_min=None, dd_min=None, minpiv=None,
    )

    for nn in range(5, 11):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6)
            gfam(f"cen{nn}", n, E, acc)
        print(
            f"census N={nn}: O-cuts={acc['cuts']} q_fail={acc['q_fail']} "
            f"row_fail={acc['row_fail']} dd_fail={acc['dd_fail']} psd_fail={acc['psd_fail']}",
            flush=True,
        )

    grN, grE = mycielski(5, Cn(5))
    gfam("Grotzsch", grN, grE, acc)
    n, E = mycielski(grN, grE)
    adj = [set() for _ in range(n)]
    for a, b in E:
        adj[a].add(b)
        adj[b].add(a)
    side = maxcut_ls(n, adj)
    scan_cut("MycGrotzsch_N23", n, adj, side, acc)

    for q in range(2, 16):
        n, E, side = glued_c5_chain(q)
        adj = [set() for _ in range(n)]
        for a, b in E:
            adj[a].add(b)
            adj[b].add(a)
        scan_cut(f"chain{q}", n, adj, side, acc)

    for sizes in [
        (2, 1, 2, 1, 2), (2, 1, 2, 1, 3), (3, 2, 3, 2, 3),
        (4, 3, 4, 3, 4), (5, 4, 5, 4, 5),
        (2, 2, 2, 2, 2), (3, 3, 3, 3, 3),
    ]:
        n, E = odd_blowup(5, list(sizes))
        if n <= 27:
            gfam(f"blow{sizes}", n, E, acc)

    isl = (5, Cn(5))
    g15 = mycielski(7, Cn(7))
    n, E = union_disjoint(isl, g15)
    n, E = add_edges((n, E), [(0, 5)])
    gfam("island", n, E, acc)

    rng = random.Random(31)
    made = 0
    tries = 0
    while made < 120 and tries < 40000:
        tries += 1
        nn = rng.choice([11, 12])
        p = rng.uniform(0.14, 0.34)
        E = [(a, b) for a in range(nn) for b in range(a + 1, nn) if rng.random() < p]
        if not E or not is_triangle_free(nn, E):
            continue
        adj = [set() for _ in range(nn)]
        for a, b in E:
            adj[a].add(b)
            adj[b].add(a)
        if any(len(adj[v]) == 0 for v in range(nn)):
            continue
        made += 1
        gfam(f"rand{made}", nn, E, acc)

    print("=" * 70)
    print("O-cuts:", acc["cuts"], "noO:", acc["noO"], "random graphs:", made)
    print("O-size histogram:", dict(sorted(acc["O_hist"].items())))
    print("Q PD failures:", acc["q_fail"], acc["q_ex"] or "")
    print("Schur Z failures:", acc["z_fail"], acc["z_ex"] or "")
    print("Schur rowsum<0 failures:", acc["row_fail"], acc["row_ex"] or "")
    print("Schur diag-dominance failures:", acc["dd_fail"], acc["dd_ex"] or "")
    print("Schur PSD failures:", acc["psd_fail"], acc["psd_ex"] or "")
    print("min rowsum:", acc["rowsum_min"])
    print("min dd gap:", acc["dd_min"])
    print("min PSD pivot:", acc["minpiv"])


if __name__ == "__main__":
    main()
