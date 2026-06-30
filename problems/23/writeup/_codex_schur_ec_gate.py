"""Gate the Schur effective-shunt domination certificate.

For the Hardy matrix H = diag(N-T)+Lstar and O={T>N}, eliminate U=V\\O to
get the exact Schur complement S on O.  Since S is a Z-matrix, write

    S = L_c + D_r,        r_i = row_sum_i(S), c_ij=-S_ij.

Let R={i:r_i<0}.  Let A=L_c+D_{r+}.  The EC certificate is

    Lambda_R := A_RR - A_RP A_PP^{-1} A_PR  >=  D_{r-}.

When A_PP is nonsingular, this is equivalent to PSD of S, but the statistics
show whether the obstruction is small (e.g. singleton R) and whether EC is a
usable proof target.
"""

import random
import subprocess
from fractions import Fraction as F

from _bdef_construct import Cn, add_edges, is_triangle_free, mycielski, union_disjoint
from _csmspec import is_psd
from _h import Bconn, GENG, dec
from _hardy_gate import BETA, build_H, maxcut_ls
from _Klocal_gate import glued_c5_chain
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _wf_deficit_farkas import odd_blowup


def adj_from_edges(n, edges):
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    return adj


def schur_eliminate(M, keep):
    n = len(M)
    keep = list(keep)
    keep_set = set(keep)
    elim = [i for i in range(n) if i not in keep_set]
    A = [row[:] for row in M]
    min_pivot = None
    for q in elim:
        d = A[q][q]
        if min_pivot is None or d < min_pivot:
            min_pivot = d
        if d <= 0:
            return None, min_pivot
        for i in range(n):
            if i == q or A[i][q] == 0:
                continue
            fac = A[i][q] / d
            for j in range(n):
                A[i][j] -= fac * A[q][j]
    return [[A[i][j] for j in keep] for i in keep], min_pivot


def positive_network_from_schur(S):
    m = len(S)
    rows = [sum(S[i]) for i in range(m)]
    A = [[F(0) for _ in range(m)] for _ in range(m)]
    for i in range(m):
        if rows[i] > 0:
            A[i][i] += rows[i]
    for i in range(m):
        for j in range(i + 1, m):
            c = -S[i][j]
            if c < 0:
                raise ValueError("S is not a Z-matrix")
            if c == 0:
                continue
            A[i][i] += c
            A[j][j] += c
            A[i][j] -= c
            A[j][i] -= c
    return A, rows


def ec_margin(S):
    A, rows = positive_network_from_schur(S)
    R = [i for i, r in enumerate(rows) if r < 0]
    P = [i for i, r in enumerate(rows) if r >= 0]
    if not R:
        return {
            "R": R,
            "rows": rows,
            "ok": True,
            "app_pd": True,
            "minpiv": None,
            "margin_minpiv": None,
            "margin_matrix": [],
        }
    # Schur complement of A onto R, eliminating P.
    Lam, app_min = schur_eliminate(A, R)
    if Lam is None:
        return {"R": R, "rows": rows, "ok": False, "app_pd": False, "minpiv": app_min}
    for a, i in enumerate(R):
        Lam[a][a] += rows[i]  # subtract r^- = add negative row sum.
    ok, minpiv = is_psd(Lam)
    return {
        "R": R,
        "rows": rows,
        "ok": ok,
        "app_pd": True,
        "minpiv": app_min,
        "margin_minpiv": minpiv,
        "margin_matrix": Lam,
    }


def scan_cut(name, n, adj, side, acc):
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    M, ell, T, _mu, cyc = st
    if not M:
        return
    O = [v for v in range(n) if T[v] > n]
    if not O:
        acc["noO"] += 1
        return
    H = build_H(n, M, ell, T, cyc, BETA)
    S, qmin = schur_eliminate(H, O)
    acc["cuts"] += 1
    acc["O_hist"][len(O)] = acc["O_hist"].get(len(O), 0) + 1
    if S is None:
        acc["q_fail"] += 1
        if acc["first"] is None:
            acc["first"] = ("q_fail", name, n, "".join(map(str, side)), O, str(qmin))
        return
    try:
        d = ec_margin(S)
    except ValueError as exc:
        acc["z_fail"] += 1
        if acc["first"] is None:
            acc["first"] = ("z_fail", name, n, "".join(map(str, side)), O, str(exc))
        return
    rsize = len(d["R"])
    acc["R_hist"][rsize] = acc["R_hist"].get(rsize, 0) + 1
    if rsize:
        acc["R_nonempty"] += 1
        if acc["example_R"] is None:
            acc["example_R"] = (name, n, "".join(map(str, side)), O, d["R"], [str(x) for x in d["rows"]])
    if not d["app_pd"]:
        acc["app_fail"] += 1
        if acc["first"] is None:
            acc["first"] = ("app_fail", name, n, "".join(map(str, side)), O, d["R"], str(d["minpiv"]))
        return
    if not d["ok"]:
        acc["ec_fail"] += 1
        if acc["first"] is None:
            acc["first"] = (
                "ec_fail",
                name,
                n,
                "".join(map(str, side)),
                O,
                d["R"],
                str(d["margin_minpiv"]),
            )
    if d["margin_minpiv"] is not None:
        val = d["margin_minpiv"]
        if acc["min_margin"] is None or val < acc["min_margin"][0]:
            acc["min_margin"] = (val, name, n, "".join(map(str, side)), O, d["R"])


def gfam(name, n, edges, acc):
    adj = adj_from_edges(n, edges)
    try:
        _gamma, cuts = gmins(n, edges)
    except Exception:
        return
    for side in cuts:
        scan_cut(name, n, adj, side, acc)


def main():
    acc = {
        "cuts": 0,
        "noO": 0,
        "q_fail": 0,
        "z_fail": 0,
        "app_fail": 0,
        "ec_fail": 0,
        "O_hist": {},
        "R_hist": {},
        "R_nonempty": 0,
        "example_R": None,
        "min_margin": None,
        "first": None,
    }

    for nn in range(5, 11):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, edges = dec(g6)
            gfam(f"cen{nn}", n, edges, acc)
        print(
            f"census N={nn}: O-cuts={acc['cuts']} R_nonempty={acc['R_nonempty']} ec_fail={acc['ec_fail']}",
            flush=True,
        )

    grN, grE = mycielski(5, Cn(5))
    gfam("Grotzsch", grN, grE, acc)

    n, edges = mycielski(grN, grE)
    scan_cut("MycGrotzsch_N23", n, adj_from_edges(n, edges), maxcut_ls(n, adj_from_edges(n, edges)), acc)

    for q in range(2, 16):
        n, edges, side = glued_c5_chain(q)
        scan_cut(f"chain{q}", n, adj_from_edges(n, edges), side, acc)

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
        if n <= 27:
            gfam(f"blow{sizes}", n, edges, acc)

    island = (5, Cn(5))
    g15 = mycielski(7, Cn(7))
    n, edges = union_disjoint(island, g15)
    n, edges = add_edges((n, edges), [(0, 5)])
    gfam("island", n, edges, acc)

    rng = random.Random(41)
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

    print("=" * 70)
    print("O-cuts:", acc["cuts"], "noO:", acc["noO"], "random graphs:", made)
    print("O hist:", dict(sorted(acc["O_hist"].items())))
    print("R hist:", dict(sorted(acc["R_hist"].items())))
    print("R nonempty:", acc["R_nonempty"], "example:", acc["example_R"] or "")
    print("q_fail:", acc["q_fail"], "z_fail:", acc["z_fail"], "app_fail:", acc["app_fail"], "ec_fail:", acc["ec_fail"])
    print("min EC margin pivot:", acc["min_margin"])
    print("first failure:", acc["first"] or "")


if __name__ == "__main__":
    main()
