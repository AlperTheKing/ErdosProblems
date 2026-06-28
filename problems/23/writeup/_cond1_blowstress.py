"""Overloaded blow-up STRESS for condition (1) (guardrail: stress N>=18-22, census caused a false
closure before). For many base triangle-free graphs (census N<=11) and blow-up factors t, build the
t-blow-up, and EXACT-verify:
  - rowsum(K_QQ) <= N for all q in Q
  - block-diagonal-by-component reduction: prod block det == full det (Fractions)
  - every block det > 0  (=> N*I-K_QQ nonsingular)
  - inverse(N*I-K_QQ) entrywise >= 0  (Stieltjes)
  - NO critical KQQ-component (KQQ-connected, all T=N, all leak=0)
  - max O-isolated-component size (want: all singletons)
Reports the smallest margin block det and worst case. Concentrate on N in [18,32].
"""
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads
from _cond1_proof import build_K, det_frac, reach_components
from _schur_spec import matinv_frac

def blow(g6,t):
    n,E=dec(g6); EE=[]
    for (a,b) in E:
        for i in range(t):
            for j in range(t): EE.append((a*t+i,b*t+j))
    return n*t,EE

def check(info):
    K,T,O,Q,N,n=build_K(info)
    if not O: return None
    m=len(Q)
    KQQ=[[K[Q[i]][Q[j]] for j in range(m)] for i in range(m)]
    leak=[sum(K[Q[i]][o] for o in O) for i in range(m)]
    r=[F(N)-T[Q[i]] for i in range(m)]
    comp,ncomp=reach_components(KQQ)
    # rowsum bound
    rowsum_ok=all(sum(KQQ[i][j] for j in range(m))<=F(N) for i in range(m))
    AQQ=[[ (F(N) if i==j else F(0)) - KQQ[i][j] for j in range(m)] for i in range(m)]
    fulldet=det_frac(AQQ)
    prod=F(1); blockdet_pos=True; critical=0; max_iso=0
    for c in range(ncomp):
        nodes=[i for i in range(m) if comp[i]==c]
        if all(leak[i]==0 for i in nodes): max_iso=max(max_iso,len(nodes))
        if all(r[i]==0 and leak[i]==0 for i in nodes): critical+=1
        block=[[ (F(N) if i==j else F(0)) - KQQ[nodes[i]][nodes[j]] for j in range(len(nodes))] for i in range(len(nodes))]
        bd=det_frac(block); prod*=bd
        if bd<=0: blockdet_pos=False
    blockprod_ok=(prod==fulldet)
    Inv=matinv_frac(AQQ)
    inv_ok = Inv is not None and all(Inv[i][j]>=0 for i in range(m) for j in range(m))
    ok = rowsum_ok and blockdet_pos and blockprod_ok and inv_ok and critical==0 and fulldet>0
    return dict(N=N,m=m,nO=len(O),ncomp=ncomp,rowsum_ok=rowsum_ok,fulldet_pos=fulldet>0,
                blockdet_pos=blockdet_pos,blockprod_ok=blockprod_ok,inv_ok=inv_ok,
                critical=critical,max_iso=max_iso,ok=ok)

if __name__=="__main__":
    print("=== Condition (1) overloaded BLOW-UP stress (target N in [18,32]) ===")
    # base graphs known to have O (overloaded), from earlier runs + a spread
    bases=["G?bF`w","H?AAF_}","I?BD@g]Qo","I?ABCc]}?","J???E?pNu\\?","J?`@C_W{Ck?",
           "J?AE@`KkH{?","J?AEB?oE?W?"]
    seen=0; fails=0; worst=None
    for g6 in bases:
        for t in range(2,5):
            nn,EE=blow(g6,t)
            if nn>34: continue
            info=loads(nn,EE)
            if info is None: continue
            d=check(info)
            if d is None: continue
            if not (18<=d['N']<=34) and t==2 and d['N']<18:
                pass
            seen+=1
            status="OK" if d['ok'] else "FAIL"
            if not d['ok']: fails+=1; worst=(g6,t,d)
            print(f"  {g6}[{t}] N={d['N']}: {status} m={d['m']} nO={d['nO']} ncomp={d['ncomp']} "
                  f"rowsum<=N:{d['rowsum_ok']} blockdet>0:{d['blockdet_pos']} blockprod:{d['blockprod_ok']} "
                  f"inv>=0:{d['inv_ok']} critical={d['critical']} maxOiso={d['max_iso']}",flush=True)
    print(f"\n  TOTAL: {seen} blow-ups, {fails} FAILS")
    if worst: print("  WORST:",worst)
