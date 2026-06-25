#!/usr/bin/env python3
"""SKEPTIC D1 part C: push SOUNDNESS to n=10,11 (NOT directly in the n=9 cert) to test whether the
per-rule average  g_r(H) >= d_mono(H) - 2/25  can ever fail on larger / denser triangle-free graphs.

This is adversarial: the closure logic extends n=9 to all n<=36 via blow-up + integrality, but the
per-rule soundness inequality is a graphon identity that should hold for ALL n. If it fails at n=10/11
that would expose a real gap in the 'min_r g_r >= d_mono - 2/25' lemma. We sample n=10,11 (and full
n=10 if feasible) and report the min gap and any violation. We compute g_r with the SAME independent
reimplementation (cm via combinations, q from pmap)."""
import pickle, itertools, time
from fractions import Fraction as F
import flag_engine as fe
import flag_sdp as fs

T = F(2, 25)

def maxcut(n, A):
    adj = [[(A[u] >> v) & 1 for v in range(n)] for u in range(n)]
    best = 0
    for mask in range(1 << (n - 1)):
        cut = 0
        for u in range(n):
            su = (mask >> u) & 1
            row = adj[u]
            for v in range(u + 1, n):
                if row[v] and su != ((mask >> v) & 1):
                    cut += 1
        if cut > best:
            best = cut
    return best

def load_atoms():
    d = pickle.load(open('dual_cert_n9.pkl', 'rb'))
    ndix, lam, prov = d['ndix'], d['lam'], d['prov']
    atoms = []
    for c in range(len(lam)):
        if F(lam[c]) == 0: continue
        pr = prov[ndix[c]]
        if pr[0] == "deficit":
            _, k, A, cls, p = pr
            pmap = {cls[j]: F(int(p[j])) for j in range(len(cls))}
        else:
            _, k, A, pmap = pr
        atoms.append((c, k, A, pmap))
    return atoms

def gr_one(n, A, adj, k, Asig, pmap):
    sigma = (k, Asig)
    m = n - k
    if m < 2: return F(0)
    Cm2 = m * (m - 1) // 2
    nk = 1
    for i in range(k): nk *= (n - i)
    if nk == 0 or Cm2 == 0: return F(0)
    g = F(0)
    for R in itertools.permutations(range(n), k):
        if not fs._induces_sigma_ordered(A, R, sigma):
            continue
        Rset = set(R)
        rest = [w for w in range(n) if w not in Rset]
        q = {}
        for w in rest:
            alpha = frozenset(ii for ii in range(k) if adj[w][R[ii]])
            q[w] = pmap.get(alpha, F(1, 2))
        cm = F(0)
        for u, v in itertools.combinations(rest, 2):
            if adj[u][v]:
                cm += q[u]*q[v] + (1-q[u])*(1-q[v])
        g += (cm / Cm2 - T)
    return g / nk

def main():
    atoms = load_atoms()
    for n in (10, 11):
        t0 = time.time()
        states = fe.enumerate_graphs(n, triangle_free=True)
        print(f"n={n}: {len(states)} triangle-free states [{time.time()-t0:.0f}s enum]")
        min_gap = F(10**9); viol = []; nb_checked = 0
        for si, (nn, A) in enumerate(states):
            adj = [[bool((A[u] >> v) & 1) for v in range(nn)] for u in range(nn)]
            # only check band-ish + a margin; but for soundness test ALL densities
            e = sum(1 for u in range(nn) for v in range(u+1, nn) if adj[u][v])
            mc = maxcut(nn, A)
            dm = F(2*(e-mc), nn*nn)
            rhs = dm - T
            nb_checked += 1
            for (c, k, Asig, pmap) in atoms:
                g = gr_one(nn, A, adj, k, Asig, pmap)
                gap = g - rhs
                if gap < min_gap:
                    min_gap = gap
                if gap < 0:
                    viol.append((n, si, c, float(g), float(rhs)))
            if si % 2000 == 0 and si:
                print(f"   ...{si}/{len(states)} min_gap={float(min_gap):.4e} viol={len(viol)} [{time.time()-t0:.0f}s]", flush=True)
        print(f"n={n}: checked {nb_checked} states x {len(atoms)} atoms; min gap = {float(min_gap):.6e}; violations = {len(viol)} [{time.time()-t0:.0f}s]", flush=True)
        for v in viol[:20]:
            print("   VIOLATION", v)

if __name__ == "__main__":
    main()
