#!/usr/bin/env python3
"""HORN envelope with WARM-STARTED dual-simplex (highspy persistent model). Cutting-plane re-optimizes
INCREMENTALLY each round (addRows + warm-start) instead of scipy re-solving from scratch -> pool size becomes
irrelevant (the IPM-on-big-pool blowup that crippled order-10g/envelope_horn is gone). No pruning needed.
Resumes env from envelope_horn_state.pkl. k7+k8+rooted-Horn CP cuts. max eta; eta<=0 => band closed."""
import os
os.environ.setdefault("OMP_NUM_THREADS","32"); os.environ.setdefault("OPENBLAS_NUM_THREADS","32"); os.environ.setdefault("MKL_NUM_THREADS","32")
import numpy as np, pickle, time, itertools
import highspy
from scipy.sparse import csr_matrix, vstack
from joblib import Parallel, delayed
import flag_cutgen as fc
from run_k7b import sep_multi, precompute_k7
from cutting_plane_u8 import maxcut_coloring
LO,HI=0.2486,0.3197; INF=highspy.kHighsInf

def horn_tuples_for_R(P, MAXP=12, KEEP=2):
    m=P.shape[0]
    if m<5: return []
    deg=P.sum(1)-np.diag(P); top=list(np.argsort(deg)[::-1][:min(MAXP,m)]); found=[]
    for sub in itertools.combinations(top,5):
        s=list(sub); tot=P[np.ix_(s,s)].sum(); best=None; bestc=None
        for perm in itertools.permutations(s[1:]):
            cyc=[s[0]]+list(perm); cs=sum(P[cyc[i],cyc[(i+1)%5]] for i in range(5)); H=tot-4*cs
            if best is None or H<best: best=H; bestc=cyc
        if best<-1e-12: found.append((best,bestc))
    found.sort(key=lambda z:z[0]); return found[:KEEP]

def run(maxit=120, tol=1e-9, keep=2, resume=True):
    ns,dedge,rows,provtypes,_=pickle.load(open("cp_cache.pkl","rb"))
    C=pickle.load(open("cache_n9.pkl","rb")); states=C["states"]; t=C["t"]
    d=np.load("c5lift_cache.npz",allow_pickle=True)
    D=csr_matrix((d["Dval"],(d["Drow"],d["Dcol"])),shape=(ns,int(d["nJ"]))); nJ=D.shape[1]; DT=D.T.tocsr()
    De=pickle.load(open("u8_decomp.pkl","rb"));    dec_e=De["decomp"]; nR=De["nR"]
    Da=pickle.load(open("u8_decomp_all.pkl","rb")); dec_a=Da["decomp"]; Rprof=Da["Rprofiles"]
    q0=np.load("witness.npz",allow_pickle=True)["q"]
    dt7=precompute_k7(states); n7=len(dt7)
    mom_idx=[i for i in range(len(rows)) if (provtypes[i][0] if isinstance(provtypes[i],(list,tuple)) else provtypes[i])=='moment']
    nv=nJ+1+n7+nR; ETA=nJ; U7=nJ+1; U8=nJ+1+n7
    dedge_q=np.asarray(DT@dedge).ravel(); sum_q=np.asarray(D.sum(axis=0)).ravel()
    mom_q=[np.asarray(DT@np.asarray(rows[i])).ravel() for i in mom_idx]
    print(f"ns={ns} nJ={nJ} n7={n7} nR={nR} MOMENT={len(mom_idx)}; WARM-START dual simplex; keep={keep}",flush=True)
    def sprow(dd):
        cols=np.fromiter(dd.keys(),int,len(dd)); data=np.fromiter(dd.values(),float,len(dd))
        return csr_matrix((data,(np.zeros(len(cols),int),cols)),shape=(1,nv))
    # ---- build static rows (row-wise) + their bounds ----
    srows=[]; rlo=[]; rup=[]
    srows.append(sprow({j:dedge_q[j] for j in range(nJ) if dedge_q[j]})); rlo.append(-INF); rup.append(HI)
    srows.append(sprow({j:-dedge_q[j] for j in range(nJ) if dedge_q[j]})); rlo.append(-INF); rup.append(-LO)
    for vq in mom_q: srows.append(sprow({j:-vq[j] for j in range(nJ) if vq[j]})); rlo.append(-INF); rup.append(0.0)
    srows.append(sprow({ETA:1.0,**{U7+i:-1.0 for i in range(n7)}})); rlo.append(-INF); rup.append(0.0)
    srows.append(sprow({ETA:1.0,**{U8+i:-1.0 for i in range(nR)}})); rlo.append(-INF); rup.append(-2.0/25.0)
    srows.append(sprow({j:sum_q[j] for j in range(nJ) if sum_q[j]})); rlo.append(1.0); rup.append(1.0)  # equality
    # ---- resume env ----
    env_rows=[]
    if resume and os.path.exists("envelope_horn_state.pkl"):
        st=pickle.load(open("envelope_horn_state.pkl","rb"))
        for (dat,idx) in st["env"]:
            env_rows.append(csr_matrix((np.asarray(dat),(np.zeros(len(dat),int),np.asarray(idx))),shape=(1,nv)))
        print(f"RESUMED {len(env_rows)} env cuts (it{st.get('it')} eta={st.get('eta'):+.4e})",flush=True)
    # ---- highspy model ----
    h=highspy.Highs()
    h.setOptionValue("output_flag",False); h.setOptionValue("solver","simplex")
    h.setOptionValue("simplex_strategy",1)  # dual
    h.setOptionValue("threads",16)
    h.addVars(nv, np.array([0.0]*nJ+[-INF]+[0.0]*(n7+nR)), np.array([INF]*nv))
    cost=np.zeros(nv); cost[ETA]=-1.0
    h.changeColsCost(nv, np.arange(nv,dtype=np.int32), cost)
    all_env=list(env_rows)  # track env cuts (beyond static) for resumable state-saving
    def add_rows(rlist, lo, up):
        if not rlist: return
        E=vstack(rlist,format="csr")
        h.addRows(E.shape[0], np.asarray(lo,float), np.asarray(up,float),
                  E.nnz, E.indptr[:-1].astype(np.int32), E.indices.astype(np.int32), E.data.astype(float))
    add_rows(srows, rlo, rup)
    add_rows(env_rows, [-INF]*len(env_rows), [0.0]*len(env_rows))
    nenv=len(env_rows)
    def solve():
        h.run()
        sol=h.getSolution(); z=np.asarray(sol.col_value)
        eta=-h.getInfo().objective_function_value
        return eta, z[:nJ], z[U7:U7+n7], z[U8:U8+nR]
    def sep_k7(x,q,u7):
        def one(i,E,S):
            ps,gs=sep_multi(E,S,x,t,1e9,tol,keep=1); res=[]
            for p in ps:
                g=fc.cut_from_p(E,S,p,t); gq=np.asarray(DT@np.asarray(g)).ravel()
                if u7 is not None and u7[i]>float(gq@q)+tol: res.append(gq)
            return i,res
        out=Parallel(n_jobs=40,prefer="threads")(delayed(one)(i,E,S) for i,(k,A,E,S,cls) in enumerate(dt7))
        new=[]
        for (i,res) in out:
            for gq in res: new.append(sprow({U7+i:1.0,**{int(j):-float(gq[j]) for j in np.nonzero(gq)[0]}}))
        return new
    def sep_k8(q,u8):
        W=[dict() for _ in range(nR)]; sup=np.where(q>1e-12)[0]
        for jj in sup:
            qj=float(q[jj])
            for (rid,A,B) in dec_e[jj]:
                key=(A,B) if (len(A),A)<=(len(B),B) else (B,A); W[rid][key]=W[rid].get(key,0.0)+qj/90.0
        cm={}
        for rid in range(nR):
            if not W[rid]: continue
            profs=set(); off={}
            for (a,b),w in W[rid].items():
                profs.add(a); profs.add(b)
                if a!=b: off[(a,b)]=off.get((a,b),0.0)+w
            cm[rid]=maxcut_coloring(list(profs),off)
        acc={rid:{} for rid in cm}
        for jj in range(nJ):
            for (rd,A,B) in dec_e[jj]:
                if rd in cm and cm[rd].get(A,0)==cm[rd].get(B,0): a=acc[rd]; a[jj]=a.get(jj,0)+1
        new=[]
        for rid,a in acc.items():
            js=np.fromiter(a.keys(),int,len(a)); cs=np.fromiter(a.values(),float,len(a))/90.0
            L=float(cs@q[js]) if len(js) else 0.0
            if u8 is not None and u8[rid]>L+tol:
                new.append(sprow({U8+rid:1.0,**{int(jj):-float(c) for jj,c in zip(js,cs)}}))
        return new
    def build_PR(q):
        acc=[dict() for _ in range(nR)]; sup=np.where(q>1e-13)[0]
        for jj in sup:
            qj=float(q[jj])
            for (rid,A,B) in dec_a[jj]: acc[rid][(A,B)]=acc[rid].get((A,B),0.0)+qj/90.0
        out=[]
        for rid in range(nR):
            if not acc[rid]: continue
            profs=sorted(set(tuple(p) for p in Rprof[rid])|set(a for (a,b) in acc[rid])|set(b for (a,b) in acc[rid]))
            idx={p:i for i,p in enumerate(profs)}; m=len(profs); P=np.zeros((m,m))
            for (A,B),w in acc[rid].items(): P[idx[A],idx[B]]+=w
            P=0.5*(P+P.T); out.append((rid,profs,P,float(P.sum())))
        return out
    def sep_horn(q):
        PRs=build_PR(q)
        def one(rid,profs,P,pr):
            ev=np.linalg.eigvalsh(P); lh=ev[0]/pr if pr>1e-13 else 0.0
            tups=horn_tuples_for_R(P,KEEP=keep); cms=[]
            for (Hval,s) in tups:
                Hmat={}
                for a in s:
                    for b in s: Hmat[(a,b)]=Hmat.get((a,b),0.0)+1.0
                for i in range(5):
                    a,b=s[i],s[(i+1)%5]; Hmat[(a,b)]=Hmat.get((a,b),0.0)-4.0
                cms.append({(profs[a],profs[b]):c for (a,b),c in Hmat.items() if abs(c)>1e-12})
            return rid,lh,cms
        res=Parallel(n_jobs=40,prefer="threads")(delayed(one)(rid,profs,P,pr) for (rid,profs,P,pr) in PRs)
        worst=0.0; cutM={}
        for rid,lh,cms in res:
            if lh<worst: worst=lh
            if cms: cutM[rid]=cms
        if not cutM: return [],worst
        coeffs={(rid,k):dict() for rid,cms in cutM.items() for k in range(len(cms))}
        for jj in range(nJ):
            for (rd,A,B) in dec_a[jj]:
                cms=cutM.get(rd)
                if cms is None: continue
                for k,Md in enumerate(cms):
                    v=Md.get((A,B))
                    if v is not None:
                        co=coeffs[(rd,k)]; co[jj]=co.get(jj,0.0)+v
        new=[sprow({int(jj):-vv/90.0 for jj,vv in co.items()}) for key,co in coeffs.items() if co]
        return new,worst
    eta,q,u7,u8=solve(); print(f"resume-solve(warm): eta={eta:+.7e} pool={nenv}",flush=True)
    for it in range(11,11+maxit):
        ts=time.time()
        qs=q.copy()
        if (q>1e-12).sum()>800:
            order=np.argsort(q)[::-1]; cms=np.cumsum(q[order])
            kkeep=int(np.searchsorted(cms, 1.0-1e-4))+1; thrq=q[order[min(kkeep,nJ-1)]]
            qs=np.where(q>=thrq, q, 0.0); s=qs.sum(); qs=qs/s if s>0 else qs
        x=np.asarray(D@qs).ravel()
        n7c=sep_k7(x,qs,u7); n8c=sep_k8(qs,u8); nhc,worst=sep_horn(qs)
        allnew=n7c+n8c+nhc
        if not allnew: print(f"CONVERGED it{it}: eta={eta:+.7e} minLh={worst:+.2e}",flush=True); break
        add_rows(allnew,[-INF]*len(allnew),[0.0]*len(allnew)); nenv+=len(allnew); all_env.extend(allnew)
        eta,q,u7,u8=solve()
        nn=thr(eta)
        print(f"it{it}: +{len(n7c)}k7 +{len(n8c)}k8 +{len(nhc)}horn (pool {nenv}) eta={eta:+.7e} n<={nn} minLh={worst:+.2e} [{time.time()-ts:.0f}s]",flush=True)
        if it%2==0:
            pickle.dump(dict(env=[(e.data.tolist(),e.indices.tolist()) for e in all_env],eta=float(eta),it=it,nv=nv),
                        open("envelope_horn_state.pkl","wb"),protocol=4)
        if eta<=tol:
            pickle.dump(dict(env=[(e.data.tolist(),e.indices.tolist()) for e in all_env],eta=float(eta),it=it,nv=nv),
                        open("envelope_horn_state.pkl","wb"),protocol=4)
            print(f">>> eta<=0 -> CANDIDATE band CLOSURE (k7+k8+HORN warm).",flush=True); break
    print(f"FINAL horn-hs eta={eta:+.7e} (closed iff<=0; N<=180 iff<6.17e-5; n<={thr(eta)})",flush=True)
    return eta

def thr(e):
    import math
    return int(math.floor(math.sqrt(2.0/(25*e)))) if e>0 else 999

if __name__=="__main__":
    print("=== HORN envelope, WARM-STARTED dual simplex (highspy) ===",flush=True)
    run(); print("DONE",flush=True)
