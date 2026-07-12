# CHECK-1 (corpus miner): exact f2(p,t) = max edges of a triangle-free graph on p vertices
# containing >= 2 vertices of degree >= t (the two rotating profile owners' shore demand),
# and the t-uniform bottom-of-window kill table combining:
#   (a) R49 endpoint-trichotomy branch  (q = t  ==> all coverage Type-1 on owner-shore externals)
#   (b) Mantel-with-degree squeeze     (e_L >= t^2 - floor(q^2/4), e_L <= f2(p,t))
# Integer arithmetic only.
#
# Claimed closed form: f2(p,t) = t*(p-t) for t+2 <= p <= 2t-1 ; floor(p^2/4) for p >= 2t-1.
# Derivation (structured complete decomposition): any tri-free G with deg(v)=d>=t has N(v)=I
# independent; R = rest (k = p-1-d); edges = d + sum_i |S_i| + e(H) with S_i = {r : i~r}
# required H-independent (shared I-neighbour of an H-edge = triangle); so
# f2 = max_{d>=t} [ d + max_{H tri-free on k} ( d*alpha(H) + e(H) ) ].
# This script computes that exactly (H exhaustive) AND cross-validates with a fully
# exhaustive generation of ALL labelled triangle-free graphs for p <= 7.

import itertools, sys
from functools import lru_cache

def triangle_free(adj, p):
    for a in range(p):
        for b in range(a+1, p):
            if adj[a] >> b & 1:
                if adj[a] & adj[b]:
                    return False
    return True

def gen_trifree_graphs(k):
    """All labelled graphs on k vertices, triangle-free, as adjacency bitmask lists."""
    edges = list(itertools.combinations(range(k), 2))
    out = []
    for mask in range(1 << len(edges)):
        adj = [0]*k
        for idx, (a, b) in enumerate(edges):
            if mask >> idx & 1:
                adj[a] |= 1 << b
                adj[b] |= 1 << a
        if triangle_free(adj, k):
            out.append((adj, bin(mask).count('1')))
    return out

def alpha_of(adj, k):
    best = 0
    for mask in range(1 << k):
        ok = True
        mm = mask
        while mm:
            a = (mm & -mm).bit_length() - 1
            mm &= mm - 1
            if adj[a] & mask:
                ok = False; break
        if ok:
            best = max(best, bin(mask).count('1'))
    return best

@lru_cache(maxsize=None)
def f2_structured(p, t):
    """Exact max edges, tri-free on p vertices, >=2 vertices of degree >= t.
    Uses the complete v-rooted decomposition; second owner realized inside a maximum
    independent set of H (degree d >= t) or, when p-d >= t, inside I."""
    best = -1
    for d in range(t, p):
        k = p - 1 - d
        if k < 0: continue
        if k == 0:
            # only v has degree d; second deg->=t vertex impossible (others deg<=1)
            continue
        for adj, eH in gen_trifree_graphs(k):
            a = alpha_of(adj, k)
            # uniform max assignment: every i in I takes one fixed maximum independent set S*
            # -> every r in S* has degree d + deg_H(r) >= d >= t  (second owner exists, a>=1)
            if a >= 1:
                tot = d + d*a + eH
                best = max(best, tot)
            # also: second owner in I possible iff deg_I <= 1 + k gives p - d >= t;
            # then edges counted the same way (no gain beyond the above forms because
            # total <= d + d*alpha + e(H) regardless of where m sits) -- the uniform
            # assignment already attains the unconstrained maximum, and it realizes m.
    return best

def f2_formula(p, t):
    if p < t + 2:
        return None
    if p <= 2*t - 1:
        return t*(p - t)
    return (p*p)//4

def exhaustive_f2(p, t):
    """Fully exhaustive over all labelled tri-free graphs on p vertices (p<=7),
    generated recursively by adding vertices with independent-set neighbourhoods."""
    best = -1
    def rec(v, adj, ecount):
        nonlocal best
        if v == p:
            degs = sorted((bin(a).count('1') for a in adj), reverse=True)
            if len(degs) >= 2 and degs[1] >= t:
                best = max(best, ecount)
            return
        # neighbourhood of new vertex v must be an independent set in current graph
        for mask in range(1 << v):
            ok = True
            mm = mask
            while mm:
                a = (mm & -mm).bit_length() - 1
                mm &= mm - 1
                if adj[a] & mask:
                    ok = False; break
            if ok:
                newadj = adj + [mask]
                add = bin(mask).count('1')
                for b in range(v):
                    if mask >> b & 1:
                        newadj[b] = newadj[b] | (1 << v)
                rec(v + 1, newadj, ecount + add)
    rec(0, [], 0)
    return best

print("== f2(p,t) exact vs formula ==")
bad = 0
for t in (4, 5, 6, 7):
    for p in range(t+2, min(2*t+2, 13)):
        s = f2_structured(p, t)
        f = f2_formula(p, t)
        tag = "OK" if s == f else "MISMATCH"
        if s != f: bad += 1
        print(f"  t={t} p={p}: structured={s} formula={f} {tag}")
print()
print("== cross-validation, fully exhaustive p<=7 ==")
for (p, t) in [(6,4),(7,4),(7,5)]:
    e = exhaustive_f2(p, t)
    s = f2_structured(p, t)
    tag = "OK" if e == s else "MISMATCH"
    if e != s: bad += 1
    print(f"  p={p} t={t}: exhaustive={e} structured={s} {tag}")
print()

# ---- t-uniform bottom-of-window kill table ----
# order n, shores (p owner side, q blue side), p+q=n.
# constraints: p >= t+2 (v,m + N_M(v) with v,m not in N_M(v); |N_M(v)|=t; m outside);
#              q >= t   (N_B(v) has t vertices).
# demand:  e_L >= t^2 - floor(q^2/4)  (bads split; blue side Mantel)
#          e_L >= 2t                  (v,m bad stars edge-disjoint)
# capacity: e_L <= f2(p,t)
# trichotomy branch: q == t  ==> r_ext = 0 ==> all t-1 coverage atoms Type-1
#          = bad edges among owner-shore vertices outside {v} u N_M(v) (that pool has
#            size ell = p-1-t, includes m), themselves triangle-free:
#          need floor(ell^2/4) >= t-1, else KILL. (Also middles q~ live in same pool: ignored, upper bound only.)
def split_survives(n, p, t, verbose=False):
    q = n - p
    if p < t+2 or q < t:
        return False, "shore-size"
    fl = f2_formula(p, t)
    demand = max(t*t - (q*q)//4, 2*t)
    if demand > fl:
        return False, f"Mantel-degree (need e_L>={demand} > f2={fl})"
    if q == t:
        ell = p - 1 - t
        if (ell*ell)//4 < t - 1:
            return False, f"trichotomy Type-1 (floor(ell^2/4)={ (ell*ell)//4 } < t-1={t-1}, ell={ell})"
        if (ell*ell)//4 == t - 1:
            return True, f"EQUALITY-RIGID trichotomy (Type-1 bads = Mantel-extremal on ell={ell})"
    if demand == fl:
        return True, f"EQUALITY-RIGID Mantel-degree (e_L forced = f2 = {fl}; unique extremal shape)"
    return True, "live"

print("== t-uniform window bottoms (all splits per order) ==")
for t in (5, 6, 7, 8, 9, 10):
    top = t*t - t + 1   # cycle-rank cap (R46/R48): |V| <= t^2 - t + 1
    nmin = None
    detail = {}
    for n in range(2*t+2, top+1):
        alive = []
        for p in range(t+2, n - t + 1):
            s, why = split_survives(n, p, t)
            if s:
                alive.append((p, n-p, why))
        detail[n] = alive
        if alive and nmin is None:
            nmin = n
    print(f"t={t}: first surviving order n_min = {nmin}  (cycle-rank top = {top})")
    for n in range(2*t+2, min(nmin+2, top)+1):
        rows = detail[n]
        if not rows:
            print(f"   order {n}: ALL SPLITS DEAD")
        else:
            for (p, q, why) in rows:
                print(f"   order {n}: split ({p},{q}) survives [{why}]")
print()
print("mismatches:", bad)
