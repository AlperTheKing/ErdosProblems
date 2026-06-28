"""STRESS the single-geodesic bound  sum_{v in C} S(v) <= N  on blowups to N=18-24
and Mycielskians, random tri-free. EXACT Fraction.  (single-geodesic is stronger than ROWSUM-O)"""
import subprocess, random
from fractions import Fraction as F
from _h import dec, GENG, loads

def pf_vec(info, f):
    Ps = info['cyc'][f]; nf = len(Ps); cnt = {}
    for P in Ps:
        for v in P: cnt[v] = cnt.get(v,0)+1
    return {v: F(cnt[v], nf) for v in cnt}

def worst_single(info):
    n=info['n']; N=n; M=info['M']; cyc=info['cyc']
    pfs={f:pf_vec(info,f) for f in M}
    S={v:sum(pfs[g].get(v,F(0)) for g in M) for v in range(n)}
    w=F(-10); ws=None
    for f in M:
        for P in cyc[f]:
            tot=sum(S[v] for v in P)
            if tot-N>w: w=tot-N; ws=(f,float(tot),N)
    return w,ws

def Cblow(k,q):
    L=2*k+1; m=L*q; E=[]
    for i in range(L):
        for a in range(q):
            for b in range(q): E.append((i*q+a,((i+1)%L)*q+b))
    return m,E

def blowup_g6(g6,t):
    n,E=dec(g6); nn=n*t; EE=[]
    for (a,b) in E:
        for i in range(t):
            for j in range(t): EE.append((a*t+i,b*t+j))
    return nn,EE

if __name__=="__main__":
    print("=== odd-cycle blowups C(2k+1)[q] ===")
    for (k,q) in [(2,4),(2,5),(3,3),(4,2),(2,3),(3,2),(2,2)]:
        m,E=Cblow(k,q)
        info=loads(m,E)
        if info is None: print(f"  C{2*k+1}[{q}] N={m}: skip"); continue
        w,ws=worst_single(info)
        print(f"  C{2*k+1}[{q}] N={m}: max(sum_C S - N)={float(w):+.4f} {'OK' if w<=0 else 'VIOLATION'} @ {ws}",flush=True)
    print("=== blowups of small witnesses ===")
    for g6,t in [("J???E?pNu\\?",2),("J?AEB?oE?W?",2),("H?bB@_W",2),("I?rFf_{N?",2),("FCp`_",3)]:
        try:
            nn,EE=blowup_g6(g6,t)
            info=loads(nn,EE)
            if info is None: print(f"  {g6}[{t}]: skip"); continue
            w,ws=worst_single(info)
            print(f"  {g6}[{t}] N={nn}: max(sum_C S - N)={float(w):+.4f} {'OK' if w<=0 else 'VIOLATION'}",flush=True)
        except Exception as e:
            print(f"  {g6}[{t}]: err {e}")
