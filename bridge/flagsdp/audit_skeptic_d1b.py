#!/usr/bin/env python3
"""SKEPTIC D1 part B: probe the MECHANISM and the AVERAGING caveat of soundness.

(D) Per-R analysis: for each inducing R, is cm/Cm2 >= d_mono(H)?  (cm = mono on non-root subgraph
    under the explicit q-cut). If NOT always, then g_r (the AVERAGE) relies on cross-R cancellation
    and could fail for some graph. Report min over (state, R) of (cm/Cm2 - d_mono).

(E) Adversarial: search for ANY triangle-free state (n=5..9) and atom where the AVERAGE g_r is
    closest to d_mono - 2/25 from above, and where the per-R min dips BELOW d_mono. This tells us
    whether soundness is averaging-robust or knife-edge.

(F) Direct restatement of the certificate's soundness lemma: the cut q induces a GLOBAL bipartition
    of ALL n vertices? NO -- roots have no q. Reconstruct what global cut the rule corresponds to and
    verify cm + (root-incident mono) relationship. Specifically test: is the rule's implied cut a
    REAL cut of H, so cm >= beta over the non-root subgraph, and how that lifts to all of H.
"""
import pickle, itertools
from fractions import Fraction as F
import flag_engine as fe
import flag_sdp as fs

T = F(2, 25)

def maxcut(n, A):
    adj = [[(A[u] >> v) & 1 for v in range(n)] for u in range(n)]
    best = 0
    for mask in range(1 << (n - 1)):
        side = [(mask >> u) & 1 for u in range(n)]
        cut = 0
        for u in range(n):
            su = side[u]
            for v in range(u + 1, n):
                if adj[u][v] and su != side[v]:
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

def main():
    atoms = load_atoms()

    # (D) per-R: cm/Cm2 vs d_mono(H)
    print("=== (D) per-R: min over (state,R,atom) of (cm/Cm2 - d_mono(H)) ===")
    min_perR = F(10**9); arg = None
    cnt_below = 0; cnt_total = 0
    for n in range(5, 10):
        states = fe.enumerate_graphs(n, triangle_free=True)
        for si, (nn, A) in enumerate(states):
            adj = [[bool((A[u] >> v) & 1) for v in range(nn)] for u in range(nn)]
            e = sum(1 for u in range(nn) for v in range(u + 1, nn) if adj[u][v])
            mc = maxcut(nn, A)
            dm = F(2 * (e - mc), nn * nn)
            m = None
            for (c, k, Asig, pmap) in atoms:
                sigma = (k, Asig)
                mloc = nn - k
                if mloc < 2: continue
                Cm2 = mloc * (mloc - 1) // 2
                for R in itertools.permutations(range(nn), k):
                    if not fs._induces_sigma_ordered(A, R, sigma):
                        continue
                    Rset = set(R)
                    rest = [w for w in range(nn) if w not in Rset]
                    q = {}
                    for w in rest:
                        alpha = frozenset(ii for ii in range(k) if adj[w][R[ii]])
                        q[w] = pmap.get(alpha, F(1, 2))
                    cm = F(0)
                    for u, v in itertools.combinations(rest, 2):
                        if adj[u][v]:
                            cm += q[u]*q[v] + (1-q[u])*(1-q[v])
                    val = cm / Cm2 - dm
                    cnt_total += 1
                    if val < 0: cnt_below += 1
                    if val < min_perR:
                        min_perR = val; arg = (n, si, c)
    print(f"  min per-R (cm/Cm2 - d_mono) = {float(min_perR):.6e}  arg={arg}")
    print(f"  per-R terms below d_mono: {cnt_below}/{cnt_total}")
    print("  NOTE: per-R below d_mono is FINE; what matters is the per-rule AVERAGE g_r >= d_mono - t.")

    # (G) blow-up invariance: g_r is a graphon density functional; cert applied at n=9 extends via
    # beta(G[t])=t^2 beta(G). Verify d_mono is blow-up invariant and g_r too (sanity that n=9 binds).
    print("\n=== (G) blow-up invariance check d_mono(G[2]) == d_mono(G) for small G ===")
    bad = 0; tot = 0
    for n in range(3, 6):
        for (nn, A) in fe.enumerate_graphs(n, triangle_free=True):
            adj = [[(A[u] >> v) & 1 for v in range(nn)] for u in range(nn)]
            e = sum(1 for u in range(nn) for v in range(u+1, nn) if adj[u][v])
            mc = maxcut(nn, A); dm = F(2*(e-mc), nn*nn)
            # build G[2]: blow up each vertex to 2 (independent set within class)
            t = 2; N = nn * t
            B = [0]*N
            for u in range(nn):
                for v in range(nn):
                    if u != v and adj[u][v]:
                        for a in range(t):
                            for b in range(t):
                                ua, vb = u*t+a, v*t+b
                                B[ua] |= 1 << vb
            eB = sum(1 for u in range(N) for v in range(u+1, N) if (B[u]>>v)&1)
            mcB = maxcut(N, B); dmB = F(2*(eB-mcB), N*N)
            tot += 1
            if dmB != dm: bad += 1
    print(f"  d_mono(G[2]) != d_mono(G): {bad}/{tot}  (must be 0 for blow-up arg to hold)")

if __name__ == "__main__":
    main()
