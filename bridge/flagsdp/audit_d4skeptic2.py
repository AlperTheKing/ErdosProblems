#!/usr/bin/env python3
"""D4 SKEPTIC part 2: verify on the CERTIFIED domain (order-9 states) that
   sum_r lam_r g_r(H) <= delta   for every triangle-free H on 9 vertices,
using MY independent g_r re-implementation, and cross-check vs fx.gr_exact.

This is the real certified inequality (since gam>=0, m>=0, mu=nu=0, the moment
terms only add, so the deficit part alone must be <= delta on the n=9 domain).
If max_H sum_lam_g(H) > delta on n=9, the cert's own claim fails (modulo my
recompute being correct, which I cross-check against fx).

ALSO: the chain-(e) averaging claim. For each n=9 state separately I confirm
sum_lam_g <= delta. Then I test the chain (b) inequality sum_lam_g >= d_mono-2/25
on the n=9 domain (this is what makes the closure work)."""
import itertools, pickle
from fractions import Fraction as F
import flag_engine as fe
import flag_sdp as fs
import flag_exact as fx

T = F(2, 25)

def beta_bf(n, A):
    edges = [(i, j) for i in range(n) for j in range(i+1, n) if (A[i] >> j) & 1]
    e = len(edges); best = 0
    for mask in range(1 << n):
        c = sum(1 for (i, j) in edges if ((mask >> i) & 1) != ((mask >> j) & 1))
        if c > best: best = c
    return e - best

def d_mono(n, A):
    return F(2*beta_bf(n, A), n*n) if n else F(0)

def my_gr(states, k, Asig, pmap, t):
    sigma = (k, Asig); out = []
    for (n, A) in states:
        if n < 2: out.append(F(0)); continue
        adj = [[bool((A[u] >> v) & 1) for v in range(n)] for u in range(n)]
        nk = 1
        for i in range(k): nk *= (n - i)
        m = n - k; Cm2 = m*(m-1)//2
        if Cm2 <= 0 or nk == 0: out.append(F(0)); continue
        g = F(0)
        for R in itertools.permutations(range(n), k):
            if not fs._induces_sigma_ordered(A, R, sigma): continue
            Rset = set(R); rest = [w for w in range(n) if w not in Rset]
            q = {}
            for w in rest:
                alpha = frozenset(i for i in range(k) if adj[w][R[i]])
                q[w] = pmap.get(alpha, F(1, 2))
            cm = F(0)
            for ui in range(len(rest)):
                u = rest[ui]
                for vi in range(ui+1, len(rest)):
                    v = rest[vi]
                    if adj[u][v]: cm += q[u]*q[v] + (1-q[u])*(1-q[v])
            g += (cm/Cm2 - t)
        out.append(g/nk)
    return out

def load_pmap(prov, idx):
    pr = prov[idx]
    if pr[0] == "deficit":
        _, k, A, cls, p = pr
        return k, A, {cls[i]: F(int(p[i])) for i in range(len(cls))}
    _, k, A, pmap = pr
    return k, A, pmap

def main():
    d = pickle.load(open('dual_cert_n9.pkl', 'rb'))
    prov = d['prov']; ndix = d['ndix']; lam = [F(s) for s in d['lam']]
    mn = int(d['maxPhi_num']); md = int(d['maxPhi_den']); delta = F(mn, md)
    active = [(ndix[c], lam[c]) for c in range(len(ndix)) if lam[c] != 0]

    states = fe.enumerate_graphs(9, triangle_free=True)
    print("n=9 states:", len(states))

    # cross-check + accumulate combo using MY gr
    combos = [F(0)]*len(states)
    for (i, v) in active:
        k, A, pmap = load_pmap(prov, i)
        gmine = my_gr(states, k, A, pmap, T)
        gthe = fx.gr_exact(states, k, A, pmap, T)
        mm = sum(1 for a, b in zip(gmine, gthe) if a != b)
        print(f"atom {i} k={k}: cross-check mismatches {mm}/{len(gmine)}")
        for s in range(len(states)):
            combos[s] += v*gmine[s]

    # CERTIFIED claim: sum_lam_g(H) <= delta for all n=9 H (since moment adds nonneg)
    over = [(s, combos[s]) for s in range(len(states)) if combos[s] > delta]
    print("n=9 states with sum_lam_g > delta:", len(over))
    if over:
        mx = max(over, key=lambda t: t[1])
        print("  MAX sum_lam_g =", float(mx[1]), "vs delta", float(delta), "ratio", float(mx[1]/delta))
        n, A = states[mx[0]]
        print("  offending n=", n, "edges=", fe.num_edges(n, A), "d_mono=", float(d_mono(n, A)))
    mxall = max(combos)
    print("  overall MAX sum_lam_g over n=9 =", float(mxall), " delta =", float(delta))

    # chain (b) on n=9 domain: sum_lam_g >= d_mono - 2/25 ?
    viol = 0; worst = None
    for s, (n, A) in enumerate(states):
        slack = combos[s] - (d_mono(n, A) - T)
        if slack < 0:
            viol += 1
            if worst is None or slack < worst[0]:
                worst = (slack, n, A)
    print("chain(b) n=9: violations sum_lam_g >= d_mono-2/25 :", viol, "/", len(states))
    if worst:
        print("  worst slack", float(worst[0]))

if __name__ == "__main__":
    main()
