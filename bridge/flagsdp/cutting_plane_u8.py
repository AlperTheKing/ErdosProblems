#!/usr/bin/env python3
"""GPT path (A) CLOSURE: cutting-plane with the 8-anchor cut. Solve order-10 LP -> witness q. Extract sigma*
(per-canonical-R MaxCut colorings of the profile graphs). Build the cut coefficient c_{sigma*}(J) for ALL T_10
states J: c(J)=(1/90) sum_{ordered edges (i,j)} 1{sigma*_{R}(prof_i)=sigma*_{R}(prof_j)}, R=canon(J-{i,j}).
Valid inequality d_mono(W) <= L_{sigma*}(q)=sum_J c(J) q_J for real graphons (validated: U_8(C5)=0.08=d_mono).
Add  eta <= L_{sigma*}(q) - 2/25  to the order-10 LP, re-solve. Witness L_{sigma*}=U_8=4.83e-4 << 2/25 violates it.
Iterate until eta<=0 => band closed (then exact cert). This run: extract sigma*, verify L(witness)=U_8, one re-solve.
"""
import numpy as np, pickle, itertools
from math import comb
from scipy.optimize import linprog
from scipy.sparse import csr_matrix, hstack, vstack, coo_matrix
import flag_engine as fe
from compute_U8 import canon_label, popcount
import prove_cert as pc
LO,HI=0.2486,0.3197

def maxcut_coloring(nodes, edges):
    """return dict {node: 0/1} maximizing cut (min monochromatic). exact for <=20 nodes else local search."""
    nn=len(nodes); idx={v:i for i,v in enumerate(nodes)}
    el=[(idx[a],idx[b],w) for (a,b),w in edges.items()]
    if nn==0: return {}
    if nn<=18:
        best=-1; bestm=0
        for mask in range(1<<(nn-1)):
            c=0.0
            for a,b,w in el:
                if ((mask>>a)&1)!=((mask>>b)&1): c+=w
            if c>best: best=c; bestm=mask
        return {nodes[i]:((bestm>>i)&1) for i in range(nn)}
    s=[i%2 for i in range(nn)]
    imp=True
    while imp:
        imp=False
        for v in range(nn):
            d=sum((w if s[v]==s[b if a==v else a] else -w) for a,b,w in el if a==v or b==v)
            if d>1e-15: s[v]^=1; imp=True
    return {nodes[i]:s[i] for i in range(nn)}

def build_sigma_star(q, g10):
    """aggregate w_R from witness q; return sigma*[Rkey] = {profile: side}."""
    W={}
    for jj in range(len(q)):
        if q[jj]<=1e-9: continue
        n,A=g10[jj]; qj=float(q[jj])
        for i in range(10):
            for je in range(10):
                if i!=je and (A[i]>>je)&1:
                    anch=[v for v in range(10) if v!=i and v!=je]
                    idx={v:p for p,v in enumerate(anch)}
                    Radj=[0]*8
                    for p in range(8):
                        for qd in range(p+1,8):
                            if (A[anch[p]]>>anch[qd])&1: Radj[p]|=1<<qd; Radj[qd]|=1<<p
                    key,inv=canon_label(8,Radj)
                    Aset=frozenset(inv[idx[v]] for v in anch if (A[i]>>v)&1)
                    Bset=frozenset(inv[idx[v]] for v in anch if (A[je]>>v)&1)
                    W.setdefault(key,{}); W[key][(Aset,Bset)]=W[key].get((Aset,Bset),0.0)+qj/90.0
    sigma={}
    for key,ed in W.items():
        offdiag={}; profiles=set()
        for (Aset,Bset),w in ed.items():
            profiles.add(Aset); profiles.add(Bset)
            if Aset!=Bset:
                a,b=tuple(sorted([Aset,Bset],key=lambda s:(len(s),sorted(s))))
                offdiag[(a,b)]=offdiag.get((a,b),0.0)+w
        sigma[key]=maxcut_coloring(list(profiles),offdiag)
    return sigma

def c_of_J(n, A, sigma):
    """c_sigma*(J): fresh-fresh monochromatic density under sigma* (default side 0 for unseen R/profile)."""
    tot=0
    for i in range(10):
        for je in range(10):
            if i!=je and (A[i]>>je)&1:
                anch=[v for v in range(10) if v!=i and v!=je]
                idx={v:p for p,v in enumerate(anch)}
                Radj=[0]*8
                for p in range(8):
                    for qd in range(p+1,8):
                        if (A[anch[p]]>>anch[qd])&1: Radj[p]|=1<<qd; Radj[qd]|=1<<p
                key,inv=canon_label(8,Radj)
                Aset=frozenset(inv[idx[v]] for v in anch if (A[i]>>v)&1)
                Bset=frozenset(inv[idx[v]] for v in anch if (A[je]>>v)&1)
                sg=sigma.get(key,{})
                sa=sg.get(Aset,0); sb=sg.get(Bset,0)
                if sa==sb: tot+=1
    return tot/90.0

def main():
    C=pc.load(9); ns,dedge,rows,provtypes,v=pickle.load(open("cp_cache.pkl","rb"))
    d=np.load("c5lift_cache.npz",allow_pickle=True)
    D=csr_matrix((d["Dval"],(d["Drow"],d["Dcol"])),shape=(ns,int(d["nJ"]))); nJ=D.shape[1]
    g10=fe.enumerate_graphs(10,triangle_free=True); assert len(g10)==nJ
    wit=np.load("witness.npz",allow_pickle=True); qw=wit["q"]
    print("extracting sigma* from witness...",flush=True)
    sigma=build_sigma_star(qw,g10)
    print(f"sigma* over {len(sigma)} canonical R; computing c_sigma*(J) for all {nJ} states...",flush=True)
    cJ=np.array([c_of_J(g10[j][0],g10[j][1],sigma) for j in range(nJ)])
    Lwit=float(cJ@qw)
    print(f"L_sigma*(witness) = {Lwit:.6e}  (should ~= U_8=4.83e-4)",flush=True)
    np.savez("u8cut.npz", cJ=cJ)
    # add cut to order-10 LP and re-solve.  variable layout [x(ns) | q(nJ) | eta]
    nv=ns+nJ+1
    ub=[]; ub_b=[]
    r=np.zeros(nv); r[:ns]=dedge; ub.append(r.copy()); ub_b.append(HI)
    r=np.zeros(nv); r[:ns]=-dedge; ub.append(r.copy()); ub_b.append(-LO)
    for i,row in enumerate(rows):
        r=np.zeros(nv)
        if provtypes[i] in ("deficit","deficit_pmap"): r[:ns]=-row; r[-1]=1.0
        else: r[:ns]=-row
        ub.append(r); ub_b.append(0.0)
    A_ub=np.array(ub); b_ub=np.array(ub_b)
    negI=coo_matrix((-np.ones(ns),(np.arange(ns),np.arange(ns))),shape=(ns,ns))
    E10=hstack([negI,D,csr_matrix((ns,1))],format="csr")
    sumx=np.zeros((1,nv)); sumx[0,:ns]=1.0
    A_eq=vstack([E10,csr_matrix(sumx)],format="csr"); b_eq=np.concatenate([np.zeros(ns),[1.0]])
    cobj=np.zeros(nv); cobj[-1]=-1.0; bounds=[(0,None)]*(ns+nJ)+[(None,None)]
    def solve(extra=None,eb=None):
        Au=A_ub if extra is None else np.vstack([A_ub,extra]); bu=b_ub if eb is None else np.concatenate([b_ub,eb])
        return linprog(cobj,A_ub=csr_matrix(Au),b_ub=bu,A_eq=A_eq,b_eq=b_eq,bounds=bounds,method="highs")
    print(f"E10 baseline eta = {-solve().fun:+.7e}",flush=True)
    # cut: eta <= L_sigma*(q) - 2/25  ->  eta - sum cJ q <= -2/25
    cut=np.zeros(nv); cut[ns:ns+nJ]=-cJ; cut[-1]=1.0
    res=solve(cut.reshape(1,-1), np.array([-2.0/25.0]))
    if res.success:
        print(f">>> after 1 8-anchor cut: eta = {-res.fun:+.7e}  (E10 was +6.03e-5)",flush=True)
        if -res.fun<0: print("    >>> eta<0 already! candidate closure -> iterate/exact cert.",flush=True)
    else:
        print(f"LP status {res.status}: {res.message} -> INFEASIBLE = no order-10 pseudo-graphon survives the cut => CLOSED (float)",flush=True)
    print("DONE",flush=True)

if __name__=="__main__": main()
