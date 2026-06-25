#!/usr/bin/env python3
"""GPT path (A): ALL-PAIRS 8-anchor decomposition for the (8,9) conditional-profile Gram PSD constraint.
For each order-10 triangle-free state J and EVERY ordered pair (i,j), i!=j (edge AND non-edge): anchors = other 8,
R = canon(J[anchors]), A=prof(i), B=prof(j) (anchor-adjacency sets; independent in R since J triangle-free).
P_R(A,B;q) = sum_J q_J * count_{J,R,A,B} / 90 = Pr_q(R, prof9=A, prof10=B) summing the 9,10 in E and not-in-E cases.
For a real graphon P_R = E_z[1_R p(z)p(z)^T] is PSD (cond. i.i.d. profile draws); a pseudo-state can violate it.
Cache u8_decomp_all.pkl : per J list of (Rid, A_tuple, B_tuple) over all 90 ordered pairs; + Rprofiles, Rid map.
"""
import numpy as np, pickle, time
import flag_engine as fe
from compute_U8 import canon_label

def main():
    g10=fe.enumerate_graphs(10,triangle_free=True); nJ=len(g10)
    print(f"nJ={nJ}; all-pairs decomposition (memoized canon)...",flush=True)
    memo={}; Rkeys={}; Rprofiles={}; decomp=[None]*nJ
    t0=time.time(); ncanon=0
    for jj in range(nJ):
        n,A=g10[jj]; lst=[]
        for i in range(10):
            Ai=A[i]
            for je in range(10):
                if i==je: continue
                anchors=[v for v in range(10) if v!=i and v!=je]
                m,Radj=fe.induced(A,anchors); rk=tuple(Radj)
                mm=memo.get(rk)
                if mm is None:
                    key,inv=canon_label(8,Radj); ncanon+=1
                    rid=Rkeys.get(key)
                    if rid is None: rid=len(Rkeys); Rkeys[key]=rid; Rprofiles[rid]=set()
                    mm=(rid,inv); memo[rk]=mm
                rid,inv=mm
                Aset=tuple(sorted(inv[p] for p,v in enumerate(anchors) if (Ai>>v)&1))
                Bset=tuple(sorted(inv[p] for p,v in enumerate(anchors) if (A[je]>>v)&1))
                Rprofiles[rid].add(Aset); Rprofiles[rid].add(Bset)
                lst.append((rid,Aset,Bset))
        decomp[jj]=lst
        if jj%2000==0: print(f"  J={jj}/{nJ} [{time.time()-t0:.0f}s] nR={len(Rkeys)}",flush=True)
    nR=len(Rkeys)
    pickle.dump(dict(nJ=nJ,nR=nR,decomp=decomp,
                     Rprofiles={k:[list(p) for p in v] for k,v in Rprofiles.items()}),
                open("u8_decomp_all.pkl","wb"),protocol=4)
    sz=sum(len(l) for l in decomp)
    print(f"DONE: nR={nR}, canon={ncanon}, contribs={sz} (avg {sz/nJ:.1f}/state), [{time.time()-t0:.0f}s]",flush=True)

if __name__=="__main__": main()
