#!/usr/bin/env python3
"""Benchmark LP solvers on the order-10 LP (it4 state): scipy-HiGHS(ds/ipm), highspy(threads), ortools-PDLP.
Pick the fastest for the cutting-plane (need eta + q to ~1e-7 for separation)."""
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
Aeq=sprow({j:sum_q[j] for j in range(nJ) if sum_q[j]}); beq=np.array([1.0])
c=np.zeros(nv); c[ETA]=-1.0
print(f"LP: {A_ub.shape[0]} ineq rows, 1 eq, {nv} vars, nnz={A_ub.nnz}",flush=True)

def report(name, t, eta):
    print(f"  {name:22s} {t:7.1f}s  eta={eta}",flush=True)

print("(scipy highs-ds known = 662.8s; skipping)",flush=True)

# highspy with threads
try:
    import highspy
    h=highspy.Highs(); h.setOptionValue("output_flag", False); h.setOptionValue("threads", 64)
    inf=highspy.kHighsInf
    # build via passModel: need col-wise. Use addVars + addRows.
    nrow=A_ub.shape[0]
    lp=highspy.HighsLp()
    lp.num_col_=nv; lp.num_row_=nrow+1
    lp.col_cost_=c.tolist()
    lp.col_lower_=([0.0]*nJ)+[-inf]+([0.0]*(n7+nR))
    lp.col_upper_=[inf]*nv
    # rows: A_ub x <= b_ub (lower -inf, upper b_ub); Aeq x = 1
    Afull=vstack([A_ub,Aeq],format="csc")
    lp.a_matrix_.format_=highspy.MatrixFormat.kColwise
    lp.a_matrix_.start_=Afull.indptr.tolist()
    lp.a_matrix_.index_=Afull.indices.tolist()
    lp.a_matrix_.value_=Afull.data.tolist()
    lp.row_lower_=([-inf]*nrow)+[1.0]
    lp.row_upper_=b_ub.tolist()+[1.0]
    lp.sense_=highspy.ObjSense.kMinimize
    for solver in ["choose","simplex","pdlp"]:
        h2=highspy.Highs(); h2.setOptionValue("output_flag", False); h2.setOptionValue("threads", 64); h2.setOptionValue("solver", solver)
        h2.passModel(lp)
        t0=time.time(); h2.run(); sol=h2.getSolution(); info=h2.getInfo()
        eta=-info.objective_function_value
        report(f"highspy {solver} (64t)", time.time()-t0, eta)
except Exception as e:
    print("  highspy FAILED:", repr(e)[:200],flush=True)

# ortools PDLP
try:
    from ortools.linear_solver import pywraplp
    solver=pywraplp.Solver.CreateSolver("PDLP")
    if solver:
        solver.SetNumThreads(64)
        xs=[solver.NumVar(0,solver.infinity(),f"x{i}") if i!=ETA else solver.NumVar(-solver.infinity(),solver.infinity(),"eta") for i in range(nv)]
        Acsr=A_ub.tocsr()
        for r_ in range(Acsr.shape[0]):
            s,e=Acsr.indptr[r_],Acsr.indptr[r_+1]
            ct=solver.Constraint(-solver.infinity(), float(b_ub[r_]))
            for k in range(s,e): ct.SetCoefficient(xs[Acsr.indices[k]], float(Acsr.data[k]))
        eqr=Aeq.tocsr(); ct=solver.Constraint(1.0,1.0)
        for k in range(eqr.indptr[0],eqr.indptr[1]): ct.SetCoefficient(xs[eqr.indices[k]], float(eqr.data[k]))
        obj=solver.Objective(); obj.SetCoefficient(xs[ETA],1.0); obj.SetMaximization()
        t0=time.time(); status=solver.Solve()
        report(f"ortools PDLP (64t) st={status}", time.time()-t0, xs[ETA].solution_value() if status in (0,1) else "fail")
except Exception as e:
    print("  ortools FAILED:", repr(e)[:200],flush=True)
print("DONE",flush=True)
