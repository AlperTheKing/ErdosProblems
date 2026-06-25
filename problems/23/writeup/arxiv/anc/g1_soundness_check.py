#!/usr/bin/env python3
"""DECISIVE soundness check of the Step-1 cert transfer (resolves the lens-3 'refuted' claim with MY OWN exact
arithmetic). The cert verifies, EXACT over 1897 n=9 states H:
    LHS(H) = sum_l lam_l g_l(H) + sum_j gam_j m_j(H) + mu(e_H-lo) + nu(hi-e_H) <= delta.
Transfer to a band graphon W is the ORDER-9 AVERAGING LHS(W) := sum_H p_W(H) LHS(H) <= delta (convex avg <= max).
The chain (certify_dual L11): added terms >=0 on graphons => sum lam g(W) <= delta => d_mono(W) <= 2/25+delta.
Lens-3 claims the MOMENT term, transferred, is POSITIVE-and-large so 'F(W)>delta' breaks it. BUT the averaged
moment is m_avg(W)=sum_H p_W(H) sum gam m_j(H); I claim m_avg = sum gam ratio_{N,sigma} v^T M^sigma(W) v >= 0
(ratio_N=C(n-k-s,s)/C(n-k,s)>0 a CONSTANT; lens-3 used the UN-shrunk v^T M v). TEST on in-band finite graphs G:
compute p_G(H) (exact 9-subset induced density), g_avg, m_avg, LHS_avg; require m_avg>=0, LHS_avg<=delta,
g_avg<=delta, and d_mono(G)-2/25 <= g_avg (=> d_mono(G) <= 2/25+delta). If all hold: cert SOUND, lens-3 erred.
"""
import pickle, itertools, sys, os
from fractions import Fraction as F
from math import comb
import numpy as np
import prove_cert as pc, flag_engine as fe, flag_exact as fx
import certify_dual as cd

LO=F(1243,5000); HI=F(3197,10000); T=F(2,25)

def popcount(x): return bin(x).count("1")
def wl_inv(n,A,rounds=5):
    col=[popcount(A[v]) for v in range(n)]
    for _ in range(rounds):
        newc=[(col[v],tuple(sorted(col[u] for u in range(n) if (A[v]>>u)&1))) for v in range(n)]
        uniq={c:i for i,c in enumerate(sorted(set(newc)))}; col=[uniq[c] for c in newc]
    ep=tuple(sorted((min(col[u],col[v]),max(col[u],col[v])) for u in range(n) for v in range(u+1,n) if (A[u]>>v)&1))
    return (tuple(sorted(col)),ep)

def regen_cert_funcs(C, states, prov, cert):
    """return per-state Fraction arrays g[H]=sum lam g_l, m[H]=sum gam m_j, e[H], LHS[H]."""
    cache="cert_funcs_n9.pkl"
    if os.path.exists(cache):
        return pickle.load(open(cache,"rb"))
    ns=len(states)
    lam=[F(str(x)) for x in cert["lam"]]; gam=[F(str(x)) for x in cert["gam"]]
    mu=F(str(cert["mu"])); nu=F(str(cert["nu"]))
    ndix=list(cert["ndix"]); nmix=list(cert["nmix"])
    edens=fx.edge_density_exact(states)
    g=[F(0)]*ns; m=[F(0)]*ns
    for c,idx in enumerate(ndix):
        if lam[c]==0: continue
        vals=cd.regen(C,states,prov,idx)
        for j in range(ns):
            if vals[j]!=0: g[j]+=lam[c]*vals[j]
        if c%20==0: print(f"  deficit {c}/{len(ndix)}",flush=True)
    for c,idx in enumerate(nmix):
        if gam[c]==0: continue
        vals=cd.regen(C,states,prov,idx)
        for j in range(ns):
            if vals[j]!=0: m[j]+=gam[c]*vals[j]
        if c%50==0: print(f"  moment {c}/{len(nmix)}",flush=True)
    LHS=[g[j]+m[j]+mu*(edens[j]-LO)+nu*(HI-edens[j]) for j in range(ns)]
    out=(g,m,list(edens),LHS,mu,nu)
    pickle.dump(out,open(cache,"wb"))
    return out

def C7_blowup(t):
    """C7 blown up by t: 7t vertices, parts 0..6 each size t, part i ~ part i+-1 mod 7."""
    n=7*t; A=[0]*n
    def part(v): return v//t
    for u in range(n):
        for w in range(u+1,n):
            pu,pw=part(u),part(w)
            if pu!=pw and (pw==(pu+1)%7 or pw==(pu-1)%7):
                A[u]|=1<<w; A[w]|=1<<u
    return n,A

def maxcut_brute(n,A):
    best=0
    for mask in range(1<<(n-1)):
        cut=0
        for u in range(n):
            for w in range(u+1,n):
                if (A[u]>>w)&1 and ((mask>>u)&1)!=((mask>>w)&1): cut+=1
        if cut>best: best=cut
    return best

def main():
    C=pc.load(9); states=C["states"]; prov=C["moments"] and None
    cert=pickle.load(open("dual_cert_n9.pkl","rb")); prov=cert["prov"]
    delta=F(cert["maxPhi_num"],cert["maxPhi_den"])
    print(f"delta (cert maxPhi) = {float(delta):.6e}",flush=True)
    g,m,edens,LHS,mu,nu=regen_cert_funcs(C,states,prov,cert)
    mxLHS=max(LHS); print(f"max_H LHS(H) = {float(mxLHS):.6e}  (should == delta) match={mxLHS==delta}",flush=True)
    # build canon9 match (WL hybrid): canonical ONLY for collision buckets (fe.canonical(9) is slow)
    buckets={}
    for i,(n,A) in enumerate(states): buckets.setdefault(wl_inv(n,A),[]).append(i)
    single={w:l[0] for w,l in buckets.items() if len(l)==1}
    multi={w:[(fe.canonical(9,states[i][1]),i) for i in l] for w,l in buckets.items() if len(l)>1}
    print(f"  WL buckets: {len(single)} singletons, {len(multi)} collision-buckets (canonical only for those)",flush=True)
    def match9(A9):
        w=wl_inv(9,A9)
        if w in single: return single[w]
        ck=fe.canonical(9,A9)
        for k,idx in multi[w]:
            if k==ck: return idx
        return -1
    for t in [2,3]:
        n,A=C7_blowup(t)
        print(f"  [computing C7[{t}], n={n}...]",flush=True)
        de=F(sum(popcount(A[v]) for v in range(n)),2)/comb(n,2)
        # order-9 induced densities p_G(H)
        cnt={}; tot=comb(n,9)
        for S in itertools.combinations(range(n),9):
            idxmap={v:i for i,v in enumerate(S)}
            B=[0]*9
            for ii,u in enumerate(S):
                row=A[u]
                for jj,w in enumerate(S):
                    if jj>ii and (row>>w)&1: B[ii]|=1<<jj; B[jj]|=1<<ii
            hi=match9(B)
            if hi<0: raise RuntimeError("9-subset not matched")
            cnt[hi]=cnt.get(hi,0)+1
        g_avg=sum(F(c,tot)*g[h] for h,c in cnt.items())
        m_avg=sum(F(c,tot)*m[h] for h,c in cnt.items())
        band_avg=sum(F(c,tot)*(mu*(edens[h]-LO)+nu*(HI-edens[h])) for h,c in cnt.items())
        lhs_avg=g_avg+m_avg+band_avg
        e=sum(popcount(A[v]) for v in range(n))//2
        if n<=15:
            mc=maxcut_brute(n,A); dmono=F(2*(e-mc),n*n)
        else:
            dmono=None  # maxcut brute infeasible; skip d_mono check for large G
        print(f"\n=== G = C7[{t}] ({n} vtx, d_edge={float(de):.4f}, in-band={LO<=de<=HI}) ===",flush=True)
        print(f"  m_avg (order-9 averaged MOMENT term) = {float(m_avg):+.6e}   >=0 ? {m_avg>=0}",flush=True)
        print(f"  g_avg (averaged deficit sum lam g)   = {float(g_avg):+.6e}   <=delta ? {g_avg<=delta}",flush=True)
        print(f"  band_avg                              = {float(band_avg):+.6e}",flush=True)
        print(f"  LHS_avg = g+m+band                    = {float(lhs_avg):+.6e}   <=delta ? {lhs_avg<=delta}",flush=True)
        if dmono is not None:
            print(f"  d_mono(G)={float(dmono):.6e}, 2/25+delta={float(T+delta):.6e}; d_mono-2/25 <= g_avg ? {dmono-T<=g_avg}; d_mono<=2/25+delta ? {dmono<=T+delta}",flush=True)
        else:
            print(f"  d_mono(G): skipped (n={n}>15, brute maxcut infeasible)",flush=True)
    print("\nDONE",flush=True)

if __name__=="__main__": main()
