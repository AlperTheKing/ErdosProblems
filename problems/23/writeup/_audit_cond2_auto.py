"""Adversarial finding: condition (2) (E offdiag <= 0) is AUTOMATIC given condition (1) (Aqq^{-1} >= 0).
Proof: E[o_i,o_j] (i!=j) = Aoo[o_i,o_j] - (Aoq Aqq^{-1} Aqo)[i,j].
  Aoo[o_i,o_j] = -K[o_i,o_j] <= 0  (offdiag of N*I-K, K>=0).
  Aoq = -K[O,Q] (entrywise <=0), Aqo = -K[Q,O] (<=0), Aqq^{-1} >= 0 (cond 1).
  => Aoq Aqq^{-1} Aqo = K[O,Q] Aqq^{-1} K[Q,O] >= 0 entrywise.
  => E_offdiag = (<=0) - (>=0) <= 0.  ALWAYS, given (1).
Verify numerically that whenever inv_neg is False (cond 1 holds), offdiag_pos is False (cond 2 holds),
i.e. cond1 alone implies cond2 across census + blowups."""
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads
from _audit_stress import build_K, blow
from _schur_spec import matinv_frac

def check(info):
    K,T,N,n=build_K(info)
    O=[v for v in range(n) if T[v]>N]; Q=[v for v in range(n) if T[v]<=N]
    if not O: return None
    nq,no=len(Q),len(O)
    A=[[(F(N) if i==j else F(0))-K[i][j] for j in range(n)] for i in range(n)]
    Aqq=[[A[Q[i]][Q[j]] for j in range(nq)] for i in range(nq)]
    Inv=matinv_frac(Aqq)
    if Inv is None: return ('SING',)
    inv_nonneg=all(Inv[i][j]>=0 for i in range(nq) for j in range(nq))
    Aqo=[[A[Q[i]][O[j]] for j in range(no)] for i in range(nq)]
    Aoq=[[A[O[i]][Q[j]] for j in range(nq)] for i in range(no)]
    Aoo=[[A[O[i]][O[j]] for j in range(no)] for i in range(no)]
    X=[[sum(Inv[i][k]*Aqo[k][j] for k in range(nq)) for j in range(no)] for i in range(nq)]
    E=[[Aoo[i][j]-sum(Aoq[i][k]*X[k][j] for k in range(nq)) for j in range(no)] for i in range(no)]
    offdiag_ok=all(E[i][j]<=0 for i in range(no) for j in range(no) if i!=j)
    # the implication: inv_nonneg => offdiag_ok
    return ('IMPL_BROKEN' if (inv_nonneg and not offdiag_ok) else 'ok', inv_nonneg, offdiag_ok)

if __name__=="__main__":
    def overloaded(nn,stride=1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()[::stride]
        return [g6 for g6 in out if (lambda i: i is not None and any(t>nn for t in i['T']))(loads(*dec(g6)))]
    print("=== verify: cond1 (Aqq^-1>=0) => cond2 (E offdiag<=0) ===",flush=True)
    bad=0; tot=0
    for nn in range(7,12):
        st=1 if nn<=10 else 5
        for g6 in overloaded(nn,st):
            r=check(loads(*dec(g6)))
            if r is None: continue
            tot+=1
            if r[0]=='IMPL_BROKEN': bad+=1; print(f"  IMPL BROKEN {g6} N={nn}: inv_nonneg={r[1]} offdiag_ok={r[2]}")
    # blowups
    for nn in range(8,11):
        st=1
        for g6 in overloaded(nn,st):
            for t in (2,):
                NN,EE=blow(g6,t)
                if NN>20: continue
                info=loads(NN,EE)
                if info is None: continue
                r=check(info)
                if r is None: continue
                tot+=1
                if r[0]=='IMPL_BROKEN': bad+=1; print(f"  IMPL BROKEN {g6}[{t}] N={NN}")
    print(f"  tested {tot} overloaded cases (census+blowups), cond1=>cond2 implication broken: {bad}",flush=True)
