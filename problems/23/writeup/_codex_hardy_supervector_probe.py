"""Probe ground-state/supervector certificates for the Hardy matrix H.

H = diag(N-T) + Lstar is a symmetric Z-matrix.  If there is a strictly
positive vector phi with H phi >= 0 coordinatewise, then the standard
ground-state transform proves H is PSD:

  x^T H x = sum_{uv} c_uv phi_u phi_v (x_u/phi_u-x_v/phi_v)^2
            + sum_v (H phi)_v/phi_v x_v^2.

This script tests simple exact candidate phis on the usual guardrail battery.
It is a proof-search probe, not an acceptance gate.
"""
import subprocess
import random
from fractions import Fraction as F

from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _hardy_gate import build_H, BETA, maxcut_ls
from _wf_deficit_farkas import odd_blowup
from _bdef_construct import Cn, mycielski, is_triangle_free, union_disjoint, add_edges
from _Klocal_gate import glued_c5_chain


def mat_vec(H, phi):
    return [sum(H[i][j] * phi[j] for j in range(len(phi))) for i in range(len(phi))]


def candidates(n, T):
    N = F(n)
    out = {}
    out["one"] = [F(1) for _ in range(n)]
    out["T"] = [t for t in T]
    for c in [F(1, 1000), F(1, 100), F(1, 10), F(1, 2), F(2), F(5)]:
        out[f"T_plus_{c}"] = [t + c for t in T]
    out["N_plus_T"] = [N + t for t in T]
    out["one_plus_T"] = [1 + t for t in T]
    out["N_minus_T_shift"] = [1 + N - t if 1 + N - t > 0 else F(1, 10**6) for t in T]
    out["inv_N_plus_T_scaled"] = [F(1, 1) / (N + t) for t in T]
    out["inv_one_plus_T"] = [F(1, 1) / (1 + t) for t in T]
    # A crude overload-damped candidate: smaller on overloaded vertices.
    out["N_over_N_plus_T"] = [N / (N + t) for t in T]
    return out


def scan_cut(name, n, adj, side, acc):
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    M, ell, T, cyc = st[0], st[1], st[2], st[4]
    if not M:
        return
    H = build_H(n, M, ell, T, cyc, BETA)
    acc["cuts"] += 1
    for cname, phi in candidates(n, T).items():
        y = mat_vec(H, phi)
        mn = min(y)
        if mn < 0:
            acc["fail"][cname] = acc["fail"].get(cname, 0) + 1
            if cname not in acc["ex"]:
                v = min(range(n), key=lambda i: y[i])
                acc["ex"][cname] = (name, n, "".join(map(str, side)), v, str(mn), str(T[v]))
        else:
            acc["pass"][cname] = acc["pass"].get(cname, 0) + 1
        if cname not in acc["min"] or mn < acc["min"][cname][0]:
            v = min(range(n), key=lambda i: y[i])
            acc["min"][cname] = (mn, name, n, v, str(T[v]))


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
    acc = {"cuts": 0, "fail": {}, "pass": {}, "ex": {}, "min": {}}
    for nn in range(5, 11):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6)
            gfam(f"cen{nn}", n, E, acc)
        print("census N=%d cuts=%d" % (nn, acc["cuts"]), flush=True)

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
        if n <= 24:
            gfam(f"blow{sizes}", n, E, acc)

    isl = (5, Cn(5))
    g15 = mycielski(7, Cn(7))
    n, E = union_disjoint(isl, g15)
    n, E = add_edges((n, E), [(0, 5)])
    gfam("island", n, E, acc)

    rng = random.Random(23)
    made = 0
    tries = 0
    while made < 80 and tries < 30000:
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
    print("cuts:", acc["cuts"], "random graphs:", made)
    for cname in sorted(acc["min"]):
        print(
            cname,
            "fail", acc["fail"].get(cname, 0),
            "pass", acc["pass"].get(cname, 0),
            "min", str(acc["min"][cname]),
            "first_ex", acc["ex"].get(cname, ""),
        )


if __name__ == "__main__":
    main()
