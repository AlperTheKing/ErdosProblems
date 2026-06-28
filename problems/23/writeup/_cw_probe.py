"""Probe: is (KT)_v = N*T_v an IDENTITY for the max-vertex only, or for ALL v? And WHICH vertices attain equality?
If max_v(KT-N T)=0 always but it is NOT all-v, then equality is attained on a special vertex set.
Also: print full (KT)_v vs N*T_v per vertex on a few non-tight graphs to see the pattern."""
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads, blow

def pf_exact(info):
    M=info['M']; cyc=info['cyc']; pf=[]
    for f in M:
        Ps=cyc[f]; nf=len(Ps); cnt={}
        for Pp in Ps:
            for v in Pp: cnt[v]=cnt.get(v,0)+1
        pf.append({v:F(cnt[v],nf) for v in cnt})
    return pf

def detail(info, g6=None):
    n=info['n']; N=n; M=info['M']; ell=info['ell']; m=len(M)
    pf=pf_exact(info)
    T=[sum(ell[M[g]]*pf[g].get(v,F(0)) for g in range(m)) for v in range(n)]
    def ip(a,b):
        s=F(0)
        for w,av in a.items():
            bv=b.get(w)
            if bv is not None: s+=av*bv
        return s
    O=[[ip(pf[i],pf[j]) for j in range(m)] for i in range(m)]
    Oell=[sum(O[i][j]*ell[M[j]] for j in range(m)) for i in range(m)]
    KT=[sum(pf[i].get(v,F(0))*Oell[i] for i in range(m)) for v in range(n)]
    res=[KT[v]-N*T[v] for v in range(n)]
    Gamma=sum(t for t in T)
    return T,Oell,KT,res,Gamma,ell,M

def show(g6):
    n,E=dec(g6); info=loads(n,E)
    T,Oell,KT,res,Gamma,ell,M=detail(info,g6)
    N=n
    print(f"\n{g6} N={N} Gamma={Gamma}={float(Gamma):.3f} Gamma/N^2={float(Gamma)/(N*N):.4f}  #bad={len(M)}")
    print(f"  ell(f): {[ell[f] for f in M]}")
    print(f"  (O ell)_f vs N*ell(f):  Cycle-SM residual = {[ (float(Oell[i]-N*ell[M[i]])) for i in range(len(M))]}")
    print(f"  per-vertex T_v: {[float(t) for t in T]}")
    print(f"  per-vertex (KT)_v - N*T_v: {[float(r) for r in res]}")
    nz=[v for v in range(n) if T[v]!=0]
    eqset=[v for v in range(n) if res[v]==0 and T[v]!=0]
    print(f"  vertices with T>0: {nz}   equality (KT=N T) vertices: {eqset}")
    # also: sum over v of res = sum KT - N sum T = sum_f Oell_f - N Gamma... check sign of total
    print(f"  SUM_v (KT-N T) = {float(sum(res)):.4f}  (=sum_f(Oell_f)-N*Gamma)")

if __name__=="__main__":
    # non-tight small graphs where the max was 0 (suspicious)
    for g6 in ["G?AEBw","G?bF`w","F?bBo","H??CE@}"]:
        show(g6)
    # a clearly-non-extremal one with strict slack
    print("\n=== a few more N=8 to see strict-slack vertices ===")
    out=subprocess.run([GENG,"-tc","8"],capture_output=True,text=True).stdout.split()
    shown=0
    for g6 in out:
        n,E=dec(g6); info=loads(n,E)
        if info is None: continue
        T,Oell,KT,res,Gamma,ell,M=detail(info,g6)
        # find a graph where some T>0 vertex has strict NEGATIVE res
        strict=[v for v in range(n) if T[v]!=0 and res[v]<0]
        if strict and shown<3:
            show(g6); shown+=1
