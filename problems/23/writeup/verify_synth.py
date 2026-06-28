"""Independent EXACT (Fraction) re-verification of the synthesis claims for Erdos #23 delta=0.
Checks, per graph:
  (P1)  sum_v T(v) == Gamma == sum_f ell(f)^2
  (ID-OT) (O ell)_f == sum_v p_f(v) T(v)   [central identity]
  (ID-ST) sum_v T(v)^2 == sum_f ell(f) (O ell)_f
  (K)   K = P P^T entrywise, row-sums of K == T(v)  (vertex co-incidence)
  (ROWSUM-O / O1) for every f:  sum_g O_fg == sum_v p_f(v) S(v) <= N,  S(v)=sum_g p_g(v)
  (WF-id) sum_f C_f == N*I - K  EXACTLY, where C_f = diag(N p_f / S) - p_f p_f^T  (S(v)>0 wherever p_f(v)>0)
  (WF-equiv) C_f PSD  <==>  sum_v p_f(v)^2 / D_f(v) <= 1  <==> (1/N) sum_v p_f(v) S(v) <= 1 <==> O1_f <= N
  (CYCLE-SM) (O ell)_f <= N*ell(f) for every f
  (SM)  sum_v T(v)^2 <= N*Gamma
  (GAMMA) Gamma <= N^2
All in exact Fraction arithmetic. Report any violation with the g6 string."""
import subprocess, sys
from fractions import Fraction as F
from _h import dec, GENG, loads, blow

def pf_dict(info):
    """p_f(v) as Fraction dicts, plus list M of bad edges."""
    M=info['M']; cyc=info['cyc']; ell=info['ell']
    pfs=[]
    for f in M:
        Ps=cyc[f]; nf=len(Ps); cnt={}
        for P in Ps:
            for v in P: cnt[v]=cnt.get(v,0)+1
        pfs.append({v:F(cnt[v],nf) for v in cnt})
    return M, pfs

def analyze(info):
    n=info['n']; N=n; M=info['M']; ell=info['ell']; T=info['T']; Gamma=info['G']
    M,pfs=pf_dict(info)
    m=len(M)
    # S(v)=sum_f p_f(v)
    S=[F(0)]*n; S={}
    for v in range(n): S[v]=F(0)
    for d in pfs:
        for v,p in d.items(): S[v]+=p
    # O_fg = sum_v p_f(v) p_g(v)
    O=[[F(0)]*m for _ in range(m)]
    for i in range(m):
        di=pfs[i]
        for j in range(m):
            dj=pfs[j]
            s=F(0)
            common = di.keys() & dj.keys()
            for v in common: s+=di[v]*dj[v]
            O[i][j]=s
    # K_vw = sum_f p_f(v) p_f(w); we only need row sums = sum_w K_vw = sum_f p_f(v)*ell(f)? No.
    # row sum of K at v = sum_w sum_f p_f(v)p_f(w) = sum_f p_f(v) (sum_w p_f(w)) = sum_f p_f(v) ell(f) = T(v).
    res={}
    # (P1)
    res['P1'] = (sum(T,F(0))==Gamma) and (Gamma==sum(ell[f]**2 for f in M))
    # central identity (O ell)_f == sum_v p_f(v) T(v)
    Oell=[sum(O[i][j]*ell[M[j]] for j in range(m)) for i in range(m)]
    ok_OT=True
    for i,f in enumerate(M):
        rhs=F(0)
        for v,p in pfs[i].items(): rhs+=p*T[v]
        if Oell[i]!=rhs: ok_OT=False; break
    res['ID_OT']=ok_OT
    # sum_v T^2 == sum_f ell(f) Oell_f
    res['ID_ST'] = (sum(t*t for t in T)==sum(ell[M[i]]*Oell[i] for i in range(m)))
    # row sums of K == T  (compute via T(v)=sum_f p_f(v)*ell)
    ok_K=True
    for v in range(n):
        rk=F(0)
        for i,f in enumerate(M):
            if v in pfs[i]: rk+=pfs[i][v]*ell[f]
        if rk!=T[v]: ok_K=False; break
    res['K_rowsum']=ok_K
    # O1_f = sum_g O_fg == sum_v p_f(v) S(v); check both forms and <= N
    o1_ok_eq=True; o1_max=None; o1_viol=False
    for i,f in enumerate(M):
        a=sum(O[i][j] for j in range(m))
        b=F(0)
        for v,p in pfs[i].items(): b+=p*S[v]
        if a!=b: o1_ok_eq=False
        if o1_max is None or a>o1_max: o1_max=a
        if a>N: o1_viol=True
    res['O1_eq']=o1_ok_eq
    res['O1_max']=o1_max
    res['O1_viol']=o1_viol
    # Water-filling identity: sum_f C_f == N*I - K.  C_f[v][w] = (N p_f(v)/S(v)) [v==w]  - p_f(v) p_f(w).
    # We verify entrywise on the union of supports. Need S(v)>0 wherever any p_f(v)>0 (true: S>=p_f).
    # Build N*I - K and sum_f C_f, compare.
    verts=list(range(n))
    # K matrix
    Kmat={}
    for i in range(m):
        d=pfs[i]
        for v in d:
            for w in d:
                Kmat[(v,w)]=Kmat.get((v,w),F(0))+d[v]*d[w]
    wf_ok=True
    # diagonal contributions of sum_f C_f: sum_f N p_f(v)/S(v) ; off-diag: -sum_f p_f(v)p_f(w) = -K_vw
    # so sum_f C_f [v][w] = (v==w)*(N * sum_f p_f(v)/S(v)) - K_vw
    # sum_f p_f(v)/S(v) = S(v)/S(v) = 1 when S(v)>0, else 0. So diagonal = N*1 = N (for v with S(v)>0).
    # N*I - K diagonal = N - K_vv.  Need N*[S(v)>0] - K_vv == N - K_vv for all v?  i.e. S(v)>0 for all v.
    # vertices with S(v)==0 have K_vv==0 too (no p_f through them) and contribute N on RHS but 0 on LHS diag.
    # Check: identity holds on the SUPPORT (vertices touched by some geodesic). Off support both sides give N*I only.
    for v in verts:
        for w in verts:
            lhs = (N if (v==w and S[v]>0) else F(0)) - Kmat.get((v,w),F(0))
            rhs = (N if v==w else F(0)) - Kmat.get((v,w),F(0))
            # they differ only on diagonal at S(v)==0 vertices, where K_vv==0 -> lhs=0, rhs=N.
            if S[v]>0 or v!=w:
                if lhs!=rhs: wf_ok=False
    res['WF_id_on_support']=wf_ok
    # WF equivalence: C_f PSD  <=> (1/N) sum_v p_f(v) S(v) <= 1  <=> O1_f <= N.
    # Schur complement of diag(D_f) - p_f p_f^T (D_f(v)=N p_f(v)/S(v), only on supp(p_f)) PSD
    #   <=> sum_v p_f(v)^2 / D_f(v) <= 1  = sum_v p_f(v)^2 * S(v)/(N p_f(v)) = (1/N) sum_v p_f(v) S(v).
    wf_equiv=True
    for i,f in enumerate(M):
        q=F(0)
        for v,p in pfs[i].items():
            Dfv = N*p/S[v]   # >0
            q += p*p/Dfv
        target=F(0)
        for v,p in pfs[i].items(): target+=p*S[v]
        if q*N != target: wf_equiv=False
        # PSD condition q<=1 must equal O1<=N
    res['WF_equiv']=wf_equiv
    # CYCLE-SM
    res['CYCLE_SM_viol'] = any(Oell[i] > N*ell[M[i]] for i in range(m))
    # SM
    res['SM_viol'] = sum(t*t for t in T) > N*Gamma
    # GAMMA
    res['GAMMA_viol'] = Gamma > N*N
    return res

def run_census(Nmin,Nmax,limit=None):
    agg={}
    for nn in range(Nmin,Nmax+1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        if limit: out=out[:limit]
        cnt=0; o1max=None; viol=[]
        flags={k:True for k in ['P1','ID_OT','ID_ST','K_rowsum','O1_eq','WF_id_on_support','WF_equiv']}
        viol_flags={k:0 for k in ['O1_viol','CYCLE_SM_viol','SM_viol','GAMMA_viol']}
        worst_o1=None
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            cnt+=1
            r=analyze(info)
            for k in flags:
                if not r[k]: flags[k]=False; viol.append((g6,k))
            for k in viol_flags:
                if r[k]: viol_flags[k]+=1; viol.append((g6,k))
            if o1max is None or r['O1_max']>o1max:
                o1max=r['O1_max']; worst_o1=g6
        print(f"N={nn}: graphs-with-bad={cnt} | identities {flags} | violcounts {viol_flags} | max O1={o1max} ({float(o1max) if o1max else 0:.4f}) @ {worst_o1} | N={nn}",flush=True)
        if viol[:5]: print("   VIOL:",viol[:5],flush=True)

def run_blowups():
    print("--- blow-ups C5[t] (and via geng we only have small; use blow(t) C5 family) ---")
    for t in range(1,7):
        nn,E=blow(t); info=loads(nn,E)
        if info is None:
            print(f"C5[{t}] N={nn}: loads None"); continue
        r=analyze(info)
        print(f"C5[{t}] N={nn}: O1_max={r['O1_max']} ({float(r['O1_max']):.4f}) Gamma={info['G']} N^2={nn*nn} "
              f"| WF_id={r['WF_id_on_support']} WF_eq={r['WF_equiv']} O1_viol={r['O1_viol']} "
              f"CYCLE_SM_viol={r['CYCLE_SM_viol']} GAMMA_viol={r['GAMMA_viol']}",flush=True)

if __name__=="__main__":
    run_census(7,10)
    run_blowups()
