import pickle, numpy as np, time
from scipy.sparse import csr_matrix, vstack
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
sumq=sprow({j:sum_q[j] for j in range(nJ) if sum_q[j]})
Afull=vstack([A_ub, sumq],format="csc")
nrow=A_ub.shape[0]
inf_=1e30
print(f"LP {nrow+1}x{nv} nnz={Afull.nnz}; scipy-simplex=662s eta=8.6668e-4",flush=True)
import highspy
def run_pdlp(thr, gap):
    h=highspy.Highs(); h.setOptionValue("output_flag", False)
    h.setOptionValue("solver","pdlp"); h.setOptionValue("threads",thr)
    h.setOptionValue("pdlp_d_gap_tol", gap)
    lp=highspy.HighsLp(); lp.num_col_=nv; lp.num_row_=nrow+1
    c=np.zeros(nv); c[ETA]=-1.0
    lp.col_cost_=c.tolist()
    lp.col_lower_=([0.0]*nJ)+[-inf_]+([0.0]*(n7+nR))
    lp.col_upper_=[inf_]*nv
    lp.a_matrix_.format_=highspy.MatrixFormat.kColwise
    lp.a_matrix_.start_=Afull.indptr.astype(np.int32).tolist()
    lp.a_matrix_.index_=Afull.indices.astype(np.int32).tolist()
    lp.a_matrix_.value_=Afull.data.tolist()
    lp.row_lower_=([-inf_]*nrow)+[1.0]
    lp.row_upper_=b_ub.tolist()+[1.0]
    lp.sense_=highspy.ObjSense.kMinimize
    t0=time.time(); h.passModel(lp); tb=time.time()-t0
    t0=time.time(); h.run(); ts=time.time()-t0
    info=h.getInfo(); eta=-info.objective_function_value
    st_=h.getModelStatus()
    print(f"highspy PDLP {thr}t gap={gap}: build={tb:.0f}s solve={ts:.0f}s eta={eta:.7e} status={h.modelStatusToString(st_)}",flush=True)
run_pdlp(64, 1e-8)
print("DONE",flush=True)
