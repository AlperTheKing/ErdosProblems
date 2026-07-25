"""Q5: make the And(4) blocking self-contained.

Q5_k5minor.exe found an explicit ODD-K5 minor in And(4) = Gamma_11:
   B1={0,4,8} B2={1,5,9} B3={2,6,10} B4={3} B5={7},  p-mask 112 (vertices 4,5,6)
By idealness-under-minors this forces a weight w >= 0 with tau*_w < tau_w.
Here we EXHIBIT one exactly, so the blocking does not rest on any citation.

Also: verify that And(4) sits as an INDUCED subgraph of And(k) for k = 5,6,7, so
the obstruction propagates to the whole tail of the Andrasfai family.
"""
import sys, os, random, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fractions import Fraction
from Q5_lib import *
from Q5_theory import andrasfai


def structured():
    print("=== structured weight from the odd-K5 minor of And(4) ===")
    N, adj = andrasfai(4)
    E = edges_of(N, adj)
    B = [{0, 4, 8}, {1, 5, 9}, {2, 6, 10}, {3}, {7}]
    lab = {}
    for i, b in enumerate(B):
        for v in b:
            lab[v] = i
    for zero_internal in (True, False):
        w = {}
        for (u, v) in E:
            same = lab[u] == lab[v]
            w[(u, v)] = (Fraction(0) if zero_internal else Fraction(3)) if same else Fraction(1)
        tau, _ = bip_exact(N, adj, weights=w)
        ts = tau_star(N, adj, w=w)["value"]
        print(f"  internal={'0' if zero_internal else '3'} crossing=1 :"
              f" tau={tau} tau*={ts} gap={tau-ts}")
        if ts < tau:
            print(f"    *** EXACT GAP WITNESS on And(4): w = "
                  f"{ {str(k): str(v) for k, v in w.items()} }")
            return w, ts, tau
    return None


def randomsearch(trials=4000, seed=99):
    print("=== random 0/1 weight search on And(4) ===")
    rnd = random.Random(seed)
    N, adj = andrasfai(4)
    E = edges_of(N, adj)
    for t in range(trials):
        w = {e: Fraction(1 if rnd.random() < 0.6 else 0) for e in E}
        tau, _ = bip_exact(N, adj, weights=w)
        ts = tau_star(N, adj, w=w)["value"]
        if ts < tau:
            supp = sorted(e for e in E if w[e] == 1)
            print(f"  *** EXACT GAP at trial {t}: tau={tau} tau*={ts} gap={tau-ts}")
            print(f"      w = 1 on {supp}")
            print(f"      w = 0 on {[e for e in E if w[e]==0]}")
            return w, ts, tau
    print(f"  no gap in {trials} random 0/1 weightings")
    return None


def induced_iso(nS, aS, nB, aB):
    """Is (nS,aS) an induced subgraph of (nB,aB)?  Backtracking with degree pruning."""
    degS = [len(a) for a in aS]
    degB = [len(a) for a in aB]
    order = sorted(range(nS), key=lambda v: -degS[v])
    mapping = {}
    used = set()

    def bt(i):
        if i == nS:
            return True
        u = order[i]
        for x in range(nB):
            if x in used or degB[x] < degS[u]:
                continue
            ok = True
            for j in range(i):
                v = order[j]
                y = mapping[v]
                if (v in aS[u]) != (y in aB[x]):
                    ok = False
                    break
            if ok:
                mapping[u] = x
                used.add(x)
                if bt(i + 1):
                    return True
                used.discard(x)
                del mapping[u]
        return False

    return (mapping.copy() if bt(0) else None)


def chain():
    print("=== And(4) as an INDUCED subgraph of And(k) ===")
    n4, a4 = andrasfai(4)
    for k in (5, 6, 7, 8):
        nk, ak = andrasfai(k)
        m = induced_iso(n4, a4, nk, ak)
        print(f"  And(4) induced in And({k}) (N={nk}) : {m is not None}"
              f"   image={sorted(m.values()) if m else None}")


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if which in ("all", "chain"):
        chain()
    if which in ("all", "struct"):
        structured()
    if which in ("all", "rand"):
        randomsearch()
