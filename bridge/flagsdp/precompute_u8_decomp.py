#!/usr/bin/env python3
"""Precompute the per-state 8-anchor decomposition for the U_8 per-R envelope LP (GPT's u_R closure).
For each order-10 triangle-free state J and each ORDERED edge (i,j) with A[i][j]=1: anchors = other 8 vertices,
R = canon(J[anchors]) (8-vertex), Aset/Bset = profiles of i,j in canonical anchor coords. We store, per J, the
list of (Rid, Aset, Bset). Then for ANY q: w_R(A,B)=sum_J q_J*count_{J,R,A,B}/90 (per-R MaxCut = sigma*_R), and
for ANY per-R coloring c the linear row L_{R,c}(q) has coeff_{R,c}(J)=(1/90) sum_{(i,j)->R} 1{c(Aset)=c(Bset)}.
Memoize canon_label by Radj bitmask (few thousand distinct 8-graphs). One-time; cache to u8_decomp.pkl.
"""
import numpy as np, pickle, time, sys
import flag_engine as fe
from compute_U8 import canon_label

def main():
    g10=fe.enumerate_graphs(10,triangle_free=True); nJ=len(g10)
    print(f"nJ={nJ}; building decomposition (memoized canon)...",flush=True)
    memo={}
    Rkeys={}            # canonical R tuple -> Rid
    Rprofiles={}        # Rid -> set of profile tuples
    decomp=[None]*nJ    # per J: list of (Rid, Aset_tuple, Bset_tuple)
    t0=time.time(); ncanon=0
    for jj in range(nJ):
        n,A=g10[jj]; lst=[]
        for i in range(10):
            Ai=A[i]
            for je in range(10):
                if i!=je and (Ai>>je)&1:
                    anchors=[v for v in range(10) if v!=i and v!=je]
                    m,Radj=fe.induced(A,anchors)
                    rk=tuple(Radj)
                    mm=memo.get(rk)
                    if mm is None:
                        key,inv=canon_label(8,Radj); ncanon+=1
                        rid=Rkeys.get(key)
                        if rid is None:
                            rid=len(Rkeys); Rkeys[key]=rid; Rprofiles[rid]=set()
                        mm=(rid,inv); memo[rk]=mm
                    rid,inv=mm
                    # anchors[p] is the original vertex at canonical position inv[p]
                    Aset=tuple(sorted(inv[p] for p,v in enumerate(anchors) if (Ai>>v)&1))
                    Bset=tuple(sorted(inv[p] for p,v in enumerate(anchors) if (A[je]>>v)&1))
                    Rprofiles[rid].add(Aset); Rprofiles[rid].add(Bset)
                    lst.append((rid,Aset,Bset))
        decomp[jj]=lst
        if jj%2000==0: print(f"  J={jj}/{nJ} [{time.time()-t0:.0f}s] nR={len(Rkeys)} ncanon={ncanon}",flush=True)
    nR=len(Rkeys)
    print(f"DONE decomp: nR={nR}, total canon calls={ncanon}, [{time.time()-t0:.0f}s]",flush=True)
    pickle.dump(dict(nJ=nJ,nR=nR,decomp=decomp,
                     Rprofiles={k:[list(p) for p in v] for k,v in Rprofiles.items()}),
                open("u8_decomp.pkl","wb"),protocol=4)
    sz=sum(len(l) for l in decomp)
    print(f"saved u8_decomp.pkl ; total edge-contribs={sz} (avg {sz/nJ:.1f}/state)",flush=True)

if __name__=="__main__": main()
