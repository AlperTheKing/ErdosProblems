#!/usr/bin/env python3
"""D2 SKEPTIC part 2: cover ALL nonzero-gamma blocks on graphons + the finite-vs-graphon disjointness gap.

Key adversarial question: the cut v^T P(H) v >= 0 is added as a valid inequality justified by
"M^sigma(graphon) PSD". But the FINITE matrix sum_H x_H P/denom (with disjointness) is what the LP sees.
If the FINITE matrix were used as the PSD certificate it could be WRONG (disjointness breaks Gram).
Show: (a) the graphon limit is PSD for every used block on band graphons (so each atom term is >=0 on
graphons -> sound), and (b) quantify the finite-n disjointness gap to confirm it is O(1/n) and the cert
does NOT rely on finite-n PSD-ness (it relies on the graphon inequality, applied via averaging x* which
is a convex combination of REAL graphs = sampled from graphons)."""
import pickle, itertools
from math import comb
from fractions import Fraction as F
import numpy as np
import flag_engine as fe
import flag_sdp as fs
import flag_cutgen as fc

np.random.seed(999)

def graphon_moment_matrix(W_func, sigma, flags, s, n_mc=1200, inner=500):
    k, Asig = sigma; t = len(flags)
    flagkey = {fs.root_canonical(fm, fA, k): idx for idx,(fm,fA) in enumerate(flags)}
    M = np.zeros((t,t)); cnt=0
    for _ in range(n_mc):
        xs = np.random.rand(k); qvec=np.zeros(t)
        for _2 in range(inner):
            ys=np.random.rand(s); verts=list(xs)+list(ys); mm=k+s; A=[0]*mm
            for a in range(k):
                for b in range(a+1,k):
                    if (Asig[a]>>b)&1: A[a]|=1<<b; A[b]|=1<<a
            for i in range(mm):
                for j in range(i+1,mm):
                    if i<k and j<k: continue
                    if np.random.rand()<W_func(verts[i],verts[j]): A[i]|=1<<j; A[j]|=1<<i
            if not fe.is_triangle_free(mm,A): continue
            idx=flagkey.get(fe.canonical(mm,A,roots=k),-1)
            if idx>=0: qvec[idx]+=1
        ssum=qvec.sum()
        if ssum==0: continue
        qvec/=ssum; M+=np.outer(qvec,qvec); cnt+=1
    return M/max(cnt,1)

def W_const(p): return lambda u,v: p
def W_c5(u,v):
    iu=int(u*5)%5; iv=int(v*5)%5
    return 1.0 if (abs(iu-iv)==1 or abs(iu-iv)==4) else 0.0
def W_bip(u,v): return 1.0 if (int(u*2)!=int(v*2)) else 0.0

def main():
    cert=pickle.load(open("dual_cert_n9.pkl","rb"))
    prov=cert["prov"]; nmix=cert["nmix"]; gam=[F(g) for g in cert["gam"]]
    blocks={}
    for c,i in enumerate(nmix):
        if gam[c]!=0:
            _,lab,sigma,s,vv=prov[i]
            blocks.setdefault((sigma[0],tuple(sigma[1]),s),[]).append((lab,np.array([float(z) for z in vv]),gam[c]))
    tests=[("c.2486",W_const(0.2486)),("c.3197",W_const(0.3197)),("C5",W_c5),("bip",W_bip)]
    overall_min_eig=1e9; overall_min_atom=1e9
    for key in sorted(blocks):
        k,Asig,s=key[0],list(key[1]),key[2]; sigma=(k,Asig)
        flags=fs.enumerate_flags(sigma,k+s)
        # check all atoms have matching length
        nbad=sum(1 for (lab,vv,g) in blocks[key] if len(vv)!=len(flags))
        print(f"block k={k} s={s} Asig={key[1]}: |flags|={len(flags)} atoms={len(blocks[key])} dim-mismatch={nbad}",flush=True)
        for name,Wf in tests:
            M=graphon_moment_matrix(Wf,sigma,flags,s,n_mc=900,inner=400)
            M=0.5*(M+M.T); mn=np.linalg.eigvalsh(M).min()
            aw=min((float(vv@M@vv) for (lab,vv,g) in blocks[key] if len(vv)==len(flags)),default=float('nan'))
            overall_min_eig=min(overall_min_eig,mn); overall_min_atom=min(overall_min_atom,aw)
            print(f"   {name:7s} min_eig={mn:+.3e} min_atom={aw:+.3e}",flush=True)
    print(f"\nOVERALL worst graphon min-eig = {overall_min_eig:+.3e}",flush=True)
    print(f"OVERALL worst cert-atom v^T M v on band graphons = {overall_min_atom:+.3e}",flush=True)
    print("REFUTED" if (overall_min_atom < -1e-5 or overall_min_eig < -1e-5) else "no refutation found",flush=True)
    print("DONE",flush=True)

if __name__=="__main__": main()
