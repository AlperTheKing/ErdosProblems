"""Codex ASK (block 9): exact Schur-complement M-matrix certificate for SPEC (rho(K)<=N).
K[v,w]=sum_f p_f(v)p_f(w); T[v]=sum_f ell(f)p_f(v); A=N*I-K (Fractions); O={v:T[v]>N}, Q=V\\O.
E = A[O,O] - A[O,Q] A[Q,Q]^{-1} A[Q,O]  (Schur complement). Candidate:
 (1) A[Q,Q] nonsingular + M-matrix: offdiag<=0 (auto, K>=0) AND inverse entrywise >=0 (Stieltjes => PSD);
 (2) E offdiagonal <=0;
 (3) every row sum of E >= 0.
If (1)-(3): E symmetric weakly-diag-dominant with nonpos offdiag => PSD; with A[Q,Q] PSD => A=N*I-K PSD => SPEC.
EXACT rational. Report smallest violation: graph6,N,O,min row sum E, failed condition; A[Q,Q] singular ever?"""
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads

def pf_exact(info):
    M=info['M']; cyc=info['cyc']; ell=info['ell']; n=info['n']
    P=[]  # list over f of dict v->Fraction
    for f in M:
        Ps=cyc[f]; nf=len(Ps); cnt={}
        for p in Ps:
            for v in p: cnt[v]=cnt.get(v,0)+1
        P.append({v:F(cnt[v],nf) for v in cnt})
    return P,M,ell,n

def matinv_frac(Aqq):
    """exact inverse of a list-of-lists Fraction matrix via Gauss-Jordan. returns None if singular."""
    m=len(Aqq)
    if m==0: return []
    Aug=[[Aqq[i][j] for j in range(m)]+[F(1) if i==j else F(0) for j in range(m)] for i in range(m)]
    for col in range(m):
        piv=None
        for r in range(col,m):
            if Aug[r][col]!=0: piv=r; break
        if piv is None: return None
        Aug[col],Aug[piv]=Aug[piv],Aug[col]
        pv=Aug[col][col]
        Aug[col]=[x/pv for x in Aug[col]]
        for r in range(m):
            if r!=col and Aug[r][col]!=0:
                fac=Aug[r][col]
                Aug[r]=[Aug[r][k]-fac*Aug[col][k] for k in range(2*m)]
    return [[Aug[i][m+j] for j in range(m)] for i in range(m)]

def test(info):
    P,M,ell,n=pf_exact(info); N=n
    K=[[F(0)]*n for _ in range(n)]
    for d in P:
        items=list(d.items())
        for a in range(len(items)):
            va,pa=items[a]
            for b in range(len(items)):
                vb,pb=items[b]
                K[va][vb]+=pa*pb
    T=[sum(ell[M[fi]]*P[fi].get(v,F(0)) for fi in range(len(M))) for v in range(n)]
    A=[[ (F(N) if i==j else F(0)) - K[i][j] for j in range(n)] for i in range(n)]
    O=[v for v in range(n) if T[v]>N]
    Q=[v for v in range(n) if T[v]<=N]
    if not O: return ('pass-noO',None)
    Aqq=[[A[i][j] for j in Q] for i in Q]
    Inv=matinv_frac(Aqq)
    if Inv is None: return ('SINGULAR_AQQ',O)
    # (1) inverse >=0 ?
    inv_neg=any(Inv[i][j]<0 for i in range(len(Q)) for j in range(len(Q)))
    # X = Aqq^{-1} A[Q,O]
    Aqo=[[A[q][o] for o in O] for q in Q]
    X=[[sum(Inv[i][k]*Aqo[k][jj] for k in range(len(Q))) for jj in range(len(O))] for i in range(len(Q))]
    Aoq=[[A[o][q] for q in Q] for o in O]
    Aoo=[[A[o][o2] for o2 in O] for o in O]
    E=[[Aoo[i][j]-sum(Aoq[i][k]*X[k][j] for k in range(len(Q))) for j in range(len(O))] for i in range(len(O))]
    mo=len(O)
    offdiag_pos=any(E[i][j]>0 for i in range(mo) for j in range(mo) if i!=j)
    rowsums=[sum(E[i][j] for j in range(mo)) for i in range(mo)]
    minrow=min(rowsums)
    fails=[]
    if inv_neg: fails.append('AQQ_inv_neg')
    if offdiag_pos: fails.append('E_offdiag_pos')
    if minrow<0: fails.append('E_rowsum_neg')
    return ('ok' if not fails else 'FAIL', dict(O=O,minrow=minrow,fails=fails,inv_neg=inv_neg,offdiag_pos=offdiag_pos))

def run_census(Nmax,Nmin=7,stride=1):
    for nn in range(Nmin,Nmax+1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()[::stride]
        nt=0; fails=0; sing=0; worst=None; wg=None; minmargin=None
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            nt+=1; st,d=test(info)
            if st=='SINGULAR_AQQ': sing+=1
            elif st=='FAIL':
                fails+=1
                if worst is None or d['minrow']<worst: worst=d['minrow']; wg=(g6,d['fails'])
            elif st=='ok':
                if minmargin is None or d['minrow']<minmargin: minmargin=d['minrow']
        print(f"  N={nn}(str{stride}): cfg={nt} | FAILS:{fails}{(' worst minrow='+str(float(worst))+'@'+str(wg)) if worst is not None else ''} | AQQ singular:{sing} | min E-rowsum margin(ok cases)={float(minmargin) if minmargin is not None else 'na'}",flush=True)

def blow(g6,t):
    n,E=dec(g6); EE=[]
    for (a,b) in E:
        for i in range(t):
            for j in range(t): EE.append((a*t+i,b*t+j))
    return n*t,EE

if __name__=="__main__":
    print("=== exact Schur-complement M-matrix certificate for SPEC (rho(K)<=N) ===")
    for g6 in ["G?bF`w","I?BD@g]Qo","I?ABCc]}?","J?AEB?oE?W?"]:
        n,E=dec(g6); info=loads(n,E); st,d=test(info)
        print(f"  {g6:13} N={n}: {st} {d}")
    nn,EE=blow("J???E?pNu\\?",2); info=loads(nn,EE); st,d=test(info)
    print(f"  J???E?pNu?[2] N={nn}: {st} | O={d['O'] if d else None} minrow={float(d['minrow']) if d and 'minrow' in d else 'na'} fails={d['fails'] if d else None}")
    run_census(9,7,1)
    run_census(10,10,6)
    run_census(11,11,80)
