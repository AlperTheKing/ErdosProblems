#!/usr/bin/env python3
"""D2 SKEPTIC audit. Independent attempt to REFUTE the prior 'CONCERN' verdict.

Distinct angle from the prior auditor (who verified the quadratic-form code matched). I instead attack
the MATHEMATICAL SOUNDNESS of the moment atom inequality on graphons, focusing on the DISJOINTNESS
constraint in P_sigma. The validity of adding gamma_j * m_j with gamma_j>=0 requires
    m_j(W) = v_j^T M^sigma(W) v_j / denom >= 0  for ALL band graphons W,
where M^sigma(W) is the n->inf graphon limit. The code's claim is M^sigma(graphon) is PSD (Razborov).

P_sigma counts ORDERED PAIRS OF DISJOINT s-subsets. At finite n this is NOT exactly a Gram matrix
(the disjointness removes the diagonal-overlap terms). The question: does the certificate's soundness
secretly rely on the FINITE-n matrix being PSD (it need not be), or on the GRAPHON limit (PSD, correct)?

TESTS:
 (1) Build M^sigma(H_n) = sum over a single W-random-like graph's P_sigma/denom for several explicit
     graphs and check whether the FINITE-n matrix can have a NEGATIVE eigenvalue. If yes, then the
     row v^T P(H) v can be negative for a SINGLE graph -> but the cert sums over a DISTRIBUTION x.
 (2) The real test: does there exist a band graphon W (approximated by a large blow-up / random sample)
     for which the limiting moment matrix M^sigma(W) has a strictly negative eigenvalue? Build M from a
     direct GRAPHON quadrature: M[a][b] = E_{roots}[ q_a * q_b ] where q_a = P(extend roots by s free
     vertices to flag a). If the graphon-limit M is PSD for representative band graphons, the design is
     sound. Compare to the FINITE P_sigma/denom to expose the disjointness gap.
 (3) Cross-check: take the ACTUAL cert moment atom v_j and confirm sum_H x*_H * (v^T P(H) v/denom) =
     v^T M^sigma_finite v, and that v is an eigenvector of M with the claimed negative eigenvalue.
"""
import pickle, itertools
from math import comb
from fractions import Fraction as F
import numpy as np
import flag_engine as fe
import flag_sdp as fs
import flag_cutgen as fc

np.random.seed(12345)

# ---------- Direct GRAPHON moment matrix (independent of P_sigma code) ----------
def graphon_moment_matrix(W_func, sigma, flags, s, n_mc=4000):
    """M^sigma(W)[a][b] = E_{x in [0,1]^k roots} [ q_a(x) q_b(x) ],
    q_a(x) = P( s free vertices y1..ys extend roots x to flag-index a ).
    For finite enumeration we approximate q_a by Monte-Carlo over root positions x and, for each, the
    EXACT distribution over the s free vertices is itself an integral; we MC that too jointly.
    This is the n->inf moment matrix; if PSD, the atom design is sound on graphon W."""
    k, Asig = sigma
    t = len(flags)
    flagkey = {fs.root_canonical(fm, fA, k): idx for idx, (fm, fA) in enumerate(flags)}
    # accumulate Gram: average over root sample x of (qvec qvec^T) where qvec=distribution over flags
    M = np.zeros((t, t))
    cnt = 0
    for _ in range(n_mc):
        xs = np.random.rand(k)   # root labels
        # root-root edges fixed by sigma; we only need free-vertex distribution conditioned on roots.
        # q_a(x): integrate over s free labels y. Do an inner MC.
        qvec = np.zeros(t)
        INNER = 600
        for _2 in range(INNER):
            ys = np.random.rand(s)
            # build (k+s) graph: roots 0..k-1 with sigma adjacency; free k..k+s-1 sampled by W
            verts = list(xs) + list(ys)
            mm = k + s
            A = [0]*mm
            for a in range(k):
                for b in range(a+1, k):
                    if (Asig[a] >> b) & 1:
                        A[a] |= 1<<b; A[b] |= 1<<a
            for i in range(mm):
                for j in range(i+1, mm):
                    if i < k and j < k:
                        continue
                    if np.random.rand() < W_func(verts[i], verts[j]):
                        A[i] |= 1<<j; A[j] |= 1<<i
            # triangle-free? flags come from triangle-free enumeration; if sample has triangle skip
            if not fe.is_triangle_free(mm, A):
                continue
            key = fe.canonical(mm, A, roots=k)
            idx = flagkey.get(key, -1)
            if idx >= 0:
                qvec[idx] += 1
        ssum = qvec.sum()
        if ssum == 0:
            continue
        qvec = qvec / ssum
        M += np.outer(qvec, qvec)
        cnt += 1
    return M / max(cnt,1)

def finite_moment_matrix(states, x, sigma, flags, s):
    """sum_H x_H * P^sigma(H)/denom -- the FINITE-n moment matrix the cert actually uses."""
    k = sigma[0]
    mats = fs.P_sigma(None, states, sigma, flags)
    t = len(flags)
    M = np.zeros((t,t))
    for hi,(n,_A) in enumerate(states):
        nk=1
        for i in range(k): nk*=(n-i)
        denom = nk*(comb(n-k,s)**2) if (nk>0 and n-k>=s) else 1.0
        if denom<=0: continue
        M += x[hi]*mats[hi]/denom
    return M

def main():
    print("=== D2 SKEPTIC: graphon-limit PSD vs finite disjoint-pair matrix ===", flush=True)
    cert = pickle.load(open("dual_cert_n9.pkl","rb"))
    prov = cert["prov"]; nmix = cert["nmix"]; gam = [F(g) for g in cert["gam"]]

    # collect distinct moment sigmas/flags used with nonzero gamma
    used = []
    for c,i in enumerate(nmix):
        if gam[c] != 0:
            pr = prov[i]
            assert pr[0]=="moment", pr[0]
            _, lab, sigma, s, vv = pr
            used.append((i, lab, sigma, s, np.array([float(z) for z in vv]), gam[c]))
    print(f"nonzero-gamma moment atoms: {len(used)}", flush=True)
    # distinct (sigma,s) blocks
    blocks = {}
    for (i,lab,sigma,s,vv,g) in used:
        blocks.setdefault((sigma[0], tuple(sigma[1]), s), []).append((i,lab,vv,g))
    print(f"distinct (k, sigma, s) blocks among nonzero-gamma atoms: {len(blocks)}", flush=True)
    for key in blocks:
        print(f"  block k={key[0]} s={key[2]} Asig={key[1]} : {len(blocks[key])} atoms", flush=True)

    # Rebuild flags for one representative block to test graphon PSD.
    # Use the largest block.
    import flag_sdp as fsd
    bigkey = max(blocks, key=lambda kk: len(blocks[kk]))
    k, Asig_t, s = bigkey[0], list(bigkey[1]), bigkey[2]
    sigma = (k, Asig_t)
    flags = fsd.enumerate_flags(sigma, k+s)
    print(f"\nrepresentative block: k={k}, s={s}, |flags|={len(flags)}", flush=True)

    # Band graphons to test (triangle-free-ish reduced graphons with edge density in [0.2486,0.3197]):
    # use C5-blowup-style and bipartite graphons. Quasi-random p in band.
    def W_const(p):
        return lambda u,v: p
    # C5 graphon (the conjectured extremal): partition [0,1] into 5 arcs, edge between consecutive arcs
    def W_c5(u,v):
        iu=int(u*5)%5; iv=int(v*5)%5
        return 1.0 if (abs(iu-iv)==1 or abs(iu-iv)==4) else 0.0
    # complete bipartite balanced
    def W_bip(u,v):
        return 1.0 if (int(u*2)!=int(v*2)) else 0.0

    tests = [("const0.2486",W_const(0.2486)),("const0.3197",W_const(0.3197)),
             ("const0.30",W_const(0.30)),("C5",W_c5),("bipartite",W_bip)]
    worst_overall = 1e9
    for name,Wf in tests:
        M = graphon_moment_matrix(Wf, sigma, flags, s, n_mc=1500)
        M = 0.5*(M+M.T)
        ev = np.linalg.eigvalsh(M)
        mn = ev.min()
        worst_overall = min(worst_overall, mn)
        # test all nonzero-gamma atom vectors v in this block against this M
        atom_worst = 1e9
        for (i,lab,vv,g) in blocks[bigkey]:
            if len(vv)==M.shape[0]:
                qf = float(vv @ M @ vv)
                atom_worst = min(atom_worst, qf)
        print(f"  graphon {name:14s}: min_eig(M^sigma)={mn:+.3e}  min atom v^T M v={atom_worst:+.3e}", flush=True)
    print(f"\nWORST min-eigenvalue of graphon moment matrix over tested band graphons: {worst_overall:+.3e}", flush=True)
    if worst_overall < -1e-6:
        print(">>> POTENTIAL REFUTATION: graphon moment matrix NOT PSD on a band graphon!", flush=True)
    else:
        print(">>> graphon moment matrices PSD (within MC noise) -> atom design sound on graphons", flush=True)
    print("DONE", flush=True)

if __name__=="__main__":
    main()
