#!/usr/bin/env python3
"""Potential game-changer: CLARABEL (Rust conic IPM, robust+fast) on the it17 pool where HiGHS IPM hit 7324s and
dual-simplex >30min. If CLARABEL solves in minutes AND matches eta=2.22e-4, the cutting-plane is revived ->
can reach closure. Clarabel form: min q'x s.t. Ax+s=b, s in K. LP: A=[A_ub; A_eq; -I_bounded], cones=[NN,Zero,NN]."""
import os
os.environ.setdefault("OMP_NUM_THREADS","48"); os.environ.setdefault("OPENBLAS_NUM_THREADS","48")
import numpy as np, pickle, time
import clarabel
from scipy import sparse
from scipy.sparse import csr_matrix, vstack, csc_matrix
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
ub=[]; ubb=[]
ub.append(sprow({j:dedge_q[j] for j in range(nJ) if dedge_q[j]})); ubb.append(HI)
ub.append(sprow({j:-dedge_q[j] for j in range(nJ) if dedge_q[j]})); ubb.append(-LO)
for vq in mom_q: ub.append(sprow({j:-vq[j] for j in range(nJ) if vq[j]})); ubb.append(0.0)
ub.append(sprow({ETA:1.0,**{U7+i:-1.0 for i in range(n7)}})); ubb.append(0.0)
ub.append(sprow({ETA:1.0,**{U8+i:-1.0 for i in range(nR)}})); ubb.append(-2.0/25.0)
st=pickle.load(open("envelope_horn_state.pkl","rb"))
for (dat,idx) in st["env"]:
    ub.append(csr_matrix((np.asarray(dat),(np.zeros(len(dat),int),np.asarray(idx))),shape=(1,nv))); ubb.append(0.0)
A_ub=vstack(ub,format="csr"); b_ub=np.asarray(ubb,float); m_ub=A_ub.shape[0]
A_eq=sprow({j:sum_q[j] for j in range(nJ) if sum_q[j]}); b_eq=np.array([1.0]); m_eq=1
# x>=0 for bounded indices (all except ETA): rows -e_i, b=0
bnd=[i for i in range(nv) if i!=ETA]
rowi=np.arange(len(bnd)); B=csr_matrix((-np.ones(len(bnd)),(rowi,np.asarray(bnd))),shape=(len(bnd),nv))
A=vstack([A_ub,A_eq,B],format="csc")
b=np.concatenate([b_ub,b_eq,np.zeros(len(bnd))])
q=np.zeros(nv); q[ETA]=-1.0  # minimize -eta
P=csc_matrix((nv,nv))
cones=[clarabel.NonnegativeConeT(m_ub), clarabel.ZeroConeT(m_eq), clarabel.NonnegativeConeT(len(bnd))]
print(f"LP {A.shape[0]}x{nv} nnz={A.nnz}; CLARABEL on it17 pool ({len(st['env'])} cuts)...",flush=True)
settings=clarabel.DefaultSettings(); settings.max_iter=200; settings.verbose=True
t0=time.time()
solver=clarabel.DefaultSolver(P,q,A,b,cones,settings)
sol=solver.solve()
dt=time.time()-t0
eta=-sol.obj_val
print(f"CLARABEL: {dt:.0f}s status={sol.status} eta={eta:+.7e} (saved it17 eta=2.2192e-4)",flush=True)
print("DONE",flush=True)
