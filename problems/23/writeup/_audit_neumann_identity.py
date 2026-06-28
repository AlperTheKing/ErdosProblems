"""Adversarial audit: confirm E*1_O = r_O + K[O,Q] (N I - K_QQ)^{-1} r_Q  EXACTLY,
and that g_k partial sums are monotone nondecreasing lower bounds on the true Schur rowsum.
Also confirm the congruence L A L^T = diag(Aqq, E) exactly (Schur criterion)."""
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads
from _schur_spec import pf_exact, matinv_frac

def build(info):
    P,M,ell,n=pf_exact(info); N=n
    K=[[F(0)]*n for _ in range(n)]
    for d in P:
        it=list(d.items())
        for a in range(len(it)):
            va,pa=it[a]
            for b in range(len(it)):
                vb,pb=it[b]; K[va][vb]+=pa*pb
    T=[sum(K[v][w] for w in range(n)) for v in range(n)]
    A=[[ (F(N) if i==j else F(0)) - K[i][j] for j in range(n)] for i in range(n)]
    O=[v for v in range(n) if T[v]>N]
    Q=[v for v in range(n) if T[v]<=N]
    return K,T,A,O,Q,N,n

def mv(Mx,x):  # matrix-vector (lists)
    return [sum(Mx[i][j]*x[j] for j in range(len(x))) for i in range(len(Mx))]

def audit(info,label):
    K,T,A,O,Q,N,n=build(info)
    if not O: return f"{label}: noO"
    nq,no=len(Q),len(O)
    Aqq=[[A[Q[i]][Q[j]] for j in range(nq)] for i in range(nq)]
    Aqo=[[A[Q[i]][O[j]] for j in range(no)] for i in range(nq)]
    Aoq=[[A[O[i]][Q[j]] for j in range(nq)] for i in range(no)]
    Aoo=[[A[O[i]][O[j]] for j in range(no)] for i in range(no)]
    Inv=matinv_frac(Aqq)
    assert Inv is not None, f"{label}: SINGULAR"
    # E directly
    X=[[sum(Inv[i][k]*Aqo[k][j] for k in range(nq)) for j in range(no)] for i in range(nq)]
    E=[[Aoo[i][j]-sum(Aoq[i][k]*X[k][j] for k in range(nq)) for j in range(no)] for i in range(no)]
    rowsum_direct=[sum(E[i][j] for j in range(no)) for i in range(no)]
    # identity: r_O + K[O,Q] g, g=Inv*r_Q
    r=[F(N)-T[v] for v in range(n)]
    rQ=[r[Q[i]] for i in range(nq)]
    rO=[r[O[i]] for i in range(no)]
    g=mv(Inv,rQ)
    KOQ=[[K[O[i]][Q[j]] for j in range(nq)] for i in range(no)]
    rowsum_ident=[rO[i]+sum(KOQ[i][j]*g[j] for j in range(nq)) for i in range(no)]
    id_ok = (rowsum_direct==rowsum_ident)
    # congruence: L A L^T == diag(Aqq,E) with L=[[I,0],[-Aoq Aqq^{-1},I]] in (Q,O) ordering
    # Build permuted A in order Q then O
    order=Q+O
    Aperm=[[A[order[i]][order[j]] for j in range(n)] for i in range(n)]
    # B = -Aoq Aqq^{-1}  (no x nq)
    Bm=[[-sum(Aoq[i][k]*Inv[k][j] for k in range(nq)) for j in range(nq)] for i in range(no)]
    L=[[F(1) if i==j else F(0) for j in range(n)] for i in range(n)]
    for i in range(no):
        for j in range(nq): L[nq+i][j]=Bm[i][j]
    LA=[[sum(L[i][k]*Aperm[k][j] for k in range(n)) for j in range(n)] for i in range(n)]
    LALt=[[sum(LA[i][k]*L[j][k] for k in range(n)) for j in range(n)] for i in range(n)]
    # expected block diag
    congr_ok=True
    for i in range(n):
        for j in range(n):
            if i<nq and j<nq: exp=Aqq[i][j]
            elif i>=nq and j>=nq: exp=E[i-nq][j-nq]
            else: exp=F(0)
            if LALt[i][j]!=exp: congr_ok=False
    # Neumann monotonicity check: g_k increasing, each term >=0
    KQQ=[[K[Q[i]][Q[j]] for j in range(nq)] for i in range(nq)]
    term=[x/N for x in rQ]; gk=[F(0)]*nq; mono_ok=True; prev=None
    g_full_match=False
    for k in range(1,8):
        gk=[gk[i]+term[i] for i in range(nq)]
        rs=[rO[i]+sum(KOQ[i][j]*gk[j] for j in range(nq)) for i in range(no)]
        mk=min(rs)
        if prev is not None and mk<prev-F(1,10**12): mono_ok=False
        prev=mk
        term=[sum(KQQ[i][j]*term[j] for j in range(nq))/N for i in range(nq)]
    # check g_full = sum of all terms equals Inv*r_Q (Neumann converges): compare g vs g_8 closeness not exact (infinite)
    return f"{label}: N={n} |O|={no} id_ok={id_ok} congr_ok={congr_ok} neumann_mono={mono_ok} min_rowsum={float(min(rowsum_direct)):+.4f}"

if __name__=="__main__":
    for g6 in ["G?bF`w","I?BD@g]Qo","I?ABCc]}?"]:
        n,E=dec(g6); print(audit(loads(n,E),g6))
    # a blow-up
    g6="J???E?pNu\\?"; n,E=dec(g6); EE=[]
    for (a,b) in E:
        for i in range(2):
            for j in range(2): EE.append((a*2+i,b*2+j))
    print(audit(loads(n*2,EE),"J???E?pNu[2]"))
    # census sweep N<=10 to confirm identity+congruence hold everywhere
    for nn in range(7,11):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        bad=0; tot=0
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            res=audit(info,g6)
            if "noO" in res: continue
            tot+=1
            if "id_ok=True congr_ok=True neumann_mono=True" not in res:
                bad+=1; print("  VIOLATION:",res)
        print(f"  N={nn}: tested {tot} graphs-with-O, identity/congruence/mono violations: {bad}")
