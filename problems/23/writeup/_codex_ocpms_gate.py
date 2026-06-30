"""Gate the proposed OC-PMS dichotomy.

For every gamma-min connected-B maximum cut and every shortest-cycle row
P in cyc[f], test:

  If R(P)=sum_{v in P} T(v) > ell(f)*N, then the row must be in the
  claimed pentagonal overload case:
      ell(f)=5, the positive K-component of P is all vertices, and all
      bad edges in that component have length 5.

In that pentagonal-global case, also test the graph-level B5/PMS inequality:
      75*(I(P)-N) <= 2*(N^2 - 25*|M|)
where I(P)=sum_g E_Q |P cap Q|.  This is equivalent to
      15*Over(P) <= 2*(N^2 - 25|M|)
with Over(P)=5*(I(P)-N).

The script is deliberately narrow: it gates the exact statement proposed in
the current OC-PMS message, not the stronger abstract 5-layer PMS model.
"""
import subprocess
import random
from collections import deque
from fractions import Fraction as F

from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _wf_deficit_farkas import odd_blowup
from _bdef_construct import Cn, mycielski, is_triangle_free, union_disjoint, add_edges
from _Klocal_gate import glued_c5_chain


def kcomp(n, M, cyc, seed):
    adj = [set() for _ in range(n)]
    for g in M:
        for Q in cyc[g]:
            Qs = set(Q)
            for a in Qs:
                adj[a].update(b for b in Qs if b != a)
    seen = set(seed)
    dq = deque(seed)
    while dq:
        u = dq.popleft()
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                dq.append(v)
    return seen


def scan_cut(name, n, adj, side, acc):
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    M, ell, T, cyc = st[0], st[1], st[2], st[4]
    if not M:
        return
    N = F(n)
    for f in M:
        L = ell[f]
        for P in cyc[f]:
            R = sum(T[v] for v in P)
            acc["rows"] += 1
            if R <= L * N:
                continue
            acc["over_rows"] += 1
            C = kcomp(n, M, cyc, set(P))
            comp_edges = [
                g for g in M
                if any(set(Q) <= C for Q in cyc[g])
            ]
            pentagonal = (
                L == 5
                and len(C) == n
                and comp_edges
                and all(ell[g] == 5 for g in comp_edges)
            )
            if not pentagonal:
                acc["collapse_fail"] += 1
                if acc["collapse_ex"] is None:
                    acc["collapse_ex"] = (
                        name, n, tuple(P), f, L, str(R), str(L * N),
                        len(C), sorted(set(ell[g] for g in comp_edges)),
                    )
                continue

            Pset = set(P)
            I = sum(
                F(1, len(cyc[g])) * sum(len(Pset & set(Q)) for Q in cyc[g])
                for g in M
            )
            Def = N * N - 25 * len(M)
            margin = F(2) * Def - 75 * (I - N)
            acc["pms_rows"] += 1
            if margin < 0:
                acc["pms_fail"] += 1
                if acc["pms_ex"] is None:
                    acc["pms_ex"] = (name, n, tuple(P), str(I), str(Def), str(margin))
            elif acc["pms_min"] is None or margin < acc["pms_min"]:
                acc["pms_min"] = margin
                acc["pms_min_ex"] = (name, n, tuple(P), str(I), str(Def), str(margin))


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


def maxcut_ls(n, adj, seeds=80):
    best = None
    best_val = -1
    rng = random.Random(13)
    for _ in range(seeds):
        side = [rng.randint(0, 1) for _ in range(n)]
        improving = True
        while improving:
            improving = False
            for v in range(n):
                same = sum(1 for w in adj[v] if side[w] == side[v])
                opp = sum(1 for w in adj[v] if side[w] != side[v])
                if same > opp:
                    side[v] ^= 1
                    improving = True
        val = sum(1 for v in range(n) for w in adj[v] if w > v and side[v] != side[w])
        if val > best_val:
            best_val = val
            best = side[:]
    return best


def main():
    acc = dict(
        rows=0,
        over_rows=0,
        collapse_fail=0,
        collapse_ex=None,
        pms_rows=0,
        pms_fail=0,
        pms_ex=None,
        pms_min=None,
        pms_min_ex=None,
    )

    for nn in range(5, 11):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6)
            gfam(f"cen{nn}", n, E, acc)
        print(
            f"census N={nn}: rows={acc['rows']} over={acc['over_rows']} "
            f"collapse_fail={acc['collapse_fail']} pms_fail={acc['pms_fail']}",
            flush=True,
        )

    grN, grE = mycielski(5, Cn(5))
    gfam("Grotzsch", grN, grE, acc)
    m2N, m2E = mycielski(grN, grE)
    adj = [set() for _ in range(m2N)]
    for a, b in m2E:
        adj[a].add(b)
        adj[b].add(a)
    side = maxcut_ls(m2N, adj)
    scan_cut("MycGrotzsch_N23", m2N, adj, side, acc)

    for q in range(2, 16):
        n, E, side = glued_c5_chain(q)
        adj = [set() for _ in range(n)]
        for a, b in E:
            adj[a].add(b)
            adj[b].add(a)
        scan_cut(f"chain_q{q}", n, adj, side, acc)

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
    gfam("isl_C5_MycC7", n, E, acc)

    rng = random.Random(17)
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
    print("rows:", acc["rows"], "overload rows:", acc["over_rows"], "random N11/12:", made)
    print("OC collapse failures:", acc["collapse_fail"], acc["collapse_ex"] or "")
    print("PMS rows:", acc["pms_rows"], "PMS failures:", acc["pms_fail"], acc["pms_ex"] or "")
    print("PMS min margin:", str(acc["pms_min"]), acc["pms_min_ex"] or "")
    print(
        "VERDICT:",
        "OC-PMS survives this exact battery"
        if acc["collapse_fail"] == 0 and acc["pms_fail"] == 0
        else "OC-PMS fails on this battery",
    )


if __name__ == "__main__":
    main()
