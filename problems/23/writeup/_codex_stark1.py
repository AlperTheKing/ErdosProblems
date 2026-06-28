"""Exact tests for the pure-K one-hop |O|=1 star bound.

For A = N I - K = L_K + diag(N-T), the singleton-O Schur condition is
an effective conductance lower bound in the K-network.  A direct Rayleigh
lower bound keeps only the one-edge paths

    o --K_oq-- q --(N-T(q))-- ground.

Candidate STAR-K1:

    sum_{q in Q, K[o,q]>0, T(q)<N}
        K[o,q] (N-T(q)) / (K[o,q] + N-T(q))
    >= T(o)-N

This is the pure-K analogue of the now-false omega STAR-O1.
"""
from fractions import Fraction as F
import subprocess

from _h import dec, GENG
from _angleD_O1 import gmin_sides
from _test_fullg import build_K
from _bdef_construct import Cn, union_disjoint, mycielski, is_triangle_free
from _superphi import blow


def stark1(adj, side, n):
    r = build_K(adj, side, n)
    if r is None:
        return None
    K, T = r
    O = [v for v in range(n) if T[v] > n]
    if len(O) != 1:
        return None
    o = O[0]
    D = T[o] - n
    lb = F(0)
    Atot = F(0)
    Rtot = F(0)
    terms = []
    for q in range(n):
        if q == o:
            continue
        R = F(n) - T[q]
        a = K[o][q]
        if a > 0 and R > 0:
            t = a * R / (a + R)
            lb += t
            Atot += a
            Rtot += R
            terms.append((q, a, R, t))
    k0 = Atot * Rtot / (Atot + Rtot) if Atot + Rtot > 0 else F(0)
    return lb >= D, (lb / D if D > 0 else None), D, lb, o, terms, k0


def run_graph(name, n, E, report=True, acc=None, given_sides=None):
    if given_sides is None:
        adj, sides = gmin_sides(n, E)
    else:
        adj = [set() for _ in range(n)]
        for x, y in E:
            adj[x].add(y)
            adj[y].add(x)
        sides = given_sides
    total = fails = 0
    k0fails = 0
    minr = None
    mink0r = None
    first = None
    firstk0 = None
    for side in sides:
        d = stark1(adj, side, n)
        if d is None:
            continue
        ok, ratio, D, lb, o, terms, k0 = d
        total += 1
        k0ok = k0 >= D
        if not ok:
            fails += 1
            if first is None:
                first = (name, "".join(map(str, side)), o, D, lb, k0, terms[:12])
        if not k0ok:
            k0fails += 1
            if firstk0 is None:
                firstk0 = (name, "".join(map(str, side)), o, D, lb, k0, terms[:12])
        if ratio is not None and (minr is None or ratio < minr):
            minr = ratio
        if D > 0:
            k0r = k0 / D
            if mink0r is None or k0r < mink0r:
                mink0r = k0r
    if acc is not None:
        acc["total"] += total
        acc["fails"] += fails
        acc["k0fails"] += k0fails
        if first is not None and acc["first"] is None:
            acc["first"] = first
        if firstk0 is not None and acc["firstk0"] is None:
            acc["firstk0"] = firstk0
        if minr is not None and (acc["minr"] is None or minr < acc["minr"]):
            acc["minr"] = minr
            acc["minwit"] = name
        if mink0r is not None and (acc["mink0r"] is None or mink0r < acc["mink0r"]):
            acc["mink0r"] = mink0r
            acc["mink0wit"] = name
    if report:
        print(
            f"{name} N={n}: |O|=1 cuts={total} fails={fails} minratio={float(minr) if minr else None} "
            f"K0fails={k0fails} K0minratio={float(mink0r) if mink0r else None}",
            flush=True,
        )
        if first:
            print(" FIRST", first[:5], flush=True)
        if firstk0:
            print(" FIRST-K0", firstk0[:6], flush=True)
    return total, fails, minr, first


def nonuniform_c5():
    sizes = [1, 48, 6, 8, 48]
    start = [0]
    for s in sizes[:-1]:
        start.append(start[-1] + s)
    E = []
    for i, j in [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)]:
        for a in range(start[i], start[i] + sizes[i]):
            for b in range(start[j], start[j] + sizes[j]):
                E.append((min(a, b), max(a, b)))
    side = []
    for i, s in enumerate(sizes):
        bit = 0 if i in (0, 2, 4) else 1
        side.extend([bit] * s)
    return sum(sizes), E, side


def lifted_side_for_blowup(g6, t):
    n, E = dec(g6)
    adj, sides = gmin_sides(n, E)
    if not sides:
        return None
    base = sides[0]
    side = []
    for b in base:
        side.extend([b] * t)
    return side


if __name__ == "__main__":
    print("=== STAR-K1 pure-K one-hop bound for |O|=1 ===", flush=True)
    cur = (5, Cn(5))
    for name in ["Grotzsch=N11", "Myc2(C5)=N23"]:
        cur = mycielski(*cur)
        run_graph(name, cur[0], cur[1])
    cur = mycielski(7, Cn(7))
    run_graph("Myc(C7)=N15", cur[0], cur[1])
    n, E, side = nonuniform_c5()
    run_graph("nonuniform-C5(1,48,6,8,48)", n, E, given_sides=[side])
    for g6, t in [("J???E?pNu\\?", 2), ("I?BD@g]Qo", 2), ("G?bF`w", 3)]:
        nn, EE = blow(g6, t)
        side = lifted_side_for_blowup(g6, t)
        run_graph(f"{g6}[{t}]", nn, EE, given_sides=[side] if side else None)

    print("--- census N=7..10 ---", flush=True)
    for nn in range(7, 11):
        acc = {
            "total": 0,
            "fails": 0,
            "k0fails": 0,
            "first": None,
            "firstk0": None,
            "minr": None,
            "minwit": None,
            "mink0r": None,
            "mink0wit": None,
        }
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6)
            run_graph(g6, n, E, report=False, acc=acc)
            if acc["first"] is not None or acc["firstk0"] is not None:
                break
        print(
            f"N={nn}: |O|=1 cuts={acc['total']} fails={acc['fails']} "
            f"minratio={float(acc['minr']) if acc['minr'] else None} minwit={acc['minwit']} "
            f"K0fails={acc['k0fails']} K0minratio={float(acc['mink0r']) if acc['mink0r'] else None} K0minwit={acc['mink0wit']}",
            flush=True,
        )
        if acc["first"] is not None:
            print(" FIRST", acc["first"][:5], flush=True)
            break
        if acc["firstk0"] is not None:
            print(" FIRST-K0", acc["firstk0"][:6], flush=True)
            break
