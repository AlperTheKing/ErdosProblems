#!/usr/bin/env python3
"""GPT's first concrete step: compute h_min = min_{R, 5-tuple} H_R/Pr(R), the rooted Horn (C5) inequality.
H_R(A_0..A_4) = sum_{i,j} P_R(A_i,A_j) - 4 sum_i P_R(A_i,A_{i+1}) (mod 5).  Real graphon: H_R>=0 (Motzkin-Straus/CP).
A pseudo-state can violate it. Candidates from high-weight 5-cycles in the profile edge matrix w_R (=off-diag P_R).
Test on the order-10 witness q. If h_min<0 => Horn is the new sound cut beyond PSD (CP-cone, DNN-vs-CP gap)."""
import numpy as np, pickle, itertools, time
Da=pickle.load(open("u8_decomp_all.pkl","rb")); decomp=Da["decomp"]; nR=Da["nR"]; Rprof=Da["Rprofiles"]
q=np.load("witness.npz",allow_pickle=True)["q"]

def build_PR(q):
    acc=[dict() for _ in range(nR)]; pr=np.zeros(nR); sup=np.where(q>1e-13)[0]
    for jj in sup:
        qj=float(q[jj])
        for (rid,A,B) in decomp[jj]:
            acc[rid][(A,B)]=acc[rid].get((A,B),0.0)+qj/90.0; pr[rid]+=qj/90.0
    out=[]
    for rid in range(nR):
        if not acc[rid]: continue
        profs=sorted(set(tuple(p) for p in Rprof[rid])|set(a for (a,b) in acc[rid])|set(b for (a,b) in acc[rid]))
        idx={p:i for i,p in enumerate(profs)}; m=len(profs); P=np.zeros((m,m))
        for (A,B),w in acc[rid].items(): P[idx[A],idx[B]]+=w
        P=0.5*(P+P.T)
        out.append((rid,profs,P,pr[rid]))
    return out

def horn_min_for_R(P, MAXP=14):
    """min over 5-cycles (distinct profiles, cyclic) of H = sum_{i,j}P[a_i,a_j] - 4 sum_i P[a_i,a_{i+1}].
    Restrict to the top-MAXP profiles by total off-diagonal weight (candidates carry the frustrated mass)."""
    m=P.shape[0]
    if m<5: return 0.0,None
    deg=(P.sum(1)-np.diag(P))
    top=list(np.argsort(deg)[::-1][:min(MAXP,m)])
    best=0.0; bestt=None
    for sub in itertools.combinations(top,5):
        s=list(sub)
        Psub=P[np.ix_(s,s)]; tot=Psub.sum()
        # best cyclic order = max cycle-edge sum over the 12 distinct 5-cycles on these 5 nodes
        for perm in itertools.permutations(s[1:]):
            cyc=[s[0]]+list(perm)
            cycsum=sum(P[cyc[i],cyc[(i+1)%5]] for i in range(5))
            H=tot-4*cycsum
            if H<best: best=H; bestt=cyc
    return best,bestt

def main():
    t0=time.time(); PRs=build_PR(q)
    worst=0.0; worstR=-1; nneg=0
    for (rid,profs,P,pr) in PRs:
        h,tt=horn_min_for_R(P)
        lh=h/pr if pr>1e-13 else 0.0
        if lh<worst: worst=lh; worstR=rid
        if h<-1e-9: nneg+=1
    print(f"WITNESS q: roots active={len(PRs)}  min_R h_R/Pr(R) = {worst:+.4e} (rid {worstR})  #roots with Horn<0: {nneg}  [{time.time()-t0:.0f}s]",flush=True)
    print(f"  => Horn (C5) inequality {'IS VIOLATED' if worst<-1e-9 else 'NOT violated'} on the witness pseudo-state.",flush=True)
    print("DONE",flush=True)
if __name__=="__main__": main()
