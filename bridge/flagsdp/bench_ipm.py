import pickle, numpy as np, time
from scipy.sparse import csr_matrix, vstack
from scipy.optimize import linprog
LO,HI=0.2486,0.3197
ns,dedge,rows,provtypes,_=pickle.load(open("cp_cache.pkl","rb"))
d=np.load("c5lift_cache.npz",allow_pickle=True)
D=csr_matrix((d["Dval"],(d["Drow"],d["Dcol"])),shape=(ns,int(d["nJ"]))); nJ=D.shape[1]; DT=D.T.tocsr()
n7=107; nR=410; nv=nJ+1+n7+nR; ETA=nJ; U7=nJ+1; U8=nJ+1+n7
mom_idx=[i for i in range(len(rows)) if (provtypes[i][0] if isinstance(provtypes[i],(list,tuple)) else provtypes[i])=='moment']
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
st=pickle.load(open("envelope_order10_state.pkl","rb"))
env=[csr_matrix((np.asarray(dat),(np.zeros(len(dat),int),np.asarray(idx))),shape=(1,nv)) for (dat,idx) in st["env"]]
A_ub=vstack(static+env,format="csr"); b_ub=np.concatenate([sb,np.zeros(len(env))])
Aeq=sprow({j:sum_q[j] for j in range(nJ) if sum_q[j]}); beq=np.array([1.0])
c=np.zeros(nv); c[ETA]=-1.0; bnds=[(0,None)]*nJ+[(None,None)]+[(0,None)]*(n7+nR)
print(f"LP {A_ub.shape[0]}x{nv} nnz={A_ub.nnz}; scipy-ds=662s eta=8.6668e-4",flush=True)
t0=time.time(); r=linprog(c,A_ub=A_ub,b_ub=b_ub,A_eq=Aeq,b_eq=beq,bounds=bnds,method="highs-ipm")
print(f"highs-ipm: {time.time()-t0:.0f}s success={r.success} eta={-r.fun if r.success else 'fail'}",flush=True)
print("DONE",flush=True)
