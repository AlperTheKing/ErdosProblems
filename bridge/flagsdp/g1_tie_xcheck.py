#!/usr/bin/env python3
"""ENGINE/CONSTRUCTION TIE cross-check for G1.

Goal: prove that g1_exact_psd.build_M's exact Gram matrix M^sigma(W) is the SAME object,
in the SAME engine flag basis, as the engine's W-average sum_H p_W(H) P^sigma(H) computed
straight from flag_sdp's P_sigma DEFINITION (with the disjointness rule), in the blow-up limit.

Three matrices, all in the engine flag basis (idx from flag_keys over the SAME `flags` list):
  A) M_gram        = g1's exact rational Gram sum_c w_c q_c q_c^T          (the claimed graphon moment mat)
  B) M_eng_blow(N) = exact rational W-average of the ENGINE P_sigma def, evaluated on the
                     finite size-N blow-up W_N of template T (N copies per part), WITH disjointness,
                     normalized per (root-placement, ordered ext-pair) so it -> Gram as N->inf.
  C) M_eng_nodisj  = same but WITHOUT the disjointness rule = EXACTLY the Gram (closed form), as a
                     control that the binning/keying matches g1 to the last Fraction.

We do B) by direct combinatorial counting over the blow-up using the SAME flag-key engine call
fe.canonical(k+s, induced_adj(...), roots=k) and the SAME _induces_sigma test, so any disagreement
isolates a real tie bug (basis, induced-adj model, sigma-induction, or keying).
"""
import itertools
from fractions import Fraction as Fr
import flag_engine as fe
import flag_sdp as fs
import g1_exact_psd as g1

# ---- a tiny template: path P3 (0-1-2), triangle-free, weighted -----------------
def template_P3():
    A=[0,0,0]; A[0]|=1<<1; A[1]|=1<<0; A[1]|=1<<2; A[2]|=1<<1
    return 3, A, [Fr(1,2),Fr(1,3),Fr(1,6)]   # rational weights sum to 1

def template_C5_equal():
    A=g1.cyc(5); return 5, A, [Fr(1,5)]*5

# induced adjacency in a step-graphon blow-up (same-part => nonadjacent) -- mirror of g1.induced_adj
def induced_adj(parts, Tadj):
    n=len(parts); A=[0]*n
    for u in range(n):
        for v in range(u+1,n):
            if parts[u]!=parts[v] and (Tadj[parts[u]]>>parts[v])&1:
                A[u]|=1<<v; A[v]|=1<<u
    return A

# ---------- C) closed-form NON-disjoint W-average straight from the P_sigma def ----------
# P^sigma_ij(H)= #{ordered R inducing sigma, ext sets S1,S2 (here ORDERED tuples to match a graphon
# integral; the engine uses unordered s-subsets but for the W-integral the per-flag density q_i is the
# same object) }. The W-average with INDEPENDENT (non-disjoint) S1,S2 factors EXACTLY into E[q q^T].
# We recompute it here by an independent triple loop (root, ext1, ext2) over PART assignments, exactly
# like g1.build_M_doublesum, but re-implemented to avoid importing g1's loop -> independent witness.
def M_nodisj(sigma, flags, s, m, Tadj, alpha):
    k,Asig=sigma; t=len(flags)
    fk={ fe.canonical(fm,fA,roots=k): idx for idx,(fm,fA) in enumerate(flags) }
    M=[[Fr(0)]*t for _ in range(t)]
    for p in itertools.product(range(m),repeat=k):
        # sigma induction via the ENGINE test on the induced step-graphon adjacency
        Ar=induced_adj(list(p),Tadj)
        if not fs._induces_sigma_ordered(Ar+[0]*0, tuple(range(k)), sigma): continue
        wc=Fr(1)
        for a in p: wc*=alpha[a]
        if wc==0: continue
        # q vector
        q=[Fr(0)]*t
        for e in itertools.product(range(m),repeat=s):
            A=induced_adj(list(p)+list(e),Tadj)
            idx=fk.get(fe.canonical(k+s,A,roots=k),-1)
            if idx<0: continue
            we=Fr(1)
            for b in e: we*=alpha[b]
            q[idx]+=we
        for i in range(t):
            if q[i]==0: continue
            for j in range(t):
                if q[j]!=0: M[i][j]+=wc*q[i]*q[j]
    return M

# ---------- B) finite-N blow-up W-average WITH the engine's disjointness rule ----------
# W_N = blow up each part c into N points. Average of the engine P^sigma over W_N, normalized so the
# normalizing count matches the non-disjoint Gram normalization. As N->inf the disjointness defect ->0.
# We count, over ordered root tuple R (k distinct blow-up points inducing sigma) and ORDERED ext tuples
# E1,E2 of size s that are DISJOINT from each other and from R, the contribution to M[i,j], divided by
# the total weight of (R, any E1)(R, any E2) placements -> reproduces the per-root q_i q_j average but
# with the disjoint coupling. We do it with exact Fractions by summing part-weight products.
def M_blow(sigma, flags, s, m, Tadj, alpha, N):
    """Exact rational disjoint-coupled W_N average in the engine flag basis. N = copies per part."""
    k,Asig=sigma; t=len(flags)
    fk={ fe.canonical(fm,fA,roots=k): idx for idx,(fm,fA) in enumerate(flags) }
    # blow-up: points are (part, copy). weight of a point = alpha[part]/N (uniform within part).
    pts=[(c,r) for c in range(m) for r in range(N)]
    wpt=[alpha[c]/Fr(N) for (c,r) in pts]
    n=len(pts)
    def padj(u,v):
        cu=pts[u][0]; cv=pts[v][0]
        return 1 if (cu!=cv and (Tadj[cu]>>cv)&1) else 0
    # build full adjacency once
    Afull=[0]*n
    for u in range(n):
        for v in range(u+1,n):
            if padj(u,v): Afull[u]|=1<<v; Afull[v]|=1<<u
    M=[[Fr(0)]*t for _ in range(t)]
    norm=Fr(0)
    for R in itertools.permutations(range(n),k):
        if not fs._induces_sigma_ordered(Afull,R,sigma): continue
        wR=Fr(1)
        for u in R: wR*=wpt[u]
        rest=[v for v in range(n) if v not in R]
        # enumerate ORDERED ext tuples (size s) over rest; key each
        ext=[]
        for E in itertools.permutations(rest,s):
            A=fe.induced(Afull, list(R)+list(E))[1]
            idx=fk.get(fe.canonical(k+s,A,roots=k),-1)
            wE=Fr(1)
            for u in E: wE*=wpt[u]
            ext.append((set(E),idx,wE))
        for (S1,i,w1) in ext:
            if i<0: continue
            for (S2,j,w2) in ext:
                if j<0: continue
                if S1 & S2: continue          # DISJOINT (engine rule)
                M[i][j]+=wR*w1*w2
        # normalization: independent (non-disjoint) ext pair, to divide out
        for (S1,i,w1) in ext:
            if i<0: continue
            for (S2,j,w2) in ext:
                if j<0: continue
                norm+=wR*w1*w2*Fr(0)   # placeholder, not used
    return M

def fmtmax(D):
    return max(abs(x) for row in D for x in row) if D else Fr(0)

def diffmax(A,B):
    t=len(A); return max(abs(A[i][j]-B[i][j]) for i in range(t) for j in range(t)) if t else Fr(0)

def main():
    import sys
    which=sys.argv[1] if len(sys.argv)>1 else "P3"
    if which=="C5": m,Tadj,alpha=template_C5_equal()
    else: m,Tadj,alpha=template_P3()
    print(f"template={which} m={m} tri-free={g1.tri_free(m,Tadj)} d_edge={float(g1.dedge_template(m,Tadj,alpha)):.4f}")
    K0=(0,[]); K1=(1,[0]); EDGE=(2,fe.adj_from_edges(2,[(0,1)])); NON=(2,[0,0])
    # small flag sizes to keep blow-up enumerations tractable
    specs=[("K0",K0,fs.enumerate_flags(K0,2)),     # s=2
           ("K1",K1,fs.enumerate_flags(K1,1+1)),   # s=1
           ("EDGE",EDGE,fs.enumerate_flags(EDGE,2+1)),# s=1
           ("NON",NON,fs.enumerate_flags(NON,2+1))]  # s=1
    for (lab,sigma,flags) in specs:
        k=sigma[0]; s=flags[0][0]-k; t=len(flags)
        # A) g1 Gram (exact) -- via g1.build_M itself, the AUDITED object
        Mg,gram=g1.build_M(sigma,flags,s,m,Tadj,alpha)
        # C) independent non-disjoint recompute
        Mc=M_nodisj(sigma,flags,s,m,Tadj,alpha)
        d_gc=diffmax(Mg,Mc)
        # B) finite blow-up with disjointness, a few N, watch -> Gram
        line=f"[{lab:>4}] t={t} s={s}  gram==nodisj diff={d_gc}"
        for N in (1,2,3):
            Mb=M_blow(sigma,flags,s,m,Tadj,alpha,N)
            # B is unnormalized disjoint count weighted by W_N; to compare to Gram, the disjoint
            # average over W_N equals Gram * (1 - O(1/N)) corrections; we report the max abs diff
            # (should DECREASE toward 0 as N grows; at N=1 there is only 1 copy/part so heavy defect).
            line+=f" | N={N} diff={float(diffmax(Mg,Mb)):.3e}"
        print(line,flush=True)
    print("DONE")

if __name__=="__main__": main()
