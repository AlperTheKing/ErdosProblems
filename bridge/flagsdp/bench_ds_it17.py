#!/usr/bin/env python3
"""Decisive solver test: is highs-ds (dual simplex, conditioning-immune) steady on the it17 pool where IPM
exploded to 7324s? If <~1500s the cutting-plane lives (switch solver); if also huge, it's dead -> pivot."""
import os
os.environ.setdefault("OMP_NUM_THREADS","32"); os.environ.setdefault("OPENBLAS_NUM_THREADS","32")
import numpy as np, pickle, time
from scipy.optimize import linprog
from scipy.sparse import csr_matrix, vstack
LO,HI=0.2486,0.3197
ns,dedge,rows,provtypes,_=pickle.load(open("cp_cache.pkl","rb"))
d=np.load("c5lift_cache.npz",allow_pickle=True)
D=csr_matrix((d["Dval"],(d["Drow"],d["Dcol"])),shape=(ns,int(d["nJ"]))); nJ=D.shape[1]; DT=D.T.tocsr()
De=pickle.load(open("u8_decomp.pkl","rb")); nR=De["nR"]
C=pickle.load(open("cache_n9.pkl","rb")); states=C["states"]
from run_k7b import precompute_k7
n7=len(precompute_k7(states))
mom_idx=[i for i in range(len(rows)) if (provtypes[i][0] if isinstance(provtypes[i],(list,tuple)) else provtypes[i])=='moment']
nv=nJ+1+n7+nR; ETA=nJ; U7=nJ+1; U8=nJ+1+n7
dedge_q=np.asarray(DT@dedge).ravel(); sum_q=np.asarray(D.sum(axis=0)).ravel()
mom_q=[np.asarray(DT@np.asarray(rows[i])).ravel() for i in mom_idx]
def sprow(dd):
    cols=np.fromiter(dd.keys(),int,len(dd)); data=np.fromiter(dd.values(),float,len(dd))
    return csr_matrix((data,(np.zeros(len(cols),int),cols)),shape=(1,nv))
static=[]; sb=[]
static.append(sprow({j:dedge_q[j] for j in range(nJ) if dedge_q[j]})); sb.append(HI)
static.append(sprow({j:-dedge_q[j] for j in range(nJ) if dedge_q[j]})); sb.append(-LO)
for vq in mom_q: static.append(sprow({j:-vq[j] for j in range(nJ) if vq[j]})); sb.append(0.0)
static.append(sprow({ETA:1.0,**{U7+i:-1.0 for i in range(n7)}})); sb.append(0.0)
static.append(sprow({ETA:1.0,**{U8+i:-1.0 for i in range(nR)}})); sb.append(-2.0/25.0)
Aeq=sprow({j:sum_q[j] for j in range(nJ) if sum_q[j]}); beq=[1.0]
cobj=np.zeros(nv); cobj[ETA]=-1.0
bounds=[(0,None)]*nJ+[(None,None)]+[(0,None)]*(n7+nR)
st=pickle.load(open("envelope_horn_state.pkl","rb"))
env=[csr_matrix((np.asarray(dat),(np.zeros(len(dat),int),np.asarray(idx))),shape=(1,nv)) for (dat,idx) in st["env"]]
A=vstack(static+env,format="csr"); b=np.concatenate([sb,np.zeros(len(env))])
print(f"LP {A.shape[0]}x{nv} nnz={A.nnz}; testing highs-ds on it17 pool ({len(env)} cuts)...",flush=True)
for meth in ["highs-ds"]:
    t0=time.time()
    rr=linprog(cobj,A_ub=A,b_ub=b,A_eq=Aeq,b_eq=beq,bounds=bounds,method=meth)
    dt=time.time()-t0
    eta=float(-rr.fun) if rr.success else None
    print(f"{meth}: {dt:.0f}s success={rr.success} eta={eta}",flush=True)
print("DONE",flush=True)
