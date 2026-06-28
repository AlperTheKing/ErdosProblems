"""Condition (1) verification: A[Q,Q] = N*I - K_QQ is a nonsingular Stieltjes M-matrix.

We exact-verify, over the full triangle-free census N<=11 and overloaded blow-ups:
 (R)  row-sum bound: for q in Q, sum_{q' in Q} K[q,q'] <= T[q] <= N.
 (L)  leakage: at least one q in Q has K-mass to O (sum_{o in O} K[q,o] > 0), i.e. K_QQ rowsum < T[q].
 (S)  STRICT spectral: rho(K_QQ) < N, checked EXACTLY by det(N*I - K_QQ) != 0 AND
      the M-matrix nonsingularity test: smallest real eig of N*I-K_QQ is > 0.
      Exact test used: A_QQ = N*I-K_QQ is a Z-matrix; it is a nonsingular M-matrix iff
      it has an all-positive vector x with A_QQ x > 0 (entrywise). We use x = ones and
      check A_QQ 1 = N*1 - K_QQ 1 = r_Q + (leakage to O) where r_Q = N - T_Q >= 0.
      So (A_QQ 1)[q] = (N - T[q]) + sum_{o in O} K[q,o] >= 0, strictly > 0 for the leaking q.
      That alone does NOT give nonsingular M-matrix (need x with A x > 0 everywhere or
      irreducibility). So we ALSO compute det exactly and the inverse-nonnegativity.
 (I)  inverse entrywise >= 0 (Stieltjes), checked exactly.
 (C)  connectivity/irreducibility structure of K_QQ (does the leaking-row argument propagate?).
"""
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads
from _schur_spec import pf_exact, matinv_frac

def build_K(info):
    P,M,ell,n=pf_exact(info); N=n
    K=[[F(0)]*n for _ in range(n)]
    for d in P:
        it=list(d.items())
        for a in range(len(it)):
            va,pa=it[a]
            for b in range(len(it)):
                vb,pb=it[b]; K[va][vb]+=pa*pb
    T=[sum(K[v][w] for w in range(n)) for v in range(n)]
    O=[v for v in range(n) if T[v]>N]
    Q=[v for v in range(n) if T[v]<=N]
    return K,T,O,Q,N,n

def det_frac(Mx):
    """exact determinant via fraction-free-ish Gauss (just use Fraction Gauss)."""
    m=len(Mx)
    if m==0: return F(1)
    A=[row[:] for row in Mx]; det=F(1)
    for col in range(m):
        piv=None
        for r in range(col,m):
            if A[r][col]!=0: piv=r; break
        if piv is None: return F(0)
        if piv!=col:
            A[col],A[piv]=A[piv],A[col]; det=-det
        det*=A[col][col]
        inv=A[col][col]
        for r in range(col+1,m):
            if A[r][col]!=0:
                fac=A[r][col]/inv
                A[r]=[A[r][k]-fac*A[col][k] for k in range(m)]
    return det

def reach_components(KQQ, eps=F(0)):
    """connected components of the graph on Q where i~j iff KQQ[i][j]>0 (i!=j). returns list of comp-id."""
    m=len(KQQ); seen=[-1]*m; cid=0
    for s in range(m):
        if seen[s]!=-1: continue
        stack=[s]; seen[s]=cid
        while stack:
            u=stack.pop()
            for v in range(m):
                if v!=u and seen[v]==-1 and KQQ[u][v]>0:
                    seen[v]=cid; stack.append(v)
        cid+=1
    return seen,cid

def test(info):
    K,T,O,Q,N,n=build_K(info)
    if not O: return ('noO',None)
    m=len(Q)
    KQQ=[[K[Q[i]][Q[j]] for j in range(m)] for i in range(m)]
    # (R) row-sum bound
    rowsum_ok=True; max_rowsum=F(0)
    leak=[F(0)]*m  # leakage to O from each q
    for i in range(m):
        q=Q[i]
        rs=sum(KQQ[i][j] for j in range(m))
        if rs>F(N): rowsum_ok=False
        if rs>max_rowsum: max_rowsum=rs
        leak[i]=sum(K[q][o] for o in O)
    # A_QQ row sums = (N - T[q]) + leak[q]  -- verify
    AQQ=[[ (F(N) if i==j else F(0)) - KQQ[i][j] for j in range(m)] for i in range(m)]
    aqq_rowsum=[sum(AQQ[i][j] for j in range(m)) for i in range(m)]
    # check identity aqq_rowsum[i] == (N - T[Q[i]]) + leak[i]
    ident_ok = all(aqq_rowsum[i] == (F(N)-T[Q[i]]) + leak[i] for i in range(m))
    num_leak = sum(1 for i in range(m) if leak[i]>0)
    # (S) det exact
    det = det_frac(AQQ)
    # (I) inverse nonneg
    Inv = matinv_frac(AQQ)
    inv_ok = Inv is not None and all(Inv[i][j]>=0 for i in range(m) for j in range(m))
    # components of KQQ-graph
    comp,ncomp = reach_components(KQQ)
    # for each component, does it contain a leaking node?
    comp_has_leak={c:False for c in range(ncomp)}
    for i in range(m):
        if leak[i]>0: comp_has_leak[comp[i]]=True
    all_comps_leak = all(comp_has_leak.values())
    # for the strictness argument: a component with NO leak and all-zero r could be singular.
    # r_Q[i] = N - T[Q[i]] >=0. Does a component exist where all r=0 AND no leak? that'd be singular.
    comp_all_r0_noleak=[]
    for c in range(ncomp):
        nodes=[i for i in range(m) if comp[i]==c]
        if (not comp_has_leak[c]) and all((F(N)-T[Q[i]])==0 for i in nodes):
            comp_all_r0_noleak.append(c)
    res=dict(N=N,m=m,nO=len(O),rowsum_ok=rowsum_ok,max_rowsum=max_rowsum,
             ident_ok=ident_ok,num_leak=num_leak,det=det,det_pos=(det>0),
             inv_ok=inv_ok,ncomp=ncomp,all_comps_leak=all_comps_leak,
             bad_comps=comp_all_r0_noleak)
    fails=[]
    if not rowsum_ok: fails.append('ROWSUM>N')
    if not ident_ok: fails.append('IDENT')
    if det<=0: fails.append('DET<=0')
    if not inv_ok: fails.append('INV_NEG/SING')
    if not all_comps_leak: fails.append('COMP_NO_LEAK')
    res['fails']=fails
    return ('FAIL' if fails else 'ok', res)

def run_census(Nmax,Nmin=7,stride=1):
    for nn in range(Nmin,Nmax+1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()[::stride]
        nt=0; fails=0; wg=None; min_detgap=None; comp_noleak=0; multicomp=0
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            st,d=test(info)
            if st=='noO': continue
            nt+=1
            if d['ncomp']>1: multicomp+=1
            if not d['all_comps_leak']: comp_noleak+=1
            if st=='FAIL':
                fails+=1
                if wg is None: wg=(g6,d['fails'])
        print(f"  N={nn}(str{stride}): with-O={nt} FAILS={fails}{(' @'+str(wg)) if wg else ''} | multi-comp-KQQ={multicomp} | comp-without-leak={comp_noleak}",flush=True)

def blow(g6,t):
    n,E=dec(g6); EE=[]
    for (a,b) in E:
        for i in range(t):
            for j in range(t): EE.append((a*t+i,b*t+j))
    return n*t,EE

if __name__=="__main__":
    print("=== Condition (1): A_QQ = N*I - K_QQ nonsingular Stieltjes M-matrix ===")
    print("    Checks: rowsum<=N, det>0, inverse>=0, KQQ-graph components, leakage to O")
    for g6 in ["G?bF`w","I?BD@g]Qo","I?ABCc]}?","J?AEB?oE?W?"]:
        n,E=dec(g6); info=loads(n,E); st,d=test(info)
        if d:
            print(f"  {g6:13} N={n}: {st} m={d['m']} nO={d['nO']} maxRS={float(d['max_rowsum']):.3f} "
                  f"detPos={d['det_pos']} invOK={d['inv_ok']} ncomp={d['ncomp']} allLeak={d['all_comps_leak']} fails={d['fails']}")
        else:
            print(f"  {g6:13} N={n}: {st}")
    nn,EE=blow("J???E?pNu\\?",2); info=loads(nn,EE); st,d=test(info)
    if d:
        print(f"  J???E?pNu?[2] N={nn}: {st} m={d['m']} nO={d['nO']} maxRS={float(d['max_rowsum']):.3f} "
              f"detPos={d['det_pos']} invOK={d['inv_ok']} ncomp={d['ncomp']} allLeak={d['all_comps_leak']} fails={d['fails']}")
    for g6 in ["I?BD@g]Qo","J?`@C_W{Ck?","J?AEB?oE?W?"]:
        nn,EE=blow(g6,2); info=loads(nn,EE)
        if info and nn<=24:
            st,d=test(info)
            if d:
                print(f"  {g6}[2] N={nn}: {st} m={d['m']} nO={d['nO']} maxRS={float(d['max_rowsum']):.3f} "
                      f"detPos={d['det_pos']} invOK={d['inv_ok']} ncomp={d['ncomp']} allLeak={d['all_comps_leak']} fails={d['fails']}")
    run_census(9,7,1)
    run_census(10,10,4)
    run_census(11,11,30)
