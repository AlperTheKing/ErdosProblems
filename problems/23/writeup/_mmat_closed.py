"""Test CLOSED-FORM candidate x>0 with Kx<=Nx (entrywise). EXACT Fraction.
Candidates (all positive):
  c1: x_v = 1                       (fails on O)
  c2: x_v = N/(2N - T_v)            (>1 when T_v>N; =1 when T_v=N; positive since T_v<2N? need T<2N)
  c3: x_v = 1 + (T_v - N)_+ / N
  c4: x_v = 1/(1 - (T_v-N)_+/N) truncated
  c5: x_v = sum over geodesics... structural
Check max over v of (Kx)_v - N x_v  (want <=0).
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
    return P,M,ell,K,T,N,n

def maxviol(K,T,N,n,x):
    mv=None; arg=None
    for v in range(n):
        kv=sum(K[v][w]*x[w] for w in range(n))
        d=kv-N*x[v]
        if mv is None or d>mv: mv=d; arg=v
    return mv,arg

def cand(name,K,T,N,n):
    if name=='c2':
        # need T_v<2N for positivity; else cap
        return [F(N,1)/(2*N-T[v]) if 2*N-T[v]>0 else None for v in range(n)]
    if name=='c3':
        return [F(1)+(max(T[v]-N,F(0)))/N for v in range(n)]
    if name=='c4':
        # 1/(1-(T-N)+/N) = N/(N-(T-N)+) ; need N-(T-N)+>0 i.e T<2N
        return [F(N)/(N-max(T[v]-N,F(0))) if (N-max(T[v]-N,F(0)))>0 else None for v in range(n)]
    return None

GRAPHS=["G?bF`w","I?BD@g]Qo","I?ABCc]}?"]
if __name__=="__main__":
    for g6 in GRAPHS:
        n,E=dec(g6); info=loads(n,E); P,M,ell,K,T,N,n=build(info)
        print("=== %s N=%d  maxT=%.2f ===" % (g6,n,float(max(T))))
        for name in ['c2','c3','c4']:
            x=cand(name,K,T,N,n)
            if any(v is None for v in x):
                print("  %s: x not positive (T>=2N somewhere)" % name); continue
            mv,arg=maxviol(K,T,N,n,x)
            print("  %s: max (Kx-Nx) = %.4f @v=%d  %s" % (name,float(mv),arg,"OK(<=0)" if mv<=0 else "VIOL"))
