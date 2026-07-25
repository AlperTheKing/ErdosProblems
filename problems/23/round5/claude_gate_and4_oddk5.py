"""ROOT-AGENT GATE (Claude): does And(4) = Gamma_11 really carry an ODD-K5 minor?

R3-C19 recorded a genuine tension: round 7 claimed an odd-K5 minor in And(4) with branch sets
{0,4,8},{1,5,9},{2,6,10},{3},{7} (which by Guenin's theorem forces some weight w >= 0 with
tau_w > tau*_w), while my own searches -- 4000 random integer weights, 1500 product weights,
3000 random objectives -- found no integrality gap at all, and four exact packings certified
equality.  Random sampling cannot settle this.  The signed-minor conditions can, exactly.

THE TEST.  All edges of Gamma_11 are odd (the signed graph is (G, E)).  Signed-minor operations:
delete edges/vertices, contract EVEN edges, and resign (switch).  Hence

  * a branch set may be contracted iff it induces a CONNECTED BIPARTITE subgraph
    (balanced = no odd cycle inside; with all edges odd, balanced <=> bipartite),
  * switching to make that subgraph all-even means labelling it by its 2-colouring l,
  * a connecting edge uv (u in T_i, v in T_j) has new sign 1 + l(u) + l(v), so it survives as
    ODD exactly when l(u) = l(v),
  * every other connecting edge is simply deleted.

So an odd-K5 minor on branch sets T_1..T_5 exists iff there is a choice of the (unique up to
global flip) 2-colouring of each T_i such that ALL TEN pairs carry a connecting edge with
l(u) = l(v).  That is 2^5 checks, exact and finite.

Runs (flags): --and4 (the claimed minor), --wagner (exhaustive: no odd-K5 minor in Gamma_8),
--gap (explicit finite gap weight on Gamma_11), --chain (Gamma_11 induced in Gamma_14?).
Default: all of them.
"""
import sys
from fractions import Fraction as F
from itertools import combinations


# ---------------------------------------------------------------- the graphs

def gamma(n):
    """Andrasfai circle graph: u ~ v iff 3 * circdist(u,v) > n.  And(k) = Gamma_{3k-1}."""
    E = []
    for u in range(n):
        for v in range(u + 1, n):
            d = min((u - v) % n, (v - u) % n)
            if 3 * d > n:
                E.append((u, v))
    return E


def adjacency(n, E):
    A = [set() for _ in range(n)]
    for u, v in E:
        A[u].add(v)
        A[v].add(u)
    return A


# ------------------------------------------------- branch sets and odd minors

def colouring(T, A):
    """2-colour the subgraph induced on T.  Returns dict or None if disconnected/non-bipartite."""
    T = list(T)
    start = T[0]
    col = {start: 0}
    stack = [start]
    seen = {start}
    Tset = set(T)
    while stack:
        u = stack.pop()
        for v in A[u] & Tset:
            if v not in col:
                col[v] = 1 - col[u]
                seen.add(v)
                stack.append(v)
            elif col[v] == col[u]:
                return None                      # odd cycle inside: not balanced
    if len(seen) != len(T):
        return None                              # disconnected
    return col


def odd_k5(branch, A):
    """Return a flip vector making all 10 pairs odd-connected, else None."""
    cols = []
    for T in branch:
        c = colouring(T, A)
        if c is None:
            return None
        cols.append(c)
    for mask in range(1 << (len(branch) - 1)):   # fix branch 0's flip by global switching
        flip = [0] + [(mask >> i) & 1 for i in range(len(branch) - 1)]
        ok = True
        for i in range(5):
            for j in range(i + 1, 5):
                found = False
                for u in branch[i]:
                    for v in branch[j]:
                        if v in A[u] and (cols[i][u] ^ flip[i]) == (cols[j][v] ^ flip[j]):
                            found = True
                            break
                    if found:
                        break
                if not found:
                    ok = False
                    break
            if not ok:
                break
        if ok:
            return flip, cols
    return None


def kept_edges(branch, A, flip, cols):
    out = []
    for i in range(5):
        for j in range(i + 1, 5):
            for u in branch[i]:
                for v in branch[j]:
                    if v in A[u] and (cols[i][u] ^ flip[i]) == (cols[j][v] ^ flip[j]):
                        out.append((i, j, tuple(sorted((u, v)))))
                        break
                else:
                    continue
                break
    return out


# ------------------------------------------------------------------ the runs

def run_and4():
    n = 11
    E = gamma(n)
    A = adjacency(n, E)
    print(f"Gamma_11 = And(4): |V| = {n}, |E| = {len(E)}   degrees {sorted(len(a) for a in A)[:1]}..")
    assert len(E) == 22, len(E)
    branch = [{0, 4, 8}, {1, 5, 9}, {2, 6, 10}, {3}, {7}]
    print(f"  claimed branch sets: {[sorted(T) for T in branch]}")
    for T in branch:
        c = colouring(T, A)
        ind = [tuple(sorted((u, v))) for u, v in combinations(sorted(T), 2) if v in A[u]]
        print(f"    {sorted(T)}: induced edges {ind}, connected+bipartite = {c is not None}, "
              f"colouring {c}")
    r = odd_k5(branch, A)
    if r is None:
        print("  VERDICT: the claimed branch sets do NOT give an odd-K5 minor.")
        return False
    flip, cols = r
    ke = kept_edges(branch, A, flip, cols)
    print(f"  flip vector {flip}  ->  all 10 pairs odd-connected")
    for i, j, e in ke:
        print(f"    pair ({i},{j}) realised by the odd edge {e}")
    assert len({(i, j) for i, j, _ in ke}) == 10
    print("  VERDICT: the odd-K5 minor in And(4) is GENUINE.")
    return True


def run_wagner():
    """Exhaustive: Gamma_8 = And(3) = Wagner has NO odd-K5 minor (hence is weakly bipartite)."""
    n = 8
    E = gamma(n)
    A = adjacency(n, E)
    print(f"Gamma_8 = And(3) = Wagner: |V| = {n}, |E| = {len(E)}")
    assert len(E) == 12, len(E)
    found = []
    tested = [0]

    def rec(v, parts):
        if found:
            return
        if v == n:
            if len(parts) == 5 and all(parts):
                tested[0] += 1
                if odd_k5(parts, A) is not None:
                    found.append([sorted(p) for p in parts])
            return
        rec(v + 1, parts)                              # v unused (vertex deletion)
        for i in range(len(parts)):
            parts[i].add(v)
            rec(v + 1, parts)
            parts[i].remove(v)
        if len(parts) < 5:                             # open a new branch set (canonical order)
            parts.append({v})
            rec(v + 1, parts)
            parts.pop()

    rec(0, [])
    print(f"  exhaustive over all canonical 5-tuples of disjoint branch sets: {tested[0]} tested")
    print(f"  VERDICT: odd-K5 minors found = {len(found)}"
          + (f"  e.g. {found[0]}" if found else "  -> Wagner IS weakly bipartite (Guenin)"))
    return not found


def cycles_odd(n, E, A):
    """All odd cycles (as frozensets of edge indices)."""
    idx = {tuple(sorted(e)): i for i, e in enumerate(E)}
    out = set()
    for s in range(n):
        path = [s]
        used = {s}

        def dfs(u, elist):
            for v in sorted(A[u]):
                if v == s and len(path) >= 3 and len(path) % 2 == 1:
                    out.add(frozenset(elist + [idx[tuple(sorted((u, v)))]]))
                elif v > s and v not in used:
                    used.add(v)
                    path.append(v)
                    dfs(v, elist + [idx[tuple(sorted((u, v)))]])
                    path.pop()
                    used.remove(v)

        dfs(s, [])
    return sorted(out, key=lambda c: (len(c), sorted(c)))


def run_gap():
    """Explicit FINITE weight on Gamma_11 with tau_w > tau*_w, certified exactly."""
    n = 11
    E = gamma(n)
    A = adjacency(n, E)
    idx = {tuple(sorted(e)): i for i, e in enumerate(E)}
    branch = [{0, 4, 8}, {1, 5, 9}, {2, 6, 10}, {3}, {7}]
    r = odd_k5(branch, A)
    if r is None:
        print("  no minor, skipping gap search")
        return False
    flip, cols = r
    keep = {idx[e] for _, _, e in kept_edges(branch, A, flip, cols)}
    inside = {idx[tuple(sorted((u, v)))]
              for T in branch for u, v in combinations(sorted(T), 2) if v in A[u]}
    rest = set(range(len(E))) - keep - inside
    print(f"  contracted (weight 0): {sorted(inside)}   kept (weight 1): {sorted(keep)}   "
          f"deleted (weight M): {sorted(rest)}")

    oc = cycles_odd(n, E, A)
    print(f"  odd cycles of Gamma_11: {len(oc)}  (lengths {sorted({len(c) for c in oc})})")

    try:
        import numpy as np
        from scipy.optimize import linprog
    except Exception as ex:
        print(f"  scipy unavailable ({ex}); reporting tau only")
        linprog = None

    for M in (2, 3, 4, 5, 6, 8, 12, 100):
        w = [0] * len(E)
        for i in keep:
            w[i] = 1
        for i in rest:
            w[i] = M
        tau = None
        for m in range(1 << (n - 1)):                  # exact integer min over all cuts
            S = (m << 1) | 1
            s = sum(w[i] for i, (u, v) in enumerate(E) if ((S >> u) & 1) == ((S >> v) & 1))
            if tau is None or s < tau:
                tau = s
        line = f"  M = {M:3d}:  tau_w = {tau}"
        if linprog is not None:
            Aub = np.zeros((len(oc), len(E)))
            for k, c in enumerate(oc):
                for i in c:
                    Aub[k, i] = -1.0
            res = linprog(np.array(w, dtype=float), A_ub=Aub, b_ub=-np.ones(len(oc)),
                          bounds=[(0, None)] * len(E), method='highs')
            if res.success:
                line += f"   tau*_w ~ {res.fun:.6f}"
                if res.fun < tau - 1e-7:
                    cert = None
                    for D in (2, 3, 4, 6, 12, 24, 60):
                        y = [F(int(round(t * D)), D) for t in res.x]
                        if all(sum(y[i] for i in c) >= 1 for c in oc):
                            val = sum(F(w[i]) * y[i] for i in range(len(E)))
                            if val < tau:
                                cert = (D, val, y)
                                break
                    if cert:
                        D, val, y = cert
                        line += f"   EXACT GAP: feasible y over 1/{D} of cost {val} < {tau} = tau_w"
                    else:
                        line += "   (numeric gap, no small-denominator exact certificate)"
        print(line)
    return True


def run_chain():
    """Is Gamma_11 an induced subgraph of Gamma_14 (so the obstruction persists for k >= 4)?"""
    for (a, b) in ((11, 14), (14, 17)):
        Ea, Eb = gamma(a), gamma(b)
        Aa, Ab = adjacency(a, Ea), adjacency(b, Eb)
        hit = None
        for S in combinations(range(b), a):
            pos = {v: i for i, v in enumerate(S)}
            deg = sorted(len(Ab[v] & set(S)) for v in S)
            if deg != sorted(len(x) for x in Aa):
                continue
            for sh in range(a):                       # try the rotation identification only
                ok = True
                for u, v in combinations(range(a), 2):
                    e1 = S[v] in Ab[S[u]]
                    e2 = ((u + sh) % a) in Aa[(v + sh) % a] if False else (v in Aa[u])
                    if e1 != e2:
                        ok = False
                        break
                if ok:
                    hit = S
                    break
            if hit:
                break
        print(f"  Gamma_{a} induced in Gamma_{b} by the identity-order embedding: "
              f"{sorted(hit) if hit else 'not found by this test'}")


if __name__ == '__main__':
    flags = set(sys.argv[1:]) or {'--and4', '--wagner', '--gap', '--chain'}
    if '--and4' in flags:
        print("=== (A) the claimed odd-K5 minor in And(4) ===")
        run_and4()
    if '--wagner' in flags:
        print("\n=== (B) exhaustive odd-K5 search in And(3) = Wagner ===")
        run_wagner()
    if '--gap' in flags:
        print("\n=== (C) explicit finite gap weight on Gamma_11 ===")
        run_gap()
    if '--chain' in flags:
        print("\n=== (D) does the obstruction persist upward? ===")
        run_chain()
