"""AUDIT of G8: (a) explicit homomorphisms And(k) -> And(k+1) (monotonicity claim,
independent of the quoted Bondy-Hell theorem);
(b) the section 6.3 blocking test EXTENDED to k = 6, 7 (the report verified only 4, 5
but states the conclusion for all k >= 4);
(c) the atom count of section 6.2 ("all 3496 atoms").
"""
import sys, itertools
from fractions import Fraction
from audit_G8_core import and_circulant, edges_of
from audit_G8_hom import hom_to_C5


def hom_search(nA, adjA, nB, adjB):
    """backtracking hom from graph A to graph B; returns the map or None."""
    order = sorted(range(nA), key=lambda v: -bin(adjA[v]).count("1"))
    pos = {v: i for i, v in enumerate(order)}
    assign = {}

    def rec(i):
        if i == nA:
            return True
        v = order[i]
        for c in range(nB):
            ok = True
            for u in range(nA):
                if (adjA[v] >> u) & 1 and u in assign:
                    if not ((adjB[c] >> assign[u]) & 1):
                        ok = False
                        break
            if ok:
                assign[v] = c
                if rec(i + 1):
                    return True
                del assign[v]
        return False

    return dict(assign) if rec(0) else None


def induced_C5s(n, adjm):
    out = []
    for S in itertools.combinations(range(n), 5):
        Ss = set(S)
        sub = [(u, v) for u in S for v in S if u < v and (adjm[u] >> v) & 1]
        if len(sub) != 5:
            continue
        deg = {v: 0 for v in S}
        for (u, v) in sub:
            deg[u] += 1
            deg[v] += 1
        if all(d == 2 for d in deg.values()):
            out.append(sub)
    return out


def intersection_empty(k):
    n, adjm = and_circulant(k)
    C5s = induced_C5s(n, adjm)
    survivors = []
    for mask in range(1 << (n - 1)):
        side = [0] * n
        m = mask
        for v in range(1, n):
            side[v] = (m >> (v - 1)) & 1
        ok = True
        for sub in C5s:
            cnt = 0
            for (u, v) in sub:
                if side[u] == side[v]:
                    cnt += 1
                    if cnt > 1:
                        break
            if cnt != 1:
                ok = False
                break
        if ok:
            survivors.append(mask)
    return len(C5s), survivors, n


def atom_count(k, max_mono=None):
    """number of atoms (S,A,B): S a cut, mono(S) bipartite with parts inside A,B."""
    n, adjm = and_circulant(k)
    E = edges_of(n, adjm)
    tot = 0
    for mask in range(1 << (n - 1)):
        side = [0] + [(mask >> (v - 1)) & 1 for v in range(1, n)]
        mono = [(u, v) for (u, v) in E if side[u] == side[v]]
        if not mono:
            continue
        if max_mono is not None and len(mono) > max_mono:
            continue
        adjmono = {}
        verts = set()
        for (u, v) in mono:
            adjmono.setdefault(u, []).append(v)
            adjmono.setdefault(v, []).append(u)
            verts.add(u); verts.add(v)
        colour = {}
        comps = 0
        ok = True
        for s in sorted(verts):
            if s in colour:
                continue
            comps += 1
            colour[s] = 0
            st = [s]
            while st:
                a = st.pop()
                for b in adjmono[a]:
                    if b not in colour:
                        colour[b] = 1 - colour[a]
                        st.append(b)
                    elif colour[b] == colour[a]:
                        ok = False
        if not ok:
            continue
        free = n - len(verts)
        tot += (2 ** comps) * (3 ** free)
    return tot


if __name__ == "__main__":
    print("(a) explicit homomorphisms And(k) -> And(k+1):")
    for k in range(2, 8):
        nA, adjA = and_circulant(k)
        nB, adjB = and_circulant(k + 1)
        f = hom_search(nA, adjA, nB, adjB)
        ok = f is not None
        if ok:
            ok = all(((adjB[f[u]] >> f[v]) & 1)
                     for u in range(nA) for v in range(nA)
                     if u < v and (adjA[u] >> v) & 1)
        print(f"   And({k}) -> And({k+1}) : {ok}   map={[f[v] for v in range(nA)] if f else None}")
        # and the reverse should FAIL
        g = hom_search(nB, adjB, nA, adjA)
        print(f"   And({k+1}) -> And({k}) : {g is not None}  (must be False for strictness)")
    print()

    print("(b) section 6.3 blocking test, extended:")
    for k in (3, 4, 5, 6, 7):
        nc, surv, n = intersection_empty(k)
        print(f"   And({k}) n={n}: {nc} induced C5s; cuts active at ALL of them: {len(surv)}"
              f"   => {'NOT blocked' if surv else 'BLOCKED'}")
        sys.stdout.flush()
    print()

    print("(c) atom counts for And(3):")
    print(f"   atoms with |mono| <= 6 : {atom_count(3, 6)}")
    print(f"   atoms, no restriction  : {atom_count(3, None)}")
