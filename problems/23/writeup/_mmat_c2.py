"""TEST candidate x_v = N/(2N - T_v) for Kx <= Nx (entrywise) over FULL census + blow-ups. EXACT.
If valid: NI-K is a symmetric Z-matrix with M-matrix vector x>0 => NI-K is an M-matrix => PSD => SPEC.
Requires 2N-T_v>0 i.e. T_v<2N (positivity of x). Report max T_v and any violations.

Inequality per row v:  sum_w K[v][w]/(2N-T_w) <= N/(2N-T_v).
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
    return K,T,N,n

def testc2(K,T,N,n):
    # positivity
    if any(2*N-T[v]<=0 for v in range(n)):
        return ('T>=2N', max(float(t) for t in T))
    x=[F(N)/(2*N-T[v]) for v in range(n)]
    worst=None
    for v in range(n):
        lhs=sum(K[v][w]*x[w] for w in range(n))
        rhs=N*x[v]
        d=lhs-rhs  # want <=0
        if worst is None or d>worst: worst=d
    return ('ok', worst)

def blow(g6,t):
    n,E=dec(g6); EE=[]
    for (a,b) in E:
        for i in range(t):
            for j in range(t): EE.append((a*t+i,b*t+j))
    return n*t,EE

def census(Nmax,Nmin=5,stride=1):
    for nn in range(Nmin,Nmax+1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()[::stride]
        ntot=0; fails=0; worstd=None; wg=None; maxT=0; t2cnt=0
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            K,T,N,n=build(info); ntot+=1
            mt=max(float(t) for t in T); maxT=max(maxT,mt)
            st,d=testc2(K,T,N,n)
            if st=='T>=2N': t2cnt+=1; continue
            if d>0:
                fails+=1
                if worstd is None or d>worstd: worstd=d; wg=g6
        print("  N=%d(str%d): cfg=%d | c2 VIOL:%d %s | T>=2N:%d | maxT=%.2f(=%.3fN)" % (nn,stride,ntot,fails,(' worst=+'+str(float(worstd))+'@'+wg) if worstd else '',t2cnt,maxT,maxT/nn),flush=True)

if __name__=="__main__":
    print("=== c2: x_v=N/(2N-T_v), test Kx<=Nx EXACT ===")
    bases=["G?bF`w","I?BD@g]Qo","I?ABCc]}?","J?AEB?oE?W?","H?AFBo]"]
    print("-- blow-ups (stress N>=18) --")
    for g6 in bases:
        for t in [2,3]:
            nn,EE=blow(g6,t)
            if nn>33: continue
            info=loads(nn,EE)
            if info is None: print("  %s[%d] N=%d loads=None"%(g6,t,nn)); continue
            K,T,N,n=build(info)
            st,d=testc2(K,T,N,n)
            print("  %s[%d] N=%d: %s worst(Kx-Nx)=%s maxT=%.2f" % (g6,t,nn,st, ('%.5f'%float(d)) if st=='ok' else '-', max(float(x) for x in T)))
    print("-- census --")
    census(9,5,1)
    census(10,10,4)
    census(11,11,40)
