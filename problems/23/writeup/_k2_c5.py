"""C5 blowup analysis (the extremal/tight case T=N uniform). Plus a slightly overloaded perturbation.
On C5[t]: T[v]=N for all v => no O => trivially fine. We need OVERLOADED examples to see tightness.
Use C5[t] minus/plus an edge, or C7 etc. Just examine general structure on the census worst-margin graph.
Find the graph + o with the SMALLEST F(o)/(N^2(T_o-N)) ratio (tightest) over census N<=9.
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

def Fo(K,T,O,Q,N,n,o):
    r=[F(N)-T[v] for v in range(n)]
    t0=N*N*r[o]; t1=N*sum(K[o][q]*r[q] for q in Q)
    t2=sum(K[o][q]*K[q][qp]*r[qp] for q in Q for qp in Q)
    return t0+t1+t2

if __name__=="__main__":
    worst=None
    for nn in range(5,10):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            P,M,ell,K,T,O,Q,N,n=build(info)
            for o in O:
                f=Fo(K,T,O,Q,N,n,o)
                # ratio F / (N^2 (T_o - N)) -- closer to 0 = tighter
                denom=N*N*(T[o]-N)
                ratio=f/denom
                if worst is None or ratio<worst[0]:
                    worst=(ratio,g6,n,o,float(T[o]),float(f))
    print("tightest (smallest F/(N^2(T_o-N))):")
    print("  ratio=%.5f g6=%s N=%d o=%d T_o=%.3f F=%.3f" % (float(worst[0]),worst[1],worst[2],worst[3],worst[4],worst[5]))
