"""Probe local lower bounds for the Schur harvest inequality.

For a minority overloaded vertex o, put psi=1-h on U.  The harvest crux is

    25 * (sum_u c_ou psi_u - a_o) >= 4 * (cU_o - a_o).

This diagnostic tests whether psi can be replaced by elementary star terms
depending only on the U-vertex deficit d_u=N-T(u) and its conductance back to
O.  It is not an acceptance gate.
"""

import random
import subprocess
from fractions import Fraction as F

from _bdef_construct import Cn, add_edges, is_triangle_free, mycielski, union_disjoint
from _h import Bconn, GENG, dec
from _hardy_gate import BETA, build_H, maxcut_ls
from _Klocal_gate import glued_c5_chain
from _Rsize_gate import solve_mat
from _satzmu_conn import struct_for_side
from _schur_absorption_hall_gate import adj_from_edges, schur_on_O
from _stark1 import gmins
from _wf_deficit_farkas import odd_blowup


def harmonic_psi(H, O, U, T, n):
    Huu = [[H[a][b] for b in U] for a in U]
    rhs = [[F(n) - T[u]] for u in U]
    sol = solve_mat(Huu, rhs)
    if sol is None:
        return None
    return {U[i]: sol[i][0] for i in range(len(U))}


def push_min(items, key, rec, limit=10):
    items.append((key, rec))
    items.sort(key=lambda x: x[0])
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
    psi = harmonic_psi(H, O, U, T, n)
    acc["Ocuts"] += 1
    if S is None or psi is None:
        acc["singular"] += 1
        return

    a = [T[o] - N for o in O]
    A = sum(a)
    rho = [sum(S[i]) for i in range(len(O))]
    side_s = "".join(map(str, side))
    conduct_U = {
        u: {w: -H[u][w] for w in U if w != u and -H[u][w] > 0}
        for u in U
    }
    denom = {}
    deficit = {}
    for u in U:
        deficit[u] = N - T[u]
        cO = sum(-H[u][oo] for oo in O if -H[u][oo] > 0)
        cUU = sum(conduct_U[u].values())
        denom[u] = deficit[u] + cO + cUU
    jacobi = []
    phi = {u: F(0) for u in U}
    for _step in range(6):
        phi = {
            u: (deficit[u] + sum(c * phi[w] for w, c in conduct_U[u].items())) / denom[u]
            if denom[u]
            else F(0)
            for u in U
        }
        jacobi.append(phi)

    for i, o in enumerate(O):
        if a[i] > A - a[i]:
            continue
        neigh = [u for u in U if -H[o][u] > 0]
        if not neigh:
            continue
        cU = sum(-H[o][u] for u in neigh)
        I = sum((-H[o][u]) * psi[u] for u in neigh)
        e = cU - a[i]

        star_O = F(0)
        star_full = F(0)
        for u in neigh:
            c = -H[o][u]
            d = N - T[u]
            cO = sum(-H[u][oo] for oo in O if -H[u][oo] > 0)
            cUU = sum(-H[u][w] for w in U if w != u and -H[u][w] > 0)
            if d + cO > 0:
                star_O += c * d / (d + cO)
            if d + cO + cUU > 0:
                star_full += c * d / (d + cO + cUU)

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
            "I": I,
            "e": e,
            "harvest": 25 * rho[i] - 4 * e,
            "I_minus_star_O": I - star_O,
            "I_minus_star_full": I - star_full,
            "harvest_star_O": 25 * (star_O - a[i]) - 4 * e,
            "harvest_star_full": 25 * (star_full - a[i]) - 4 * e,
        }
        push_min(acc["I_star_O"], I - star_O, rec)
        push_min(acc["I_star_full"], I - star_full, rec)
        push_min(acc["harvest_star_O"], rec["harvest_star_O"], rec)
        push_min(acc["harvest_star_full"], rec["harvest_star_full"], rec)
        for step, phi_step in enumerate(jacobi, start=1):
            I_step = sum((-H[o][u]) * phi_step[u] for u in neigh)
            margin = 25 * (I_step - a[i]) - 4 * e
            if margin < 0:
                acc["jacobi_fail"][step] += 1
            rec_step = dict(rec)
            rec_step["jacobi_step"] = step
            rec_step["jacobi_margin"] = margin
            push_min(acc["jacobi_min"][step], margin, rec_step)
        if I < star_O:
            acc["I_star_O_fail"] += 1
        if 25 * (star_O - a[i]) < 4 * e:
            acc["harvest_star_O_fail"] += 1


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
        "harvest": float(rec["harvest"]),
        "I_minus_star_O": float(rec["I_minus_star_O"]),
        "I_minus_star_full": float(rec["I_minus_star_full"]),
        "harvest_star_O": float(rec["harvest_star_O"]),
        "harvest_star_full": float(rec["harvest_star_full"]),
    }


def main():
    acc = {
        "Ocuts": 0,
        "singular": 0,
        "I_star_O": [],
        "I_star_full": [],
        "harvest_star_O": [],
        "harvest_star_full": [],
        "jacobi_fail": {step: 0 for step in range(1, 7)},
        "jacobi_min": {step: [] for step in range(1, 7)},
        "I_star_O_fail": 0,
        "harvest_star_O_fail": 0,
    }

    for nn in range(5, 11):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, edges = dec(g6)
            gfam(f"cen{nn}", n, edges, acc)
        print(f"census N={nn}: Ocuts={acc['Ocuts']}", flush=True)

    grN, grE = mycielski(5, Cn(5))
    gfam("Grotzsch", grN, grE, acc)
    m2N, m2E = mycielski(grN, grE)
    test_cut("MycGrotzsch_N23", m2N, adj_from_edges(m2N, m2E), maxcut_ls(m2N, adj_from_edges(m2N, m2E)), acc)

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
        edges = [(a, b) for a in range(nn) for b in range(a + 1, nn) if rng.random() < p]
        if not edges or not is_triangle_free(nn, edges):
            continue
        adj = adj_from_edges(nn, edges)
        if any(len(adj[v]) == 0 for v in range(nn)):
            continue
        made += 1
        gfam(f"rand{made}", nn, edges, acc)

    print("=" * 72)
    print("Ocuts", acc["Ocuts"], "singular", acc["singular"], "random", made)
    print("I_star_O_fail", acc["I_star_O_fail"], "harvest_star_O_fail", acc["harvest_star_O_fail"])
    print("jacobi_fail", acc["jacobi_fail"])
    for step in range(1, 7):
        print("jacobi_min", step)
        for val, rec in acc["jacobi_min"][step][:3]:
            print(float(val), fmt_rec(rec))
    for key in ["I_star_O", "I_star_full", "harvest_star_O", "harvest_star_full"]:
        print(key)
        for val, rec in acc[key][:5]:
            print(float(val), fmt_rec(rec))


if __name__ == "__main__":
    main()
