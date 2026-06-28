"""STRESS (k2) on overloaded blow-ups to N>=18. EXACT Fraction. Per guardrail:
census-only caused a false closure; verify (k2)>=0 on big overloaded graphs.
Blow up small overloaded graphs C_{2k+1}[t] variants and the known overloaded witnesses.
(k2)_o = N^2 r_o + N sum_{q in Q} K[o,q] r_q + sum_{q,q' in Q} K[o,q]K[q,q'] r_q'   >= 0.
Report min over o of (k2)/N^2 (margin) per graph; flag any < 0.
"""
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads
from _schur_spec import pf_exact

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
    O=[v for v in range(n) if T[v]>N]
    Q=[v for v in range(n) if T[v]<=N]
    return P,M,ell,K,T,O,Q,N,n

def k2min(info):
    P,M,ell,K,T,O,Q,N,n=build(info)
    if not O: return ('noO',None)
    r=[F(N)-T[v] for v in range(n)]
    W={q:sum(K[q][qp]*r[qp] for qp in Q) for q in Q}
    mn=None
    for o in O:
        t0=N*N*r[o]; t1=N*sum(K[o][q]*r[q] for q in Q)
        t2=sum(K[o][q]*W[q] for q in Q)
        val=(t0+t1+t2)
        if mn is None or val<mn: mn=val
    return ('ok', mn/(N*N))  # margin scaled

def blow(g6,t):
    n,E=dec(g6); EE=[]
    for (a,b) in E:
        for i in range(t):
            for j in range(t): EE.append((a*t+i,b*t+j))
    return n*t,EE

# build C_{2k+1} with one "extra chord" to force overload, then blow up.
def odd_cycle_chorded(L):
    # cycle 0..L-1, plus we just use plain odd cycle (uniform, no O). Need asymmetry.
    pass

if __name__=="__main__":
    # overloaded base graphs from census (have O):
    bases=["G?bF`w","I?BD@g]Qo","I?ABCc]}?","J?AEB?oE?W?","H?AFBo]"]
    # also the N=22 sandwich-killer witness base (already n=11) blown x2:
    print("=== STRESS (k2) on overloaded blow-ups (EXACT) ===")
    for g6 in bases:
        for t in [2,3]:
            nn,EE=blow(g6,t)
            if nn>30: continue
            info=loads(nn,EE)
            if info is None:
                print("  %s[%d] N=%d: loads=None (skip)" % (g6,t,nn)); continue
            st,mg=k2min(info)
            if st=='noO':
                print("  %s[%d] N=%d: no overloaded vertex" % (g6,t,nn))
            else:
                print("  %s[%d] N=%d: min (k2)/N^2 margin = %.5f %s" % (g6,t,nn,float(mg), "<<< NEG!!!" if mg<0 else "OK"))
