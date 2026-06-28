"""Efficient (k2) stress on overloaded blow-ups N>=18. FLOAT first (fast), EXACT-confirm if margin tiny.
(k2)_o/N^2 = r_o + (1/N) sum_{q in Q} K[o,q] r_q + (1/N^2) sum K[o,q]K[q,q'] r_q'  >= 0.
"""
import numpy as np
from fractions import Fraction as F
from _h import dec, loads
from _schur_spec import pf_exact

def buildK_float(info):
    P,M,ell,n=pf_exact(info); N=n
    K=np.zeros((n,n))
    for d in P:
        vs=list(d.keys()); ps=np.array([float(d[v]) for v in vs])
        for ai,va in enumerate(vs):
            K[va,[vs]]  # noop
    # simpler:
    K=np.zeros((n,n))
    for d in P:
        vs=list(d.keys()); pv=np.array([float(d[v]) for v in vs])
        outer=np.outer(pv,pv)
        for ai,va in enumerate(vs):
            for bi,vb in enumerate(vs):
                K[va,vb]+=outer[ai,bi]
    T=K.sum(1)
    return K,T,N,n

def k2min_float(info):
    K,T,N,n=buildK_float(info)
    O=[v for v in range(n) if T[v]>N+1e-12]
    Q=[v for v in range(n) if T[v]<=N+1e-12]
    if not O: return None,None
    r=N-T
    KQQ=K[np.ix_(Q,Q)]; rQ=r[Q]
    W=KQQ@rQ  # length |Q|
    mn=None; argo=None
    for o in O:
        Koq=K[o,Q]
        val=r[o]+ (Koq@rQ)/N + (Koq@W)/(N*N)
        if mn is None or val<mn: mn=val; argo=o
    return mn,argo

def blow(g6,t):
    n,E=dec(g6); EE=[]
    for (a,b) in E:
        for i in range(t):
            for j in range(t): EE.append((a*t+i,b*t+j))
    return n*t,EE

if __name__=="__main__":
    print("=== (k2) FLOAT stress on blow-ups (margin = min_o (k2)_o/N^2) ===")
    bases=["G?bF`w","I?BD@g]Qo","I?ABCc]}?","J?AEB?oE?W?","H?AFBo]","J???E?pNu\\?","J??CE?{{?]?"]
    for g6 in bases:
        for t in [2,3]:
            nn,EE=blow(g6,t)
            if nn>40: continue
            info=loads(nn,EE)
            if info is None: print("  %s[%d] N=%d loads=None"%(g6,t,nn)); continue
            mn,o=k2min_float(info)
            if mn is None: print("  %s[%d] N=%d: no O"%(g6,t,nn))
            else: print("  %s[%d] N=%d: min (k2)/N^2 = %.6f @o=%d %s"%(g6,t,nn,mn,o,"<<<NEG"if mn<-1e-9 else "OK"))
